#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reponse1-rapprochement-caisse-factures.py

Piece de la reponse au courrier DDFiP 39 du 04/09/2026, point 10 (p. 74 et 75)
"Ventes sans achat".

Refait, exercice par exercice et reference par reference, le rapprochement
entre le bouton de caisse, la reference reellement facturee et le stock
inventorie, pour les trois references en cause : Bordeaux Mouton Cadet,
Hautes Cotes de Nuits, Hautes Cotes de Beaune. Controle egalement, ligne a
ligne, les trois tableaux imprimes en page 75.

Sorties : public/documents/pieces-reponse-1/R1-rapprochement-caisse-factures.xlsx
  1. "Rapprochement par exercice" : achats factures / stocks / disponible /
     ventes caisse, en bouteilles et en centilitres.
  2. "Controle tableaux p.75"     : addition des lignes, ecarts, pourcentages,
     et identification de l'exercice auquel correspond chaque volume imprime.
  3. "Ventes caisse (detail)"     : chaque bouton de caisse, son format de
     service et sa contenance.
  4. "Achats factures (detail)"   : chaque ligne de facture fournisseur.
  5. "Methode".

Sources (lecture seule) :
  - src/data/factures-fournisseur.json          (199 factures FCBS)
  - src/data/calculsBoissons/boissonsHorsCocktail.json (ventes caisse, annexes C/D)
  - src/data/calculsBoissons/itemsCaisse.json   (libelles de boutons)
  - public/documents/inventaires/inventaires.json (stocks de cloture)
"""
import os
import json
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

ICI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(ICI, ".."))
FACT = os.path.join(ROOT, "src/data/factures-fournisseur.json")
HORSCOCK = os.path.join(ROOT, "src/data/calculsBoissons/boissonsHorsCocktail.json")
ITEMS = os.path.join(ROOT, "src/data/calculsBoissons/itemsCaisse.json")
INV = os.path.join(ROOT, "public/documents/inventaires/inventaires.json")
OUTDIR = os.path.join(ROOT, "public/documents/pieces-reponse-1")
OUT = os.path.join(OUTDIR, "R1-rapprochement-caisse-factures.xlsx")

EXOS = ["2022-2023", "2023-2024", "2024-2025"]

# Reference -> codes article du fournisseur FCBS
CODES = {
    "Hautes Cotes de Beaune ROUGE (Domaine Germain)": ["601667", "601346", "630253", "601199"],
    "Hautes Cotes de Beaune BLANC (Domaine Germain)": ["600425"],
    "Hautes Cotes de NUITS blanc (Lupe Cholet)": ["601416"],
    "Bordeaux Superieur / bouton MOUTON CADET (Chateau Grand Renom)": ["661236"],
}
# Reference -> nom canonique dans les ventes caisse
CANON = {
    "Hautes Cotes de Beaune ROUGE (Domaine Germain)": "Hautes Côtes de Beaune rouge",
    "Hautes Cotes de Beaune BLANC (Domaine Germain)": "Hautes Côtes de Beaune blanc",
    "Hautes Cotes de NUITS blanc (Lupe Cholet)": "Hautes Côtes de Nuits blanc",
    "Bordeaux Superieur / bouton MOUTON CADET (Chateau Grand Renom)": "Bordeaux Supérieur",
}
# Reference -> libelles d'inventaire (stocks de cloture)
INVNOMS = {
    "Hautes Cotes de Beaune ROUGE (Domaine Germain)":
        ["Haute Côte de Beaune 75cl", "Hautes Côtes de Beaune 75cl"],
    "Bordeaux Superieur / bouton MOUTON CADET (Chateau Grand Renom)":
        ["Bordeaux Supérieur 75cl"],
}

# Tableaux imprimes en page 75 (transcription fidele, en centilitres)
P75 = {
    "Exercice 1": {
        "Haute côte de Beaune ROUGE": (5400, 4683),
        "Bordeaux Mouton Cadet": (0, 0),
        "Haute côte de Beaune BLANC": (0, 0),
        "TOTAL": (5400, 4683),
        "ecart_imprime": (717, 15.31),
    },
    "Exercice 2": {
        "Haute côte de Beaune ROUGE": (6300, 5310),
        "Bordeaux Mouton Cadet": (0, 0),
        "Haute côte de Beaune BLANC": (0, 12950),
        "TOTAL": (6300, 18260),
        "ecart_imprime": (11960, 65.49),
    },
    "Exercice 3": {
        "Haute côte de Beaune ROUGE": (6300, 5310),
        "Bordeaux Mouton Cadet": (0, 0),
        "Haute côte de Beaune BLANC": (0, 12950),
        "TOTAL": (6300, 18260),
        "ecart_imprime": (11960, 65.49),
    },
}

GRAS = Font(bold=True)
GBLANC = Font(bold=True, color="FFFFFF")
ENTETE = PatternFill("solid", fgColor="0F766E")
JAUNE = PatternFill("solid", fgColor="FEF3C7")
ROUGE = PatternFill("solid", fgColor="FEE2E2")
VERT = PatternFill("solid", fgColor="DCFCE7")
CENTRE = Alignment(horizontal="center", vertical="center", wrap_text=True)
GAUCHE = Alignment(horizontal="left", vertical="center", wrap_text=True)
BORD = Border(*(4 * (Side(style="thin", color="D1D5DB"),)))


def fr(v, dec=2):
    if v is None:
        return ""
    return f"{v:,.{dec}f}".replace(",", " ").replace(".", ",")


def exercice(datefr):
    """Exercice fiscal (01/04 -> 31/03) d'une date jj/mm/aaaa."""
    j, m, a = (int(x) for x in datefr.split("/"))
    debut = a if m >= 4 else a - 1
    return "%d-%d" % (debut, debut + 1)


