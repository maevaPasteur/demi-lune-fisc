#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REPONSE 1 - D'ou viennent les doses que le service retient ?

Piece produite : public/documents/pieces-reponse-1/R1-doses-origines.xlsx

Objet
-----
La reconstitution du service divise un volume d'alcool disponible par une DOSE.
Ce script recense, dose par dose, l'ORIGINE que le service lui-meme indique, en
citant mot a mot la phrase et la page ou elle figure, puis controle si les
tableaux chiffres du courrier du 04/09/2026 sont reproductibles a partir des
nombres imprimes.

Sources reellement ouvertes (aucune valeur n'est estimee) :
  - Proposition de rectifications du 18/05/2026,
    public/documents/rapports-des-finances-publiques/Proposition_1_Lettre.pdf,
    pages 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47 et 48 ;
  - src/data/reconstitution-administration.json (transcription des
    « Annexes finales », Proposition_4_Annexes_Finales.pdf) ;
  - courrier du service du 04/09/2026, images p. 62, 63, 65, 66, 67, 68 et 85.

Le script n'ecrit QUE le fichier xlsx ci-dessus. Il ne modifie aucun autre
fichier du depot et ne regenere aucune piece existante.
"""
import json
import os

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
JSON_ANNEXES = os.path.join(ROOT, "src/data/reconstitution-administration.json")
OUT = os.path.join(ROOT, "public/documents/pieces-reponse-1/R1-doses-origines.xlsx")

PROP = "Proposition 18/05/2026"
COUR = "Courrier 04/09/2026"

# ---------------------------------------------------------------------------
# 1. LES DOSES DU SERVICE, ARTICLE PAR ARTICLE
#    (article, dose, unite, usage, origine declaree par le service, document,
#     page, citation mot a mot)
#    « origine non indiquee » = le service donne la dose sans en dire la source.
# ---------------------------------------------------------------------------
DOSES = [
    # --- Regle generale d'origine ------------------------------------------
    ("[Regle generale] Toutes doses de boissons vendues", None, "", "Vente",
     "Menus et cartes des plats et boissons",
     PROP, 36,
     "Afin de se faire une idee de l'exploitation, le verificateur a pu, d'abord, "
     "avoir acces aux menus et cartes des plats et boissons qui sont ou ont ete "
     "proposes a la clientele du restaurant. Ces documents indiquant pour une "
     "grande partie des articles, les volumes vendus a la dose aux clients, il a "
     "ete possible de s'en servir pour determiner le nombre de doses disponibles "
     "pour la clientele sur chacun des exercices."),
    ("[Regle generale] Colonne « dose » des annexes 7-1 a 7-3", None, "", "Vente",
     "Cartes de boissons + precisions des dirigeants",
     PROP, 40,
     "D'une maniere generale, les doses inscrites dans cette colonne proviennent "
     "des informations des cartes de boissons et des precisions apportees par les "
     "dirigeants."),
    ("[Regle generale] Doses des alcools de cuisine", None, "", "Cuisine",
     "Recommandations des dirigeants",
     COUR, 68,
     "Pour toutes les doses des alcools necessaires a la cuisine, le service n'a "
     "fait que suivre les recommandations des dirigeants."),

    # --- Vins au verre / pichet (carte) ------------------------------------
    ("Vin au verre", 15, "cl", "Vente", "Carte (article propose a la vente)",
     PROP, 36, "la societe propose comme article a la vente : - vin au verre (doses de 15cl)"),
    ("Vin au pichet", 50, "cl", "Vente", "Carte (article propose a la vente)",
     PROP, 36, "- vin au pichet de 50 cl"),
    ("Vin au pichet / bouteille", 75, "cl", "Vente", "Carte (article propose a la vente)",
     PROP, 36, "- vin au pichet de 75 cl."),

    # --- Vins et petillants specifiques (carte, p. 37) ----------------------
    ("Cremant (verre)", 12, "cl", "Vente", "Carte des boissons",
     PROP, 37,
     "Dans cette categorie, la societe propose a la vente des verres de : - 12 "
     "centilitres pour le Cremant"),
    ("Macvin (verre)", 6, "cl", "Vente", "Carte des boissons",
     PROP, 37, "- 6 centilitres pour le Macvin"),
    ("Vin de paille (verre)", 6, "cl", "Vente", "Carte des boissons",
     PROP, 37, "- 6 centilitres pour le Vin de Paille"),
    ("Vin jaune (verre)", 12, "cl", "Vente", "Carte des boissons",
     PROP, 37, "- 12 centilitres pour le Vin Jaune"),

    # --- Alcools forts et digestifs (carte, p. 37) --------------------------
    ("Alcools forts et digestifs (regle)", 4, "cl", "Vente", "Carte des boissons",
     PROP, 37,
     "Les doses proposees a la vente sont de 4 centilitres. Il existe de rares "
     "exceptions a ce principe general"),
    ("Pontarlier", 2, "cl", "Vente", "Carte des boissons",
     PROP, 37, "- 2 centilitres pour le Pontarlier"),
    ("Pastis et Ricard", 2, "cl", "Vente", "Carte des boissons",
     PROP, 37, "- 2 centilitres pour le Pastis et le Ricard"),
    ("Baby whisky", 2, "cl", "Vente", "Carte des boissons",
     PROP, 37, "- 2 centilitres pour les Baby whisky"),
    ("Porto et Martini blanc", 6, "cl", "Vente", "Carte des boissons",
     PROP, 37, "- 6 centilitres pour le Porto et le martini Blanc"),

    # --- Cocktails ----------------------------------------------------------
    ("Cocktails (tous)", None, "", "Vente",
     "Recettes demandees aux dirigeants le 06/03/2026, reputees confirmees faute de reponse",
     PROP, 37,
     "Lors de l'entrevue du 06 mars 2026, le verificateur a pu demander les "
     "recettes precises des differents cocktails proposes a la vente. Un compte "
     "rendu rappelant leurs dosages respectifs a ete adresse aux dirigeants, les "
     "invitant a preciser ou corriger les elements evoques. Aucune reponse sur ce "
     "point n'ayant ete adressee au service, le verificateur ne peut que "
     "considerer que ces dosages sont confirmes."),

    # --- Cafes --------------------------------------------------------------
    ("Cafe expresso simple", 7, "g", "Vente", "Dose normee (norme non citee)",
     PROP, 37,
     "Pour tous les produits a base de cafe, le service retiendra la dose normee "
     "de 7 grammes pour un cafe expresso simple ou 14 grammes pour les doubles "
     "expresso."),
    ("Cafe double expresso", 14, "g", "Vente", "Dose normee (norme non citee)",
     PROP, 37,
     "le service retiendra la dose normee de 7 grammes pour un cafe expresso "
     "simple ou 14 grammes pour les doubles expresso"),

    # --- Cuisine : courriel des dirigeants (p. 37) --------------------------
    ("Creme brulee a l'Absinthe", 1.14, "cl", "Cuisine",
     "Courriel des dirigeants (entrevue du 30/03/2026)", PROP, 37,
     "Creme brulee a l'Absinthe : 8 cl/Litre pour 7 pers. = 1.14 cl d'Absinthe/Pers."),
    ("Babas", 4, "cl", "Cuisine",
     "Courriel des dirigeants (entrevue du 30/03/2026)", PROP, 37,
     "Babas : 4 cl d'alcool (Quelque soit l'alcool)"),
    ("Coupes de glaces alcoolisees", 4, "cl", "Cuisine",
     "Courriel des dirigeants (entrevue du 30/03/2026)", PROP, 37,
     "Coupes de glaces alcoolisees : 4 cl d'alcool  (Quelque soit l'alcool)"),
    ("Crepes flambees", 4, "cl", "Cuisine",
     "Courriel des dirigeants (entrevue du 30/03/2026)", PROP, 37,
     "Crepes flambees : 4 cl d'alcool  (Quelque soit l'alcool)"),
    ("Sauce Jurassienne (vin jaune)", 1, "cl", "Cuisine",
     "Courriel des dirigeants (entrevue du 30/03/2026)", PROP, 37,
     "Sauce Jurassienne : 10 cl de vin jaune pour 1 litre de sauce pour 10 parts "
     "= 1 cl de vin jaune/Pers."),
    ("Sauce Forestiere et Sauce Morilles (porto)", 1, "cl", "Cuisine",
     "Courriel des dirigeants (entrevue du 30/03/2026)", PROP, 37,
     "Sauce Forestiere et Sauce Morilles : 10 cl de Porto pour 1 litre de sauce "
     "pour 10 parts = 1 cl de Porto/Pers."),
    ("Camembert, Assiette Franc-Comtoise, Assiette du Pere Gregoire",
     None, "4 a 5 cl", "Cuisine",
     "Courriel des dirigeants (fourchette 4 a 5 cl, Macvin ou Calvados)", PROP, 37,
     "Camembert, Assiette Franc-Comtoise et Assiette du Pere Gregoire : Ce sont "
     "des plats flambes devant les clients, environ 4 a 5 cl d'alcool/Pers. "
     "(Macvin ou Calvados)"),
    ("Fondue Jurassienne", None, "9 ou 10 cl", "Cuisine",
     "Courriel des dirigeants (fourchette 9 ou 10 cl)", PROP, 37,
     "Fondue Jurassienne : 9 ou10 cl de vin/Pers."),
    ("Fondue Vin Jaune et Fondue des Gourmets", None, "9 ou 10 cl", "Cuisine",
     "Courriel des dirigeants (fourchette 9 ou 10 cl)", PROP, 37,
     "Fondue Vin Jaune et Fondue des Gourmets : 9 ou 10 cl de vin jaune/Pers."),

    # --- Doses rappelees dans la description de la methode (p. 39-40, 43) ---
    ("Limonade (verre)", 25, "cl", "Vente", "Cartes de boissons (regle p. 40)",
     PROP, 40, "- la limonade est vendue par verre de 25 centilitres"),
    ("Sirops a l'eau", 4, "cl", "Vente",
     "Menus/cartes (« les menus/cartes pouvaient indiquer la volumetrie »)", PROP, 43,
     "il s'agit des articles pour lesquels les menus/cartes pouvaient indiquer la "
     "volumetrie necessaire pour ce type de produit. Il y a ainsi respectivement : "
     "- Les sirops a l'eau (4 cl)"),
    ("Autres aperitifs", None, "2, 4 ou 6 cl", "Vente", "Menus/cartes",
     PROP, 43, "- Les autres aperitifs (soit 2 cl, soit 4 cl , soit 6 cl)"),
    ("Plats du jour : part supplementaire de vin", None, "10 % du disponible",
     "Cuisine", "DECISION DU SERVICE (aucune source exterieure)", PROP, 43,
     "Enfin, il est utile de preciser que le service a decide, pour la conception "
     "des plats du jour, de considerer qu'une part supplementaire de 10 % de vin "
     "disponible serait utilisee a cette fin."),

    # --- Cocktails : limonade (p. 46) --------------------------------------
    ("Diabolo (limonade)", 21, "cl", "Vente",
     "Recettes des dirigeants ou carte des boissons", PROP, 46,
     "la societe utilise de la limonade (conformement aux recettes obtenues des "
     "dirigeants ou de la carte des boissons, ou d'internet (*), a defaut) "
     "respectivement pour : [...] - Diabolo (21 cl de limonade et 4 cl de sirop)"),
    ("Diabolo (sirop)", 4, "cl", "Vente",
     "Recettes des dirigeants ou carte des boissons", PROP, 46,
     "- Diabolo (21 cl de limonade et 4 cl de sirop)"),
    ("Mambo (limonade)", 10, "cl", "Vente",
     "Recettes des dirigeants ou carte des boissons", PROP, 46,
     "- Manbo (10 cl de limonade)"),
    ("Luna (limonade)", 10, "cl", "Vente",
     "Recettes des dirigeants ou carte des boissons", PROP, 46,
     "- Luna (10 cl de limonade)"),
    ("Rabasse (limonade)", 21, "cl", "Vente",
     "Recettes des dirigeants ou carte des boissons", PROP, 46,
     "- Rabasse ( 21 cl de limonade)"),
    ("Panache (limonade)", 13, "cl", "Vente",
     "INTERNET (repere (*) : « ou d'internet (*), a defaut »)", PROP, 46,
     "- Panache (13 cl de limonade) (*)"),
    ("Monaco (limonade)", 5, "cl", "Vente",
     "INTERNET (repere (*) : « ou d'internet (*), a defaut »)", PROP, 46,
     "- Monaco (5 cl de limonade) (*)."),

    # --- Cocktails : cremant (p. 46) ---------------------------------------
    ("La Vouivre (cremant)", 6, "cl", "Vente",
     "Recettes des dirigeants ou carte des boissons", PROP, 46,
     "la societe utilise du cremant (conformement aux recettes obtenues des "
     "dirigeants ou de la carte des boissons) respectivement pour : - Le cocktail "
     "La vouivre (6 cl)"),
    ("Le Pere Gregoire (cremant)", 6, "cl", "Vente",
     "Recettes des dirigeants ou carte des boissons", PROP, 46,
     "- Le cocktail Le Pere Gregoire (6 cl)"),
    ("KITTYKIR (cremant)", 6, "cl", "Vente",
     "Recettes des dirigeants ou carte des boissons", PROP, 46,
     "- le KITTYKIR (6 cl)"),
    ("Cremant (verre)", 12, "cl", "Vente",
     "Recettes des dirigeants ou carte des boissons", PROP, 46,
     "- Le verre de cremant (12 cl)"),
    ("Cremant (bouteille)", 75, "cl", "Vente",
     "Recettes des dirigeants ou carte des boissons", PROP, 46,
     "- La bouteille de Cremant (75 cl)"),

    # --- Cocktails : macvin (p. 47) ----------------------------------------
    ("Macvin (verre)", 6, "cl", "Vente",
     "Recettes des dirigeants ou carte des boissons", PROP, 47,
     "la societe utilise du Macvin (conformement aux recettes obtenues des "
     "dirigeants ou de la carte des boissons) respectivement pour : - Le verre de "
     "Macvin (6 cl)"),
    ("La Vouivre (macvin)", 4, "cl", "Vente",
     "Recettes des dirigeants ou carte des boissons", PROP, 47,
     "- Le cocktail La vouivre (4 cl)"),
    ("Le Pere Gregoire (macvin)", 4, "cl", "Vente",
     "Recettes des dirigeants ou carte des boissons", PROP, 47,
     "- Le cocktail Le Pere Gregoire (4 cl)"),
    ("Le Chat perche (macvin)", 4, "cl", "Vente",
     "Recettes des dirigeants ou carte des boissons", PROP, 47,
     "- Le cocktail Le Chat perche (4 cl)"),

    # --- Doses appliquees dans les tableaux de repere (p. 42, 44, 45, 48) ---
    ("Filet Poulet Jurassienne (vin blanc)", 2, "cl", "Cuisine",
     "ORIGINE NON INDIQUEE (dose portee au tableau du repere A-1, sans source)",
     PROP, 42, "Filet Poulet Jurassienne | 955 | 955 | 2 | 1 910"),
    ("Sauce Vin jaune (vin blanc)", 2, "cl", "Cuisine",
     "ORIGINE NON INDIQUEE (tableau du repere A-1, sans source)",
     PROP, 42, "Sauce Vin jaune | 91 | 91 | 2 | 182"),
    ("Fondue Jurassienne (vin blanc)", 10, "cl", "Cuisine",
     "Fourchette « 9 ou 10 cl » des dirigeants : borne HAUTE retenue",
     PROP, 42, "Fondue Jurassienne | 372 | 372 | 10 | 3 720"),
    ("Fondue Vin jaune (vin blanc)", 10, "cl", "Cuisine",
     "ORIGINE NON INDIQUEE pour le vin BLANC (les dirigeants ne citent que du vin jaune)",
     PROP, 42, "Fondue Vin jaune | 133 | 133 | 10 | 1 330"),
    ("Fondue des Gourmets (vin blanc)", 10, "cl", "Cuisine",
     "ORIGINE NON INDIQUEE pour le vin BLANC (les dirigeants ne citent que du vin jaune)",
     PROP, 42, "Fondue des Gourmet | 88 | 88 | 10 | 880"),
    ("Camembert Roti (calvados)", 4, "cl", "Cuisine",
     "Fourchette « 4 a 5 cl » des dirigeants : borne BASSE retenue",
     PROP, 44, "Camembert Roti | 512 | 512 | 4 | 2 048"),
    ("Assiette du Pere Gregoire (calvados)", 4, "cl", "Cuisine",
     "Fourchette « 4 a 5 cl » des dirigeants : borne BASSE retenue",
     PROP, 44, "Assiette du Pere Gregoire | 222 | 222 | 4 | 888"),
    ("Menu Vegetarien (calvados)", 4, "cl", "Cuisine",
     "Fourchette « 4 a 5 cl » des dirigeants, ponderee par 35,58 % de choix en caisse",
     PROP, 44, "Menu Vegetarien | 263 | 35,58 % | 94 | 4 | 374"),
    ("Filet Poulet Jurassienne (vin jaune)", 1, "cl", "Cuisine",
     "Courriel des dirigeants (1 cl de vin jaune/pers. pour la sauce)",
     PROP, 45, "Filet Poulet Jurassienne | 955 | 955 | 1 | 955"),
    ("Fondue Vin jaune (vin jaune)", 10, "cl", "Cuisine",
     "Fourchette « 9 ou 10 cl » des dirigeants : borne HAUTE retenue",
     PROP, 45, "Fondue Vin jaune | 133 | 133 | 10 | 1 330"),
    ("Fondue des Gourmets (vin jaune)", 10, "cl", "Cuisine",
     "Fourchette « 9 ou 10 cl » des dirigeants : borne HAUTE retenue",
     PROP, 45, "Fondue des Gourmet | 88 | 88 | 10 | 880"),
    ("Sauce Forestiere / Morille (porto)", 1, "cl", "Cuisine",
     "Dires des dirigeants (1 cl par portion de sauce servie)", PROP, 45,
     "un repere G, qui detaille le volume de Porto destine a la conception des "
     "sauces Forestiere et Morille (en se basant sur 1 cl par portion de sauce "
     "servie, conformement aux dires des dirigeants en la matiere)"),
    ("Porto en cuisine (entree)", 1, "cl", "Cuisine",
     "Dires des dirigeants", PROP, 46,
     "grace au volume de la dose de Porto utilisee par entree (1 centilitre selon "
     "les dirigeants), le service est en mesure d'etablir le volume total de Porto "
     "theoriquement utilise pour la cuisine"),
    ("Creme de cassis (coupe dijonnaise)", 4, "cl", "Cuisine",
     "ORIGINE NON INDIQUEE (repere I, dose citee sans source)", PROP, 43,
     "un repere I, qui tient compte de la consommation de creme de cassis, en "
     "centilitres (4 cl), pour la conception de la coupe dijonnaise dans le menu "
     "Bourguignon."),
    ("Calvados en cuisine (repere D)", 1, "cl", "Cuisine",
     "ORIGINE NON INDIQUEE (« un repere D, relatif au calvados consomme pour la "
     "conception des desserts ou des plats », 1 cl annonce p. 43 contre 4 cl "
     "applique p. 44)", PROP, 43,
     "un repere D, relatif au calvados consomme pour la conception des desserts ou "
     "des plats"),
    ("Macvin en cuisine (exercice 1)", 5, "cl", "Cuisine",
     "Dires des dirigeants (5 cl)", PROP, 48,
     "grace au volume de la dose de Macvin (5 centilitres selon les dirigeants), le "
     "service est en mesure d'etablir le volume total de Macvin theoriquement "
     "utilise pour la cuisine"),

    # --- Cocktails valorises en bloc (annexes finales) ---------------------
    ("Picon biere (picon)", 3, "cl", "Vente",
     "Recette de cocktail reputee confirmee (entrevue du 06/03/2026)",
     "Annexes finales", 0, "Picon biere (3 cl picon + 22 cl biere)"),
    ("Picon biere (biere)", 22, "cl", "Vente",
     "Recette de cocktail reputee confirmee (entrevue du 06/03/2026)",
     "Annexes finales", 0, "Picon biere (3 cl picon + 22 cl biere)"),
    ("Pinte Picon (picon)", 6, "cl", "Vente",
     "Recette de cocktail reputee confirmee (entrevue du 06/03/2026)",
     "Annexes finales", 0, "Pinte Picon (6 cl picon + 44 cl biere)"),
    ("Pinte Picon (biere)", 44, "cl", "Vente",
     "Recette de cocktail reputee confirmee (entrevue du 06/03/2026)",
     "Annexes finales", 0, "Pinte Picon (6 cl picon + 44 cl biere)"),
    ("Biere pression", 25, "cl", "Vente", "Carte des boissons",
     "Annexes finales", 0, "Pression (25 cl)"),
    ("Biere pinte", 50, "cl", "Vente", "Carte des boissons",
     "Annexes finales", 0, "Pinte (50 cl)"),

    # --- Doses enoncees dans le courrier du 04/09/2026 ---------------------
    ("Cremant (verre)", 12, "cl", "Vente",
     "Dires des dirigeants", COUR, 63,
     "pour le cas du cremant, et du type de verre (petite coupe) generalement "
     "utilise dans la profession pour ce type de boisson, la dose vendue "
     "s'etablissant a 12 centilitres (conformement aux dires des dirigeants) une "
     "sur-dose de 23,60 % conduirait a remplir le verre d'une facon exageree."),
    ("La Vouivre / Pere Gregoire / KITTYKIR (cremant)", 6, "cl", "Vente",
     "Tableau de caisse reproduit par le service (colonne « Dose (en centilitres) »)",
     COUR, 62, "La Vouivre (H) | 5,17 EUR | 622 | 6 | 3 732 | 31,61 %"),
    ("Cremant (verre), tableau de caisse", 12, "cl", "Vente",
     "Tableau de caisse reproduit par le service (colonne « Dose (en centilitres) »)",
     COUR, 62, "Cremant (verre) | 3,85 EUR | 242 | 12 | 2 904 | 24,59 %"),
    ("Calvados en cuisine (par plat)", 4, "cl", "Cuisine",
     "ORIGINE NON INDIQUEE SUR LA PAGE (en-tete de colonne seulement ; le service "
     "renvoie ailleurs aux « doses fournies par les dirigeants »)", COUR, 65,
     "Volume consomme (a raison de 4 cl par plat)"),
    ("Doses de cuisine (generalite)", None, "", "Cuisine",
     "« volumes de doses fournies par les dirigeants », que le service dit pouvoir "
     "estimer maximisees et « totalement errones »", COUR, 66,
     "Le service serait meme en droit d'estimer que les volumes de doses fournies "
     "par les dirigeants ont ete maximisees, donc sont totalement errones, et "
     "aboutissent a minorer les montants des chiffres d'affaires reconstitues, "
     "situation qui serait susceptible d'arranger la societe."),
    ("Vin jaune (verre)", 12, "cl", "Vente",
     "Enonce du service", COUR, 66, "Cet alcool est utilise pour : - des articles au verre (dose de 12 cl)"),
    ("Vin jaune (verre), en-tete du tableau", 6, "cl", "Vente",
     "CONTRADICTION INTERNE : l'en-tete du tableau de la meme page dit 6 cl quand "
     "le texte, 8 lignes plus haut, dit 12 cl", COUR, 66,
     "Volume consomme total (Plats + vente au verre de 6 cl)"),
    ("Vin jaune en cuisine (sauces / fondues)", None, "1 cl / 10 cl", "Cuisine",
     "En-tete de colonne du tableau (deux doses coexistantes)", COUR, 66,
     "Donnees de la caisse Nombre de plats (necessitant une dose) 1cl / 10 cl"),
    ("Porto en cuisine (sauces)", 1, "cl", "Cuisine",
     "Dose « fournie par les dirigeants lors des operations sur place »", COUR, 67,
     "Pour expliquer l'ecart entre volume consomme ressortant de la caisse et le "
     "volume disponible, si le service devait suivre la logique de Maitre THIVEND "
     "il faudrait multiplier par 5 la dose d'un centilitre fournie par les "
     "dirigeants lors des operations sur place."),
    ("Porto (verre)", 6, "cl", "Vente", "Enonce du service", COUR, 67,
     "Cet alcool est utilise pour - les sauces en cuisse pour des plats "
     "specifiques (1cl). - des articles au verre (dose de 6 cl)."),
    ("Macvin (verre)", 6, "cl", "Vente", "Enonce du service", COUR, 67,
     "Cet alcool est utilise pour : - des articles au verre (dose de 6 cl)"),
    ("Macvin en cuisine (plats/desserts)", 4, "cl", "Cuisine",
     "Enonce du service p. 67, CONTRADICTOIRE avec les 5 cl « selon les dirigeants » "
     "de la proposition p. 48 (exercice 1)", COUR, 67,
     "- 4 cl, pour la preparation des plats/desserts ( en cuisine )"),
    ("Cremant (verre)", 12, "cl", "Vente", "Dires des dirigeants", COUR, 85,
     "pour le cas du cremant, et du type de verre (petite coupe) generalement "
     "utilise dans la profession pour ce type de boisson, la dose vendue "
     "s'etablissant a 12 centilitres (conformement aux dires des dirigeants)"),
]

# ---------------------------------------------------------------------------
# 2. LE TABLEAU DU CALVADOS, COURRIER DU 04/09/2026, PAGE 65
#    En-tete de colonne : « Volume consomme (a raison de 4 cl par plat) »
# ---------------------------------------------------------------------------
CALVADOS_P65 = [
    # (exercice, volume consomme cl, nb plats, volume disponible cl)
    ("Exercice 1 (clos au 31/03/2023)", 3310, 997, 3100),
    ("Exercice 2 (clos au 31/03/2024)", 3002, 880, 2200),
    ("Exercice 3 (clos au 31/03/2025)", 3005, 873, 2000),
]
DOSE_ANNONCEE_CALVADOS = 4.0

# Detail du repere D, exercice 1, tel qu'imprime page 44 de la proposition.
# (article, nb articles caisse, proportion menu ou None, dose cl, quantite cl imprimee)
REPERE_D_EX1 = [
    ("Camembert Roti", 512, None, 4, 2048),
    ("Assiette du Pere Gregoire", 222, None, 4, 888),
    ("Menu Vegetarien", 263, 0.3558, 4, 374),
]

# ---------------------------------------------------------------------------
# 3. LES AUTRES TABLEAUX DU COURRIER : VIN JAUNE (p. 66), PORTO ET MACVIN (p. 67)
#    Colonne « Volume consomme total (Plats + vente au verre de 6 cl) »
# ---------------------------------------------------------------------------
# (alcool, page, exercice, volume plats, volume verre, total imprime,
#  nb plats imprime, volume disponible, dose annoncee en en-tete)
TABLEAUX = [
    ("Vin jaune (repere E)", 66, "Exercice 1", 3717, 1044, 4761, "1 507 / 221", 7409, "1 cl / 10 cl"),
    ("Vin jaune (repere E)", 66, "Exercice 2", 3693, 1224, 4917, "1 449 / 247", 6758, "1 cl / 10 cl"),
    ("Vin jaune (repere E)", 66, "Exercice 3", 3748, 1476, 5224, "1 748 / 189", 7874, "1 cl / 10 cl"),
    ("Porto (repere G)", 67, "Exercice 1", 398, 213, 611, "478", 2730, "1 cl"),
    ("Porto (repere G)", 67, "Exercice 2", 583, 282, 865, "745", 4760, "1 cl"),
    ("Porto (repere G)", 67, "Exercice 3", 556, 282, 838, "783", 4480, "1 cl"),
    ("Macvin (repere Q)", 67, "Exercice 1", 7774, 8610, 16384, "2 400", 24000, "4 cl"),
    ("Macvin (repere Q)", 67, "Exercice 2", 8832, 10120, 18952, "2 510", 28350, "4 cl"),
    ("Macvin (repere Q)", 67, "Exercice 3", 7406, 9398, 16804, "2 714", 27150, "4 cl"),
]

# Details des reperes E, G et Q pour l'exercice 1, imprimes proposition p. 45 et 48.
REPERE_E_EX1 = [  # vin jaune
    ("Filet Poulet Jurassienne", 955, None, 1, 955),
    ("Sauce Vin jaune", 91, None, 1, 91),
    ("Fondue Vin jaune", 133, None, 10, 1330),
    ("Fondue des Gourmet", 88, None, 10, 880),
    ("Menu Franc Comtois", 748, 0.6165, 1, 461),
]
REPERE_G_EX1 = [  # porto
    ("Sauce Forestiere", 33, None, 1, 33),
    ("Entrecote Forestiere", 238, None, 1, 238),
    ("Sauce Morille", 37, None, 1, 37),
    ("Entrecote Morille", 17, None, 1, 17),
    ("Menu Demi-Lune", 153, 0.4783, 1, 73),
]
REPERE_Q_EX1 = [  # macvin
    ("Baba au Macvin", 310, None, 5, 1550),
    ("Saucisse flambee au Macvin", 594, None, 5, 2970),
    ("Menu Franc Comtois - plat (Poulet/Assiette)", 748, 0.3835, 5, 1434),
    ("Menu Franc Comtois - dessert (Baba / Creme brulee)", 748, 0.4867, 5, 1820),
]

SOURCES = [
    ("public/documents/rapports-des-finances-publiques/Proposition_1_Lettre.pdf",
     "Proposition de rectifications du 18/05/2026",
     "p. 34 a 48 (lues avec l'outil Read, parametre pages)",
     "Origine des doses : p. 36 (menus et cartes), p. 37 (carte des boissons, "
     "cocktails de l'entrevue du 06/03/2026, cafes, courriel des dirigeants du "
     "30/03/2026), p. 40 (regle generale), p. 43 (categories a la dose et decision "
     "des 10 % plats du jour), p. 42/44/45/48 (tableaux des reperes A-1, D, E, G, Q)."),
    ("public/documents/rapports-des-finances-publiques/Proposition_4_Annexes_Finales.pdf",
     "Annexes finales de la proposition (3 pages scannees)",
     "transcription : src/data/reconstitution-administration.json",
     "Doses implicites recalculees volume / nombre d'articles, et volume / "
     "(nombre d'articles x proportion) lorsqu'une proportion figure."),
    ("src/data/reconstitution-administration.json", "Transcription des annexes finales",
     "lue par ce script", "Sert a recalculer les doses implicites de la feuille "
     "« Doses implicites annexes »."),
    ("scratchpad/pages/p-62.png", "Courrier du service du 04/09/2026, page 62",
     "image ouverte", "Cremant : tableau de caisse avec colonne « Dose (en centilitres) » "
     "6 / 12 / 75 cl ; quantites disponibles par exercice."),
    ("scratchpad/pages/p-63.png", "Courrier du service du 04/09/2026, page 63",
     "image ouverte", "Cremant : dose de 12 cl « conformement aux dires des dirigeants »."),
    ("scratchpad/pages/p-65.png", "Courrier du service du 04/09/2026, page 65",
     "image ouverte", "Calvados (repere D) : tableau « Volume consomme (a raison de 4 cl "
     "par plat) » / « Nombre de plats » / « Volume Disponible »."),
    ("scratchpad/pages/p-66.png", "Courrier du service du 04/09/2026, page 66",
     "image ouverte", "Vin jaune (repere E) : verre a 12 cl dans le texte, 6 cl dans "
     "l'en-tete du tableau ; plats a 1 cl / 10 cl."),
    ("scratchpad/pages/p-67.png", "Courrier du service du 04/09/2026, page 67",
     "image ouverte", "Porto (repere G) : sauces 1 cl, verre 6 cl, « dose d'un "
     "centilitre fournie par les dirigeants lors des operations sur place ». "
     "Macvin (repere Q) : verre 6 cl, cuisine 4 cl."),
    ("scratchpad/pages/p-68.png", "Courrier du service du 04/09/2026, page 68",
     "image ouverte", "« Pour toutes les doses des alcools necessaires a la cuisine, "
     "le service n'a fait que suivre les recommandations des dirigeants. »"),
    ("scratchpad/pages/p-85.png", "Courrier du service du 04/09/2026, page 85",
     "image ouverte", "Cremant : rappel de la dose de 12 cl « conformement aux dires "
     "des dirigeants »."),
]


# ---------------------------------------------------------------------------
# Calculs
# ---------------------------------------------------------------------------
def doses_implicites_annexes():
    """Dose implicite = volumeCl / nbArticles, et / proportion si elle figure."""
    doc = json.load(open(JSON_ANNEXES, encoding="utf-8"))
    lignes = []
    for ing in doc.get("ingredients", []):
        ded = ing.get("deductions") or {}
        for d in ded.get("detail", []):
            n = d.get("nbArticles")
            vol = d.get("volumeCl")
            prop = d.get("proportion")
            if not n or vol is None:
                continue
            brut = vol / n
            net = vol / (n * prop) if prop else None
            lignes.append((ing["ref"], d["usage"], n, prop, vol, brut, net))
        # Deductions globales sans nombre d'articles : dose non calculable.
        for cle, lib in (("dessertsAlcoolsFortsCl", "Desserts a base d'alcools forts"),
                         ("consoPersonnelPertesPct", "Conso personnel + pertes (taux)")):
            if cle in ded and cle == "dessertsAlcoolsFortsCl":
                lignes.append((ing["ref"], lib, None, None, abs(ded[cle]), None, None))
    return lignes


def controle(detail):
    """Rejoue un tableau de repere : somme des quantites et des articles bruts."""
    som_vol = sum(l[4] for l in detail)
    som_brut = sum(l[1] for l in detail)
    som_net = sum((l[1] * l[2] if l[2] else l[1]) for l in detail)
    som_theo = sum(round(l[1] * l[2] * l[3]) if l[2] else l[1] * l[3] for l in detail)
    return som_vol, som_brut, som_net, som_theo


def fr(x, n=2):
    return f"{x:,.{n}f}".replace(",", " ").replace(".", ",")


# ---------------------------------------------------------------------------
# Ecriture du classeur
# ---------------------------------------------------------------------------
def ecrire():
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    white = Font(bold=True, color="FFFFFF")
    bold = Font(bold=True)
    head = PatternFill("solid", fgColor="0F766E")
    alert = PatternFill("solid", fgColor="FEE2E2")
    ok = PatternFill("solid", fgColor="DCFCE7")
    sub = PatternFill("solid", fgColor="E6F4F1")
    thin = Side(style="thin", color="D8DEE4")
    bd = Border(left=thin, right=thin, top=thin, bottom=thin)
    right = Alignment(horizontal="right")
    haut = Alignment(vertical="top", wrap_text=True)

    def entete(ws, cols):
        row = ws.max_row + 1
        for c, lab in enumerate(cols, 1):
            cell = ws.cell(row=row, column=c, value=lab)
            cell.font = white
            cell.fill = head
            cell.alignment = Alignment(horizontal="center", vertical="center",
                                       wrap_text=True)
            cell.border = bd
        return row

    def titre(ws, t, st=None):
        ws.append([t])
        ws.cell(row=ws.max_row, column=1).font = Font(bold=True, size=13)
        if st:
            ws.append([st])
            c = ws.cell(row=ws.max_row, column=1)
            c.font = Font(italic=True, size=9, color="64748B")
            c.alignment = haut
        ws.append([])

    def largeurs(ws, ws_widths):
        for i, w in enumerate(ws_widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w

    def ligne(ws, vals, fill=None, gras=False):
        ws.append(vals)
        r = ws.max_row
        for c in range(1, len(vals) + 1):
            cell = ws.cell(row=r, column=c)
            cell.border = bd
            cell.alignment = haut
            if fill:
                cell.fill = fill
            if gras:
                cell.font = bold
        return r

    # ---- Feuille 1 : Doses du service ------------------------------------
    ws = wb.active
    ws.title = "Doses du service"
    titre(ws, "Les doses retenues par le service, et l'origine qu'il leur donne",
          "Chaque ligne vient d'une page reellement ouverte. La citation est recopiee "
          "mot a mot (accents des PDF scannes normalises). Lorsque le service donne "
          "une dose sans en indiquer la provenance, la colonne « Origine declaree » "
          "porte ORIGINE NON INDIQUEE : c'est un constat, pas une lacune de lecture.")
    cols = ["Article / usage", "Dose", "Unite", "Emploi", "Origine declaree par le service",
            "Document", "Page", "Citation exacte"]
    entete(ws, cols)
    sans_origine = 0
    for art, dose, unite, emploi, origine, doc, page, cit in DOSES:
        if dose is None:
            dval = unite if unite else "(regle generale)"
            uval = ""
        else:
            dval = dose
            uval = unite
        pg = "n.c. (extrait non pagine)" if page == 0 else page
        f = alert if "NON INDIQUEE" in origine or "CONTRADICTION" in origine \
            or "INTERNET" in origine or "DECISION DU SERVICE" in origine else None
        if "NON INDIQUEE" in origine:
            sans_origine += 1
        ligne(ws, [art, dval, uval, emploi, origine, doc, pg, cit], fill=f)
    largeurs(ws, [40, 10, 12, 10, 46, 22, 8, 90])
    ws.freeze_panes = ws.cell(row=5, column=2)

    # ---- Feuille 2 : Calvados p.65 ---------------------------------------
    ws2 = wb.create_sheet("Calvados p.65")
    titre(ws2, "Courrier du 04/09/2026, page 65 : la dose implicite du Calvados",
          "En-tete de colonne imprime par le service : « Volume consomme (a raison de "
          "4 cl par plat) ». La dose implicite est le simple rapport entre les deux "
          "colonnes que le service imprime cote a cote. Les trois valeurs ne sont pas "
          "harmonisees : leur instabilite est le constat.")
    cols2 = ["Exercice", "Volume consomme (cl)", "Nombre de plats (caisse)",
             "Dose implicite volume / plats (cl)", "Dose annoncee en en-tete (cl)",
             "Ecart a l'en-tete (cl)", "4 cl x nb plats (cl)",
             "Ecart avec la colonne imprimee (cl)", "Volume disponible (cl)"]
    entete(ws2, cols2)
    for lib, vol, plats, dispo in CALVADOS_P65:
        implicite = vol / plats
        theo = DOSE_ANNONCEE_CALVADOS * plats
        r = ligne(ws2, [lib, vol, plats, round(implicite, 4), DOSE_ANNONCEE_CALVADOS,
                        round(implicite - DOSE_ANNONCEE_CALVADOS, 4), theo,
                        vol - theo, dispo])
        for c in (4, 6):
            ws2.cell(row=r, column=c).number_format = '0.00'
            ws2.cell(row=r, column=c).alignment = right
        ws2.cell(row=r, column=4).fill = alert
    vals = [v / p for _, v, p, _ in CALVADOS_P65]
    ws2.append([])
    ligne(ws2, ["Amplitude des trois doses implicites : "
                f"{fr(min(vals))} a {fr(max(vals))} cl, soit un ecart de "
                f"{fr(max(vals) - min(vals))} cl "
                f"({fr((max(vals) / min(vals) - 1) * 100, 1)} %)"], gras=True)
    ws2.append([])

    # Reconstitution du 3 310 a partir de la proposition p. 44
    titre(ws2, "D'ou vient le 3 310 ? Proposition du 18/05/2026, page 44, repere D",
          "Le tableau du repere D, exercice clos au 31/03/2023, est imprime en toutes "
          "lettres dans la proposition. Il applique bien 4 cl, mais a un nombre de plats "
          "PONDERE : les 263 menus vegetariens ne comptent que pour 35,58 %, proportion "
          "lue en caisse des plats servis a la carte. Le « nombre de plats » de la page 65 "
          "les compte, lui, pour 263.")
    cols3 = ["Article", "Nb articles caisse", "Proportion (*)", "Nb articles nets",
             "Dose appliquee (cl)", "Quantite imprimee (cl)", "Controle dose x nets (cl)"]
    entete(ws2, cols3)
    for art, n, prop, dose, q in REPERE_D_EX1:
        nets = n * prop if prop else n
        ligne(ws2, [art, n, (f"{fr(prop * 100)} %" if prop else ""), round(nets, 2),
                    dose, q, round(nets * dose, 1)])
    vol_d, brut_d, net_d, _ = controle(REPERE_D_EX1)
    _, _, _, theo_d = controle(REPERE_D_EX1)
    ligne(ws2, ["TOTAL", brut_d, "", round(net_d, 2), 4, vol_d, theo_d],
          fill=sub, gras=True)
    ws2.append([])
    ligne(ws2, [f"Le total des quantites imprimees est {vol_d} cl : c'est exactement le "
                f"« volume consomme » de l'exercice 1 page 65."], fill=ok, gras=True)
    ligne(ws2, [f"La somme des articles de caisse est {brut_d} : c'est exactement le "
                f"« nombre de plats » de l'exercice 1 page 65."], fill=ok, gras=True)
    ligne(ws2, ["Les deux colonnes de la page 65 ne portent donc pas sur la meme "
                "population : le volume est calcule sur "
                f"{fr(net_d)} plats ponderes, le nombre de plats en affiche {brut_d}. "
                "La dose de 4 cl est bien appliquee ; c'est le denominateur imprime a cote "
                "qui n'est pas celui du calcul."], fill=ok)
    ligne(ws2, ["Cette explication n'est PAS donnee page 65 : elle doit etre reconstituee "
                "a partir de la page 44 de la proposition du 18/05/2026. La page 65 "
                "juxtapose les deux colonnes sans avertir que leurs perimetres different."],
          fill=alert)
    largeurs(ws2, [46, 20, 16, 18, 18, 20, 22])

    # ---- Feuille 3 : Reproductibilite des tableaux -----------------------
    ws3 = wb.create_sheet("Reproductibilite p.66-67")
    titre(ws3, "Les colonnes « Volume consomme total » sont-elles reproductibles ?",
          "Controle 1 : la somme imprimee (plats + verre) est-elle juste ? Controle 2 : "
          "le volume « plats » se retrouve-t-il en multipliant le nombre de plats imprime "
          "par la dose annoncee ? Controle 3 : le detail du repere, imprime dans la "
          "proposition pour l'exercice 1, redonne-t-il le chiffre ?")
    cols4 = ["Alcool", "Page", "Exercice", "Volume plats (cl)", "Volume verre (cl)",
             "Total imprime (cl)", "Somme recalculee (cl)", "Addition juste ?",
             "Nb plats imprime", "Dose annoncee", "Dose implicite plats / nb plats (cl)",
             "Volume disponible (cl)"]
    entete(ws3, cols4)
    for alc, page, exo, vplats, vverre, tot, nplats, dispo, dose_ann in TABLEAUX:
        somme = vplats + vverre
        juste = "oui" if somme == tot else f"NON ({somme})"
        if "/" in nplats:
            a, b = [int(x.replace(" ", "")) for x in nplats.split("/")]
            implicite = ""
            recalc = a * 1 + b * 10
            dose_txt = f"1x{a} + 10x{b} = {recalc} cl"
        else:
            n = int(nplats.replace(" ", ""))
            implicite = round(vplats / n, 4)
            dose_txt = ""
        r = ligne(ws3, [alc, page, exo, vplats, vverre, tot, somme, juste, nplats,
                        dose_ann, implicite if implicite != "" else dose_txt, dispo],
                  fill=ok if somme == tot else alert)
        if implicite != "":
            ws3.cell(row=r, column=11).number_format = '0.00'
    ws3.append([])

    titre(ws3, "Controle 3 : le detail imprime dans la proposition, exercice 1",
          "Les tableaux de reperes E (p. 45), G (p. 45) et Q (p. 48) sont imprimes pour "
          "l'exercice clos au 31/03/2023. On les rejoue ligne a ligne.")
    cols5 = ["Repere", "Article", "Nb articles caisse", "Proportion (*)",
             "Nb articles nets", "Dose (cl)", "Quantite imprimee (cl)",
             "Controle dose x nets (cl)"]
    entete(ws3, cols5)
    for rep, detail, page in (("E - Vin jaune", REPERE_E_EX1, 45),
                              ("G - Porto", REPERE_G_EX1, 45),
                              ("Q - Macvin", REPERE_Q_EX1, 48)):
        for art, n, prop, dose, q in detail:
            nets = n * prop if prop else n
            ligne(ws3, [rep, art, n, (f"{fr(prop * 100)} %" if prop else ""),
                        round(nets, 2), dose, q, round(nets * dose, 1)])
        vol, brut, net, theo = controle(detail)
        ligne(ws3, [rep, f"TOTAL (page {page} de la proposition)", brut, "",
                    round(net, 2), "", vol, theo],
              fill=sub, gras=True)
    ws3.append([])
    ligne(ws3, ["Vin jaune, exercice 1 : 1 507 plats a 1 cl + 221 plats a 10 cl = 3 717 cl. "
                "La colonne « plats » de la page 66 est exactement reproductible. Le "
                "1 507 inclut deja les 461 menus ponderes (955 + 91 + 461)."], fill=ok)
    ligne(ws3, ["Vin jaune, exercices 2 et 3 : 1 449 + 10 x 247 = 3 919 cl contre 3 693 cl "
                "imprimes ; 1 748 + 10 x 189 = 3 638 cl contre 3 748 cl imprimes. Ces deux "
                "lignes ne sont PAS reproductibles a partir des nombres imprimes : le "
                "detail des exercices 2 et 3 n'est pas publie."], fill=alert)
    ligne(ws3, ["Porto, exercice 1 : 398 cl = 1 cl x (33 + 238 + 37 + 17 + 73). Le 478 de la "
                "colonne « nombre de plats » est la somme BRUTE (33 + 238 + 37 + 17 + 153), "
                "menus non ponderes. Meme mecanique que le Calvados, non expliquee page 67."],
          fill=ok)
    ligne(ws3, ["Macvin, exercice 1 : 7 774 cl = 5 cl x (310 + 594 + 287 + 364), et le 2 400 "
                "de la colonne « nombre de plats » est la somme brute 310 + 594 + 748 + 748, "
                "ou les 748 menus sont comptes DEUX FOIS (une fois en plat, une fois en "
                "dessert). L'en-tete de la page 67 annonce pourtant « dose de 4 cl », quand "
                "la proposition p. 48 ecrit « 5 centilitres selon les dirigeants »."],
          fill=alert)
    largeurs(ws3, [22, 46, 18, 14, 16, 12, 20, 22])

    # ---- Feuille 4 : Doses implicites des annexes finales -----------------
    ws4 = wb.create_sheet("Doses implicites annexes")
    titre(ws4, "Annexes finales : dose implicite = volume / nombre d'articles",
          "Source : src/data/reconstitution-administration.json, transcription de "
          "Proposition_4_Annexes_Finales.pdf. Quand une proportion figure, la dose est "
          "aussi rapportee au nombre d'articles NET (nb x proportion).")
    cols6 = ["Ingredient", "Usage", "Nb articles", "Proportion", "Volume (cl)",
             "Dose brute volume / nb (cl)", "Dose nette volume / (nb x proportion) (cl)"]
    entete(ws4, cols6)
    lignes = doses_implicites_annexes()
    distinctes = set()
    for ref, usage, n, prop, vol, brut, net in lignes:
        if net is not None:
            distinctes.add(round(net, 1))
        elif brut is not None:
            distinctes.add(round(brut, 1))
        r = ligne(ws4, [ref, usage, n if n else "non indique",
                        (f"{fr(prop * 100)} %" if prop else ""), vol,
                        round(brut, 3) if brut else "non calculable",
                        round(net, 3) if net else ""])
        for c in (6, 7):
            ws4.cell(row=r, column=c).number_format = '0.000'
    ws4.append([])
    ligne(ws4, [f"Doses distinctes retrouvees dans cet extrait : "
                f"{', '.join(fr(d, 1) for d in sorted(distinctes))} cl."], gras=True)
    ligne(ws4, ["L'extrait des annexes finales couvre l'exercice clos au 31/03/2025 "
                "(volume disponible Macvin 27 150 cl, consommation cuisine 7 406 cl : "
                "ce sont les chiffres de l'exercice 3 du tableau de la page 67). La dose "
                "de Macvin y est de 4 cl, alors que la proposition page 48 applique 5 cl "
                "aux memes articles sur l'exercice 1."], fill=alert)
    ligne(ws4, ["Doses distinctes appliquees par le service a la CUISINE, tous documents "
                "confondus : 1 cl (sauces jurassienne, forestiere, morille), 1,14 cl "
                "(creme brulee absinthe), 2 cl (vin blanc du filet poulet et de la sauce "
                "vin jaune), 4 cl (flambages, babas, coupes, crepes, Macvin exercice 3, "
                "Calvados), 5 cl (Macvin exercice 1), 10 cl (fondues). Amplitude : de 1 a "
                "10 cl, soit un rapport de 1 a 10 pour des usages tous qualifies de "
                "« cuisine »."], fill=sub)
    largeurs(ws4, [16, 48, 14, 14, 14, 22, 26])

    # ---- Feuille 5 : Sources ----------------------------------------------
    ws5 = wb.create_sheet("Sources")
    titre(ws5, "Documents ouverts pour etablir cette piece",
          "Aucune valeur de ce classeur ne provient d'une autre source que celles-ci.")
    entete(ws5, ["Fichier", "Nature", "Pages ouvertes", "Ce qui en a ete tire"])
    for f, nat, pg, tire in SOURCES:
        ligne(ws5, [f, nat, pg, tire])
    ws5.append([])
    ligne(ws5, [f"Doses recensees : {len([d for d in DOSES if d[1] is not None])} valeurs "
                f"chiffrees sur {len(DOSES)} lignes ; "
                f"{sans_origine} portent la mention ORIGINE NON INDIQUEE."], gras=True)
    ligne(ws5, ["Script : scripts/reponse1-doses-origines.py (relancer le script "
                "reproduit ce fichier a l'identique)."])
    largeurs(ws5, [64, 42, 34, 90])

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    wb.save(OUT)
    return sans_origine


def main():
    print("== Calvados, courrier du 04/09/2026 page 65 ==")
    print("En-tete : « Volume consomme (a raison de 4 cl par plat) »")
    for lib, vol, plats, dispo in CALVADOS_P65:
        print(f"  {lib} : {vol} / {plats} = {fr(vol / plats)} cl "
              f"| 4 x {plats} = {4 * plats} cl (ecart {vol - 4 * plats} cl) "
              f"| disponible {dispo} cl")
    vol_d, brut_d, net_d, _ = controle(REPERE_D_EX1)
    print(f"  Repere D p.44 (exercice 1) : total quantites {vol_d} cl = volume p.65 ; "
          f"articles bruts {brut_d} = nombre de plats p.65 ; articles ponderes {fr(net_d)}")

    print("\n== Vin jaune p.66, Porto et Macvin p.67 ==")
    for alc, page, exo, vp, vv, tot, npl, dispo, dose in TABLEAUX:
        etat = "somme juste" if vp + vv == tot else f"SOMME FAUSSE ({vp + vv})"
        print(f"  {alc:22s} p.{page} {exo} : {vp} + {vv} = {tot} -> {etat} "
              f"| plats {npl} | dose annoncee {dose}")
    for nom, detail, page in (("E vin jaune", REPERE_E_EX1, 45),
                              ("G porto", REPERE_G_EX1, 45),
                              ("Q macvin", REPERE_Q_EX1, 48)):
        vol, brut, net, theo = controle(detail)
        print(f"  Repere {nom} p.{page} : total imprime {vol} cl | recalcul dose x nets "
              f"{theo} cl | articles bruts {brut} | articles ponderes {fr(net)}")
    print("  Vin jaune ex.1 : 1507 x 1 + 221 x 10 =", 1507 + 221 * 10, "cl (imprime 3717)")
    print("  Vin jaune ex.2 : 1449 x 1 + 247 x 10 =", 1449 + 247 * 10, "cl (imprime 3693)")
    print("  Vin jaune ex.3 : 1748 x 1 + 189 x 10 =", 1748 + 189 * 10, "cl (imprime 3748)")

    print("\n== Doses implicites des annexes finales ==")
    for ref, usage, n, prop, vol, brut, net in doses_implicites_annexes():
        if n:
            s = f"{vol}/{n} = {fr(brut, 3)} cl"
            if net:
                s += f" | net {vol}/({n} x {prop}) = {fr(net, 3)} cl"
        else:
            s = f"{vol} cl, nombre d'articles non indique -> dose non calculable"
        print(f"  {ref:12s} {usage[:46]:46s} {s}")

    n = ecrire()
    print(f"\necrit : {OUT}")
    print(f"{len(DOSES)} lignes de doses, dont {n} sans origine indiquee par le service")


if __name__ == "__main__":
    main()
