"""Mission 4 : construit 171-R2 (seconde série : 17 tickets ; 55 règlements etat = 9 ; rapprochements journaliers).
Sources : annexes H-1 à H-3 (H.pkl), C-1 à C-3 (lot23 CC.pkl), B-1 à B-3 (lot23 B.pkl), F-1 à F-3 (F.pkl), G-1 à G-3 (G.pkl), E-1 à E-3 (E.pkl), export natif (SOURCE.pkl).
Règles par ticket : t04 (règle stricte et placebo jour + 7, lus dans out/t04_serie2_tables.txt) ; règle du point 2.2.4 e : lot 2.5 (13 reprises, dont 3 compatibles avec le hasard).
Lignes etat = 9 : v02 (C4 : sept lignes à règlement identique sur une note candidate, contenu repris)."""
import sys, json, re, datetime as dt; sys.path.insert(0,'scripts/lot5-tva')
import pandas as pd, numpy as np
from pieces_common import cell, header, methode, check_dash, wb, EUR, INT, PCT2
CA='scripts/lot6-evenement-reglement/cache/'; FN='public/documents/pieces-lot6/171-R2-seconde-serie-17-tickets-et-55-reglements-etat-9.xlsx'
c=lambda x:int(round(float(x)*100))
H=pd.read_pickle(CA+'H.pkl'); F=pd.read_pickle(CA+'F.pkl'); G=pd.read_pickle(CA+'G.pkl'); E=pd.read_pickle(CA+'E.pkl'); S=pd.read_pickle(CA+'SOURCE.pkl')
B=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/B.pkl'); CC=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/CC.pkl')
txt=open('scripts/lot6-evenement-reglement/out/t04_serie2_tables.txt').read()
strict={int(m.group(1)):(m.group(2),m.group(3)) for m in re.finditer(r'id (\d+) n°\d+ Z \d+ TTC [\d ,]+ TVA [\d.]+ lignes \d+ ; repris par \[([^\]]*)\] ; placebo \[([^\]]*)\]',txt)}
assert len(strict)==17, len(strict)
NONREP_224E={60502,60508,62929,65479}; HASARD_224E={60526,63993,65179}
DUP={('2023-07-14','CB',7356):'56411',('2023-10-25','CB',1670):'59264',('2023-12-28','CB',14952):'60147',('2024-11-02','TR',2500):'66059',('2024-12-18','CHV',9000):'66861',('2025-03-19','TR',2500):'67434 ; 67442'}
CONT={'56411':0.0,'59264':0.0,'60147':0.0,'66059':0.0,'66861':0.0,'67434 ; 67442':20.80}
w=wb(); EXP={}
M=['171-R2. Seconde série de la caisse : les 17 tickets non nuls et les 55 règlements « etat = 9 » ; rapprochements journaliers des annexes',
 'Sources : annexes H-1 à H-3 (liste des tickets, colonne série déduite des deux compteurs tot_sum), C-1 à C-3, B-1 à B-3, F-1 à F-3, G-1 à G-3, E-1 à E-3 du service ; export natif des règlements (colonne etat). Ce classeur : scripts/b5_A5.py ; mesures d\'origine : t03 (B-6), t04 (B-10 c), v02 (C4) ; règle du point 2.2.4 e : lot 2.5 (B3, C6).',
 '§ Règles de reprise des 17 tickets',
 'Règle stricte (t04) : toutes les lignes du ticket (référence, prix, quantité) figurent sur une note de la première série du même Z close dans les 150 minutes ; placebo : même recherche sept jours plus tard.',
 'Règle du point 2.2.4 e (lot 2.5) : reprise entière sur une à trois notes de la première série du même jour, closes à la même heure ou après ; trois reprises (59,80 €, 13,20 €, 6,10 €) se retrouveraient aussi au hasard.',
 'Les colonnes « repris par » et « 2.2.4 e » sont les résultats de ces scripts, portés en valeurs ; les dénombrements et sommes sont des formules.',
 '§ Lignes etat = 9',
 'Doublon possible (v02, C4) : une ligne de même mode et de même montant existe sur une note de la première série du même Z close dans [t − 90 ; t + 150] min. Contenu repris : montant des articles de la table retrouvés sur la note candidate.',
 'Témoins de v02, portés ici en valeurs et non en formules (200 réplications, graine 20261123) : 2,18 lignes en moyenne (au plus 6) en décalant les dates de ±1 à ±8 semaines ; 0,65 (au plus 5) en permutant les montants.',
 '§ Jours',
 'Agrégats journaliers (valeurs) : Σ des lignes de B (Total TTC), Σ tot_ttc de H par série, Σ Tot_rem_Ttc de C, Σ montants de F (et des lignes etat = 9), Σ tot_ttc de G (un ticket compté une fois). Les écarts et les résidus sont des formules.']
