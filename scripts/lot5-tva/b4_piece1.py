"""B4 : construit 161 (décalage du champ « taux » des annexes C). Sources : caches C_b3.pkl (annexes C-1 à C-3
contrôlées en s01), G_paliers.pkl et G (annexes G-1 à G-3), H (annexes H-1 à H-3), B5_tickets.pkl (première série)."""
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import json
from common import *
from pieces_common import *
CC=pd.read_pickle(CA+'C_b3.pkl').reset_index(drop=True)
T=pd.read_pickle(CA+'B5_tickets.pkl'); gid=set(T.index)
CC['s2']=[0 if (a,b) in gid else 1 for a,b in zip(CC.ex,CC.id)]
N=len(CC); R0=2; RL=R0+N-1           # lignes 2 .. 97770
EXP={}                                # valeurs attendues (chiffres du texte) par cellule de « Synthèse »
w=wb()
M=['161. Décalage d\'une ligne du champ « Taux_tva » (colonne 16) des annexes C-1 à C-3',
 'Sources : annexes C-1 à C-3 (17-annexe-c1-2022-2023.xls, 18-annexe-c2-2023-2024.xls, 19-annexe-c3-2024-2025.xls, 97 769 lignes de vente), annexes G-1 à G-3 (journal de TVA, 29 588 lignes, 16 605 tickets), annexes H-1 à H-3 (19 903 notes). Scripts : scripts/lot5-tva/b1_calculs.py, b3_c1_c3.py, b3_c8_colonnes.py, s05_validation_G.py ; ce classeur : b4_piece1.py.',
 '§ Définitions',
 'Ordre du fichier : ordre des lignes des annexes C, trié par date puis par Id de note ; les trois annexes sont mises bout à bout dans l\'onglet « Lignes » (C-1, puis C-2, puis C-3).',
 'Taux du fichier : valeur de la colonne 16 « Taux_tva » de l\'annexe C (onglet « Lignes », colonne M).',
 'Taux appliqué : taux de la colonne 16 de la ligne suivante dans l\'ordre du fichier ; il est unique pour chaque référence (316 références vendues au moins deux fois sur 316, onglet « Références ») et il est reporté comme attribut de la référence (colonne N). La colonne Y recopie par formule le taux de la ligne suivante et la colonne Z vérifie qu\'il est égal à la colonne N.',
 'Taux appliqué de la ligne précédente : colonne O, formule = colonne N de la ligne du dessus (vide pour la première ligne de C-1, seule ligne sans ligne précédente).',
 'Accord : colonne P = 1 si le taux du fichier est égal au taux appliqué. Même taux que l\'article précédent : colonne Q. Exception : colonne R = 1 si P et Q diffèrent.',
 'Première ligne de note : colonne T = 1 si l\'Id de note diffère de celui de la ligne précédente. Seconde série : colonne W = 1 pour les notes de l\'annexe H absentes du journal de TVA G.',
 'Paliers : pour chaque ticket du journal de TVA, palier G = VAT_base + taux lu en euros, par taux ; paliers C = somme des Tot_rem_Ttc des lignes de la note selon le taux retenu (taux appliqué, taux de la colonne 16, taux du service : taux « correct » de la colonne E pour les lignes signalées, colonne 16 sinon). Ces sommes sont des valeurs calculées par le script (jointure C / G), les égalités sont des formules.',
 '§ Remarques',
 'Les deux premières lignes de C-2 et de C-3 ont une ligne précédente dans l\'ordre des trois fichiers mis bout à bout (dernière ligne de C-1, de C-2) : la colonne 16 de la première ligne de C-2 porte 10 %, taux appliqué de la dernière ligne de C-1 ; celle de C-3 porte 10 %, taux appliqué de la dernière ligne de C-2. 97 768 lignes ont ainsi une ligne précédente ; 97 766 si chaque annexe est prise isolément.',
 'Témoin : avec le taux de la même ligne, 29 références sur 316 ont un taux unique. Placebo (permutation aléatoire des taux à l\'intérieur de chaque exercice, 100 tirages, graine 20261123, script s05) : au plus 14 références sur 316.',
 'L\'arrondi de la taxe : tax_amount diffère de 0,01 € de ROUND(palier × taux / (100 + taux) ; 2) sur 242 lignes du journal G (onglet « Paliers lignes G », colonne M).',
 'Le classeur est recalculé sous LibreOffice ; aucun commentaire argumentatif : faits et calculs seulement.']
