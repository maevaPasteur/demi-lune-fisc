"""C-4 : profil des tables vidées par catégorie chronologique de B1 D-2 (définition 2 : 2 359 tables, 155-R3 version C, ticket = plus petit
id de la minute ; définition 1 en contrôle). Catégories : (a) aucune note encaissée close au plus tard à la minute ; (b-a) séquence attestée
impossible mais note antérieure existante ; (c) aucune séquence ; reste (séquence attestée possible) ; témoin : notes encaissées.
Sorties : out/B2/04.txt, 04_tables.csv"""
import sys; sys.path.insert(0,"scripts/lot7-tables-virtuelles")
from B2_common import *
C,E,F,H,A=load(); p=out2('04.txt'); P=plats()
Pop=pd.read_csv(OUT2+'01_tables.csv')
D=E[(E.typEven=='DEL')]
N=H[(H.serie==1)&(H.tc!=0)][['date_ticket','t','id','tc','no_z_report']]; ND={d:g for d,g in N.groupby('date_ticket')}
def cat(d,t,x):
    g=ND.get(d)
    if g is None: return 'a'
    bef=g[g.t<=t]
    if len(bef)==0: return 'a'
    if len(bef[bef.id>x])==0:
        if len(g[g.t>=t])==0: return 'c'
        return 'b'
    return 'reste'
Pop['cat']=[cat(d,t,x) for d,t,x in zip(Pop.d,Pop.t,Pop.tid)]
# (c) au sens B1 : (b) et aucune note close à la minute ou après -> déjà isolé ; (a) est prioritaire sur (c)
p('Effectifs (définition 2) :',Pop.cat.value_counts().to_dict(),' ; montants :',Pop.groupby('cat').V.sum().div(100).round(2).to_dict())
# lignes DEL par table
Dpos=D[D.ac>0]; dl=Dpos.groupby(['dateEven','t']).ac.apply(list)
Pop['lignes']=[dl.get((d,t),[]) for d,t in zip(Pop.d,Pop.t)]
Pop['nl']=Pop.lignes.map(len)
# nature des prix
Lg=pd.read_pickle('scripts/lot5-tva/cache/B3_articles.pkl'); nat=dict(zip(Lg.ref.astype(str),Lg.nature))
C['ref']=C.ref.astype(str); C['nat']=C.ref.map(nat); C['pc']=(C.pu*100).round().astype(int)
def kind(s):
    if s<=P: return 'plats_menus'
    return None
pr={}
for ex,g in C[C.pc>0].groupby('ex'):
    for pc,gg in g.groupby('pc'):
        libs=set(gg.libs); nats=set(gg.nat.dropna())
        drink=all('boisson' in n or 'bière' in n for n in nats) and len(nats)>0
        plat=libs<=P
        pr[(ex,pc)]='boisson' if drink else ('plat ou menu' if plat else 'mixte ou autre aliment')
def lines_profile(sub):
    allp=[(ex,a) for ex,ls in zip(sub.ex,sub.lignes) for a in ls]
    k=pd.Series([pr.get(x,'hors carte') for x in allp]).value_counts(normalize=True).mul(100).round(1).to_dict()
    return len(allp),k
def bins(n): return '1' if n==1 else ('2' if n==2 else ('3' if n==3 else ('4 à 6' if n<=6 else '7 et plus')))
CON=E[E.typEven=='CON'][['no_zEport','t']]; CZ={z:g.t.values for z,g in CON.groupby('no_zEport')}
def since_con(z,t):
    v=CZ.get(z); 
    if v is None: return np.nan
    v=v[v<=t]; return t-v.max() if len(v) else np.nan
first_day=N.groupby('date_ticket').t.min()
def first_svc(d,t):
    g=ND.get(d)
    if g is None: return np.nan
    g2=g[(g.t>=t)&((g.t<1080)==(t<1080))]; return g2.t.min()-t if len(g2) else np.nan
