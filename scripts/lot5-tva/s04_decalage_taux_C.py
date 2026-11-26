"""s04 : la colonne Taux_tva des annexes C est-elle décalée d'une ligne ?
Vérité terrain indépendante du service : taux modal de l'article (ref) estimé sur la colonne décalée (rf[i+1]),
puis contrôle par le journal G (paliers TTC 10/20 par ticket). Placebo : permutations aléatoires (graine 20261123)."""
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
rng=np.random.default_rng(20261123)
CC=loadC().reset_index(drop=True)
CC['rf']=CC.tva.astype(int)
CC['rc']=np.where(CC.Es=='10 % / 20 %',20,np.where(CC.Es=='20 % / 10 %',10,CC.rf)).astype(int)   # taux corrigé par le service
print('E "10 % / 20 %" : taux fichier 10 -> corrigé 20 ; F = TTC*(20/120-10/110) :',
      np.allclose(CC[CC.Es=='10 % / 20 %'].Fs, CC[CC.Es=='10 % / 20 %'].tot*(20/120-10/110)) )
for k,(a,b) in {'10 % / 20 %':(10,20),'20 % / 10 %':(20,10)}.items():
    x=CC[CC.Es==k]; fx=x.tot*(b/(100+b)-a/(100+a)); fA=x.A*(b/(100+b)-a/(100+a))
    print(f'  E={k}: lignes {len(x)} ; F == Tot_rem_Ttc*(...) : {(abs(x.Fs-fx)<1e-6).sum()} ; F == colonne A*(...) : {(abs(x.Fs-fA)<1e-6).sum()} ; ni l\'un ni l\'autre : {((abs(x.Fs-fx)>=1e-6)&(abs(x.Fs-fA)>=1e-6)).sum()}')
bad=CC[(CC.Es!='')&(abs(CC.Fs-np.where(CC.Es=='10 % / 20 %',CC.tot*(20/120-10/110),CC.tot*(10/110-20/120)))>1e-6)]
print('  lignes où F ≠ Tot_rem_Ttc × écart de taux :',len(bad)); print(bad[['ex','rowC','lib','qte','pu','tot','A','Es','Fs']].head(8).to_string())
# décalages
print('\naccord Taux_tva(i) avec taux corrigé(i+k), ordre du fichier, par exercice :')
for ex in EX:
    c=CC[CC.ex==ex]
    print(' ',ex,{k:round(float((c.rf.values[max(0,k):len(c)+min(0,k)]==c.rc.values[max(0,-k):len(c)-max(0,k)]).mean()),4) for k in [-2,-1,0,1,2]})
# vérité indépendante : taux de l'article estimé par la ligne suivante
CC['next_rf']=CC.groupby('ex').rf.shift(-1)
mod=CC.dropna(subset=['next_rf']).groupby('ref').next_rf.agg(lambda s:int(s.value_counts().index[0])); CC['rart']=CC.ref.map(mod)
share=CC.dropna(subset=['next_rf']).groupby('ref').next_rf.agg(lambda s:s.value_counts(normalize=True).iloc[0])
print('\nrefs',len(mod),' part des refs dont le taux "suivant" est univoque à ≥99 % :',round((share>=0.99).mean(),4),' à 100 % :',round((share==1).mean(),4))
print('taux article (estimé sans le service) == taux corrigé par le service :',round((CC.rart==CC.rc).mean(),5),' lignes en désaccord :',(CC.rart!=CC.rc).sum())
CC['prev_rart']=CC.groupby('ex').rart.shift(1)
ok=(CC.rf==CC.prev_rart)
print('Taux_tva(i) == taux article(i-1) :',ok.sum(),'/',CC.prev_rart.notna().sum(),f'= {ok.sum()/CC.prev_rart.notna().sum():.5f}',' ; Taux_tva(i)==taux article(i) :',round((CC.rf==CC.rart).mean(),5))
# position dans la note
CC['pos']=CC.groupby(['ex','id']).cumcount(); first=CC.pos==0
print('  1re ligne de note : accord avec article(i-1) [dernière ligne de la note précédente]',round(ok[first].mean(),5),' ; lignes suivantes',round(ok[~first].mean(),5))
CC['ok']=ok
# résidus
r=CC[~ok & CC.prev_rart.notna()]
print('  résidus',len(r),' par exercice',r.ex.value_counts().to_dict())
print(r[['ex','rowC','date','ticket','lib','tot','rf','rart','prev_rart']].head(15).to_string())
# placebo : permutation intra-exercice de la colonne Taux_tva
pl=[]
for _ in range(200):
    p=CC.groupby('ex').rf.transform(lambda s: rng.permutation(s.values))
    pl.append((p==CC.prev_rart).mean())
print('placebo (200 permutations, graine 20261123) accord moyen',round(np.mean(pl),5),' max',round(np.max(pl),5))
# lignes signalées par le service = lignes où taux article(i-1) ≠ taux article(i) ?
CC['flag']=CC.Es!=''; CC['chg']=(CC.prev_rart!=CC.rart)
print('\nlignes signalées par le service',CC.flag.sum(),' ; lignes où le taux de l\'article précédent diffère :',CC.chg.sum(),
      ' ; croisement', pd.crosstab(CC.flag,CC.chg).to_dict())
CC.to_pickle(CA+'C_taux.pkl')
