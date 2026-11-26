"""s05 : validation du décalage par le journal G (fichier distinct) et témoin/placebo de l'univocité.
Paliers TTC par ticket : G (VAT_base + taux) vs Σ Tot_rem_Ttc des lignes C selon (a) Taux_tva du fichier, (b) taux corrigés service, (c) taux article (décalage)."""
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
rng=np.random.default_rng(20261123)
CC=pd.read_pickle(CA+'C_taux.pkl'); Gp=pd.read_pickle(CA+'G_paliers.pkl'); G=loadG()
# univocité : témoin (même ligne), décalage +1, décalage +2, placebo permutation
def univ(col):
    d=CC.dropna(subset=[col]); vc=d.groupby('ref')[col].nunique(); n=d.groupby('ref').size()
    return int((vc==1).sum()), int(len(vc)), int(((vc==1)&(n>=2)).sum()), int((n>=2).sum())
CC['rf_n1']=CC.groupby('ex').rf.shift(-1); CC['rf_n2']=CC.groupby('ex').rf.shift(-2); CC['rf_p1']=CC.groupby('ex').rf.shift(1)
for col,lab in [('rf','même ligne (témoin)'),('rf_n1','ligne suivante'),('rf_n2','ligne +2'),('rf_p1','ligne précédente')]:
    u=univ(col); print(f'refs à taux univoque, {lab}: {u[0]}/{u[1]} ; parmi refs vues ≥2 fois : {u[2]}/{u[3]}')
pl=[]
for _ in range(100):
    CC['pp']=CC.groupby('ex').rf.transform(lambda s: rng.permutation(s.values)); pl.append(univ('pp')[2])
print('placebo permutation (100 tirages, graine 20261123) refs ≥2 fois univoques : moyenne',np.mean(pl),' max',max(pl))
# ventilation par ticket
G['r']=G['taux_tva%'].astype(int); G['pal']=G.VAT_base_c+G.r*100
gp=G.pivot_table(index=['ex','dateTicket','heureTicket','noTicket','no_zReport'],columns='r',values='pal',aggfunc='sum',fill_value=0)
gp.columns=['G10','G20']; gp=gp.reset_index()
CC['tc']=CC.tot.map(c)
out=[]
for col,lab in [('rf','fichier'),('rc','corrigé service'),('rart','article (décalage)')]:
    x=CC.assign(p20=np.where(CC[col]==20,CC.tc,0)).groupby(['ex','date','heure','ticket','z']).agg(C20=('p20','sum'),CT=('tc','sum')).reset_index()
    m=x.merge(gp,left_on=['ex','date','heure','ticket','z'],right_on=['ex','dateTicket','heureTicket','noTicket','no_zReport'],how='inner')
    for ex in EX+['3ex']:
        mm=m if ex=='3ex' else m[m.ex==ex]
        tot_ok=(mm.CT==mm.G10+mm.G20)
        ok=(mm.C20==mm.G20)
        print(f'{lab:22s} {ex}: tickets appariés {len(mm)} ; TTC C == TTC G : {tot_ok.sum()} ; palier 20 % identique au centime : {ok.sum()} ({100*ok.mean():.2f} %) ; parmi TTC égaux : {(ok&tot_ok).sum()}/{tot_ok.sum()} ({100*(ok&tot_ok).sum()/tot_ok.sum():.2f} %) ; Σ|écart 20 %| {e(int((mm.C20-mm.G20).abs().sum()))}')
    if col=='rart': mres=m
nm=mres[(mres.CT==mres.G10+mres.G20)&(mres.C20!=mres.G20)]
print('tickets à TTC égal où le taux article ne retrouve pas G :',len(nm)); print(nm.head(10).to_string())
CC.to_pickle(CA+'C_taux2.pkl'); mres.to_pickle(CA+'C_vs_G_tickets.pkl')
