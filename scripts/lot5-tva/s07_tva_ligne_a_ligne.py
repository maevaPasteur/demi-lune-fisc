"""s07 : TVA de la note (tot_tva, = Σ tax_amount G) contre TVA ligne à ligne de C selon le taux du fichier / corrigé / article.
Contrôle du constat du lot 2.3 (caisse ≈ −0,72 % sous le ligne à ligne). Notes de C absentes de G (seconde série)."""
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
CC=pd.read_pickle(CA+'C_taux2.pkl'); G=loadG()
gk=G.drop_duplicates('tk')[['ex','dateTicket','heureTicket','noTicket','no_zReport','tot_ttc_c','tot_tva_c']]
for col in ['rf','rc','rart']:
    CC['l_'+col]=[round(t*r/(100+r)+1e-9,2) for t,r in zip(CC.tot,CC[col])]
n=CC.groupby(['ex','id','date','heure','ticket','z']).agg(ttc=('tot_ttc','first'),tva=('tot_tva','first'),lf=('l_rf','sum'),lc=('l_rc','sum'),la=('l_rart','sum'),nl=('tot','size')).reset_index()
m=n.merge(gk,left_on=['ex','date','heure','ticket','z'],right_on=['ex','dateTicket','heureTicket','noTicket','no_zReport'],how='left',indicator=True)
print('notes C',len(n),' appariées à G',(m._merge=='both').sum(),' absentes de G',(m._merge=='left_only').sum())
o=m[m._merge=='left_only']; print('  notes C absentes de G par exercice', o.groupby('ex').agg(n=('id','size'),ttc=('ttc','sum'),tva=('tva','sum')).round(2).to_dict('index'))
print('  dont TTC nul :',(o.ttc==0).sum())
b=m[m._merge=='both']
for ex in EX+['3ex']:
    x=b if ex=='3ex' else b[b.ex==ex]
    T=x.tva.sum()
    print(f'{ex}: Σ tot_tva {T:,.2f} ; ligne à ligne taux fichier {x.lf.sum():,.2f} (écart {T-x.lf.sum():+,.2f} = {100*(T-x.lf.sum())/x.lf.sum():+.3f} %) ; corrigé {x.lc.sum():,.2f} ({T-x.lc.sum():+,.2f}) ; article {x.la.sum():,.2f} ({T-x.la.sum():+,.2f}) ; notes où tot_tva = ligne à ligne article ±0,02 : {((x.tva-x.la).abs()<=0.02+1e-9).sum()}/{len(x)} ; max |écart| {(x.tva-x.la).abs().max():.2f}')
