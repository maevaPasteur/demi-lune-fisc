#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reponse1-numeros-de-note.py

Réponse DDFiP du 04/09/2026, partie F « Trop de tables / Tables virtuelles »
(p. 35 à 37).

Objet : établir, jour par jour et sur les trois exercices vérifiés, que le
numéro porté par l'export de la caisse est un RANG DE NOTE QUOTIDIEN et non un
numéro de table physique.

Démonstration :
  1. La numérotation repart à 1 chaque jour d'ouverture (le rang n° 1 est
     présent tous les jours ouverts, sans exception).
  2. Le rang le plus élevé de la journée suit le nombre d'additions du jour
     (corrélation quasi parfaite), et non un parc de tables constant (14).
  3. Le rang le plus élevé dépasse très souvent 18, alors que la salle ne
     comporte aucune table au delà du n° 15 à l'intérieur.

Lecture SEULE des annexes de caisse :
  public/documents/caisse-enregistreuse/ANNEXE-C{1,2,3}_detail-tickets_*.xls
    col 0 = date, col 1 = heure, col 2 = n° de note, col 10 = libellé, col 11 = qté.
La classification « plat/menu = un couvert » est reprise telle quelle du script
scripts/rendu-final-couverts.py (aucun double référentiel).

Sortie : public/documents/pieces-reponse-1/R1-numeros-de-note-par-jour.xlsx
"""
import os
import importlib.util
import collections
import datetime
import statistics

import xlrd
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

ICI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(ICI, ".."))
CAISSE = os.path.join(ROOT, "public/documents/caisse-enregistreuse/")
OUT = os.path.join(ROOT, "public/documents/pieces-reponse-1/")
EXOS = ["2022-2023", "2023-2024", "2024-2025"]
C = {e: CAISSE + f"ANNEXE-C{i}_detail-tickets_{e}.xls" for i, e in enumerate(EXOS, 1)}
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
# Places réelles (plan de salle confirmé, cf. src/data/renduFinal/tables-trop-nombreuses.json).
# Un seul espace est ouvert à chaque service : terrasse de début mai à début
# septembre, intérieur le reste de l'année.
PLACES_INTERIEUR = 44
PLACES_TERRASSE = 43

GRAS = Font(bold=True)
BLANC_GRAS = Font(bold=True, color="FFFFFF")
FOND = PatternFill("solid", fgColor="0F766E")
BORD = Border(*(Side(style="thin", color="BFBFBF"),) * 4)
GAUCHE = Alignment(horizontal="left", vertical="top", wrap_text=True)


def classification():
    spec = importlib.util.spec_from_file_location(
        "rfcouverts", os.path.join(ICI, "rendu-final-couverts.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    fam_of = m.familles()
    libs = set(fam_of)
    for e in EXOS:
        sh = xlrd.open_workbook(C[e]).sheet_by_index(0)
        for r in range(1, sh.nrows):
            lib = str(sh.cell_value(r, 10)).strip()
            if lib:
                libs.add(lib)
    return {lib: m.classer(lib, fam_of.get(lib)) for lib in libs}


def lire(classif):
    """notes[(exo, date, no)] = {heure_min, couverts}"""
    notes = {}
    for e in EXOS:
        sh = xlrd.open_workbook(C[e]).sheet_by_index(0)
        for r in range(1, sh.nrows):
            date = str(sh.cell_value(r, 0))[:10]
            if len(date) != 10 or date[4] != "-":
                continue
            no = sh.cell_value(r, 2)
            if not isinstance(no, float):
                continue
            key = (e, date, int(no))
            heure = str(sh.cell_value(r, 1))[:5]
            lib = str(sh.cell_value(r, 10)).strip()
            try:
                q = float(sh.cell_value(r, 11))
            except (ValueError, TypeError):
                q = 0.0
            rec = notes.setdefault(key, {"heure": heure, "couverts": 0.0})
            if heure and heure < rec["heure"]:
                rec["heure"] = heure
            v = classif.get(lib)
            if v and v[0]:
                rec["couverts"] += q
    return notes


def par_jour(notes):
    jours = {}
    for (e, date, no), rec in notes.items():
        j = jours.setdefault((e, date), {"nos": [], "couverts": 0.0,
                                         "midi": 0, "soir": 0,
                                         "couv_midi": 0.0, "couv_soir": 0.0})
        j["nos"].append(no)
        j["couverts"] += rec["couverts"]
        if rec["heure"] and rec["heure"] < "18:00":
            j["midi"] += 1
            j["couv_midi"] += rec["couverts"]
        else:
            j["soir"] += 1
            j["couv_soir"] += rec["couverts"]
    lignes = []
    for (e, date), j in sorted(jours.items(), key=lambda k: (k[0][1],)):
        nos = sorted(j["nos"])
        d = datetime.date(*map(int, date.split("-")))
        espace = "terrasse" if d.month in (5, 6, 7, 8) else "intérieur"
        places = PLACES_TERRASSE if espace == "terrasse" else PLACES_INTERIEUR
        lignes.append({
            "espace": espace, "places": places,
            "couv_midi": round(j["couv_midi"]), "couv_soir": round(j["couv_soir"]),
            "occ_midi": round(100 * j["couv_midi"] / places) if j["midi"] else "",
            "occ_soir": round(100 * j["couv_soir"] / places) if j["soir"] else "",
            "exo": e, "date": date, "jour": JOURS[d.weekday()],
            "nb_notes": len(nos), "note_max": nos[-1], "note_min": nos[0],
            "couverts": round(j["couverts"]),
            "services": (1 if j["midi"] else 0) + (1 if j["soir"] else 0),
            "midi": j["midi"], "soir": j["soir"],
            "suite_continue": nos == list(range(1, len(nos) + 1)),
        })
    return lignes


def entete(ws, ligne, ncols):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=ligne, column=c)
        cell.font = BLANC_GRAS
        cell.fill = FOND
        cell.border = BORD
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)


def ecrire(lignes, notes, stats, exemples):
    os.makedirs(OUT, exist_ok=True)
    wb = openpyxl.Workbook()

    # --- Feuille 1 : synthèse
    ws = wb.active
    ws.title = "Synthese"
    ws.append(["R1 : le numéro de note de la caisse est un rang quotidien, pas un numéro de table"])
    ws["A1"].font = Font(bold=True, size=13)
    ws.append(["Source : annexes C1 à C3 (détail des tickets). Lecture seule, script "
               "scripts/reponse1-numeros-de-note.py."])
    ws["A2"].alignment = GAUCHE
    ws.append([])
    ws.append(["Indicateur", "Valeur"])
    entete(ws, 4, 2)
    for k, v in stats:
        ws.append([k, v])
    ws.column_dimensions["A"].width = 78
    ws.column_dimensions["B"].width = 24

    # --- Feuille 2 : jour par jour
    ws = wb.create_sheet("Jour par jour")
    cols = ["Exercice", "Date", "Jour", "Nb de notes", "N° de note le plus élevé",
            "N° de note le plus bas", "Couverts", "Nb de services",
            "Notes midi", "Notes soir", "Suite 1..n sans trou",
            "Espace ouvert", "Places", "Couverts midi", "Couverts soir",
            "Occupation midi (%)", "Occupation soir (%)"]
    ws.append(cols)
    entete(ws, 1, len(cols))
    for l in lignes:
        ws.append([l["exo"], l["date"], l["jour"], l["nb_notes"], l["note_max"],
                   l["note_min"], l["couverts"], l["services"], l["midi"], l["soir"],
                   "Oui" if l["suite_continue"] else "Non",
                   l["espace"], l["places"], l["couv_midi"], l["couv_soir"],
                   l["occ_midi"], l["occ_soir"]])
    for c, w in zip("ABCDEFGHIJKLMNOPQ",
                    [11, 12, 11, 12, 16, 16, 10, 13, 11, 11, 18,
                     13, 8, 13, 13, 17, 17]):
        ws.column_dimensions[c].width = w
    ws.freeze_panes = "A2"

    # --- Feuille 3 : fréquence de chaque rang
    ws = wb.create_sheet("Frequence des rangs")
    ws.append(["Rang de note", "Nombre de jours où ce rang est utilisé",
               "Part des jours d'ouverture"])
    entete(ws, 1, 3)
    total_jours = len(lignes)
    freq = collections.Counter()
    for (e, date, no) in notes:
        freq[no] += 1
    for no in sorted(freq):
        ws.append([no, freq[no], round(100 * freq[no] / total_jours, 1)])
    for c, w in zip("ABC", [14, 38, 24]):
        ws.column_dimensions[c].width = w

    # --- Feuille 4 : journées d'exemple
    ws = wb.create_sheet("Journees exemple")
    ws.append(["Deux journées détaillées : le rang de note s'incrémente avec l'heure "
               "des additions, et repart à 1 le lendemain."])
    ws["A1"].font = GRAS
    ws.append([])
    r = 3
    for date in exemples:
        ws.cell(row=r, column=1, value=f"Journée du {date}").font = GRAS
        r += 1
        for i, lab in enumerate(["N° de note", "Heure de la note", "Couverts"], start=1):
            ws.cell(row=r, column=i, value=lab)
        entete(ws, r, 3)
        r += 1
        jour = sorted([(no, rec) for (e, d, no), rec in notes.items() if d == date])
        for no, rec in jour:
            ws.cell(row=r, column=1, value=no)
            ws.cell(row=r, column=2, value=rec["heure"])
            ws.cell(row=r, column=3, value=round(rec["couverts"], 1))
            r += 1
        r += 2
    for c, w in zip("ABC", [14, 18, 12]):
        ws.column_dimensions[c].width = w

    p = os.path.join(OUT, "R1-numeros-de-note-par-jour.xlsx")
    wb.save(p)
    return p


def main():
    classif = classification()
    notes = lire(classif)
    lignes = par_jour(notes)
    total_jours = len(lignes)

    # rang n°1 présent chaque jour ?
    j1 = sum(1 for l in lignes if l["note_min"] == 1)
    continues = sum(1 for l in lignes if l["suite_continue"])
    egal = sum(1 for l in lignes if l["note_max"] == l["nb_notes"])
    sup18 = sum(1 for l in lignes if l["note_max"] > 18)
    sup15 = sum(1 for l in lignes if l["note_max"] > 15)
    xs = [l["nb_notes"] for l in lignes]
    ys = [l["note_max"] for l in lignes]
    r = statistics.correlation(xs, ys)
    maxi = max(ys)
    # journées d'exemple : une journée creuse et une journée de pointe
    calmes = sorted(lignes, key=lambda l: l["nb_notes"])
    exemple_calme = calmes[len(calmes) // 12]["date"]
    exemple_pointe = max(lignes, key=lambda l: l["nb_notes"])["date"]

    occs = [o for l in lignes for o in (l["occ_midi"], l["occ_soir"]) if o != ""]
    occ_moy = round(statistics.mean(occs), 1)
    occ_sup = sum(1 for o in occs if o > 100)
    occ_max = max(occs)

    stats = [
        ("Jours d'ouverture couverts par les annexes C1 à C3", total_jours),
        ("Jours où la numérotation commence au n° 1", f"{j1} ({round(100*j1/total_jours,1)} %)"),
        ("Jours où les numéros forment la suite 1, 2, 3 … n sans trou",
         f"{continues} ({round(100*continues/total_jours,1)} %)"),
        ("Jours où le numéro le plus élevé égale le nombre de notes",
         f"{egal} ({round(100*egal/total_jours,1)} %)"),
        ("Corrélation entre le numéro le plus élevé et le nombre de notes du jour",
         round(r, 4)),
        ("Numéro de note le plus élevé observé sur les trois exercices", maxi),
        ("Jours où le numéro le plus élevé dépasse 15 (dernière table de la salle)",
         f"{sup15} ({round(100*sup15/total_jours,1)} %)"),
        ("Jours où le numéro le plus élevé dépasse 18 (dernier numéro d'écran)",
         f"{sup18} ({round(100*sup18/total_jours,1)} %)"),
        ("Notes (additions) au total", len(notes)),
        ("Couverts estimés au total", round(sum(l["couverts"] for l in lignes))),
        ("Services servis (midi ou soir avec au moins un couvert)", len(occs)),
        ("Occupation moyenne mesurée par service (couverts / places de l'espace ouvert)",
         f"{occ_moy} %"),
        ("Services dépassant 100 % des places : rotation de table déjà comptée",
         f"{occ_sup} ({round(100*occ_sup/len(occs),1)} %)"),
        ("Occupation la plus forte observée sur un service", f"{occ_max} %"),
        ("Journée d'exemple : jour creux", exemple_calme),
        ("Journée d'exemple : jour de pointe", exemple_pointe),
    ]
    p = ecrire(lignes, notes, stats, [exemple_calme, exemple_pointe])
    for k, v in stats:
        print(f"{k} : {v}")
    # moyennes par tranche de notes
    print("\n--- notes/jour vs numéro max ---")
    par_tranche = collections.defaultdict(list)
    for l in lignes:
        par_tranche[min(l["nb_notes"] // 10, 5)].append(l)
    for t in sorted(par_tranche):
        g = par_tranche[t]
        print(f"{t*10:>3}-{t*10+9:<3} notes/jour : {len(g):4d} jours, "
              f"n° max moyen {statistics.mean(x['note_max'] for x in g):.1f}, "
              f"couverts moyens {statistics.mean(x['couverts'] for x in g):.1f}")
    print(f"\nXLSX -> {p}")


if __name__ == "__main__":
    main()
