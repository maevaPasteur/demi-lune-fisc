"""B1 : contrôles B-1 (ordre et décalage), B-2 (paliers G / C), B-5 (TVA légale ticket par ticket, cache B5_tickets.pkl),
B-6 (arrondis), B-9 (VAT_base), B-10 (paliers négatifs), B-12 (clés de tri), B-13 (seconde série), B-17 (formules et menus)."""
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
from decimal import Decimal, ROUND_HALF_UP
R2=lambda x: float(Decimal(str(round(x,6))).quantize(Decimal('0.01'),ROUND_HALF_UP))
CC=pd.read_pickle(CA+'C_taux2.pkl').sort_values(['ex','rowC']).reset_index(drop=True)
A=pd.read_pickle(CA+'B3_articles.pkl').set_index('ref'); G=loadG(); H=loadH()
CC['nat']=CC.ref.map(A.nature); CC['tl']=CC.ref.map(lambda r: A.taux_legal[r] if A.taux_legal[r]!='' else np.nan)
CC['tb']=CC.rf; CC['ts']=CC.rc
CC['tsuiv']=CC.groupby('ex').rf.shift(-1); CC['tprec']=CC.groupby('ex').rf.shift(1)
P=lambda *a: print(*a)
# ---------------- B-1
P('===== B-1')
for ex in EX+['3ex']:
    x=CC if ex=='3ex' else CC[CC.ex==ex]
    m=x.tsuiv.notna(); mp=x.tprec.notna()
    P(f'{ex}: lignes {len(x)} ; t_brut=t_serv {100*(x.tb==x.ts).mean():.3f} % ; t_suiv=t_serv {100*(x.tsuiv[m]==x.ts[m]).mean():.3f} % ({m.sum()} l.) ; t_prec=t_serv {100*(x.tprec[mp]==x.ts[mp]).mean():.3f} %')
for i,ex in enumerate(EX):
    x=CC[CC.ex==ex]; last=x.iloc[-1]; first=x.iloc[0]
    nxt=CC[CC.ex==EX[i+1]].iloc[0] if i<2 else None
    P(f'  {ex}: 1re ligne rowC {first.rowC} {first.lib_s} t_brut {first.tb} (taux article {first.rart}) ; dernière ligne rowC {last.rowC} {last.lib_s} taux article {last.rart}'+
      (f' ; 1re ligne du fichier suivant : t_brut {nxt.tb} → {"=" if nxt.tb==last.rart else "≠"} taux article de la dernière ligne' if nxt is not None else ''))
    # ordre : Id croissant ?
    d=np.diff(x.id.values); P(f'     ordre des lignes : Id non décroissant sur {100*(d>=0).mean():.3f} % des transitions ; ruptures {int((d<0).sum())} ; (date,Id) croissant : {bool(((x.date.values[1:]>x.date.values[:-1])|((x.date.values[1:]==x.date.values[:-1])&(d>=0))).all())}')
# ---------------- B-2
P('===== B-2')
G['r']=G['taux_tva%'].astype(int); G['pal']=G.VAT_base_c+100*G.r; G['paltax']=G.tax_amount_c*(100+G.r)/G.r
k3=G.drop_duplicates('tk').groupby(['ex','dateTicket','noTicket','heureTicket']).size()
P('clé (exercice,date,n°,heure) dans G : tickets',len(k3),' doublons',int((k3>1).sum()))
gp=G.pivot_table(index=['ex','dateTicket','noTicket','heureTicket'],columns='r',values='pal',aggfunc='sum',fill_value=0); gp.columns=['G10','G20']
gt=G.pivot_table(index=['ex','dateTicket','noTicket','heureTicket'],columns='r',values='paltax',aggfunc='sum',fill_value=0); gt.columns=['T10','T20']
gp=gp.join(gt).reset_index()
# jointure par id via H
AN0={'2022-2023':977739.78,'2023-2024':1381110.20,'2024-2025':1819103.12}
H1=H[H.apply(lambda r: r.tot_sum>=AN0[r.ex]-1e-6,axis=1)]
kh=H.groupby(['ex','date_ticket','no_ticket','heure_ticket']).size(); P('clé (ex,date,n°,heure) dans H complet : notes',len(H),' clés en doublon',int((kh>1).sum()),' ; H première série',len(H1))
hh=H1[['ex','date_ticket','no_ticket','heure_ticket','id']].copy(); hh['no_ticket']=hh.no_ticket.astype(int); hh['id']=hh.id.astype(int)
j=gp.merge(hh,left_on=['ex','dateTicket','noTicket','heureTicket'],right_on=['ex','date_ticket','no_ticket','heure_ticket'],how='left')
P('tickets G avec un id H :',j.id.notna().sum(),'/',len(j),' ids distincts',j.id.nunique())
for col,lab in [('tb','t_brut'),('ts','t_serv'),('tsuiv','t_suiv'),('tprec','t_prec')]:
    c20=CC.assign(v=np.where(CC[col]==20,CC.tot.map(c),0)).groupby('id').v.sum()
    jj=j.assign(C20=j.id.map(c20))
    for ex in EX+['3ex']:
        z=jj if ex=='3ex' else jj[jj.ex==ex]
        d=(z.G20-z.C20).abs()
        P(f'  {lab:7s} {ex}: tickets {len(z)} ; |palG20−palC20| = 0 : {(d==0).sum()} ({100*(d==0).mean():.2f} %) ; ≤ 0,05 € : {(d<=5).sum()} ({100*(d<=5).mean():.2f} %)')
