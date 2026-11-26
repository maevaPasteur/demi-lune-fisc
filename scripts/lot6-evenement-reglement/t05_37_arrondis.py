"""B-11 complément : les différences Σ DEL − Σ règlements des 37 notes sont-elles anormalement « rondes » ? Témoins : totaux de notes de série 1 ;
différences V − note pour des couples (table vidée, note de série 1 du même Z) tirés au hasard (graine 20261123)."""
import pandas as pd, numpy as np
CA='scripts/lot6-evenement-reglement/cache/'
H=pd.read_pickle(CA+'H.pkl'); F=pd.read_pickle(CA+'F.pkl'); E=pd.read_pickle(CA+'E.pkl'); TB=pd.read_pickle(CA+'tables_videes_B.pkl')
out=open('scripts/lot6-evenement-reglement/out/t05_37_arrondis.txt','w')
def p(*a): print(*a); print(*a,file=out)
DEL=E[(E.typEven=='DEL')&(E.amount_c<100000)]; dm=DEL.groupby(['dateEven','no_zEport','t']).amount_c.sum()
z=F[F.tot_ttc_c==0]; Hi=H.set_index('id')
d=[]
for i,g in z.groupby('id'):
    h=Hi.loc[i]; V=dm.get((h.date_ticket,h.no_z_report,h.t),0); d.append(V-g.montant_c.sum())
d=np.array(d)
def r(x): return {'×10 €':float(np.mean(x%1000==0)),'×5 €':float(np.mean(x%500==0)),'entier €':float(np.mean(x%100==0))}
p('37 différences (Σ DEL − Σ règl.) : n',len(d),' parts',{k:round(v*100,1) for k,v in r(d).items()},' ; nombres',{'×10':int((d%1000==0).sum()),'×5':int((d%500==0).sum()),'entier':int((d%100==0).sum())})
s1=H[(H.serie==1)&(H.tot_ttc_c!=0)].tot_ttc_c.values
p('témoin 1, totaux de notes série 1 (16 605) :',{k:round(v*100,1) for k,v in r(s1).items()})
p('témoin 2, valeurs V des 2 361 tables vidées :',{k:round(v*100,1) for k,v in r(TB.V.values).items()})
rng=np.random.default_rng(20261123)
byz=H[(H.serie==1)&(H.tot_ttc_c!=0)].groupby(['date_ticket','no_z_report']).tot_ttc_c.apply(list).to_dict()
sim=[]
for _ in range(20):
    for dd,zz,v in zip(TB.d,TB.z,TB.V):
        L=byz.get((dd,zz))
        if L: x=v-L[rng.integers(len(L))]; 
        if L and x>0: sim.append(x)
sim=np.array(sim); p('témoin 3, V − une note du même Z tirée au hasard (différences positives, 20 tirages) : n',len(sim),{k:round(v*100,1) for k,v in r(sim).items()})
from math import comb
pr=r(s1)['×10 €']; k=int((d%1000==0).sum()); n=len(d)
pv=sum(comb(n,j)*pr**j*(1-pr)**(n-j) for j in range(k,n+1)); p(f'probabilité binomiale d\'au moins {k} multiples de 10 € sur {n} au taux du témoin 1 ({pr*100:.1f} %) : {pv:.2e}')
out.close()
out=open('scripts/lot6-evenement-reglement/out/t05_37_arrondis.txt','a')
ex=[Hi.loc[i].ex for i,_ in z.groupby('id')]
D=pd.DataFrame({'ex':ex,'d':d})
D['rond10']=D.d%1000==0
p('Σ différences par exercice (€) :',(D.groupby('ex').d.sum()/100).round(2).to_dict(),' ; dont multiples de 10 € :',(D[D.rond10].groupby('ex').d.sum()/100).round(2).to_dict(),
  ' ; à comparer à compta − F en CHV : 825,99 / 7 023,10 / 2 895,34 et au total compta − (F − etat 9) : 158,06 / 5 423,51 / 79,98')
out.close()
