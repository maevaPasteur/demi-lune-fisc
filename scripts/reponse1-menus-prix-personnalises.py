#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REPONSE 1 - Partie B « Les factures sans detail (menus a prix personnalise) ».

Deux demonstrations reproductibles, produites dans un seul classeur :

 1. MENUS PAR PERIODE DE CARTE (P1 a P5). Pour chaque menu : prix catalogue,
    nombre vendu au prix catalogue, nombre vendu hors catalogue, recette hors
    catalogue et TOTAL ENCAISSE. Source : src/data/renduFinalCalculs.json,
    blocs `menus_par_periode` et `menus_custom`, eux-memes recalcules depuis
    les annexes de caisse par scripts/rendu-final-calculs.py.

 2. RAPPROCHEMENT EVENEMENTS / TICKETS. Le service ecrit (p. 20) que le
    numero d'identification est « different » dans tpvevenement.xls, ce qui le
    priverait de toute tracabilite. On mesure, exercice par exercice, la part
    des suppressions (« DEL ») rattachables au fichier des tickets par la
    journee et le numero de ticket Z, puis par le montant a l'euro pres.
    Sources : ANNEXE-E{1,2,3}_tpvevenement_*.xls et
              ANNEXE-C{1,2,3}_detail-tickets_*.xls (lecture seule).

