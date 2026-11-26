"""C4 (règlements etat = 9 reportés ?) et C5 (soldes ronds des 37 tables). Placebos : ±1 à ±8 semaines (200 réplications) et permutation des montants ; graine 20261123."""
import pandas as pd, numpy as np, datetime as dt, itertools
from collections import defaultdict
from math import comb
CA='scripts/lot6-evenement-reglement/cache/'
e=lambda n:f"{n/100:,.2f}".replace(',',' ').replace('.',',')
c=lambda x:int(round(float(x)*100))
out=open('scripts/lot6-evenement-reglement/out/v02_C4_C5.txt','w')
def p(*a): print(*a); print(*a,file=out)
H=pd.read_pickle(CA+'H.pkl'); F=pd.read_pickle(CA+'F.pkl'); E=pd.read_pickle(CA+'E.pkl'); S=pd.read_pickle(CA+'SOURCE.pkl'); TB=pd.read_pickle(CA+'tables_videes_B.pkl')
CC=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/CC.pkl'); CC['tc']=CC.tot.map(c); CC['pu_c']=CC.pu.map(c)
Ht=H.set_index('id'); zday=H.groupby('date_ticket').no_z_report.first().to_dict()
S1=H[(H.serie==1)&(H.tot_ttc_c!=0)]
notes=defaultdict(list)
for r in S1.itertuples(): notes[r.date_ticket].append((r.id,r.t,r.tot_ttc_c))
pay=defaultdict(list)
for r in F.itertuples(): pay[r.id].append((r.mod_regl,r.montant_c))
z=F[F.tot_ttc_c==0].copy(); z['d']=z.id.map(Ht.date_ticket); z['t']=z.id.map(Ht.t)
def search(d,t,mode,amt,lo=-90,hi=150):
    return [i for i,tn,_ in notes.get(d,[]) if t+lo<=tn<=t+hi and (mode,amt) in pay[i]]
def run(rows):
    n=0;a=0
    for d,t,mode,amt in rows:
        if search(d,t,mode,amt): n+=1;a+=amt
    return n,a
base=list(zip(z.d,z.t,z.mod_regl,z.montant_c))
real=run(base)
# paires (somme de deux lignes d'une même note)
pairs=[]
for i,g in z.groupby('id'):
    L=list(zip(g.mod_regl,g.montant_c))
    for (m1,a1),(m2,a2) in itertools.combinations(L,2):
        if m1==m2: pairs.append((g.d.iloc[0],g.t.iloc[0],m1,a1+a2))
realp=run(pairs)
rng=np.random.default_rng(20261123)
P=[];PP=[]
for rep in range(200):
    sh=rng.choice([-8,-7,-6,-5,-4,-3,-2,-1,1,2,3,4,5,6,7,8],len(base))*7
    rows=[((dt.date.fromisoformat(d)+dt.timedelta(days=int(s))).isoformat(),t,m,a) for (d,t,m,a),s in zip(base,sh)]
    P.append(run(rows))
    perm=rng.permutation([a for _,_,_,a in base])
    PP.append(run([(d,t,m,a) for (d,t,m,_),a in zip(base,perm)]))
P=np.array(P);PP=np.array(PP)
p(f'== C4. 55 lignes etat = 9 : ligne de même mode et même montant sur une note de série 1 du même Z dans [t − 90 ; t + 150] : {real[0]} lignes, {e(real[1])}')
p(f'   placebo ±1-8 semaines : {P[:,0].mean():.2f} lignes (max {P[:,0].max()}), {e(P[:,1].mean())} ; montants permutés : {PP[:,0].mean():.2f} (max {PP[:,0].max()})')
p(f'   sommes de deux lignes etat = 9 de même mode sur une même note : {len(pairs)} paires ; retrouvées {realp[0]} ({e(realp[1])})')
det=[]
for d,t,m,a in base:
    s=search(d,t,m,a)
    if s: det.append((d,t,m,e(a),s))
p('   détail des lignes retrouvées :',det)
# 4. contenu de la table retrouvé sur la note candidate
DEL=E[(E.typEven=='DEL')&(E.amount_c<100000)]; dk=DEL.groupby(['dateEven','no_zEport','t']).amount_c.apply(list).to_dict()
lines=defaultdict(list)
for i,pu,tt in zip(CC.id,CC.pu_c,CC.tc): lines[i].append((pu,tt))
for d,t,m,a,s in det:
    i37=z[(z.d==d)&(z.t==t)].id.iloc[0]; amts=dk.get((d,Ht.no_z_report[i37],t),[])
    for cand in s:
        L=list(lines[cand]); got=0
        for x in amts:
            for j,(pu,tt) in enumerate(L):
                if x==pu or x==tt: got+=x; L.pop(j); break
        p(f'   note 0 € {i37} ({d} {t//60:02d}:{t%60:02d}) table {e(sum(amts))} → candidate {cand} (total {e(Ht.tot_ttc_c[cand])}) : contenu retrouvé {e(got)}')
