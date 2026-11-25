"""Annexe B : typologie des lignes selon Qté (entière/fractionnaire) et écart col. B du service ; pied de page."""
import pandas as pd, numpy as np
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import C
B=pd.read_pickle(C+'B.pkl')
B['frac']=(abs(B.qte-B.qte.round())>1e-9)
# écart recalculé = pu*qte - tot (col B du service = A - 10)
B['ecart_calc']=(B.pu*B.qte-B.tot).round(6)
B['ecB']=B.B.round(6)
print('col A = pu*qte ?', (abs(B.A-B.pu*B.qte)>0.0005).sum(), ' col B = A - tot ?', (abs(B.B-(B.A-B.tot))>0.0005).sum())
def cls(x):
    return 'neg' if x< -0.005 else ('pos' if x>0.005 else 'zero')
B['sgn']=B.ecB.map(cls)
for ex,g in B.groupby('ex'):
    foot=pd.read_pickle(C+f'B_foot_{ex}.pkl')
    t=pd.crosstab(g.frac,g.sgn)
    print('====',ex); print(t)
    print(' somme Qté',round(g.qte.sum(),2),'pied',foot[5],' | somme tot',round(g.tot.sum(),2),'pied',foot[9],' | somme A',round(g.A.sum(),3),'pied',foot[10],' | somme B',round(g.B.sum(),3),'pied',foot[11])
    print(' somme écarts négatifs',round(g.B[g.sgn=="neg"].sum(),2),' dont entiers',round(g.B[(g.sgn=="neg")&~g.frac].sum(),2),' dont frac',round(g.B[(g.sgn=="neg")&g.frac].sum(),2),' somme écarts positifs',round(g.B[g.sgn=="pos"].sum(),2),' n pos',(g.sgn=="pos").sum(), ' somme |B|<0.005 non nuls', round(g.B[g.sgn=="zero"].sum(),4))
B.to_pickle(C+'B.pkl')
