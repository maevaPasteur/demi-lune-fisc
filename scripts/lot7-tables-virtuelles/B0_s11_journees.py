"""B0 points 6 et 7 : journée du 9 septembre 2022 (Z 3052) et journée du 14 avril 2022.
Sortie : out/s11_journees.txt"""
import pandas as pd, numpy as np
O='scripts/lot7-tables-virtuelles/out/'
C=pd.read_pickle(O+'B0cache/C.pkl'); A=pd.read_pickle(O+'B0cache/A.pkl'); H=pd.read_pickle(O+'B0cache/H2.pkl'); E=pd.read_pickle(O+'B0cache/E.pkl'); F=pd.read_pickle(O+'B0cache/F.pkl')
out=open(O+'B0_s11_journees.txt','w')
def p(*a): print(*a); print(*a,file=out)
def tm(h): return int(h[:2])*60+int(h[3:])
d='2022-09-09'
e=E[E.dateEven==d]; D=e[e.typEven=='DEL']
p('09/09/2022 : événements',len(e),' types',e.typEven.value_counts().to_dict(),' Z',e.no_zEport.unique().tolist(),' ids',e.id.min(),'-',e.id.max())
p('  DEL',len(D),' montant',round(D.amount.sum(),2),' minutes distinctes',D.heureEven.nunique())
R=D.groupby('heureEven').amount.agg(['size','sum']).round(2); p(R.to_string())
p('  ids DEL 11:09 à 12:36 :',D[(D.heureEven>='11:09')&(D.heureEven<='12:36')].id.agg(['min','max']).tolist(),' CON :',e[e.typEven=='CON'][['heureEven','id']].values.tolist())
h=H[H.date_ticket==d].copy(); h['t']=h.heure_ticket.map(tm)
p('  H : tickets',len(h),' encaissés (≠0)',int((h.tot_ttc!=0).sum()),' à 0',int((h.tot_ttc==0).sum()),' n° encaissés',sorted(h[h.tot_ttc!=0].no_ticket.tolist())==list(range(1,26)),' somme',h[h.tot_ttc!=0].no_ticket.sum())
z=h[h.tot_ttc==0].sort_values('t')
mins=set(D.heureEven.map(tm))
z['exact']=z.t.isin(mins); z['m1']=z.t.apply(lambda t: (t-1 in mins) or (t+1 in mins))
p(z[['heure_ticket','no_ticket','id','exact','m1']].to_string())
p('  à 0 € : minute exacte',int(z.exact.sum()),' ; à une minute près seulement',int((~z.exact&z.m1).sum()),' ; sans DEL à +/-1 min',int((~z.exact&~z.m1).sum()))
p('  dernière note encaissée :',h[h.tot_ttc!=0].sort_values('t').tail(1)[['heure_ticket','no_ticket','tot_ttc']].values.tolist())
a=A[A.date==d]
for n in [1,2,3,8]:
    x=a[a.no==n]; i=x.id.iloc[0]
    p(f'  note {n} : {x.heure.iloc[0]} total {x.tot.iloc[0]} id {i} ; articles',C[C.id==i][['lib','qte','pu']].values.tolist(),' ; règlements',F[F.id==i][['mod_regl','montant']].values.tolist())
# rafales vs totaux de notes
tots=a.set_index('no').tot
for hh,r in R.iterrows():
    eq=tots[np.isclose(tots,r['sum'])]
    if len(eq): p('  rafale',hh,r['sum'],'= note(s)',eq.index.tolist())
# notes à 18 numéros d'écran
p('  notes encaissées',len(a),' ; n° max',a.no.max())
# 14/04/2022
d='2022-04-14'; a=A[A.date==d].sort_values('no')
p('\n14/04/2022 : additions',len(a),' n° 1..',a.no.max(),' somme',a.no.sum())
for n in [13,14]:
    x=a[a.no==n]; i=x.id.iloc[0]
    p(f'  note {n} : {x.heure.iloc[0]} total {x.tot.iloc[0]} articles',C[C.id==i][['lib','qte','pu']].values.tolist())
e=E[(E.dateEven==d)]; e2=e[(e.typEven=='DEL')]
p('  DEL du jour :',e2[['heureEven','amount']].values.tolist())
p('  DEL entre 12:26 et 13:34 (bornes incluses) :',len(e2[(e2.heureEven>='12:26')&(e2.heureEven<='13:34')]),' ; strictement entre :',len(e2[(e2.heureEven>'12:26')&(e2.heureEven<'13:34')]))
h=H[(H.date_ticket==d)&(H.tot_ttc==0)]; p('  tickets à 0 € du jour :',h[['heure_ticket','no_ticket']].values.tolist())
# 9 juillet 2022
a=A[A.date=='2022-07-09']; p('\n09/07/2022 : ',a[a.no.isin([1,20,35,57])][['no','heure']].values.tolist())
out.close()
