"""s11 : décomposition exacte de B − C (tableau 56) : B = TVA (non arrondie) aux taux corrigés du service sur toutes les lignes de C.
B − 445710 = [TVA taux article, tickets G] − Σ tax_amount G (arrondis caisse) + Σ tax_amount G − 445710 + [Δ service − article] + [seconde série]."""
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
CC=pd.read_pickle(CA+'C_taux2.pkl'); G=loadG()
gk=set(zip(G.ex,G.dateTicket,G.heureTicket,G.noTicket,G.no_zReport))
CC['inG']=[k in gk for k in zip(CC.ex,CC.date,CC.heure,CC.ticket,CC.z)]
tv=lambda t,r: t*r/(100+r)
tot=dict(B=0,a=0,b=0,c=0,d=0,e=0)
for i,ex in enumerate(EX):
    x=CC[CC.ex==ex]; m=x[x.inG]; s=x[~x.inG]
    B=tv(x.tot,x.rc).sum(); C445=P26['445710'][i]; Gtax=G[G.ex==ex].tax_amount_c.sum()/100
    a=tv(m.tot,m.rart).sum()-Gtax          # arrondis : ligne à ligne (taux article) − taxe caisse
    b=Gtax-C445                            # caisse − 445710
    cc=(tv(m.tot,m.rc)-tv(m.tot,m.rart)).sum()   # écart des corrections du service au taux réellement appliqué
    d=tv(s.tot,s.rc).sum()                 # seconde série (hors G), aux taux corrigés
    print(f'{ex}: B−445710 = {B-C445:+.2f} = arrondis {a:+.2f} + (caisse−445710) {b:+.2f} + (service−article) {cc:+.2f} + seconde série {d:+.2f} ; contrôle {a+b+cc+d-(B-C445):+.4f}')
    for k,v in zip('Babcd',[B-C445,a,b,cc,d]): tot[k]+=v
print('3 ex :',{k:round(v,2) for k,v in tot.items() if k!='e'})