check_dash(M); methode(w,M)
# ---------- Synthèse (écrite plus bas, formules vers les autres onglets) : on prépare les onglets d'abord en mémoire
LG='Lignes'
def rng(col): return f"'{LG}'!${col}${R0}:${col}${RL}"
# ---------- Lignes
ws_s=w.create_sheet('Synthèse')
ws=w.create_sheet(LG)
cols=['exercice','rowC (ligne de l\'annexe C)','date','heure','n° ticket','Id note','Z','ref','libellé','Qte','PU','Tot_rem_Ttc','taux col. 16 (fichier)','taux appliqué (attribut de la référence)',
 'taux appliqué ligne précédente','accord (col. 16 = appliqué)','même taux appliqué que la ligne précédente','exception (P ≠ Q)','col. 16 = taux appliqué ligne précédente','première ligne de note',
 'E du service','F du service','seconde série (1 = note hors journal G)','PU × Qte = Tot_rem_Ttc à 0,01 € près','taux col. 16 de la ligne suivante','ligne suivante = taux appliqué']
header(ws,cols,[10,8,11,7,7,8,6,7,28,6,7,9,7,7,7,7,7,7,7,7,11,9,7,7,7,7])
for i,r in enumerate(CC.itertuples(index=False)):
    k=R0+i; first=(i==0)
    E=r.Es if r.Es!='' else None; F=None if pd.isna(r.Fs) else float(r.Fs)
    ws.append([r.ex,int(r.rowC),r.date,r.heure,int(r.ticket),int(r.id),int(r.z),r.ref,r.lib_s,float(r.qte),float(r.pu),float(r.tot),int(r.rf),int(r.rart),
      None if first else f'=N{k-1}', f'=IF(M{k}=N{k},1,0)', '' if first else f'=IF(N{k}=O{k},1,0)', '' if first else f'=IF(P{k}<>Q{k},1,0)',
      '' if first else f'=IF(M{k}=O{k},1,0)', 1 if first else f'=IF(OR(A{k}<>A{k-1},F{k}<>F{k-1}),1,0)', E, F, int(r.s2),
      f'=IF(ABS(ROUND(K{k}*J{k}*100,0)-ROUND(L{k}*100,0))<=1,1,0)', '' if k==RL else f'=M{k+1}', '' if k==RL else f'=IF(Y{k}=N{k},1,0)'])
print('Lignes écrites',N)
# ---------- Journées
days=sorted(CC.date.unique()); JD=len(days)
wj=w.create_sheet('Journées'); header(wj,['date','lignes','lignes en désaccord (P = 0)'],[12,10,14])
for i,d in enumerate(days):
    k=2+i; wj.append([d,f"=COUNTIF({rng('C')},A{k})",f"=COUNTIFS({rng('C')},A{k},{rng('P')},0)"])
# ---------- Paliers (tickets G)
G=loadG(); G['r']=G['taux_tva%'].astype(int); G['pal']=G.VAT_base_c+G.r*100
gp=G.pivot_table(index=['ex','dateTicket','heureTicket','noTicket','no_zReport'],columns='r',values='pal',aggfunc='sum',fill_value=0)
gp.columns=['G10','G20']; gp=gp.reset_index()
CC['tc']=CC.tot.map(c); key=['ex','date','heure','ticket','z']
pc=CC[CC.s2==0].groupby(key+['id']).size().reset_index()[key+['id']]
for col,lab in [('rart','app'),('rf','f16'),('tserv','serv')]:
    C1=CC[CC.s2==0]; x=C1.assign(p10=np.where(C1[col]==10,C1.tc,0),p20=np.where(C1[col]==20,C1.tc,0)).groupby(key+['id']).agg(**{f'{lab}10':('p10','sum'),f'{lab}20':('p20','sum')}).reset_index()
    pc=pc.merge(x,on=key+['id'])
