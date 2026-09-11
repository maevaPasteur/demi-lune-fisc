#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REPONSE 1 - Relevé, page par page, de ce que la réponse du 04/09/2026 examine
et de ce qu'elle n'examine pas, sur le bloc « reconstitution du chiffre d'affaires »
(partie L, onze points numérotés, puis parties M à T : pages 59 à 92).

Chaque ligne est une rubrique « Réponse du service » du courrier, avec :
  - sa page dans le courrier du 04/09/2026 ;
  - le poste du bilan matière qu'elle concerne ;
  - la phrase de conclusion, telle qu'elle figure dans le courrier ;
  - la NATURE des chiffres que le service oppose, classée en quatre catégories :
      * "aucun chiffre"            : le service ne produit aucun nombre sur le poste ;
      * "abattement de sa méthode" : le service oppose les taux qu'il applique déjà
                                     dans sa propre reconstitution (15 %, 5 % + 5 % + 5 %,
                                     repères D/E/G/Q), pour soutenir un double emploi ;
      * "calcul de cohérence"      : le service compare le volume disponible aux
                                     quantités de caisse pour montrer une impossibilité ;
      * "concession"               : le service admet que le grief est sans effet sur la base ;
  - et surtout : le service oppose-t-il un VOLUME ALTERNATIF au poste, c'est-à-dire
    dit-il combien de litres sont réellement partis dans ce poste ? (colonne « oui/non »)

Aucun chiffre n'est calculé ici : le fichier est un relevé de lecture du courrier,
chaque ligne portant sa page. Il est produit pour être vérifié page par page.

