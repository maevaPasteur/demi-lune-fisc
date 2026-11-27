"""Annexe 174 (définitive) : passerelle, par formules sur les annexes C, E, F et H, entre tickets, additions, tickets à 0,00 €, tables vidées,
règlements et numéros affichés ; test de la numérotation par journée et par série. Sorties : pieces/174-R2-passerelle-tickets-tables-videes-reglements.xlsx ; out/B4/03.txt"""
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from B4_common import *
NAME = '174-R2-passerelle-tickets-tables-videes-reglements.xlsx'
C, E, F, H, A = load(); S = source(); S['id'] = S.id.astype(int)
log = open(O4 + '03.txt', 'w')
def p(*a): print(*a); print(*a, file=log)
D = E[E.typEven == 'DEL'].sort_values(['dateEven', 'heureEven', 'id'])
Dm = D.groupby(['dateEven', 'heureEven']).size().reset_index()[['dateEven', 'heureEven']]
e9 = set(S[S.etat.astype(str) == '9'].id)
Hh = H.sort_values(['date_ticket', 'heure_ticket', 'id']).reset_index(drop=True)
Ac = A.sort_values(['date', 'no', 'id']).reset_index(drop=True)
days = sorted(H.date_ticket.unique())
wb = openpyxl.Workbook()
methode(wb, 'Annexe n° 174 : passerelle entre tickets, additions, tickets à 0,00 €, tables vidées, règlements et numéros affichés',
  ['Chaque chiffre de la section 2.7 sur les populations de tickets est recalculé par formule sur les fichiers remis au service (onglet « Passerelle », lignes 2 à 44).',
   'L onglet « Journees » teste, journée par journée et série par série, que les numéros affichés forment une suite 1, 2, … n sans trou ni doublon.'],
  'B4_03_annexe_174.py',
  ['Ticket à 0,00 € : ticket des annexes H dont le total TTC vaut 0,00 €. Sans article : ticket dont l identifiant ne figure pas dans les annexes C.',
   'À la minute d un DEL : au moins une ligne « DEL » des annexes E porte la même date et la même minute (heure et minute) que la clôture du ticket.',
   'Tables vidées : minutes distinctes portant au moins un ticket sans article clos à la minute d un DEL, hors les minutes dont la somme des lignes « DEL » est nulle ou négative et celle qui porte une ligne d au moins 1 000 € (68 993,10 €) ; montant : somme des lignes « DEL » de la minute.',
   'Série : première série si le totalisateur tot_sum atteint 100 000 (notes encaissées, chaînées par le totalisateur), seconde série sinon (tickets à 0,00 € et 17 tickets non nuls).',
   'État 9 : valeur 9 de la colonne etat de l export natif des règlements.',
   'Suite 1 … n : pour une journée et une série, le plus petit numéro vaut 1, le plus grand vaut le nombre de tickets, et aucun numéro ne figure deux fois.',
   'Additions des annexes C : identifiants distincts ; numéros distincts : couples (journée, numéro affiché) distincts.',
   'Exercices : 1er avril au 31 mars.'],
  src_rows(['C', 'H', 'E', 'F'], natif=True),
  ['Passerelle : grandeurs, valeurs par formules et chiffre du texte, lignes 2 à 44.', 'Journees : une ligne par journée d ouverture (659).',
   'Sources_H : tickets des annexes H (colonnes A à H, valeurs) et colonnes de calcul I à U (formules).', 'Sources_C : additions des annexes C (identifiant, date, numéro).',
   'Sources_DEL : lignes « DEL » des annexes E ; DEL_minutes : agrégation par minute (formules).', 'Sources_F : lignes de règlement des annexes F, avec l état de l export natif.'],
  ['Les fichiers ne portent ni le libellé ni la quantité des articles retirés par une suppression « DEL ».', 'Le recalcul complet du classeur prend quelques minutes.'])
# Sources_C
wc = wb.create_sheet('Sources_C'); header(wc, ['Id (annexe C)', 'Date', 'N° affiché'])
put_df(wc, Ac[['id', 'date', 'no']]); nC = len(Ac) + 1
# Sources_DEL
we = wb.create_sheet('Sources_DEL'); header(we, ['Id événement', 'Date', 'Heure', 'Z', 'Montant'])
put_df(we, D[['id', 'dateEven', 'heureEven', 'no_zEport', 'amount']]); nE = len(D) + 1; fmt(we, 'E', EUR)
# DEL_minutes
wm = wb.create_sheet('DEL_minutes'); header(wm, ['Date', 'Heure', 'Lignes DEL', 'Somme', 'Ligne la plus forte'])
RE = lambda c: f'Sources_DEL!${c}$2:${c}${nE}'
for i, r in enumerate(Dm.itertuples(), start=2):
    wm.cell(i, 1, r.dateEven).font = BLUE; wm.cell(i, 2, r.heureEven).font = BLUE
    wm.cell(i, 3, f'=COUNTIFS({RE("B")},A{i},{RE("C")},B{i})'); wm.cell(i, 4, f'=SUMIFS({RE("E")},{RE("B")},A{i},{RE("C")},B{i})')
    wm.cell(i, 5, f'=_xlfn.MAXIFS({RE("E")},{RE("B")},A{i},{RE("C")},B{i})')
