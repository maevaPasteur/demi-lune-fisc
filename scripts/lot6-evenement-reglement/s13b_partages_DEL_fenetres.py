"""Sensibilité de s13 à la fenêtre : [−30;+30], [−120;+60], [−240;+120] min ; réel contre placebo jour + 7."""
import pandas as pd, numpy as np, datetime as dt
from collections import defaultdict
CA='scripts/lot6-evenement-reglement/cache/'
E=pd.read_pickle(CA+'E.pkl'); H=pd.read_pickle(CA+'H.pkl'); CC=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/CC.pkl')
c=lambda x:int(round(float(x)*100))
CC['pu_c']=CC.pu.map(c); CC['t']=CC.heure.map(lambda h:int(h[:2])*60+int(h[3:5]))
fr=CC[CC.frac].drop_duplicates(['id','ref','pu_c'])
D=E[E.typEven=='DEL']
base=pd.DataFrame({'d':D.dateEven,'z':D.no_zEport,'t':D.t,'a':D.amount_c})
zday=H.groupby('date_ticket').no_z_report.first().to_dict()
P1=base.copy(); P1['d']=[(dt.date.fromisoformat(x)-dt.timedelta(days=7)).isoformat() for x in P1.d]; P1['z']=P1.d.map(zday); P1=P1.dropna(subset=['z']); P1['z']=P1.z.astype(int)
def build(Dx):
    idx=defaultdict(list)
    for r in Dx.itertuples(): idx[(r.d,r.z)].append((r.t,r.a))
    return idx
I0=build(base); I1=build(P1)
out=open('scripts/lot6-evenement-reglement/out/s13b_partages_DEL_fenetres.txt','w')
for lo,hi in [(-30,30),(-60,15),(-120,60),(-240,120)]:
    res=[]
    for idx in (I0,I1):
        n=sum(any(r.t+lo<=t<=r.t+hi and a==r.pu_c for t,a in idx.get((r.date,r.z),[])) for r in fr.itertuples())
        res.append(n)
    s=f'fenêtre [{lo};{hi}] : réel {res[0]}/{len(fr)} ({res[0]/len(fr)*100:.2f} %) ; placebo J+7 {res[1]} ({res[1]/len(fr)*100:.2f} %) ; excès {res[0]-res[1]}'
    print(s); print(s,file=out)
out.close()
