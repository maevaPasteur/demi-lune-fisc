# -*- coding: utf-8 -*-
"""
Source de vérité du rapprochement de noms : caisse <-> inventaire <-> factures.
canon = nom canonique (= nom inventaire s'il existe, sinon nom facture).
Chaque produit canonique porte : categorie, nom_inventaire, nom_facture, et un flag.
"""

# canonique -> (categorie, nom_inventaire, nom_facture, flag)
PRODUIT = {
 # ---- Vins rouges ----
 "Arbois Trousseau":("vin_rouge","Arbois Trousseau 75cl","ARBOIS TROUSSEAU 75 CL (J-L Tissot)",""),
 "Saint Joseph Rouge":("vin_rouge","Saint Joseph Rouge 75cl","SAINT JOSEPH ROUGE 75 CL (Ogier)",""),
 "Moulin à Vent":("vin_rouge","Moulin à Vent 75cl","MOULIN A VENT 75 CL",""),
 "Hautes Côtes de Beaune rouge":("vin_rouge","Hautes Côtes de Beaune 75cl","HTES COTES DE BEAUNE RGE 75 CL (Domaine Germain)",""),
 "Bordeaux Supérieur":("vin_rouge","Bordeaux Supérieur 75cl","BORDEAUX SUPERIEUR 75 CL (Château Grand Renom)","Libellé caisse 'Mouton Cadet' = Bordeaux Supérieur (confirmé)"),
 "Côtes du Rhône rouge maison (Chusclan)":("vin_rouge","Côtes du Rhône Rouge BIB 10L","BIB COTES DU RHONE ROUGE 10 L (Chusclan)","Vin maison rouge au verre/pichet"),
 # ---- Vins blancs ----
 "Arbois Savagnin":("vin_blanc","Arbois Savagnin 75cl","ARBOIS SAVAGNIN 75 CL","Servi aussi en pichet 50cl (depuis bouteille 75cl)"),
 "Arbois Béthanie":("vin_blanc","Arbois Béthanie 75cl","ARBOIS BETHANIE 75 CL / 37,5 CL",""),
 "Arbois Chardonnay":("vin_blanc","Arbois Chardonnay 75cl","ARBOIS CHARDONNAY 75 CL (J-L Tissot)",""),
 "Saint Véran":("vin_blanc","Saint Véran 75cl","SAINT VERAN 75 CL (Lupé Cholet)",""),
 "Chablis":("vin_blanc","Chablis 75cl","CHABLIS 75 CL",""),
 "Gewurztraminer":("vin_blanc","Gewurztraminer 75cl","GEWURZTRAMINER 75 CL (Les Sorcières)",""),
 "Macon":("vin_blanc","Macon 75cl","MACON 75 CL",""),
 "Grand Pavois":("vin_blanc","Grand Pavois 75cl","GRAND PAVOIS N°8 BLANC 75 CL",""),
 "Hautes Côtes de Beaune blanc":("vin_blanc","Haute Côte de Beaune 75cl","HTES COTES DE BEAUNE BLC 75 CL (Domaine Germain)",""),
 "Hautes Côtes de Nuits blanc":("vin_blanc",None,"HTES CTES DE NUITS BLANC 75 CL (Lupé Cholet)","ABSENT de l'inventaire (présent en facture) - distinct de Beaune"),
 "Bourgogne Aligoté maison":("vin_blanc","Bourgogne Aligoté BIB 10L","BIB BOURGOGNE ALIGOTE 10 L","Vin maison blanc au verre/pichet"),
 # ---- Vins rosés ----
 "Rosé Les Jamelles (Clair de Rosé)":("vin_rose","Rosé Les Jamelles 75cl","ROSE GRENACHE JAMELLES 75 CL (Clair de Rosé)",""),
 "Bohème Rosé (Le Pive)":("vin_rose","Bohème Rosé (Le Pive) 75cl","ROSE DOM LE PIVE 75 CL",""),
 "Rosé Le Pive":("vin_rose","Rosé Le Pive 75cl","ROSE DOM LE PIVE 75 CL",""),
 "Côtes de Provence Rosé Minuty":("vin_rose","Côtes de Provence Rosé Minuty 75cl","COTES DE PROVENCE ROSE 75 CL (M de Minuty)",""),
 "Miraval Rosé":("vin_rose",None,"MIRAVAL ROSE 75 CL CÔTES DE PROVENCE AOP","ABSENT de l'inventaire (présent en facture)"),
 "Côtes de Provence rosé maison (Cap des Pins)":("vin_rose","Côtes de Provence Rosé BIB 10L","BIB COTES DE PROV ROSE 10 L (Cap des Pins)","Vin maison rosé au verre/pichet"),
 # ---- Spécialités / vins du Jura ----
 "Macvin":("vin_de_liqueur","Macvin 75cl","MACVIN BLANC 75 CL (Domaine Rolet)",""),
 "Vin de Paille":("vin","Vin de Paille 37,5cl","VIN DE PAILLE 37,5 CL",""),
 "Arbois Vin Jaune":("vin","Arbois Vin Jaune 62cl","ARBOIS VIN JAUNE 62 CL (J-L Tissot)",""),
 "Ravelin":("vin","Ravelin Blanc 99cl","BIB BLANC 10 L RAVELIN (André Bonnot) / RAVELIN 99 CL","Vin de cuisson fondues"),
 # ---- Pétillants ----
 "Crémant du Jura":("petillant","Crémant du Jura 75cl","CREMANT DU JURA 75 CL (Arbois)",""),
 "Champagne":("petillant","Champagne Jean Sandrin 75cl","CHAMPAGNE JEAN SANDRIN 75 CL / CHAMPAGNE LANSON 75 CL","Jean Sandrin OU Lanson selon stock"),
 "Cidre Brut":("cidre","Cidre Brut 75cl","CIDRE BRUT 75 CL",""),
 "Cidre Doux":("cidre","Cidre Doux 75cl","CIDRE DOUX 75 CL",""),
 "Cidre La Mordue":("cidre","Cidre La Mordue 27cl","CIDRE LA MORDUE 27 CL",""),
 # ---- Bières ----
 "Fût Affligem":("biere","Fût Affligem 8L","FUT AFFLIGEM BLADE 8 L 6,7°","Pression/pinte/panaché/picon/monaco"),
 "Rouget de Lisle Ambrée 33cl":("biere","Rouget de Lisle Ambrée 33cl","LA ROUGET AMBREE 33 CL VP",""),
 "Rouget de Lisle Blanche 33cl":("biere","Rouget de Lisle Blanche 33cl","LA ROUGET BLANCHE 33 CL VP",""),
 # ---- Apéritifs / spiritueux ----
 "Porto":("aperitif","Porto 75cl","PORTO SANDEMAN ROUGE 75 CL",""),
 "Martini Blanc":("aperitif","Martini Blanc 100cl","MARTINI BIANCO 100 CL",""),
 "Pastis 51":("aperitif","Pastis 51 100cl","PASTIS 51 100 CL",""),
 "Ricard":("aperitif","Ricard 100cl","RICARD 100 CL",""),
 "Pontarlier Anis":("aperitif","Pontarlier Anis 100cl","PONTARLIER ANIS 100 CL",""),
 "Clan Campbell":("spiritueux","Clan Campbell 70cl","CLAN CAMPBELL 70 CL 40°","Libellé caisse 'Whisky L.J / Long John' ; SEUL whisky acheté = Clan Campbell"),
 "Jack Daniel's":("spiritueux","Jack Daniel's 70cl","JACK DANIEL'S 70 CL",""),
 "Tequila Camino Real":("spiritueux",None,"TEQUILA CAMINO REAL 70 CL 35°","ABSENT de l'inventaire (présent en facture)"),
 "Vodka":("spiritueux","Vodka 70cl","VODKA POLIAKOV 70 CL",""),
 # ---- Digestifs / liqueurs ----
 "Bailey's":("liqueur","Bailey's 70cl","BAILEY'S 70 CL",""),
 "Calvados":("eau_de_vie","Calvados 100cl","CALVADOS BEAUJOUR 100 CL 40°",""),
 "Cognac":("eau_de_vie","Cognac 70cl","COGNAC PARK 70 CL",""),
 "Eau de Vie de Poire":("eau_de_vie","Eau de Vie de Poire 70cl","EAU DE VIE DE POIRE 70 CL",""),
 "Eau de Vie Framboise":("eau_de_vie","Eau de Vie Framboise 70cl","EAU DE VIE FRAMBOISE 70 CL",""),
 "Eau de Vie Mirabelle":("eau_de_vie","Eau de Vie Mirabelle 70cl","EAU DE VIE MIRABELLE 70 CL",""),
 "Marc du Jura":("eau_de_vie","Marc du Jura 70cl","MARC DU JURA 70 CL (Tissot)",""),
 "Marc de Bourgogne":("eau_de_vie","Marc de Bourgogne 70cl","MARC DE BOURGOGNE 70 CL",""),
 "Get 27":("liqueur","Get 27 70cl","GET 27 70 CL",""),
 "Get 31":("liqueur","Get 31 70cl","GET 31 70 CL",""),
 "Génépi":("liqueur","Génépi 70cl","GENEPI 70 CL",""),
 "Grand Marnier":("liqueur","Grand Marnier 70cl","GRAND MARNIER CORDON ROUGE 70 CL 40°",""),
 "Liqueur de Poire":("liqueur","Liqueur de Poire 70cl","LIQUEUR DE POIRE WILLIAM 70 CL",""),
 "Liqueur de Sapin":("liqueur","Liqueur de Sapin 70cl","LIQUEUR DE SAPIN 70 CL",""),
 "Liqueur de Cerise":("liqueur","Liqueur de Cerise 70cl","LIQUEUR DE CERISE 70 CL",""),
 "Soho Litchi":("liqueur","Soho Litchi 70cl","SOHO LITCHI 70 CL 15°",""),
 "Passoa":("liqueur","Passoa 70cl","PASSOA 70 CL 15°",""),
 "Crème de Cassis":("liqueur","Crème de Cassis 70cl","CREME CASSIS BRIOTTET 20° 70 CL",""),
 "Picon":("aperitif","Picon 100cl","PICON BIERE 100 CL 18°",""),
 "Guignolet":("liqueur","Liqueur de Cerise 70cl","LIQUEUR DE CERISE 70 CL","Guignolet (cerise) rattaché à Liqueur de Cerise - 1 unité"),
 # ---- Cubis générique (couleur inconnue) ----
 "Cubis de vin (couleur non précisée)":("vin",None,None,"Couleur non récupérable en caisse - rapprochement manuel inventaire/factures"),
 # ---- Sirops / jus / sodas (ingrédients cocktails, sans alcool) ----
 "Sirop Châtaigne":("sirop","Monin Châtaigne 100cl","MONIN CHATAIGNE 100 CL",""),
 "Sirop Framboise":("sirop","Monin Framboise 100cl","MONIN FRAMBOISE 100 CL",""),
 "Sirop Curaçao bleu":("sirop","Monin Curaçao 100cl","MONIN CURACAO 100 CL",""),
 "Sirop Grenadine":("sirop","Monin Grenadine 100cl","MONIN GRENADINE 100 CL",""),
 "Sirop Pamplemousse":("sirop","Monin Pamplemousse 100cl","MONIN PAMPLEMOUSSE 100 CL",""),
 "Jus d'orange":("jus","Granini Jus Orange 1L","GRANINI JUS ORANGE 1 L",""),
 "Jus d'ananas":("jus","Granini Jus Ananas 1L","GRANINI JUS ANANAS 1 L",""),
 "Jus de pomme":("jus","Granini Jus Pomme 1L","GRANINI JUS POMME 1 L",""),
 "Jus de poire":("jus","Jus de Poire 1L","JUS DE POIRE 100 CL",""),
 "Jus de fraise":("jus","Granini Fraise 25cl","GRANINI FRAISE 25 CL",""),
 "Jus de framboise":("jus","Granini Framboise 25cl","GRANINI FRAMBOISE 25 CL",""),
 "Limonade":("soda","Limonade Mortuacienne 1L","LIMONADE MORTUACIENNE 1 L",""),
 "Coca":("soda","Coca-Cola 33cl","COCA-COLA 33 CL",""),
}

