"""D-1 : sémantique de l'identifiant de note (id de H/C/F) et de sy_uk (export natif).
Sorties : out/B1/D01.txt, out/B1/D01_syuk.csv"""
import sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from B1_common import *
from scipy.stats import spearmanr
C,E,F,H,A=load(); S=source(); p=out('D01.txt')
H=H.sort_values('id').reset_index(drop=True)
# 1. Spearman par journée, séries séparées
for lab,sub in [('série 1 (notes, tot_sum > 100 000)',H[H.serie==1]),('série 2 (tickets à 0 et 17 non nuls)',H[H.serie==2]),('tout H',H)]:
    rs=[]; inv=0; pairs=0; inv_strict=0
    for d,g in sub.groupby('date_ticket'):
        g=g.sort_values('id')
        if len(g)>=3: rs.append(spearmanr(g.id,g.t).statistic)
        dt=np.diff(g.t.values); pairs+=len(dt); inv+=(dt<0).sum()
    rs=np.array(rs)
    p(f'{lab} : journées {len(rs)} ; Spearman id/heure de clôture médian {np.nanmedian(rs):.3f}, P10 {np.nanpercentile(rs,10):.3f}, min {np.nanmin(rs):.3f} ; couples consécutifs du même jour {pairs}, heure décroissante {inv} ({inv/pairs*100:.1f} %)')
# variante du sondage A : tous couples consécutifs par id dans H (y compris changement de jour), heure ou date décroissante
h=H.sort_values('id'); key=h.date_ticket+' '+h.heure_ticket
dec=(key.values[1:]<key.values[:-1]).sum(); p(f'tous couples consécutifs par id (19 902) : (date, heure) décroissante {dec} ; même jour seulement, heure décroissante : voir ci-dessus')
# rang de clôture : le n° de note suit-il l'heure de clôture ?
a=A.sort_values(['date','no']); bad=0
for d,g in a.groupby('date'): bad+=(np.diff(g.t.values)<0).sum()
p(f'numéro de note (série 1, C) contre heure de clôture : couples consécutifs de rangs où l heure décroît : {bad} sur {len(a)-a.date.nunique()}')
z=H[H.serie==2].sort_values(['date_ticket','no_ticket']); badz=0; nz=0
for d,g in z.groupby('date_ticket'): x=np.diff(g.t.values); badz+=(x<0).sum(); nz+=len(x)
p(f'rang de seconde série contre heure de clôture : {badz} décroissances sur {nz} couples')
# 2. notes partagées : groupes de notes du même Z, mêmes lignes (libellé, quantité), au moins une quantité fractionnaire, clôtures à 10 min au plus
sig=C.groupby('id').apply(lambda g: tuple(sorted(zip(g.libs,g.qte.round(4)))),include_groups=False)
fr=C.groupby('id').qte.apply(lambda s: ((s-s.round()).abs()>1e-9).any())
a=A.set_index('id'); a['sig']=sig; a['fr']=fr
a=a[a.fr].reset_index()
grp=[]
for (z_,s_),g in a.groupby(['z','sig']):
    if len(g)>=2 and g.t.max()-g.t.min()<=10: grp.append(g.sort_values('id'))
n=len(grp); after=sum(1 for g in grp if g.t.iloc[0]>g.t.iloc[1:].max()); before=sum(1 for g in grp if g.t.iloc[0]<g.t.iloc[1:].min()); same=n-after-before
p(f'groupes de parts identiques (même Z, mêmes lignes fractionnaires, ≤ 10 min) : {n} ; plus petit id clos après toutes ses parts {after} ({after/n*100:.1f} %) ; avant toutes {before} ({before/n*100:.1f} %) ; autre (même minute ou intercalé) {same}')
# 3. sy_uk
S['id']=S.id.astype(int)
u=S.drop_duplicates('id').sort_values('id').copy()
p(f'sy_uk : {len(u)} valeurs, 18 chiffres ; structure observée : 4 chiffres (préfixe) + « 000201 » ({(u.sy.str[4:10]=="000201").mean()*100:.1f} %) + compteur')
p('  sy_uk strictement croissant avec id :',bool((np.diff(u.sy_uk.astype('int64').values)>0).all()),' ; préfixe non décroissant avec id :',bool((np.diff(u.pre.values)>=0).all()))
u['d']=pd.to_datetime(u.date_ticket); u['jour_pre']=pd.Timestamp('2012-09-25')+pd.to_timedelta(u.pre,unit='D')
u['lag']=(u.d-u.jour_pre).dt.days
p('  préfixe = nombre de jours depuis le 25/09/2012 (calage sur la journée de clôture la plus fréquente) ; écart clôture - jour du préfixe :',u.lag.value_counts().sort_index().head(12).to_dict())
p('  écart négatif (préfixe postérieur à la clôture) :',int((u.lag<0).sum()))
# le compteur repart-il à chaque changement de préfixe ?
u['newpre']=u.pre.diff()!=0
p('  compteur au premier sy_uk de chaque préfixe : médiane',int(u[u.newpre]['tail'].median()),' ; compteur médian global',int(u['tail'].median()))
# compteur et temps

u['dtail']=u['tail'].diff(); u['dpre']=u.pre.diff(); u['did']=u.id.diff()
w=u[u.dpre==0].copy(); nl=C.groupby('id').size(); w['nl']=w.id.map(nl).fillna(0)
p(f'  incrément du compteur (même préfixe) : médiane {w.dtail.median():.0f}, P10 {w.dtail.quantile(.1):.0f}, P90 {w.dtail.quantile(.9):.0f} ; corrélation avec l écart d id {np.corrcoef(w.dtail,w.did)[0,1]:.3f} ; avec le nombre de lignes C de la note {np.corrcoef(w.dtail,w.nl)[0,1]:.3f}')
for k in [1,2,3]:
    x=w[w.did==k].dtail; p(f'    écart d id = {k} : {len(x)} couples, incrément médian {x.median():.0f}')
# temps : incrément par minute de clôture écoulée entre deux notes consécutives du même jour
w['dtc']=w.heure_ticket.map(tm).diff().where(w.date_ticket==w.date_ticket.shift())
x=w[w.dtc.notna()&(w.dtc>0)]; p(f'    corrélation incrément / minutes écoulées entre clôtures (même jour, dt>0) : {np.corrcoef(x.dtail,x.dtc)[0,1]:.3f}')
# jours de remise à zéro du compteur : changement de préfixe
ch=u[u.dpre>0]; p(f'  changements de préfixe : {len(ch)} ; journées de clôture distinctes dans l export : {u.date_ticket.nunique()}')
# 4. notes à préfixe décalé : date du préfixe contre position de l'id
odd=u[u.lag>3].copy()
p(f'  notes dont la clôture suit de plus de 3 jours le jour du préfixe : {len(odd)}')
p(odd[['id','date_ticket','heure_ticket','no_ticket','tot_ttc','jour_pre','lag']].to_string())
# pour ces notes : dates de clôture des id voisins
H2=H.set_index('id')
for i in odd.id:
    nb=[j for j in range(i-3,i+4) if j in H2.index and j!=i]
    p('   ',i,'voisins',[(j,H2.loc[j,'date_ticket'],H2.loc[j,'heure_ticket']) for j in nb])
u[['id','sy_uk','pre','tail','date_ticket','heure_ticket','jour_pre','lag']].to_csv(OUT+'D01_syuk.csv',index=False)
