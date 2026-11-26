"""C2 (identifiants manquants : mécanisme), C3 (borne par les modes ; profils), C6 (règlements mixtes et partie X). Graine 20261123."""
import pandas as pd, numpy as np
from collections import defaultdict, Counter
from scipy import stats
CA='scripts/lot6-evenement-reglement/cache/'
e=lambda n:f"{n/100:,.2f}".replace(',',' ').replace('.',',')
c=lambda x:int(round(float(x)*100))
out=open('scripts/lot6-evenement-reglement/out/v03_C2_C3_C6.txt','w')
def p(*a): print(*a); print(*a,file=out)
H=pd.read_pickle(CA+'H.pkl'); F=pd.read_pickle(CA+'F.pkl'); E=pd.read_pickle(CA+'E.pkl'); TB=pd.read_pickle(CA+'tables_videes_B.pkl')
CC=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/CC.pkl')
rng=np.random.default_rng(20261123)
# ---------------- C2
p('== C2')
DEL=E[E.typEven=='DEL']; nk=set(zip(H.date_ticket,H.no_z_report,H.t))
orph=DEL[[not any((d,z,t+x) in nk for x in range(-5,6)) for d,z,t in zip(DEL.dateEven,DEL.no_zEport,DEL.t)]]
Hs=H.sort_values('id').reset_index(drop=True); ids=Hs.id.values
miss=[]
for k in range(1,len(ids)):
    for m in range(ids[k-1]+1,ids[k]): miss.append((m,k))
W=[(m,k) for m,k in miss if Hs.date_ticket[k-1]==Hs.date_ticket[k]]
# (1) lignes portant le montant des orphelins dans les fenêtres
win=defaultdict(list)
for m,k in W:
    a=Hs.iloc[k-1]; b=Hs.iloc[k]; win[a.date_ticket].append((min(a.t,b.t)-30,max(a.t,b.t)+30))
inw=orph[[any(lo<=t<=hi for lo,hi in win.get(d,[])) for d,t in zip(orph.dateEven,orph.t)]]
p('  (1) orphelins dans les fenêtres :',len(inw),e(inw.amount_c.sum()),' ; lignes ≥ 1 000 € :',inw[inw.amount_c>=100000][['dateEven','heureEven','amount']].values.tolist(),' ; hors ≥ 1 000 € :',e(inw[inw.amount_c<100000].amount_c.sum()))
p('      montant placebo hors ≥ 1 000 € : voir u01 (moyenne 9 201,98 € toutes lignes) ; recalcul ci-dessous')
fracnotes=set(CC[(CC.qte-CC.qte.round()).abs()>1e-9].id)
z0=set(H[(H.tot_ttc_c==0)&(H.serie==2)].id)
rpr=set(zip(E[E.typEven=='RPR'].dateEven,E[E.typEven=='RPR'].no_zEport,E[E.typEven=='RPR'].t))
S1=H[(H.serie==1)&(H.tot_ttc_c!=0)]
eqn=set()
for (d,zz),g in S1.groupby(['date_ticket','no_z_report']):
    L=list(zip(g.id,g.t,g.tot_ttc_c))
    for i,t,v in L:
        if any(j!=i and v==w and abs(t-u)<=10 for j,u,w in L): eqn.add(i)
pos={i:k for k,i in enumerate(ids)}; H2=Hs.set_index('id')
def neigh(k):  # voisins présents id−3..id+3 autour du trou (indices k−1, k et au-delà)
    return [ids[j] for j in range(max(0,k-3),min(len(ids),k+3))]
tests={'note à quantité fractionnaire':lambda i:i in fracnotes,'ticket 0 € série 2':lambda i:i in z0,
 'RPR à la minute de clôture':lambda i:(H2.date_ticket[i],H2.no_z_report[i],H2.t[i]) in rpr,'note de total égal à une autre (±10 min)':lambda i:i in eqn}
