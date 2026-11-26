"""C1 complément : égalité Qté B = Qté C + Σ partenaires sous au moins une fenêtre (±15, ±30, ±60, journée du Z) ; résidu listé."""
import pandas as pd, numpy as np
from collections import defaultdict
CA='scripts/lot6-evenement-reglement/cache/'
c=lambda x:int(round(float(x)*100))
H=pd.read_pickle(CA+'H.pkl'); Ht=H.set_index('id')
Cr=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/Crec.pkl'); Cr=Cr[Cr.inB].copy()
Cr['q']=Cr.qteC.map(lambda x:int(round(x*100))); Cr['qB']=Cr.qte.map(lambda x:int(round(x*100)))
Cr['art']=Cr.lib.astype(str).str.strip()+'|'+Cr.pu.map(c).astype(str)
Cr['z']=Cr.id.map(Ht.no_z_report); Cr['t']=Cr.id.map(Ht.t)
Cr['fracC']=(Cr.qteC-Cr.qteC.round()).abs()>1e-9
shared=set(Cr[Cr.fracC].id); fr=Cr[Cr.id.isin(shared)]
idx=defaultdict(list)
for r in fr.itertuples(): idx[(r.date,r.z,r.art)].append((r.id,r.t,r.q))
D=Cr[Cr.qB!=Cr.q]
res=[]
for r in D.itertuples():
    ok=None
    for W in (15,30,60,2000):
        oth=[q for i,t,q in idx.get((r.date,r.z,r.art),[]) if i!=r.id and abs(t-r.t)<=W]
        if oth and r.qB==r.q+sum(oth): ok=W; break
    # sous-ensemble : un sous-groupe des partenaires du jour suffit-il ?
    sub=False
    if ok is None:
        oth=[q for i,t,q in idx.get((r.date,r.z,r.art),[]) if i!=r.id]
        need=r.qB-r.q; s={0}
        for q in oth: s|={x+q for x in s}
        sub=need in s and need>0
    res.append((r.ex,r.date,r.ticket,r.art,r.qB,r.q,ok,sub,r.id in shared))
R=pd.DataFrame(res,columns=['ex','date','ticket','art','qB','qC','fenetre','sous_ensemble','note_partagee'])
out=open('scripts/lot6-evenement-reglement/out/v01b_C1_union.txt','w')
def p(*a): print(*a); print(*a,file=out)
p('égalité sous une fenêtre :',R.fenetre.value_counts(dropna=False).to_dict())
p('sans égalité de fenêtre mais égalité avec un sous-ensemble des partenaires du jour :',int(R.sous_ensemble.sum()))
rest=R[R.fenetre.isna()&~R.sous_ensemble]
p('résidu :',len(rest),' ; dont note sans aucune ligne fractionnaire en C :',int((~rest.note_partagee).sum()),' ; Qté B − Qté C dans le résidu (centièmes) :',rest.assign(d=rest.qB-rest.qC).d.value_counts().head(8).to_dict())
p(rest.head(40).to_string())
R.to_csv('scripts/lot6-evenement-reglement/out/v01b_C1_lignes.csv',index=False)
out.close()
# résidu : partenaires = toutes notes du même (date, Z) dans ±15 / ±60 min portant le même article (quantité quelconque) ; placebo : partenaires tirés au hasard le même jour
out=open('scripts/lot6-evenement-reglement/out/v01b_C1_union.txt','a')
allidx=defaultdict(list)
for r in Cr.itertuples(): allidx[(r.date,r.z,r.art)].append((r.id,r.t,r.q))
def test(rows,W):
    k=0
    for r in rows.itertuples():
        oth=[q for i,t,q in allidx.get((r.date,Cr_z[r.Index],r.art),[]) if i!=Cr_id[r.Index] and abs(t-Cr_t[r.Index])<=W]
        if oth and r.qB==r.qC+sum(oth): k+=1
    return k
Dd=D.reset_index(drop=True); Cr_z=Dd.z.values; Cr_id=Dd.id.values; Cr_t=Dd.t.values
restI=R.index[R.fenetre.isna()&~R.sous_ensemble]
rr=R.loc[restI]
for W in (15,60):
    p(f'résidu {len(rr)} : égalité avec partenaires non fractionnaires (même article, même Z, ±{W} min) : {test(rr,W)}')
rng=np.random.default_rng(20261123)
nd=H[(H.serie==1)&(H.tot_ttc_c!=0)].groupby('date_ticket').id.apply(list).to_dict()
qmap=defaultdict(int)
for r in Cr.itertuples(): qmap[(r.id,r.art)]+=r.q
pl=[]
for rep in range(200):
    k=0
    for j in restI:
        r=R.loc[j]; n=len([1 for i,t,q in allidx.get((r.date,Cr_z[j],r.art),[]) if i!=Cr_id[j] and abs(t-Cr_t[j])<=15])
        if n==0: continue
        cand=[i for i in nd.get(r.date,[]) if i!=Cr_id[j]]; pick=rng.choice(cand,min(n,len(cand)),replace=False)
        if r.qB==r.qC+sum(qmap.get((i,r.art),0) for i in pick): k+=1
    pl.append(k)
p(f'placebo (partenaires au hasard le même jour, 200 tirages) sur le résidu : moyenne {np.mean(pl):.1f}, max {np.max(pl)}')
out.close()
