"""s00 : chargement des annexes de caisse C-1 à C-3 (détail des tickets), G-1 à G-3 (journal de TVA), H-1 à H-3 (liste des
tickets), F-1 à F-3 (règlements) et E-1 à E-3 (événements). Sorties : cache/CC.pkl, G.pkl, H.pkl, F.pkl, E.pkl (et pieds de page).
Mêmes règles de lecture que la chaîne scripts/lot3-quantites (s30_loadC.py, c1_loadG.py, m1_B07.py, s00_load.py)."""
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
# ---- C
cols=['date','heure','ticket','datz','z','tot_ttc','tot_tva','tot_rem','id','ref','lib','qte','unite','pu','disc','tva','tot','A','Bs','Cs','Ds','Es','Fs','Gs']
Cs=[]; foots={}
for ex,f in zip(EX,CF):
    s=xlrd.open_workbook(f).sheet_by_index(0); rows=[]
    for r in range(1,s.nrows):
        v=s.row_values(r)
        if v[2]=='TOTAL': foots[ex]=v; continue
        if v[0]=='': continue
        rows.append(v)
    df=pd.DataFrame(rows,columns=cols); df['ex']=ex; df['rowC']=np.arange(len(df))+2
    for k in ['ticket','z','id']: df[k]=df[k].astype(float).astype(int)
    for k in ['Cs','Ds','Fs','Gs']: df[k]=pd.to_numeric(df[k].replace('',np.nan),errors='coerce')
    Cs.append(df); print(ex,'C lignes',len(df))
CC=pd.concat(Cs,ignore_index=True); CC['lib_s']=CC.lib.astype(str).str.strip()
CC['frac']=(CC.qte-CC.qte.round()).abs()>1e-9
CC.to_pickle(CA+'CC.pkl'); pd.to_pickle(foots,CA+'C_foot.pkl')
# ---- G
Gs=[]; foots={}
for ex,f in zip(EX,GF):
    s=xlrd.open_workbook(f).sheet_by_index(0); hdr=s.row_values(0); rows=[]; ft=[]
    for r in range(1,s.nrows):
        v=s.row_values(r)
        if str(v[0])[:2]=='20': rows.append(v)
        else: ft.append(v)
    g=pd.DataFrame(rows,columns=hdr); g['ex']=ex; g['rowG']=range(len(g)); Gs.append(g); foots[ex]=ft
    print(ex,'G lignes',len(g))
G=pd.concat(Gs,ignore_index=True)
for k in ['noTicket','no_zReport']: G[k]=G[k].astype(float).astype(int)
for k in ['tot_ttc','tot_tva','tot_sum','tot_tax_sum','tot_remGlobale','taux_tva%','VAT_base','tax_amount']: G[k]=pd.to_numeric(G[k],errors='coerce')
G['t']=G.heureTicket.map(tmin)
G.to_pickle(CA+'G.pkl'); pd.to_pickle(foots,CA+'G_foot.pkl')
# ---- H
Hs=[]
for ex,f in zip(EX,HF):
    s=xlrd.open_workbook(f).sheet_by_index(0); hdr=s.row_values(0)
    rows=[s.row_values(r) for r in range(1,s.nrows) if str(s.row_values(r)[0])[:2]=='20']
    h=pd.DataFrame(rows,columns=hdr); h['ex']=ex; Hs.append(h); print(ex,'H lignes',len(h))
H=pd.concat(Hs,ignore_index=True); H['t']=H.heure_ticket.map(tmin); H['no']=H.no_ticket.astype(float).astype(int)
H.to_pickle(CA+'H.pkl')
# ---- F
Fs=[]
for ex,f in zip(EX,FF):
    s=xlrd.open_workbook(f).sheet_by_index(0); hdr=s.row_values(0); rows=[]
    for r in range(1,s.nrows):
        v=s.row_values(r)
        if v[0]=='': continue
        rows.append(v)
    df=pd.DataFrame(rows,columns=hdr); df['ex']=ex; df['rowF']=np.arange(len(df))+2
    for k in ['no_ticket','no_zReport','id']: df[k]=df[k].astype(float).astype(int)
    Fs.append(df); print(ex,'F lignes',len(df))
F=pd.concat(Fs,ignore_index=True); F.to_pickle(CA+'F.pkl')
# ---- E
Es=[]
for ex,f in zip(EX,[annexe('E',k) for k in (1,2,3)]):
    s=xlrd.open_workbook(f).sheet_by_index(0); hdr=s.row_values(0); rows=[]
    for r in range(1,s.nrows):
        v=s.row_values(r)
        if v[1]=='Nb lignes' or v[0]=='': continue
        rows.append(v)
    df=pd.DataFrame(rows,columns=hdr); df['ex']=ex; df['rowE']=np.arange(len(df))+2
    Es.append(df); print(ex,'E lignes',len(df))
E=pd.concat(Es,ignore_index=True); E.to_pickle(CA+'E.pkl')
# ---- chemins des pièces d'origine des errata (lus par b4_errata.py, exécuté dans LibreOffice)
import json
json.dump({'38':PIECE_38,'85':PIECE_85,'86':PIECE_86,'87':PIECE_87,'88':PIECE_88},open(CA+'entrees.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
