"""Contrôles B-4, B-5, B-16 c. Appariement multiensemble B / C ; quantités ; clé avec Qté ; PU × Qté ≠ montant."""
import pandas as pd, numpy as np, xlrd
from collections import Counter, defaultdict
c=lambda x:int(round(float(x)*100)); q=lambda x:int(round(float(x)*1000)); e=lambda n:f"{n/100:,.2f}".replace(',',' ').replace('.',',')
B=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/B.pkl'); CC=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/CC.pkl')
out=open('scripts/lot6-evenement-reglement/out/t02_BC_quantites.txt','w')
def p(*a): print(*a); print(*a,file=out)
EX=['2022-2023','2023-2024','2024-2025']
for df in (B,CC):
    df['k']=list(zip(df.date,df.ticket,df.ref.astype(str).str.strip(),df.lib.astype(str).str.strip(),df.tot.map(c)))
    df['pu_c']=df.pu.map(c); df['q_m']=df.qte.map(q)
p('== B-4. Appariement (date, n° ticket, réf., libellé, TTC) ; dans chaque groupe de clé, appariement par rang de quantité croissante')
tot=[]
for ex in EX:
    b=B[B.ex==ex]; cc=CC[CC.ex==ex]
    gb=defaultdict(list); gc=defaultdict(list)
    for k,qq,pu,d,t in zip(b.k,b.q_m,b.pu_c,b.date,b.ticket): gb[k].append(qq)
    for k,qq in zip(cc.k,cc.q_m): gc[k].append(qq)
    pairs=[]; amb=0
    for k,lb in gb.items():
        lc=gc.get(k,[])
        if len(set(lb))>1 or len(set(lc))>1: amb+=1
        for x,y in zip(sorted(lb),sorted(lc)): pairs.append((k,x,y))
    P=pd.DataFrame([(k[0],k[1],k[4],x,y) for k,x,y in pairs],columns=['date','ticket','tot','qB','qC'])
    pu=dict(zip(b.k,b.pu_c))
    P['pu']=[pu[k] for k,_,_ in pairs]
    d=P[P.qB!=P.qC]
    tot.append(len(d))
    p(f'{ex} : paires {len(P)} ; Qté B ≠ Qté C {len(d)} ; tickets (date, n°) {d[["date","ticket"]].drop_duplicates().shape[0]} ; jours {d.date.nunique()} ; '
      f'Σ(QtéB − QtéC) {(d.qB-d.qC).sum()/1000:.2f} ; Σ(QtéB − QtéC) × PU {e(round(((d.qB-d.qC)*d.pu).sum()/1000))} ; paires QtéC > QtéB {int((P.qC>P.qB).sum())} ; groupes de clé à quantités multiples (appariement par rang) {amb}')
    # B seul : PU × Qté ≠ TTC
    bb=b[(b.pu_c*b.q_m/1000-b.tot.map(c)).abs()>=1]
    p(f'     B : lignes PU × Qté ≠ TTC (≥ 0,01 €) {len(bb)} ; Σ(PU×Qté − TTC) {e(round((bb.pu_c*bb.q_m/1000-bb.tot.map(c)).sum()))} ; C : lignes {int(((cc.pu_c*cc.q_m/1000-cc.tot.map(c)).abs()>=1).sum())}')
p('Total paires Qté B ≠ Qté C :',sum(tot),' (lot 2.3 : 7 146)')
p('\n== B-5. Clé avec la quantité (date, ticket, réf., libellé, TTC, Qté)')
for ex in EX:
    b=B[B.ex==ex]; cc=CC[CC.ex==ex]
    kb=Counter(zip(b.k,b.q_m)); kc=Counter(zip(cc.k,cc.q_m))
    ob=kb-kc; oc=kc-kb
    p(f'{ex} : lignes de B sans correspondant dans C {sum(ob.values())} ({sum(ob.values())/len(b)*100:.2f} %) ; montant {e(sum(k[0][4]*v for k,v in ob.items()))} ; lignes de C sans correspondant {sum(oc.values())} ; montant {e(sum(k[0][4]*v for k,v in oc.items()))}')
p('\n== 33 220 (R2) contre 33 222 (R1), 2022-2023 : lignes physiques du fichier B-1')
for f in ['24-annexe-b1-2022-2023.xls','17-annexe-c1-2022-2023.xls']:
    s=xlrd.open_workbook('public/documents/caisse-enregistreuse/'+f).sheet_by_index(0)
    vides=sum(1 for r in range(s.nrows) if all(v=='' for v in s.row_values(r)))
    p(f'  {f} : lignes Excel {s.nrows} = 1 en-tête + {s.nrows-1-1-vides} lignes de vente + {vides} ligne vide + 1 ligne de total ; {s.nrows-1} = lignes sous l\'en-tête')
p('\n== B-16 c. Lignes de C où PU × Qté ≠ montant à 0,01 € près')
CC['d']=(CC.pu_c*CC.q_m/1000-CC.tot.map(c))
x=CC[CC.d.abs()>=1]
x=x.assign(type=np.where(x.disc!=0,'remise','autre'))
p(x.groupby(['ex','type']).d.agg(['size','sum']).to_string())
p(x[x.type=='autre'][['ex','date','ticket','lib','qte','pu','tot','d']].head(40).to_string())
out.close()
