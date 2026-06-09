#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ÉTAPE 1 — Extraction des sources primaires (aucune donnée du fisc).
Produit 4 JSON dans analyses-independantes/boissons/data/ :
  achats-exercice.json, ventes-caisse.json, prix-carte.json, anomalies.json
Ré-exécutable : python3 scripts/boissons/01_extraction.py
"""
import json, os, re, glob
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA = os.path.join(ROOT, 'analyses-independantes', 'boissons', 'data')
os.makedirs(DATA, exist_ok=True)

EXERCICES = ['2022-2023', '2023-2024', '2024-2025']

def exercice_de(date_str):
    """'DD/MM/YYYY' -> 'AAAA-AAAA' (clôture 31/03) ou 'hors-periode'."""
    if not date_str:
        return 'hors-periode'
    m = re.match(r'(\d{2})/(\d{2})/(\d{4})', str(date_str))
    if not m:
        return 'hors-periode'
    d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
    # exercice qui commence le 01/04 : avril..decembre -> debut = y ; janv..mars -> debut = y-1
    debut = y if mo >= 4 else y - 1
    ex = f'{debut}-{debut+1}'
    return ex if ex in EXERCICES else 'hors-periode'

def num(v):
    try:
        if v is None or (isinstance(v, float) and pd.isna(v)):
            return 0.0
        return float(v)
    except Exception:
        return 0.0

# =============================================================================
# A) ACHATS re-ventilés par EXERCICE (depuis factures-fournisseur.json),
#    enrichis de la contenance/catégorie via achats-par-produit.json.
# =============================================================================
def extraction_achats():
    fact = json.load(open(os.path.join(ROOT, 'src/data/factures-fournisseur.json')))
    appj = json.load(open(os.path.join(ROOT, 'src/data/achats-par-produit.json')))
    meta = {p['code']: p for p in appj['produits']}  # code -> produit (libelle, categorie, contenanceCl, accise)

    def contenance_fallback(lib):
        """Déduit une contenance (cl) depuis le libellé d'achat si meta = None."""
        s = (lib or '').upper().replace(',', '.')
        m = re.search(r'(\d+(?:\.\d+)?)\s*CL', s)
        if m:
            return float(m.group(1))
        m = re.search(r'(\d+(?:\.\d+)?)\s*L\b', s)
        if m:
            return float(m.group(1)) * 100
        m = re.search(r'\b(\d{2})\.5\b', s)   # demi-bouteille "37.5"
        if m:
            return float(m.group(1)) + 0.5
        return None

    for code, p in meta.items():
        if p.get('contenanceCl') in (None, 0):
            p['contenanceCl'] = contenance_fallback(p.get('libelle'))

    def est_materiel(lib):
        """Ligne NON liquide (verrerie, kit, paille, bloc-notes, récup verre). On la
        CONSERVE (rien n'est exclu) ; son volume de boisson est simplement nul."""
        s = (lib or '').upper()
        return bool(re.match(r'^\s*(VERRES?\b|SOUS.?BOCK|KIT |NAPPE|SERVIETTE|PAILLES?\b|BLOCS? ?NOTES?|CAISSE RECUP|RECUP VERRE)', s))

    def est_fut(lib):
        """Fût de bière : la quantité facturée est en LITRES (colis × 8 L, facturée au
        litre). On NE multiplie donc PAS par la contenance du fût (800 cl) : 1 L = 100 cl.
        Vérifié sur facture : colis=3 fûts → qté=24 L → 3,59 €/L → 28,72 €/fût (prix réel)."""
        return bool(re.search(r'\bF[UÛ]TS?\b', (lib or '').upper()))

    prods = {}  # code -> dict
    ignorees = []  # lignes non facturées (marchandise manquante/refusée, déconsigne…)
    for f in fact['factures']:
        ex = exercice_de(f.get('dateFacture'))
        for li in f.get('lignes', []):
            code = li.get('code')
            if not code:
                continue
            ht_raw = li.get('montantHT')
            # Une ligne ne compte (volume ET coût) que si elle a été RÉELLEMENT facturée.
            # HT vide/0 = marchandise non reçue (M/SE MANQUANTE/REFUSÉE), déconsigne ou
            # échantillon → ne crée ni volume disponible ni coût. (Les avoirs HT<0 comptent.)
            if ht_raw is None or ht_raw == 0:
                ignorees.append({'code': code, 'designation': li.get('designation'),
                                 'conditionnement': li.get('conditionnement'),
                                 'quantite': li.get('quantite'), 'exercice': ex,
                                 'categorie': meta.get(code, {}).get('categorie', 'autre')})
                continue
            m = meta.get(code, {})
            lib = m.get('libelle') or li.get('designation')
            typ = 'materiel' if est_materiel(lib) else 'boisson'
            fut = est_fut(lib)
            p = prods.setdefault(code, {
                'code': code,
                'libelle': lib,
                'categorie': m.get('categorie', 'autre'),
                'contenanceCl': m.get('contenanceCl'),
                'type': typ,
                'estFut': fut,
                'parExercice': {},
            })
            qte = num(li.get('quantite'))
            ht = float(ht_raw)
            cont = p['contenanceCl']
            if typ == 'materiel':
                vol = 0.0                  # non-liquide : volume de boisson nul
            elif fut:
                vol = qte * 100.0          # quantité = litres → cl (1 L = 100 cl)
            else:
                vol = (qte * cont) if cont else 0.0
            b = p['parExercice'].setdefault(ex, {'qte': 0.0, 'volCl': 0.0, 'ht': 0.0, 'nbLignes': 0})
            b['qte'] += qte
            b['volCl'] += vol
            b['ht'] += ht
            b['nbLignes'] += 1

    # totaux + pu moyen
    for p in prods.values():
        tot = {'qte': 0.0, 'volCl': 0.0, 'ht': 0.0, 'nbLignes': 0}
        for ex, b in p['parExercice'].items():
            b['puMoyen'] = round(b['ht'] / b['qte'], 4) if b['qte'] else None
            for k in tot:
                tot[k] += b[k]
            for k in ('qte', 'volCl', 'ht'):
                b[k] = round(b[k], 2)
        tot['puMoyen'] = round(tot['ht'] / tot['qte'], 4) if tot['qte'] else None
        for k in ('qte', 'volCl', 'ht'):
            tot[k] = round(tot[k], 2)
        p['total'] = tot

    out = {'genereDepuis': 'factures-fournisseur.json + achats-par-produit.json',
           'exercices': EXERCICES, 'nbProduits': len(prods),
           'lignesIgnorees': len(ignorees),
           'produits': sorted(prods.values(), key=lambda x: -x['total']['ht'])}
    json.dump(out, open(os.path.join(DATA, 'achats-exercice.json'), 'w'), ensure_ascii=False, indent=1)
    # Lignes ignorées (non facturées) : trace + preuve « facturé non livré / refusé ».
    json.dump({'nb': len(ignorees), 'note': 'Lignes de facture à HT vide/0 : marchandise manquante/refusée, déconsigne ou échantillon — non comptées en volume ni en coût.',
               'lignes': ignorees}, open(os.path.join(DATA, 'lignes-ignorees.json'), 'w'), ensure_ascii=False, indent=1)
    # sanity : exercice + hors vs total calendaire de achats-par-produit
    tot_ex = sum(b['ht'] for p in prods.values() for ex, b in p['parExercice'].items() if ex in EXERCICES)
    tot_hors = sum(b['ht'] for p in prods.values() for ex, b in p['parExercice'].items() if ex == 'hors-periode')
    tot_cal = sum(p['total']['montantHT'] for p in appj['produits'])
    print(f"[ACHATS] {len(prods)} produits | HT exercices={tot_ex:.0f} + hors-periode={tot_hors:.0f} = {tot_ex+tot_hors:.0f} (calendaire app.json={tot_cal:.0f}) | lignes ignorées={len(ignorees)}")
    return out

