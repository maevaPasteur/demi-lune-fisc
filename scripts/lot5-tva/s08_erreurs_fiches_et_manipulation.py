"""s08 : (1) erreurs probables de taux dans les fiches articles (taux caisse reconstitué par décalage, validé par G) ;
(2) répartition des usages : changement de taux d'un article dans le temps, par caissier, par heure ; usage des touches mal taxées
(bière à 10 % vs bière à 20 %) par caissier / heure / mois, avec témoin (touche glace à 20 %) ; graine 20261123."""
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
rng=np.random.default_rng(20261123)
CC=pd.read_pickle(CA+'C_taux2.pkl'); G=loadG()
cais=G.drop_duplicates('tk')[['ex','dateTicket','heureTicket','noTicket','no_zReport','caissier']]
CC=CC.merge(cais,left_on=['ex','date','heure','ticket','z'],right_on=['ex','dateTicket','heureTicket','noTicket','no_zReport'],how='left')
print('lignes C sans caissier (notes hors G) :',CC.caissier.isna().sum())
# (0) un taux par article sur 3 ans ? par article × exercice ? par article × caissier ?
print('refs à taux caisse unique sur 3 ans :',(CC.groupby('ref').rart.nunique()==1).sum(),'/',CC.ref.nunique())
lib_multi=CC.groupby(CC.lib_s.str.upper().str.replace(r'\s+',' ',regex=True)).agg(nref=('ref','nunique'),rates=('rart',lambda s:sorted(s.unique())))
print('libellés (normalisés) portés par plusieurs refs à taux différents :'); print(lib_multi[lib_multi.rates.map(len)>1].to_string())
# (1) erreurs probables (classement par le nom : INFERENCE, non constat)
sus10={'1989':'Pinte','1949':'VOUIVRE','0099':'Panaché','0354':'Monaco'}   # boissons à base de bière à 10 %
sus20={'1816':'1 Boule Glace','2119':'CREPE MARRON CHANTIL'}            # denrées à 20 %
k=20/120-10/110
rows=[]
for ref,lib in {**sus10,**sus20}.items():
    x=CC[CC.ref==ref]
    for ex in EX:
        y=x[x.ex==ex]
        if len(y)==0: continue
        sign=1 if ref in sus10 else -1
        rows.append([ref,lib,int(y.rart.iloc[0]),ex,len(y),round(y.tot.sum(),2),round(sign*y.tot.sum()*k,2),y.date.min(),y.date.max()])
R=pd.DataFrame(rows,columns=['ref','lib','taux_caisse','ex','lignes','TTC','TVA_manquante(+)/excédentaire(-)','1re_date','dern_date'])
print(R.to_string()); print('net par exercice :',R.groupby('ex')['TVA_manquante(+)/excédentaire(-)'].sum().round(2).to_dict(),' total',round(R['TVA_manquante(+)/excédentaire(-)'].sum(),2))
# usage des homologues
for a,b in [('1949','0357'),('1816','1957')]:
    x=CC[CC.ref.isin([a,b])]; print(f'\nhomologues {a}/{b} par exercice (lignes):',x.groupby(['ex','ref']).size().unstack(fill_value=0).to_dict('index'))
    print('  par mois (lignes ref',a,') :',x[x.ref==a].date.str[:7].value_counts().sort_index().to_dict())
    print('  par caissier :',x.groupby(['caissier','ref']).size().unstack(fill_value=0).to_dict('index'))
# (2) test caissier : part des bières vendues sur touches à 10 % (Pinte, VOUIVRE 1949, Panaché, Monaco) vs bières à 20 % (pression, La Vouivre 0357, Blanche, Ambrée, Picon bière, Pinte Picon, Chat perché?)
beer20={'2005':'pression','0357':'La Vouivre','1993':'Blanche des plateaux','2000':'Ambrée','0353':'Picon bière'}
ref20=CC[CC.lib_s.isin(['pression','La Vouivre','Blanche des plateaux','Ambrée','Picon bière','Pinte Picon','Bohème','Pontarlier'])].ref.unique().tolist()
B=CC[CC.ref.isin(list(sus10)+ref20)].copy(); B['bas']=B.ref.isin(list(sus10))
B['h']=B.heure.str[:2].astype(int)
def chi(tab):
    from scipy.stats import chi2_contingency
    t=tab.values; t=t[(t.sum(1)>0)]; return chi2_contingency(t)[:2]
tc=pd.crosstab(B.caissier,B.bas); print('\nbières : lignes touches 10 % (True) / 20 % (False) par caissier'); print(tc.assign(part=lambda d:(d[True]/(d[True]+d[False])).round(3)).to_string())
print('  chi2, p :',chi(tc))
th=pd.crosstab(B.h,B.bas); print('par heure'); print(th.assign(part=lambda d:(d[True]/(d[True]+d[False])).round(3)).to_string()); print('  chi2, p :',chi(th))
tm=pd.crosstab(B.date.str[:7],B.bas); print('par mois : part touches 10 %'); print((tm[True]/(tm[True]+tm[False])).round(3).to_dict())
# corrélation avec le montant du ticket
tk=B.groupby('id').agg(bas=('bas','max'),ttc=('tot_ttc','first'))
print('TTC moyen des notes avec bière touche 10 % :',round(tk[tk.bas].ttc.mean(),2),' sans :',round(tk[~tk.bas].ttc.mean(),2))
# placebo caissier : permutation du caissier entre notes
obs=chi(tc)[0]; pl=[]
ids=B.drop_duplicates('id')[['id','caissier']]
for _ in range(200):
    perm=dict(zip(ids.id,rng.permutation(ids.caissier.values))); pl.append(chi(pd.crosstab(B.id.map(perm),B.bas))[0])
print('placebo caissier (200 permutations, graine 20261123) : chi2 observé',round(obs,1),' ; placebo moyenne',round(np.mean(pl),1),' max',round(max(pl),1),' p empirique',(np.array(pl)>=obs).mean())
