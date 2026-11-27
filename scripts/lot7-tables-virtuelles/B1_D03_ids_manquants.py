"""D-3 : identifiants de note absents de H (plage 46 621 à 67 681), encadrement, répartition, rapprochement avec les DEL
« orphelins », contre-épreuve par tirage (graine 20261123), hypothèse d'identifiants consommés par d'autres objets (sy_uk),
voisinage des partages, notes closes un jour ultérieur. Sorties : out/B1/D03.txt, D03_manquants.csv, D03_multijours.csv"""
import sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from B1_common import *
C,E,F,H,A=load(); S=source(); S['id']=S.id.astype(int); p=out('D03.txt')
G=pd.read_pickle(Q+'G.pkl')
p('colonnes G :',list(G.columns)[:12],' (aucune colonne d identifiant de note)')
ids=set(H.id); lo,hi=min(ids),max(ids); miss=sorted(set(range(lo,hi+1))-ids)
p(f'H : id {lo} à {hi} ({hi-lo+1} valeurs) ; tickets {len(ids)} ; absents {len(miss)}')
p('  absents présents dans C :',len(set(miss)&set(C.id)),' ; F :',len(set(miss)&set(F.id)),' ; export natif :',len(set(miss)&set(S.id)))
# sauts
runs=[]; cur=[miss[0]]
for x in miss[1:]:
    if x==cur[-1]+1: cur.append(x)
    else: runs.append(cur); cur=[x]
runs.append(cur); L=pd.Series([len(r) for r in runs])
p(f'  sauts : {len(runs)} ; longueur : {L.value_counts().sort_index().to_dict()}')
Hs=H.set_index('id').sort_index(); hid=Hs.index.values
rows=[]
for r in runs:
    a,b=r[0]-1,r[-1]+1
    pa=Hs.loc[a]; pb=Hs.loc[b]
    for x in r:
        rows.append(dict(id=x,run=len(r),prev=a,prev_date=pa.date_ticket,prev_h=pa.heure_ticket,prev_serie=int(pa.serie),prev_tot=pa.tot_ttc,
                         next=b,next_date=pb.date_ticket,next_h=pb.heure_ticket,next_serie=int(pb.serie),next_tot=pb.tot_ttc))
M=pd.DataFrame(rows); M['intra']=M.prev_date==M.next_date
M['ex']=M.prev_date.map(ex_of)
def svc(r):
    if not r.intra: return 'à cheval'
    t1,t2=tm(r.prev_h),tm(r.next_h)
    if max(t1,t2)<18*60: return 'midi'
    if min(t1,t2)>=18*60: return 'soir'
    return 'midi/soir'
M['service']=M.apply(svc,axis=1)
p(f'  intra-journée {int(M.intra.sum())} ; à cheval sur deux journées {int((~M.intra).sum())}')
p('  par exercice (date du précédent) :',M.ex.value_counts().sort_index().to_dict())
p('  par service :',M.service.value_counts().to_dict())
M['mois']=M.prev_date.str[5:7]; M['jsem']=pd.to_datetime(M.prev_date).dt.dayofweek
nd=A.groupby(A.date.str[5:7]).size()
p('  par mois (manquants / 1 000 notes) :',{m:round(c/nd[m]*1000,1) for m,c in M.mois.value_counts().sort_index().items()})
ndw=A.groupby(pd.to_datetime(A.date).dt.dayofweek).size()
p('  par jour de semaine 0=lundi (manquants / 1 000 notes) :',{d:round(c/ndw[d]*1000,1) for d,c in M.jsem.value_counts().sort_index().items()})
p('  série des voisins (précédent, suivant) :',M.groupby(['prev_serie','next_serie']).size().to_dict())
# -- sy_uk : les identifiants manquants avancent-ils le compteur ?
u=S.drop_duplicates('id').sort_values('id').copy(); u['k']=u['tail']//1000; u['base']=u.id-u.k
sess=u.groupby('pre').agg(idmin=('id','min'),idmax=('id','max'),nb=('base','nunique'))
def sess_of(x):
    s=sess[(sess.idmin<=x)&(sess.idmax>=x)]; return s.index[0] if len(s) else None
