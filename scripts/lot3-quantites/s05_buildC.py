"""Reconstitution d'une annexe C ligne à ligne, datée, à partir de :
 - B (date, n° ticket, libellé, PU, Total TTC) : 97 694 lignes
 - Lignes C (78) pour la Qté C des 11 026 lignes fractionnaires (rattachées à B par clé)
 - Qté C des autres lignes : Qté B si écart nul ; sinon Total/PU (ligne de clôture)
Contrôle : multiset (PU, Qté, CA) de la reconstitution vs Sources_C (89), sans date.
Sortie : cache/Crec.pkl"""
import pandas as pd, numpy as np
from collections import Counter, defaultdict
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import C
B=pd.read_pickle(C+'B.pkl'); LC=pd.read_pickle(C+'LC.pkl'); SC=pd.read_pickle(C+'SC.pkl'); F=pd.read_pickle(C+'F.pkl')
r2=lambda x: int(round(float(x)*100))
LC['date']=LC.date.astype(str)
B['key']=list(zip(B.ex,B.date,B.ticket,B.lib.str.strip(),B.pu.map(r2),B.tot.map(r2)))
LC['key']=list(zip(LC.ex,LC.date,LC.note.astype(int),LC.lib.astype(str).str.strip(),LC.pu.map(r2),LC.enc.map(r2)))
# greedy assignment: prefer B rows with negative écart? ambiguous only if duplicates; record ambiguity
pool=defaultdict(list)
for i,k in zip(B.index,B.key): pool[k].append(i)
B['lc_row']=np.nan; amb=0
for j,k in zip(LC.index,LC.key):
    cand=pool[k]
    if len(cand)>1: amb+=1
    # choose candidate whose B qte is closest to LC qte (identical if écart nul), else first
    q=LC.at[j,'qte']
    cand.sort(key=lambda i: abs(B.at[i,'qte']-q))
    i=cand.pop(0); B.at[i,'lc_row']=j
print('LC lines assigned',B.lc_row.notna().sum(),'ambiguous keys',amb)
B['qteC']=np.where(B.lc_row.notna(), B.lc_row.map(lambda j: LC.at[int(j),'qte'] if j==j else np.nan), np.nan)
neg=B.B< -0.005
B.loc[B.qteC.isna() & ~neg,'qteC']=B.qte
m=B.qteC.isna() & neg
B.loc[m,'qteC']=(B.tot/B.pu)[m]
print('closing lines (écart<0) not in LC: ',m.sum(),' of which tot/pu non-integer:',(abs(B.loc[m,'qteC']-B.loc[m,'qteC'].round())>0.001).sum())
B.loc[m,'qteC']=B.loc[m,'qteC'].round(2)
# affinage : chaque ligne B consomme une ligne de Sources_C de même (PU, total) ; on retient la Qté C la plus proche de l'estimation
B['qteC_est']=B.qteC; B['qteC_src']='est'
for ex in ['2022-2023','2023-2024','2024-2025']:
    c=SC[SC.ex==ex]; bucket=defaultdict(list)
    for pu,ca,q in zip(c.puC.map(r2),c.caC.map(r2),c.qteC): bucket[(pu,ca)].append(q)
    idx=B.index[B.ex==ex]
    # d'abord les lignes LC (exactes), puis les autres
    order=sorted(idx,key=lambda i: 0 if B.at[i,'lc_row']==B.at[i,'lc_row'] else 1)
    for i in order:
        k=(r2(B.at[i,'pu']),r2(B.at[i,'tot'])); q0=B.at[i,'qteC']; lst=bucket[k]
        if not lst: B.at[i,'qteC_src']='absent_SC'; continue
        jbest=min(range(len(lst)),key=lambda j: abs(lst[j]-q0)); q=lst.pop(jbest)
        if abs(q-q0)>1e-6: B.at[i,'qteC_src']='SC_diff'
        else: B.at[i,'qteC_src']='SC_eq'
        B.at[i,'qteC']=q
print(B.qteC_src.value_counts())
print(B[B.qteC_src=='SC_diff'][['ex','date','ticket','lib','qte','pu','tot','B','qteC_est','qteC']].to_string())
print('B frac lines with écart 0 assigned to LC:',(B.lc_row.notna() & ~neg & B.frac).sum(), ' B closing lines assigned to LC:',(B.lc_row.notna()&neg).sum(),' B integer écart-0 lines assigned to LC (should be 0):',(B.lc_row.notna()&~neg&~B.frac).sum())
# id note
fi=F[F.tot_ttc!=0].drop_duplicates('id')[['ex','dateTicket','no_ticket','id','heureTicket','tot_ttc']]
B=B.merge(fi,left_on=['ex','date','ticket'],right_on=['ex','dateTicket','no_ticket'],how='left').drop(columns=['dateTicket','no_ticket'])
# LC id consistency
chk=B[B.lc_row.notna()]
print('LC id == F id (via date,ticket):',(chk.lc_row.map(lambda j: LC.at[int(j),'id']).values==chk.id.values).sum(),'/',len(chk))
for ex in ['2022-2023','2023-2024','2024-2025']:
    b=B[B.ex==ex]; c=SC[SC.ex==ex]
    m1=Counter(zip(b.pu.map(r2),b.qteC.map(r2),b.tot.map(r2))); m2=Counter(zip(c.puC.map(r2),c.qteC.map(r2),c.caC.map(r2)))
    print(ex,'Crec lines',len(b),'sumQ Crec',round(b.qteC.sum(),2),'| multiset vs SC: only Crec',sum((m1-m2).values()),'only SC',sum((m2-m1).values()))
    if sum((m1-m2).values()): print('   onlyCrec',sorted((m1-m2).items())[:20])
B.to_pickle(C+'Crec.pkl')
