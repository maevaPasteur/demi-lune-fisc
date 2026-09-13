#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REPONSE 1 - Degustation offerte : ou la larme peut-elle s'imputer ?

Le service (reponse DDFiP 39 du 04/09/2026, p. 64) oppose au decompte des
degustations un argument de FAIT : la larme ne s'ajouterait pas a la dose vendue,
elle s'y imputerait, parce que le client "conserve son verre qui est finalement
rempli a hauteur du solde de la dose vendue".

Ce mecanisme suppose qu'un VERRE de ce vin ait ete vendu sur la note : il faut un
"solde de la dose vendue" pour completer le verre. Quand le vin nomme n'apparait
sur la note que sous forme de PICHET, il n'y a aucun verre vendu a completer, et
le pichet est un contenant pre-mesure :
  - proposition de rectification p. 36 : "vin au verre (doses de 15cl) / vin au
    pichet de 50 cl / vin au pichet de 75 cl" ; p. 41 et p. 42 : le vin est vendu
    "soit au verre, soit au pichet de 50 cl, soit a la bouteille/pichet de 75 cl" ;
  - reponse du 04/09/2026 p. 80 : "les contenants pour ces volumes sont normes
    dans le commerce" ; p. 92 : "sur-dose sur des bouteilles de 75 cl et pichet
    de 50 cl => impossible".

Ce script partitionne donc les degustations selon que le vin nomme figure sur la
note au VERRE (le mecanisme du service a un objet) ou UNIQUEMENT AU PICHET (il
n'en a aucun), par exercice, par vin et par conditionnement d'achat.

Il produit aussi :
  - l'assiette des notes (combien de notes au total, combien portent un vin nomme),
    qui repond a l'objection du service selon laquelle "tous les clients (et donc
    toutes les notes) ne consomment pas tous du vin" ;
  - le releve des lignes de vin nomme enregistrees a prix zero, qui verifie que la
    degustation ne laisse pas de trace en caisse ;
  - les contenances retenues, libelle par libelle, avec leur source.

DEUX RETRAITS, appliques ici et communs aux deux pages du dossier :
  1. Les deux vins achetes en BIB de 10 L (Bourgogne Aligote maison, Cotes du
     Rhone rouge maison de Chusclan), 1 092 degustations et 21,84 L, releves de
     l'abattement "vins au BIB" de 198 L que le service oppose : ils sortent de
     la demande.
  2. Les lignes de VENTE DE BOUTEILLE ENTIERE que le libelle tronque de la caisse
     faisait passer pour un article au verre, alors que la regle de comptage
     exclut les bouteilles : "Arbois Chardonnay Le" (reference 2019, vendu 24,90
     puis 29,00 euros, prix de la colonne bouteille de la carte ; le service
     lui-meme range le Chardonnay parmi les "ventes de bouteilles specifiques",
     proposition p. 36) et "Beaujolais Moulin a" sous la SEULE reference 1831
     (29,00 puis 38,00 euros, prix bouteille), la reference 1832 du meme libelle
     etant, elle, le verre (5,80 puis 7,60 euros). 329 degustations, 6,58 L.

Le decompte passe ainsi de 6 292 degustations (125,84 L), chiffre repris tel quel
par le service, a 5 963 (119,26 L), dont 1 092 au BIB (21,84 L) : la demande
porte sur 4 871 degustations, soit 97,42 L.

Regle de comptage, pour le reste identique a scripts/reponse1-degustations.py :
  une degustation de 2 cl par VIN NOMME et par NOTE (date + n. ticket), quelle que
  soit la quantite. Generiques "Verre de vin" / "Pichet vin" (cubis) et bouteilles
  EXCLUS.

Sources : public/documents/caisse-enregistreuse/ANNEXE-C{1,2,3}_detail-tickets_*.xls
  col 0 = date ticket, col 2 = n. ticket, col 9 = reference article, col 10 =
  libelle, col 11 = quantite, col 13 = prix unitaire TTC, col 16 = total ligne TTC ;
  src/data/calculsBoissons/consoTotaleParBoisson.json, champ "unite_achat" ;
  src/data/calculsBoissons/itemsCaisse.json, champs "format_service" et
  "volume_unitaire_cl".
