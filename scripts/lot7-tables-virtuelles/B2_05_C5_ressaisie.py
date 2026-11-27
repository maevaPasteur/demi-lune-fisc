"""C-5 : test de ressaisie différée. Pour chaque table vidée (définition 2, ticket = plus petit id de la minute), candidates = notes de la
première série du même Z, closes entre la minute du vidage et W minutes après (W = 60, 120, 240), d'identifiant supérieur au ticket vidé
(variante sans contrainte d'identifiant pour la comparaison au hasard). Inclusion : appariement sans remise (couplage biparti maximal) de
chaque ligne DEL positive à une ligne distincte d'UNE candidate dont le montant (pu × qte) ou le prix unitaire égale la ligne DEL ;
valeurs prises dans C, puis dans B (quantités commandées). Variantes : 2 ou 3 candidates mises en commun (W = 60) ; somme des DEL = total B
d'une candidate. Hasard : mêmes jeux de lignes appliqués aux notes des 1er, 2e, 3e, 5e et 8e jours d'ouverture suivants (même minute, sans
contrainte d'id). Sorties : out/B2/05.txt, 05_tables.csv, 05_0909.txt"""
import sys; sys.path.insert(0,"scripts/lot7-tables-virtuelles")
from B2_common import *
from itertools import combinations
C,E,F,H,A=load(); p=out2('05.txt')
Pop=pd.read_csv(OUT2+'04_tables.csv')
D=E[(E.typEven=='DEL')&(E.ac>0)]; dl=D.groupby(['dateEven','t']).ac.apply(lambda s: sorted(s.tolist()))
Pop['L']=[dl.get((d,t),[]) for d,t in zip(Pop.d,Pop.t)]
B=pd.read_pickle('scripts/lot3-quantites/cache/B.pkl'); B['ticket']=B.ticket.astype(int)
N=H[(H.serie==1)&(H.tc!=0)][['id','date_ticket','t','no_ticket','no_z_report','tc']].copy()
C['pc']=(C.pu*100).round().astype(int); C['lc']=(C.tot_lig*100).round().astype(int)
cl=C.groupby('id').apply(lambda g: [ {a,b} for a,b in zip(g.pc,g.lc)],include_groups=False)
B['pc']=(B.pu*100).round().astype(int); B['lc']=(B.tot*100).round().astype(int)
bl=B.groupby(['date','ticket']).apply(lambda g: [ {a,b} for a,b in zip(g.pc,g.lc)],include_groups=False)
bt=B.groupby(['date','ticket']).lc.sum()
N['Cl']=N.id.map(cl); N['Bl']=[bl.get((d,n)) for d,n in zip(N.date_ticket,N.no_ticket)]; N['Bt']=[bt.get((d,n),np.nan) for d,n in zip(N.date_ticket,N.no_ticket)]
ND={d:g for d,g in N.groupby('date_ticket')}
days=sorted(H.date_ticket.unique()); di={d:i for i,d in enumerate(days)}
def match(vals,lines):
    if not lines: return 0
    adj=[[j for j,s in enumerate(lines) if v in s] for v in vals]
    mt={}
    def aug(i,seen):
        for j in adj[i]:
            if j in seen: continue
            seen.add(j)
            if j not in mt or aug(mt[j],seen): mt[j]=i; return True
        return False
    return sum(aug(i,set()) for i in range(len(vals)))
def best(vals,cands,col):
    if not vals or len(cands)==0: return 0.0,0.0
    tot=sum(vals); bn=0; bm=0.0
    for lines in cands[col]:
        if lines is None: continue
        n=match(vals,lines)
        if n>bn: bn=n
    return bn/len(vals), bn
