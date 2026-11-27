"""B0 point 5 : lecture des couverts des pièces 11, 12, 92 (Services (source)), 93 (Jour par jour) et comparaison entre elles.
Sortie : out/s08_couverts_pieces.txt ; out/B0cache/P11.pkl, P12.pkl, S92.pkl, J93.pkl"""
import openpyxl, pandas as pd, numpy as np
D='scripts/lot7-tables-virtuelles/cache/entrees/lot27/'; O='scripts/lot7-tables-virtuelles/out/'
out=open(O+'B0_s08_couverts_pieces.txt','w')
def p(*a): print(*a); print(*a,file=out)
def sheet(f,s,hdr,start):
    ws=openpyxl.load_workbook(D+f,data_only=True)[s]
    rows=[r for r in ws.iter_rows(min_row=start,values_only=True) if r[0] is not None]
    return pd.DataFrame(rows,columns=hdr)
P11=sheet('11-rf-encaissements-couverts.xlsx','Encaissements couverts',['date','heure','id','ex','cv'],3)
p('P11 lignes non numériques :',P11[pd.to_numeric(P11.cv,errors='coerce').isna()].values.tolist())
P11=P11[pd.to_numeric(P11.cv,errors='coerce').notna()].copy(); P11['cv']=P11.cv.astype(float); P11['id']=P11.id.astype(int)
P12=sheet('12-rf-couverts-par-service.xlsx','Couverts par service',['date','ex','midi','soir','tot','notes'],3)
S92=pd.read_excel(O+'B0_pieces_recalc/92-R2-tables-virtuelles-rangs-de-note-659-journees-tickets-zero-occupation.xlsx',sheet_name='Services (source)')
S92.columns=['ex','date','service','espace','places','cv','occ']
J93=pd.read_excel(D+'93-R1-numeros-de-note-couverts-et-occupation-jour-par-jour.xlsx',sheet_name='Jour par jour')
p('P11 notes :',len(P11),' Id distincts',P11.id.nunique(),' couverts',P11.cv.sum(),' notes à 0 couvert',(P11.cv==0).sum())
A=pd.read_pickle(O+'B0cache/A.pkl')
p('  Id de C absents de P11 :',(~A.id.isin(P11.id)).sum(),' ; Id de P11 absents de C :',(~P11.id.isin(A.id)).sum())
miss=A[~A.id.isin(P11.id)]; p(miss[['date','no','heure','id','tot']].to_string())
p('  doublons (date,heure) ?',P11.duplicated(['id']).sum())
p('  P12 lignes non date :',P12[~P12.date.astype(str).str.match(r'^20\d\d-')].values.tolist())
P12=P12[P12.date.astype(str).str.match(r'^20\d\d-')].copy()
for c in ['midi','soir','tot']: P12[c]=P12[c].astype(float)
p('P12 lignes :',len(P12),' midi',P12.midi.sum(),' soir',P12.soir.sum(),' total',P12.tot.sum(),' jours distincts',P12.date.nunique())
p('  lignes non date :',P12[~P12.date.astype(str).str.match(r'^20\d\d-')].values.tolist())
P12=P12[P12.date.astype(str).str.match(r'^20\d\d-')].copy()
p('S92 :',len(S92),' couverts',S92.cv.sum(),' services midi/soir',S92.service.value_counts().to_dict(),' espaces',S92.espace.value_counts().to_dict(),' jours',S92.date.nunique())
p('  places par espace :',S92.groupby('espace').places.unique().to_dict(),' ; services à 0 couvert :',(S92.cv==0).sum(),' ; couverts non entiers :',(S92.cv%1!=0).sum())
p('J93 :',len(J93),' couverts',J93.Couverts.sum(),' services',J93['Nb de services'].sum(),' espaces',J93['Espace ouvert'].value_counts().to_dict())
# comparaison S92 vs P12 (midi/soir)
m=P12.melt(id_vars=['date'],value_vars=['midi','soir'],var_name='service',value_name='cv12')
x=S92.merge(m,on=['date','service'],how='outer')
p('S92 vs P12 : services S92',len(S92),' ; P12 midi/soir non nuls',(m.cv12>0).sum(),' ; écarts',(x.cv!=x.cv12).sum())
p(x[(x.cv!=x.cv12)].head(20).to_string())
# J93 vs S92
j=J93.rename(columns={'Date':'date','Couverts midi':'midi','Couverts soir':'soir','Espace ouvert':'esp'}).melt(id_vars=['date','esp'],value_vars=['midi','soir'],var_name='service',value_name='cv93')
y=S92.merge(j,on=['date','service'],how='outer')
p('S92 vs J93 : écarts couverts',((y.cv!=y.cv93)&~(y.cv.isna()&(y.cv93==0))).sum(),' ; écarts espace',((y.espace!=y.esp)&y.espace.notna()).sum())
p(y[((y.cv!=y.cv93)&~(y.cv.isna()&(y.cv93==0)))].head(20).to_string())
# P11 agrégé par jour vs P12
P11['t']=P11.heure.map(lambda h:int(h[:2])*60+int(h[3:]))
P11['service']=np.where(P11.t<18*60,'midi','soir')
g=P11.groupby(['date','service']).cv.sum().reset_index()
z=g.merge(m,on=['date','service'],how='outer')
p('P11 agrégé (heure<18h = midi) vs P12 : écarts',(~np.isclose(z.cv.fillna(0),z.cv12.fillna(0))).sum(),' ; total P11',P11.cv.sum())
p(z[~np.isclose(z.cv.fillna(0),z.cv12.fillna(0))].head(20).to_string())
# espace : règle calendaire ?
S92['mois']=S92.date.str[5:7]; S92['an']=S92.date.str[:4]
p('Espace par mois et année :'); p(pd.crosstab([S92.an,S92.mois],S92.espace).to_string())
for k,v in [('P11',P11),('P12',P12),('S92',S92),('J93',J93)]: v.to_pickle(O+f'B0cache/{k}.pkl')
out.close()
