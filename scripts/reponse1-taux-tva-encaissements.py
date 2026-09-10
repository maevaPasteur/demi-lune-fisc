#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reponse1-taux-tva-encaissements.py
================================================================================
Reponse DDFiP 39 du 04/09/2026, partie U "Motifs de rejet de comptabilite absent
dans la reponse" (p. 93), sous-points b/ (erreurs de taux de TVA article par
article) et c/ (differentiel d'encaissements par mode de reglement).

OBJET
  Le service affirme (p. 93) que les annexes C-1 a C-3 revelent "des erreurs
  d'application de taux de TVA sur les articles" et que les encaissements par
  mode de reglement different entre la caisse et la comptabilite, sans chiffrer
  ni l'un ni l'autre. On les chiffre ici, a partir de ses propres annexes.

  b/ TAUX DE TVA
     Les annexes C-1 a C-3 comportent deux colonnes ajoutees par le service :
       col 21 (E) "Erreur Taux TVA dans Base Envoyee Faux/Correct" -> "10 % / 20 %"
               (ligne portee a 10 %, taux legal 20 %) ou "20 % / 10 %" (inverse) ;
       col 22 (F) "Correction TVA Sur Taux" -> l'incidence en euros de la
               correction, signee (+ = TVA supplementaire due au Tresor).
     On totalise ces deux colonnes par exercice et par sens, et on rapporte le
     resultat a la TVA collectee declaree.
     On verifie ensuite si ces "erreurs" sont des erreurs de parametrage de fiche
     article : un article a UN taux dans le logiciel. On compte donc, par
     exercice, les references qui apparaissent dans le fichier AUX DEUX taux.

  c/ ENCAISSEMENTS
     Trois sources sont rapprochees :
       - annexe F (fichier des reglements, ligne a ligne, mode par mode) ;
       - annexe A (synthese de caisse, bloc "Encaissements Tickets Mode") ;
       - comptabilite, comptes de tresorerie, telle que le service la reproduit
         page 25 de la proposition de rectifications du 18/05/2026.
     On chiffre l'ecart par mode et par exercice, et on le rapporte au chiffre
     d'affaires TTC declare.

SOURCES (lecture seule)
  public/documents/caisse-enregistreuse/ANNEXE-C{1,2,3}_detail-tickets_*.xls
      col 9 Ref_prd | 10 Lib_ticket | 15 Taux_tva% | 16 Tot_rem Ttc
      col 21 (E) "Erreur Taux TVA" du service | 22 (F) "Correction TVA sur taux"
  public/documents/caisse-enregistreuse/ANNEXE-F{1,2,3}_reglements_*.xls
      col 9 mod_regl | 10 montant  (les dernieres lignes portent "TOTAL" col 8)
  public/documents/caisse-enregistreuse/ANNEXE-A{1,2,3}_synthese-CA_*.xls
      bloc "Encaissements Tickets Mode"
  public/documents/caisse-enregistreuse/ANNEXE-G{1,2,3}_journal-tva_*.xls
      col 12 taux_tva% | 14 tax_amount (TVA reellement encaissee)
  Comptabilite : proposition de rectifications du 18/05/2026, p. 25 (comptes de
  tresorerie) et p. 26 (706300 / 706000 / 445710 / 706800).

SORTIE
  public/documents/pieces-reponse-1/R1-taux-tva-et-encaissements.xlsx

USAGE
  python3 scripts/reponse1-taux-tva-encaissements.py
================================================================================
"""
import os
import collections

import xlrd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

ICI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(ICI, ".."))
CAISSE = os.path.join(ROOT, "public/documents/caisse-enregistreuse/")
PIECES = os.path.join(ROOT, "public/documents/pieces-reponse-1/")
OUT = os.path.join(PIECES, "R1-taux-tva-et-encaissements.xlsx")

EXOS = ["2022-2023", "2023-2024", "2024-2025"]
LABEL = {"2022-2023": "Ex. clos 31/03/2023",
         "2023-2024": "Ex. clos 31/03/2024",
         "2024-2025": "Ex. clos 31/03/2025"}
C = {e: CAISSE + f"ANNEXE-C{i}_detail-tickets_{e}.xls" for i, e in enumerate(EXOS, 1)}
F = {e: CAISSE + f"ANNEXE-F{i}_reglements_{e}.xls" for i, e in enumerate(EXOS, 1)}
A = {e: CAISSE + f"ANNEXE-A{i}_synthese-CA_{e}.xls" for i, e in enumerate(EXOS, 1)}
G = {e: CAISSE + f"ANNEXE-G{i}_journal-tva_{e}.xls" for i, e in enumerate(EXOS, 1)}

# --- Reperes issus de la proposition de rectifications du 18/05/2026 ---------
# p. 26 : comptabilite (706300 base 10 %, 706000 base 20 %, 445710 TVA collectee,
#         706800 pourboires).
COMPTA_TVA = {
    "2022-2023": dict(ht10=296105.87, ht20=64712.51, tva445710=42614.45,
                      pourboires=598.04, ca_ttc=404030.87),
    "2023-2024": dict(ht10=319179.31, ht20=72416.55, tva445710=46464.79,
                      pourboires=597.75, ca_ttc=438658.43),
    "2024-2025": dict(ht10=318345.43, ht20=70517.47, tva445710=46005.45,
                      pourboires=656.57, ca_ttc=435524.92),
}
# p. 25 : comptes de tresorerie, montants NETS retenus par le service lui-meme.
COMPTA_REGL = {
    "2022-2023": {"Carte bancaire": 370144.08, "Cheque": 4627.35,
                  "Ticket restaurant": 9486.32 + 935.10,
                  "Cheque vacances": 14715.00, "Cheque KDOLE": 290.00,
                  "Especes": 3330.63},
    "2023-2024": {"Carte bancaire": 399903.10, "Cheque": 3600.12,
                  "Ticket restaurant": 9105.04 + 1024.27,
                  "Cheque vacances": 23300.00, "Cheque KDOLE": 525.00,
                  "Especes": 5958.90},
    "2024-2025": {"Carte bancaire": 397677.38, "Cheque": 4529.10,
                  "Ticket restaurant": 4708.89 + 4392.72,
                  "Cheque vacances": 20405.00, "Cheque KDOLE": 390.00,
                  "Especes": 2804.75},
}
COMPTA_REGL_TOTAL = {"2022-2023": 403528.48, "2023-2024": 443416.43,
                     "2024-2025": 434907.84}
MODES = ["Carte bancaire", "Cheque", "Ticket restaurant", "Cheque vacances",
         "Cheque KDOLE", "Especes"]
MODE_DE_CODE = {"CB": "Carte bancaire", "CHQ": "Cheque", "TR": "Ticket restaurant",
                "CHV": "Cheque vacances", "ESP": "Especes"}
MODE_DE_LIB_A = {"Carte Bancaire": "Carte bancaire", "Chèque": "Cheque",
                 "Ticket restaurant": "Ticket restaurant",
                 "Chèque vacances": "Cheque vacances", "Espèce": "Especes"}


def num(v):
    return v if isinstance(v, (int, float)) else 0.0


def nbsp(s):
    return str(s).replace("\xa0", " ").strip()


# ===========================================================================
# 1. Taux de TVA : les colonnes E et F ajoutees par le service (annexes C)
# ===========================================================================
def lire_C(path):
    sh = xlrd.open_workbook(path).sheet_by_index(0)
    sens = collections.defaultdict(lambda: dict(n=0, ttc=0.0, inc=0.0))
    par_article = collections.defaultdict(lambda: dict(lib="", n10=0, n20=0))
    releve = collections.defaultdict(lambda: dict(lib="", n=0, ttc=0.0, inc=0.0))
    lignes = []
    n_lignes = 0
    for r in range(1, sh.nrows):
        taux = sh.cell_value(r, 15)
        ttc = sh.cell_value(r, 16)
        if not isinstance(taux, (int, float)) or not isinstance(ttc, (int, float)):
            continue
        n_lignes += 1
        ref = nbsp(sh.cell_value(r, 9))
        lib = nbsp(sh.cell_value(r, 10))
        pa = par_article[ref]
        pa["lib"] = pa["lib"] or lib
        if taux == 10.0:
            pa["n10"] += 1
        elif taux == 20.0:
            pa["n20"] += 1
        e = sh.cell_value(r, 21)
        if not isinstance(e, str) or not e.strip():
            continue
        s = nbsp(e)
        inc = num(sh.cell_value(r, 22))
        d = sens[s]
        d["n"] += 1
        d["ttc"] += ttc
        d["inc"] += inc
        k = (ref, s)
        rv = releve[k]
        rv["lib"] = rv["lib"] or lib
        rv["n"] += 1
        rv["ttc"] += ttc
        rv["inc"] += inc
        lignes.append((nbsp(sh.cell_value(r, 0)), nbsp(sh.cell_value(r, 1)),
                       nbsp(sh.cell_value(r, 2)).replace(".0", ""), ref, lib,
                       taux, round(ttc, 2), s, round(inc, 2)))
    return dict(n_lignes=n_lignes, sens=dict(sens), par_article=dict(par_article),
                releve=dict(releve), lignes=lignes)


def lire_G(path):
    """TVA reellement encaissee par la caisse (colonne tax_amount)."""
    sh = xlrd.open_workbook(path).sheet_by_index(0)
    t = 0.0
    for r in range(2, sh.nrows):
        if sh.cell_value(r, 12) == "":
            continue
        t += num(sh.cell_value(r, 14))
    return round(t, 2)


# ===========================================================================
# 2. Encaissements : annexes F et A
# ===========================================================================
def lire_F(path):
    sh = xlrd.open_workbook(path).sheet_by_index(0)
    agg = collections.Counter()
    nb = collections.Counter()
    total_declare = None
    for r in range(1, sh.nrows):
        c8 = nbsp(sh.cell_value(r, 8))
        code = nbsp(sh.cell_value(r, 9))
        montant = num(sh.cell_value(r, 10))
        if c8 == "TOTAL GENERAL":          # ligne de total du fichier
            total_declare = round(montant, 2)
            continue
        if c8 == "TOTAL":                  # totaux par mode, deja dans le detail
            continue
        mode = MODE_DE_CODE.get(code, code)
        agg[mode] += montant
        nb[mode] += 1
    return dict(par_mode={k: round(v, 2) for k, v in agg.items()},
                nb=dict(nb), total=round(sum(agg.values()), 2),
                total_declare=total_declare)


def lire_A(path):
    sh = xlrd.open_workbook(path).sheet_by_index(0)
    agg = collections.Counter()
    nb = collections.Counter()
    total = None
    dans_bloc = False
    for r in range(sh.nrows):
        c0 = nbsp(sh.cell_value(r, 0))
        if c0.startswith("Encaissements Tickets Mode"):
            dans_bloc = True
            continue
        if not dans_bloc:
            continue
        if c0 == "":
            dans_bloc = False
            continue
        if c0 == "TOTAL":
            total = round(num(sh.cell_value(r, 2)), 2)
            dans_bloc = False
            continue
        mode = MODE_DE_LIB_A.get(c0, c0)
        agg[mode] += num(sh.cell_value(r, 2))
        nb[mode] += num(sh.cell_value(r, 1))
    return dict(par_mode={k: round(v, 2) for k, v in agg.items()},
                nb={k: int(v) for k, v in nb.items()},
                total=round(sum(agg.values()), 2), total_declare=total)


print("Lecture des annexes C (taux de TVA) ...")
JC = {e: lire_C(C[e]) for e in EXOS}
print("Lecture des annexes G (TVA encaissee) ...")
JG = {e: lire_G(G[e]) for e in EXOS}
print("Lecture des annexes F et A (encaissements) ...")
JF = {e: lire_F(F[e]) for e in EXOS}
JA = {e: lire_A(A[e]) for e in EXOS}

S1020 = "10 % / 20 %"   # ligne a 10 %, taux legal 20 % -> TVA supplementaire
S2010 = "20 % / 10 %"   # ligne a 20 %, taux legal 10 % -> TVA payee en trop

for e in EXOS:
    d = JC[e]
    a = d["sens"].get(S1020, dict(n=0, ttc=0.0, inc=0.0))
    b = d["sens"].get(S2010, dict(n=0, ttc=0.0, inc=0.0))
    net = a["inc"] + b["inc"]
    deux = sum(1 for v in d["par_article"].values() if v["n10"] and v["n20"])
    print(f"  {e} : lignes {d['n_lignes']} | signalees {a['n']+b['n']} "
          f"({a['n']} 10->20 / {b['n']} 20->10) | incidence nette {net:+.2f} € | "
          f"references aux deux taux {deux}/{len(d['par_article'])}")
    print(f"           caisse (annexe F) {JF[e]['total']:.2f} € | "
          f"annexe A {JA[e]['total']:.2f} € | comptabilite {COMPTA_REGL_TOTAL[e]:.2f} €")

NET_TVA = round(sum(JC[e]["sens"].get(S1020, {"inc": 0})["inc"]
                    + JC[e]["sens"].get(S2010, {"inc": 0})["inc"] for e in EXOS), 2)
TVA_DECL = round(sum(COMPTA_TVA[e]["tva445710"] for e in EXOS), 2)
print(f"  CUMUL incidence nette des 'erreurs de taux' : {NET_TVA:+.2f} € "
      f"sur {TVA_DECL:.2f} € de TVA collectee declaree "
      f"({NET_TVA / TVA_DECL * 100:+.2f} %)")

ECART_REGL = {e: round(COMPTA_REGL_TOTAL[e] - JF[e]["total"], 2) for e in EXOS}
print(f"  CUMUL ecart comptabilite / caisse (annexe F) : "
      f"{sum(ECART_REGL.values()):+.2f} €")

# ===========================================================================
# XLSX
# ===========================================================================
HEAD = Font(bold=True, color="FFFFFF", size=11)
HEADFILL = PatternFill("solid", fgColor="0F766E")
SUB = Font(bold=True)
THIN = Side(style="thin", color="D9D9D9")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
EUR = '#,##0.00" €"'
PCT = '0.000"%"'

wb = openpyxl.Workbook()


def feuille(titre, entetes, largeurs):
    ws = wb.create_sheet(titre)
    ws.append(entetes)
    for i, c in enumerate(ws[1], 1):
        c.font = HEAD
        c.fill = HEADFILL
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        ws.column_dimensions[get_column_letter(i)].width = largeurs[i - 1]
    ws.freeze_panes = "A2"
    return ws


def fmt(ws, col_eur=(), col_pct=(), debut=2):
    for row in ws.iter_rows(min_row=debut):
        for c in row:
            c.border = BORDER
            if c.column in col_eur:
                c.number_format = EUR
            elif c.column in col_pct:
                c.number_format = PCT


# --- 0. Lecture -------------------------------------------------------------
ws = wb.active
ws.title = "Lecture"
ws.column_dimensions["A"].width = 118
LECTURE = [
    ("R1 : taux de TVA article par article et encaissements par mode de règlement", True),
    ("", False),
    ("Pièce établie en réponse à la partie U de la réponse de la DDFiP du Jura du 04/09/2026 (p. 93),", False),
    ("sous-points b/ (erreurs de taux de TVA sur les articles) et c/ (différentiel d’encaissements).", False),
    ("", False),
    ("Toutes les données proviennent des annexes du service, en lecture seule. Script reproductible :", False),
    ("scripts/reponse1-taux-tva-encaissements.py", False),
    ("", False),
    ("b/ TAUX DE TVA", True),
    ("Les annexes C-1 à C-3 comportent deux colonnes ajoutées par le vérificateur : la colonne E", False),
    ("« Erreur Taux TVA dans Base Envoyée Faux/Correct » et la colonne F « Correction TVA sur taux »", False),
    ("(incidence en euros, signée). Les onglets TVA-1 à TVA-4 totalisent ces deux colonnes.", False),
    ("L’onglet TVA-2 vérifie si ces écarts peuvent être des erreurs de paramétrage : dans un logiciel", False),
    ("de caisse, une fiche article porte un seul taux. Or la plupart des références apparaissent dans", False),
    ("le même fichier tantôt à 10 %, tantôt à 20 %.", False),
    ("", False),
    ("c/ ENCAISSEMENTS", True),
    ("Trois sources sont rapprochées : l’annexe F (fichier des règlements, ligne à ligne), l’annexe A", False),
    ("(synthèse de caisse, bloc « Encaissements Tickets Mode ») et la comptabilité (comptes de", False),
    ("trésorerie 511200, 511210, 511220, 511221, 511230, 511240 et 530), telle que le service la", False),
    ("reproduit page 25 de la proposition de rectifications du 18/05/2026.", False),
    ("", False),
    ("Les totaux par mode recalculés depuis l’annexe F reproduisent exactement le tableau publié par", False),
    ("le service page 24 de la proposition de rectifications : le calcul est donc contrôlable.", False),
]
for txt, gras in LECTURE:
    ws.append([txt])
    if gras:
        ws.cell(ws.max_row, 1).font = SUB

# --- TVA-1 : synthèse -------------------------------------------------------
ws = feuille("TVA-1 Synthèse",
             ["Exercice", "Lignes d’articles", "Lignes signalées",
              "dont 10 % au lieu de 20 %", "TTC concerné",
              "TVA supplémentaire due (+)", "dont 20 % au lieu de 10 %",
              "TTC concerné", "TVA payée en trop (−)", "Incidence nette",
              "TVA collectée déclarée (445710)", "Incidence nette / TVA déclarée"],
             [22, 16, 15, 16, 14, 16, 16, 14, 16, 14, 18, 16])
for e in EXOS:
    d = JC[e]
    a = d["sens"].get(S1020, dict(n=0, ttc=0.0, inc=0.0))
    b = d["sens"].get(S2010, dict(n=0, ttc=0.0, inc=0.0))
    net = round(a["inc"] + b["inc"], 2)
    tva = COMPTA_TVA[e]["tva445710"]
    ws.append([LABEL[e], d["n_lignes"], a["n"] + b["n"], a["n"], round(a["ttc"], 2),
               round(a["inc"], 2), b["n"], round(b["ttc"], 2), round(b["inc"], 2),
               net, tva, round(net / tva * 100, 3)])
tot_a = sum(JC[e]["sens"].get(S1020, {"n": 0})["n"] for e in EXOS)
tot_b = sum(JC[e]["sens"].get(S2010, {"n": 0})["n"] for e in EXOS)
ws.append(["CUMUL 3 exercices", sum(JC[e]["n_lignes"] for e in EXOS), tot_a + tot_b,
           tot_a, round(sum(JC[e]["sens"].get(S1020, {"ttc": 0})["ttc"] for e in EXOS), 2),
           round(sum(JC[e]["sens"].get(S1020, {"inc": 0})["inc"] for e in EXOS), 2),
           tot_b, round(sum(JC[e]["sens"].get(S2010, {"ttc": 0})["ttc"] for e in EXOS), 2),
           round(sum(JC[e]["sens"].get(S2010, {"inc": 0})["inc"] for e in EXOS), 2),
           NET_TVA, TVA_DECL, round(NET_TVA / TVA_DECL * 100, 3)])
for c in ws[ws.max_row]:
    c.font = SUB
fmt(ws, col_eur=(5, 6, 8, 9, 10, 11), col_pct=(12,))

# --- TVA-2 : articles présents aux deux taux --------------------------------
ws = feuille("TVA-2 Articles aux deux taux",
             ["Exercice", "Référence", "Libellé", "Lignes à 10 %", "Lignes à 20 %",
              "Présent aux deux taux"],
             [22, 12, 34, 13, 13, 18])
for e in EXOS:
    for ref, v in sorted(JC[e]["par_article"].items(),
                         key=lambda kv: -(kv[1]["n10"] + kv[1]["n20"])):
        ws.append([LABEL[e], ref, v["lib"], v["n10"], v["n20"],
                   "OUI" if v["n10"] and v["n20"] else "non"])
fmt(ws)

# --- TVA-3 : relevé par article --------------------------------------------
ws = feuille("TVA-3 Relevé par article",
             ["Exercice", "Référence", "Libellé", "Sens de l’écart signalé",
              "Lignes", "TTC concerné", "Incidence TVA (€)"],
             [22, 12, 34, 20, 10, 15, 16])
for e in EXOS:
    for (ref, s), v in sorted(JC[e]["releve"].items(), key=lambda kv: kv[1]["inc"]):
        ws.append([LABEL[e], ref, v["lib"], s, v["n"], round(v["ttc"], 2),
                   round(v["inc"], 2)])
fmt(ws, col_eur=(6, 7))

# --- TVA-4 : détail des lignes signalées ------------------------------------
ws = feuille("TVA-4 Lignes signalées",
             ["Exercice", "Date", "Heure", "N° note", "Référence", "Libellé",
              "Taux porté au fichier", "TTC de la ligne", "Sens de l’écart signalé",
              "Incidence TVA (€)"],
             [22, 12, 8, 10, 12, 32, 15, 14, 20, 15])
for e in EXOS:
    for l in JC[e]["lignes"]:
        ws.append([LABEL[e]] + list(l))
fmt(ws, col_eur=(8, 10))

# --- ENC-1 : caisse, annexe F ----------------------------------------------
ws = feuille("ENC-1 Caisse (annexe F)",
             ["Exercice", "Mode de règlement", "Nombre de règlements",
              "Montant recalculé", "Total du fichier (ligne TOTAL GENERAL)"],
             [22, 22, 18, 16, 26])
for e in EXOS:
    for m in MODES:
        if m in JF[e]["par_mode"]:
            ws.append([LABEL[e], m, JF[e]["nb"].get(m, 0), JF[e]["par_mode"][m], ""])
    ws.append([LABEL[e], "TOTAL", sum(JF[e]["nb"].values()), JF[e]["total"],
               JF[e]["total_declare"]])
    for c in ws[ws.max_row]:
        c.font = SUB
fmt(ws, col_eur=(4, 5))

# --- ENC-2 : annexe A contre annexe F --------------------------------------
ws = feuille("ENC-2 Annexe A vs annexe F",
             ["Exercice", "Mode de règlement", "Annexe A (synthèse de caisse)",
              "Annexe F (fichier des règlements)", "Écart A − F",
              "Total porté au fichier (annexe A)"],
             [22, 22, 22, 22, 16, 22])
for e in EXOS:
    for m in MODES:
        a = JA[e]["par_mode"].get(m)
        f = JF[e]["par_mode"].get(m)
        if a is None and f is None:
            continue
        ws.append([LABEL[e], m, a or 0.0, f or 0.0, round((a or 0.0) - (f or 0.0), 2)])
    ws.append([LABEL[e], "TOTAL", JA[e]["total"], JF[e]["total"],
               round(JA[e]["total"] - JF[e]["total"], 2), JA[e]["total_declare"]])
    for c in ws[ws.max_row]:
        c.font = SUB
fmt(ws, col_eur=(3, 4, 5, 6))

# --- ENC-3 : caisse contre comptabilité ------------------------------------
ws = feuille("ENC-3 Caisse vs comptabilité",
             ["Exercice", "Mode de règlement", "Caisse (annexe F)",
              "Comptabilité (proposition p. 25)", "Écart comptabilité − caisse",
              "Écart / CA TTC déclaré"],
             [22, 22, 18, 24, 20, 18])
for e in EXOS:
    ca = COMPTA_TVA[e]["ca_ttc"]
    for m in MODES:
        f = JF[e]["par_mode"].get(m, 0.0)
        cpt = COMPTA_REGL[e].get(m, 0.0)
        ws.append([LABEL[e], m, f, cpt, round(cpt - f, 2),
                   round((cpt - f) / ca * 100, 3)])
    ws.append([LABEL[e], "TOTAL", JF[e]["total"], COMPTA_REGL_TOTAL[e],
               ECART_REGL[e], round(ECART_REGL[e] / ca * 100, 3)])
    for c in ws[ws.max_row]:
        c.font = SUB
ca_tot = round(sum(COMPTA_TVA[e]["ca_ttc"] for e in EXOS), 2)
f_tot = round(sum(JF[e]["total"] for e in EXOS), 2)
c_tot = round(sum(COMPTA_REGL_TOTAL[e] for e in EXOS), 2)
ws.append(["CUMUL 3 exercices", "TOTAL", f_tot, c_tot, round(c_tot - f_tot, 2),
           round((c_tot - f_tot) / ca_tot * 100, 3)])
for c in ws[ws.max_row]:
    c.font = SUB
fmt(ws, col_eur=(3, 4, 5), col_pct=(6,))

# --- ENC-4 : contrôle TVA encaissée ----------------------------------------
ws = feuille("ENC-4 Contrôle TVA caisse",
             ["Exercice", "TVA encaissée par la caisse (annexe G, tax_amount)",
              "TVA collectée déclarée (445710)", "Écart", "Écart / TVA déclarée"],
             [22, 30, 24, 14, 18])
for e in EXOS:
    t = COMPTA_TVA[e]["tva445710"]
    ws.append([LABEL[e], JG[e], t, round(JG[e] - t, 2), round((JG[e] - t) / t * 100, 3)])
g_tot = round(sum(JG[e] for e in EXOS), 2)
ws.append(["CUMUL 3 exercices", g_tot, TVA_DECL, round(g_tot - TVA_DECL, 2),
           round((g_tot - TVA_DECL) / TVA_DECL * 100, 3)])
for c in ws[ws.max_row]:
    c.font = SUB
fmt(ws, col_eur=(2, 3, 4), col_pct=(5,))

os.makedirs(PIECES, exist_ok=True)
wb.save(OUT)
print("Ecrit :", OUT)
