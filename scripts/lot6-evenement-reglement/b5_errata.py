"""Lot 2.6, mission 4 : errata R3 des pièces 72, 89, 90, 91.
Copie de la pièce d'origine (public/documents/caisse-enregistreuse/), ajout d'un onglet « Erratum R2 » en tête par UNO (LibreOffice headless),
recalcul, enregistrement xlsx. Aucune cellule d'origine n'est touchée (contrôle : b5_errata_check.py).
Sources des corrections : sorties s06, s08, s09, t07 ; pieds des annexes B et C du service."""
import sys, os, shutil; sys.path.insert(0,'scripts/lot5-tva')
import uno
from b4_recalc import connect, pv
SRC='public/documents/caisse-enregistreuse/'; DST='public/documents/pieces-lot6/'
H=['Onglet de la pièce','Cellule(s)','Texte ou valeur de la pièce','Correction','Renvoi']
INTRO=('Onglet ajouté le 26/11/2026. Le contenu des autres onglets est inchangé, valeurs et formules comprises. '
       'Les corrections ci-dessous se lisent avec la section 2.6 de la réponse et les annexes 167 à 171.')
E={}
E['89']=('89-R2-fichiers-E-F-C-reconciliation-DEL-reglements-CA-quantites-TVA-3-exercices.xlsx',
         '89-R3-fichiers-E-F-C-reconciliation-DEL-reglements-CA-quantites-TVA-3-exercices-erratum.xlsx',[
 ('Calcul','B30, C30:E30','« TVA ligne à ligne, taux envoyés (SOMMEPROD) » : 45 711,80 / 49 774,68 / 49 003,27 €',
  'calcul sur la colonne 16 des annexes C, qui porte le taux de l\'article de la ligne précédente (décalage d\'une ligne) : grandeur sans signification fiscale','tableau 67 ; 161 ; point 2.5.6'),
 ('Calcul','B31, C31:E31','« TVA corrigée = TVA envoyée + colonne F » : 42 422,25 / 46 416,20 / 46 226,56 €',
  'artefact du même décalage, corrigé par la colonne F du service ; écarts au compte 445710 (42 614,45 / 46 464,79 / 46 005,45 €) : −192,20 / −48,59 / +221,11 €, qui se compensent','tableau 67'),
 ('Calcul','C34','144 489,75 €','même correction que C30:E30 (somme des trois exercices)','tableau 67'),
 ('Calcul','C35','135 065,01 €','coïncidence par compensation des écarts de C31:E31, et non concordance avec le compte 445710','tableau 67'),
 ('Calcul','B36, C36','« TVA collectée reversée (compte 445710, proposition p. 26) » : 135 084,69 €','« TVA comptabilisée (445710) » ; le montant est inchangé','tableau 67 ; proposition p. 26'),
 ('Calcul','B37, C37','« Écart TVA corrigée cumulée vs TVA reversée » : 19,68 €',
  'retiré. L\'écart pertinent est celui de la TVA légalement due (135 529,10 €) sur le compte 445710 (135 084,69 €) : 444,41 €','point 2.5.6 c ; tableau 67'),
 ('Methode','B14','contrôle de la TVA de l\'annexe C','ajouter « sur le champ décalé » : le calcul porte sur la colonne 16 décalée d\'une ligne','tableau 67'),
 ('Sources_C-1, Sources_C-2, Sources_C-3','A1','« Tot_rem_Ttc (CA, col.16) »','« Tot_rem_Ttc (CA, col. 17) »','annexes C1 à C3 du service'),
 ('Sources_C-1, Sources_C-2, Sources_C-3','E1','« Taux_TVA % (col.16) »','« Taux_TVA % (col. 16, décalé d\'une ligne) »','161'),
 ('Sources_C-1, Sources_C-2, Sources_C-3','F1, G1','« E = Erreur Taux TVA (col.21) » ; « F = Correction TVA (col.22) »',
  '22e et 23e colonnes des annexes C (colonnes du service intitulées E et F)','annexes C1 à C3 du service'),
 ('Calcul ; Remises','Calcul l. 6-7, 10-15, 18-24, 27-29 ; Remises l. 4-17','lignes citées par la section 2.6','confirmées, inchangées','section 2.6')])
