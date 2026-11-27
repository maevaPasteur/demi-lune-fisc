"""B0 point 8 : DEL au prix de carte (hors 4 lignes >= 1 000 €), témoin pondéré par tranche, sensibilité aux tranches.
Carte = PU > 0 distincts de l'annexe C (colonne 14 Uprice_wt) de l'exercice. Témoin = totaux H non nuls de la 1re série.
Sortie : out/s05_del_prix.txt"""
import pandas as pd, numpy as np
O='scripts/lot7-tables-virtuelles/out/'
C=pd.read_pickle(O+'B0cache/C.pkl'); D=pd.read_pickle(O+'B0cache/DEL.pkl'); H=pd.read_pickle(O+'B0cache/H2.pkl')
c=lambda x:int(round(float(x)*100))
out=open(O+'B0_s05_del_prix.txt','w')
def p(*a): print(*a); print(*a,file=out)
D['ac']=D.amount.map(c); H['tc']=H.tot_ttc.map(c)
BINS={'lot26 (5/10/20/50/100)':[0,500,1000,2000,5000,10000,10**9],
      'fines (2/5/10/15/20/30/50/100)':[0,200,500,1000,1500,2000,3000,5000,10000,10**9],
      'larges (10/50)':[0,1000,5000,10**9],'sans pondération':[0,10**9]}
for ex in ['2022-2023','2023-2024','2024-2025']:
    cat=set(v for v in C[C.ex==ex].pu.map(c) if v>0)
    d=D[(D.ex==ex)&(D.ac>0)&(D.ac<100000)].ac; n=H[(H.ex==ex)&(H.serie==1)&(H.tc!=0)].tc
    d_all=D[(D.ex==ex)&(D.ac>0)].ac
    p(f'{ex} : PU distincts {len(cat)} ; DEL positifs {len(d_all)} dont hors >=1000 {len(d)} ; = PU {d.isin(cat).sum()} ({d.isin(cat).mean()*100:.2f} %) ; avec les aberrantes {d_all.isin(cat).mean()*100:.2f} %')
    for lb,b in BINS.items():
        cd=pd.cut(d,b); cn=pd.cut(n,b)
        w=cd.value_counts(sort=False); t=n.groupby(cn,observed=False).apply(lambda s: s.isin(cat).mean() if len(s) else np.nan)
        ok=t.notna()
        p(f'    témoin {lb} : {(w[ok]*t[ok]).sum()/w[ok].sum()*100:.1f} %')
out.close()
