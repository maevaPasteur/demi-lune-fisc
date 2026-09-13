#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REPONSE 1 - Degustation offerte : DANS QUEL CONTENANT LE VIN NOMME A-T-IL ETE VENDU ?

Objet. Le service, page 64 de sa reponse du 04/09/2026, ne conteste aucune ligne
du decompte des degustations : il conteste le geste. Il soutient que la larme ne
consomme aucun centilitre supplementaire parce que le client « conserve son verre
qui est finalement rempli a hauteur du solde de la dose vendue ».

Ce mecanisme suppose un VERRE rempli jusqu'a une dose. Le present script etablit,
article par article et reference de caisse par reference de caisse, dans quel
contenant chaque vin nomme a reellement ete vendu, en appariant le prix unitaire
lu dans le detail des tickets au prix imprime sur la carte des vins.

Il produit trois resultats.

1. DEUX RETRAITS DE PERIMETRE que la societe opere d'elle-meme.
   a) Les vins achetes en BIB de 10 L (Bourgogne Aligote maison, Cotes du Rhone
      rouge maison de Chusclan) : deja retires par scripts/reponse1-degustations.py,
      l'abattement « vins au BIB » du service (198 L) les couvre.
   b) Les notes ou le vin nomme n'apparait que comme BOUTEILLE VENDUE ENTIERE.
      La regle de comptage exclut les bouteilles ; deux references de caisse y
      echappaient parce que leur libelle, tronque a vingt caracteres, est celui
      d'un article au verre :
        - « Arbois Chardonnay Le », reference 2019, vendu 24,90 EUR puis 29,00 EUR :
          c'est le prix de la « Bouteille 75 cl » de la carte, et l'Arbois
          Chardonnay n'y figure QUE en bouteille. Le service le dit lui-meme
          (proposition de rectifications du 18/05/2026, p. 36) : « Hormis pour des
          ventes de bouteilles specifiques, comme l'Arbois Blanc Bethanie, le
          Chardonnay et les bouteilles bouchees de rose, la societe propose comme
          article a la vente : vin au verre (doses de 15cl) ; vin au pichet de
          50 cl ; vin au pichet de 75 cl. »
        - « Beaujolais Moulin a », reference 1831, vendu 29,00 EUR puis 38,00 EUR :
          c'est le prix de la « Bouteille 75 cl » de la carte. Le meme libelle
          tronque porte aussi la reference 1832, vendue 5,80 EUR puis 7,60 EUR,
          qui est la colonne « Verre 15cl ».

2. LA PARTITION VERRE / PICHET du volume qui reste demande, qui mesure la part
   du decompte que l'objection de la page 64 peut atteindre. Le pichet est un
   contenant de contenance imprimee sur la carte (« Pichet 50cl ») ; le service
   en fixe lui-meme le volume (proposition, p. 36) et ecrit que « les contenants
   pour ces volumes sont normes dans le commerce » (reponse du 04/09/2026, p. 80).

3. L'ASSIETTE DES NOTES : combien de notes comporte le fichier de caisse, combien
   le decompte en retient. Reponse a l'objection de la page 64 selon laquelle le
   comptage « part du principe que du vin est consomme pour chaque note ».

Regle de comptage, inchangee : une degustation de 2 cl par VIN NOMME et par NOTE
(date + n. ticket), quelle que soit la quantite ; generiques « Verre de vin » et
« Pichet vin » (cubis, type non precise) exclus, bouteilles exclues. Le
dictionnaire des libelles et la table des conditionnements d'achat sont importes
de scripts/reponse1-degustations.py : aucun libelle n'est ajoute ni retire.

Sources :
  public/documents/caisse-enregistreuse/ANNEXE-C{1,2,3}_detail-tickets_*.xls
    col 0 = date ticket, col 2 = n. ticket, col 9 = Ref_prd, col 10 = libelle,
    col 11 = quantite, col 13 = prix unitaire TTC.
  public/documents/vins-boissons/carte_vins-boissons_2021-07-20.pdf et
    carte_vins-boissons_2023-04-26_actuelle.pdf (colonnes et prix imprimes ; les
    noms de fichiers sont inverses par rapport au contenu, ne pas s'y fier pour
    dater une carte).
