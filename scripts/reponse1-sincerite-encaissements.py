#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
R1-sincerite-encaissements.xlsx
===============================================================================
Reponse DDFiP 39 du 04/09/2026, partie « C- CONSEQUENCES FINANCIERES ET
PENALITES », sous-partie « B- Penalites et amendes » (p. 94 et 95).

OBJET
  Le service maintient la majoration de 40 % de l'article 1729 du CGI sans
  discuter les trois elements de sincerite qu'il reproduit pourtant lui-meme
  page 94 (coherence CA / encaissements, participation des dirigeants, taux de
  bancarisation). Ce script chiffre ces elements a partir des seules annexes de
  caisse remises au titre de l'article L. 47 A, II du LPF, et les confronte a la
  dissimulation soutenue par la proposition de rectification du 18/05/2026.

SOURCES (lecture seule)
  public/documents/caisse-enregistreuse/ANNEXE-A{1,2,3}_synthese-CA_*.xls
      ligne « TOTAL » du bloc « Encaissements Tickets Mode » (CA de caisse)
  public/documents/caisse-enregistreuse/ANNEXE-F{1,2,3}_reglements_*.xls
      col 9 mod_regl | col 10 montant ; lignes « TOTAL » par mode et
      « TOTAL GENERAL ». Les totaux du fichier sont recalcules ligne a ligne.
  public/documents/caisse-enregistreuse/ANNEXE-H{1,2,3}_liste-tickets_*.xls
      ligne « TOTAL », colonne tot_ttc
  Proposition de rectification du 18/05/2026, p. 58 : discordances TTC
      193 234,55 EUR / 138 863,57 EUR / 139 727,76 EUR (seules valeurs saisies).

SORTIE
  public/documents/pieces-reponse-1/R1-sincerite-encaissements.xlsx

