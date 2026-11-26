"""B-17 complément : lignes de menus/formules à prix hors catalogue (règle « prix personnalisé » du référentiel client :
un tel menu « peut contenir n'importe quel plat/boisson de la carte »), toutes au taux de 10 %. Borne de TVA en jeu."""
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
CC=pd.read_pickle(CA+'C_taux2.pkl')
CAT={"Menu 'Demi Lune'":[45.0],'Menu du Dahu':[29.9],'Menu Végétarien':[23.0,25.0,26.5],'Menu Bourguignon':[32.0,34.0],'Menu Franc-Comtois':[32.0,34.0],
     'Formule Express':[15.0,16.5,18.6],'FORMULE EXPRESS':[15.0,16.5,18.6],"Menu 'Galette'":[15.9,17.0,19.5],"Menu 'Enfant'":[9.9],'Menu Bambin':[6.9],
     'Formule à 12.5':[11.0,12.5],'Formule à 11':[11.0,12.5],'Menu du jour':[]}
m=CC[CC.lib_s.isin(CAT)].copy()
m['hors']=[not any(abs(p-x)<0.005 for x in CAT[l]) for l,p in zip(m.lib_s,m.pu)]
m['hors_nonnul']=m.hors&(m.pu>0)
k=20/120-10/110
print('libellés de menus trouvés :',sorted(m.lib_s.unique()))
print('taux appliqués aux menus :',m.rart.value_counts().to_dict())
t=m.groupby('ex').apply(lambda g: pd.Series(dict(lignes=len(g),hors=int(g.hors_nonnul.sum()),TTC_hors=round(g[g.hors_nonnul].tot.sum(),2),TTC_total=round(g.tot.sum(),2))))
t['borne_TVA_si_tout_alcool']=(t.TTC_hors*k).round(2); print(t.to_string()); print('cumul',t.sum().round(2).to_dict())
print(m[m.hors_nonnul].groupby(['ex','lib_s']).agg(lignes=('pu','size'),TTC=('tot','sum')).round(2).to_string())
