"""M0-3 : 2.6.5 ; B contre C ligne à ligne (tableau 64), colonne de contrôle A / B-Ecart (tableau 65), remises,
exemple du 14/04/2022 notes 11 et 12 (tableau 66), Expresso 2022-2023, origine des 17 561,00 €."""
import pandas as pd, numpy as np, xlrd
from collections import Counter
CA='scripts/lot6-evenement-reglement/cache/'; D='public/documents/caisse-enregistreuse/'
EX=['2022-2023','2023-2024','2024-2025']
c=lambda x:int(round(float(x)*100)); q=lambda x:int(round(float(x)*1000)); e=lambda n:f"{n/100:,.2f}".replace(',',' ').replace('.',',')
out=open('scripts/lot6-evenement-reglement/out/s08_B_contre_C.txt','w')
def p(*a):
    print(*a); print(*a,file=out)
B=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/B.pkl'); CC=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/CC.pkl'); H=pd.read_pickle(CA+'H.pkl')
# contrôle des caches 2.3 contre les pieds des xls (relus)
for ex,fb,fc in zip(EX,['24-annexe-b1-2022-2023.xls','25-annexe-b2-2023-2024.xls','26-annexe-b3-2024-2025.xls'],['17-annexe-c1-2022-2023.xls','18-annexe-c2-2023-2024.xls','19-annexe-c3-2024-2025.xls']):
    sb=xlrd.open_workbook(D+fb).sheet_by_index(0); fbv=sb.row_values(sb.nrows-1)
    sc=xlrd.open_workbook(D+fc).sheet_by_index(0); fcv=sc.row_values(sc.nrows-1)
    b=B[B.ex==ex]; cc=CC[CC.ex==ex]
    p(f'{ex} : B lignes {len(b)} ; Σqté {round(b.qte.sum(),2)} (pied {fbv[5]}) ; ΣTTC {e(b.tot.map(c).sum())} (pied {fbv[9]}) ; ΣA {round(b.A.sum(),3)} (pied {fbv[10]}) ; ΣB {round(b.B.sum(),3)} (pied {fbv[11]})')
    p(f'        C lignes {len(cc)} ; Σqté {round(cc.qte.sum(),2)} (pied {fcv[11]}) ; ΣTTC {e(cc.tot.map(c).sum())} (pied {fcv[16]}) ; ΣA {round(cc.A.sum(),3)} (pied {fcv[17]}) ; ΣB {round(cc.Bs.sum(),3)} (pied {fcv[18]}) ; ΣF {round(cc.Fs.sum(),2)} (pied {fcv[22]})')
    p(f'        signe colonne B de l\'annexe B : B = TTC − A sur {int(((b.B-(b.tot-b.A)).abs()<1e-6).sum())}/{len(b)} lignes ; = A − TTC sur {int(((b.B-(b.A-b.tot)).abs()<1e-6).sum())} ; colonne B de C = A − TTC sur {int(((cc.Bs-(cc.A-cc.tot)).abs()<1e-6).sum())}/{len(cc)}')
    p(f'        écart A − TTC : B {e(c(b.A.sum())-b.tot.map(c).sum())} ({(b.A.sum()-b.tot.sum())/b.tot.sum()*100:.3f} %) ; C {round(cc.A.sum()-cc.tot.sum(),3)} ({(cc.A.sum()-cc.tot.sum())/cc.tot.sum()*100:.4f} %)')
# ---- B contre C, clé (date, n° ticket, réf, libellé, TTC) en multiensemble
r2=c
p('\nRapprochement multiensemble B / C sur (date, n° ticket, réf, libellé, TTC) :')
tot75=0
for ex in EX:
    b=B[B.ex==ex]; cc=CC[CC.ex==ex]
    kb=Counter(zip(b.date,b.ticket,b.ref.astype(str).str.strip(),b.lib.astype(str).str.strip(),b.tot.map(r2)))
    kc=Counter(zip(cc.date,cc.ticket,cc.ref.astype(str).str.strip(),cc.lib.astype(str).str.strip(),cc.tot.map(r2)))
    ob=kb-kc; oc=kc-kb
    p(f'  {ex} : B {len(b)} ; C {len(cc)} ; B absentes de C {sum(ob.values())} ; C absentes de B {sum(oc.values())} ; montant C absentes {e(sum(k[4]*v for k,v in oc.items()))} ; tickets concernés {len(set((k[0],k[1]) for k in oc))}')
    tot75+=sum(oc.values())