# Libellé caisse exact -> (canonique, format_service, volume_cl)
CAISSE2CANON = {
 # Vins rouges
 "Arbois Trousseau Le":("Arbois Trousseau","Verre",15),"PiCHET TROUSSEAU":("Arbois Trousseau","Pichet 50cl",50),"Arbois Trousseau Bou":("Arbois Trousseau","Bouteille",75),
 "C du  Rhone St Josep":("Saint Joseph Rouge","Verre",15),"C du Rhone St  Josep":("Saint Joseph Rouge","Bouteille",75),"pichet Saint Joseph":("Saint Joseph Rouge","Pichet 50cl",50),
 "Beaujolais Moulin à":("Moulin à Vent","Verre",15),"PICHET MOULIN A VENT":("Moulin à Vent","Pichet 50cl",50),
 "H.C.DE BEAUNE  VERRE":("Hautes Côtes de Beaune rouge","Verre",15),"VERRE H.C.DE BEAUNE":("Hautes Côtes de Beaune rouge","Verre",15),"PICHET C.DE BEAUNE R":("Hautes Côtes de Beaune rouge","Pichet 50cl",50),"PICHET HCB":("Hautes Côtes de Beaune rouge","Pichet 50cl",50),"H.C.B BEAUNE BTL":("Hautes Côtes de Beaune rouge","Bouteille",75),"H.C.BEAUNE BOUTEILLE":("Hautes Côtes de Beaune rouge","Bouteille",75),
 "BORD.  MOUTON CADET":("Bordeaux Supérieur","Bouteille",75),
 "LA COTE ROUGE":("Bordeaux Supérieur","Bouteille",75),
 "Pichet CHUSLAN":("Côtes du Rhône rouge maison (Chusclan)","Pichet 50cl",50),"Pichet CdR CHUSCLAN":("Côtes du Rhône rouge maison (Chusclan)","Pichet 50cl",50),"VERRE CHUSCLAN":("Côtes du Rhône rouge maison (Chusclan)","Verre",15),"Verre CHUSCLAN":("Côtes du Rhône rouge maison (Chusclan)","Verre",15),
 # Vins blancs
 "Savagnin verre":("Arbois Savagnin","Verre",15),"PICHET SAVAGNIN":("Arbois Savagnin","Pichet 50cl",50),"Arbois Savagnin":("Arbois Savagnin","Bouteille",75),
 "1/2 Arbois Béthanie":("Arbois Béthanie","Demi-bouteille",37.5),"Arbois Béthanie":("Arbois Béthanie","Bouteille",75),
 "Arbois Chardonnay Le":("Arbois Chardonnay","Verre",15),
 "Saint Véran Verre":("Saint Véran","Verre",15),"Saint Véran":("Saint Véran","Bouteille",75),"PICHET SAINT VERAN":("Saint Véran","Pichet 50cl",50),
 "Chablis Le Verre":("Chablis","Verre",15),"Chablis":("Chablis","Bouteille",75),"Pichet Chablis":("Chablis","Pichet 50cl",50),
 "Gewurztraminer Le ve":("Gewurztraminer","Verre",15),"Alsace Gewurztramine":("Gewurztraminer","Bouteille",75),"PICHET GEWURZTRAMINE":("Gewurztraminer","Pichet 50cl",50),
 "MACON VERRE":("Macon","Verre",15),"MACON bouteille":("Macon","Bouteille",75),"PICHET MACON":("Macon","Pichet 50cl",50),
 "GASCOGNE Gd PAVOIS":("Grand Pavois","Bouteille",75),
 "PICHET C.DE BEAUNE B":("Hautes Côtes de Beaune blanc","Pichet 50cl",50),
 "H.COTES DE NUITS":("Hautes Côtes de Nuits blanc","Bouteille",75),
 "Verre ALIGOTE":("Bourgogne Aligoté maison","Verre",15),"PICHET ALIGOTE 50cL":("Bourgogne Aligoté maison","Pichet 50cl",50),
 # Vins rosés
 "Clair de Rosé":("Rosé Les Jamelles (Clair de Rosé)","Bouteille",75),
 "Bohème":("Bohème Rosé (Le Pive)","Bouteille",75),
 "DOMAINE LE PIVE":("Rosé Le Pive","Bouteille",75),
 "Chateau Minuty":("Côtes de Provence Rosé Minuty","Bouteille",75),"Mminuty":("Côtes de Provence Rosé Minuty","Bouteille",75),
 "MIRAVAL":("Miraval Rosé","Bouteille",75),
 "VERRE ROSE":("Côtes de Provence rosé maison (Cap des Pins)","Verre",15),"Verre Rosé":("Côtes de Provence rosé maison (Cap des Pins)","Verre",15),
 "VERRE ROSE/PICHET C.DE BEAUNE R":("Côtes de Provence rosé maison (Cap des Pins)","Verre",15),  # corruption de lecture (réf 2088 = VERRE ROSE)
 "PICHET ROSE":("Côtes de Provence rosé maison (Cap des Pins)","Pichet 50cl",50),
 # Pichets génériques sans couleur
 "Verre de vin":("Cubis de vin (couleur non précisée)","Verre",15),"Pichet 50cl vin":("Cubis de vin (couleur non précisée)","Pichet 50cl",50),"Pichet 75cl vin":("Cubis de vin (couleur non précisée)","Pichet 75cl",75),
 # Pétillants
 "Crémant":("Crémant du Jura","Verre",10),"Crément / Jura VERRE":("Crémant du Jura","Verre",10),"Crémant du Jura":("Crémant du Jura","Bouteille",75),"Crément du Jura":("Crémant du Jura","Bouteille",75),"Crémant Rosé":("Crémant du Jura","Bouteille",75),
 "Champagne":("Champagne","Verre",12),'"Champagne Brut "':("Champagne","Bouteille",75),
 "Cidre Bouché Brut":("Cidre Brut","Bouteille",75),"Cidre Bouché Doux":("Cidre Doux","Bouteille",75),"cidre la Mordue":("Cidre La Mordue","Bouteille 27cl",27),
 # Spécialités
 "Macvin du Jura":("Macvin","Verre",6),"Vin de Paille":("Vin de Paille","Verre",6),"VIN PAILLE":("Vin de Paille","Verre",6),"Vin jaune":("Arbois Vin Jaune","Verre",12),"Pontarlier":("Pontarlier Anis","Verre",2),
 # Autres apéritifs / spiritueux secs
 "Porto":("Porto","Verre",6),"Martini Blanc":("Martini Blanc","Verre",6),"Pastis":("Pastis 51","Verre",2),"Ricard":("Ricard","Verre",2),
 "Jack Daniel's":("Jack Daniel's","Verre",4),"Whisky L.J (4cl)":("Clan Campbell","Verre",4),"Whisky L.J (2cl) Bab":("Clan Campbell","Verre",2),
 # Digestifs
 "Baileys":("Bailey's","Verre",4),"BAILEYS":("Bailey's","Verre",4),"Calvados":("Calvados","Verre",4),"Calvados (4cl)":("Calvados","Verre",4),"Cognac (4cl)":("Cognac","Verre",4),
 "Eau de Vie de Poire":("Eau de Vie de Poire","Verre",4),"Eau de vie Framboise":("Eau de Vie Framboise","Verre",4),"Eau de vie Mirabelle":("Eau de Vie Mirabelle","Verre",4),
 "Get 27 (4cl)":("Get 27","Verre",4),"Get 31":("Get 31","Verre",4),"Génépi":("Génépi","Verre",4),"Grand Marnier":("Grand Marnier","Verre",4),"GRAND MARNIER":("Grand Marnier","Verre",4),
 "Liqueur de Poire":("Liqueur de Poire","Verre",4),"Liqueur de Sapin":("Liqueur de Sapin","Verre",4),"Marc du Jura (4cl)":("Marc du Jura","Verre",4),"Vieux Marc Bourgogne":("Marc de Bourgogne","Verre",4),
 "TEQUILA":("Tequila Camino Real","Verre",4),"Guignolet":("Guignolet","Verre",4),
 # Bières
 "pression":("Fût Affligem","Pression 25cl",25),"Pinte":("Fût Affligem","Pinte 50cl",50),"Panaché":("Fût Affligem","Panaché 25cl",25),"Monaco":("Fût Affligem","Monaco 25cl",25),
 "Picon bière":("Fût Affligem","Demi+Picon 25cl",25),"Pinte Picon":("Fût Affligem","Pinte+Picon 50cl",50),
 "Ambrée":("Rouget de Lisle Ambrée 33cl","Bouteille 33cl",33),"Blanche des plateaux":("Rouget de Lisle Blanche 33cl","Bouteille 33cl",33),
}