# =============================================================================
# B) VENTES caisse par produit / exercice (annexes D1/D2/D3).
# =============================================================================
def contenance_depuis_lib(lib):
    """Déduit une contenance (cl) depuis un libellé caisse, si explicite."""
    s = (lib or '').lower().replace(',', '.')
    m = re.search(r'(\d+(?:\.\d+)?)\s*cl', s)
    if m:
        return float(m.group(1))
    if 'litre' in s or re.search(r'\b1\s*l\b', s) or '100cl' in s:
        return 100.0
    m = re.search(r'(\d+(?:\.\d+)?)\s*l\b', s)
    if m:
        return float(m.group(1)) * 100
    return None

def extraction_ventes():
    res = {'genereDepuis': 'ANNEXE-D{1,2,3}', 'exercices': EXERCICES, 'parExercice': {}}
    totaux_ca = {}
    for i, ex in enumerate(EXERCICES, start=1):
        path = glob.glob(os.path.join(ROOT, f'public/documents/caisse-enregistreuse/ANNEXE-D{i}_*'))[0]
        df = pd.ExcelFile(path).parse(0, header=None)
        tva = None          # '10' | '20' | 'solide' | None
        sous = None
        last_ref = None     # report de la réf. pour les lignes-prix de continuation (réf. vide)
        prods = {}          # ref -> agg
        totals_section = {}
        for _, row in df.iterrows():
            c0, c1, c2, c3, c4, c5 = [row.get(j) for j in range(6)]
            s0 = '' if pd.isna(c0) else str(c0).strip().replace('\xa0', ' ')
            is_section = s0 and pd.isna(c2) and pd.isna(c4)
            if is_section:
                up = s0.upper()
                if up.startswith('TOTAL'):
                    totals_section[s0] = num(c2) or num(c3) or num(c4) or num(c5)
                    continue
                if 'LIQUIDE' in up and 'TVA 10' in up:
                    tva, sous, last_ref = '10', None, None; continue
                if 'LIQUIDE' in up and 'TVA 20' in up:
                    tva, sous, last_ref = '20', None, None; continue
                if 'SOLIDE' in up:
                    tva, sous, last_ref = 'solide', None, None; continue
                sous, last_ref = s0.rstrip(' :'), None   # sous-categorie
                continue
            if s0 == 'Ref_prd':
                continue
            if tva not in ('10', '20'):   # on ignore les solides
                continue
            # Réf. présente = nouveau produit ; réf. vide = ligne-prix de continuation
            # du produit précédent (NE PAS ignorer : elle porte une qté/CA réels).
            if s0:
                ref = s0
                last_ref = s0
            else:
                if last_ref is None or (pd.isna(c2) and pd.isna(c4) and pd.isna(c5)):
                    continue
                ref = last_ref
            lib = '' if pd.isna(c1) else str(c1).strip()
            uprice = num(c2)
            prixmoy = c3 if (c3 is not None and not pd.isna(c3)) else None
            qte = num(c4)
            ca = num(c5)
            p = prods.setdefault(ref, {
                'ref': ref, 'libelle': lib, 'tva': tva, 'sousCategorie': sous,
                'qte': 0.0, 'caTtc': 0.0, 'prixMoyen': None, 'prixDistincts': [],
                'contenanceCl': contenance_depuis_lib(lib),
            })
            p['qte'] += qte
            p['caTtc'] += ca
            if prixmoy is not None and p['prixMoyen'] is None:
                p['prixMoyen'] = round(float(prixmoy), 4)
            if uprice and uprice not in p['prixDistincts']:
                p['prixDistincts'].append(uprice)
        for p in prods.values():
            p['qte'] = round(p['qte'], 2)
            p['caTtc'] = round(p['caTtc'], 2)
            if p['prixMoyen'] is None and p['qte']:
                p['prixMoyen'] = round(p['caTtc'] / p['qte'], 4)
            p['prixDistincts'] = sorted(p['prixDistincts'])
        res['parExercice'][ex] = {
            'nbProduits': len(prods),
            'caLiquide10': round(sum(p['caTtc'] for p in prods.values() if p['tva'] == '10'), 2),
            'caLiquide20': round(sum(p['caTtc'] for p in prods.values() if p['tva'] == '20'), 2),
            'totauxFichier': totals_section,
            'produits': sorted(prods.values(), key=lambda x: -x['caTtc']),
        }
        totaux_ca[ex] = res['parExercice'][ex]
        print(f"[VENTES] {ex}: {len(prods)} produits liquides | CA10={res['parExercice'][ex]['caLiquide10']:.0f} CA20={res['parExercice'][ex]['caLiquide20']:.0f}")
    json.dump(res, open(os.path.join(DATA, 'ventes-caisse.json'), 'w'), ensure_ascii=False, indent=1)
    return res

