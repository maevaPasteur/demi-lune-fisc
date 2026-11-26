"""Mission 4 : construit 168-R2 (partie X : modes de règlement, encaissements comptables et chiffre d'affaires, 3 exercices).
Sources : transcription ligne à ligne des tableaux p. 25 et 26 de la proposition (t01, dictionnaires T, C530, TOT25, P26) ; annexes F-1 à F-3 (cache F.pkl) ;
colonne « etat » de l'export natif SOURCE-reglement-brut_2022-2025.xls (cache SOURCE.pkl, identique ligne à ligne à F) ; annexes H-1 à H-3 (cache H.pkl).
Mesures d'origine : t01 (B-1, B-17), v01 (C11), v03 (C6)."""
import sys, json; sys.path.insert(0,'scripts/lot5-tva'); sys.path.insert(0,'scripts/lot6-evenement-reglement')
import pandas as pd, numpy as np
from pieces_common import cell, header, methode, check_dash, wb, EUR, PCT2, INT
CA='scripts/lot6-evenement-reglement/cache/'; FN='public/documents/pieces-lot6/168-R2-partie-X-modes-de-reglement-encaissements-et-CA-3-exercices.xlsx'
EX=['2022-2023','2023-2024','2024-2025']
T={'511200':[(519465,-56730,462735),(352256,7756,360012),(475410,-22500,452910)],
 '511210':[(None,None,37014408),(None,None,39990310),(39766638,1100,39767738)],
 '511220':[(962050,-13418,948632),(911236,-732,910504),(None,None,470889)],
 '511221':[(93510,None,93510),(224005,-121573,102427),(None,None,439272)],
 '511230':[(1493450,-21950,1471500),(2302662,27338,2330000),(2020300,20200,2040500)],
 '511240':[(None,None,29000),(None,None,52500),(None,None,39000)]}
C530=[(339065,53802,-59804,333063),(601043,54622,-59775,595890),(361309,-15177,-65657,280475)]
TOT25=[40352848,44341643,43490784]
P26={'706000':[6471251,7241655,7051747],'706300':[29610587,31917931,31834543],'706800':[59804,59775,65657],'445710':[4261445,4646479,4600545],'TOT':[40403087,43865843,43552492]}
MODE={'511200':'CHQ','511210':'CB','511220':'TR','511221':'TR','511230':'CHV','511240':'KDOLE','530':'ESP'}
F=pd.read_pickle(CA+'F.pkl').reset_index(drop=True); S=pd.read_pickle(CA+'SOURCE.pkl').reset_index(drop=True); H=pd.read_pickle(CA+'H.pkl').reset_index(drop=True)
assert (F.id.values==S.id.astype(int).values).all()
u=lambda x: None if x is None else x/100
w=wb(); EXP={}
M=['168-R2. Partie X de la proposition : encaissements comptables, règlements de la caisse et chiffre d\'affaires comptabilisé, par mode et par exercice',
 'Sources : proposition de rectification, p. 25 (comptes 511 et 530) et p. 26 (706000, 706300, 706800, 445710), transcrites ligne à ligne (onglet « Sources_p25_p26 », valeurs imprimées) ; annexes F-1 à F-3 du service (19 334 lignes) ; colonne « etat » de l\'export natif des règlements (identique ligne à ligne à F) ; annexes H-1 à H-3 (première et seconde séries). Ce classeur : scripts/b5_A2.py ; mesures d\'origine : t01, v01, v03.',
 '§ Conventions',
 'Encaissements comptables : nets imprimés des comptes 511 et 530 (530 net de pourboires), total imprimé de la p. 25. Chiffre d\'affaires comptabilisé hors pourboires : 706000 + 706300 + 445710, somme des lignes de la p. 26.',
 'Correspondance des modes : CB = 511210 ; chèques = 511200 ; KDOLE = 511240 (mode absent de la caisse) ; titres-restaurant = 511220 + 511221 ; chèques-vacances = 511230 ; espèces = 530 net.',
 'Lignes « etat = 9 » : 55 lignes de règlement portées sur 37 tickets à 0,00 € (colonne retirée des annexes F par le service ; annexe 165).',
 'Reclassements : la règle « toute note comportant le mode X est portée en entier en X » est appliquée aux notes de F hors lignes etat = 9 ; l\'écart par mode y est celui du tableau 62 bis, KDOLE rattaché aux chèques (comme dans v03) ; résidu = écart − effet de la règle.',
 'Aucune saisie dans les onglets de calcul : tout est formule sur les onglets « Sources_ ».']