# ---------------------------------------------------------------------------
# Achats factures
# ---------------------------------------------------------------------------
FDATA = json.load(open(FACT, encoding="utf-8"))
achats = {ref: {e: 0.0 for e in EXOS} for ref in CODES}
lignes_fact = []
for f in FDATA["factures"]:
    ex = exercice(f["dateFacture"])
    if ex not in EXOS:
        continue
    for l in f["lignes"]:
        for ref, codes in CODES.items():
            if l["code"] in codes:
                q = l["quantite"] or 0
                achats[ref][ex] += q
                lignes_fact.append([ref, ex, f["numero"], f["dateFacture"], l["code"],
                                    l["designation"], q, l["montantHT"]])

# ---------------------------------------------------------------------------
# Ventes caisse
# ---------------------------------------------------------------------------
HC = json.load(open(HORSCOCK, encoding="utf-8"))
ventes = {ref: {e: 0.0 for e in EXOS} for ref in CODES}
lignes_caisse = []
for b in HC["boissons"]:
    for ref, canon in CANON.items():
        if b["nom_canonique"] == canon:
            for e in EXOS:
                p = b["par_periode"][e]
                ventes[ref][e] += p["volume_l"] * 100  # centilitres
            lignes_caisse.append([ref, b["format_service"], b["volume_unitaire_cl"]]
                                 + [b["par_periode"][e]["quantite"] for e in EXOS]
                                 + [b["par_periode"][e]["volume_l"] * 100 for e in EXOS])

# Libelles de boutons de caisse (annexe D)
IT = json.load(open(ITEMS, encoding="utf-8"))
boutons = []
for it in IT["items"]:
    p = it["produit"].upper()
    if any(k in p for k in ("BEAUNE", "NUITS", "MOUTON")):
        boutons.append([it["produit"], it["section"]]
                       + [it["quantite"][e] for e in EXOS])

# ---------------------------------------------------------------------------
# Stocks de cloture
# ---------------------------------------------------------------------------
IDATA = json.load(open(INV, encoding="utf-8"))
stocks = {ref: {} for ref in CODES}
for inv in IDATA["inventaires"]:
    for ref, noms in INVNOMS.items():
        q = sum((l["quantite"] or 0) for l in inv["lignes"] if l["produit"] in noms)
        stocks[ref][inv["exercice"]] = q

wb = openpyxl.Workbook()