Exécution : python3 scripts/reponse1-releve-motivation.py
"""
import os

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SORTIE = os.path.join(ROOT, "public/documents/pieces-reponse-1/R1-releve-reponses-service.xlsx")

# (repère, page(s), poste du bilan matière, nature des chiffres opposés,
#  volume alternatif opposé ?, conclusion telle qu'elle figure au courrier)
LIGNES = [
    ("L", "59", "Chapeau du bloc : aucun poste",
     "aucun chiffre", "sans objet",
     "Aucune rubrique « Réponse du service » : le service reproduit l'encadré des 10 622 L "
     "et annonce onze points."),
    ("1", "60", "Sur-versement au verre",
     "aucun chiffre", "non",
     "« le service ne voit aucune raison de modifier sa reconstitution qui demeurera dans ses "
     "montants les mêmes que ceux figurant dans la proposition de rectifications »"),
    ("2", "61", "Freinte technique de la bière",
     "abattement de sa méthode", "non",
     "« le service retient donc en fait, un taux total de 30 % sur la bière » (15 % dans la "
     "méthode + 15 % en fin de méthode), puis « aucune raison de modifier sa reconstitution »"),
    ("3", "62 et 63", "Crémant non vendu",
     "calcul de cohérence", "non",
     "« 93,20 litres sur les 206,25 litres disponibles seraient jetés, soit 45,18 % de pertes » : "
     "le service oppose une impossibilité, il ne dit pas quel volume a été jeté."),
    ("4", "64", "Dégustation offerte",
     "abattement de sa méthode", "non",
     "« le service a déjà retenu un taux offert/perte/consommation du personnel de 15 % » : "
     "198 L sur les BIB et environ 500 L sur les bouteilles, tirés de son propre abattement."),
    ("5", "65 à 68", "Alcool de cuisine",
     "calcul de cohérence", "non",
     "Tableaux « Volume consommé / Données de la caisse / Volume disponible » pour le Calvados, "
     "le vin jaune, le porto et le macvin : comparaison de volumes, aucun volume de cuisine retenu."),
    ("6", "68 à 70", "Alcool cuit dans les plats des menus",
     "abattement de sa méthode", "non",
     "Le service rappelle ce qu'il déduit déjà : Calvados 93 L, vin jaune 111 L, porto 15 L, "
     "macvin 240 L, BIB 796,43 L, crèmes 33,28 L (arrondis du courrier)."),
    ("7", "70 et 71", "Consommation du personnel",
     "abattement de sa méthode", "non",
     "« 5 % de ce volume correspondent donc à 83,84 litres » puis « 61,46 litres » : le service "
     "oppose le produit de son propre forfait, pas un relevé de consommation."),
    ("8", "71 à 73", "Offerts, pertes, personnel (les trois 5 %)",
     "abattement de sa méthode", "non",
     "« le service minore le montant du chiffre d'affaires TTC reconstitué à hauteur de "
     "35 133,26 € » par forfait et par exercice, opposé à nos 8 010 € d'offerts."),
    ("9", "74", "Volume disponible et variation de stock",
     "aucun chiffre", "non",
     "« La réponse se base sur un montant en euros. Or, la reconstitution ne s'est basée que des "
     "volumes en stocks. »"),
    ("10", "74 et 75", "Ventes sans achat",
     "concession", "sans objet",
     "« Dans la méthode de reconstitution, les ventes sans achats n'ont pas entraîné de chiffre "
     "d'affaires reconstitué. »"),
    ("11", "76", "Coefficient liquides vers solides",
     "aucun chiffre", "non",
     "« ce rapport liquides/solides provient directement des données de la caisse informatique "
     "qui reflète des données d'exploitation qui peuvent être considérées comme significatives »"),
    ("M", "76 et 77", "Le bilan matière lui-même (10 622 L)",
     "aucun chiffre", "non",
     "« tout au long des parties précédentes, le service s'est attaché à contredire chacun des "
     "arguments » : renvoi aux points précédents, aucun bilan matière opposé."),
    ("N", "78 à 82", "Sur-versement au verre (reprise)",
     "aucun chiffre", "non",
     "« Il n'y a donc pas lieu que le service modifie sa reconstitution qui demeurera dans ses "
     "montants les mêmes que ceux figurant dans la proposition de rectifications. »"),
    ("O", "82 et 83", "Freinte de la bière (reprise)",
     "abattement de sa méthode", "non",
     "« en cumulant les deux taux de sa méthode de reconstitution, le service avait déjà » "
     "retenu davantage : cumul de 15 % + 15 %."),
    ("P", "84 et 85", "Perte de crémant (reprise)",
     "calcul de cohérence", "non",
     "« Le service a déjà répondu à cette problématique dans la présente réponse en partie "
     "L- Reconstitution du chiffre d'affaires. »"),
    ("Q", "85 et 86", "Dégustation offerte (reprise)",
     "abattement de sa méthode", "non",
     "« le service a déjà répondu à cette question dans cette réponse en partie L- "
     "Reconstitution du chiffre d'affaires »"),
    ("R", "87 et 88", "Alcool de cuisine (reprise)",
     "calcul de cohérence", "non",
     "« le service va se limiter à rappeler ses conclusions pour les différents alcools des "
     "tableaux cités »"),
    ("S", "89", "Offerts, pertes, personnel (reprise)",
     "abattement de sa méthode", "non",
     "« le service va se limiter à résumer ses conclusions en la matière »"),
    ("T", "90 à 92", "Extrapolation cuisine",
     "aucun chiffre", "non",
     "« Il est normal que les rehaussements proposés correspondent à 75 % puisqu'il s'agit "
     "d'une conséquence directe du rapport. »"),
]

# Formules de non-modification relevées dans le courrier, page par page.
# « le service ne voit aucune raison de modifier sa reconstitution » : 14 occurrences.
PAGES_FORMULE_1 = [60, 61, 63, 64, 68, 70, 71, 73, 74, 75, 85, 86, 88, 89]
# « il n'y a donc pas lieu que le service modifie sa reconstitution » : 2 occurrences.
PAGES_FORMULE_2 = [77, 82]


def main():
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    blanc = Font(bold=True, color="FFFFFF")
    tete = PatternFill("solid", fgColor="0F766E")
    surligne = PatternFill("solid", fgColor="CCE7E2")
    trait = Side(style="thin", color="D8DEE4")
    bord = Border(left=trait, right=trait, top=trait, bottom=trait)
    haut = Alignment(vertical="top", wrap_text=True)

    ws = wb.active
    ws.title = "Releve"
    ws.append(["Ce que la reponse du 04/09/2026 examine, et ce qu'elle n'examine pas "
               "(bloc reconstitution, pages 59 a 92)"])
    ws["A1"].font = Font(bold=True, size=13)
    ws.append(["Une ligne par rubrique du courrier. La derniere colonne est la seule qui compte "
               "dans un bilan matiere : le service dit-il, pour ce poste, combien de litres sont "
               "reellement partis ? Chaque ligne porte sa page : le releve est verifiable."])
    ws["A2"].font = Font(italic=True, size=9, color="64748B")
    ws.append([])
    cols = ["Repere", "Page(s) du courrier", "Poste du bilan matiere",
            "Nature des chiffres opposes", "Volume alternatif oppose ?",
            "Conclusion telle qu'elle figure au courrier"]
    ws.append(cols)
    for c in range(1, len(cols) + 1):
        cell = ws.cell(row=4, column=c)
        cell.font, cell.fill, cell.border = blanc, tete, bord
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    for l in LIGNES:
        ws.append(list(l))
        r = ws.max_row
        for c in range(1, len(cols) + 1):
            ws.cell(row=r, column=c).border = bord
            ws.cell(row=r, column=c).alignment = haut
    n = len(LIGNES)
    nb_non = sum(1 for l in LIGNES if l[4] == "non")
    ws.append(["TOTAL", f"{n} rubriques", "",
               f"aucun chiffre : {sum(1 for l in LIGNES if l[3] == 'aucun chiffre')} / "
               f"abattement de sa methode : {sum(1 for l in LIGNES if l[3] == 'abattement de sa methode' or l[3] == 'abattement de sa méthode')} / "
               f"calcul de coherence : {sum(1 for l in LIGNES if l[3] == 'calcul de coherence' or l[3] == 'calcul de cohérence')} / "
               f"concession : {sum(1 for l in LIGNES if l[3] == 'concession')}",
               f"non : {nb_non} sur {n}", ""])
    r = ws.max_row
    for c in range(1, len(cols) + 1):
        ws.cell(row=r, column=c).font = Font(bold=True)
        ws.cell(row=r, column=c).fill = surligne
        ws.cell(row=r, column=c).border = bord
        ws.cell(row=r, column=c).alignment = haut
    for i, w in enumerate([10, 20, 34, 26, 22, 82], 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A5"

    ws2 = wb.create_sheet("Formules de non-modification")
    ws2.append(["Les conclusions de non-modification, page par page"])
    ws2["A1"].font = Font(bold=True, size=13)
    ws2.append([])
    ws2.append(["Formule relevee dans le courrier", "Nombre d'occurrences", "Pages"])
    for c in range(1, 4):
        cell = ws2.cell(row=3, column=c)
        cell.font, cell.fill, cell.border = blanc, tete, bord
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    for lib, pages in [
        ("« le service ne voit aucune raison de modifier sa reconstitution qui demeurera dans "
         "ses montants les memes que ceux figurant dans la proposition de rectifications »",
         PAGES_FORMULE_1),
        ("« il n'y a donc pas lieu que le service modifie sa reconstitution qui demeurera dans "
         "ses montants les memes que ceux figurant dans la proposition de rectifications »",
         PAGES_FORMULE_2),
    ]:
        ws2.append([lib, len(pages), ", ".join("p. %d" % p for p in pages)])
        r = ws2.max_row
        for c in range(1, 4):
            ws2.cell(row=r, column=c).border = bord
            ws2.cell(row=r, column=c).alignment = haut
    total = len(PAGES_FORMULE_1) + len(PAGES_FORMULE_2)
    ws2.append(["TOTAL", total, "pages 60 a 89"])
    r = ws2.max_row
    for c in range(1, 4):
        ws2.cell(row=r, column=c).font = Font(bold=True)
        ws2.cell(row=r, column=c).fill = surligne
        ws2.cell(row=r, column=c).border = bord
    for i, w in enumerate([96, 22, 60], 1):
        ws2.column_dimensions[get_column_letter(i)].width = w

    wb.save(SORTIE)
    print("écrit :", SORTIE)
    print(f"{n} rubriques relevées, {nb_non} sans volume alternatif opposé.")
    print(f"{total} conclusions de non-modification, pages 60 à 89.")


if __name__ == "__main__":
    main()
