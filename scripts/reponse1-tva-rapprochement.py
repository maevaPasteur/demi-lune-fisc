#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reponse1-tva-rapprochement.py
================================================================================
Reponse DDFiP 39 du 04/09/2026, partie H "Incoherences de TVA" (p. 46-47).

OBJET
  Rapprocher, par exercice et par taux, TROIS sources independantes :
    (1) le JOURNAL DE CAISSE (annexe G, colonne tax_amount = TVA figee par la
        caisse au moment du paiement) ;
    (2) le DETAIL DES TICKETS (annexe C, ligne a ligne : TTC de la ligne et taux
        legal de l'article, en reprenant la correction de taux que le service a
        lui-meme portee en colonnes E et F de l'annexe C) ;
    (3) la COMPTABILITE / TVA COLLECTEE REVERSEE (445710, ventilee d'apres
        706300 = base 10 % et 706000 = base 20 %), telle que le service la
        reproduit p. 26 de la proposition de rectifications.

  On verifie aussi deux faits materiels invoques par le service p. 47 :
    - "les six dernieres colonnes ... peuvent afficher des montants negatifs" :
      on compte les valeurs negatives colonne par colonne ;
    - "les deux dernieres colonnes proviennent d'un calcul du service" : on
      verifie que les QUATRE colonnes de ventilation (Base TVA 10 %, TVA 10 %,
      Base TVA 20 %, TVA 20 %) sont la simple recopie de VAT_base et tax_amount
      selon le taux de la ligne, donc quatre colonnes construites, et non deux.

SOURCES (lecture seule)
  public/documents/caisse-enregistreuse/ANNEXE-G{1,2,3}_journal-tva_*.xls
      col 7 tot_ttc | 8 tot_tva | 12 taux_tva% | 13 VAT_base | 14 tax_amount
      col 15 Base TVA10% | 16 TVA10% | 17 Base TVA20% | 18 TVA20%
  public/documents/caisse-enregistreuse/ANNEXE-C{1,2,3}_detail-tickets_*.xls
      col 0 date | 1 heure | 2 no_ticket | 5 Tot_ttc | 6 Tot_tva
      col 15 Taux_tva% | 16 Tot_rem Ttc (TTC de la ligne)
      col 21 (E) "Erreur Taux TVA" du service | 22 (F) "Correction TVA sur taux"

SORTIE
  public/documents/pieces-reponse-1/R1-tva-rapprochement.xlsx

USAGE
  python3 scripts/reponse1-tva-rapprochement.py
================================================================================
"""
import os
import collections

import xlrd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

ICI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(ICI, ".."))
CAISSE = os.path.join(ROOT, "public/documents/caisse-enregistreuse/")
PIECES = os.path.join(ROOT, "public/documents/pieces-reponse-1/")
OUT = os.path.join(PIECES, "R1-tva-rapprochement.xlsx")

EXOS = ["2022-2023", "2023-2024", "2024-2025"]
LABEL = {"2022-2023": "Ex. clos 31/03/2023",
         "2023-2024": "Ex. clos 31/03/2024",
         "2024-2025": "Ex. clos 31/03/2025"}
G = {e: CAISSE + f"ANNEXE-G{i}_journal-tva_{e}.xls" for i, e in enumerate(EXOS, 1)}
C = {e: CAISSE + f"ANNEXE-C{i}_detail-tickets_{e}.xls" for i, e in enumerate(EXOS, 1)}

# Comptabilite reproduite par le service p. 26 de la proposition de rectifications
COMPTA = {
    "2022-2023": dict(ht10=296105.87, ht20=64712.51, tva445710=42614.45),
    "2023-2024": dict(ht10=319179.31, ht20=72416.55, tva445710=46464.79),
    "2024-2025": dict(ht10=318345.43, ht20=70517.47, tva445710=46005.45),
}

C_TTC, C_TVA, C_TAUX, C_VATBASE, C_TA = 7, 8, 12, 13, 14
COLS6 = [(13, "VAT_base"), (14, "tax_amount"), (15, "Base TVA 10 %"),
         (16, "TVA 10 %"), (17, "Base TVA 20 %"), (18, "TVA 20 %")]


def num(v):
    return v if isinstance(v, (int, float)) else 0.0


# ---------------------------------------------------------------------------
# 1. Journal de caisse (annexe G)
# ---------------------------------------------------------------------------
def lire_G(path):
    sh = xlrd.open_workbook(path).sheet_by_index(0)
    tva = {10.0: 0.0, 20.0: 0.0}
    base_service = {10.0: 0.0, 20.0: 0.0}   # colonne VAT_base retenue par le service
    neg = collections.Counter()
    nlig = 0
    copie_ok = True
    ttc = 0.0
    vus = set()
    for r in range(2, sh.nrows):
        taux = sh.cell_value(r, C_TAUX)
        if taux == "":
            continue
        nlig += 1
        v = [sh.cell_value(r, c) for c in range(19)]
        for idx, nom in COLS6:
            x = v[idx]
            if isinstance(x, (int, float)) and x < 0:
                neg[nom] += 1
        # les 4 colonnes de ventilation sont-elles la recopie de 13 et 14 ?
        if taux == 10.0:
            if v[15] != v[13] or v[16] != v[14] or v[17] != "" or v[18] != "":
                copie_ok = False
        elif taux == 20.0:
            if v[17] != v[13] or v[18] != v[14] or v[15] != "" or v[16] != "":
                copie_ok = False
        if taux in tva:
            tva[taux] += num(v[C_TA])
            base_service[taux] += num(v[C_VATBASE])
        cle = (v[0], v[2], v[3])
        if cle not in vus:
            vus.add(cle)
            ttc += num(v[C_TTC])
    return dict(tva10=round(tva[10.0], 2), tva20=round(tva[20.0], 2),
                tva=round(tva[10.0] + tva[20.0], 2), neg=neg, nlig=nlig,
                copie_ok=copie_ok, ttc=round(ttc, 2),
                # base retenue par le service (colonne VAT_base) vs base deduite
                # de la TVA encaissee (colonne tax_amount / taux legal)
                bs10=round(base_service[10.0], 2), bs20=round(base_service[20.0], 2),
                bg10=round(tva[10.0] / 0.10, 2), bg20=round(tva[20.0] / 0.20, 2))


# ---------------------------------------------------------------------------
# 2. Detail des tickets (annexe C)
# ---------------------------------------------------------------------------
def lire_C(path):
    sh = xlrd.open_workbook(path).sheet_by_index(0)
    ttc_brut = collections.defaultdict(float)   # au taux porte par le fichier
    ttc_corr = collections.defaultdict(float)   # au taux legal (correction E/F)
    n_err = 0
    nlig = 0
    tickets = {}
    for r in range(1, sh.nrows):
        taux = sh.cell_value(r, 15)
        mtt = sh.cell_value(r, 16)
        cle = (sh.cell_value(r, 0), sh.cell_value(r, 1), sh.cell_value(r, 2))
        if isinstance(sh.cell_value(r, C_TVA - 2), (int, float)):
            tickets[cle] = (num(sh.cell_value(r, 5)), num(sh.cell_value(r, 6)))
        if not isinstance(mtt, (int, float)) or not isinstance(taux, (int, float)):
            continue
        nlig += 1
        ttc_brut[taux] += mtt
        f = sh.cell_value(r, 22)
        if isinstance(f, (int, float)) and f != 0:      # taux errone signale par le service
            n_err += 1
            ttc_corr[20.0 if taux == 10.0 else 10.0] += mtt
        else:
            ttc_corr[taux] += mtt
    def tva(d):
        return {k: round(v * k / (100 + k), 2) for k, v in d.items()}
    tb, tc = tva(ttc_brut), tva(ttc_corr)
    return dict(
        tva10=tc.get(10.0, 0.0), tva20=tc.get(20.0, 0.0),
        tva=round(tc.get(10.0, 0.0) + tc.get(20.0, 0.0), 2),
        tva_brut=round(tb.get(10.0, 0.0) + tb.get(20.0, 0.0), 2),
        n_err=n_err, nlig=nlig,
        tva_tickets=round(sum(x[1] for x in tickets.values()), 2),
        ttc_tickets=round(sum(x[0] for x in tickets.values()), 2),
        n_tickets=len(tickets))


print("Lecture des annexes G et C ...")
JG = {e: lire_G(G[e]) for e in EXOS}
JC = {e: lire_C(C[e]) for e in EXOS}

for e in EXOS:
    c = COMPTA[e]
    c["tva10"] = round(c["ht10"] * 0.10, 2)
    c["tva20"] = round(c["ht20"] * 0.20, 2)
    c["tva"] = round(c["tva10"] + c["tva20"], 2)
    print(f"  {e} : caisse {JG[e]['tva']:.2f} | tickets {JC[e]['tva']:.2f} | "
          f"compta 445710 {c['tva445710']:.2f}")

TOT_G = round(sum(JG[e]["tva"] for e in EXOS), 2)
TOT_C = round(sum(JC[e]["tva"] for e in EXOS), 2)
TOT_CPT = round(sum(COMPTA[e]["tva445710"] for e in EXOS), 2)
TOT_TK = round(sum(JC[e]["tva_tickets"] for e in EXOS), 2)
NEG = collections.Counter()
for e in EXOS:
    NEG.update(JG[e]["neg"])
NLIG_G = sum(JG[e]["nlig"] for e in EXOS)

print(f"  CUMUL : caisse {TOT_G:.2f} | tickets (par taux) {TOT_C:.2f} | "
      f"tickets (Tot_tva) {TOT_TK:.2f} | compta {TOT_CPT:.2f}")
print(f"  Ecart caisse / comptabilite : {TOT_G - TOT_CPT:+.2f} € "
      f"({(TOT_G - TOT_CPT) / TOT_CPT * 100:+.4f} %)")
print(f"  Lignes de ventilation lues dans l'annexe G : {NLIG_G}")
print(f"  Valeurs negatives par colonne : {dict(NEG)}")
print(f"  Les 4 colonnes de ventilation sont la recopie de VAT_base/tax_amount : "
      f"{all(JG[e]['copie_ok'] for e in EXOS)}")

# ===========================================================================
# XLSX
# ===========================================================================
HEAD = Font(bold=True, color="FFFFFF", size=11)
HEADFILL = PatternFill("solid", fgColor="0F766E")
SUBHEAD = Font(bold=True)
THIN = Side(style="thin", color="D9D9D9")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
EURO = u'# ##0,00\xa0"€";-# ##0,00\xa0"€"'
PCT = u'+0,000\xa0%;-0,000\xa0%'


def feuille(wb, titre, entete, lignes, euro_cols=(), pct_cols=(), widths=(),
            total_rows=()):
    ws = wb.create_sheet(titre) if wb.sheetnames != ["Sheet"] else wb.active
    if ws.title == "Sheet":
        ws.title = titre
    ws.append(entete)
    for lig in lignes:
        ws.append(lig)
    for r in range(2, ws.max_row + 1):
        for c in euro_cols:
            ws.cell(row=r, column=c).number_format = EURO
        for c in pct_cols:
            ws.cell(row=r, column=c).number_format = PCT
    for r in total_rows:
        rr = r if r > 0 else ws.max_row + r
        for c in range(1, len(entete) + 1):
            ws.cell(row=rr, column=c).font = SUBHEAD
    for c in range(1, len(entete) + 1):
        cell = ws.cell(row=1, column=c)
        cell.font = HEAD
        cell.fill = HEADFILL
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER
    ws.freeze_panes = "A2"
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w
    return ws


wb = openpyxl.Workbook()

# --- Onglet 1 : rapprochement par exercice et par taux ---------------------
lig = []
for e in EXOS:
    for taux, kg, kc, kk in ((10, "tva10", "tva10", "tva10"),
                             (20, "tva20", "tva20", "tva20")):
        a, b, d = JG[e][kg], JC[e][kc], COMPTA[e][kk]
        lig.append([LABEL[e], f"{taux} %", a, b, d, round(a - d, 2),
                    (a - d) / d if d else 0])
    a = JG[e]["tva"]
    d = COMPTA[e]["tva445710"]
    lig.append([LABEL[e], "TOTAL (445710)", a, JC[e]["tva"], d,
                round(a - d, 2), (a - d) / d])
lig.append(["CUMUL 3 EXERCICES", "TOTAL (445710)", TOT_G, TOT_C, TOT_CPT,
            round(TOT_G - TOT_CPT, 2), (TOT_G - TOT_CPT) / TOT_CPT])

feuille(wb, "1. Rapprochement TVA",
        ["Exercice", "Taux",
         "TVA journal de caisse (annexe G, tax_amount)",
         "TVA recalculee depuis le detail des tickets (annexe C)",
         "TVA collectee comptabilisee et reversee (445710 / 706300 / 706000)",
         "Ecart caisse - comptabilite (€)", "Ecart (%)"],
        lig, euro_cols=(3, 4, 5, 6), pct_cols=(7,),
        widths=[22, 17, 26, 28, 30, 22, 12],
        total_rows=[4, 7, 10, 11])

# --- Onglet 2 : bases d'imposition par taux --------------------------------
lb = []
for e in EXOS:
    for taux, ks, kg, kc in ((10, "bs10", "bg10", "ht10"), (20, "bs20", "bg20", "ht20")):
        s, g_, c = JG[e][ks], JG[e][kg], COMPTA[e][kc]
        lb.append([LABEL[e], f"{taux} %", s, g_, c, round(s - c, 2), round(g_ - c, 2)])
S_TOT = round(sum(JG[e]["bs10"] + JG[e]["bs20"] for e in EXOS), 2)
G_TOT = round(sum(JG[e]["bg10"] + JG[e]["bg20"] for e in EXOS), 2)
C_TOT = round(sum(COMPTA[e]["ht10"] + COMPTA[e]["ht20"] for e in EXOS), 2)
lb.append(["CUMUL 3 EXERCICES", "10 % + 20 %", S_TOT, G_TOT, C_TOT,
           round(S_TOT - C_TOT, 2), round(G_TOT - C_TOT, 2)])
print(f"  Base : colonne du service {S_TOT:.2f} | colonne de la caisse {G_TOT:.2f} | "
      f"comptabilite {C_TOT:.2f} (ecart colonne du service {S_TOT - C_TOT:+.2f})")

feuille(wb, "2. Bases par taux",
        ["Exercice", "Taux", "Base retenue par le service (VAT_base)",
         "Base deduite de la TVA encaissee (tax_amount / taux)",
         "Base en comptabilite (706300 / 706000)",
         "Ecart colonne du service - comptabilite",
         "Ecart colonne de la caisse - comptabilite"],
        lb, euro_cols=(3, 4, 5, 6, 7), widths=[22, 14, 26, 30, 26, 26, 26],
        total_rows=[0])

# --- Onglet 3 : controle ticket par ticket ---------------------------------
feuille(wb, "3. Controle par ticket",
        ["Exercice", "Nombre de tickets", "TVA totale des tickets (annexe C, Tot_tva)",
         "TVA journal de caisse (annexe G)", "TVA comptabilisee (445710)",
         "Ecart tickets - comptabilite (€)"],
        [[LABEL[e], JC[e]["n_tickets"], JC[e]["tva_tickets"], JG[e]["tva"],
          COMPTA[e]["tva445710"],
          round(JC[e]["tva_tickets"] - COMPTA[e]["tva445710"], 2)] for e in EXOS]
        + [["CUMUL 3 EXERCICES", sum(JC[e]["n_tickets"] for e in EXOS), TOT_TK,
            TOT_G, TOT_CPT, round(TOT_TK - TOT_CPT, 2)]],
        euro_cols=(3, 4, 5, 6), widths=[22, 18, 28, 24, 24, 24], total_rows=[0])

# --- Onglet 4 : les six colonnes visees p. 47 ------------------------------
feuille(wb, "4. Les six colonnes p47",
        ["Colonne de l'annexe G (p. 47 du courrier)", "Origine",
         "Lignes portant une valeur negative (3 exercices)",
         "Lignes de ventilation lues (3 exercices)"],
        [["VAT_base (base HT d'affichage)", "colonne native de l'export",
          NEG.get("VAT_base", 0), NLIG_G],
         ["tax_amount (TVA de la ligne)", "colonne native de l'export",
          NEG.get("tax_amount", 0), NLIG_G],
         ["Base TVA 10 %", "recopie de VAT_base si taux = 10 % (calcul du service)",
          NEG.get("Base TVA 10 %", 0), NLIG_G],
         ["TVA 10 %", "recopie de tax_amount si taux = 10 % (calcul du service)",
          NEG.get("TVA 10 %", 0), NLIG_G],
         ["Base TVA 20 %", "recopie de VAT_base si taux = 20 % (calcul du service)",
          NEG.get("Base TVA 20 %", 0), NLIG_G],
         ["TVA 20 %", "recopie de tax_amount si taux = 20 % (calcul du service)",
          NEG.get("TVA 20 %", 0), NLIG_G]],
        widths=[38, 46, 26, 24])

# --- Onglet 5 : erreurs de taux relevees par le service --------------------
feuille(wb, "5. Erreurs de taux annexe C",
        ["Exercice", "Lignes du detail des tickets",
         "Lignes dont le taux est signale errone par le service (col. E/F)",
         "TVA au taux porte par le fichier", "TVA au taux legal (col. F appliquee)",
         "TVA journal de caisse (annexe G)"],
        [[LABEL[e], JC[e]["nlig"], JC[e]["n_err"], JC[e]["tva_brut"], JC[e]["tva"],
          JG[e]["tva"]] for e in EXOS],
        euro_cols=(4, 5, 6), widths=[22, 22, 30, 24, 26, 24])

# --- Onglet 6 : methode ----------------------------------------------------
ws = wb.create_sheet("6. Methode")
for l in [
    ["Piece R1-tva-rapprochement.xlsx"],
    ["Reponse a la partie H du courrier de la DDFiP du Jura du 04/09/2026 (p. 46-47)."],
    [],
    ["Source 1", "Journal de caisse, annexes G1/G2/G3, colonne tax_amount : TVA figee par la caisse a chaque paiement, ventilee par le taux de la ligne (colonne taux_tva %)."],
    ["Source 2", "Detail des tickets, annexes C1/C2/C3 : TTC de chaque ligne (col. 17 Tot_rem Ttc) affecte de son taux legal, en appliquant la correction de taux portee par le service lui-meme en colonnes E et F de l'annexe C."],
    ["Source 3", "Comptabilite : TVA collectee 445710 et bases 706300 (10 %) / 706000 (20 %), chiffres reproduits par le service p. 26 de la proposition de rectifications du 18/05/2026."],
    [],
    ["Controle", "L'onglet 2 oppose, taux par taux, le total de la colonne VAT_base retenue par le service, le total de la base deduite de la TVA encaissee et la base comptabilisee."],
    ["Controle", "L'onglet 3 refait le total de TVA ticket par ticket a partir de la colonne Tot_tva de l'annexe C, sans utiliser aucune ventilation par taux."],
    ["Controle", "L'onglet 4 compte, colonne par colonne, les valeurs negatives des six dernieres colonnes de l'annexe G visees p. 47 du courrier, et indique lesquelles sont une construction du service."],
    [],
    ["Script", "scripts/reponse1-tva-rapprochement.py (recalculable de bout en bout depuis les annexes de caisse)."],
]:
    ws.append(l)
ws.column_dimensions["A"].width = 14
ws.column_dimensions["B"].width = 130
ws["A1"].font = Font(bold=True, size=13)
for r in range(1, ws.max_row + 1):
    ws.cell(row=r, column=2).alignment = Alignment(wrap_text=True, vertical="top")

os.makedirs(PIECES, exist_ok=True)
wb.save(OUT)
print("Ecrit :", OUT)
