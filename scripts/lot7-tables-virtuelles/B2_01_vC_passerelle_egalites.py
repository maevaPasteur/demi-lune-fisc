"""Version C (site, 26/11) : passerelle 2 449 tickets / 2 362 minutes / 2 359 tables ; recalcul indépendant du tableau 17
(146 tables égales au centime à 1 à 4 notes de la première série du même Z closes dans la fenêtre ; 4 notes seulement si la fenêtre
en compte 15 au plus) et du hasard (200 permutations des montants au sein de l'exercice, graine 20261123 ; même minute un autre jour
d'ouverture, décalages 1, 2, 3, 5, 8). Sorties : out/B2/01.txt, 01_tables.csv"""
import sys; sys.path.insert(0,"scripts/lot7-tables-virtuelles")
from B2_common import *
from itertools import combinations
C,E,F,H,A=load(); p=out2('01.txt')
Pop=sheet(F155,'Population'); Pop=Pop[pd.to_numeric(Pop['N° de table'],errors='coerce').notna()].copy()
Pop['d']=pd.to_datetime(Pop['Date']).dt.strftime('%Y-%m-%d'); Pop['t']=Pop['Minute du vidage'].map(tm); Pop['V']=(Pop['Montant'].astype(float)*100).round().astype(int)
Pop['tid']=Pop['Ticket à 0,00 € (id)'].astype(int); Pop['z']=Pop['Ticket Z'].astype(int)
p(f'Population 155-R3 version C : {len(Pop)} tables ; {Pop.V.sum()/100:.2f} € ; minutes distinctes {Pop[["d","t"]].drop_duplicates().shape[0]}')
# passerelle
D=E[E.typEven=='DEL']; Z=H[~H.dansC].copy(); dk=set(zip(D.dateEven,D.t)); Z['atm']=[(d,t) in dk for d,t in zip(Z.date_ticket,Z.t)]
Zm=Z[Z.atm]; mins=Zm.groupby(['date_ticket','t']).agg(n=('id','size'),ids=('id',lambda s: sorted(s))).reset_index()
Dmin=D.groupby(['dateEven','t']).agg(tot=('ac','sum'),pos=('ac',lambda s: s[s>0].sum()),mx=('ac','max'),neg=('ac',lambda s:(s<0).sum()),nl=('ac','size')).reset_index()
mins=mins.merge(Dmin,left_on=['date_ticket','t'],right_on=['dateEven','t'],how='left')
popk=set(zip(Pop.d,Pop.t)); mins['dans_2359']=[(d,t) in popk for d,t in zip(mins.date_ticket,mins.t)]
p(f'Tickets sans article à la minute d un DEL : {len(Zm)} ; minutes {len(mins)} ; minutes à plusieurs tickets {int((mins.n>1).sum())} (tickets en excédent {int((mins.n-1).sum())})')
ex=mins[~mins.dans_2359]
p('Minutes écartées par le lot 2.2 :'); p(ex[['date_ticket','t','n','ids','tot','pos','mx','neg']].assign(t=ex.t.map(lambda x:f'{x//60:02d}:{x%60:02d}')).to_string())
tidpop=set(Pop.tid); 
p(f'Ticket retenu par table (155 Population) : appartient aux tickets de sa minute pour {sum(t in set(i for l in mins.ids for i in l) for t in Pop.tid)} tables ; pour les minutes à plusieurs tickets, le ticket retenu est le plus petit id : {sum(1 for _,r in mins[mins.dans_2359&(mins.n>1)].iterrows() if min(r.ids) in tidpop)} / {int((mins.dans_2359&(mins.n>1)).sum())}')
p(f'Montant des 2 359 minutes recalculé sur E (lignes positives) : {mins[mins.dans_2359].pos.sum()/100:.2f} € ; total algébrique {mins[mins.dans_2359].tot.sum()/100:.2f} €')
# égalités
N=H[(H.serie==1)&(H.tc!=0)][['id','date_ticket','t','tc','no_z_report']]
NZ={z:(g.t.values,g.tc.values) for z,g in N.groupby('no_z_report')}
days=sorted(H.date_ticket.unique()); di={d:i for i,d in enumerate(days)}
zday=H.groupby('date_ticket').no_z_report.agg(lambda s: s.mode()[0])
WIN={'5 min avant':(-5,0),'30 min avant':(-30,0),'30 min après':(0,30),'30 min avant ou après':(-30,30)}
def sumset(z,t,a,b):
    if z not in NZ: return set(),set()
    tt,vv=NZ[z]; v=vv[(tt>=t+a)&(tt<=t+b)]; n=len(v); s1=set(); s2=set()
    s1|=set(v.tolist())
    for k in (2,3)+((4,) if n<=15 else ()):
        if n>=k:
            for c in combinations(v.tolist(),k): s2.add(sum(c))
    return s1,s2
rng=np.random.default_rng(SEED)
Pop['ex']=Pop.d.map(ex_of)
res={}
for w,(a,b) in WIN.items():
    S=[sumset(z,t,a,b) for z,t in zip(Pop.z,Pop.t)]
    hit=np.array([v in s1 or v in s2 for v,(s1,s2) in zip(Pop.V,S)]); multi=np.array([(v not in s1) and v in s2 for v,(s1,s2) in zip(Pop.V,S)])
    perm=[]
    for _ in range(200):
        V2=Pop.V.values.copy()
        for e in Pop.ex.unique():
            ix=np.where(Pop.ex.values==e)[0]; V2[ix]=rng.permutation(V2[ix])
        perm.append(sum(v in s1 or v in s2 for v,(s1,s2) in zip(V2,S)))
    oth=[]
    for k in (1,2,3,5,8):
        c=0
        for v,d,t in zip(Pop.V,Pop.d,Pop.t):
            j=di[d]+k
            if j<len(days):
                s1,s2=sumset(zday[days[j]],t,a,b); c+= v in s1 or v in s2
        oth.append(c)
    res[w]=(hit,multi)
    p(f'{w} : tables égales {hit.sum()} ; montant {Pop.V.values[hit].sum()/100:.2f} € ; dont deux notes ou plus {multi.sum()} ; permutations : moyenne {np.mean(perm):.2f}, max {max(perm)} ; excès {hit.sum()-np.mean(perm):.2f} ; autre jour {oth} (min {min(oth)}, max {max(oth)}) ; excès sur l autre jour [{hit.sum()-max(oth)} ; {hit.sum()-min(oth)}]')
Pop['egal_30']=res['30 min avant ou après'][0]
Pop[['N° de table','d','t','z','tid','V','ex','egal_30']].to_csv(OUT2+'01_tables.csv',index=False)
# comparaison avec Egalites_detail
Ed=sheet(F155,'Egalites_detail'); Ed=Ed[Ed['Fenêtre']=='30 min avant ou après']
p(f'Egalites_detail (30 min avant ou après) : {Ed["N° de table"].nunique()} tables ; recalcul : {Pop.egal_30.sum()} ; communes {len(set(Ed["N° de table"].astype(int))&set(Pop[Pop.egal_30]["N° de table"].astype(int)))}')
