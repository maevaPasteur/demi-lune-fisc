#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
R1-consequences-financieres.xlsx

Recapitulatif, exercice par exercice, des consequences financieres notifiees par la
proposition de rectification du 18/05/2026 (SARL LA DEMI LUNE) et maintenues a
l'identique par la reponse de la DDFiP du Jura du 04/09/2026 (p. 94 et 95) :
rappels, profit sur le Tresor, majoration de 40 %, amende de 100 % et interets de retard.

REGLE : aucun montant saisi sans source. Chaque montant porte, dans l'onglet
« Sources », la page exacte de la proposition de rectification du 18/05/2026
d'ou il est repris. Aucun montant n'est recalcule ni estime : les seules valeurs
calculees sont des totaux (sommes des trois exercices), signalees comme telles.

Sortie : public/documents/pieces-reponse-1/R1-consequences-financieres.xlsx
"""

from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

RACINE = Path(__file__).resolve().parent.parent
SORTIE = RACINE / "public" / "documents" / "pieces-reponse-1" / "R1-consequences-financieres.xlsx"

EXOS = ["Exercice clos le 31/03/2023", "Exercice clos le 31/03/2024", "Exercice clos le 31/03/2025"]

# ---------------------------------------------------------------------------
# Donnees : chaque ligne = (poste, [ex1, ex2, ex3], texte applicable, source, moyen oppose)
# Les montants sont repris a l'identique de la proposition de rectification du
# 18/05/2026 (pages indiquees dans la colonne « Source »).
# ---------------------------------------------------------------------------

POSTES = [
    dict(
        poste="Discordance de chiffre d'affaires HT (base des rehaussements IS)",
        montants=[172813.45, 124009.56, 125076.16],
        texte="CGI, art. 38-1",
        source="Proposition de rectification du 18/05/2026, p. 53 et 55 (« Dont Minoration CA Hors Taxe »)",
        moyen="Base contestee dans son principe et dans son quantum : la reconstitution repose sur des doses figees, une perte nulle et une extrapolation cuisine par coefficient. Voir les pages du bloc « Reconstitution du chiffre d'affaires ».",
    ),
    dict(
        poste="Discordance de chiffre d'affaires TTC (assiette des distributions)",
        montants=[193234.55, 138863.57, 139727.76],
        texte="CGI, art. 109-1-1° et 110",
        source="Proposition de rectification du 18/05/2026, p. 58",
        moyen="Il n'y a de revenu distribue que s'il y a des recettes occultees etablies. L'assiette suit integralement le sort de la reconstitution contestee.",
    ),
    dict(
        poste="Rappel de TVA collectee (montant enonce dans le corps de la proposition)",
        montants=[20421.0, 14854.0, 14652.0],
        texte="CGI, art. 256, 269, 278 et 279-0 bis",
        source="Proposition de rectification du 18/05/2026, p. 54 et 56 (« TVA nette due en Euros »)",
        moyen="Le rappel n'a pas d'assiette propre : il est le decalque du chiffre d'affaires reconstitue. Pas de CA minore, pas de TVA rappelee.",
    ),
    dict(
        poste="Droits de TVA rappeles (montant des tableaux recapitulatifs)",
        montants=[20041.0, 14854.0, 14652.0],
        texte="LPF, art. L. 48",
        source="Proposition de rectification du 18/05/2026, p. 59 (ligne « Cascade a deduire ») et p. 63 (« Droits rappeles » / « Droits mis en recouvrement »)",
        moyen="Ecart de 380 EUR sur le premier exercice avec le montant enonce p. 54 et 56 (20 421 EUR). Les tableaux de liquidation retiennent 20 041 EUR ; le total TVA de la p. 65 (49 547 EUR) est etabli sur cette derniere valeur.",
    ),
    dict(
        poste="Profit sur le Tresor (reintegration au resultat)",
        montants=[20421.0, 14854.0, 14652.0],
        texte="LPF, art. L. 77 ; CGI, art. 38-2",
        source="Proposition de rectification du 18/05/2026, p. 56 (« II-2- Profit sur le tresor »)",
        moyen="Mecanisme strictement accessoire : il n'existe que par le rappel de TVA dont il procede. Le service l'admet lui-meme p. 94 de sa reponse du 04/09/2026.",
    ),
    dict(
        poste="Cascade deduite du resultat (art. L. 77 du LPF)",
        montants=[-20041.0, -14854.0, -14652.0],
        texte="LPF, art. L. 77",
        source="Proposition de rectification du 18/05/2026, p. 59 (ligne « Cascade a deduire »)",
        moyen="Deduction automatique, sauf renonciation expresse dans le delai de reponse. Elle suit egalement le sort du rappel de TVA.",
    ),
    dict(
        poste="Impot sur les societes supplementaire (droits)",
        montants=[42908.0, 27120.0, 27482.0],
        texte="CGI, art. 205 et 219",
        source="Proposition de rectification du 18/05/2026, p. 60 (« IS apres controle » moins « IS avant controle »)",
        moyen="Consequence arithmetique des rehaussements de produits et du profit sur le Tresor.",
    ),
    dict(
        poste="Majoration de 40 % pour manquement delibere (IS)",
        montants=[17163.0, 10848.0, 10993.0],
        texte="CGI, art. 1729, a ; LPF, art. L. 195 A et L. 80 D",
        source="Proposition de rectification du 18/05/2026, p. 61 et 62 (« Manquement delibere : 40 % (article 1729) »)",
        moyen="La preuve de l'element intentionnel incombe a l'administration (LPF, art. L. 195 A). La reponse du 04/09/2026 (p. 94 et 95) n'articule aucun fait, aucun exercice et aucun montant propres a la penalite et se borne a un renvoi global.",
    ),
    dict(
        poste="Majoration de 40 % pour manquement delibere (TVA)",
        montants=[8016.0, 5942.0, 5861.0],
        texte="CGI, art. 1729, a ; LPF, art. L. 195 A et L. 80 D",
        source="Proposition de rectification du 18/05/2026, p. 63, 64 et 65 (« Manquement delibere : 40 % (article 1729) ») ; total p. 65 : 19 819 EUR",
        moyen="Meme moyen. La majoration est en outre assise sur des droits eux-memes contestes.",
    ),
    dict(
        poste="Interets de retard (IS)",
        montants=[2918.0, 1193.0, 550.0],
        texte="CGI, art. 1727",
        source="Proposition de rectification du 18/05/2026, p. 60, 61 et 62 (34 / 22 / 10 mois ; taux 6,8 % / 4,4 % / 2 %)",
        moyen="Accessoire des rappels : ils suivent leur sort. Ils ne constituent pas une sanction et ne sont donc pas discutes pour eux-memes. Reserve : la colonne « Base » des trois tableaux (44 588 / 27 450 / 27 799 EUR) ne produit pas, au taux indique, le montant liquide ; celui-ci correspond au taux applique aux droits (42 908 / 27 120 / 27 482 EUR).",
    ),
    dict(
        poste="Interets de retard (TVA)",
        montants=[1483.0, 743.0, 381.0],
        texte="CGI, art. 1727",
        source="Proposition de rectification du 18/05/2026, p. 63, 64 et 65 (bases 20 041 / 14 854 / 14 652 EUR, 37 / 25 / 13 mois) ; total p. 65 : 2 607 EUR",
        moyen="Meme moyen. Le decompte du premier exercice est etabli sur la base de 20 041 EUR, et non sur les 20 421 EUR enonces p. 54.",
    ),
    dict(
        poste="Amende de 100 % sur distributions presumees",
        montants=[193234.55, 138863.57, 139727.76],
        texte="CGI, art. 1759 ; CGI, art. 117",
        source="Proposition de rectification du 18/05/2026, p. 58 (« la penalite prevue a l'article 1759 du C-G-I et dont le montant est fixe a 100 % des sommes versees ou distribuees »)",
        moyen="L'amende suppose que la societe « ne revele pas l'identite » des beneficiaires. Par courrier du 16 juin 2026, dont le service accuse reception p. 95 de sa reponse du 04/09/2026, Mme Ghislaine BEHEM et M. Thierry PASTEUR ont ete designes comme beneficiaires. La condition d'application n'est pas remplie.",
    ),
]

RECAP = [
    ("Droits IS", [42908.0, 27120.0, 27482.0], "Proposition, p. 60"),
    ("Droits TVA", [20041.0, 14854.0, 14652.0], "Proposition, p. 63 a 65 (total p. 65 : 49 547 EUR)"),
    ("Interets de retard IS + TVA", [2918.0 + 1483.0, 1193.0 + 743.0, 550.0 + 381.0], "Proposition, p. 60 a 65 (somme des deux impots)"),
    ("Majorations de 40 % IS + TVA", [17163.0 + 8016.0, 10848.0 + 5942.0, 10993.0 + 5861.0], "Proposition, p. 61 a 65 (somme des deux impots)"),
    ("Amende de 100 % (art. 1759 du CGI)", [193234.55, 138863.57, 139727.76], "Proposition, p. 58"),
]

RESERVES = [
    (
        "Ecart interne de 380 EUR sur le rappel de TVA du premier exercice",
        "Le corps de la proposition retient 20 421 EUR (p. 54 et 56, « TVA nette due en Euros ») ; les tableaux de liquidation retiennent 20 041 EUR (p. 59 « Cascade a deduire », p. 63 « Droits rappeles », « Droits eludes », « Droits penalisables » et base des interets de retard). Le total TVA de la p. 65 (49 547 EUR) est etabli a partir de 20 041 EUR, et la majoration de 8 016 EUR correspond a 40 % de 20 041 EUR. Les deux valeurs sont reproduites ici sans arbitrage.",
    ),
    (
        "Colonne « Base » des interets de retard a l'IS",
        "Les tableaux des p. 60, 61 et 62 indiquent des bases de 44 588, 27 450 et 27 799 EUR pour des taux de 6,8 %, 4,4 % et 2 %. Ces produits donneraient 3 032, 1 208 et 556 EUR. Les montants liquides sont de 2 918, 1 193 et 550 EUR, soit exactement les memes taux appliques aux droits (42 908, 27 120 et 27 482 EUR). Les majorations de 40 % (17 163, 10 848 et 10 993 EUR) sont egalement calculees sur ces droits. La colonne « Base » n'est donc l'assiette d'aucun des deux calculs : elle appelle une explication avant mise en recouvrement.",
    ),
    (
        "Neutralite du profit sur le Tresor sur la base IS",
        "Sur les trois exercices, le profit sur le Tresor reintegre et la cascade deduite au titre de l'article L. 77 du LPF portent sur le meme montant et s'annulent : le resultat fiscal rectifie (212 356, 127 685 et 129 704 EUR, p. 59) est egal au resultat declare augmente de la seule minoration de chiffre d'affaires HT (39 543 + 172 813 ; 3 675 + 124 010 ; 4 628 + 125 076). Le profit sur le Tresor n'a donc, dans ce dossier, aucune incidence nette autonome sur la base de l'impot sur les societes.",
    ),
    (
        "Aucun montant n'est recalcule",
        "Les seules valeurs calculees dans ce fichier sont des totaux (sommes des trois exercices) et les regroupements IS + TVA de l'onglet « Synthese ». Tous les autres montants sont recopies a l'identique de la proposition de rectification du 18/05/2026.",
    ),
    (
        "Perimetre",
        "Ce fichier ne porte que sur les consequences financieres notifiees a la SARL LA DEMI LUNE. Les propositions de rectifications personnelles annoncees p. 95 de la reponse du 04/09/2026 a l'encontre de Mme Ghislaine BEHEM et de M. Thierry PASTEUR ne sont pas chiffrees : elles n'avaient pas ete notifiees a la date d'etablissement du present recapitulatif.",
    ),
    (
        "Reponse de la DDFiP du Jura du 04/09/2026",
        "Le service maintient l'integralite de ces montants : « les chiffres d'affaires reconstitues n'ont pas ete impactes et demeurent les memes que ceux qui figuraient dans la proposition de rectifications » (p. 94 et 95), « Tous les rappels et rehaussements demeurant inchanges, le profit sur le tresor demeure egalement identique » (p. 94), « Il n'y a donc pas lieu que les penalites et amendes proposes au stade de la proposition de rectifications soient modifies d'une quelconque maniere » (p. 95), « les interets de retard demeurent egalement identiques » (p. 95).",
    ),
]

# ---------------------------------------------------------------------------
# Mise en forme
# ---------------------------------------------------------------------------

BLEU = PatternFill("solid", fgColor="1F3864")
GRIS = PatternFill("solid", fgColor="EDEDED")
OR = PatternFill("solid", fgColor="FFF2CC")
ROUGE = PatternFill("solid", fgColor="FCE4E4")
BLANC_GRAS = Font(bold=True, color="FFFFFF", size=11)
GRAS = Font(bold=True, size=11)
FIN = Side(style="thin", color="BFBFBF")
BORDURE = Border(left=FIN, right=FIN, top=FIN, bottom=FIN)
EURO = '# ##0.00 " €";-# ##0.00 " €"'


def entete(ws, ligne, valeurs, largeurs=None):
    for i, v in enumerate(valeurs, start=1):
        c = ws.cell(row=ligne, column=i, value=v)
        c.fill = BLEU
        c.font = BLANC_GRAS
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = BORDURE
    if largeurs:
        for i, l in enumerate(largeurs, start=1):
            ws.column_dimensions[get_column_letter(i)].width = l
    ws.row_dimensions[ligne].height = 32


def titre(ws, texte, sous_titre):
    ws["A1"] = texte
    ws["A1"].font = Font(bold=True, size=14, color="1F3864")
    ws["A2"] = sous_titre
    ws["A2"].font = Font(italic=True, size=9, color="595959")
    ws["A2"].alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[2].height = 30


def construire():
    wb = Workbook()

    # ---- Onglet 1 : Synthese ------------------------------------------------
    ws = wb.active
    ws.title = "Synthèse"
    titre(
        ws,
        "SARL LA DEMI LUNE : conséquences financières notifiées et maintenues",
        "Montants repris de la proposition de rectification du 18/05/2026, maintenus à l’identique par la réponse de la DDFiP du Jura du 04/09/2026 (p. 94 et 95). "
        "Chaque montant est sourcé, page par page, dans l’onglet « Sources et réserves ».",
    )
    entete(ws, 4, ["Poste", *EXOS, "Total 3 exercices", "Source"], [40, 20, 20, 20, 20, 52])
    r = 5
    for lib, m, src in RECAP:
        ws.cell(row=r, column=1, value=lib).font = GRAS
        for j, v in enumerate(m):
            c = ws.cell(row=r, column=2 + j, value=v)
            c.number_format = EURO
        t = ws.cell(row=r, column=5, value=sum(m))
        t.number_format = EURO
        t.font = GRAS
        t.fill = GRIS
        s = ws.cell(row=r, column=6, value=src)
        s.alignment = Alignment(wrap_text=True, vertical="top")
        s.font = Font(size=8, color="595959")
        for col in range(1, 7):
            ws.cell(row=r, column=col).border = BORDURE
        if lib.startswith("Amende"):
            for col in range(1, 6):
                ws.cell(row=r, column=col).fill = ROUGE
        r += 1

    ws.cell(row=r, column=1, value="TOTAL").font = GRAS
    for j in range(3):
        c = ws.cell(row=r, column=2 + j, value=sum(m[j] for _, m, _ in RECAP))
        c.number_format = EURO
        c.font = GRAS
    tot = ws.cell(row=r, column=5, value=sum(sum(m) for _, m, _ in RECAP))
    tot.number_format = EURO
    tot.font = GRAS
    ws.cell(row=r, column=6, value="Somme calculée des lignes ci-dessus").font = Font(size=8, italic=True, color="595959")
    for col in range(1, 7):
        ws.cell(row=r, column=col).fill = OR
        ws.cell(row=r, column=col).border = BORDURE
    ligne_total = r

    part = sum(sum(m) for lib, m, _ in RECAP if lib.startswith("Amende")) / sum(sum(m) for _, m, _ in RECAP)
    r += 2
    ws.cell(
        row=r,
        column=1,
        value="L’amende de 100 %% de l’article 1759 du CGI représente %.1f %% du total notifié." % (part * 100),
    ).font = Font(bold=True, size=11, color="C00000")

    # ---- Onglet 2 : Détail par poste ---------------------------------------
    ws2 = wb.create_sheet("Détail par poste")
    titre(
        ws2,
        "Détail poste par poste : montant, texte applicable et moyen opposé",
        "Les montants sont recopiés à l’identique de la proposition de rectification du 18/05/2026 ; "
        "aucun n’est recalculé. La colonne « Total » est une somme.",
    )
    entete(
        ws2,
        4,
        ["Poste", *EXOS, "Total 3 exercices", "Texte applicable", "Source (proposition du 18/05/2026)", "Moyen opposé"],
        [40, 18, 18, 18, 18, 30, 46, 62],
    )
    r = 5
    for p in POSTES:
        ws2.cell(row=r, column=1, value=p["poste"]).font = GRAS
        ws2.cell(row=r, column=1).alignment = Alignment(wrap_text=True, vertical="top")
        for j, v in enumerate(p["montants"]):
            c = ws2.cell(row=r, column=2 + j, value=v)
            c.number_format = EURO
        t = ws2.cell(row=r, column=5, value=sum(p["montants"]))
        t.number_format = EURO
        t.font = GRAS
        t.fill = GRIS
        for col, key in ((6, "texte"), (7, "source"), (8, "moyen")):
            c = ws2.cell(row=r, column=col, value=p[key])
            c.alignment = Alignment(wrap_text=True, vertical="top")
            c.font = Font(size=9)
        for col in range(1, 9):
            ws2.cell(row=r, column=col).border = BORDURE
        if p["poste"].startswith("Amende"):
            for col in range(1, 6):
                ws2.cell(row=r, column=col).fill = ROUGE
        ws2.row_dimensions[r].height = 78
        r += 1

    # ---- Onglet 3 : Sources et réserves ------------------------------------
    ws3 = wb.create_sheet("Sources et réserves")
    titre(
        ws3,
        "Sources de chaque montant et réserves de lecture",
        "Aucun montant de ce fichier n’est estimé. Les réserves ci-dessous signalent les points où la proposition "
        "de rectification du 18/05/2026 n’est pas homogène avec elle-même.",
    )
    entete(ws3, 4, ["Point", "Contenu"], [46, 120])
    r = 5
    for t_, c_ in RESERVES:
        ws3.cell(row=r, column=1, value=t_).font = GRAS
        ws3.cell(row=r, column=1).alignment = Alignment(wrap_text=True, vertical="top")
        cc = ws3.cell(row=r, column=2, value=c_)
        cc.alignment = Alignment(wrap_text=True, vertical="top")
        cc.font = Font(size=9)
        for col in (1, 2):
            ws3.cell(row=r, column=col).border = BORDURE
        ws3.row_dimensions[r].height = 96
        r += 1

    r += 1
    ws3.cell(row=r, column=1, value="Document source").font = GRAS
    ws3.cell(
        row=r,
        column=2,
        value="Proposition de rectification n° 3924 du 18/05/2026, SARL LA DEMI LUNE, pages 53 à 66 "
        "(fichier du dossier : public/documents/rapports-des-finances-publiques/Proposition_1_Lettre.pdf). "
        "Réponse aux observations du contribuable de la DDFiP du Jura du 04/09/2026, pages 94 et 95.",
    ).alignment = Alignment(wrap_text=True, vertical="top")
    ws3.row_dimensions[r].height = 60

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    wb.save(SORTIE)
    print("Écrit :", SORTIE)
    print("Total notifié (3 exercices) :", round(sum(sum(m) for _, m, _ in RECAP), 2), "€")
    print("Part de l’amende de 100 %% : %.1f %%" % (part * 100))
    print("Ligne de total :", ligne_total)


if __name__ == "__main__":
    construire()
