"""Classification exhaustive des 7 149 lignes B à écart négatif (catégories (a) à (m) ci-dessous) + contrôle quantité.
Sorties : cache/B02_neg.pkl et cache/out/B02_*.csv.
(a) note de clôture exacte d'un article refermé de 77 ; (b) clôture « autre quantité » (49) ; (r) clôture d'un article du résidu ;
(c1) contrepartie en montant (±0,02 €, ≤ 6 notes) à ±30 min, sur une note de la même table 77 (article non fractionné) ;
(c2) idem hors table 77 ; (d) contrepartie trouvée seulement sur la journée ; (e) aucune ; (m) remise (Qté B = Qté C)."""
import os, sys, itertools; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
from collections import defaultdict
Cr,F,E,Fid,tabs,nd,A=load()
Cr['neg']=Cr.B< -0.005
Cr['e100']=(-(Cr.B.fillna(0))*100).round().astype(int); Cr['tot100']=(Cr.tot*100).round().astype(int)
note2tab={i:k for k,(ex,d,ids) in enumerate(tabs) if len(ids)>=2 for i in ids}
Cr['tab']=Cr.id.map(note2tab)
neg=Cr[Cr.neg].copy()
neg['cat']=None
# (a)(b)(r) : lignes de clôture des articles 77
by=defaultdict(list)
for i,r in zip(neg.index,neg.itertuples()): by[(r.id,r.libn,r.pu100)].append(i)
A=A.copy(); A['pu100']=(A.pu*100).round().astype(int); A['libn']=A.lib.map(norm)
for r in A.itertuples():
    L=[i for k in r.ids for i in by.get((k,r.libn,r.pu100),[]) if abs(neg.at[i,'qte']-round(neg.at[i,'qte']))<1e-9]
    tgt=round(r.somme)
    for i in L:
        if neg.at[i,'cat'] is not None: continue
        if not r.ref: neg.at[i,'cat']='r'
        elif abs(neg.at[i,'qte']-tgt)<0.011: neg.at[i,'cat']='a'
        else: neg.at[i,'cat']='b'
neg.loc[neg.cat.isna() & ((neg.qte-neg.qteC).abs()<1e-9),'cat']='m'
grp={k:g for k,g in Cr.groupby(['date','libn','pu100'])}
def amount_match(L,sub,tol=2,maxk=6):
    per=sub.groupby('id').tot100.sum()
    vals=list(per.values); e=L.e100
    # DP : sommes atteignables avec ≤ maxk notes
    states={0:0}
    for v in vals:
        new=dict(states)
        for s,n in states.items():
            if n<maxk and s+v<=e+tol:
                if s+v not in new or new[s+v]>n+1: new[s+v]=n+1
        states=new
    return any(n>0 and abs(s-e)<=tol for s,n in states.items())
for i in neg.index[neg.cat.isna()]:
    L=neg.loc[i]; g=grp[(L.date,L.libn,L.pu100)]; oth=g[g.id!=L.id]
    w=oth[(oth.t-L.t).abs()<=30]
    if len(w) and amount_match(L,w):
        intab = L.tab==L.tab and (w.tab==L.tab).any() and amount_match(L,w[w.tab==L.tab])
        neg.at[i,'cat']='c1' if intab else 'c2'
    elif len(oth) and amount_match(L,oth): neg.at[i,'cat']='d'
    else: neg.at[i,'cat']='e'
neg['qC_frac']=(neg.qteC-neg.qteC.round()).abs()>1e-9
neg['e']=neg.e100/100
lab={'a':'(a) clôture exacte article refermé 77','b':'(b) clôture autre quantité (49)','r':'(r) clôture article du résidu','m':'(m) remise (Qté B = Qté C)',
     'c1':'(c1) contrepartie ±30 min, même table 77 (article entier)','c2':'(c2) contrepartie ±30 min hors table 77','d':'(d) contrepartie sur la journée seulement','e':'(e) aucune contrepartie'}
neg['catl']=neg.cat.map(lab)
T1=pd.crosstab(neg.catl,neg.ex,margins=True,margins_name='Total'); T2=neg.pivot_table(index='catl',columns='ex',values='e',aggfunc='sum',margins=True,margins_name='Total').round(2)
T3=pd.crosstab(neg.catl,neg.qC_frac.map({True:'Qté C fractionnaire',False:'Qté C entière'}),margins=True,margins_name='Total')
print(T1.to_string()); print(T2.to_string()); print(T3.to_string())
e=neg[neg.cat.isin(['e','m'])].copy()
e['heureF']=e.id.map(Fid.heure); e['mode']=e.id.map(Fid.mods)
print(e[['cat','ex','date','ticket','lib','qte','qteC','pu','tot','e','heureF','mode']].to_string())
neg.to_pickle(C+'B02_neg.pkl')
T1.to_csv(OUT+'B02_effectifs.csv'); T2.to_csv(OUT+'B02_euros.csv'); T3.to_csv(OUT+'B02_qte.csv')