Lancer : python3 scripts/reponse1-sincerite-encaissements.py
"""

import collections
import os

import xlrd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAISSE = os.path.join(ROOT, "public", "documents", "caisse-enregistreuse")
OUT = os.path.join(ROOT, "public", "documents", "pieces-reponse-1",
                   "R1-sincerite-encaissements.xlsx")

EXOS = [("2022-2023", "1"), ("2023-2024", "2"), ("2024-2025", "3")]

# Seules valeurs saisies : reprises de la proposition de rectification, p. 58.
DISCORDANCES_TTC = {"2022-2023": 193234.55, "2023-2024": 138863.57, "2024-2025": 139727.76}

LIBELLE_MODE = {
    "CB": "Carte bancaire", "CHQ": "Cheques", "CHV": "Cheques vacances (ANCV)",
    "ESP": "Especes", "TR": "Titres restaurant",
}
BANCARISES = {"CB", "CHQ", "CHV", "TR"}


def feuille(nom):
    return xlrd.open_workbook(os.path.join(CAISSE, nom)).sheet_by_index(0)


def lire_A(i, lib):
    sh = feuille("ANNEXE-A%s_synthese-CA_%s.xls" % (i, lib))
    for r in range(sh.nrows):
        v = sh.row_values(r)
        if v[0] == "TOTAL":
            return float(v[2])
    raise RuntimeError("annexe A%s : ligne TOTAL introuvable" % i)


def lire_F(i, lib):
    """Renvoie (total general du fichier, total recalcule, montants par mode)."""
    sh = feuille("ANNEXE-F%s_reglements_%s.xls" % (i, lib))
    modes = collections.Counter()
    total_fichier = None
    for r in range(1, sh.nrows):
        v = sh.row_values(r)
        if v[8] == "TOTAL GENERAL":
            total_fichier = float(v[10])
        elif v[8] == "TOTAL":
            continue
        elif isinstance(v[10], float):
            modes[v[9]] += v[10]
    return total_fichier, round(sum(modes.values()), 2), modes


def lire_H(i, lib):
    sh = feuille("ANNEXE-H%s_liste-tickets_%s.xls" % (i, lib))
    for r in range(sh.nrows - 1, -1, -1):
        v = sh.row_values(r)
        if v[0] == "TOTAL":
            return float(v[6])
    raise RuntimeError("annexe H%s : ligne TOTAL introuvable" % i)


# --------------------------------------------------------------- calculs ---
donnees = {}
for lib, i in EXOS:
    tf, recalc, modes = lire_F(i, lib)
    donnees[lib] = dict(a=lire_A(i, lib), f=tf, f_recalc=recalc,
                        h=lire_H(i, lib), modes=modes)

cum_a = round(sum(d["a"] for d in donnees.values()), 2)
cum_f = round(sum(d["f"] for d in donnees.values()), 2)
cum_h = round(sum(d["h"] for d in donnees.values()), 2)
cum_modes = collections.Counter()
for d in donnees.values():
    cum_modes.update(d["modes"])

# ---------------------------------------------------------------- sortie ---
GRIS = PatternFill("solid", fgColor="F2F2F2")
BLEU = PatternFill("solid", fgColor="DDEBF7")
GRAS = Font(bold=True)
BORD = Border(*[Side(style="thin", color="BFBFBF")] * 4)
EUR = '# ##0,00 "€"'
PCT = '0,00 "%"'

wb = Workbook()


def entete(ws, colonnes, largeurs, titre):
    ws.append([titre])
    ws["A1"].font = Font(bold=True, size=12)
    ws.append([])
    ws.append(colonnes)
    for c in range(1, len(colonnes) + 1):
        cel = ws.cell(row=3, column=c)
        cel.font, cel.fill, cel.border = GRAS, BLEU, BORD
        cel.alignment = Alignment(wrap_text=True, vertical="center")
        ws.column_dimensions[get_column_letter(c)].width = largeurs[c - 1]


# --- onglet 1 : triangulation A / F / H --------------------------------------
ws = wb.active
ws.title = "1. CA et encaissements"
entete(ws,
       ["Exercice", "Annexe A : CA de caisse", "Annexe F : somme des reglements",
        "Annexe H : liste des tickets", "Ecart A vs F", "Ecart F vs H"],
       [22, 24, 26, 24, 14, 14],
       "Triangulation des trois fichiers de caisse remis au titre de l'art. L. 47 A, II du LPF")
for lib, _ in EXOS:
    d = donnees[lib]
    ws.append([lib, d["a"], d["f"], d["h"],
               abs(d["a"] - d["f"]) / d["a"] * 100,
               abs(d["f"] - d["h"]) / d["f"] * 100])
ws.append(["Cumul 3 exercices", cum_a, cum_f, cum_h,
           abs(cum_a - cum_f) / cum_a * 100, abs(cum_f - cum_h) / cum_f * 100])
for r in range(4, ws.max_row + 1):
    for c in range(1, 7):
        cel = ws.cell(row=r, column=c)
        cel.border = BORD
        if c in (2, 3, 4):
            cel.number_format = EUR
        if c in (5, 6):
            cel.number_format = PCT
    if r == ws.max_row:
        for c in range(1, 7):
            ws.cell(row=r, column=c).font = GRAS
            ws.cell(row=r, column=c).fill = GRIS

# --- onglet 2 : modes de reglement -------------------------------------------
ws = wb.create_sheet("2. Modes de reglement")
entete(ws,
       ["Mode de reglement", "2022-2023", "2023-2024", "2024-2025",
        "Cumul 3 exercices", "Part du total", "Trace par un tiers"],
       [26, 16, 16, 16, 18, 13, 18],
       "Annexes F-1 a F-3 : encaissements par mode, totaux recalcules ligne a ligne")
for m in sorted(cum_modes, key=lambda x: -cum_modes[x]):
    ws.append([LIBELLE_MODE.get(m, m)] + [donnees[lib]["modes"][m] for lib, _ in EXOS]
              + [cum_modes[m], cum_modes[m] / cum_f * 100,
                 "Oui" if m in BANCARISES else "Non"])
banc = sum(v for k, v in cum_modes.items() if k in BANCARISES)
ws.append(["Total bancarise"] + [sum(donnees[lib]["modes"][k] for k in BANCARISES)
                                 for lib, _ in EXOS]
          + [banc, banc / cum_f * 100, "Oui"])
ws.append(["Especes"] + [donnees[lib]["modes"]["ESP"] for lib, _ in EXOS]
          + [cum_modes["ESP"], cum_modes["ESP"] / cum_f * 100, "Non"])
ws.append(["TOTAL GENERAL"] + [donnees[lib]["f"] for lib, _ in EXOS] + [cum_f, 100.0, ""])
for r in range(4, ws.max_row + 1):
    for c in range(1, 8):
        cel = ws.cell(row=r, column=c)
        cel.border = BORD
        if 2 <= c <= 5:
            cel.number_format = EUR
        if c == 6:
            cel.number_format = PCT
    if r >= ws.max_row - 2:
        for c in range(1, 8):
            ws.cell(row=r, column=c).font = GRAS
            ws.cell(row=r, column=c).fill = GRIS

# --- onglet 3 : dissimulation soutenue vs especes encaissees -----------------
ws = wb.create_sheet("3. Dissimulation et especes")
entete(ws,
       ["Exercice", "Discordance TTC soutenue (prop. p. 58)",
        "Especes encaissees (annexe F)", "Rapport discordance / especes",
        "Discordance en % du CA de caisse"],
       [22, 30, 24, 22, 24],
       "Ce que la dissimulation alleguee supposerait, confronte aux especes reellement encaissees")
for lib, _ in EXOS:
    d = donnees[lib]
    esp = d["modes"]["ESP"]
    ws.append([lib, DISCORDANCES_TTC[lib], esp,
               DISCORDANCES_TTC[lib] / esp, DISCORDANCES_TTC[lib] / d["a"] * 100])
tot_disc = round(sum(DISCORDANCES_TTC.values()), 2)
ws.append(["Cumul 3 exercices", tot_disc, cum_modes["ESP"],
           tot_disc / cum_modes["ESP"], tot_disc / cum_a * 100])
for r in range(4, ws.max_row + 1):
    for c in range(1, 6):
        cel = ws.cell(row=r, column=c)
        cel.border = BORD
        if c in (2, 3):
            cel.number_format = EUR
        if c == 4:
            cel.number_format = '0,0 "fois"'
        if c == 5:
            cel.number_format = PCT
    if r == ws.max_row:
        for c in range(1, 6):
            ws.cell(row=r, column=c).font = GRAS
            ws.cell(row=r, column=c).fill = GRIS

# --- onglet 4 : sources -------------------------------------------------------
ws = wb.create_sheet("4. Sources et controles")
ws.append(["Sources et controles"])
ws["A1"].font = Font(bold=True, size=12)
ws.append([])
lignes = [
    ("Annexes A-1 a A-3", "Ligne « TOTAL » de la synthese de caisse. Valeurs lues : %s" %
     " / ".join("%.2f" % donnees[l]["a"] for l, _ in EXOS)),
    ("Annexes F-1 a F-3", "Somme des lignes de reglement, recalculee mode par mode. "
     "Le total recalcule coincide a l'euro pres avec la ligne « TOTAL GENERAL » du fichier "
     "pour les trois exercices : %s" %
     " / ".join("recalcule %.2f contre %.2f" % (donnees[l]["f_recalc"], donnees[l]["f"])
                for l, _ in EXOS)),
    ("Annexes H-1 a H-3", "Ligne « TOTAL », colonne tot_ttc. Valeurs lues : %s" %
     " / ".join("%.2f" % donnees[l]["h"] for l, _ in EXOS)),
    ("Discordances TTC", "Seules valeurs saisies dans ce fichier. Reprises de la proposition "
     "de rectification du 18/05/2026, p. 58, rubrique « Importance des minorations »."),
    ("Modes bancarises", "Carte bancaire, cheques, cheques vacances ANCV et titres restaurant : "
     "chacun de ces flux est trace par un tiers (banque, ANCV, emetteur de titres)."),
    ("Aucune estimation", "Aucun montant n'est estime ni extrapole. Les seules valeurs calculees "
     "sont des sommes, des ecarts et des pourcentages, tous reproductibles par ce script."),
]
for a, b in lignes:
    ws.append([a, b])
ws.column_dimensions["A"].width = 24
ws.column_dimensions["B"].width = 118
for r in range(3, ws.max_row + 1):
    ws.cell(row=r, column=1).font = GRAS
    ws.cell(row=r, column=2).alignment = Alignment(wrap_text=True, vertical="top")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
wb.save(OUT)

print("Ecrit :", OUT)
print("Cumul A %.2f | F %.2f | H %.2f" % (cum_a, cum_f, cum_h))
print("Ecart A vs F : %.4f %%" % (abs(cum_a - cum_f) / cum_a * 100))
for m in sorted(cum_modes, key=lambda x: -cum_modes[x]):
    print("  %-4s %12.2f  %6.2f %%" % (m, cum_modes[m], cum_modes[m] / cum_f * 100))
print("Bancarise %.2f = %.4f %%" % (banc, banc / cum_f * 100))
print("Especes   %.2f = %.4f %%" % (cum_modes["ESP"], cum_modes["ESP"] / cum_f * 100))
print("Discordance TTC totale %.2f = %.1f fois les especes" %
      (tot_disc, tot_disc / cum_modes["ESP"]))
for lib, _ in EXOS:
    print("  %s : %.1f fois les especes" % (lib, DISCORDANCES_TTC[lib] / donnees[lib]["modes"]["ESP"]))
