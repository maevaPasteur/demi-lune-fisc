"""D-2 complément : sensibilité de l'excès au choix du placebo (30 réplications par variante, graine 20261123)."""
"""D-2 : robustesse du rattachement de l'annexe 155-R3 (onglet « Reprise », f = 11,7 %).
(a) f par critère, depuis les colonnes D à K de l'onglet (sommes non exclusives et affectation exclusive de l'annexe).
(b) Réimplémentation B des trois critères sur les fichiers primaires, puis placebo B : table déplacée de ±1 à ±8 semaines (même minute, Z du jour cible), 200 réplications, graine 20261123.
    (1) égalité au centime avec 1 à 3 notes de série 1 du même Z closes dans [t − 90 ; t + 150] ;
    (2) table entière : toutes les lignes DEL appariées une à une, au même prix (PU ou total de ligne), aux lignes d'une seule note de série 1 du même jour close avant le vidage ;
    (3) montant des lignes DEL appariées une à une, au même prix, à des lignes des notes de série 1 du même Z (journée entière).
(c) excès en euros et intervalle."""
import pandas as pd, numpy as np, openpyxl, datetime as dt
from collections import defaultdict
CA='scripts/lot6-evenement-reglement/cache/'
e=lambda n:f"{n/100:,.2f}".replace(',',' ').replace('.',',')
c=lambda x:int(round(float(x)*100))
out=open('scripts/lot6-evenement-reglement/out/u02b_sensibilite_placebo.txt','w')
def p(*a): print(*a); print(*a,file=out)
wb=openpyxl.load_workbook('public/documents/pieces-lot2/155-R3-tables-videes-traces-egalites-paiements-separes.xlsx',read_only=True,data_only=True)
R=pd.DataFrame([r for r in list(wb['Reprise'].iter_rows(values_only=True))[1:] if isinstance(r[0],(int,float)) and isinstance(r[1],(int,float))],
  columns=['no','M','lignes','c1','c2','c3','obs','a1','a2','a3','autre'])
Pop=pd.DataFrame(list(wb['Population'].iter_rows(values_only=True))[1:],columns=['no','ex','date','t','z','tz','n','M']); Pop=Pop[Pop.no.map(lambda x:isinstance(x,(int,float))) & Pop.t.map(lambda x:isinstance(x,str))]
DT=pd.DataFrame(list(wb['DEL_tables'].iter_rows(values_only=True))[1:],columns=['no','date','t','z','idE','a','f','l']); DT=DT[DT.no.map(lambda x:isinstance(x,(int,float)))&DT.a.map(lambda x:isinstance(x,(int,float)))]
M=R.M.sum()
p(f'== (a) Annexe 155, onglet Reprise : {len(R)} tables, {M:,.2f} €')
for k,(o,a) in {'(1) égalité':(R.M*R.c1,R.M*R.a1),'(2) table entière':(R.M*R.c2,R.M*R.a2),'(3) lignes au même prix':(R.c3,R.a3)}.items():
    O=o.sum()/M; A=a.sum()/M
    p(f'  {k} seul : observé {o.sum():,.2f} ({O:.2%}) ; autre jour {a.sum():,.2f} ({A:.2%}) ; excès {o.sum()-a.sum():,.2f} € ; f = {(O-A)/(1-A):.2%}')
O=R.obs.sum(); A=R.autre.sum()
p(f'  affectation exclusive (annexe) : observé {O:,.2f} ({O/M:.2%}) ; autre jour {A:,.2f} ({A/M:.2%}) ; excès {O-A:,.2f} € ({(O-A)/M:.2%}) ; f = {(O/M-A/M)/(1-A/M):.2%}')
# ---- (b) réimplémentation
H=pd.read_pickle(CA+'H.pkl'); CC=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/CC.pkl')
CC['pu_c']=CC.pu.map(c); CC['tot_c']=CC.tot.map(c)
S1=H[(H.serie==1)&(H.tot_ttc_c!=0)]
notes=defaultdict(list)   # (date) -> list (id, t, tot)
for r in S1.itertuples(): notes[r.date_ticket].append((r.id,r.t,r.tot_ttc_c))
lines=defaultdict(list)
for i,pu,tt in zip(CC.id,CC.pu_c,CC.tot_c): lines[i].append((pu,tt))
zday=H.groupby('date_ticket').no_z_report.first().to_dict()
Pop['d']=pd.to_datetime(Pop.date).dt.strftime('%Y-%m-%d'); Pop['tm']=Pop.t.map(lambda h:int(h[:2])*60+int(h[3:5]))
DT['a_c']=DT.a.map(c)
tabs={int(n):sorted(g.a_c.tolist()) for n,g in DT.groupby('no')}
Pop=Pop[Pop.no.isin(tabs)]
def match(amts,L):
    used=[False]*len(L); got=0
    for a in amts:
        for j,(pu,tt) in enumerate(L):
            if not used[j] and (a==pu or a==tt): used[j]=True; got+=a; break
    return got
