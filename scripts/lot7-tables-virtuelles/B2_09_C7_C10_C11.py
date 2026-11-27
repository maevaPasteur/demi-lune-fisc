"""C-7 (830 tickets sans DEL à leur minute), C-10 (rotation : fenêtres glissantes de clôtures), C-11 (sensibilité : tables vidées, calendrier).
Sorties : out/B2/09.txt"""
import sys; sys.path.insert(0,"scripts/lot7-tables-virtuelles")
from B2_common import *
C,E,F,H,A=load(); p=out2('09.txt'); P=plats()
D=E[E.typEven=='DEL']; Z=H[~H.dansC].copy(); dk=set(zip(D.dateEven,D.t))
Z['atm']=[(d,t) in dk for d,t in zip(Z.date_ticket,Z.t)]; W=Z[~Z.atm].copy()
DZ={z:g.t.values for z,g in D.groupby('no_zEport')}; ZZ={z:g.t.values for z,g in Z.groupby('no_z_report')}
p(f'C-7. 830 tickets sans DEL à leur minute : {len(W)}')
rest=W.copy()
for k in (1,2,5):
    keep=[]
    for _,r in rest.iterrows():
        v=DZ.get(r.no_z_report,np.array([])); near=v[(abs(v-r.t)<=k)]
        others=ZZ[r.no_z_report]; oth=((abs(others-r.t)<=k)&(others!=r.t)).sum()   # autre ticket vide dans la fenêtre
        keep.append(not (len(near)>0 and oth==0))
    rest=rest[keep]; p(f'   après tolérance ± {k} min (DEL du même Z, aucun autre ticket vide dans la fenêtre) : restent {len(rest)}')
CON=E[E.typEven=='CON']; CZ={z:g.t.values for z,g in CON.groupby('no_zEport')}
RPR=E[E.typEven=='RPR']; rk=set(zip(RPR.dateEven,RPR.t))
N1=H[(H.serie==1)&(H.tc!=0)]; firstd=H.groupby('date_ticket').t.min(); nk=set(zip(N1.date_ticket,N1.t,N1.no_ticket))
def cls(r):
    v=CZ.get(r.no_z_report,np.array([])); v=v[v<=r.t]
    if len(v) and r.t-v.max()<=30: return 'dans les 30 min après un CON'
    if r.t==firstd[r.date_ticket]: return 'premier ticket de la journée'
    if (r.date_ticket,r.t) in rk: return 'à la minute d un RPR'
    if (r.date_ticket,r.t,r.no_ticket) in nk: return 'à la minute d une note de même rang'
    return 'résidu'
rest['cls']=rest.apply(cls,axis=1); p('   classement du reste :',rest.cls.value_counts().to_dict())
res=rest[rest.cls=='résidu']
def hb(s): return pd.cut(s,[0,600,720,840,1080,1200,1440],right=False,labels=['<10h','10-12h','12-14h','14-18h','18-20h','≥20h']).value_counts().sort_index().to_dict()
p('   résidu, heure :',hb(res.t),' ; tickets vides à la minute d un DEL, heure :',hb(Z[Z.atm].t))
# C-10 rotation
p('\nC-10. Rotation : couverts clos dans une fenêtre glissante (liste de la société, pièce 11)')
P11=pd.read_pickle(Q+'P11.pkl'); S92=pd.read_pickle(Q+'S92.pkl')
P11['svc']=np.where(P11.t<1080,'midi','soir')
def maxwin(g,w):
    t=g.t.values; c=g.cv.values; o=np.argsort(t); t=t[o]; c=c[o]; m=0
    for i in range(len(t)):
        m=max(m,c[(t>=t[i])&(t<t[i]+w)].sum())
    return m
rows=[]
for (d,s),g in P11.groupby(['date','svc']):
    rows.append(dict(date=d,service=s,notes=len(g),premiere=g.t.min(),derniere=g.t.max(),m60=maxwin(g,60),m90=maxwin(g,90),m120=maxwin(g,120)))
