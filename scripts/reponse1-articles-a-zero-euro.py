#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REPONSE 1 - Partie C : articles a prix 0 EUR (reponse DDFiP 39 du 04/09/2026,
p. 21 a 27).

Le service maintient le grief en opposant aux 272 lignes a 0 EUR trois
"extraits" de fichiers de caisse (p. 23 a 26) et des quantites non entieres.

Ce script, entierement reproductible et en lecture seule, refait le comptage
depuis les annexes de caisse certifiees et produit la piece jointe :

  1. comptage total des lignes de vente et des lignes a prix unitaire nul,
     par exercice, recoupe avec la colonne "G Prix a 0 EUR" de l'annexe ;
  2. somme des quantites portees par ces lignes (le "nombre d'articles reels"
     dont se prevaut le service) ;
  3. pour CHAQUE ligne a 0 EUR : date, heure, no de ticket, no de Z, libelle,
     quantite ET TOTAL TTC DU TICKET auquel elle appartient (colonne decisive :
     elle etablit que le ticket a bien ete encaisse) ;
  4. les lignes a quantite non entiere, regroupees par ticket partage, avec la
     somme des fractions (qui reconstitue un nombre entier) ;
  5. le detail complet de trois tickets de demonstration.

Sources (lecture seule) :
  public/documents/caisse-enregistreuse/ANNEXE-C{1,2,3}_detail-tickets_*.xls

Sortie :
  public/documents/pieces-reponse-1/R1-articles-a-zero-euro.xlsx