def table_test(vals,g,t,W,tid=None):
    if g is None: return dict(c_tot=0,c_80=0,b_tot=0,b_80=0,bsum=0)
    cand=g[(g.t>=t)&(g.t<=t+W)]
    if tid is not None: cand=cand[cand.id>tid]
    fc,_=best(vals,cand,'Cl'); fb,_=best(vals,cand,'Bl')
    return dict(c_tot=int(fc==1),c_80=int(fc>=0.8),b_tot=int(fb==1),b_80=int(fb>=0.8),bsum=int((cand.Bt==sum(vals)).any()) if vals else 0)
res=[]
for W in (60,120,240):
    for _,r in Pop.iterrows():
        g=ND.get(r.d); x=table_test(r.L,g,r.t,W,tid=r.tid); y=table_test(r.L,g,r.t,W)
        hz=[]
        for k in (1,2,3,5,8):
            j=di[r.d]+k
            if j<len(days): hz.append(table_test(r.L,ND.get(days[j]),r.t,W))
        hz={kk:np.mean([h[kk] for h in hz]) for kk in hz[0]} if hz else {}
        res.append(dict(W=W,table=r['N° de table'],cat=r['cat'],ex=r['ex'],V=r['V'],**{f'{k}':v for k,v in x.items()},**{f'{k}_sansid':v for k,v in y.items()},**{f'{k}_hasard':v for k,v in hz.items()}))
R=pd.DataFrame(res); R.to_csv(OUT2+'05_tables.csv',index=False)
for W in (60,120,240):
    p(f'\n=== Fenêtre {W} min après le vidage')
    for cat in ['a','b','c','reste','toutes']:
        s=R[(R.W==W)&((R.cat==cat) if cat!='toutes' else True)]
        for m,lab in [('c_tot','inclusion totale (C)'),('c_80','inclusion ≥ 80 % (C)'),('b_tot','inclusion totale (B)'),('bsum','somme DEL = total B d une candidate')]:
            obs=int(s[m].sum()); obs_s=int(s[m+'_sansid'].sum()); hz=s[m+'_hasard'].sum(); amt=s[s[m]==1].V.sum()/100; amt_h=(s[m+'_hasard']*s.V).sum()/100
            p(f'  [{cat}] {lab} : {obs} tables ({amt:.2f} €) ; sans contrainte d id {obs_s} ; hasard (autre jour, sans contrainte) {hz:.1f} ({amt_h:.2f} €) ; excès (sans contrainte − hasard) {obs_s-hz:.1f} tables, {(s[s[m+"_sansid"]==1].V.sum()/100)-amt_h:.2f} €')
    s=R[R.W==W]
    for ex,g in s.groupby('ex'): p(f'  exercice {ex} : inclusion totale C {int(g.c_tot.sum())} (sans id {int(g.c_tot_sansid.sum())}, hasard {g.c_tot_hasard.sum():.1f})')
# recouvrement avec les 133 conversions (157-R4) et les 146 égalités
import openpyxl
wb=openpyxl.load_workbook('scripts/lot7-tables-virtuelles/cache/entrees/lot27/157-R4-conversions-au-forfait-133-suites.xlsx',data_only=True,read_only=True)
rows=list(wb['Suites'].iter_rows(values_only=True)); Su=pd.DataFrame(rows[1:],columns=rows[0]); Su=Su[pd.to_numeric(Su['Suite n°'],errors='coerce').notna()]
conv=set(zip(pd.to_datetime(Su['Date']).dt.strftime('%Y-%m-%d'),Su['Minute'].map(tm)))
Pop['conv']=[(d,t) in conv for d,t in zip(Pop.d,Pop.t)]
eg=pd.read_csv(OUT2+'01_tables.csv')[['N° de table','egal_30']]; Pop2=Pop.merge(eg,on='N° de table')
s=R[R.W==240].merge(Pop2[['N° de table','conv','egal_30']],left_on='table',right_on='N° de table')
p(f'\nRecouvrement (W = 240, inclusion totale C) : tables incluses {int(s.c_tot.sum())} ; dont conversions 157-R4 {int((s.c_tot&s.conv).sum())} ; dont égalités au centime ± 30 min (146) {int((s.c_tot&s.egal_30).sum())}')
