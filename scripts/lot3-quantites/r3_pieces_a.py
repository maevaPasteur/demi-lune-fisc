"""Pièces n° 77 et 78 mises à jour, pièce n° 8 complétée d'un onglet « Erratum ». Les données et formules d'origine sont conservées ; seuls les libellés,
la méthode, les noms d'onglets (avec mise à jour des formules qui les citent) et les renvois changent."""
import os, sys, re, openpyxl; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
from openpyxl.styles import Font, Alignment
N77='77-R3-quantites-fractionnaires-recomposition-5062-articles-866-tables.xlsx'
N78='78-R3-quantites-fractionnaires-chiffrage-service-62487-87-recompose-et-note-d-origine-annexe-B.xlsx'
N08='08-R3-quantites-anormales-erratum.xlsx'
def rename_sheet(wb,old,new):
    wb[old].title=new
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value,str) and c.value.startswith('='):
                    c.value=c.value.replace(f"'{old}'!",f"'{new}'!").replace(f"{old}!",f"'{new}'!")
def replace_all(wb,pairs,formulas=True):
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value,str) and (formulas or not c.value.startswith('=')):
                    v=c.value
                    for a,b in pairs: v=v.replace(a,b)
                    c.value=v
def set_method(ws,lines):
    for r in range(1,ws.max_row+1): ws.cell(r,1).value=None
    for i,t in enumerate(lines,1):
        c=ws.cell(i,1); c.value=t; c.alignment=Alignment(wrap_text=True,vertical='top')
        c.font=Font(bold=bool(t) and len(t)<60 and not t.endswith('.'))
    ws.column_dimensions['A'].width=140