# =============================================================================
# C) CARTE : prix de vente + dose (cl) par boisson (3 versions).
# =============================================================================
def dose_cl(q):
    s = (str(q) if q is not None else '').lower().replace(',', '.')
    m = re.search(r'(\d+(?:\.\d+)?)\s*cl', s)
    if m:
        return float(m.group(1))
    m = re.search(r'(\d+(?:\.\d+)?)\s*l\b', s)
    if m:
        return float(m.group(1)) * 100
    return None

def extraction_carte():
    versions = []
    for path in sorted(glob.glob(os.path.join(ROOT, 'public/documents/vins-boissons/carte_*.xls'))):
        df = pd.ExcelFile(path).parse(0, header=0)
        items = []
        for _, r in df.iterrows():
            titre = r.get('Titre')
            if titre is None or (isinstance(titre, float) and pd.isna(titre)):
                continue
            q = r.get('Quantité')
            prix = r.get('Prix')
            items.append({
                'titre': str(titre).strip(),
                'description': None if pd.isna(r.get('Description')) else str(r.get('Description')).strip(),
                'doseRaw': None if (q is None or pd.isna(q)) else str(q).strip(),
                'doseCl': dose_cl(q),
                'prix': None if (prix is None or pd.isna(prix)) else round(float(prix), 2),
            })
        versions.append({'fichier': os.path.basename(path), 'nbItems': len(items), 'items': items})
        print(f"[CARTE] {os.path.basename(path)}: {len(items)} items")
    json.dump({'genereDepuis': 'carte_*.xls', 'versions': versions},
              open(os.path.join(DATA, 'prix-carte.json'), 'w'), ensure_ascii=False, indent=1)
    return versions

