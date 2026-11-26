"""s01 : contrôle des tables de s00_charger.py contre les xls primaires ; inventaire des colonnes de G, H, C ; pieds."""
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
G=loadG(); H=loadH(); CC=loadC()
for i,ex in enumerate(EX):
    s=xlrd.open_workbook(D+GF[i]).sheet_by_index(0); hdr=s.row_values(0)
    rows=[s.row_values(r) for r in range(1,s.nrows) if str(s.row_values(r)[0])[:2]=='20']
    g=G[G.ex==ex]
    print(ex,'G xls lignes',len(rows),'cache',len(g),'colonnes',len(hdr),hdr)
    for j,k in enumerate(hdr[7:],7):
        try: tot=sum(c(r[j]) for r in rows if r[j]!='')
        except: continue
        print(f'   col {j} {k!r}: Σ {e(tot)} ; non vides {sum(1 for r in rows if r[j]!="")}')
    print('   pied', [[x for x in s.row_values(r) if x!=''] for r in range(s.nrows) if not str(s.row_values(r)[0])[:2]=='20' and r>0])
    # identités des 4 colonnes du service
    print('   B10s==VAT_base si taux 10 :', ((g['taux_tva%']==10)&(g.B10s.map(lambda x: x!='' and c(x))==g.VAT_base_c)).sum(), '/', (g['taux_tva%']==10).sum(),
          '; B20s==VAT_base si taux 20 :', ((g['taux_tva%']==20)&(g.B20s.map(lambda x: x!='' and c(x))==g.VAT_base_c)).sum(), '/', (g['taux_tva%']==20).sum(),
          '; T10s==tax :', ((g['taux_tva%']==10)&(g.T10s.map(lambda x: x!='' and c(x))==g.tax_amount_c)).sum(),
          '; T20s==tax :', ((g['taux_tva%']==20)&(g.T20s.map(lambda x: x!='' and c(x))==g.tax_amount_c)).sum(),
          '; taux présents', g['taux_tva%'].value_counts().to_dict())
    s=xlrd.open_workbook(D+HF[i]).sheet_by_index(0); print('   H',HF[i],'lignes',s.nrows-1,'cache',(H.ex==ex).sum(),'hdr',s.row_values(0))
    print('   H pied',[[x for x in s.row_values(r) if x!=''] for r in range(s.nrows) if not str(s.row_values(r)[0])[:2]=='20' and r>0])
    s=xlrd.open_workbook(D+CF[i]).sheet_by_index(0); print('   C',CF[i],'lignes données',sum(1 for r in range(1,s.nrows) if s.row_values(r)[0]!=''),'cache',(CC.ex==ex).sum())
    print('   C entêtes', [h.replace('\n',' ') for h in s.row_values(0)])
print('C colonne E valeurs', CC.Es.value_counts().to_dict())
print('C taux par valeur de E', pd.crosstab(CC.Es,CC.tva).to_dict())
