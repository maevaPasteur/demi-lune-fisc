#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REPONSE 1 - Partie G : le compteur perpetuel de la caisse et l'origine des
quatre montants opposes par le service
=========================================================================
Reponse DDFiP 39 du 04/09/2026, p. 38 a 46 (et proposition du 18/05/2026,
parties IX a XIII).

Le service oppose quatre montants de chiffre d'affaires par exercice
(annexes B, C, F et G), y voit une « fluctuation » et en deduit que les
donnees de caisse seraient « de nature changeante », puis « de nature
instable », puis depourvues d'archive inalterable.

Ce script etablit, a partir des seuls fichiers de caisse remis au service :

  1. que les annexes H et G portent des compteurs cumulatifs jamais remis a
     zero (colonnes tot_sum et tot_tax_sum), dont la valeur d'ouverture est
     intitulee « A NOUVEAUX » dans le fichier, et que ces colonnes portent
     deux series distinctes et non une seule ;
  2. que la valeur atteinte a la fin d'un exercice est reprise au centime
     comme valeur d'ouverture de l'exercice suivant, sur les deux series et
     sur les deux colonnes, soit huit raccords sans ecart ;
  3. que la somme des tickets de la premiere serie donne les montants des
     annexes B, et les deux series reunies ceux des annexes C ;
  4. que l'ecart entre ces deux lectures correspond exactement aux tickets
     clotures apres la derniere ligne du fichier ;
  5. que l'annexe B (extraction du 10/02/2026) est un sous-ensemble strict
     de l'annexe C (remise du 13/03/2026) : aucune ligne de B n'est absente
     de C, et les lignes supplementaires de C expliquent au centime l'ecart
     de chiffre d'affaires entre les deux ;
  6. que la colonne de controle creee par le service (prix unitaire x
     quantite) reproduit le chiffre d'affaires de l'annexe C, et non celui
     de l'annexe B.

READ-ONLY sur les sources. Sortie :
  public/documents/pieces-reponse-1/R1-compteur-perpetuel.xlsx