# ---------------- 77
wb=openpyxl.load_workbook(PIECE_77)
s=wb['Synthèse']
s['A1']='RECOMPOSITION DES QUANTITÉS FRACTIONNAIRES : synthèse recalculée par formule, directement sur les annexes C-1 à C-3 et F-1 à F-3'
s['A7']='dont somme non entière (articles non refermés)'
s['A10']="Complément arithmétique des articles non refermés (€) (dépend de la fenêtre ; ce n'est pas un montant maximal : voir l'annexe n° 159)"
rename_sheet(wb,'Résidu (8 tables)','Non refermés (8 tables)')
r=wb['Non refermés (8 tables)']; r['A1']="Les 8 tables portant au moins un article non refermé (50 articles). Complément arithmétique par table ; les parts annulées sans règlement et leur montant maximal sont établis à l'annexe n° 159."
r['E3']='Complément arithmétique (€)'
wb['Calcul']['I1']='Complément arithmétique (€)'
set_method(wb['Méthode'],[
 'Objet',
 "Recomposer, table par table et jour par jour, les quantités fractionnaires des annexes C-1 à C-3 et mesurer par formule la part des articles dont les fractions se referment sur un entier. Recalcul mené directement sur les annexes primaires des trois exercices.",
 '',
 'Sources primaires (aucune donnée intermédiaire)',
 "Annexes C-1 à C-3 (détail des tickets ; annexes n° 17 à 19) pour les quantités ; annexes F-1 à F-3 (règlements ; annexes n° 20 à 22) pour l'encaissement. Les 5 062 lignes de l'onglet « Sources » sont extraites directement de ces fichiers ; aucune valeur de résultat n'y est recopiée.",
 '',
 'Identification de la note',
 "Chaque note = un identifiant unique (colonne « Id ») des fichiers C et F, le numéro d'identification unique que le service met lui-même en avant. Comptage par identifiant : 5 660 + 5 534 + 5 430 = 16 624 notes. Par couple (date, n° du jour), on compte 16 607 couples : l'écart de 17 correspond exactement aux 17 notes de la seconde série du compteur de l'annexe H (17 couples, chacun formé d'une note encaissée et d'une note sans règlement à l'annexe F, qui réutilise le n° du jour de la première). Aucune de ces 17 notes ne porte de quantité fractionnaire : elles sont hors du périmètre de la présente pièce.",
 '',
 'Regroupement en tables (règle explicite)',
 "Pour chaque journée, les notes portant une quantité fractionnaire sont triées par heure puis par numéro. Elles sont chaînées en une même table tant que la note suivante est encaissée à quinze minutes au plus (≤ 15 min) de la précédente ET partage au moins un article fractionné (même libellé normalisé, même prix) avec la table en cours. Une table compte au moins deux notes. La fenêtre de quinze minutes est un paramètre de méthode, non une donnée de caisse : de 5 minutes à la journée entière, le taux d'articles refermés reste compris entre 97,2 % et 99,0 %.",
 '',
 "Test d'entier (colonne G de « Calcul »)",
 "Pour chaque article d'une table, on additionne les fractions portées par chacune des notes. Si la somme est à moins de 0,02 d'un entier, l'article est refermé. Le seuil est sans effet : aucune somme n'est à moins de 0,20 d'un entier sans lui être égale.",
 '',
 'Complément arithmétique (colonne I de « Calcul » ; « Synthèse », ligne 10)',
 "Pour un article non refermé : (entier supérieur − somme des fractions) × prix unitaire. C'est un indicateur arithmétique, qui varie avec la fenêtre de regroupement ; ce n'est pas un montant maximal. Le montant maximal des parts annulées sans règlement, toutes fenêtres confondues (3 330,36 € TTC, soit 2 944,71 € HT), est établi à l'annexe n° 159.",
 '',
 'Résultats (recalculés par formule)',
 "Articles fractionnés : 5 062. Refermés sur un entier : 5 012 (99,0 %). Tables partagées : 866, dont 858 entièrement refermées (onglet « Tables », colonne I). Notes rattachées : 1 849, toutes retrouvées à l'annexe F (634 / 649 / 566 ; colonne J). Articles non refermés : 50, sur 8 tables (25 / 25 / 0 ; onglet « Non refermés (8 tables) »).",
 '',
 'Pièces liées',
 "Annexe n° 158 : note d'origine dans l'annexe B (7 146 lignes) et concordance des 1 913 notes à fraction dans les annexes C, H, G et F. Annexe n° 159 : les 64 notes isolées et les 8 tables à articles non refermés (63 partages non aboutis), montant maximal par fenêtre. Annexe n° 160 : test placebo (600 tirages). Annexe n° 78 : chiffrage du service recomposé.",
])
wb.save(P+N77)
# ---------------- 78
wb=openpyxl.load_workbook(PIECE_78)
rename_sheet(wb,'Clôture annexe B',"Note d’origine annexe B")
rename_sheet(wb,'Synthèse clôture',"Synthèse note d’origine")
replace_all(wb,[('résidu (8 tables)','non refermé (8 tables)'),('Statut (recomposition R2)','Statut (annexe n° 77)'),('(pièce R2-quantites-recomposition.xlsx)',"(annexe n° 77, "+N77+")"),
                ('Somme des fractions (R2)','Somme des fractions (annexe n° 77)'),('Refermé ? (R2) (1/0)','Refermé ? (annexe n° 77) (1/0)')])
nd_=wb["Note d’origine annexe B"]
nd_['I1']="Note d'origine trouvée dans l'annexe B (n°) : ligne du même article à quantité entière et à écart négatif"
nd_['M1']="Contrôle : Qté annexe B = entier cible (1/0)"
ex=wb['Exemples annexe B']
ex['A1']="LIGNES DE L'ANNEXE B DU SERVICE (prix-vente-quantité) POUR LES TABLES CITÉES DANS LA SECTION 2.3 : la note d'origine porte la quantité commandée pour toute la table, et l'« écart » du service (col. B) est le montant déjà payé par les autres notes."
for row in ex.iter_rows(min_row=4):
    c=row[11]
    if isinstance(c.value,str) and 'clôture' in c.value:
        c.value="note d'origine : quantité commandée pour la table, écart = parts payées par les autres notes"
