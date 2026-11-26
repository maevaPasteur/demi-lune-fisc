"""Chaînage strict des compteurs (série 1 : 16 605 tickets non nuls ; série 2 : 17) et cohérence avec l'heure de clôture."""
import pandas as pd, numpy as np
CA='scripts/lot6-evenement-reglement/cache/'; H=pd.read_pickle(CA+'H.pkl')
out=open('scripts/lot6-evenement-reglement/out/s11_chainage.txt','w')
def p(*a): print(*a); print(*a,file=out)
for s,op in [(1,97773978),(2,5140)]:
    X=H[(H.serie==s)&(H.tot_ttc_c!=0)].sort_values('tot_sum_c').reset_index(drop=True)
    prev=np.r_[op,X.tot_sum_c.values[:-1]]
    ok=(X.tot_sum_c.values-prev==X.tot_ttc_c.values)
    p(f'série {s} : tickets non nuls {len(X)} ; compteurs distincts {X.tot_sum_c.nunique()} ; chaînage exact depuis {op/100:.2f} : {int(ok.sum())}/{len(X)} ; fin {X.tot_sum_c.iloc[-1]/100:.2f}')
    Z=H[(H.serie==s)&(H.tot_ttc_c==0)]
    p(f'   tickets à 0 : {len(Z)} ; leur compteur = un compteur existant ou l\'ouverture : {int(Z.tot_sum_c.isin(set(X.tot_sum_c)|{op}).sum())}')
    X['dt']=X.date_ticket+' '+X.heure_ticket
    inv=(X.dt.values[1:]<X.dt.values[:-1]).sum()
    p(f'   ordre du compteur contre ordre (date, heure de clôture) : inversions {int(inv)} sur {len(X)-1} paires consécutives')
    if inv: 
        k=np.where(X.dt.values[1:]<X.dt.values[:-1])[0][:8]
        for i in k: p('    ',X.loc[i,['date_ticket','heure_ticket','no_ticket','tot_sum']].tolist(),'→',X.loc[i+1,['date_ticket','heure_ticket','no_ticket','tot_sum']].tolist())
    # même contrôle pour la taxe
    Xt=X.sort_values('tot_tax_sum_c'); p('   ordre identique compteur recettes / compteur taxe :',bool((Xt.index.values==X.index.values).all()))
out.close()
