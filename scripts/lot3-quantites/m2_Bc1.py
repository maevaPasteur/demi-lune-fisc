"""Sort de la part supprimée (55 notes isolées à miroir DEL complet ; 47 parts du résidu appariées à un DEL).
Pour chaque cas : chronologie exacte ; recherche, le même jour, (R1) d'une note encaissée APRÈS le DEL portant le même ensemble
d'articles (libellé normalisé, PU) aux mêmes quantités ; (R2) idem, quantités ≥ (note qui contient la part) ;
(T1) d'une note encaissée après le DEL dont le total F = somme supprimée ±0,02 ; (T2) d'une ligne de règlement F (montant) = somme ±0,02 après le DEL ;
(Z) d'un des 37 règlements F sur id à tot_ttc nul (même jour, montant de ligne ou somme par id = somme ±0,02).
Témoin : pour chaque cas, une note non fractionnaire du même jour (graine 20261123), traitée comme « part supprimée » à son heure."""
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
from collections import defaultdict
rng=np.random.default_rng(20261123)
Cr,F,E,Fid,tabs,nd,A=load()
D=E[E.typEven=='DEL'].copy(); Dd={d:g for d,g in D.groupby('dateEven')}
Fz=F[F.tot_ttc==0].copy(); Fz['t']=Fz.heureTicket.map(tmin)
Fpos=F[F.tot_ttc!=0].copy(); Fpos['t']=Fpos.heureTicket.map(tmin)
notes=Cr.drop_duplicates('id')[['id','ex','date','ticket','t']].set_index('id')
notes=notes[notes.index.isin(Fid.index)]
lines={i:g for i,g in Cr.groupby('id')}
frac_ids=set(Cr[Cr.fracC].id)
def match_del(d,t0,t1,amounts,tol=0.02):
    g=Dd.get(d); out=[]
    if g is None: return [None]*len(amounts)
    g=g[(g.t>=t0)&(g.t<=t1)]; used=set()
    for a in amounts:
        c=[j for j in g.index[(g.amount-a).abs()<=tol] if j not in used]
        if c: used.add(c[0]); out.append((j:=c[0],g.at[c[0],'t'],g.at[c[0],'amount']))
        else: out.append(None)
    return out
def search(d,tdel,arts,qty,somme,exclude):
    """arts: list of (libn,pu100) ; qty: dict art->qty supprimée ; renvoie dict de résultats"""
    day=notes[(notes.date==d)&(~notes.index.isin(exclude))]
    after=day[day.t>=tdel]
    r=dict(R1=[],R2=[],T1=[],T2=[],Z=[],R1b=[],J=[])
    for j,row in day.iterrows():
        q=lines[j].groupby(['libn','pu100']).qteC.sum().to_dict()
        if all(abs(q.get(a,0)-qty[a])<1e-6 for a in arts): r['R1b'].append((j,row.t))
        if abs(Fid.tot[j]-somme)<=0.02 or all(q.get(a,0)>=qty[a]-1e-6 for a in arts): r['J'].append((j,row.t))
    for j,row in after.iterrows():
        L=lines[j]; q=L.groupby(['libn','pu100']).qteC.sum().to_dict()
        if all(abs(q.get(a,0)-qty[a])<1e-6 for a in arts) and len(q)==len(arts): r['R1'].append((j,row.t))
        elif all(q.get(a,0)>=qty[a]-1e-6 for a in arts): r['R2'].append((j,row.t))
        if abs(Fid.tot[j]-somme)<=0.02: r['T1'].append((j,row.t))
    fp=Fpos[(Fpos.dateTicket==d)&(Fpos.t>=tdel)&(~Fpos.id.isin(exclude))]
    r['T2']=list(fp[(fp.montant-somme).abs()<=0.02].id)
    fz=Fz[Fz.dateTicket==d]
    zs=fz.groupby('id').montant.sum()
    r['Z']=sorted(set(fz[(fz.montant-somme).abs()<=0.02].id)|set(zs[(zs-somme).abs()<=0.02].index))
    return r
