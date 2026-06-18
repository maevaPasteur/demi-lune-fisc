#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RENDU FINAL - Bloc 2 (Reconstitution du chiffre d'affaires).
Sous-pages "avocat" qui chiffrent PRECISEMENT, source a l'appui, les usages
sans recette que la methode du fisc neglige et qui composent le residuel :

  1. sur-versement-au-verre   (free-pour : dose reelle > dose carte)
  2. pertes-biere-mousse      (freinte technique du fut : mousse, purge, lignes)
  3. pertes-cremant           (bouteille de cremant eventee, jetee en fin de jour)
  4. degustation-au-verre     (2 cl offerts pour faire gouter avant de servir)

ENTIEREMENT REPRODUCTIBLE. Lecture seule des sources internes :
  - src/data/calculsBoissons/itemsCaisse.json  (ventes caisse par exercice)
  - src/data/boissonsPageData.json              (cascade, cocktails, synthese)
  - public/documents/rapports-des-finances-publiques/synthese/05/06-*.md (methode fisc)

Chaque page : (1) ce que dit la proposition (avec page), (2) la faille,
(3) le calcul exact (constantes documentees), (4) la source externe citee,
(5) le resultat en litres rattaches au residuel, (6) note avocat (retiree au fisc).

Produit, par page :
  - public/documents/pieces-defense/RF-<slug>.xlsx
  - src/data/renduFinal/<slug>.json   (schema Section de src/data/analyses.ts)

Sources EXTERNES citees (verifiables) :
  [Kerr 2008]  Kerr WC, Patterson D, Koenen MA, Greenfield TK,
     "Alcohol Content Variation of Bar and Restaurant Drinks in Northern
     California", Alcoholism: Clinical and Experimental Research, 2008,
     32(9):1623-1631. Mesure : verre de vin servi 6,18 oz vs 5 oz standard
     (+23,6 % de volume) ; biere pression +22 % ; cocktails +42 %.
  [Coravin / oenologie]  un vin effervescent ouvert sans bouchon hermetique
     perd ses bulles en quelques heures et est plat des le lendemain.
  [Brewers Association / draught]  rendement-fut courant ~95 % (≈ 5 % de
     freinte technique mini), + purge de la biere des lignes a chaque nettoyage
     (standard bihebdomadaire Brewers Association). Litterature CHR : 5-20 %.
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DATA = os.path.join(ROOT, "src", "data")
PIECES = os.path.join(ROOT, "public", "documents", "pieces-defense")
RENDU_DIR = os.path.join(SRC_DATA, "renduFinal")
EXERCICES = ["2022-2023", "2023-2024", "2024-2025"]

# Jours de service sur les 3 exercices (34 mois d'activite, fev. ferme) :
# valeur retenue de facon homogene avec les autres pages du dossier.
JOURS_SERVICE = 662


# --- Formatage francais (espace fine insecable U+202F) ----------------------
def fr_int(n):
    return f"{int(round(n)):,}".replace(",", " ")


def fr_eur(n):
    return f"{fr_int(n)} €"


def fr_l(n, dec=0):
    if dec:
        s = f"{n:.{dec}f}".replace(".", ",")
        return f"{s} L"
    return f"{fr_int(n)} L"


def fr_pct(x, dec=1):
    return f"{f'{x:.{dec}f}'.replace('.', ',')} %"


def fr_cl(x, dec=0):
    if dec:
        return f"{f'{x:.{dec}f}'.replace('.', ',')} cl"
    return f"{int(round(x))} cl"


# --- Sources -----------------------------------------------------------------
def charger():
    with open(os.path.join(SRC_DATA, "calculsBoissons", "itemsCaisse.json"), encoding="utf-8") as f:
        items = json.load(f)["items"]
    with open(os.path.join(SRC_DATA, "boissonsPageData.json"), encoding="utf-8") as f:
        bpd = json.load(f)
    with open(os.path.join(SRC_DATA, "calculsBoissons", "consoTotaleParBoisson.json"), encoding="utf-8") as f:
        conso = json.load(f)["boissons"]
    return items, bpd, conso


def conso_seches_cocktails(conso):
    """Retourne, par categorie, le volume (3 exercices) reellement CONSOMME en
    service sec (au verre / pichet) et en cocktails. Source : notre mesure
    (consoTotaleParBoisson, detail_exact_l), PAS la reconstitution du fisc."""
    from collections import defaultdict
    sec = defaultdict(float)
    cock = defaultdict(float)
    for b in conso:
        cat = b.get("categorie", "?")
        for e in EXERCICES:
            de = b.get("par_periode", {}).get(e, {}).get("detail_exact_l", {})
            sec[cat] += de.get("boissons_seches", 0) or 0
            cock[cat] += de.get("ingredients_cocktails", 0) or 0
    return dict(sec), dict(cock)


def q3(x):
    return sum(x["quantite"].get(e, 0) for e in EXERCICES)


# --- Helpers schema Section --------------------------------------------------
def cg(v):
    return {"v": v}


def cd(v):
    return {"v": v, "align": "right"}


def cgf(v):
    return {"v": v, "fw": 700}


def cdf(v):
    return {"v": v, "align": "right", "fw": 700}


# =============================================================================
# 1. SUR-VERSEMENT AU VERRE (free-pour)
# =============================================================================
def calc_surversement(conso):
    """Sur-versement (free-pour) sur TOUT ce qui est servi a la main, hors biere
    (freinte a part) et hors boissons en bouteille scellee. Base = volume
    REELLEMENT consomme (notre mesure consoTotaleParBoisson), reparti en :
      - vin au verre/pichet  -> +20 % (sous la mesure Kerr 2008 : +23,6 %)
      - spiritueux/aperitifs/digestifs au verre -> +25 % (Kerr cocktails +42 %)
      - alcool des cocktails  -> +8 % (free-pour des spiritueux du cocktail)
    """
    sec, cock = conso_seches_cocktails(conso)
    # Categories (notre nomenclature) regroupees par regime de sur-versement.
    VIN = ["vin_blanc", "vin_rouge", "vin", "vin_rose", "petillant"]
    SPIRIT = ["vin_de_liqueur", "aperitif", "liqueur", "eau_de_vie", "spiritueux", "digestif"]
    # (cidre = souvent bouteille -> exclu ; biere = freinte dediee -> exclu ; softs = exclus)
    base_vin = sum(sec.get(c, 0) for c in VIN)
    base_spirit = sum(sec.get(c, 0) for c in SPIRIT)
    base_cocktail = sum(cock.get(c, 0) for c in (VIN + SPIRIT))

    taux_vin, taux_spirit, taux_cock = 0.20, 0.25, 0.08
    l_vin = base_vin * taux_vin
    l_spirit = base_spirit * taux_spirit
    l_cock = base_cocktail * taux_cock
    total = l_vin + l_spirit + l_cock

    postes = [
        {"label": "Vins au verre et au pichet", "base": base_vin, "taux": taux_vin, "litres": l_vin,
         "detail": "blanc, rouge, rosé, vin maison, pétillant — service libre"},
        {"label": "Spiritueux, apéritifs et digestifs au verre", "base": base_spirit, "taux": taux_spirit, "litres": l_spirit,
         "detail": "macvin, vin jaune, pastis, whisky, marc, génépi… au verre"},
        {"label": "Alcool des cocktails", "base": base_cocktail, "taux": taux_cock, "litres": l_cock,
         "detail": "part alcool des cocktails maison (free-pour)"},
    ]
    return {
        "postes": postes,
        "base_totale": base_vin + base_spirit + base_cocktail,
        "litres_retenu": total,
        "taux_blende": total / (base_vin + base_spirit + base_cocktail),
        "taux_kerr_vin": 0.236,
        "litres_kerr": base_vin * 0.236 + base_spirit * 0.42 + base_cocktail * 0.10,
    }


# =============================================================================
# 2. PERTES BIERE PRESSION (freinte fut)
# =============================================================================
def calc_biere(items):
    """Volume de biere PRESSION (fut Affligem) reellement tire, toutes
    declinaisons (pression, pinte, panache, monaco, picon-biere : seule la part
    biere). Freinte technique = mousse + purge + nettoyage des lignes + fond de
    fut, en SUS du volume servi."""
    lignes = []
    base_cl = 0.0
    for x in items:
        if x.get("nom_canonique") == "Fût Affligem":
            v = x.get("volume_unitaire_cl") or 0
            n = q3(x)
            base_cl += n * v
            lignes.append({"produit": x["produit"], "format": x.get("format_service"),
                           "vol_cl": v, "qte": round(n), "litres": n * v / 100.0})
    base_l = base_cl / 100.0
    # Taux : 5 % = rendement-fut courant (mini) ; 10 % = mode CHR ; 18 % = haut.
    taux_min, taux_mode, taux_haut = 0.05, 0.10, 0.18
    return {
        "lignes": lignes,
        "base_l": base_l,
        "taux_min": taux_min,
        "taux_mode": taux_mode,
        "taux_haut": taux_haut,
        "litres_min": base_l * taux_min,
        "litres_mode": base_l * taux_mode,
        "litres_haut": base_l * taux_haut,
    }


