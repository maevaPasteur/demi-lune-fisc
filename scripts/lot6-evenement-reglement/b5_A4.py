"""Mission 4 : construit 170-R2 (quantités B et C : 7 146 lignes, règle de la quantité commandée 6 272 / 7 037 / 109 ; fractions ; partages et suppressions).
Sources : rapprochement ligne à ligne des annexes B et C (lot23 Crec.pkl : clé date, n° de ticket, référence, libellé, montant TTC, sans la quantité) ;
valeurs par ligne et tirages des témoins : b5_A4_prep.py (reproduit v01, v01b et s13, graine 20261123)."""
import sys, json, pickle; sys.path.insert(0,'scripts/lot5-tva')
import pandas as pd, numpy as np
from pieces_common import cell, header, methode, check_dash, wb, EUR, INT, PCT2
CA='scripts/lot6-evenement-reglement/cache/'; FN='public/documents/pieces-lot6/170-R2-quantites-B-C-7146-lignes-regle-6272-7037-109.xlsx'
Cr=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/Crec.pkl').reset_index(drop=True)
P=pickle.load(open(CA+'b5_A4.pkl','rb')); D=P['D'].reset_index(drop=True); PART=P['PART'].reset_index(drop=True); SH=P['SH'].reset_index(drop=True)
w=wb(); EXP={}
M=['170-R2. Quantités des annexes B et C : les 7 146 lignes dont la quantité diffère, et la règle de la quantité commandée pour la table',
 'Sources : annexes B-1 à B-3 (extraction SERVILOG) et C-1 à C-3 du service, rapprochées ligne à ligne sur la clé date du ticket, n° de ticket, référence, libellé et montant TTC, qui exclut la quantité (97 694 lignes communes ; 75 lignes de C sans correspondant dans B). Ce classeur : scripts/b5_A4.py ; valeurs par ligne et témoins : scripts/b5_A4_prep.py (reproduit v01, v01b et s13 ; graine 20261123).',
 '§ Règle (tableau 64 bis)',
 'Groupe : notes de la première série du même jour et du même Z, portant au moins une ligne à quantité fractionnaire dans C, portant le même article (libellé et prix). Test : quantité B de la ligne = quantité C de la ligne + Σ des quantités C du même article sur les autres notes du groupe.',
 'Fenêtre de 15 minutes (règle stricte), puis 30, 60 minutes et journée du Z (colonne « fenêtre » = 2000) ; à défaut, sous-ensemble des notes partenaires du jour ; à défaut, partage par unités entières (partenaires du même article sans condition de fraction, 15 minutes).',
 'Témoins : partenaires remplacés par des notes de la première série tirées au hasard le même jour (200 tirages) ; onglet « Témoins », un tirage par ligne.',
 '§ Partages et suppressions',
 'Article partagé : ligne de C à quantité fractionnaire, unité (note, référence, prix). Rapprochement : une suppression « DEL » du même jour et du même Z, de montant égal au prix, dans [clôture − 60 ; clôture + 15] minutes. Témoin : mêmes suppressions sept jours plus tard.',
 'Les colonnes de règle (« groupe », « fenêtre », « sous-ensemble », « unités entières », « note d\'origine », « DEL rapproché ») sont des résultats de script portés en valeurs ; les dénombrements sont des formules.']
check_dash(M); methode(w,M)
SY=w.create_sheet('Synthèse')
wq=w.create_sheet('Quantités B C'); N=len(Cr)
header(wq,['exercice','date','n° ticket','id','libellé','prix unitaire','montant TTC','quantité C','présente dans B (1/0)','quantité B','quantité différente (1/0)','B > C (1/0)','quantité C fractionnaire (1/0)','quantité B fractionnaire (1/0)'],[10,11,6,8,24,8,9,8,7,8,7,6,7,7])
for i,x in Cr.iterrows():
    k=2+i; inb=bool(x.inB)
    wq.append([x.ex,x.date,int(x.ticket),int(x.id),str(x.lib).strip(),float(x.pu),round(float(x.tot),2),float(x.qteC),int(inb),(float(x.qte) if inb else None),
               f'=IF(AND(I{k}=1,ROUND(J{k}-H{k},2)<>0),1,0)',f'=IF(AND(K{k}=1,J{k}>H{k}),1,0)',f'=IF(ABS(H{k}-ROUND(H{k},0))>0.000000001,1,0)',f'=IF(I{k}=1,IF(ABS(J{k}-ROUND(J{k},0))>0.000000001,1,0),"")'])