sc=wb["Synthèse note d’origine"]
sc['A1']="LA NOTE D'ORIGINE DANS L'ANNEXE B DU SERVICE : pour chaque article refermé de l'annexe n° 77, l'annexe B porte-t-elle, sur une note de la table, l'article à la quantité commandée pour toute la table ?"
sc['A2']="Formules COUNTIFS sur l'onglet « Note d’origine annexe B »."
sc['A5']='Articles fractionnés recomposés (annexe n° 77)'
sc['A7']="dont refermés ET note d'origine à la quantité entière exacte dans l'annexe B"
sc['A9']="Refermés avec note d'origine à une autre quantité entière (la règle des quinze minutes réunit deux partages distincts, ou en scinde un)"
sc['A10']="Refermés sans note d'origine à quantité entière dans l'annexe B"
sc['A11']="Non refermés (8 tables) avec une note d'origine dans la table"
sc['A15']="Lignes à écart du service négatif (col. B) : notes d'origine, remises et autres contreparties (détail : annexe n° 158)"
s=wb['Synthèse']; s['A12']="Décomposition du chiffrage du service selon le sort de l'article dans la recomposition (annexe n° 77, "+N77+")"
s['A26']="Lecture : pour une paire 0,50 + 0,50, la colonne D vaut PU/2 sur chaque note, soit PU au total : le service compte comme « occulté » le prix entier d'un article servi une fois et payé une fois."
lc=wb['Lignes C']; lc['K1']='Statut (annexe n° 77)'
set_method(wb['Méthode'],[
 'Objet',
 "Recomposer le montant de « chiffre d'affaires occulté » écrit par le service p. 22 de la proposition du 18/05/2026 (20 035,60 € / 22 397,96 € / 20 054,31 €) à partir de ses propres annexes C-1 à C-3, puis le ventiler selon le sort de chaque article dans la recomposition des tables partagées (annexe n° 77, "+N77+").",
 '',
 'Sources',
 "Annexes C-1 à C-3 (détail des tickets ; annexes n° 17 à 19) : colonnes 12 (Qté), 14 (Uprice_wt), 17 (Tot_rem Ttc), C (« Prix TTC (14) × Qté virgule neutralisée ») et D (« Écart C − 17 ») telles qu'elles figurent dans les fichiers remis par le service. Annexes B-1 à B-3 (prix de vente / quantité ; annexes n° 24 à 26) : colonnes 6 (Qté), 8 (Prix de vente TTC), 10 (Total TTC), A (Prix TTC × Qté) et B (Écart A − 10).",
 '',
 'Onglet « Lignes C »',
 "Les 11 026 lignes des annexes C dont la quantité n'est pas un entier (3 839 / 3 809 / 3 378), recopiées avec leurs colonnes C et D telles que calculées par le service. Les colonnes M à O recalculent par formule PU × entier supérieur − encaissé et vérifient que la colonne D du service suit cette règle (11 023 lignes sur 11 026 ; « Synthèse », ligne 9). Appliquée seule, la règle donne 62 519,67 € (somme de la colonne N) ; les 3 lignes qui s'en écartent dans le fichier du service (quantités 2,25 et 2,50) expliquent 31,80 €.",
 '',
 'Statut (colonne K)',
 "Chaque ligne est rattachée, par (exercice, date, numéro de note, article, prix), à l'article de l'annexe n° 77 : « refermé (somme entière) » si la somme des fractions de la table est entière, « non refermé (8 tables) » sinon ; « note isolée (non rattachée) » si la note n'appartient à aucune table (64 notes, examinées une à une à l'annexe n° 159).",
 '',
 "Onglet « Note d’origine annexe B »",
 "Pour chacun des 5 062 articles de l'annexe n° 77, recherche dans l'annexe B, parmi les notes de la table, d'une ligne du même article à quantité entière et à écart négatif (colonne B du service). Cette ligne est celle de la note d'origine : la note de la table dont l'identifiant est le plus petit (835 tables sur 835 parmi celles qui ont une seule note portant des écarts négatifs ; annexe n° 158). Elle conserve la quantité commandée pour toute la table, et son montant est celui de la seule part réglée sur cette note. Contrôle par formule (colonne M) : quantité annexe B = entier cible (arrondi de la somme des fractions).",
 '',
 'Résultats et limites',
 "4 949 des 5 012 articles refermés ont, dans l'annexe B, une note d'origine à la quantité entière exacte (98,7 %). 49 en ont une à une autre quantité entière, lorsque la règle des quinze minutes réunit deux partages distincts (44) ou en scinde un (5) ; 14 n'en ont pas, dont 8 articles à prix nul. Sur les 7 146 lignes communes aux annexes B et C dont la quantité diffère, la quantité de l'annexe B est exactement la quantité restée sur la note d'origine plus les parts du même article portées sur les autres notes (7 146 sur 7 146 ; annexe n° 158). Cette lecture est une observation des fichiers du service ; elle n'est pas documentée par l'éditeur du logiciel.",
])
wb.save(P+N78)
# ---------------- 08
CC=pd.read_pickle(C+'CC.pkl'); E=pd.read_pickle(C+'E.pkl')
wb=openpyxl.load_workbook(PIECE_08)
# contrôle (sans modification) de l'onglet 1 contre l'annexe E
q=wb['Qte elevees (supprimees)']; okE=0
for r in range(2,q.max_row+1):
    d,h,m=q.cell(r,2).value,q.cell(r,3).value,q.cell(r,4).value
    okE+=int(((E.typEven=='DEL')&(E.dateEven==d)&(E.heureEven==h)&((E.amount-m).abs()<0.005)).any())
