"""Contrôles C1 (Qté B fonction de C ?), C9 (avril 2022), C10 (contrôles), C11 (sensibilité 5 355,78 €), C12 (17 tickets)."""
import pandas as pd, numpy as np
from collections import defaultdict
CA='scripts/lot6-evenement-reglement/cache/'
c=lambda x:int(round(float(x)*100)); e=lambda n:f"{n/100:,.2f}".replace(',',' ').replace('.',',')
out=open('scripts/lot6-evenement-reglement/out/v01_C1_C9_C10_C11.txt','w')
def p(*a): print(*a); print(*a,file=out)
H=pd.read_pickle(CA+'H.pkl'); F=pd.read_pickle(CA+'F.pkl'); S=pd.read_pickle(CA+'SOURCE.pkl'); G=pd.read_pickle(CA+'G.pkl')
Cr=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/Crec.pkl'); CC=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/CC.pkl')
Ht=H.set_index('id')
Cr=Cr[Cr.inB].copy()
Cr['q']=Cr.qteC.map(lambda x:int(round(x*100))); Cr['qB']=Cr.qte.map(lambda x:int(round(x*100))); Cr['pu_c']=Cr.pu.map(c)
Cr['fracC']=(Cr.qteC-Cr.qteC.round()).abs()>1e-9
Cr['z']=Cr.id.map(Ht.no_z_report); Cr['t']=Cr.id.map(Ht.t); Cr['art']=Cr.lib.astype(str).str.strip()+'|'+Cr.pu_c.astype(str)
shared=set(Cr[Cr.fracC].id)
fr=Cr[Cr.id.isin(shared)]   # notes de partage : au moins une ligne fractionnaire en C
# index : (date, z, art) -> list (id, t, q)
idx=defaultdict(list)
for r in fr.itertuples(): idx[(r.date,r.z,r.art)].append((r.id,r.t,r.q))
D=Cr[Cr.qB!=Cr.q]
p('== C1. Lignes Qté B ≠ Qté C :',len(D))
rng=np.random.default_rng(20261123)
notes_day=H[(H.serie==1)&(H.tot_ttc_c!=0)].groupby('date_ticket').id.apply(list).to_dict()
qmap=defaultdict(int)
for r in Cr.itertuples(): qmap[(r.id,r.art)]+=r.q
for W in (15,30,60):
    ok=0; orig=0; nogroup=[]; bad=[]
    for r in D.itertuples():
        grp=[(i,t,q) for i,t,q in idx.get((r.date,r.z,r.art),[]) if abs(t-r.t)<=W]
        others=[q for i,t,q in grp if i!=r.id]
        if not others: nogroup.append(r); continue
        if r.qB==r.q+sum(others): ok+=1
        else: bad.append((r.date,r.ticket,r.art,r.qB,r.q,sum(others)))
        if r.id==min(i for i,_,_ in grp): orig+=1
    p(f'  fenêtre ±{W} min : égalités exactes {ok}/{len(D)} ; écarts {len(bad)} ; sans autre note du groupe {len(nogroup)} ; note portant l\'écart = plus petit id du groupe : {orig}')
    if W==15: bad15=bad; ng15=nogroup
p('  exemples d\'écarts (±15) :',bad15[:10])
# 3. autres notes des groupes
oth_set=set()
for r in D.itertuples():
    for i,t,q in idx.get((r.date,r.z,r.art),[]):
        if i!=r.id and abs(t-r.t)<=15: oth_set.add((i,r.art))
m=Cr[[ (i,a) in oth_set for i,a in zip(Cr.id,Cr.art)]]
cnt=len(m); eq=int((m.qB==m.q).sum())
p(f'  (3) lignes des autres notes des mêmes groupes : {cnt} ; Qté B = Qté C : {eq}')
# 5. placebo : partenaires remplacés par des notes tirées au hasard le même jour
pl=[]
for rep in range(200):
    k=0
    for r in D.itertuples():
        grp=[i for i,t,q in idx.get((r.date,r.z,r.art),[]) if abs(t-r.t)<=15 and i!=r.id]
        if not grp: continue
        cand=[i for i in notes_day.get(r.date,[]) if i!=r.id]
        pick=rng.choice(cand,min(len(grp),len(cand)),replace=False)
        if r.qB==r.q+sum(qmap.get((i,r.art),0) for i in pick): k+=1
    pl.append(k)
p(f'  (5) placebo (partenaires tirés au hasard le même jour, 200 tirages) : égalités moyenne {np.mean(pl):.1f}, max {np.max(pl)}')
p('  (6) lignes Qté B ≠ Qté C sans autre note du groupe (±15) :',len(ng15),[(r.date,r.ticket,r.art,r.qB,r.q) for r in ng15[:30]])
# ---- C9
p('\n== C9')
f=H[(H.ex=='2022-2023')&(H.serie==1)].sort_values(['date_ticket','t']).iloc[0]
p(f'  premier ticket série 1 : {f.date_ticket} {f.heure_ticket} id {f.id} ; tot_sum − tot_ttc = {e(f.tot_sum_c-f.tot_ttc_c)} ; tot_tax_sum − tot_tva = {e(f.tot_tax_sum_c-c(f.tot_tva))} ; A NOUVEAUX 977 739,78 / 102 865,15')
S['idn']=S.id.astype(float).astype(int)
p('  export natif : date min',S.date_ticket.min(),' ; id min',S.idn.min(),'(date',S.loc[S.idn.idxmin(),'date_ticket'],') ; lignes avant le 14/04/2022 :',int((S.date_ticket<'2022-04-14').sum()),' ; plus petit sy_uk',S.sy_uk.min())
# ---- C10
p('\n== C10')
X=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot25/C_b3.pkl')
for ref in ['1989','0099','0354','1816','2119']:
    a=X[X.ref==ref]; p(f'  réf {ref} : taux appliqué (rart, déduit des paliers G) {sorted(a.rart.unique())} ; lignes {len(a)} ; dernière vente {a.date.max()}')
