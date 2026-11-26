"""D-1 : 1 158 identifiants de notes absents de H contre les 2 118 DEL « orphelins » (minute sans clôture de note ni de ticket à 0 € à ±5 min, même Z)
et contre les tables vidées. Fenêtre d'un identifiant manquant : voisins présents (id précédent et suivant) du même jour, [min(t) − 30 ; max(t) + 30].
Placebo : même nombre d'identifiants PRÉSENTS tirés au hasard le même jour (hors premier et dernier), fenêtre construite de même sur leurs voisins ; 1 000 tirages, graine 20261123.
Complément : corrélation journalière identifiants manquants / tickets à 0 €, avec placebo par permutation et corrélation partielle à activité égale."""
import pandas as pd, numpy as np
from collections import defaultdict
CA='scripts/lot6-evenement-reglement/cache/'
E=pd.read_pickle(CA+'E.pkl'); H=pd.read_pickle(CA+'H.pkl'); CC=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/CC.pkl'); TB=pd.read_pickle(CA+'tables_videes_B.pkl')
e=lambda n:f"{n/100:,.2f}".replace(',',' ').replace('.',',')
out=open('scripts/lot6-evenement-reglement/out/u01_D1_ids_DEL.txt','w')
def p(*a): print(*a); print(*a,file=out)
DEL=E[E.typEven=='DEL']
nk=set(zip(H.date_ticket,H.no_z_report,H.t))
orph=DEL[[not any((d,z,t+x) in nk for x in range(-5,6)) for d,z,t in zip(DEL.dateEven,DEL.no_zEport,DEL.t)]]
p('DEL orphelins',len(orph),e(orph.amount_c.sum()))
Hs=H.sort_values('id').reset_index(drop=True)
ids=Hs.id.values; pos={i:k for k,i in enumerate(ids)}
miss=[]
for k in range(1,len(ids)):
    for m in range(ids[k-1]+1,ids[k]): miss.append(k)   # k = indice du voisin suivant
def window(k):
    a=Hs.iloc[k-1]; b=Hs.iloc[k]
    if a.date_ticket!=b.date_ticket: return None
    return a.date_ticket,min(a.t,b.t)-30,max(a.t,b.t)+30
W=[window(k) for k in miss]; Wd=[w for w in W if w]
p('identifiants manquants',len(miss),' ; avec voisins du même jour',len(Wd))
odays=defaultdict(list)
for r in orph.itertuples(): odays[r.dateEven].append((r.t,r.amount_c))
tdays=defaultdict(list)
for r in TB.itertuples(): tdays[r.d].append((r.t,r.V))
def measure(wins):
    byd=defaultdict(list)
    for d,lo,hi in wins: byd[d].append((lo,hi))
    n=a=nt=at=0
    for d,L in byd.items():
        for t,v in odays.get(d,[]):
            if any(lo<=t<=hi for lo,hi in L): n+=1;a+=v
        for t,v in tdays.get(d,[]):
            if any(lo<=t<=hi for lo,hi in L): nt+=1;at+=v
    return n,a,nt,at
real=measure(Wd)
cover=sum(hi-lo for _,lo,hi in Wd)
p(f'réel : DEL orphelins dans les fenêtres {real[0]} ({e(real[1])}) ; tables vidées {real[2]} ({e(real[3])}) ; longueur cumulée des fenêtres {cover} min')
# placebo
byday=Hs.groupby('date_ticket').indices
need=defaultdict(int)
for d,_,_ in Wd: need[d]+=1
rng=np.random.default_rng(20261123); P=[]
for rep in range(1000):
    wins=[]
    for d,k in need.items():
        idx=byday[d]; cand=[i for i in idx if i>0 and i<len(ids) and Hs.date_ticket[i-1]==d]
        if not cand: continue
        for i in rng.choice(cand,min(k,len(cand)),replace=False):
            a=Hs.iloc[i-1]; b=Hs.iloc[i]; wins.append((d,min(a.t,b.t)-30,max(a.t,b.t)+30))
    P.append(measure(wins))
P=np.array(P)
for j,lab in enumerate(['DEL orphelins (n)','DEL orphelins (montant)','tables vidées (n)','tables vidées (montant)']):
    v=P[:,j]; r=real[j]
    fmt=(lambda x:e(x)) if 'montant' in lab else (lambda x:f'{x:.1f}')
    p(f'  {lab} : réel {fmt(r)} ; placebo moyenne {fmt(v.mean())} ; IC 95 % [{fmt(np.percentile(v,2.5))} ; {fmt(np.percentile(v,97.5))}] ; part des tirages ≥ réel {np.mean(v>=r):.3f}')
# corrélations journalières
days=sorted(set(H.date_ticket))
md=defaultdict(int)
for k in miss: md[Hs.date_ticket[k-1]]+=1
T=pd.DataFrame({'manq':[md.get(d,0) for d in days],
 'zero':H[H.tot_ttc_c==0].groupby('date_ticket').size().reindex(days,fill_value=0).values,
 'notes':H[H.tot_ttc_c!=0].groupby('date_ticket').size().reindex(days,fill_value=0).values,
 'orph':orph.groupby('dateEven').size().reindex(days,fill_value=0).values})
r0=T.manq.corr(T.zero); rn=T.manq.corr(T.notes); rz=T.zero.corr(T.notes)
part=(r0-rn*rz)/np.sqrt((1-rn**2)*(1-rz**2))
perm=[np.corrcoef(T.manq,rng.permutation(T.zero.values))[0,1] for _ in range(1000)]
p(f'corrélation jour : manquants / tickets à 0 € {r0:.3f} (placebo permutation : moyenne {np.mean(perm):.3f}, max {np.max(perm):.3f}) ; manquants / notes payées {rn:.3f} ; partielle (notes constantes) {part:.3f} ; manquants / DEL orphelins {T.manq.corr(T.orph):.3f}')
out.close()