P('  tolérance m-1 : |palG − palG_tax| max 10 %% = %.4f €, 20 %% = %.4f €' % ((G[G.r==10].pal-G[G.r==10].paltax).abs().max()/100,(G[G.r==20].pal-G[G.r==20].paltax).abs().max()/100))
# ---------------- B-5
P('===== B-5')
CC['tl0']=CC.tl.fillna(CC.rart)          # indéterminés au taux appliqué
CC['tl20']=CC.tl.fillna(20); CC['tl10']=CC.tl.fillna(10)
CC['tc']=CC.tot.map(c)
def tva_tickets(df,col):
    p=df.assign(r=df[col].astype(int)).groupby(['ex','id','r']).tc.sum().reset_index()
    p['tva']=[int((Decimal(int(v))*r/(100+r)).quantize(Decimal(1),ROUND_HALF_UP)) for v,r in zip(p.tc,p.r)]
    return p.groupby(['ex','id']).tva.sum()
s1=CC[CC.id.isin(j.id.dropna().astype(int))]; s2=CC[~CC.id.isin(j.id.dropna().astype(int)) & (CC.tot_ttc!=0)]
gtax=G.groupby('tk').tax_amount_c.sum(); idtk=j.set_index('id')
for lab,df in [('première série',s1),('seconde série (notes non nulles)',s2)]:
    P(f'--- {lab} : notes {df.id.nunique()}')
    base=tva_tickets(df,'rart'); leg=tva_tickets(df,'tl0'); l20=tva_tickets(df,'tl20'); l10=tva_tickets(df,'tl10')
    tt=df.groupby(['ex','id']).tot_tva.first().map(c)
    T=pd.DataFrame(dict(app=base,leg=leg,l20=l20,l10=l10,tot_tva=tt))
    T['mal']=df.assign(m=df.tl0!=df.rart).groupby(['ex','id']).m.any()
    for ex in EX+['3ex']:
        if ex!='3ex' and ex not in T.index.get_level_values(0): continue
        z=T if ex=='3ex' else T.loc[ex]
        dl=z.leg-z.tot_tva; dr=z.leg-z.app
        P(f'  {ex}: Σ tot_tva {e(z.tot_tva.sum())} ; Σ TVA recalculée taux appliqués {e(z.app.sum())} (écart arrondi caisse {e(z.app.sum()-z.tot_tva.sum())}, tickets ≠ {(z.app!=z.tot_tva).sum()}) ; '
          f'TVA légale {e(z.leg.sum())} ; légale − tot_tva : tickets ≠ {(dl!=0).sum()}, + {e(dl[dl>0].sum())}, − {e(dl[dl<0].sum())}, solde {e(dl.sum())} ; '
          f'effet taux pur (légale − appliquée) : tickets ≠ {(dr!=0).sum()} (tickets avec article mal taxé {int(z.mal.sum())}), + {e(dr[dr>0].sum())}, − {e(dr[dr<0].sum())}, solde {e(dr.sum())} ; '
          f'sensibilité indéterminés à 20 % : {e((z.l20-z.app).sum())} ; à 10 % : {e((z.l10-z.app).sum())}')
    if lab=='première série':
        # comparaison à Σ tax_amount G
        gsum={ex:G[G.ex==ex].tax_amount_c.sum() for ex in EX}
        P('  Σ tax_amount G :',{ex:e(v) for ex,v in gsum.items()},' = Σ tot_tva :',{ex:T.loc[ex].tot_tva.sum()==gsum[ex] for ex in EX})
        T.to_pickle(CA+'B5_tickets.pkl')
    # décomposition par article (non arrondie), par exercice
    mm=df[df.tl0!=df.rart]
    dec=mm.assign(v=mm.tot*(mm.tl0/(100+mm.tl0)-mm.rart/(100+mm.rart))).groupby(['ref','lib_s','ex']).agg(lignes=('v','size'),tickets=('id','nunique'),TTC=('tot','sum'),dTVA=('v','sum')).round(2)
    P(dec.to_string())
    P('  Σ décomposition non arrondie par exercice :',dec.groupby('ex').dTVA.sum().round(2).to_dict())
    # indéterminés
    ind=df[df.tl.isna()].groupby(['ref','lib_s','ex','rart']).agg(lignes=('tot','size'),TTC=('tot','sum')).round(2)
    P('  indéterminés :'); P(ind.to_string())
