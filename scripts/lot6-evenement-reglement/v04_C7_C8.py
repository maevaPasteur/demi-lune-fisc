"""C7 (113 tables tardives : délais, listes, bootstrap de la différence d'excès) et C8 (DEL hors tables vidées). Graine 20261123.
Placebo par table : moyenne sur R réplications (±1 à ±8 semaines) ; R = 50 (tardives), 10 (autres)."""
import pandas as pd, numpy as np, datetime as dt
from collections import defaultdict
CA='scripts/lot6-evenement-reglement/cache/'
e=lambda n:f"{n/100:,.2f}".replace(',',' ').replace('.',',')
c=lambda x:int(round(float(x)*100))
out=open('scripts/lot6-evenement-reglement/out/v04_C7_C8.txt','w')
def p(*a): print(*a); print(*a,file=out)
H=pd.read_pickle(CA+'H.pkl'); E=pd.read_pickle(CA+'E.pkl'); TB=pd.read_pickle(CA+'tables_videes_B.pkl'); CC=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/CC.pkl')
CC['pu_c']=CC.pu.map(c); CC['tc']=CC.tot.map(c)
S1=H[(H.serie==1)&(H.tot_ttc_c!=0)]
notes=defaultdict(list)
for r in S1.itertuples(): notes[r.date_ticket].append((r.id,r.t))
lines=defaultdict(list)
for i,pu,tt in zip(CC.id,CC.pu_c,CC.tc): lines[i].append((pu,tt))
D=E[(E.typEven=='DEL')&(E.amount_c<100000)&(E.amount_c>0)]
amts={k:sorted(g.amount_c.tolist()) for k,g in D.groupby(['dateEven','no_zEport','t'])}
zday=H.groupby('date_ticket').no_z_report.first().to_dict()
def found(d,t,a,before=True):
    L=[l for i,tn in notes.get(d,[]) if (tn<t if before else True) for l in lines[i]]
    used=[False]*len(L); got=0
    for x in a:
        for j,(pu,tt) in enumerate(L):
            if not used[j] and (x==pu or x==tt): used[j]=True; got+=x; break
    return got
TB=TB[TB.V>0].copy(); TB['a']=[amts.get((d,z,t),[]) for d,z,t in zip(TB.d,TB.z,TB.t)]; TB['V2']=TB.a.map(sum)
TB['f']=[found(d,t,a) for d,t,a in zip(TB.d,TB.t,TB.a)]
last={k:max(tn for _,tn in L) for k,L in notes.items()}
lastid={k:max(L,key=lambda x:x[1]) for k,L in notes.items()}
rng=np.random.default_rng(20261123)
def plmean(r,R):
    s=0;n=0
    for _ in range(R):
        d2=(dt.date.fromisoformat(r.d)+dt.timedelta(days=int(rng.choice([-8,-7,-6,-5,-4,-3,-2,-1,1,2,3,4,5,6,7,8])*7))).isoformat()
        if d2 in zday: s+=found(d2,r.t,r.a)
        n+=1
    return s/n
late=TB[TB.apres_derniere].copy(); oth=TB[~TB.apres_derniere].copy()
late['pl']=[plmean(r,50) for r in late.itertuples()]; oth['pl']=[plmean(r,10) for r in oth.itertuples()]
late['delai']=[t-last[d] for d,t in zip(late.d,late.t)]
p('== C7 (1) délai dernière note de série 1 → vidage (min) :',pd.cut(late.delai,[0,5,15,60,10**4]).value_counts(sort=False).to_dict())
full=late[late.f==late.V2]
p('(2) tables entièrement retrouvées :',len(full))
for r in full.itertuples():
    p(f'   {r.d} {r.t//60:02d}:{r.t%60:02d} {e(r.V2)} ; délai {r.delai} min ; dernière note {lastid[r.d][0]}')
none=late[late.f==0]; p('(3) aucune ligne retrouvée :',[(r.d,f'{r.t//60:02d}:{r.t%60:02d}',e(r.V2),r.delai) for r in none.itertuples()])
def exc(df): return (df.f.sum()-df.pl.sum())/df.V2.sum()
diffs=[]
for _ in range(1000):
    a=late.sample(len(late),replace=True,random_state=int(rng.integers(1e9))); b=oth.sample(len(oth),replace=True,random_state=int(rng.integers(1e9)))
    diffs.append(exc(a)-exc(b))
