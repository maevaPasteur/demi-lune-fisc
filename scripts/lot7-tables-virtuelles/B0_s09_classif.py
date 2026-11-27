"""B0 point 5 : reconstitution de la classification « plat / menu » implicite de la pièce 11 (couverts par note),
par moindres carrés bornés sur les quantités de l'annexe C (variable par libellé), puis arrondi 0/1 et contrôle exact.
Sortie : out/s09_classif.txt ; out/s09_libelles.csv (libellé, inclus, lignes, quantité)"""
import pandas as pd, numpy as np, unicodedata, re
from scipy.sparse import csr_matrix
from scipy.optimize import lsq_linear
O='scripts/lot7-tables-virtuelles/out/'
C=pd.read_pickle(O+'B0cache/C.pkl'); P11=pd.read_pickle(O+'B0cache/P11.pkl')
out=open(O+'B0_s09_classif.txt','w')
def p(*a): print(*a); print(*a,file=out)
C['libs']=C.lib.astype(str).str.strip()
X=C[C.id.isin(P11.id)].groupby(['id','libs']).qte.sum().reset_index()
ids={v:i for i,v in enumerate(P11.id)}; libs=sorted(X.libs.unique()); li={v:i for i,v in enumerate(libs)}
M=csr_matrix((X.qte.values,( X.id.map(ids).values, X.libs.map(li).values)),shape=(len(ids),len(libs)))
y=P11.cv.values
r=lsq_linear(M,y,bounds=(0,1),lsmr_tol='auto',max_iter=5000)
x=np.round(r.x)
pred=M@x
p('libellés',len(libs),' ; inclus (arrondi)',int(x.sum()),' ; notes exactes',int(np.isclose(pred,y,atol=1e-6).sum()),'/',len(y),' ; somme prédite',round(pred.sum(),2),' vs',round(y.sum(),2))
amb=[(libs[i],round(r.x[i],3)) for i in range(len(libs)) if 0.05<r.x[i]<0.95]; p('coefficients ambigus :',amb[:40])
bad=np.where(~np.isclose(pred,y,atol=1e-6))[0]
p('notes non expliquées :',len(bad))
for i in bad[:15]:
    nid=P11.id.iloc[i]; p('  ',nid,'P11=',y[i],'pred=',pred[i],C[C.id==nid][['libs','qte']].values.tolist())
L=pd.DataFrame({'lib':libs,'inclus':x.astype(int),'coef':r.x.round(3)})
st=C.groupby('libs').agg(lignes=('qte','size'),qte=('qte','sum'),pu_med=('pu','median'),ref=('ref',lambda s: ','.join(sorted(set(map(str,s))))[:40]))
L=L.merge(st,left_on='lib',right_index=True,how='left').sort_values(['inclus','qte'],ascending=False)
L.to_csv(O+'B0_s09_libelles.csv',index=False)
p('Libellés inclus (top 60 par quantité) :'); p(L[L.inclus==1].head(60)[['lib','qte','pu_med','ref']].to_string())
p('Libellés exclus (top 60 par quantité) :'); p(L[L.inclus==0].head(60)[['lib','qte','pu_med','ref']].to_string())
out.close()