cases=[]
# 55 notes isolées
iso=[x[0] for ex,d,x in tabs if len(x)==1]
for i in iso:
    L=lines[i]; d=L.date.iloc[0]; t=Fid.t[i]
    m=match_del(d,t-5,t+30,list(L.tot))
    if any(x is None for x in m): continue
    arts=list(L.groupby(['libn','pu100']).qteC.sum().index); qty=L.groupby(['libn','pu100']).qteC.sum().to_dict()
    tdel=[x[1] for x in m]; somme=round(sum(x[2] for x in m),2)
    cases.append(dict(type='note isolée',ex=L.ex.iloc[0],date=d,ref=f"n° {L.ticket.iloc[0]} (id {i})",t_note=t,t_del_min=min(tdel),t_del_max=max(tdel),n_del=len(m),somme=somme,
                      mode=Fid.mods[i],arts=arts,qty=qty,exclude=[i]))
# articles non refermés : parts appariées à un DEL
R=A[~A.ref]
for (ex,d,ids),g in R.groupby(['ex','date','ids']):
    comps=[]; arts=[]; qty={}
    for r in g.itertuples():
        c=round((math.ceil(r.somme-1e-9)-r.somme)*r.pu,2); comps.append(c); a=(norm(r.lib),round(r.pu*100)); arts.append(a); qty[a]=round(math.ceil(r.somme-1e-9)-r.somme,6)
    ts=[Fid.t[i] for i in ids]
    m=match_del(d,min(ts)-5,max(ts)+30,comps,tol=0.05)   # tolérance 0,05 € : 47 parts appariées sur 50
    ok=[(a,x) for a,x in zip(arts,m) if x is not None]
    if not ok: continue
    arts2=[a for a,x in ok]; tdel=[x[1] for a,x in ok]; somme=round(sum(x[2] for a,x in ok),2)
    cases.append(dict(type='résidu',ex=ex,date=d,ref='n° '+'+'.join(str(nd.tk[i]) for i in ids),t_note=max(ts),t_note_min=min(ts),t_del_min=min(tdel),t_del_max=max(tdel),n_del=len(ok),
                      somme=somme,mode=' / '.join(Fid.mods[i] for i in ids),arts=arts2,qty={a:qty[a] for a in arts2},exclude=list(ids)))
out=[]
for c in cases:
    r=search(c['date'],c['t_del_min'],c['arts'],c['qty'],c['somme'],c['exclude'])
    cat=('ressaisie identique et réglée' if r['R1'] else ('réglée par un règlement sans note (37)' if r['Z'] else ('contenue dans une note réglée après (Qté ≥)' if r['R2'] else ('même total réglé après' if (r['T1'] or r['T2']) else 'aucune trace'))))
    out.append(dict(type=c['type'],ex=c['ex'],date=c['date'],ref=c['ref'],heure_note=f"{c['t_note']//60:02d}:{c['t_note']%60:02d}",
        DEL_de=f"{c['t_del_min']//60:02d}:{c['t_del_min']%60:02d}",DEL_a=f"{c['t_del_max']//60:02d}:{c['t_del_max']%60:02d}",decal_min=c['t_del_min']-c['t_note'],decal_max=c['t_del_max']-c['t_note'],
        n_del=c['n_del'],somme=c['somme'],mode=c['mode'],R1b_jour=len(r['R1b']),J_jour=len(r['J']),R1=len(r['R1']),R2=len(r['R2']),T1=len(r['T1']),T2=len(r['T2']),Z=len(r['Z']),
        R1_ids=';'.join(f"{j}@{t//60:02d}:{t%60:02d}" for j,t in r['R1']),R2_ids=';'.join(f"{j}@{t//60:02d}:{t%60:02d}" for j,t in r['R2'][:5]),T1_ids=';'.join(f"{j}@{t//60:02d}:{t%60:02d}" for j,t in r['T1']),Z_ids=';'.join(map(str,r['Z'])),cat=cat,
        notes_apres_DEL=int(((notes.date==c['date'])&(notes.t>=c['t_del_min'])).sum())))
