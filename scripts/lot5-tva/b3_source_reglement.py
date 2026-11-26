"""B3 / C7-2 : fichier natif de la cliente SOURCE-reglement-brut_2022-2025.xls (SpreadsheetML) contre annexes F."""
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
import xml.etree.ElementTree as ET
P=SOURCE_REGLEMENT
ns={'ss':'urn:schemas-microsoft-com:office:spreadsheet'}
root=ET.parse(P).getroot(); rows=[]
for r in root.iter('{urn:schemas-microsoft-com:office:spreadsheet}Row'):
    vals=[]; 
    for cell in r.findall('ss:Cell',ns):
        idx=cell.get('{urn:schemas-microsoft-com:office:spreadsheet}Index')
        if idx: 
            while len(vals)<int(idx)-1: vals.append(None)
        d=cell.find('ss:Data',ns); vals.append(d.text if d is not None else None)
    rows.append(vals)
hdr=rows[0]; S=pd.DataFrame([r+[None]*(len(hdr)-len(r)) for r in rows[1:]],columns=hdr)
print('lignes natif',len(S),'colonnes',hdr)
for k in ['etat','(null)','mf_number','mf_desc','cod_clt','tot_rem_lig','sy_uk']: print(' ',k,S[k].value_counts(dropna=False).head(8).to_dict())
S['id']=S.id.astype(float).astype(int); S['montant_c']=S.montant.astype(float).map(c); S['tot_ttc_c']=S.tot_ttc.astype(float).map(c)
F=pd.read_pickle(C23+'F.pkl'); F['montant_c']=F.montant.map(c)
a=Counter=None
from collections import Counter
k1=Counter(zip(S.id,S.date_ticket,S.heure_ticket,S.no_ticket.astype(float).astype(int),S.mod_regl,S.montant_c,S.tot_ttc_c))
k2=Counter(zip(F.id,F.dateTicket,F.heureTicket,F.no_ticket,F.mod_regl,F.montant_c,F.tot_ttc.map(c)))
print('natif − F :',sum((k1-k2).values()),' F − natif :',sum((k2-k1).values()),' ; Σ montants natif',e(S.montant_c.sum()),' F',e(F.montant_c.sum()))
print('ordre : F (3 fichiers concaténés) == natif ligne à ligne :',list(zip(F.id,F.mod_regl,F.montant_c))==list(zip(S.id,S.mod_regl,S.montant_c)))
z=S[S.tot_ttc_c==0]; print('règlements natifs sur notes à 0 € :',len(z),'lignes,',z.id.nunique(),'notes, Σ',e(z.montant_c.sum()))
print(z.groupby(['etat','(null)','mf_desc'],dropna=False).size().to_string())
print('etat sur les autres notes :',S[S.tot_ttc_c!=0].etat.value_counts(dropna=False).to_dict(), ' (null) :',S[S.tot_ttc_c!=0]['(null)'].value_counts(dropna=False).head(5).to_dict())
print(z[['date_ticket','heure_ticket','no_ticket','no_z_report','id','etat','(null)','mf_desc','sy_uk','mod_regl','montant','tot_sum','tot_tax_sum']].head(60).to_string())
S.to_pickle(CA+'SOURCE_reglement.pkl')