E['90']=('90-R1-compteur-perpetuel-deux-series-quatre-montants-B-dans-C.xlsx',
         '90-R3-compteur-perpetuel-deux-series-quatre-montants-B-dans-C-erratum.xlsx',[
 ('7 - Colonne de contrôle','D2, E2 (B 2022-2023)','420 931,64 ; 17 561,22','pied du service (ligne TOTAL de l\'annexe B1) : 420 931,42 ; 17 561,00','tableau 65'),
 ('7 - Colonne de contrôle','D3, E3 (C 2022-2023)','403 370,68 ; 0,26 (en valeur absolue)','pied du service (annexe C1) : 403 370,38 ; −0,04','tableau 65'),
 ('7 - Colonne de contrôle','D4, E4 (B 2023-2024)','458 004,11 ; 20 011,19','pied du service (annexe B2) : 458 004,04 ; 20 011,12','tableau 65'),
 ('7 - Colonne de contrôle','D5, E5 (C 2023-2024)','438 325,78 ; 44,66','pied du service (annexe C2) : 438 325,70 ; 44,58','tableau 65'),
 ('7 - Colonne de contrôle','D6, E6 (B 2024-2025)','454 943,22 ; 20 115,36','pied du service (annexe B3) : 454 943,14 ; 20 115,28','tableau 65'),
 ('7 - Colonne de contrôle','D7, E7 (C 2024-2025)','435 696,12 ; 131,16','pied du service (annexe C3) : 435 696,04 ; 131,08','tableau 65'),
 ('7 - Colonne de contrôle','F2:F7','pourcentages calculés sur D2:E7','à lire avec les pieds du service : 4,35 / 4,57 / 4,63 % pour l\'annexe B','tableau 65'),
 ('7 - Colonne de contrôle','B2, B4, B6','« Annexe B (extraction du 10/02/2026) »','annexe B transmise par courriel daté par le service du 10 et du 13/02/2026','section 2.6, point 2.6.5'),
 ('7 - Colonne de contrôle','B12, B13','39 998,93 ; 39 132,88 (sommes des lignes)','pieds du service : 39 997,93 ; 39 131,88. Les sommes des lignes sont exactes ; les pieds du service diffèrent d\'une unité','annexes B2 et B3 du service'),
 ('0 - Méthode','A19','« Script : scripts/reponse1-compteur-perpetuel.py »','script absent du dossier : à joindre, ou à remplacer par les scripts du lot 2.6 (s06, s11)','section 2.6'),
 ('1 à 6','ensemble','tableaux 60 et 61','confirmés, inchangés','tableaux 60 et 61')])
E['91']=('91-R1-reconciliation-annexes-A-B-C-F-G-H-quantites-exemple-14-04-2022.xlsx',
         '91-R3-reconciliation-annexes-A-B-C-F-G-H-quantites-exemple-14-04-2022-erratum.xlsx',[
 ('1 CA par annexe','D5, D13, D21','« Somme de la colonne « Tot_rem Ttc » de l\'archive certifiee du 16/03/2026 »','« Somme de la colonne « Tot_rem Ttc » de l\'extraction remise le 13/03/2026 (option c) »','point 2.6.7'),
 ('1 CA par annexe','F6, F14, F22','« les avoirs et les differences de date d\'encaissement jouent »',
  'explication fausse. F − C = 32,45 / 1 319,18 / −418,67 € tient aux 55 règlements etat = 9 (1 958,26 € sur trois exercices) et aux 17 tickets de la seconde série (1 025,30 €)','point 2.6.4 d ; 171'),
 ('1 CA par annexe','F7, F15, F23','« (fichier trie par n° de ticket, pas par ordre chronologique) »','« (fichier trié par date puis par identifiant de note, c\'est-à-dire par ordre d\'ouverture) »','point 2.6.4 b'),
 ('1 CA par annexe','F12','« 13 de plus (286.73 EUR) »','« 13 de plus (288,20 €) », égal à E12','170'),
 ('1 CA par annexe','F20','« 62 de plus (734.01 EUR) »','« 62 de plus (737,10 €) », égal à E20','170'),
 ('1 CA par annexe','C10, C18 et E2:E3, E10:E11, E18:E19','annexes A rattachées aux exercices ; écarts 5 650,34 / −9 076,61 / 2 133,53 €',
  'C10 (429 204,51 €) et C18 (437 698,49 €) sont, au centime, les sommes de la première série des années civiles 2023 et 2024 : les annexes A sont civiles, les écarts aux exercices sont sans objet (à confirmer sur les annexes A elles-mêmes)','annexes H1 à H3 du service, sommes de la première série par année civile'),
 ('6 Colonnes TVA du service','F2:F4','« EN DEFAVEUR DU TRESOR : la TVA due DIMINUE »','démenti : la TVA légalement due excède le compte 445710 de 444,41 €','point 2.5.6 c ; tableau 67'),
 ('6 Colonnes TVA du service','A6','lecture concluant à une diminution de la TVA due','démentie pour la même raison ; la colonne F du service mesure pour 102,9 % de son total des artefacts du décalage de la colonne 16','point 2.5.6 c ; 164'),
 ('4 Exemple 14-04-2022, 5 Lignes C absentes de B','ensemble','exemple et lignes absentes','confirmés, inchangés','points 2.6.5 et 2.6.6')])