nD = len(Dm) + 1
# Sources_F
wf = wb.create_sheet('Sources_F'); header(wf, ['Id', 'Mode', 'Montant', 'État (export natif)'])
Fx = F[['id', 'mod_regl', 'montant']].copy(); Fx['etat'] = np.where(Fx.id.isin(e9), 9, 0)
put_df(wf, Fx); nF = len(Fx) + 1
# Sources_H
wh = wb.create_sheet('Sources_H')
hh = ['Id', 'Date', 'Heure', 'N°', 'Z', 'Exercice', 'TTC', 'tot_sum', 'Lignes C (calcul)', 'Sans article (1 = oui)', 'Lignes DEL à la minute', 'Sans article à la minute d un DEL',
      'Nouvelle minute', 'Minute écartée (somme ≤ 0 ou ligne ≥ 1 000 €)', 'Règlements F', 'État 9', 'Série (1 = tot_sum ≥ 100 000)', 'Montant DEL de la minute retenue',
      'Première ligne de la journée', 'Dernière ligne de la journée', 'N° en double dans la série du jour (1 = oui)']
header(wh, hh)
nH = len(Hh) + 1
RD = lambda c: f'DEL_minutes!${c}$2:${c}${nD}'
for i, r in enumerate(Hh.itertuples(), start=2):
    for j, v in enumerate((int(r.id), r.date_ticket, r.heure_ticket, int(r.no_ticket), int(r.no_z_report), r.ex, round(r.tot_ttc, 2), round(r.tot_sum, 2)), start=1):
        wh.cell(i, j, v).font = BLUE
    wh.cell(i, 9, f'=COUNTIF(Sources_C!$A$2:$A${nC},A{i})'); wh.cell(i, 10, f'=IF(I{i}=0,1,0)')
    wh.cell(i, 11, f'=COUNTIFS({RD("A")},B{i},{RD("B")},C{i})'); wh.cell(i, 12, f'=IF(AND(J{i}=1,K{i}>0),1,0)')
    wh.cell(i, 13, f'=IF(L{i}=1,IF(COUNTIFS(B$1:B{i - 1},B{i},C$1:C{i - 1},C{i},L$1:L{i - 1},1)=0,1,0),0)' if i > 2 else f'=L{i}')
    wh.cell(i, 14, f'=IF(M{i}=1,IF(OR(SUMIFS({RD("D")},{RD("A")},B{i},{RD("B")},C{i})<=0,SUMIFS({RD("E")},{RD("A")},B{i},{RD("B")},C{i})>=1000),1,0),0)')
    wh.cell(i, 15, f'=SUMIF(Sources_F!$A$2:$A${nF},A{i},Sources_F!$C$2:$C${nF})')
    wh.cell(i, 16, f'=IF(COUNTIFS(Sources_F!$A$2:$A${nF},A{i},Sources_F!$D$2:$D${nF},9)>0,1,0)')
    wh.cell(i, 17, f'=IF(H{i}>=100000,1,2)')
    wh.cell(i, 18, f'=IF(AND(M{i}=1,N{i}=0),SUMIFS({RD("D")},{RD("A")},B{i},{RD("B")},C{i}),0)')
    wh.cell(i, 19, f'=INDEX(Journees!$B$2:$B${len(days) + 1},MATCH(B{i},Journees!$A$2:$A${len(days) + 1},0))')
    wh.cell(i, 20, f'=INDEX(Journees!$D$2:$D${len(days) + 1},MATCH(B{i},Journees!$A$2:$A${len(days) + 1},0))')
    wh.cell(i, 21, f'=IF(COUNTIFS(INDEX($D:$D,S{i}):INDEX($D:$D,T{i}),D{i},INDEX($Q:$Q,S{i}):INDEX($Q:$Q,T{i}),Q{i})>1,1,0)')
