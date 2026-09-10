#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REPONSE 1 - Degustation offerte : recomptage EXERCICE PAR EXERCICE.

Le service (reponse DDFiP 39 du 04/09/2026, p. 64 et p. 86) ne conteste ni les
6 292 degustations, ni la dose de 2 cl, ni la lecture ligne a ligne de l'annexe C.
Il oppose seulement que les 125,80 L sont "une globalisation sur 3 ans" et que ses
abattements forfaitaires de 15 % (BIB puis bouteilles bouchees) les couvriraient deja.

Ce script :
 1. refait le comptage sur les donnees reelles (ANNEXE-C1/C2/C3), en le ventilant
    PAR EXERCICE et PAR VIN NOMME (ce que le service reprochait de ne pas avoir) ;
 2. recontrole l'arithmetique des calculs du service de la page 64 / 86 ;
 3. dresse le releve des postes de perte auxquels le service oppose, dans le meme
    courrier, le meme et unique taux de 15 % (controle du double emploi).

Regle appliquee, identique a celle du memoire du 10/07/2026 :
  une degustation de 2 cl par VIN NOMME et par NOTE (date + n. ticket),
  quelle que soit la quantite. Generiques "Verre de vin" / "Pichet vin" (cubis,
  type non precise) et bouteilles EXCLUS.

Source : public/documents/caisse-enregistreuse/ANNEXE-C{1,2,3}_detail-tickets_*.xls
  col 0 = date ticket, col 2 = n. ticket, col 10 = libelle, col 11 = quantite.