S['idn']=S.id.astype(float).astype(int)
p('   (5) tot_sum natif des lignes etat 9 : série 2 (51,40 à 1 076,70) ; les candidates sont en série 1 : le compteur n\'enregistre aucun report (le ticket à 0 € n\'incrémente rien)')
# ---------- C5
p('\n== C5')
lin_amt=defaultdict(list)
for i,tt in zip(CC.id,CC.tc): lin_amt[i].append(tt)
cache={}
def subsums(i):
    if i in cache: return cache[i]
    L=lin_amt.get(i,[])
    if len(L)<=12:
        s={0}
        for x in L: s|={y+x for y in s}
    else:
        s={0}|set(L)|{a+b for a,b in itertools.combinations(L,2)}|{a+b+c_ for a,b,c_ in itertools.combinations(L,3)}
    s.discard(0); cache[i]=np.array(sorted(s)); return cache[i]
def found(d,t,dd):
    N=[i for i,tn,_ in notes.get(d,[]) if t-90<=tn<=t+150]
    arrs=[subsums(i) for i in N]
    for a in arrs:
        if dd in set(a.tolist()): return True
    for a,b in itertools.combinations(arrs,2):
        if np.isin(dd-a,b).any(): return True
    return False
rows=[]
for i,g in z.groupby('id'):
    d=g.d.iloc[0]; t=g.t.iloc[0]; V=sum(dk.get((d,Ht.no_z_report[i],t),[])); reg=g.montant_c.sum(); rows.append((i,d,t,V,reg,V-reg,'+'.join(sorted(set(g.mod_regl)))))
T=pd.DataFrame(rows,columns=['id','d','t','V','reg','dd','modes'])
T['f']=[found(d,t,dd) if dd>0 else False for d,t,dd in zip(T.d,T.t,T.dd)]
pl=[]
for rep in range(200):
    sh=rng.choice([-8,-7,-6,-5,-4,-3,-2,-1,1,2,3,4,5,6,7,8],len(T))*7; k=0
    for (d,t,dd),s in zip(zip(T.d,T.t,T.dd),sh):
        d2=(dt.date.fromisoformat(d)+dt.timedelta(days=int(s))).isoformat()
        if dd>0 and d2 in zday and found(d2,t,dd): k+=1
    pl.append(k)
p(f'(1-2) solde d retrouvé comme somme de lignes d\'une ou deux notes de série 1 (même Z, [t − 90 ; t + 150]) : {int(T.f.sum())} / {int((T.dd>0).sum())} ; placebo ±1-8 semaines : moyenne {np.mean(pl):.1f}, max {np.max(pl)} ; excès {T.f.sum()-np.mean(pl):.1f}')
p('   tables retrouvées :',T[T.f][['id','d','dd']].assign(dd=lambda x:x.dd.map(e)).values.tolist())
# 3. témoins
rd=T[T.dd>0]
p(f'(3) règlements etat 9 multiples de 10 € : {int((z.montant_c%1000==0).sum())}/55 ; soldes d multiples de 10 € : {int((rd.dd%1000==0).sum())}/{len(rd)} ; valeurs V des 2 361 tables multiples de 10 € : {(TB.V%1000==0).mean()*100:.2f} %')
multi=F[F.tot_ttc_c!=0].groupby('id').filter(lambda g:len(g)>=2)
g2=multi.groupby('id')
any10=g2.montant_c.apply(lambda s:(s%1000==0).any())
p(f'   notes de série 1 réglées en ≥ 2 lignes : {g2.ngroups} ; dont une ligne au moins multiple de 10 € : {any10.mean()*100:.2f} %')
# 5. témoin pertinent : total − une ligne multiple de 10 €
def partial(g):
    tot=g.tot_ttc_c.iloc[0]; return any(((tot-a)%1000==0) and tot-a>0 for a in g.montant_c)
pp=g2.apply(partial).mean()
k=int((rd.dd%1000==0).sum()); n=len(T)
pv=sum(comb(n,j)*pp**j*(1-pp)**(n-j) for j in range(k,n+1))
p(f'(5) témoin « règlement partiel » : part des notes à ≥ 2 lignes où total − une ligne est un multiple de 10 € : {pp*100:.2f} % ; P(≥ {k} sur {n}) = {pv:.2e}')
# 4. modes des 11 soldes ronds ; note de série 1 réglée CHV/TR > d
r10=T[(T.dd>0)&(T.dd%1000==0)]
for r in r10.itertuples():
    cand=[(i,[(m,a) for m,a in pay[i] if m in ('CHV','TR')]) for i,tn,_ in notes.get(r.d,[]) if r.t-90<=tn<=r.t+150]
    big=[i for i,L in cand if sum(a for m,a in L)>=r.dd]
    p(f'   {r.d} id {r.id} : solde {e(r.dd)} ; modes de la table {r.modes} ; notes de série 1 voisines réglées CHV/TR pour au moins le solde : {len(big)}')
out.close()
