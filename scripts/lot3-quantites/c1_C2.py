"""Les 63 cas de m2_Bc1.py (55 notes isolées et 8 tables à articles non refermés) : sorties cache/out/C2_*.csv.
Questions (a) à (g) : note d'origine vidée ? même Z ? jamais encaissé ? concordance journalière ; structure ; reliquat ; fréquence)."""
import os, sys, datetime as dt; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
from collections import defaultdict
rng=np.random.default_rng(20261123)
Cr,F,E,Fid,tabs,nd,A=load()
CC=pd.read_pickle(C+'CC.pkl'); H=pd.read_pickle(C+'H.pkl'); G=pd.read_pickle(C+'G.pkl'); H['id']=pd.to_numeric(H.id,errors='coerce')
Cn=CC.drop_duplicates('id').set_index('id')
D=E[E.typEven=='DEL'].copy(); Dd={d:g for d,g in D.groupby('dateEven')}
Z=H[H.tot_ttc==0]; Zd={d:g for d,g in Z.groupby('date_ticket')}
lines={i:g for i,g in Cr.groupby('id')}
frac_ids=set(Cr[Cr.fracC].id)
def mdel(d,t0,t1,amts,tol):
    g=Dd.get(d); out=[]
    if g is None: return [None]*len(amts)
    g=g[(g.t>=t0)&(g.t<=t1)]; used=set()
    for a in amts:
        c=[j for j in g.index[(g.amount-a).abs()<=tol] if j not in used]
        if c: used.add(c[0]); out.append(c[0])
        else: out.append(None)
    return out
cases=[]
iso=[x[0] for ex,d,x in tabs if len(x)==1]
for i in iso:
    L=lines[i]; d=L.date.iloc[0]; t=Fid.t[i]; m=mdel(d,t-5,t+30,list(L.tot),0.02)
    if any(x is None for x in m): continue
    cases.append(dict(type='note isolée',ex=L.ex.iloc[0],date=d,ids=[i],tnote=[t],dels=m,somme=round(D.loc[m].amount.sum(),2),paid=round(L.tot.sum(),2)))
for (ex,d,ids),g in A[~A.ref].groupby(['ex','date','ids']):
    comps=[round((math.ceil(r.somme-1e-9)-r.somme)*r.pu,2) for r in g.itertuples()]
    ts=[Fid.t[i] for i in ids]; m=[x for x in mdel(d,min(ts)-5,max(ts)+30,comps,0.05) if x is not None]
    cases.append(dict(type='résidu',ex=ex,date=d,ids=list(ids),tnote=ts,dels=m,somme=round(D.loc[m].amount.sum(),2),paid=None))
print('cas',len(cases),' Σ supprimé',round(sum(c['somme'] for c in cases),2))
# ---------- C2-a ticket à 0 € dans [1er DEL − 2 ; dernier DEL + 2]
def zsearch(d,t0,t1):
    z=Zd.get(d); 
    if z is None: return z
    return z[(z.t>=t0)&(z.t<=t1)]
used_no_day=defaultdict(set)
for r in Cn.itertuples(): used_no_day[r.date].add(r.ticket)
rows=[]
for c in cases:
    td=D.loc[c['dels']].t; z=zsearch(c['date'],td.min()-2,td.max()+2)
    n=0 if z is None else len(z)
    lt=0; miss=0; info=''
    if n:
        lt=int((z.id<min(c['ids'])).sum()); miss=int((~z.no.isin(used_no_day[c['date']])).sum())
        info=';'.join(f"id {int(r.id)} n°{r.no} {r.heure_ticket} Z{int(float(r.no_z_report))}" for r in z.itertuples())
    zn=set(D.loc[c['dels']].no_zEport.astype(int)); zc=set(Cn.loc[c['ids']].z.astype(int))
    rows.append(dict(type=c['type'],ex=c['ex'],date=c['date'],ref='+'.join(str(nd.tk[i]) for i in c['ids']),ids='+'.join(map(str,c['ids'])),
        heure_notes='/'.join(Fid.heure[i] for i in c['ids']),DEL=f"{int(td.min())//60:02d}:{int(td.min())%60:02d}-{int(td.max())//60:02d}:{int(td.max())%60:02d}",
        n_del=len(c['dels']),somme=c['somme'],ticket0=n,ticket0_id_inf=lt,ticket0_no_manquant=miss,ticket0_info=info,memeZ=zn==zc,Z_DEL='/'.join(map(str,sorted(zn))),Z_notes='/'.join(map(str,sorted(zc)))))
R=pd.DataFrame(rows); R.to_csv(OUT+'C2_cas.csv',index=False)
# témoin (note non fractionnaire du jour, fenêtre [t − 2 ; t + 2 + amplitude DEL du cas]) et placebo J+7 (même fenêtre horaire)
ctl=[]; plc=[]
for c,r in zip(cases,rows):
    td=D.loc[c['dels']].t; amp=int(td.max()-td.min())
    day=Cn[(Cn.date==c['date'])&~Cn.index.isin(frac_ids)&Cn.index.isin(Fid.index)]
    j=day.index[rng.integers(len(day))]; tj=Fid.t[j]
    z=zsearch(c['date'],tj-2,tj+2+amp); ctl.append((0 if z is None else len(z), 0 if z is None else int((z.id<j).sum())))
    d7=(dt.date.fromisoformat(c['date'])+dt.timedelta(days=7)).isoformat()
    z=zsearch(d7,td.min()-2,td.max()+2); plc.append(0 if z is None else len(z))
