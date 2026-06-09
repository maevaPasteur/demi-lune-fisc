# -*- coding: utf-8 -*-
"""Mapping EXPLICITE : produit d'achat (facture) -> nom canonique de boisson.
Règles ordonnées (spécifique avant générique). na() = minuscule sans accent.
Sert à inclure TOUTES les boissons achetées dans le rapprochement, avec un mapping contrôlé."""
import re,unicodedata
def na(s): return ''.join(c for c in unicodedata.normalize('NFD',str(s)) if unicodedata.category(c)!='Mn').lower()

# (motif regex sur na(designation), canonique). Premier match gagne.
RULES = [
 # --- Jura spécialités ---
 (r"macvin.*rose|macvin du jura rose","Macvin rosé"),
 (r"macvin","Macvin"),
 (r"vin\s*jaune","Arbois Vin Jaune"),
 (r"vin de paille|vin paille|paille 37","Vin de Paille"),
 (r"ravelin","Ravelin"),
 # --- Vins rouges nommés ---
 (r"trousseau","Arbois Trousseau"),
 (r"saint joseph|st joseph","Saint Joseph Rouge"),
 (r"moulin a vent","Moulin à Vent"),
 (r"cotes de beaune.*(blc|blanc)|beaune blc","Hautes Côtes de Beaune blanc"),
 (r"cotes de beaune|hcb|beaune rge","Hautes Côtes de Beaune rouge"),
 (r"nuits","Hautes Côtes de Nuits blanc"),
 (r"auxey|duresses","Auxey-Duresses (rouge)"),
 (r"cote rouge","La Côte Rouge"),
 (r"arbois rouge|rouge tradition","Arbois Rouge Tradition"),
 (r"bordeaux superieur|mouton cadet","Bordeaux Supérieur"),
 # --- Vins blancs nommés ---
 (r"chardonnay.*jamelles","Chardonnay Les Jamelles"),
 (r"chardonnay","Arbois Chardonnay"),
 (r"bethanie","Arbois Béthanie"),
 (r"savagnin","Arbois Savagnin"),
 (r"saint veran|st veran","Saint Véran"),
 (r"chablis","Chablis"),
 (r"gewurztraminer|gewurz","Gewurztraminer"),
 (r"macon","Macon"),
 (r"grand pavois|gascogne|pavois","Grand Pavois"),
 (r"sauternes","Sauternes"),
 # --- Pétillants / champagnes ---
 (r"champagne.*ruinart|ruinart","Champagne Ruinart"),
 (r"champagne.*lanson|lanson","Champagne Lanson"),
 (r"champagne","Champagne"),
 (r"cremant|crement","Crémant du Jura"),
 # --- Vins maison (BIB) ---
 (r"aligote","Bourgogne Aligoté maison"),
 (r"cotes du rhone rouge|chusclan|chuslan","Côtes du Rhône rouge maison (Chusclan)"),
 (r"cap des pins","Côtes de Provence rosé maison (Cap des Pins)"),
 # --- Rosés ---
 (r"jamelles|clair de rose","Rosé Les Jamelles (Clair de Rosé)"),
 (r"boheme gris","Bohème Gris"),
 (r"le pive|dom le pive|boheme rose","Rosé Le Pive"),
 (r"minuty","Côtes de Provence Rosé Minuty"),
 (r"miraval","Miraval Rosé"),
 (r"gourmandise","Gourmandise Rosé"),
 (r"gassier|esprit gassier","Rosé Esprit Gassier"),
 (r"gardilles","Rosé Gardilles (BIB)"),
 (r"masterel|haut masterel","Rosé Haut Masterel (BIB)"),
 # --- Cidres ---
 (r"mordue","Cidre La Mordue"),
 (r"(bolee|contemporaine|val de rance).*doux|doux.*(bolee|contemporaine|rance)|cidre doux","Cidre Doux"),
 (r"bolee|armoriq|cidre brut","Cidre Brut"),
 (r"val de rance","Cidre Val de Rance"),
 # --- Bières ---
 (r"affligem","Fût Affligem"),
 (r"rouget.*ambree|ambree.*rouget","Rouget de Lisle Ambrée 33cl"),
 (r"rouget.*blanche|blanche.*rouget","Rouget de Lisle Blanche 33cl"),
 (r"mort subite","Bière Mort Subite (perso)"),
 (r"mont blanc|bleue du mont","Bière Bleue du Mont Blanc (perso)"),
 (r"sziget","Bière Sziget (perso)"),
 (r"white rabbit","Bière White Rabbit (perso)"),
 (r"fut heineken|heineken.*fut","Fût Heineken (perso)"),
 (r"heineken","Bière Heineken bouteille (perso)"),
 (r"1664","Bière 1664 (perso)"),
 (r"grimbergen","Bière Grimbergen (perso)"),
 (r"blanche des neiges","Bière Blanche des Neiges (perso)"),
 (r"biere blanche.*(baume|abbaye)|abbaye de baume","Bière Blanche Baume (perso)"),
 # --- Apéritifs / spiritueux ---
 (r"aperol","Aperol"),
 (r"porto","Porto"),
 (r"martini","Martini Blanc"),
 (r"pastis","Pastis 51"),
 (r"ricard","Ricard"),
 (r"pontarlier","Pontarlier Anis"),
 (r"clan campbell","Clan Campbell"),
 (r"jack daniel","Jack Daniel's"),
 (r"tequila","Tequila Camino Real"),
 (r"vodka","Vodka"),
 (r"passoa","Passoa"),
 (r"soho","Soho Litchi"),
 (r"cognac","Cognac"),
 (r"calvados","Calvados"),
 # --- Digestifs / liqueurs / eaux de vie ---
 (r"get 27","Get 27"),
 (r"get 31","Get 31"),
 (r"genepi","Génépi"),
 (r"grand marnier|gd marnier","Grand Marnier"),
 (r"marc du jura","Marc du Jura"),
 (r"marc de bourgogne","Marc de Bourgogne"),
 (r"sapin","Liqueur de Sapin"),
 (r"golden eight|(liqueur.*poire)|(poire william.*25)","Liqueur de Poire"),
 (r"poire william","Eau de Vie de Poire"),
 (r"mirabelle","Eau de Vie Mirabelle"),
 (r"framboise","Eau de Vie Framboise"),
 (r"capucine creme cassis|creme cassis|cassis briottet","Crème de Cassis"),
 (r"creme cerise|cerise","Liqueur de Cerise"),
 (r"creme mure|mure","Crème de Mûre"),
 (r"baileys|bailey","Bailey's"),
 (r"picon","Picon"),
 (r"absinthe","Absinthe"),
 (r"terrasses","Terrasses Rosé"),
]
# Marques NON ALCOOL (softs/eaux/jus/sirops/chaud) : testées EN TÊTE, avant les fruits alcoolisés (framboise, mûre...)
NONALC_RULES = [
 (r"fanta|fuzetea|orangina|schweppes|sprite|tropico|volvic","Sodas divers (canette/PET)"),
 (r"perrier|pellegrino|pelegrino|vittel|badoit|carola","Eaux minérales (divers)"),
 (r"granini|pulco","Jus / Nectars (divers)"),
 (r"monin|routin","Sirops Monin/Routin (divers)"),
 (r"malongo|infusion|verveine|camomille|tilleul|peppermint|jasmin|kusmi|segafredo|baronny|the noir|the vert|the jardin|\bcafe\b|\bthe\b","Café / Thé / Infusions"),
]
# Produits canoniques NOUVEAUX (achetés mais non vendus en caisse, absents de consoTotale)
NOUVEAUX = {"Macvin rosé","Auxey-Duresses (rouge)","La Côte Rouge","Arbois Rouge Tradition",
 "Chardonnay Les Jamelles","Champagne Ruinart","Champagne Lanson","Bohème Gris","Rosé Esprit Gassier",
 "Rosé Gardilles (BIB)","Rosé Haut Masterel (BIB)","Cidre Val de Rance","Aperol","Crème de Mûre",
 "Bière Mort Subite (perso)","Bière Bleue du Mont Blanc (perso)","Bière Sziget (perso)","Bière White Rabbit (perso)",
 "Fût Heineken (perso)","Bière Heineken bouteille (perso)","Bière 1664 (perso)","Bière Grimbergen (perso)",
 "Bière Blanche des Neiges (perso)","Bière Blanche Baume (perso)","Sauternes","Absinthe","Terrasses Rosé"}
