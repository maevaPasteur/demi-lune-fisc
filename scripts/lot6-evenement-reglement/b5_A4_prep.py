"""Mission 4 (170) : valeurs ligne à ligne des règles de v01 / v01b et des articles partagés de s13 ; tirages des témoins (200 réplications chacun),
mêmes graines (20261123) et même ordre de tirage que v01 (C1 (5)), v01b (résidu) et s13 (placebo jour + 7, sans tirage). Sortie : cache/b5_A4.pkl."""
import pandas as pd, numpy as np, datetime as dt, pickle
from collections import defaultdict
CA='scripts/lot6-evenement-reglement/cache/'
c=lambda x:int(round(float(x)*100))
H=pd.read_pickle(CA+'H.pkl'); Ht=H.set_index('id')
Cr=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/Crec.pkl'); Cr0=Cr.copy()
Cr=Cr[Cr.inB].copy()
Cr['q']=Cr.qteC.map(lambda x:int(round(x*100))); Cr['qB']=Cr.qte.map(lambda x:int(round(x*100))); Cr['pu_c']=Cr.pu.map(c)
Cr['fracC']=(Cr.qteC-Cr.qteC.round()).abs()>1e-9
Cr['z']=Cr.id.map(Ht.no_z_report); Cr['t']=Cr.id.map(Ht.t); Cr['art']=Cr.lib.astype(str).str.strip()+'|'+Cr.pu_c.astype(str)
shared=set(Cr[Cr.fracC].id); fr=Cr[Cr.id.isin(shared)]
idx=defaultdict(list)
for r in fr.itertuples(): idx[(r.date,r.z,r.art)].append((r.id,r.t,r.q))
D=Cr[Cr.qB!=Cr.q]
# v01 : groupe ±15, note d'origine, placebo (5)
L={}
for r in D.itertuples():
    grp=[(i,t,q) for i,t,q in idx.get((r.date,r.z,r.art),[]) if abs(t-r.t)<=15]
    others=[q for i,t,q in grp if i!=r.id]
    L[r.Index]={'groupe15':int(bool(others)),'egal15':int(bool(others) and r.qB==r.q+sum(others)),'origine15':int(bool(others) and r.id==min(i for i,_,_ in grp))}
oth_set=set()
for r in D.itertuples():
    for i,t,q in idx.get((r.date,r.z,r.art),[]):
        if i!=r.id and abs(t-r.t)<=15: oth_set.add((i,r.art))
PART=Cr[[(i,a) in oth_set for i,a in zip(Cr.id,Cr.art)]][['ex','date','ticket','id','art','qB','q']]
rng=np.random.default_rng(20261123)
notes_day=H[(H.serie==1)&(H.tot_ttc_c!=0)].groupby('date_ticket').id.apply(list).to_dict()
qmap=defaultdict(int)
for r in Cr.itertuples(): qmap[(r.id,r.art)]+=r.q
pl1=[]
for rep in range(200):
    k=0
    for r in D.itertuples():
        grp=[i for i,t,q in idx.get((r.date,r.z,r.art),[]) if abs(t-r.t)<=15 and i!=r.id]
        if not grp: continue
        cand=[i for i in notes_day.get(r.date,[]) if i!=r.id]
        pick=rng.choice(cand,min(len(grp),len(cand)),replace=False)
        if r.qB==r.q+sum(qmap.get((i,r.art),0) for i in pick): k+=1
    pl1.append(k)
print('témoin règle stricte : moyenne',np.mean(pl1),'max',max(pl1))
# v01b : fenêtres, sous-ensemble, unités entières
for r in D.itertuples():
    ok=None
    for W in (15,30,60,2000):
        oth=[q for i,t,q in idx.get((r.date,r.z,r.art),[]) if i!=r.id and abs(t-r.t)<=W]
        if oth and r.qB==r.q+sum(oth): ok=W; break
    sub=False
    if ok is None:
        oth=[q for i,t,q in idx.get((r.date,r.z,r.art),[]) if i!=r.id]
        need=r.qB-r.q; s={0}
        for q in oth: s|={x+q for x in s}
        sub=need in s and need>0
    L[r.Index].update({'fenetre':ok,'sous_ensemble':int(sub)})
allidx=defaultdict(list)
for r in Cr.itertuples(): allidx[(r.date,r.z,r.art)].append((r.id,r.t,r.q))
for r in D.itertuples():
    d=L[r.Index]; d['unites']=0
    if d['fenetre'] is None and not d['sous_ensemble']:
        oth=[q for i,t,q in allidx.get((r.date,r.z,r.art),[]) if i!=r.id and abs(t-r.t)<=15]
        d['unites']=int(bool(oth) and r.qB==r.q+sum(oth))
Dd=D.reset_index(drop=True); Cr_z=Dd.z.values; Cr_id=Dd.id.values; Cr_t=Dd.t.values
rest=[j for j,ix in enumerate(D.index) if L[ix]['fenetre'] is None and not L[ix]['sous_ensemble']]
rng=np.random.default_rng(20261123)
nd=notes_day; pl2=[]
for rep in range(200):
    k=0
    for j in rest:
        r=Dd.iloc[j]; n=len([1 for i,t,q in allidx.get((r.date,Cr_z[j],r.art),[]) if i!=Cr_id[j] and abs(t-Cr_t[j])<=15])
        if n==0: continue
        cand=[i for i in nd.get(r.date,[]) if i!=Cr_id[j]]; pick=rng.choice(cand,min(n,len(cand)),replace=False)
        if r.qB==r.q+sum(qmap.get((i,r.art),0) for i in pick): k+=1
    pl2.append(k)
print('témoin unités entières : moyenne',np.mean(pl2),'max',max(pl2))
# s13 : articles partagés
E=pd.read_pickle(CA+'E.pkl'); CC=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/CC.pkl')
CC['pu_c']=CC.pu.map(c); CC['t']=CC.heure.map(lambda h:int(h[:2])*60+int(h[3:5]))
frs=CC[CC.frac].drop_duplicates(['id','ref','pu_c'])
De=E[E.typEven=='DEL']
base=pd.DataFrame({'d':De.dateEven,'z':De.no_zEport,'t':De.t,'a':De.amount_c})
zday=H.groupby('date_ticket').no_z_report.first().to_dict()
def build(Dx):
    ix=defaultdict(list)
    for r in Dx.itertuples(): ix[(r.d,r.z)].append((r.t,r.a))
    return ix
P1=base.copy(); P1['d']=[(dt.date.fromisoformat(x)-dt.timedelta(days=7)).isoformat() for x in P1.d]
P1['z']=P1.d.map(zday); P1=P1.dropna(subset=['z']); P1['z']=P1.z.astype(int)
def hits(ix): return [int(any(r.t-60<=t<=r.t+15 and a==r.pu_c for t,a in ix.get((r.date,r.z),[]))) for r in frs.itertuples()]
SH=frs[['ex','date','heure','id','ref','lib','pu']].copy(); SH['reel']=hits(build(base)); SH['j7']=hits(build(P1))
print('articles partagés',len(SH),SH.reel.sum(),SH.j7.sum())
Dout=D[['ex','date','ticket','id','art','qB','q']].copy()
for k in ['groupe15','egal15','origine15','fenetre','sous_ensemble','unites']: Dout[k]=[L[i][k] for i in D.index]
pickle.dump({'D':Dout,'PART':PART,'pl1':pl1,'pl2':pl2,'SH':SH},open(CA+'b5_A4.pkl','wb'))