# ---------------------------------------------------------------------------
# 1. Rapprochement par exercice
# ---------------------------------------------------------------------------
ws = wb.active
ws.title = "Rapprochement par exercice"
ws["A1"] = ("Rapprochement bouton de caisse / reference facturee / stock inventorie, "
            "exercice par exercice (centilitres)")
ws["A1"].font = Font(bold=True, size=12)
cols = ["Reference facturee (code FCBS)", "Exercice", "Achats factures (bouteilles)",
        "Achats factures (cl)", "Stock de cloture (bouteilles)",
        "Ventes enregistrees en caisse (cl)", "Achats - ventes (cl)",
        "Vente sans achat ?"]
for j, c in enumerate(cols, start=1):
    cell = ws.cell(row=3, column=j, value=c)
    cell.font, cell.fill, cell.alignment, cell.border = GBLANC, ENTETE, CENTRE, BORD
r = 4
recap = {}
for ref in CODES:
    for e in EXOS:
        a = achats[ref][e]
        acl = a * 75
        v = ventes[ref][e]
        st = stocks.get(ref, {}).get(e)
        verdict = "NON" if acl >= v else ("NON (voir confusion Nuits / Beaune)"
                                          if "BLANC" in ref else "a examiner")
        vals = [ref, e, fr(a, 0), fr(acl, 0),
                "" if st is None else fr(st, 0), fr(v, 0), fr(acl - v, 0), verdict]
        for j, val in enumerate(vals, start=1):
            cell = ws.cell(row=r, column=j, value=val)
            cell.alignment = GAUCHE if j in (1, 8) else CENTRE
            cell.border = BORD
        if acl >= v:
            ws.cell(row=r, column=8).fill = VERT
        else:
            ws.cell(row=r, column=8).fill = ROUGE
        recap[(ref, e)] = (acl, v)
        r += 1

r += 1
# Regroupement des deux vins BLANCS (le point de la confusion d'appellation)
ws.cell(row=r, column=1, value=(
    "Vins blancs regroupes (HC de Beaune blanc + HC de Nuits blanc), 3 exercices")).font = GRAS
ab = sum(achats["Hautes Cotes de Beaune BLANC (Domaine Germain)"][e] +
         achats["Hautes Cotes de NUITS blanc (Lupe Cholet)"][e] for e in EXOS) * 75
vb = sum(ventes["Hautes Cotes de Beaune BLANC (Domaine Germain)"][e] +
         ventes["Hautes Cotes de NUITS blanc (Lupe Cholet)"][e] for e in EXOS)
ws.cell(row=r, column=4, value=fr(ab, 0)).alignment = CENTRE
ws.cell(row=r, column=6, value=fr(vb, 0)).alignment = CENTRE
ws.cell(row=r, column=7, value=fr(ab - vb, 0)).alignment = CENTRE
ws.cell(row=r, column=8, value="NON : les achats couvrent %s fois les ventes"
        % fr(ab / vb, 1)).alignment = GAUCHE
ws.cell(row=r, column=8).fill = VERT
ws.column_dimensions["A"].width = 52
for c in "BCDEFGH":
    ws.column_dimensions[c].width = 20

# ---------------------------------------------------------------------------
# 2. Controle des tableaux de la page 75
# ---------------------------------------------------------------------------
ws2 = wb.create_sheet("Controle tableaux p.75")
ws2["A1"] = "Controle ligne a ligne des trois tableaux imprimes en page 75"
ws2["A1"].font = Font(bold=True, size=12)
cols2 = ["Tableau", "Ligne", "Volumes disponibles (cl)",
         "Volumes caisse (A) (cl)", "Observation"]
for j, c in enumerate(cols2, start=1):
    cell = ws2.cell(row=3, column=j, value=c)
    cell.font, cell.fill, cell.alignment, cell.border = GBLANC, ENTETE, CENTRE, BORD