Sortie : public/documents/pieces-reponse-1/R1-degustations-par-note.xlsx
Lecture seule, reproductible.
"""
import os
import collections
import xlrd

ICI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(ICI, ".."))
CAISSE = os.path.join(ROOT, "public/documents/caisse-enregistreuse/")
PIECES = os.path.join(ROOT, "public/documents/pieces-reponse-1/")
OUT = os.path.join(PIECES, "R1-degustations-par-note.xlsx")

EXOS = ["2022-2023", "2023-2024", "2024-2025"]
LIB_EXO = {"2022-2023": "Exercice 1 (2022-2023)",
           "2023-2024": "Exercice 2 (2023-2024)",
           "2024-2025": "Exercice 3 (2024-2025)"}
C = {e: CAISSE + f"ANNEXE-C{i}_detail-tickets_{e}.xls" for i, e in enumerate(EXOS, 1)}
DOSE_DEG = 2.0  # cl offerts par degustation

# Mapping libelle caisse -> vin nomme (verre/pichet), identique a
# scripts/rendu-final-degustation-notes.py : aucun ajout, aucun retrait.
TASTE = {
    "Savagnin verre": "Savagnin", "PICHET SAVAGNIN": "Savagnin",
    "Arbois Trousseau Le": "Arbois Trousseau", "PiCHET TROUSSEAU": "Arbois Trousseau",
    "Saint Véran Verre": "Saint Véran", "PICHET SAINT VERAN": "Saint Véran",
    "PICHET ALIGOTE 50cL": "Aligoté", "Verre ALIGOTE": "Aligoté",
    "Pichet CHUSLAN": "Chusclan", "Pichet CdR CHUSCLAN": "Chusclan",
    "VERRE CHUSCLAN": "Chusclan", "Verre CHUSCLAN": "Chusclan",
    "Arbois Chardonnay Le": "Arbois Chardonnay",
    "Chablis Le Verre": "Chablis", "Pichet Chablis": "Chablis",
    "Gewurztraminer Le ve": "Gewurztraminer", "PICHET GEWURZTRAMINE": "Gewurztraminer",
    "MACON VERRE": "Mâcon", "PICHET MACON": "Mâcon",
    "H.C.DE BEAUNE  VERRE": "HC de Beaune", "VERRE H.C.DE BEAUNE": "HC de Beaune",
    "PICHET C.DE BEAUNE R": "HC de Beaune", "PICHET C.DE BEAUNE B": "HC de Beaune",
    "PICHET HCB": "HC de Beaune",
    "Beaujolais Moulin à": "Moulin à Vent", "PICHET MOULIN A VENT": "Moulin à Vent",
    "pichet Saint Joseph": "Saint Joseph",
}

# --- Calculs du service a recontroler (p. 64 et p. 86, termes identiques) -----
# (categorie, exercice, base annoncee, unite de la base, resultat annonce en L)
CALCULS_SERVICE = [
    ("Vins au BIB", "Exercice 1", 45433.0, "cl", 67.99),
    ("Vins au BIB", "Exercice 2", 44079.0, "cl", 66.12),
    ("Vins au BIB", "Exercice 3", 42696.0, "cl", 64.04),
    ("Vins bouteilles bouchées", "Exercice 1", 1169.0, "L", 175.35),
    ("Vins bouteilles bouchées", "Exercice 2", 1153.87, "L", 173.08),
    ("Vins bouteilles bouchées", "Exercice 3", 1020.75, "L", 153.11),
]
CUMULS_SERVICE = [("Vins au BIB", 198.0), ("Vins bouteilles bouchées", 500.0)]

# --- Postes que le service impute au MEME taux forfaitaire de 15 % -----------
# (page, poste de perte en discussion, ce que le service oppose, citation exacte)
DOUBLE_EMPLOI_ROWS = [
    ("p. 61", "Freinte technique de la bière (mousse, collerette, nettoyage des lignes, fond de fût)",
     "Le taux de 15 % de fin de méthode, cumulé avec un taux spécifique de 15 % sur la bière",
     "« le service, compte tenu de la méthode de reconstitution employée, applique, en fin de "
     "méthode, 15 %, supplémentaires en taux de perte/offert/consommation du personnel » ; "
     "« le service retient donc en fait, un taux total de 30 % sur la bière »"),
    ("p. 72", "Offerts commerciaux",
     "La tranche de 5 % « offerts », comprise dans le 15 %",
     "« La réponse n’apporte aucun élément pertinent susceptible de considérer que les offerts, "
     "les pertes et les consommations du personnel pourraient être supérieurs aux 15 % retenus "
     "par le service. » ; « avec la proportion de 5 % pour l’offert, le service a minoré le "
     "montant du chiffre d’affaires TTC reconstitué, sur le premier exercice à hauteur de "
     "35 133,26 € »"),
    ("p. 72", "Pertes et casse",
     "La tranche de 5 % « pertes », comprise dans le 15 %",
     "« avec la proportion de 5 % pour les pertes, le service minore le montant du chiffre "
     "d’affaires TTC reconstitué à hauteur de 35 133,26 € »"),
    ("p. 73", "Consommation du personnel",
     "La tranche de 5 % « consommation du personnel », comprise dans le 15 %",
     "« le taux de 5 % appliqué pour la consommation du personnel, impacte toutes les boissons, "
     "y compris celles alcoolisées » ; « avec la proportion de 5 % pour la consommation du "
     "personnel, service a minoré le montant du chiffre d’affaires TTC reconstitué, sur le "
     "premier exercice à hauteur de 35 133,26 € »"),
    ("p. 83", "Freinte technique de la bière (à nouveau)",
     "Le même 15 % de fin de méthode, additionné au 15 % interne à la méthode",
     "« en fin de reconstitution, le service applique bien un taux de 15 % pour pertes, offerts "
     "et consommations du personnel. Mais, à l’intérieur de la méthode de reconstitution, le "
     "service avait, auparavant, déjà appliqué un taux spécifique sur perte de bière de 15 %. » ; "
     "« en cumulant les deux taux de sa méthode de reconstitution, le service avait déjà appliqué "
     "un taux de pertes, offerts, consommation du personnel de 30 % »"),
    ("p. 64 et p. 86", "Dégustation offerte (goûter du vin)",
     "Le même 15 %, appliqué cette fois au volume de vin disponible (198 L au BIB, 500 L en bouteilles)",
     "« le service a déjà retenu un taux offert/perte/consommation du personnel de 15 % (en fin "
     "de méthode de reconstitution) » ; « le cumul de 500 litres (arrondis) sur les trois "
     "exercices est près de 4 fois supérieur aux 125,80 litres proposées par Maître THIVEND »"),
    ("p. 89", "Dégustation offerte (à nouveau)",
     "Les trois mêmes tranches de 5 %, chiffrées aux mêmes 35 133,26 € par exercice",
     "« en retenant un taux de 5 % d’offerts dans sa méthode de reconstitution, a minoré le "
     "montant du chiffre d’affaires TTC reconstitué, sur le premier exercice à hauteur de "
     "35 133,26 € » ; « avec une proportion de 5 % pour les pertes, le service minore […] "
     "35 133,26 €, pour un exercice » ; « Avec la proportion de 5 % pour la consommation du "
     "personnel, service a minoré […] 35 133,26 € »"),
    ("p. 93", "Vraisemblance du coefficient multiplicateur",
     "Le même 15 %, cette fois utilisé une seule fois (et non 30 %) pour justifier le coefficient",
     "« grâce aux taux de perte/offerts/consommation du personnel de 15 %, retenu par le service, "
     "le coefficient moyen de l’exploitation de la société devrait être de : 3,85 x (1-0,15) "
     "= 3,2725 »"),
    ("p. 62 et p. 63", "Crémant jeté",
     "Aucun abattement opposé : le service conteste le principe même de la perte",
     "Ces deux pages n’invoquent aucun taux d’abattement pour pertes : le forfait de 15 % n’y "
     "est pas mentionné."),
]


def lire_lignes():
    """Lignes de vin nomme au verre/pichet : (exo, date, note, vin)."""
    lignes = []
    for exo, fn in C.items():
        sh = xlrd.open_workbook(fn).sheet_by_index(0)
        for r in range(1, sh.nrows):
            vin = TASTE.get(str(sh.cell_value(r, 10)).strip())
            if not vin:
                continue
            try:
                qte = float(sh.cell_value(r, 11))
            except ValueError:
                qte = 0.0
            if qte <= 0:
                continue
            lignes.append((exo, str(sh.cell_value(r, 0))[:10],
                           str(sh.cell_value(r, 2)), vin))
    return lignes


def compter(lignes):
    """Degustations = couples (exercice, date, note, vin) distincts."""
    distinct = set(lignes)
    par_exo_vin = collections.Counter()
    par_exo = collections.Counter()
    par_vin = collections.Counter()
    notes_exo = collections.defaultdict(set)
    for (exo, date, note, vin) in distinct:
        par_exo_vin[(exo, vin)] += 1
        par_exo[exo] += 1
        par_vin[vin] += 1
        notes_exo[exo].add((date, note))
    return par_exo_vin, par_exo, par_vin, notes_exo


def litres(n):
    return round(n * DOSE_DEG / 100.0, 2)


def ecrire_xlsx(par_exo_vin, par_exo, par_vin, notes_exo, n_lignes):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    white = Font(bold=True, color="FFFFFF")
    bold = Font(bold=True)
    head = PatternFill("solid", fgColor="0F766E")
    head2 = PatternFill("solid", fgColor="B45309")
    sub = PatternFill("solid", fgColor="E6F4F1")
    warn = PatternFill("solid", fgColor="FEF3C7")
    thin = Side(style="thin", color="D8DEE4")
    bd = Border(left=thin, right=thin, top=thin, bottom=thin)
    right = Alignment(horizontal="right")

    def entete(ws, cols, row, fill=head):
        for c, lab in enumerate(cols, 1):
            cell = ws.cell(row=row, column=c, value=lab)
            cell.font = white
            cell.fill = fill
            cell.alignment = Alignment(horizontal="center", vertical="center",
                                       wrap_text=True)
            cell.border = bd

    def titre(ws, t, st=None):
        ws.append([t])
        ws.cell(row=ws.max_row, column=1).font = Font(bold=True, size=13)
        if st:
            ws.append([st])
            ws.cell(row=ws.max_row, column=1).font = Font(italic=True, size=9,
                                                          color="64748B")
        ws.append([])

    vins = [v for v, _ in par_vin.most_common()]

    # ---- Feuille 1 : par exercice et par vin -------------------------------
    ws = wb.active
    ws.title = "Par exercice et par vin"
    titre(ws, "Dégustations offertes : décompte par exercice et par vin nommé",
          "2 cl offerts une seule fois par vin nommé et par note (date + n° de ticket). "
          "Génériques « Verre de vin » / « Pichet vin » (cubis) et bouteilles exclus. "
          "Source : ANNEXE-C1/C2/C3 (détail des tickets).")
    cols = ["Vin nommé"]
    for e in EXOS:
        cols += [f"{LIB_EXO[e]} : notes", f"{LIB_EXO[e]} : litres"]
    cols += ["3 exercices : notes", "3 exercices : litres"]
    hrow = ws.max_row + 1
    entete(ws, cols, hrow)
    for vin in vins:
        row = [vin]
        for e in EXOS:
            n = par_exo_vin[(e, vin)]
            row += [n, litres(n)]
        row += [par_vin[vin], litres(par_vin[vin])]
        ws.append(row)
        for c in range(1, len(cols) + 1):
            ws.cell(row=ws.max_row, column=c).border = bd
            if c > 1:
                ws.cell(row=ws.max_row, column=c).alignment = right
            if c % 2 == 1 and c > 1:
                ws.cell(row=ws.max_row, column=c).number_format = '#,##0.00 "L"'
    row = ["TOTAL"]
    for e in EXOS:
        row += [par_exo[e], litres(par_exo[e])]
    tot = sum(par_vin.values())
    row += [tot, litres(tot)]
    ws.append(row)
    for c in range(1, len(cols) + 1):
        cell = ws.cell(row=ws.max_row, column=c)
        cell.font = bold
        cell.fill = sub
        cell.border = bd
        if c > 1:
            cell.alignment = right
        if c % 2 == 1 and c > 1:
            cell.number_format = '#,##0.00 "L"'
    ws.append([])
    ws.append(["Lignes de vin nommé lues en caisse (verre / pichet)", n_lignes])
    ws.append(["Notes (additions) distinctes concernées, 3 exercices",
               sum(len(s) for s in notes_exo.values())])
    ws.append(["Dose retenue par dégustation", "2 cl"])
    for i, w in enumerate([22] + [13] * 8, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = ws.cell(row=hrow + 1, column=2)

    # ---- Feuille 2 : comparaison avec le service ---------------------------
    ws2 = wb.create_sheet("Comparaison service")
    titre(ws2, "Le volume offert, ramené à l’exercice",
          "Le service objecte (p. 86) que les 125,80 litres sont « une globalisation sur 3 ans ». "
          "Voici le même décompte, exercice par exercice.")
    entete(ws2, ["Exercice", "Dégustations (notes × vin)", "Volume offert (L)",
                 "Abattement 15 % BIB annoncé par le service (L)",
                 "Abattement 15 % bouteilles annoncé par le service (L)"], ws2.max_row + 1)
    bib = {"Exercice 1": 67.99, "Exercice 2": 66.12, "Exercice 3": 64.04}
    bout = {"Exercice 1": 175.35, "Exercice 2": 173.08, "Exercice 3": 153.11}
    for i, e in enumerate(EXOS, 1):
        k = f"Exercice {i}"
        ws2.append([LIB_EXO[e], par_exo[e], litres(par_exo[e]), bib[k], bout[k]])
        for c in range(1, 6):
            ws2.cell(row=ws2.max_row, column=c).border = bd
            if c > 1:
                ws2.cell(row=ws2.max_row, column=c).alignment = right
    ws2.append(["Cumul 3 exercices", tot, litres(tot),
                round(sum(bib.values()), 2), round(sum(bout.values()), 2)])
    for c in range(1, 6):
        ws2.cell(row=ws2.max_row, column=c).font = bold
        ws2.cell(row=ws2.max_row, column=c).fill = sub
        ws2.cell(row=ws2.max_row, column=c).border = bd
    ws2.append([])
    ws2.append(["Périmètre du décompte de dégustation",
                "Vins nommés servis au verre ou au pichet, versés depuis une bouteille."])
    ws2.append(["Périmètre exclu du décompte",
                "Génériques « Verre de vin » / « Pichet vin » (cubis, c’est-à-dire le BIB) "
                "et bouteilles vendues entières."])
    ws2.append(["Conséquence",
                "L’abattement de 15 % « vins au BIB » (198 L) porte exactement sur le "
                "périmètre que le décompte exclut : les deux volumes ne se recouvrent pas."])
    for i, w in enumerate([24, 22, 18, 30, 30], 1):
        ws2.column_dimensions[get_column_letter(i)].width = w

    # ---- Feuille 3 : controle arithmetique --------------------------------
    ws3 = wb.create_sheet("Contrôle arithmétique")
    titre(ws3, "Recontrôle des calculs du service (p. 64 et p. 86)",
          "Chaque ligne applique le taux de 15 % à la base que le service énonce lui-même.")
    entete(ws3, ["Catégorie", "Exercice", "Base énoncée par le service", "Taux",
                 "Résultat annoncé (L)", "Résultat recalculé (L)", "Écart (L)"],
           ws3.max_row + 1)
    for (cat, exo, base, unite, annonce) in CALCULS_SERVICE:
        calc = base * 0.15 / (100.0 if unite == "cl" else 1.0)
        ecart = round(calc - annonce, 4)
        ws3.append([cat, exo, f"{base:,.2f}".replace(",", " ").replace(".", ",") + " " + unite,
                    "15 %", annonce, round(calc, 4), ecart])
        for c in range(1, 8):
            ws3.cell(row=ws3.max_row, column=c).border = bd
            if c > 2:
                ws3.cell(row=ws3.max_row, column=c).alignment = right
        if abs(ecart) >= 0.01:
            ws3.cell(row=ws3.max_row, column=7).fill = warn
            ws3.cell(row=ws3.max_row, column=7).font = bold
    ws3.append([])
    for cat, cumul in CUMULS_SERVICE:
        somme = round(sum(a for (c_, e_, b_, u_, a) in CALCULS_SERVICE if c_ == cat), 2)
        ws3.append([cat, "Cumul 3 exercices", "Somme des 3 lignes ci-dessus", "",
                    cumul, somme, round(somme - cumul, 2)])
        for c in range(1, 8):
            ws3.cell(row=ws3.max_row, column=c).border = bd
            ws3.cell(row=ws3.max_row, column=c).font = bold
            if c > 2:
                ws3.cell(row=ws3.max_row, column=c).alignment = right
    for i, w in enumerate([26, 18, 26, 8, 20, 20, 12], 1):
        ws3.column_dimensions[get_column_letter(i)].width = w

    # ---- Feuille 4 : controle du double emploi du 15 % ---------------------
    ws4 = wb.create_sheet("Double emploi 15 %")
    titre(ws4, "Le même abattement de 15 %, opposé à des postes de perte différents",
          "Relevé des passages de la réponse du 04/09/2026 dans lesquels le service oppose "
          "un taux forfaitaire de 15 % à une demande de déduction. Le taux est unique ; "
          "les postes auxquels il est opposé sont distincts.")
    entete(ws4, ["Page", "Poste de perte en discussion",
                 "Ce que le service oppose", "Citation du courrier"],
           ws4.max_row + 1, fill=head2)
    for (page, poste, oppose, citation) in DOUBLE_EMPLOI_ROWS:
        ws4.append([page, poste, oppose, citation])
        for c in range(1, 5):
            cell = ws4.cell(row=ws4.max_row, column=c)
            cell.border = bd
            cell.alignment = Alignment(vertical="top", wrap_text=True)
    ws4.append([])
    ws4.append(["Conclusion",
                "Un taux unique de 15 %, appliqué une seule fois en fin de reconstitution, "
                "est opposé successivement à plusieurs postes de perte distincts. Chacun de "
                "ces postes ne peut être réputé « déjà couvert » par la totalité du même taux."])
    ws4.cell(row=ws4.max_row, column=1).font = bold
    ws4.cell(row=ws4.max_row, column=2).alignment = Alignment(vertical="top", wrap_text=True)
    for i, w in enumerate([10, 30, 34, 78], 1):
        ws4.column_dimensions[get_column_letter(i)].width = w

    os.makedirs(PIECES, exist_ok=True)
    wb.save(OUT)


def main():
    lignes = lire_lignes()
    par_exo_vin, par_exo, par_vin, notes_exo = compter(lignes)
    ecrire_xlsx(par_exo_vin, par_exo, par_vin, notes_exo, len(lignes))
    tot = sum(par_vin.values())
    print("REPONSE 1 - Degustations offertes, par exercice")
    print("-" * 60)
    print(f"  lignes de vin nomme lues : {len(lignes)}")
    for e in EXOS:
        print(f"  {LIB_EXO[e]:26s} {par_exo[e]:5d} deg.  {litres(par_exo[e]):7.2f} L  "
              f"({len(notes_exo[e])} notes)")
    print(f"  {'TOTAL 3 exercices':26s} {tot:5d} deg.  {litres(tot):7.2f} L")
    print("-" * 60)
    print("  Controle arithmetique des calculs du service :")
    for (cat, exo, base, unite, annonce) in CALCULS_SERVICE:
        calc = base * 0.15 / (100.0 if unite == "cl" else 1.0)
        print(f"    {cat:26s} {exo}  annonce {annonce:8.2f} L  "
              f"recalcule {calc:8.4f} L  ecart {calc - annonce:+.4f}")
    for cat, cumul in CUMULS_SERVICE:
        somme = round(sum(a for (c_, e_, b_, u_, a) in CALCULS_SERVICE if c_ == cat), 2)
        print(f"    {cat:26s} cumul annonce {cumul:8.2f} L  somme reelle {somme:8.2f} L")
    print("-" * 60)
    print(f"  XLSX : {OUT}")


if __name__ == "__main__":
    main()
