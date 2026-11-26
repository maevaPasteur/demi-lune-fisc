"""s09 : audit des pièces de la société : 85 (sources G1-3 vs annexes G), 36 (extrait), 37, 39-41, 86, 87, 88 (valeurs en cache)."""
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
import openpyxl, csv
G=loadG()
wb=openpyxl.load_workbook(PIECE_85,read_only=True)
for i,ex in enumerate(EX):
    rows=list(wb[f'G{i+1}-source'].iter_rows(min_row=2,values_only=True)); g=G[G.ex==ex]
    a=[(r[0],int(r[1]),int(r[2]),c(r[3]),c(r[4]),int(r[5]),c(r[6]),c(r[13]),c(r[14])) for r in rows if r[0]]
    b=list(zip(g.dateTicket,g.noTicket,g['taux_tva%'].astype(int),g.VAT_base_c,g.tax_amount_c,g.no_zReport,g.tot_ttc_c,g.tot_sum_c,g.tot_tax_sum_c))
    print(ex,'pièce 85 lignes',len(a),'annexe',len(b),' identiques ligne à ligne (même ordre) :',sum(x==y for x,y in zip(a,b)))
# pièce 36 : extrait
with open(PIECE_36,encoding='utf-8-sig') as f: r36=list(csv.reader(f,delimiter=';'))[1:]
g=G[G.dateTicket=='2022-04-14']; ok=0
for r in r36:
    m=g[(g.noTicket==int(r[1]))&(g['taux_tva%']==int(r[2]))&(g.VAT_base_c==c(r[3].replace(',','.')))&(g.tax_amount_c==c(r[4].replace(',','.')))&(g.tot_ttc_c==c(r[5].replace(',','.')))]
    ok+=len(m)>=1
print('pièce 36 :',len(r36),'lignes ; retrouvées dans G-1 :',ok, ' ; G-1 du 14/04/2022 compte',len(g),'lignes, n° tickets',sorted(g.noTicket.unique()))
# ticket 2 : base réelle
t=G[(G.dateTicket=='2022-04-14')&(G.noTicket==2)]
for _,x in t.iterrows():
    r=int(x['taux_tva%']); pal=x.VAT_base_c+100*r
    print(f'  ticket 2 taux {r}: palier {e(pal)} ; HT réel palier−taxe {e(pal-x.tax_amount_c)} ; « base correcte » TVA/taux {e(round(x.tax_amount_c*100/r))}')
# 86, 87, 88 : dump des valeurs
for f in [PIECE_86,PIECE_87,PIECE_38]:
    w=openpyxl.load_workbook(f,data_only=True,read_only=True)
    for ws in w.worksheets:
        print('#####',os.path.basename(f),ws.title)
        for row in ws.iter_rows(values_only=True):
            if any(v is not None for v in row): print('   ',[v for v in row if v is not None])
w=openpyxl.load_workbook(PIECE_88,data_only=True,read_only=True)
for sh in ['Lecture','TVA-1 Synthèse','ENC-4 Contrôle TVA caisse']:
    print('#####88',sh)
    for row in w[sh].iter_rows(values_only=True):
        if any(v is not None for v in row): print('   ',[v for v in row if v is not None])
for sh in ['TVA-2 Articles aux deux taux','TVA-3 Relevé par article','TVA-4 Lignes signalées']:
    rows=list(w[sh].iter_rows(values_only=True)); print('#####88',sh,len(rows)); [print('   ',r) for r in rows[:4]]