check_dash(M); methode(w,M)
SY=w.create_sheet('Synthèse')
# Seconde série
H2=H[(H.serie==2)&(H.tot_ttc_c!=0)].sort_values('id').reset_index(drop=True)
ws=w.create_sheet('Seconde série')
header(ws,['exercice','date','heure','id','n°','Z','TTC','TVA','règle stricte : repris par','règle stricte : repris (1/0)','placebo jour + 7 : repris par','placebo : repris (1/0)','2.2.4 e : repris (1/0)','2.2.4 e : compatible avec le hasard (1/0)','2.2.4 e : repris de façon robuste (1/0)'],[10,11,6,8,4,6,9,8,14,8,14,8,8,8,8])
for i,x in H2.iterrows():
    k=2+i; rp,pl=strict[int(x.id)]
    ws.append([x.ex,x.date_ticket,x.heure_ticket,int(x.id),int(x.no_ticket),int(x.no_z_report),x.tot_ttc_c/100,x.tot_tva_c/100,rp,f'=IF(LEN(I{k})>0,1,0)',pl,f'=IF(LEN(K{k})>0,1,0)',
               0 if x.id in NONREP_224E else 1,1 if x.id in HASARD_224E else 0,f'=IF(AND(M{k}=1,N{k}=0),1,0)'])
N2=len(H2); R2=lambda col:f"'Seconde série'!${col}$2:${col}${1+N2}"
# Etat 9
S9=S[S.etat=='9'].reset_index(drop=True)
De=E[E.typEven=='DEL']
we=w.create_sheet('Etat 9')
header(we,['ligne','date','heure','id (note à 0,00 €)','mode','montant','tot_ttc de la note','note candidate (même mode, même montant)','doublon possible (1/0)','contenu de la table repris sur la candidate (€)','première ligne de la note (1/0)'],[5,11,6,9,6,9,8,14,8,10,8])
seen=set()
for i,x in S9.iterrows():
    k=2+i; key=(x.date_ticket,x.mod_regl,c(x.montant)); cand=DUP.get(key,'')
    we.append([i+1,x.date_ticket,x.heure_ticket,int(x.id),x.mod_regl,round(float(x.montant),2),round(float(x.tot_ttc),2),cand,f'=IF(LEN(H{k})>0,1,0)',
               (CONT[cand] if cand else None),f'=IF(COUNTIF($D$1:D{k},D{k})=1,1,0)'])
    if cand: seen.add(cand)
N9=len(S9); R9=lambda col:f"'Etat 9'!${col}$2:${col}${1+N9}"
# Jours
z9=set(F[F.tot_ttc_c==0].id)
J=pd.DataFrame({'B':B.groupby('date').tot.apply(lambda s:s.map(c).sum()),
 'H1':H[H.serie==1].groupby('date_ticket').tot_ttc_c.sum(),'H2':H[H.serie==2].groupby('date_ticket').tot_ttc_c.sum(),
 'C':CC.groupby('date').tot.apply(lambda s:s.map(c).sum()),'F':F.groupby('dateTicket').montant_c.sum(),
 'F9':F[F.id.isin(z9)].groupby('dateTicket').montant_c.sum(),
 'G':G.drop_duplicates(['dateTicket','heureTicket','noTicket','no_zReport']).groupby('dateTicket').tot_ttc_c.sum()}).fillna(0).astype(int).sort_index()
wj=w.create_sheet('Jours')
header(wj,['date','B','H première série','H seconde série','C','F','F etat = 9','G','B − H1','H1 − G','H1 − F','H1 − (F − etat 9)','B − C','résidu B − C + H2','C − F','résidu C − F − H2 + F etat 9'],[11]+[11]*15)
for i,(d,x) in enumerate(J.iterrows()):
    k=2+i
    wj.append([d]+[x[col]/100 for col in ['B','H1','H2','C','F','F9','G']]+[f'=ROUND(B{k}-C{k},2)',f'=ROUND(C{k}-H{k},2)',f'=ROUND(C{k}-F{k},2)',f'=ROUND(C{k}-(F{k}-G{k}),2)',f'=ROUND(B{k}-E{k},2)',f'=ROUND(B{k}-E{k}+D{k},2)',f'=ROUND(E{k}-F{k},2)',f'=ROUND(E{k}-F{k}-D{k}+G{k},2)'])
