"""Contrôles B-10, B-11, B-12, B-13, B-14, B-15 (seconde série, 37 notes, événements, DEL hors tables vidées, part non rattachée).
Définition (B, reproductible) : « table vidée » = groupe (date, Z, minute) où se clôture au moins un ticket à 0,00 € sans ligne
et où figure au moins un DEL ; valeur V = Σ des DEL du groupe (lignes ≥ 1 000 € exclues).
Rattachement : note de la série 1, même Z, clôturée dans [t − 90 ; t + 150] min, de total = V, ou k notes (2 ≤ k ≤ 4) de même total T avec k × T = V.
Placebo : chaque table déplacée d'un nombre de semaines tiré au hasard (±1 à ±8, graine 20261123), même heure, Z du jour cible ; 200 réplications."""
import pandas as pd, numpy as np, datetime as dt
from collections import defaultdict
CA='scripts/lot6-evenement-reglement/cache/'
c=lambda x:int(round(float(x)*100)); e=lambda n:f"{n/100:,.2f}".replace(',',' ').replace('.',',')
E=pd.read_pickle(CA+'E.pkl'); H=pd.read_pickle(CA+'H.pkl'); F=pd.read_pickle(CA+'F.pkl'); CC=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/CC.pkl')
out=open('scripts/lot6-evenement-reglement/out/t04_serie2_tables.txt','w')
def p(*a): print(*a); print(*a,file=out)
withl=set(CC.id)
Z0=H[(H.tot_ttc_c==0)&(~H.id.isin(withl))].copy()
DEL=E[E.typEven=='DEL']; DELn=DEL[DEL.amount_c<100000]
dmin=DELn.groupby(['dateEven','no_zEport','t']).amount_c.agg(['sum','size'])
dmin_all=DEL.groupby(['dateEven','no_zEport','t']).amount_c.agg(['sum','size'])
# ---------- B-10
p('== B-10 (a) numérotation quotidienne : n° de ticket répétés le même jour entre séries :',int(H.groupby(['date_ticket','no_ticket']).serie.nunique().gt(1).sum()),
  ' ; n° de série 2 commençant à 1 chaque jour :',int((H[H.serie==2].groupby('date_ticket').no_ticket.min()==1).sum()),'/',H[H.serie==2].date_ticket.nunique())
key=set(dmin_all.index)
Z0['at_del']=[(d,z,t) in key for d,z,t in zip(Z0.date_ticket,Z0.no_z_report,Z0.t)]
nd=Z0[~Z0.at_del]
p('(b) tickets à 0 € sans ligne',len(Z0),' ; clos à la minute d\'un DEL',int(Z0.at_del.sum()),' ; autres',len(nd))
dl=defaultdict(list)
for r in DEL.itertuples(): dl[(r.dateEven,r.no_zEport)].append(r.t)
ev=defaultdict(list)
for r in E[E.typEven.isin(['RPR','CON'])].itertuples(): ev[(r.dateEven,r.no_zEport)].append(r.t)
def near(L,t):
    if not L: return np.nan,np.nan
    a=np.array(L); bef=t-a[a<=t].max() if (a<=t).any() else np.nan; aft=a[a>=t].min()-t if (a>=t).any() else np.nan
    return bef,aft
rows=[(lambda b,a,b2,a2:(b,a,b2,a2))(*near(dl[(r.date_ticket,r.no_z_report)],r.t),*near(ev[(r.date_ticket,r.no_z_report)],r.t)) for r in nd.itertuples()]
R=pd.DataFrame(rows,columns=['DEL_avant','DEL_apres','RPRCON_avant','RPRCON_apres'])
R['DEL_proche']=R[['DEL_avant','DEL_apres']].min(axis=1)
bins=[-1,0,1,2,5,15,60,10**4]
p('   écart (min) au DEL le plus proche du même Z :',pd.cut(R.DEL_proche,bins).value_counts(sort=False).to_dict(),' ; sans DEL ce Z :',int(R.DEL_proche.isna().sum()))
p('   écart (min) au RPR/CON le plus proche :',pd.cut(R[['RPRCON_avant','RPRCON_apres']].min(axis=1),bins).value_counts(sort=False).to_dict())
p('   médianes : DEL avant',R.DEL_avant.median(),' DEL après',R.DEL_apres.median())
# (c) 17 tickets
s2=H[(H.serie==2)&(H.tot_ttc_c!=0)].copy()
lines=CC.assign(pu_c=CC.pu.map(c),q=CC.qte.map(lambda x:int(round(x*100)))).groupby('id').apply(lambda g:sorted(zip(g.ref,g.pu_c,g.q))).to_dict()
s1=H[(H.serie==1)&(H.tot_ttc_c!=0)]
s1_by=defaultdict(list)
for r in s1.itertuples(): s1_by[(r.date_ticket,r.no_z_report)].append((r.id,r.t,r.tot_ttc_c))
zday=H.groupby('date_ticket').no_z_report.first().to_dict()
from collections import Counter
def reprise(d,z,t,L):
    res=[]
    for i,tn,tot in s1_by.get((d,z),[]):
        if t<=tn<=t+150:
            Ci=Counter(lines.get(i,[])); Cs=Counter(L)
            if not (Cs-Ci): res.append(i)
    return res
