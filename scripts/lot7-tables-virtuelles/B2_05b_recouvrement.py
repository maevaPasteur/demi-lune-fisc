"""C-5 (suite) : recouvrement des tables à inclusion totale (W = 240) avec les 133 conversions (157-R4) et les 146 égalités (155-R3 version C, recalculées en B2_01) ;
détail du 9 septembre 2022. Sortie : out/B2/05b.txt"""
import sys; sys.path.insert(0,"scripts/lot7-tables-virtuelles")
from B2_common import *
import openpyxl
p=out2('05b.txt'); R=pd.read_csv(OUT2+'05_tables.csv'); Pop=pd.read_csv(OUT2+'04_tables.csv')
wb=openpyxl.load_workbook('scripts/lot7-tables-virtuelles/cache/entrees/lot27/157-R4-conversions-au-forfait-133-suites.xlsx',data_only=True,read_only=True)
rows=list(wb['Suites'].iter_rows(values_only=True)); Su=pd.DataFrame(rows[1:],columns=rows[0]); Su=Su[pd.to_numeric(Su['Suite n°'],errors='coerce').notna()]
conv=set(zip(pd.to_datetime(Su['Date']).dt.strftime('%Y-%m-%d'),Su['Minute'].map(tm)))
Pop['conv']=[(d,t) in conv for d,t in zip(Pop.d,Pop.t)]
s=R[R.W==240].merge(Pop[['N° de table','conv','egal_30','d','t']],left_on='table',right_on='N° de table')
for c in ['c_tot','c_tot_sansid']:
    x=s[s[c]==1]; p(f'{c} (W = 240) : {len(x)} tables ; dont conversions 157-R4 {int(x.conv.sum())} ; dont égalités au centime ± 30 min (146) {int(x.egal_30.sum())} ; ni l un ni l autre {int((~x.conv&~x.egal_30).sum())} ({x[~x.conv&~x.egal_30].V.sum()/100:.2f} €)')
p(f'Tables conversions 157-R4 parmi les 2 359 : {int(Pop.conv.sum())}')
d=s[s.d=='2022-09-09'][['d','t','V','cat','c_tot','c_tot_sansid','c_80','bsum']]; d['t']=d.t.map(lambda x:f'{int(x)//60:02d}:{int(x)%60:02d}')
p('09/09/2022 (W = 240) :'); p(d.to_string())
p(f'Conversions 157-R4 qui sont des tables vidées : {int(Pop.conv.sum())} ; dont parmi les 146 égalités (± 30 min) : {int((Pop.conv&Pop.egal_30).sum())}')
