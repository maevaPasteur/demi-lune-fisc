"""Test placebo du pouvoir discriminant de la recomposition 77 (≤ 15 min, chaînage, ≥ 1 article fractionné commun, seuil 0,02).
(a) chaque note fractionnaire réaffectée à un jour d'ouverture tiré au hasard dans son exercice (heure et lignes conservées) ;
(b) idem, jour tiré dans le même mois ; (c) jours conservés, heures permutées entre les notes fractionnaires du jour.
200 tirages par variante, graine 20261123. Variante de critère : toutes les notes de la table portent le même ensemble d'articles fractionnés.
Sorties : cache/out/B09_tirages_a.csv, B09_tirages_b.csv, B09_tirages_c.csv, B09_synthese.csv."""
import os, sys, time; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
from collections import defaultdict
Cr,F,E,Fid,tabs,nd,A=load()
fr_ids=sorted(Cr[Cr.fracC].id.unique())
X=Cr[Cr.id.isin(fr_ids)]
NOTE={}
for i,g in X.groupby('id'):
    q=defaultdict(float)
    for l,p,v in zip(g.libn,g.pu100,g.qteC): q[(l,p)]+=v
    fs=frozenset(zip(g[g.fracC].libn,g[g.fracC].pu100))
    NOTE[i]=dict(ex=g.ex.iloc[0],date=g.date.iloc[0],t=Fid.t[i],tk=int(g.ticket.iloc[0]),q=dict(q),fs=fs,tot=Fid.tot[i])
days={ex:sorted(set(Cr[Cr.ex==ex].date)) for ex in EX}
def run(assign, same_set=False, W=15, eps=0.02):
    """assign: dict id -> (date, t). Retourne tables, notes rattachées, isolées, articles, refermés, résidu €."""
    byday=defaultdict(list)
    for i,(d,t) in assign.items(): byday[(NOTE[i]['ex'],d)].append((t,NOTE[i]['tk'],i))
    ntab=nnotes=niso=nart=nref=0; comp=0.0
    for key,L in byday.items():
        L.sort()
        cur=[]; arts=set(); lastt=None; ref_set=None
        def close(cur):
            nonlocal ntab,nnotes,niso,nart,nref,comp
            if len(cur)<2: niso+=len(cur); return
            ntab+=1; nnotes+=len(cur)
            keys=set().union(*[NOTE[i]['fs'] for i in cur])
            for a in keys:
                s=round(sum(NOTE[i]['q'].get(a,0.0) for i in cur),6); nart+=1
                if abs(s-round(s))<eps: nref+=1
                else: comp+=(math.ceil(s-1e-9)-s)*a[1]/100
        for t,tk,i in L:
            fs=NOTE[i]['fs']
            ok = bool(cur) and (t-lastt)<=W and ((fs==ref_set) if same_set else bool(fs & arts))
            if ok: cur.append(i); arts|=fs; lastt=t
            else:
                close(cur); cur=[i]; arts=set(fs); lastt=t; ref_set=fs
        close(cur)
    return dict(tables=ntab,notes=nnotes,isolees=niso,articles=nart,refermes=nref,taux=round(nref/nart*100,3) if nart else np.nan,residu=round(comp,2))
real={i:(NOTE[i]['date'],NOTE[i]['t']) for i in fr_ids}
R0=run(real); print('réel',R0)
Rs=run(real,same_set=True); print('variante « même ensemble »',Rs)
rng=np.random.default_rng(20261123)
month={ex:defaultdict(list) for ex in EX}
for ex in EX:
    for d in days[ex]: month[ex][d[:7]].append(d)
res=defaultdict(list); t0=time.time()
for it in range(200):
    a={i:(days[NOTE[i]['ex']][rng.integers(len(days[NOTE[i]['ex']]))],NOTE[i]['t']) for i in fr_ids}; res['a'].append(run(a))
    b={}
    for i in fr_ids:
        m=month[NOTE[i]['ex']][NOTE[i]['date'][:7]]; b[i]=(m[rng.integers(len(m))],NOTE[i]['t'])
    res['b'].append(run(b))
    c={}; byd=defaultdict(list)
    for i in fr_ids: byd[NOTE[i]['date']].append(i)
    for d,ids in byd.items():
        ts=[NOTE[i]['t'] for i in ids]; perm=rng.permutation(len(ts))
        for j,i in enumerate(ids): c[i]=(d,ts[perm[j]])
    res['c'].append(run(c))
print('durée',round(time.time()-t0,1),'s')
lab={'a':'(a) jour au hasard dans l exercice','b':'(b) jour au hasard dans le mois','c':'(c) heures permutées dans le jour'}
out=[]
for v in 'abc':
    D=pd.DataFrame(res[v]); D.to_csv(OUT+f'B09_tirages_{v}.csv',index=False)
    for m in ['tables','notes','isolees','articles','refermes','taux','residu']:
        out.append((lab[v],m,D[m].quantile(0.05),D[m].median(),D[m].quantile(0.95),D[m].min(),D[m].max(),R0[m]))
T=pd.DataFrame(out,columns=['variante','indicateur','q05','médiane','q95','min','max','réel'])
pd.set_option('display.width',250); print(T.to_string(index=False)); T.to_csv(OUT+'B09_synthese.csv',index=False)
# parité des demi-parts
A2=A.copy()
def allhalf(r):
    vals=[NOTE[i]['q'].get((norm(r.lib),round(r.pu*100)),0) for i in r.ids]
    fr=[v for v in vals if abs(v-round(v))>1e-9]
    return all(abs(v-math.floor(v)-0.5)<1e-9 for v in fr)
A2['half']=A2.apply(allhalf,axis=1)
print('articles 77 dont toutes les fractions sont des demi-parts (x,5) :',A2.half.sum(),'/',len(A2),round(A2.half.mean()*100,2),'% ; refermés parmi eux',A2[A2.half].ref.sum(),' ; parmi les autres',A2[~A2.half].ref.sum(),'/',(~A2.half).sum())