# Noms d'ingrédients (recettes cocktails) et types (plats/menus) -> canonique
INGREDIENT2CANON = {
 "Crémant":"Crémant du Jura","Macvin":"Macvin","Crème de cassis":"Crème de Cassis","Aligoté":"Bourgogne Aligoté maison",
 "Soho (liqueur de litchi)":"Soho Litchi","Liqueur de litchi":"Soho Litchi","Liqueur de cerise":"Liqueur de Cerise",
 "Passoa":"Passoa","Vodka":"Vodka","Tequila":"Tequila Camino Real","Pontarlier":"Pontarlier Anis","Liqueur de sapin":"Liqueur de Sapin",
 "Picon":"Picon","Bière (fût)":"Fût Affligem","Côtes de Provence rosé":"Côtes de Provence rosé maison (Cap des Pins)",
 "Whisky":"Clan Campbell",
 "Sirop de châtaigne":"Sirop Châtaigne","Sirop de framboise":"Sirop Framboise","Sirop curaçao bleu":"Sirop Curaçao bleu","Sirop de grenadine":"Sirop Grenadine","Sirop de pamplemousse":"Sirop Pamplemousse",
 "Jus d'orange":"Jus d'orange","Jus d'ananas":"Jus d'ananas","Jus de pomme":"Jus de pomme","Jus de poire":"Jus de poire","Jus de fraise":"Jus de fraise","Jus de framboise":"Jus de framboise",
 "Limonade":"Limonade","Coca":"Coca",
 # types plats/menus
 "Porto":"Porto","Ravelin":"Ravelin","Vin jaune":"Arbois Vin Jaune","Calvados":"Calvados","Baileys":"Bailey's",
 "Marc de bourgogne":"Marc de Bourgogne","Liqueur de poire":"Liqueur de Poire","Grand Marnier":"Grand Marnier",
}

