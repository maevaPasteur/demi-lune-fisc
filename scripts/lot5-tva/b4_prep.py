"""B4 : préparation des tables des pièces 161 à 164 (contrôle des chiffres avant écriture)."""
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
CC=pd.read_pickle(CA+'C_b3.pkl')
T=pd.read_pickle(CA+'B5_tickets.pkl'); gid=set(T.index)
CC['s2']=[0 if (a,b) in gid else 1 for a,b in zip(CC.ex,CC.id)]
CC['first']=(CC.groupby('ex').id.shift(1)!=CC.id).astype(int)
print('pos0 == first :',int(((CC.pos==0).astype(int)==CC['first']).all()))
CC['acc']=(CC.rf==CC.rart).astype(int)
for ex in EX:
    x=CC[CC.ex==ex]; print(ex,len(x),x.acc.sum(),(1-x.acc).sum(),((x.acc==0)&(x['first']==1)).sum(),'s2',x.s2.sum())
f1=CC[CC.prev_rart.isna()]; print('1res lignes',f1[['ex','rowC','rf','rart','acc']].values.tolist())
m=CC.prev_rart.notna(); print('rf==prev',int((CC.rf[m]==CC.prev_rart[m]).sum()),m.sum(),'exceptions',int(((CC.acc==1)!=(CC.rart==CC.prev_rart))[m].sum()))
d=CC[m].groupby('date').acc.min(); print('journées',len(CC.date.unique()),'avec désaccord',int((CC.groupby('date').acc.min()==0).sum()))
s2=CC[CC.s2==1]; print('s2 lignes',len(s2),'rf==prev',int((s2.rf==s2.prev_rart).sum()))
# concat order: first line of C2 and C3 vs last of previous
for ex0,ex1 in [(EX[0],EX[1]),(EX[1],EX[2])]:
    a=CC[CC.ex==ex0].iloc[-1]; b=CC[CC.ex==ex1].iloc[0]; print(ex1,'1re ligne rf',b.rf,'rart',b.rart,'taux art. dernière ligne préc.',a.rart)
# refs
g=CC.groupby('ref'); n=g.size()
nxt=CC.groupby('ex').rf.shift(-1); CC['nxt']=nxt
u_next=CC.dropna(subset=['nxt']).groupby('ref').nxt.nunique(); u_same=g.rf.nunique()
print('refs',len(n),'≥2 lignes',(n>=2).sum(),'unique next (≥2)',int(((n>=2)&(u_next.reindex(n.index)==1)).sum()),'unique same (≥2)',int(((n>=2)&(u_same==1)).sum()), 'rart unique',int((g.rart.nunique()==1).sum()))
print('next_rf vs nxt equal',int((CC.next_rf.fillna(-1)==CC.nxt.fillna(-1)).sum()))