P=pc.merge(gp,left_on=key,right_on=['ex','dateTicket','heureTicket','noTicket','no_zReport'],how='inner')
assert len(P)==16605, len(P)
P=P.sort_values(['ex','date','heure','ticket']).reset_index(drop=True); NP=len(P)
wp=w.create_sheet('Paliers')
header(wp,['exercice','date','heure','n° ticket','Z','Id note','palier G 10 % (VAT_base + 10)','palier G 20 % (VAT_base + 20)','palier C 10 %, taux appliqué','palier C 20 %, taux appliqué',
 'palier C 10 %, col. 16','palier C 20 %, col. 16','palier C 10 %, taux du service','palier C 20 %, taux du service','égalité au centime, taux appliqué','égalité, col. 16','égalité, taux du service'],[10,11,7,7,6,8]+[11]*8+[9,9,9])
for i,r in enumerate(P.itertuples(index=False)):
    k=2+i
    wp.append([r.ex,r.date,r.heure,int(r.ticket),int(r.z),int(r.id),r.G10/100,r.G20/100,r.app10/100,r.app20/100,r.f1610/100,r.f1620/100,r.serv10/100,r.serv20/100,
      f'=IF(AND(ROUND(I{k}-G{k},2)=0,ROUND(J{k}-H{k},2)=0),1,0)',f'=IF(AND(ROUND(K{k}-G{k},2)=0,ROUND(L{k}-H{k},2)=0),1,0)',f'=IF(AND(ROUND(M{k}-G{k},2)=0,ROUND(N{k}-H{k},2)=0),1,0)'])
for ex in EX:
    p=P[P.ex==ex]; print(ex,'paliers app',int(((p.app10==p.G10)&(p.app20==p.G20)).sum()),'f16',int(((p.f1610==p.G10)&(p.f1620==p.G20)).sum()),'serv',int(((p.serv10==p.G10)&(p.serv20==p.G20)).sum()),len(p))
# ---------- Paliers lignes G (29 588)
cmap={}
x=CC[CC.s2==0].assign(p=CC.tc).groupby(key+['rart']).p.sum()
G=G.sort_values(['ex','rowG']).reset_index(drop=True)
wg=w.create_sheet('Paliers lignes G')
header(wg,['exercice','ligne G (rowG)','date','heure','n° ticket','Z','taux','VAT_base','tax_amount','palier C au taux appliqué (Σ Tot_rem_Ttc)','VAT_base + taux en euros','VAT_base = palier C − taux (au centime)','tax_amount = ROUND(palier × taux / (100 + taux) ; 2)'],[10,8,11,7,7,6,6,10,10,12,12,10,12])
NG=len(G)
for i,r in enumerate(G.itertuples(index=False)):
    k=2+i; pal=x.get((r.ex,r.dateTicket,r.heureTicket,r.noTicket,r.no_zReport,r.r))
    wg.append([r.ex,int(r.rowG),r.dateTicket,r.heureTicket,int(r.noTicket),int(r.no_zReport),r.r,r.VAT_base_c/100,r.tax_amount_c/100,None if pal is None else pal/100,
      f'=H{k}+G{k}',f'=IF(ROUND(J{k}-G{k}-H{k},2)=0,1,0)',f'=IF(ROUND(ROUND(J{k}*G{k}/(100+G{k}),2)-I{k},2)=0,1,0)'])
# ---------- Références
g=CC.groupby('ref'); n=g.size()
CC['nxt']=CC.rf.shift(-1)   # ordre des trois fichiers bout à bout
u_next=CC.dropna(subset=['nxt']).groupby('ref').nxt.nunique().reindex(n.index); u_same=g.rf.nunique()
wr=w.create_sheet('Références')
hd=['ref','libellé(s)','lignes','nombre de taux distincts, taux de la ligne suivante','nombre de taux distincts, taux de la même ligne (témoin)','taux appliqué']
for ex in EX: hd+= [f'{ex} lignes',f'{ex} taux distincts col. 16',f'{ex} taux distincts service',f'{ex} taux distincts appliqués']
hd+=['3 ex. taux distincts service','max par exercice, taux distincts service']
header(wr,hd,[7,30,7,10,10,7]+[8]*14)
refs=list(n.index); NR=len(refs)
for i,ref in enumerate(refs):
    k=2+i; z=CC[CC.ref==ref]; row=[ref,' / '.join(sorted(z.lib_s.unique()))[:120],int(len(z)),int(u_next[ref]),int(u_same[ref]),int(z.rart.iloc[0])]
    for ex in EX:
        y=z[z.ex==ex]; row+= [int(len(y)),int(y.rf.nunique()),int(y.tserv.nunique()),int(y.rart.nunique())]
    row+=[int(z.tserv.nunique()),f'=MAX(I{k},M{k},Q{k})']
    wr.append(row)
