"""s10 : rapprochement CA TTC / HT / TVA par exercice selon C, H, G, F et comptes p.26 ; décomposition des écarts."""
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
G=loadG(); H=loadH(); CC=loadC(); F=pd.read_pickle(C23+'F.pkl')
gk=G.drop_duplicates('tk')
for i,ex in enumerate(EX):
    g=gk[gk.ex==ex]; h=H[H.ex==ex]; cc=CC[CC.ex==ex]; f=F[F.ex==ex]
    cn=cc.drop_duplicates('id')
    Gt,Gv=g.tot_ttc_c.sum(),g.tot_tva_c.sum(); Ht,Hv=h.tot_ttc.map(c).sum(),h.tot_tva.map(c).sum()
    Ct,Cv=cn.tot_ttc.map(c).sum(),cn.tot_tva.map(c).sum(); Cl=cc.tot.map(c).sum()
    Fm=f.montant.map(c).sum(); Ft=f.drop_duplicates('id').tot_ttc.map(c).sum()
    # H : seconde série = lignes dont le compteur tot_sum n'appartient pas à la série principale (< AN)
    AN={'2022-2023':977739.78,'2023-2024':1381110.20,'2024-2025':1819103.12}[ex]
    h2=h[h.tot_sum<AN-1e-6]
    p=P26; cpt_ttc=c(p['706000'][i])+c(p['706300'][i])+c(p['445710'][i]); cpt_ht=c(p['706000'][i])+c(p['706300'][i])
    print(f'===== {ex}')
    print(f'  G : TTC {e(Gt)} TVA {e(Gv)} HT {e(Gt-Gv)} ({len(g)} tickets)')
    print(f'  H : TTC {e(Ht)} TVA {e(Hv)} ({len(h)} lignes) ; seconde série (tot_sum < A NOUVEAUX) : {len(h2)} lignes, {(h2.tot_ttc!=0).sum()} non nulles, TTC {e(h2.tot_ttc.map(c).sum())} TVA {e(h2.tot_tva.map(c).sum())} ; H − G : TTC {e(Ht-Gt)} TVA {e(Hv-Gv)}')
    print(f'  C : Σ Tot_ttc par note {e(Ct)} ; Σ lignes Tot_rem_Ttc {e(Cl)} ; Σ Tot_tva {e(Cv)} ({len(cn)} notes)')
    print(f'  F : Σ montants règlements {e(Fm)} ; Σ tot_ttc par note {e(Ft)} ; F − G {e(Fm-Gt)}')
    print(f'  Compta (706000+706300+445710) {e(cpt_ttc)} ; HT {e(cpt_ht)} ; + 706800 = {e(cpt_ttc+c(p["706800"][i]))} vs imprimé {p["TOT"][i]}')
    print(f'  Compta − G : TTC {e(cpt_ttc-Gt)} = TVA {e(c(p["445710"][i])-Gv)} + HT {e(cpt_ht-(Gt-Gv))}')
    print(f'  Compta − H(total) : TTC {e(cpt_ttc-Ht)} ; TVA {e(c(p["445710"][i])-Hv)}')
    print(f'  Compta − F : TTC {e(cpt_ttc-Fm)} ; avec 706800 : {e(cpt_ttc+c(p["706800"][i])-Fm)}')
