"""D-9 : les quatre lignes DEL ≥ 1 000 €. Décompositions « prix unitaire de la carte de l'exercice (annexes C et B) × quantité entière »,
notes et tickets à 0 € de la même minute et de la suivante. Sortie : out/B1/D09.txt"""
import sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from B1_common import *
C,E,F,H,A=load(); p=out('D09.txt')
B=pd.read_pickle('scripts/lot3-quantites/cache/B.pkl')
p(f'Contrôle : 27,40 × 2 518 = {27.40*2518:.2f} € ; 6,90 × 9 999 = {6.90*9999:.2f} €')
big=E[(E.typEven=='DEL')&(E.ac>=100000)]
for _,r in big.iterrows():
    ex=r.ex; ac=r.ac
    pc=set((C[(C.ex==ex)&(C.pu>0)].pu*100).round().astype(int))|set((B[(B.ex==ex)&(B.pu>0)].pu*100).round().astype(int))
    dec=sorted([(u/100,ac//u) for u in pc if ac%u==0 and ac//u>=2])
    p(f'{r.dateEven} {r.heureEven} Z {r.no_zEport} id {r.id} : {r.amount:.2f} € ; {len(dec)} décompositions PU × quantité entière (PU de la carte {ex}) :')
    for u,q in dec:
        libs=sorted(set(C[(C.ex==ex)&((C.pu*100).round()==round(u*100))].libs))
        p(f'     {u:.2f} € × {q} ; articles à ce prix : {libs[:6]}')
    for k in (0,1):
        t=r.t+k
        n=H[(H.date_ticket==r.dateEven)&(H.t==t)]
        p(f'   tickets H clos à {t//60:02d}:{t%60:02d} :',n[['no_ticket','id','tot_ttc','serie']].values.tolist())
        for i in n.id: p('      ',i,C[C.id==i][['libs','qte','pu']].values.tolist())
    p('   autres DEL de la minute et de la suivante :',E[(E.dateEven==r.dateEven)&(E.typEven=='DEL')&(E.t.between(r.t,r.t+1))&(E.id!=r.id)][['heureEven','amount','id']].values.tolist())
