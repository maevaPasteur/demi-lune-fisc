#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ÉTAPE 2 — Calcul indépendant des « disparitions » de boissons.
Croise achats (par exercice) et ventes caisse (attribuées par dose/recette)
via les tables de correspondance map-*.json. Valorise l'écart au COÛT d'achat
et au PRIX de vente. Aucune donnée du fisc.

Sorties :
  data/disparitions.json   (résultat structuré, réutilisable pour inventaire/simulations)
  RAPPORT-disparitions.md   (tableaux lisibles)
Ré-exécutable : python3 scripts/boissons/02_disparitions.py
"""
import json, glob, os
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
BASE = os.path.join(ROOT, 'analyses-independantes', 'boissons')
DATA = os.path.join(BASE, 'data')
EX = ['2022-2023', '2023-2024', '2024-2025']
RANG_CONF = {'haute': 3, 'moyenne': 2, 'basse': 1, None: 1}

ach = json.load(open(f'{DATA}/achats-exercice.json'))
ven = json.load(open(f'{DATA}/ventes-caisse.json'))
prod = {p['code']: p for p in ach['produits']}

# --- Fusion des cartes de correspondance ------------------------------------
mapref = {}   # ref caisse -> entrée map
for f in sorted(glob.glob(f'{DATA}/map-*.json')):
    for v in json.load(open(f)).get('ventes', []):
        mapref[v['ref']] = v

# Prix CARTE par bouton et par période (carte 20/07/2021 pour 2022-2023 ;
# carte 26/04/2023 pour 2023-2025). Permet une valorisation au TARIF CARTE.
carteref = {}
try:
    for b in json.load(open(f'{DATA}/prix-carte-par-bouton.json')).get('boutons', []):
        carteref[b['ref']] = b
except FileNotFoundError:
    pass
def prix_carte_bouton(ex, ref):
    b = carteref.get(ref)
    if not b:
        return None
    return b.get('prixCarte_2022_2023') if ex == '2022-2023' else b.get('prixCarte_2023_2025')

# --- 1. Attribution du VOLUME VENDU à chaque code d'achat -------------------
vendu_cl = {ex: defaultdict(float) for ex in EX}     # ex -> code -> cl vendus
conf_code = defaultdict(lambda: 3)                    # code -> pire confiance (3=haute)
# Prix de vente par cl, observé PAR EXERCICE (reflète l'évolution des prix / les 3
# cartes successives) — calculé sur les boutons MONO-ingrédient (produit servi pur).
ca_mono = {ex: defaultdict(float) for ex in EX}   # ex -> code -> Σ (prix/cl × volume)
cl_mono = {ex: defaultdict(float) for ex in EX}   # ex -> code -> Σ volume mono-ingrédient
ca_carte = {ex: defaultdict(float) for ex in EX}  # idem mais au TARIF CARTE de la période
cl_carte = {ex: defaultdict(float) for ex in EX}
ca_couvert = {ex: 0.0 for ex in EX}
ca_total = {ex: 0.0 for ex in EX}

for ex in EX:
    for p in ven['parExercice'][ex]['produits']:
        ca_total[ex] += p['caTtc']
        m = mapref.get(p['ref'])
        if not m or not m.get('ingredients'):
            continue
        qte = p['qte']
        ca_couvert[ex] += p['caTtc']
        conf = RANG_CONF.get(m.get('confiance'), 1)
        ings = m['ingredients']
        dose = m.get('doseTotaleCl')
        somme = sum((i.get('clParUnite') or 0) for i in ings)
        # Normalisation : UN service = doseTotaleCl. Les millésimes substituts d'un
        # même bouton (Σ clParUnite > dose) sont ramenés à la dose réelle, répartie
        # proportionnellement — sinon une coupe est comptée une fois par millésime.
        scale = (dose / somme) if (dose and somme and somme > dose) else 1.0
        # Service "pur" = tous les ingrédients d'une même catégorie (vin/spiritueux
        # servi seul) ; un cocktail mélange plusieurs catégories -> pas de prix/cl.
        cats = {prod[i['achatCode']]['categorie'] for i in ings if i['achatCode'] in prod}
        pur = (len(cats) == 1 and dose)
        ppc = (p['prixMoyen'] / dose) if (pur and p.get('prixMoyen')) else None
        pcarte = prix_carte_bouton(ex, p['ref'])
        ppc_carte = (pcarte / dose) if (pur and pcarte) else None
        for ing in ings:
            c = ing['achatCode']
            w = qte * (ing.get('clParUnite') or 0) * scale
            vendu_cl[ex][c] += w
            conf_code[c] = min(conf_code[c], conf)
            if ppc is not None:
                ca_mono[ex][c] += ppc * w   # contribution prix×volume (de cet exercice)
                cl_mono[ex][c] += w
            if ppc_carte is not None:
                ca_carte[ex][c] += ppc_carte * w
                cl_carte[ex][c] += w

# prix de vente TTC/cl PAR EXERCICE (produits servis purs) + repli toutes années
prix_vente_cl = {ex: {c: (ca_mono[ex][c] / cl_mono[ex][c]) for c in cl_mono[ex] if cl_mono[ex][c] > 0} for ex in EX}
_camg = defaultdict(float); _clmg = defaultdict(float)
for ex in EX:
    for c in cl_mono[ex]:
        _camg[c] += ca_mono[ex][c]; _clmg[c] += cl_mono[ex][c]
prix_vente_cl_glob = {c: (_camg[c] / _clmg[c]) for c in _clmg if _clmg[c] > 0}
def pvc_de(ex, code):
    """Prix de vente/cl de cet exercice ; repli sur la moyenne 3 ans si absent."""
    return prix_vente_cl[ex].get(code) or prix_vente_cl_glob.get(code)

# Idem au TARIF CARTE (par exercice). Pas de repli inter-période (les prix changent).
prix_carte_cl = {ex: {c: (ca_carte[ex][c] / cl_carte[ex][c]) for c in cl_carte[ex] if cl_carte[ex][c] > 0} for ex in EX}
def pcc_de(ex, code):
    return prix_carte_cl[ex].get(code)

# --- 2. Bilan par PRODUIT ----------------------------------------------------
INV = {'haute': 3, 'moyenne': 2, 'basse': 1}
CONF_TXT = {3: 'haute', 2: 'moyenne', 1: 'basse'}
produits_res = []
for code, p in prod.items():
    if p.get('type') == 'materiel':   # verrerie/kits : conservés mais sans volume de boisson
        continue
    cont = p.get('contenanceCl')
    cat = p['categorie']
    pe = {}
    for ex in EX:
        b = p['parExercice'].get(ex, {})
        achat_cl = b.get('volCl', 0) or 0
        achat_qte = b.get('qte', 0) or 0
        pu = b.get('puMoyen')
        v_cl = round(vendu_cl[ex].get(code, 0.0), 1)
        if not cont:           # contenance inconnue -> bilan volume impossible
            pe[ex] = {'achatQte': achat_qte, 'achatCl': achat_cl, 'venduCl': v_cl,
                      'ecartCl': None, 'note': 'contenance inconnue'}
            continue
        ecart_cl = round(achat_cl - v_cl, 1)
        ecart_bt = round(ecart_cl / cont, 2)
        # coût par cl pris DIRECTEMENT du rapport HT/volume (exact pour bouteilles ET fûts)
        cout_cl = (b.get('ht', 0) / achat_cl) if achat_cl else None
        val_cout = round(ecart_cl * cout_cl, 2) if cout_cl is not None else None
        pvc = pvc_de(ex, code)   # prix de vente/cl DE CET EXERCICE (caisse, évolution des prix)
        val_vente = round(ecart_cl * pvc, 2) if pvc is not None else None
        pcc = pcc_de(ex, code)   # prix de vente/cl au TARIF CARTE de la période
        val_carte = round(ecart_cl * pcc, 2) if pcc is not None else None
        pe[ex] = {'achatQte': achat_qte, 'achatCl': achat_cl, 'venduCl': v_cl,
                  'ecartCl': ecart_cl, 'ecartBouteilles': ecart_bt,
                  'puAchatHT': pu, 'prixVenteParClTTC': round(pvc, 4) if pvc else None,
                  'prixCarteParClTTC': round(pcc, 4) if pcc else None,
                  'valEcartCoutHT': val_cout, 'valEcartVenteTTC': val_vente,
                  'valEcartVenteCarteTTC': val_carte}
    # total
    tot_achat_cl = sum((p['parExercice'].get(ex, {}).get('volCl', 0) or 0) for ex in EX)
    tot_vendu_cl = sum(vendu_cl[ex].get(code, 0.0) for ex in EX)
    t = {'achatCl': round(tot_achat_cl, 1), 'venduCl': round(tot_vendu_cl, 1)}
    tot_ht = sum((p['parExercice'].get(ex, {}).get('ht', 0) or 0) for ex in EX)
    if cont:
        t['ecartCl'] = round(tot_achat_cl - tot_vendu_cl, 1)
        t['ecartBouteilles'] = round(t['ecartCl'] / cont, 2)
        t['ecartPct'] = round(100 * t['ecartCl'] / tot_achat_cl, 1) if tot_achat_cl else None
        cout_cl_g = (tot_ht / tot_achat_cl) if tot_achat_cl else None
        t['valEcartCoutHT'] = round(t['ecartCl'] * cout_cl_g, 2) if cout_cl_g else None
        # total revente = somme des valorisations PAR EXERCICE (prix de chaque année)
        vv = [pe[ex].get('valEcartVenteTTC') for ex in EX if pe.get(ex, {}).get('valEcartVenteTTC') is not None]
        t['valEcartVenteTTC'] = round(sum(vv), 2) if vv else None
        vc = [pe[ex].get('valEcartVenteCarteTTC') for ex in EX if pe.get(ex, {}).get('valEcartVenteCarteTTC') is not None]
        t['valEcartVenteCarteTTC'] = round(sum(vc), 2) if vc else None
    produits_res.append({
        'code': code, 'libelle': p['libelle'], 'categorie': cat,
        'contenanceCl': cont, 'accise': p.get('accise', False),
        'aVenteCaisse': tot_vendu_cl > 0,
        'confiance': CONF_TXT[conf_code[code]] if tot_vendu_cl > 0 else None,
        'parExercice': pe, 'total': t,
    })

# --- 3. Agrégat par CATÉGORIE (robuste aux boutons génériques) --------------
BOIS = {'vin', 'macvin', 'cremant_petillant', 'biere', 'spiritueux_digestif', 'soft', 'jus', 'eau', 'sirop'}
cat_res = {}
for cat in sorted(BOIS):
    incat = [c for c in prod if prod[c]['categorie'] == cat and prod[c].get('type') != 'materiel']
    pe = {}
    for ex in EX:
        a_cl = sum((prod[c]['parExercice'].get(ex, {}).get('volCl', 0) or 0) for c in incat)
        v_cl = sum(vendu_cl[ex].get(c, 0.0) for c in incat)
        a_ht = sum((prod[c]['parExercice'].get(ex, {}).get('ht', 0) or 0) for c in incat)
        ecart = a_cl - v_cl
        # valorisation coût de l'écart catégorie : écart_cl × coût moyen par cl de la catégorie
        cout_cl = (a_ht / a_cl) if a_cl else None
        val_cout = round(ecart * cout_cl, 2) if cout_cl else None
        pe[ex] = {'achatCl': round(a_cl, 1), 'venduCl': round(v_cl, 1),
                  'ecartCl': round(ecart, 1),
                  'ecartPct': round(100 * ecart / a_cl, 1) if a_cl else None,
                  'achatHT': round(a_ht, 2), 'valEcartCoutHT': val_cout}
    tA = sum(pe[ex]['achatCl'] for ex in EX); tV = sum(pe[ex]['venduCl'] for ex in EX)
    tHT = sum(pe[ex]['achatHT'] for ex in EX)
    cat_res[cat] = {'parExercice': pe, 'total': {
        'achatCl': round(tA, 1), 'venduCl': round(tV, 1), 'ecartCl': round(tA - tV, 1),
        'ecartPct': round(100 * (tA - tV) / tA, 1) if tA else None,
        'achatHT': round(tHT, 2),
        'valEcartCoutHT': round((tA - tV) * (tHT / tA), 2) if tA else None}}

# --- 4. Totaux globaux -------------------------------------------------------
ca_vendu = {ex: round(ven['parExercice'][ex]['caLiquide10'] + ven['parExercice'][ex]['caLiquide20'], 2) for ex in EX}
achat_ht_bois = {ex: round(sum((prod[c]['parExercice'].get(ex, {}).get('ht', 0) or 0)
                               for c in prod if prod[c]['categorie'] in BOIS and prod[c].get('type') != 'materiel'), 2) for ex in EX}
val_cout_glob = {ex: round(sum(cat_res[cat]['parExercice'][ex]['valEcartCoutHT'] or 0 for cat in cat_res), 2) for ex in EX}

# Valorisation à la REVENTE (théorique) : somme des écarts produits valorisés au
# prix de vente observé — disponible seulement pour les produits servis purs.
val_vente_glob = round(sum((p['total'].get('valEcartVenteTTC') or 0) for p in produits_res), 2)
val_carte_glob = round(sum((p['total'].get('valEcartVenteCarteTTC') or 0) for p in produits_res), 2)
# Part de l'écart (en volume) effectivement couverte par un prix carte, pour la transparence.
ecart_cl_avec_carte = sum(p['total'].get('ecartCl', 0) for p in produits_res if p['total'].get('valEcartVenteCarteTTC') is not None and (p['total'].get('ecartCl') or 0) > 0)
ecart_cl_total = sum((p['total'].get('ecartCl') or 0) for p in produits_res if (p['total'].get('ecartCl') or 0) > 0)

glob = {
    'caVenduLiquideTTC': {**ca_vendu, 'total': round(sum(ca_vendu.values()), 2)},
    'achatBoissonsHT': {**achat_ht_bois, 'total': round(sum(achat_ht_bois.values()), 2)},
    'valDisparitionCoutHT': {**val_cout_glob, 'total': round(sum(val_cout_glob.values()), 2)},
    'valDisparitionVenteTTC_prixCaisse': val_vente_glob,
    'valDisparitionVenteTTC_tarifCarte': val_carte_glob,
    'couvertureTarifCartePctVolume': round(100 * ecart_cl_avec_carte / ecart_cl_total, 1) if ecart_cl_total else None,
    'couvertureCaissePct': {ex: round(100 * ca_couvert[ex] / ca_total[ex], 1) for ex in EX},
}

# Lignes matériel (verrerie/kits) : CONSERVÉES et documentées, volume de boisson nul.
materiel = [{'code': c, 'libelle': prod[c]['libelle'],
             'ht': round(sum((prod[c]['parExercice'].get(ex, {}).get('ht', 0) or 0) for ex in EX), 2)}
            for c in prod if prod[c].get('type') == 'materiel']
materiel_ht = round(sum(m['ht'] for m in materiel), 2)

caveats = [
    "BIÈRE PRESSION INCLUSE : le fût (212122 « FUT AFFLIGEM ») est bien le LIQUIDE — quantité facturée en LITRES (colis×8 L, ~3,59 €/L = ~28,72 €/fût). Volume = litres×100 cl (et non ×800). La consigne est hors lignes (totalFacture − totalTTC).",
    f"Aucune ligne exclue. {len(materiel)} lignes 'matériel' (verrerie/kits, {materiel_ht:.0f} € HT) conservées avec un volume de boisson nul (ce ne sont pas des liquides).",
    "Aucun inventaire : stock initial = stock final = 0 supposé. Un écart positif (acheté>vendu) peut être une constitution de stock, pas une disparition.",
    "Consommation du personnel, offerts, pertes, casse, usages cuisine NON déduits (paramètres de simulation à venir).",
    "Volume vendu attribué par dose/recette (doses de la carte). Confiance par produit : 'basse' = cocktail/recette estimée.",
    "Boutons caisse génériques (Sirop à l'eau, Jus de Fruit, Verre/Pichet de vin de base) : l'attribution par SKU est imparfaite → privilégier le bilan PAR CATÉGORIE.",
    f"Couverture : ~{int(sum(glob['couvertureCaissePct'].values())/3)}% du CA caisse liquide est attribué à un achat ; le reste = café/thé/expresso (hors fournisseur boissons) et libellés tronqués non identifiables.",
    "Valorisation au prix de vente : prix/cl observé en caisse, calculé PAR EXERCICE (reflète l'évolution des prix et les 3 cartes successives : carte 20/07/2021 pour 2022-2023, carte 26/04/2023 pour 2023-2025). Doses identiques sur les 3 cartes → volumes inchangés. Seuls les produits servis purs sont valorisés à la revente ; les ingrédients de cocktails au coût uniquement.",
    f"Valorisation à la REVENTE (théorique) = {val_vente_glob:,.0f} € TTC : borne HAUTE qui suppose tout le volume manquant vendu au prix carte. La borne BASSE, rigoureuse, est la valeur au COÛT d'achat ({glob['valDisparitionCoutHT']['total']:,.0f} € HT).".replace(',', ' '),
    "Chiffres PAR PRODUIT au sein d'un groupe de substituts (même vin/spiritueux servi sous un bouton unique, plusieurs millésimes/domaines) = RÉPARTITIONS indicatives ; seul le total PAR CATÉGORIE est robuste.",
]

out = {'genereDepuis': 'achats-exercice.json + ventes-caisse.json + map-*.json',
       'exercices': EX, 'global': glob, 'parCategorie': cat_res,
       'parProduit': sorted(produits_res, key=lambda x: -(x['total'].get('valEcartCoutHT') or -1e9)),
       'materiel': materiel, 'caveats': caveats}
json.dump(out, open(f'{DATA}/disparitions.json', 'w'), ensure_ascii=False, indent=1)

# --- 5. Rapport markdown -----------------------------------------------------
def e(x):
    return '—' if x is None else f"{x:,.0f} €".replace(',', ' ')
def cl(x):
    return '—' if x is None else f"{x/100:,.0f} L".replace(',', ' ')
def pct(x):
    return '—' if x is None else f"{x:.0f} %"

L = []
L.append('# Disparitions de boissons — calcul indépendant (hors fisc)\n')
L.append('> Croisement achats fournisseur ⇄ ventes caisse. Voir `00-METHODOLOGIE.md`. Généré par `scripts/boissons/02_disparitions.py`.\n')
L.append('## Vue d’ensemble (3 exercices)\n')
L.append('| Indicateur | 2022-2023 | 2023-2024 | 2024-2025 | Cumul |')
L.append('|---|--:|--:|--:|--:|')
L.append('| Achats boissons (HT) | ' + ' | '.join(e(glob['achatBoissonsHT'][x]) for x in EX) + ' | ' + e(glob['achatBoissonsHT']['total']) + ' |')
L.append('| CA boissons vendu (TTC, caisse) | ' + ' | '.join(e(glob['caVenduLiquideTTC'][x]) for x in EX) + ' | ' + e(glob['caVenduLiquideTTC']['total']) + ' |')
L.append('| **Disparitions au COÛT d’achat (HT) — borne basse** | ' + ' | '.join('**'+e(glob['valDisparitionCoutHT'][x])+'**' for x in EX) + ' | **' + e(glob['valDisparitionCoutHT']['total']) + '** |')
L.append('| Couverture du CA caisse attribuée | ' + ' | '.join(pct(glob['couvertureCaissePct'][x]) for x in EX) + ' |  |')
L.append('')
L.append(f"> **Disparitions valorisées à la REVENTE** (produits servis purs, par exercice) — au **prix encaissé caisse** : **{e(glob['valDisparitionVenteTTC_prixCaisse'])} TTC** ; au **tarif carte** de chaque période : **{e(glob['valDisparitionVenteTTC_tarifCarte'])} TTC** (couvre {glob['couvertureTarifCartePctVolume']} % du volume d’écart).")
L.append('> ⚠️ Bornes AVANT déduction de la consommation du personnel, des offerts, des pertes/casse, des usages cuisine et de l’inventaire (stock). Voir limites en bas.')
L.append('')
L.append('## Bilan par catégorie (volume acheté vs vendu, cumul 3 ans)\n')
L.append('| Catégorie | Acheté | Vendu (attribué) | Écart | Écart % | Disparition au coût HT |')
L.append('|---|--:|--:|--:|--:|--:|')
for cat in sorted(cat_res, key=lambda c: -(cat_res[c]['total']['valEcartCoutHT'] or -1e9)):
    t = cat_res[cat]['total']
    L.append(f"| {cat} | {cl(t['achatCl'])} | {cl(t['venduCl'])} | {cl(t['ecartCl'])} | {pct(t['ecartPct'])} | {e(t['valEcartCoutHT'])} |")
L.append('')
L.append('## Top produits par valeur de disparition (au coût HT, cumul)\n')
L.append('| Produit | Cat. | Conf. | Acheté | Vendu | Écart bout. | Coût HT | Vente TTC |')
L.append('|---|---|---|--:|--:|--:|--:|--:|')
for p in out['parProduit'][:30]:
    t = p['total']
    if t.get('valEcartCoutHT') is None:
        continue
    L.append(f"| {p['libelle'][:34]} | {p['categorie'][:6]} | {p['confiance'] or '—'} | "
             f"{cl(t['achatCl'])} | {cl(t['venduCl'])} | {t.get('ecartBouteilles','—')} | "
             f"{e(t.get('valEcartCoutHT'))} | {e(t.get('valEcartVenteTTC'))} |")
L.append('')
L.append('## Hypothèses & limites\n')
for c in caveats:
    L.append(f'- {c}')
L.append('')
open(f'{BASE}/RAPPORT-disparitions.md', 'w').write('\n'.join(L))

# --- 6. Résultats compacts pour le SITE (src/data) : chiffres exacts, reproductibles ---
SRC = os.path.join(ROOT, 'src', 'data')
resultats = {
    '_genere': 'scripts/boissons/02_disparitions.py — NE PAS éditer à la main',
    'exercices': EX,
    'achatsHT': glob['achatBoissonsHT'],
    'caVenduTTC': glob['caVenduLiquideTTC'],
    'caVenduLiquideParExercice': {ex: round(ven['parExercice'][ex]['caLiquide10'] + ven['parExercice'][ex]['caLiquide20'], 2) for ex in EX},
    'ecartCoutHT': glob['valDisparitionCoutHT'],
    'reventeCaisseTTC': glob['valDisparitionVenteTTC_prixCaisse'],
    'reventeCarteTTC': glob['valDisparitionVenteTTC_tarifCarte'],
    'couvertureCartePctVolume': glob['couvertureTarifCartePctVolume'],
    'couvertureCaissePct': glob['couvertureCaissePct'],
    'nbFactures': 199, 'nbLignesNonLivrees': None,
    'parCategorie': [
        {'categorie': cat,
         'achatL': round(cat_res[cat]['total']['achatCl'] / 100, 1),
         'venduL': round(cat_res[cat]['total']['venduCl'] / 100, 1),
         'ecartPct': cat_res[cat]['total']['ecartPct'],
         'ecartCoutHT': cat_res[cat]['total']['valEcartCoutHT']}
        for cat in sorted(cat_res, key=lambda c: -(cat_res[c]['total']['valEcartCoutHT'] or -1e9))
    ],
}
try:
    li = json.load(open(f'{DATA}/lignes-ignorees.json')); resultats['nbLignesNonLivrees'] = li.get('nb')
except Exception:
    pass
json.dump(resultats, open(os.path.join(SRC, 'boissons-resultats.json'), 'w'), ensure_ascii=False, indent=1)

# --- console ---
print('=== ÉTAPE 2 — DISPARITIONS ===')
for ex in EX:
    print(f"{ex}: achatHT={achat_ht_bois[ex]:.0f} | CAvendu={ca_vendu[ex]:.0f} | disparitionCoûtHT={val_cout_glob[ex]:.0f} | couverture={glob['couvertureCaissePct'][ex]}%")
print(f"CUMUL disparition au coût HT = {glob['valDisparitionCoutHT']['total']:.0f} €")
print('--- par catégorie (écart % cumul) ---')
for cat in sorted(cat_res, key=lambda c: -(cat_res[c]['total']['ecartPct'] or -1e9)):
    t = cat_res[cat]['total']
    print(f"  {cat:22} acheté={t['achatCl']/100:7.0f}L vendu={t['venduCl']/100:7.0f}L écart={t['ecartPct']}% coûtHT={t['valEcartCoutHT']}")
print('OK — disparitions.json + RAPPORT-disparitions.md')
