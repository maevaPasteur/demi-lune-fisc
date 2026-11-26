"""2.6.5 d, dernière puce, et p. 42 du service (« ne s'y retrouvaient que pour une infime partie ») :
pour chaque article partagé (ligne C à quantité fractionnaire ; unité = (note, réf, PU)), existe-t-il un DEL du même (date, Z)
dont le montant = PU (ou PU × quantité entière 2 à 4), dans [clôture − 60 ; clôture + 15] min ?
Placebos (graine 20261123) : DEL du jour + 7 (Z du jour cible) ; montants DEL permutés dans l'exercice."""
import pandas as pd, numpy as np, datetime as dt
from collections import defaultdict
CA='scripts/lot6-evenement-reglement/cache/'
E=pd.read_pickle(CA+'E.pkl'); H=pd.read_pickle(CA+'H.pkl'); CC=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/CC.pkl')
c=lambda x:int(round(float(x)*100))
out=open('scripts/lot6-evenement-reglement/out/s13_partages_DEL.txt','w')
def p(*a): print(*a); print(*a,file=out)
CC['pu_c']=CC.pu.map(c); CC['t']=CC.heure.map(lambda h:int(h[:2])*60+int(h[3:5]))
fr=CC[CC.frac].drop_duplicates(['id','ref','pu_c'])
p('articles partagés (note, réf, PU) :',len(fr),' notes',fr.id.nunique(),' par exercice',fr.groupby('ex').size().to_dict())
D=E[E.typEven=='DEL'].copy()
def build(Dx):
    idx=defaultdict(list)
    for r in Dx.itertuples(): idx[(r.d,r.z)].append((r.t,r.a))
    return idx
base=pd.DataFrame({'d':D.dateEven,'z':D.no_zEport,'t':D.t,'a':D.amount_c,'ex':D.ex})
zday=H.groupby('date_ticket').no_z_report.first().to_dict()
def rate(idx,lab):
    hit=[]
    for r in fr.itertuples():
        L=idx.get((r.date,r.z),[])
        ok=any(r.t-60<=t<=r.t+15 and (a==r.pu_c or (a%r.pu_c==0 and 2<=a//r.pu_c<=4)) for t,a in L) if r.pu_c>0 else False
        ok1=any(r.t-60<=t<=r.t+15 and a==r.pu_c for t,a in L)
        hit.append((r.ex,ok,ok1))
    R=pd.DataFrame(hit,columns=['ex','ok','ok_pu'])
    g=R.groupby('ex').agg(n=('ok','size'),PU_ou_multiple=('ok','sum'),PU_exact=('ok_pu','sum'))
    g.loc['Total']=g.sum(); g['% PU ou multiple']=(g.PU_ou_multiple/g.n*100).round(2); g['% PU exact']=(g.PU_exact/g.n*100).round(2)
    p(f'\n== {lab}'); p(g.to_string())
rate(build(base),'Réel')
P1=base.copy(); P1['d']=[(dt.date.fromisoformat(x)-dt.timedelta(days=7)).isoformat() for x in P1.d]  # DEL du jour J servent de placebo au jour J-7 (= DEL de J+7 pour chaque note)
P1['z']=P1.d.map(zday); P1=P1.dropna(subset=['z']); P1['z']=P1.z.astype(int)
rate(build(P1),'Placebo : DEL du jour + 7 (même heure)')
rng=np.random.default_rng(20261123)
P2=base.copy(); P2['a']=P2.groupby('ex').a.transform(lambda s: rng.permutation(s.values))
rate(build(P2),'Placebo : montants DEL permutés dans l\'exercice')
# exemple R1 du 16/04/2022 et 14/05/2022
for d in ['2022-04-16','2022-05-14']:
    p('\nDEL du',d,':',D[D.dateEven==d][['heureEven','amount']].values.tolist()[:40])
out.close()
