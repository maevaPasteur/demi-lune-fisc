"""Lot 2.7 / B0 : lecture indépendante des fichiers de caisse d'origine (C, E, F, H, G), sans passer par les caches.
Sorties : out/B0cache/{C,E,F,H,G}.pkl ; out/s00_load.txt (comptes, pieds de fichier, comparaison aux caches lot26)."""
import xlrd, pandas as pd, numpy as np, hashlib
D='scripts/lot7-tables-virtuelles/cache/entrees/'; O='scripts/lot7-tables-virtuelles/out/'
EX=['2022-2023','2023-2024','2024-2025']
FILES={'E':['14-annexe-e1-2022-2023.xls','15-annexe-e2-2023-2024.xls','16-annexe-e3-2024-2025.xls'],
 'C':['17-annexe-c1-2022-2023.xls','18-annexe-c2-2023-2024.xls','19-annexe-c3-2024-2025.xls'],
 'F':['20-annexe-f1-2022-2023.xls','21-annexe-f2-2023-2024.xls','22-annexe-f3-2024-2025.xls'],
 'G':['ANNEXE-G1_journal-tva_2022-2023.xls','ANNEXE-G2_journal-tva_2023-2024.xls','ANNEXE-G3_journal-tva_2024-2025.xls'],
 'H':['ANNEXE-H1_liste-tickets_2022-2023.xls','ANNEXE-H2_liste-tickets_2023-2024.xls','ANNEXE-H3_liste-tickets_2024-2025.xls']}
out=open(O+'B0_s00_load.txt','w')
def p(*a): print(*a); print(*a,file=out)
res={}
for k,fl in FILES.items():
    parts=[]
    for ex,f in zip(EX,fl):
        wb=xlrd.open_workbook(D+f); s=wb.sheet_by_index(0)
        hdr=[str(h).replace('\n',' ').strip() for h in s.row_values(0)]
        rows=[]; foot=[]
        for r in range(1,s.nrows):
            v=s.row_values(r)
            first=v[0]
            # lignes de données : la 1re colonne (date) a la forme AAAA-MM-JJ, sauf E (noCaisse numérique) 
            if k=='E':
                ok=isinstance(first,float) and isinstance(v[1],str) and v[1][:2]=='20'
            else:
                ok=isinstance(first,str) and len(first)==10 and first[:2]=='20'
            if ok: rows.append(v+[r+1])
            else: foot.append((r+1,v))
        df=pd.DataFrame(rows,columns=hdr+['ligneXLS']); df['ex']=ex
        parts.append(df)
        p(f'{k} {f} md5={hashlib.md5(open(D+f,"rb").read()).hexdigest()} lignes données={len(df)} ; lignes hors données={len(foot)}')
        for r,v in foot: p('    hors données ligne',r,[x for x in v if x!=''][:12])
    res[k]=pd.concat(parts,ignore_index=True)
# renommages courts
C=res['C']; C.columns=['date','heure','no','datz','z','tot_ttc','tot_tva','tot_rem','id','ref','lib','qte','unite','pu','remise','taux','tot_lig']+list(C.columns[17:])
E=res['E']; H=res['H']; F=res['F']; G=res['G']
for df,cols in [(C,['no','z','id']),(E,['no_zEport','id','noCaisse']),(H,['no_ticket','no_z_report','id']),(F,['no_ticket','no_zReport','id'])]:
    for c in cols: df[c]=df[c].astype(int)
for k,df in [('C',C),('E',E),('F',F),('H',H),('G',G)]:
    df.to_pickle(O+f'B0cache/{k}.pkl'); p(k,df.shape)
# comparaison aux caches lot26 (E,F,H,G)
L='scripts/lot6-evenement-reglement/cache/'
for k,keys in [('E',['id','dateEven','heureEven','typEven','no_zEport','amount']),('H',['id','date_ticket','heure_ticket','no_ticket','no_z_report','tot_ttc','tot_sum']),('F',['id','dateTicket','heureTicket','no_ticket','mod_regl','montant'])]:
    a=res[k][keys].reset_index(drop=True); b=pd.read_pickle(L+k+'.pkl')[keys].reset_index(drop=True)
    from pandas.api.types import is_numeric_dtype
    eq=(a.shape==b.shape) and all(np.allclose(a[c].astype(float),b[c].astype(float)) if is_numeric_dtype(b[c]) else (a[c].astype(str)==b[c].astype(str)).all() for c in keys)
    p(f'cache lot26 {k}: forme {b.shape} ; identique aux fichiers sur {keys}: {eq}')
out.close()
