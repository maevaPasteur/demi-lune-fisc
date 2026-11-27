"""D-6 : couverts identifiables dans les tables vidées. Une ligne DEL positive (< 1 000 €) compte un couvert lorsque son montant est
le prix unitaire d'articles de la carte de l'exercice (annexe C, PU > 0) qui sont TOUS classés « plat / menu » (classification B0_s09).
Borne basse : les lignes multiples (quantité > 1) et les prix partagés avec un article non classé ne comptent pas.
Sortie : out/B1/D06.txt"""
import sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from B1_common import *
C,E,F,H,A=load(); P=plats(); p=out('D06.txt')
S92=pd.read_pickle(Q+'S92.pkl')
C['pc']=(C.pu*100).round().astype(int)
carte={ex:g[g.pc>0].groupby('pc').libs.apply(set) for ex,g in C.groupby('ex')}
def uniq_plat(ex,ac):
    s=carte[ex].get(ac); return s is not None and s<=P
D=E[(E.typEven=='DEL')&(E.ac>0)&(E.ac<100000)].copy()
D['plat']=[uniq_plat(ex,ac) for ex,ac in zip(D.ex,D.ac)]
D['carte']=[ac in carte[ex].index for ex,ac in zip(D.ex,D.ac)]
Z=H[~H.dansC]; zk=set(zip(Z.date_ticket,Z.t))
tv=tv2359()[['d','t']].copy(); tv['d']=tv.d.astype(str); tv['t']=tv.t.astype(str).map(tm); k2=set(zip(tv.d,tv.t))
D['def1']=[(d,t) in zk for d,t in zip(D.dateEven,D.t)]; D['def2']=[(d,t) in k2 for d,t in zip(D.dateEven,D.t)]
F_=F.groupby('id').montant.sum(); z37=Z[Z.id.map(F_).fillna(0)!=0]; k37=set(zip(z37.date_ticket,z37.t))
D['t37']=[(d,t) in k37 for d,t in zip(D.dateEven,D.t)]
cvx=S92.groupby('ex').cv.sum()
p(f'Lignes DEL positives < 1 000 € : {len(D)} ; égales à un prix de la carte {int(D.carte.sum())} ; à un prix propre aux plats et menus {int(D.plat.sum())}')
for lab,col in [('toutes les lignes DEL','carte'),('tables vidées, définition 1 (minutes des 2 449 tickets)','def1'),('tables vidées, définition 2 (minutes des 2 359 tables)','def2'),('37 tickets porteurs de règlements','t37')]:
    sub=D if col=='carte' else D[D[col]]
    g=sub.groupby('ex').agg(lignes=('ac','size'),couverts=('plat','sum'))
    g['part_non_identifiable_%']=((1-g.couverts/g.lignes)*100).round(1); g['rapport_aux_couverts_comptés_%']=(g.couverts/cvx*100).round(2)
    p(f'{lab} :'); p(g.to_string()); p(f'   total : lignes {len(sub)} ; couverts identifiables {int(sub.plat.sum())} ({sub.plat.sum()/S92.cv.sum()*100:.2f} % des 37 373)')
# effet sur l'occupation (définition 2), en ajoutant les couverts identifiables au service de la minute de la ligne
x=D[D.def2&D.plat].copy(); x['service']=np.where(x.t<1080,'midi','soir')
add=x.groupby(['dateEven','service']).size().rename('add').reset_index().rename(columns={'dateEven':'date'})
S=S92.merge(add,on=['date','service'],how='left'); S['add']=S['add'].fillna(0)
S['occ2']=(S.cv+S['add'])/S.places*100
p(f'Effet (définition 2, borne basse) : occupation moyenne {S.occ.mean():.2f} % → {S.occ2.mean():.2f} % ; services > 100 % : {int((S.cv>S.places).sum())} → {int((S.cv+S["add"]>S.places).sum())}')
j=S[S['add']>0]; p(f'  services concernés {len(j)} ; leur occupation {j.occ.mean():.1f} % → {j.occ2.mean():.1f} % ; parmi les 42 au-delà de 100 % : {int(((S.cv>S.places)&(S["add"]>0)).sum())} reçoivent {int(S[(S.cv>S.places)]["add"].sum())} couverts')
p('Limite : une partie du contenu des tables vidées a pu être ressaisie sur des notes encaissées (estimation de la société : 11,7 à 14,8 % du montant) ; ces couverts seraient alors déjà comptés.')
