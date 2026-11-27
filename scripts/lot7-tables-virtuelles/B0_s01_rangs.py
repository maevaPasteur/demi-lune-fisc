"""B0 point 1 : test suite 1..n par journée, additions, numéros distincts, n° max, corrélation, 101-126.
Annexe C : colonne 3 « No_ticket » (numéro de note), colonne 9 « Id » (identifiant interne), colonne 1 « Date Ticket ».
Sortie : out/s01_rangs.txt, out/s01_jours.csv"""
import pandas as pd, numpy as np
O='scripts/lot7-tables-virtuelles/out/'
C=pd.read_pickle(O+'B0cache/C.pkl'); H=pd.read_pickle(O+'B0cache/H.pkl')
out=open(O+'B0_s01_rangs.txt','w')
def p(*a): print(*a); print(*a,file=out)
p('date != datz dans C :',(C.date!=C.datz).sum(),' ; Id rattaché à plusieurs (date,no) :',(C.groupby('id')[['date','no']].nunique()>1).sum().to_dict())
A=C.groupby('id').agg(date=('date','first'),no=('no','first'),heure=('heure','first'),ex=('ex','first'),z=('z','first'),tot=('tot_ttc','first'),nlig=('lib','size')).reset_index()
p('Additions (Id distincts) par exercice :',A.groupby('ex').size().to_dict(),' total',len(A))
p('Journées (dates distinctes) :',A.groupby('ex').date.nunique().to_dict(),' total',A.date.nunique())
p('Couples (date,no) distincts :',A.drop_duplicates(['date','no']).groupby('ex').size().to_dict(),' total',len(A.drop_duplicates(['date','no'])))
p('Couples (z,no) distincts :',len(A.drop_duplicates(['z','no'])),' ; Z distincts :',A.z.nunique())
# test par journée sur l'ensemble des numéros DISTINCTS
J=A.groupby('date').agg(ex=('ex','first'),nadd=('id','size'),nmin=('no','min'),nmax=('no','max'),ndist=('no','nunique'),somme_dist=('no',lambda s: s.drop_duplicates().sum()),somme_brute=('no','sum')).reset_index()
J['attendu']=J.nmax*(J.nmax+1)//2
J['suite']=(J.nmin==1)&(J.ndist==J.nmax)&(J.somme_dist==J.attendu)
# variante « trois égalités » appliquée à n = nombre de numéros attribués distincts
J['suite_n']=(J.nmin==1)&(J.nmax==J.ndist)&(J.somme_dist==J.ndist*(J.ndist+1)//2)
# variante appliquée au nombre d'additions (avec doublons)
J['suite_add']=(J.nmin==1)&(J.nmax==J.nadd)&(J.somme_brute==J.nadd*(J.nadd+1)//2)
p('Journées suite 1..n (numéros distincts) :',J.groupby('ex').suite.sum().to_dict(),' total',J.suite.sum())
p('Journées suite où n = nombre d additions (doublons compris) :',J.groupby('ex').suite_add.sum().to_dict(),' total',J.suite_add.sum())
p('N° max par exercice :',J.groupby('ex').nmax.max().to_dict())
p('Journées n° max > 18 :',(J.nmax>18).groupby(J.ex).sum().to_dict(),' total',(J.nmax>18).sum(),f'({(J.nmax>18).mean()*100:.2f} %)')
for ex,g in J.groupby('ex'):
    p(f'  corrélation n° max / additions {ex} : {np.corrcoef(g.nmax,g.nadd)[0,1]:.6f}')
p('  corrélation 3 ex :',round(np.corrcoef(J.nmax,J.nadd)[0,1],6))
p('Journées avec doublon (date,no) :',(J.nadd>J.ndist).sum(),' rangs en double :',(J.nadd-J.ndist).sum())
p(J[J.nadd>J.ndist][['date','nadd','ndist','nmax']].to_string())
# numéros >= 100
p('Numéros >= 58 dans C :',(A.no>=58).sum(),' ; dans 101..126 :',A.no.between(101,126).sum())
p('H no_ticket max :',H.no_ticket.max(),' ; H no dans 101..126 :',H.no_ticket.between(101,126).sum())
p('Exemples : ');
for d in ['2022-07-09','2022-04-14']:
    r=J[J.date==d].iloc[0]; p('  ',d,dict(nadd=r.nadd,nmin=r.nmin,nmax=r.nmax,somme=r.somme_dist,attendu=r.attendu,suite=r.suite))
J.to_csv(O+'B0_s01_jours.csv',index=False); A.to_pickle(O+'B0cache/A.pkl')
# H : même numéro ? rapprochement Id C <-> H
m=A.merge(H[['id','no_ticket','date_ticket','heure_ticket','tot_ttc']],on='id',how='left')
p('Additions C trouvées dans H par Id :',m.no_ticket.notna().sum(),'/',len(m),' ; même n° :',(m.no==m.no_ticket).sum(),' ; même date :',(m.date==m.date_ticket).sum(),' ; même heure :',(m.heure==m.heure_ticket).sum(),' ; même total :',(np.isclose(m.tot,m.tot_ttc)).sum())
# profil mensuel
A['mois']=A.date.str[5:7]
M=A.groupby('mois').agg(add=('id','size'),jours=('date','nunique')); M['par_jour']=M['add']/M.jours
p('Profil mensuel (additions / journée) :'); p(M.round(2).to_string())
# 09/07/2022 notes 1,20,35,57
d=A[A.date=='2022-07-09'].sort_values('no')
p('09/07/2022 :',d[d.no.isin([1,20,35,57])][['no','heure','tot','id']].to_string())
# rangs (figure 29)
R=A.groupby('no').size(); p('Rangs 1..57 : total',R.sum(),' ; rangs présents',len(R),' ; min',R.index.min(),' max',R.index.max())
R.to_csv(O+'B0_s01_rangs.csv')
out.close()