RQ=lambda c:f"'Quantités B C'!${c}$2:${c}${1+N}"
wl=w.create_sheet('Lignes'); ND=len(D)
header(wl,['exercice','date','n° ticket','id','article (libellé|prix en centimes)','quantité B (centièmes)','quantité C (centièmes)','groupe 15 min (1/0)','égalité 15 min (1/0)','note d\'origine = plus petit id du groupe (1/0)','fenêtre de l\'égalité (min)','sous-ensemble (1/0)','unités entières (1/0)','règle qui explique la ligne','sans explication (1/0)'],[10,11,6,8,26,8,8,6,6,8,8,6,6,22,7])
for i,x in D.iterrows():
    k=2+i
    wl.append([x.ex,x.date,int(x.ticket),int(x.id),x.art,int(x.qB),int(x.q),int(x.groupe15),int(x.egal15),int(x.origine15),(None if pd.isna(x.fenetre) or x.fenetre is None else int(x.fenetre)),int(x.sous_ensemble),int(x.unites),
               f'=IF(K{k}=15,"1. quinze minutes",IF(K{k}=30,"2. trente minutes",IF(K{k}=60,"3. soixante minutes",IF(K{k}=2000,"4. journée du Z",IF(L{k}=1,"5. sous-ensemble",IF(M{k}=1,"6. unités entières","sans explication"))))))',
               f'=IF(N{k}="sans explication",1,0)'])
RL=lambda c:f"Lignes!${c}$2:${c}${1+ND}"
wp=w.create_sheet('Partenaires'); NP=len(PART)
header(wp,['exercice','date','n° ticket','id','article','quantité B (centièmes)','quantité C (centièmes)','B = C (1/0)'],[10,11,6,8,26,8,8,6])
for i,x in PART.iterrows(): k=2+i; wp.append([x.ex,x.date,int(x.ticket),int(x.id),x.art,int(x.qB),int(x.q),f'=IF(F{k}=G{k},1,0)'])
wt=w.create_sheet('Témoins'); header(wt,['tirage','règle stricte : égalités','unités entières : égalités'],[8,14,14])
for j,(a,b) in enumerate(zip(P['pl1'],P['pl2'])): wt.append([j+1,int(a),int(b)])
ws=w.create_sheet('Partages et suppressions'); NS=len(SH)
header(ws,['exercice','date','heure de clôture','id','référence','libellé','prix','DEL rapproché (1/0)','témoin jour + 7 (1/0)'],[10,11,7,8,8,24,8,7,7])
for x in SH.itertuples(): ws.append([x.ex,x.date,x.heure,int(x.id),str(x.ref),str(x.lib).strip(),float(x.pu),int(x.reel),int(x.j7)])
RS=lambda c:f"'Partages et suppressions'!${c}$2:${c}${1+NS}"
SY.column_dimensions['A'].width=92; SY.column_dimensions['B'].width=16; SY.column_dimensions['C'].width=16
SY.append([cell(SY,'Synthèse : chaque chiffre est une formule ; colonne C, chiffre cité par la section 2.6',bold=True)])
r=2; RW={}
def s(lab,f,e,fm=INT,key=None,disp=None):
    global r
    if f is None: SY.append([cell(SY,lab,bold=True)]); r+=1; return
    if disp is None: disp=(f'{e:,.2f}'.replace(',',' ').replace('.',',') if isinstance(e,float) else (e if not isinstance(e,list) else (f'{e[1]:.1f} %' if e[0]=='pct1' else f'{e[1]:.2f} %').replace('.',',')))
    SY.append([lab,cell(SY,f,fmt=fm),disp]); EXP[f'B{r}']=e
    if key: RW[key]=r
    r+=1