# ---------- Extrait p. 44
X=CC[(CC.ex==EX[0])&(CC.rowC>=37)&(CC.rowC<=76)].copy(); assert len(X)==40
X['vis']=(X.qte==0.5).astype(int)
we=w.create_sheet('Extrait p. 44')
header(we,['rowC','heure','n° ticket','Id note','ref','libellé','Qte','Tot_rem_Ttc','taux col. 16','taux appliqué','taux appliqué ligne précédente','taux légal','E du service','taux du service','F du service','visible sur l\'image p. 44 (Qte = 0,50)',
 'col. 16 = appliqué ligne précédente','col. 16 = appliqué','appliqué = légal','signalée (E non vide)','artefact (signalée et taux du service = appliqué)','Père Gregoire porté vers 10 %'],[6,7,6,8,6,28,6,9,7,7,7,7,11,7,9,8,8,8,8,8,8,8])
for i,r in enumerate(X.itertuples(index=False)):
    k=2+i
    we.append([int(r.rowC),r.heure,int(r.ticket),int(r.id),r.ref,r.lib_s,float(r.qte),float(r.tot),int(r.rf),int(r.rart),int(r.prev_rart),None if pd.isna(r.tl) else int(r.tl),r.Es or None,int(r.tserv),None if pd.isna(r.Fs) else float(r.Fs),int(r.vis),
      f'=IF(I{k}=K{k},1,0)',f'=IF(I{k}=J{k},1,0)',f'=IF(J{k}=L{k},1,0)',f'=IF(M{k}<>"",1,0)',f'=IF(AND(T{k}=1,N{k}=J{k}),1,0)',f'=IF(AND(T{k}=1,ISNUMBER(SEARCH("gregoire",F{k})),N{k}=10),1,0)'])
# notes de l'extrait : paliers et TVA
Xn=X.groupby(['id','heure','ticket']).size().reset_index()
TV=T.loc[EX[0]]
we.append([]); we.append([cell(we,'Notes de l\'extrait',bold=True)])
hrow=44; we.append([cell(we,h,bold=True,fill=True,wrap=True) for h in ['Id note','n° ticket','palier C 10 %, appliqué','palier C 20 %, appliqué','palier G 10 %','palier G 20 %','TVA recalculée au taux appliqué','TVA légale','tot_tva (H)','paliers C = G','TVA appliquée = légale = tot_tva']])
for j,r in enumerate(Xn.itertuples(index=False)):
    k=hrow+1+j; p=P[(P.ex==EX[0])&(P.id==r.id)].iloc[0]; t=TV.loc[r.id]
    we.append([int(r.id),int(r.ticket),p.app10/100,p.app20/100,p.G10/100,p.G20/100,t.app/100,t.leg/100,t.tot_tva/100,f'=IF(AND(ROUND(C{k}-E{k},2)=0,ROUND(D{k}-F{k},2)=0),1,0)',f'=IF(AND(ROUND(G{k}-H{k},2)=0,ROUND(H{k}-I{k},2)=0),1,0)'])
NX=len(Xn)
# ---------- Autres colonnes (concordance C / H, valeurs du script b3_c8_colonnes.py recalculées ici)
H=loadH(); h=H.assign(id=H.id.astype(int)).drop_duplicates(['ex','id']).set_index(['ex','id'])
wa=w.create_sheet('Autres colonnes')
header(wa,['colonne de l\'annexe C','colonne de l\'annexe H (même Id de note)','lignes C concordantes','lignes C','source du calcul'],[24,24,12,12,60])
for col,hc in [('date','date_ticket'),('heure','heure_ticket'),('ticket','no_ticket'),('z','no_z_report'),('datz','dat_z'),('tot_ttc','tot_ttc'),('tot_tva','tot_tva')]:
    hv=h[hc].reindex(list(zip(CC.ex,CC.id))).values; cv=CC[col].values
    if col in ('ticket','z'): eq=(pd.to_numeric(pd.Series(cv)).values==pd.to_numeric(pd.Series(hv)).values)
    elif col in ('tot_ttc','tot_tva'): eq=np.abs(cv.astype(float)-hv.astype(float))<0.005
    else: eq=(pd.Series(cv).astype(str).values==pd.Series(hv).astype(str).values)
    wa.append([col,hc,int(eq.sum()),N,'valeur calculée par b4_piece1.py (jointure par exercice et Id de note)'])
    print('H',col,int(eq.sum()))
