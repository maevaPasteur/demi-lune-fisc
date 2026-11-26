"""M0-2 : 2.6.4 c (tableau 62, 37 notes à 0 €, etat = 9 de l'export natif) ; p. 25 (comptes 511 / 530) par mode et par exercice ;
décomposition des 5 355,78 € et des 7 023,10 € de 2023-2024 ; nature des montants CHV/TR de F."""
import pandas as pd, numpy as np, xml.etree.ElementTree as ET
from collections import Counter
CA='scripts/lot6-evenement-reglement/cache/'
EX=['2022-2023','2023-2024','2024-2025']
c=lambda x:int(round(float(x)*100)); e=lambda n:f"{n/100:,.2f}".replace(',',' ').replace('.',',')
out=open('scripts/lot6-evenement-reglement/out/s07_reglements.txt','w')
def p(*a):
    print(*a); print(*a,file=out)
F=pd.read_pickle(CA+'F.pkl'); H=pd.read_pickle(CA+'H.pkl')
# ---- tableau 62
T=F.groupby(['mod_regl','ex']).montant_c.sum().unstack(fill_value=0); T['cumul']=T.sum(axis=1)
tot=T.sum(); T.loc['TOTAL']=tot
T['part %']=(T.cumul/tot.cumul*100).round(2)
p('Tableau 62 recalculé (centimes) :'); p(T.to_string())
p('Lignes F par mode :',F.groupby('mod_regl').size().to_dict(),' lignes négatives :',F[F.montant_c<0].groupby('mod_regl').size().to_dict(),' nulles :',int((F.montant_c==0).sum()))
# ---- notes / séries
Hs=H.set_index('id')
F['serie']=F.id.map(Hs.serie); F['Htot']=F.id.map(Hs.tot_ttc_c)
p('\nF : ids absents de H :',int(F.serie.isna().sum()))
z=F[F.tot_ttc_c==0]
p('Règlements sur notes à 0 € : lignes',len(z),' notes',z.id.nunique(),' Σ',e(z.montant_c.sum()),' par exercice',{k:e(v) for k,v in z.groupby('ex').montant_c.sum().items()},
  ' notes par exercice',z.groupby('ex').id.nunique().to_dict(),' série',z.serie.value_counts().to_dict(),' par mode',{k:e(v) for k,v in z.groupby(['ex','mod_regl']).montant_c.sum().items()})
p('  première et dernière date :',z.dateTicket.min(),z.dateTicket.max())
nz=F[F.tot_ttc_c!=0]
per=nz.groupby('id').agg(m=('montant_c','sum'),t=('tot_ttc_c','first'))
p('Notes ≠ 0 dans F :',len(per),' Σ règlements = tot_ttc note par note :',int((per.m==per.t).sum()),' écarts :',int((per.m!=per.t).sum()))
for ex in EX:
    s1=H[(H.serie==1)&(H.ex==ex)].tot_ttc_c.sum(); f=F[F.ex==ex].montant_c.sum(); f0=z[z.ex==ex].montant_c.sum()
    p(f'  {ex} : F {e(f)} − série 1 {e(s1)} = {e(f-s1)} ; règlements notes à 0 € {e(f0)} ; F hors notes à 0 € − série 1 = {e(f-f0-s1)}')
p('  notes série 1 ≠0 absentes de F :',int(((H.serie==1)&(H.tot_ttc_c!=0)&(~H.id.isin(F.id))).sum()),' ; notes de F en série 2 non nulles :',int(((F.serie==2)&(F.tot_ttc_c!=0)).sum()))
# ---- export natif
P='/mnt/user-data/uploads/demi-lune-comptabilite/public/documents/caisse-enregistreuse/SOURCE-reglement-brut_2022-2025.xls'
ns='{urn:schemas-microsoft-com:office:spreadsheet}'
rows=[]
for r in ET.parse(P).getroot().iter(ns+'Row'):
    vals=[]
    for cell in r.findall(ns+'Cell'):
        idx=cell.get(ns+'Index')
        if idx:
            while len(vals)<int(idx)-1: vals.append(None)
        d=cell.find(ns+'Data'); vals.append(d.text if d is not None else None)
    rows.append(vals)
hdr=rows[0]; S=pd.DataFrame([r+[None]*(len(hdr)-len(r)) for r in rows[1:]],columns=hdr)
S.to_pickle(CA+'SOURCE.pkl')
p('\nExport natif : lignes',len(S),' colonnes',hdr)
S['id_']=S.id.astype(float).astype(int); S['m_c']=S.montant.astype(float).map(c); S['t_c']=S.tot_ttc.astype(float).map(c)
same=list(zip(F.id,F.dateTicket,F.heureTicket,F.no_ticket,F.no_zReport,F.mod_regl,F.montant_c,F.tot_ttc_c))==list(zip(S.id_,S.date_ticket,S.heure_ticket,S.no_ticket.astype(float).astype(int),S.no_z_report.astype(float).astype(int),S.mod_regl,S.m_c,S.t_c))
p('F (3 fichiers concaténés) identique au natif ligne à ligne sur id, date, heure, n°, Z, mode, montant, tot_ttc :',same)
p('Colonnes du natif absentes de F :',[h for h in hdr if h not in ['date_ticket','heure_ticket','no_ticket','dat_z','no_z_report','tot_ttc','tot_tva','id','mod_regl','montant','tot_rem_globale']])
for k in ['etat','(null)','mf_number','mf_desc','cod_clt','tot_rem_lig','no_caisse','caissier']:
    p(f'  {k} :',S[k].value_counts(dropna=False).head(6).to_dict())