EX=['2022-2023','2023-2024','2024-2025']
s('§ Rapprochement B / C (point 2.6.5 b)',None,None)
s('Lignes de C',f'=COUNTA({RQ("A")})',97769); s('Lignes de C présentes dans B (lignes communes)',f'=SUM({RQ("I")})',97694)
s('Lignes de C absentes de B',f'=COUNTIF({RQ("I")},0)',75); s('Montant de ces lignes (€)',f'=SUMIF({RQ("I")},0,{RQ("G")})',1025.30,EUR)
s('Lignes à quantité différente',f'=SUM({RQ("K")})',7146,key='n');
for ex,v in zip(EX,[2337,2471,2338]): s(f'  dont {ex}',f'=SUMIFS({RQ("K")},{RQ("A")},"{ex}")',v)
s('Lignes à quantité différente avec B > C',f'=SUM({RQ("L")})',7146)
s('Lignes de l\'onglet « Lignes » (contrôle)',f'=COUNTA({RL("A")})',7146)
s('§ Tableau 64 bis',None,None)
s('Quinze minutes (règle stricte)',f'=COUNTIF({RL("K")},15)',6272,key='r15'); s('  en % des 7 146',f'=B{r-1}/B{RW["n"]}',['pct1',87.8],PCT2)
s('Témoin au hasard, moyenne des 200 tirages','=AVERAGE(Témoins!$B$2:$B$201)',355.77,'0.0',disp='355,8')
s('Témoin au hasard, maximum','=MAX(Témoins!$B$2:$B$201)',398)
s('Trente minutes, en plus',f'=COUNTIF({RL("K")},30)',23); s('Soixante minutes, en plus',f'=COUNTIF({RL("K")},60)',11); s('Journée du Z, en plus',f'=COUNTIF({RL("K")},2000)',32)
s('Cumul après les fenêtres',f'=COUNT({RL("K")})',6338)
s('Sous-ensemble des notes partenaires du jour, en plus',f'=SUM({RL("L")})',188); s('Cumul',f'=B{r-2}+B{r-1}',6526)
s('Partage par unités entières, en plus',f'=SUM({RL("M")})',511); s('Cumul (règles élargies)',f'=B{r-2}+B{r-1}',7037,key='c'); s('  en % des 7 146',f'=B{r-1}/B{RW["n"]}',['pct1',98.5],PCT2)
s('Témoin unités entières, moyenne des 200 tirages','=AVERAGE(Témoins!$C$2:$C$201)',51.67,'0.0',disp='51,7')
s('Témoin unités entières, maximum','=MAX(Témoins!$C$2:$C$201)',76)
s('Lignes sans explication par ces règles',f'=SUM({RL("O")})',109)
s('Autres notes des groupes (15 min) : lignes',f'=COUNTA(Partenaires!$A$2:$A${1+NP})',7097); s('  dont B = C',f'=SUM(Partenaires!$H$2:$H${1+NP})',6935)
s('Note portant l\'écart = plus petit identifiant du groupe (15 min)',f'=SUM({RL("J")})',6355)
s('§ Lignes à quantité fractionnaire (point 2.6.5 d)',None,None)
for ex,(vc,vb) in zip(EX,[(3839,2174),(3809,2040),(3378,1753)]):
    s(f'{ex} : C',f'=SUMIFS({RQ("M")},{RQ("A")},"{ex}")',vc); s(f'{ex} : B',f'=SUMIFS({RQ("N")},{RQ("A")},"{ex}")',vb)
s('§ Partages et suppressions (point 2.6.5 d)',None,None)
s('Articles partagés',f'=COUNTA({RS("A")})',11026); s('Rapprochés d\'une suppression au prix de l\'article',f'=SUM({RS("H")})',2001)
s('  en %',f'=B{r-1}/B{r-2}',['pct2',18.15],PCT2); s('Témoin jour + 7',f'=SUM({RS("I")})',1940); s('  en %',f'=B{r-1}/B{r-4}',['pct2',17.59],PCT2)
# valeurs brutes : remplacer les marqueurs
for k,v in list(EXP.items()):
    if isinstance(v,list) and v[0]=='raw': EXP[k]=v[1]
    if v is None: del EXP[k]
w.save(FN); json.dump({'file':FN,'sheet':'Synthèse','exp':EXP},open('scripts/lot6-evenement-reglement/out/.exp_A4.json','w'),ensure_ascii=False); print('écrit',FN,len(EXP))
