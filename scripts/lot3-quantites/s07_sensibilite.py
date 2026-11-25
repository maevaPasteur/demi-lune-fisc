"""Sensibilité de la recomposition : seuil eps et fenêtre W ; variantes (<= / <, partage d'article exigé ou non, sans fenêtre).
Réutilise build() de s06 ; calcul des articles accéléré."""
import pandas as pd, os, sys, math
from collections import defaultdict
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from s06_recompo import build, NOTES, Fid
from common import C
lines=defaultdict(list)
for r in NOTES.itertuples(): lines[r.id].append((r.lib_s,r.pu100,r.qteC,r.fracC))
def arts(tabs):
    rows=[]
    for k,(ex,d,ids) in enumerate(tabs):
        if len(ids)<2: continue
        s=defaultdict(float); fk={}; nn=defaultdict(set)   # fk : dictionnaire ordonné (ordre de première apparition)
        for i in ids:
            for lib,pu,q,f in lines[i]:
                s[(lib,pu)]+=q; nn[(lib,pu)].add(i)
                if f: fk.setdefault((lib,pu))
        for a in fk:   # ordre fixe, indépendant de la randomisation des hachages (PYTHONHASHSEED)
            rows.append((k,ex,d,a[0],a[1]/100,round(s[a],6),len(nn[a]),len(ids)))
    return pd.DataFrame(rows,columns=['tab','ex','date','lib','pu','somme','nn','ntab'])
def summ(tabs,A,eps):
    A=A.copy(); A['ref']=(A.somme-A.somme.round()).abs()<eps
    A['comp']=[0.0 if r else (math.ceil(s-1e-9)-s)*p for r,s,p in zip(A.ref,A.somme,A.pu)]
    T=[t for t in tabs if len(t[2])>=2]
    out={}
    for ex in ['2022-2023','2023-2024','2024-2025','ALL']:
        a=A if ex=='ALL' else A[A.ex==ex]
        tt=[t for t in T if ex=='ALL' or t[0]==ex]
        nids=[i for t in tt for i in t[2]]
        out[ex]=dict(tables=len(tt),notes_tab=len(nids),notes_iso=sum(1 for t in tabs if len(t[2])==1 and (ex=='ALL' or t[0]==ex)),
            art=len(a),ref=int(a.ref.sum()),nonref=int((~a.ref).sum()),comp=round(a.comp.sum(),2),tab_res=a[~a.ref].tab.nunique(),
            tot_tab=round(sum(Fid.tot[i] for i in nids),2),tab_full=len(tt)-a[~a.ref].tab.nunique())
    return out
if __name__=='__main__':
    rows=[]
    for le in [True,False]:
      for share in [True,False]:
        for W in [5,10,15,20,30,60,None]:
            tabs,nd=build(W if W is not None else 0, share=share, nowin=(W is None), le=le)
            A=arts(tabs)
            for eps in [0.001,0.005,0.01,0.011,0.015,0.02,0.021,0.03,0.05,0.051]:
                o=summ(tabs,A,eps)
                for ex,v in o.items():
                    v.update(cmp='<=' if le else '<',share=share,W='jour' if W is None else W,eps=eps,exo=ex); rows.append(v)
    R=pd.DataFrame(rows); R['taux']=(R.ref/R.art*100).round(2)
    R.to_pickle(C+'sensibilite.pkl')
    pd.set_option('display.width',300); pd.set_option('display.max_rows',1000)
    print(R[R.exo=='ALL'][['cmp','share','W','eps','tables','notes_tab','notes_iso','art','ref','nonref','taux','comp','tab_res','tot_tab']].to_string())