R['temoin_t0']=[x[0] for x in ctl]; R['placebo_t0']=plc
print('C2-a')
for ty in ['note isolée','résidu']:
    x=R[R.type==ty]; print(f'  {ty}: cas {len(x)} ; ticket à 0 € trouvé {(x.ticket0>0).sum()} ; dont id < id note {(x.ticket0_id_inf>0).sum()} ; n° hors des n° utilisés du jour {(x.ticket0_no_manquant>0).sum()} ; témoin {(x.temoin_t0>0).sum()} ; placebo J+7 {(x.placebo_t0>0).sum()}')
print('  total : cas',len(R),' trouvé',(R.ticket0>0).sum(),' id<',(R.ticket0_id_inf>0).sum(),' témoin',(R.temoin_t0>0).sum(),' placebo',(R.placebo_t0>0).sum())
print('C2-b : même Z (DEL = notes) :',R.memeZ.sum(),'/',len(R))
# ---------- C2-c : somme supprimée retrouvée en F (J-1..J+1), en G (tot_ttc de ticket, J-1..J+1), en C (note de même total, ou mêmes lignes) ; témoin
def found(d,somme,excl):
    ds=[(dt.date.fromisoformat(d)+dt.timedelta(days=k)).isoformat() for k in (-1,0,1)]
    f=F[F.dateTicket.isin(ds)&~F.id.isin(excl)]; g=G[G.dateTicket.isin(ds)].drop_duplicates(['dateTicket','noTicket','heureTicket'])
    c=Cn[Cn.date.isin(ds)&~Cn.index.isin(excl)]
    return int(((f.montant-somme).abs()<=0.02).any()), int(((g.tot_ttc-somme).abs()<=0.02).any()), int(((c.tot_ttc-somme).abs()<=0.02).any())
cc=[found(c['date'],c['somme'],c['ids']) for c in cases]
R['F_J1'],R['G_J1'],R['C_J1']=zip(*cc)
# lignes supprimées (une à une) dans C hors note : en proportion, avec placebo (mêmes montants)
print('C2-c : somme supprimée égale (±0,02) à : une ligne F J±1',R.F_J1.sum(),' un ticket G J±1',R.G_J1.sum(),' une note C J±1',R.C_J1.sum(),' (sur',len(R),')')
tc=[]
for c in cases:
    day=Cn[(Cn.date==c['date'])&~Cn.index.isin(frac_ids)]; j=day.index[rng.integers(len(day))]
    tc.append(found(c['date'],round(Cn.loc[j].tot_ttc,2),[j]))
tc=np.array(tc); print('  témoin (total d une note non fractionnaire du même jour) : F',tc[:,0].sum(),' G',tc[:,1].sum(),' C',tc[:,2].sum())
# ---------- C2-d concordance journalière
def daily(dates):
    out=[]
    for d in dates:
        c=Cn[Cn.date==d].tot_ttc.sum(); h=H[H.date_ticket==d].tot_ttc.sum()
        g=G[G.dateTicket==d].drop_duplicates(['noTicket','heureTicket','no_zReport']).tot_ttc.sum(); f=F[F.dateTicket==d].montant.sum()
        de=D[D.dateEven==d].amount.sum(); z0=(Z.date_ticket==d).sum()
        out.append(dict(date=d,C=round(c,2),H=round(h,2),G=round(g,2),F=round(f,2),DEL=round(de,2),tickets0=int(z0)))
    o=pd.DataFrame(out); o['C-H']=(o.C-o.H).round(2); o['C-G']=(o.C-o.G).round(2); o['F-C']=(o.F-o.C).round(2); return o
J=daily(sorted(set(R.date))); J.to_csv(OUT+'C2_journees.csv',index=False)
print('C2-d journées des 63 cas :',len(J),' C=H',(J['C-H'].abs()<0.005).sum(),' C=G',(J['C-G'].abs()<0.005).sum(),' F=C',(J['F-C'].abs()<0.005).sum()); print(J[(J['C-G'].abs()>0.005)|(J['F-C'].abs()>0.005)].to_string(index=False))
ALL=daily(sorted(set(Cn.date)))
print('  toutes journées :',len(ALL),' C=H',(ALL['C-H'].abs()<0.005).sum(),' C=G',(ALL['C-G'].abs()<0.005).sum(),' F=C',(ALL['F-C'].abs()<0.005).sum(),
      ' Σ(C−G)',round(ALL['C-G'].sum(),2),' Σ(F−C)',round(ALL['F-C'].sum(),2),' jours C≠G',(ALL['C-G'].abs()>0.005).sum(),' jours F≠C',(ALL['F-C'].abs()>0.005).sum())