def ref(canon):
    cat,inv,fac,flag = PRODUIT.get(canon,("?",None,None,"CANONIQUE INCONNU"))
    return {"canonique":canon,"categorie":cat,"nom_inventaire":inv,"nom_facture":fac,"flag":flag}

# Prix de revente carte (canonique -> (contenance_service_cl, prix_€)). Prix carte 26/04/2023.
# Absents = non vendus seuls (ingrédients cocktails, Ravelin de cuisson) ou hors carte (Champagne, Minuty).
CARTE_PRIX = {
 "Arbois Trousseau":(15,6.4),"Saint Joseph Rouge":(15,7.2),"Moulin à Vent":(15,5.8),
 "Hautes Côtes de Beaune rouge":(15,7.9),"Hautes Côtes de Beaune blanc":(15,7.9),"Hautes Côtes de Nuits blanc":(15,7.9),
 "Bordeaux Supérieur":(75,36.0),"Arbois Chardonnay":(75,24.9),"Arbois Béthanie":(75,29.9),
 "Arbois Savagnin":(15,7.2),"Saint Véran":(15,7.9),"Chablis":(15,7.9),"Gewurztraminer":(15,7.0),
 "Macon":(15,6.3),"Grand Pavois":(75,22.0),
 "Rosé Les Jamelles (Clair de Rosé)":(75,18.0),"Bohème Rosé (Le Pive)":(75,29.0),"Rosé Le Pive":(75,29.0),"Miraval Rosé":(75,45.0),
 "Bourgogne Aligoté maison":(15,3.9),"Côtes du Rhône rouge maison (Chusclan)":(15,3.9),"Côtes de Provence rosé maison (Cap des Pins)":(15,3.9),
 "Crémant du Jura":(12,3.9),
 "Macvin":(6,4.9),"Vin de Paille":(6,6.0),"Arbois Vin Jaune":(12,12.0),"Pontarlier Anis":(2,3.8),
 "Pastis 51":(2,3.8),"Ricard":(2,3.8),"Porto":(6,3.8),"Martini Blanc":(6,3.8),
 "Clan Campbell":(4,5.8),"Jack Daniel's":(4,7.5),
 "Bailey's":(4,5.2),"Calvados":(4,6.9),"Cognac":(4,5.2),"Get 27":(4,5.2),"Get 31":(4,5.2),
 "Génépi":(4,6.5),"Grand Marnier":(4,5.2),"Marc du Jura":(4,6.5),"Marc de Bourgogne":(4,5.2),
 "Eau de Vie de Poire":(4,6.5),"Eau de Vie Mirabelle":(4,6.5),"Eau de Vie Framboise":(4,6.5),
 "Liqueur de Poire":(4,6.5),"Liqueur de Sapin":(4,5.2),
 "Fût Affligem":(25,3.9),"Rouget de Lisle Ambrée 33cl":(33,5.9),"Rouget de Lisle Blanche 33cl":(33,5.9),
 "Cidre Brut":(75,14.0),"Cidre Doux":(75,16.0),"Cidre La Mordue":(27.5,4.0),
 "Coca":(33,3.9),"Limonade":(25,3.9),
 # Sirops vendus "Sirop à l'eau" 25cl 2,2€ (même prix pour tous). Dose de sirop par verre ~2cl (standard bar).
 "Sirop Châtaigne":(2,2.2),"Sirop Framboise":(2,2.2),"Sirop Curaçao bleu":(2,2.2),"Sirop Grenadine":(2,2.2),"Sirop Pamplemousse":(2,2.2),
 # Jus vendus "Jus de Fruits au choix" 25cl 3,9€ (jus non dilué)
 "Jus d'orange":(25,3.9),"Jus d'ananas":(25,3.9),"Jus de pomme":(25,3.9),"Jus de poire":(25,3.9),"Jus de fraise":(25,3.9),"Jus de framboise":(25,3.9),
}
