"""Tableau 58, puces : part des DEL positifs (hors 4 lignes ≥ 1 000 €) égaux à un PU de la carte de l'exercice ; témoin : totaux de notes encaissées.
Carte = ensemble des PU (colonne 14 Uprice_wt) présents dans l'annexe C de l'exercice (variante : annexe B, colonne 8)."""
import pandas as pd, numpy as np
CA='scripts/lot6-evenement-reglement/cache/'
E=pd.read_pickle(CA+'E.pkl'); H=pd.read_pickle(CA+'H.pkl'); F=pd.read_pickle(CA+'F.pkl')
CC=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/CC.pkl'); B=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/B.pkl')
c=lambda x:int(round(float(x)*100))
out=open('scripts/lot6-evenement-reglement/out/s10_DEL_prix.txt','w')
def p(*a): print(*a); print(*a,file=out)
D=E[E.typEven=='DEL']
big=D[D.amount_c>=100000]
p('Lignes DEL ≥ 1 000 € :',len(big),' Σ',big.amount_c.sum()/100,' part du total',round(big.amount_c.sum()/D.amount_c.sum()*100,2),'%')
p(big[['ex','dateEven','heureEven','no_zEport','amount','id','ligneXLS']].to_string())
for lab,src,col in [('carte = PU de C',CC,'pu'),('carte = PU de B',B,'pu')]:
    for ex in ['2022-2023','2023-2024','2024-2025']:
        carte=set(src[src.ex==ex][col].map(c))
        d=D[(D.ex==ex)&(D.amount_c>0)&(D.amount_c<100000)]
        h=H[(H.ex==ex)&(H.tot_ttc_c!=0)]; f=F[F.ex==ex].groupby('id').montant_c.sum()
        p(f'{lab} {ex} : PU distincts {len(carte)} ; DEL positifs hors ≥1000 {len(d)} ; = un PU {int(d.amount_c.isin(carte).sum())} ({d.amount_c.isin(carte).mean()*100:.1f} %) ; '
          f'totaux de notes H ≠0 {len(h)} = un PU {h.tot_ttc_c.isin(carte).mean()*100:.1f} % ; totaux F par note {f.isin(carte).mean()*100:.1f} %')
p('DEL ≤ 0 :',int((D.amount_c<=0).sum()),' négatifs',D[D.amount_c<0][['dateEven','heureEven','amount']].values.tolist())
out.close()