er=wb.create_sheet('Erratum'); bold=Font(bold=True)
def w(r,vals,b=False):
    for j,v in enumerate(vals,1):
        c=er.cell(r,j,v)
        if b: c.font=bold
w(1,['ERRATUM À LA PIÈCE N° 8 (réponse du 10 juillet 2026). Les trois premiers onglets sont reproduits sans modification ; le présent onglet corrige ou précise leurs chiffres, à partir des annexes C-1 à C-3 (n° 17 à 19) et E-1 à E-3 (n° 14 à 16).'],True)
w(3,['1. Onglet « Notes-exemples », note n° 15 du 10/03/2023 (identifiant 53579, 20:22, partage à sept, réglée en espèces) : la pièce recalculait chaque montant (prix × quantité, arrondi) au lieu de le lire dans l\'annexe C. Montants exacts ci-dessous.'],True)
w(4,['Article','Quantité','Prix unitaire (€)','Montant pièce n° 8 (€)','Montant annexe C-1 (€)','Écart (€)'],True)
n15=CC[CC.id==53579].reset_index(drop=True)
src={str(wb['Notes-exemples'].cell(r,2).value):r for r in range(32,55)}
r0=5
for i,x in n15.iterrows():
    rr=r0+i; srow=src.get(x.lib)
    old=float(wb['Notes-exemples'].cell(srow,5).value.replace(' €','').replace(',','.')) if srow else None
    w(rr,[x.lib,float(x.qte),float(x.pu),old,float(x.tot),f'=D{rr}-E{rr}'])
