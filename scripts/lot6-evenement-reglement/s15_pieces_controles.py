"""Contrôles des pièces 90 (onglet 7) et 91 (onglet 1, F7 : ordre du fichier)."""
import pandas as pd, numpy as np
B=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/B.pkl'); CC=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/CC.pkl'); H=pd.read_pickle('scripts/lot6-evenement-reglement/cache/H.pkl')
out=open('scripts/lot6-evenement-reglement/out/s15_pieces_controles.txt','w')
def p(*a): print(*a); print(*a,file=out)
for ex in ['2022-2023','2023-2024','2024-2025']:
    b=B[B.ex==ex]; c=CC[CC.ex==ex]
    p(ex,'Σ round(PU×Qté,2) : B',round((b.pu*b.qte).round(2).sum(),2),' C',round((c.pu*c.qte).round(2).sum(),2),
      ' | Σ PU×Qté brut : B',round((b.pu*b.qte).sum(),3),' C',round((c.pu*c.qte).sum(),3),' | Σ |A−TTC| ligne : C',round((c.A-c.tot).abs().sum(),2))
# ordre du fichier H
for ex,g in H.groupby('ex'):
    g=g.sort_values('ligneXLS')
    p(ex,'H trié par (date, id) :',bool((g[['date_ticket','id']].apply(tuple,axis=1).is_monotonic_increasing)),' par (date, n° ticket) :',bool(g[['date_ticket','no_ticket']].apply(tuple,axis=1).is_monotonic_increasing),
      ' par (date,heure) :',bool((g.date_ticket+g.heure_ticket).is_monotonic_increasing),' inversions id dans le jour :',int(((g.id.diff()<0)&(g.date_ticket==g.date_ticket.shift())).sum()))
out.close()
