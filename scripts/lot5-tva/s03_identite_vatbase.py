"""s03 : identité VAT_base = palier TTC - taux (lu en euros) ; tax_amount = palier*r/(100+r) ; lignes négatives."""
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN
G=loadG(); G['r']=G['taux_tva%'].astype(int)
G['pal_c']=G.VAT_base_c+G.r*100                       # palier supposé = VAT_base + taux en euros
G['tax_th']=[int((Decimal(p)*r/(100+r)).quantize(Decimal(1),ROUND_HALF_UP)) for p,r in zip(G.pal_c,G.r)]
G['pal_tax']=G.tax_amount_c*(100+G.r)/G.r               # palier déduit de la taxe (non arrondi)
G['d_pal']=G.pal_c-G.pal_tax
res=[]
for ex in EX+['3ex']:
    g=G if ex=='3ex' else G[G.ex==ex]
    tk=g.groupby('tk').agg(ttc=('tot_ttc_c','first'),tva=('tot_tva_c','first'),pal=('pal_c','sum'),tax=('tax_amount_c','sum'),n=('r','size'),
                           neg=('VAT_base_c',lambda s:(s<0).sum()),rates=('r',lambda s:tuple(sorted(s))))
    n10=(g.r==10).sum(); n20=(g.r==20).sum()
    print(f'===== {ex}: lignes {len(g)} (10% {n10}, 20% {n20}) tickets {len(tk)} ; composition {tk.rates.value_counts().to_dict()}')
    print('  Σ VAT_base + 10*n10 + 20*n20 =', e(g.VAT_base_c.sum()+1000*n10+2000*n20), ' ; Σ tot_ttc tickets', e(tk.ttc.sum()))
    print('  tickets où Σ(VAT_base+taux) == tot_ttc au centime :',(tk.pal==tk.ttc).sum(),'/',len(tk), ' ; Σ tax == tot_tva :',(tk.tax==tk.tva).sum())
    print('  lignes où tax_amount == arrondi(palier*r/(100+r)) au centime :',(g.tax_th==g.tax_amount_c).sum(),'/',len(g), ' écarts max (cts)', (g.tax_th-g.tax_amount_c).abs().max())
    print('  |palier(VAT_base) - palier(taxe)| max en € : 10%', round(g[g.r==10].d_pal.abs().max()/100,4),' 20%', round(g[g.r==20].d_pal.abs().max()/100,4),
          ' ; lignes ≤0,05 € :',(g.d_pal.abs()<=5+1e-9).sum(),'/',len(g), ' ; ≤0,055 € :',(g.d_pal.abs()<=5.5+1e-9).sum())
    print('  VAT_base multiple de 5 cts :',(g.VAT_base_c%5==0).sum(),'/',len(g), ' ; multiple de 10 cts :',(g.VAT_base_c%10==0).sum(), ' ; tot_ttc multiple 10 cts (tickets):',(tk.ttc%10==0).sum(),'/',len(tk))
    neg10=((g.r==10)&(g.VAT_base_c<0)).sum(); neg20=((g.r==20)&(g.VAT_base_c<0)).sum(); z=(g.VAT_base_c==0).sum()
    print(f'  lignes VAT_base<0 : 10% {neg10}  20% {neg20}  total {neg10+neg20} ; =0 : {z} ; % des lignes 20% négatives {100*neg20/n20:.2f}')
    print(f'  lignes tax_amount<0 : {(g.tax_amount_c<0).sum()} ; =0 : {(g.tax_amount_c==0).sum()} ; palier<taux ⇔ VAT_base<0 : {((g.pal_c<g.r*100)==(g.VAT_base_c<0)).all()}')
    nt=(tk.neg>0).sum(); print(f'  tickets avec ≥1 ligne négative {nt}/{len(tk)} = {100*nt/len(tk):.2f} % ; tickets avec ligne 20% : {tk.rates.map(lambda t:20 in t).sum()}')
    print(f'  tickets avec ligne 20% négative : {g[(g.r==20)&(g.VAT_base_c<0)].tk.nunique()} ; avec ligne 10% négative : {g[(g.r==10)&(g.VAT_base_c<0)].tk.nunique()} ; les deux : {len(set(g[(g.r==20)&(g.VAT_base_c<0)].tk)&set(g[(g.r==10)&(g.VAT_base_c<0)].tk))}')
    # palier exact déduit de la taxe vs palier VAT_base : unicité
    print('  doublons de taux dans un ticket :', (tk.rates.map(lambda t: len(t)!=len(set(t)))).sum())
    print('  Σ base déduite tax/taux : 10%', e(round((g[g.r==10].tax_amount_c*10).sum())), ' 20%', e(round((g[g.r==20].tax_amount_c*5).sum())),
          ' ; Σ base déduite + Σ tax', e(round((g[g.r==10].tax_amount_c*10).sum()+(g[g.r==20].tax_amount_c*5).sum()+g.tax_amount_c.sum())))
    print('  Σ (palier - taxe) = base HT réelle : 10%', e((g[g.r==10].pal_c-g[g.r==10].tax_amount_c).sum()),' 20%', e((g[g.r==20].pal_c-g[g.r==20].tax_amount_c).sum()),
          ' total', e((g.pal_c-g.tax_amount_c).sum()))
    res.append(ex)
G[['ex','tk','r','VAT_base_c','tax_amount_c','pal_c','tax_th']].to_pickle(CA+'G_paliers.pkl')
