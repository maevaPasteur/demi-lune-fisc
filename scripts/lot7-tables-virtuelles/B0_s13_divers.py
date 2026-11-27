"""B0 : contrôles divers : journée la plus chargée ; CA des journées des 4 lignes aberrantes ; jours avec DEL. Sortie : out/s13_divers.txt"""
import pandas as pd, numpy as np
O='scripts/lot7-tables-virtuelles/out/'
A=pd.read_pickle(O+'B0cache/A.pkl'); S92=pd.read_pickle(O+'B0cache/S92.pkl'); E=pd.read_pickle(O+'B0cache/E.pkl')
out=open(O+'B0_s13_divers.txt','w')
def p(*a): print(*a); print(*a,file=out)
d=S92.groupby('date').cv.sum().sort_values(ascending=False); p('Journées les plus chargées (couverts S92) :',d.head(5).to_dict())
n=A.groupby('date').size().sort_values(ascending=False); p('Journées aux plus nombreuses additions :',n.head(5).to_dict())
ca=A.groupby('date').tot.sum()
for dd in ['2022-07-26','2023-06-21','2022-08-07','2024-08-15']: p(f'  CA TTC des notes (C) le {dd} : {ca.get(dd):.2f} € ; DEL du jour hors ligne aberrante :',round(E[(E.dateEven==dd)&(E.typEven=="DEL")&(E.amount<1000)].amount.sum(),2))
D=E[E.typEven=='DEL']; p('Journées (dates) avec au moins un DEL :',D.dateEven.nunique(),' ; Z distincts avec DEL :',D.no_zEport.nunique(),' ; Z distincts dans E :',E.no_zEport.nunique())
p('Couverts de la journée 09/07/2022 :',int(d.get('2022-07-09')))
out.close()
out=open(O+'B0_s13_divers.txt','a')
S=S92.copy(); S['an']=S.date.str[:4]; S['mois']=S.date.str[5:7]
M=S.groupby(['an','mois']).occ.mean().round(1).unstack(0); p('Occupation moyenne (S92) par mois et année civile :'); p(M.to_string())
p('Par mois (3 ex.) :',S.groupby('mois').occ.mean().round(1).to_dict())
out.close()