p('(c) 17 tickets non nuls de la série 2 : reprise entière (toutes leurs lignes (réf., PU, Qté) contenues dans une note de série 1 du même Z clôturée dans [t ; t + 150] min) ; placebo jour + 7')
n_r=0;n_p=0;am_r=0
for r in s2.sort_values('id').itertuples():
    L=lines[r.id]; rp=reprise(r.date_ticket,r.no_z_report,r.t,L)
    d7=(dt.date.fromisoformat(r.date_ticket)+dt.timedelta(days=7)).isoformat(); pl=reprise(d7,zday.get(d7),r.t,L) if d7 in zday else []
    n_r+=bool(rp); n_p+=bool(pl); am_r+=r.tot_ttc_c if rp else 0
    p(f'   {r.date_ticket} {r.heure_ticket} id {r.id} n°{r.no_ticket} Z {r.no_z_report} TTC {e(r.tot_ttc_c)} TVA {r.tot_tva:.2f} lignes {len(L)} ; repris par {rp} ; placebo {pl}')
p(f'   repris en entier : {n_r} / 17 ({e(am_r)}) ; placebo : {n_p} / 17')
p('(d) tickets de série 2 portant un règlement F, hors les 37 :',int(F[F.id.isin(H[H.serie==2].id)&(F.tot_ttc_c!=0)].id.nunique()))
# ---------- B-11
p('\n== B-11. Les 37 notes à 0 € porteuses de règlements')
z37=F[F.tot_ttc_c==0]; Hi=H.set_index('id')
def eq_note(d,z,t,target):
    return [ (i,tn) for i,tn,tot in s1_by.get((d,z),[]) if t-90<=tn<=t+150 and tot==target]
rows=[]; rng=np.random.default_rng(20261123)
for i,g in z37.groupby('id'):
    h=Hi.loc[i]; k=(h.date_ticket,h.no_z_report,h.t)
    V=int(dmin.loc[k,'sum']) if k in dmin.index else 0; n=int(dmin.loc[k,'size']) if k in dmin.index else 0
    reg=int(g.montant_c.sum()); diff=V-reg
    m_reg=eq_note(*k,reg); m_diff=eq_note(*k,diff) if diff>0 else []
    d7=(dt.date.fromisoformat(h.date_ticket)+dt.timedelta(days=7)).isoformat()
    pl_reg=eq_note(d7,zday.get(d7),h.t,reg) if d7 in zday else []; pl_diff=eq_note(d7,zday.get(d7),h.t,diff) if (d7 in zday and diff>0) else []
    rows.append((h.ex,h.date_ticket,h.heure_ticket,i,int(h.no_ticket),n,e(V),' + '.join(f'{m} {e(v)}' for m,v in g.groupby('mod_regl').montant_c.sum().items()),e(reg),e(diff),len(m_reg),len(m_diff),len(pl_reg),len(pl_diff)))