Sortie : public/documents/pieces-reponse-1/R1-degustation-verre-et-pichet.xlsx
Lecture seule sur les donnees, reproductible.
"""
import os
import json
import collections
import xlrd

ICI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(ICI, ".."))
CAISSE = os.path.join(ROOT, "public/documents/caisse-enregistreuse/")
CONSO = os.path.join(ROOT, "src/data/calculsBoissons/consoTotaleParBoisson.json")
ITEMS = os.path.join(ROOT, "src/data/calculsBoissons/itemsCaisse.json")
PIECES = os.path.join(ROOT, "public/documents/pieces-reponse-1/")
OUT = os.path.join(PIECES, "R1-degustation-verre-et-pichet.xlsx")

EXOS = ["2022-2023", "2023-2024", "2024-2025"]
LIB_EXO = {"2022-2023": "Exercice 1 (2022-2023)",
           "2023-2024": "Exercice 2 (2023-2024)",
           "2024-2025": "Exercice 3 (2024-2025)"}
C = {e: CAISSE + f"ANNEXE-C{i}_detail-tickets_{e}.xls" for i, e in enumerate(EXOS, 1)}
DOSE_DEG = 2.0  # cl offerts par degustation

# Mapping libelle caisse -> vin nomme, repris a l'identique de
# scripts/reponse1-degustations.py : aucun ajout, aucun retrait.
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

# Lignes de VENTE DE BOUTEILLE ENTIERE a retirer du decompte :
# libelle -> references concernees (None = toutes). Voir l'en-tete.
VENTE_BOUTEILLE = {
    "Arbois Chardonnay Le": None,
    "Beaujolais Moulin à": {"1831"},
}

# Libelles de caisse portant le MEME vin nomme sous un autre format (verre ou
# bouteille) et absents du mapping de degustation. Ils ne creent aucune
# degustation : ils servent au seul controle de la partition verre / pichet.
AUTRE_FORMAT = {
    "Arbois Savagnin": "Savagnin",
    "Saint Véran": "Saint Véran",
    "Chablis": "Chablis",
    "MACON bouteille": "Mâcon",
    "Alsace Gewurztramine": "Gewurztraminer",
    "Arbois Trousseau Bou": "Arbois Trousseau",
    "C du  Rhone St Josep": "Saint Joseph",
    "C du Rhone St  Josep": "Saint Joseph",
    "H.C.B BEAUNE BTL": "HC de Beaune",
    "H.C.BEAUNE BOUTEILLE": "HC de Beaune",
}

VIN_SOURCE = {
    "Savagnin": "Arbois Savagnin",
    "Arbois Trousseau": "Arbois Trousseau",
    "Saint Véran": "Saint Véran",
    "Aligoté": "Bourgogne Aligoté maison",
    "Chusclan": "Côtes du Rhône rouge maison (Chusclan)",
    "HC de Beaune": "Hautes Côtes de Beaune rouge",
    "Moulin à Vent": "Moulin à Vent",
    "Mâcon": "Macon",
    "Gewurztraminer": "Gewurztraminer",
    "Arbois Chardonnay": "Arbois Chardonnay",
    "Chablis": "Chablis",
    "Saint Joseph": "Saint Joseph Rouge",
}
BIB = "BIB 10 L"
BOUT = "Bouteille bouchée 75 cl"
ORDRE_COND = [BOUT, BIB]
VERRE, PICHET = "Verre", "Pichet seul"


def conditionnements():
    src = {b["nom_canonique"]: b for b in
           json.load(open(CONSO, encoding="utf-8"))["boissons"]}
    out = {}
    for vin, canon in VIN_SOURCE.items():
        unite = str(src[canon]["unite_achat"]).strip()
        out[vin] = BIB if unite.upper().startswith("BIB") else BOUT
        if out[vin] == BOUT:
            assert "75" in unite, (vin, unite)
    assert set(out) == set(TASTE.values()), "mapping conditionnement incomplet"
    return out


def formats():
    """Libelle caisse -> (format de service, volume unitaire en cl), lus dans
    itemsCaisse.json. Tous les libelles du mapping doivent y figurer."""
    src = {}
    for it in json.load(open(ITEMS, encoding="utf-8"))["items"]:
        nom = it.get("produit")
        if nom in TASTE and it.get("format_service"):
            src[nom] = (str(it["format_service"]), float(it["volume_unitaire_cl"]))
    manquants = sorted(set(TASTE) - set(src))
    assert not manquants, f"format de service absent d'itemsCaisse.json : {manquants}"
    return src


COND = conditionnements()
FORMAT = formats()
# Un libelle est un pichet si son format de service en est un : la lecture ne
# repose pas sur le libelle, parfois tronque ou mal capitalise
# (« PiCHET TROUSSEAU »), mais sur le format porte par l'article de la carte.
EST_PICHET = {lib: FORMAT[lib][0].lower().startswith("pichet") for lib in TASTE}


def est_vente_bouteille(lib, ref):
    if lib not in VENTE_BOUTEILLE:
        return False
    refs = VENTE_BOUTEILLE[lib]
    return refs is None or str(ref) in refs


def fmt_n(n):
    return f"{n:,}".replace(",", " ")


def fmt_l(x):
    return f"{x:.2f}".replace(".", ",") + " L"


def lire():
    """Retourne (lignes, notes_par_exo, zero, autres, retirees)."""
    lignes, notes_par_exo, zero = [], collections.defaultdict(set), []
    autres = collections.defaultdict(set)
    retirees = set()
    for exo, fn in C.items():
        sh = xlrd.open_workbook(fn).sheet_by_index(0)
        for r in range(1, sh.nrows):
            date, note = str(sh.cell_value(r, 0))[:10], str(sh.cell_value(r, 2))
            notes_par_exo[exo].add((date, note))
            lib = str(sh.cell_value(r, 10)).strip()
            ref = str(sh.cell_value(r, 9))
            vin = TASTE.get(lib)
            try:
                qte = float(sh.cell_value(r, 11))
            except ValueError:
                qte = 0.0
            if qte > 0 and lib in AUTRE_FORMAT:
                autres[(exo, date, note)].add(AUTRE_FORMAT[lib])
            if not vin or qte <= 0:
                continue
            if est_vente_bouteille(lib, ref):
                retirees.add((exo, date, note, vin))
                continue
            lignes.append((exo, date, note, vin, EST_PICHET[lib]))
            try:
                pu = float(sh.cell_value(r, 13))
                tot = float(sh.cell_value(r, 16))
            except ValueError:
                pu = tot = -1.0
            if pu == 0.0 and tot == 0.0:
                zero.append((exo, date, note, lib, vin, qte, FORMAT[lib][1]))
    return lignes, notes_par_exo, zero, autres, retirees


def classer(lignes):
    """Degustation = couple distinct (exo, date, note, vin).

    « Pichet seul » : sur cette note, ce vin nomme n'apparait, parmi les libelles
    retenus par le decompte, que sous des libelles de pichet. Le mecanisme decrit
    par le service, qui complete un verre a hauteur du solde de la dose vendue,
    n'y a alors aucun support."""
    a_un_verre = collections.defaultdict(bool)
    for (exo, date, note, vin, est_pichet) in lignes:
        cle = (exo, date, note, vin)
        a_un_verre[cle] = a_un_verre[cle] or (not est_pichet)
    return {cle: (VERRE if v else PICHET) for cle, v in a_un_verre.items()}


