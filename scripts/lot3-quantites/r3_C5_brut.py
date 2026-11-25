"""Montant maximal des parts annulées sans règlement, par fenêtre de regroupement, non arrondi (onglet « Montant par fenêtre »
de l'annexe n° 159). Reprend le calcul C5 de c1_C4C5.py ; sortie cache/out/C5_brut.csv."""
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
import s06_recompo as s6
from s07_sensibilite import arts as artsf
Cr,F,E,Fid,tabs0,nd0,A0=load()
CC=pd.read_pickle(C+'CC.pkl'); Cr=Cr.merge(CC[['rowC','ex','tva']],on=['rowC','ex'],how='left')
Cr['ht']=Cr.tot/(1+Cr.tva/100)
CA={'2022-2023':403370.42,'2023-2024':438281.12,'2024-2025':435564.96}
CAht={ex:round(Cr[Cr.ex==ex].ht.sum(),2) for ex in EX}
REH_HT={'2022-2023':172813,'2023-2024':124010,'2024-2025':125076}; REH_TVA={'2022-2023':20421,'2023-2024':14854,'2024-2025':14652}
D=E[E.typEven=='DEL']; Dd={d:g for d,g in D.groupby('dateEven')}
lines={i:g for i,g in Cr.groupby('id')}
def mdel(d,t0,t1,amts,tol):
    g=Dd.get(d); out=[]
    if g is None: return [None]*len(amts)
    g=g[(g.t>=t0)&(g.t<=t1)]; used=set()
    for a in amts:
        c=[j for j in g.index[(g.amount-a).abs()<=tol] if j not in used]
        if c: used.add(c[0]); out.append(g.at[c[0],'amount'])
        else: out.append(None)
    return out
def majorant(tabs,A):
    res={ex:np.zeros(2) for ex in EX}; det={ex:{'miroir':0,'miroir_partiel':0,'sans_trace':0,'paire':0,'residu_DEL':0,'residu_sans_DEL':0} for ex in EX}
    iso=[x[0] for ex,d,x in tabs if len(x)==1]; isoset=set(iso)
    for i in iso:
        L=lines[i]; ex=L.ex.iloc[0]; d=L.date.iloc[0]; t=Fid.t[i]
        m=mdel(d,t-5,t+30,list(L.tot),0.02)
        if all(x is not None for x in m):
            res[ex]+=[sum(m),(L.ht).sum()]; det[ex]['miroir']+=sum(m); continue
        Lf=L[L.fracC]; mf=[x for x,fr in zip(m,L.fracC) if fr and x is not None]
        # contrepartie payée (autre note isolée jumelle du même jour)
        day=Cr[(Cr.date==d)&(Cr.id!=i)&Cr.fracC]
        for r,x in zip(L.itertuples(),m):
            if not r.fracC: continue
            if x is not None: res[ex]+=[x,x/(1+r.tva/100)]; det[ex]['miroir_partiel']+=x; continue
            o=day[(day.libn==r.libn)&(day.pu100==r.pu100)]
            if (((o.qteC+r.qteC)-(o.qteC+r.qteC).round()).abs()<0.02).any(): det[ex]['paire']+=0; continue   # contrepartie payée le même jour
            c_=(math.ceil(r.qteC-1e-9)-r.qteC)*r.pu; res[ex]+=[c_,c_/(1+r.tva/100)]; det[ex]['sans_trace']+=c_
    for (ex,d,k),g in A[~A.ref].groupby(['ex','date','tab']):
        ids=tabs[k][2]; ts=[Fid.t[i] for i in ids]
        comps=[round((math.ceil(r.somme-1e-9)-r.somme)*r.pu,2) for r in g.itertuples()]
        m=mdel(d,min(ts)-5,max(ts)+30,comps,0.05)
        for r,c_,x in zip(g.itertuples(),comps,m):
            rate=Cr[(Cr.id.isin(ids))&(Cr.lib_s==r.lib)&((Cr.pu-r.pu).abs()<0.001)].tva.iloc[0]
            v=x if x is not None else c_
            res[ex]+=[v,v/(1+rate/100)]; det[ex]['residu_DEL' if x is not None else 'residu_sans_DEL']+=v
    return res,det
rows=[]
for W in [5,10,15,20,30,60,None]:
    tabs,nd=s6.build(W or 0,True,nowin=(W is None)); A=artsf(tabs); A['ref']=(A.somme-A.somme.round()).abs()<0.02
    res,det=majorant(tabs,A)
    r=dict(fenetre='jour' if W is None else W)
    for ex in EX: r[ex+' TTC']=round(res[ex][0],6); r[ex+' HT']=round(res[ex][1],6)
    r['Total TTC']=round(sum(res[ex][0] for ex in EX),2); r['Total HT']=round(sum(res[ex][1] for ex in EX),2)
    for k in ['miroir','miroir_partiel','sans_trace','residu_DEL','residu_sans_DEL']: r[k]=round(sum(det[ex][k] for ex in EX),2)
    rows.append(r)
M=pd.DataFrame(rows); pd.set_option('display.width',300); print('C5 majorant consolidé'); print(M.to_string(index=False)); M.to_csv(OUT+'C5_brut.csv',index=False)
