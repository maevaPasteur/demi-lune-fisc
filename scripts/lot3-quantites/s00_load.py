"""Chargement des annexes B, E et F du service et des reprises de l'annexe C (onglet « Lignes C » de la pièce n° 78 en version R2,
onglets « Sources_C-1 » à « Sources_C-3 » de la pièce n° 89). Sortie : cache/*.pkl"""
import xlrd, openpyxl, pandas as pd, numpy as np, datetime as dt
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import C, EX, annexe, PIECE_78, PIECE_89
def xl2date(x):
    return (dt.datetime(1899,12,30)+dt.timedelta(days=float(x)))
# ---- B
Bs=[]
for ex,f in zip(EX,[annexe('B',k) for k in (1,2,3)]):
    s=xlrd.open_workbook(f).sheet_by_index(0)
    rows=[]; foot=None
    for r in range(1,s.nrows):
        v=s.row_values(r)
        if v[0]=='' :
            if v[5]!='': foot=v
            continue
        rows.append(v)
    df=pd.DataFrame(rows,columns=['date','caisse','ticket','ref','lib','qte','unite','pu','marge','tot','A','B'])
    df['datetime']=df['date'].map(xl2date); df['date']=df['datetime'].dt.strftime('%Y-%m-%d')
    df['ticket']=df['ticket'].astype(float).astype(int)
    df['ex']=ex; df['rowB']=np.arange(len(df))+2  # ligne Excel
    Bs.append(df)
    print(ex,'B lignes',len(df),'pied',foot)
    pd.to_pickle(foot,C+f'B_foot_{ex}.pkl')
B=pd.concat(Bs,ignore_index=True); B.to_pickle(C+'B.pkl')
# ---- F
Fs=[]
for ex,f in zip(EX,[annexe('F',k) for k in (1,2,3)]):
    s=xlrd.open_workbook(f).sheet_by_index(0)
    hdr=s.row_values(0); rows=[]; foot=[]
    for r in range(1,s.nrows):
        v=s.row_values(r)
        if v[0]=='': foot.append(v); continue
        rows.append(v)
    df=pd.DataFrame(rows,columns=hdr); df['ex']=ex; df['rowF']=np.arange(len(df))+2
    for c in ['no_ticket','no_zReport','id']: df[c]=df[c].astype(float).astype(int)
    Fs.append(df); print(ex,'F lignes',len(df),'pied',foot)
F=pd.concat(Fs,ignore_index=True); F.to_pickle(C+'F.pkl')
# ---- E
Es=[]
for ex,f in zip(EX,[annexe('E',k) for k in (1,2,3)]):
    s=xlrd.open_workbook(f).sheet_by_index(0)
    hdr=s.row_values(0); rows=[]; foot=[]
    for r in range(1,s.nrows):
        v=s.row_values(r)
        if v[1]=='Nb lignes' or v[0]=='' : foot.append(v); continue
        rows.append(v)
    df=pd.DataFrame(rows,columns=hdr); df['ex']=ex; df['rowE']=np.arange(len(df))+2
    Es.append(df); print(ex,'E lignes',len(df),'pied',foot)
E=pd.concat(Es,ignore_index=True); E.to_pickle(C+'E.pkl')
# ---- 89 Sources_C
wb=openpyxl.load_workbook(PIECE_89,read_only=True)
Cs=[]
for i,ex in enumerate(EX):
    ws=wb[f'Sources_C-{i+1}']
    rows=list(ws.iter_rows(values_only=True))
    df=pd.DataFrame(rows[1:],columns=['caC','puC','qteC','remC','tvaC','errTVA','corTVA']); df['ex']=ex
    Cs.append(df); print(ex,'Sources_C',len(df))
SC=pd.concat(Cs,ignore_index=True); SC.to_pickle(C+'SC.pkl')
# ---- 78 Lignes C
wb=openpyxl.load_workbook(PIECE_78,read_only=True)
rows=list(wb['Lignes C'].iter_rows(values_only=True))
LC=pd.DataFrame(rows[1:],columns=['ex','date','note','id','lib','pu','qte','enc','colC','colD','statut','table','f1','f2','f3'])
LC=LC.drop(columns=['f1','f2','f3']); LC['rowLC']=np.arange(len(LC))+2
LC.to_pickle(C+'LC.pkl'); print('Lignes C',len(LC))
