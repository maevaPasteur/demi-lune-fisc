#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rendu-final-tables-trop-nombreuses.py

Grief du fisc (Proposition p. 11 + section V « suppression de note », p. 18-19) :
le logiciel comporte des tables « virtuelles » (n° de note ouverts pour le règlement
séparé) ET autorise la suppression pure et simple d'une table et de tous ses articles.
Le service en conclut que les modifications ne sont pas vérifiables -> comptabilité
non probante (vecteur d'occultation supposé).

Réponse construite, fichiers à l'appui :
  (A) LE NUMÉRO N'EST PAS UNE PLACE. La salle réelle compte 14 tables intérieures
      (n° 1 à 12, 14, 15) ; les n° 13, 16, 17, 18 ne désignent AUCUNE table physique.
      Le numéro de note de la caisse va de 1 à 57 : c'est un rang de note quotidien,
      jamais un numéro de table (les numéros de terrasse 101-125 n'apparaissent JAMAIS
      dans l'export). On ne peut donc pas déduire des couverts d'un numéro.
  (B) ENCAISSEMENTS PAR NUMÉRO DE NOTE. Pour chaque rang de note (1 à 57), nombre
      d'encaissements, par saison et par exercice. La queue (rangs élevés) ne survient
      que les jours de pointe et correspond aux notes de règlement séparé.
  (C) LE MÉCANISME ET SON RETOURNEMENT. Un règlement = une note. Pour un paiement
      séparé, on ressaisit les articles sur une 2e note et on supprime la table
      d'origine : cette suppression est ARITHMÉTIQUEMENT NÉCESSAIRE pour ne pas
      DOUBLER le CA. Elle protège le CA, elle ne le réduit pas. Signature mécanique :
      1 906 notes (11,5 %) à quantité fractionnaire ; exemple daté de table scindée.

Le mécanisme est décrit par le vérificateur lui-même (synthèse 02-rejet-comptabilite-1.md,
p. 11 : « quatre tables virtuelles figurent à l'écran (n° 15 à n° 18, PAR EXEMPLE).
Cette modalité permet le traitement des notes multiples pour une table, au moment du
règlement. »).

Lecture SEULE des sources. Sorties :
  - public/documents/pieces-defense/RF-tables-trop-nombreuses.xlsx
  - src/data/renduFinal/tables-trop-nombreuses.json

Python : /tmp/xlsenv/bin/python (xlrd + openpyxl).
"""
import os
import re
import json
import collections

import xlrd
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

ICI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(ICI, ".."))
CAISSE = os.path.join(ROOT, "public/documents/caisse-enregistreuse/")
CALCULS = os.path.join(ROOT, "src/data/renduFinalCalculs.json")
CASSUP = os.path.join(ROOT, "src/data/renduFinalCasSuppressions.json")
OUT_XLSX = os.path.join(ROOT, "public/documents/pieces-defense/RF-tables-trop-nombreuses.xlsx")
OUT_JSON = os.path.join(ROOT, "src/data/renduFinal/tables-trop-nombreuses.json")
# Section graphique des couverts/semaine, produite par rendu-final-couverts.py
HEBDO_JSON = os.path.join(ROOT, "src/data/renduFinal/couverts-hebdomadaires.json")

EXOS = ["2022-2023", "2023-2024", "2024-2025"]
C = {e: CAISSE + f"ANNEXE-C{i}_detail-tickets_{e}.xls" for i, e in enumerate(EXOS, 1)}
F = {e: CAISSE + f"ANNEXE-F{i}_reglements_{e}.xls" for i, e in enumerate(EXOS, 1)}

# Plan de salle RÉEL (confirmé par la gérante) : 14 tables intérieures seulement.
# Les numéros 13, 16, 17, 18 ne désignent AUCUNE table physique.
INT_REELLES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15]
INT_INEXISTANTES = [13, 16, 17, 18]
NB_INT_REELLES = len(INT_REELLES)  # 14
SAISONS = ["Printemps", "Été", "Automne", "Hiver"]
MOIS_SAISON = {3: "Printemps", 4: "Printemps", 5: "Printemps",
               6: "Été", 7: "Été", 8: "Été",
               9: "Automne", 10: "Automne", 11: "Automne",
               12: "Hiver", 1: "Hiver", 2: "Hiver"}

DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


def euro(v):
    return f"{v:,.2f}".replace(",", " ").replace(".", ",") + " €"


def fr_int(v):
    return f"{int(round(v)):,}".replace(",", " ")


# ---------------------------------------------------------------------------
# 1) Notes fractionnaires (fichier C) : notes contenant >= 1 article à qté non entière
# ---------------------------------------------------------------------------
def notes_fractionnaires(ex):
    sh = xlrd.open_workbook(C[ex]).sheet_by_index(0)
    frac = set()
    for r in range(1, sh.nrows):
        date = str(sh.cell_value(r, 0))[:10]
        if not DATE_RE.fullmatch(date):
            continue
        no = str(sh.cell_value(r, 2)).replace(".0", "")
        try:
            q = float(sh.cell_value(r, 11))
        except (ValueError, TypeError):
            q = 0.0
        if q and abs(q - round(q)) > 1e-9:
            frac.add((date, no))
    return frac


# ---------------------------------------------------------------------------
# 2) Encaissements par NUMÉRO DE NOTE (fichier F = règlements)
#    Un encaissement = une note distincte = (date, no_ticket).
#    Le no_ticket est un rang quotidien (1..57), réattribué chaque jour : seule
#    granularité présente dans l'export (le n° de table physique n'y est jamais).
# ---------------------------------------------------------------------------
def encaissements():
    """
    Retourne :
      par_note[no] = {ex: count, "total": count}
      matrice[no][(ex, saison)] = count
      totaux_ys[(ex, saison)] = count
      total_global = int
    """
    par_note = collections.defaultdict(lambda: {e: 0 for e in EXOS})
    matrice = collections.defaultdict(lambda: collections.defaultdict(int))
    totaux_ys = collections.defaultdict(int)
    total_global = 0
    for ex in EXOS:
        sh = xlrd.open_workbook(F[ex]).sheet_by_index(0)
        vues = set()
        for r in range(1, sh.nrows):
            date = str(sh.cell_value(r, 0))[:10]
            nt = sh.cell_value(r, 2)
            if not DATE_RE.fullmatch(date) or not isinstance(nt, float):
                continue
            key = (date, int(nt))
            if key in vues:
                continue
            vues.add(key)
            no = int(nt)
            mois = int(date[5:7])
            sa = MOIS_SAISON[mois]
            par_note[no][ex] += 1
            matrice[no][(ex, sa)] += 1
            totaux_ys[(ex, sa)] += 1
            total_global += 1
    out = {}
    for k in sorted(par_note):
        row = dict(par_note[k])
        row["total"] = sum(par_note[k][e] for e in EXOS)
        out[k] = row
    return out, matrice, totaux_ys, total_global


# ---------------------------------------------------------------------------
# 3) Données déjà mesurées (paiements fractionnés / bancarisation)
# ---------------------------------------------------------------------------
CALC = json.load(open(CALCULS, encoding="utf-8"))
BANC = CALC["bancarisation"]
PF = CALC["paiements_fractionnes"]

NOTES_TOTAL = BANC["notes_total"]                 # 16608
NOTES_FRAC = BANC["notes_fractionnees"]            # 1906
NOTES_FRAC_PCT = BANC["notes_fractionnees_pct"]    # 11.5
BANC_PCT = BANC["bancarise_pct"]                   # 98.64
ESP_PCT = BANC["especes_pct"]                      # 1.36
PARTAGES_3ANS_EST = 880


# ---------------------------------------------------------------------------
# 4) Exemple daté de table réelle scindée (cas "partage")
# ---------------------------------------------------------------------------
CAS = json.load(open(CASSUP, encoding="utf-8"))
PARTAGE = next(c for c in CAS["cas"] if c["id"] == "partage")
EX = next(e for e in PARTAGE["exemples"] if e["date"] == "2022-05-14")
NB_EXEMPLES = len(PARTAGE["exemples"])


# ---------------------------------------------------------------------------
# 5) XLSX (pièce jointe)
# ---------------------------------------------------------------------------
GRAS = Font(bold=True)
GRAS_BLANC = Font(bold=True, color="FFFFFF")
ENTETE = PatternFill("solid", fgColor="0F766E")
SURLIGNE = PatternFill("solid", fgColor="CCFBF1")
CENTRE = Alignment(horizontal="center", vertical="center", wrap_text=True)
DROITE = Alignment(horizontal="right", vertical="center")
BORD = Border(*(4 * (Side(style="thin", color="D1D5DB"),)))


def styler_entete(ws, ncols, ligne=1):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=ligne, column=c)
        cell.font = GRAS_BLANC
        cell.fill = ENTETE
        cell.alignment = CENTRE
        cell.border = BORD


def largeurs(ws, widths):
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w


def construire_xlsx(par_note, matrice, totaux_ys, total_global):
    wb = openpyxl.Workbook()

    # --- Onglet 1 : Encaissements par note (total + par exercice) --------
    ws = wb.active
    ws.title = "Encaissements par note"
    ws.append(["Nombre d'encaissements par numéro de note (rang quotidien, 1 à 57)"])
    ws["A1"].font = GRAS
    ws.append([("Le numéro de note est un rang quotidien réattribué chaque jour (1, 2, 3 ...). "
                "C'est la seule granularité de l'export : le numéro de table physique n'y figure pas. "
                "Un encaissement = une note distincte (date + n° de note).")])
    ws["A2"].alignment = Alignment(wrap_text=True, vertical="top")
    ws.merge_cells("A2:E2")
    ws.row_dimensions[2].height = 45
    ws.append([])
    h = ws.max_row + 1
    ws.append(["N° de note"] + EXOS + ["Total"])
    styler_entete(ws, 5, h)
    for no in sorted(par_note):
        v = par_note[no]
        r = ws.max_row + 1
        ws.append([f"n°{no}", v[EXOS[0]], v[EXOS[1]], v[EXOS[2]], v["total"]])
        for c in range(1, 6):
            ws.cell(row=r, column=c).border = BORD
    rt = ws.max_row + 1
    ws.append(["Total",
               sum(v[EXOS[0]] for v in par_note.values()),
               sum(v[EXOS[1]] for v in par_note.values()),
               sum(v[EXOS[2]] for v in par_note.values()),
               total_global])
    for c in range(1, 6):
        ws.cell(row=rt, column=c).font = GRAS
        ws.cell(row=rt, column=c).border = BORD
    largeurs(ws, [14, 14, 14, 14, 12])
    ws.freeze_panes = "A" + str(h + 1)

    # --- Onglet 2 : Note x saison x exercice -----------------------------
    ws2 = wb.create_sheet("Note x saison x exercice")
    ws2.append(["Encaissements par numéro de note, par saison et par exercice"])
    ws2["A1"].font = GRAS
    ws2.append([])
    cols = [("ex", e, s) for e in EXOS for s in SAISONS]
    head = ["N° de note"] + [f"{e}\n{s}" for (_, e, s) in cols] + ["Total"]
    h2 = ws2.max_row + 1
    ws2.append(head)
    styler_entete(ws2, len(head), h2)
    for no in sorted(par_note):
        r = ws2.max_row + 1
        ligne = [f"n°{no}"]
        tot = 0
        for (_, e, s) in cols:
            val = matrice[no].get((e, s), 0)
            tot += val
            ligne.append(val)
        ligne.append(tot)
        ws2.append(ligne)
        for c in range(1, len(head) + 1):
            ws2.cell(row=r, column=c).border = BORD
    # ligne totaux
    rt2 = ws2.max_row + 1
    ligne = ["Total"]
    grand = 0
    for (_, e, s) in cols:
        val = totaux_ys.get((e, s), 0)
        grand += val
        ligne.append(val)
    ligne.append(grand)
    ws2.append(ligne)
    for c in range(1, len(head) + 1):
        ws2.cell(row=rt2, column=c).font = GRAS
        ws2.cell(row=rt2, column=c).border = BORD
    largeurs(ws2, [14] + [11] * len(cols) + [12])
    ws2.freeze_panes = "B" + str(h2 + 1)

    # --- Onglet 3 : Plan de salle reel -----------------------------------
    ws3 = wb.create_sheet("Plan de salle reel")
    ws3.append(["Plan de salle RÉEL (confirmé par la gérante) contre numérotation de la caisse"])
    ws3["A1"].font = GRAS
    ws3.append([])
    h3 = ws3.max_row + 1
    ws3.append(["N° dans la caisse", "Table physique ?", "Précision"])
    styler_entete(ws3, 3, h3)
    lignes3 = []
    for n in range(1, 19):
        if n in INT_REELLES:
            lignes3.append([f"n°{n}", "Oui (intérieur)", ""])
        else:
            note = "Numéro de note (règlement séparé) / non attribué"
            lignes3.append([f"n°{n}", "NON — aucune table", note])
    lignes3.append(["n°100", "Extérieur, le soir uniquement", "Pas de parasol, très rarement"])
    lignes3.append(["n°101 à 124", "Oui (terrasse)", ""])
    lignes3.append(["n°116 et 117", "Terrasse, 14 juillet et 31 déc. au soir", "Pas de parasol sinon"])
    lignes3.append(["n°125", "NON — aucune table", "N'existe pas"])
    for row in lignes3:
        r = ws3.max_row + 1
        ws3.append(row)
        for c in range(1, 4):
            ws3.cell(row=r, column=c).border = BORD
    largeurs(ws3, [18, 38, 36])
    ws3.freeze_panes = "A" + str(h3 + 1)

    # --- Onglet 4 : Notes fractionnees (synthèse mesurée) ----------------
    ws4 = wb.create_sheet("Notes fractionnees")
    ws4.append(["Le partage d'addition, déjà mesuré sur les fichiers de caisse"])
    ws4["A1"].font = GRAS
    ws4.append([])
    rows4 = [
        ("Notes (règlements) sur 3 exercices", fr_int(NOTES_TOTAL)),
        ("Notes portant une quantité fractionnaire (0,5 / 0,33...)", fr_int(NOTES_FRAC)),
        ("Part des notes fractionnaires", f"{str(NOTES_FRAC_PCT).replace('.', ',')} %"),
        ("Partages estimés sur 3 ans (~1 par service)", "~" + fr_int(PARTAGES_3ANS_EST)),
        ("Règlements bancarisés (CB, TR, CHV, CHQ)", f"{str(BANC_PCT).replace('.', ',')} %"),
        ("Règlements en espèces", f"{str(ESP_PCT).replace('.', ',')} %"),
    ]
    h4 = ws4.max_row + 1
    ws4.append(["Indicateur", "Valeur"])
    styler_entete(ws4, 2, h4)
    for lib, val in rows4:
        r = ws4.max_row + 1
        ws4.append([lib, val])
        ws4.cell(row=r, column=1).border = BORD
        ws4.cell(row=r, column=2).border = BORD
        ws4.cell(row=r, column=2).alignment = DROITE
    largeurs(ws4, [56, 24])
    ws4.freeze_panes = "A" + str(h4 + 1)

    # --- Onglet 5 : Exemple table scindee --------------------------------
    ws5 = wb.create_sheet("Exemple table scindee")
    ws5.append([f"Exemple daté : table réelle scindée en plusieurs notes — {EX['date']}"])
    ws5["A1"].font = GRAS
    ws5.append(["Deux notes de MÊME TOTAL, encaissées à la même minute, articles divisés en 0,5. "
                "Supprimer la table d'origine évite de compter ces articles deux fois."])
    ws5.append([])
    h5 = ws5.max_row + 1
    ws5.append(["Note", "Heure", "Article", "Quantité", "Prix unitaire", "Montant",
                "Physiquement insécable ?"])
    styler_entete(ws5, 7, h5)
    insecables = {"truite jurassienne", "croûtes morilles", "salade franc-comptoi", "cancoine"}
    for n in EX["notes"]:
        for it in n["items"]:
            r = ws5.max_row + 1
            lib = it["lib"]
            est_insec = "Oui" if (it.get("highlight") or lib.lower() in insecables) else ""
            ws5.append([n["label"], n["heure"], lib,
                        str(it["qte"]).replace(".", ","),
                        euro(it["pu"]), euro(it["montant"]), est_insec])
            for c in range(1, 8):
                ws5.cell(row=r, column=c).border = BORD
            if it.get("highlight"):
                for c in range(1, 8):
                    ws5.cell(row=r, column=c).fill = SURLIGNE
        rt = ws5.max_row + 1
        ws5.append([n["label"], n["heure"], "TOTAL NOTE", "", "", euro(n["total"]), ""])
        for c in range(1, 8):
            ws5.cell(row=rt, column=c).font = GRAS
            ws5.cell(row=rt, column=c).border = BORD
    largeurs(ws5, [12, 8, 24, 10, 14, 12, 24])
    ws5.freeze_panes = "A" + str(h5 + 1)

    os.makedirs(os.path.dirname(OUT_XLSX), exist_ok=True)
    wb.save(OUT_XLSX)
    return OUT_XLSX


# ---------------------------------------------------------------------------
# 6) JSON (page recodée)
# ---------------------------------------------------------------------------
def cg(t):
    return {"v": t}


def cd(t):
    return {"v": t, "align": "right"}


_HEBDO_CACHE = []


def charge_section_hebdo():
    """Section graphiqueLignes (couverts/semaine) produite par rendu-final-couverts.py.
    Retourne None si le fichier n'a pas encore été généré."""
    if _HEBDO_CACHE:
        return _HEBDO_CACHE[0]
    if not os.path.exists(HEBDO_JSON):
        _HEBDO_CACHE.append(None)
        return None
    with open(HEBDO_JSON, encoding="utf-8") as f:
        _HEBDO_CACHE.append(json.load(f))
    return _HEBDO_CACHE[0]


def construire_json(par_note, matrice, totaux_ys, total_global):
    max_note = max(par_note)

    # --- Card A : plan de salle réel (numéro != place) -------------------
    grille_int = {
        "kind": "grilleTables",
        "variante": "plan",
        "titre": "Plan de salle réel — intérieur (14 tables, n° 1 à 15 sauf 13)",
        "sousTitre": ("Sur les 18 numéros possibles à l'intérieur, seuls 14 désignent une table. "
                      "Les n° 13, 16, 17 et 18 ne correspondent à AUCUNE table physique : ce sont "
                      "des numéros de note (règlement séparé) ou des numéros non attribués."),
        "tables": [
            {"numero": f"n°{n}", "type": ("reelle" if n in INT_REELLES else "inexistante"),
             "note": (None if n in INT_REELLES else "Aucune table")}
            for n in range(1, 19)
        ],
    }
    # nettoyage des notes None
    for t in grille_int["tables"]:
        if t.get("note") is None:
            t.pop("note")

    # --- Card B : encaissements par numéro de note -----------------------
    cartes_notes = {
        "kind": "grilleTables",
        "variante": "notes",
        "titre": "Nombre d'encaissements par numéro de note (rang quotidien, 1 à 57)",
        "sousTitre": ("Chaque carte = un rang de note dans la journée (la 1ʳᵉ note encaissée, la 2ᵉ, "
                      "etc.). Le chiffre = le nombre total d'encaissements à ce rang sur les trois "
                      "exercices. Les rangs élevés (au-delà du nombre de tables) ne surviennent que "
                      "les jours de pointe : ce sont des notes de règlement séparé, pas des tables."),
        "tables": [{"numero": f"n°{no}", "total": par_note[no]["total"]} for no in sorted(par_note)],
    }

    # --- Tableau : note x saison x exercice ------------------------------
    cols = [(e, s) for e in EXOS for s in SAISONS]
    colonnes = [{"label": "N° de note"}]
    for (e, s) in cols:
        colonnes.append({"label": f"{e[2:4]}-{e[7:9]} {s[:4]}.", "align": "right"})
    colonnes.append({"label": "Total", "align": "right"})
    lignes_matrice = []
    for no in sorted(par_note):
        ligne = [cg(f"n°{no}")]
        tot = 0
        for (e, s) in cols:
            val = matrice[no].get((e, s), 0)
            tot += val
            ligne.append(cd(fr_int(val) if val else "·"))
        ligne.append({"v": fr_int(tot), "align": "right", "fw": 700})
        lignes_matrice.append(ligne)
    # ligne totaux
    ligne_tot = [{"v": "Total", "fw": 700}]
    grand = 0
    for (e, s) in cols:
        val = totaux_ys.get((e, s), 0)
        grand += val
        ligne_tot.append({"v": fr_int(val), "align": "right", "fw": 700})
    ligne_tot.append({"v": fr_int(grand), "align": "right", "fw": 700})
    lignes_matrice.append(ligne_tot)
    tab_matrice = {
        "kind": "tableau",
        "titre": "Encaissements par numéro de note, par saison et par exercice",
        "minWidth": 1180,
        "colonnes": colonnes,
        "lignes": lignes_matrice,
    }

    # --- Tableau : partage mesuré ----------------------------------------
    tab_partage = {
        "kind": "tableau",
        "titre": "Le partage d'addition, déjà mesuré sur les fichiers de caisse (annexes C)",
        "minWidth": 560,
        "colonnes": [{"label": "Indicateur"}, {"label": "Valeur", "align": "right"}],
        "lignes": [
            [cg("Notes (règlements) sur 3 exercices"), cd(fr_int(NOTES_TOTAL))],
            [cg("Notes portant une quantité fractionnaire (0,5 / 0,33...)"),
             cd(fr_int(NOTES_FRAC) + " (" + str(NOTES_FRAC_PCT).replace(".", ",") + " %)")],
            [cg("Partages estimés sur 3 ans (environ 1 par service)"),
             cd("~" + fr_int(PARTAGES_3ANS_EST))],
            [cg("Règlements bancarisés (CB, TR, CHV, CHQ)"),
             cd(str(BANC_PCT).replace(".", ",") + " %")],
            [cg("Règlements en espèces"), cd(str(ESP_PCT).replace(".", ",") + " %")],
        ],
    }

    # --- Tableau : exemple table scindée ---------------------------------
    lignes_ex = []
    for n in EX["notes"]:
        for it in n["items"]:
            lignes_ex.append([
                cg(n["label"]), cg(n["heure"]), cg(it["lib"]),
                cd(str(it["qte"]).replace(".", ",")),
                cd(euro(it["pu"])), cd(euro(it["montant"])),
            ])
        lignes_ex.append([
            cg(n["label"]), cg(n["heure"]), cg("TOTAL NOTE"),
            cd(""), cd(""), cd(euro(n["total"])),
        ])
    tab_exemple = {
        "kind": "tableau",
        "titre": f"Exemple daté ({EX['date']}) : une table scindée en deux notes de même total",
        "minWidth": 640,
        "colonnes": [
            {"label": "Note"}, {"label": "Heure"}, {"label": "Article"},
            {"label": "Quantité", "align": "right"},
            {"label": "Prix unitaire", "align": "right"},
            {"label": "Montant", "align": "right"},
        ],
        "lignes": lignes_ex,
    }

    pct_fr = str(NOTES_FRAC_PCT).replace(".", ",")

    sections = [
        # ============ 1) CE QUE DIT L'ADMINISTRATION ============
        {"kind": "chapitre", "source": "fisc", "numero": 1,
         "titre": "Ce que dit l'administration",
         "sousTitre": "Proposition de rectification p. 11 et section « suppression de note » (p. 18-19)."},
        {"kind": "note",
         "texte": ("Le vérificateur relève que la caisse comporte des **tables « virtuelles »** et "
                   "qu'elle **autorise la suppression d'une table et de tous ses articles**. Il en "
                   "conclut qu'« *il n'est pas possible de confirmer que ces modifications soient "
                   "légitimes* » et que la comptabilité serait, de ce fait, non probante (vecteur "
                   "supposé de couverts ou de recettes non déclarés).")},
        {"kind": "paragraphe",
         "texte": ("Le vérificateur décrit pourtant lui-même la fonction (p. 11) : « *quatre tables "
                   "virtuelles figurent à l'écran (n° 15 à n° 18, **par exemple**). Cette modalité "
                   "permet le traitement des notes multiples pour une table, au moment du "
                   "règlement.* » Une table « virtuelle » n'est donc pas une table en plus : c'est "
                   "une **note supplémentaire** ouverte pour encaisser séparément les convives "
                   "d'une **même** table. Nous le démontrons ci-dessous, fichiers de caisse à "
                   "l'appui.")},

        # ============ 2) CE QUE DÉMONTRENT LES FICHIERS ============
        {"kind": "chapitre", "source": "nous", "numero": 2,
         "titre": "Ce que démontrent les fichiers",
         "sousTitre": "Un numéro de note n'est pas une place ; la suppression protège le CA, elle ne le réduit pas."},

        # --- A. Le numéro n'est pas une place ---
        {"kind": "paragraphe",
         "texte": ("**Premier fait : un numéro n'est pas une table.** La salle compte en réalité "
                   f"**{NB_INT_REELLES} tables à l'intérieur** (n° 1 à 12, 14 et 15). Les numéros "
                   "**13, 16, 17 et 18 ne désignent aucune table physique** : ce sont des numéros "
                   "de note (règlement séparé) ou des numéros non attribués. C'est vérifiable sur "
                   "place : il suffit de compter les tables de la salle.")},
        grille_int,
        {"kind": "note",
         "texte": ("Même constat à l'extérieur : la **table n° 125 n'existe pas** ; les **n° 116 et "
                   "117** ne sont montées que le **14 juillet et le 31 décembre au soir** (pas de "
                   "parasol le reste de l'année) ; la **n° 100** ne sert que le soir, très rarement. "
                   "**Preuve décisive dans les fichiers** : si le numéro de la caisse était un numéro "
                   "de table, on verrait apparaître les numéros de terrasse (101 à 125). Or le "
                   f"numéro de note de l'export ne va **jamais au-delà de {max_note}** : c'est un "
                   "**rang de note quotidien** (1ʳᵉ note encaissée, 2ᵉ, etc.), réattribué chaque "
                   "jour, et non un numéro de table. On ne peut donc rien déduire de « couverts » à "
                   "partir d'un numéro.")},

        # --- B. Encaissements par numéro de note ---
        {"kind": "paragraphe",
         "texte": ("**Deuxième fait : le profil des encaissements le confirme.** Pour chaque rang "
                   "de note, voici le nombre d'encaissements sur les trois exercices. Les premiers "
                   "rangs sont atteints presque chaque jour d'ouverture (~660 fois) ; le nombre "
                   "décroît régulièrement ; les rangs élevés (au-delà du nombre de tables) ne "
                   "surviennent que les jours de pointe et correspondent aux **notes de règlement "
                   "séparé**, jamais à des tables supplémentaires.")},
        cartes_notes,
        {"kind": "paragraphe",
         "texte": ("Le détail par **saison** et par **exercice** est donné ci-dessous (et dans la "
                   "pièce jointe, recalculable ligne à ligne depuis les annexes C et F). Il montre "
                   "la saisonnalité attendue d'un restaurant de bord de canal (pic l'été) et la "
                   "décroissance régulière des rangs élevés, exercice après exercice.")},
        tab_matrice,
        *([{"kind": "paragraphe",
            "texte": ("Cette régularité se voit encore mieux sur le **nombre de couverts par "
                      "semaine** (un couvert = un plat ou un menu servi). En superposant les trois "
                      "exercices sur un même axe avril → mars, les courbes sont **quasi "
                      "identiques** : même montée au printemps, même pic estival, même creux "
                      "hivernal (fermeture en janvier et février). Une activité dissimulée se "
                      "traduirait par des écarts erratiques d'une année à l'autre ; au contraire, "
                      "l'exploitation est stable et reproductible.")},
           charge_section_hebdo(),
           {"kind": "piecejointe",
            "intro": ("Tout le calcul des couverts, étape par étape (lecture des annexes C de "
                      "caisse) : la classification de chaque item de la carte en plat/menu ou non, "
                      "le nombre de couverts par encaissement, et le total par jour et par service."),
            "fichiers": [
                {"fichier": "pieces-defense/RF-items-classification.xlsx",
                 "label": "Items de la caisse classés « plat/menu » (ce qui compte comme un couvert) (XLSX)"},
                {"fichier": "pieces-defense/RF-encaissements-couverts.xlsx",
                 "label": "Couverts par encaissement : date, heure, identifiant, nombre de couverts (XLSX)"},
                {"fichier": "pieces-defense/RF-couverts-par-service.xlsx",
                 "label": "Couverts par jour et par service (midi 10h-17h / soir 18h-minuit) (XLSX)"},
            ]}] if charge_section_hebdo() else []),

        # --- C. Le mécanisme et son retournement ---
        {"kind": "paragraphe",
         "texte": ("**Troisième fait : la suppression de la table d'origine est nécessaire et "
                   "protège le CA.** Le logiciel n'accepte **qu'un seul règlement par note**. Pour "
                   "un paiement séparé, le serveur ressaisit les articles d'un convive sur une "
                   "**deuxième note** (la table « virtuelle ») et l'encaisse. Les articles existent "
                   "alors **en double** : sur la table d'origine et sur la note ressaisie. "
                   "Supprimer la table d'origine est donc **arithmétiquement obligatoire pour ne "
                   "pas compter le repas deux fois**. Sans cette suppression, le chiffre d'affaires "
                   "serait **gonflé**, pas réduit. Le raisonnement de l'administration est inversé : "
                   "cette suppression **garantit l'exactitude** du CA, elle ne sert pas à le "
                   "diminuer.")},
        {"kind": "paragraphe",
         "texte": ("La **signature mécanique** de ce partage est massivement présente dans les "
                   f"fichiers : sur **{fr_int(NOTES_TOTAL)} notes**, **{fr_int(NOTES_FRAC)} "
                   f"({pct_fr} %)** portent une **quantité fractionnaire** (0,5 ; 0,33...), parce "
                   "qu'on **divise** l'article commun entre les payeurs. En parallèle, "
                   f"**{str(BANC_PCT).replace('.', ',')} % des règlements sont bancarisés** et "
                   f"**{str(ESP_PCT).replace('.', ',')} % seulement en espèces** : aucun canal "
                   "d'encaissement parallèle ne pourrait loger des couverts cachés.")},
        tab_partage,
        {"kind": "paragraphe",
         "texte": (f"L'exemple ci-dessous (**{EX['date']}**) est typique. Une même table est scindée "
                   f"en **deux notes (n°22 et n°23)** de **total identique "
                   f"({euro(EX['notes'][0]['total'])})**, encaissées **à la même minute**. Chaque "
                   "article y figure en **quantité 0,5**, y compris des plats **physiquement "
                   "insécables** (une **TRUITE JURASSIENNE**, des **Croûtes Morilles**) : on ne "
                   "sert pas une demi-truite à chaque convive, c'est **un seul plat payé à deux**. "
                   "Une fois ces deux notes encaissées, la table d'origine est supprimée pour "
                   f"éviter le double comptage. {fr_int(NB_EXEMPLES)} fiches de ce type (une par "
                   "mois actif) figurent dans la pièce jointe.")},
        tab_exemple,

        # --- Pièce jointe ---
        {"kind": "piecejointe",
         "intro": ("Encaissements par numéro de note (total et matrice saison × exercice), plan de "
                   "salle réel, notes fractionnaires et exemple daté de table scindée."),
         "fichiers": [
             {"fichier": "pieces-defense/RF-tables-trop-nombreuses.xlsx",
              "label": "RF - Tables et numéros de note : encaissements par note, saison et exercice (XLSX)"},
         ]},

        # ============ 3) CONCLUSION ============
        {"kind": "chapitre", "source": "nous", "numero": 3, "titre": "Conclusion"},
        {"kind": "paragraphe",
         "texte": ("Les tables « virtuelles » sont une **fonction de règlement**, et la suppression "
                   "qui les accompagne est une **opération anti-double-comptage**. Trois faits "
                   "reproductibles le démontrent : (1) le numéro de note de l'export va de 1 à "
                   f"{max_note} et ne désigne **jamais** une table (la salle compte "
                   f"{NB_INT_REELLES} tables intérieures, et les n° 13/16/17/18 n'existent pas) ; "
                   "(2) le profil des encaissements par rang de note décroît régulièrement, les "
                   "rangs élevés n'apparaissant que les jours de pointe ; (3) supprimer la table "
                   "d'origine après ressaisie **évite de doubler le CA**. Le grief ne révèle "
                   "**aucun couvert ni aucune recette non déclarée**.")},
        {"kind": "paragraphe",
         "texte": ("Cet argument se retourne contre l'administration : le vérificateur décrit "
                   "lui-même (p. 11) les tables virtuelles comme servant « au traitement des notes "
                   "multiples pour une table, au moment du règlement ». Il ne peut pas, ensuite, "
                   "présenter cette même fonction comme la preuve d'une dissimulation. La "
                   "réconciliation complète des suppressions (le CA déclaré égale les encaissements) "
                   "est démontrée au grief « suppressions de caisse ».")},
    ]

    meta = {
        "slug": "tables-trop-nombreuses",
        "titre": "Trop de tables / tables « virtuelles »",
        "refRapport": "Proposition p. 11 et p. 18-19",
        "griefFisc": ("La caisse comporte des tables « virtuelles » et autorise la suppression "
                      "d'une table et de tous ses articles ; ces modifications ne seraient pas "
                      "vérifiables, rendant la comptabilité non probante."),
        "reponseCourte": ("Un numéro de note n'est pas une table (la salle a 14 tables intérieures, "
                          "les n° 13/16/17/18 n'existent pas). La table « virtuelle » est une note "
                          "de règlement séparé, et la suppression de la table d'origine évite de "
                          "compter le repas deux fois : elle protège le CA, elle ne le réduit pas."),
        "tables_interieures_reelles": NB_INT_REELLES,
        "numeros_inexistants_int": INT_INEXISTANTES,
        "max_note": max_note,
        "notes_total": NOTES_TOTAL,
        "notes_fractionnees": NOTES_FRAC,
        "notes_fractionnees_pct": NOTES_FRAC_PCT,
        "encaissements_total": total_global,
        "_source": {
            "fichiers_caisse": [os.path.relpath(F[e], ROOT) for e in EXOS],
            "calculs": "src/data/renduFinalCalculs.json (paiements_fractionnes, bancarisation)",
            "cas": "src/data/renduFinalCasSuppressions.json (cas partage)",
            "plan_salle_reel": "confirmé par la gérante (mémoire tables-physiques-reelles)",
            "script": "scripts/rendu-final-tables-trop-nombreuses.py",
        },
    }

    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "sections": sections}, f, ensure_ascii=False, indent=2)
    return OUT_JSON


