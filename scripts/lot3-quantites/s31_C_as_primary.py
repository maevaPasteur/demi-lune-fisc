"""Remplace la reconstitution Crec par l'annexe C primaire (CC), enrichie des colonnes de B (Qté B, écart B) par appariement
(date, ticket, libellé, PU, TTC, Qté C) puis (date,ticket,libellé,PU,TTC). Les 75 lignes C absentes de B restent sans colonnes B.
L'ancienne reconstitution est conservée dans cache/Crec_reconstit.pkl."""
import pandas as pd, numpy as np, os, shutil
from collections import defaultdict
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import C
if not os.path.exists(C+'Crec_reconstit.pkl'): shutil.copy(C+'Crec.pkl',C+'Crec_reconstit.pkl')
Old=pd.read_pickle(C+'Crec_reconstit.pkl'); CC=pd.read_pickle(C+'CC.pkl')
r2=lambda x:int(round(float(x)*100))
pool=defaultdict(list); pool2=defaultdict(list)
for i,r in zip(Old.index,Old.itertuples()):
    pool[(r.date,r.ticket,r.lib.strip(),r2(r.pu),r2(r.tot),r2(r.qteC))].append(i)
used=set(); match=[]
for r in CC.itertuples():
    k=(r.date,r.ticket,r.lib_s,r2(r.pu),r2(r.tot),r2(r.qte)); L=[i for i in pool.get(k,[]) if i not in used]
    if not L:
        k2=k[:5]; L=[i for i in Old.index[(Old.date==r.date)&(Old.ticket==r.ticket)&(Old.lib.str.strip()==r.lib_s)&((Old.pu*100).round()==r2(r.pu))&((Old.tot*100).round()==r2(r.tot))] if i not in used]
    if L: used.add(L[0]); match.append(L[0])
    else: match.append(np.nan)
CC['oldidx']=match
print('lignes C appariées à une ligne B :',CC.oldidx.notna().sum(),'/',len(CC),' lignes B non utilisées :',len(Old)-len(used))
N=pd.DataFrame({'ex':CC.ex,'date':CC.date,'ticket':CC.ticket,'lib':CC.lib.astype(str),'pu':CC.pu,'tot':CC.tot,'qteC':CC.qte,'id':CC.id,'heureTicket':CC.heure,
   'rowC':CC.rowC,'Cs':CC.Cs,'Ds':CC.Ds,'disc':CC.disc})
N['qte']=[Old.at[int(i),'qte'] if i==i else np.nan for i in CC.oldidx]
N['B']=[Old.at[int(i),'B'] if i==i else np.nan for i in CC.oldidx]
N['A']=[Old.at[int(i),'A'] if i==i else np.nan for i in CC.oldidx]
N['rowB']=[Old.at[int(i),'rowB'] if i==i else np.nan for i in CC.oldidx]
N['frac']=(N.qte-N.qte.round()).abs()>1e-9
N['inB']=CC.oldidx.notna().values
d=N[N.inB & ((N.qteC-Old.loc[CC.oldidx.dropna().astype(int)].qteC.reindex(CC.oldidx.fillna(-1).astype(int)).values).abs()>1e-6)]
print('lignes où Qté C primaire ≠ Qté C reconstituée :',len(d)); print(d[['ex','date','ticket','lib','qte','qteC','pu','tot','B']].to_string())
N.to_pickle(C+'Crec.pkl')
