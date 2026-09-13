#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reponse1-menu-demi-lune-conversions.py

Piece de la reponse n. 1 (partie J : "instabilite des prix du Menu Demi Lune").

Objet : demontrer, sur les fichiers de caisse remis au service, que chaque
"prix personnalise" du Menu Demi Lune correspond a une CONVERSION AU FORFAIT :
la somme des lignes supprimees (evenements DEL, annexe E) est EGALE AU CENTIME
au total de la note encaissee (annexe C), qui contient un Menu Demi Lune a un
prix hors catalogue. L'ecart est nul : aucune recette n'est perdue.

Sources (lecture seule) :
  public/documents/caisse-enregistreuse/ANNEXE-C{1,2,3}_detail-tickets_*.xls
  public/documents/caisse-enregistreuse/ANNEXE-E{1,2,3}_tpvevenement_*.xls
  src/data/renduFinalCalculs.json (bloc "menus_par_periode", annexe B)

Methode de rapprochement (identique a scripts/rendu-final-prix-menu-demi-lune.py) :
  - rafale DEL = evenements de type DEL d'une meme journee partageant la meme
    minute (champ heureEven), au moins 2 lignes ;
  - une note est retenue si elle contient un "Menu Demi Lune" a un prix
    different du prix catalogue (45,00 EUR), si toutes ses lignes sont des
    lignes de menu/formule, si la rafale se situe a 10 minutes ou moins de
    l'heure de la note, et si somme(rafale) = total de la note (< 0,05 EUR).