Sortie : public/documents/pieces-reponse-1/R1-menus-prix-personnalises.xlsx
Le script imprime aussi en JSON les chiffres cites dans la page.
"""
import os, re, json, collections
import xlrd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill

ICI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(ICI, ".."))
CAISSE = os.path.join(ROOT, "public/documents/caisse-enregistreuse/")
PIECES = os.path.join(ROOT, "public/documents/pieces-reponse-1/")
CALCULS = os.path.join(ROOT, "src/data/renduFinalCalculs.json")
EXOS = ["2022-2023", "2023-2024", "2024-2025"]

TITRE = Font(bold=True, color="FFFFFF")
FOND = PatternFill("solid", fgColor="1F4E5F")
GRAS = Font(bold=True)


def entete(ws, cols, largeurs):
    ws.append(cols)
    for i, c in enumerate(cols, 1):
        cell = ws.cell(row=1, column=i)
        cell.font, cell.fill = TITRE, FOND
        cell.alignment = Alignment(horizontal="center", wrap_text=True)
        ws.column_dimensions[cell.column_letter].width = largeurs[i - 1]
    ws.freeze_panes = "A2"


# ----------------------------------------------------------------------------
# 1. Menus par periode de carte
# ----------------------------------------------------------------------------
D = json.load(open(CALCULS, encoding="utf-8"))
PERIODES = D["menus_par_periode"]
CUSTOM = D["menus_custom"]

synthese_periodes = []
for p in PERIODES:
    cat = sum(m["qte_catalogue"] for m in p["menus"])
    hc = sum(m["qte_hors_catalogue"] for m in p["menus"])
    eur_cat = sum(m["qte_catalogue"] * m["prix_catalogue"] for m in p["menus"])
    eur_hc = sum(m["eur_hors_catalogue"] for m in p["menus"])
    synthese_periodes.append({
        "periode": p["periode"], "carte": p["carte"], "exercice": p["exercice"],
        "dates": p["dates"], "qte_catalogue": cat, "qte_hors_catalogue": hc,
        "pct_hors_catalogue": round(100 * hc / (cat + hc), 1),
        "eur_catalogue": round(eur_cat), "eur_hors_catalogue": round(eur_hc),
        "eur_total": round(eur_cat + eur_hc),
    })

TOTAUX = {
    "qte_catalogue": sum(s["qte_catalogue"] for s in synthese_periodes),
    "qte_hors_catalogue": sum(s["qte_hors_catalogue"] for s in synthese_periodes),
    "eur_catalogue": sum(s["eur_catalogue"] for s in synthese_periodes),
    "eur_hors_catalogue": sum(s["eur_hors_catalogue"] for s in synthese_periodes),
}
TOTAUX["eur_total"] = TOTAUX["eur_catalogue"] + TOTAUX["eur_hors_catalogue"]
TOTAUX["pct_hors_catalogue"] = round(
    100 * TOTAUX["qte_hors_catalogue"]
    / (TOTAUX["qte_catalogue"] + TOTAUX["qte_hors_catalogue"]), 1)

# ----------------------------------------------------------------------------
# 2. Rapprochement evenements (DEL) / tickets, par la journee, le Z, le montant
# ----------------------------------------------------------------------------
def rapprochement(exo, i):
    E = xlrd.open_workbook(CAISSE + f"ANNEXE-E{i}_tpvevenement_{exo}.xls").sheet_by_index(0)
    C = xlrd.open_workbook(CAISSE + f"ANNEXE-C{i}_detail-tickets_{exo}.xls").sheet_by_index(0)
    # C : 0 Date, 1 Heure, 2 No_ticket, 4 No_z, 8 Id, 16 Tot_rem_ttc
    lignes = collections.defaultdict(list)
    tickets = set()
    for r in range(1, C.nrows):
        d, z = C.cell_value(r, 0), C.cell_value(r, 4)
        lignes[(d, z)].append(round(float(C.cell_value(r, 16) or 0), 2))
        tid = C.cell_value(r, 8)
        if isinstance(tid, float):
            tickets.add(tid)
    # E : 1 dateEven, 3 typEven, 6 no_zEport, 8 amount, 9 id
    ids_e, dels = set(), []
    for r in range(1, E.nrows):
        v = E.cell_value(r, 9)
        if isinstance(v, float):
            ids_e.add(v)
        if str(E.cell_value(r, 3)).strip() == "DEL":
            d = str(E.cell_value(r, 1))[:10]
            # meme filtre que scripts/rendu-final-calculs.py : on ecarte les
            # lignes de synthese (dates non conformes), pas des suppressions.
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", d):
                continue
            dels.append((d, E.cell_value(r, 6),
                         round(float(E.cell_value(r, 8) or 0), 2)))
    jour_z = sum(1 for d, z, a in dels if (d, z) in lignes)
    montant = sum(1 for d, z, a in dels if a in lignes.get((d, z), ()))
    return {
        "exercice": exo, "nb_del": len(dels),
        "rattaches_jour_et_z": jour_z,
        "pct_jour_et_z": round(100 * jour_z / len(dels), 2),
        "montant_retrouve": montant,
        "pct_montant": round(100 * montant / len(dels), 1),
        "id_evenements_min": int(min(ids_e)), "id_evenements_max": int(max(ids_e)),
        "id_tickets_min": int(min(tickets)), "id_tickets_max": int(max(tickets)),
    }


RAPPRO = [rapprochement(e, i) for i, e in enumerate(EXOS, 1)]

# Continuite de la sequence d'identifiants du fichier des evenements sur les
# trois exercices : un seul compteur, sans trou, donc aucun evenement manquant.
IDS = set()
for i, e in enumerate(EXOS, 1):
    sh = xlrd.open_workbook(CAISSE + f"ANNEXE-E{i}_tpvevenement_{e}.xls").sheet_by_index(0)
    IDS |= {int(sh.cell_value(r, 9)) for r in range(1, sh.nrows)
            if isinstance(sh.cell_value(r, 9), float)}
CONTINUITE = {
    "id_min": min(IDS), "id_max": max(IDS),
    "attendus": max(IDS) - min(IDS) + 1, "presents": len(IDS),
    "manquants": (max(IDS) - min(IDS) + 1) - len(IDS),
}
RAPPRO_TOT = {
    "nb_del": sum(r["nb_del"] for r in RAPPRO),
    "rattaches_jour_et_z": sum(r["rattaches_jour_et_z"] for r in RAPPRO),
    "montant_retrouve": sum(r["montant_retrouve"] for r in RAPPRO),
}
RAPPRO_TOT["pct_jour_et_z"] = round(
    100 * RAPPRO_TOT["rattaches_jour_et_z"] / RAPPRO_TOT["nb_del"], 2)
RAPPRO_TOT["pct_montant"] = round(
    100 * RAPPRO_TOT["montant_retrouve"] / RAPPRO_TOT["nb_del"], 1)

# ----------------------------------------------------------------------------
# Classeur
# ----------------------------------------------------------------------------
wb = Workbook()

ws = wb.active
ws.title = "Synthese par periode"
entete(ws, ["Periode", "Carte", "Exercice", "Dates", "Menus au prix catalogue",
            "Menus hors catalogue", "% hors catalogue", "Encaisse au catalogue (EUR)",
            "Encaisse hors catalogue (EUR)", "Total encaisse (EUR)"],
       [10, 8, 13, 26, 22, 20, 15, 22, 22, 20])
for s in synthese_periodes:
    ws.append([s["periode"], s["carte"], s["exercice"], s["dates"], s["qte_catalogue"],
               s["qte_hors_catalogue"], s["pct_hors_catalogue"], s["eur_catalogue"],
               s["eur_hors_catalogue"], s["eur_total"]])
ws.append(["TOTAL", "", "", "", TOTAUX["qte_catalogue"], TOTAUX["qte_hors_catalogue"],
           TOTAUX["pct_hors_catalogue"], TOTAUX["eur_catalogue"],
           TOTAUX["eur_hors_catalogue"], TOTAUX["eur_total"]])
for c in range(1, 11):
    ws.cell(row=ws.max_row, column=c).font = GRAS

ws = wb.create_sheet("Synthese par menu")
entete(ws, ["Menu", "Menus vendus (total)", "Dont hors catalogue",
            "% hors catalogue", "Recette hors catalogue (EUR)"],
       [22, 20, 20, 16, 26])
for menu, v in CUSTOM["par_menu"].items():
    ws.append([menu, v["total_q"], v["custom_q"], v["pct"], v["custom_eur"]])
ws.append(["TOTAL", CUSTOM["total_q"], CUSTOM["custom_q"], CUSTOM["pct"],
           CUSTOM["custom_eur"]])
for c in range(1, 6):
    ws.cell(row=ws.max_row, column=c).font = GRAS

for p in PERIODES:
    ws = wb.create_sheet(f"{p['periode']} carte {p['carte']}")
    entete(ws, ["Menu", "Prix catalogue (EUR)", "Vendus au prix catalogue",
                "Vendus hors catalogue", "Nb de prix distincts hors catalogue",
                "Encaisse au catalogue (EUR)", "Encaisse hors catalogue (EUR)",
                "Total encaisse (EUR)"],
           [22, 18, 22, 20, 24, 22, 22, 20])
    for m in p["menus"]:
        cat = m["qte_catalogue"] * m["prix_catalogue"]
        ws.append([m["menu"], m["prix_catalogue"], m["qte_catalogue"],
                   m["qte_hors_catalogue"], m["nb_prix_custom"], round(cat),
                   m["eur_hors_catalogue"], round(cat + m["eur_hors_catalogue"])])
    ws.append([f"{p['periode']} ({p['dates']}, exercice {p['exercice']})"])
    ws.cell(row=ws.max_row, column=1).font = GRAS

ws = wb.create_sheet("Prix hors catalogue")
entete(ws, ["Periode", "Carte", "Exercice", "Menu", "Prix catalogue (EUR)",
            "Prix pratique (EUR)", "Quantite", "Montant (EUR)"],
       [10, 8, 13, 22, 18, 18, 12, 14])
for p in PERIODES:
    for m in p["menus"]:
        for prix, qte in m["prix_custom"]:
            ws.append([p["periode"], p["carte"], p["exercice"], m["menu"],
                       m["prix_catalogue"], prix, qte, round(prix * qte, 2)])

ws = wb.create_sheet("Rapprochement DEL-tickets")
entete(ws, ["Exercice", "Suppressions (DEL)", "Rattachees a une journee et un Z du fichier tickets",
            "%", "Dont montant retrouve au centime sur une ligne du meme Z", "%",
            "Plage des id du fichier evenements", "Plage des id du fichier tickets"],
       [14, 18, 30, 8, 30, 8, 26, 26])
for r in RAPPRO:
    ws.append([r["exercice"], r["nb_del"], r["rattaches_jour_et_z"], r["pct_jour_et_z"],
               r["montant_retrouve"], r["pct_montant"],
               f"{r['id_evenements_min']} a {r['id_evenements_max']}",
               f"{r['id_tickets_min']} a {r['id_tickets_max']}"])
ws.append(["TOTAL", RAPPRO_TOT["nb_del"], RAPPRO_TOT["rattaches_jour_et_z"],
           RAPPRO_TOT["pct_jour_et_z"], RAPPRO_TOT["montant_retrouve"],
           RAPPRO_TOT["pct_montant"], "", ""])
for c in range(1, 9):
    ws.cell(row=ws.max_row, column=c).font = GRAS
ws.append([])
ws.append(["Continuite du compteur du fichier evenements (3 exercices) :",
           f"identifiants {CONTINUITE['id_min']} a {CONTINUITE['id_max']}",
           f"{CONTINUITE['presents']} evenements presents sur {CONTINUITE['attendus']} attendus",
           "", f"{CONTINUITE['manquants']} identifiant(s) manquant(s)"])
ws.cell(row=ws.max_row, column=1).font = GRAS

os.makedirs(PIECES, exist_ok=True)
sortie = os.path.join(PIECES, "R1-menus-prix-personnalises.xlsx")
wb.save(sortie)

print(json.dumps({
    "sortie": sortie,
    "periodes": synthese_periodes,
    "totaux": TOTAUX,
    "menus_custom": CUSTOM,
    "rapprochement": RAPPRO,
    "rapprochement_total": RAPPRO_TOT,
    "continuite_identifiants": CONTINUITE,
}, ensure_ascii=False, indent=2))
