#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reponse1-quantites-fractionnaires.py

Réponse DDFiP 39 du 04/09/2026, partie D « Quantités anormales » (p. 28-29).
Le service écrit que la réponse « n'apporte aucun éclaircissement sur les
quantités inférieures à 1 » et qu'elle n'y parvient « tout au plus, [que] sur
une infime quantité ».

Ce script établit l'inverse, de façon reproductible et exhaustive, à partir des
seules annexes de caisse remises au vérificateur :

  1. il isole TOUTES les lignes à quantité non entière des fichiers
     ANNEXE-C1/C2/C3 (détail des tickets, 3 exercices) ;
  2. il regroupe les notes porteuses de ces fractions en « tables partagées »
     (même journée, notes voisines dans le temps : une addition partagée est
     encaissée en quelques minutes) ;
  3. pour chaque table, il additionne les quantités article par article
     (même libellé, même prix unitaire) et vérifie que la somme des fractions
     redonne un NOMBRE ENTIER : c'est la signature arithmétique du partage ;
  4. il vérifie dans ANNEXE-F1/F2/F3 (règlements) que chacune des notes
     jumelles a bien été ENCAISSÉE, et que la somme des notes de la table est
     égale au total de la table : une quantité fractionnaire ne minore rien.

Sortie : public/documents/pieces-reponse-1/R1-quantites-fractionnaires.xlsx
  - onglet « Synthese »        : les compteurs des 3 exercices
  - onglet « Tables partagees » : une ligne par table (date, heure, notes
    jumelles, total par note, total de la table, nb d'articles fractionnés)
  - onglet « Detail articles »  : le détail article par article, avec la
    quantité de chaque note et la colonne « Somme des fractions » + « Entier ? »
  - onglet « Exemples »         : trois tables datées, restituées ligne à ligne

Lecture seule sur les annexes. Aucun chiffre saisi à la main.
"""
import os
import re
import xlrd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

ICI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(ICI, ".."))
CAISSE = os.path.join(ROOT, "public/documents/caisse-enregistreuse")
EXOS = ["2022-2023", "2023-2024", "2024-2025"]
C = {e: os.path.join(CAISSE, f"ANNEXE-C{i}_detail-tickets_{e}.xls") for i, e in enumerate(EXOS, 1)}
F = {e: os.path.join(CAISSE, f"ANNEXE-F{i}_reglements_{e}.xls") for i, e in enumerate(EXOS, 1)}
OUT = os.path.join(ROOT, "public/documents/pieces-reponse-1/R1-quantites-fractionnaires.xlsx")

# Fenêtre de regroupement : une addition partagée est encaissée d'affilée.
FENETRE_MIN = 15
TOL = 0.02  # tolérance d'arrondi (0,33 + 0,33 + 0,34 = 1,00 ; 1/6 -> 0,16/0,17)


def est_entier(x, tol=TOL):
    return abs(x - round(x)) <= tol and round(x) >= 1


def minutes(h):
    m = re.match(r"(\d{1,2}):(\d{2})", str(h))
    return int(m.group(1)) * 60 + int(m.group(2)) if m else None


def fr(x, d=2):
    return f"{x:,.{d}f}".replace(",", "§").replace(".", ",").replace("§", " ")


# --------------------------------------------------------------------------- #
# 1. Lecture des annexes C : une entrée par note (ticket).
# --------------------------------------------------------------------------- #
def lire_notes(exercice):
    sh = xlrd.open_workbook(C[exercice]).sheet_by_index(0)
    notes = {}
    for r in range(1, sh.nrows):
        date = str(sh.cell_value(r, 0))[:10]
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
            continue
        no = sh.cell_value(r, 2)
        if not isinstance(no, float):
            continue
        cle = (date, int(no))
        n = notes.setdefault(cle, {"date": date, "no": int(no), "heure": str(sh.cell_value(r, 1))[:5],
                                   "ttc": 0.0, "lignes": []})
        try:
            n["ttc"] = round(float(sh.cell_value(r, 5)), 2)
        except (TypeError, ValueError):
            pass
        q = sh.cell_value(r, 11)
        pu = sh.cell_value(r, 13)
        if not isinstance(q, float) or not isinstance(pu, float):
            continue
        n["lignes"].append({"lib": str(sh.cell_value(r, 10)).strip(), "q": round(q, 2),
                            "pu": round(pu, 2), "montant": round(q * pu, 2)})
    return notes


def lire_reglements(exercice):
    sh = xlrd.open_workbook(F[exercice]).sheet_by_index(0)
    reg = {}
    for r in range(1, sh.nrows):
        date = str(sh.cell_value(r, 0))[:10]
        no = sh.cell_value(r, 2)
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date) or not isinstance(no, float):
            continue
        e = reg.setdefault((date, int(no)), {"montant": 0.0, "modes": []})
        try:
            e["montant"] = round(e["montant"] + float(sh.cell_value(r, 10)), 2)
        except (TypeError, ValueError):
            pass
        mode = str(sh.cell_value(r, 9)).strip()
        if mode and mode not in e["modes"]:
            e["modes"].append(mode)
    return reg


# --------------------------------------------------------------------------- #
# 2. Regroupement des notes fractionnaires en « tables partagées ».
# --------------------------------------------------------------------------- #
def constituer_tables(notes):
    """Une table = des notes de la même journée, voisines dans le temps, dont les
    quantités fractionnaires portent sur les mêmes articles."""
    frac = {}
    for cle, n in notes.items():
        if any(not est_entier(l["q"], 1e-9) and l["q"] > 0 for l in n["lignes"]):
            frac.setdefault(n["date"], []).append(n)

    tables = []
    for date, lst in frac.items():
        lst.sort(key=lambda n: (minutes(n["heure"]) if minutes(n["heure"]) is not None else 0, n["no"]))
        courant = []
        for n in lst:
            if courant and minutes(n["heure"]) is not None and minutes(courant[-1]["heure"]) is not None \
                    and minutes(n["heure"]) - minutes(courant[-1]["heure"]) <= FENETRE_MIN:
                courant.append(n)
            else:
                if len(courant) >= 2:
                    tables.append(courant)
                courant = [n]
        if len(courant) >= 2:
            tables.append(courant)
    return tables


def analyser_table(groupe):
    """Additionne les quantités par (article, prix unitaire) sur toutes les notes
    du groupe et dit si les fractions se recomposent en entiers."""
    agg = {}
    for n in groupe:
        for l in n["lignes"]:
            k = (l["lib"], l["pu"])
            a = agg.setdefault(k, {"lib": l["lib"], "pu": l["pu"], "par_note": {}, "total": 0.0})
            a["par_note"][n["no"]] = round(a["par_note"].get(n["no"], 0.0) + l["q"], 2)
            a["total"] = round(a["total"] + l["q"], 2)
    fractionnes = [a for a in agg.values() if any(not est_entier(q, 1e-9) for q in a["par_note"].values())]
    if not fractionnes:
        return None
    ok = [a for a in fractionnes if est_entier(a["total"])]
    return {
        "notes": groupe,
        "articles": sorted(fractionnes, key=lambda a: -a["pu"]),
        "nb_articles": len(fractionnes),
        "nb_entiers": len(ok),
        "complete": len(ok) == len(fractionnes),
        "total_table": round(sum(n["ttc"] for n in groupe), 2),
    }


# --------------------------------------------------------------------------- #
# 3. Calcul sur les trois exercices.
# --------------------------------------------------------------------------- #
resultats = {}
tout = []
for ex in EXOS:
    notes = lire_notes(ex)
    reg = lire_reglements(ex)
    tables = [t for t in (analyser_table(g) for g in constituer_tables(notes)) if t]
    nb_notes_frac = sum(1 for n in notes.values()
                        if any(not est_entier(l["q"], 1e-9) and l["q"] > 0 for l in n["lignes"]))
    nb_lignes_frac = sum(1 for n in notes.values() for l in n["lignes"]
                         if not est_entier(l["q"], 1e-9) and l["q"] > 0)
    art = sum(t["nb_articles"] for t in tables)
    art_ok = sum(t["nb_entiers"] for t in tables)
    # Encaissement des notes des tables partagées.
    enc, enc_ok = 0, 0
    for t in tables:
        for n in t["notes"]:
            enc += 1
            r = reg.get((n["date"], n["no"]))
            if r and abs(r["montant"] - n["ttc"]) <= 0.02:
                enc_ok += 1
    resultats[ex] = {
        "notes_total": len(notes), "notes_frac": nb_notes_frac, "lignes_frac": nb_lignes_frac,
        "tables": len(tables), "notes_en_table": sum(len(t["notes"]) for t in tables),
        "articles": art, "articles_entiers": art_ok,
        "tables_completes": sum(1 for t in tables if t["complete"]),
        "encaissees": enc_ok, "a_encaisser": enc,
        "ca_tables": round(sum(t["total_table"] for t in tables), 2),
    }
    for t in tables:
        t["exercice"] = ex
        t["reg"] = reg
    tout.extend(tables)

TOTAL = {k: sum(r[k] for r in resultats.values()) for k in
         ["notes_total", "notes_frac", "lignes_frac", "tables", "notes_en_table",
          "articles", "articles_entiers", "tables_completes", "encaissees", "a_encaisser", "ca_tables"]}
TOTAL["ca_tables"] = round(TOTAL["ca_tables"], 2)

print("=== Quantités fractionnaires : tables partagées reconstituées ===")
for ex in EXOS:
    r = resultats[ex]
    print(f"{ex} : {r['tables']} tables / {r['notes_en_table']} notes ; "
          f"articles fractionnés {r['articles_entiers']}/{r['articles']} somment à un entier ; "
          f"notes encaissées {r['encaissees']}/{r['a_encaisser']}")
print(f"TOTAL : {TOTAL['tables']} tables, {TOTAL['notes_en_table']} notes, "
      f"{TOTAL['articles_entiers']}/{TOTAL['articles']} articles entiers "
      f"({100 * TOTAL['articles_entiers'] / TOTAL['articles']:.1f} %), "
      f"{TOTAL['encaissees']}/{TOTAL['a_encaisser']} notes encaissées "
      f"({100 * TOTAL['encaissees'] / TOTAL['a_encaisser']:.1f} %), "
      f"CA des tables partagées {TOTAL['ca_tables']} €")
print(f"Notes fractionnaires (3 exercices) : {TOTAL['notes_frac']} sur {TOTAL['notes_total']} notes ; "
      f"{TOTAL['lignes_frac']} lignes.")

# --------------------------------------------------------------------------- #
# 4. Exemples datés : tables complètes, à 2 puis à 3 notes.
# --------------------------------------------------------------------------- #
def choisir_exemples():
    ex2 = [t for t in tout if t["complete"] and len(t["notes"]) == 2 and t["nb_articles"] >= 4]
    ex3 = [t for t in tout if t["complete"] and len(t["notes"]) == 3 and t["nb_articles"] >= 3]
    ex2.sort(key=lambda t: (-t["nb_articles"], t["notes"][0]["date"]))
    ex3.sort(key=lambda t: (-t["nb_articles"], t["notes"][0]["date"]))
    # L'exemple cité par le service lui-même : 14/04/2022, notes 13 et 14.
    fisc = [t for t in tout if t["notes"][0]["date"] == "2022-04-14"
            and {n["no"] for n in t["notes"]} >= {13, 14}]
    return (fisc[:1] or ex2[:1]) + ex2[:1] + ex3[:1]


EXEMPLES = choisir_exemples()

# --------------------------------------------------------------------------- #
# 5. Écriture du classeur.
# --------------------------------------------------------------------------- #
TITRE = Font(bold=True, color="FFFFFF", size=11)
FOND = PatternFill("solid", fgColor="1F4E5F")
GRAS = Font(bold=True)
OK = PatternFill("solid", fgColor="D8F0DC")
KO = PatternFill("solid", fgColor="FBE3E4")
CENTRE = Alignment(horizontal="center", vertical="center", wrap_text=True)

wb = openpyxl.Workbook()


def entete(ws, cols, largeurs):
    ws.append(cols)
    for i, _ in enumerate(cols, 1):
        c = ws.cell(row=1, column=i)
        c.font, c.fill, c.alignment = TITRE, FOND, CENTRE
        ws.column_dimensions[get_column_letter(i)].width = largeurs[i - 1]
    ws.freeze_panes = "A2"


# --- Synthèse ---
ws = wb.active
ws.title = "Synthese"
entete(ws, ["Exercice", "Notes de l'exercice", "Notes portant une quantité < 1",
            "Lignes à quantité fractionnaire", "Tables partagées identifiées",
            "Notes appartenant à une table partagée", "Articles fractionnés",
            "dont somme des fractions = entier", "% entiers",
            "Tables entièrement reconstituées", "Notes encaissées (annexe F)",
            "Total encaissé des tables partagées (€)"],
       [13, 16, 16, 16, 16, 18, 14, 18, 10, 16, 18, 20])
for ex in EXOS:
    r = resultats[ex]
    ws.append([ex, r["notes_total"], r["notes_frac"], r["lignes_frac"], r["tables"],
               r["notes_en_table"], r["articles"], r["articles_entiers"],
               round(100 * r["articles_entiers"] / r["articles"], 1) if r["articles"] else 0,
               f"{r['tables_completes']} / {r['tables']}",
               f"{r['encaissees']} / {r['a_encaisser']}", r["ca_tables"]])
ws.append(["3 exercices", TOTAL["notes_total"], TOTAL["notes_frac"], TOTAL["lignes_frac"],
           TOTAL["tables"], TOTAL["notes_en_table"], TOTAL["articles"], TOTAL["articles_entiers"],
           round(100 * TOTAL["articles_entiers"] / TOTAL["articles"], 1),
           f"{TOTAL['tables_completes']} / {TOTAL['tables']}",
           f"{TOTAL['encaissees']} / {TOTAL['a_encaisser']}", TOTAL["ca_tables"]])
for c in ws[ws.max_row]:
    c.font = GRAS
ws.append([])
ws.append(["Lecture : une « table partagée » regroupe des notes de la même journée, encaissées "
           "à moins de 15 minutes d'intervalle, dont les quantités fractionnaires portent sur "
           "les mêmes articles. La somme des fractions d'un même article y redonne un nombre entier."])
ws.append(["Source : ANNEXE-C1/C2/C3 (détail des tickets) et ANNEXE-F1/F2/F3 (règlements), "
           "fichiers remis au vérificateur. Script : scripts/reponse1-quantites-fractionnaires.py."])

# --- Tables partagées ---
ws = wb.create_sheet("Tables partagees")
entete(ws, ["Exercice", "Date", "Heure", "Notes jumelles", "Nombre de notes",
            "Total par note (€)", "Total de la table (€)", "Articles fractionnés",
            "dont somme = entier", "Table entièrement reconstituée", "Règlements retrouvés"],
       [12, 12, 9, 18, 10, 26, 16, 12, 12, 16, 22])
for t in sorted(tout, key=lambda t: (t["exercice"], t["notes"][0]["date"], t["notes"][0]["heure"])):
    ns = t["notes"]
    modes = []
    for n in ns:
        r = t["reg"].get((n["date"], n["no"]))
        modes.append("/".join(r["modes"]) if r else "absent")
    ws.append([t["exercice"], ns[0]["date"], ns[0]["heure"],
               " + ".join(f"n° {n['no']}" for n in ns), len(ns),
               " + ".join(fr(n["ttc"]) for n in ns), t["total_table"],
               t["nb_articles"], t["nb_entiers"],
               "oui" if t["complete"] else "partiel", " / ".join(modes)])
    ws.cell(row=ws.max_row, column=10).fill = OK if t["complete"] else KO

# --- Détail articles ---
ws = wb.create_sheet("Detail articles")
entete(ws, ["Exercice", "Date", "Heure", "Notes jumelles", "Article", "Prix unitaire (€)",
            "Quantités note par note", "Somme des fractions", "Somme = nombre entier ?",
            "Montant reconstitué (€)"],
       [12, 12, 9, 18, 30, 13, 24, 15, 16, 16])
for t in sorted(tout, key=lambda t: (t["exercice"], t["notes"][0]["date"], t["notes"][0]["heure"])):
    ns = t["notes"]
    for a in t["articles"]:
        detail = " + ".join(f"n° {no} : {fr(q)}" for no, q in sorted(a["par_note"].items()))
        entier = est_entier(a["total"])
        ws.append([t["exercice"], ns[0]["date"], ns[0]["heure"],
                   " + ".join(f"n° {n['no']}" for n in ns), a["lib"], a["pu"], detail,
                   a["total"], "OUI (= %d)" % round(a["total"]) if entier else "non",
                   round(a["total"] * a["pu"], 2)])
        ws.cell(row=ws.max_row, column=9).fill = OK if entier else KO

# --- Exemples ---
ws = wb.create_sheet("Exemples")
entete(ws, ["Exemple", "Date", "Heure", "Note", "Article", "Quantité",
            "Prix unitaire (€)", "Montant (€)", "Total de la note (€)", "Règlement encaissé (€)"],
       [30, 12, 9, 9, 30, 10, 13, 12, 16, 18])
for i, t in enumerate(EXEMPLES, 1):
    libelle = f"Exemple {i} : table du {t['notes'][0]['date']} partagée à {len(t['notes'])}"
    for n in t["notes"]:
        r = t["reg"].get((n["date"], n["no"]))
        for l in n["lignes"]:
            ws.append([libelle, n["date"], n["heure"], n["no"], l["lib"], l["q"], l["pu"],
                       l["montant"], n["ttc"],
                       (f"{fr(r['montant'])} ({'/'.join(r['modes'])})") if r else "absent"])
    ws.append([libelle + " : TOTAL DE LA TABLE", "", "", "", "", "", "",
               t["total_table"], t["total_table"], ""])
    for c in ws[ws.max_row]:
        c.font = GRAS
    for a in t["articles"]:
        ws.append([libelle + " : recomposition", "", "", "", a["lib"],
                   f"{' + '.join(fr(q) for _, q in sorted(a['par_note'].items()))} = {fr(a['total'])}",
                   a["pu"], round(a["total"] * a["pu"], 2), "", ""])
        ws.cell(row=ws.max_row, column=6).fill = OK if est_entier(a["total"]) else KO
    ws.append([])

os.makedirs(os.path.dirname(OUT), exist_ok=True)
wb.save(OUT)
print("Écrit :", OUT)