R=pd.DataFrame(rows).merge(S92[['date','service','places','occ','cv']],on=['date','service'])
R['etal']=R.derniere-R.premiere
o=R[R.occ>100]
p(f'   42 services au-delà de 100 % : notes médiane {o.notes.median():.0f} ; étalement médian {o.etal.median():.0f} min ; max sur 60 / 90 / 120 min rapporté aux places (médiane) {(o.m60/o.places).median()*100:.0f} / {(o.m90/o.places).median()*100:.0f} / {(o.m120/o.places).median()*100:.0f} % ; services où aucune fenêtre de 90 min ne dépasse les places : {int((o.m90<=o.places).sum())}')
p(f'   1 269 services : fenêtre de 90 min > places : {int((R.m90>R.places).sum())} ; distribution du rapport m90 / places (P50, P90, max) : {(R.m90/R.places).quantile(.5)*100:.0f} / {(R.m90/R.places).quantile(.9)*100:.0f} / {(R.m90/R.places).max()*100:.0f} %')
p('   limite : l heure de clôture n est pas l heure d arrivée.')
# C-11
p('\nC-11. Sensibilité')
SD=pd.read_csv(OUT2+'07_services_DPc.csv')
x=D[(D.ac>0)&(D.ac<100000)].copy()
C['pc']=(C.pu*100).round().astype(int)
carte={ex:g[g.pc>0].groupby('pc').libs.apply(set) for ex,g in C.groupby('ex')}
L=pd.read_csv(OUT2+'07_libelles.csv'); DPc=set(L[L.DP_corrigee==1].lib)
x['plat']=[(ac in carte[ex].index) and carte[ex][ac]<=DPc for ex,ac in zip(x.ex,x.ac)]
Pop=pd.read_csv(OUT2+'04_tables.csv'); pk=set(zip(Pop.d,Pop.t)); x=x[np.array([ (d,t) in pk for d,t in zip(x.dateEven,x.t)])&x.plat.values]
x['svc']=np.where(x.t<1080,'midi','soir'); add=x.groupby(['dateEven','svc']).size()
SD['add']=[add.get((d,s),0) for d,s in zip(SD.date,SD.svc)]
o2=(SD.cv+SD['add'])/SD.pl*100
p(f'   D-P corrigée : couverts identifiables des tables vidées {int(SD["add"].sum())} ; occupation {SD.o.mean():.2f} % → {o2.mean():.2f} % si aucun n a été ressaisi ; > 100 % {int((SD.o>100).sum())} → {int((o2>100).sum())}')
R5=pd.read_csv(OUT2+'05_tables.csv'); inc=R5[(R5.W==240)&(R5.c_tot==1)].table
Pi=Pop[Pop['N° de table'].isin(inc)]; ik=set(zip(Pi.d,Pi.t)); x2=x[np.array([ (d,t) not in ik for d,t in zip(x.dateEven,x.t)])]
add2=x2.groupby(['dateEven','svc']).size(); SD['add2']=[add2.get((d,s),0) for d,s in zip(SD.date,SD.svc)]
o3=(SD.cv+SD['add2'])/SD.pl*100
p(f'   en retirant les tables à inclusion totale de C-5 (W = 240) : couverts {int(SD["add2"].sum())} ; occupation {o3.mean():.2f} %')
# calendrier
def cal(row,rule):
    m=int(row.date[5:7]); j=int(row.date[8:10])
    if rule=='R1':   # terrasse de mai à la mi-septembre
        return m in (5,6,7,8) or (m==9 and j<=15)
    return m in (5,6,7,8)
CP={'2022-07-14','2023-07-14','2024-07-14','2022-09-30','2022-10-01','2022-10-02','2023-09-30','2023-10-01','2024-09-27','2024-09-28','2024-09-29'}
for lab,rule,cp in [('pièce 92 (mai à août)','92',False),('R1 (mai à mi-septembre)','R1',False),('R1 + 14 juillet et Chat Perché en terrasse','R1',True)]:
    for nm,S in [('V0',pd.read_pickle(Q+'S92.pkl').rename(columns={'service':'svc'})),('D-P corrigée',SD)]:
        S=S.copy(); S['terr']=[cal(r,rule) or (cp and r.date in CP) for r in S.itertuples()]
        pl=np.where(S.terr,48,46); oc=S.cv/pl*100
        p(f'   calendrier {lab}, {nm} : occupation {oc.mean():.2f} % ; > 100 % {int((oc>100).sum())}')
p('   écart de capacité entre espaces : 46 / 48 places ; effet maximal d une règle de calendrier (B0) : 61,4 % (48 partout) à 64,0 % (46 partout)')
