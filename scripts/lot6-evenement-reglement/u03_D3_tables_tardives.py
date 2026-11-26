"""D-3 : les 113 tables vidées après la dernière note de série 1 de leur Z (11 267,01 €) : part de leurs lignes DEL retrouvées au même prix
(PU ou total de ligne, appariement un à un) sur les notes de série 1 du même jour closes avant le vidage ; placebo : même minute, autre jour
(±1 à ±8 semaines, 200 réplications, graine 20261123) ; ventilation par exercice. Témoin : les autres tables vidées."""
import pandas as pd, numpy as np, datetime as dt
from collections import defaultdict
CA='scripts/lot6-evenement-reglement/cache/'
e=lambda n:f"{n/100:,.2f}".replace(',',' ').replace('.',',')
c=lambda x:int(round(float(x)*100))
out=open('scripts/lot6-evenement-reglement/out/u03_D3_tables_tardives.txt','w')
def p(*a): print(*a); print(*a,file=out)
H=pd.read_pickle(CA+'H.pkl'); E=pd.read_pickle(CA+'E.pkl'); CC=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/CC.pkl'); TB=pd.read_pickle(CA+'tables_videes_B.pkl')
CC['pu_c']=CC.pu.map(c); CC['tot_c']=CC.tot.map(c)
S1=H[(H.serie==1)&(H.tot_ttc_c!=0)]
notes=defaultdict(list)
for r in S1.itertuples(): notes[r.date_ticket].append((r.id,r.t))
lines=defaultdict(list)
for i,pu,tt in zip(CC.id,CC.pu_c,CC.tot_c): lines[i].append((pu,tt))
D=E[(E.typEven=='DEL')&(E.amount_c<100000)&(E.amount_c>0)]
amts={k:sorted(g.amount_c.tolist()) for k,g in D.groupby(['dateEven','no_zEport','t'])}
zday=H.groupby('date_ticket').no_z_report.first().to_dict()
def found(d,t,a):
    L=[l for i,tn in notes.get(d,[]) if tn<t for l in lines[i]]
    used=[False]*len(L); got=0
    for x in a:
        for j,(pu,tt) in enumerate(L):
            if not used[j] and (x==pu or x==tt): used[j]=True; got+=x; break
    return got
TB=TB[TB.V>0].copy()
TB['a']=[amts.get((d,z,t),[]) for d,z,t in zip(TB.d,TB.z,TB.t)]
TB['V2']=TB.a.map(sum)
TB['f']=[found(d,t,a) for d,t,a in zip(TB.d,TB.t,TB.a)]
rng=np.random.default_rng(20261123)
def placebo(sub,reps=200):
    res=[]
    for _ in range(reps):
        sh=rng.choice([-8,-7,-6,-5,-4,-3,-2,-1,1,2,3,4,5,6,7,8],len(sub))*7; s=0
        for (d,t,a),k in zip(zip(sub.d,sub.t,sub.a),sh):
            d2=(dt.date.fromisoformat(d)+dt.timedelta(days=int(k))).isoformat()
            if d2 in zday: s+=found(d2,t,a)
        res.append(s)
    return np.array(res)
for lab,sub in [('113 tables tardives',TB[TB.apres_derniere]),('autres tables (témoin)',TB[~TB.apres_derniere])]:
    pl=placebo(sub, 200 if len(sub)<200 else 30)
    o=sub.f.sum(); M=sub.V2.sum()
    p(f'{lab} : {len(sub)} tables, {e(M)} ; lignes retrouvées sur notes antérieures du jour {e(o)} ({o/M:.2%}) ; placebo {e(pl.mean())} ({pl.mean()/M:.2%}) [{e(np.percentile(pl,2.5))} ; {e(np.percentile(pl,97.5))}] ; excès {e(o-pl.mean())} ({(o-pl.mean())/M:.2%})')
    if lab.startswith('113'):
        for ex,g in sub.groupby('ex'):
            p(f'   {ex} : {len(g)} tables, {e(g.V2.sum())} ; retrouvé {e(g.f.sum())} ({g.f.sum()/g.V2.sum():.2%})')
        p('   tables entièrement retrouvées :',int((sub.f==sub.V2).sum()),' ; aucune ligne retrouvée :',int((sub.f==0).sum()))
out.close()