def crit(d,t,amts,V):
    N=notes.get(d,[])
    x=np.array([tot for i,tn,tot in N if t-90<=tn<=t+150],dtype=np.int64)
    c1=False
    if len(x):
        if (x==V).any(): c1=True
        elif len(x)>1:
            s2=np.add.outer(x,x); iu=np.triu_indices(len(x),1)
            if (s2[iu]==V).any(): c1=True
            elif len(x)>2 and len(x)<=60:
                s3=s2[:,:,None]+x[None,None,:]; i,j,k=np.indices(s3.shape)
                if (s3[(i<j)&(j<k)]==V).any(): c1=True
    c2=False
    for i,tn,tot in N:
        if tn<t and match(amts,lines[i])==sum(amts): c2=True; break
    allL=[l for i,tn,tot in N for l in lines[i]]
    c3=match(amts,allL)
    return c1,c2,c3
rows=[]
for r in Pop.itertuples():
    amts=tabs[int(r.no)]; V=sum(amts); c1,c2,c3=crit(r.d,r.tm,amts,V)
    rows.append((int(r.no),V,c1,c2,c3))
B=pd.DataFrame(rows,columns=['no','V','c1','c2','c3']).merge(R[['no','c1','c2','c3']].rename(columns={'c1':'a_c1','c2':'a_c2','c3':'a_c3'}),on='no')
p(f'\n== (b) réimplémentation B : tables {len(B)} ; Σ V {e(B.V.sum())}')
p(f'  accord avec l\'annexe : (1) {int((B.c1==(B.a_c1==1)).sum())}/{len(B)} ; (2) {int((B.c2==(B.a_c2==1)).sum())}/{len(B)} ; (3) montants égaux au centime {int((B.c3==(B.a_c3*100).round().astype(int)).sum())}/{len(B)} ; Σ(3) B {e(B.c3.sum())} contre annexe {R.c3.sum():,.2f}')
def summ(df):
    o1=df.V[df.c1].sum(); o2=df.V[df.c2].sum(); o3=df.c3.sum()
    ex=np.where(df.c1,df.V,np.where(df.c2,df.V,df.c3)).sum()
    return o1,o2,o3,ex
real=summ(B)

days=sorted(zday); di={d:k for k,d in enumerate(days)}
popi=Pop.set_index('no')
def run(shifter,reps,lab):
    rng=np.random.default_rng(20261123); P=[]
    for rep in range(reps):
        rr=[]
        for no,V in zip(B.no,B.V):
            r=popi.loc[no]; d2=shifter(r.d,rng)
            if d2 is None or d2 not in zday: rr.append((V,False,False,0)); continue
            c1,c2,c3=crit(d2,r.tm,tabs[no],V); rr.append((V,c1,c2,c3))
        P.append(summ(pd.DataFrame(rr,columns=['V','c1','c2','c3'])))
    P=np.array(P); Mt=B.V.sum()
    for j,l in enumerate(['(1)','(2)','(3)','exclusive']):
        o=real[j]; a=P[:,j]; A_=a.mean()/Mt
        p(f'{lab} {l} : réel {o/Mt:.2%} ; placebo {A_:.2%} ; excès {e(o-a.mean())} [{e(o-np.percentile(a,97.5))} ; {e(o-np.percentile(a,2.5))}] ; f {(o/Mt-A_)/(1-A_):.2%}')
def wk(k):
    return lambda d,rng:(dt.date.fromisoformat(d)+dt.timedelta(days=int(rng.choice([-k,k])*7))).isoformat()
def od(lst):
    def f(d,rng):
        j=di[d]+int(rng.choice(lst)); return days[j] if 0<=j<len(days) else None
    return f
run(wk(1),30,'semaine ±1')
run(wk(2),30,'semaines ±2')
run(od([1,3,8]),30,'jours d\'ouverture +1/+3/+8 (règle 155)')
run(od([-8,-3,-1,1,3,8]),30,'jours d\'ouverture ±1/±3/±8')
out.close()