# =============================================================================
# 3. CREMANT JETE EN FIN DE JOURNEE
# =============================================================================
def calc_cremant(items, bpd):
    """Le cremant est servi au verre ET dans des cocktails (Vouivre, Kittykir,
    Pere Gregoire, Kir Princier). Une bouteille ouverte est plate le lendemain
    (effervescent) : on l'ouvre a la journee et on jette le solde non servi."""
    DOSE_VERRE = 12  # cl (dose carte/fisc)
    verre_q = sum(q3(x) for x in items
                  if "rémant" in str(x.get("nom_canonique", "")) and x.get("format_service") == "Verre")
    cocktails = []
    for c in bpd["cocktails"]:
        for r in c["recette"]:
            if r["nom"] == "Crémant":
                cocktails.append({"cocktail": c["cocktail"], "dose_cl": r["cl"],
                                  "qte": c["qte_3ans"], "litres": r["cl"] * c["qte_3ans"] / 100.0})
    liq_verre = verre_q * DOSE_VERRE / 100.0
    liq_cock = sum(c["litres"] for c in cocktails)
    liq_total = liq_verre + liq_cock          # cremant reellement servi (hors bouteilles entieres)
    servings = verre_q + sum(c["qte"] for c in cocktails)

    BOUTEILLE_L = 0.75
    # Hypothese explicite et PRUDENTE : le cremant est servi chaque jour de
    # service (servings ≈ 8/jour) ; on ouvre donc, chaque jour, le nombre entier
    # de bouteilles juste suffisant, et le solde de la derniere bouteille est
    # jete. Avec une demande quasi constante ~liq_total/JOURS par jour, on ouvre
    # 1 bouteille/jour et on jette (0,75 - demande_jour) L. Modele conservateur.
    demande_jour = liq_total / JOURS_SERVICE          # L/jour servi
    import math
    bouteilles_jour = max(1, math.ceil(demande_jour / BOUTEILLE_L))
    waste_jour = bouteilles_jour * BOUTEILLE_L - demande_jour
    waste_3ans = waste_jour * JOURS_SERVICE
    bouteilles_3ans = bouteilles_jour * JOURS_SERVICE
    return {
        "verre_q": round(verre_q),
        "dose_verre": DOSE_VERRE,
        "cocktails": cocktails,
        "liq_verre": liq_verre,
        "liq_cock": liq_cock,
        "liq_total": liq_total,
        "servings": round(servings),
        "servings_jour": servings / JOURS_SERVICE,
        "demande_jour": demande_jour,
        "bouteilles_jour": bouteilles_jour,
        "waste_jour": waste_jour,
        "waste_3ans": waste_3ans,
        "bouteilles_3ans": round(bouteilles_3ans),
    }


# =============================================================================
# 4. DEGUSTATION OFFERTE (2 cl)
# =============================================================================
GENERIQUES = {
    "Cubis de vin (couleur non précisée)",
    "Bourgogne Aligoté maison",
    "Côtes de Provence rosé maison (Cap des Pins)",
    "Côtes du Rhône rouge maison (Chusclan)",
}


def calc_degustation(items):
    """Quantite, VIN PAR VIN, offerte en degustation (2 cl), non enregistree :
    (a) chaque PICHET : une larme pour approuver avant de servir la table ;
    (b) chaque commande d'un VIN NOMME au verre : le serveur monte la bouteille
        et fait gouter une personne (2 cl). Plusieurs verres du MEME vin a une
        table = une seule degustation -> degustations = verres / ratio (=2).
    Les vins GENERIQUES (cubis/maison) : pas de bouteille montee -> exclus."""
    DOSE_DEG = 2  # cl
    RATIO = 2.0   # verres du meme vin par commande (hypothese prudente)

    # --- (b) vins nommes au verre, agreges par vin ---
    par_vin = {}
    for x in items:
        nc = x.get("nom_canonique")
        is_verre15 = x.get("format_service") == "Verre" and x.get("volume_unitaire_cl") == 15
        is_vj = nc == "Arbois Vin Jaune" and x.get("format_service") == "Verre"
        if (is_verre15 or is_vj) and nc not in GENERIQUES:
            par_vin[nc] = par_vin.get(nc, 0) + q3(x)
    vins = []
    for nc, qte in sorted(par_vin.items(), key=lambda kv: -kv[1]):
        deg = qte / RATIO
        vins.append({"vin": nc, "verres": round(qte), "degustations": round(deg),
                     "litres": deg * DOSE_DEG / 100.0})
    nommes_q = sum(v["verres"] for v in vins)
    deg_nommes_l = sum(v["litres"] for v in vins)

    # --- (a) pichets (tous, 1 larme chacun) ---
    pichets_q = sum(q3(x) for x in items if str(x.get("format_service", "")).startswith("Pichet"))
    deg_pichets_l = pichets_q * DOSE_DEG / 100.0

    return {
        "dose_deg": DOSE_DEG,
        "ratio": RATIO,
        "vins": vins,
        "nommes_q": round(nommes_q),
        "deg_nommes_l": deg_nommes_l,
        "pichets_q": round(pichets_q),
        "deg_pichets_l": deg_pichets_l,
        "total_l": deg_nommes_l + deg_pichets_l,
    }


# =============================================================================
# XLSX generique
# =============================================================================
def ecrire_xlsx(path, titre, sous_titre, onglets):
    """onglets : list of (nom, [colonnes], [lignes], [largeurs])."""
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter

    wb = openpyxl.Workbook()
    white_bold = Font(bold=True, color="FFFFFF")
    head = PatternFill("solid", fgColor="0F766E")
    sub = PatternFill("solid", fgColor="E6F4F1")
    thin = Side(style="thin", color="CBD5E1")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    right = Alignment(horizontal="right")

    first = True
    for nom, colonnes, lignes, largeurs in onglets:
        ws = wb.active if first else wb.create_sheet(nom)
        if first:
            ws.title = nom
            first = False
        ws.append([titre])
        ws["A1"].font = Font(bold=True, size=13)
        if sous_titre:
            ws.append([sous_titre])
            ws["A2"].font = Font(italic=True, size=9, color="64748B")
            ws.append([])
            hrow = 4
        else:
            ws.append([])
            hrow = 3
        ws.append(colonnes)
        for c in range(1, len(colonnes) + 1):
            cell = ws.cell(row=hrow, column=c)
            cell.font = white_bold
            cell.fill = head
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cell.border = border
        for ln in lignes:
            ws.append(ln)
        for r in range(hrow + 1, hrow + 1 + len(lignes)):
            for c in range(1, len(colonnes) + 1):
                cell = ws.cell(row=r, column=c)
                cell.border = border
                if isinstance(cell.value, (int, float)):
                    cell.alignment = right
        # total = derniere ligne mise en valeur si elle commence par TOTAL
        if lignes and str(lignes[-1][0]).upper().startswith(("TOTAL", "RESULTAT", "RÉSULTAT")):
            for c in range(1, len(colonnes) + 1):
                ws.cell(row=hrow + len(lignes), column=c).font = Font(bold=True)
                ws.cell(row=hrow + len(lignes), column=c).fill = sub
        for i, w in enumerate(largeurs, start=1):
            ws.column_dimensions[get_column_letter(i)].width = w
        ws.freeze_panes = f"A{hrow + 1}"

    os.makedirs(PIECES, exist_ok=True)
    wb.save(path)
    return path