p(f'(4) excès tardives {exc(late)*100:.2f} pts ; autres {exc(oth)*100:.2f} pts ; différence {(exc(late)-exc(oth))*100:.2f} pts ; bootstrap IC 95 % [{np.percentile(diffs,2.5)*100:.2f} ; {np.percentile(diffs,97.5)*100:.2f}]')
# ---- C8
p('\n== C8')
DEL=E[E.typEven=='DEL']
zk=set(zip(TB.d,TB.z,TB.t))
X=DEL[[ (d,z,t) not in zk for d,z,t in zip(DEL.dateEven,DEL.no_zEport,DEL.t)]].copy()
close=defaultdict(list)
for r in H.itertuples(): close[(r.date_ticket,r.no_z_report)].append(r.t)
X['delai']=[min([u-t for u in close[(d,z)] if u>=t],default=np.nan) for d,z,t in zip(X.dateEven,X.no_zEport,X.t)]
p(f'(1) DEL hors tables vidées : {len(X)} ; délai jusqu\'à la prochaine clôture (toute série) :',pd.cut(X.delai,[-1,0,5,15,60,10**4]).value_counts(sort=False).to_dict(),' ; sans clôture ultérieure',int(X.delai.isna().sum()))
pu_by=defaultdict(list)
for i,tn in [(i,tn) for d,L in notes.items() for i,tn in L]: pass
def svc_end(t): return 18*60 if t<18*60 else 24*60
def follow(d,t,a):
    return any(t<=tn<svc_end(t) and any(a==pu for pu,_ in lines[i]) for i,tn in notes.get(d,[]))
Xp=X[(X.amount_c>0)&(X.amount_c<100000)]
real=np.mean([follow(d,t,a) for d,t,a in zip(Xp.dateEven,Xp.t,Xp.amount_c)])
pl=[]
for rep in range(30):
    sh=rng.choice([-8,-7,-6,-5,-4,-3,-2,-1,1,2,3,4,5,6,7,8],len(Xp))*7
    pl.append(np.mean([follow((dt.date.fromisoformat(d)+dt.timedelta(days=int(s))).isoformat(),t,a) for d,t,a,s in zip(Xp.dateEven,Xp.t,Xp.amount_c,sh)]))
p(f'(2) DEL (> 0, < 1 000 €) suivis dans le service d\'une note de série 1 portant un article au même prix : {real*100:.1f} % ; placebo (30 réplications) {np.mean(pl)*100:.1f} % [{np.percentile(pl,2.5)*100:.1f} ; {np.percentile(pl,97.5)*100:.1f}]')
nk=set(zip(H.date_ticket,H.no_z_report,H.t))
orph=X[[not any((d,z,t+x) in nk for x in range(-5,6)) for d,z,t in zip(X.dateEven,X.no_zEport,X.t)]]
dl=defaultdict(list)
for r in DEL.itertuples(): dl[(r.dateEven,r.no_zEport)].append((r.t,r.id))
burst=[any(abs(u-t)<=10 and j!=i for u,j in dl[(d,z)]) for d,z,t,i in zip(orph.dateEven,orph.no_zEport,orph.t,orph.id)]
first={}
for r in S1.itertuples():
    k=(r.date_ticket,'midi' if r.t<18*60 else 'soir'); first[k]=min(first.get(k,10**4),r.t)
early=[t-first.get((d,'midi' if t<18*60 else 'soir'),10**4)<=60 for d,t in zip(orph.dateEven,orph.t)]
o=orph.assign(b=burst,ea=early)
p(f'(3) orphelins {len(o)} ({e(o.amount_c.sum())}) : à ±10 min d\'un autre DEL du même Z {int(o.b.sum())} ({e(o[o.b].amount_c.sum())}) ; dans les 60 min après la première note du service (ou avant) {int(o.ea.sum())} ({e(o[o.ea].amount_c.sum())})')
bins=[-10**6,0,500,1000,2000,5000,10000,100000,10**9]; lab=['≤0','0-5','5-10','10-20','20-50','50-100','100-1000','≥1000']
p('(4) répartition par montant (%) : DEL hors tables',(pd.cut(X.amount_c,bins,labels=lab).value_counts(normalize=True,sort=False)*100).round(1).to_dict())
p('                                lignes de C',(pd.cut(CC.tc,bins,labels=lab).value_counts(normalize=True,sort=False)*100).round(1).to_dict())
out.close()
