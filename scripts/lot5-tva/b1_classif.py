"""B1 : classification légale des 323 références (B-3, B-4). Taux appliqué = taux de la ligne suivante (validé par G, s05).
Sources de nature : cartes boissons client (20/07/2021 et 26/04/2023),
proposition p.11, 46-51, référentiel client alcool-plats-cocktails-menus.json, libellé et prix. Sorties : cache/out/b1/B3_articles.csv, cache/B3_articles.pkl"""
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
CC=pd.read_pickle(CA+'C_taux2.pkl')
def nrm(s):
    s=unicodedata.normalize('NFKD',str(s)); s=''.join(ch for ch in s if not unicodedata.combining(ch)); return re.sub(r'\s+',' ',s.lower()).strip()
CC['ln']=CC.lib.map(nrm)
SOFT={'0111','0368','0094','0108','0342','0352','0096','0095','0110','0119','0107','0343','0092','0112','0120','0109','1813','0113','2010','0093','1994','0114','0106','1996','1997','1674'}
BIERE10={'1989':'Pinte : prix 7,80/8,00 € = « Pression Affligem 50 cl » (cartes 2021 et 2023) ; proposition p.50 « Pinte (50 cl de bière) »',
         '0099':'Panaché : carte « Panaché Bière + Limonade » 25/50 cl ; BOI-TVA-LIQ-30-10-10 § 130 (« mélanges … tels que les panachés »)',
         '0354':'Monaco : absent des cartes ; proposition p.46/50 « 15 cl de bière » + limonade ; R2 3.3.2 « à moitié bière »'}
BIERE20={'2005','1993','2009','0353','1991'}
ALIM20={'1816':'1 Boule Glace : prix 2,00/3,50 € = « GLACE 1 BOULE » réf. 1957 (10 %) ; vendue avec des crêpes (supplément)',
        '2119':'CREPE MARRON CHANTIL : crêpe 8,90 € (« Crêpe Marrons » réf. 2059 à 10 %)'}
INDET={'1949':'VOUIVRE : absente des cartes ; 9,00 € puis 14,60 € ; R2 § 3 la range parmi les libellés de crémant (non démontré)',
       '2017':'Griottines : 1 vente 5,90 € ; cerises à l\'eau-de-vie : boisson (digestif) ou dessert ?',
       '2078':'CHOUKA : 11,00 € ; absent des cartes et du référentiel'}
def classe(ref,t):
    if ref in BIERE10: return 'bière (> 0,5 % vol) ou mélange de bière','carte / proposition / BOFiP : '+BIERE10[ref],20
    if ref in BIERE20: return 'bière (> 0,5 % vol) ou mélange de bière','cartes 2021-2023 (pression, Rouget de Lisle, Picon bière)',20
    if ref in ALIM20: return 'aliment, plat ou dessert',ALIM20[ref],10
    if ref in INDET: return 'indéterminé',INDET[ref],None
    if ref in SOFT: return 'boisson non alcoolique','cartes 2021-2023 (softs, cafés, « Apéritifs sans alcool » Mambo/Luna)',10
    if t==20: return 'autre boisson alcoolique (> 1,2 % vol)','cartes 2021-2023 (vins, apéritifs, cocktails, digestifs) ; proposition p.46-50',20
    return 'aliment, plat ou dessert','libellé et prix ; proposition p.11 ; référentiel client (plats, galettes, crêpes, coupes ; Do…Si = coupes glacées, prop. p.49)',10
rows=[]
for ref,g in CC.groupby('ref'):
    t=int(g.rart.iloc[0]); nat,src,tl=classe(ref,t)
    r=dict(ref=ref,libelles=' / '.join(g.lib_s.value_counts().index),lignes=len(g),qte=round(g.qte.sum(),2),pu_median=g.pu.median(),
           premiere=g.date.min(),derniere=g.date.max(),t_suiv=t,nature=nat,source=src,taux_legal=tl if tl else '',
           concordant=('?' if tl is None else ('oui' if tl==t else 'NON')))
    for ex in EX: r['TTC_'+ex]=round(g[g.ex==ex].tot.sum(),2)
    rows.append(r)
A=pd.DataFrame(rows); A.to_csv(OUT+'b1/B3_articles.csv',index=False,sep=';',decimal=',')
pd.to_pickle(A,CA+'B3_articles.pkl')
print('références',len(A),'; libellés bruts',CC.lib.nunique(),'; libellés normalisés',CC.ln.nunique(),'; couples réf×libellé normalisé',CC[['ref','ln']].drop_duplicates().shape[0])
g=CC.groupby('ln').rart.nunique(); print('libellés normalisés à deux taux (taux suivant) :',(g>1).sum())
g=CC.groupby('ref').ln.nunique(); print('réfs à plusieurs libellés :',{r:CC[CC.ref==r].ln.value_counts().to_dict() for r in g[g>1].index})
print(A.groupby(['nature','t_suiv']).agg(refs=('ref','size'),lignes=('lignes','sum')).to_string())
print('\nNON concordants et indéterminés :'); print(A[A.concordant!='oui'][['ref','libelles','t_suiv','taux_legal','lignes','TTC_2022-2023','TTC_2023-2024','TTC_2024-2025','source']].to_string())
EXPR=['Pinte','Panaché','Monaco','pression','Picon bière','Pinte Picon','Mambo','Luna','PASSION','FLIRT','Do','Ré','Mi','Fa','Sol','La','Si','VOUIVRE','La Vouivre','Père Gregoire','Chat perché','Sprintz','BALIDOU','MAEVA','Rêve Bleu','Rabasse','1 Boule Glace','GLACE 1 BOULE','GLACE 2 BOULES','GLACE 3 BOULES','CREPE MARRON CHANTIL','Griottines','Whisky L.J (2cl) Bab','Baba','IVRESSE','Café  Irlandais','Café Viennois','Flambée','Crêpe Flambée','Normandine','PEUTE','Crémeux du Jura']
sel=A[A.libelles.apply(lambda s: any(x==p.strip() for x in s.split(' / ') for p in EXPR))]
print('\nArticles à traiter expressément :'); print(sel[['ref','libelles','t_suiv','nature','taux_legal','concordant','lignes','pu_median']].to_string())
