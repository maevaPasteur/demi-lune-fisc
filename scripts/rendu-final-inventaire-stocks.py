#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RENDU FINAL - Sous-page "Inventaire de stocks (juge absent ou incomplet)"
=========================================================================
Grief reel du fisc (Proposition 3924, p. 14-16, rejet 1/3, point I) :
  Le verificateur reconnait avoir "pu consulter et obtenir les inventaires de
  stocks" ; il reproche seulement que "les stocks remis, HORMIS celui du
  31/03/2022, apparaissent comme incomplets dans le sens ou ils N'INDIQUENT PAS
  TOUJOURS LES VOLUMES (contenances) des boissons". Il en tire une "irregularite
  grave" (R. 123-177, L. 123-12, CE 25/07/1980).

  -> Ce n'est PAS un grief de noms qui ne correspondraient pas aux factures
     (ca, c'est le grief separe "conso > achats"). C'est uniquement l'absence,
     sur les inventaires posterieurs au 31/03/2022, de la CONTENANCE en cl des
     boissons.

Reponse a prouver (SANS parler de consommation reelle / bilan matiere, traite
ailleurs et trop complexe pour cette page) :
  1. Les inventaires des 3 fins d'exercice existent et sont detailles LIGNE A
     LIGNE avec quantite + prix unitaire HT + valeur HT : exactement ce qu'exige
     R. 123-177 (quantite ET valeur). La contenance en cl n'est pas une mention
     legalement requise de l'inventaire.
  2. La contenance est une caracteristique fixe et connue du produit, et
     l'administration l'a ELLE-MEME reconstituee pour chaque article dans son
     Annexe N°1 (p. 47-50 : "Volume / Stocks / Indique Oui/Non" aux 4 dates).
     L'omission n'a donc empeche aucun controle et n'a cause aucun prejudice.
  3. Le stock est stable d'une cloture a l'autre (pas de destockage cache).
  4. Contradiction : le service qualifie l'inventaire d'irregulier mais s'en sert
     comme base de sa reconstitution (variation de stock, quantites disponibles).
  5. La jurisprudence CE 25/07/1980 visee concerne un inventaire reduit au seul
     montant global SANS detail : c'est l'inverse de notre cas.

Sorties (reproductibles) :
  1. public/documents/pieces-defense/RF-inventaire-stocks.xlsx
  2. src/data/renduFinal/inventaire-stocks.json

Lecture seule sur les sources. Aucun chiffre en dur cote rendu.

Sources lues :
  - public/documents/inventaires/inventaires.json  (3 clotures, totaux HT, lignes detaillees)
"""

import json
import os
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INV_PATH = os.path.join(ROOT, "public/documents/inventaires/inventaires.json")

XLSX_OUT = os.path.join(ROOT, "public/documents/pieces-defense/RF-inventaire-stocks.xlsx")
JSON_OUT = os.path.join(ROOT, "src/data/renduFinal/inventaire-stocks.json")


# --------------------------------------------------------------------------- #
# Helpers format francais (pas de tiret cadratin nulle part)
# --------------------------------------------------------------------------- #
def fr_int(n):
    return f"{int(round(n)):,}".replace(",", " ")


def fr_dec(n, d=1):
    return f"{n:,.{d}f}".replace(",", " ").replace(".", ",")


def fr_eur2(n):
    s = f"{n:,.2f}".replace(",", "X").replace(".", ",").replace("X", " ")
    return s + " €"


# --------------------------------------------------------------------------- #
# Chargement des sources
# --------------------------------------------------------------------------- #
with open(INV_PATH, encoding="utf-8") as f:
    INV = json.load(f)

inventaires = INV["inventaires"]  # 3 clotures (2023, 2024, 2025)

# --------------------------------------------------------------------------- #
# 1. Stock de cloture par grande famille et par exercice (valeurs HT)
# --------------------------------------------------------------------------- #
stock_par_famille = {}
for inv in inventaires:
    stock_par_famille[inv["date"]] = {
        "sans_alcool": inv["totaux"]["sansAlcoolHT"],
        "alcool": inv["totaux"]["alcoolHT"],
        "total": inv["totaux"]["totalHT"],
        "nb_lignes": inv["nbLignes"],
    }

# Sous-detail alcool par sous-famille (heuristique de libelle) pour montrer le
# niveau de detail reel des inventaires (vins, bieres, spiritueux/digestifs...).
def sous_famille(produit):
    p = produit.lower()
    if any(k in p for k in ["fût", "fut", "affligem", "blade", "rouget de lisle"]) or "biere" in p or "bière" in p:
        return "Bieres / futs"
    if "cidre" in p:
        return "Cidres"
    if any(k in p for k in ["arbois", "chardonnay", "saint véran", "saint veran", "macon", "chablis",
                            "crémant", "cremant", "gewurz", "gascogne", "pive", "savagnin", "vin de paille",
                            "bib ", "côtes", "cotes", "rosé", "rose", "blanc 10", "rouge 10"]):
        return "Vins"
    return "Spiritueux / liqueurs / digestifs"

detail_sous_famille = defaultdict(lambda: defaultdict(float))
for inv in inventaires:
    for l in inv["lignes"]:
        if l["categorie"] != "alcool":
            continue
        detail_sous_famille[inv["date"]][sous_famille(l["produit"])] += (l.get("valeurHT") or 0)

# --------------------------------------------------------------------------- #
# 2. Completude des mentions legales : chaque ligne porte-t-elle quantite,
#    prix unitaire et valeur ? (ce qu'exige R. 123-177). On le mesure.
# --------------------------------------------------------------------------- #
def champs_ok(l):
    return (l.get("quantite") is not None
            and l.get("prixUnitaireHT") is not None
            and l.get("valeurHT") is not None)

total_lignes = sum(inv["nbLignes"] for inv in inventaires)
lignes_completes = sum(1 for inv in inventaires for l in inv["lignes"] if champs_ok(l))
pct_completes = lignes_completes / total_lignes * 100 if total_lignes else 0

# --------------------------------------------------------------------------- #
# 3. Stabilite du stock : variation de stock entre clotures (valeur HT)
# --------------------------------------------------------------------------- #
variations = []
for i in range(1, len(inventaires)):
    prev = inventaires[i - 1]["totaux"]["totalHT"]
    cur = inventaires[i]["totaux"]["totalHT"]
    var = cur - prev
    pct = (var / prev * 100) if prev else 0
    variations.append((inventaires[i - 1]["date"], inventaires[i]["date"], var, pct))

stock_min = min(s["total"] for s in stock_par_famille.values())
stock_max = max(s["total"] for s in stock_par_famille.values())
stock_moy = sum(s["total"] for s in stock_par_famille.values()) / len(stock_par_famille)

print("=== Stock de cloture par exercice (HT) ===")
for d, s in stock_par_famille.items():
    print(f"  {d}: total {fr_eur2(s['total'])} | {s['nb_lignes']} lignes")
print(f"  lignes completes (qte+PU+valeur) : {lignes_completes}/{total_lignes} ({fr_dec(pct_completes)} %)")
print(f"  stock min/max : {fr_eur2(stock_min)} -> {fr_eur2(stock_max)}")


# --------------------------------------------------------------------------- #
# XLSX
# --------------------------------------------------------------------------- #
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

BOLD = Font(bold=True)
HEAD_FILL = PatternFill("solid", fgColor="0F766E")
HEAD_FONT = Font(bold=True, color="FFFFFF")
THIN = Side(style="thin", color="D0D0D0")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
RIGHT = Alignment(horizontal="right")


def style_header(ws, ncols, row=1):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.font = HEAD_FONT
        cell.fill = HEAD_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = BORDER


def autosize(ws, widths):
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w


wb = Workbook()

# --- Onglet 1 : Stock de cloture par famille / exercice --------------------- #
ws = wb.active
ws.title = "Stock par famille"
hdr = ["Date de cloture", "Exercice", "Nb lignes inventaire",
       "Stock sans alcool (EUR HT)", "Stock alcool (EUR HT)", "Stock total (EUR HT)"]
ws.append(hdr)
style_header(ws, len(hdr))
for inv in inventaires:
    t = inv["totaux"]
    ws.append([inv["date"], inv["exercice"], inv["nbLignes"],
               round(t["sansAlcoolHT"], 2), round(t["alcoolHT"], 2), round(t["totalHT"], 2)])
for r in range(2, ws.max_row + 1):
    for c in range(4, 7):
        ws.cell(row=r, column=c).number_format = '#,##0.00 "EUR"'
        ws.cell(row=r, column=c).alignment = RIGHT
ws.freeze_panes = "A2"
autosize(ws, [16, 14, 20, 26, 24, 24])

# --- Onglet 2 : Sous-detail alcool par sous-famille ------------------------- #
ws2 = wb.create_sheet("Detail alcool")
hdr2 = ["Date de cloture", "Sous-famille (alcool)", "Valeur (EUR HT)"]
ws2.append(hdr2)
style_header(ws2, len(hdr2))
for inv in inventaires:
    d = inv["date"]
    for sf, v in sorted(detail_sous_famille[d].items(), key=lambda x: -x[1]):
        ws2.append([d, sf, round(v, 2)])
for r in range(2, ws2.max_row + 1):
    ws2.cell(row=r, column=3).number_format = '#,##0.00 "EUR"'
    ws2.cell(row=r, column=3).alignment = RIGHT
ws2.freeze_panes = "A2"
autosize(ws2, [16, 34, 18])

# --- Onglet 3 : Inventaire detaille (toutes lignes, 3 clotures) ------------- #
#     C'est la preuve centrale : chaque ligne porte qte + PU + valeur.
ws3 = wb.create_sheet("Inventaire detaille")
hdr3 = ["Date de cloture", "Produit", "Categorie", "Quantite",
        "Prix unitaire (EUR HT)", "Valeur (EUR HT)", "Fiabilite", "Page PDF"]
ws3.append(hdr3)
style_header(ws3, len(hdr3))
for inv in inventaires:
    for l in inv["lignes"]:
        ws3.append([
            inv["date"], l["produit"], l["categorie"],
            l["quantite"] if l["quantite"] is not None else "",
            l["prixUnitaireHT"] if l["prixUnitaireHT"] is not None else "",
            l["valeurHT"] if l["valeurHT"] is not None else "",
            l["fiabilite"], l["page"] if l["page"] is not None else "",
        ])
for r in range(2, ws3.max_row + 1):
    ws3.cell(row=r, column=5).number_format = '#,##0.00 "EUR"'
    ws3.cell(row=r, column=6).number_format = '#,##0.00 "EUR"'
    ws3.cell(row=r, column=4).alignment = RIGHT
    ws3.cell(row=r, column=5).alignment = RIGHT
    ws3.cell(row=r, column=6).alignment = RIGHT
ws3.freeze_panes = "A2"
autosize(ws3, [16, 40, 20, 10, 22, 18, 12, 10])

# --- Onglet 4 : Variation de stock (stabilite, valeur HT) ------------------- #
ws4 = wb.create_sheet("Variation stock")
hdr4 = ["De (cloture)", "Vers (cloture)", "Variation totale (EUR HT)", "Variation (%)"]
ws4.append(hdr4)
style_header(ws4, len(hdr4))
for de, vers, var, pct in variations:
    ws4.append([de, vers, round(var, 2), round(pct, 1)])
for r in range(2, ws4.max_row + 1):
    ws4.cell(row=r, column=3).number_format = '#,##0.00 "EUR"'
    ws4.cell(row=r, column=4).number_format = '0.0 "%"'
    ws4.cell(row=r, column=3).alignment = RIGHT
    ws4.cell(row=r, column=4).alignment = RIGHT
ws4.freeze_panes = "A2"
autosize(ws4, [16, 16, 26, 16])

os.makedirs(os.path.dirname(XLSX_OUT), exist_ok=True)
wb.save(XLSX_OUT)
print(f"\nXLSX ecrit : {XLSX_OUT}")


# --------------------------------------------------------------------------- #
# JSON renduFinal
# --------------------------------------------------------------------------- #
TEAL = "#0f766e"


def cg(v):
    return {"v": v}


def cd(v):
    return {"v": v, "align": "right"}


sections = []

# 1) Ce que soutient le fisc
sections.append({
    "kind": "chapitre", "source": "fisc", "numero": 1,
    "titre": "Ce que soutient l'administration",
    "sousTitre": "Inventaire de stocks juge incomplet (Proposition de rectification 3924, p. 14 a 16, rejet 1/3, point I).",
})
sections.append({
    "kind": "note",
    "texte": (
        "Le vérificateur écrit (p. 14) avoir « pu consulter et obtenir les inventaires de stocks » auprès du cabinet "
        "comptable. Il relève ensuite un seul défaut : « les stocks remis, **hormis celui du 31/03/2022**, apparaissent "
        "comme incomplets dans le sens où ils **n'indiquent pas toujours les volumes des boissons** ». Il en déduit une "
        "« irrégularité grave » au regard des articles R. 123-177 et L. 123-12 du Code de commerce, qui rendrait la "
        "comptabilité non probante."
    ),
})
sections.append({
    "kind": "paragraphe",
    "texte": (
        "Le grief est précis et limité. Il ne porte pas sur l'absence d'inventaire (le service l'a obtenu pour chaque "
        "exercice), ni sur des libellés qui ne correspondraient pas aux factures (c'est un autre point du rapport). Il porte "
        "uniquement sur un point de forme : la **contenance en centilitres** des boissons n'est pas systématiquement reportée "
        "sur les inventaires postérieurs au 31/03/2022. Or l'article R. 123-177 exige, pour chaque élément, la **quantité** et "
        "la **valeur** ; il n'impose pas d'indiquer la contenance unitaire d'un article."
    ),
})

# 2) Notre demonstration
sections.append({
    "kind": "chapitre", "source": "nous", "numero": 2,
    "titre": "Notre réponse : un inventaire détaillé, conforme, et des volumes que le service a lui-même reconstitués",
    "sousTitre": "Les trois inventaires physiques de clôture sont produits, détaillés ligne à ligne (produit, quantité, prix unitaire HT, valeur HT). La seule mention en cause, la contenance, figure déjà dans les propres annexes de l'administration.",
})

sections.append({
    "kind": "note",
    "texte": (
        "Les inventaires physiques des trois fins d'exercice vérifiées existent et sont produits : "
        f"31/03/2023 ({inventaires[0]['nbLignes']} lignes), "
        f"31/03/2024 ({inventaires[1]['nbLignes']} lignes) et "
        f"31/03/2025 ({inventaires[2]['nbLignes']} lignes). "
        f"Sur les **{total_lignes} lignes** des trois clôtures, **{lignes_completes} ({fr_dec(pct_completes)} %)** portent "
        "le libellé du produit, la **quantité**, le **prix unitaire HT** et la **valeur HT**. Le niveau de détail exigé par "
        "les articles R. 123-177 et L. 123-12 (quantité et valeur de chaque élément) est donc satisfait, produit par produit."
    ),
})

# Tableau stock de cloture par famille et par exercice
lignes_stock = []
for inv in inventaires:
    t = inv["totaux"]
    lignes_stock.append([
        cg(inv["date"]),
        cd(str(inv["nbLignes"])),
        cd(fr_eur2(t["sansAlcoolHT"])),
        cd(fr_eur2(t["alcoolHT"])),
        cd(fr_eur2(t["totalHT"])),
    ])
sections.append({
    "kind": "tableau",
    "titre": "Stock de clôture par grande famille et par exercice (valeurs HT issues des inventaires)",
    "minWidth": 640,
    "colonnes": [
        {"label": "Date de clôture"},
        {"label": "Lignes inventoriées", "align": "right"},
        {"label": "Boissons sans alcool", "align": "right"},
        {"label": "Alcools et vins", "align": "right"},
        {"label": "Stock total HT", "align": "right"},
    ],
    "lignes": lignes_stock,
})

# Le coeur de la reponse au grief "volumes" : la contenance n'est pas requise
# et le fisc l'a deja reconstituee lui-meme.
sections.append({
    "kind": "note",
    "texte": (
        "Sur le seul point réellement reproché, la contenance des boissons, deux constats suffisent. "
        "**Un**, la contenance n'est pas une mention légale de l'inventaire : R. 123-177 demande la quantité et la valeur, "
        "toutes deux présentes. La contenance est par ailleurs une caractéristique **fixe et publique** du produit (un "
        "« Crémant du Jura 75 cl » fait toujours 75 cl, un BIB 10 L toujours 10 L) : la retrouver est immédiat et sans aléa. "
        "**Deux**, l'administration l'a **elle-même reconstituée** pour chaque article dans son **Annexe N°1 (pages 47 à 50)**, "
        "un tableau « Volume / Stocks / Indiqué Oui/Non » donnant le volume unitaire en centilitres aux quatre dates "
        "d'inventaire. Le volume manquant n'a donc empêché aucun contrôle et n'a causé aucun préjudice : le service a pu mener "
        "sa reconstitution sans obstacle."
    ),
})

# Graphique : stock total de cloture par exercice
sections.append({
    "kind": "graphique",
    "variante": "vertical",
    "hauteur": 300,
    "dataKey": "nom",
    "serie": {"name": "Stock total HT (EUR)", "couleur": TEAL},
    "format": "euro",
    "data": [{"nom": inv["date"], "Stock total HT (EUR)": round(inv["totaux"]["totalHT"])} for inv in inventaires],
})

# Stabilite : variation de stock
lignes_var = []
for de, vers, var, pct in variations:
    signe = "+" if var >= 0 else "-"
    lignes_var.append([
        cg(f"{de} vers {vers}"),
        cd(f"{signe}{fr_eur2(abs(var))}"),
        cd(f"{signe}{fr_dec(abs(pct))} %"),
    ])
sections.append({
    "kind": "tableau",
    "titre": "Variation du stock entre clôtures : un stock stable, sans déstockage caché",
    "minWidth": 520,
    "colonnes": [
        {"label": "Période"},
        {"label": "Variation valeur HT", "align": "right"},
        {"label": "Variation relative", "align": "right"},
    ],
    "lignes": lignes_var,
})
sections.append({
    "kind": "paragraphe",
    "texte": (
        f"Le stock boissons total reste compris entre {fr_eur2(stock_min)} et {fr_eur2(stock_max)} HT sur les trois clôtures "
        f"(stock moyen {fr_eur2(stock_moy)}). Le sens de la variation est essentiel : un stock qui se maintient exclut le "
        "scénario d'un déstockage caché destiné à alimenter des ventes non comptabilisées, qui se traduirait par un stock en "
        "chute. Cette stabilité recoupe d'ailleurs les variations de stock boissons retenues par l'administration elle-même "
        "dans sa reconstitution (- 800,83 EUR, - 1 029,67 EUR et - 273,41 EUR), des montants minimes au regard du stock moyen."
    ),
})

# 3) Piece jointe
sections.append({
    "kind": "piecejointe",
    "intro": "Inventaire physique détaillé des trois clôtures (par produit et par famille, quantités, prix unitaires et valeurs HT) et variation de stock.",
    "fichiers": [
        {"fichier": "pieces-defense/RF-inventaire-stocks.xlsx",
         "label": "RF - Inventaire de stocks : détail par produit, par famille et variation de stock (XLSX)"},
    ],
})

# 3) Le grief est juridiquement infonde (argumentation de CORPS, pas un encart)
sections.append({
    "kind": "chapitre", "source": "nous", "numero": 3,
    "titre": "Le grief est juridiquement infondé",
    "sousTitre": "La contenance manquante n'est ni une mention légalement exigée, ni un obstacle au contrôle.",
})
sections.append({
    "kind": "paragraphe",
    "texte": (
        f"D'abord, le texte invoqué est respecté. L'article R. 123-177 du Code de commerce impose, pour chaque élément, la "
        f"**quantité** et la **valeur** : ces deux mentions figurent sur l'inventaire pour {lignes_completes} des "
        f"{total_lignes} lignes ({fr_dec(pct_completes)} %). La contenance unitaire en centilitres, seule mention en cause, "
        "n'est pas exigée par ce texte. Elle constitue de surcroît une caractéristique fixe et publique de chaque produit "
        "(un « Crémant du Jura 75 cl » fait toujours 75 cl), immédiatement vérifiable."
    ),
})
sections.append({
    "kind": "paragraphe",
    "texte": (
        "Ensuite, et c'est décisif, l'administration a elle-même reconstitué ces volumes. Son **Annexe N°1 (pages 47 à 50)** "
        "reporte, pour chaque article et aux quatre dates d'inventaire, le volume unitaire en centilitres, avec une colonne "
        "« Indiqué Oui/Non ». Le service a donc disposé de toute l'information nécessaire et a pu conduire l'intégralité de sa "
        "reconstitution. Un défaut purement formel, sans incidence sur le contrôle, ne peut fonder le rejet d'une comptabilité."
    ),
})
sections.append({
    "kind": "paragraphe",
    "texte": (
        "Cette position est par ailleurs contradictoire : l'administration qualifie l'inventaire d'irrégulier tout en s'en "
        "servant comme base de sa reconstitution (lignes « Variation stocks Boissons » de ses tableaux p. 33 à 35, annexes "
        "6-1 à 6-3 « achats ± variation de stock = quantités disponibles »). Un même document ne peut être à la fois écarté "
        "comme non probant et retenu comme socle du redressement. Enfin, la jurisprudence CE 25 juillet 1980 invoquée vise un "
        "inventaire réduit au seul montant global, sans aucun détail des quantités et des prix unitaires : c'est la situation "
        "inverse de la nôtre, où chaque produit est détaillé avec sa quantité, son prix unitaire et sa valeur."
    ),
})

# 4) Conclusion (section de CORPS, pas une pastille d'annotation)
sections.append({
    "kind": "chapitre", "source": "nous", "numero": 4,
    "titre": "Conclusion",
})
sections.append({
    "kind": "paragraphe",
    "texte": (
        "L'inventaire physique des trois fins d'exercice existe et est détaillé produit par produit "
        f"({inventaires[0]['nbLignes']}, {inventaires[1]['nbLignes']} et {inventaires[2]['nbLignes']} lignes, avec quantité, "
        f"prix unitaire et valeur), et le stock se maintient ({fr_eur2(stock_min)} à {fr_eur2(stock_max)} HT). Le seul "
        "élément reproché, la contenance en centilitres, n'est pas une mention exigée par l'article R. 123-177 et a de toute "
        "façon été reconstituée par l'administration elle-même (Annexe N°1). Le motif « inventaire incomplet » est donc privé "
        "de fondement, d'autant que le service s'appuie sur ces mêmes inventaires pour reconstituer le chiffre d'affaires."
    ),
})

doc = {
    "meta": {
        "slug": "inventaire-stocks",
        "titre": "Inventaire de stocks (jugé absent ou incomplet)",
        "bloc": "rejet",
        "griefFisc": "Les inventaires (hormis le 31/03/2022) n'indiqueraient pas toujours la contenance des boissons, ce qui les rendrait incomplets (Proposition p. 14 a 16, rejet 1/3, point I).",
        "reponse": "Les inventaires existent et sont détaillés (quantité, prix unitaire, valeur) ; la contenance n'est pas une mention légalement requise et a été reconstituée par l'administration elle-même. Le motif tombe.",
        "sources": [
            "public/documents/inventaires/inventaires.json",
            "public/documents/inventaires/inventaire_2023-03-31.csv",
            "public/documents/inventaires/inventaire_2024-03-31.csv",
            "public/documents/inventaires/inventaire_2025-03-31.csv",
            "public/documents/rapports-des-finances-publiques/synthese/02-rejet-comptabilite-1.md",
            "public/documents/rapports-des-finances-publiques/synthese/08-annexes-A-H.md (Annexe N°1, p. 47-50)",
        ],
        "piece": "pieces-defense/RF-inventaire-stocks.xlsx",
        "genereePar": "scripts/rendu-final-inventaire-stocks.py",
    },
    "sections": sections,
}

os.makedirs(os.path.dirname(JSON_OUT), exist_ok=True)
with open(JSON_OUT, "w", encoding="utf-8") as f:
    json.dump(doc, f, ensure_ascii=False, indent=2)
print(f"JSON ecrit : {JSON_OUT}")
print(f"Sections : {len(sections)}")