check_dash(M); methode(w,M)
SY=w.create_sheet('Synthèse')
# Sources_p25_p26
wp=w.create_sheet('Sources_p25_p26')
header(wp,['page','compte','mode','exercice','brut imprimé','ajustement imprimé','pourboires (530)','net imprimé','net recalculé (si brut et ajustement imprimés)','écart imprimé − recalculé'],[6,9,7,10,12,12,12,12,14,12])
r=2; P25ROWS=[]
for i,ex in enumerate(EX):
    for k,v in T.items():
        b,a,n=v[i]; wp.append([25,k,MODE[k],ex,u(b),u(a),None,u(n),f'=IF(AND(ISNUMBER(E{r}),ISNUMBER(F{r})),E{r}+F{r},"sans objet")',f'=IF(ISNUMBER(I{r}),H{r}-I{r},"sans objet")']); r+=1
    b,a,pb,n=C530[i]; wp.append([25,'530','ESP',ex,u(b),u(a),u(pb),u(n),f'=E{r}+F{r}+G{r}',f'=H{r}-I{r}']); r+=1
NP25=r-1
for i,ex in enumerate(EX): wp.append([25,'TOTAL p. 25','',ex,None,None,None,u(TOT25[i]),f'=SUMIFS($H$2:$H${NP25},$D$2:$D${NP25},D{r})',f'=H{r}-I{r}']); r+=1
R25T0=NP25+1
P26R={}
for i,ex in enumerate(EX):
    for k in ['706000','706300','706800','445710']: wp.append([26,k,'',ex,None,None,None,u(P26[k][i]),None,None]); P26R[(k,ex)]=r; r+=1
    wp.append([26,'TOTAL p. 26','',ex,None,None,None,u(P26['TOT'][i]),f'=SUM(H{r-4}:H{r-1})',f'=H{r}-I{r}']); P26R[('TOT',ex)]=r; r+=1
NPP=r-1
RP=lambda c:f"Sources_p25_p26!${c}$2:${c}${NP25}"
# Sources_F
wf=w.create_sheet('Sources_F'); NF=len(F)
header(wf,['ligne','exercice','id','date','mode','montant','tot_ttc','etat (export natif)','note comporte CHV','note comporte TR','note comporte CB'],[6,10,8,11,6,10,10,8,8,8,8])
RFc=lambda c:f"${c}$2:${c}${1+NF}"
for i,x in F.iterrows():
    k=2+i
    wf.append([int(x.ligneXLS),x.ex,int(x.id),x.dateTicket,x.mod_regl,float(x.montant_c)/100,float(x.tot_ttc_c)/100,int(S.etat[i]),
      *[f'=IF(COUNTIFS({RFc("C")},C{k},{RFc("E")},"{m}")>0,1,0)' for m in ['CHV','TR','CB']]])
RF=lambda c:f"Sources_F!${c}$2:${c}${1+NF}"
# Sources_H
wh=w.create_sheet('Sources_H'); NH=len(H)
header(wh,['id','exercice','date','série','tot_ttc'],[8,10,11,6,10])
for x in H.itertuples(): wh.append([int(x.id),x.ex,x.date_ticket,int(x.serie),x.tot_ttc_c/100])
RHH=lambda c:f"Sources_H!${c}$2:${c}${1+NH}"
# Par mode (tableau 62 bis)
wm=w.create_sheet('Par mode')
header(wm,['mode','exercice','comptabilité (nets p. 25)','règlements F','comptabilité − F','dont F etat = 9','comptabilité − (F hors etat 9)'],[12,10,14,14,14,12,16])
r=2; PM={}
for m in ['CB','CHQ','KDOLE','TR','CHV','ESP']:
    for ex in EX+['cumul']:
        if ex=='cumul':
            wm.append([m,ex]+[f'=SUM({c}{r-3}:{c}{r-1})' for c in 'CDEFG'])
        else:
            fm='0' if m=='KDOLE' else f'=SUMIFS({RF("F")},{RF("B")},B{r},{RF("E")},A{r})'
            f9='0' if m=='KDOLE' else f'=SUMIFS({RF("F")},{RF("B")},B{r},{RF("E")},A{r},{RF("H")},9)'
            wm.append([m,ex,f'=SUMIFS({RP("H")},{RP("C")},A{r},{RP("D")},B{r})',f'={fm}' if fm=='0' else fm,f'=C{r}-D{r}',f'={f9}' if f9=='0' else f9,f'=C{r}-(D{r}-F{r})'])
        PM[(m,ex)]=r; r+=1