T37=pd.DataFrame(rows,columns=['ex','date','heure','id','n°','DEL même minute','Σ DEL','règlements','Σ règl.','Σ DEL − Σ règl.','notes = règl.','notes = diff.','placebo = règl.','placebo = diff.'])
p(T37.to_string(index=False))
p('   notes avec DEL à la minute :',int((T37['DEL même minute']>0).sum()),'/37 ; Σ DEL = Σ règl. :',int((T37['Σ DEL − Σ règl.']=='0,00').sum()),
  ' ; note série 1 = diff. trouvée :',int((T37['notes = diff.']>0).sum()),' (placebo',int((T37['placebo = diff.']>0).sum()),') ; = règl. :',int((T37['notes = règl.']>0).sum()),' (placebo',int((T37['placebo = règl.']>0).sum()),')')
# ---------- B-12
p('\n== B-12. RPR, CON, TIR')
dk=set(zip(DEL.dateEven,DEL.no_zEport,DEL.t)); zk=set(zip(Z0.date_ticket,Z0.no_z_report,Z0.t)); nk=set(zip(H.date_ticket,H.no_z_report,H.t))
def within(S,d,z,t,w): return any((d,z,t+x) in S for x in range(-w,w+1))
for ty in ['RPR','CON','TIR']:
    x=E[E.typEven==ty]
    a=[(d,z,t) in dk for d,z,t in zip(x.dateEven,x.no_zEport,x.t)]; b=[(d,z,t) in zk for d,z,t in zip(x.dateEven,x.no_zEport,x.t)]; cc_=[(d,z,t) in nk for d,z,t in zip(x.dateEven,x.no_zEport,x.t)]
    a5=[within(dk,d,z,t,5) for d,z,t in zip(x.dateEven,x.no_zEport,x.t)]; b5=[within(zk,d,z,t,5) for d,z,t in zip(x.dateEven,x.no_zEport,x.t)]; c5=[within(nk,d,z,t,5) for d,z,t in zip(x.dateEven,x.no_zEport,x.t)]
    seq=sum(1 for d,z,t in zip(x.dateEven,x.no_zEport,x.t) if any((d,z,t+u) in dk and any((d,z,t+u+v) in zk for v in range(0,11-u)) for u in range(0,11)))
    p(f'  {ty} ({len(x)}) : même minute DEL {sum(a)} ; ticket à 0 € {sum(b)} ; clôture de note {sum(cc_)} ; ±5 min : DEL {sum(a5)} ; ticket à 0 € {sum(b5)} ; note {sum(c5)} ; suivis dans les 10 min d\'un DEL puis d\'un ticket à 0 € : {seq}')
p('  RPR par jour : min',E[E.typEven=='RPR'].groupby('dateEven').size().min(),' ; jours sans RPR',659-E[E.typEven=='RPR'].dateEven.nunique(),' ; heure médiane RPR',E[E.typEven=='RPR'].heureEven.median() if False else sorted(E[E.typEven=='RPR'].heureEven)[653])
p('  TIR :',E[E.typEven=='TIR'][['dateEven','heureEven','no_zEport','id']].values.tolist())
p('  DEL : caissier',DEL.caissier.value_counts().to_dict(),' caissier_droit',DEL.caissier_droit.value_counts().to_dict(),' ; caissier ≠ caissier_droit',int((DEL.caissier!=DEL.caissier_droit).sum()))
# ---------- B-13
p('\n== B-13. DEL hors tables vidées')
inT=[(d,z,t) in zk for d,z,t in zip(DEL.dateEven,DEL.no_zEport,DEL.t)]
D2=DEL[~np.array(inT)]; D1=DEL[np.array(inT)]
p(f'  DEL à la minute de clôture d\'un ticket à 0 € sans ligne : {len(D1)} ({e(D1.amount_c.sum())}) ; hors : {len(D2)} ({e(D2.amount_c.sum())}), hors lignes ≥ 1 000 € : {int((D2.amount_c<100000).sum())} ({e(D2[D2.amount_c<100000].amount_c.sum())})')
iso=[not within(nk,d,z,t,5) for d,z,t in zip(D2.dateEven,D2.no_zEport,D2.t)]
D3=D2[np.array(iso)]
p(f'  dont à une minute sans clôture de note ni de ticket à 0 € (même Z, ±5 min) : {len(D3)} ({e(D3.amount_c.sum())} ; hors ≥ 1 000 € {e(D3[D3.amount_c<100000].amount_c.sum())})')
p('  (le chiffre 12 991 suppose une autre définition des tables vidées ; voir 2.2 / annexe 155, absente)')
# ---------- B-14 / B-15 : tables
G_=[(k,int(v)) for k,v in dmin['sum'].items() if k in zk]
TB=pd.DataFrame([(d,z,t,v) for (d,z,t),v in G_],columns=['d','z','t','V'])
ex_of=lambda d:'2022-2023' if d<'2023-04-01' else ('2023-2024' if d<'2024-04-01' else '2024-2025')
TB['ex']=TB.d.map(ex_of)
p(f'\n== Tables vidées (définition B) : {len(TB)} groupes ; Σ V {e(TB.V.sum())} ; par exercice',{k:(int(g.shape[0]),e(g.V.sum())) for k,g in TB.groupby("ex")})
def rattache(d,z,t,V,lo=-90,hi=150):
    L=[tot for i,tn,tot in s1_by.get((d,z),[]) if t+lo<=tn<=t+hi]
    if V in L: return 1
    cnt=Counter(L)
    for T_,n in cnt.items():
        for k in range(2,5):
            if n>=k and k*T_==V: return k
    return 0