ALL.to_csv(OUT+'C2_toutes_journees.csv',index=False)
# ---------- C2-e structure (55)
fp=[]; ratio=[]; ident=0
for c in cases:
    if c['type']!='note isolée': continue
    L=lines[c['ids'][0]]
    for q in L[L.fracC].qteC: fp.append(round(q-math.floor(q),2))
    ratio.append(round(c['paid']/(c['paid']+c['somme']),4))
    dels=D.loc[c['dels']]
    if len(dels)==len(L) and sorted((dels.amount*100).round())==sorted((L.tot*100).round()): ident+=1
fp=pd.Series(fp); rt=pd.Series(ratio)
print('C2-e fractions payées (partie décimale) :',fp.value_counts().to_dict())
print('  rapport payé / (payé + supprimé) :',rt.value_counts().sort_index().to_dict())
print('  miroir identique ligne à ligne (mêmes montants à ±0,02 €, même nombre) :',ident,'/ 55 ; à l égalité stricte au centime :',sum(1 for c in cases if c['type']=='note isolée' and sorted((D.loc[c['dels']].amount*100).round())==sorted((lines[c['ids'][0]].tot*100).round())))
# ---------- C2-f reliquat
def ht(L): return round((L.tot/(1+L.tva/100)).sum(),2)
CCx=CC.set_index('rowC')
def tva_lines(L): return CC[(CC.ex.isin(L.ex))&CC.rowC.isin(L.rowC)][['rowC','ex','tva']]
print('C2-f')
for d,tk in [('2023-04-12',14),('2024-08-01',6),('2022-10-23',17)]:
    i=Cn[(Cn.date==d)&(Cn.ticket==tk)].index[0]; L=lines[i].merge(tva_lines(lines[i]),on=['rowC','ex']); Lf=L[L.fracC]
    ceil=((np.ceil(Lf.qteC-1e-9)-Lf.qteC)*Lf.pu); eq=(Lf.pu*(1-Lf.qteC.mod(1))) ; 
    ceil_ht=(ceil/(1+Lf.tva/100)).sum(); eq_ht=(eq/(1+Lf.tva/100)).sum()
    print(f'  {d} n°{tk} (id {i}) lignes fract. {len(Lf)} : CEILING {ceil.sum():.2f} TTC / {ceil_ht:.2f} HT ; parts égales {eq.sum():.2f} TTC / {eq_ht:.2f} HT ; encaissé fract {Lf.tot.sum():.2f}')
    if d=='2022-10-23':
        m=mdel(d,Fid.t[i]-5,Fid.t[i]+30,list(L.tot),0.02); nm=L[[x is None for x in m]]
        print('     lignes non miroir :',nm[['lib_s','qteC','pu','tot']].values.tolist(),' complément parts égales des lignes fract. non miroir',round((nm[nm.fracC].pu*(1-nm[nm.fracC].qteC.mod(1))).sum(),2))
# 3 articles du résidu sans DEL
unm=[]
for (ex,d,ids),g in A[~A.ref].groupby(['ex','date','ids']):
    comps=[round((math.ceil(r.somme-1e-9)-r.somme)*r.pu,2) for r in g.itertuples()]
    ts=[Fid.t[i] for i in ids]; m=mdel(d,min(ts)-5,max(ts)+30,comps,0.05)
    for r,cmp_,x in zip(g.itertuples(),comps,m):
        if x is None: unm.append((d,r.lib,r.pu,r.somme,cmp_))
print('  résidu sans DEL :',unm,' Σ',round(sum(x[4] for x in unm),2))
compo=sum(round((math.ceil(r.somme-1e-9)-r.somme)*r.pu,2) for r in A[~A.ref].itertuples()); print('  Σ compléments arrondis à la ligne',round(compo,2),' ; Σ montants DEL appariés 246,01 ; 264,99 − 246,01 =',round(264.99-246.01,2))
# ---------- C2-g fréquence
R['mois']=R.date.str[:7]; R['service']=R.heure_notes.str[:2].astype(int).map(lambda h:'midi' if h<16 else 'soir')
tabm=pd.Series([d[:7] for ex,d,ids in tabs if len(ids)>=2]).value_counts()
M=R.groupby(['mois','type']).size().unstack(fill_value=0); M['tables_partagées']=tabm.reindex(M.index).fillna(0).astype(int)
print('C2-g par exercice et type :',R.groupby(['ex','type']).size().to_dict(),' service :',R.groupby(['type','service']).size().to_dict())
allm=pd.DataFrame({'tables':tabm}).join(R.groupby('mois').size().rename('cas')).fillna(0); allm['taux_%']=(allm.cas/(allm.tables+allm.cas)*100).round(1)
print(allm.sort_index().to_string()); allm.sort_index().to_csv(OUT+'C2_mois.csv')
print('taux global cas / (tables + cas) :',round(len(R)/(866+len(R))*100,2),'% ; par exercice',{ex:round((R.ex==ex).sum()/(((R.ex==ex).sum())+sum(1 for e,d,i in tabs if len(i)>=2 and e==ex))*100,2) for ex in EX})
R.to_csv(OUT+'C2_cas.csv',index=False)