last=r-1
for ex in EX+['cumul']:
    wm.append(['TOTAL',ex]+[f'=SUMIFS({c}$2:{c}${last},$B$2:$B${last},B{r})' for c in 'CDEFG']); PM[('TOTAL',ex)]=r; r+=1
for ex in EX+['cumul']:
    t=PM[('TOTAL',ex)]; wm.append(['en % des règlements de la caisse',ex,None,None,cell(wm,f'=E{t}/D{t}',fmt=PCT2)]); PM[('PCT',ex)]=r; r+=1
# Décomposition (tableau 62 ter)
wd=w.create_sheet('Décomposition')
header(wd,['ligne','2022-2023','2023-2024','2024-2025','cumul'],[70,14,14,14,14])
DR={}
def drow(lab,fs,key):
    rr=wd.max_row+1 if False else None
    wd.append([lab]+fs); DR[key]=len(DR)+2
cols='BCD'
drow('Encaissements comptables (total imprimé p. 25)',[f'=SUMIFS(Sources_p25_p26!$H$2:$H${NPP},Sources_p25_p26!$B$2:$B${NPP},"TOTAL p. 25",Sources_p25_p26!$D$2:$D${NPP},"{ex}")' for ex in EX]+['=SUM(B2:D2)'],'enc')
drow('Chiffre d\'affaires comptabilisé hors 706800 (706000 + 706300 + 445710, somme des lignes p. 26)',[f'=Sources_p25_p26!H{P26R[("706000",ex)]}+Sources_p25_p26!H{P26R[("706300",ex)]}+Sources_p25_p26!H{P26R[("445710",ex)]}' for ex in EX]+['=SUM(B3:D3)'],'ca')
drow('Encaissements comptables − chiffre d\'affaires comptabilisé',[f'={c}2-{c}3' for c in 'BCDE'],'enc_ca')
drow('égal à : encaissements comptables − règlements de la caisse (tableau 62 bis)',[f'=\'Par mode\'!E{PM[("TOTAL",ex)]}' for ex in EX+['cumul']],'enc_f')
drow('plus : règlements portés sur les 37 tickets à 0,00 € (etat = 9)',[f'=\'Par mode\'!F{PM[("TOTAL",ex)]}' for ex in EX+['cumul']],'e9')
drow('plus : tickets de la première série − chiffre d\'affaires comptabilisé',[f'=SUMIFS({RHH("E")},{RHH("B")},"{ex}",{RHH("D")},1)-{c}3' for ex,c in zip(EX,'BCD')]+['=SUM(B7:D7)'],'s1_ca')
drow('contrôle : somme des trois termes − ligne 4 (doit valoir 0)',[f'={c}5+{c}6+{c}7-{c}4' for c in 'BCDE'],'chk')
drow('Variante : F hors etat 9, encaissements comptables − (F − etat 9)',[f'=\'Par mode\'!G{PM[("TOTAL",ex)]}' for ex in EX+['cumul']],'hors9')
drow('Variante : contrôle (F hors etat 9) + (première série − CA) − ligne 4',[f'={c}9+{c}7-{c}4' for c in 'BCDE'],'chk2')
drow('Fourchette basse : CA = total imprimé p. 26 − 706800',[f'={c}2-(Sources_p25_p26!H{P26R[("TOT",ex)]}-Sources_p25_p26!H{P26R[("706800",ex)]})' for ex,c in zip(EX,'BCD')]+[None],'lo')
drow('Fourchette haute : compte 511221 corrigé (net recalculé brut + ajustement)',[f'={c}4-SUMIFS(Sources_p25_p26!$J$2:$J${NP25},Sources_p25_p26!$B$2:$B${NP25},"511221",Sources_p25_p26!$D$2:$D${NP25},"{ex}")' for ex,c in zip(EX,'BCD')]+[None],'hi')
drow('Écart en % du chiffre d\'affaires comptabilisé de l\'exercice',[cell(wd,f'={c}4/{c}3',fmt=PCT2) for c in 'BCDE'],'pct')
# Reclassements
wr=w.create_sheet('Reclassements')
header(wr,['exercice','règle (mode X)','mode','écart du tableau 62 bis (KDOLE avec les chèques)','effet de la règle','résidu = écart − effet','|écart|','|résidu|'],[10,10,7,16,12,12,10,10])
r=2; RR={}
for ex in EX:
    for X,col in [('CHV','I'),('TR','J'),('CB','K')]:
        r0=r
        for m in ['CB','CHQ','TR','CHV','ESP']:
            gap=f"'Par mode'!E{PM[(m,ex)]}"+(f"+'Par mode'!E{PM[('KDOLE',ex)]}" if m=='CHQ' else '')
            if m==X: eff=f'SUMIFS({RF("F")},{RF("B")},A{r},{RF(col)},1,{RF("H")},0,{RF("E")},"<>{X}")'
            else: eff=f'-SUMIFS({RF("F")},{RF("B")},A{r},{RF(col)},1,{RF("H")},0,{RF("E")},"{m}")'
            wr.append([ex,X,m,f'={gap}',f'={eff}',f'=D{r}-E{r}',f'=ABS(D{r})',f'=ABS(F{r})']); r+=1
        wr.append([ex,X,'Σ',None,None,None,f'=SUM(G{r0}:G{r-1})',f'=SUM(H{r0}:H{r-1})']); RR[(ex,X)]=r; r+=1
