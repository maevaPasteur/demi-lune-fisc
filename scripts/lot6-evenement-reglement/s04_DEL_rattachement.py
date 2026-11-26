"""M0-1 : peut-on rattacher chaque DEL (annexe E) à une note (annexes H/C) ? Taux exacts par exercice, avec placebos.
Clés disponibles dans E : dateEven, heureEven (minute), no_zEport, amount, caissier (constant), id (séquence propre).
R0 : (date, Z) existe dans H.
R1 : note(s) du même (date, Z) clôturée(s) à la même minute que le DEL.
R2(W) : note(s) du même (date, Z) clôturée(s) dans [t ; t+W] min portant une ligne C dont le PU ou le total TTC = montant du DEL (au centime).
Unicité : exactement un candidat.
Placebos (graine 20261123) : P1 date + 7 jours (même heure, montant) ; P2 montants permutés dans l'exercice ; P3 heure décalée de +60 à +180 min (tirage uniforme entier)."""
import pandas as pd, numpy as np, datetime as dt
from collections import defaultdict
CA='scripts/lot6-evenement-reglement/cache/'
E=pd.read_pickle(CA+'E.pkl'); H=pd.read_pickle(CA+'H.pkl')
CC=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/CC.pkl')
c=lambda x:int(round(float(x)*100))
CC['pu_c']=CC.pu.map(c); CC['tot_c']=CC.tot.map(c)
out=open('scripts/lot6-evenement-reglement/out/s04_DEL_rattachement.txt','w')
def p(*a):
    print(*a); print(*a,file=out)
DEL=E[E.typEven=='DEL'].copy()
# index des notes par date
notes_by_day=defaultdict(list)
amts=CC.groupby('id').apply(lambda g:set(g.pu_c)|set(g.tot_c)).to_dict()
for r in H.itertuples():
    notes_by_day[r.date_ticket].append((r.id,r.t,r.no_z_report,amts.get(r.id,set()),r.tot_ttc_c))
zday={d:set(z for _,_,z,_,_ in L) for d,L in notes_by_day.items()}
def classify(d,t,z,a,W):
    L=notes_by_day.get(d)
    if L is None: return None
    if z is None:  # placebo jour : Z du jour décalé (le seul Z du jour)
        zs=zday[d]; z=next(iter(zs)) if len(zs)==1 else None
    r1=[i for i,tn,zn,_,_ in L if zn==z and tn==t]
    r2=[i for i,tn,zn,s,_ in L if zn==z and t<=tn<=t+W and a in s]
    return len(r1),len(r2)
def run(df,W,label,zfree=False):
    res=[]
    for r in df.itertuples():
        k=classify(r.d,r.t,None if zfree else r.z,r.a,W)
        if k is None: continue
        res.append((r.ex,)+k)
    R=pd.DataFrame(res,columns=['ex','n1','n2'])
    def cat(n): return np.select([n==0,n==1],['0','1'],'2+')
    R['c1']=cat(R.n1); R['c2']=cat(R.n2)
    R['uniq']=(R.n1==1)|((R.n1==0)&(R.n2==1))
    g=R.groupby('ex')
    tab=pd.DataFrame({'DEL testés':g.size(),
        'R1=0':g.c1.apply(lambda s:(s=='0').sum()),'R1=1':g.c1.apply(lambda s:(s=='1').sum()),'R1≥2':g.c1.apply(lambda s:(s=='2+').sum()),
        f'R2({W})=0':g.c2.apply(lambda s:(s=='0').sum()),f'R2({W})=1':g.c2.apply(lambda s:(s=='1').sum()),f'R2({W})≥2':g.c2.apply(lambda s:(s=='2+').sum()),
        'unique R1 sinon R2':g.uniq.sum()})
    tab.loc['Total']=tab.sum()
    tab['% R1=1']=(tab['R1=1']/tab['DEL testés']*100).round(2)
    tab[f'% R2=1']=(tab[f'R2({W})=1']/tab['DEL testés']*100).round(2)
    tab['% unique']=(tab['unique R1 sinon R2']/tab['DEL testés']*100).round(2)
    p(f'\n== {label} (W={W} min)'); p(tab.to_string())
    return tab
base=pd.DataFrame({'ex':DEL.ex,'d':DEL.dateEven,'t':DEL.t,'z':DEL.no_zEport,'a':DEL.amount_c})
p('DEL',len(base),' ; (date,Z) présent dans H :',sum(z in zday.get(d,()) for d,z in zip(base.d,base.z)))
for W in (30,120):
    run(base,W,'Réel')
rng=np.random.default_rng(20261123)
# P1 : J+7, Z du jour cible
P1=base.copy(); P1['d']=[(dt.date.fromisoformat(d)+dt.timedelta(days=7)).isoformat() for d in P1.d]
P1=P1[P1.d.isin(notes_by_day.keys())]
for W in (30,120): run(P1,W,f'Placebo P1 jour + 7 ({len(P1)} DEL dont le jour cible existe)',zfree=True)
# P2 : montants permutés dans l'exercice
P2=base.copy(); P2['a']=P2.groupby('ex').a.transform(lambda s: rng.permutation(s.values))
for W in (30,120): run(P2,W,'Placebo P2 montants permutés')
# P3 : heure décalée
P3=base.copy(); P3['t']=P3.t+rng.integers(60,181,len(P3))
for W in (30,120): run(P3,W,'Placebo P3 heure + 60 à 180 min')
out.close()