k=wa_row=9
wa.append(['PU × Qte = Tot_rem_Ttc à 0,01 € près','(contrôle interne de la ligne, H ne porte pas de détail par ligne)',f"=COUNTIF({rng('X')},1)",N,'formule sur l\'onglet « Lignes », colonne X'])
wa.append(['Tot_rem (remise de note)','tot_remGlobale du journal G (H ne porte pas de remise)',16579,16605,'valeur calculée par b3_c8_colonnes.py (tickets du journal G)'])
wa.append([]); wa.append(['Note : l\'annexe H est un fichier de notes (une ligne par note) ; elle ne porte ni prix unitaire, ni quantité, ni montant par ligne. Les colonnes prix unitaire, quantité et montant des annexes C ne peuvent être rapprochées que par le contrôle interne PU × Qte et par les paliers du journal G (onglet « Paliers »).'])
# ---------- Synthèse
S=ws_s; S.column_dimensions['A'].width=78
for cl in 'BCDE': S.column_dimensions[cl].width=15
S.append([cell(S,'Tableau 56 et constats du point 2.5.6 b, par formules',bold=True)])
S.append([cell(S,h,bold=True,fill=True) for h in ['Grandeur','Ex. 31/03/2023','Ex. 31/03/2024','Ex. 31/03/2025','Cumul 3 ex.']])
row=[2]
def line(lab,fs,cum='sum',fmt=INT,exp=None):
    row[0]+=1; k=row[0]
    c4=f'=SUM(B{k}:D{k})' if cum=='sum' else cum
    S.append([lab]+[cell(S,f,fmt=fmt) for f in fs]+[cell(S,c4,fmt=fmt)])
    if exp:
        for cl,v in zip('BCDE',exp):
            if v is not None: EXP[f'{cl}{k}']=v
    return k
ex_=lambda e: f'"{e}"'
kL=line('Lignes de vente (annexes C)',[f"=COUNTIF({rng('A')},{ex_(e)})" for e in EX],exp=[33220,32758,31791,97769])
kA=line('Lignes dont le taux du fichier est celui appliqué par la caisse',[f"=COUNTIFS({rng('A')},{ex_(e)},{rng('P')},1)" for e in EX],exp=[22300,22018,21261,65579])
k=line('en %',[f'={c}{kA}/{c}{kL}' for c in 'BCD'],cum=f'=E{kA}/E{kL}',fmt=PCT1,exp=[0.671,0.672,0.669,0.671]); EXP.update({f'{cl}{k}':('pct1',v) for cl,v in zip('BCDE',[67.1,67.2,66.9,67.1])})
kD=line('Lignes en désaccord',[f"=COUNTIFS({rng('A')},{ex_(e)},{rng('P')},0)" for e in EX],exp=[10920,10740,10530,32190])
line('dont lignes où l\'article précédent a le même taux appliqué',[f"=COUNTIFS({rng('A')},{ex_(e)},{rng('P')},0,{rng('Q')},1)" for e in EX],exp=[0,0,0,0])
line('dont première ligne d\'une note (taux venu de la note précédente)',[f"=COUNTIFS({rng('A')},{ex_(e)},{rng('P')},0,{rng('T')},1)" for e in EX],exp=[3101,3082,2711,8894])
PR=lambda col: f"'Paliers'!${col}$2:${col}${1+NP}"
kT=line('Tickets du journal de TVA',[f"=COUNTIF({PR('A')},{ex_(e)})" for e in EX],exp=[5658,5529,5418,16605])
line('Tickets dont les paliers C égalent les paliers G au centime, taux appliqué',[f"=COUNTIFS({PR('A')},{ex_(e)},{PR('O')},1)" for e in EX],exp=[5658,5529,5418,16605])
k=line('idem, taux de la colonne 16',[f"=COUNTIFS({PR('A')},{ex_(e)},{PR('P')},1)" for e in EX],exp=[1147,1018,1095,3260])
line('en % des tickets',[f'={c}{k}/{c}{kT}' for c in 'BCD'],cum=f'=E{k}/E{kT}',fmt=PCT1)
EXP[f'E{row[0]}']=('pct1',19.6)
k=line('idem, taux corrigés par le service (colonne E)',[f"=COUNTIFS({PR('A')},{ex_(e)},{PR('Q')},1)" for e in EX],exp=[4312,4664,4675,13651])
line('en % des tickets',[f'={c}{k}/{c}{kT}' for c in 'BCD'],cum=f'=E{k}/E{kT}',fmt=PCT1); EXP[f'E{row[0]}']=('pct1',82.2)
S.append([]); row[0]+=1
S.append([cell(S,'Constats sur l\'ensemble des trois fichiers mis bout à bout',bold=True),cell(S,'Valeur',bold=True),cell(S,'Sur',bold=True)]); row[0]+=1
def one(lab,f,f2=None,exp=None,exp2=None,fmt=INT):
    row[0]+=1; k=row[0]; S.append([lab,cell(S,f,fmt=fmt),cell(S,f2,fmt=INT) if f2 else None])
    if exp is not None: EXP[f'B{k}']=exp
    if exp2 is not None: EXP[f'C{k}']=exp2
    return k