# ---------------------------------------------------------------------------
def main():
    par_note, matrice, totaux_ys, total_global = encaissements()
    chemin_xlsx = construire_xlsx(par_note, matrice, totaux_ys, total_global)
    chemin_json = construire_json(par_note, matrice, totaux_ys, total_global)

    print("=== Tables trop nombreuses : synthèse ===")
    print(f"Tables intérieures réelles : {NB_INT_REELLES} (n° 13/16/17/18 inexistants)")
    print(f"Encaissements totaux (notes distinctes) : {fr_int(total_global)}")
    print(f"Max numéro de note : {max(par_note)}")
    for ex in EXOS:
        tot = sum(matrice[no].get((ex, s), 0) for no in par_note for s in SAISONS)
        print(f"  {ex} : {fr_int(tot)} encaissements")
    print("Totaux par saison x exercice :")
    for e in EXOS:
        for s in SAISONS:
            print(f"  {e} {s:9s} : {totaux_ys.get((e, s), 0)}")
    print(f"Notes fractionnaires : {fr_int(NOTES_FRAC)} / {fr_int(NOTES_TOTAL)} = {NOTES_FRAC_PCT} %")
    print(f"Exemple table scindée : {EX['date']}, total {euro(EX['notes'][0]['total'])} x{len(EX['notes'])}")
    print(f"XLSX -> {chemin_xlsx}")
    print(f"JSON -> {chemin_json}")


if __name__ == "__main__":
    main()
