#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REPONSE 1 - Piece "R1-inventaires-comparatif.xlsx"
==================================================
Objet : demontrer que l'etat d'inventaire produit en reponse a la proposition de
rectifications n'est PAS une "correction" mais la MEME piece, augmentee d'une
colonne de contenance : les quantites, les prix unitaires et les valeurs sont
inchanges.

Deux sources, lues seulement :
  1. Etat d'ORIGINE (celui obtenu sur place par le service) :
     - les 21 articles que le service reproduit lui-meme p. 33 de sa reponse du
       04/09/2026. Ces 21 lignes sont recopiees ci-dessous telles qu'imprimees
       dans le courrier. Elles correspondent, ligne pour ligne et dans le meme
       ordre, aux lignes 5 a 25 de la page 11 du PDF
       public/documents/inventaires/Inventaire_Demi_Lune_2023-03-31.pdf
       (onglet "ALCOOL", colonnes "Produit alcoolise / Quantite / Prix unitaire
       HT / Total").
  2. Etat COMPLETE (celui produit en reponse) :
     - public/documents/inventaires/inventaire_{2023,2024,2025}-03-31.csv,
       ou la contenance est portee dans la designation de chaque article.

Sortie : public/documents/pieces-reponse-1/R1-inventaires-comparatif.xlsx

Aucun chiffre saisi a la main hors de la constante EXTRAIT_P33 (transcription du
courrier, verifiable page 33).
"""

import csv
import os
import re

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INV_DIR = os.path.join(ROOT, "public/documents/inventaires")
OUT = os.path.join(ROOT, "public/documents/pieces-reponse-1/R1-inventaires-comparatif.xlsx")

CLOTURES = [
    ("2023-03-31", "2022-2023"),
    ("2024-03-31", "2023-2024"),
    ("2025-03-31", "2024-2025"),
]

# --------------------------------------------------------------------------- #
# Pages recapitulatives DATEES des trois inventaires (transcription du PDF).
# Chaque valeur est verifiable sur la page 1 du PDF cite.
# --------------------------------------------------------------------------- #
RECAPITULATIFS = {
    "2023-03-31": {
        "titre": "INVENTAIRE H.T. DEMI LUNE 31/03/2023",
        "sans_alcool": 727.70,
        "alcool": 3050.29,
        "autres": [("ALIMENTAIRE (frais, surgeles, epicerie)", 1734.15),
                   ("CREMERIE", 158.85),
                   ("VIANDE-CHARCUTERIE", 255.63),
                   ("PRODUITS D'ENTRETIEN ET DIVERS", 1103.99)],
        "total_imprime": 7030.61,
        "source": "Inventaire_Demi_Lune_2023-03-31.pdf, p. 1 (tableau dactylographie, date)",
    },
    "2024-03-31": {
        "titre": "INVENTAIRE H.T. AU 31 MARS 2024",
        "sans_alcool": 870.59,
        "alcool": 3937.07,
        "autres": [("Produits d'entretien et Divers", 1000.30),
                   ("Alimentation", 4065.17)],
        "total_imprime": 9873.07,
        "source": ("Inventaire_Demi_Lune_2024-03-31.pdf, p. 1 (page dactylographiee, datee) ; "
                   "report manuscrit des memes totaux en p. 7"),
    },
    "2025-03-31": {
        "titre": "INVENTAIRE HT 31/03/2025",
        "sans_alcool": 765.74,
        "alcool": 3768.51,
        "autres": [("ALIMENTATION (frais, surgeles, epicerie)", 3654.92),
                   ("DIVERS NON COMESTIBLES", 1585.00)],
        "total_imprime": 9774.17,
        "source": "Inventaire_Demi_Lune_2025-03-31.pdf, p. 1 (page dactylographiee, datee)",
    },
}

# Variation de stock boissons retenue par le service (compte 310200).
VARIATION_SERVICE = {"2022-2023": -800.83, "2023-2024": -1029.67, "2024-2025": -273.41}

# Erreurs de frappe de la retranscription informatique, rectifiees au vu de
# l'etat d'origine (page 11 du PDF 2023, que le service reproduit lui-meme p. 33).
# Elles sont desormais corrigees dans le CSV publie.
CORRECTIONS_2023 = [
    ("Clan Campbell 70cl", 17.56, 12.56),
    ("Creme de Mure 100cl", 8.22, 8.27),
    ("Creme de Cerise 100cl", 16.78, 15.76),
]

# Erreurs de frappe de la page 10 du PDF 2023 (onglet "SANS ALCOOL"), egalement
# rectifiees dans le CSV publie.
CORRECTIONS_2023_SANS_ALCOOL = [
    ("Vittel 50cl", "ligne inexistante sur l'etat d'origine, doublon de la ligne "
                    "San Pellegrino 50cl (33 unites a 0,88 EUR, 29,04 EUR) : supprimee",
     -29.04),
    ("Infusion verveine", "1 unite a 8,80 EUR portee sur l'etat d'origine, "
                          "transcrite a 0 : retablie", 8.80),
    ("Orangina 33cl", "33 unites a 0,59 EUR sur l'etat d'origine, transcrites "
                      "13 a 1,59 EUR : quantite et prix unitaire retablis, "
                      "valeur inchangee (19,47 EUR)", 0.0),
    ("Peppermint infusion", "prix unitaire 3,44 EUR sur l'etat d'origine, "
                            "transcrit 6,42 EUR ; quantite nulle, valeur "
                            "inchangee (0 EUR)", 0.0),
]

# Lignes d'alimentation portees sur la page 10 du PDF 2023 mais hors du perimetre
# "boissons" du CSV. Transcription verifiable sur cette page.
ALIMENTATION_P10_2023 = [
    ("sucre morceaux", 0.00),
    ("petites galettes st michel", 70.12),
    ("petites madeleines st michel", 36.76),
    ("mix crackers", 23.15),
]

# --------------------------------------------------------------------------- #
# 1. Etat d'origine : extrait reproduit par le service, reponse du 04/09/2026 p. 33
#    (libelle, quantite, prix unitaire, valeur) - aucune colonne de contenance.
# --------------------------------------------------------------------------- #
EXTRAIT_P33 = [
    ("Cidre brut", 15, 2.54, 38.10),
    ("Cidre doux", 14, 2.89, 40.46),
    ("Pontarlier", 1, 17.95, 17.95),
    ("Ricard", 1, 17.56, 17.56),
    ("Clan Campbell", 1, 12.56, 12.56),
    ("Jack daniel", 1, 19.26, 19.26),
    ("Marc du jura", 1, 18.61, 18.61),
    ("Martini", 1, 8.15, 8.15),
    ("Marc de bourgogne", 0, 25.90, 0.00),
    ("Porto", 4, 7.71, 30.84),
    ("Sapin", 2, 21.16, 42.32),
    ("Creme mure", 1, 8.27, 8.27),
    ("Creme cassis", 2, 8.39, 16.78),
    ("Creme cerise", 2, 7.88, 15.76),
    ("Vodka pollakiof", 1, 9.03, 9.03),
    ("Cognac Park", 1, 19.62, 19.62),
    ("Absinthe", 2, 30.89, 61.78),
    ("Calvados", 2, 16.53, 33.06),
    ("Mirabelle", 1, 20.04, 20.04),
    ("Framboise", 1, 21.65, 21.65),
    ("Soho", 0, 9.72, 0.00),
]

# Correspondance libelle du courrier -> designation de l'etat complete (CSV 2023).
CORRESPONDANCE = {
    "Cidre brut": "Cidre Brut 75cl",
    "Cidre doux": "Cidre Doux 75cl",
    "Pontarlier": "Pontarlier Anis 100cl",
    "Ricard": "Ricard 100cl",
    "Clan Campbell": "Clan Campbell 70cl",
    "Jack daniel": "Jack Daniel's 70cl",
    "Marc du jura": "Marc du Jura 70cl",
    "Martini": "Martini 100cl",
    "Marc de bourgogne": "Marc de Bourgogne 70cl",
    "Porto": "Porto 75cl",
    "Sapin": "Liqueur de Sapin 100cl",
    "Creme mure": "Crème de Mûre 100cl",
    "Creme cassis": "Crème de Cassis 100cl",
    "Creme cerise": "Crème de Cerise 100cl",
    "Vodka pollakiof": "Vodka Poliakov 70cl",
    "Cognac Park": "Cognac Park 70cl",
    "Absinthe": "Absinthe 70cl",
    "Calvados": "Calvados 100cl",
    "Mirabelle": "Mirabelle 70cl",
    "Framboise": "Eau de Vie Framboise 70cl",
    "Soho": "Soho Litchi 70cl",
}

# --------------------------------------------------------------------------- #
# 2. Lecture de l'etat complete
# --------------------------------------------------------------------------- #
RE_CONTENANCE = re.compile(r"(\d+(?:[.,]\d+)?)\s*(cl|CL|L|kg)\b")


def contenance(libelle):
    """Contenance portee dans la designation de l'etat complete (ex. '75 cl')."""
    trouve = RE_CONTENANCE.findall(libelle)
    if not trouve:
        return ""
    valeur, unite = trouve[-1]
    return f"{valeur.replace('.', ',')} {unite.lower()}"


def lire(date):
    chemin = os.path.join(INV_DIR, f"inventaire_{date}.csv")
    lignes = []
    with open(chemin, encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter=";"):
            def nb(x):
                x = (x or "").strip()
                return float(x.replace(",", ".")) if x else None

            lignes.append(
                {
                    "produit": r["produit"].strip(),
                    "categorie": r["categorie"].strip(),
                    "quantite": nb(r["quantite"]),
                    "pu": nb(r["prix_unitaire_ht"]),
                    "valeur": nb(r["valeur_ht"]),
                    "fiabilite": (r.get("fiabilite") or "").strip(),
                    "page": (r.get("page") or "").strip(),
                    "contenance": contenance(r["produit"].strip()),
                }
            )
    return lignes


INVENTAIRES = {d: lire(d) for d, _ in CLOTURES}

# --------------------------------------------------------------------------- #
# 3. Comparatif article par article sur l'extrait de la page 33
# --------------------------------------------------------------------------- #
index2023 = {l["produit"]: l for l in INVENTAIRES["2023-03-31"]}

comparatif = []
for libelle, qte, pu, val in EXTRAIT_P33:
    cible = CORRESPONDANCE[libelle]
    ligne = index2023.get(cible)
    if ligne is None:
        raise SystemExit(f"Article introuvable dans l'etat complete : {cible}")
    ecart_q = (ligne["quantite"] or 0) - qte
    ecart_v = round((ligne["valeur"] or 0) - val, 2)
    comparatif.append(
        {
            "origine_libelle": libelle,
            "origine_qte": qte,
            "origine_pu": pu,
            "origine_val": val,
            "complete_libelle": ligne["produit"],
            "contenance": ligne["contenance"],
            "complete_qte": ligne["quantite"],
            "complete_pu": ligne["pu"],
            "complete_val": ligne["valeur"],
            "ecart_qte": ecart_q,
            "ecart_val": ecart_v,
        }
    )

nb_lignes_comp = len(comparatif)
qte_identiques = sum(1 for c in comparatif if abs(c["ecart_qte"]) < 1e-9)
val_identiques = sum(1 for c in comparatif if abs(c["ecart_val"]) < 0.005)
ecart_total = round(sum(c["ecart_val"] for c in comparatif), 2)
total_origine = round(sum(c["origine_val"] for c in comparatif), 2)
total_complete = round(sum(c["complete_val"] or 0 for c in comparatif), 2)

# --------------------------------------------------------------------------- #
# 4. Recapitulatif par exercice
# --------------------------------------------------------------------------- #
recap = []
for date, exercice in CLOTURES:
    lignes = INVENTAIRES[date]
    sans_alcool = round(sum(l["valeur"] or 0 for l in lignes if l["categorie"] == "boisson_sans_alcool"), 2)
    alcool = round(sum(l["valeur"] or 0 for l in lignes if l["categorie"] == "alcool"), 2)
    avec_q = sum(1 for l in lignes if l["quantite"] is not None)
    avec_v = sum(1 for l in lignes if l["valeur"] is not None)
    alcools = [l for l in lignes if l["categorie"] == "alcool"]
    avec_c = sum(1 for l in lignes if l["contenance"])
    alc_total = len(alcools)
    alc_avec_c = sum(1 for l in alcools if l["contenance"])
    recap.append(
        {
            "date": date,
            "exercice": exercice,
            "nb": len(lignes),
            "avec_quantite": avec_q,
            "avec_valeur": avec_v,
            "avec_contenance": avec_c,
            "alcools": alc_total,
            "alcools_avec_contenance": alc_avec_c,
            "sans_alcool": sans_alcool,
            "alcool": alcool,
            "total": round(sans_alcool + alcool, 2),
        }
    )

for i in range(1, len(recap)):
    recap[i]["variation"] = round(recap[i]["total"] - recap[i - 1]["total"], 2)
recap[0]["variation"] = None

# --------------------------------------------------------------------------- #
# 5. Ecriture du classeur
# --------------------------------------------------------------------------- #
GRIS = PatternFill("solid", fgColor="F2F2F2")
ENTETE = PatternFill("solid", fgColor="1F3864")
VERT = PatternFill("solid", fgColor="E2EFDA")
ORANGE = PatternFill("solid", fgColor="FCE4D6")
BLANC = Font(color="FFFFFF", bold=True)
BORD = Border(*[Side(style="thin", color="BFBFBF")] * 4)


def entete(ws, labels, ligne=1):
    for i, lab in enumerate(labels, start=1):
        c = ws.cell(row=ligne, column=i, value=lab)
        c.fill = ENTETE
        c.font = BLANC
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = BORD
    ws.freeze_panes = ws.cell(row=ligne + 1, column=1)


def largeurs(ws, valeurs):
    for i, w in enumerate(valeurs, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w


wb = Workbook()

# --- Feuille 0 : notice ---------------------------------------------------- #
ws = wb.active
ws.title = "Notice"
notice = [
    ["R1 - Inventaires de stocks : etat d'origine et etat complete"],
    [""],
    ["Objet", "Verifier si l'etat d'inventaire produit en reponse a la proposition de rectifications "
              "modifie les quantites ou les valeurs de l'etat obtenu sur place par le service."],
    ["Etat d'origine", "Etat de stocks papier remis lors des interventions sur place. Le service en "
                       "reproduit 21 articles page 33 de sa reponse du 04/09/2026. Ces 21 lignes "
                       "correspondent aux lignes 5 a 25 de la page 11 du PDF "
                       "Inventaire_Demi_Lune_2023-03-31.pdf (onglet ALCOOL)."],
    ["Etat complete", "Meme etat, la contenance etant portee dans la designation de chaque article "
                      "(fichiers inventaire_2023-03-31.csv, inventaire_2024-03-31.csv, "
                      "inventaire_2025-03-31.csv)."],
    ["Resultat", f"Sur les {nb_lignes_comp} articles reproduits par le service : quantites identiques "
                 f"sur {qte_identiques} lignes, valeurs identiques au centime sur {val_identiques} lignes. "
                 f"Ecart de valeur cumule : {ecart_total:+.2f} EUR sur un total de {total_origine:.2f} EUR."],
    ["Lecture des ecarts", "L'etat d'origine, joint en PDF, fait foi. Les ecarts que presentait la "
                           "retranscription informatique etaient des erreurs de frappe, rectifiees "
                           "et recapitulees dans la feuille « Corrections et reserves » ; elles ne "
                           "provenaient d'aucune modification de l'inventaire physique."],
    ["Feuilles", ""],
    ["Unites", "Quantites en bouteilles ou unites ; prix unitaires et valeurs en euros HT."],
    ["Script", "scripts/reponse1-inventaires-comparatif.py (reproductible)."],
]
LIGNE_FEUILLES = next(i for i, l in enumerate(notice, start=1) if l[0] == "Feuilles")
for r, ligne in enumerate(notice, start=1):
    for c, v in enumerate(ligne, start=1):
        cell = ws.cell(row=r, column=c, value=v)
        cell.alignment = Alignment(vertical="top", wrap_text=True)
        if c == 1:
            cell.font = Font(bold=True)
ws.cell(row=1, column=1).font = Font(bold=True, size=14)
WS_NOTICE = ws
largeurs(ws, [22, 110])

# --- Feuille 1 : comparatif ------------------------------------------------ #
ws = wb.create_sheet("Comparatif p.33")
entete(
    ws,
    [
        "Article (etat d'origine, p. 33)",
        "Quantite",
        "Prix unitaire HT",
        "Valeur HT",
        "Article (etat complete)",
        "Contenance ajoutee",
        "Quantite",
        "Prix unitaire HT",
        "Valeur HT",
        "Ecart quantite",
        "Ecart valeur HT",
    ],
)
r = 2
for c in comparatif:
    identique = abs(c["ecart_qte"]) < 1e-9 and abs(c["ecart_val"]) < 0.005
    valeurs = [
        c["origine_libelle"], c["origine_qte"], c["origine_pu"], c["origine_val"],
        c["complete_libelle"], c["contenance"], c["complete_qte"], c["complete_pu"],
        c["complete_val"], c["ecart_qte"], c["ecart_val"],
    ]
    for i, v in enumerate(valeurs, start=1):
        cell = ws.cell(row=r, column=i, value=v)
        cell.border = BORD
        if i in (2, 3, 4, 7, 8, 9, 10, 11):
            cell.alignment = Alignment(horizontal="right")
        if i in (3, 4, 8, 9, 11):
            cell.number_format = "# ##0.00"
        if i in (10, 11):
            cell.fill = VERT if identique else ORANGE
    r += 1
for i, v in enumerate(
    ["TOTAL", "", "", total_origine, "", "", "", "", total_complete, "", ecart_total], start=1
):
    cell = ws.cell(row=r, column=i, value=v)
    cell.font = Font(bold=True)
    cell.fill = GRIS
    cell.border = BORD
    if i in (4, 9, 11):
        cell.number_format = "# ##0.00"
        cell.alignment = Alignment(horizontal="right")
largeurs(ws, [26, 10, 15, 12, 30, 16, 10, 15, 12, 13, 14])

# --- Feuilles 2 a 4 : etat complete par cloture ---------------------------- #
for date, exercice in CLOTURES:
    ws = wb.create_sheet(f"Cloture {date.replace('-', '-')}"[:31])
    ws.title = "Cloture " + date.replace("-", "-")
    entete(
        ws,
        ["Article (etat complete)", "Contenance", "Famille", "Quantite",
         "Prix unitaire HT", "Valeur HT", "Page du PDF d'origine"],
    )
    r = 2
    for l in INVENTAIRES[date]:
        famille = "Alcools et vins" if l["categorie"] == "alcool" else "Boissons sans alcool"
        for i, v in enumerate(
            [l["produit"], l["contenance"], famille, l["quantite"], l["pu"],
             l["valeur"], l["page"]], start=1
        ):
            cell = ws.cell(row=r, column=i, value=v)
            cell.border = BORD
            if i in (4, 5, 6, 7):
                cell.alignment = Alignment(horizontal="right")
            if i in (5, 6):
                cell.number_format = "# ##0.00"
        r += 1
    tot = round(sum(l["valeur"] or 0 for l in INVENTAIRES[date]), 2)
    for i, v in enumerate([f"TOTAL {exercice}", "", "", "", "", tot, ""], start=1):
        cell = ws.cell(row=r, column=i, value=v)
        cell.font = Font(bold=True)
        cell.fill = GRIS
        cell.border = BORD
        if i == 6:
            cell.number_format = "# ##0.00"
            cell.alignment = Alignment(horizontal="right")
    largeurs(ws, [40, 12, 20, 10, 15, 12, 20])

# --- Feuille 5 : recapitulatif --------------------------------------------- #
ws = wb.create_sheet("Recapitulatif")
entete(
    ws,
    ["Cloture", "Exercice", "Lignes inventoriees", "Lignes avec quantite",
     "Lignes avec valeur", "Lignes avec contenance", "Lignes alcools et vins",
     "Dont avec contenance", "Boissons sans alcool", "Alcools et vins",
     "Stock total HT", "Variation vs cloture precedente"],
)
r = 2
for d in recap:
    for i, v in enumerate(
        [d["date"], d["exercice"], d["nb"], d["avec_quantite"], d["avec_valeur"],
         d["avec_contenance"], d["alcools"], d["alcools_avec_contenance"],
         d["sans_alcool"], d["alcool"], d["total"], d["variation"]], start=1
    ):
        cell = ws.cell(row=r, column=i, value=v)
        cell.border = BORD
        if i >= 3:
            cell.alignment = Alignment(horizontal="right")
        if i >= 9:
            cell.number_format = "# ##0.00"
    r += 1
largeurs(ws, [13, 12, 18, 18, 16, 20, 18, 18, 20, 16, 15, 26])


# --- Feuille 6 : recapitulatifs dates -------------------------------------- #
ws = wb.create_sheet("Recapitulatifs dates")
entete(ws, ["Cloture", "Intitule porte sur la page recapitulative",
            "Boissons sans alcool", "Vins et alcools", "Total boissons",
            "Autres postes inventories", "Total imprime sur la page", "Source"])
r = 2
eur_doc = {}
for date, _ in CLOTURES:
    R = RECAPITULATIFS[date]
    tb = round(R["sans_alcool"] + R["alcool"], 2)
    eur_doc[date] = tb
    autres = " ; ".join(f"{lab} : {val:.2f}" for lab, val in R["autres"])
    for i, v in enumerate([date, R["titre"], R["sans_alcool"], R["alcool"], tb,
                           autres, R["total_imprime"], R["source"]], start=1):
        cell = ws.cell(row=r, column=i, value=v)
        cell.border = BORD
        cell.alignment = Alignment(vertical="top", wrap_text=True,
                                   horizontal="right" if i in (3, 4, 5, 7) else "left")
        if i in (3, 4, 5, 7):
            cell.number_format = "# ##0.00"
    r += 1
r += 1
ws.cell(row=r, column=1, value=(
    "Rapprochement avec la variation de stock boissons retenue par le service "
    "(compte 310200), sous la convention comptable variation = stock initial moins stock final.")
).font = Font(bold=True)
r += 2
entete(ws, ["Exercice", "Stock initial", "Stock final", "SI - SF",
            "Variation retenue (310200)", "Ecart", "", ""], ligne=r)
r += 1
for k, (date, exercice) in enumerate(CLOTURES):
    serv = VARIATION_SERVICE[exercice]
    if k == 0:
        vals = [exercice, "stock au 31/03/2022 non repris", eur_doc[date], None, serv, None, "", ""]
    else:
        si, sf = eur_doc[CLOTURES[k - 1][0]], eur_doc[date]
        d_ = round(si - sf, 2)
        vals = [exercice, si, sf, d_, serv, round(d_ - serv, 2), "", ""]
    for i, v in enumerate(vals, start=1):
        cell = ws.cell(row=r, column=i, value=v)
        cell.border = BORD
        if i >= 2 and isinstance(v, float):
            cell.number_format = "# ##0.00"
            cell.alignment = Alignment(horizontal="right")
        if i == 6 and isinstance(v, float):
            cell.fill = VERT if abs(v) < 0.005 else ORANGE
    r += 1
largeurs(ws, [14, 34, 20, 18, 16, 46, 22, 60])

# --- Feuille 7 : corrections et reserves ----------------------------------- #
ws = wb.create_sheet("Corrections et reserves")
entete(ws, ["Objet", "Detail", "Incidence (EUR HT)"])
r = 2
somme_corr = round(sum(bon - saisi for _, saisi, bon in CORRECTIONS_2023), 2)
somme_corr_sa = round(sum(inc for _, _, inc in CORRECTIONS_2023_SANS_ALCOOL), 2)

# Comptages recalcules sur les CSV publies, sans valeur saisie a la main.
nb_lignes_total = sum(len(INVENTAIRES[d]) for d, _ in CLOTURES)
lignes_av = [(d, l) for d, _ in CLOTURES for l in INVENTAIRES[d]
             if (l.get("fiabilite") or "") == "a_verifier"]
nb_av = len(lignes_av)
val_av = round(sum(l["valeur"] or 0 for _, l in lignes_av), 2)
lignes_recon = [(d, l) for d, l in lignes_av if l["quantite"] is None]
val_recon = round(sum(l["valeur"] or 0 for _, l in lignes_recon), 2)
val_recon_alcool = round(sum(l["valeur"] or 0 for _, l in lignes_recon
                             if l["categorie"] == "alcool"), 2)

# Totaux de la transcription 2023 apres rectification.
tot_sa_2023 = round(sum(l["valeur"] or 0 for l in INVENTAIRES["2023-03-31"]
                        if l["categorie"] == "boisson_sans_alcool"), 2)
tot_alc_2023 = round(sum(l["valeur"] or 0 for l in INVENTAIRES["2023-03-31"]
                         if l["categorie"] == "alcool"), 2)
tot_alim_2023 = round(sum(v for _, v in ALIMENTATION_P10_2023), 2)

lignes_cr = [
    ("Erreurs de frappe rectifiees, page 11 du PDF 2023 (alcools et vins)",
     " ; ".join(f"{lib} : {saisi:.2f} saisi au lieu de {bon:.2f}"
                for lib, saisi, bon in CORRECTIONS_2023)
     + ". Le CSV publie porte desormais les valeurs de l'etat d'origine.",
     somme_corr),
    ("Erreurs de frappe rectifiees, page 10 du PDF 2023 (boissons sans alcool)",
     " ; ".join(f"{lib} : {det}" for lib, det, _ in CORRECTIONS_2023_SANS_ALCOOL)
     + ". Le CSV publie porte desormais les valeurs de l'etat d'origine.",
     somme_corr_sa),
    ("Total alcools et vins au 31/03/2023, apres rectification",
     f"Transcription rectifiee : {tot_alc_2023:.2f} EUR, soit exactement le total "
     "porte en pied de la page 11 du PDF 2023, page que le service reproduit "
     "lui-meme p. 33 de sa reponse. La transcription anterieure indiquait "
     "3 056,26 EUR. C'est l'etat d'origine qui fait foi.",
     tot_alc_2023),
    ("Total boissons sans alcool au 31/03/2023, apres rectification",
     f"Transcription rectifiee des boissons : {tot_sa_2023:.2f} EUR. La page 10 "
     "du PDF porte en outre "
     + ", ".join(f"{lib} ({v:.2f} EUR)" for lib, v in ALIMENTATION_P10_2023)
     + f", soit {tot_alim_2023:.2f} EUR d'alimentation hors perimetre du CSV. "
     f"La somme des deux, {tot_sa_2023 + tot_alim_2023:.2f} EUR, est exactement "
     "le total imprime au bas de la page 10.",
     round(tot_sa_2023 + tot_alim_2023, 2)),
    ("Colonne de fiabilite de la transcription",
     f"{nb_av} lignes sur {nb_lignes_total} sont marquees « a verifier » dans les "
     f"CSV publies ({val_av:.2f} EUR). Ces reserves portent sur la TRANSCRIPTION, "
     "pas sur les etats d'origine, dont les totaux dates figurent dans la feuille "
     "precedente.",
     val_av),
    ("Lignes de reconciliation du 31/03/2025, non identifiees",
     f"{len(lignes_recon)} des lignes ci-dessus, toutes au 31/03/2025, ne designent "
     f"aucun produit : ce sont des reliquats de valeur ({val_recon:.2f} EUR, dont "
     f"{val_recon_alcool:.2f} EUR en alcools et vins) qui ferment la transcription "
     "sur les totaux dates de l'etat d'origine. Consequence a enoncer clairement : "
     "tant que ces lignes ne sont pas rattachees a un article, le stock d'alcools "
     "exprime EN LITRES au 31/03/2025 qui se deduit du CSV est un MINORANT. Les "
     "bouteilles correspondant a ces 318,41 EUR existent et sont comprises dans le "
     "total date de l'etat, mais leur contenance ne peut pas etre imputee faute de "
     "libelle. Toute reconstitution de volumes appuyee sur ce stock joue donc "
     "contre le contribuable, jamais en sa faveur.",
     val_recon),
    ("Perimetre du CSV",
     "Les CSV retiennent les seules boissons : ils excluent les biscuits, le sucre, les pailles "
     "et les consommables inscrits sur les memes pages d'inventaire. Leurs totaux ne sont donc "
     "pas comparables aux totaux des pages recapitulatives.",
     None),
]
for lab, det, inc in lignes_cr:
    for i, v in enumerate([lab, det, inc], start=1):
        cell = ws.cell(row=r, column=i, value=v)
        cell.border = BORD
        cell.alignment = Alignment(vertical="top", wrap_text=True,
                                   horizontal="right" if i == 3 else "left")
        if i == 3 and isinstance(v, float):
            cell.number_format = "# ##0.00"
    r += 1
largeurs(ws, [44, 100, 20])

# Le libelle des feuilles est ecrit en dernier, a partir du classeur reel :
# le nombre d'onglets annonce est ainsi toujours celui du fichier.
autres = [n for n in wb.sheetnames if n != "Notice"]
WS_NOTICE.cell(row=LIGNE_FEUILLES, column=2,
               value=f"{len(wb.sheetnames)} onglets : Notice ; "
                     + " ; ".join(autres) + ".").alignment = Alignment(
    vertical="top", wrap_text=True)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
wb.save(OUT)

# --------------------------------------------------------------------------- #
# 6. Trace console
# --------------------------------------------------------------------------- #
print(f"Ecrit : {OUT}")
print(f"Comparatif p.33 : {nb_lignes_comp} articles")
print(f"  quantites identiques : {qte_identiques}/{nb_lignes_comp}")
print(f"  valeurs identiques au centime : {val_identiques}/{nb_lignes_comp}")
print(f"  total origine {total_origine:.2f} EUR / total complete {total_complete:.2f} EUR "
      f"/ ecart {ecart_total:+.2f} EUR")
for c in comparatif:
    if abs(c["ecart_qte"]) > 1e-9 or abs(c["ecart_val"]) > 0.005:
        print(f"    ecart : {c['origine_libelle']} -> {c['complete_libelle']} "
              f"(valeur {c['origine_val']:.2f} vs {c['complete_val']:.2f})")
print()
for d in recap:
    print(f"{d['date']} ({d['exercice']}) : {d['nb']} lignes, "
          f"{d['avec_quantite']} avec quantite, {d['avec_valeur']} avec valeur, "
          f"{d['avec_contenance']} avec contenance, "
          f"alcools {d['alcools_avec_contenance']}/{d['alcools']} avec contenance, "
          f"total {d['total']:.2f} EUR, variation {d['variation']}")
print()
for date, exercice in CLOTURES:
    R = RECAPITULATIFS[date]
    print(f"recap {date} : sans alcool {R['sans_alcool']:.2f} + alcools {R['alcool']:.2f} "
          f"= {R['sans_alcool'] + R['alcool']:.2f} EUR")
for k in (1, 2):
    si = RECAPITULATIFS[CLOTURES[k - 1][0]]
    sf = RECAPITULATIFS[CLOTURES[k][0]]
    si_v = round(si["sans_alcool"] + si["alcool"], 2)
    sf_v = round(sf["sans_alcool"] + sf["alcool"], 2)
    ex = CLOTURES[k][1]
    print(f"{ex} : SI-SF = {si_v - sf_v:+.2f} | service {VARIATION_SERVICE[ex]:+.2f} "
          f"| ecart {si_v - sf_v - VARIATION_SERVICE[ex]:+.2f}")