O=pd.DataFrame(out); O.to_csv(OUT+'Bc1_cas.csv',index=False)
pd.set_option('display.width',320); pd.set_option('display.max_colwidth',40)
print(O.drop(columns=['R2_ids']).to_string(index=False))
print(pd.crosstab([O.type,O.cat],O.ex,margins=True))
print(O.pivot_table(index=['type','cat'],columns='ex',values='somme',aggfunc='sum',margins=True).round(2))
# témoin
ctl=[]
pool_day={d:[j for j in notes[notes.date==d].index if j not in frac_ids] for d in set(O.date)}
for c in cases:
    cand=pool_day[c['date']]
    nl=len(c['arts'])
    cc=[j for j in cand if abs(lines[j].groupby(['libn','pu100']).ngroups-nl)<=1] or cand
    j=cc[rng.integers(len(cc))]; L=lines[j]
    arts=list(L.groupby(['libn','pu100']).qteC.sum().index); qty=L.groupby(['libn','pu100']).qteC.sum().to_dict()
    r=search(c['date'],Fid.t[j],arts,qty,round(L.tot.sum(),2),[j])
    cat=('ressaisie identique et réglée' if r['R1'] else ('réglée par un règlement sans note (37)' if r['Z'] else ('contenue dans une note réglée après (Qté ≥)' if r['R2'] else ('même total réglé après' if (r['T1'] or r['T2']) else 'aucune trace'))))
    ctl.append(dict(type=c['type'],ex=c['ex'],cat=cat,R1b_jour=len(r['R1b']),J_jour=len(r['J']),R1=len(r['R1']),R2=len(r['R2']),T1=len(r['T1']),T2=len(r['T2']),Z=len(r['Z'])))
Q=pd.DataFrame(ctl); Q.to_csv(OUT+'Bc1_temoin.csv',index=False)
print('TÉMOIN'); print(pd.crosstab([Q.type,Q.cat],Q.ex,margins=True))
for nm,df in [('cas',O),('témoin',Q)]:
    print(nm,'≥1 R1b(jour, mêmes articles et Qté, autres lignes admises)',(df.R1b_jour>0).sum(),' ≥1 J (jour, total égal ou articles contenus)',(df.J_jour>0).sum(),' ≥1 R1',(df.R1>0).sum(),' ≥1 R2',(df.R2>0).sum(),' ≥1 T1',(df.T1>0).sum(),' ≥1 T2',(df.T2>0).sum(),' ≥1 Z',(df.Z>0).sum(),' n',len(df))
# --- chronologie comparée : délai entre 1re et 2e note des tables refermées de 2 notes ; délai entre notes consécutives des tables refermées
full=[ids for ex,d,ids in tabs if len(ids)==2 and A[A.ids==tuple(ids)].ref.all()]
dl=pd.Series([abs(Fid.t[a]-Fid.t[b]) for a,b in full])
print('tables refermées de 2 notes :',len(dl),' délai 2e − 1re (min) :',dl.value_counts().sort_index().to_dict(),' moyenne',round(dl.mean(),3),' médiane',dl.median())
iso_=O[O.type=='note isolée']
print('notes isolées : décalage 1er DEL − note :',iso_.decal_min.value_counts().sort_index().to_dict(),' moyenne',round(iso_.decal_min.mean(),3),' médiane',iso_.decal_min.median())
print('  tous DEL dans [0 ; 2] min :',((iso_.decal_min>=0)&(iso_.decal_max<=2)).sum(),' même minute :',((iso_.decal_min==0)&(iso_.decal_max==0)).sum(),' au moins un DEL avant la note :',(iso_.decal_min<0).sum(),' dernier DEL > 2 min :',(iso_.decal_max>2).sum())
print('  part des délais ≤ 2 min : tables refermées',round((dl<=2).mean()*100,1),'% ; notes isolées (1er DEL)',round(((iso_.decal_min>=0)&(iso_.decal_min<=2)).mean()*100,1),'%')