# Canoniques NON ALCOOL (softs) : disparu non significatif (boutons caisse génériques)
NONALC = {"Sodas divers (canette/PET)","Eaux minérales (divers)","Jus / Nectars (divers)",
 "Sirops Monin/Routin (divers)","Café / Thé / Infusions"}

def canon_achat(designation):
    d=na(designation)
    # 1) marques softs EN TÊTE (Monin/Routin/Granini/sodas/eaux/café) avant les fruits alcoolisés
    for pat,c in NONALC_RULES:
        if re.search(pat,d): return c
    # 2) garde-fous : sirops/jus VENDUS mappés EXPLICITEMENT (évite collision avec eaux-de-vie/liqueurs homonymes)
    if re.search(r"\bsirop\b",d) and not re.search(r"monin|routin",d):
        if "chataigne" in d: return "Sirop Châtaigne"
        if "curacao" in d or "bleu" in d: return "Sirop Curaçao bleu"
        if "framboise" in d: return "Sirop Framboise"
        if "grenadine" in d: return "Sirop Grenadine"
        if "pamplem" in d: return "Sirop Pamplemousse"
        return None
    if re.search(r"\bjus\b",d) and not re.search(r"granini|pulco",d):
        if "orange" in d: return "Jus d'orange"
        if "ananas" in d: return "Jus d'ananas"
        if "fraise" in d: return "Jus de fraise"
        if "framboise" in d: return "Jus de framboise"
        if "poire" in d: return "Jus de poire"
        if "pomme" in d: return "Jus de pomme"
        return None
    for pat,c in RULES:
        if re.search(pat,d): return c
    return None
