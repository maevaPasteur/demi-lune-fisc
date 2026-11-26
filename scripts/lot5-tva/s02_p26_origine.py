"""s02 : origine au centime des chiffres p.26 (tableau G) : Total CA TTC, Total TVA, bases et TVA par taux.
Hypothèses testées : compteur dernière ligne - A NOUVEAUX ; compteur max - AN ; Σ tickets ; etc."""
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
G=loadG(); H=loadH()
AN={'2022-2023':(977739.78,102865.15),'2023-2024':(1381110.20,145417.91),'2024-2025':(1819103.12,191817.99)}
for i,ex in enumerate(EX):
    g=G[G.ex==ex]; tk=g.drop_duplicates('tk'); an_s,an_t=c(AN[ex][0]),c(AN[ex][1])
    print(f'===== {ex}  lignes {len(g)} tickets distincts (ex,date,heure,n°,Z) {len(tk)}')
    print('  Σ tot_ttc une fois par ticket', e(tk.tot_ttc_c.sum()), '; Σ tot_tva une fois par ticket', e(tk.tot_tva_c.sum()))
    print('  Σ tax_amount', e(g.tax_amount_c.sum()), ' 10%', e(g[g['taux_tva%']==10].tax_amount_c.sum()),' 20%', e(g[g['taux_tva%']==20].tax_amount_c.sum()))
    print('  Σ VAT_base 10%', e(g[g['taux_tva%']==10].VAT_base_c.sum()),' 20%', e(g[g['taux_tva%']==20].VAT_base_c.sum()), ' total', e(g.VAT_base_c.sum()))
    last=g.iloc[-1]; mx_s=g.tot_sum_c.max(); mx_t=g.tot_tax_sum_c.max()
    print('  dernière ligne du fichier :', last.dateTicket,last.heureTicket,'n°',last.noTicket,'Z',last.no_zReport,' tot_sum',last.tot_sum,' tot_tax_sum',last.tot_tax_sum)
    print('  dernière ligne - AN : CA', e(last.tot_sum_c-an_s),' TVA', e(last.tot_tax_sum_c-an_t), '  p26 :',P26G['CA'][i],P26G['TVA'][i])
    print('  max - AN : CA', e(mx_s-an_s), ' TVA', e(mx_t-an_t))
    imx=g.tot_sum_c.idxmax(); r=g.loc[imx]; print('  ligne du max :',r.dateTicket,r.heureTicket,'n°',r.noTicket,'Z',r.no_zReport,'rowG',r.rowG,'/',len(g)-1)
    # écarts : tickets postérieurs (au compteur) à la dernière ligne
    after=tk[tk.tot_sum_c>last.tot_sum_c]
    print('  tickets dont compteur > compteur dernière ligne :',len(after),' Σ TTC',e(after.tot_ttc_c.sum()),' Σ TVA',e(after.tot_tva_c.sum()))
    # monotonie du compteur dans l'ordre du fichier
    d=np.diff(tk.tot_sum_c.values); print('  ruptures de monotonie du compteur dans l\'ordre du fichier (tickets) :',(d<0).sum())
    # identité compteur : tot_sum(t) - tot_sum(t-1) = tot_ttc(t) en triant par compteur
    t2=tk.sort_values(['tot_sum_c']); dd=np.diff(np.r_[an_s,t2.tot_sum_c.values]) - t2.tot_ttc_c.values
    print('  compteur trié : incréments ≠ tot_ttc :',(dd!=0).sum(), ' Σ écarts', e(dd.sum()))
    dt=np.diff(np.r_[an_t,t2.tot_tax_sum_c.values]) - t2.tot_tva_c.values; print('  compteur TVA trié : incréments ≠ tot_tva :',(dt!=0).sum(),' Σ', e(dt.sum()))
    print('  ordre du fichier : tri par', 'date' if (g.dateTicket.values[:-1]<=g.dateTicket.values[1:]).all() else 'non trié par date', '; dernière date', g.dateTicket.max(), '; date de la dernière ligne', last.dateTicket)
    # H
    h=H[H.ex==ex]; print('  H lignes',len(h),' Σ tot_ttc',e(h.tot_ttc.map(c).sum()),' Σ tot_tva',e(h.tot_tva.map(c).sum()),' dernière ligne tot_sum',h.iloc[-1].tot_sum,' max tot_sum',h.tot_sum.max())
    print('     H dernière ligne - AN', e(c(h.iloc[-1].tot_sum)-an_s), e(c(h.iloc[-1].tot_tax_sum)-an_t))