Lancer :  python3 scripts/reponse1-compteur-perpetuel.py
"""

import collections
import datetime
import os
from decimal import Decimal

import xlrd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAISSE = os.path.join(ROOT, "public", "documents", "caisse-enregistreuse")
OUT_DIR = os.path.join(ROOT, "public", "documents", "pieces-reponse-1")
OUT = os.path.join(OUT_DIR, "R1-compteur-perpetuel.xlsx")

EXOS = [("2022-2023", "1"), ("2023-2024", "2"), ("2024-2025", "3")]

# Montants opposes par le service (reponse du 04/09/2026 p. 40 et p. 45,
# proposition du 18/05/2026 p. 28). Repris tels qu'il les ecrit.
SERVICE = {
    "2022-2023": {"B": 403370.42, "C": 403370.42, "F": 403402.87, "G": 403324.72},
    "2023-2024": {"B": 437992.92, "C": 438281.12, "F": 439600.30, "G": 437881.12},
    "2024-2025": {"B": 434827.86, "C": 435594.96, "F": 435146.29, "G": 434709.26},
}


def sheet(nom):
    return xlrd.open_workbook(os.path.join(CAISSE, nom)).sheet_by_index(0)


def xdate(v):
    return datetime.datetime(*xlrd.xldate_as_tuple(v, 0)).strftime("%Y-%m-%d")


def d2(x):
    """Arrondi decimal a deux decimales, sans passer par le binaire."""
    return Decimal(repr(round(float(x), 2)))


# ------------------------------------------------------------------ lecture --
def lire_H(i, lib):
    """Annexe H : liste des tickets. Renvoie l'ouverture des deux compteurs et
    la liste des tickets (date, heure, no, z, ttc, tva, tot_sum, tot_tax_sum)."""
    sh = sheet("ANNEXE-H%s_liste-tickets_%s.xls" % (i, lib))
    ouv = (sh.cell_value(1, 8), sh.cell_value(1, 9))  # ligne « A NOUVEAUX »
    fin = [r for r in range(sh.nrows) if sh.cell_value(r, 0) == "TOTAL"][0]
    tickets = []
    for r in range(2, fin):
        v = sh.row_values(r)
        if not isinstance(v[8], float):
            continue
        tickets.append(dict(date=v[0], heure=v[1], no=v[2], z=v[4],
                            ttc=v[6], tva=v[7], somme=v[8], taxe=v[9]))
    total = [sh.cell_value(fin, c) for c in (6, 7, 8, 9)]
    return ouv, tickets, total


def lire_lignes_B(i, lib):
    sh = sheet("ANNEXE-B%s_prix-vente-quantite_%s.xls" % (i, lib))
    lignes, qte, ca, colA = [], Decimal(0), Decimal(0), Decimal(0)
    for r in range(1, sh.nrows):
        v = sh.row_values(r)
        if not isinstance(v[0], float):
            continue
        lignes.append((xdate(v[0]), int(float(v[2])), str(v[3]), str(v[4]), d2(v[9])))
        qte += d2(v[5])
        ca += d2(v[9])
        colA += d2(v[10])
    return lignes, qte, ca, colA


def lire_lignes_C(i, lib):
    sh = sheet("ANNEXE-C%s_detail-tickets_%s.xls" % (i, lib))
    lignes, qte, ca, colA = [], Decimal(0), Decimal(0), Decimal(0)
    for r in range(1, sh.nrows):
        v = sh.row_values(r)
        if v[2] == "TOTAL" or not isinstance(v[11], float):
            continue
        lignes.append((v[0], int(v[2]), str(v[9]), str(v[10]), d2(v[16])))
        qte += d2(v[11])
        ca += d2(v[16])
        colA += d2(v[17])
    return lignes, qte, ca, colA


def lire_F(i, lib):
    sh = sheet("ANNEXE-F%s_reglements_%s.xls" % (i, lib))
    tot = Decimal(0)
    for r in range(1, sh.nrows):
        v = sh.row_values(r)
        if isinstance(v[10], float) and isinstance(v[2], float):
            tot += d2(v[10])
    return tot


# ------------------------------------------------------------------- calculs --
SEUIL = 100000.0  # separe les deux series de compteurs du fichier


def calculer():
    res = {}
    for lib, i in EXOS:
        ouv, tickets, total = lire_H(i, lib)
        sommes = [t["somme"] for t in tickets]
        taxes = [t["taxe"] for t in tickets]
        mx, mxt = max(sommes), max(taxes)
        der, dert = tickets[-1]["somme"], tickets[-1]["taxe"]
        apres = [t for t in tickets if t["somme"] > der]
        # Deux series de compteurs dans le meme fichier.
        s1 = sorted([t for t in tickets if t["somme"] >= SEUIL], key=lambda t: t["somme"])
        s2 = sorted([t for t in tickets if t["somme"] < SEUIL], key=lambda t: t["somme"])
        ouv2 = d2(s2[0]["somme"]) - d2(s2[0]["ttc"]) if s2 else Decimal(0)
        serie1 = dict(n=len(s1), ouv=d2(ouv[0]), fin=d2(s1[-1]["somme"]),
                      ttc=sum((d2(t["ttc"]) for t in s1), Decimal(0)))
        serie2 = dict(n=len(s2), ouv=ouv2, fin=d2(s2[-1]["somme"]) if s2 else Decimal(0),
                      ttc=sum((d2(t["ttc"]) for t in s2), Decimal(0)),
                      nz=[t for t in s2 if t["ttc"] != 0.0])
        lb, qb, cab, colAb = lire_lignes_B(i, lib)
        lc, qc, cac, colAc = lire_lignes_C(i, lib)
        cb, cc = collections.Counter(lb), collections.Counter(lc)
        seulC, seulB = cc - cb, cb - cc
        res[lib] = dict(
            ouv=ouv[0], ouv_taxe=ouv[1], mx=mx, mx_taxe=mxt, der=der, der_taxe=dert,
            ttc=sum((d2(t["ttc"]) for t in tickets), Decimal(0)),
            tva=sum((d2(t["tva"]) for t in tickets), Decimal(0)),
            n_tickets=len(tickets), total_H=total, apres=apres,
            lignes_B=len(lb), lignes_C=len(lc), qte_B=qb, qte_C=qc,
            ca_B=cab, ca_C=cac, colA_B=colAb, colA_C=colAc,
            serie1=serie1, serie2=serie2,
            seulC=seulC, seulB=seulB,
            n_seulC=sum(seulC.values()), n_seulB=sum(seulB.values()),
            m_seulC=sum((k[4] * v for k, v in seulC.items()), Decimal(0)),
            m_seulB=sum((k[4] * v for k, v in seulB.items()), Decimal(0)),
            ca_F=lire_F(i, lib),
        )
    return res


# ------------------------------------------------------------------- ecriture --
TITRE = Font(bold=True, color="FFFFFF", size=11)
FOND = PatternFill("solid", fgColor="1F3864")
GRAS = Font(bold=True)
EUR = '# ##0.00 " €"'


def entete(ws, cols, largeurs):
    ws.append(cols)
    for c in range(1, len(cols) + 1):
        ws.cell(row=1, column=c).font = TITRE
        ws.cell(row=1, column=c).fill = FOND
        ws.cell(row=1, column=c).alignment = Alignment(wrap_text=True, vertical="center")
        ws.column_dimensions[get_column_letter(c)].width = largeurs[c - 1]
    ws.freeze_panes = "A2"


def onglet_compteur(wb, res):
    ws = wb.create_sheet("1 - Compteur perpétuel")
    entete(ws, ["Exercice", "Compteur à l'ouverture (« A NOUVEAUX »)",
                "Valeur maximale atteinte", "Variation (max - ouverture)",
                "Compteur de la dernière ligne du fichier",
                "Variation (dernière ligne - ouverture)",
                "Somme des montants TTC des tickets", "Nombre de tickets"],
           [14, 20, 18, 18, 20, 20, 20, 12])
    for lib, _ in EXOS:
        r = res[lib]
        ws.append([lib, r["ouv"], r["mx"], round(r["mx"] - r["ouv"], 2), r["der"],
                   round(r["der"] - r["ouv"], 2), float(r["ttc"]), r["n_tickets"]])
    ws.append([])
    ws.append(["Compteur de taxe (tot_tax_sum), même fichier"])
    ws.cell(row=ws.max_row, column=1).font = GRAS
    ws.append(["Exercice", "Ouverture", "Maximum", "Variation", "Dernière ligne",
               "Variation", "Somme de la TVA des tickets", ""])
    for c in range(1, 8):
        ws.cell(row=ws.max_row, column=c).font = GRAS
    for lib, _ in EXOS:
        r = res[lib]
        ws.append([lib, r["ouv_taxe"], r["mx_taxe"], round(r["mx_taxe"] - r["ouv_taxe"], 2),
                   r["der_taxe"], round(r["der_taxe"] - r["ouv_taxe"], 2), float(r["tva"]), ""])
    ws.append([])
    ws.append(["Raccord d'un exercice au suivant : la valeur maximale de l'exercice N "
               "est-elle la valeur d'ouverture de l'exercice N+1 ?"])
    ws.cell(row=ws.max_row, column=1).font = GRAS
    ws.append(["Passage", "Compteur : maximum de N", "Compteur : ouverture de N+1", "Écart",
               "Taxe : maximum de N", "Taxe : ouverture de N+1", "Écart", ""])
    for c in range(1, 8):
        ws.cell(row=ws.max_row, column=c).font = GRAS
    for (a, _), (b, _) in zip(EXOS, EXOS[1:]):
        ra, rb = res[a], res[b]
        ws.append(["%s vers %s" % (a, b), ra["mx"], rb["ouv"], round(rb["ouv"] - ra["mx"], 2),
                   ra["mx_taxe"], rb["ouv_taxe"], round(rb["ouv_taxe"] - ra["mx_taxe"], 2), ""])
    for row in ws.iter_rows(min_row=2):
        for c in row:
            if isinstance(c.value, float):
                c.number_format = EUR


def onglet_series(wb, res):
    ws = wb.create_sheet("2 - Les deux séries")
    entete(ws, ["Série de compteurs", "Exercice", "Nombre de tickets",
                "Valeur d'ouverture", "Valeur de clôture",
                "Écart avec l'ouverture de l'exercice suivant",
                "Somme des montants TTC des tickets"],
           [20, 14, 16, 18, 18, 20, 22])
    for nom, cle in (("Première série", "serie1"), ("Seconde série", "serie2")):
        for k, (lib, _) in enumerate(EXOS):
            s = res[lib][cle]
            if k + 1 < len(EXOS):
                suiv = res[EXOS[k + 1][0]][cle]["ouv"]
                ecart = float(suiv - s["fin"])
            else:
                ecart = "fin de période"
            ws.append([nom, lib, s["n"], float(s["ouv"]), float(s["fin"]), ecart, float(s["ttc"])])
    ws.append([])
    ws.append(["Tickets de la seconde série dont le montant n'est pas nul"])
    ws.cell(row=ws.max_row, column=1).font = GRAS
    ws.append(["Exercice", "Date", "Heure", "N° de ticket", "N° de ticket Z", "Montant TTC", ""])
    for c in range(1, 7):
        ws.cell(row=ws.max_row, column=c).font = GRAS
    for lib, _ in EXOS:
        for t in res[lib]["serie2"]["nz"]:
            ws.append([lib, t["date"], t["heure"], int(t["no"]), int(t["z"]), t["ttc"], ""])
    for row in ws.iter_rows(min_row=2):
        for c in row:
            if isinstance(c.value, float):
                c.number_format = EUR


def onglet_quatre(wb, res):
    ws = wb.create_sheet("3 - Les quatre montants")
    entete(ws, ["Exercice", "Série d'annexes", "Montant opposé par le service",
                "Ce que ce montant est, dans les fichiers", "Montant recalculé",
                "Écart"],
           [12, 16, 20, 58, 18, 12])
    ORIG = {
        "B": "Somme de la colonne 10 « Total TTC » de l'annexe B, et somme des montants TTC "
             "des tickets de la première série de compteurs de l'annexe H",
        "C": "Somme de la colonne 17 « Tot_rem Ttc » de l'annexe C, et somme des montants "
             "TTC de tous les tickets de l'annexe H, les deux séries réunies",
        "F": "Somme des règlements encaissés, annexe F, ligne « TOTAL GENERAL »",
        "G": "Compteur perpétuel lu à la dernière ligne du fichier, moins son ouverture : "
             "porté dans la ligne TOTAL des annexes G et H sous la mention "
             "« Différence sommeEntre01-04 et 31-03 »",
    }
    for lib, _ in EXOS:
        r = res[lib]
        calc = {"B": round(r["mx"] - r["ouv"], 2), "C": float(r["ttc"]),
                "F": float(r["ca_F"]), "G": round(r["der"] - r["ouv"], 2)}
        for k in ("B", "C", "F", "G"):
            ws.append([lib, "Annexes %s-1 à %s-3" % (k, k), SERVICE[lib][k], ORIG[k],
                       calc[k], round(calc[k] - SERVICE[lib][k], 2)])
        mx, mn = max(calc.values()), min(calc.values())
        ws.append([lib, "Amplitude des quatre", "", "Écart entre le plus haut et le plus bas",
                   round(mx - mn, 2), "%.3f %%" % ((mx - mn) / mn * 100)])
        for c in range(1, 7):
            ws.cell(row=ws.max_row, column=c).font = GRAS
    for row in ws.iter_rows(min_row=2):
        for c in row:
            if isinstance(c.value, float):
                c.number_format = EUR


def onglet_apres(wb, res):
    ws = wb.create_sheet("4 - Écart des deux lectures")
    entete(ws, ["Exercice", "Écart entre les deux lectures du compteur",
                "Tickets clôturés après la dernière ligne du fichier",
                "Total TTC de ces tickets", "Date", "Heure", "N° de ticket",
                "N° de ticket Z", "Montant TTC"],
           [12, 20, 20, 16, 12, 10, 12, 12, 14])
    for lib, _ in EXOS:
        r = res[lib]
        ecart = round((r["mx"] - r["ouv"]) - (r["der"] - r["ouv"]), 2)
        somme = round(sum(t["ttc"] for t in r["apres"]), 2)
        prem = True
        for t in r["apres"]:
            ws.append([lib if prem else "", ecart if prem else "",
                       len(r["apres"]) if prem else "", somme if prem else "",
                       t["date"], t["heure"], int(t["no"]), int(t["z"]), t["ttc"]])
            prem = False
    for row in ws.iter_rows(min_row=2):
        for c in row:
            if isinstance(c.value, float):
                c.number_format = EUR


def onglet_bc(wb, res):
    ws = wb.create_sheet("5 - Annexe B dans annexe C")
    entete(ws, ["Exercice", "Lignes de l'annexe B", "Lignes de l'annexe C",
                "Lignes de B absentes de C", "Montant correspondant",
                "Lignes de C absentes de B", "Montant correspondant",
                "CA annexe C - CA annexe B"],
           [12, 16, 16, 18, 16, 18, 16, 18])
    ws.append([])
    ws.delete_rows(2)
    for lib, _ in EXOS:
        r = res[lib]
        ws.append([lib, r["lignes_B"], r["lignes_C"], r["n_seulB"], float(r["m_seulB"]),
                   r["n_seulC"], float(r["m_seulC"]), float(r["ca_C"] - r["ca_B"])])
    ws.append([])
    ws.append(["Clé de rapprochement : date du ticket, numéro de ticket, référence produit, "
               "libellé de l'article, montant TTC de la ligne."])
    for row in ws.iter_rows(min_row=2):
        for c in row:
            if isinstance(c.value, float):
                c.number_format = EUR


def onglet_detail(wb, res):
    ws = wb.create_sheet("6 - Lignes de C absentes de B")
    entete(ws, ["Exercice", "Date du ticket", "N° de ticket", "Référence",
                "Libellé de l'article", "Montant TTC"],
           [12, 14, 12, 12, 40, 14])
    for lib, _ in EXOS:
        for (date, no, ref, lib_art, montant), n in sorted(res[lib]["seulC"].items()):
            for _ in range(n):
                ws.append([lib, date, no, ref, lib_art, float(montant)])
    for row in ws.iter_rows(min_row=2):
        for c in row:
            if isinstance(c.value, float):
                c.number_format = EUR


def onglet_controle(wb, res):
    ws = wb.create_sheet("7 - Colonne de contrôle")
    entete(ws, ["Exercice", "Annexe", "Chiffre d'affaires de l'annexe",
                "Colonne créée par le service : prix unitaire x quantité",
                "Écart, en valeur absolue", "Écart en % du chiffre d'affaires"],
           [12, 26, 20, 26, 18, 18])
    for lib, _ in EXOS:
        r = res[lib]
        for nom, ca, cola in (
            ("Annexe B (extraction du 10/02/2026)", r["ca_B"], r["colA_B"]),
            ("Annexe C (remise du 13/03/2026)", r["ca_C"], r["colA_C"]),
        ):
            ecart = abs(cola - ca)
            ws.append([lib, nom, float(ca), float(cola), float(ecart),
                       "%.4f %%" % (float(ecart) / float(ca) * 100)])
    ws.append([])
    ws.append(["Somme des quantités, annexe B puis annexe C, par exercice"])
    ws.cell(row=ws.max_row, column=1).font = GRAS
    ws.append(["Exercice", "Quantités annexe B", "Quantités annexe C", "Écart", "", ""])
    for c in range(1, 5):
        ws.cell(row=ws.max_row, column=c).font = GRAS
    for lib, _ in EXOS:
        r = res[lib]
        ws.append([lib, float(r["qte_B"]), float(r["qte_C"]),
                   float(r["qte_B"] - r["qte_C"]), "", ""])
    for row in ws.iter_rows(min_row=2):
        for c in row:
            if isinstance(c.value, float):
                c.number_format = EUR


def onglet_methode(wb):
    ws = wb.create_sheet("0 - Méthode", 0)
    ws.column_dimensions["A"].width = 118
    lignes = [
        ("Objet", True),
        ("Origine, fichier par fichier, des quatre montants de chiffre d'affaires que le "
         "service oppose dans sa réponse du 04/09/2026 (p. 40 et p. 45) et dans sa "
         "proposition du 18/05/2026 (p. 28), et comparaison ligne à ligne des deux "
         "extractions de caisse remises au service.", False),
        ("", False),
        ("Sources, toutes lues en lecture seule", True),
        ("public/documents/caisse-enregistreuse/ANNEXE-B1 à B3 (extraction transmise par "
         "courriel, annexes construites par le service)", False),
        ("public/documents/caisse-enregistreuse/ANNEXE-C1 à C3 (fichier « ticket ligne », "
         "remise du 13/03/2026)", False),
        ("public/documents/caisse-enregistreuse/ANNEXE-F1 à F3 (fichier « reglement »)", False),
        ("public/documents/caisse-enregistreuse/ANNEXE-G1 à G3 (fichier « tva »)", False),
        ("public/documents/caisse-enregistreuse/ANNEXE-H1 à H3 (fichier « ticket »)", False),
        ("", False),
        ("Ce que le script calcule", True),
        ("1. Le compteur cumulatif des annexes H et G (colonnes tot_sum et tot_tax_sum), sa "
         "valeur d'ouverture intitulée « A NOUVEAUX » dans le fichier, sa valeur maximale, sa "
         "valeur à la dernière ligne, et le raccord d'un exercice au suivant.", False),
        ("2. L'origine de chacun des quatre montants opposés par le service.", False),
        ("3. Les tickets dont la clôture est postérieure à la dernière ligne du fichier, qui "
         "expliquent l'écart entre les deux lectures du compteur.", False),
        ("4. Le rapprochement ligne à ligne des annexes B et C, sur la clé date du ticket, "
         "numéro de ticket, référence produit, libellé et montant TTC.", False),
        ("5. Le détail des lignes présentes dans l'annexe C et absentes de l'annexe B.", False),
        ("6. La colonne de contrôle créée par le service (prix unitaire multiplié par la "
         "quantité), comparée au chiffre d'affaires de l'annexe qui la porte.", False),
        ("", False),
        ("Aucune saisie manuelle. Script : scripts/reponse1-compteur-perpetuel.py", True),
    ]
    for txt, gras in lignes:
        ws.append([txt])
        ws.cell(row=ws.max_row, column=1).alignment = Alignment(wrap_text=True, vertical="top")
        if gras:
            ws.cell(row=ws.max_row, column=1).font = GRAS


def main():
    res = calculer()
    wb = Workbook()
    wb.remove(wb.active)
    onglet_compteur(wb, res)
    onglet_series(wb, res)
    onglet_quatre(wb, res)
    onglet_apres(wb, res)
    onglet_bc(wb, res)
    onglet_detail(wb, res)
    onglet_controle(wb, res)
    onglet_methode(wb)
    os.makedirs(OUT_DIR, exist_ok=True)
    wb.save(OUT)
    print("Ecrit :", OUT)
    for lib, _ in EXOS:
        r = res[lib]
        print("  %s : compteur %.2f -> %.2f (max) / %.2f (derniere ligne) ; "
              "B=%.2f C=%.2f F=%.2f G=%.2f ; lignes B absentes de C : %d"
              % (lib, r["ouv"], r["mx"], r["der"], r["ca_B"], r["ca_C"], r["ca_F"],
                 r["der"] - r["ouv"], r["n_seulB"]))


if __name__ == "__main__":
    main()