Sortie : public/documents/pieces-reponse-1/R1-degustation-contenants.xlsx
Lecture seule, reproductible.
"""
import os
import collections
import importlib.util

import xlrd

ICI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(ICI, ".."))
CAISSE = os.path.join(ROOT, "public/documents/caisse-enregistreuse/")
PIECES = os.path.join(ROOT, "public/documents/pieces-reponse-1/")
OUT = os.path.join(PIECES, "R1-degustation-contenants.xlsx")

EXOS = ["2022-2023", "2023-2024", "2024-2025"]
LIB_EXO = {"2022-2023": "Exercice 1 (2022-2023)",
           "2023-2024": "Exercice 2 (2023-2024)",
           "2024-2025": "Exercice 3 (2024-2025)"}
C = {e: CAISSE + f"ANNEXE-C{i}_detail-tickets_{e}.xls" for i, e in enumerate(EXOS, 1)}
DOSE_DEG = 2.0  # cl offerts par degustation

_spec = importlib.util.spec_from_file_location(
    "rf_deg", os.path.join(ICI, "reponse1-degustations.py"))
_deg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_deg)
TASTE = _deg.TASTE
COND = _deg.COND
BIB, BOUT = _deg.BIB, _deg.BOUT

VERRE, PICHET, BTL = "verre", "pichet", "bouteille"

# References de caisse dont le libelle tronque evoque un article au verre mais
# dont le prix est celui de la bouteille de 75 cl imprimee sur la carte.
REF_BOUTEILLE = {
    "2019": ("Arbois Chardonnay Le", "Arbois Chardonnay", "24,90 € puis 29,00 €",
             "Colonne bouteille des deux cartes, 24,90 € sur l’une et 29,00 € sur "
             "l’autre ; l’Arbois Chardonnay ne figure sur aucune "
             "carte au verre ni au pichet"),
    "1831": ("Beaujolais Moulin à", "Moulin à Vent", "29,00 € puis 38,00 €",
             "Colonne « Bouteille 75cl » des deux cartes, 29,00 € puis 38,00 € ; "
             "le même libellé tronqué porte aussi la référence 1832, vendue "
             "5,80 € puis 7,60 €, qui est la colonne « Verre 15cl »"),
}

# Contenances et prix imprimes sur les deux cartes des vins de la societe, releves
# sur le texte des PDF eux-memes. Les colonnes y sont intitulees « Verre 15cl »,
# « Pichet 50cl » et « Bouteille 75cl ». ATTENTION : les noms des deux fichiers PDF
# sont inverses par rapport a leur contenu, verifie sur les prix et sur la date
# d'apparition des articles en caisse ; ne jamais dater une carte par son nom de
# fichier. Le prix retenu ci-dessous est celui de la carte dont les prix
# correspondent a ceux de la caisse sur les exercices verifies.
CARTE = [
    ("Arbois Savagnin", "Verre 15cl", "7,20 €", "1734", "7,20 € puis 8,30 €"),
    ("Arbois Savagnin", "Pichet 50cl", "28,00 €", "2089", "28,00 €"),
    ("Arbois Trousseau", "Verre 15cl", "6,40 €", "1828", "6,40 € puis 7,20 €"),
    ("Arbois Trousseau", "Pichet 50cl", "24,00 €", "2086", "24,00 € puis 28,00 €"),
    ("Saint Véran", "Verre 15cl", "7,90 €", "1737", "7,90 €"),
    ("Saint Véran", "Pichet 50cl", "30,00 €", "2090", "30,00 €"),
    ("Hautes Côtes de Beaune", "Verre 15cl", "7,90 €", "2026 et 1822",
     "7,90 € puis 9,50 €"),
    ("Hautes Côtes de Beaune", "Pichet 50cl", "30,00 €", "2088, 2091 et 2126",
     "30,00 € puis 32,00 €"),
    ("Moulin à Vent", "Verre 15cl", "5,80 €", "1832", "5,80 € puis 7,60 €"),
    ("Moulin à Vent", "Pichet 50cl", "21,00 €", "2087", "21,00 € puis 26,00 €"),
    ("Moulin à Vent", "Bouteille 75cl", "29,00 €", "1831", "29,00 € puis 38,00 €"),
    ("Mâcon Roche blanche", "Verre 15cl", "6,30 €", "2110", "6,30 €"),
    ("Mâcon Roche blanche", "Pichet 50cl", "21,00 €", "2125", "21,00 €"),
    ("Gewurztraminer", "Verre 15cl", "7,00 €", "1825", "7,00 €"),
    ("Gewurztraminer", "Pichet 50cl", "27,00 €", "2092", "27,00 €"),
    ("Chablis St Martin", "Verre 15cl", "7,90 €", "2021", "7,90 €"),
    ("Chablis St Martin", "Pichet 50cl", "30,00 €", "2098", "30,00 €"),
    ("Saint Joseph", "Pichet 50cl", "28,00 €", "2085", "28,00 € puis 32,20 €"),
    ("Arbois Chardonnay", "Bouteille 75cl", "24,90 €", "2019",
     "24,90 € puis 29,00 €"),
    ("Bourgogne Aligoté", "Verre 15cl", "3,90 €", "2112", "3,90 €"),
    ("Bourgogne Aligoté", "Pichet 50cl", "9,90 € puis 10,50 €", "2113", "10,50 €"),
    ("Côtes du Rhône (Chusclan)", "Verre 15cl", "3,90 €", "2115 et 0309", "3,90 €"),
    ("Côtes du Rhône (Chusclan)", "Pichet 50cl", "9,90 € puis 9,50 €",
     "2121 et 2114", "9,50 €"),
]

# Article au verre present en caisse mais absent du decompte, signale par honnetete.
SJ_VERRE_REF = "1830"


def type_contenant(libelle, ref):
    if ref in REF_BOUTEILLE:
        return BTL
    return PICHET if "pichet" in libelle.lower() else VERRE


def fmt_l(x):
    return f"{x:.2f}".replace(".", ",") + " L"


def fmt_n(n):
    return f"{n:,}".replace(",", " ")


def litres(n):
    return round(n * DOSE_DEG / 100.0, 2)


def lire():
    deg = collections.defaultdict(set)
    notes_totales = {}
    lignes = collections.Counter()
    sj_verre = set()
    sj_pichet = set()
    for exo, fn in C.items():
        sh = xlrd.open_workbook(fn).sheet_by_index(0)
        toutes = set()
        for r in range(1, sh.nrows):
            date = str(sh.cell_value(r, 0))[:10]
            note = str(sh.cell_value(r, 2))
            toutes.add((date, note))
            try:
                qte = float(sh.cell_value(r, 11))
            except ValueError:
                qte = 0.0
            if qte <= 0:
                continue
            ref = str(sh.cell_value(r, 9)).strip()
            if ref == SJ_VERRE_REF:
                sj_verre.add((exo, date, note))
            if ref == "2085":
                sj_pichet.add((exo, date, note))
            lib = str(sh.cell_value(r, 10)).strip()
            vin = TASTE.get(lib)
            if not vin:
                continue
            deg[(exo, date, note, vin)].add(type_contenant(lib, ref))
            lignes[(lib, ref, exo)] += 1
        notes_totales[exo] = len(toutes)
    return deg, notes_totales, lignes, sj_verre, sj_pichet


def classer(types):
    if types == {BTL}:
        return BTL
    if types == {PICHET}:
        return PICHET
    if types == {VERRE}:
        return VERRE
    if BTL in types:
        return "mixte-bouteille"
    return "mixte"


def ecrire(deg, notes_totales, lignes, sj_verre, sj_pichet):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    white = Font(bold=True, color="FFFFFF")
    bold = Font(bold=True)
    head = PatternFill("solid", fgColor="0F766E")
    sub = PatternFill("solid", fgColor="E6F4F1")
    warn = PatternFill("solid", fgColor="FEF3C7")
    thin = Side(style="thin", color="D8DEE4")
    bd = Border(left=thin, right=thin, top=thin, bottom=thin)
    right = Alignment(horizontal="right")
    haut = Alignment(vertical="top", wrap_text=True)

    def entete(ws, cols, row):
        for c, lab in enumerate(cols, 1):
            cell = ws.cell(row=row, column=c, value=lab)
            cell.font = white
            cell.fill = head
            cell.alignment = Alignment(horizontal="center", vertical="center",
                                       wrap_text=True)
            cell.border = bd

    def titre(ws, t, st=None):
        ws.append([t])
        ws.cell(row=ws.max_row, column=1).font = Font(bold=True, size=13)
        if st:
            ws.append([st])
            c = ws.cell(row=ws.max_row, column=1)
            c.font = Font(italic=True, size=9, color="64748B")
            c.alignment = haut
        ws.append([])

    CATS = [VERRE, PICHET, "mixte", BTL, "mixte-bouteille"]
    par_vin_cat = collections.Counter()
    par_vin = collections.Counter()
    par_exo_cat = collections.Counter()
    par_cond_cat = collections.Counter()
    notes_retenues = collections.defaultdict(set)
    for (exo, date, note, vin), types in deg.items():
        k = classer(types)
        par_vin_cat[(vin, k)] += 1
        par_vin[vin] += 1
        par_exo_cat[(exo, k)] += 1
        par_cond_cat[(COND[vin], k)] += 1
        notes_retenues[exo].add((date, note))
    vins = [v for v, _ in par_vin.most_common()]

    # ---- Feuille 1 : par vin ---------------------------------------------
    ws = wb.active
    ws.title = "Contenant par vin"
    titre(ws, "Le contenant réellement vendu sur la note, vin par vin",
          "Une dégustation = un vin nommé sur une note. Elle est classée selon les "
          "articles de ce vin figurant sur cette note, identifiés par leur référence "
          "de caisse et par leur prix, appariés au format imprimé sur la carte des "
          "vins. Source : ANNEXE-C1/C2/C3, détail des tickets, colonnes 9, 10, 11 et 13.")
    cols = ["Vin nommé", "Conditionnement d’achat",
            "Notes à verres seuls", "Notes à pichets seuls", "Notes verre et pichet",
            "Notes à bouteilles seules", "Total", "Volume compté",
            "Volume retiré de la demande", "Volume demandé"]
    ncol = len(cols)
    hrow = ws.max_row + 1
    entete(ws, cols, hrow)

    def bloc(lib, cond, cpt, retire_tout):
        n_v, n_p, n_m = cpt[VERRE], cpt[PICHET], cpt["mixte"]
        n_b = cpt[BTL] + cpt["mixte-bouteille"]
        tot = n_v + n_p + n_m + n_b
        if retire_tout:
            retire, demande = tot, 0
        else:
            retire, demande = n_b, n_v + n_p + n_m
        ws.append([lib, cond, n_v, n_p, n_m, n_b, tot,
                   litres(tot), litres(retire), litres(demande)])
        for c in range(1, ncol + 1):
            cell = ws.cell(row=ws.max_row, column=c)
            cell.border = bd
            if c > 2:
                cell.alignment = right
            if c >= 8:
                cell.number_format = '#,##0.00 "L"'
        return tot, retire, demande

    for cond in (BOUT, BIB):
        agg = collections.Counter()
        for vin in [v for v in vins if COND[v] == cond]:
            cpt = {k: par_vin_cat[(vin, k)] for k in CATS}
            for k in CATS:
                agg[k] += cpt[k]
            bloc(vin, cond, cpt, cond == BIB)
        lib = ("Sous-total bouteilles bouchées de 75 cl" if cond == BOUT
               else "Sous-total BIB de 10 L, entièrement retiré de la demande")
        bloc(lib, cond, agg, cond == BIB)
        for c in range(1, ncol + 1):
            ws.cell(row=ws.max_row, column=c).font = bold
            ws.cell(row=ws.max_row, column=c).fill = sub

    tot_all = collections.Counter()
    for vin in vins:
        for k in CATS:
            tot_all[k] += par_vin_cat[(vin, k)]
    n_v = tot_all[VERRE]
    n_p = tot_all[PICHET]
    n_m = tot_all["mixte"]
    n_b = tot_all[BTL] + tot_all["mixte-bouteille"]
    total = n_v + n_p + n_m + n_b
    bib_tot = sum(par_cond_cat[(BIB, k)] for k in CATS)
    dem_v = par_cond_cat[(BOUT, VERRE)] + par_cond_cat[(BOUT, "mixte")]
    dem_p = par_cond_cat[(BOUT, PICHET)]
    demande = dem_v + dem_p
    ws.append(["TOTAL", "Les douze vins nommés", n_v, n_p, n_m, n_b, total,
               litres(total), litres(bib_tot + n_b), litres(demande)])
    for c in range(1, ncol + 1):
        cell = ws.cell(row=ws.max_row, column=c)
        cell.border = bd
        cell.font = bold
        cell.fill = sub
        if c > 2:
            cell.alignment = right
        if c >= 8:
            cell.number_format = '#,##0.00 "L"'
    for i, w in enumerate([42, 24, 13, 13, 13, 13, 10, 13, 16, 13], 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = ws.cell(row=hrow + 1, column=3)

    # ---- Feuille 2 : du volume compté au volume demandé -------------------
    ws2 = wb.create_sheet("Du compté au demandé")
    titre(ws2, "Du volume compté au volume demandé : deux retraits de périmètre",
          "Les deux retraits sont opérés par la société elle-même. Ils ne sont pas "
          "demandés par le service, qui ne recalcule aucune ligne du décompte.")
    entete(ws2, ["Étape", "Dégustations", "Volume", "Motif"], ws2.max_row + 1)
    etapes = [
        ("Dégustations comptées note par note (annexes C1, C2, C3)", total,
         litres(total), "Une dégustation de 2 cl par vin nommé et par note"),
        ("moins les vins achetés en BIB de 10 L (Aligoté, Chusclan)", -bib_tot,
         -litres(bib_tot),
         "L’abattement « vins au BIB » du service, 198 L sur trois exercices, "
         "couvre déjà ce périmètre"),
        ("moins les notes où le vin nommé n’apparaît qu’en bouteille vendue entière",
         -n_b, -litres(n_b),
         "La règle de comptage exclut les bouteilles : références 2019 (Arbois "
         "Chardonnay, prix de la bouteille de 75 cl) et 1831 (Moulin à Vent, "
         "prix de la bouteille de 75 cl)"),
        ("Volume demandé", demande, litres(demande),
         "Vin nommé servi au verre ou au pichet depuis une bouteille bouchée de 75 cl"),
        ("dont vendu au verre, exposé à l’objection de la page 64", dem_v,
         litres(dem_v),
         "Il y a un verre et une dose de 15 cl : le mécanisme décrit par le service "
         "a un objet"),
        ("dont vendu au pichet, hors de portée de l’objection de la page 64", dem_p,
         litres(dem_p),
         "Le volume vendu est la contenance du récipient, « Pichet 50cl » sur la "
         "carte : il n’y a pas de solde de dose à compléter dans un verre"),
    ]
    for lab, n, l, motif in etapes:
        ws2.append([lab, n, l, motif])
        for c in range(1, 5):
            cell = ws2.cell(row=ws2.max_row, column=c)
            cell.border = bd
            if c in (2, 3):
                cell.alignment = right
            if c == 3:
                cell.number_format = '#,##0.00 "L"'
            if c == 4:
                cell.alignment = haut
        if lab.startswith(("Dégustations comptées", "Volume demandé")):
            for c in range(1, 5):
                ws2.cell(row=ws2.max_row, column=c).font = bold
                ws2.cell(row=ws2.max_row, column=c).fill = sub
    ws2.append([])
    ws2.append(["Article au verre présent en caisse et absent du décompte",
                len(sj_verre - sj_pichet), litres(len(sj_verre - sj_pichet)),
                "Le verre de Saint Joseph, référence 1830, vendu 7,20 € puis 9,70 €, "
                "soit le prix de la colonne « Verre 15cl » de la carte, figure sur 300 notes. "
                "Le décompte ne retient pour ce vin que le pichet. Ce volume n’est "
                "pas réclamé."])
    for c in range(1, 5):
        cell = ws2.cell(row=ws2.max_row, column=c)
        cell.border = bd
        cell.fill = warn
        if c in (2, 3):
            cell.alignment = right
        if c == 3:
            cell.number_format = '#,##0.00 "L"'
        if c == 4:
            cell.alignment = haut
    ws2.append([])
    ws2.append(["Ce que cette pièce n’établit pas", "", "",
                "Elle n’établit pas dans quel récipient la larme est versée lorsque "
                "le vin est vendu au verre. Ce point est un fait d’exploitation, que "
                "le décompte de caisse ne peut pas trancher."])
    ws2.cell(row=ws2.max_row, column=4).alignment = haut
    for i, w in enumerate([64, 14, 14, 62], 1):
        ws2.column_dimensions[get_column_letter(i)].width = w

    # ---- Feuille 3 : les notes retenues -----------------------------------
    ws3 = wb.create_sheet("Notes retenues")
    titre(ws3, "Le décompte ne part pas des notes : il part des lignes de vin nommé",
          "Réponse à l’objection de la page 64 selon laquelle le comptage « part du "
          "principe que du vin est consommé pour chaque note » et néglige que « tous "
          "les clients (et donc toutes les notes) ne consomment pas tous du vin ».")
    entete(ws3, ["Exercice", "Notes du fichier de caisse", "Notes retenues",
                 "Part retenue", "Notes écartées", "Dégustations comptées",
                 "Volume compté"], ws3.max_row + 1)

    def ligne3(lab, tot_n, ret, n_deg, gras=False):
        ws3.append([lab, tot_n, ret, ret / tot_n, tot_n - ret, n_deg, litres(n_deg)])
        for c in range(1, 8):
            cell = ws3.cell(row=ws3.max_row, column=c)
            cell.border = bd
            if c > 1:
                cell.alignment = right
            if c == 4:
                cell.number_format = "0,0 %"
            if c == 7:
                cell.number_format = '#,##0.00 "L"'
            if gras:
                cell.font = bold
                cell.fill = sub

    for exo in EXOS:
        ligne3(LIB_EXO[exo], notes_totales[exo], len(notes_retenues[exo]),
               sum(par_exo_cat[(exo, k)] for k in CATS))
    ligne3("Cumul des 3 exercices", sum(notes_totales.values()),
           sum(len(s) for s in notes_retenues.values()), total, gras=True)
    for i, w in enumerate([26, 20, 16, 13, 16, 18, 14], 1):
        ws3.column_dimensions[get_column_letter(i)].width = w

    # ---- Feuille 4 : carte et caisse --------------------------------------
    ws4 = wb.create_sheet("Carte et caisse")
    titre(ws4, "Le format vendu, apparié entre la carte des vins et la caisse",
          "Relevé sur le texte des deux cartes des vins de la société. Chaque prix "
          "unitaire relevé dans le détail des tickets correspond à une colonne "
          "imprimée sur la carte : « Verre 15cl », « Pichet 50cl » ou "
          "« Bouteille 75cl ».")
    entete(ws4, ["Vin, libellé de la carte", "Format imprimé sur la carte",
                 "Prix carte", "Référence de caisse", "Prix relevés en caisse"],
           ws4.max_row + 1)
    for row in CARTE:
        ws4.append(list(row))
        for c in range(1, 6):
            cell = ws4.cell(row=ws4.max_row, column=c)
            cell.border = bd
            if c > 2:
                cell.alignment = right
        if row[1].startswith("Bouteille"):
            for c in range(1, 6):
                ws4.cell(row=ws4.max_row, column=c).fill = warn
    for i, w in enumerate([30, 22, 22, 22, 24], 1):
        ws4.column_dimensions[get_column_letter(i)].width = w

    # ---- Feuille 5 : articles retenus -------------------------------------
    ws5 = wb.create_sheet("Articles retenus")
    titre(ws5, "Les articles de caisse retenus, référence par référence",
          "Aucun autre libellé n’est retenu. Les génériques « Verre de vin » et "
          "« Pichet vin » (cubis, type non précisé) restent exclus.")
    entete(ws5, ["Libellé exact en caisse", "Référence", "Vin nommé", "Contenant",
                 "Lignes exercice 1", "Lignes exercice 2", "Lignes exercice 3",
                 "Total lignes"], ws5.max_row + 1)
    cles = sorted({(lib, ref) for (lib, ref, _) in lignes},
                  key=lambda k: (TASTE[k[0]], k[0], k[1]))
    for lib, ref in cles:
        n = [lignes[(lib, ref, e)] for e in EXOS]
        t = type_contenant(lib, ref)
        ws5.append([lib, ref, TASTE[lib],
                    {VERRE: "Verre 15cl", PICHET: "Pichet 50cl",
                     BTL: "Bouteille 75cl"}[t]] + n + [sum(n)])
        for c in range(1, 9):
            cell = ws5.cell(row=ws5.max_row, column=c)
            cell.border = bd
            if c > 4:
                cell.alignment = right
            if t == BTL:
                cell.fill = warn
    for i, w in enumerate([26, 12, 22, 16, 15, 15, 15, 13], 1):
        ws5.column_dimensions[get_column_letter(i)].width = w

    os.makedirs(PIECES, exist_ok=True)
    wb.save(OUT)
    return {"total": total, "bib": bib_tot, "btl": n_b, "demande": demande,
            "dem_v": dem_v, "dem_p": dem_p,
            "notes_totales": sum(notes_totales.values()),
            "notes_retenues": sum(len(s) for s in notes_retenues.values()),
            "lignes": sum(lignes.values()),
            "sj": len(sj_verre - sj_pichet)}


def main():
    deg, notes_totales, lignes, sj_verre, sj_pichet = lire()
    r = ecrire(deg, notes_totales, lignes, sj_verre, sj_pichet)
    print(f"Dégustations comptées                          : {fmt_n(r['total'])} "
          f"({fmt_l(litres(r['total']))})")
    print(f"  retrait vins au BIB de 10 L                  : {fmt_n(r['bib'])} "
          f"({fmt_l(litres(r['bib']))})")
    print(f"  retrait notes en bouteille vendue entière    : {fmt_n(r['btl'])} "
          f"({fmt_l(litres(r['btl']))})")
    print(f"Volume demandé                                 : {fmt_n(r['demande'])} "
          f"({fmt_l(litres(r['demande']))})")
    print(f"  dont vendu au verre, exposé à la page 64     : {fmt_n(r['dem_v'])} "
          f"({fmt_l(litres(r['dem_v']))})")
    print(f"  dont vendu au pichet, hors de portée         : {fmt_n(r['dem_p'])} "
          f"({fmt_l(litres(r['dem_p']))})")
    print(f"Lignes de vin nommé lues                       : {fmt_n(r['lignes'])}")
    print(f"Notes du fichier de caisse                     : {fmt_n(r['notes_totales'])}")
    print(f"Notes retenues par le décompte                 : {fmt_n(r['notes_retenues'])} "
          f"({r['notes_retenues'] / r['notes_totales']:.1%})")
    print(f"Verre de Saint Joseph omis, non réclamé         : {fmt_n(r['sj'])} notes")
    print(f"Pièce écrite : {OUT}")


if __name__ == "__main__":
    main()
