"""B0 point 3 : rapprochement des 2 449 tickets sans article « à la minute d'un DEL » avec les 2 359 tables vidées du lot 2.2 (cache lot26, b5_tables_videes.pkl).
Sortie : out/s14_tv_2359.txt"""
import pandas as pd
O='scripts/lot7-tables-virtuelles/out/'
tv=pd.read_pickle('scripts/lot6-evenement-reglement/cache/b5_tables_videes.pkl'); Z=pd.read_csv(O+'B0_s03_zero.csv')
out=open(O+'B0_s14_tv_2359.txt','w')
def p(*a): print(*a); print(*a,file=out)
k_tv=set(zip(tv.d.astype(str),tv.t.astype(str)))
Z['k']=list(zip(Z.date_ticket.astype(str),Z.heure_ticket.astype(str)))
m=Z[Z.m0]
p('Tables vidées lot 2.2 :',len(tv),' montant',round(tv.V.sum()/100,2),' € ; minutes (date, heure) distinctes',len(k_tv))
p('Tickets sans article à la minute d un DEL :',len(m),' ; minutes distinctes',m.k.nunique(),' ; dont minute présente parmi les 2 359 :',int(m.k.isin(k_tv).sum()))
p('Minutes des 2 359 sans ticket sans article à la même minute :',len(k_tv-set(Z.k)))
p('Plusieurs tickets sans article à la même minute DEL :',int((m.k.value_counts()>1).sum()),' minutes ; tickets en excédent',int((m.k.value_counts()-1).clip(lower=0).sum()))
out.close()