byday=Hs.groupby('date_ticket').indices
need=Counter(Hs.date_ticket[k] for m,k in W)
for lab,fn in tests.items():
    real=np.mean([any(fn(i) for i in neigh(k)) for m,k in W])
    pl=[]
    for rep in range(300):
        ks=[]
        for d,n in need.items():
            cand=[j for j in byday[d] if j>0]; ks+=list(rng.choice(cand,min(n,len(cand)),replace=False))
        pl.append(np.mean([any(fn(i) for i in neigh(k)) for k in ks]))
    p(f'  (2-3) voisin (±3) {lab} : réel {real*100:.1f} % ; placebo {np.mean(pl)*100:.1f} % [{np.percentile(pl,2.5)*100:.1f} ; {np.percentile(pl,97.5)*100:.1f}]')
# (4) heure et jour de semaine
hh=pd.Series([Hs.t[k]//60 for m,k in W]).value_counts(normalize=True).sort_index()
hn=(S1.t//60).value_counts(normalize=True).sort_index()
p('  (4) heure de clôture du voisin suivant (part %) manquants / notes :',{int(h):(round(hh.get(h,0)*100,1),round(hn.get(h,0)*100,1)) for h in sorted(set(hh.index)|set(hn.index))})
wd=pd.Series([pd.Timestamp(Hs.date_ticket[k]).day_name()[:3] for m,k in W]).value_counts(normalize=True)
wn=pd.to_datetime(S1.date_ticket).dt.day_name().str[:3].value_counts(normalize=True)
p('      jour (part %) manquants / notes :',{d:(round(wd.get(d,0)*100,1),round(wn.get(d,0)*100,1)) for d in wn.index})
# (5) longueur du trou contre taille du groupe de partage voisin (notes fractionnaires du même Z à ±15 min du voisin)
gs=[]
for k in range(1,len(ids)):
    g=ids[k]-ids[k-1]-1
    if g>0 and Hs.date_ticket[k-1]==Hs.date_ticket[k]:
        a=Hs.iloc[k-1]
        n=int(((S1.date_ticket==a.date_ticket)&(S1.no_z_report==a.no_z_report)&((S1.t-a.t).abs()<=15)&S1.id.isin(fracnotes)).sum())
        gs.append((g,n))
G=pd.DataFrame(gs,columns=['trou','partage']); p('  (5) trous (même jour) :',len(G),' ; corrélation longueur / notes fractionnaires voisines',round(G.trou.corr(G.partage),3),' ; trou k et partage k+1 :',int((G.partage==G.trou+1).sum()))
p('      tableau croisé :',pd.crosstab(G.trou.clip(upper=4),G.partage.clip(upper=5)).to_dict())
# ---------------- C3
p('\n== C3')
z9=set(F[F.tot_ttc_c==0].id); Fn=F[~F.id.isin(z9)]
part={}
for ex,g in Fn.groupby('ex'):
    s=g.groupby('mod_regl').montant_c.sum(); part[ex]=s/s.sum()
    p(f'  (1) {ex} :',{m:(e(v),f'{v/s.sum()*100:.2f} %') for m,v in s.items()})
NR={'2022-2023':6464468,'2023-2024':5809610,'2024-2025':4868465}; dCB={'2022-2023':85989,'2023-2024':64040,'2024-2025':29086}
ESP={'2022-2023':379795,'2023-2024':819148,'2024-2025':534375}
for ex in NR:
    cb=part[ex]['CB']; p(f'  (2) {ex} : non rattaché {e(NR[ex])} × part CB {cb*100:.2f} % = {e(NR[ex]*cb)} contre 511210 − F CB {e(dCB[ex])} ; x maximal compatible {e(dCB[ex]/cb)}')
    p(f'  (3) {ex} : H1 espèces hors caisse : {e(NR[ex])} = {NR[ex]/ESP[ex]:.1f} fois les espèces enregistrées ; part des espèces dans (enregistré + hypothétique) {(ESP[ex]+NR[ex])/(Fn[Fn.ex==ex].montant_c.sum()+NR[ex])*100:.2f} % contre {part[ex]["ESP"]*100:.2f} %')
p('  limite : le lien entre 511210 et les remises bancaires CB n\'est pas établi sans grand livre ni télécollectes')
B1=pd.read_pickle(CA+'tables_videes_B.pkl')
mods=Fn.groupby('id').mod_regl.apply(lambda s:tuple(sorted(set(s)))); tot=Fn.groupby('id').montant_c.sum()
prof={'tables vidées (V)':B1.V.values}
for m in ['CB','ESP','CHV','TR']: prof[f'notes {m} seul']=tot[mods==(m,)].values
q=lambda a:[e(int(np.percentile(a,x))) for x in (10,25,50,75,90)]
for k,a in prof.items():
    ks=stats.ks_2samp(prof['tables vidées (V)'],a) if k!='tables vidées (V)' else None
    p(f'  (4) {k} : n {len(a)} ; quantiles 10/25/50/75/90 {q(a)}' + (f' ; KS D = {ks.statistic:.3f}, p = {ks.pvalue:.1e}' if ks else ''))
Ht=H.set_index('id')
def svc(t): return 'midi' if t<18*60 else 'soir'
p('  (5) service midi/soir : tables',pd.Series([svc(t) for t in B1.t]).value_counts(normalize=True).round(3).to_dict(),
  ' ; notes CB',pd.Series([svc(Ht.t[i]) for i in tot[mods==("CB",)].index]).value_counts(normalize=True).round(3).to_dict(),
  ' ; notes ESP',pd.Series([svc(Ht.t[i]) for i in tot[mods==("ESP",)].index]).value_counts(normalize=True).round(3).to_dict())
p('      jour : tables',pd.to_datetime(B1.d).dt.day_name().str[:3].value_counts(normalize=True).round(3).to_dict())
p('             notes ESP',pd.to_datetime(pd.Series([Ht.date_ticket[i] for i in tot[mods==("ESP",)].index])).dt.day_name().str[:3].value_counts(normalize=True).round(3).to_dict())
# ---------------- C6
p('\n== C6')
gap={'2022-2023':{'CB':85989,'CHQ':-68876+29000,'TR':-69419,'CHV':82599,'ESP':-46732},
     '2023-2024':{'CB':64040,'CHQ':-15173+52500,'TR':-198806,'CHV':702310,'ESP':-223258},
     '2024-2025':{'CB':29086,'CHQ':-10880+39000,'TR':-116685,'CHV':289534,'ESP':-253900}}
for ex,g in Fn.groupby('ex'):
    mm=g.groupby('id').mod_regl.apply(lambda s:'+'.join(sorted(set(s))))
    multi=mm[mm.str.contains(r'\+')]
    gg=g[g.id.isin(multi.index)].assign(comb=lambda x:x.id.map(mm))
    p(f'  {ex} : notes multi-modes {len(multi)} ; montant {e(gg.montant_c.sum())}')
    p('     par combinaison (n notes ; Σ par mode) :',{k:(int(v.id.nunique()),{m:e(a) for m,a in v.groupby("mod_regl").montant_c.sum().items()}) for k,v in gg.groupby('comb')})
    # règles : toute note comportant le mode X est portée en entier en X
    for X in ['CHV','TR','CB']:
        sim=defaultdict(int)
        for i,s in g.groupby('id'):
            ms=set(s.mod_regl)
            if X in ms and len(ms)>1: sim[X]+=s.montant_c.sum(); [sim.__setitem__(m,sim[m]-a) for m,a in zip(s.mod_regl,s.montant_c) if m!=X]; sim[X]-=s[s.mod_regl==X].montant_c.sum()
        res={m:gap[ex][m]-sim.get(m,0) for m in gap[ex]}
        p(f'     règle « toute note comportant {X} portée en {X} » : effet {dict((m,e(v)) for m,v in sim.items())} ; résidu par mode {dict((m,e(v)) for m,v in res.items())} ; Σ|résidu| {e(sum(abs(v) for v in res.values()))} contre Σ|écart| {e(sum(abs(v) for v in gap[ex].values()))}')
    ch=g[g.mod_regl=='CHV'].montant_c
    p(f'     CHV de F : multiples de 5 € {(ch%500==0).mean()*100:.1f} % ; de 10 € {(ch%1000==0).mean()*100:.1f} %')
out.close()