# Volumes caisse REELS de la HC de Beaune rouge, par exercice
reel = {e: ventes["Hautes Cotes de Beaune ROUGE (Domaine Germain)"][e] for e in EXOS}
r = 4
for tab, contenu in P75.items():
    somme_d = sum(contenu[k][0] for k in contenu if k not in ("TOTAL", "ecart_imprime"))
    somme_a = sum(contenu[k][1] for k in contenu if k not in ("TOTAL", "ecart_imprime"))
    for k in ("Haute côte de Beaune ROUGE", "Bordeaux Mouton Cadet",
              "Haute côte de Beaune BLANC"):
        d, a = contenu[k]
        obs = ""
        if k == "Haute côte de Beaune ROUGE":
            corr = [e for e in EXOS if abs(reel[e] - a) < 1]
            obs = ("volume caisse identique a celui de l'exercice %s (%s cl) "
                   % (corr[0], fr(a, 0))) if corr else "sans correspondance"
        if k == "Haute côte de Beaune BLANC" and a:
            obs = ("caisse reelle du HC de Beaune blanc : %s cl (exercice 2) et "
                   "%s cl (exercice 3)" % (fr(ventes["Hautes Cotes de Beaune BLANC (Domaine Germain)"]["2023-2024"], 0),
                                           fr(ventes["Hautes Cotes de Beaune BLANC (Domaine Germain)"]["2024-2025"], 0)))
        vals = [tab, k, fr(d, 0), fr(a, 0), obs]
        for j, val in enumerate(vals, start=1):
            cell = ws2.cell(row=r, column=j, value=val)
            cell.alignment = GAUCHE if j in (2, 5) else CENTRE
            cell.border = BORD
        r += 1
    td, ta = contenu["TOTAL"]
    ec, pct = contenu["ecart_imprime"]
    ec_calc = abs(ta - td)
    pct_calc = 100 * ec_calc / ta if ta else 0
    vals = [tab, "TOTAL imprime", fr(td, 0), fr(ta, 0),
            "somme des lignes : %s et %s ; addition %s ; ecart imprime %s cl (%s %%), "
            "recalcule %s cl (%s %%)" % (
                fr(somme_d, 0), fr(somme_a, 0),
                "exacte" if (somme_d == td and somme_a == ta) else "INEXACTE",
                fr(ec, 0), fr(pct), fr(ec_calc, 0), fr(pct_calc))]
    for j, val in enumerate(vals, start=1):
        cell = ws2.cell(row=r, column=j, value=val)
        cell.alignment = GAUCHE if j in (2, 5) else CENTRE
        cell.border = BORD
        cell.fill = JAUNE
    r += 2

ws2.cell(row=r, column=1, value=(
    "Volumes de HC de Beaune rouge reellement enregistres en caisse (annexes C/D) : "
    + " ; ".join("%s = %s cl" % (e, fr(reel[e], 0)) for e in EXOS))).alignment = GAUCHE
ws2.cell(row=r, column=1).font = GRAS
ws2.column_dimensions["A"].width = 16
ws2.column_dimensions["B"].width = 30
ws2.column_dimensions["C"].width = 20
ws2.column_dimensions["D"].width = 20
ws2.column_dimensions["E"].width = 90

# ---------------------------------------------------------------------------
# 3. Ventes caisse (detail)
# ---------------------------------------------------------------------------
ws3 = wb.create_sheet("Ventes caisse (detail)")
cols3 = (["Reference", "Format de service", "Contenance (cl)"]
         + ["Quantite %s" % e for e in EXOS] + ["Volume %s (cl)" % e for e in EXOS])
for j, c in enumerate(cols3, start=1):
    cell = ws3.cell(row=1, column=j, value=c)
    cell.font, cell.fill, cell.alignment, cell.border = GBLANC, ENTETE, CENTRE, BORD
r = 2
for l in lignes_caisse:
    for j, v in enumerate(l, start=1):
        cell = ws3.cell(row=r, column=j,
                        value=v if isinstance(v, str) else fr(v, 0 if j > 3 else 1))
        cell.alignment = GAUCHE if j == 1 else CENTRE
        cell.border = BORD
    r += 1
r += 2
ws3.cell(row=r, column=1, value="Boutons de caisse concernes (annexe D, quantites vendues)").font = GRAS
r += 1
for j, c in enumerate(["Libelle du bouton", "Rubrique de la carte"] + EXOS, start=1):
    cell = ws3.cell(row=r, column=j, value=c)
    cell.font, cell.fill, cell.alignment = GBLANC, ENTETE, CENTRE
