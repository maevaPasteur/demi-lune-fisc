"""Contrôles B-6 (rapprochements journaliers et par ticket), B-7 (ordre et compteurs de H et G), B-8 (identifiants), B-9 (calendrier)."""
import pandas as pd, numpy as np, datetime as dt
CA='scripts/lot6-evenement-reglement/cache/'
c=lambda x:int(round(float(x)*100)); e=lambda n:f"{n/100:,.2f}".replace(',',' ').replace('.',',')
H=pd.read_pickle(CA+'H.pkl'); F=pd.read_pickle(CA+'F.pkl'); G=pd.read_pickle(CA+'G.pkl'); E=pd.read_pickle(CA+'E.pkl')
B=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/B.pkl'); CC=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/CC.pkl')
out=open('scripts/lot6-evenement-reglement/out/t03_jours_ordre_calendrier.txt','w')
def p(*a): print(*a); print(*a,file=out)
# ---- B-6
z9=set(F[F.tot_ttc_c==0].id)
J=pd.DataFrame({'B':B.groupby('date').tot.apply(lambda s:s.map(c).sum()),
 'H1':H[H.serie==1].groupby('date_ticket').tot_ttc_c.sum(),
 'C':CC.groupby('date').tot.apply(lambda s:s.map(c).sum()),
 'F':F.groupby('dateTicket').montant_c.sum(),
 'F_sans9':F[~F.id.isin(z9)].groupby('dateTicket').montant_c.sum(),
 'G':G.drop_duplicates(['dateTicket','heureTicket','noTicket','no_zReport']).groupby('dateTicket').tot_ttc_c.sum()}).fillna(0).astype(int)
p('== B-6. Jours',len(J))
for a,b in [('B','H1'),('B','C'),('H1','C'),('H1','F'),('H1','F_sans9'),('H1','G'),('C','F')]:
    d=J[a]-J[b]; nz=d[d!=0]
    p(f'  {a} − {b} : jours ≠ 0 : {len(nz)} ; écart absolu max {e(nz.abs().max() if len(nz) else 0)} ; Σ|écarts| {e(nz.abs().sum())} ; Σ écarts {e(d.sum())}')
# par ticket série 1
s1=H[(H.serie==1)&(H.tot_ttc_c!=0)].set_index('id')
fs=F.groupby('id').montant_c.sum()
m=s1.tot_ttc_c.to_frame().join(fs.rename('F'))
p('  tickets série 1 non nuls',len(m),' ; sans règlement',int(m.F.isna().sum()),' ; Σ F ≠ tot_ttc',int(((m.F-m.tot_ttc_c).abs()>0).sum()))
p('  tickets série 1 à 0 € avec règlement :',int(H[(H.serie==1)&(H.tot_ttc_c==0)].id.isin(F.id).sum()))
Hd=H.set_index('id')
p('  lignes F dont la date ≠ date du ticket H :',int((F.dateTicket!=F.id.map(Hd.date_ticket)).sum()),' ; heure ≠ :',int((F.heureTicket!=F.id.map(Hd.heure_ticket)).sum()),' ; date de Z ≠ date du ticket (F) :',int((F.dat_z!=F.dateTicket).sum()))
# ---- B-7
p('\n== B-7. Ordre des fichiers et compteurs')
for nm,df,idc,dc,hc,tc in [('H',H,'id','date_ticket','heure_ticket','no_ticket')]:
    for ex,g in df.groupby('ex'):
        g=g.sort_values('ligneXLS')
        p(f'  {nm} {ex} : trié par (date, id) {g[[dc,idc]].apply(tuple,axis=1).is_monotonic_increasing} ; par (date, heure) {(g[dc]+g[hc]).is_monotonic_increasing} ; par (date, n°) {g[[dc,tc]].apply(tuple,axis=1).is_monotonic_increasing}')
for ex,g in G.groupby('ex'):
    g=g.sort_values('ligneXLS'); k=g.drop_duplicates(['dateTicket','heureTicket','noTicket','no_zReport'])
    hh=H[H.ex==ex].sort_values('ligneXLS')
    same=list(zip(k.dateTicket,k.heureTicket,k.noTicket))==list(zip(hh.date_ticket,hh.heure_ticket,hh.no_ticket.astype(int)))
    hh1=hh[hh.tot_ttc_c!=0]; hh1=hh1[hh1.serie==1]
    same1=list(zip(k.dateTicket,k.heureTicket,k.noTicket))==list(zip(hh1.date_ticket,hh1.heure_ticket,hh1.no_ticket.astype(int)))
    p(f'  G {ex} : tickets {len(k)} ; ordre identique à H (tous) {same} ; à H série 1 non nuls {same1}')