NJ=len(J); RJ=lambda col:f"Jours!${col}$2:${col}${1+NJ}"
# Synthèse
SY.column_dimensions['A'].width=90; SY.column_dimensions['B'].width=16; SY.column_dimensions['C'].width=16
SY.append([cell(SY,'Synthèse : chaque chiffre est une formule ; colonne C, chiffre cité par la section 2.6',bold=True)])
r=2
def s(lab,f,e,fm=EUR):
    global r
    if f is None: SY.append([cell(SY,lab,bold=True)]); r+=1; return
    SY.append([lab,cell(SY,f,fmt=fm),(f'{e:,.2f}'.replace(',',' ').replace('.',',') if isinstance(e,float) else e)]); EXP[f'B{r}']=e; r+=1
s('§ Seconde série : 17 tickets non nuls (point 2.6.4 d)',None,None)
s('Tickets non nuls de la seconde série',f'=COUNT({R2("D")})',17,INT); s('Montant TTC (€)',f'=SUM({R2("G")})',1025.30); s('TVA (€)',f'=SUM({R2("H")})',108.58)
s('Règle stricte : tickets repris',f'=SUM({R2("J")})',11,INT); s('Règle stricte : montant repris (€)',f'=SUMIF({R2("J")},1,{R2("G")})',574.00)
s('Règle stricte : tickets non repris',f'=COUNTIF({R2("J")},0)',6,INT); s('Règle stricte : montant non repris (€)',f'=SUMIF({R2("J")},0,{R2("G")})',451.30)
s('Règle stricte : placebo jour + 7, tickets repris',f'=SUM({R2("L")})',1,INT)
s('Règle du 2.2.4 e : tickets repris',f'=SUM({R2("M")})',13,INT); s('Règle du 2.2.4 e : tickets repris de façon robuste',f'=SUM({R2("O")})',10,INT)
s('Règle du 2.2.4 e : montant repris de façon robuste (€)',f'=SUMIF({R2("O")},1,{R2("G")})',639.40)
s('Règle du 2.2.4 e : tickets non repris',f'=COUNTIF({R2("M")},0)',4,INT); s('Règle du 2.2.4 e : montant non repris (€)',f'=SUMIF({R2("M")},0,{R2("G")})',306.80)
s('Règle du 2.2.4 e : TVA des tickets non repris (€)',f'=SUMIF({R2("M")},0,{R2("H")})',32.03)
s('§ Règlements etat = 9 (point 2.6.4 c)',None,None)
s('Lignes etat = 9',f'=COUNT({R9("A")})',55,INT); s('Notes à 0,00 € concernées',f'=SUM({R9("K")})',37,INT); R1958=r; s('Montant (€)',f'=SUM({R9("F")})',1958.26)
s('Lignes à règlement identique sur une note candidate',f'=SUM({R9("I")})',7,INT); s('Montant de ces lignes (€)',f'=SUMIF({R9("I")},1,{R9("F")})',453.34)
s('Lignes sans report retrouvé',f'=COUNTIF({R9("I")},0)',48,INT); s('Montant de ces lignes (€)',f'=SUMIF({R9("I")},0,{R9("F")})',1504.92)
s('Notes candidates dont le contenu repris est nul',f'=COUNTIF({R9("J")},0)',6,INT); s('Contenu repris sur la dernière (€)',f'=SUMIF({R9("J")},">0")',20.80)
s('Tickets de la seconde série et règlements etat = 9, ensemble (€)',f'=B4+B{R1958}',2983.56)
s('§ Rapprochements journaliers (659 jours ; point 2.6.4 d)',None,None)
s('Jours',f'=COUNTA({RJ("A")})',659,INT)
for col,lab,n,tot in [('I','B − H première série',0,0.0),('J','H première série − G',0,0.0),('K','H première série − F',35,-1958.26),('L','H première série − (F hors etat 9)',0,0.0),
                      ('M','B − C',14,-1025.30),('N','résidu B − C + seconde série',0,0.0),('O','C − F',47,-932.96),('P','résidu C − F − seconde série + etat 9',0,0.0)]:
    s(f'{lab} : jours à écart non nul',f'=COUNTIF({RJ(col)},"<>0")',n,INT); s(f'{lab} : Σ des écarts (€)',f'=SUM({RJ(col)})',tot)
w.save(FN); json.dump({'file':FN,'sheet':'Synthèse','exp':EXP},open('scripts/lot6-evenement-reglement/out/.exp_A5.json','w'),ensure_ascii=False); print('écrit',FN,len(EXP))