def litres(n):
    return round(n * DOSE_DEG / 100.0, 2)


def ecrire(deg, notes_par_exo, zero, autres, retirees, n_lignes, n_lignes_vin):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    white = Font(bold=True, color="FFFFFF")
    bold = Font(bold=True)
    head = PatternFill("solid", fgColor="0F766E")
    head2 = PatternFill("solid", fgColor="B45309")
    sub = PatternFill("solid", fgColor="E6F4F1")
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

    par = collections.Counter()
    par_vin = collections.Counter()
    par_cond = collections.Counter()
    par_exo_cond = collections.Counter()
    for (exo, _d, _n, vin), cat in deg.items():
        par[(exo, vin, cat)] += 1
        par_vin[(vin, cat)] += 1
        par_cond[(COND[vin], cat)] += 1
        par_exo_cond[(exo, COND[vin], cat)] += 1
    total_vin = collections.Counter()
    for (vin, _c), n in par_vin.items():
        total_vin[vin] += n
    vins = [v for v, _ in total_vin.most_common()]
    notes_deg = {(e, d, n) for (e, d, n, _v) in deg}

    # ---- Feuille 1 : par exercice, par vin -------------------------------
    ws = wb.active
    ws.title = "Verre ou pichet"
    titre(ws, "Où la larme pourrait-elle s’imputer ? Le décompte partagé selon la forme du service",
          "Le mécanisme décrit par le service (réponse du 04/09/2026, p. 64) suppose un verre vendu "
          "dont le remplissage serait complété. « Pichet seul » désigne les notes où le vin nommé "
          "n’apparaît que sous forme de pichet, contenant pré-mesuré de 50 cl : il n’y a alors aucun "
          "verre vendu à compléter. Une dégustation = un couple distinct note x vin nommé, 2 cl. "
          "Les ventes de bouteille entière sont retirées, voir la feuille « Bouteilles retirées ».")
    cols = ["Exercice", "Vin nommé", "Conditionnement d’achat",
            "Un verre du vin figure sur la note : dégustations", "Volume",
            "Le vin n’y figure qu’au pichet : dégustations", "Volume",
            "Total : dégustations", "Total : litres"]
    ncol = len(cols)
    hrow = ws.max_row + 1
    entete(ws, cols, hrow)

    def styler(r, fill=None, gras=False):
        for c in range(1, ncol + 1):
            cell = ws.cell(row=r, column=c)
            cell.border = bd
            if c > 3:
                cell.alignment = right
            if c in (5, 7, 9):
                cell.number_format = '#,##0.00 "L"'
            if fill is not None:
                cell.fill = fill
            if gras:
                cell.font = bold

    for exo in EXOS:
        for cond in ORDRE_COND:
            for vin in [v for v in vins if COND[v] == cond]:
                nv, np_ = par[(exo, vin, VERRE)], par[(exo, vin, PICHET)]
                if nv + np_ == 0:
                    continue
                ws.append([LIB_EXO[exo], vin, cond, nv, litres(nv), np_, litres(np_),
                           nv + np_, litres(nv + np_)])
                styler(ws.max_row)
            nv = par_exo_cond[(exo, cond, VERRE)]
            np_ = par_exo_cond[(exo, cond, PICHET)]
            if nv + np_ == 0:
                continue
            ws.append([LIB_EXO[exo], f"Sous-total {cond}", cond, nv, litres(nv),
                       np_, litres(np_), nv + np_, litres(nv + np_)])
            styler(ws.max_row, fill=sub, gras=True)

    tv = sum(par_exo_cond[(e, c, VERRE)] for e in EXOS for c in ORDRE_COND)
    tp = sum(par_exo_cond[(e, c, PICHET)] for e in EXOS for c in ORDRE_COND)
    ws.append(["Cumul 3 exercices", "TOTAL", "Les douze vins nommés", tv, litres(tv),
               tp, litres(tp), tv + tp, litres(tv + tp)])
    styler(ws.max_row, fill=sub, gras=True)
    for i, w in enumerate([22, 30, 24, 16, 12, 16, 12, 14, 12], 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = ws.cell(row=hrow + 1, column=4)

    # ---- Feuille 2 : cumul par vin ---------------------------------------
    ws2 = wb.create_sheet("Cumul par vin")
    titre(ws2, "Les trois exercices cumulés, vin par vin",
          "Les deux vins achetés en BIB de 10 L (Aligoté, Chusclan) sont retirés de la demande : "
          "l’abattement « vins au BIB » de 198 L du service porte déjà sur ce périmètre.")
    cols2 = ["Vin nommé", "Conditionnement d’achat",
             "Un verre du vin figure sur la note : dégustations", "Volume",
             "Le vin n’y figure qu’au pichet : dégustations", "Volume",
             "Total : dégustations", "Total : litres"]
    n2 = len(cols2)
    h2 = ws2.max_row + 1
    entete(ws2, cols2, h2)

    def styler2(r, fill=None, gras=False):
        for c in range(1, n2 + 1):
            cell = ws2.cell(row=r, column=c)
            cell.border = bd
            if c > 2:
                cell.alignment = right
            if c in (4, 6, 8):
                cell.number_format = '#,##0.00 "L"'
            if fill is not None:
                cell.fill = fill
            if gras:
                cell.font = bold

    for cond in ORDRE_COND:
        for vin in [v for v in vins if COND[v] == cond]:
            nv, np_ = par_vin[(vin, VERRE)], par_vin[(vin, PICHET)]
            ws2.append([vin, cond, nv, litres(nv), np_, litres(np_),
                        nv + np_, litres(nv + np_)])
            styler2(ws2.max_row)
        nv, np_ = par_cond[(cond, VERRE)], par_cond[(cond, PICHET)]
        lib = ("Sous-total bouteilles bouchées (volume demandé)" if cond == BOUT
               else "Sous-total BIB de 10 L (retiré de la demande)")
        ws2.append([lib, cond, nv, litres(nv), np_, litres(np_),
                    nv + np_, litres(nv + np_)])
        styler2(ws2.max_row, fill=sub, gras=True)
    ws2.append(["TOTAL", "Les douze vins nommés", tv, litres(tv), tp, litres(tp),
                tv + tp, litres(tv + tp)])
    styler2(ws2.max_row, fill=sub, gras=True)
    ws2.append([])
    nvb, npb = par_cond[(BOUT, VERRE)], par_cond[(BOUT, PICHET)]
    n_strict = sum(1 for (e, d, n, v), c in deg.items()
                   if c == PICHET and COND[v] == BOUT and v in autres.get((e, d, n), ()))
    for lab, val in [
        ("Volume demandé (vins en bouteille bouchée)",
         f"{fmt_n(nvb + npb)} dégustations, soit {fmt_l(litres(nvb + npb))}"),
        ("dont notes où le vin nommé n’est vendu qu’au pichet de 50 cl",
         f"{fmt_n(npb)} dégustations, soit {fmt_l(litres(npb))}"),
        ("dont notes comportant un verre de ce vin",
         f"{fmt_n(nvb)} dégustations, soit {fmt_l(litres(nvb))}"),
        ("Contrôle de la partition",
         f"{n_strict} de ces notes « pichet seul » portent, sous un libellé de caisse absent du "
         f"décompte, un autre format du même vin. Une lecture plus stricte les écarterait et "
         f"ramènerait la part « pichet seul » à {fmt_n(npb - n_strict)} dégustations, soit "
         f"{fmt_l(litres(npb - n_strict))}. L’écart ne change pas le volume demandé, qui reste "
         "entier : il ne déplace que la frontière entre la part couverte par l’argument du service "
         "et celle qui y échappe."),
        ("Portée du mécanisme décrit par le service p. 64",
         "Il suppose un verre vendu dont le remplissage est complété « à hauteur du solde de la "
         "dose vendue », et il place la dégustation avant ce remplissage. Sur les notes au pichet "
         "seul, aucun verre du vin nommé n’est vendu, et le pichet est un contenant pré-mesuré de "
         "50 cl : proposition de rectification p. 36, 41 et 42 ; réponse du 04/09/2026 p. 80, "
         "« les contenants pour ces volumes sont normés dans le commerce », et p. 92, « sur-dose "
         "sur des bouteilles de 75 cl et pichet de 50 cl => impossible »."),
    ]:
        ws2.append([lab, val])
        ws2.cell(row=ws2.max_row, column=2).alignment = Alignment(vertical="top",
                                                                  wrap_text=True)
    for i, w in enumerate([46, 40, 16, 12, 16, 12, 14, 12], 1):
        ws2.column_dimensions[get_column_letter(i)].width = w

    # ---- Feuille 3 : bouteilles retirees ----------------------------------
    ws6 = wb.create_sheet("Bouteilles retirées")
    titre(ws6, "Les ventes de bouteille entière retirées du décompte",
          "La règle de comptage exclut les bouteilles. Deux libellés tronqués de la caisse "
          "désignent pourtant une bouteille entière, au prix de la colonne « bouteille » de la "
          "carte. Ils sont retirés, exercice par exercice.")
    entete(ws6, ["Libellé de caisse", "Référence", "Vin nommé", "Prix unitaires relevés",
                 "Motif du retrait"], ws6.max_row + 1, fill=head2)
    for lib, refs, prix, motif in [
        ("Arbois Chardonnay Le", "2019, toutes lignes", "24,90 € puis 29,00 €",
         "Prix de la colonne « bouteille » de la carte. La proposition de rectification range "
         "elle-même le Chardonnay parmi les « ventes de bouteilles spécifiques » (p. 36)."),
        ("Beaujolais Moulin à", "1831 seulement", "29,00 € puis 38,00 €",
         "Même libellé tronqué que le verre, mais référence et prix distincts : la référence 1832 "
         "du même libellé est le verre, vendu 5,80 € puis 7,60 €."),
    ]:
        ws6.append([lib, refs, TASTE[lib], prix, motif])
        for c in range(1, 6):
            ws6.cell(row=ws6.max_row, column=c).border = bd
            ws6.cell(row=ws6.max_row, column=c).alignment = Alignment(vertical="top",
                                                                      wrap_text=True)
    ws6.append([])
    entete(ws6, ["Exercice", "Dégustations retirées", "Volume", "", ""],
           ws6.max_row + 1, fill=head2)
    retire_exo = collections.Counter()
    for (e, _d, _n, _v) in retirees:
        retire_exo[e] += 1
    for e in EXOS:
        ws6.append([LIB_EXO[e], retire_exo[e], litres(retire_exo[e]), "", ""])
        for c in range(1, 4):
            ws6.cell(row=ws6.max_row, column=c).border = bd
            if c == 3:
                ws6.cell(row=ws6.max_row, column=c).number_format = '#,##0.00 "L"'
    ws6.append(["Cumul 3 exercices", len(retirees), litres(len(retirees)), "", ""])
    for c in range(1, 4):
        ws6.cell(row=ws6.max_row, column=c).border = bd
        ws6.cell(row=ws6.max_row, column=c).font = bold
        ws6.cell(row=ws6.max_row, column=c).fill = sub
        if c == 3:
            ws6.cell(row=ws6.max_row, column=c).number_format = '#,##0.00 "L"'
    for i, w in enumerate([24, 20, 20, 22, 70], 1):
        ws6.column_dimensions[get_column_letter(i)].width = w

    # ---- Feuille 4 : contenances -----------------------------------------
    ws3 = wb.create_sheet("Contenances")
    titre(ws3, "Les vingt-sept libellés de caisse et leur contenance",
          "Format de service et volume unitaire lus dans src/data/calculsBoissons/itemsCaisse.json, "
          "renseignés d’après la carte des vins et boissons. Le service retient les mêmes volumes "
          "dans sa méthode : verre 15 cl, pichet 50 cl, pichet ou bouteille 75 cl "
          "(proposition de rectification p. 36, 41 et 42).")
    entete(ws3, ["Libellé de caisse", "Vin nommé", "Format de service",
                 "Volume unitaire", "Forme de service"], ws3.max_row + 1)
    for lib in sorted(TASTE, key=lambda x: (EST_PICHET[x], TASTE[x], x)):
        f, v = FORMAT[lib]
        ws3.append([lib, TASTE[lib], f, f"{v:.0f} cl",
                    "Pichet" if EST_PICHET[lib] else "Verre"])
        for c in range(1, 6):
            ws3.cell(row=ws3.max_row, column=c).border = bd
    for i, w in enumerate([26, 22, 18, 14, 18], 1):
        ws3.column_dimensions[get_column_letter(i)].width = w

    # ---- Feuille 5 : assiette des notes ----------------------------------
    ws4 = wb.create_sheet("Assiette des notes")
    titre(ws4, "Combien de notes le décompte concerne-t-il ?",
          "Le service objecte (p. 64) que « tous les clients (et donc toutes les notes) ne "
          "consomment pas tous du vin ». Le décompte ne suppose rien : il ne retient que les notes "
          "portant effectivement une ligne de vin nommé au verre ou au pichet. Le comptage "
          "ci-dessous est celui d’origine, avant le retrait des ventes de bouteille entière.")
    entete(ws4, ["Exercice", "Notes distinctes, tous articles confondus",
                 "Notes portant un vin nommé au verre ou au pichet",
                 "Part des notes retenues", "Dégustations comptées"],
           ws4.max_row + 1, fill=head2)
    notes_origine = notes_deg | {(e, d, n) for (e, d, n, _v) in retirees}
    deg_origine = set(deg) | retirees
    tot_notes = tot_ret = 0
    for exo in EXOS:
        n_tot = len(notes_par_exo[exo])
        n_ret = len({(d, n) for (e, d, n) in notes_origine if e == exo})
        n_deg = sum(1 for (e, _d, _n, _v) in deg_origine if e == exo)
        tot_notes += n_tot
        tot_ret += n_ret
        ws4.append([LIB_EXO[exo], n_tot, n_ret, n_ret / n_tot, n_deg])
        for c in range(1, 6):
            cell = ws4.cell(row=ws4.max_row, column=c)
            cell.border = bd
            if c > 1:
                cell.alignment = right
            if c == 4:
                cell.number_format = "0,0 %"
    ws4.append(["Cumul 3 exercices", tot_notes, tot_ret, tot_ret / tot_notes,
                len(deg_origine)])
    for c in range(1, 6):
        cell = ws4.cell(row=ws4.max_row, column=c)
        cell.border = bd
        cell.font = bold
        cell.fill = sub
        if c > 1:
            cell.alignment = right
        if c == 4:
            cell.number_format = "0,0 %"
    ws4.append([])
    ws4.append(["Lignes lues dans les annexes C1, C2 et C3", n_lignes])
    ws4.append(["dont lignes de vin nommé au verre ou au pichet, quantité positive, "
                "hors ventes de bouteille entière", n_lignes_vin])
    for i, w in enumerate([44, 32, 34, 18, 20], 1):
        ws4.column_dimensions[get_column_letter(i)].width = w

    # ---- Feuille 6 : lignes a prix zero ----------------------------------
    ws5 = wb.create_sheet("Vin nommé à prix zéro")
    titre(ws5, "Les lignes de vin nommé enregistrées à prix nul",
          "Vérification : une dégustation de 2 cl ne laisse aucune trace en caisse. Le service "
          "l’écrit lui-même pour les offerts, p. 72 : « Les données de caisse, aux dires des "
          "dirigeants, ne les gèrent pas. »")
    entete(ws5, ["Exercice", "Date", "N° de note", "Libellé", "Vin nommé",
                 "Quantité", "Volume"], ws5.max_row + 1, fill=head2)
    vol_zero = 0.0
    for (exo, date, note, lib, vin, qte, vcl) in sorted(zero):
        v = qte * vcl / 100.0
        vol_zero += v
        ws5.append([LIB_EXO[exo], date, note, lib, vin, qte, round(v, 2)])
        for c in range(1, 8):
            cell = ws5.cell(row=ws5.max_row, column=c)
            cell.border = bd
            if c >= 6:
                cell.alignment = right
            if c == 7:
                cell.number_format = '#,##0.00 "L"'
    ws5.append(["TOTAL", "", "", f"{len(zero)} ligne(s)", "",
                sum(z[5] for z in zero), round(vol_zero, 2)])
    for c in range(1, 8):
        cell = ws5.cell(row=ws5.max_row, column=c)
        cell.border = bd
        cell.font = bold
        cell.fill = sub
        if c == 7:
            cell.number_format = '#,##0.00 "L"'
    ws5.append([])
    ws5.append(["Lecture",
                "Ces lignes sont des verres et des pichets entiers enregistrés à prix nul, "
                "et non des larmes de 2 cl."])
    ws5.cell(row=ws5.max_row, column=2).alignment = Alignment(vertical="top", wrap_text=True)
    for i, w in enumerate([22, 12, 12, 24, 20, 10, 12], 1):
        ws5.column_dimensions[get_column_letter(i)].width = w

    os.makedirs(PIECES, exist_ok=True)
    wb.save(OUT)


if __name__ == "__main__":
    LIGNES_VIN, NOTES, ZERO, AUTRES, RETIREES = lire()
    N_LIGNES = sum(xlrd.open_workbook(fn).sheet_by_index(0).nrows - 1
                   for fn in C.values())
    DEG = classer(LIGNES_VIN)
    cat = collections.Counter(DEG.values())
    nb_bout = sum(1 for (_e, _d, _n, v) in DEG if COND[v] == BOUT)
    nb_bout_p = sum(1 for k, c in DEG.items() if COND[k[3]] == BOUT and c == PICHET)
    print(f"lignes de caisse lues        : {N_LIGNES}")
    print(f"lignes de vin nomme retenues : {len(LIGNES_VIN)}")
    print(f"ventes de bouteille retirees : {len(RETIREES)} soit {litres(len(RETIREES))} L")
    print(f"degustations                 : {len(DEG)} soit {litres(len(DEG))} L")
    print(f"  dont verre                 : {cat[VERRE]} soit {litres(cat[VERRE])} L")
    print(f"  dont pichet seul           : {cat[PICHET]} soit {litres(cat[PICHET])} L")
    print(f"bouteilles bouchees          : {nb_bout} soit {litres(nb_bout)} L")
    print(f"  dont pichet seul           : {nb_bout_p} soit {litres(nb_bout_p)} L")
    print(f"lignes de vin nomme a 0 EUR  : {len(ZERO)}")
    print(f"notes distinctes 3 exercices : {sum(len(s) for s in NOTES.values())}")
    ecrire(DEG, NOTES, ZERO, AUTRES, RETIREES, N_LIGNES, len(LIGNES_VIN))
    print("ecrit :", OUT)
