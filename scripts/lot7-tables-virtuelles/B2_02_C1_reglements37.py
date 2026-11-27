"""C-1 : règlements des 37 tickets (55 lignes « état 9 »). (1) report sur des notes de la première série du même Z ;
(2) parts égales du contenu ; (3) différences rondes ; (4) état 9 ; (5) réconciliation 35 / 36. Hasard : décalage de date
(1, 2, 3, 5, 8 jours d'ouverture, même minute) et permutations (graine 20261123). Sorties : out/B2/02.txt, 02_lignes.csv, 02_tickets.csv"""
import sys; sys.path.insert(0,"scripts/lot7-tables-virtuelles")
from B2_common import *
from itertools import combinations
C,E,F,H,A=load(); S=source(); S['id']=S.id.astype(int); p=out2('02.txt')
F['t']=F.heureTicket.map(tm); F['mc']=(F.montant*100).round().astype(int)
L=S[S.etat.astype(str)=='9'].copy(); L['mc']=(L.montant.astype(float)*100).round().astype(int); L['t']=L.heure_ticket.map(tm); L['z']=L.no_z_report.astype(int)
p(f'Lignes état 9 : {len(L)} ; tickets {L.id.nunique()} ; montant {L.mc.sum()/100:.2f} € ; modes {L.groupby("mod_regl").mc.sum().div(100).to_dict()}')
n1=set(H[(H.serie==1)&(H.tc!=0)].id)
F1=F[F.id.isin(n1)].copy(); F1['z']=F1.no_zReport.astype(int)
FZ={z:g for z,g in F1.groupby('z')}
days=sorted(H.date_ticket.unique()); di={d:i for i,d in enumerate(days)}; zday=H.groupby('date_ticket').no_z_report.agg(lambda s:s.mode()[0])
def test(z,t,mode,amt,a=-90,b=180,tot=None,modes=None):
    g=FZ.get(z)
    if g is None: return (0,0,0)
    w=g[(g.t>=t+a)&(g.t<=t+b)]
    wm=w[w.mod_regl==mode].mc.values
    i=int((wm==amt).any())
    ii=0
    for k in (2,3):
        if len(wm)>=k and any(sum(c)==amt for c in combinations(wm.tolist(),k)): ii=1;break
    iii=0
    if tot is not None:
        wv=w[w.mod_regl.isin(modes)].mc.values
        for k in (1,2,3):
            if len(wv)>=k and any(sum(c)==tot for c in combinations(wv.tolist(),k)): iii=1;break
    return (i,ii,iii)
tk=L.groupby('id').agg(tot=('mc','sum'),modes=('mod_regl',lambda s:set(s)))
rows=[]
for _,r in L.iterrows():
    i,ii,iii=test(r.z,r.t,r.mod_regl,r.mc,tot=tk.loc[r.id,'tot'],modes=tk.loc[r.id,'modes'])
    j,_,_=test(r.z,r.t,r.mod_regl,r.mc,a=-90,b=150)
    k30,_,_=test(r.z,r.t,r.mod_regl,r.mc,a=-30,b=30)
    rows.append(dict(id=r.id,date=r.date_ticket,heure=r.heure_ticket,z=r.z,mode=r.mod_regl,montant=r.mc/100,i_meme_ligne=i,ii_somme_2_3=ii,iii_total_ticket=iii,i_fenetre_90_150=j,i_fenetre_30=k30))
R=pd.DataFrame(rows); R.to_csv(OUT2+'02_lignes.csv',index=False)
for c in ['i_meme_ligne','ii_somme_2_3','iii_total_ticket','i_fenetre_90_150','i_fenetre_30']:
    p(f'  {c} : {int(R[c].sum())} lignes, {R[R[c]==1].montant.sum():.2f} €')
# hasard par décalage de date
hz={c:[] for c in ['i','ii','iii']}
for k in (1,2,3,5,8):
    s=[0,0,0]
    for _,r in L.iterrows():
        j=di[r.date_ticket]+k
        if j>=len(days): continue
        x=test(zday[days[j]],r.t,r.mod_regl,r.mc,tot=tk.loc[r.id,'tot'],modes=tk.loc[r.id,'modes'])
        s=[a+b for a,b in zip(s,x)]
    for c,v in zip(['i','ii','iii'],s): hz[c].append(v)
p('  hasard (décalage 1, 2, 3, 5, 8 jours, fenêtre -90 / +180) :',{c:(v,round(np.mean(v),2)) for c,v in hz.items()})
rng=np.random.default_rng(SEED); perm=[]
for _ in range(200):
    am=rng.permutation(L.mc.values)
    perm.append(sum(test(z,t,m,a)[0] for z,t,m,a in zip(L.z,L.t,L.mod_regl,am)))
p(f'  hasard (200 permutations des montants entre les 55 lignes, test i) : moyenne {np.mean(perm):.2f}, IC 95 % [{np.percentile(perm,2.5):.0f} ; {np.percentile(perm,97.5):.0f}], max {max(perm)}')
p('  lignes i (fenêtre -90/+150) :',R[R.i_fenetre_90_150==1][['date','heure','id','mode','montant']].values.tolist())
p('  lignes i (fenêtre ±30) :',R[R.i_fenetre_30==1][['date','heure','id','mode','montant']].values.tolist())
# (2) parts égales et (3) différences rondes, contenu = DEL de la minute de clôture (règle de 156-R3, Contenu_37)
Cn=sheet(F156,'Contenu_37'); Cn=Cn[pd.to_numeric(Cn['id du ticket'],errors='coerce').notna()].copy()
Cn['id']=Cn['id du ticket'].astype(int); Cn['cont']=(Cn['Contenu de la table (DEL de la minute)'].astype(float)*100).round().astype(int)
Cn['regl']=(Cn['Règlements (37_tickets)'].astype(float)*100).round().astype(int); Cn['diff']=Cn.cont-Cn.regl
p(f'\n(5) 156-R3, onglet Contenu_37 : contenu = colonne H (DEL de la minute de clôture), différence = colonne I, positive = colonne J : {int((Cn["diff"]>0).sum())} tickets, {Cn[Cn["diff"]>0]["diff"].sum()/100:.2f} € ; tickets à différence ≤ 0 : {Cn[Cn["diff"]<=0][["id","cont","regl"]].values.tolist()}')
def parts(regl_lines,tot,cont,tol=1):
    if cont<=0: return 0
    vals=list(regl_lines)+[tot]
    for n in range(2,9):
        for k in range(1,n):
            x=cont*k/n
            if any(abs(v-x)<=tol for v in vals): return 1
    return 0
