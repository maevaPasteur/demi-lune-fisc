#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reponse1-variation-de-stock-volumes.py

Piece de la reponse au courrier DDFiP 39 du 04/09/2026, point 9 (p. 74)
"Volume disponible gonfle par une variation de stock erronee".

Le service ecarte la demonstration au motif qu'elle "se base sur un montant en
Euros" alors que "la reconstitution ne s'est base que des volumes en stocks".
Ce script refait donc la demonstration EN VOLUMES (litres), a partir des trois
inventaires physiques de cloture, et la met en regard des memes donnees en euros
et de la variation de stock retenue par le service (compte 310200).

Sorties : public/documents/pieces-reponse-1/R1-variation-de-stock-en-volumes.xlsx
  1. "Volumes par cloture"   : litres en stock aux 3 clotures, par categorie.
  2. "Volumes vs euros"      : variation physique (L et EUR) vs variation retenue.
  3. "Detail par produit"    : chaque ligne d'inventaire, contenance, litres.
  4. "Methode"               : sources et conventions.

Sources (lecture seule) :
  - public/documents/inventaires/inventaires.json  (3 inventaires physiques)
  - src/data/analyseBoissons.ts  (variations du compte 310200 retenues par le
    service : -800,83 / -1 029,67 / -273,41 EUR ; transcrites ci-dessous)
