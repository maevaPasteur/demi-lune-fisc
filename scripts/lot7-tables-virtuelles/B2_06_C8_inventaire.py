"""C-8 : inventaire des données disponibles pour une suppression ; nature du montant DEL ; écart de lignes B / C ;
contenu d'origine lisible dans B (notes partagées dont une note porte la table entière). Sorties : out/B2/06.txt"""
import sys; sys.path.insert(0,"scripts/lot7-tables-virtuelles")
from B2_common import *
from itertools import combinations
C,E,F,H,A=load(); S=source(); p=out2('06.txt'); G=pd.read_pickle(Q+'G.pkl')
B=pd.read_pickle('scripts/lot3-quantites/cache/B.pkl')
for nm,df in [('E',E),('H',H),('C',C),('B',B),('F',F),('G',G),('export natif',S)]:
    cols=[c for c in df.columns if c not in ('ligneXLS','ex','t','ac','tc','serie','dansC','libs','sy','pre','tail','k')]
    low={c:sorted(map(str,df[c].dropna().unique()))[:6] for c in cols if df[c].nunique()<=6}
    p(f'{nm} : {len(df)} lignes ; colonnes {cols}')
    if low: p(f'   colonnes à faible cardinalité : {low}')
# 2. nature du montant DEL
D=E[E.typEven=='DEL'].copy(); C['pc']=(C.pu*100).round().astype(int)
carte={ex:set(g[g.pc>0].pc) for ex,g in C.groupby('ex')}
def nature(ex,a):
    if a<=0: return 'nul ou négatif'
    if a>=100000: return '≥ 1 000 €'
    cs=carte[ex]
    if a in cs: return 'prix unitaire'
    if any(a%k==0 and a//k in cs for k in range(2,11)): return 'k × prix unitaire (k = 2 à 10)'
    if a*2 in cs: return '0,5 × prix unitaire'
    return 'aucun'
D['nat']=[nature(e,a) for e,a in zip(D.ex,D.ac)]
p('Nature du montant des 21 302 lignes DEL :',D.nat.value_counts().to_dict())
x=D[D.ac<=0]; p('   lignes nulles ou négatives :',len(x),' montant',x.ac.sum()/100,' ; négatives :',x[x.ac<0][['dateEven','heureEven','amount','no_zEport']].values.tolist())
# contrôle : en C, part des lignes à quantité ≠ 1 (si DEL = ligne d'article, on attendrait des multiples au même rythme)
q=C.qte; p(f'   pour comparaison, lignes C : quantité 1 {(q==1).mean()*100:.1f} % ; entière > 1 {((q>1)&(q%1==0)).mean()*100:.1f} % ; fractionnaire {(q%1!=0).mean()*100:.1f} %')
# 3. B contre C
B['ticket']=B.ticket.astype(int)
kb=B.groupby(['date','ticket']).size(); kc=C.groupby(['date','no']).size()
p(f'Lignes B {len(B)} ; C {len(C)} ; écart {len(C)-len(B)}')
onlyB=set(kb.index)-set(kc.index); onlyC=set(kc.index)-set(kb.index)
p(f'   couples (date, n°) de B absents de C : {len(onlyB)} ; de C absents de B : {len(onlyC)}')
s2=H[(H.serie==2)&(H.tc!=0)]; s2k=set(zip(s2.date_ticket,s2.no_ticket))
p(f'   lignes C des 17 tickets non nuls de seconde série : {int(C.id.isin(s2.id).sum())} ; lignes de B sur les couples (date, n°) partagés par ces tickets : {int(B.set_index(["date","ticket"]).index.isin(list(s2k)).sum())}')
both=kb.reindex(list(set(kb.index)&set(kc.index))); cc=kc.reindex(both.index)
p(f'   couples communs : {len(both)} ; nombre de lignes identique {int((both==cc).sum())} ; différent {int((both!=cc).sum())} ; somme des écarts (C − B) {int((cc-both).sum())}')
z0=H[(H.tc==0)&~H.dansC]; z0k=set(zip(z0.date_ticket,z0.no_ticket)); n1k=set(zip(H[H.serie==1].date_ticket,H[H.serie==1].no_ticket))
p(f'   couples (date, n°) de B qui ne correspondent qu à un ticket sans article (et à aucune note de première série) : {len([k for k in kb.index if k in z0k and k not in n1k])}')
# 4. notes partagées : groupes de B1 D-1, note portant la table entière dans B ; égalité du total B de la table entière avec une table vidée ± 30 min
sig=C.groupby('id').apply(lambda g: tuple(sorted(zip(g.libs,g.qte.round(4)))),include_groups=False)
fr=C.groupby('id').qte.apply(lambda s: ((s-s.round()).abs()>1e-9).any())
a=A.set_index('id'); a['sig']=sig; a['fr']=fr; a=a[a.fr].reset_index()
B['lc']=(B.tot*100).round().astype(int); B['libs']=B.lib.astype(str).str.strip()
bq=B.groupby(['date','ticket']).apply(lambda g: dict(zip(g.libs,g.qte)),include_groups=False); bt=B.groupby(['date','ticket']).lc.sum()
grp=[]
for (z_,s_),g in a.groupby(['z','sig']):
    if len(g)>=2 and g.t.max()-g.t.min()<=10: grp.append(g)
ent=0; ent_eq=0; ent_eq_h=[]
Pop=pd.read_csv(OUT2+'04_tables.csv'); PZ={z:g for z,g in Pop.groupby('z')}
days=sorted(H.date_ticket.unique()); di={d:i for i,d in enumerate(days)}; zday=H.groupby('date_ticket').no_z_report.agg(lambda s:s.mode()[0])
for g in grp:
    k=len(g); full=False; tot=None
    for d,n in zip(g.date,g.no):
        q=bq.get((d,n))
        if q is None: continue
        cq=C[C.id==g[g.no==n].id.iloc[0]].groupby('libs').qte.sum()
        if all(abs(q.get(l,0)-cq[l]*k)<1e-6 for l in cq.index): full=True; tot=bt[(d,n)]; break
    if full:
        ent+=1; t0=g.t.min(); z=g.z.iloc[0]
        pz=PZ.get(z); ent_eq+= int(pz is not None and ((pz.V==tot)&((pz.t-t0).abs()<=30)).any())
        hh=[]
        for kk in (1,2,3,5,8):
            j=di[g.date.iloc[0]]+kk
            if j<len(days):
                pz2=PZ.get(zday[days[j]]); hh.append(int(pz2 is not None and ((pz2.V==tot)&((pz2.t-t0).abs()<=30)).any()))
        ent_eq_h.append(np.mean(hh) if hh else 0)
p(f'Notes partagées (groupes de B1 D-1) : {len(grp)} ; groupes dont une note porte dans B la quantité de la table entière (k × quantité C de chaque article) : {ent} ; dont le total B de la table entière égale au centime une table vidée du même Z à ± 30 min : {ent_eq} ; attendu au hasard (autre jour, même minute) {sum(ent_eq_h):.1f}')