M['session']=M.id.map(sess_of)
inside=M[M.session.notna()]
p(f'  manquants situés à l intérieur d une session sy_uk (entre deux notes de même préfixe) : {len(inside)} ; hors session (entre deux préfixes) : {len(M)-len(inside)}')
# pour chaque couple de notes consécutives de l'export d'une même session : écart d'id vs écart k
u['did']=u.id.diff(); u['dk']=u.k.diff(); u['same']=u.pre.diff()==0
w=u[u.same]
p(f'  couples consécutifs de l export dans une même session : {len(w)} ; dk = did : {int((w.dk==w.did).sum())} ; dk < did : {int((w.dk<w.did).sum())} ; dk > did : {int((w.dk>w.did).sum())}')
# combien de manquants sont « comptés » par le compteur (dk = did sur le couple qui les encadre dans l'export)
cnt_ok=0; cnt_no=0
uu=u.set_index('id')
for x in miss:
    prv=u[u.id<x].tail(1); nxt=u[u.id>x].head(1)
    if len(prv) and len(nxt) and prv.pre.iloc[0]==nxt.pre.iloc[0]:
        if nxt.k.iloc[0]-prv.k.iloc[0]==nxt.id.iloc[0]-prv.id.iloc[0]: cnt_ok+=1
        else: cnt_no+=1
p(f'  manquants encadrés dans l export par deux notes de la même session : compteur avancé d autant que l id {cnt_ok} ; non {cnt_no}')
# changements de session : saut d'id au démarrage ?
first=u[~u.same]; 
p('  premier id de chaque session moins dernier id de la session précédente (toutes notes H) :')
gaps=[]
for _,r in first.iloc[1:].iterrows():
    prevH=hid[hid<r.id]; gaps.append(r.id-prevH.max() if len(prevH) else None)
p('   ',pd.Series(gaps).value_counts().sort_index().head(8).to_dict())
# -- rapprochement avec E : DEL orphelins
D=E[E.typEven=='DEL'].copy()
closeH=set(zip(H.date_ticket,H.t))
D['orph']=[(d,t) not in closeH for d,t in zip(D.dateEven,D.t)]
D['orph1']=[all((d,t+k) not in closeH for k in (-1,0,1)) for d,t in zip(D.dateEven,D.t)]
Dm=D.groupby(['dateEven','t']).agg(n=('ac','size'),m=('ac','sum'),orph=('orph','first'),orph1=('orph1','first'),big=('ac',lambda s:(s>=100000).any())).reset_index()
p(f'  rafales DEL (date, minute) : {len(Dm)} ; orphelines (aucun ticket H clos à la minute) : {int(Dm.orph.sum())} pour {Dm[Dm.orph].m.sum()/100:.2f} € ({Dm[Dm.orph&~Dm.big].m.sum()/100:.2f} € hors lignes ≥ 1 000 €) ; orphelines à ± 1 min : {int(Dm.orph1.sum())}')
# fenêtres
Mi=M[M.intra].copy(); Mi['t1']=Mi[['prev_h','next_h']].map(tm).min(axis=1)-30; Mi['t2']=Mi[['prev_h','next_h']].map(tm).max(axis=1)+30
ORPH={d:(g.t.values,g.m.values) for d,g in Dm[Dm.orph&~Dm.big].groupby('dateEven')}
def score(win):  # win : DataFrame date,t1,t2 ; union des fenêtres par jour
    tot=0; mt=0
    for d,t1,t2 in zip(win.date.values,win.t1.values,win.t2.values):
        pass
    for d,g in win.groupby('date',sort=False):
        if d not in ORPH: continue
        tt,mm=ORPH[d]; mask=np.zeros(len(tt),bool)
        for a,b in zip(g.t1.values,g.t2.values): mask|=(tt>=a)&(tt<=b)
        tot+=mask.sum(); mt+=mm[mask].sum()
    return tot,mt/100
real=score(Mi.rename(columns={'prev_date':'date'})[['date','t1','t2']])
# placebo : ids présents du même jour, dont précédent et suivant sont du même jour
Hd=H.sort_values('id').reset_index(drop=True); Hd['pd']=Hd.date_ticket.shift(); Hd['nd']=Hd.date_ticket.shift(-1); Hd['ph']=Hd.t.shift(); Hd['nh']=Hd.t.shift(-1)
cand=Hd[(Hd.pd==Hd.date_ticket)&(Hd.nd==Hd.date_ticket)]
need=Mi.groupby('prev_date').size()
rng=np.random.default_rng(SEED); res=[]
cg={d:g for d,g in cand.groupby('date_ticket')}
CGA={d:(np.minimum(g.ph.values,g.nh.values).astype(int)-30,np.maximum(g.ph.values,g.nh.values).astype(int)+30) for d,g in cg.items()}
for it in range(1000):
    tot=0; mt=0
    for d,k in need.items():
        a1,a2=CGA[d]; sel=rng.choice(len(a1),size=min(k,len(a1)),replace=False)
        if d not in ORPH: continue
        tt,mm=ORPH[d]; mask=np.zeros(len(tt),bool)
        for a,b in zip(a1[sel],a2[sel]): mask|=(tt>=a)&(tt<=b)
        tot+=mask.sum(); mt+=mm[mask].sum()
    res.append((tot,mt/100))