rl=r0+len(n15)
w(rl,['Total','','',f'=SUM(D{r0}:D{rl-1})',f'=SUM(E{r0}:E{rl-1})',f'=D{rl}-E{rl}'],True)
w(rl+1,["Somme des lignes exacte : 27,54 €, égale au total de la note dans les annexes C-1 et F-1 (et non 27,88 €)."])
k=rl+3
w(k,['2. Onglet « Fractions = partage a N » : tableau corrigé (recompté sur les 11 026 lignes à quantité non entière des annexes C-1 à C-3).'],True)
w(k+1,['Partage','Fraction unitaire','Fractions observées','Lignes','Notes'],True)
T=[('Partage à 2','1/2','0,5 ; 1,5 ; 2,5 ; 3,5 ; 4,5',9804,1781),('Partage à 3','1/3','0,33 ; 0,34 ; 0,66 ; 0,67 ; 1,33 ; 1,67 ; 3,33',502,81),
   ('Partage à 4','1/4','0,25 ; 0,75 ; 1,25 ; 1,75 ; 2,25 ; 5,25 ; 6,75',340,58),('Partage à 5','1/5','0,2 ; 0,4 ; 0,6 ; 0,8 ; 1,6 ; 2,4 ; 3,2',208,15),
   ('Partage à 6, ou parts inégales','1/6','0,16 ; 0,17 ; 0,83',11,7),('Partage à 7','1/7','0,14 ; 0,15 ; 0,28 ; 0,29 ; 0,42 ; 0,43',161,7)]
for i,t in enumerate(T): w(k+2+i,list(t))
kt=k+2+len(T); w(kt,['Total (lignes) ; somme de la colonne Notes','','',f'=SUM(D{k+2}:D{kt-1})',f'=SUM(E{k+2}:E{kt-1})'],True)
w(kt+1,['Notes distinctes','','','',1913],True)
w(kt+2,['Écart (notes portant plusieurs types de fractions : 35 notes, dont une à trois types)','','','',f'=E{kt}-E{kt+1}'])
w(kt+3,["Corrections : la ligne « Partage a 12 convives (0,42 ; 2 lignes ; 1 note) » est supprimée. Les deux lignes à 0,42 (Kir Bourgogne, Galette nature) appartiennent à la note n° 15 du 10/03/2023, un partage à sept de trois unités : 0,42 + 6 × 0,43 = 3,00 (notes n° 9 à 14 : 0,43). Le partage à sept compte donc 161 lignes (7 notes × 23 lignes), et non 159. Des 11 lignes en 0,16 / 0,17 / 0,83, 6 relèvent d'un partage à six (09/11/2023 : 0,17 × 4 + 0,16 × 2 = 1) et 5 d'un partage inégal 1/3 + 1/6 + 1/2 (25/05/2024, note n° 35)."])
k=kt+5
w(k,['3. Commentaire de la réponse du 10 juillet 2026 qui cite la pièce (reproduit par le service, réponse du 04/09/2026, p. 28)'],True)
w(k+1,['Texte de la réponse','Correction','Source'],True)
w(k+2,['« seules 167 notes […] portent une fraction autre que 0,50 »','Exact : 167 notes distinctes (73 / 61 / 33), soit 1,005 % des notes','Annexes C-1 à C-3'])
w(k+3,['« environ 1 % des 16 610 notes »','16 624 notes (5 660 + 5 534 + 5 430), par identifiant unique','Annexes C-1 à C-3'])
w(k+4,['« plus de 99 % d\'entre elles se réconcilient au centime »','100 % : pour les 1 913 notes à fraction, somme des lignes = total du ticket = règlement (annexe F) = ticket (annexe H) = journal de TVA (annexe G), TVA comprise','Annexe n° 158'])
w(k+6,[f"4. Onglet « Qte elevees (supprimees) » : contrôlé sans correction. Les {okE} montants sur {q.max_row-1} figurent comme événements « DEL » de l'annexe E à la date, à l'heure et au montant indiqués."],True)
er.column_dimensions['A'].width=60; er.column_dimensions['C'].width=40
for col in 'BDEF': er.column_dimensions[col].width=22
wb.save(P+N08)
print('77, 78, 08 écrits ; contrôle onglet 1 de 08 :',okE,'/',q.max_row-1)