X=H[(H.serie==1)&(H.tot_ttc_c!=0)].copy()
for lab,key in [('ordre du fichier',['ex','ligneXLS']),('ordre des id',['id']),('ordre (date, heure, n°)',['date_ticket','heure_ticket','no_ticket'])]:
    Y=X.sort_values(key); inv=(np.diff(Y.tot_sum_c.values)<0)
    p(f'  tot_sum série 1 selon {lab} : inversions {int(inv.sum())}')
    if 0<inv.sum()<=60:
        k=np.where(inv)[0]
        p('    '+' ; '.join(f'{Y.iloc[i].date_ticket} {Y.iloc[i].heure_ticket} n°{Y.iloc[i].no_ticket} ({e(Y.iloc[i].tot_sum_c)}) > {Y.iloc[i+1].heure_ticket} n°{Y.iloc[i+1].no_ticket} ({e(Y.iloc[i+1].tot_sum_c)})' for i in k[:15]))
p('  (c)(d) chaînage : voir s11 (16 605 / 16 605 et 17 / 17, recettes et taxe)')
for ex in ['2022-2023','2023-2024','2024-2025']:
    y=H[(H.serie==2)&(H.ex==ex)]
    first=y.loc[y.tot_tax_sum_c.idxmin()]
    p(f'  (e) taxe série 2 {ex} : ouverture {e(first.tot_tax_sum_c-c(first.tot_tva))} ; clôture {e(y.tot_tax_sum_c.max())}')
p('  (f) voir s06 (tickets 45,70 / 75,40 + 36,40 / 118,60 ; ids 53892 ; 60886, 60894 ; 67675 ; dernières lignes ids :',[int(H[H.ex==ex].sort_values("ligneXLS").iloc[-1].id) for ex in ['2022-2023','2023-2024','2024-2025']],')')
p('  (g) export natif au dossier : SOURCE-reglement-brut (règlements) seulement ; il ne contient aucune ligne TOTAL ni « Différence somme » ; les natifs ticket et tva sont absents')
# ---- B-8
p('\n== B-8. Identifiants (voir s02, s03)')
Hs=H.sort_values('id'); p('  H : id',H.id.min(),'à',H.id.max(),' ; manquants 1 158 (s03) ; inversions (date, heure de clôture) dans l\'ordre des id :',int(((Hs.date_ticket+Hs.heure_ticket).values[1:]<(Hs.date_ticket+Hs.heure_ticket).values[:-1]).sum()))
Es=E.sort_values('id'); p('  E : inversions (date, heure) dans l\'ordre des id :',int(((Es.dateEven+Es.heureEven).values[1:]<(Es.dateEven+Es.heureEven).values[:-1]).sum()))
miss=pd.read_csv if False else None
# ---- B-9
p('\n== B-9. Calendrier')
days=sorted(set(H.date_ticket)); zs=H.groupby('date_ticket').no_z_report.agg(['min','max','nunique'])
p('  premier jour',days[0],'Z',zs.loc[days[0],'min'],' ; dernier',days[-1],'Z',zs.loc[days[-1],'max'],' ; jours',len(days),' ; Z distincts',H.no_z_report.nunique(),' ; Z continus',H.no_z_report.max()-H.no_z_report.min()+1==H.no_z_report.nunique(),' ; jours à plusieurs Z',int((zs['nunique']>1).sum()))
allday=pd.date_range('2022-04-01','2025-03-31').strftime('%Y-%m-%d'); off=[d for d in allday if d not in set(days)]
p('  jours sans Z :',len(off))
# regrouper en périodes
per=[]; s=None; prev=None
for d in off:
    dd=dt.date.fromisoformat(d)
    if s is None: s=dd
    elif (dd-prev).days>1: per.append((s,prev)); s=dd
    prev=dd
per.append((s,prev))
p('  périodes sans Z de 4 jours ou plus :',[(a.isoformat(),b.isoformat(),(b-a).days+1) for a,b in per if (b-a).days>=3])
wd=pd.Series([dt.date.fromisoformat(d).strftime('%a') for d in off]).value_counts().to_dict(); p('  jours sans Z par jour de semaine :',wd)
for y in [2022,2023,2024]:
    p(f'  1er au 13 avril {y} : jours avec Z',[d for d in days if d.startswith(f'{y}-04-') and int(d[8:])<=13])
out.close()