"""
import os
import re
import json
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

ICI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(ICI, ".."))
INV = os.path.join(ROOT, "public/documents/inventaires/inventaires.json")
OUTDIR = os.path.join(ROOT, "public/documents/pieces-reponse-1")
OUT = os.path.join(OUTDIR, "R1-variation-de-stock-en-volumes.xlsx")

# Variations du compte de stock boissons retenues par le service
# (Proposition de rectification, tableau de comptabilite matiere ; reprises en
#  annexe n°7-2 pour -1 029,67 EUR).
VARIATION_SERVICE = {
    "2022-2023": -800.83,
    "2023-2024": -1029.67,
    "2024-2025": -273.41,
}

GRAS = Font(bold=True)
GBLANC = Font(bold=True, color="FFFFFF")
ENTETE = PatternFill("solid", fgColor="0F766E")
JAUNE = PatternFill("solid", fgColor="FEF3C7")
ROUGE = PatternFill("solid", fgColor="FEE2E2")
CENTRE = Alignment(horizontal="center", vertical="center", wrap_text=True)
GAUCHE = Alignment(horizontal="left", vertical="center", wrap_text=True)
BORD = Border(*(4 * (Side(style="thin", color="D1D5DB"),)))


def fr(v, dec=2):
    if v is None:
        return ""
    return f"{v:,.{dec}f}".replace(",", " ").replace(".", ",")


def contenance_l(libelle, prix_unitaire=None):
    """Contenance unitaire en litres, lue dans le libelle d'inventaire.

    Exception documentee : les futs de biere Affligem 8 L sont facteures AU LITRE
    par le fournisseur (4,07 a 4,23 EUR le litre). Lorsque le prix unitaire porte
    sur l'inventaire est celui d'un litre et non celui d'un fut (soit environ 8
    fois moins), la quantite inventoriee est deja exprimee en litres : la
    contenance unitaire a retenir est alors de 1 litre, non de 8.
    """
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*(cl|CL|L|l)\b", libelle)
    if not m:
        return None
    v = float(m.group(1).replace(",", "."))
    c = v / 100 if m.group(2).lower() == "cl" else v
    if "ût" in libelle or "ut Affligem" in libelle:
        if prix_unitaire is not None and prix_unitaire < 10:
            return 1.0
    return c


DATA = json.load(open(INV, encoding="utf-8"))
INVENTAIRES = DATA["inventaires"]
DATES = [i["date"] for i in INVENTAIRES]

# ---------------------------------------------------------------------------
# Agregation
# ---------------------------------------------------------------------------
CATS = ["alcool", "boisson_sans_alcool"]
vol = {d: {c: 0.0 for c in CATS} for d in DATES}          # litres, toutes lignes
vol_ex = {d: {c: 0.0 for c in CATS} for d in DATES}        # litres, lignes "exact"
eur = {d: {c: 0.0 for c in CATS} for d in DATES}
sans_contenance = {d: 0 for d in DATES}
detail = []

for inv in INVENTAIRES:
    d = inv["date"]
    for l in inv["lignes"]:
        cat = l["categorie"]
        q = l["quantite"] or 0
        v = l["valeurHT"] or 0
        c = contenance_l(l["produit"], l.get("prixUnitaireHT"))
        eur[d][cat] += v
        if c is None:
            sans_contenance[d] += 1
        else:
            vol[d][cat] += c * q
            if l["fiabilite"] == "exact":
                vol_ex[d][cat] += c * q
        detail.append({
            "date": d, "produit": l["produit"], "categorie": cat,
            "contenance_cl": None if c is None else round(c * 100, 1),
            "quantite": q, "litres": None if c is None else round(c * q, 3),
            "valeurHT": v, "fiabilite": l["fiabilite"],
        })

wb = openpyxl.Workbook()

# ---------------------------------------------------------------------------
# 1. Volumes par cloture
# ---------------------------------------------------------------------------
ws = wb.active
ws.title = "Volumes par cloture"
ws["A1"] = ("Stock physique de boissons aux trois clotures, EN LITRES "
            "(inventaires physiques, contenance lue sur le libelle)")
ws["A1"].font = Font(bold=True, size=12)
cols = ["Poste", "31/03/2023", "31/03/2024", "31/03/2025",
        "Variation 2023-2024", "Variation 2024-2025"]
for j, c in enumerate(cols, start=1):
    cell = ws.cell(row=3, column=j, value=c)
    cell.font, cell.fill, cell.alignment, cell.border = GBLANC, ENTETE, CENTRE, BORD

lignes_vol = [
    ("Alcools et vins (litres)", [vol[d]["alcool"] for d in DATES]),
    ("Boissons sans alcool (litres)", [vol[d]["boisson_sans_alcool"] for d in DATES]),
    ("TOTAL boissons (litres)", [sum(vol[d].values()) for d in DATES]),
    ("dont lignes d'inventaire non annotees (litres)", [sum(vol_ex[d].values()) for d in DATES]),
]
r = 4
for lab, vals in lignes_vol:
    ws.cell(row=r, column=1, value=lab).alignment = GAUCHE
    for j, v in enumerate(vals, start=2):
        ws.cell(row=r, column=j, value=fr(v)).alignment = CENTRE
    ws.cell(row=r, column=5, value=fr(vals[1] - vals[0])).alignment = CENTRE
    ws.cell(row=r, column=6, value=fr(vals[2] - vals[1])).alignment = CENTRE
    if lab.startswith("TOTAL"):
        for j in range(1, 7):
            ws.cell(row=r, column=j).font = GRAS
            ws.cell(row=r, column=j).fill = JAUNE
    for j in range(1, 7):
        ws.cell(row=r, column=j).border = BORD
    r += 1

r += 1
ws.cell(row=r, column=1, value=(
    "Lecture : entre le 31/03/2023 et le 31/03/2024, le stock physique de boissons "
    "AUGMENTE de %s litres. Une augmentation de stock DIMINUE le volume disponible "
    "a la vente ; la variation retenue par le service la fait au contraire augmenter."
    % fr(sum(vol[DATES[1]].values()) - sum(vol[DATES[0]].values()))
)).alignment = GAUCHE
ws.column_dimensions["A"].width = 46
for c in "BCDEF":
    ws.column_dimensions[c].width = 18

# ---------------------------------------------------------------------------
# 2. Volumes vs euros
# ---------------------------------------------------------------------------
ws2 = wb.create_sheet("Volumes vs euros")
ws2["A1"] = ("La meme demonstration dans les deux unites : le sens de la variation "
             "de stock est identique en litres et en euros")
ws2["A1"].font = Font(bold=True, size=12)
cols2 = ["Exercice", "Variation physique (litres)", "Variation physique (EUR HT)",
         "Variation retenue par le service (compte 310200, EUR)",
         "Ecart (EUR)", "Sens"]
for j, c in enumerate(cols2, start=1):
    cell = ws2.cell(row=3, column=j, value=c)
    cell.font, cell.fill, cell.alignment, cell.border = GBLANC, ENTETE, CENTRE, BORD

tot_e = [sum(eur[d].values()) for d in DATES]
tot_v = [sum(vol[d].values()) for d in DATES]
rows2 = [
    ("2022-2023 (cloture 31/03/2023)", None, None, VARIATION_SERVICE["2022-2023"], None,
     "stock d'ouverture au 31/03/2022 non repris dans nos inventaires"),
    ("2023-2024 (cloture 31/03/2024)", tot_v[1] - tot_v[0], tot_e[1] - tot_e[0],
     VARIATION_SERVICE["2023-2024"], None, None),
    ("2024-2025 (cloture 31/03/2025)", tot_v[2] - tot_v[1], tot_e[2] - tot_e[1],
     VARIATION_SERVICE["2024-2025"], None, None),
]
r = 4
ecart_total = 0.0
for lab, dv, de, serv, _, note in rows2:
    ws2.cell(row=r, column=1, value=lab).alignment = GAUCHE
    ws2.cell(row=r, column=2, value=fr(dv)).alignment = CENTRE
    ws2.cell(row=r, column=3, value=fr(de)).alignment = CENTRE
    ws2.cell(row=r, column=4, value=fr(serv)).alignment = CENTRE
    if de is not None:
        ec = de - serv
        ecart_total += ec
        ws2.cell(row=r, column=5, value=fr(ec)).alignment = CENTRE
        ws2.cell(row=r, column=5).fill = ROUGE
        sens = ("stock EN HAUSSE en litres comme en euros, variation retenue NEGATIVE"
                if de > 0 else "meme sens, mais amplitude retenue trop forte")
        ws2.cell(row=r, column=6, value=sens).alignment = GAUCHE
    else:
        ws2.cell(row=r, column=6, value=note).alignment = GAUCHE
    for j in range(1, 7):
        ws2.cell(row=r, column=j).border = BORD
    r += 1

ws2.cell(row=r, column=1, value="Sur-evaluation cumulee du volume disponible (EUR)").font = GRAS
ws2.cell(row=r, column=5, value=fr(ecart_total)).font = GRAS
ws2.cell(row=r, column=5).fill = JAUNE
r += 2

# Fourchette de conversion EUR -> litres (prix d'achat moyen du stock d'alcools)
pl_haut = eur[DATES[1]]["alcool"] / vol[DATES[1]]["alcool"]
pl_bas = eur[DATES[2]]["alcool"] / vol[DATES[2]]["alcool"]
pmin, pmax = min(pl_haut, pl_bas), max(pl_haut, pl_bas)
ws2.cell(row=r, column=1, value=(
    "Conversion de l'ecart en volume : au prix d'achat moyen du stock d'alcools "
    "constate aux inventaires (%s a %s EUR HT le litre), %s EUR representent "
    "environ %s a %s litres de boissons ajoutes au volume disponible."
    % (fr(pmin), fr(pmax), fr(ecart_total), fr(ecart_total / pmax, 0),
       fr(ecart_total / pmin, 0))
)).alignment = GAUCHE
ws2.column_dimensions["A"].width = 40
for c in "BCDEF":
    ws2.column_dimensions[c].width = 24

# ---------------------------------------------------------------------------
# 3. Detail par produit
# ---------------------------------------------------------------------------
ws3 = wb.create_sheet("Detail par produit")
cols3 = ["Cloture", "Produit (libelle d'inventaire)", "Categorie",
         "Contenance unitaire (cl)", "Quantite", "Volume (litres)",
         "Valeur (EUR HT)", "Fiabilite"]
for j, c in enumerate(cols3, start=1):
    cell = ws3.cell(row=1, column=j, value=c)
    cell.font, cell.fill, cell.alignment, cell.border = GBLANC, ENTETE, CENTRE, BORD
r = 2
for d in detail:
    vals = [d["date"], d["produit"], d["categorie"],
            fr(d["contenance_cl"], 1), fr(d["quantite"], 0),
            fr(d["litres"], 3), fr(d["valeurHT"]), d["fiabilite"]]
    for j, v in enumerate(vals, start=1):
        cell = ws3.cell(row=r, column=j, value=v)
        cell.alignment = GAUCHE if j == 2 else CENTRE
        cell.border = BORD
    r += 1
ws3.column_dimensions["A"].width = 14
ws3.column_dimensions["B"].width = 46
for c in "CDEFGH":
    ws3.column_dimensions[c].width = 16
ws3.freeze_panes = "A2"

# ---------------------------------------------------------------------------
# 4. Methode
# ---------------------------------------------------------------------------
ws4 = wb.create_sheet("Methode")
notes = [
    ("Objet", "Refaire en volumes (litres) la demonstration du point 9, le service "
              "objectant que la reponse « se base sur un montant en Euros »."),
    ("Source des volumes", "public/documents/inventaires/inventaires.json : les trois "
                           "inventaires physiques de cloture (31/03/2023, 31/03/2024, "
                           "31/03/2025), transcrits ligne a ligne depuis les PDF."),
    ("Conversion en litres", "La contenance unitaire est lue directement dans le libelle "
                             "de l'inventaire (ex. « Crémant du Jura 75cl » = 0,75 L, "
                             "« Bourgogne Aligoté BIB 10L » = 10 L). Aucune contenance "
                             "n'est supposee."),
    ("Lignes sans contenance", "Cafes, thes et infusions (produits non liquides en stock) "
                               "et lignes de reconciliation : %s au 31/03/2023, %s au "
                               "31/03/2024, %s au 31/03/2025. Elles sont exclues des "
                               "litres, jamais des euros."
                               % tuple(sans_contenance[d] for d in DATES)),
    ("Variation retenue par le service", "-800,83 EUR, -1 029,67 EUR et -273,41 EUR "
                                         "(compte de stock boissons). Le montant de "
                                         "-1 029,67 EUR figure egalement en annexe n°7-2 "
                                         "de la proposition de rectification."),
    ("Genere par", "scripts/reponse1-variation-de-stock-volumes.py"),
]
r = 1
for k, v in notes:
    ws4.cell(row=r, column=1, value=k).font = GRAS
    ws4.cell(row=r, column=1).alignment = GAUCHE
    ws4.cell(row=r, column=2, value=v).alignment = GAUCHE
    r += 1
ws4.column_dimensions["A"].width = 32
ws4.column_dimensions["B"].width = 100

os.makedirs(OUTDIR, exist_ok=True)
wb.save(OUT)
print("OK ->", OUT)
print("Volumes (L) :", {d: round(sum(vol[d].values()), 2) for d in DATES})
print("Euros       :", {d: round(sum(eur[d].values()), 2) for d in DATES})
print("Var L       :", round(tot_v[1] - tot_v[0], 2), round(tot_v[2] - tot_v[1], 2))
print("Var EUR     :", round(tot_e[1] - tot_e[0], 2), round(tot_e[2] - tot_e[1], 2))
print("Ecart EUR   :", round(ecart_total, 2))
print("Prix/L      :", round(pmin, 2), round(pmax, 2))
print("Ecart en L  :", round(ecart_total / pmax), "a", round(ecart_total / pmin))
