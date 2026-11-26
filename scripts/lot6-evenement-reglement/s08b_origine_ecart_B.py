"""Origine de l'écart A − TTC de l'annexe B (17 561,00 / 20 011,12 / 20 115,28 €) : lignes dont la Qté B diffère de la Qté C
(appariement ligne à ligne du lot 2.3, Crec, contrôlé ici sur les totaux)."""
import pandas as pd
c=lambda x:int(round(float(x)*100)); e=lambda n:f"{n/100:,.2f}".replace(',',' ').replace('.',',')
Cr=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/Crec.pkl'); B=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/B.pkl')
out=open('scripts/lot6-evenement-reglement/out/s08b_origine_ecart_B.txt','w')
def p(*a): print(*a); print(*a,file=out)
for ex,x in Cr.groupby('ex'):
    x=x[x.inB]
    d=(x.qte-x.qteC).abs()>1e-9; disc=x.disc!=0
    eb=(x.pu*x.qte-x.tot)
    p(f'{ex} : lignes appariées {len(x)} (B {int((B.ex==ex).sum())}) ; Σ TTC apparié {e(x.tot.map(c).sum())} ; Σ(PU×QtéB − TTC) {e(c(eb.sum()))} ; '
      f'lignes QtéB≠QtéC {int(d.sum())} → {e(c(eb[d].sum()))} ; lignes à remise {int(disc.sum())} → {e(c(eb[disc & ~d].sum()))} ; autres {e(c(eb[~d & ~disc].sum()))} ; '
      f'Σ(QtéB − QtéC) {round((x.qte-x.qteC).sum(),2)} ; lignes QtéB<QtéC {int((x.qte<x.qteC-1e-9).sum())} ; QtéB>QtéC {int((x.qte>x.qteC+1e-9).sum())}')
p('total lignes QtéB≠QtéC',int(((Cr[Cr.inB].qte-Cr[Cr.inB].qteC).abs()>1e-9).sum()))
out.close()
