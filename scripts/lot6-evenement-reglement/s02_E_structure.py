"""M0-1 : structure du fichier E (journal tpvevenement) et liens possibles avec C, F, H.
Relit les xls primaires (pas les caches) pour E, F, H ; C depuis le cache 2.3 contrôlé contre les pieds.
Sortie : out/s02_E_structure.txt ; cache/E.pkl, H.pkl, F.pkl"""
import xlrd, pandas as pd, numpy as np, sys
D='public/documents/caisse-enregistreuse/'; CA='scripts/lot6-evenement-reglement/cache/'
EX=['2022-2023','2023-2024','2024-2025']
out=open('scripts/lot6-evenement-reglement/out/s02_E_structure.txt','w')
def p(*a):
    print(*a); print(*a,file=out)
c=lambda x:int(round(float(x)*100))
# ---------- E
Es=[];Ef={}
for ex,f in zip(EX,['14-annexe-e1-2022-2023.xls','15-annexe-e2-2023-2024.xls','16-annexe-e3-2024-2025.xls']):
    s=xlrd.open_workbook(D+f).sheet_by_index(0); hdr=s.row_values(0); rows=[];ft=[]
    for r in range(1,s.nrows):
        v=s.row_values(r)
        if v[1]=='Nb lignes': ft.append(v); continue
        if v[0]=='': continue
        rows.append(v+[r+1])
    df=pd.DataFrame(rows,columns=hdr+['ligneXLS']); df['ex']=ex; Es.append(df); Ef[ex]=ft
E=pd.concat(Es,ignore_index=True)
for k in ['noCaisse','no_zEport','mf_Number','id']: E[k]=E[k].astype(float).astype(int)
E['amount_c']=E.amount.map(c); E['t']=E.heureEven.map(lambda h:int(h[:2])*60+int(h[3:5]))
E.to_pickle(CA+'E.pkl')
p('E colonnes :',list(E.columns[:10]))
p('E lignes',len(E),' par exercice',E.groupby('ex').size().to_dict())
for col in ['noCaisse','mf_Number','caissier','caissier_droit']:
    p(f'  {col} :',E[col].value_counts(dropna=False).to_dict())
p('  caissier_droit vide par type :',E[E.caissier_droit==''].typEven.value_counts().to_dict())
t=E.pivot_table(index='typEven',columns='ex',values='amount_c',aggfunc=['size','sum'],fill_value=0)
p(t.to_string())
p('  cumul par type :',E.groupby('typEven').size().to_dict(),' montant cumulé DEL (c) :',E[E.typEven=='DEL'].amount_c.sum())
for ex in EX: p('  pied',ex,[[x for x in r if x!=''] for r in Ef[ex]])
p('  id E : min',E.id.min(),'max',E.id.max(),' n',len(E),' distincts',E.id.nunique(),' croissant',E.id.is_monotonic_increasing,
  ' trous',int(E.id.max()-E.id.min()+1-E.id.nunique()))
p('  frontières d\'exercice :',[(ex,int(g.id.min()),int(g.id.max()),g.dateEven.min(),g.dateEven.max()) for ex,g in E.groupby('ex')])
p('  E montants négatifs / nuls par type :',E.assign(s=np.sign(E.amount_c)).groupby(['typEven','s']).size().to_dict())
# ordre chronologique de E
E['dt']=E.dateEven+' '+E.heureEven
p('  E trié par (date,heure) selon id :',bool((E.sort_values('id').dt.values[1:]>=E.sort_values('id').dt.values[:-1]).all()),
  ' inversions',int((E.sort_values('id').dt.values[1:]<E.sort_values('id').dt.values[:-1]).sum()))
# ---------- H
Hs=[];Hf={}
for ex,f in zip(EX,['ANNEXE-H1_liste-tickets_2022-2023.xls','ANNEXE-H2_liste-tickets_2023-2024.xls','ANNEXE-H3_liste-tickets_2024-2025.xls']):
    s=xlrd.open_workbook(D+f).sheet_by_index(0); hdr=s.row_values(0); rows=[]; ft=[]
    for r in range(1,s.nrows):
        v=s.row_values(r)
        if str(v[0])[:2]=='20': rows.append(v+[r+1])
        else: ft.append((r+1,v))
    df=pd.DataFrame(rows,columns=hdr+['ligneXLS']); df['ex']=ex; Hs.append(df); Hf[ex]=ft
