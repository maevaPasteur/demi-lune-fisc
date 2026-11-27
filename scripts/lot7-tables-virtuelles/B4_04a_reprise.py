"""Reprise des tables vidées (règle du script B2_05_C5_ressaisie.py, inchangée), avec conservation du résultat de chacun des cinq décalages
(1, 2, 3, 5 et 8 jours d ouverture) pour l onglet « Reprise » de l annexe 175. Sortie : out/B4/04a_reprise.csv, out/B4/04a.txt.
Règle d origine : Pour chaque table vidée (définition 2, ticket = plus petit id de la minute), candidates = notes de la
première série du même Z, closes entre la minute du vidage et W minutes après (W = 60, 120, 240), d'identifiant supérieur au ticket vidé
(variante sans contrainte d'identifiant pour la comparaison au hasard). Inclusion : appariement sans remise (couplage biparti maximal) de
chaque ligne DEL positive à une ligne distincte d'UNE candidate dont le montant (pu × qte) ou le prix unitaire égale la ligne DEL ;
valeurs prises dans C, puis dans B (quantités commandées). Variantes : 2 ou 3 candidates mises en commun (W = 60) ; somme des DEL = total B
d'une candidate. Hasard : mêmes jeux de lignes appliqués aux notes des 1er, 2e, 3e, 5e et 8e jours d'ouverture suivants (même minute, sans
contrainte d'id). Sorties : out/B2/05.txt, 05_tables.csv, 05_0909.txt"""
import sys; sys.path.insert(0,"scripts/lot7-tables-virtuelles")
from B2_common import *
from itertools import combinations
C,E,F,H,A=load(); log=open(O+'B4/04a.txt','w')
def p(*a): print(*a); print(*a,file=log)
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
KS=(1,2,3,5,8)
for W in (60,120,240):
    for _,r in Pop.iterrows():
        g=ND.get(r.d); x=table_test(r.L,g,r.t,W,tid=r.tid); y=table_test(r.L,g,r.t,W)
        row=dict(W=W,table=r['N° de table'],cat=r['cat'],ex=r['ex'],V=r['V'],**{f'{k}':v for k,v in x.items()},**{f'{k}_sansid':v for k,v in y.items()})
        for k in KS:
            j=di[r.d]+k
            h=table_test(r.L,ND.get(days[j]),r.t,W) if j<len(days) else None
            for kk in ('c_tot','c_80','b_tot','b_80'):
                row[f'{kk}_d{k}']=np.nan if h is None else h[kk]
        res.append(row)
R=pd.DataFrame(res); R.to_csv(O+'B4/04a_reprise.csv',index=False)
R5=pd.read_csv(OUT2+'05_tables.csv')
for kk in ('c_tot','c_80','b_tot','b_80'):
    m=R[[f'{kk}_d{k}' for k in KS]].mean(axis=1)
    p(kk,'contrôle de la moyenne des décalages contre 05_tables.csv : écart max',float(np.nanmax(np.abs(m.values-R5[kk+"_hasard"].values))), "; NaN des deux côtés", int(m.isna().sum()), int(R5[kk+"_hasard"].isna().sum()),'; égalité des autres colonnes', bool((R[[kk,kk+'_sansid']].values==R5[[kk,kk+'_sansid']].values).all()))
s=R[R.W==240]; p('W=240 : avec id',int(s.c_tot.sum()),'sans id',int(s.c_tot_sansid.sum()),'hasard',round(s[[f"c_tot_d{k}" for k in KS]].mean(axis=1).sum(),1))