Lancer avec : python3 scripts/reponse1-articles-a-zero-euro.py
"""

import os
from collections import defaultdict

import xlrd
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAISSE = os.path.join(ROOT, "public", "documents", "caisse-enregistreuse")
PIECES = os.path.join(ROOT, "public", "documents", "pieces-reponse-1")
XLSX_OUT = os.path.join(PIECES, "R1-articles-a-zero-euro.xlsx")

EXERCICES = [("1", "2022-2023", "C-1"),
             ("2", "2023-2024", "C-2"),
             ("3", "2024-2025", "C-3")]

# Colonnes de l'annexe C (detail des tickets), cf. ligne d'en-tete :
COL_DATE, COL_HEURE, COL_NOTICKET, COL_DATZ, COL_NOZ = 0, 1, 2, 3, 4
COL_TOTTTC = 5
COL_ID, COL_REF, COL_LIB, COL_QTE = 8, 9, 10, 11
COL_PU = 13
COL_FLAG_ZERO = 23   # colonne "G / Prix a 0 €" de l'annexe elle-meme

# Tickets de demonstration : (exercice, date, no de ticket, commentaire)
DEMOS = [
    ("1", "2022-07-03", 15.0,
     "Note encaissee 303,00 EUR : 22 lignes payantes, 5 expressos offerts"),
    ("1", "2022-06-04", 11.0,
     "Note encaissee 232,30 EUR : 3 menus payes, apero et cafes offerts"),
    ("2", "2023-09-09", 39.0,
     "Addition partagee 25 % / 75 % (part 1 sur 2), Vittel litre offert"),
    ("2", "2023-09-09", 40.0,
     "Addition partagee 25 % / 75 % (part 2 sur 2), Vittel litre offert"),
]


# --------------------------------------------------------------------------
# Formatage francais
# --------------------------------------------------------------------------
def fr_int(n):
    return "{:,}".format(int(round(n))).replace(",", " ")


def fr_qte(q):
    if float(q) == int(q):
        return str(int(q))
    return ("%.2f" % float(q)).replace(".", ",")


def fr_eur(n):
    s = "{:,.2f}".format(float(n)).replace(",", " ").replace(".", ",")
    return s + " €"


def fr_pct(n, dec=2):
    return (("{:." + str(dec) + "f}").format(n).replace(".", ",")) + " %"


def f(cell):
    try:
        return float(cell)
    except (TypeError, ValueError):
        return 0.0


# --------------------------------------------------------------------------
# 1) Lecture des annexes
# --------------------------------------------------------------------------
def lire():
    par_exo = {}
    lignes_zero = []          # toutes les lignes a 0 EUR, 3 exercices
    tickets_demo = defaultdict(list)

    for num, exo, annexe in EXERCICES:
        path = os.path.join(CAISSE,
                            "ANNEXE-C%s_detail-tickets_%s.xls" % (num, exo))
        sh = xlrd.open_workbook(path).sheet_by_index(0)

        total = zero = zero_paye = zero_nul = flag = 0
        articles = 0.0
        encaisse_zero = 0.0

        for r in range(1, sh.nrows):
            ref = str(sh.cell_value(r, COL_REF)).strip()
            lib = str(sh.cell_value(r, COL_LIB)).strip()
            if ref == "" and lib == "":
                continue                      # ligne technique vide
            total += 1

            if str(sh.cell_value(r, COL_FLAG_ZERO)).strip() != "":
                flag += 1

            pu = f(sh.cell_value(r, COL_PU))
            date = str(sh.cell_value(r, COL_DATE)).strip()
            noticket = f(sh.cell_value(r, COL_NOTICKET))

            for dnum, ddate, dnot, _ in DEMOS:
                if dnum == num and ddate == date and dnot == noticket:
                    tickets_demo[(num, ddate, dnot)].append({
                        "heure": str(sh.cell_value(r, COL_HEURE)).strip(),
                        "noz": f(sh.cell_value(r, COL_NOZ)),
                        "ttc": f(sh.cell_value(r, COL_TOTTTC)),
                        "lib": lib,
                        "qte": f(sh.cell_value(r, COL_QTE)),
                        "pu": pu,
                    })

            if pu != 0.0:
                continue

            zero += 1
            qte = f(sh.cell_value(r, COL_QTE))
            ttc = f(sh.cell_value(r, COL_TOTTTC))
            articles += qte
            encaisse_zero += pu * qte
            if ttc > 0:
                zero_paye += 1
            else:
                zero_nul += 1

            lignes_zero.append({
                "exo": exo,
                "annexe": annexe,
                "date": date,
                "heure": str(sh.cell_value(r, COL_HEURE)).strip(),
                "noticket": noticket,
                "noz": f(sh.cell_value(r, COL_NOZ)),
                "ref": ref,
                "lib": lib,
                "qte": qte,
                "pu": pu,
                "ttc": ttc,
            })

        par_exo[exo] = {
            "annexe": annexe, "total": total, "zero": zero, "flag": flag,
            "articles": articles, "zero_paye": zero_paye,
            "zero_nul": zero_nul, "encaisse_zero": encaisse_zero,
        }

    return par_exo, lignes_zero, tickets_demo


# --------------------------------------------------------------------------
# 2) Quantites non entieres : regroupement par addition partagee
# --------------------------------------------------------------------------
def fractions(lignes_zero):
    """Regroupe les lignes a 0 EUR de quantite non entiere par (date, Z, libelle)
    et somme les fractions : elles doivent reconstituer un nombre entier."""
    frac = [l for l in lignes_zero if l["qte"] != int(l["qte"])]
    groupes = defaultdict(list)
    for l in frac:
        groupes[(l["exo"], l["date"], l["noz"], l["lib"])].append(l)
    out = []
    for cle in sorted(groupes, key=lambda k: (k[1], k[3])):
        parts = sorted(groupes[cle], key=lambda l: l["noticket"])
        out.append({
            "exo": cle[0], "date": cle[1], "noz": cle[2], "lib": cle[3],
            "parts": parts,
            "somme": sum(p["qte"] for p in parts),
        })
    return out


# --------------------------------------------------------------------------
# 3) Ecriture XLSX
# --------------------------------------------------------------------------
H_FILL = PatternFill("solid", fgColor="0F766E")
H_FONT = Font(bold=True, color="FFFFFF")
BOLD = Font(bold=True)
RIGHT = Alignment(horizontal="right")
WRAP = Alignment(wrap_text=True, vertical="top")


def entete(ws, ncol, row=1):
    for c in range(1, ncol + 1):
        cell = ws.cell(row=row, column=c)
        cell.font = H_FONT
        cell.fill = H_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center",
                                   wrap_text=True)
    ws.freeze_panes = "A%d" % (row + 1)


def largeurs(ws, widths):
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w


def ecrire(par_exo, lignes_zero, tickets_demo, tot, frac):
    os.makedirs(PIECES, exist_ok=True)
    wb = openpyxl.Workbook()

    # --- Onglet 1 : Synthese -------------------------------------------------
    ws = wb.active
    ws.title = "Synthese"
    ws.append(["SARL LA DEMI LUNE - Articles enregistres a prix 0 €"])
    ws.cell(row=1, column=1).font = Font(bold=True, size=13)
    ws.append(["Reponse a la partie C de la lettre du 04/09/2026 (p. 21 a 27). "
               "Source : annexes de caisse C-1, C-2 et C-3, lues ligne a ligne."])
    ws.append([])
    ws.append(["Indicateur", "Valeur"])
    entete(ws, 2, row=4)
    for k, v in [
        ("Lignes de vente analysees (3 exercices)", fr_int(tot["total"])),
        ("Lignes a prix unitaire 0 €", fr_int(tot["zero"])),
        ("Part des lignes de vente", fr_pct(tot["pct"], 2)),
        ("Controle : colonne « Prix a 0 € » de l'annexe",
         fr_int(tot["flag"])),
        ("Montant encaisse par ces lignes (prix unitaire x quantite)",
         fr_eur(tot["encaisse_zero"])),
        ("Quantite totale portee par ces lignes (« articles reels »)",
         fr_qte(tot["articles"])),
        ("Lignes situees dans un ticket par ailleurs encaisse",
         fr_int(tot["zero_paye"])),
        ("Lignes situees sur un ticket integralement a 0 €",
         fr_int(tot["zero_nul"])),
        ("Lignes a quantite non entiere (additions partagees)",
         fr_int(len([l for l in lignes_zero if l["qte"] != int(l["qte"])]))),
    ]:
        ws.append([k, v])
        ws.cell(row=ws.max_row, column=2).alignment = RIGHT
    largeurs(ws, [64, 22])

    # --- Onglet 2 : Par exercice --------------------------------------------
    ws = wb.create_sheet("Par exercice")
    ws.append(["Exercice", "Annexe", "Lignes de vente", "Lignes a 0 €",
               "Part", "Quantite (articles)",
               "Dont ticket encaisse", "Dont ticket a 0 €",
               "Montant encaisse"])
    entete(ws, 9)
    for _, exo, _ in EXERCICES:
        e = par_exo[exo]
        ws.append([exo, e["annexe"], fr_int(e["total"]), fr_int(e["zero"]),
                   fr_pct(100.0 * e["zero"] / e["total"], 3),
                   fr_qte(e["articles"]), fr_int(e["zero_paye"]),
                   fr_int(e["zero_nul"]), fr_eur(e["encaisse_zero"])])
        for c in range(3, 10):
            ws.cell(row=ws.max_row, column=c).alignment = RIGHT
    ws.append(["TOTAL", "C-1 a C-3", fr_int(tot["total"]), fr_int(tot["zero"]),
               fr_pct(tot["pct"], 3), fr_qte(tot["articles"]),
               fr_int(tot["zero_paye"]), fr_int(tot["zero_nul"]),
               fr_eur(tot["encaisse_zero"])])
    for c in range(1, 10):
        ws.cell(row=ws.max_row, column=c).font = BOLD
        if c >= 3:
            ws.cell(row=ws.max_row, column=c).alignment = RIGHT
    largeurs(ws, [13, 11, 15, 13, 10, 17, 18, 16, 16])

    # --- Onglet 3 : les 272 lignes ------------------------------------------
    ws = wb.create_sheet("Lignes a 0 EUR")
    ws.append(["Exercice", "Annexe", "Date", "Heure", "N° ticket",
               "N° Z", "Ref. produit", "Libelle", "Quantite",
               "Prix unitaire TTC", "TOTAL TTC DU TICKET",
               "Ticket encaisse ?"])
    entete(ws, 12)
    for l in sorted(lignes_zero, key=lambda x: (x["date"], x["heure"],
                                                x["noticket"], x["lib"])):
        ws.append([l["exo"], l["annexe"], l["date"], l["heure"],
                   int(l["noticket"]), int(l["noz"]), l["ref"], l["lib"],
                   fr_qte(l["qte"]), fr_eur(l["pu"]), fr_eur(l["ttc"]),
                   "OUI" if l["ttc"] > 0 else "non (note offerte)"])
        for c in (5, 6, 9, 10, 11):
            ws.cell(row=ws.max_row, column=c).alignment = RIGHT
        ws.cell(row=ws.max_row, column=11).font = BOLD
    largeurs(ws, [12, 9, 12, 9, 11, 9, 13, 30, 10, 16, 20, 19])

    # --- Onglet 4 : quantites non entieres ----------------------------------
    ws = wb.create_sheet("Quantites non entieres")
    ws.append(["Les quantites fractionnaires proviennent du partage d'addition : "
               "une meme table reglee en plusieurs notes. La somme des fractions "
               "d'une meme table reconstitue un nombre entier."])
    ws.cell(row=1, column=1).font = BOLD
    ws.append([])
    ws.append(["Date", "N° Z", "Libelle offert", "N° ticket", "Heure",
               "Quantite de la part", "Total TTC du ticket",
               "SOMME DES PARTS", "Entier ?"])
    entete(ws, 9, row=3)
    for g in frac:
        first = True
        for p in g["parts"]:
            ws.append([g["date"] if first else "",
                       int(g["noz"]) if first else "",
                       g["lib"] if first else "",
                       int(p["noticket"]), p["heure"], fr_qte(p["qte"]),
                       fr_eur(p["ttc"]),
                       fr_qte(g["somme"]) if first else "",
                       ("OUI" if g["somme"] == int(g["somme"]) else "non")
                       if first else ""])
            for c in (4, 6, 7, 8):
                ws.cell(row=ws.max_row, column=c).alignment = RIGHT
            if first:
                ws.cell(row=ws.max_row, column=8).font = BOLD
            first = False
    largeurs(ws, [12, 9, 26, 11, 9, 19, 19, 17, 10])

    # --- Onglet 5 : tickets de demonstration --------------------------------
    ws = wb.create_sheet("Tickets de demonstration")
    row = 1
    for num, date, not_, comment in DEMOS:
        lignes = tickets_demo.get((num, date, not_), [])
        if not lignes:
            continue
        ws.cell(row=row, column=1,
                value="Ticket du %s a %s, n° %d (Z n° %d) : %s"
                      % (date, lignes[0]["heure"], int(not_),
                         int(lignes[0]["noz"]), comment)).font = Font(
                             bold=True, size=11)
        row += 1
        ws.cell(row=row, column=1,
                value="Total TTC encaisse : %s" % fr_eur(lignes[0]["ttc"]))
        row += 1
        for i, lab in enumerate(["Libelle", "Quantite", "Prix unitaire TTC",
                                 "Ligne offerte ?"], start=1):
            c = ws.cell(row=row, column=i, value=lab)
            c.font = H_FONT
            c.fill = H_FILL
            c.alignment = Alignment(horizontal="center")
        row += 1
        for l in lignes:
            ws.cell(row=row, column=1, value=l["lib"])
            ws.cell(row=row, column=2, value=fr_qte(l["qte"])).alignment = RIGHT
            ws.cell(row=row, column=3, value=fr_eur(l["pu"])).alignment = RIGHT
            ws.cell(row=row, column=4,
                    value="OFFERTE" if l["pu"] == 0 else "").alignment = RIGHT
            row += 1
        row += 2
    largeurs(ws, [34, 12, 20, 18])

    wb.save(XLSX_OUT)


# --------------------------------------------------------------------------
def main():
    par_exo, lignes_zero, tickets_demo = lire()
    tot = {k: sum(e[k] for e in par_exo.values())
           for k in ("total", "zero", "flag", "articles", "zero_paye",
                     "zero_nul", "encaisse_zero")}
    tot["pct"] = 100.0 * tot["zero"] / tot["total"]
    frac = fractions(lignes_zero)

    assert tot["zero"] == tot["flag"], "comptage != colonne G de l'annexe"
    assert tot["encaisse_zero"] == 0.0, "les lignes a 0 EUR encaissent 0"

    ecrire(par_exo, lignes_zero, tickets_demo, tot, frac)

    print("Lignes de vente      :", fr_int(tot["total"]))
    print("Lignes a 0 EUR       :", fr_int(tot["zero"]),
          "(", fr_pct(tot["pct"], 2), ") - controle colonne G :",
          fr_int(tot["flag"]))
    print("Quantite (articles)  :", fr_qte(tot["articles"]))
    print("Dont ticket encaisse :", tot["zero_paye"],
          "| ticket a 0 EUR :", tot["zero_nul"])
    print("Montant encaisse     :", fr_eur(tot["encaisse_zero"]))
    for _, exo, ann in EXERCICES:
        e = par_exo[exo]
        print("  %s (%s) : %d lignes a 0 EUR, %s articles"
              % (exo, ann, e["zero"], fr_qte(e["articles"])))
    print("Groupes de quantites non entieres :", len(frac))
    for g in frac:
        print("   %s Z%d %-24s parts=%s somme=%s"
              % (g["date"], int(g["noz"]), g["lib"],
                 [fr_qte(p["qte"]) for p in g["parts"]], fr_qte(g["somme"])))
    print("XLSX ->", XLSX_OUT)


if __name__ == "__main__":
    main()