# Journees
wj = wb.create_sheet('Journees')
hj = ['Date', 'Première ligne (Sources_H)', 'Tickets du jour', 'Dernière ligne (Sources_H)', 'Première série : tickets', 'Première série : plus petit n°', 'Première série : plus grand n°',
      'Première série : n° en double', 'Première série : suite 1 … n (1 = oui)', 'Seconde série : tickets', 'Seconde série : plus petit n°', 'Seconde série : plus grand n°',
      'Seconde série : n° en double', 'Seconde série : suite 1 … m (1 = oui)', 'Porte des tickets de la seconde série (1 = oui)', 'Additions des annexes C', 'Première ligne (Sources_C)',
      'Numéros distincts des additions', 'Numéros = additions (1 = oui)']
header(wj, hj, [11] + [11] * 18)
RH = lambda c: f'Sources_H!${c}$2:${c}${nH}'
RC = lambda c: f'Sources_C!${c}$2:${c}${nC}'
for i, d in enumerate(days, start=2):
    wj.cell(i, 1, d).font = BLUE
    wj.cell(i, 2, f'=MATCH(A{i},{RH("B")},0)+1'); wj.cell(i, 3, f'=COUNTIF({RH("B")},A{i})'); wj.cell(i, 4, f'=B{i}+C{i}-1')
    for c0, s in ((5, 1), (10, 2)):
        wj.cell(i, c0, f'=COUNTIFS({RH("B")},A{i},{RH("Q")},{s})')
        wj.cell(i, c0 + 1, f'=IF({CL(c0)}{i}=0,"",_xlfn.MINIFS({RH("D")},{RH("B")},A{i},{RH("Q")},{s}))')
        wj.cell(i, c0 + 2, f'=IF({CL(c0)}{i}=0,"",_xlfn.MAXIFS({RH("D")},{RH("B")},A{i},{RH("Q")},{s}))')
        wj.cell(i, c0 + 3, f'=SUMIFS({RH("U")},{RH("B")},A{i},{RH("Q")},{s})')
        wj.cell(i, c0 + 4, f'=IF({CL(c0)}{i}=0,"",IF(AND({CL(c0 + 1)}{i}=1,{CL(c0 + 2)}{i}={CL(c0)}{i},{CL(c0 + 3)}{i}=0),1,0))')
    wj.cell(i, 15, f'=IF(J{i}>0,1,0)')
    wj.cell(i, 16, f'=COUNTIF({RC("B")},A{i})'); wj.cell(i, 17, f'=MATCH(A{i},{RC("B")},0)+1')
    wj.cell(i, 18, f'=SUMPRODUCT(1/COUNTIF(INDEX(Sources_C!$C:$C,Q{i}):INDEX(Sources_C!$C:$C,Q{i}+P{i}-1),INDEX(Sources_C!$C:$C,Q{i}):INDEX(Sources_C!$C:$C,Q{i}+P{i}-1)))')
    wj.cell(i, 19, f'=IF(ROUND(R{i},6)=P{i},1,0)')
nJ = len(days) + 1
# Passerelle
wp = wb.create_sheet('Passerelle', 1)
header(wp, ['Grandeur', 'Valeur (formule)', 'Montant ou dénominateur (formule)', 'Chiffre de la section 2.7'], [70, 16, 22, 40])
rg = lambda c: RH(c)
items = [
 ('Tickets des annexes H', f'=COUNTA({rg("A")})', None, '19 903'),
 ('dont 2022-2023', f'=COUNTIF({rg("F")},"2022-2023")', None, '6 848'), ('dont 2023-2024', f'=COUNTIF({rg("F")},"2023-2024")', None, '6 630'),
 ('dont 2024-2025', f'=COUNTIF({rg("F")},"2024-2025")', None, '6 425'),
 ('Tickets à 0,00 €', f'=COUNTIF({rg("G")},0)', None, '3 281'), ('Tickets sans article', f'=SUM({rg("J")})', None, '3 279'),
 ('Tickets à 0,00 € portant des lignes C (3 281 − 3 279)', f'=COUNTIFS({rg("G")},0,{rg("J")},0)', None, '2'),
 ('Tickets non nuls sans ligne C', f'=COUNTIFS({rg("G")},"<>0",{rg("J")},1)', None, '0 (aucun ticket non nul des annexes H absent des annexes C)'),
 ('Additions des annexes C (identifiants)', f'=COUNTA({RC("A")})', None, '16 624'),
 ('Sans article à la minute d un DEL', f'=SUM({rg("L")})', None, '2 449'), ('Minutes correspondantes', f'=SUM({rg("M")})', None, '2 362'),
 ('Minutes écartées (somme ≤ 0 ou ligne ≥ 1 000 €)', f'=SUM({rg("N")})', None, '3'), ('Tables vidées (minutes retenues)', '=B12-B13', None, '2 359'),
 ('Montant des tables vidées', f'=SUM({rg("R")})', None, '180 003,94 €'),
 ('Sans article sans DEL à la minute', '=B7-B11', None, '830'),
 ('Tickets sans article portant des règlements', f'=COUNTIFS({rg("J")},1,{rg("O")},"<>0")', None, '37'), ('Montant de ces règlements', f'=SUMIFS({rg("O")},{rg("J")},1)', None, '1 958,26 €'),
 ('dont tickets portant l état 9', f'=SUM({rg("P")})', None, '37'),
 ('Lignes DEL', f'=SUM(DEL_minutes!C2:C{nD})', None, '21 302'), ('Montant DEL', f'=SUM(DEL_minutes!D2:D{nD})', None, '430 763,15 €'),
 ('N° de note entre 101 et 126 (annexes H)', f'=COUNTIFS({rg("D")},">=101",{rg("D")},"<=126")', None, '0 (aucun numéro de terrasse)'),
 ('Tickets non nuls de la seconde série', f'=COUNTIFS({rg("Q")},2,{rg("G")},"<>0")', None, '17')]