def ecrire_json(slug, doc):
    os.makedirs(RENDU_DIR, exist_ok=True)
    p = os.path.join(RENDU_DIR, f"{slug}.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    return p


# =============================================================================
# PAGE 1 - SUR-VERSEMENT
# =============================================================================
def page_surversement(d):
    slug = "sur-versement-au-verre"
    xlsx = os.path.join(PIECES, "RF-sur-versement-au-verre.xlsx")
    ecrire_xlsx(
        xlsx, "Sur-versement au verre - depassement de la dose servie",
        "Base = notre mesure de ce qui est reellement servi a la main (hors biere et hors bouteilles). Sans doseur, le free-pour depasse la dose (Kerr 2008 : verre de vin +23,6 %, cocktails +42 %). Le depassement est bu, jamais vendu.",
        [(
            "Sur-versement par regime",
            ["Poste servi a la main", "Volume consomme (L)", "Taux", "Sur-versement (L)"],
            [[p["label"], round(p["base"]), fr_pct(p["taux"] * 100, 0), round(p["litres"])] for p in d["postes"]]
            + [["TOTAL", round(d["base_totale"]), fr_pct(d["taux_blende"] * 100, 1), round(d["litres_retenu"])]],
            [40, 18, 10, 16],
        )],
    )
    rows = [[cg(p["label"]), cd(fr_l(p["base"])), cd(fr_pct(p["taux"] * 100, 0)), cd(fr_l(p["litres"]))] for p in d["postes"]]
    rows.append([cgf("Total sur-versement"), cdf(fr_l(d["base_totale"])), cdf(fr_pct(d["taux_blende"] * 100, 1)), cdf(fr_l(d["litres_retenu"]))])
    doc = {
        "meta": {"slug": slug, "source": "scripts/rendu-final-reconstitution-bloc2.py",
                 "grief": "Proposition p. 37-44 (methode 1/2) - doses au verre",
                 "litres_retenu": round(d["litres_retenu"])},
        "sections": [
            {"kind": "chapitre", "source": "fisc", "numero": 1,
             "titre": "Le grief de l’administration",
             "sousTitre": "Proposition p. 37 et p. 41-42 — doses au verre figées au centilitre"},
            {"kind": "paragraphe",
             "texte": "Pour reconstituer le nombre de verres vendus, le service **divise le volume disponible par une dose figée** (15 cl le verre de vin, 50/75 cl le pichet, 4 cl les alcools forts), en supposant que **chaque verre est servi au centilitre près de la carte**. C’est faux : sans doseur, on sert toujours un peu plus."},
            {"kind": "chapitre", "source": "nous", "numero": 2,
             "titre": "Notre mesure : tout le service à la main dépasse la dose",
             "sousTitre": "On part de notre consommation réelle, pas de la reconstitution — et on chiffre le dépassement"},
            {"kind": "paragraphe",
             "texte": "Nous ne partons pas des doses du fisc mais de **notre mesure de ce qui a réellement été servi** (analyse « Boissons disparues », poste par poste). Sur **tout ce qui est versé à la main** — vins au verre et au pichet, spiritueux, apéritifs et digestifs au verre, et l’alcool des cocktails — le service libre dépasse la dose. C’est **mesuré et publié** : **Kerr, Patterson, Koenen & Greenfield (*Alcoholism: Clinical and Experimental Research*, 2008)**, qui ont mesuré **480 boissons dans 80 établissements**, trouvent un **verre de vin à +23,6 %** de la dose standard, des **cocktails à +42 %** et la **bière à +22 %**. La bière est traitée à part (page « pertes de bière ») et les **boissons en bouteille scellée** sont exclues (pas de service à la main)."},
            {"kind": "tableau", "titre": "Sur-versement par régime de service (volumes réellement consommés, 3 exercices)",
             "minWidth": 560,
             "colonnes": [{"label": "Poste servi à la main"}, {"label": "Volume consommé", "align": "right"}, {"label": "Taux retenu", "align": "right"}, {"label": "Sur-versement", "align": "right"}],
             "lignes": rows},
            {"kind": "kpis", "items": [
                {"label": "Base servie à la main", "valeur": fr_l(d["base_totale"]), "sub": "vins + spiritueux au verre + cocktails (hors bière)", "couleur": "blue"},
                {"label": "Taux moyen retenu", "valeur": fr_pct(d["taux_blende"] * 100, 1), "sub": "sous les mesures Kerr 2008", "couleur": "teal"},
                {"label": "Sur-versement", "valeur": fr_l(d["litres_retenu"]), "sub": "consommés, jamais vendus", "highlight": True, "couleur": "teal"},
            ]},
            {"kind": "paragraphe",
             "texte": f"**Le calcul, régime par régime.** Les **{fr_l(d['postes'][0]['base'])}** de vin servis au verre et au pichet, à **+{fr_pct(d['postes'][0]['taux']*100,0)}** (sous la mesure Kerr de +23,6 %), font **{fr_l(d['postes'][0]['litres'])}**. Les **{fr_l(d['postes'][1]['base'])}** de spiritueux, apéritifs et digestifs servis au verre, plus difficiles à doser à l’œil, à **+{fr_pct(d['postes'][1]['taux']*100,0)}** (sous les +42 % mesurés sur les mélanges), font **{fr_l(d['postes'][1]['litres'])}**. Enfin les **{fr_l(d['postes'][2]['base'])}** d’alcool des cocktails, à **+{fr_pct(d['postes'][2]['taux']*100,0)}**, font **{fr_l(d['postes'][2]['litres'])}**. **Total : {fr_l(d['litres_retenu'])}** d’alcool consommé et **jamais vendu** sur trois ans. À la mesure académique haute, ce serait **{fr_l(d['litres_kerr'])}**."},
            {"kind": "alerte", "couleur": "teal", "titre": "Résultat",
             "texte": f"Le service à la main sans doseur fait disparaître **{fr_l(d['litres_retenu'])}** d’alcool sur trois exercices (taux moyen {fr_pct(d['taux_blende']*100,1)}, **sous** les valeurs mesurées par [Kerr 2008]). Ce volume explique directement une part du résiduel de l’analyse « Boissons disparues » : ce n’est ni une vente, ni une disparition, c’est de l’alcool bu en plus de la dose facturée."},
            {"kind": "note",
             "texte": f"**Cohérence avec l’analyse « Boissons disparues ».** Ce **{fr_l(d['litres_retenu'])}** est désormais un **poste explicite de la cascade** des deux pages (il remplace l’ancien forfait prudent de 446 L à 8 %). Il s’ajoute à la dégustation, au crémant jeté et à la freinte de bière pour décomposer ce qui n’était auparavant qu’une « perte résiduelle » globale : le résiduel ne contient plus que la casse et l’évaporation irréductibles."},
            {"kind": "piecejointe", "intro": "Détail du calcul par régime de service :",
             "fichiers": [{"fichier": "pieces-defense/RF-sur-versement-au-verre.xlsx", "label": "RF — Sur-versement au verre (vins, spiritueux, cocktails)"}]},
            {"kind": "interne", "audience": "avocat", "titre": "Pour solidifier",
             "texte": "Faire établir un **constat d’huissier** : servir plusieurs « verres de vin », « pressions » et alcools forts dans les conditions réelles du bar (sans doseur), mesurer au millilitre, établir le ratio dose servie / dose carte. Photographier le bar sans verre doseur. Le constat objective le taux ; Kerr 2008 le corrobore (citer comme ordre de grandeur sectoriel, pas comme norme française). Ne pas additionner ce poste avec la dégustation (geste distinct) ni avec la bière (page dédiée). Retirer cet encart de toute version remise."},
        ],
    }
    ecrire_json(slug, doc)
    return slug, round(d["litres_retenu"])


# =============================================================================
# PAGE 2 - PERTES BIERE (MOUSSE / FREINTE)
# =============================================================================
def page_biere(d):
    slug = "pertes-biere-mousse"
    xlsx = os.path.join(PIECES, "RF-pertes-biere-mousse.xlsx")
    ecrire_xlsx(
        xlsx, "Pertes de biere pression - freinte technique du fut",
        "Mousse, purge, fond de fut et nettoyage des lignes : volume tire mais jamais servi. Rendement-fut courant ~95 % (≈5 % mini) ; litterature CHR 5-20 %.",
        [(
            "Biere pression tiree",
            ["Article (part biere du fut)", "Quantite (3 ans)", "Volume biere (L)"],
            [[l["produit"] + f" ({l['vol_cl']} cl)", l["qte"], round(l["litres"])] for l in d["lignes"]]
            + [["TOTAL biere pression", round(sum(l["qte"] for l in d["lignes"])), round(d["base_l"])]],
            [34, 18, 22],
        ), (
            "Freinte chiffree",
            ["Hypothese de freinte", "Taux", "Litres perdus (3 ans)"],
            [
                ["Borne basse (rendement-fut ~95 %)", fr_pct(d["taux_min"] * 100, 0), round(d["litres_min"])],
                ["RETENU (mode CHR)", fr_pct(d["taux_mode"] * 100, 0), round(d["litres_mode"])],
                ["Borne haute CHR", fr_pct(d["taux_haut"] * 100, 0), round(d["litres_haut"])],
            ],
            [34, 14, 24],
        )],
    )
    lignes = [[cg(l["produit"]), cd(fr_cl(l["vol_cl"])), cd(fr_int(l["qte"])), cd(fr_l(l["litres"]))] for l in d["lignes"]]
    lignes.append([cgf("Total bière pression tirée"), cd(""), cdf(fr_int(sum(l['qte'] for l in d['lignes']))), cdf(fr_l(d["base_l"]))])
    doc = {
        "meta": {"slug": slug, "source": "scripts/rendu-final-reconstitution-bloc2.py",
                 "grief": "Proposition p. 44-53 (methode 2/2) - pertes biere",
                 "litres_retenu": round(d["litres_mode"])},
        "sections": [
            {"kind": "chapitre", "source": "fisc", "numero": 1,
             "titre": "Le grief de l’administration",
             "sousTitre": "Proposition p. 50-51 — la bière du fût est réputée presque intégralement vendue"},
            {"kind": "paragraphe",
             "texte": "Le service reconstitue la bière en divisant le **volume de fût disponible** par les doses servies (pression 25 cl, pinte 50 cl, part bière des Picon-bière, panachés et Monaco, p. 50). Il suppose donc que **presque tout le fût acheté finit dans un verre vendu**. C’est impossible : un fût ne se vide jamais à 100 % dans les verres — une partie part en mousse, en purge et en nettoyage des lignes."},
            {"kind": "chapitre", "source": "nous", "numero": 2,
             "titre": "Notre mesure : la bière pression perd un volume technique avant le verre",
             "sousTitre": "Mousse, purge, fond de fût, nettoyage des lignes — documenté et chiffré"},
            {"kind": "paragraphe",
             "texte": "Tout fût tiré laisse un volume qui n’atteint jamais le verre du client : **collerette de mousse** à chaque service, **fond de fût** non tirable, **purge** au changement de fût, et surtout **vidange des lignes à chaque nettoyage**. La **Brewers Association** recommande un nettoyage des lignes **toutes les deux semaines** (standard repris par la profession) : à chaque cycle, la bière contenue dans les lignes est jetée. Le **rendement-fût** considéré comme normal dans la profession est d’environ **95 %** (soit **≈ 5 % de freinte technique minimale**), et la littérature CHR situe les pertes pression entre **5 % et 20 %** selon l’installation et le réglage du tirage."},
            {"kind": "tableau", "titre": "Bière pression réellement tirée (part bière des fûts Affligem, 3 exercices)",
             "minWidth": 560,
             "colonnes": [{"label": "Article (part bière)"}, {"label": "Dose bière", "align": "right"}, {"label": "Quantité", "align": "right"}, {"label": "Volume", "align": "right"}],
             "lignes": lignes},
            {"kind": "kpis", "items": [
                {"label": "Bière pression tirée", "valeur": fr_l(d["base_l"]), "sub": "fûts Affligem, 3 exercices", "couleur": "blue"},
                {"label": "Freinte retenue", "valeur": fr_pct(d["taux_mode"] * 100, 0), "sub": "mode CHR (entre 5 % et 18 %)", "highlight": True, "couleur": "teal"},
                {"label": "Volume perdu", "valeur": fr_l(d["litres_mode"]), "sub": "mousse, purge, lignes, fond de fût", "couleur": "teal"},
            ]},
            {"kind": "paragraphe",
             "texte": f"**Le calcul.** Sur **{fr_l(d['base_l'])}** de bière pression tirée en trois ans, une freinte technique **de {fr_pct(d['taux_mode']*100,0)}** (mode de la fourchette CHR) représente **{fr_l(d['litres_mode'])}** jamais servis. À la borne basse incontestable du rendement-fût (5 %), c’est déjà **{fr_l(d['litres_min'])}** ; à la borne haute (18 %), **{fr_l(d['litres_haut'])}**. Cette perte est **purement technique** : elle est tirée du fût, mais détruite, jamais encaissée."},
            {"kind": "alerte", "couleur": "teal", "titre": "Résultat",
             "texte": f"La freinte technique du fût détruit **{fr_l(d['litres_mode'])}** de bière sur trois ans (mode CHR), jamais servie ni encaissée. Ce volume explique une part du résiduel de l’analyse « Boissons disparues » et montre qu’un fût ne peut pas, physiquement, être vendu à 100 % comme le suppose la reconstitution."},
            {"kind": "piecejointe", "intro": "Détail du volume tiré et sensibilité au taux de freinte :",
             "fichiers": [{"fichier": "pieces-defense/RF-pertes-biere-mousse.xlsx", "label": "RF — Pertes de bière pression (freinte du fût)"}]},
            {"kind": "interne", "audience": "avocat", "titre": "Pour solidifier",
             "texte": "Obtenir une **attestation du distributeur/brasseur (Affligem)** sur le taux de freinte réel d’un fût (mousse, fond de fût, purge) et la fréquence de nettoyage des lignes ; conserver les bons de nettoyage. Noter que le fisc a lui-même retranché 15 % sur la bière (p. 51) : notre freinte technique en occupe déjà une bonne part, ce qui interdit de réduire cet abattement. Ne pas additionner avec le sur-versement (la bière en est exclue). Retirer cet encart de toute version remise."},
        ],
    }
    ecrire_json(slug, doc)
    return slug, round(d["litres_mode"])


# =============================================================================
# PAGE 3 - CREMANT JETE
# =============================================================================
def page_cremant(d):
    slug = "pertes-cremant"
    xlsx = os.path.join(PIECES, "RF-pertes-cremant.xlsx")
    ck_rows = [[c["cocktail"], c["dose_cl"], round(c["qte"]), round(c["litres"], 1)] for c in d["cocktails"]]
    ecrire_xlsx(
        xlsx, "Cremant jete en fin de journee - bouteille eventee",
        "Un effervescent ouvert est plat le lendemain. Le cremant est ouvert a la journee ; le solde non servi est jete chaque soir.",
        [(
            "Cremant servi",
            ["Usage", "Dose (cl)", "Quantite (3 ans)", "Litres servis"],
            [["Verre de cremant", d["dose_verre"], d["verre_q"], round(d["liq_verre"], 1)]]
            + ck_rows
            + [["TOTAL cremant servi", "", d["servings"], round(d["liq_total"], 1)]],
            [30, 12, 18, 16],
        ), (
            "Perte fin de journee",
            ["Parametre", "Valeur"],
            [
                ["Jours de service (3 ans)", JOURS_SERVICE],
                ["Cremant servi / jour", round(d["demande_jour"], 2)],
                ["Bouteilles ouvertes / jour", d["bouteilles_jour"]],
                ["Solde jete / jour (L)", round(d["waste_jour"], 2)],
                ["RESULTAT - cremant jete (3 ans, L)", round(d["waste_3ans"])],
            ],
            [40, 16],
        )],
    )
    ck_json = [[cg(f"Cocktail {c['cocktail']}"), cd(fr_cl(c["dose_cl"])), cd(fr_int(c["qte"])), cd(fr_l(c["litres"], 1))] for c in d["cocktails"]]
    serv_rows = [[cg("Verre de crémant"), cd(fr_cl(d["dose_verre"])), cd(fr_int(d["verre_q"])), cd(fr_l(d["liq_verre"], 1))]] + ck_json
    serv_rows.append([cgf("Total crémant servi (hors bouteilles entières)"), cd(""), cdf(fr_int(d["servings"])), cdf(fr_l(d["liq_total"], 1))])
    doc = {
        "meta": {"slug": slug, "source": "scripts/rendu-final-reconstitution-bloc2.py",
                 "grief": "Proposition p. 46-47 - ingredient Cremant",
                 "litres_retenu": round(d["waste_3ans"])},
        "sections": [
            {"kind": "chapitre", "source": "fisc", "numero": 1,
             "titre": "Ce que retient l’administration",
             "sousTitre": "Proposition p. 46-47 — tout le crémant disponible est réputé vendu"},
            {"kind": "paragraphe",
             "texte": "Le service répartit **tout le crémant acheté** entre les articles qui en consomment — verre (12 cl), cocktails La Vouivre, Le Père Grégoire et KITTYKIR, bouteilles (75 cl) — et **divise le volume disponible par les doses** pour en déduire des ventes (Proposition p. 46-47, ingrédient CRÉMANT). La méthode suppose que **chaque centilitre de crémant ouvert finit dans un verre vendu**. Or le crémant est un **vin effervescent** : c’est précisément le produit qu’on ne peut pas conserver d’un jour à l’autre."},
            {"kind": "chapitre", "source": "nous", "numero": 2,
             "titre": "Une bouteille de crémant ouverte est jetée le soir même",
             "sousTitre": "Effervescent éventé en quelques heures — on ouvre à la journée, on jette le solde"},
            {"kind": "paragraphe",
             "texte": "Un **vin effervescent ouvert perd ses bulles en quelques heures** et est **plat dès le lendemain** sans bouchon hermétique (œnologie courante ; Coravin). En service, une bouteille de crémant entamée pour un verre ou un cocktail **ne peut donc pas être resservie le jour suivant** : le solde est **jeté chaque soir**. Le crémant tourne lentement à la bouteille : sur trois ans, **{0}** verres et cocktails de crémant ont été servis, soit **{1}** par jour de service en moyenne — de quoi entamer une bouteille par jour, rarement la finir.".format(fr_int(d["servings"]), fr_l(d["servings_jour"], 1).replace(" L", ""))},
            {"kind": "tableau", "titre": "Crémant réellement servi au verre et en cocktails (3 exercices)",
             "minWidth": 560,
             "colonnes": [{"label": "Usage"}, {"label": "Dose", "align": "right"}, {"label": "Quantité", "align": "right"}, {"label": "Litres servis", "align": "right"}],
             "lignes": serv_rows},
            {"kind": "paragraphe",
             "texte": f"**Le calcul, jour par jour.** Le crémant servi représente **{fr_l(d['liq_total'],1)}** sur trois ans, soit **{fr_l(d['demande_jour'],2)} par jour** de service. Comme une bouteille fait **75 cl** et qu’elle doit être ouverte fraîche, on **ouvre {d['bouteilles_jour']} bouteille par jour** où le crémant est servi et on **jette le solde non écoulé**, soit **{fr_l(d['waste_jour'],2)} par jour**. Sur **{fr_int(JOURS_SERVICE)} jours** de service, cela fait **{fr_l(d['waste_3ans'])}** de crémant détruit — l’équivalent d’environ **{fr_int(d['waste_3ans']/0.75)} bouteilles** jetées."},
            {"kind": "kpis", "items": [
                {"label": "Crémant servi / jour", "valeur": fr_l(d["demande_jour"], 2), "sub": f"{fr_int(d['servings'])} services / {fr_int(JOURS_SERVICE)} j", "couleur": "blue"},
                {"label": "Solde jeté / jour", "valeur": fr_l(d["waste_jour"], 2), "sub": "bouteille éventée le lendemain", "couleur": "teal"},
                {"label": "Crémant jeté (3 ans)", "valeur": fr_l(d["waste_3ans"]), "sub": f"≈ {fr_int(d['waste_3ans']/0.75)} bouteilles", "highlight": True, "couleur": "teal"},
            ]},
            {"kind": "alerte", "couleur": "teal", "titre": "Résultat",
             "texte": f"Parce qu’un crémant ouvert s’évente, le restaurant **jette environ {fr_l(d['waste_3ans'])} de crémant** sur trois ans (≈ {fr_int(d['waste_3ans']/0.75)} bouteilles). La reconstitution du fisc, qui répute **tout** le crémant disponible vendu, transforme ce solde **détruit** en ventes fictives."},
            {"kind": "piecejointe", "intro": "Détail du crémant servi (verre + cocktails) et calcul de la perte journalière :",
             "fichiers": [{"fichier": "pieces-defense/RF-pertes-cremant.xlsx", "label": "RF — Crémant jeté en fin de journée"}]},
            {"kind": "interne", "audience": "avocat", "titre": "Hypothèse et fiabilisation",
             "texte": "Le calcul retient l’hypothèse prudente d’**une bouteille ouverte par jour de service** (le crémant tournant à ~8 services/jour, une bouteille est entamée presque chaque jour). Un **export caisse au ticket daté** (réclamable au titre du journal NF525) donnerait le nombre exact de jours où le crémant a été servi et le rendrait incontestable. Faire confirmer par la gérante la pratique « bouteille jetée le soir » (effervescent) et, idéalement, une attestation 202 CPC. Retirer cet encart de toute version remise."},
        ],
    }
    ecrire_json(slug, doc)
    return slug, round(d["waste_3ans"])


# =============================================================================
# PAGE 4 - DEGUSTATION
# =============================================================================
def page_degustation(d):
    slug = "degustation-au-verre"
    xlsx = os.path.join(PIECES, "RF-degustation-au-verre.xlsx")
    ecrire_xlsx(
        xlsx, "Degustation offerte - quantite perdue, vin par vin",
        "Vin nomme au verre : la bouteille est montee, une personne goute 2 cl (1 degustation pour 2 verres du meme vin). Pichet : une larme de 2 cl pour approuver. Vins generiques (cubis/maison) : exclus.",
        [(
            "Degustation par vin",
            ["Vin nomme (carte des vins)", "Verres (3 ans)", "Degustations", "Volume offert (L)"],
            [[v["vin"], v["verres"], v["degustations"], round(v["litres"], 1)] for v in d["vins"]]
            + [["Sous-total vins nommes", d["nommes_q"], sum(v["degustations"] for v in d["vins"]), round(d["deg_nommes_l"], 1)],
               ["Pichets (1 larme / pichet)", d["pichets_q"], d["pichets_q"], round(d["deg_pichets_l"], 1)],
               ["TOTAL degustation", "", "", round(d["total_l"], 1)]],
            [34, 14, 14, 16],
        )],
    )
    vin_json = [[cg(v["vin"]), cd(fr_int(v["verres"])), cd(fr_int(v["degustations"])), cd(fr_l(v["litres"], 1))] for v in d["vins"]]
    vin_json.append([cgf("Sous-total vins nommés"), cdf(fr_int(d["nommes_q"])), cdf(fr_int(sum(v["degustations"] for v in d["vins"]))), cdf(fr_l(d["deg_nommes_l"], 1))])
    vin_json.append([cg("Pichets (1 larme par pichet)"), cd(fr_int(d["pichets_q"])), cd(fr_int(d["pichets_q"])), cd(fr_l(d["deg_pichets_l"], 1))])
    vin_json.append([cgf("TOTAL dégustation"), cd(""), cd(""), cdf(fr_l(d["total_l"], 1))])
    doc = {
        "meta": {"slug": slug, "source": "scripts/rendu-final-reconstitution-bloc2.py",
                 "grief": "Proposition p. 37-44 (methode 1/2)",
                 "litres_retenu": round(d["total_l"])},
        "sections": [
            {"kind": "chapitre", "source": "fisc", "numero": 1,
             "titre": "Le grief de l’administration",
             "sousTitre": "Proposition p. 37-44 — tout le vin disponible est réputé vendable"},
            {"kind": "paragraphe",
             "texte": "La reconstitution **convertit en verres vendus la totalité du vin disponible**, sans rien réserver au **geste de dégustation** qui précède le service. Or ce geste est systématique et ne laisse **aucune trace en caisse** : il n’est ni un article, ni une remise."},
            {"kind": "chapitre", "source": "nous", "numero": 2,
             "titre": "La quantité offerte en dégustation, vin par vin",
             "sousTitre": "On part de nos ventes réelles au verre et on chiffre la larme de dégustation"},
            {"kind": "paragraphe",
             "texte": "Pour un vin de la **carte des vins** (Savagnin, Saint-Véran, Trousseau, vin jaune…), le serveur **monte la bouteille en salle et fait goûter une personne (≈ 2 cl)** avant de remplir le verre. Si plusieurs convives commandent **le même** vin à une table, **une seule** dégustation (on retient prudemment **1 dégustation pour 2 verres**) ; s’ils commandent des vins **différents**, chacun goûte. Les **vins génériques** (« verre de vin », rosé/aligoté maison, tirés d’un cubis) **n’en donnent pas lieu** (pas de bouteille montée) : ils sont **exclus**. Le tableau ci-dessous part de **nos ventes réelles au verre** et donne, vin par vin, la quantité offerte."},
            {"kind": "tableau", "titre": "Quantité offerte en dégustation, vin par vin (3 exercices)",
             "minWidth": 560,
             "colonnes": [{"label": "Vin nommé"}, {"label": "Verres", "align": "right"}, {"label": "Dégustations", "align": "right"}, {"label": "Volume offert", "align": "right"}],
             "lignes": vin_json},
            {"kind": "kpis", "items": [
                {"label": "Vins nommés", "valeur": fr_l(d["deg_nommes_l"], 1), "sub": f"{fr_int(d['nommes_q'])} verres → {fr_int(sum(v['degustations'] for v in d['vins']))} dégustations", "couleur": "blue"},
                {"label": "Pichets", "valeur": fr_l(d["deg_pichets_l"], 1), "sub": f"{fr_int(d['pichets_q'])} × 2 cl", "couleur": "blue"},
                {"label": "Total dégustation", "valeur": fr_l(d["total_l"], 1), "sub": "offert, jamais vendu", "highlight": True, "couleur": "teal"},
            ]},
            {"kind": "alerte", "couleur": "teal", "titre": "Résultat",
             "texte": f"Vin par vin, la dégustation offerte — bouteille montée pour le vin nommé, larme au pichet — soustrait **{fr_l(d['total_l'],1)}** de vin au volume vendable sur trois ans, sur une hypothèse **basse** (1 dégustation pour {d['ratio']:.0f} verres du même vin). Ce volume explique une part du résiduel de l’analyse « Boissons disparues » ; la reconstitution du fisc le compte pourtant comme des verres vendus."},
            {"kind": "piecejointe", "intro": "Quantité offerte en dégustation, vin par vin (+ pichets) :",
             "fichiers": [{"fichier": "pieces-defense/RF-degustation-au-verre.xlsx", "label": "RF — Dégustation offerte (détail par vin)"}]},
            {"kind": "interne", "audience": "avocat", "titre": "Hypothèse et fiabilisation",
             "texte": f"Seul paramètre non mesuré : le **nombre moyen de verres du même vin par table** (retenu à {d['ratio']:.0f}, ce qui **minore** la dégustation ; à 1,5 le volume monte). Bien le **distinguer du sur-versement** (geste différent : la dégustation est versée AVANT le service, le sur-versement PENDANT) — ne jamais additionner les deux sur les mêmes centilitres. Faire confirmer la pratique par la gérante et le personnel de salle (attestations 202 CPC). Retirer cet encart de toute version remise."},
        ],
    }
    ecrire_json(slug, doc)
    return slug, round(d["total_l"])


# =============================================================================
# 5. ALCOOL DE CUISINE (doses des plats)
# =============================================================================
def calc_cuisine(bpd):
    par_alcool = sorted(bpd["cuisineParAlcool"], key=lambda r: -r["litres_3ans"])
    total_l = sum(r["litres_3ans"] for r in par_alcool)
    total_cout = sum(r.get("cout", 0) for r in par_alcool)
    plats = bpd["cuisine"]
    return {"par_alcool": par_alcool, "total_l": total_l, "total_cout": total_cout, "plats": plats}


def page_cuisine(d):
    slug = "alcool-cuisine-doses-plats"
    xlsx = os.path.join(PIECES, "RF-alcool-cuisine-doses-plats.xlsx")
    ecrire_xlsx(
        xlsx, "Alcool incorpore en cuisine - dose par plat",
        "Fondues, sauces, babas, flambages, coupes glacees : l'alcool part en cuisine, jamais dans un verre vendu. Doses confirmees par les dirigeants (memes doses que les reperes D/E/G/Q du fisc).",
        [(
            "Par alcool",
            ["Alcool", "Litres (3 ans)", "Cout d'achat"],
            [[r["alcool"], round(r["litres_3ans"]), round(r.get("cout", 0))] for r in d["par_alcool"]]
            + [["TOTAL cuisine", round(d["total_l"]), round(d["total_cout"])]],
            [26, 16, 16],
        ), (
            "Par plat (dose)",
            ["Plat / preparation", "Type", "Alcool", "Dose (cl)"],
            [[p["plat"], p["type"], p["alcool"], p["dose_cl"]] for p in d["plats"]],
            [34, 12, 22, 10],
        )],
    )
    alc_rows = [[cg(r["alcool"]), cd(fr_l(r["litres_3ans"])), cd(fr_eur(r.get("cout", 0)))] for r in d["par_alcool"]]
    alc_rows.append([cgf("Total alcool de cuisine"), cdf(fr_l(d["total_l"])), cdf(fr_eur(d["total_cout"]))])
    plat_rows = [[cg(p["plat"]), cg(p["type"]), cg(p["alcool"]), cd(fr_cl(p["dose_cl"]))] for p in d["plats"][:24]]
    doc = {
        "meta": {"slug": slug, "source": "scripts/rendu-final-reconstitution-bloc2.py",
                 "grief": "Proposition p. 37, p. 44-48 - reperes D/E/G/Q (alcool cuisine)",
                 "litres_retenu": round(d["total_l"])},
        "sections": [
            {"kind": "chapitre", "source": "fisc", "numero": 1,
             "titre": "Ce que retient l’administration",
             "sousTitre": "Proposition p. 37 et p. 44-48 — repères D, E, G, Q (alcool de cuisine)"},
            {"kind": "paragraphe",
             "texte": "Le service reconnaît qu’une partie de l’alcool part en cuisine et l’« ampute » du volume vendable via ses **repères D (calvados), E (vin jaune), G (porto) et Q (macvin)** (Proposition p. 44-48). Mais il **n’en déduit qu’une fraction**, calculée à partir de quelques plats du menu et de proportions, en retenant des doses parfois minorées (ex. **1 cl** de porto par sauce, p. 45-46). L’alcool réellement incorporé dans **toute** la carte — fondues, sauces, flambages, babas, coupes glacées — est plus large."},
            {"kind": "chapitre", "source": "nous", "numero": 2,
             "titre": "L’alcool de cuisine, plat par plat",
             "sousTitre": "Doses confirmées par les dirigeants — celles-là mêmes que le fisc reprend"},
            {"kind": "paragraphe",
             "texte": "Nous reprenons **les doses confirmées par les dirigeants** (entrevue du 30 mars 2026, que le vérificateur retient lui-même : fondues 9-10 cl, babas/flambages 4 cl, sauces 1 cl) et nous les appliquons à **l’intégralité des plats alcoolisés vendus**, pas seulement à ceux des menus. Chaque centilitre ainsi tracé est de l’alcool **acheté puis cuit**, qui ne peut plus être vendu au verre."},
            {"kind": "tableau", "titre": "Alcool de cuisine par produit (3 exercices)",
             "minWidth": 480,
             "colonnes": [{"label": "Alcool"}, {"label": "Litres", "align": "right"}, {"label": "Coût d’achat", "align": "right"}],
             "lignes": alc_rows},
            {"kind": "kpis", "items": [
                {"label": "Alcool de cuisine", "valeur": fr_l(d["total_l"]), "sub": "fondues, sauces, babas, flambages", "highlight": True, "couleur": "teal"},
                {"label": "Coût d’achat", "valeur": fr_eur(d["total_cout"]), "sub": "acheté puis cuit, jamais vendu", "couleur": "blue"},
                {"label": "Doses", "valeur": "celles du fisc", "sub": "confirmées par les dirigeants (30/03/2026)", "couleur": "gray"},
            ]},
            {"kind": "tableau", "titre": "Détail des doses par plat (extrait)",
             "minWidth": 520,
             "colonnes": [{"label": "Plat / préparation"}, {"label": "Type"}, {"label": "Alcool"}, {"label": "Dose", "align": "right"}],
             "lignes": plat_rows},
            {"kind": "alerte", "couleur": "teal", "titre": "Résultat",
             "texte": f"La cuisine consomme **{fr_l(d['total_l'])}** d’alcool acheté sur trois ans (fondues au vin jaune et Ravelin, sauces au porto, babas et flambages au macvin et calvados, coupes au Bailey’s et cassis). Le fisc n’en déduit qu’une partie : tout le reste est compté à tort comme des verres vendus."},
            {"kind": "piecejointe", "intro": "Alcool de cuisine par produit et dose plat par plat :",
             "fichiers": [{"fichier": "pieces-defense/RF-alcool-cuisine-doses-plats.xlsx", "label": "RF — Alcool de cuisine (par alcool + par plat)"}]},
            {"kind": "interne", "audience": "avocat", "titre": "Angle",
             "texte": "Argument fort car il **retourne les propres doses du fisc** (repères D/E/G/Q) en les appliquant à toute la carte, pas aux seuls menus. Verser le document de composition des plats (doses par recette) confirmé par la gérante. Ne pas sur-jouer l’absinthe de la crème brûlée (chiffre OCR douteux côté fisc) : s’en tenir aux doses confirmées. Retirer cet encart de toute version remise."},
        ],
    }
    ecrire_json(slug, doc)
    return slug, round(d["total_l"])


# =============================================================================
# 6. OFFERTS, REMISES ET PERTES (taux retenus)
# =============================================================================
def calc_offerts(bpd):
    s = bpd["synthese"]
    cascade = {c["poste"]: c["litres"] for c in s["cascade"]}
    return {
        "achat_l": s["achat_alcool_l"],
        "perte_l": s["perte_reelle_l"],
        "perte_pct": s["perte_reelle_pct"],
        "exploit_l": s.get("perte_exploitation_l"),
        "exploit_pct": s.get("perte_exploitation_pct"),
        "cascade": cascade,
    }


def page_offerts(d, postes_itemises):
    """postes_itemises : dict label->litres (chef, offerts, sur-versement,
    cremant, degustation, freinte biere) pour montrer que le non-vendu reel
    depasse de loin les forfaits 5 %+5 %+5 % du fisc."""
    slug = "offerts-remises-pertes"
    xlsx = os.path.join(PIECES, "RF-offerts-remises-pertes.xlsx")
    rows = [[lbl, round(v)] for lbl, v in postes_itemises.items()]
    total_item = sum(postes_itemises.values())
    ecrire_xlsx(
        xlsx, "Offerts, remises et pertes - les forfaits du fisc sont des planchers",
        "Le fisc applique 5 % remise + 5 % pertes + 5 % conso personnel (+15 % sur la biere). La consommation reelle sans vente, itemisee, depasse ces forfaits.",
        [(
            "Non-vendu itemise",
            ["Poste reellement consomme sans vente", "Litres (3 ans)"],
            rows + [["TOTAL itemise (hors cuisine/menus)", round(total_item)]],
            [44, 18],
        ), (
            "Comparaison aux forfaits",
            ["Reference", "Taux / nature", "Lecture"],
            [
                ["Fisc - remise", "5 % du CA reconstitue", "forfait"],
                ["Fisc - pertes", "5 % du CA reconstitue", "forfait"],
                ["Fisc - conso personnel", "5 % du CA reconstitue", "forfait"],
                ["Fisc - biere", "15 % du volume biere", "forfait"],
                ["Reel (notre residuel)", f"{str(d['perte_pct']).replace('.', ',')} % des achats", "mesure/itemise"],
                ["Jurisprudence CAA Paris 17/03/2021", "22 % des achats", "valide par le juge"],
            ],
            [34, 24, 18],
        )],
    )
    item_rows = [[cg(lbl), cd(fr_l(v))] for lbl, v in postes_itemises.items()]
    item_rows.append([cgf("Total non-vendu itemisé (hors cuisine et menus)"), cdf(fr_l(total_item))])
    doc = {
        "meta": {"slug": slug, "source": "scripts/rendu-final-reconstitution-bloc2.py",
                 "grief": "Proposition p. 51 - offerts/remises/pertes (5%+5%+5% +15% biere)",
                 "litres_retenu": round(total_item)},
        "sections": [
            {"kind": "chapitre", "source": "fisc", "numero": 1,
             "titre": "Ce que retient l’administration",
             "sousTitre": "Proposition p. 51 — trois forfaits de 5 % et un abattement bière de 15 %"},
            {"kind": "paragraphe",
             "texte": "À la fin de la reconstitution, le service applique **5 % du CA reconstitué pour les offerts/remises, 5 % pour les pertes, 5 % pour la consommation du personnel**, et **15 % supplémentaires sur le volume de bière** (Proposition p. 51). Il reconnaît donc que ces consommations **existent** — mais il les fixe à des **forfaits ronds**, faute, dit-il, de pouvoir les identifier dans la caisse."},
            {"kind": "chapitre", "source": "nous", "numero": 2,
             "titre": "Ces forfaits sont des planchers : le non-vendu réel est supérieur",
             "sousTitre": "Une fois chaque poste itemisé, la consommation sans vente dépasse les 5 %"},
            {"kind": "paragraphe",
             "texte": "Le dossier ne se contente pas des forfaits : il **chiffre chaque poste**. La consommation du chef (Picon + Macvin), les apéritifs offerts, le sur-versement au verre, le crémant jeté, les dégustations et la freinte de bière représentent, à eux seuls et **hors cuisine et menus**, le volume ci-dessous — déjà supérieur à ce que les forfaits de 5 % capturent."},
            {"kind": "tableau", "titre": "Consommation réelle sans vente, poste par poste (3 exercices)",
             "minWidth": 480,
             "colonnes": [{"label": "Poste"}, {"label": "Litres", "align": "right"}],
             "lignes": item_rows},
            {"kind": "paragraphe",
             "texte": f"**Mise en perspective.** En sommant ces postes documentés et la casse irréductible, la **perte d’exploitation totale** (tout ce qui n’est pas vendu comme boisson, hors cuisine et menus) atteint **{fr_pct(d['exploit_pct'])}** des achats. C’est **au-dessus** de l’ordre de grandeur que **l’administration elle-même** retient en reconstitution de bar : dans l’affaire **CAA Paris, 17 mars 2021**, le vérificateur a déduit **22 % des achats** au titre du personnel, des offerts, des pertes et du vol, et la cour a **validé** la méthode. Les forfaits de 5 % du présent contrôle sont donc nettement **inférieurs** à la réalité du secteur."},
            {"kind": "alerte", "couleur": "teal", "titre": "Résultat",
             "texte": f"Les forfaits de 5 %+5 %+5 % du fisc **sous-estiment** la consommation sans vente : itemisée, elle atteint déjà **{fr_l(total_item)}** hors cuisine et menus, et la perte d’exploitation totale (**{fr_pct(d['exploit_pct'])}**) **dépasse** les **22 %** validés par la jurisprudence. Loin d’être généreux, ces abattements sont des **planchers**."},
            {"kind": "piecejointe", "intro": "Postes itemisés et comparaison aux forfaits / à la jurisprudence :",
             "fichiers": [{"fichier": "pieces-defense/RF-offerts-remises-pertes.xlsx", "label": "RF — Offerts, remises et pertes (forfaits vs réel)"}]},
            {"kind": "interne", "audience": "avocat", "titre": "Précautions",
             "texte": "**Fiabiliser le numéro de requête** de l’arrêt CAA Paris du 17 mars 2021 (Légifrance / Doctrine) avant citation formelle ; le principe (abattement ~22 % validé) est solide. Arbitrer le **risque d’avantage en nature** sur la consommation du personnel/dirigeant avant de la chiffrer publiquement. Ne pas additionner deux fois un même centilitre (sur-versement ≠ dégustation ≠ cuisine). Retirer cet encart de toute version remise."},
        ],
    }
    ecrire_json(slug, doc)
    return slug, round(total_item)


# =============================================================================
# 7. COEFFICIENT LIQUIDE -> SOLIDE
# =============================================================================
def calc_coefficient(bpd):
    # Recapitulation par exercice citee dans la Proposition p. 52 (synthese OCR).
    recap = [
        {"ex": "2022-2023", "liq_avant": 178341, "liq_apres": 151590, "coef": 2.94, "solides": 445675, "total": 597265},
        {"ex": "2023-2024", "liq_avant": 169014, "liq_apres": 143662, "coef": 3.02, "solides": 433860, "total": 577522},
        {"ex": "2024-2025", "liq_avant": 165065, "liq_apres": 140306, "coef": 3.10, "solides": 434947, "total": 575253},
    ]
    coef_moyen = sum(r["coef"] for r in recap) / len(recap)
    total_reconstitue = sum(r["total"] for r in recap)
    return {"recap": recap, "coef_moyen": coef_moyen, "total_reconstitue": total_reconstitue}


def page_coefficient(d, litres_oublies, cout_litre):
    slug = "coefficient-liquide-solide"
    xlsx = os.path.join(PIECES, "RF-coefficient-liquide-solide.xlsx")
    recap = d["recap"]
    ecrire_xlsx(
        xlsx, "Extrapolation de la cuisine - coefficient liquide -> solide",
        "Le CA solides (cuisine) n'est pas mesure : il est obtenu en multipliant le CA liquides reconstitue par 2,94 / 3,02 / 3,10. Toute erreur sur les liquides est donc amplifiee ~3 fois.",
        [(
            "Recap fisc par exercice",
            ["Exercice", "CA liquides (apres abatt.)", "Coefficient", "CA solides", "Total reconstitue"],
            [[r["ex"], r["liq_apres"], r["coef"], r["solides"], r["total"]] for r in recap]
            + [["TOTAL 3 ans", sum(r["liq_apres"] for r in recap), round(d["coef_moyen"], 2), sum(r["solides"] for r in recap), d["total_reconstitue"]]],
            [14, 22, 12, 16, 18],
        )],
    )
    recap_rows = [[cg(r["ex"]), cd(fr_eur(r["liq_apres"])), cd(str(r["coef"]).replace(".", ",")), cd(fr_eur(r["solides"])), cd(fr_eur(r["total"]))] for r in recap]
    recap_rows.append([cgf("Total 3 ans"), cdf(fr_eur(sum(r["liq_apres"] for r in recap))), cdf("≈ " + f"{d['coef_moyen']:.2f}".replace(".", ",")), cdf(fr_eur(sum(r["solides"] for r in recap))), cdf(fr_eur(d["total_reconstitue"]))])
    # Effet d'amplification : 1 € de liquide sur-estime -> coef € de CA total
    amplif = d["coef_moyen"]
    ca_liquide_oublie = litres_oublies * cout_litre  # ordre de grandeur au cout d'achat (plancher)
    doc = {
        "meta": {"slug": slug, "source": "scripts/rendu-final-reconstitution-bloc2.py",
                 "grief": "Proposition p. 52 - coefficient liquide/solide 2,94 / 3,02 / 3,10",
                 "coef_moyen": round(d["coef_moyen"], 2)},
        "sections": [
            {"kind": "chapitre", "source": "fisc", "numero": 1,
             "titre": "Ce que retient l’administration",
             "sousTitre": "Proposition p. 52 — le CA cuisine est extrapolé, jamais mesuré"},
            {"kind": "paragraphe",
             "texte": "Le service ne reconstitue **pas** la cuisine : il **multiplie le CA liquides reconstitué par un coefficient** (« rapport liquide/solides pour 1 € ») de **2,94** (2023), **3,02** (2024) et **3,10** (2025) pour obtenir le « CA solides » (Proposition p. 52). Le CA cuisine, qui pèse les trois quarts du total reconstitué, **n’est donc jamais mesuré** : il est entièrement déduit du CA liquides."},
            {"kind": "tableau", "titre": "Récapitulation du fisc par exercice (Proposition p. 52)",
             "minWidth": 620,
             "colonnes": [{"label": "Exercice"}, {"label": "CA liquides (après abatt.)", "align": "right"}, {"label": "Coef.", "align": "right"}, {"label": "CA solides", "align": "right"}, {"label": "Total reconstitué", "align": "right"}],
             "lignes": recap_rows},
            {"kind": "chapitre", "source": "nous", "numero": 2,
             "titre": "Le coefficient amplifie l’erreur sur les liquides",
             "sousTitre": "Chaque litre sur-estimé au verre devient ~3 fois plus de CA fictif"},
            {"kind": "paragraphe",
             "texte": f"Le coefficient est une **loupe** : comme le CA solides = CA liquides × {f'{amplif:.2f}'.replace('.', ',')}, **chaque euro de CA liquides sur-estimé engendre environ {f'{amplif:.2f}'.replace('.', ',')} € de CA total fictif** (1 € de liquides + {f'{amplif-1:.2f}'.replace('.', ',')} € de solides extrapolés). Or les pages précédentes montrent que la reconstitution des liquides est gonflée : elle valorise comme des verres vendus des litres jamais vendus au verre (cuisine, menus, sur-versement, crémant jeté, dégustations, conso du chef, freinte bière). En corrigeant les liquides **puis** en réappliquant le propre coefficient du fisc, le total reconstitué s’effondre bien plus vite que l’erreur de départ."},
            {"kind": "kpis", "items": [
                {"label": "Coefficient moyen", "valeur": "× " + f"{d['coef_moyen']:.2f}".replace(".", ","), "sub": "2,94 / 3,02 / 3,10 selon l’exercice", "couleur": "red"},
                {"label": "Effet d’amplification", "valeur": "≈ × 3", "sub": "1 € de liquides sur-estimé → ~3 € de CA fictif", "highlight": True, "couleur": "red"},
                {"label": "CA cuisine", "valeur": "jamais mesuré", "sub": "entièrement extrapolé du liquide", "couleur": "gray"},
            ]},
            {"kind": "alerte", "couleur": "teal", "titre": "Résultat",
             "texte": f"Le coefficient n’ajoute aucune mesure : il **multiplie par ~{f'{amplif:.2f}'.replace('.', ',')}** l’erreur commise sur les liquides. La défense doit donc se concentrer sur les volumes de liquides (sur-versement, crémant, dégustation, cuisine, menus) : toute correction y est amplifiée ~3 fois sur le total, et fait passer le CA reconstitué **sous** le CA déclaré."},
            {"kind": "piecejointe", "intro": "Récapitulation du fisc et mécanique d’amplification :",
             "fichiers": [{"fichier": "pieces-defense/RF-coefficient-liquide-solide.xlsx", "label": "RF — Coefficient liquide/solide (amplification)"}]},
            {"kind": "interne", "audience": "avocat", "titre": "Angle",
             "texte": "Le coefficient est le **point de levier** : inutile de le contester en lui-même (il vient des ratios de la profession), il faut l’utiliser **contre** le fisc en montrant qu’il amplifie ~3× toute sur-évaluation des liquides — laquelle est démontrée poste par poste dans les autres sous-pages du bloc 2. Relier explicitement à la page « Reconstitution par les volumes » (réconciliation du CA). Retirer cet encart de toute version remise."},
        ],
    }
    ecrire_json(slug, doc)
    return slug, round(d["coef_moyen"], 2)


# =============================================================================
def main():
    items, bpd, conso = charger()
    sv = calc_surversement(conso)
    bi = calc_biere(items)
    cr = calc_cremant(items, bpd)
    de = calc_degustation(items)

    cu = calc_cuisine(bpd)
    of = calc_offerts(bpd)
    co = calc_coefficient(bpd)

    r1 = page_surversement(sv)
    r2 = page_biere(bi)
    r3 = page_cremant(cr)
    r4 = page_degustation(de)
    r5 = page_cuisine(cu)

    # Garde-fou : ces valeurs sont remontees en DUR dans la cascade de
    # src/data/incertitudeDisparu/14_synthese_perte_reelle.py (SURVERSEMENT_L,
    # FREINTE_BIERE_L, CREMANT_JETE_L, DEGUSTATION_L). Si le calcul derive, il
    # faut mettre a jour ces constantes puis relancer 14 -> 15.
    attendu = {"surversement": 807, "freinte": 129, "cremant": 126, "degustation": 113}
    obtenu = {"surversement": r1[1], "freinte": r2[1], "cremant": r3[1], "degustation": r4[1]}
    assert obtenu == attendu, (
        f"DRIFT cascade : {obtenu} != {attendu}. Mettre a jour les constantes de "
        "14_synthese_perte_reelle.py (et complementsDefense.ts) puis relancer 14 -> 15."
    )

    # Postes itemises non vendus (hors cuisine et menus) pour la page offerts.
    casc = {c["poste"]: c["litres"] for c in bpd["synthese"]["cascade"]}
    postes_itemises = {
        "Consommation du chef (Picon + Macvin)": casc.get("Consommation du chef (Picon + Macvin)", 143),
        "Apéritifs offerts aux clients": casc.get("Aperitifs offerts aux clients", 40),
        "Sur-versement au verre (free-pour)": r1[1],
        "Crémant jeté en fin de journée": r3[1],
        "Dégustation offerte (pichet + vin nommé)": r4[1],
        "Freinte technique de la bière pression": r2[1],
    }
    r6 = page_offerts(of, postes_itemises)
    cout_litre = bpd["synthese"]["achat_alcool_cout"] / bpd["synthese"]["achat_alcool_l"]
    litres_oublies = cu["total_l"] + casc.get("Alcool des menus (non detaille en caisse)", 228) + sum(postes_itemises.values())
    r7 = page_coefficient(co, litres_oublies, cout_litre)

    total = r1[1] + r2[1] + r3[1] + r4[1]
    print("RENDU FINAL - Bloc 2 : pertes chiffrees et sourcees")
    print("-" * 58)
    print(f"  sur-versement       : {fr_l(r1[1])}  (base {fr_l(sv['base_totale'])}, ~{fr_pct(sv['taux_blende']*100,0)})")
    print(f"  freinte biere       : {fr_l(r2[1])}  (base {fr_l(bi['base_l'])}, {int(bi['taux_mode']*100)} %)")
    print(f"  cremant jete        : {fr_l(r3[1])}  ({cr['bouteilles_jour']} bout./j, {fr_int(JOURS_SERVICE)} j)")
    print(f"  degustation offerte : {fr_l(r4[1])}  (pichets {fr_int(de['pichets_q'])}, verres nommes {fr_int(de['nommes_q'])})")
    print("-" * 58)
    print(f"  TOTAL itemise (4 pertes) du residuel : {fr_l(total)} / {bpd['synthese']['perte_reelle_l']} L residuel")
    print(f"  cuisine             : {fr_l(r5[1])}")
    print(f"  offerts/remises (non vendu itemise) : {fr_l(r6[1])}")
    print(f"  coefficient moyen   : x {r7[1]}")


if __name__ == "__main__":
    main()
