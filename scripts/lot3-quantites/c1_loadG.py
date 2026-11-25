"""Chargement des annexes G (journal TVA) et H complètes, avec pieds de page."""
import os, sys, xlrd; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
G=[]; foots={}
for ex,f in zip(EX,['ANNEXE-G1_journal-tva_2022-2023.xls','ANNEXE-G2_journal-tva_2023-2024.xls','ANNEXE-G3_journal-tva_2024-2025.xls']):
    s=xlrd.open_workbook(CAISSE+f).sheet_by_index(0); hdr=s.row_values(0)
    rows=[]; ft=[]
    for r in range(1,s.nrows):
        v=s.row_values(r)
        if str(v[0])[:2]=='20': rows.append(v)
        else: ft.append(v)
    g=pd.DataFrame(rows,columns=hdr); g['ex']=ex; g['rowG']=range(len(g)); G.append(g); foots[ex]=ft
G=pd.concat(G,ignore_index=True)
for c in ['noTicket','no_zReport']: G[c]=G[c].astype(float).astype(int)
for c in ['tot_ttc','tot_tva','tot_sum','tot_tax_sum','tot_remGlobale','taux_tva%','VAT_base','tax_amount']: G[c]=pd.to_numeric(G[c],errors='coerce')
G['t']=G.heureTicket.map(tmin)
G.to_pickle(C+'G.pkl'); pd.to_pickle(foots,C+'G_foot.pkl')
print(G.groupby('ex').agg(lignes=('tot_ttc','size'),tickets=('noTicket',lambda s: None)).head() if False else '')
for ex,g in G.groupby('ex'):
    k=g.groupby(['dateTicket','noTicket','heureTicket','no_zReport']).size()
    print(ex,'lignes',len(g),'tickets (date,n°,heure,Z)',len(k),' lignes/ticket',k.value_counts().to_dict(),' Σ VAT_base',round(g.VAT_base.sum(),2),' Σ tax',round(g.tax_amount.sum(),2))
    print('  pied',[[x for x in r if x!=''] for r in foots[ex]][:6])
print(G.head(6).to_string())