for ex, t in (('2022-2023', '1 190'), ('2023-2024', '1 096'), ('2024-2025', '995')):
    items.append((f'Tickets à 0,00 €, {ex}', f'=COUNTIFS({rg("G")},0,{rg("F")},"{ex}")', None, t))
for ex, t in (('2022-2023', '1 188'), ('2023-2024', '1 096'), ('2024-2025', '995')):
    items.append((f'Tickets sans article, {ex}', f'=COUNTIFS({rg("J")},1,{rg("F")},"{ex}")', None, t))
for ex, t in (('2022-2023', '953'), ('2023-2024', '795'), ('2024-2025', '701')):
    items.append((f'Sans article à la minute d un DEL, {ex}', f'=COUNTIFS({rg("L")},1,{rg("F")},"{ex}")', None, t))
for ex, t in (('2022-2023', '922 tables ; 67 238,64 €'), ('2023-2024', '776 tables ; 60 381,00 €'), ('2024-2025', '661 tables ; 52 384,30 €')):
    items.append((f'Tables vidées, {ex} : nombre (B) et montant (C)', f'=COUNTIFS({rg("M")},1,{rg("N")},0,{rg("F")},"{ex}")', f'=SUMIFS({rg("R")},{rg("F")},"{ex}")', t))
for ex, t in (('2022-2023', '235'), ('2023-2024', '301'), ('2024-2025', '294')):
    items.append((f'Sans article sans DEL à la minute, {ex}', f'=COUNTIFS({rg("J")},1,{rg("K")},0,{rg("F")},"{ex}")', None, t))
for ex, t in (('2022-2023', '2'), ('2023-2024', '28'), ('2024-2025', '7')):
    items.append((f'Tickets sans article portant des règlements, {ex}', f'=COUNTIFS({rg("J")},1,{rg("O")},"<>0",{rg("F")},"{ex}")', None, t))
items += [('Journées de la seconde série formant une suite 1 … m sans trou ni doublon (B), sur les journées qui en portent (C)', f'=SUM(Journees!N2:N{nJ})', f'=SUM(Journees!O2:O{nJ})', '637 sur 637'),
          ('Journées de la première série seule formant une suite 1 … n (B), sur les journées d ouverture (C)', f'=SUM(Journees!I2:I{nJ})', f'=COUNTA(Journees!A2:A{nJ})', '659 sur 659'),
          ('Journées où le nombre de numéros distincts égale le nombre d additions', f'=SUM(Journees!S2:S{nJ})', f'=COUNTA(Journees!A2:A{nJ})', '645 (sur 659)')]
for i, (a, b, c, t) in enumerate(items, start=2):
    wp.cell(i, 1, a).alignment = WRAP; wp.cell(i, 2, b)
    if c: wp.cell(i, 3, c)
    wp.cell(i, 4, t)
for r in (15, 18, 21): wp[f'B{r}'].number_format = EUR
for r in (33, 34, 35): wp[f'C{r}'].number_format = EUR
p('lignes Passerelle', len(items) + 1)
order = ['Méthode', 'Passerelle', 'Journees', 'Sources_H', 'Sources_C', 'Sources_DEL', 'DEL_minutes', 'Sources_F']
wb._sheets = [wb[n] for n in order]
wb.save(PC + NAME); p('écrit', PC + NAME)