TB['r']=[rattache(d,z,t,v) for d,z,t,v in zip(TB.d,TB.z,TB.t,TB.V)]
lastnote={k:max(tn for _,tn,_ in L) for k,L in s1_by.items()}
TB['apres_derniere']=[t>lastnote.get((d,z),-1) for d,z,t in zip(TB.d,TB.z,TB.t)]
p('== B-14. Tables vidées après la dernière note de série 1 du Z :',int(TB.apres_derniere.sum()),' ; Σ V',e(TB[TB.apres_derniere].V.sum()),
  ' ; dont non rattachées par égalité dans [t − 90 ; t] :',int((TB.apres_derniere&(np.array([rattache(d,z,t,v,-90,0) for d,z,t,v in zip(TB.d,TB.z,TB.t,TB.V)])==0)).sum()))
days=sorted(zday)
real_n=int((TB.r>0).sum()); real_a=int(TB[TB.r>0].V.sum())
pn=[];pa=[]
for rep in range(200):
    sh=rng.choice([-8,-7,-6,-5,-4,-3,-2,-1,1,2,3,4,5,6,7,8],len(TB))*7
    n=0;a=0
    for (d,t,v),s in zip(zip(TB.d,TB.t,TB.V),sh):
        d2=(dt.date.fromisoformat(d)+dt.timedelta(days=int(s))).isoformat()
        if d2 in zday and rattache(d2,zday[d2],t,v): n+=1;a+=v
    pn.append(n);pa.append(a)
pn=np.array(pn);pa=np.array(pa)
p(f'== B-15. Rattachées (égalité au centime, 1 à 4 notes) : réel {real_n} tables, {e(real_a)} ; placebo (200 réplications) : moyenne {pn.mean():.1f} tables, {e(pa.mean())} ; '
  f'IC 95 % placebo [{e(np.percentile(pa,2.5))} ; {e(np.percentile(pa,97.5))}]')
exc=real_a-pa.mean(); lo=real_a-np.percentile(pa,97.5); hi=real_a-np.percentile(pa,2.5)
tot=TB.V.sum()
p(f'   rattaché au-delà du hasard : {e(exc)} [{e(lo)} ; {e(hi)}] soit {exc/tot*100:.1f} % [{lo/tot*100:.1f} ; {hi/tot*100:.1f}] de {e(tot)}')
p(f'   non rattaché : {e(tot-exc)} [{e(tot-hi)} ; {e(tot-lo)}]')
CAex={ex:H[(H.ex==ex)&(H.serie==1)].tot_ttc_c.sum() for ex in ['2022-2023','2023-2024','2024-2025']}
for ex,g in TB.groupby('ex'):
    ra=g[g.r>0].V.sum(); share=exc/real_a if real_a else 0
    p(f'   {ex} : Σ V {e(g.V.sum())} ; rattaché brut {e(ra)} ; non rattaché (brut) {e(g.V.sum()-ra)} = {(g.V.sum()-ra)/CAex[ex]*100:.2f} % du CA série 1 ; borne haute non rattaché corrigé du hasard ≈ {e(g.V.sum()-ra*(exc/real_a))} ({(g.V.sum()-ra*(exc/real_a))/CAex[ex]*100:.2f} %)')
TB.to_pickle(CA+'tables_videes_B.pkl')
out.close()