R=np.array(res)
p(f'  rafales orphelines (hors ≥ 1 000 €) dans les fenêtres des {len(Mi)} manquants intra-journée [± 30 min autour des voisins] : {real[0]} ({real[1]:.2f} €) ; tirage (1 000, graine {SEED}) : moyenne {R[:,0].mean():.1f} [{np.percentile(R[:,0],2.5):.0f} ; {np.percentile(R[:,0],97.5):.0f}], montant {R[:,1].mean():.2f} € [{np.percentile(R[:,1],2.5):.2f} ; {np.percentile(R[:,1],97.5):.2f}] ; part des tirages ≥ réel (nombre) {(R[:,0]>=real[0]).mean():.3f}')
# contrôle : rafales orphelines sans manquant à proximité
allwin=Mi.rename(columns={'prev_date':'date'})[['date','t1','t2']]
near=0
for d,g in Dm[Dm.orph&~Dm.big].groupby('dateEven'):
    w_=allwin[allwin.date==d]
    for t in g.t: near+= ((w_.t1<=t)&(w_.t2>=t)).any()
no=int((Dm.orph&~Dm.big).sum())-near
p(f'  rafales orphelines (hors ≥ 1 000 €) sans aucun manquant dans ± 30 min des voisins : {no} sur {int((Dm.orph&~Dm.big).sum())}')
# -- voisinage des partages (comparaison lot 2.6 : 60,7 % contre 43,9 %)
fr=C.groupby('id').qte.apply(lambda s: ((s-s.round()).abs()>1e-9).any()); frs=set(fr[fr].index)
def nb_frac(x): return any(j in frs for j in range(x-3,x+4) if j!=x)
real_f=np.mean([nb_frac(x) for x in Mi.id])
pres=[i for i in cand.id]
rf=[np.mean([nb_frac(x) for x in rng.choice(pres,size=len(Mi),replace=False)]) for _ in range(300)]
p(f'  voisin à ± 3 id portant une quantité fractionnaire : manquants intra-journée {real_f*100:.1f} % ; ids présents tirés (300) {np.mean(rf)*100:.1f} % [{np.percentile(rf,2.5)*100:.1f} ; {np.percentile(rf,97.5)*100:.1f}]')
# corrélation journalière manquants / tickets à 0 €
md=Mi.groupby('prev_date').size(); z0=H[H.tc==0].groupby('date_ticket').size(); nn=A.groupby('date').size()
dd=pd.DataFrame({'m':md,'z':z0,'n':nn}).fillna(0)
p(f'  corrélation par journée : manquants / tickets à 0 € {dd.m.corr(dd.z):.3f} ; manquants / notes {dd.m.corr(dd.n):.3f}')
M.to_csv(OUT+'D03_manquants.csv',index=False)
# -- notes closes un jour ultérieur (position de l'id parmi les id d'une autre journée)
Hd=H.sort_values('id').reset_index(drop=True)
# jour « d'ouverture » estimé = date majoritaire des 6 voisins par id
dates=Hd.date_ticket.values; est=[]
for i in range(len(Hd)):
    nbr=[dates[j] for j in range(max(0,i-3),min(len(Hd),i+4)) if j!=i]
    est.append(pd.Series(nbr).mode().min())
Hd['jour_ouv_est']=est
mj=Hd[Hd.jour_ouv_est<Hd.date_ticket].copy()
syp=u.set_index('id')
mj['jour_prefixe']=mj.id.map(lambda i: (pd.Timestamp('2012-09-25')+pd.Timedelta(days=int(syp.loc[i,'pre']))).strftime('%Y-%m-%d') if i in syp.index else '')
mj['ex_ouv']=mj.jour_ouv_est.map(ex_of); mj['ex_clo']=mj.date_ticket.map(ex_of)
mj['articles']=mj.id.map(lambda i: '; '.join(f'{l} x{q:g}' for l,q in C[C.id==i][['libs','qte']].values))
p(f'  notes dont la date de clôture est postérieure à la journée de leurs id voisins : {len(mj)} ; non nulles {int((mj.tc!=0).sum())} pour {mj.tot_ttc.sum():.2f} € ; exercice d ouverture estimé ≠ exercice de clôture : {int((mj.ex_ouv!=mj.ex_clo).sum())}')
p(mj[['id','jour_ouv_est','jour_prefixe','date_ticket','heure_ticket','no_ticket','serie','tot_ttc','ex_ouv','ex_clo','articles']].to_string())
mj.to_csv(OUT+'D03_multijours.csv',index=False)