one('Lignes ayant une ligne précédente (ordre des trois fichiers bout à bout)',f"=COUNT({rng('Q')})",exp=97768)
one('Lignes où la colonne 16 porte le taux appliqué de la ligne précédente',f"=COUNTIF({rng('S')},1)",f"=COUNT({rng('S')})",exp=97768,exp2=97768)
one('Exceptions (accord ≠ même taux que l\'article précédent)',f"=SUM({rng('R')})",exp=0)
one('Lignes dont la colonne 16 de la ligne suivante est le taux appliqué',f"=COUNTIF({rng('Z')},1)",f"=COUNT({rng('Z')})",exp=97768,exp2=97768)
JR=lambda col: f"'Journées'!${col}$2:${col}${1+JD}"
one('Journées comptant au moins une ligne en désaccord',f"=COUNTIF({JR('C')},\">0\")",f"=COUNTA({JR('A')})",exp=658,exp2=659)
one('Seconde série : lignes où la colonne 16 porte le taux appliqué de la ligne précédente',f"=COUNTIFS({rng('W')},1,{rng('S')},1)",f"=COUNTIF({rng('W')},1)",exp=88,exp2=88)
RR=lambda col: f"'Références'!${col}$2:${col}${1+NR}"
one('Références (323)',f"=COUNTA({RR('A')})",exp=323)
one('Références vendues au moins deux fois à taux unique, taux de la ligne suivante',f"=COUNTIFS({RR('C')},\">=2\",{RR('D')},1)",f"=COUNTIF({RR('C')},\">=2\")",exp=316,exp2=316)
one('idem, taux de la même ligne (témoin)',f"=COUNTIFS({RR('C')},\">=2\",{RR('E')},1)",f"=COUNTIF({RR('C')},\">=2\")",exp=29,exp2=316)
one('Références dont le taux de la ligne suivante prend deux valeurs sur les trois exercices',f"=COUNTIF({RR('D')},2)",f"=COUNTA({RR('A')})",exp=0,exp2=323)
one('Références restant à deux taux après corrections du service (trois exercices)',f"=COUNTIF({RR('S')},2)",exp=18)
one('dont à deux taux au sein d\'un même exercice',f"=COUNTIFS({RR('S')},2,{RR('T')},2)",exp=8)
one('dont à deux taux d\'un exercice à l\'autre seulement',f"=COUNTIFS({RR('S')},2,{RR('T')},1)",exp=10)
one('Lignes du journal G où VAT_base = palier C (taux appliqué) − taux, au centime',f"=COUNTIF('Paliers lignes G'!$L$2:$L${1+NG},1)",f"=COUNTA('Paliers lignes G'!$A$2:$A${1+NG})",exp=29588,exp2=29588)
one('Lignes du journal G où tax_amount = ROUND(palier × taux / (100 + taux) ; 2)',f"=COUNTIF('Paliers lignes G'!$M$2:$M${1+NG},1)",f"=COUNTA('Paliers lignes G'!$A$2:$A${1+NG})")
S.append([]); row[0]+=1
S.append([cell(S,'Tableau 57 : références vendues apparaissant aux deux taux selon la source du taux',bold=True)]); row[0]+=1
S.append([cell(S,h,bold=True,fill=True) for h in ['Exercice','Références vendues','Aux deux taux, colonne 16','En %','Aux deux taux, après corrections du service','En %','Aux deux taux, taux appliqué']]); row[0]+=1
exp57=[(291,239,82.1,3,1.0,0),(310,256,82.6,4,1.3,0),(295,246,83.4,1,0.3,0)]
for j,e in enumerate(EX):
    base='GKO'[j]; cl=[chr(ord(base)+t) for t in range(4)]   # colonnes lignes, col16, service, appliqué de l'exercice
    row[0]+=1; k=row[0]
    S.append([e,cell(S,f"=COUNTIF({RR(cl[0])},\">0\")",fmt=INT),cell(S,f"=COUNTIF({RR(cl[1])},2)",fmt=INT),cell(S,f'=C{k}/B{k}',fmt=PCT1),cell(S,f"=COUNTIF({RR(cl[2])},2)",fmt=INT),cell(S,f'=E{k}/B{k}',fmt=PCT1),cell(S,f"=COUNTIF({RR(cl[3])},2)",fmt=INT)])
    a=exp57[j]; EXP.update({f'B{k}':a[0],f'C{k}':a[1],f'D{k}':('pct1',a[2]),f'E{k}':a[3],f'F{k}':('pct1',a[4]),f'G{k}':a[5]})