# ambiguïté de la clé (date, n° ticket) : n° de ticket répétés le même jour dans H
dup=H.groupby(['date_ticket','no_ticket']).size(); p('  (date, n° ticket) portés par plusieurs notes dans H :',int((dup>1).sum()),' ; dont jours avec note de série 2 non nulle :',
  int(sum(1 for (d,t),n in dup[dup>1].items() if ((H.date_ticket==d)&(H.no_ticket==t)&(H.serie==2)&(H.tot_ttc_c!=0)).any())))
# ---- rapprochement par note : lignes de C rattachées à l'id ; B n'a pas d'id : on compare par (date, ticket) pour les notes de série 1 uniques
# ---- 17 561,00 € : origine. Appariement ligne à ligne via Crec (lot 2.3, Qté B rattachée à chaque ligne C)
Cr=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/Crec.pkl')
p('\nCrec (lot 2.3) colonnes :',list(Cr.columns)[:30])
for ex in EX:
    x=Cr[Cr.ex==ex]
    if 'qteB' in x.columns:
        diff=(x.qteB-x.qteC).abs()>1e-9
        eb=(x.pu*x.qteB-x.tot)
        p(f'  {ex} : lignes C appariées {x.qteB.notna().sum()} ; Qté B ≠ Qté C {int(diff.sum())} ; Σ(PU×QtéB − TTC) sur ces lignes {e(c(eb[diff].sum()))} ; sur les autres {e(c(eb[~diff & x.qteB.notna()].sum()))}')
# ---- remises dans C
for ex in EX:
    cc=CC[CC.ex==ex]; d=cc[cc.disc!=0]
    res=cc.A.sum()-cc.tot.sum(); rd=(d.A-d.tot).sum()
    p(f'  {ex} : lignes à remise {len(d)} ; Σ(A − TTC) remises {round(rd,3)} ; résidu hors remises {round(res-rd,3)} ; taux {sorted(d.disc.unique())}')
    if len(d): p(d[['date','ticket','lib','qte','pu','disc','tot','A']].to_string())
# ---- exemple 14/04/2022, notes 11 et 12
p('\nExemple 14/04/2022 notes 11 et 12 :')
cb=B[(B.date=='2022-04-14')&(B.ticket.isin([11,12]))][['ticket','ref','lib','qte','pu','tot','A','B']]
cc=CC[(CC.date=='2022-04-14')&(CC.ticket.isin([11,12]))][['ticket','heure','id','ref','lib','qte','pu','tot','tot_ttc']]
p('B :'); p(cb.to_string()); p('C :'); p(cc.to_string())
p('Σ qté B',cb.qte.sum(),' Σ qté C',cc.qte.sum(),' Σ TTC B',round(cb.tot.sum(),2),' Σ TTC C',round(cc.tot.sum(),2),' tot_ttc notes',cc.groupby('ticket').tot_ttc.first().to_dict())
# ---- Expresso 2022-2023
for nm in ['Expresso']:
    b=B[(B.ex=='2022-2023')&(B.lib.str.strip()==nm)]; cc=CC[(CC.ex=='2022-2023')&(CC.lib.str.strip()==nm)]
    p(f'\n{nm} 2022-2023 : lignes B {len(b)} C {len(cc)} ; unités B {b.qte.sum()} C {cc.qte.sum()} ; TTC B {round(b.tot.sum(),2)} C {round(cc.tot.sum(),2)}')
    p('  répartition Qté B :',b.qte.round(2).value_counts().sort_index().to_dict()); p('  répartition Qté C :',cc.qte.round(2).value_counts().sort_index().to_dict())
# lignes et quantités arrondies
p('\nQuantités (pieds) arrondies à l\'unité : B',[round(B[B.ex==ex].qte.sum()) for ex in EX],' C',[round(CC[CC.ex==ex].qte.sum()+1e-9) for ex in EX],
  ' écarts',[round(B[B.ex==ex].qte.sum()-CC[CC.ex==ex].qte.sum(),2) for ex in EX])
out.close()
