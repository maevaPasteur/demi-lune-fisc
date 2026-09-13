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
  - et surtout : le service oppose-t-il un VOLUME MESURÉ au poste, c'est-à-dire
    dit-il, relevé à l'appui, combien de litres sont réellement partis dans ce poste ?
    (colonne « oui/non »)

Citer un volume et mesurer un volume sont deux choses distinctes, et le relevé les
sépare : le courrier cite bien des litres, 2 132,01 L au total, mais chacun d'eux est
le produit d'un taux forfaitaire du service (15 %, 5 %) ou d'une de ses propres
colonnes, et aucun n'est un relevé de ce qui est réellement parti dans le poste. Le
troisième bloc de l'onglet « Releve » en donne le détail, ligne à ligne, avec sa page.

Aucun chiffre n'est calculé ici : le fichier est un relevé de lecture du courrier,
chaque ligne portant sa page. Il est produit pour être vérifié page par page.

Exécution : python3 scripts/reponse1-releve-motivation.py
"""
import os

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SORTIE = os.path.join(ROOT, "public/documents/pieces-reponse-1/R1-releve-reponses-service.xlsx")

# (repère, page(s), poste du bilan matière, nature des chiffres opposés,
#  volume mesuré opposé ?, conclusion telle qu'elle figure au courrier)
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

# Repères qui ne comportent AUCUNE rubrique « Réponse du service » dans le courrier :
# ils comptent parmi les lignes du relevé, jamais au dénominateur des rubriques.
SANS_RUBRIQUE = {"L"}

# Les volumes que le courrier CITE, un à un, avec leur page et leur origine. Ils
# existent : le relevé ne soutient pas que le service n'écrit aucun litre. Il soutient
# qu'aucun de ces litres n'est un volume mesuré dans le poste auquel il est opposé.
VOLUMES_CITES = [
    ("198 L", "64", "Point 4, dégustation offerte",
     "Son taux de 15 % offert/perte/personnel appliqué aux BIB",
     "Produit d'un forfait de sa propre méthode, appliqué à un volume d'achat. Ne dit "
     "rien du nombre de dégustations réellement servies."),
    ("500 L", "64", "Point 4, dégustation offerte",
     "Le même taux de 15 % appliqué aux bouteilles",
     "« environ 500 litres » au courrier : chiffre arrondi par le service lui-même, et "
     "produit du même forfait."),
    ("93 L", "68 à 70", "Point 6, alcool cuit dans les plats des menus",
     "Repère D, Calvados déjà retranché par sa méthode",
     "Retranchement que le service opère déjà dans sa reconstitution : c'est son propre "
     "chiffre, repris pour soutenir un double emploi, non une mesure de l'alcool cuit."),
    ("111 L", "68 à 70", "Point 6, alcool cuit dans les plats des menus",
     "Repère E, vin jaune déjà retranché par sa méthode", "Idem."),
    ("15 L", "68 à 70", "Point 6, alcool cuit dans les plats des menus",
     "Repère G, porto déjà retranché par sa méthode", "Idem."),
    ("240 L", "68 à 70", "Point 6, alcool cuit dans les plats des menus",
     "Repère Q, macvin déjà retranché par sa méthode", "Idem."),
    ("796,43 L", "68 à 70", "Point 6, alcool cuit dans les plats des menus",
     "Volume unique des BIB porté par sa propre colonne",
     "Volume d'achat lu dans sa propre colonne, non un volume cuisiné."),
    ("33,28 L", "68 à 70", "Point 6, alcool cuit dans les plats des menus",
     "Crèmes, même colonne", "Idem."),
    ("83,84 L", "70 et 71", "Point 7, consommation du personnel",
     "5 % de son propre volume de référence",
     "« 5 % de ce volume correspondent donc à 83,84 litres » : le produit d'un forfait, "
     "non un relevé de ce que le personnel a consommé."),
    ("61,46 L", "70 et 71", "Point 7, consommation du personnel",
     "Le même forfait de 5 % sur l'autre assiette", "Idem."),
]
# L'addition est refaite ici a partir des libelles eux-memes : la piece ne peut pas
# afficher un total que ses propres lignes ne donnent pas.
TOTAL_CITE_L = round(sum(float(v[0].replace(" L", "").replace(",", "."))
                         for v in VOLUMES_CITES), 2)
assert TOTAL_CITE_L == 2132.01, TOTAL_CITE_L

# Volumes cités au point 3 (crémant, p. 62 et 63) : 93,20 L et 206,25 L. Ils ne sont
# PAS comptés ci-dessus, et la raison est écrite dans le relevé : ce sont nos propres
# chiffres, que le service reprend pour un calcul de cohérence (45,18 % de pertes),
# non des volumes qu'il oppose au poste.

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
    ws.append(["Une ligne par rubrique du courrier. La colonne « Volume mesure oppose ? » est "
               "la seule qui compte dans un bilan matiere : le service dit-il, pour ce poste, "
               "combien de litres sont reellement partis, releve a l'appui ? Le courrier cite "
               "bien des litres, et le troisieme bloc ci-dessous les aligne un a un : ils sont "
               "tous produits par ses propres taux ou par ses propres colonnes. Chaque ligne "
               "porte sa page : le releve est verifiable."])
    ws["A2"].font = Font(italic=True, size=9, color="64748B")
    ws.append([])
    cols = ["Repere", "Page(s) du courrier", "Poste du bilan matiere",
            "Nature des chiffres opposes", "Volume mesure oppose ?",
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
    # Denominateur : les rubriques « Reponse du service » du bloc, soit les lignes du
    # releve moins celles qui n'en comportent pas (repere L, chapeau de la page 59).
    nb_rubriques = n - sum(1 for l in LIGNES if l[0] in SANS_RUBRIQUE)
    nb_concession = sum(1 for l in LIGNES if l[3] == "concession")
    ws.append(["TOTAL", f"{n} lignes relevees", "",
               f"aucun chiffre : {sum(1 for l in LIGNES if l[3] == 'aucun chiffre')} / "
               f"abattement de sa methode : {sum(1 for l in LIGNES if l[3] == 'abattement de sa methode' or l[3] == 'abattement de sa méthode')} / "
               f"calcul de coherence : {sum(1 for l in LIGNES if l[3] == 'calcul de coherence' or l[3] == 'calcul de cohérence')} / "
               f"concession : {sum(1 for l in LIGNES if l[3] == 'concession')}",
               f"non : {nb_non} sur {nb_rubriques}",
               f"{n} lignes relevees, dont {n - nb_rubriques} repere sans rubrique "
               f"« Reponse du service » (L, chapeau de la page 59) : le denominateur est "
               f"donc de {nb_rubriques} rubriques, dont {nb_concession} concession "
               f"(point 10), sans objet au regard d'un volume."])
    r = ws.max_row
    for c in range(1, len(cols) + 1):
        ws.cell(row=r, column=c).font = Font(bold=True)
        ws.cell(row=r, column=c).fill = surligne
        ws.cell(row=r, column=c).border = bord
        ws.cell(row=r, column=c).alignment = haut
    # ----- Ce que le service CITE, et ce qu'il MESURE -------------------------
    # Le relevé ne peut pas conclure « aucun volume » quand sa propre colonne de
    # conclusion en aligne : il distingue donc ce qui est cité de ce qui est mesuré,
    # et il fait l'addition lui-même.
    ws.append([])
    ws.append(["Ce que le service CITE, et ce qu'il MESURE : les volumes ecrits dans le "
               "courrier, un a un"])
    ws.cell(row=ws.max_row, column=1).font = Font(bold=True, size=12)
    ws.append(["Le courrier n'est pas muet en litres. Il en ecrit dix, pour un total de "
               "2 132,01 L. Aucun n'est un volume mesure dans le poste auquel il est "
               "oppose : chacun est le produit d'un taux forfaitaire du service ou la "
               "lecture d'une de ses propres colonnes. C'est la distinction que porte la "
               "colonne « Volume mesure oppose ? » de l'onglet ci-dessus."])
    ws.cell(row=ws.max_row, column=1).font = Font(italic=True, size=9, color="64748B")
    sous = ["Volume cite", "Page(s)", "Rubrique du courrier", "D'ou vient ce chiffre",
            "Volume mesure dans le poste ?", "Pourquoi ce n'est pas une mesure"]
    ws.append(sous)
    r = ws.max_row
    for c in range(1, len(sous) + 1):
        cell = ws.cell(row=r, column=c)
        cell.font, cell.fill, cell.border = blanc, tete, bord
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    for vol, page, rub, origine, motif in VOLUMES_CITES:
        ws.append([vol, page, rub, origine, "non", motif])
        r = ws.max_row
        for c in range(1, len(sous) + 1):
            ws.cell(row=r, column=c).border = bord
            ws.cell(row=r, column=c).alignment = haut
    ws.append(["%s L" % ("%.2f" % TOTAL_CITE_L).replace(".", ",").replace("2132", "2 132"),
               "p. 64 a 71", "%d volumes cites" % len(VOLUMES_CITES),
               "Taux forfaitaires et colonnes du service", "non",
               "Total des volumes ecrits par le courrier sur le bloc reconstitution. Le "
               "releve ne soutient donc pas que le service ne cite aucun litre : il "
               "soutient qu'aucun de ces litres ne mesure ce qui est reellement parti "
               "dans le poste, et qu'aucun n'est donc opposable comme volume."])
    r = ws.max_row
    for c in range(1, len(sous) + 1):
        ws.cell(row=r, column=c).font = Font(bold=True)
        ws.cell(row=r, column=c).fill = surligne
        ws.cell(row=r, column=c).border = bord
        ws.cell(row=r, column=c).alignment = haut
    ws.append([])
    ws.append(["Deux volumes cites au point 3 (cremant, p. 62 et 63), 93,20 L et "
               "206,25 L, ne figurent pas dans cette addition : ce sont les chiffres de "
               "la societe, que le service reprend pour un calcul de coherence "
               "(45,18 % de pertes), non des volumes qu'il oppose au poste. Ils sont "
               "rapportes tels quels a la ligne 3 de l'onglet ci-dessus."])
    ws.cell(row=ws.max_row, column=1).alignment = haut
    ws.append(["Lecture d'ensemble. Sur les %d rubriques « Reponse du service » du bloc, "
               "%d n'opposent aucun volume mesure au poste discute ; la %s est une "
               "concession (point 10, ventes sans achat), sans objet au regard d'un "
               "volume. Le repere L, chapeau de la page 59, ne comporte pas de rubrique "
               "et ne compte donc pas au denominateur, ce qui porte le releve a %d lignes."
               % (nb_rubriques, nb_non, "derniere", n)])
    ws.cell(row=ws.max_row, column=1).alignment = haut

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
    print(f"{n} lignes relevées, {nb_rubriques} rubriques « Réponse du service », "
          f"{nb_non} sans volume mesuré opposé.")
    print(f"{len(VOLUMES_CITES)} volumes cités par le courrier, "
          f"{TOTAL_CITE_L:.2f} L au total, aucun mesuré dans le poste.")
    print(f"{total} conclusions de non-modification, pages 60 à 89.")


if __name__ == "__main__":
    main()