Sortie : public/documents/pieces-reponse-1/R1-menu-demi-lune-conversions.xlsx
Usage  : python3 scripts/reponse1-menu-demi-lune-conversions.py
"""

import collections
import json
import os

import openpyxl
import xlrd
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANNEXES = os.path.join(ROOT, "public", "documents", "caisse-enregistreuse")
CALCULS = os.path.join(ROOT, "src", "data", "renduFinalCalculs.json")
OUT = os.path.join(ROOT, "public", "documents", "pieces-reponse-1",
                   "R1-menu-demi-lune-conversions.xlsx")

EXOS = ["2022-2023", "2023-2024", "2024-2025"]
C_FILES = {e: os.path.join(ANNEXES, f"ANNEXE-C{i}_detail-tickets_{e}.xls") for i, e in enumerate(EXOS, 1)}
E_FILES = {e: os.path.join(ANNEXES, f"ANNEXE-E{i}_tpvevenement_{e}.xls") for i, e in enumerate(EXOS, 1)}
PRIX_CATALOGUE = 45.0
JOUR_SERVICE = "2022-09-09"   # journee reproduite par le service p. 55


def eur(x):
    return f"{x:,.2f}".replace(",", " ").replace(".", ",") + " €"


def tm(h):
    try:
        return int(h[:2]) * 60 + int(h[3:5])
    except Exception:
        return -1


def is_menu(lib):
    return lib.lower().startswith(("menu", "formule"))


def is_demi_lune(lib):
    l = lib.lower()
    return "demi lune" in l or "demi-lune" in l


def charger(ex):
    """Retourne (notes_par_jour, dels_par_jour) pour un exercice."""
    shc = xlrd.open_workbook(C_FILES[ex]).sheet_by_index(0)
    notes = collections.defaultdict(lambda: collections.defaultdict(
        lambda: {"h": "", "tot": 0.0, "lines": []}))
    for r in range(1, shc.nrows):
        d = str(shc.cell_value(r, 0))[:10]
        if not d.startswith("20"):
            continue
        no = str(shc.cell_value(r, 2)).replace(".0", "")
        n = notes[d][no]
        n["h"] = str(shc.cell_value(r, 1))[:5]
        try:
            n["tot"] = round(float(shc.cell_value(r, 5)), 2)
        except ValueError:
            pass
        try:
            q = float(shc.cell_value(r, 11))
            pu = round(float(shc.cell_value(r, 13) or 0), 2)
        except ValueError:
            q, pu = 0.0, 0.0
        n["lines"].append((str(shc.cell_value(r, 10)).strip(), q, pu,
                           round(float(shc.cell_value(r, 16) or 0), 2)))

    she = xlrd.open_workbook(E_FILES[ex]).sheet_by_index(0)
    dels = collections.defaultdict(list)
    for r in range(1, she.nrows):
        d = str(she.cell_value(r, 1))[:10]
        if d.startswith("20") and str(she.cell_value(r, 3)).strip() == "DEL":
            dels[d].append((str(she.cell_value(r, 2))[:5],
                            round(float(she.cell_value(r, 8) or 0), 2),
                            str(she.cell_value(r, 9)).replace(".0", "")))
    return notes, dels


def composition(n):
    parts = []
    for lib, q, pu, _ in n["lines"]:
        qs = f"{q:g}".replace(".", ",")
        parts.append(f"{qs} x {lib} a {eur(pu)}")
    return " + ".join(parts)


# ---------------------------------------------------------------------------
# 1. Balayage des trois exercices
# ---------------------------------------------------------------------------
conversions = []          # rafales DEL = total d'une note "Menu Demi Lune" hors catalogue
notes_hors_catalogue = 0
extrait_service = {"dels": [], "notes": []}

for ex in EXOS:
    notes, dels = charger(ex)
    for d in sorted(notes):
        rafales = collections.defaultdict(list)
        for h, m, ident in dels.get(d, []):
            rafales[h].append((m, ident))

        if d == JOUR_SERVICE:
            for h, m, ident in sorted(dels.get(d, []), key=lambda t: int(t[2])):
                extrait_service["dels"].append((h, m, ident))
            for no, n in sorted(notes[d].items(), key=lambda kv: kv[1]["h"]):
                for lib, q, pu, tot in n["lines"]:
                    if is_demi_lune(lib):
                        extrait_service["notes"].append((n["h"], no, lib, q, pu, tot, n["tot"]))

        for no, n in notes[d].items():
            dl = [x for x in n["lines"] if is_demi_lune(x[0])]
            if not dl or abs(dl[0][2] - PRIX_CATALOGUE) < 0.01:
                continue
            notes_hors_catalogue += 1
            if not all(is_menu(l) for l, q, pu, t in n["lines"]):
                continue
            for h, ms in sorted(rafales.items()):
                if len(ms) < 2:
                    continue
                s = round(sum(m for m, _ in ms), 2)
                if abs(s - n["tot"]) < 0.05 and abs(tm(h) - tm(n["h"])) <= 10:
                    conversions.append({
                        "exercice": ex, "date": d, "heure_rafale": h,
                        "nb_suppr": len(ms), "somme_suppr": s,
                        "detail_suppr": " + ".join(eur(m) for m, _ in sorted(ms)),
                        "note": no, "heure_note": n["h"], "total_note": round(n["tot"], 2),
                        "couverts": round(dl[0][1], 2), "prix_menu": round(dl[0][2], 2),
                        # unites = somme des quantites de TOUTES les lignes
                        # "Menu Demi Lune" de la note ; la colonne "couverts"
                        # ne retient que la quantite de la premiere d'entre elles.
                        "unites": round(sum(x[1] for x in dl), 2),
                        "composition": composition(n),
                        "ecart": round(s - n["tot"], 2),
                    })
                    break

conversions.sort(key=lambda c: (c["date"], c["heure_rafale"]))
assert conversions, "aucune conversion au forfait detectee"
for c in conversions:
    assert abs(c["ecart"]) < 0.05, c
NB_ECART_NUL = sum(1 for c in conversions if abs(c["ecart"]) < 0.005)

TOTAL_CONV = len(conversions)
TOTAL_EUR = round(sum(c["total_note"] for c in conversions), 2)
TOTAL_SUPPR_EUR = round(sum(c["somme_suppr"] for c in conversions), 2)
TOTAL_COUVERTS = round(sum(c["couverts"] for c in conversions), 2)
TOTAL_UNITES = round(sum(c["unites"] for c in conversions), 2)
TOTAL_LIGNES = sum(c["nb_suppr"] for c in conversions)
TOTAL_ECART = round(sum(c["ecart"] for c in conversions), 2)
ECART_MAX = max(abs(c["ecart"]) for c in conversions)
# Notes ou le forfait a ete saisi en plusieurs lignes "Menu Demi Lune" :
# c'est de la seule que vient l'ecart entre unites de menu et couverts.
NOTES_MULTILIGNES = [c for c in conversions if abs(c["unites"] - c["couverts"]) > 0.001]

# ---------------------------------------------------------------------------
# 2. Verification de l'extrait du service (journee du 09/09/2022)
# ---------------------------------------------------------------------------
raf_serv = collections.defaultdict(list)
for h, m, ident in extrait_service["dels"]:
    raf_serv[h].append(m)
controle_service = []
for h_note, no, lib, q, pu, tot, tot_note in extrait_service["notes"]:
    best = None
    for h, ms in raf_serv.items():
        if abs(tm(h) - tm(h_note)) <= 10 and abs(round(sum(ms), 2) - tot) < 0.05:
            best = (h, round(sum(ms), 2), len(ms))
            break
    controle_service.append((h_note, no, q, pu, tot, best))

# ---------------------------------------------------------------------------
# 3. Dispersion des prix par periode de carte (annexe B, via renduFinalCalculs)
# ---------------------------------------------------------------------------
calc = json.load(open(CALCULS, encoding="utf-8"))
periodes = []
for p in calc["menus_par_periode"]:
    for m in p["menus"]:
        if m["menu"] != "Demi Lune":
            continue
        px = [x[0] for x in m["prix_custom"] if x[0]]
        periodes.append({
            "periode": p["periode"], "carte": p["carte"], "exercice": p["exercice"],
            "dates": p["dates"], "catalogue": m["prix_catalogue"],
            "q_cat": m["qte_catalogue"], "q_hors": m["qte_hors_catalogue"],
            "nb_prix": m["nb_prix_custom"], "eur_hors": m["eur_hors_catalogue"],
            "pmin": min(px) if px else 0, "pmax": max(px) if px else 0,
        })

TQC = sum(p["q_cat"] for p in periodes)
TQH = sum(p["q_hors"] for p in periodes)

# ---------------------------------------------------------------------------
# 4. Ecriture du classeur
# ---------------------------------------------------------------------------
H1 = Font(bold=True, size=12, color="FFFFFF")
FILL1 = PatternFill("solid", fgColor="1F2933")
BOLD = Font(bold=True)
FILLT = PatternFill("solid", fgColor="DDE6ED")
THIN = Border(*[Side(style="thin", color="B8C4CE")] * 4)
RA = Alignment(horizontal="right")
WRAP = Alignment(wrap_text=True, vertical="top")


def titre(ws, texte, ncol):
    ws.append([texte])
    ws.merge_cells(start_row=ws.max_row, start_column=1, end_row=ws.max_row, end_column=ncol)
    ws.cell(ws.max_row, 1).font = H1
    ws.cell(ws.max_row, 1).fill = FILL1


def entetes(ws, cols):
    ws.append(cols)
    for c in ws[ws.max_row]:
        c.font = BOLD
        c.fill = FILLT
        c.border = THIN
        c.alignment = Alignment(horizontal="center", wrap_text=True)


def largeurs(ws, ws_widths):
    for i, w in enumerate(ws_widths, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w


wb = openpyxl.Workbook()

# --- onglet 1 : les conversions au forfait
ws = wb.active
ws.title = "Conversions au forfait"
titre(ws, "Menu Demi Lune : conversions au forfait identifiees dans la caisse "
          f"({TOTAL_CONV} notes, {TOTAL_UNITES:g} unites de Menu Demi Lune, "
          f"{TOTAL_COUVERTS:g} couverts, {eur(TOTAL_EUR)} encaisses). "
          f"Ecart maximal constate : {eur(ECART_MAX)}.", 13)
ws.append(["Somme des lignes supprimees (evenements DEL, annexe E) = total de la note encaissee "
           "(annexe C). Rapprochement : meme journee, meme minute de rafale, ecart < 0,05 €."])
ws.merge_cells(start_row=ws.max_row, start_column=1, end_row=ws.max_row, end_column=13)
entetes(ws, ["Exercice", "Date", "Heure rafale", "Nb lignes supprimees",
             "Somme lignes supprimees (€)", "Detail des lignes supprimees",
             "Note n°", "Heure note", "Total note (€)", "Couverts",
             "Unites de Menu Demi Lune", "Composition de la note", "Ecart (€)"])
for c in conversions:
    ws.append([c["exercice"], c["date"], c["heure_rafale"], c["nb_suppr"], c["somme_suppr"],
               c["detail_suppr"], c["note"], c["heure_note"], c["total_note"],
               c["couverts"], c["unites"], c["composition"], c["ecart"]])
    for cell in ws[ws.max_row]:
        cell.border = THIN
        if isinstance(cell.value, (int, float)):
            cell.alignment = RA
    ws.cell(ws.max_row, 6).alignment = WRAP
    ws.cell(ws.max_row, 12).alignment = WRAP
ws.append(["TOTAL", "", "", TOTAL_LIGNES, TOTAL_SUPPR_EUR, "", "", "",
           TOTAL_EUR, TOTAL_COUVERTS, TOTAL_UNITES, "", TOTAL_ECART])
for cell in ws[ws.max_row]:
    cell.font = BOLD
    cell.fill = FILLT
    cell.border = THIN
ws.cell(ws.max_row, 13).number_format = "0.00"
ws.append([])
_dates = ", ".join(f"{c['date']} (note {c['note']})" for c in NOTES_MULTILIGNES)
ws.append(["Lecture des deux colonnes de quantite : la colonne « Couverts » ne retient que la "
           "quantite de la PREMIERE ligne « Menu Demi Lune » de la note ; la colonne « Unites de "
           f"Menu Demi Lune » somme toutes ces lignes. Les deux totaux different de "
           f"{TOTAL_UNITES - TOTAL_COUVERTS:g} unite(s), du seul fait des "
           f"{len(NOTES_MULTILIGNES)} note(s) ou le forfait a ete saisi en deux lignes a des prix "
           f"differents : {_dates}. Total general : {TOTAL_UNITES:g} unites de Menu Demi Lune "
           f"pour {TOTAL_COUVERTS:g} couverts."])
ws.merge_cells(start_row=ws.max_row, start_column=1, end_row=ws.max_row, end_column=13)
ws.cell(ws.max_row, 1).alignment = WRAP
ws.append(["Lecture de la colonne « Ecart » : somme des lignes supprimees "
           f"({eur(TOTAL_SUPPR_EUR)}) moins total des notes encaissees ({eur(TOTAL_EUR)}), soit "
           f"{eur(TOTAL_ECART)} cumules sur les {TOTAL_CONV} conversions. Cet ecart provient d'une "
           "seule note, ou la division du total par le nombre de couverts ne tombe pas juste au "
           "centime."])
ws.merge_cells(start_row=ws.max_row, start_column=1, end_row=ws.max_row, end_column=13)
ws.cell(ws.max_row, 1).alignment = WRAP
ws.append([f"Taux de couverture : ces {TOTAL_UNITES:g} unites de Menu Demi Lune se rapportent aux "
           f"{TQH} Menus Demi Lune vendus hors catalogue que denombre l'onglet "
           f"« Dispersion par periode », soit "
           f"{100.0 * TOTAL_UNITES / TQH:.1f} %".replace(".", ",") + "."])
ws.merge_cells(start_row=ws.max_row, start_column=1, end_row=ws.max_row, end_column=13)
ws.cell(ws.max_row, 1).alignment = WRAP
largeurs(ws, (11, 12, 12, 14, 18, 46, 9, 11, 14, 10, 16, 60, 10))
ws.freeze_panes = "A4"

# --- onglet 2 : l'extrait produit par le service
ws2 = wb.create_sheet("Extrait service 09-09-2022")
titre(ws2, "Journee du 09/09/2022 reproduite par le service page 55 : le rapprochement se lit "
           "sur son propre extrait.", 6)
entetes(ws2, ["Heure note", "Note n°", "Couverts", "Prix unitaire du menu (€)",
              "Total de la note (€)", "Rafale DEL correspondante"])
for h_note, no, q, pu, tot, best in controle_service:
    lib = (f"{best[0]} : {best[2]} suppressions = {eur(best[1])}" if best else "aucune")
    ws2.append([h_note, no, q, pu, tot, lib])
    for cell in ws2[ws2.max_row]:
        cell.border = THIN
ws2.append([])
entetes(ws2, ["Heure", "Montant supprime (€)", "Id evenement", "", "", ""])
for h, m, ident in extrait_service["dels"]:
    ws2.append([h, m, ident, "", "", ""])
    for cell in ws2[ws2.max_row]:
        cell.border = THIN
largeurs(ws2, (12, 10, 12, 22, 18, 46))

# --- onglet 3 : dispersion des prix par periode de carte
ws3 = wb.create_sheet("Dispersion par periode")
titre(ws3, "Menu Demi Lune : prix catalogue et ventes hors catalogue, par periode de carte "
           "(annexe B, prix de vente et quantites).", 9)
entetes(ws3, ["Periode", "Carte", "Exercice", "Dates", "Prix catalogue (€)",
              "Ventes au prix catalogue", "Ventes hors catalogue",
              "Part hors catalogue", "Plage des prix hors catalogue (€)"])
for p in periodes:
    tot = p["q_cat"] + p["q_hors"]
    ws3.append([p["periode"], p["carte"], p["exercice"], p["dates"], p["catalogue"],
                p["q_cat"], p["q_hors"], f"{100.0 * p['q_hors'] / tot:.1f} %".replace(".", ","),
                f"{p['pmin']:.2f} a {p['pmax']:.2f}".replace(".", ",")])
    for cell in ws3[ws3.max_row]:
        cell.border = THIN
ws3.append(["Total", "", "", "", PRIX_CATALOGUE, TQC, TQH,
            f"{100.0 * TQH / (TQC + TQH):.1f} %".replace(".", ","), ""])
for cell in ws3[ws3.max_row]:
    cell.font = BOLD
    cell.fill = FILLT
    cell.border = THIN
largeurs(ws3, (10, 8, 12, 24, 16, 20, 20, 16, 28))

os.makedirs(os.path.dirname(OUT), exist_ok=True)
wb.save(OUT)

print(f"Conversions au forfait detectees : {TOTAL_CONV}")
print(f"Notes contenant un Menu Demi Lune hors catalogue : {notes_hors_catalogue}")
print(f"Total encaisse sur ces conversions : {eur(TOTAL_EUR)}  couverts : {TOTAL_COUVERTS}")
print(f"Unites de Menu Demi Lune portees par ces conversions : {TOTAL_UNITES:g} "
      f"(couverts : {TOTAL_COUVERTS:g})")
print(f"Somme des lignes supprimees : {eur(TOTAL_SUPPR_EUR)}   ecart cumule : {eur(TOTAL_ECART)}")
print(f"Ecart maximal somme(DEL) - total note : {eur(ECART_MAX)}")
print(f"Ecart strictement nul : {NB_ECART_NUL} / {TOTAL_CONV}")
print(f"Ventes au prix catalogue : {TQC}   hors catalogue : {TQH} "
      f"({100.0 * TQH / (TQC + TQH):.1f} %)")
for h_note, no, q, pu, tot, best in controle_service:
    print(f"  09/09/2022 note {no} {h_note} : {q:g} x {pu} = {tot} -> {best}")
print(f"Ecrit : {OUT}")
