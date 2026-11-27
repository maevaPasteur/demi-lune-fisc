"""D-2 : faisabilité chronologique de la séquence attestée (ressaisie sur une note ouverte après la table, encaissement,
puis vidage) pour les tables vidées. Hypothèse de travail : id = ordre d'ouverture (voir D-1).
Définition 1 : 2 449 tickets H sans article clos à la minute d'un DEL de la même date (pièce 92).
Définition 2 : 2 359 tables du lot 2.2 version C (cache lot 2.6 b5_tables_videes.pkl : date d, minute t, montant V en centimes) ;
identifiant = tickets sans article clos à cette minute (min et max).
Sorties : out/B1/D02.txt, D02_def1.csv, D02_def2.csv"""
import sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from B1_common import *
C,E,F,H,A=load(); p=out('D02.txt')
D=E[E.typEven=='DEL']
Dm=D.groupby(['dateEven','t']).agg(m=('ac','sum'),big=('ac',lambda s:(s>=100000).any())).reset_index()
dm={(d,t):(m,b) for d,t,m,b in Dm.values}
Z=H[~H.dansC].copy()
Z['k']=list(zip(Z.date_ticket,Z.t)); Z=Z[Z.k.isin(dm.keys())].copy()
nk=Z.k.value_counts(); Z['m']=[dm[k][0]/100/nk[k] for k in Z.k]; Z['big']=[dm[k][1] for k in Z.k]
Z['rang2']=Z.no_ticket
N=H[(H.serie==1)&(H.tc!=0)][['date_ticket','t','id','no_ticket','tot_ttc']]
ND={d:g for d,g in N.groupby('date_ticket')}
def cats(d,t,x_lo,x_hi):
    g=ND.get(d)
    if g is None: return dict(a=True,b=True,c1=True,c2=True,nb='',na='')
    before=g[g.t<=t]; a=len(before)==0
    b=len(before[before.id>x_hi])==0      # id supérieur à l'identifiant de la table (x_hi : le plus défavorable)
    b_lo=len(before[before.id>x_lo])==0
    after=g[g.t>=t]
    c1=b and len(after)==0
    c2=b and len(g[g.id>x_hi])==0
    nb=before.sort_values('t').tail(2).id.tolist(); na=after.sort_values('t').head(2).id.tolist()
    return dict(a=a,b=b,b_lo=b_lo,c1=c1,c2=c2,nb=nb,na=na)
def run(T,lab,amt):
    R=pd.DataFrame([cats(d,t,lo,hi) for d,t,lo,hi in zip(T.d,T.t,T.lo,T.hi)],index=T.index)
    T=pd.concat([T,R],axis=1); T['ex']=T.d.map(ex_of)
    for sub,nm in [(T,'brut'),(T[~T.big],'hors minutes ≥ 1 000 €')]:
        p(f'{lab} [{nm}] : tables {len(sub)} ; montant {sub[amt].sum():,.2f} €'.replace(',',' '))
        for c,txt in [('a','(a) aucune note encaissée du jour close au plus tard à la minute'),('b','(b) aucune note d id supérieur close au plus tard à la minute (séquence attestée impossible)'),('c1','(c) (b) et aucune note close à la minute ou après'),('c2','(c bis) (b) et aucune note d id supérieur dans la journée')]:
            s=sub[sub[c]]; byx=s.groupby('ex')[amt].agg(['size','sum']).round(2)
            p(f'   {txt} : {len(s)} ({len(s)/len(sub)*100:.1f} %) ; {s[amt].sum():.2f} € ; par exercice {byx["size"].to_dict()} / {byx["sum"].to_dict()}')
        if 'b_lo' in sub:
            s=sub[sub.b_lo]; p(f'   (b) avec l identifiant le plus petit de la minute : {len(s)} ; {s[amt].sum():.2f} €')
        p(f'   (d) tolérance d une note d id inférieur (ressaisie sur une note déjà ouverte) : tables sans aucune séquence attestée possible = (a) : {int(sub.a.sum())}')
    return T
# définition 1
T1=Z.rename(columns={'date_ticket':'d'}).assign(lo=Z.id,hi=Z.id)
T1=run(T1,'Définition 1 (tickets sans article à la minute d un DEL ; montant = DEL de la minute réparti entre les tickets de la minute)','m')
T1[T1.a|T1.b|T1.c1][['d','heure_ticket','id','m','rang2','no_z_report','a','b','c1','c2','nb','na']].to_csv(OUT+'D02_def1.csv',index=False)
# définition 2
tv=tv2359()[['d','t','V','z']].copy(); tv['d']=tv.d.astype(str); tv['t']=tv.t.astype(str).map(tm)
zz=H[~H.dansC].groupby(['date_ticket','t']).id.agg(['min','max'])
tv['lo']=[zz.loc[(d,t),'min'] if (d,t) in zz.index else np.nan for d,t in zip(tv.d,tv.t)]
tv['hi']=[zz.loc[(d,t),'max'] if (d,t) in zz.index else np.nan for d,t in zip(tv.d,tv.t)]
p(f'Définition 2 : {len(tv)} tables ; sans ticket sans article à la minute : {int(tv.lo.isna().sum())}')
tv['big']=[dm.get((d,t),(0,False))[1] for d,t in zip(tv.d,tv.t)]; tv['V€']=tv.V/100
T2=run(tv,'Définition 2 (lot 2.2 version C ; montant V ; identifiant = plus grand id sans article de la minute)','V€')
T2[T2.a|T2.b|T2.c1][['d','t','lo','hi','V€','a','b','c1','c2','nb','na']].to_csv(OUT+'D02_def2.csv',index=False)
# témoin : les notes encaissées elles-mêmes (proportion sans note d'id supérieur close avant ou à leur minute)
w=[]
for d,g in ND.items():
    for x,t in zip(g.id,g.t): w.append(len(g[(g.id>x)&(g.t<=t)&(g.id!=x)])==0)
p(f'Témoin : notes encaissées sans autre note d id supérieur close au plus tard à leur minute : {np.mean(w)*100:.1f} % ({sum(w)} / {len(w)})')

# contrôle 9 septembre 2022
p('Contrôle 09/09/2022 (définition 1) :'); p(T1[T1.d=='2022-09-09'][['heure_ticket','rang2','id','m','a','b','c1','c2','nb','na']].to_string())
# sensibilité : la note ressaisie peut être close jusqu'à k minutes après la minute du vidage
for k in [1,2,5,10]:
    n=0; mt=0
    for d,t,x,m_,big in zip(T1.d,T1.t,T1.id,T1.m,T1.big):
        if big: continue
        g=ND.get(d); ok= g is not None and len(g[(g.id>x)&(g.t<=t+k)])>0
        if not ok: n+=1; mt+=m_
    p(f'Sensibilité définition 1 hors ≥ 1 000 € : (b) avec une tolérance de {k} min après le vidage : {n} tables ; {mt:.2f} €')
# témoin : tickets sans article sans DEL à leur minute (830)
Z2=H[(~H.dansC)].copy(); Z2['k']=list(zip(Z2.date_ticket,Z2.t)); Z2=Z2[~Z2.k.isin(dm.keys())]
w=[]
for d,t,x in zip(Z2.date_ticket,Z2.t,Z2.id):
    g=ND.get(d); w.append(g is None or len(g[(g.id>x)&(g.t<=t)])==0)
p(f'Témoin : tickets sans article sans DEL à leur minute : {len(Z2)} ; condition (b) : {sum(w)} ({np.mean(w)*100:.1f} %)')