# ---------------- B-6
P('===== B-6')
for lab,df in [('toutes lignes C',CC),('première série',s1)]:
    for col,nm in [('tb','t_brut'),('ts','t_serv')]:
        r=df[col].astype(int)
        lin=[R2(t*q/(100+q)) for t,q in zip(df.tot,r)]
        df=df.assign(_l=lin,_u=df.tot*r/(100+r),_r=r)
        tk=df.groupby(['ex','id','_r']).tot.sum().reset_index(); tk['v']=[R2(t*q/(100+q)) for t,q in zip(tk.tot,tk._r)]
        out=[]
        for ex in EX:
            z=df[df.ex==ex]
            out.append(f'{ex}: ligne {sum(z._l):,.2f} | ticket×taux {tk[tk.ex==ex].v.sum():,.2f} | brut {z._u.sum():,.4f} → {R2(z._u.sum()):,.2f}')
        P(f'  {lab} {nm} : '+' ; '.join(out))
    if lab=='toutes lignes C':
        P('  A + ΣF (colonne F du service) :',{ex:round(R2(df[df.ex==ex].assign(u=df.tot*df.tb/(100+df.tb)).u.sum())+df[df.ex==ex].Fs.sum(),2) for ex in EX},
          ' ; avec A arrondi par ligne :',{ex:round(sum(R2(t*q/(100+q)) for t,q in zip(df[df.ex==ex].tot,df[df.ex==ex].tb))+round(df[df.ex==ex].Fs.sum(),2),2) for ex in EX})
P('  Σ tax_amount G :',{ex:e(G[G.ex==ex].tax_amount_c.sum()) for ex in EX})
# ---------------- B-9
P('===== B-9')
G['d']=(G.pal-G.paltax)/100
for ex in EX:
    z=G[G.ex==ex]; P(f'{ex}: VAT_base non multiple de 0,05 : {(z.VAT_base_c%5!=0).sum()} ; de 0,10 : {(z.VAT_base_c%10!=0).sum()} ; lignes {len(z)} ; max |VAT_base+t−palG_tax| {z.d.abs().max():.4f}')
P('distribution (VAT_base + t − palG_tax), arrondie au 0,01 € :',G.d.round(2).value_counts().sort_index().to_dict())
ex10=G[G.VAT_base_c%5!=0].head(10)
idmap=j.set_index(['ex','dateTicket','noTicket','heureTicket']).id
for _,r in ex10.iterrows():
    i=idmap.get((r.ex,r.dateTicket,r.noTicket,r.heureTicket)); art=CC[(CC.id==i)&(CC.rart==r.r)][['lib_s','qte','pu','tot']].values.tolist()
    P(f'  {r.dateTicket} n°{r.noTicket} {r.heureTicket} taux {r.r} VAT_base {r.VAT_base} palier {r.pal/100:.2f} tax {r.tax_amount} ; articles C {art}')
