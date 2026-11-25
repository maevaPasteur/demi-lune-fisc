"""Contrôle au niveau de la note : pour chaque note B portant ≥1 ligne à écart négatif (hors remises),
existe-t-il un même ensemble S d'autres notes du jour (|S|≤6, à ±W min) qui explique TOUTES ses lignes négatives
(Q : qC + ΣqC(S) = qB ; M : Σtot(S) = |écart| ± 0,01×(|S|+1)) ET aucune incohérence sur ses lignes à écart nul
(un article de la note présent dans S ne devrait pas avoir écart nul si la note est la note de clôture) ?
Mesure aussi si la note de clôture est la dernière encaissée du groupe."""
import pandas as pd, numpy as np, itertools, sys
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import C
Cr=pd.read_pickle(C+'Crec.pkl'); Fid=pd.read_pickle(C+'Fid2.pkl')
tabs,nd,A=pd.read_pickle(C+'recompo_base.pkl')
Cr['lib_s']=Cr.lib.str.strip(); Cr['pu100']=(Cr.pu*100).round().astype(int)
Cr['t']=Cr.id.map(Fid.t); Cr['neg']=Cr.B< -0.005
Cr['tot100']=(Cr.tot*100).round().astype(int); Cr['q100']=(Cr.qteC*100).round().astype(int); Cr['qB100']=(Cr.qte.fillna(Cr.qteC)*100).round().astype(int)
Cr['e100']=(-(Cr.B.fillna(0))*100).round().astype(int)
Cr['art']=list(zip(Cr.lib_s,Cr.pu100))
day={k:g for k,g in Cr.groupby(['ex','date'])}
W=int(sys.argv[1]) if len(sys.argv)>1 else 60
notes=Cr[Cr.neg & (Cr.qB100!=Cr.q100)].id.unique()
out=[]
for nid in notes:
    N=Cr[Cr.id==nid]; ex=N.ex.iloc[0]; d=N.date.iloc[0]; tN=N.t.iloc[0]
    negL=N[N.neg & (N.qB100!=N.q100)]
    D=day[(ex,d)]
    P=D[(D.id!=nid)&((D.t-tN).abs()<=W)]
    arts=set(negL.art)
    Pn=P[P.art.isin(arts)]
    pids=list(Pn.id.unique())
    # agrégat par note partenaire et article
    agg=Pn.groupby(['id','art']).agg(q=('q100','sum'),m=('tot100','sum'))
    agg=agg.to_dict('index')
    best=None
    for k in range(1,min(6,len(pids))+1):
        for S in itertools.combinations(pids,k):
            ok=True
            for L in negL.itertuples():
                q=sum(agg.get((s,L.art),{'q':0})['q'] for s in S); m=sum(agg.get((s,L.art),{'m':0})['m'] for s in S)
                if abs(L.q100+q-L.qB100)>1 or abs(m-L.e100)>k+1: ok=False; break
            if ok:
                # chaque note de S doit porter au moins un des articles
                best=S; break
        if best: break
    rec=dict(id=nid,ex=ex,date=d,ticket=N.ticket.iloc[0],t=tN,nneg=len(negL),e=negL.e100.sum()/100,npart=len(pids),
             found=best is not None, S=best, k=len(best) if best else 0)
    if best:
        ts=[Fid.t[s] for s in best]
        rec['last']= tN>=max(ts); rec['span']=max(ts+[tN])-min(ts+[tN])
        # lignes à écart nul de N dont l'article figure dans S (incohérence potentielle)
        z=N[~N.neg]; zs=[a for a in z.art if any((s,a) in agg for s in best)]
        # agg ne contient que les articles négatifs : recalcul
        Sl=D[D.id.isin(best)]; zs=set(z.art)&set(Sl.art)
        rec['zero_shared']=len(zs)
        rec['same_tab']= all(nd.index.isin([nid]).any() for _ in [0])
    out.append(rec)
O=pd.DataFrame(out); O.to_pickle(C+f'cloture_note_W{W}.pkl')
print('W=',W,'notes avec lignes négatives (hors remises):',len(O),' lignes',O.nneg.sum(),' €',round(O.e.sum(),2))
for ex,g in O.groupby('ex'):
    print(ex,'notes',len(g),'expliquées',g.found.sum(),'non',(~g.found).sum(),'lignes non expl.',g[~g.found].nneg.sum(),'€ non expl.',round(g[~g.found].e.sum(),2))
f=O[O.found]
print('expliquées : k distribution',f.k.value_counts().sort_index().to_dict())
print('note de clôture = dernière encaissée du groupe :',f['last'].sum(),'/',len(f))
print('span (min) quantiles',f.span.describe().to_dict())
print('notes de clôture avec article à écart nul partagé avec S:',(f.zero_shared>0).sum())
print(O[~O.found].head(40).to_string())
