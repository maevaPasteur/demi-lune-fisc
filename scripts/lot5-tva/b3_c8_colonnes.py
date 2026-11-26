"""B3 / C8 : un autre champ de C est-il décalé ? Test colonne par colonne (1 à 17) contre H (niveau note) et contre la cohérence interne de la ligne."""
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
CC=loadC().sort_values(['ex','rowC']).reset_index(drop=True); H=loadH()
h=H.assign(id=H.id.astype(int)).set_index('id')
CC['pos']=CC.groupby(['ex','id']).cumcount()
m=CC.id.map(h.tot_ttc).notna()
for col,hc in [('date','date_ticket'),('heure','heure_ticket'),('ticket','no_ticket'),('z','no_z_report'),('tot_ttc','tot_ttc'),('tot_tva','tot_tva'),('datz','dat_z')]:
    hv=CC.id.map(h[hc]); 
    if col in ('ticket','z'): hv=hv.astype(float); cv=CC[col].astype(float)
    elif col in ('tot_ttc','tot_tva'): hv=hv.map(c); cv=CC[col].map(c)
    else: cv=CC[col].astype(str); hv=hv.astype(str)
    eq=(cv==hv)[m]; first=CC.pos[m]==0
    print(f'col {col:8s} = H (même id) : {int(eq.sum())}/{int(m.sum())} ; 1res lignes de note : {int(eq[first].sum())}/{int(first.sum())}')
# niveau ligne : cohérence pu×qte×(1-disc) = tot (colonne 17) avec la ligne elle-même vs la ligne précédente
pq=(CC.pu*CC.qte).map(c); tot=CC.tot.map(c)
print('pu×qte = Tot_rem_Ttc (±1 ct) :',int(((pq-tot).abs()<=1).sum()),'/',len(CC))
d=CC[CC.disc!=0]; print('lignes avec Discount Rate ≠ 0 :',len(d))
if len(d):
    own=((d.pu*d.qte*(1-d.disc/100)).map(c)-d.tot.map(c)).abs()<=1
    prevdisc=CC.groupby('ex').disc.shift(1)[d.index]; prev=((d.pu*d.qte*(1-prevdisc/100)).map(c)-d.tot.map(c)).abs()<=1
    print('  remise propre explique le TTC :',int(own.sum()),' ; remise de la ligne précédente :',int(prev.sum()))
# ref ↔ lib : un libellé normalisé par réf (pas de décalage entre ref et lib)
g=CC.groupby('ref').lib_s.nunique(); print('réfs à un seul libellé :',int((g==1).sum()),'/',len(g),' (7 à deux libellés, renommages B1 B-3)')
# unite
print('Unite :',CC.unite.value_counts().to_dict())
# taux : t_suiv décalé ; tester le décalage sur la variable « rem » (Tot_rem) au niveau note
print('col tot_rem (remise de note) = H ? (H n a pas de remise) ; comparée à G tot_remGlobale :')
G=loadG(); gr=G.drop_duplicates('tk').set_index(['ex','dateTicket','noTicket','heureTicket']).tot_remGlobale
x=CC.drop_duplicates('id'); key=list(zip(x.ex,x.date,x.ticket,x.heure)); v=[gr.get(k,np.nan) for k in key]
x=x.assign(g=v).dropna(subset=['g']); print('  tot_rem C = tot_remGlobale G :',int((x.tot_rem.map(c)==x.g.map(c)).sum()),'/',len(x))
