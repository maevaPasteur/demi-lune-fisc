"""B3 / C6 : les 17 notes non nulles de la seconde série sont-elles reprises sur des notes de la première série (même jour) ?
C7 : les 37 notes à 0 € porteuses de règlements : DEL à la minute, double saisie d'un règlement (même jour, même mode, même montant), placebo."""
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
from itertools import combinations
from collections import Counter
rng=np.random.default_rng(20261123)
CC=pd.read_pickle(CA+'C_b3.pkl'); H=loadH(); G=loadG(); F=pd.read_pickle(C23+'F.pkl'); E=pd.read_pickle(C23+'E.pkl')
AN={'2022-2023':977739.78,'2023-2024':1381110.20,'2024-2025':1819103.12}
H['id']=H.id.astype(int); H['s']=np.where(H.tot_sum>=H.ex.map(AN)-1e-6,1,2)
s2ids=H[(H.s==2)&(H.tot_ttc!=0)].id.tolist(); s1=set(H[H.s==1].id)
CC['q100']=(CC.qte*100).round().astype(int); CC['pu_c']=CC.pu.map(c)
def need(i): 
    x=CC[CC.id==i]; return Counter({(r,p):q for (r,p),q in x.groupby(['ref','pu_c']).q100.sum().items()})
def covers(cands,nd,maxk=3,later_of=None):
    pools={j:Counter({(r,p):q for (r,p),q in CC[CC.id==j].groupby(['ref','pu_c']).q100.sum().items()}) for j in cands}
    useful=[j for j in cands if any(k in pools[j] for k in nd)]
    for k in range(1,maxk+1):
        for comb in combinations(useful,k):
            tot=Counter()
            for j in comb: tot.update(pools[j])
            if all(tot[key]>=v for key,v in nd.items()): return comb
    return None
print('===== C6')
rows=[]
dates=sorted(CC.date.unique())
for i in s2ids:
    x=CC[CC.id==i]; d=x.date.iloc[0]; nd=need(i)
    hN=tmin(x.heure.iloc[0]); CC['tm']=CC.heure.map(tmin) if 'tm' not in CC else CC.tm
    same=[j for j in CC[(CC.date==d)&(CC.id.isin(s1))&(CC.tm>=hN)].id.unique()]
    comb=covers(same,nd)
    # placebo : 20 autres jours de la même saison (graine), notes première série de ce jour
    hits=0; others=[dd for dd in dates if dd!=d]
    for dd in rng.choice(others,20,replace=False):
        cand=list(CC[(CC.date==dd)&(CC.id.isin(s1))&(CC.tm>=hN)].id.unique())
        if covers(cand,nd) is not None: hits+=1
    tva_rep=None
    if comb:
        # TVA des parts reprises : TVA légale du contenu repris, au prorata des quantités (non arrondie)
        pass
    rows.append([i,d,x.heure.iloc[0],x.tot_ttc.iloc[0],x.tot_tva.iloc[0],len(x),comb,hits/20])
R=pd.DataFrame(rows,columns=['id','date','heure','TTC','TVA','lignes','reprise (notes 1re série, même jour, closes à la même heure ou après)','placebo : part des 20 autres jours où une reprise existe'])
pd.set_option('display.width',250); print(R.to_string())
rep=R[R.iloc[:,6].notna()]
print('notes reprises',len(rep),'/',len(R),' TTC repris',round(rep.TTC.sum(),2),' TVA',round(rep.TVA.sum(),2),' ; non reprises TTC',round(R[R.iloc[:,6].isna()].TTC.sum(),2))
print('placebo moyen (toutes notes) : nombre attendu de reprises au hasard',round(R.iloc[:,7].sum(),2))
# reprises présentes dans G ?
gid=set(pd.read_pickle(CA+'B5_tickets.pkl').index.get_level_values(1))
print('notes de reprise dans G :',all(j in gid for c_ in rep.iloc[:,6] for j in c_))
print('===== C7')
fz=F[F.tot_ttc==0].copy(); notes=fz.groupby('id')
S=pd.read_pickle(CA+'SOURCE_reglement.pkl')
E['t']=E.heureEven.map(tmin); Ed=E[E.typEven=='DEL']
F1=F[F.id.isin(s1)].copy(); F1['m']=F1.montant.map(c)
def dbl(day,mode,amt): return ((F1.dateTicket==day)&(F1.mod_regl==mode)&(F1.m==amt)).sum()
out=[]; tot_dbl=0; plc=[]
for i,g in notes:
    d=g.dateTicket.iloc[0]; h=g.heureTicket.iloc[0]; z=int(g.no_zReport.iloc[0]); t=tmin(h)
    dl=Ed[(Ed.dateEven==d)&(Ed.no_zEport==z)&(Ed.t==t)]
    dm=[(r.mod_regl,r.montant,int(dbl(d,r.mod_regl,c(r.montant)))) for r in g.itertuples()]
    nd=sum(1 for x in dm if x[2]>0); tot_dbl+=nd
    out.append([i,d,h,z,round(g.montant.sum(),2),g.groupby('mod_regl').montant.sum().round(2).to_dict(),len(dl),round(dl.amount.sum(),2),nd,len(g)])
O=pd.DataFrame(out,columns=['id','date','heure','Z','Σ règl.','par mode','DEL à la minute','Σ DEL','règl. avec homologue 1re série même jour','lignes'])
print(O.to_string())
print('notes avec ≥1 DEL à la minute :',int((O['DEL à la minute']>0).sum()),'/',len(O),' ; Σ DEL',round(O['Σ DEL'].sum(),2))
print('lignes de règlement ayant un homologue (même jour, même mode, même montant) en 1re série :',tot_dbl,'/',len(fz))
# placebo : même test un autre jour (20 tirages)
pl=[]
for _ in range(20):
    n=0
    for r in fz.itertuples():
        dd=rng.choice([x for x in dates if x!=r.dateTicket]); n+= dbl(dd,r.mod_regl,c(r.montant))>0
    pl.append(n)
print('placebo (autre jour tiré, 20 tirages, graine 20261123) : moyenne',np.mean(pl),' min',min(pl),' max',max(pl))
print('natif : etat des 55 lignes',S[S.tot_ttc.astype(float)==0].etat.value_counts().to_dict(),' ; etat=9 ailleurs',int(((S.etat=='9')&(S.tot_ttc.astype(float)!=0)).sum()))
k=1958.26
for i,ex in enumerate(EX):
    v=[32.45,1607.38,318.43][i]; print(f'majorant TVA {ex}: à 10 % {v/11:.2f} ; à 20 % {v/6:.2f}')
print(f'cumul : à 10 % {k/11:.2f} ; à 20 % {k/6:.2f}')