Pop['vers_1re_note_jour']=[first_day.get(d,np.nan)-t for d,t in zip(Pop.d,Pop.t)]
Pop['vers_1re_note_service']=[first_svc(d,t) for d,t in zip(Pop.d,Pop.t)]
Pop['depuis_CON']=[since_con(z,t) for z,t in zip(Pop.z,Pop.t)]
rk=H.set_index('id').no_ticket; Pop['rang2']=Pop.tid.map(rk)
for c in ['a','b','c','reste']:
    s=Pop[Pop.cat==c]
    if not len(s): continue
    nl,k=lines_profile(s)
    p(f'\n[{c}] tables {len(s)} ; montant {s.V.sum()/100:.2f} € ; médiane {s.V.median()/100:.2f} € (Q1 {s.V.quantile(.25)/100:.2f} ; Q3 {s.V.quantile(.75)/100:.2f})')
    p(f'   lignes DEL par table : {s.nl.map(bins).value_counts().reindex(["1","2","3","4 à 6","7 et plus"]).fillna(0).astype(int).to_dict()} ; lignes {nl} ; nature du prix : {k}')
    p(f'   heure du vidage : avant 10 h {int((s.t<600).sum())} ; 10-12 h {int(((s.t>=600)&(s.t<720)).sum())} ; 12-14 h {int(((s.t>=720)&(s.t<840)).sum())} ; 14-18 h {int(((s.t>=840)&(s.t<1080)).sum())} ; 18-20 h {int(((s.t>=1080)&(s.t<1200)).sum())} ; 20 h et après {int((s.t>=1200).sum())}')
    p(f'   délai jusqu à la première note du jour (min, médiane) {s.vers_1re_note_jour.median():.0f} ; jusqu à la première note du même service (médiane) {s.vers_1re_note_service.median():.0f} ; rang en seconde série (médiane) {s.rang2.median():.0f} ; rang 1 : {int((s.rang2==1).sum())}')
    p(f'   depuis le dernier CON du Z (médiane) {s.depuis_CON.median():.0f} min ; dans les 30 min après un CON : {int((s.depuis_CON<=30).sum())} ({(s.depuis_CON<=30).mean()*100:.1f} %)')
    p(f'   tables par journée : journées {s.d.nunique()} ; journées à plusieurs tables {int((s.d.value_counts()>1).sum())}')
    one=s[s.nl==1]; p(f'   une seule ligne DEL (profil « article retiré ») : {len(one)} ({one.V.sum()/100:.2f} €)')
# témoin : notes encaissées
N['depuis_CON']=[since_con(z,t) for z,t in zip(N.no_z_report,N.t)]
p(f'\n[témoin notes encaissées] {len(N)} ; avant 10 h {int((N.t<600).sum())} ({(N.t<600).mean()*100:.2f} %) ; dans les 30 min après un CON {(N.depuis_CON<=30).mean()*100:.1f} % ; médiane depuis CON {N.depuis_CON.median():.0f} min')
# (c) une par une
c=Pop[Pop.cat=='c']
p('\n[c] une par une :')
for _,r in c.iterrows():
    g=ND.get(r.d); last=g.sort_values('t').iloc[-1]
    low=g[(g.id<r.tid)&(g.t<=r.t)]
    nxt=[dd for dd in sorted(ND) if dd>r.d][0]; gn=ND[nxt].sort_values('t').iloc[0]
    art=C[C.id==gn.id][['libs','qte']].values.tolist()
    p(f'   {r.d} {int(r.t)//60:02d}:{int(r.t)%60:02d} id {r.tid} {r.V/100:.2f} € {r.nl} lignes ; dernière note du jour {int(last.t)//60:02d}:{int(last.t)%60:02d} id {last.id} ; notes d id inférieur closes avant : {len(low)} ; jour suivant {nxt} 1re note {int(gn.t)//60:02d}:{int(gn.t)%60:02d} id {gn.id} {gn.tc/100:.2f} € {art}')
# contrôle définition 1
Z=H[~H.dansC]; dk=set(zip(D.dateEven,D.t)); Z1=Z[[ (d,t) in dk for d,t in zip(Z.date_ticket,Z.t)]]
c1=pd.Series([cat(d,t,x) for d,t,x in zip(Z1.date_ticket,Z1.t,Z1.id)]).value_counts().to_dict()
p('\nContrôle définition 1 (2 449 tickets, brut) :',c1)
Pop.drop(columns=['lignes']).to_csv(OUT2+'04_tables.csv',index=False)