lines=L.groupby('id').mc.apply(list)
Cn['parts']=[parts(lines[i],r,c) for i,r,c in zip(Cn.id,Cn.regl,Cn.cont)]
Cn['parts_0']=[parts(lines[i],r,c,tol=0) for i,r,c in zip(Cn.id,Cn.regl,Cn.cont)]
pp=[]
for _ in range(1000):
    cc=rng.permutation(Cn.cont.values); pp.append(sum(parts(lines[i],r,c) for i,r,c in zip(Cn.id,Cn.regl,cc)))
p(f'(2) parts : règlement total ou une ligne = contenu × k / n (n de 2 à 8) à 0,01 € près : {int(Cn.parts.sum())} tickets (au centime {int(Cn.parts_0.sum())}) ; hasard (1 000 permutations des contenus) moyenne {np.mean(pp):.2f}, IC 95 % [{np.percentile(pp,2.5):.0f} ; {np.percentile(pp,97.5):.0f}]')
p('    tickets :',Cn[Cn.parts==1][['id','cont','regl']].assign(cont=lambda x:x.cont/100,regl=lambda x:x.regl/100).values.tolist())
# (3) différences rondes
pos=Cn[Cn['diff']>0]
m10=pos[pos['diff']%1000==0]; m5=pos[(pos['diff']%500==0)]
p(f'(3) différences positives multiples de 10,00 € : {len(m10)} ({m10["diff"].sum()/100:.2f} €) ; de 5,00 € : {len(m5)} ({m5["diff"].sum()/100:.2f} €)')
pm=[]
for _ in range(1000):
    rr=rng.permutation(Cn.regl.values); d=Cn.cont.values-rr; pm.append(int(((d>0)&(d%1000==0)).sum()))
p(f'    hasard (1 000 permutations des règlements entre tickets) : multiples de 10 € moyenne {np.mean(pm):.2f}, IC 95 % [{np.percentile(pm,2.5):.0f} ; {np.percentile(pm,97.5):.0f}], part des tirages ≥ observé {np.mean(np.array(pm)>=len(m10)):.3f}')
# taux de base : notes ordinaires réglées en plusieurs lignes
g=F1.groupby('id').agg(n=('mc','size'),tot=('mc','sum'),lst=('mc',list))
gm=g[g.n>=2]
r1=np.mean([any(x%1000==0 for x in l) for l in gm.lst]); r2=np.mean([any((t-x)%1000==0 and t-x>0 for x in l) for l,t in zip(gm.lst,gm.tot)])
p(f'    taux de base, notes de première série réglées en plusieurs lignes ({len(gm)}) : au moins une ligne multiple de 10 € {r1*100:.1f} % ; total moins une ligne multiple de 10 € {r2*100:.1f} %')
p(f'    parmi les 37 : règlement total multiple de 10 € {int((Cn.regl%1000==0).sum())} ; contenu multiple de 10 € {int((Cn.cont%1000==0).sum())} ; règlement multiple de 1 € {int((Cn.regl%100==0).sum())}')
# contreparties des différences rondes
N1=H[(H.serie==1)&(H.tc!=0)]
for _,r in m10.iterrows():
    d=r['diff']; day=str(pd.to_datetime(r['Date']).date())
    nd=N1[(N1.date_ticket==day)]; eqn=nd[nd.tc==d][['heure_ticket','no_ticket','id']].values.tolist()
    fl=F1[F1.dateTicket==day]; e1=fl[fl.mc==d][['heureTicket','id','mod_regl','montant']].values.tolist()
    esp=fl[fl.mod_regl=='ESP'].mc.values; e23=any(sum(c)==d for k in (2,3) if len(esp)>=k for c in combinations(esp.tolist(),k))
    p(f'    {day} id {r.id} : contenu {r.cont/100:.2f} règlement {r.regl/100:.2f} différence {d/100:.2f} ; note du jour de ce total : {eqn} ; ligne F du jour de ce montant : {e1} ; somme de 2-3 lignes ESP : {e23}')
# (4) état 9
s2=H[(H.serie==2)&(H.tc!=0)]
p(f'\n(4) 17 tickets non nuls de la seconde série : lignes F {int(F.id.isin(s2.id).sum())} ; dans l export {int(S.id.isin(s2.id).sum())}')
z0=H[(H.tc==0)&~H.dansC]; z0k=z0.groupby(['date_ticket','t']).id.apply(list)
sh=[(d,t,ids) for (d,t),ids in z0k.items() if any(i in set(L.id) for i in ids) and len(ids)>1]
p(f'    minutes où un ticket état 9 côtoie un autre ticket à 0,00 € : {len(sh)} : {sh}')
p('    ordre dans la minute : F et l export sont rangés par date puis par identifiant de note ; aucune colonne n ordonne les règlements dans la minute (indécidable).')
Cn.to_csv(OUT2+'02_tickets.csv',index=False)
