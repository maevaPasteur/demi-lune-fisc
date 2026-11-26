"""Détail du rattachement R1 (même date, même Z, même minute de clôture) : nature de la note rattachée, montants ;
contrôle du chiffre des sections 2.2/2.7 : « 2 449 des 3 279 tickets sans article clôturés à la minute d'un DEL du même Z »."""
import pandas as pd, numpy as np
from collections import defaultdict
CA='scripts/lot6-evenement-reglement/cache/'
E=pd.read_pickle(CA+'E.pkl'); H=pd.read_pickle(CA+'H.pkl'); CC=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/CC.pkl')
out=open('scripts/lot6-evenement-reglement/out/s05_DEL_R1_detail.txt','w')
def p(*a):
    print(*a); print(*a,file=out)
DEL=E[E.typEven=='DEL']
withlines=set(CC.id)
H['type']=np.where(H.tot_ttc_c!=0,'note payée (≠0)',np.where(H.id.isin(withlines),'0 € avec lignes','0 € sans ligne'))
key=defaultdict(list)
for r in H.itertuples(): key[(r.date_ticket,r.no_z_report,r.t)].append((r.id,r.type))
rows=[]
for r in DEL.itertuples():
    L=key.get((r.dateEven,r.no_zEport,r.t),[])
    rows.append((r.ex,len(L),L[0][1] if len(L)==1 else ('aucune' if not L else 'plusieurs'),r.amount_c))
R=pd.DataFrame(rows,columns=['ex','n','type','a'])
t=pd.concat({'n':R.groupby(['type','ex']).size().unstack(fill_value=0),'cts':R.groupby(['type','ex']).a.sum().unstack(fill_value=0)},axis=1); t.loc['Total']=t.sum()
p('DEL selon la note clôturée à la même minute (même date, même Z) ; montants en centimes'); p(t.to_string())
# tickets sans article
z=H[H.type=='0 € sans ligne']; dk=set(zip(DEL.dateEven,DEL.no_zEport,DEL.t))
hit=[(d,zz,t) in dk for d,zz,t in zip(z.date_ticket,z.no_z_report,z.t)]
p('\ntickets à 0 € sans ligne :',len(z),' dont clôturés à la minute d\'un DEL du même (date,Z) :',sum(hit),' par exercice',z.assign(h=hit).groupby('ex').h.agg(['size','sum']).to_dict())
p('tickets à 0 € avec lignes :',int((H.type=='0 € avec lignes').sum()),' ; tickets à 0 € au total :',int((H.tot_ttc_c==0).sum()))
# placebo : même test sur les notes payées
pz=H[H.type=='note payée (≠0)']; hp=[(d,zz,t) in dk for d,zz,t in zip(pz.date_ticket,pz.no_z_report,pz.t)]
p('témoin : notes payées clôturées à la minute d\'un DEL du même Z :',sum(hp),'/',len(pz),f'({sum(hp)/len(pz)*100:.2f} %) contre',f'{sum(hit)/len(z)*100:.2f} % pour les tickets sans ligne')
# placebo heure décalée pour les tickets sans ligne
rng=np.random.default_rng(20261123); sh=rng.integers(60,181,len(z))
hit2=[(d,zz,t+s) in dk for d,zz,t,s in zip(z.date_ticket,z.no_z_report,z.t,sh)]
p('placebo tickets sans ligne, heure + 60 à 180 min :',sum(hit2),'/',len(z))
out.close()