E['72']=('72-R2-suppressions-DEL-rapprochement-ventilation-en-euros-3-exercices.xlsx',
         '72-R3-suppressions-DEL-rapprochement-ventilation-en-euros-3-exercices-erratum.xlsx',[
 ('Synthèse','A7:E8 (« multiple entier »)','2 107 lignes ; 205 640,10 €',
  'catégorie non spécifique : la même règle (prix de la carte × quotient entier ≥ 2) classe 71,7 / 65,9 / 71,3 % des totaux de notes encaissées. Ne plus la citer','point 2.6.3 d'),
 ('Synthèse','A13:E13 (« carte OU multiple »)','429 367,85 €','même réserve : non spécifique. Ne plus la citer','point 2.6.3 d'),
 ('prix exact','A5:D7','témoin des totaux de notes : 12,67 / 10,18 / 12,27 % (« 10,2 % à 12,7 % »)',
  'témoin non pondéré par le montant, non comparable aux lignes « DEL ». Témoin pondéré par tranche de montant : 70,2 / 79,3 / 76,9 %, contre 88,2 / 89,6 / 89,5 % des lignes « DEL »','point 2.6.3 d'),
 ('Synthèse ; prix exact','lignes 3 à 6, 11 et 12 ; A2:D4','21 302 lignes ; 430 763,15 € ; lignes = prix de la carte ; 4 lignes aberrantes, 138 003,10 € ; 88,2 / 89,6 / 89,5 %','confirmés, inchangés','tableau 58 ; point 2.6.3 d')])
def make(desk,key):
    src,dst,rows=E[key]
    for r in rows:
        for t in r: assert '—' not in t, t
    shutil.copy(SRC+src,DST+dst); os.chmod(DST+dst,0o644)
    doc=desk.loadComponentFromURL(uno.systemPathToFileUrl(DST+dst),'_blank',0,(pv('Hidden',True),))
    sh=doc.Sheets; sh.insertNewByName('Erratum R2',0); s=sh.getByName('Erratum R2')
    def put(r,c,t,bold=False):
        cl=s.getCellByPosition(c,r); cl.setString(t); cl.setPropertyValue('IsTextWrapped',True)
        if bold: cl.setPropertyValue('CharWeight',150.0)
    put(0,0,f'Pièce n° {key} : erratum R2 (classeur R3)',True); put(1,0,INTRO)
    for j,h in enumerate(H): put(3,j,h,True)
    for i,r in enumerate(rows):
        for j,t in enumerate(r): put(4+i,j,t)
    for j,wd in enumerate([4500,3500,7500,9500,5500]): s.getColumns().getByIndex(j).Width=wd
    doc.calculateAll()
    doc.storeToURL(uno.systemPathToFileUrl(DST+dst),(pv('FilterName','Calc MS Excel 2007 XML'),)); doc.close(True)
    return DST+dst
if __name__=='__main__':
    os.makedirs(DST,exist_ok=True); d=connect()
    for k in ['72','89','90','91']: print('écrit',make(d,k))
    try: d.terminate()
    except Exception: pass
