"""2.6.5 d, première puce : nombre de lignes et de lignes à quantité fractionnaire, B contre C ; part de quantité fractionnaire (R1 : 5,0 % / 2,6 %)."""
import pandas as pd
B=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/B.pkl'); CC=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/CC.pkl')
out=open('scripts/lot6-evenement-reglement/out/s14_fractions_BC.txt','w')
def p(*a): print(*a); print(*a,file=out)
for ex in ['2022-2023','2023-2024','2024-2025']:
    b=B[B.ex==ex]; c=CC[CC.ex==ex]
    fb=(b.qte-b.qte.round()).abs()>1e-9; fc=(c.qte-c.qte.round()).abs()>1e-9
    p(f'{ex} : lignes B {len(b)} C {len(c)} ; lignes à Qté fractionnaire B {int(fb.sum())} ({fb.mean()*100:.2f} %) C {int(fc.sum())} ({fc.mean()*100:.2f} %) ; '
      f'Qté portée par les lignes fractionnaires B {b[fb].qte.sum():.2f} ({b[fb].qte.sum()/b.qte.sum()*100:.2f} % de ΣQté) C {c[fc].qte.sum():.2f} ({c[fc].qte.sum()/c.qte.sum()*100:.2f} %)')
# extrait p. 42 (B-1) et p. 43 (C-1), 14/04/2022 notes 11 à 16, lignes à Qté 0,50
b=B[(B.date=='2022-04-14')&B.ticket.between(11,16)]; c=CC[(CC.date=='2022-04-14')&CC.ticket.between(11,16)]
p('14/04/2022 notes 11-16 : lignes B',len(b),' C',len(c),' ; lignes Qté = 0,50 : B',int((b.qte==0.5).sum()),' C',int((c.qte==0.5).sum()))
out.close()