# ---------------- B-10
P('===== B-10')
neg=G[(G.r==20)&(G.VAT_base_c<0)].merge(j[['ex','dateTicket','noTicket','heureTicket','id']],on=['ex','dateTicket','noTicket','heureTicket'])
c20=CC[CC.rart==20].groupby('id').nat.agg(lambda s: set(s))
neg['nats']=neg.id.map(c20)
neg['alc_only']=neg.nats.map(lambda s: s<= {'autre boisson alcoolique (> 1,2 % vol)','bière (> 0,5 % vol) ou mélange de bière'})
P('lignes négatives à 20 % :',len(neg),' ; paliers 100 % boissons alcooliques :',int(neg.alc_only.sum()),' ; avec ≥1 article non alcoolique ou indéterminé :',int((~neg.alc_only).sum()))
P('  détail des natures non alcooliques présentes :',neg[~neg.alc_only].nats.map(lambda s: tuple(sorted(s))).value_counts().to_dict())
tk=G.groupby('tk').r.agg(lambda s: set(s)); P('tickets sans ligne à 20 % :',int(tk.map(lambda s:20 not in s).sum()),'/',len(tk))
# alcool réel (taux légal) < 20 € par ticket
s1l=s1.assign(alc=np.where(s1.tl0==20,s1.tc,0)).groupby('id').alc.sum()
P('tickets (1re série) avec 0 < alcool légal TTC < 20 € :',int(((s1l>0)&(s1l<2000)).sum()),' ; alcool légal = 0 :',int((s1l==0).sum()),' ; ≥ 20 € :',int((s1l>=2000).sum()),' / ',len(s1l))
# ---------------- B-12
P('===== B-12')
for ex in EX:
    z=G[G.ex==ex].drop_duplicates('tk'); 
    for keys in [['dateTicket','noTicket'],['dateTicket','heureTicket'],['dateTicket','no_zReport','noTicket'],['dateTicket','heureTicket','noTicket']]:
        s=z.sort_values(keys,kind='mergesort'); P(f'  G {ex} tri {keys} reproduit l\'ordre : {(s.index.values==z.index.values).all()}')
    h=H[H.ex==ex]
    for keys in [['date_ticket','no_ticket'],['date_ticket','heure_ticket'],['id']]:
        s=h.sort_values(keys,kind='mergesort'); P(f'  H {ex} tri {keys} reproduit l\'ordre : {(s.index.values==h.index.values).all()}')
    P(f'  G {ex}: transitions tot_sum décroissantes (lignes) {int((z.tot_sum.diff()<0).sum())} (tickets) ; lignes : {int((G[G.ex==ex].tot_sum.diff()<0).sum())}')
# ---------------- B-13
P('===== B-13')
AN={'2022-2023':977739.78,'2023-2024':1381110.20,'2024-2025':1819103.12}
h2=H[H.apply(lambda r: r.tot_sum<AN[r.ex]-1e-6,axis=1)]
for ex in EX:
    z=h2[h2.ex==ex]; nz=z[z.tot_ttc!=0]
    P(f'{ex}: notes seconde série {len(z)} ; non nulles {len(nz)} ; Σ TTC {nz.tot_ttc.sum():.2f} ; Σ TVA {nz.tot_tva.sum():.2f} ; compteur TVA {z.tot_tax_sum.min():.2f} → {z.tot_tax_sum.max():.2f}')
F=pd.read_pickle(C23+'F.pkl'); gid=set(j.id.dropna().astype(int))
nz=h2[h2.tot_ttc!=0].copy(); nz['id']=nz.id.astype(int)
rows=[]
for _,r in nz.iterrows():
    cl=CC[CC.id==r.id]; rows.append([r.id,r.date_ticket,int(r.no_ticket),r.heure_ticket,int(r.no_z_report),r.tot_ttc,r.tot_tva,len(cl),'oui' if (cl.tl0==20).any() else 'non',
         r.id in set(F.id),r.id in gid,len(cl)>0])
T13=pd.DataFrame(rows,columns=['id','date','n°','heure','Z','TTC','TVA','articles','alcool','dans F','dans G','dans C']); P(T13.to_string())
s2t=tva_tickets(CC[CC.id.isin(nz.id)],'rart'); P('  TVA recalculée (taux appliqués) des 17 notes :',e(s2t.sum()),' vs Σ tot_tva',e(int(round(nz.tot_tva.sum()*100))))
# ---------------- B-17
P('===== B-17')
form=CC[CC.lib_s.str.contains('ormule|Menu du jour|FORMULE',regex=True)]
for (ref,lib),g in form.groupby(['ref','lib_s']):
    ids=g.id.unique(); oth=CC[CC.id.isin(ids)&~CC.index.isin(g.index)]
    P(f'{ref} {lib}: lignes {len(g)} ; taux {sorted(g.rart.unique())} ; PU {g.pu.value_counts().head(4).to_dict()} ; notes {len(ids)} ; '
      f'boissons à prix nul dans ces notes : {int(((oth.pu==0)&oth.nat.str.contains("boisson|bière")).sum())} ; boissons alcooliques à prix nul : {int(((oth.pu==0)&(oth.tl0==20)).sum())} ; notes avec boisson alcoolique payante : {oth[oth.tl0==20].id.nunique()}')