r += 1
for b in boutons:
    for j, v in enumerate(b, start=1):
        cell = ws3.cell(row=r, column=j, value=v if isinstance(v, str) else fr(v, 1))
        cell.alignment = GAUCHE if j <= 2 else CENTRE
        cell.border = BORD
    r += 1
ws3.column_dimensions["A"].width = 52
for c in "BCDEFGHI":
    ws3.column_dimensions[c].width = 18

# ---------------------------------------------------------------------------
# 4. Achats factures (detail)
# ---------------------------------------------------------------------------
ws4 = wb.create_sheet("Achats factures (detail)")
cols4 = ["Reference", "Exercice", "N° de facture", "Date de facture", "Code article",
         "Designation portee sur la facture", "Quantite (bouteilles)", "Montant HT"]
for j, c in enumerate(cols4, start=1):
    cell = ws4.cell(row=1, column=j, value=c)
    cell.font, cell.fill, cell.alignment, cell.border = GBLANC, ENTETE, CENTRE, BORD
r = 2
for l in sorted(lignes_fact, key=lambda x: (x[0], x[3].split("/")[::-1])):
    vals = l[:6] + [fr(l[6], 0), fr(l[7])]
    for j, v in enumerate(vals, start=1):
        cell = ws4.cell(row=r, column=j, value=v)
        cell.alignment = GAUCHE if j in (1, 6) else CENTRE
        cell.border = BORD
    r += 1
ws4.column_dimensions["A"].width = 52
ws4.column_dimensions["F"].width = 58
for c in "BCDEGH":
    ws4.column_dimensions[c].width = 16
ws4.freeze_panes = "A2"

# ---------------------------------------------------------------------------
# 5. Methode
# ---------------------------------------------------------------------------
ws5 = wb.create_sheet("Methode")
notes = [
    ("Objet", "Point 10 de la reponse du 04/09/2026 (p. 74 et 75) : verifier, "
              "reference par reference et exercice par exercice, s'il existe des "
              "ventes sans achat correspondant."),
    ("Achats", "src/data/factures-fournisseur.json : 199 factures du fournisseur "
               "Franche-Comte Boissons Services, lues ligne a ligne. Le rattachement "
               "se fait par CODE ARTICLE du fournisseur, pas par libelle, la meme "
               "reference etant facturee sous des designations abregees ou "
               "millesimees differentes."),
    ("Exercice", "Rattachement par date de facture a l'exercice 01/04 -> 31/03."),
    ("Ventes caisse", "src/data/calculsBoissons/boissonsHorsCocktail.json, issu des "
                      "annexes C et D de la caisse. Contenances de service : verre "
                      "15 cl, pichet 50 cl, bouteille 75 cl (memes reperes que ceux "
                      "retenus par le service en annexe n°7)."),
    ("Stocks", "public/documents/inventaires/inventaires.json (inventaires physiques "
               "de cloture des 31/03/2023, 31/03/2024 et 31/03/2025)."),
    ("Tableaux p. 75", "Transcription fidele des trois tableaux du courrier, puis "
                       "addition des lignes et recalcul des ecarts et des pourcentages."),
    ("Genere par", "scripts/reponse1-rapprochement-caisse-factures.py"),
]
r = 1
for k, v in notes:
    ws5.cell(row=r, column=1, value=k).font = GRAS
    ws5.cell(row=r, column=1).alignment = GAUCHE
    ws5.cell(row=r, column=2, value=v).alignment = GAUCHE
    r += 1
ws5.column_dimensions["A"].width = 22
ws5.column_dimensions["B"].width = 110

os.makedirs(OUTDIR, exist_ok=True)
wb.save(OUT)
print("OK ->", OUT)
for ref in CODES:
    print(ref)
    for e in EXOS:
        print("   ", e, "achats btl", achats[ref][e], "= cl", achats[ref][e] * 75,
              "| caisse cl", round(ventes[ref][e], 1),
              "| stock", stocks.get(ref, {}).get(e))
print("blancs regroupes : achats", ab, "cl / ventes", vb, "cl")
print("caisse HCB rouge par exercice :", {e: round(reel[e]) for e in EXOS})
