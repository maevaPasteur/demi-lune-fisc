"""M0-4 : 2.6.6 / tableau 67 ; recompte des lignes signalées (colonne E) et de la colonne F depuis les annexes C (cache 2.3 relu contre les pieds en s08),
et contrôle des agrégats du lot 2.5 (cache C_b3 : taux appliqué rart, taux légal tl) : 94,75 %, −9 701,34 €, TVA légale."""
import pandas as pd, numpy as np
CC=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/CC.pkl'); CC['Es']=CC.Es.astype(str).str.replace('\xa0',' ')
X=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot25/C_b3.pkl')
out=open('scripts/lot6-evenement-reglement/out/s09_tva_check.txt','w')
def p(*a): print(*a); print(*a,file=out)
t=CC.groupby(['ex','Es']).size().unstack(fill_value=0); p(t.to_string())
p('Σ colonne F par exercice :',CC.groupby('ex').Fs.sum().round(2).to_dict(),' total',round(CC.Fs.sum(),2))
p('lot 2.5 C_b3 identique à CC (lignes, Es, Fs) :',len(X)==len(CC), (X.sort_values(['ex','rowC']).Es.values==CC.sort_values(['ex','rowC']).Es.values).all())
fl=X.flag; art=fl&X.tl.notna()&(X.rart==X.tl)&(X.Ecor==X.rart)
p('signalées',int(fl.sum()),' ; artefacts (caisse juste et correction du service = taux appliqué)',int(art.sum()),f'({art.sum()/fl.sum()*100:.2f} %)',' ; F de ces lignes',round(X[art].Fs.sum(),2))
# variante : signalées où le taux appliqué = taux corrigé par le service (indépendamment du taux légal)
a2=fl&(X.Ecor==X.rart); p('signalées où correction du service = taux appliqué :',int(a2.sum()),f'({a2.sum()/fl.sum()*100:.2f} %)',' F',round(X[a2].Fs.sum(),2))
a3=fl&(X.rf==X.prev_rart); p('signalées où le taux du fichier = taux appliqué de la ligne précédente :',int(a3.sum()))
k=lambda t,r: t*r/(100+r)
X['tva_app']=k(X.tot,X.rart); X['tva_leg']=k(X.tot,X.tl.fillna(X.rart))
p('TVA (non arrondie, ligne à ligne) appliquée / légale par exercice :',X.groupby('ex')[['tva_app','tva_leg']].sum().round(2).to_dict())
p('références à deux taux appliqués (rart) par exercice :',X.groupby(['ex','ref']).rart.nunique().gt(1).groupby('ex').sum().to_dict(),
  ' ; à deux taux dans le fichier (rf) :',X.groupby(['ex','ref']).rf.nunique().gt(1).groupby('ex').sum().to_dict(),' ; références par exercice :',X.groupby('ex').ref.nunique().to_dict())
out.close()
