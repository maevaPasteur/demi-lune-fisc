"""B0 point 5 : contrôles complémentaires : (a) les 5 notes non expliquées de la pièce 11 = rattachement par (date, n°) des tickets
non nuls de 2e série ; (b) arrondi de la pièce 92 (Services (source), colonne F) ; (c) 13/17 tickets de 2e série repris (indicatif).
Sortie : out/s12_controles_couverts.txt"""
import pandas as pd, numpy as np
O='scripts/lot7-tables-virtuelles/out/'
C=pd.read_pickle(O+'B0cache/C.pkl'); A=pd.read_pickle(O+'B0cache/A.pkl'); H=pd.read_pickle(O+'B0cache/H2.pkl')
P11=pd.read_pickle(O+'B0cache/P11.pkl'); P12=pd.read_pickle(O+'B0cache/P12.pkl'); S92=pd.read_pickle(O+'B0cache/S92.pkl')
L=pd.read_csv(O+'B0_s09_libelles.csv'); PLAT=set(L[L.inclus==1].lib)
out=open(O+'B0_s12_controles_couverts.txt','w')
def p(*a): print(*a); print(*a,file=out)
C['libs']=C.lib.astype(str).str.strip()
cv=C[C.libs.isin(PLAT)].groupby('id').qte.sum().reindex(A.id).fillna(0); A['cv']=cv.values
s2=set(H[H.serie==2].id)
A1=A[~A.id.isin(s2)]; A2=A[A.id.isin(s2)]
g=A.groupby(['date','no']).cv.sum()
A1=A1.assign(cv_rang=[g[(d,n)] for d,n in zip(A1.date,A1.no)])
m=A1.merge(P11[['id','cv']],on='id',suffixes=('','_11'))
p('(a) notes 1re série : couverts propres = P11 :',int(np.isclose(m.cv,m.cv_11).sum()),'/',len(m),' ; couverts agrégés par (date, n°) = P11 :',int(np.isclose(m.cv_rang,m.cv_11).sum()),'/',len(m))
p('    couverts des 17 tickets de 2e série :',round(A2.cv.sum(),2),' (dont rattachés à une note de 1re série par le rang)')
# (b) arrondi
mm=P12.melt(id_vars=['date'],value_vars=['midi','soir'],var_name='service',value_name='cv12').merge(S92,on=['date','service'])
p('(b) S92 = round() Python (demi au pair) :',int((mm.cv==mm.cv12.round()).sum()),'/',len(mm),' ; = arrondi demi vers le haut :',int((mm.cv==np.floor(mm.cv12+0.5)).sum()),'/',len(mm))
p('    services à x,5 exact :',mm[(mm.cv12%1==0.5)][['date','service','cv12','cv']].values.tolist())
p('    somme non arrondie',round(mm.cv12.sum(),2),' ; somme arrondie',int(mm.cv.sum()))
# (c) 17 tickets de 2e série : chaque article repris (quantité cumulée >= ) sur des notes de 1re série du même jour, encaissées après
rob=0; res=[]
for i in sorted(s2 & set(A.id)):
    a=A[A.id==i].iloc[0]; art=C[C.id==i].groupby('libs').qte.sum()
    same=A1[(A1.date==a.date)]
    after=same[same.heure>=a.heure]
    q_all=C[C.id.isin(same.id)].groupby('libs').qte.sum(); q_after=C[C.id.isin(after.id)].groupby('libs').qte.sum()
    ok_all=all(q_all.get(k,0)>=v-1e-9 for k,v in art.items()); ok_after=all(q_after.get(k,0)>=v-1e-9 for k,v in art.items())
    res.append((a.date,a.heure,a.no,i,len(art),ok_all,ok_after))
R=pd.DataFrame(res,columns=['date','heure','rang','id','articles','repris_jour','repris_apres'])
p('(c) indicatif : 17 tickets de 2e série dont tous les articles figurent en quantité au moins égale sur des notes de 1re série du jour :',int(R.repris_jour.sum()),' ; sur des notes closes après :',int(R.repris_apres.sum()))
p(R.to_string())
out.close()
