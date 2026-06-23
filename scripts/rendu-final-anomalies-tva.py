#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rendu-final-anomalies-tva.py
================================================================================
Reponse au grief fiscal "Incoherences de ventilation de TVA" (Proposition
p. 22-28, annexe G).

IDEE DIRECTRICE (volontairement simple)
  Le fichier d'export de la caisse contient UNE colonne buggee (la colonne
  d'affichage "base HT"). Mais le MEME fichier contient la TVA reellement
  encaissee, ligne par ligne, et celle-la est juste (figee par la caisse a
  chaque paiement). Comme c'est la TVA qui sert a la comptabilite (et non la
  colonne "base HT"), ce bug d'affichage n'a aucun effet sur les comptes.

  On le demontre en trois etapes, chiffres a l'appui :
    1. les totaux ABSURDES que donne la mauvaise colonne (il manque ~100 000 €/an
       pour retomber sur le chiffre d'affaires) ;
    2. les totaux JUSTES que donne la bonne colonne (le total retombe sur le CA
       a quelques euros pres) ;
    3. le rapprochement avec la comptabilite (source independante, tenue a la
       main d'apres les tickets Z) : tout colle a l'euro pres.

SOURCES (lecture seule)
  - public/documents/caisse-enregistreuse/ANNEXE-G{1,2,3}_journal-tva_*.xls
      colonnes utiles :
        col 7  tot_ttc     (TTC du ticket, repete sur chaque ligne du ticket)
        col 8  tot_tva     (TVA totale du ticket)
        col 12 taux_tva%   (10 ou 20)
        col 13 VAT_base    (colonne "base HT" de l'export -> BUGGEE)
        col 14 tax_amount  (TVA de la ligne au taux concerne -> JUSTE)
  - Comptabilite (706300 = HT 10 %, 706000 = HT 20 %, 445710 = TVA collectee,
    706800 = pourboire) : chiffres reproduits par le service p. 26 du rapport.

SORTIES
  - public/documents/pieces-defense/RF-tva-1-extrait-fichier-caisse.csv
  - public/documents/pieces-defense/RF-tva-2-exemple-ticket.csv
  - public/documents/pieces-defense/RF-tva-3-totaux-mauvaise-colonne.csv
  - public/documents/pieces-defense/RF-tva-4-totaux-bonne-colonne.csv
  - public/documents/pieces-defense/RF-tva-5-comparaison-et-comptabilite.csv
  - public/documents/pieces-defense/RF-anomalies-tva.xlsx   (5 onglets)
  - src/data/renduFinal/anomalies-tva.json
================================================================================
"""
import os
import csv
import json
import collections
import xlrd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from rfcommun import normaliser_sections

ICI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(ICI, ".."))
CAISSE = os.path.join(ROOT, "public/documents/caisse-enregistreuse/")
PIECES = os.path.join(ROOT, "public/documents/pieces-defense/")
OUT_XLSX = os.path.join(PIECES, "RF-anomalies-tva.xlsx")
OUT_JSON = os.path.join(ROOT, "src/data/renduFinal/anomalies-tva.json")

EXOS = ["2022-2023", "2023-2024", "2024-2025"]
LABEL = {"2022-2023": "Ex. clos 31/03/2023",
         "2023-2024": "Ex. clos 31/03/2024",
         "2024-2025": "Ex. clos 31/03/2025"}
G = {e: CAISSE + f"ANNEXE-G{i}_journal-tva_{e}.xls" for i, e in enumerate(EXOS, 1)}

# Colonnes Annexe G
C_TTC, C_TVA, C_TAUX, C_VATBASE, C_TA = 7, 8, 12, 13, 14


def num(v):
    return v if isinstance(v, (int, float)) else 0.0


# ---------------------------------------------------------------------------
# Lecture du journal de caisse : TVA reellement encaissee (col tax_amount, JUSTE)
# et chiffre d'affaires TTC par ticket.
# ---------------------------------------------------------------------------
def lire_journal_tva(path):
    sh = xlrd.open_workbook(path).sheet_by_index(0)
    tva10 = tva20 = sum_ta = 0.0
    n10 = n20 = n_ta_neg = n_base_neg = 0
    par_ticket_tva = collections.defaultdict(float)
    par_ticket_tot = {}
    seen = set()
    ttc_sum = 0.0
    for r in range(2, sh.nrows):
        taux = sh.cell_value(r, C_TAUX)
        if taux == "":
            continue
        ta = num(sh.cell_value(r, C_TA))
        sum_ta += ta
        if ta < 0:
            n_ta_neg += 1
        if num(sh.cell_value(r, C_VATBASE)) < 0:
            n_base_neg += 1
        if taux == 10.0:
            tva10 += ta
            n10 += 1
        elif taux == 20.0:
            tva20 += ta
            n20 += 1
        key = (sh.cell_value(r, 0), sh.cell_value(r, 2), sh.cell_value(r, 3))
        par_ticket_tva[key] += ta
        par_ticket_tot[key] = num(sh.cell_value(r, C_TVA))
        if key not in seen:
            seen.add(key)
            ttc_sum += num(sh.cell_value(r, C_TTC))
    ecart_recon = sum(abs(par_ticket_tva[k] - par_ticket_tot[k]) for k in par_ticket_tva)
    return {
        "tva10": round(tva10, 2), "tva20": round(tva20, 2), "tva_tot": round(sum_ta, 2),
        "base10": round(tva10 / 0.10, 2), "base20": round(tva20 / 0.20, 2),
        "n10": n10, "n20": n20, "n_ta_neg": n_ta_neg, "n_base_neg": n_base_neg,
        "ca_ttc": round(ttc_sum, 2), "ecart_recon": round(ecart_recon, 2),
    }


def lire_extrait(path, n=24):
    """Premieres ventes du fichier : on montre cote a cote la colonne 'base HT'
    (buggee) et la TVA reellement encaissee (juste)."""
    sh = xlrd.open_workbook(path).sheet_by_index(0)
    out = []
    for r in range(2, sh.nrows):
        taux = sh.cell_value(r, C_TAUX)
        if taux == "":
            continue
        out.append({
            "date": sh.cell_value(r, 0),
            "ticket": int(num(sh.cell_value(r, 2))),
            "taux": int(num(taux)),
            "base_buggee": round(num(sh.cell_value(r, C_VATBASE)), 2),
            "tva_juste": round(num(sh.cell_value(r, C_TA)), 2),
            "ttc": round(num(sh.cell_value(r, C_TTC)), 2),
        })
        if len(out) >= n:
            break
    return out


print("Lecture des annexes G ...")
JG = {e: lire_journal_tva(G[e]) for e in EXOS}
EXTRAIT = lire_extrait(G["2022-2023"], 24)

# Comptabilite presentee (rapport p. 26) et lecture du fisc de l'annexe G (p. 26).
COMPTA = {
    "2022-2023": dict(ht10=296105.87, ht20=64712.51, tva=42614.45, pb=598.04, ttc=404030.87),
    "2023-2024": dict(ht10=319179.31, ht20=72416.55, tva=46464.79, pb=597.75, ttc=438658.43),
    "2024-2025": dict(ht10=318345.43, ht20=70517.47, tva=46005.45, pb=656.57, ttc=435524.92),
}
FISCG = {  # base HT lue DIRECTEMENT dans la colonne buggee, et TVA (p. 26)
    "2022-2023": dict(b10=269445.43, b20=-11645.01, tva=42548.21, ca=403324.72),
    "2023-2024": dict(b10=296113.00, b20=-1680.08, tva=46387.76, ca=437881.12),
    "2024-2025": dict(b10=296625.31, b20=572.55, tva=45914.28, ca=434709.26),
}


# --- Agregats : mauvaise colonne (fisc) vs bonne colonne (nous) -------------
def calc_bad(e):
    f = FISCG[e]
    ht = round(f["b10"] + f["b20"], 2)
    tot = round(ht + f["tva"], 2)
    ca = JG[e]["ca_ttc"]
    return dict(b10=f["b10"], b20=f["b20"], ht=ht, tva=f["tva"], tot=tot,
                ca=ca, ecart=round(tot - ca, 2))


def calc_good(e):
    g = JG[e]
    ht = round(g["base10"] + g["base20"], 2)
    tot = round(ht + g["tva_tot"], 2)
    ca = g["ca_ttc"]
    return dict(b10=g["base10"], b20=g["base20"], ht=ht, tva=g["tva_tot"], tot=tot,
                ca=ca, ecart=round(tot - ca, 2))


BAD = {e: calc_bad(e) for e in EXOS}
GOOD = {e: calc_good(e) for e in EXOS}

ECART_BAD_CUM = round(sum(BAD[e]["ecart"] for e in EXOS), 2)
ECART_GOOD_CUM = round(sum(GOOD[e]["ecart"] for e in EXOS), 2)
TVA_NOUS_CUM = round(sum(JG[e]["tva_tot"] for e in EXOS), 2)
TVA_COMPTA_CUM = round(sum(COMPTA[e]["tva"] for e in EXOS), 2)
ECART_TVA_CUM = round(TVA_NOUS_CUM - TVA_COMPTA_CUM, 2)
HT_NOUS_CUM = round(sum(GOOD[e]["ht"] for e in EXOS), 2)
HT_COMPTA_CUM = round(sum(COMPTA[e]["ht10"] + COMPTA[e]["ht20"] for e in EXOS), 2)
ECART_HT_CUM = round(HT_NOUS_CUM - HT_COMPTA_CUM, 2)

for e in EXOS:
    print(f"  {e}: mauvaise colonne total={BAD[e]['tot']:.2f} (ecart CA {BAD[e]['ecart']:.2f}) | "
          f"bonne colonne total={GOOD[e]['tot']:.2f} (ecart CA {GOOD[e]['ecart']:.2f})")
print(f"  Cumul : ecart mauvaise colonne={ECART_BAD_CUM:.2f}  ecart bonne colonne={ECART_GOOD_CUM:.2f}  "
      f"ecart TVA/compta={ECART_TVA_CUM:.2f}")


# ===========================================================================
# FICHIERS CSV (un par etape, recalculables)
# ===========================================================================
def csv_num(x):
    return f"{x:.2f}".replace(".", ",")


def ecrire_csv(nom, entete, lignes):
    chemin = os.path.join(PIECES, nom)
    with open(chemin, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(entete)
        w.writerows(lignes)
    print("CSV  ecrit :", chemin)


os.makedirs(PIECES, exist_ok=True)

# CSV 1 : extrait brut du fichier de caisse (les deux colonnes cote a cote)
ecrire_csv(
    "RF-tva-1-extrait-fichier-caisse.csv",
    ["Date", "N° ticket", "Taux TVA (%)",
     "Colonne « base HT » du fichier (BUGGEE)",
     "TVA reellement encaissee (CORRECTE)", "TTC du ticket"],
    [[x["date"], x["ticket"], x["taux"], csv_num(x["base_buggee"]),
      csv_num(x["tva_juste"]), csv_num(x["ttc"])] for x in EXTRAIT])

# CSV 2 : exemple du ticket n° 2 (vente 20,90 €)
ecrire_csv(
    "RF-tva-2-exemple-ticket.csv",
    ["Ligne du ticket n° 2 (14/04/2022)", "Colonne « base HT » (BUGGEE)",
     "TVA encaissee (CORRECTE)", "Base correcte = TVA / taux"],
    [["Ligne 10 %", csv_num(5.70), csv_num(1.43), csv_num(14.30)],
     ["Ligne 20 %", csv_num(-14.80), csv_num(0.87), csv_num(4.35)],
     ["TOTAL ticket (HT reel = 18,60 €)", csv_num(-9.10), csv_num(2.30), csv_num(18.65)]])

# CSV 3 : totaux avec la MAUVAISE colonne
ecrire_csv(
    "RF-tva-3-totaux-mauvaise-colonne.csv",
    ["Exercice", "Base HT 10 % (fichier)", "Base HT 20 % (fichier)", "HT total",
     "+ TVA", "= Total reconstitue", "CA TTC reellement encaisse", "Ecart au CA"],
    [[LABEL[e], csv_num(BAD[e]["b10"]), csv_num(BAD[e]["b20"]), csv_num(BAD[e]["ht"]),
      csv_num(BAD[e]["tva"]), csv_num(BAD[e]["tot"]), csv_num(BAD[e]["ca"]),
      csv_num(BAD[e]["ecart"])] for e in EXOS]
    + [["TOTAL 3 exercices", "", "", "", "",
        csv_num(sum(BAD[e]["tot"] for e in EXOS)),
        csv_num(sum(BAD[e]["ca"] for e in EXOS)), csv_num(ECART_BAD_CUM)]])

# CSV 4 : totaux avec la BONNE colonne
ecrire_csv(
    "RF-tva-4-totaux-bonne-colonne.csv",
    ["Exercice", "Base HT 10 % (= TVA/taux)", "Base HT 20 % (= TVA/taux)", "HT total",
     "+ TVA encaissee", "= Total reconstitue", "CA TTC reellement encaisse", "Ecart au CA"],
    [[LABEL[e], csv_num(GOOD[e]["b10"]), csv_num(GOOD[e]["b20"]), csv_num(GOOD[e]["ht"]),
      csv_num(GOOD[e]["tva"]), csv_num(GOOD[e]["tot"]), csv_num(GOOD[e]["ca"]),
      csv_num(GOOD[e]["ecart"])] for e in EXOS]
    + [["TOTAL 3 exercices", "", "", "", "",
        csv_num(sum(GOOD[e]["tot"] for e in EXOS)),
        csv_num(sum(GOOD[e]["ca"] for e in EXOS)), csv_num(ECART_GOOD_CUM)]])

# CSV 5 : comparaison + rapprochement avec la comptabilite
ecrire_csv(
    "RF-tva-5-comparaison-et-comptabilite.csv",
    ["Exercice", "Total via mauvaise colonne", "Ecart au CA (mauvaise)",
     "Total via bonne colonne", "Ecart au CA (bonne)",
     "TVA encaissee (nous)", "TVA comptabilite 445710", "Ecart TVA",
     "Base HT (nous)", "Base HT comptabilite 706000+706300", "Ecart base HT"],
    [[LABEL[e], csv_num(BAD[e]["tot"]), csv_num(BAD[e]["ecart"]),
      csv_num(GOOD[e]["tot"]), csv_num(GOOD[e]["ecart"]),
      csv_num(JG[e]["tva_tot"]), csv_num(COMPTA[e]["tva"]),
      csv_num(JG[e]["tva_tot"] - COMPTA[e]["tva"]),
      csv_num(GOOD[e]["ht"]), csv_num(COMPTA[e]["ht10"] + COMPTA[e]["ht20"]),
      csv_num(GOOD[e]["ht"] - COMPTA[e]["ht10"] - COMPTA[e]["ht20"])] for e in EXOS]
    + [["TOTAL 3 exercices", "", csv_num(ECART_BAD_CUM), "", csv_num(ECART_GOOD_CUM),
        csv_num(TVA_NOUS_CUM), csv_num(TVA_COMPTA_CUM), csv_num(ECART_TVA_CUM),
        csv_num(HT_NOUS_CUM), csv_num(HT_COMPTA_CUM), csv_num(ECART_HT_CUM)]])


# ===========================================================================
# CLASSEUR XLSX (5 onglets, un par etape)
# ===========================================================================
HEAD = Font(bold=True, color="FFFFFF", size=11)
HEADFILL = PatternFill("solid", fgColor="0F766E")
SUBHEAD = Font(bold=True)
THIN = Side(style="thin", color="D9D9D9")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
EURO = u'# ##0,00\xa0"€";-# ##0,00\xa0"€"'


def style_header(ws, ncol):
    for c in range(1, ncol + 1):
        cell = ws.cell(row=1, column=c)
        cell.font = HEAD
        cell.fill = HEADFILL
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER


def feuille(wb, titre, entete, lignes, euro_cols, widths, total=False):
    ws = wb.create_sheet(titre) if wb.sheetnames != ["Sheet"] else wb.active
    if ws.title == "Sheet":
        ws.title = titre
    ws.append(entete)
    for lig in lignes:
        ws.append(lig)
    for r in range(2, ws.max_row + 1):
        for c in euro_cols:
            ws.cell(row=r, column=c).number_format = EURO
    if total:
        for c in range(1, len(entete) + 1):
            ws.cell(row=ws.max_row, column=c).font = SUBHEAD
    style_header(ws, len(entete))
    ws.freeze_panes = "A2"
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w
    return ws


wb = openpyxl.Workbook()

# Onglet 1 : extrait du fichier
feuille(wb, "1. Extrait du fichier caisse",
        ["Date", "N° ticket", "Taux TVA (%)", "Base HT du fichier (BUGGEE)",
         "TVA encaissee (CORRECTE)", "TTC du ticket"],
        [[x["date"], x["ticket"], x["taux"], x["base_buggee"], x["tva_juste"], x["ttc"]]
         for x in EXTRAIT],
        euro_cols=(4, 5, 6), widths=[13, 11, 13, 22, 22, 14])

# Onglet 2 : exemple ticket
feuille(wb, "2. Exemple ticket n2",
        ["Ligne du ticket n° 2 (14/04/2022, TTC 20,90 €)", "Base HT (BUGGEE)",
         "TVA encaissee (CORRECTE)", "Base correcte = TVA / taux"],
        [["Ligne 10 %", 5.70, 1.43, 14.30],
         ["Ligne 20 %", -14.80, 0.87, 4.35],
         ["TOTAL ticket (HT reel = 18,60 €)", -9.10, 2.30, 18.65]],
        euro_cols=(2, 3, 4), widths=[42, 18, 24, 26], total=True)

# Onglet 3 : totaux mauvaise colonne
feuille(wb, "3. Totaux mauvaise colonne",
        ["Exercice", "Base HT 10 % (fichier)", "Base HT 20 % (fichier)", "HT total",
         "+ TVA", "= Total reconstitue", "CA TTC encaisse", "Ecart au CA"],
        [[LABEL[e], BAD[e]["b10"], BAD[e]["b20"], BAD[e]["ht"], BAD[e]["tva"],
          BAD[e]["tot"], BAD[e]["ca"], BAD[e]["ecart"]] for e in EXOS]
        + [["TOTAL 3 exercices", "", "", "", "", sum(BAD[e]["tot"] for e in EXOS),
            sum(BAD[e]["ca"] for e in EXOS), ECART_BAD_CUM]],
        euro_cols=(2, 3, 4, 5, 6, 7, 8), widths=[22, 18, 18, 14, 14, 16, 16, 14], total=True)

# Onglet 4 : totaux bonne colonne
feuille(wb, "4. Totaux bonne colonne",
        ["Exercice", "Base HT 10 % (=TVA/taux)", "Base HT 20 % (=TVA/taux)", "HT total",
         "+ TVA encaissee", "= Total reconstitue", "CA TTC encaisse", "Ecart au CA"],
        [[LABEL[e], GOOD[e]["b10"], GOOD[e]["b20"], GOOD[e]["ht"], GOOD[e]["tva"],
          GOOD[e]["tot"], GOOD[e]["ca"], GOOD[e]["ecart"]] for e in EXOS]
        + [["TOTAL 3 exercices", "", "", "", "", sum(GOOD[e]["tot"] for e in EXOS),
            sum(GOOD[e]["ca"] for e in EXOS), ECART_GOOD_CUM]],
        euro_cols=(2, 3, 4, 5, 6, 7, 8), widths=[22, 20, 20, 14, 16, 16, 16, 14], total=True)

# Onglet 5 : comparaison + comptabilite
feuille(wb, "5. Comparaison et comptabilite",
        ["Exercice", "Total mauvaise colonne", "Ecart au CA (mauvaise)",
         "Total bonne colonne", "Ecart au CA (bonne)", "TVA nous", "TVA compta 445710",
         "Ecart TVA", "Base HT nous", "Base HT compta 706000+706300", "Ecart base HT"],
        [[LABEL[e], BAD[e]["tot"], BAD[e]["ecart"], GOOD[e]["tot"], GOOD[e]["ecart"],
          JG[e]["tva_tot"], COMPTA[e]["tva"], round(JG[e]["tva_tot"] - COMPTA[e]["tva"], 2),
          GOOD[e]["ht"], round(COMPTA[e]["ht10"] + COMPTA[e]["ht20"], 2),
          round(GOOD[e]["ht"] - COMPTA[e]["ht10"] - COMPTA[e]["ht20"], 2)] for e in EXOS]
        + [["TOTAL 3 exercices", "", ECART_BAD_CUM, "", ECART_GOOD_CUM, TVA_NOUS_CUM,
            TVA_COMPTA_CUM, ECART_TVA_CUM, HT_NOUS_CUM, HT_COMPTA_CUM, ECART_HT_CUM]],
        euro_cols=(2, 3, 4, 5, 6, 7, 8, 9, 10, 11),
        widths=[22, 18, 18, 18, 18, 13, 16, 12, 14, 22, 14], total=True)

wb.save(OUT_XLSX)
print("XLSX ecrit :", OUT_XLSX)


# ===========================================================================
# JSON (textes de la page de defense) - langage simple
# ===========================================================================
def euro(x):
    return f"{x:,.2f}".replace(",", " ").replace(".", ",") + " €"


def eus(x):
    return ("+" if x >= 0 else "") + euro(x)


def _cg(t): return {"v": t}
def _cd(t): return {"v": t, "align": "right"}
def _cgb(t): return {"v": t, "fw": 700}
def _cdb(t): return {"v": t, "align": "right", "fw": 700}
def _colg(l): return {"label": l}
def _cold(l): return {"label": l, "align": "right"}


def _ko(t): return {"v": t, "align": "right", "badge": "ko"}
def _ok(t): return {"v": t, "align": "right", "badge": "ok"}


# Sources du droit (rappel court, liens complets affiches)
URL_CEDEF = "https://www.economie.gouv.fr/cedef/tva-reduite-restauration"

# Chemins des pieces (relatifs a public/documents/)
SRC_G = [("caisse-enregistreuse/ANNEXE-G1_journal-tva_2022-2023.xls",
          "Fichier de caisse — annexe G, ex. 2023 (XLS source du fisc)"),
         ("caisse-enregistreuse/ANNEXE-G2_journal-tva_2023-2024.xls",
          "Fichier de caisse — annexe G, ex. 2024 (XLS source du fisc)"),
         ("caisse-enregistreuse/ANNEXE-G3_journal-tva_2024-2025.xls",
          "Fichier de caisse — annexe G, ex. 2025 (XLS source du fisc)")]


def pj(intro, fichiers):
    return {"kind": "piecejointe", "intro": intro,
            "fichiers": [{"fichier": f, "label": l} for f, l in fichiers]}


XLSX = "pieces-defense/RF-anomalies-tva.xlsx"
S = []

# ---------------------------------------------------------------- CH. 1 (fisc)
S.append({"kind": "chapitre", "source": "fisc", "titre": "Ce que reproche le fisc"})
S.append({"kind": "paragraphe", "texte":
          "Le service a ouvert le **fichier d'export de notre caisse enregistreuse** "
          "(l'« annexe G » : un fichier qui liste, ligne par ligne, toutes les ventes "
          "des trois exercices). Dans ce fichier, il a regarde une colonne intitulee "
          "**« base HT »** et y a trouve des montants **negatifs et incoherents** — par "
          "exemple une base de 20 % de " + euro(FISCG["2022-2023"]["b20"]) + " en 2023. "
          "Il en conclut que « *les bases TVA sont totalement invraisemblables* » et, "
          "plus largement, que la comptabilite ne serait pas fiable (proposition de "
          "rectification, section XI, p. 25-27)."})
S.append({"kind": "paragraphe", "texte":
          "Le grief repose donc **entierement sur la lecture d'une seule colonne** de "
          "ce fichier. Nous allons montrer, avec ce **meme fichier**, que cette colonne "
          "est la seule a etre fausse, et qu'elle ne sert pas a la comptabilite."})
S.append(pj("Le fichier exact que le service a lu (un par exercice), et un extrait des "
            "premieres ventes ou l'on voit cote a cote la colonne « base HT » (celle qui "
            "bugue) et la TVA reellement encaissee (celle qui est juste).",
            SRC_G + [("pieces-defense/RF-tva-1-extrait-fichier-caisse.csv",
                      "Extrait du fichier de caisse : les 2 colonnes cote a cote (CSV)")]))

# ---------------------------------------------------------------- CH. 2 (nous)
S.append({"kind": "chapitre", "source": "nous", "titre": "L'explication, en une phrase"})
S.append({"kind": "paragraphe", "texte":
          "Ce fichier contient bien une colonne **« base HT » buggee**. Mais le **meme "
          "fichier** contient aussi la **TVA reellement encaissee**, ligne par ligne, et "
          "celle-la est **juste** : elle est calculee et verrouillee par la caisse au "
          "moment de chaque paiement. Or **c'est la TVA qui sert a la comptabilite, pas "
          "la colonne « base HT »**. Ce bug d'affichage n'a donc **aucun effet** sur les "
          "comptes."})
S.append({"kind": "paragraphe", "texte":
          "On le prouve en **trois etapes simples** : (1) les totaux **absurdes** que "
          "donne la mauvaise colonne ; (2) les totaux **justes** que donne la bonne "
          "colonne ; (3) le fait que ces totaux justes **collent, a l'euro pres, a la "
          "comptabilite**."})
S.append({"kind": "kpis", "items": [
    {"label": "Mauvaise colonne (lue par le fisc)", "valeur": euro(ECART_BAD_CUM),
     "sub": "ce qui manque pour retomber sur le chiffre d'affaires (3 ans)", "couleur": "red"},
    {"label": "Bonne colonne (TVA encaissee)", "valeur": euro(ECART_GOOD_CUM),
     "sub": "ecart au chiffre d'affaires sur 3 ans (simple arrondi)", "couleur": "teal"},
    {"label": "TVA contre comptabilite", "valeur": eus(ECART_TVA_CUM),
     "sub": "ecart sur 3 ans — sens favorable au Tresor", "couleur": "teal"},
]})
S.append({"kind": "paragraphe", "texte":
          "Un exemple concret pour voir le bug a l'oeil nu : le **ticket n° 2 du "
          "14/04/2022**, une vente de 20,90 € (TVA 2,30 €)."})
S.append({"kind": "tableau",
          "titre": "Ticket n° 2 — lu directement dans le fichier de caisse",
          "minWidth": 760,
          "colonnes": [_colg("Ligne du ticket"),
                       _cold("Colonne « base HT » du fichier (buggee)"),
                       _cold("TVA reellement encaissee (juste)"),
                       _cold("Base correcte = TVA / taux")],
          "lignes": [
              [_cg("Ligne a 10 %"), _cd(euro(5.70)), _cd(euro(1.43)), _cd(euro(14.30))],
              [_cg("Ligne a 20 %"), _ko(euro(-14.80)), _cd(euro(0.87)), _cd(euro(4.35))],
              [_cgb("Total du ticket"), _ko(euro(-9.10)), _cdb(euro(2.30)), _cdb(euro(18.65))],
          ]})
S.append({"kind": "paragraphe", "texte":
          "Tout est la. La colonne « base HT » du fichier donne un total de "
          "**" + euro(-9.10) + "** : **impossible** pour une vente de 20,90 €. Mais la "
          "TVA encaissee (1,43 € + 0,87 € = **2,30 €**) est **exactement** la TVA du "
          "ticket, et la base correcte (14,30 € + 4,35 € = **18,65 €**) redonne bien le "
          "HT reel (20,90 − 2,30 = 18,60 €, a 5 centimes d'arrondi pres). Le bug est "
          "dans la colonne d'affichage, **pas dans la vente**."})
S.append(pj("Le detail du ticket n° 2, recalculable.",
            [("pieces-defense/RF-tva-2-exemple-ticket.csv", "Exemple ticket n° 2 (CSV)"),
             (XLSX, "Classeur complet — onglet « 2. Exemple ticket » (XLSX)")]))

# ---------------------------------------------------------------- CH. 3 (nous)
S.append({"kind": "chapitre", "source": "nous",
          "titre": "Etape 1 — Les totaux que donne la MAUVAISE colonne"})
S.append({"kind": "paragraphe", "texte":
          "Additionnons la colonne « base HT » du fichier (celle qui bugue), exactement "
          "comme l'a fait le service. On obtient une base HT totale ; on y ajoute la "
          "TVA. Le resultat **devrait** redonner le chiffre d'affaires TTC reellement "
          "encaisse. **Il en est tres loin** : il **manque environ 100 000 € chaque "
          "annee**. C'est la preuve directe que cette colonne est cassee."})
S.append({"kind": "tableau",
          "titre": "Avec la mauvaise colonne, le fichier ne « tombe » pas juste",
          "minWidth": 920,
          "colonnes": [_colg("Exercice"), _cold("Base HT 10 % (fichier)"),
                       _cold("Base HT 20 % (fichier)"), _cold("HT total"),
                       _cold("+ TVA"), _cold("= Total"),
                       _cold("CA TTC encaisse"), _cold("Manque")],
          "lignes": [[_cg(LABEL[e]), _cd(euro(BAD[e]["b10"])),
                      _ko(euro(BAD[e]["b20"])) if BAD[e]["b20"] < 0 else _cd(euro(BAD[e]["b20"])),
                      _cd(euro(BAD[e]["ht"])), _cd(euro(BAD[e]["tva"])),
                      _cd(euro(BAD[e]["tot"])), _cd(euro(BAD[e]["ca"])),
                      _ko(euro(BAD[e]["ecart"]))] for e in EXOS]
                     + [[_cgb("Total 3 exercices"), _cd(""), _cd(""), _cd(""), _cd(""),
                         _cdb(euro(sum(BAD[e]["tot"] for e in EXOS))),
                         _cdb(euro(sum(BAD[e]["ca"] for e in EXOS))),
                         _ko(euro(ECART_BAD_CUM))]]})
S.append({"kind": "paragraphe", "texte":
          "Sur les trois exercices, le total calcule a partir de la mauvaise colonne est "
          "inferieur de **" + euro(abs(ECART_BAD_CUM)) + "** au chiffre d'affaires "
          "reellement encaisse. Aucune comptabilite ne pourrait etre tenue ainsi : c'est "
          "bien que **cette colonne n'est pas faite pour cela**."})
S.append(pj("Le calcul complet a partir de la mauvaise colonne, exercice par exercice.",
            [("pieces-defense/RF-tva-3-totaux-mauvaise-colonne.csv",
              "Totaux avec la mauvaise colonne (CSV)"),
             (XLSX, "Classeur complet — onglet « 3. Totaux mauvaise colonne » (XLSX)")]))

# ---------------------------------------------------------------- CH. 4 (nous)
S.append({"kind": "chapitre", "source": "nous",
          "titre": "Etape 2 — Les totaux que donne la BONNE colonne"})
S.append({"kind": "paragraphe", "texte":
          "Repartons maintenant de la **TVA reellement encaissee** (la colonne juste). "
          "Les taux etant fixes par la loi (**10 %** pour la restauration sur place, "
          "**20 %** pour les boissons alcoolisees), il suffit de diviser cette TVA par "
          "son taux pour retrouver la base HT correcte. On additionne, on ajoute la "
          "TVA : cette fois, le total **retombe exactement sur le chiffre d'affaires TTC "
          "encaisse**, a quelques euros pres."})
S.append({"kind": "tableau",
          "titre": "Avec la bonne colonne, le fichier « tombe » juste",
          "minWidth": 920,
          "colonnes": [_colg("Exercice"), _cold("Base HT 10 % (= TVA/taux)"),
                       _cold("Base HT 20 % (= TVA/taux)"), _cold("HT total"),
                       _cold("+ TVA encaissee"), _cold("= Total"),
                       _cold("CA TTC encaisse"), _cold("Ecart")],
          "lignes": [[_cg(LABEL[e]), _cd(euro(GOOD[e]["b10"])), _cd(euro(GOOD[e]["b20"])),
                      _cd(euro(GOOD[e]["ht"])), _cd(euro(GOOD[e]["tva"])),
                      _cd(euro(GOOD[e]["tot"])), _cd(euro(GOOD[e]["ca"])),
                      _ok(eus(GOOD[e]["ecart"]))] for e in EXOS]
                     + [[_cgb("Total 3 exercices"), _cd(""), _cd(""), _cd(""), _cd(""),
                         _cdb(euro(sum(GOOD[e]["tot"] for e in EXOS))),
                         _cdb(euro(sum(GOOD[e]["ca"] for e in EXOS))),
                         _ok(eus(ECART_GOOD_CUM))]]})
S.append({"kind": "paragraphe", "texte":
          "L'ecart au chiffre d'affaires tombe a **" + euro(abs(ECART_GOOD_CUM)) + "** "
          "sur trois ans (un simple arrondi au centime), contre "
          + euro(abs(ECART_BAD_CUM)) + " avec la mauvaise colonne. La bonne colonne "
          "**boucle** ; la mauvaise non. C'est aussi simple que cela."})
S.append(pj("Le calcul complet a partir de la bonne colonne (TVA encaissee), exercice "
            "par exercice.",
            [("pieces-defense/RF-tva-4-totaux-bonne-colonne.csv",
              "Totaux avec la bonne colonne (CSV)"),
             (XLSX, "Classeur complet — onglet « 4. Totaux bonne colonne » (XLSX)")]))

# ---------------------------------------------------------------- CH. 5 (nous)
S.append({"kind": "chapitre", "source": "nous",
          "titre": "Etape 3 — La comparaison, et la verification avec la comptabilite"})
S.append({"kind": "paragraphe", "texte":
          "Mettons les deux calculs cote a cote. D'un cote la mauvaise colonne, qui se "
          "trompe de pres de 100 000 € par an ; de l'autre la bonne colonne, qui tombe "
          "juste a quelques euros."})
S.append({"kind": "tableau",
          "titre": "Mauvaise colonne contre bonne colonne : l'ecart au chiffre d'affaires",
          "minWidth": 820,
          "colonnes": [_colg("Exercice"), _cold("Total via mauvaise colonne"),
                       _cold("Ecart au CA"), _cold("Total via bonne colonne"),
                       _cold("Ecart au CA")],
          "lignes": [[_cg(LABEL[e]), _cd(euro(BAD[e]["tot"])), _ko(euro(BAD[e]["ecart"])),
                      _cd(euro(GOOD[e]["tot"])), _ok(eus(GOOD[e]["ecart"]))] for e in EXOS]
                     + [[_cgb("Total 3 exercices"),
                         _cdb(euro(sum(BAD[e]["tot"] for e in EXOS))), _ko(euro(ECART_BAD_CUM)),
                         _cdb(euro(sum(GOOD[e]["tot"] for e in EXOS))), _ok(eus(ECART_GOOD_CUM))]]})
S.append({"kind": "paragraphe", "texte":
          "Reste la verification **decisive**. La comptabilite deposee a ete tenue **a "
          "la main**, en recopiant chaque jour les tickets de caisse (les « tickets Z ») "
          "sur un agenda — une source **totalement independante** du fichier "
          "informatique. Si nos chiffres justes collent aussi a cette comptabilite, "
          "c'est qu'ils sont bien la realite."})
S.append({"kind": "tableau",
          "titre": "Nos chiffres justes contre la comptabilite (source independante)",
          "minWidth": 940,
          "colonnes": [_colg("Exercice"), _cold("TVA encaissee (nous)"),
                       _cold("TVA comptabilite (445710)"), _cold("Ecart TVA"),
                       _cold("Base HT (nous)"),
                       _cold("Base HT compta (706000+706300)"), _cold("Ecart base HT")],
          "lignes": [[_cg(LABEL[e]), _cd(euro(JG[e]["tva_tot"])), _cd(euro(COMPTA[e]["tva"])),
                      _cd(eus(JG[e]["tva_tot"] - COMPTA[e]["tva"])),
                      _cd(euro(GOOD[e]["ht"])),
                      _cd(euro(COMPTA[e]["ht10"] + COMPTA[e]["ht20"])),
                      _cd(eus(GOOD[e]["ht"] - COMPTA[e]["ht10"] - COMPTA[e]["ht20"]))]
                     for e in EXOS]
                     + [[_cgb("Total 3 exercices"), _cdb(euro(TVA_NOUS_CUM)),
                         _cdb(euro(TVA_COMPTA_CUM)), _ok(eus(ECART_TVA_CUM)),
                         _cdb(euro(HT_NOUS_CUM)), _cdb(euro(HT_COMPTA_CUM)),
                         _ok(eus(ECART_HT_CUM))]]})
S.append({"kind": "paragraphe", "texte":
          "La TVA encaissee colle a la comptabilite a **" + euro(abs(ECART_TVA_CUM))
          + "** pres sur trois ans, et la base HT a **" + euro(abs(ECART_HT_CUM))
          + "** pres (moins de 0,01 %). Mieux : l'ecart de TVA va dans le sens d'une "
          "**sur-declaration** (l'entreprise a reverse un peu **plus** de TVA qu'elle "
          "n'en a encaisse) — on ne dissimule pas des recettes en payant trop de TVA. "
          "**Deux chaines totalement independantes** (la caisse informatique d'un cote, "
          "l'agenda manuscrit de l'autre) donnent le **meme** resultat."})
S.append(pj("La comparaison des deux methodes et le rapprochement complet avec la "
            "comptabilite (TVA, base HT), exercice par exercice.",
            [("pieces-defense/RF-tva-5-comparaison-et-comptabilite.csv",
              "Comparaison + rapprochement comptabilite (CSV)"),
             (XLSX, "Classeur complet — onglet « 5. Comparaison et comptabilite » (XLSX)")]))

# ---------------------------------------------------------------- CONCLUSION
S.append({"kind": "chapitre", "source": "nous", "titre": "Conclusion"})
S.append({"kind": "paragraphe", "texte":
          "Le resultat final est sans faille. **Une seule colonne du fichier d'export "
          "bugue** — la colonne d'affichage « base HT » — et **elle ne sert pas a la "
          "comptabilite**. La donnee qui compte, la **TVA reellement encaissee**, est "
          "juste dans le **meme fichier** : reconstituee a partir d'elle, la base HT "
          "boucle avec le chiffre d'affaires (a " + euro(abs(ECART_GOOD_CUM)) + " pres) "
          "et se reconcilie avec la comptabilite a l'euro pres, alors que la mauvaise "
          "colonne se trompe de " + euro(abs(ECART_BAD_CUM)) + "."})
S.append({"kind": "paragraphe", "texte":
          "Autrement dit : **ni recette cachee, ni erreur de TVA**. Le grief des "
          "« incoherences de TVA » repose entierement sur la lecture d'une colonne "
          "d'affichage defectueuse, alors que tout le reste du **meme fichier** prouve "
          "le contraire, et que la comptabilite — verifiee par une source independante "
          "— est exacte. **Ce grief doit etre abandonne.** (Pour memoire : restauration "
          "sur place a 10 %, boissons alcoolisees a 20 %, conformement au droit commun ; "
          "voir " + "[" + URL_CEDEF + "](" + URL_CEDEF + ").)"})
S.append(pj("Le dossier complet, recalculable de bout en bout depuis le fichier de "
            "caisse : extrait du fichier, exemple de ticket, totaux mauvaise colonne, "
            "totaux bonne colonne, comparaison et rapprochement avec la comptabilite.",
            [(XLSX, "Dossier TVA complet — 5 onglets (XLSX)")]))


# --- Ecriture du JSON --------------------------------------------------------
doc = {
    "meta": {
        "slug": "anomalies-tva",
        "titre": "Incoherences de TVA",
        "audience": "avocat",
        "sources": ["Annexe G1/G2/G3 (journal de caisse, 3 exercices)",
                    "Comptabilite : 706300, 706000, 445710 (rapport p. 26)"],
        "script": "scripts/rendu-final-anomalies-tva.py",
        "piece": "pieces-defense/RF-anomalies-tva.xlsx",
        "genere_le": "reproductible (script)",
    },
    "sections": normaliser_sections(S),
}
os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(doc, f, ensure_ascii=False, indent=2)
print("JSON ecrit :", OUT_JSON, "| sections:", len(doc["sections"]))
