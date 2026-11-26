"""Pièce 72, catégorie « multiple entier » : spécificité. Même règle appliquée aux totaux de notes de la première série (témoin)."""
import pandas as pd
CA='scripts/lot6-evenement-reglement/cache/'
E=pd.read_pickle(CA+'E.pkl'); H=pd.read_pickle(CA+'H.pkl'); CC=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/CC.pkl')
c=lambda x:int(round(float(x)*100))
out=open('scripts/lot6-evenement-reglement/out/s10b_DEL_multiple_placebo.txt','w')
def p(*a): print(*a); print(*a,file=out)
for ex in ['2022-2023','2023-2024','2024-2025']:
    cat=sorted(set(v for v in CC[CC.ex==ex].pu.map(c) if v>0))
    def cls(a):
        if a in cat: return 'carte'
        if a>0 and any(a%pp==0 and a//pp>=2 for pp in cat): return 'multiple'
        return 'aucun'
    d=E[(E.ex==ex)&(E.typEven=='DEL')].amount_c.map(cls).value_counts()
    n=H[(H.ex==ex)&(H.serie==1)&(H.tot_ttc_c!=0)].tot_ttc_c.map(cls).value_counts()
    p(ex,'PU min (c)',cat[:5],' DEL',d.to_dict(),' | témoin totaux de notes',n.to_dict(),f' part carte+multiple notes {(n.get("carte",0)+n.get("multiple",0))/n.sum()*100:.1f} %')
out.close()