# =============================================================================
# D) ANOMALIES du carnet manuscrit (qté + statut).
# =============================================================================
def parse_qte_texte(t):
    """'1 carton de 24' -> (24,'carton'); '2 fûts' -> (2,'fût'); '1 x 12' -> (12,'unite'); '6 b' -> (6,'bouteille')."""
    s = (str(t) if t is not None else '').lower().replace(',', '.')
    mult = re.search(r'(\d+)\s*(?:cartons?|caisses?|x|\*)\s*(?:de\s*)?(\d+)', s)
    if mult:
        return float(int(mult.group(1)) * int(mult.group(2))), 'carton'
    m = re.search(r'(\d+(?:\.\d+)?)', s)
    n = float(m.group(1)) if m else None
    unite = 'unite'
    if 'fût' in s or 'fut' in s:
        unite = 'fût'
    elif re.search(r'\bb\b', s) or 'bouteille' in s:
        unite = 'bouteille'
    elif 'carton' in s or 'caisse' in s:
        unite = 'carton'
    return n, unite

def extraction_anomalies():
    path = os.path.join(ROOT, 'public/documents/vins-boissons/analyse-manuscrite/analyse-manuscrite-boissons.xls')
    df = pd.ExcelFile(path).parse(0, header=0)
    lignes, par_statut = [], {}
    for _, r in df.iterrows():
        art = r.get('Article')
        if art is None or (isinstance(art, float) and pd.isna(art)):
            continue
        qn, unite = parse_qte_texte(r.get('Quantité'))
        statut = None if pd.isna(r.get('Statut')) else str(r.get('Statut')).strip()
        lignes.append({
            'page': None if pd.isna(r.get('Page (photo)')) else str(r.get('Page (photo)')),
            'mois': None if pd.isna(r.get('Mois')) else str(r.get('Mois')),
            'date': None if pd.isna(r.get('Date')) else str(r.get('Date')),
            'quantiteTexte': None if pd.isna(r.get('Quantité')) else str(r.get('Quantité')).strip(),
            'quantiteNum': qn, 'unite': unite,
            'article': str(art).strip(),
            'statut': statut,
            'incertain': not pd.isna(r.get('Incertain')),
        })
        par_statut[statut] = par_statut.get(statut, 0) + 1
    json.dump({'genereDepuis': 'analyse-manuscrite-boissons.xls',
               'nbLignes': len(lignes), 'parStatut': par_statut, 'lignes': lignes},
              open(os.path.join(DATA, 'anomalies.json'), 'w'), ensure_ascii=False, indent=1)
    print(f"[ANOMALIES] {len(lignes)} lignes | par statut: {par_statut}")

if __name__ == '__main__':
    print('=== ÉTAPE 1 — EXTRACTION ===')
    extraction_achats()
    extraction_ventes()
    extraction_carte()
    extraction_anomalies()
    print('OK — JSON écrits dans analyses-independantes/boissons/data/')