S.append([]); row[0]+=1
S.append([cell(S,'Tableau 57 bis : l\'extrait de la p. 44 (onglet « Extrait p. 44 »)',bold=True),cell(S,'32 lignes reproduites p. 44',bold=True),cell(S,'40 lignes des six notes',bold=True)]); row[0]+=1
XR=lambda col: f"'Extrait p. 44'!${col}$2:${col}$41"
XV=XR('P')
for lab,col,e1,e2 in [('Le taux du fichier est celui de l\'article de la ligne précédente','Q',32,40),('Le taux du fichier est celui appliqué par la caisse','R',24,28),('La caisse a appliqué le taux légal','S',32,40),
                      ('Lignes signalées par la colonne E du service','T',10,14),('dont artefacts du décalage','U',8,12),('dont « Père Gregoire » porté vers 10 %','V',2,2)]:
    row[0]+=1; k=row[0]; S.append([lab,f"=COUNTIFS({XV},1,{XR(col)},1)",f"=COUNTIF({XR(col)},1)"]); EXP[f'B{k}']=e1; EXP[f'C{k}']=e2
row[0]+=1; k=row[0]
S.append(['Notes dont les paliers C égalent les paliers G et dont la TVA égale la TVA légale, au centime',f"=COUNTIFS('Extrait p. 44'!$J${hrow+1}:$J${hrow+NX},1,'Extrait p. 44'!$K${hrow+1}:$K${hrow+NX},1)",f"=COUNT('Extrait p. 44'!$A${hrow+1}:$A${hrow+NX})"]); EXP[f'B{k}']=6; EXP[f'C{k}']=6
row[0]+=1; k=row[0]; S.append(['Lignes visibles sur l\'image p. 44 (filtre Qte = 0,50)',f"=SUM({XV})",'=COUNT(\'Extrait p. 44\'!$A$2:$A$41)']); EXP[f'B{k}']=32; EXP[f'C{k}']=40
fn=PIECES+'161-R2-decalage-champ-taux-annexes-C-97769-lignes.xlsx'
w.save(fn); json.dump({'file':fn,'sheet':'Synthèse','exp':EXP},open(OUT+'b4/exp_161.json','w'),ensure_ascii=False)
print('écrit',fn)