H=pd.concat(Hs,ignore_index=True)
for k in ['no_ticket','no_z_report','id']: H[k]=H[k].astype(float).astype(int)
for k in ['tot_ttc','tot_tva','tot_sum','tot_tax_sum']: H[k+'_c']=H[k].map(c)
H['t']=H.heure_ticket.map(lambda h:int(h[:2])*60+int(h[3:5]))
H.to_pickle(CA+'H.pkl'); pd.to_pickle(Hf,CA+'H_foot.pkl')
p('\nH colonnes :',hdr,' lignes',len(H),H.groupby('ex').size().to_dict())
p('  id H : min',H.id.min(),'max',H.id.max(),' distincts',H.id.nunique(),' ids manquants dans l\'intervalle',int(H.id.max()-H.id.min()+1-H.id.nunique()))
# ---------- F
Fs=[]
for ex,f in zip(EX,['20-annexe-f1-2022-2023.xls','21-annexe-f2-2023-2024.xls','22-annexe-f3-2024-2025.xls']):
    s=xlrd.open_workbook(D+f).sheet_by_index(0); hdr=s.row_values(0); rows=[]
    for r in range(1,s.nrows):
        v=s.row_values(r)
        if v[0]=='': continue
        rows.append(v+[r+1])
    df=pd.DataFrame(rows,columns=hdr+['ligneXLS']); df['ex']=ex; Fs.append(df)
F=pd.concat(Fs,ignore_index=True)
for k in ['no_ticket','no_zReport','id']: F[k]=F[k].astype(float).astype(int)
F['montant_c']=F.montant.map(c); F['tot_ttc_c']=F.tot_ttc.map(c)
F.to_pickle(CA+'F.pkl')
CC=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/CC.pkl')
p('\nIdentifiants : E',E.id.min(),'-',E.id.max(),' | notes H',H.id.min(),'-',H.id.max(),' | C',CC.id.min(),'-',CC.id.max(),' | F',F.id.min(),'-',F.id.max())
inter=set(E.id)&set(H.id)
p('  valeurs numériques communes id(E) ∩ id(H) :',len(inter),' (chevauchement d\'intervalles',max(E.id.min(),H.id.min()),'-',min(E.id.max(),H.id.max()),')')
# test : id E commun avec id H : même objet ? (date égale ?)
Hi=H.set_index('id'); Ei=E.set_index('id')
same_date=sum(1 for i in inter if Hi.date_ticket[i]==Ei.dateEven[i])
p('  parmi elles, même date E/H :',same_date,' (un identifiant partagé désignerait le même objet : il ne le fait pas)')
p('  ids C ⊂ H :',set(CC.id)<=set(H.id),' ids F ⊂ H :',set(F.id)<=set(H.id),' ids C absents de F :',len(set(CC.id)-set(F.id)),' ids F absents de C :',len(set(F.id)-set(CC.id)))
# Z : correspondance (date, Z) entre E et H
zE=set(zip(E.dateEven,E.no_zEport)); zH=set(zip(H.dat_z,H.no_z_report)); zHd=set(zip(H.date_ticket,H.no_z_report))
p('  couples (date,Z) : E',len(zE),' H (dat_z)',len(zH),' E∖H',len(zE-zH),' H∖E',len(zH-zE))
p('  Z distincts E',E.no_zEport.nunique(),' H',H.no_z_report.nunique(),' Z min/max E',E.no_zEport.min(),E.no_zEport.max(),' H',H.no_z_report.min(),H.no_z_report.max())
zmapE=E.groupby('no_zEport').dateEven.nunique(); p('  Z de E sur plusieurs dates :',int((zmapE>1).sum()))
p('  E∖H (date,Z) :',sorted(zE-zH)[:20])
p('  H∖E (date,Z) :',sorted(zH-zE)[:20])
DEL=E[E.typEven=='DEL']
p('  DEL dont (date,Z) existe dans H :',int(sum((d,z) in zH for d,z in zip(DEL.dateEven,DEL.no_zEport))),'/',len(DEL))
# ids de notes manquants
allid=set(range(H.id.min(),H.id.max()+1)); miss=sorted(allid-set(H.id))
p('  ids de notes absents de H dans l\'intervalle :',len(miss),' exemples',miss[:15])
Hs_=H.sort_values('id').reset_index(drop=True)
gaps=Hs_.id.diff().fillna(1).astype(int)-1
p('  tailles des trous (nb d\'ids manquants entre deux notes successives) :',gaps[gaps>0].value_counts().sort_index().to_dict())
p('  trous par exercice :',Hs_[gaps>0].groupby('ex').apply(lambda g:int(gaps[g.index].sum())).to_dict())
# ordre H : id croissant vs chronologique
Hs_['dt']=Hs_.date_ticket+' '+Hs_.heure_ticket
p('  H par id : inversions chronologiques',int((Hs_.dt.values[1:]<Hs_.dt.values[:-1]).sum()))
p('  H ordre du fichier : id croissant ?',bool(H.id.is_monotonic_increasing),' inversions d\'id dans l\'ordre du fichier',int((H.id.values[1:]<H.id.values[:-1]).sum()))
out.close()