# CA (tableau 63)
wc=w.create_sheet('CA')
header(wc,['exercice','CA comptable hors pourboires','tickets de la première série (H)','écart','tickets non nuls de la seconde série (H)','pourboires (706800)','CA imprimé − 706800','écart avec les totaux imprimés'],[10,16,16,10,14,12,16,14])
for j,(ex,c) in enumerate(zip(EX,'BCD')):
    k=2+j
    wc.append([ex,f'=Décomposition!{c}3',f'=SUMIFS({RHH("E")},{RHH("B")},A{k},{RHH("D")},1)',f'=B{k}-C{k}',f'=SUMIFS({RHH("E")},{RHH("B")},A{k},{RHH("D")},2)',
               f'=Sources_p25_p26!H{P26R[("706800",ex)]}',f'=Sources_p25_p26!H{P26R[("TOT",ex)]}-F{k}',f'=G{k}-C{k}'])
wc.append(['cumul']+[f'=SUM({c}2:{c}4)' for c in 'BCDEFGH'])
# Synthèse
SY.column_dimensions['A'].width=90; SY.column_dimensions['B'].width=18; SY.column_dimensions['C'].width=22
SY.append([cell(SY,'Synthèse : chaque chiffre est une formule ; colonne C, chiffre cité par la section 2.6',bold=True)])
r=2
def s(lab,f,e,fm=EUR):
    global r
    if f is None: SY.append([cell(SY,lab,bold=True)]); r+=1; return
    SY.append([lab,cell(SY,f,fmt=fm),e if isinstance(e,str) else None])
    if isinstance(e,(int,float)): EXP[f'B{r}']=e
    elif isinstance(e,str) and e.endswith('%'): EXP[f'B{r}']=['pct2' if len(e.split(',')[1].split()[0])==2 else 'pct1',float(e.split()[0].replace(',','.').replace('+',''))]
    r+=1
s('§ Tableau 62 bis : comptabilité − règlements de la caisse, par mode',None,None)
ref62={('CB','cumul'):1791.15,('CHQ','cumul'):-949.29,('KDOLE','cumul'):1205.00,('TR','cumul'):-3849.10,('CHV','cumul'):10744.43,('ESP','cumul'):-5238.90,
       ('CB','2022-2023'):859.89,('CHQ','2022-2023'):-688.76,('TR','2023-2024'):-1988.06,('CHV','2023-2024'):7023.10,('ESP','2024-2025'):-2539.00}
