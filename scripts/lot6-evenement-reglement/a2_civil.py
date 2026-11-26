# annexes A (années civiles) contre fichiers ; etat 9 par année civile ; ventes 1er janv.-13 avril 2023 et 2024
import pandas as pd, sys
S=pd.read_pickle('scripts/lot6-evenement-reglement/cache/SOURCE.pkl'); H=pd.read_pickle('scripts/lot6-evenement-reglement/cache/H.pkl')
print('SOURCE cols',list(S.columns)[:25]); print('H cols',list(H.columns)[:25])
def dcol(df):
    for c in df.columns:
        if 'date' in c.lower(): return c
ds=dcol(S); S['_d']=pd.to_datetime(S[ds],errors='coerce'); S['_y']=S['_d'].dt.year
S['montant']=pd.to_numeric(S['montant'],errors='coerce')
e9=S[S['etat'].astype(str)=='9']
print('etat 9 par annee civile :'); print(e9.groupby('_y')['montant'].sum().round(2))
print('reglements totaux par annee civile :'); print(S.groupby('_y')['montant'].sum().round(2))
dh=dcol(H); H['_d']=pd.to_datetime(H[dh],errors='coerce')
tt=[c for c in H.columns if c.lower()=='tot_ttc'][0]
H[tt]=pd.to_numeric(H[tt],errors='coerce')
for y in (2023,2024):
    a=H[(H['_d']>=f'{y}-01-01')&(H['_d']<=f'{y}-03-31')][tt].sum(); b=H[(H['_d']>=f'{y}-04-01')&(H['_d']<=f'{y}-04-13')][tt].sum()
    print(y,'01/01-31/03 :',round(a,2),' 01/04-13/04 :',round(b,2),' total 01/01-13/04 :',round(a+b,2))
print('negatifs H :',(H[tt]<0).sum())