p('  etat × (tot_ttc = 0) :',S.groupby([S.etat,S.t_c==0]).size().to_dict())
z9=S[S.etat=='9']; p('  etat = 9 : lignes',len(z9),' notes',z9.id_.nunique(),' Σ',e(z9.m_c.sum()),' toutes à tot_ttc 0 :',bool((z9.t_c==0).all()),' ; lignes à tot_ttc 0 hors etat 9 :',int(((S.t_c==0)&(S.etat!='9')).sum()))
# sy_uk
p('  sy_uk distincts',S.sy_uk.nunique(),' exemples',S.sy_uk.head(3).tolist())
# tot_sum natif des notes à 0 (série ?)
p('  tot_sum des lignes etat 9 (min-max) :',S[S.etat=='9'].tot_sum.astype(float).min(),S[S.etat=='9'].tot_sum.astype(float).max())
# ---- p. 25 : comptabilité par mode
P25={ # (brut, ajustement) imprimés p. 25 ; None si brut non imprimé ; net imprimé
 '511200 CHQ':[(5194.65,-567.30,4627.35),(3522.56,77.56,3600.12),(4754.10,-225.00,4529.10)],
 '511210 CB':[(None,None,370144.08),(None,None,399903.10),(397666.38,11.00,397677.38)],
 '511220 TR':[(9620.50,-134.18,9486.32),(9112.36,-7.32,9105.04),(None,None,4708.89)],
 '511221 TR dém.':[(None,None,935.10),(2240.05,-1215.73,1024.27),(None,None,4392.72)],
 '511230 CHV':[(14934.50,-219.50,14715.00),(23026.62,273.38,23300.00),(20203.00,202.00,20405.00)],
 '511240 KDOLE':[(None,None,290.00),(None,None,525.00),(None,None,390.00)],
 '530 caisse':[(3390.65,538.02-598.04,3330.63),(6010.43,546.22-597.75,5958.90),(3613.09,-151.77-656.57,2804.75)]}
TOTP=[403528.48,443416.43,434907.84]
p('\np. 25 : contrôle brut + ajustement = net, et total')
for k,v in P25.items():
    p(' ',k,[ (round(b+a,2)==n if b is not None else 'brut non imprimé') for b,a,n in v])
for i,ex in enumerate(EX):
    s=round(sum(v[i][2] for v in P25.values()),2); p(f'  {ex} Σ nets {s} ; total imprimé {TOTP[i]} ; écart {round(s-TOTP[i],2)}')
MAP={'CB':['511210 CB'],'CHQ':['511200 CHQ','511240 KDOLE'],'TR':['511220 TR','511221 TR dém.'],'CHV':['511230 CHV'],'ESP':['530 caisse']}
P26={'706000':[64712.51,72416.55,70517.47],'706300':[296105.87,319179.31,318345.43],'706800':[598.04,597.75,656.57],'445710':[42614.45,46464.79,46005.45],'TOT':[404030.87,438658.43,435524.92]}
rows=[]
for i,ex in enumerate(EX):
    for m,ks in MAP.items():
        comp=c(sum(P25[k][i][2] for k in ks)); f=F[(F.ex==ex)&(F.mod_regl==m)].montant_c.sum(); f0=z[(z.ex==ex)&(z.mod_regl==m)].montant_c.sum()
        rows.append((ex,m,comp,f,comp-f,f0,comp-(f-f0)))
R=pd.DataFrame(rows,columns=['ex','mode','compta','F','compta−F','F notes à 0','compta−(F−notes0)'])
R2=R.groupby('ex').sum(numeric_only=True); R2['mode']='TOTAL'; R=pd.concat([R,R2.reset_index()]).sort_values(['ex','mode'])
p('\nComptabilité p. 25 (KDOLE en CHQ, TR = 511220 + 511221, ESP = 530 net) contre F, par mode (centimes) :'); p(R.to_string(index=False))
p('\nDécomposition par exercice : encaissements comptables (511 + 530) − CA comptable hors 706800 (somme des lignes p. 26)')
for i,ex in enumerate(EX):
    enc=c(TOTP[i]); ca=c(P26['706000'][i]+P26['706300'][i]+P26['445710'][i]); f=F[F.ex==ex].montant_c.sum(); f0=z[z.ex==ex].montant_c.sum()
    s1=H[(H.serie==1)&(H.ex==ex)].tot_ttc_c.sum()
    p(f'  {ex} : enc {e(enc)} − CA {e(ca)} = {e(enc-ca)} = (enc − F) {e(enc-f)} + (F − série 1, notes à 0 €) {e(f-s1)} + (série 1 − CA compta) {e(s1-ca)}  [contrôle {e((enc-f)+(f-s1)+(s1-ca))}]')
    p(f'      total p. 26 imprimé {e(c(P26["TOT"][i]))} ; somme de ses lignes {e(c(P26["706000"][i]+P26["706300"][i]+P26["706800"][i]+P26["445710"][i]))}')
# ---- montants CHV / TR de F : entiers ? multiples ?
for m in ['CHV','TR','CB','ESP','CHQ']:
    x=F[F.mod_regl==m].montant_c
    p(f'  F {m} : lignes {len(x)} ; montants entiers (en euros) {int((x%100==0).sum())} ({(x%100==0).mean()*100:.1f} %) ; multiples de 5 € {int((x%500==0).sum())}')
# notes payées en plusieurs modes avec CHV
mix=F.groupby('id').mod_regl.apply(lambda s:tuple(sorted(set(s))))
p('  combinaisons de modes par note (top) :',mix.value_counts().head(10).to_dict())
p('  CHV par exercice : lignes',F[F.mod_regl=="CHV"].groupby('ex').size().to_dict(),' montant moyen',{k:round(v/100,2) for k,v in F[F.mod_regl=="CHV"].groupby('ex').montant_c.mean().items()})
out.close()