for (m,ex),v in ref62.items(): s(f'{m}, {ex}',f"='Par mode'!E{PM[(m,ex)]}",v)
for ex,v in zip(EX+['cumul'],[125.61,3816.13,-238.45,3703.29]): s(f'Total, {ex}',f"='Par mode'!E{PM[('TOTAL',ex)]}",v)
for ex,v in zip(EX+['cumul'],['+0,03 %','+0,87 %','−0,05 %','+0,29 %']):
    s(f'En % des règlements, {ex}',f"='Par mode'!E{PM[('PCT',ex)]}",v.replace('−','-'),PCT2)
s('§ Tableau 62 ter et point 2.6.4 c',None,None)
for lab,key,vals in [('Encaissements comptables','enc',[403528.48,443416.43,434907.84]),('CA comptabilisé hors 706800','ca',[403432.83,438060.65,434868.35]),
                     ('Encaissements − CA','enc_ca',[95.65,5355.78,39.49]),('etat = 9','e9',[32.45,1607.38,318.43]),('Première série − CA','s1_ca',[-62.41,-67.73,-40.49])]:
    for ex,c,v in zip(EX,'BCD',vals): s(f'{lab}, {ex}',f'=Décomposition!{c}{DR[key]}',v)
s('Encaissements − CA, cumul (5 490,92 €)','=Décomposition!E4',5490.92)
s('Lignes etat = 9, cumul (1 958,26 €)','=Décomposition!E6',1958.26)
s('Contrôle de la décomposition, cumul des trois exercices (0)','=SUM(Décomposition!B8:E8)',0)
s('Écart 2023-2024 en % du CA de l\'exercice (1,2 %)','=Décomposition!C13','1,2 %',PCT2)
s('Écart cumulé en % du CA des trois exercices (0,43 %)','=Décomposition!E13','0,43 %',PCT2)
s('Fourchette basse 2023-2024 (total imprimé p. 26)','=Décomposition!C11',5355.75)
s('Fourchette haute 2023-2024 (511221 corrigé)','=Décomposition!C12',5355.83)
s('Variante hors etat 9 : encaissements − (F − etat 9), 2023-2024','=Décomposition!C9',5423.51)
s('§ Reclassements (aucune règle ne rend compte des écarts)',None,None)
for (ex,X),rr in RR.items(): s(f'{ex}, règle {X} : Σ|résidu| (colonne H) contre Σ|écart| (colonne G de l\'onglet)',f'=Reclassements!H{rr}',None)
s('2022-2023, Σ|écart|',f'=Reclassements!G{RR[("2022-2023","CHV")]}',3246.15)
s('2022-2023, règle CHV, Σ|résidu|',f'=Reclassements!H{RR[("2022-2023","CHV")]}',8277.59)
s('2023-2024, Σ|écart|',f'=Reclassements!G{RR[("2023-2024","CHV")]}',12257.41)
s('2023-2024, règle CHV, Σ|résidu|',f'=Reclassements!H{RR[("2023-2024","CHV")]}',9306.89)
s('2024-2025, Σ|écart|',f'=Reclassements!G{RR[("2024-2025","CHV")]}',7173.25)
s('§ Tableau 63',None,None)
for c,lab,vals in [('B','CA comptable hors pourboires',[403432.83,438060.65,434868.35,1276361.83]),('C','Tickets de la première série',[403370.42,437992.92,434827.86,1276191.20]),
                   ('D','Écart',[62.41,67.73,40.49,170.63]),('E','Seconde série, tickets non nuls',[0.00,288.20,737.10,1025.30]),('F','Pourboires',[598.04,597.75,656.57,1852.36])]:
    for k,(ex,v) in enumerate(zip(EX+['cumul'],vals)): s(f'{lab}, {ex}',f'=CA!{c}{2+k}',v)
s('Écart cumulé avec les totaux imprimés (170,66 €)','=CA!H5',170.66)
s('Total imprimé p. 26 2023-2024 (438 658,43 €) − somme des lignes',f'=Sources_p25_p26!J{P26R[("TOT","2023-2024")]}',0.03)
w.save(FN); json.dump({'file':FN,'sheet':'Synthèse','exp':EXP},open('scripts/lot6-evenement-reglement/out/.exp_A2.json','w'),ensure_ascii=False); print('écrit',FN,len(EXP))