CC['pu_c']=CC.pu.map(c); CC['q']=CC.qte.map(lambda x:int(round(x*1000))); CC['tc']=CC.tot.map(c)
d=(CC.pu_c*CC.q/1000-CC.tc).abs()
prod_c=(CC.pu*CC.qte).round(2).map(c)
for lab,m in [('|PU×Qté − montant| < 0,5 c',d<0.5),('≤ 1 c (produit arrondi au centime)',(prod_c-CC.tc).abs()<=1),('≤ 2 c',(prod_c-CC.tc).abs()<=2),('produit arrondi = montant',(prod_c==CC.tc))]:
    p(f'  lignes C {lab} : {int(m.sum())} / {len(CC)}')
z0=H[H.tot_ttc_c==0]; p('  notes à 0 € :',len(z0),' ; avec règlement F :',int(z0.id.isin(F.id).sum()),' ; sans règlement (absentes de l\'export natif des règlements) :',int((~z0.id.isin(S.idn)).sum()))
# concordance C / H
j=CC.drop_duplicates('id').set_index('id').join(Ht[['date_ticket','heure_ticket','no_ticket','dat_z','no_z_report','tot_ttc_c']],how='left')
p('  C/H par identifiant (notes de C) :',len(j))
cols=[('date','date_ticket'),('heure','heure_ticket'),('ticket','no_ticket'),('datz','dat_z'),('z','no_z_report')]
p('   concordances :',{a:int((j[a]==j[b]).sum()) for a,b in cols},' tot_ttc :',int((j.tot_ttc.map(c)==j.tot_ttc_c).sum()))
lines_ok=CC.id.map(lambda i: True)
# table de passage 155 / B
E=pd.read_pickle(CA+'E.pkl'); DEL=E[E.typEven=='DEL']
withl=set(CC.id); Z0=H[(H.tot_ttc_c==0)&(~H.id.isin(withl))]
zk=set(zip(Z0.date_ticket,Z0.no_z_report,Z0.t))
dm=DEL.groupby(['dateEven','no_zEport','t']).amount_c.agg(['size','sum'])
dz=dm[[k in zk for k in dm.index]]
p(f'\n  passage : tickets à 0 € sans ligne {len(Z0)} ; clos à la minute d\'un DEL {sum((d,z,t) in set(dm.index) for d,z,t in zip(Z0.date_ticket,Z0.no_z_report,Z0.t))} ; minutes (date, Z, minute) distinctes {len(dz)} ; DEL dans ces minutes {int(dz["size"].sum())} ; Σ {e(dz["sum"].sum())}')
pos=DEL[[ (d,z,t) in set(dz.index) for d,z,t in zip(DEL.dateEven,DEL.no_zEport,DEL.t)]]
p(f'   dont DEL > 0 : {int((pos.amount_c>0).sum())} ; = 0 : {int((pos.amount_c==0).sum())} ; < 0 : {int((pos.amount_c<0).sum())}')
excl=dz[(dz['sum']<=0)|(dz['sum']>=100000)]
p('   minutes de total ≤ 0 ou ≥ 1 000 € :',[(k,int(v['size']),e(v['sum'])) for k,v in excl.iterrows()])
# ---- C11
p('\n== C11')
TOT25=[40352848,44341643,43490784]; CAc=[40343283,43806065,43486835]
z9=F[F.tot_ttc_c==0]
for i,ex in enumerate(['2022-2023','2023-2024','2024-2025']):
    f=F[F.ex==ex].montant_c.sum(); f9=z9[z9.ex==ex].montant_c.sum(); b=H[(H.ex==ex)&(H.serie==1)].tot_ttc_c.sum()
    p(f'  {ex} F brut : [{e(TOT25[i]-f)}] + [{e(f-b)}] + [{e(b-CAc[i])}] ; F hors etat 9 : [{e(TOT25[i]-(f-f9))}] + [{e(f-f9-b)}] + [{e(b-CAc[i])}] ; total {e(TOT25[i]-CAc[i])}')
brut={'2022-2023':{'511200':519465,'511220':962050,'511230':1493450,'530':339065-59804},
      '2023-2024':{'511200':352256,'511220':911236,'511221':224005,'511230':2302662,'530':601043-59775},
      '2024-2025':{'511200':475410,'511210':39766638,'511230':2020300,'530':361309-65657}}
net={'2022-2023':{'511200':462735,'511220':948632,'511230':1471500,'530':333063},
     '2023-2024':{'511200':360012,'511220':910504,'511221':102427,'511230':2330000,'530':595890},
     '2024-2025':{'511200':452910,'511210':39767738,'511230':2040500,'530':280475}}
for ex in brut:
    adj=sum(brut[ex][k]-net[ex][k] for k in brut[ex])
    p(f'  {ex} : Σ (brut − net) des comptes à brut imprimé {e(adj)} ; (511 + 530) en bruts {e(TOT25[["2022-2023","2023-2024","2024-2025"].index(ex)]+adj)} ; − CA {e(TOT25[["2022-2023","2023-2024","2024-2025"].index(ex)]+adj-CAc[["2022-2023","2023-2024","2024-2025"].index(ex)])}')
    for k in brut[ex]:
        m={'511200':'CHQ','511210':'CB','511220':'TR','511221':'TR','511230':'CHV','530':'ESP'}[k]
        p(f'     {k} brut {e(brut[ex][k])} net {e(net[ex][k])}')
out.close()
