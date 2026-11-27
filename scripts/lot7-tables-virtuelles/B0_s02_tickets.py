"""B0 point 2 : tableau 71 (H vs C), tickets sans article, à 0,00 €, rangs partagés, 12/04/2024.
Sortie : out/s02_tickets.txt"""
import pandas as pd, numpy as np
O='scripts/lot7-tables-virtuelles/out/'
C=pd.read_pickle(O+'B0cache/C.pkl'); H=pd.read_pickle(O+'B0cache/H.pkl'); A=pd.read_pickle(O+'B0cache/A.pkl'); F=pd.read_pickle(O+'B0cache/F.pkl')
out=open(O+'B0_s02_tickets.txt','w')
def p(*a): print(*a); print(*a,file=out)
H['dansC']=H.id.isin(A.id)
H['zero']=np.isclose(H.tot_ttc,0)
p('Tickets H par exercice :',H.groupby('ex').size().to_dict(),' total',len(H))
p('H sans article (Id absent de C) :',(~H.dansC).groupby(H.ex).sum().to_dict(),' total',(~H.dansC).sum())
p('H à 0,00 € :',H.zero.groupby(H.ex).sum().to_dict(),' total',H.zero.sum())
p('H sans article ET non nul :',((~H.dansC)&~H.zero).sum(),' ; H à 0 avec article :',(H.dansC&H.zero).sum())
p(H[H.dansC&H.zero][['date_ticket','heure_ticket','no_ticket','id','tot_ttc','ex']].to_string())
p('C Id absents de H :',(~A.id.isin(H.id)).sum())
# séries : totalisateur tot_sum ; la 1re série porte le grand cumul, la 2e un petit cumul
H=H.sort_values('id').reset_index(drop=True)
# Classement en série : 1re série = tickets dont tot_sum est le grand totalisateur (> 100000) 
H['serie']=np.where(H.tot_sum>100000,1,2)
p('Séries (tot_sum > 100 000 = série 1) :',pd.crosstab(H.serie,[H.dansC,H.zero]).to_string())
s2nz=H[(H.serie==2)&~H.zero]
p('Tickets non nuls de la seconde série :',len(s2nz),' par exercice',s2nz.groupby('ex').size().to_dict(),' journées',s2nz.date_ticket.nunique())
p(s2nz[['date_ticket','heure_ticket','no_ticket','id','tot_ttc','tot_sum']].to_string())
# ces 17 = les rangs partagés ?
dup=A[A.duplicated(['date','no'],keep=False)]
p('Additions C dont (date,no) est partagé :',len(dup),' ; parmi elles, série 2 non nulle :',dup.id.isin(s2nz.id).sum())
p('17 tickets série 2 non nuls : rang partagé avec une note de série 1 le même jour :',s2nz.apply(lambda r: ((A.date==r.date_ticket)&(A.no==r.no_ticket)&(A.id!=r.id)).any(),axis=1).sum())
p('Règlements F sur les 17 :',F[F.id.isin(s2nz.id)].groupby('id').montant.sum().to_dict())
# 12/04/2024
d=H[H.date_ticket=='2024-04-12']
p('12/04/2024 rang 4 :'); p(d[d.no_ticket==4][['heure_ticket','no_ticket','id','tot_ttc','tot_sum','serie']].to_string())
x=C[C.id==61095][['lib','qte','pu','tot_lig']]; p('Articles de 61095 :',len(x)); p(x.to_string())
for n in [19,20]:
    y=A[(A.date=='2024-04-12')&(A.no==n)]; p('note',n,y[['heure','id','tot']].to_string(index=False))
    yy=C[C.id.isin(y.id)][['lib','qte','pu','tot_lig']]; p(yy.to_string())
    p('  règlements :',F[F.id.isin(y.id)][['mod_regl','montant']].values.tolist())
p('Règlement de 61095 :',F[F.id==61095][['mod_regl','montant']].values.tolist())
# reprise : chaque article de 61095 figure à 0,5 sur 19 et 20 ?
ids=A[(A.date=='2024-04-12')&(A.no.isin([19,20]))].id.tolist()
c95=C[C.id==61095].groupby('lib').qte.sum(); c1920=C[C.id.isin(ids)].groupby(['id','lib']).qte.sum().unstack(0)
cmp=pd.concat([c95.rename('q61095'),c1920],axis=1); p(cmp.to_string())
H.to_pickle(O+'B0cache/H2.pkl')
out.close()
