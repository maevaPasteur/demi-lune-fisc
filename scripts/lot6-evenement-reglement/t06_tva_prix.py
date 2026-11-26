"""Contrôles B-16 a-b (références mal paramétrées ; dénombrements), B-18 (placebo des prix de carte par tranche ; décalage ±0,10 €)."""
import pandas as pd, numpy as np
CA='scripts/lot6-evenement-reglement/cache/'
X=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot25/C_b3.pkl'); A=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot25/B3_articles.pkl')
E=pd.read_pickle(CA+'E.pkl'); H=pd.read_pickle(CA+'H.pkl'); CC=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/CC.pkl'); B=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/B.pkl')
c=lambda x:int(round(float(x)*100))
out=open('scripts/lot6-evenement-reglement/out/t06_tva_prix.txt','w')
def p(*a): print(*a); print(*a,file=out)
p('== B-16 a. Lignes où taux appliqué ≠ taux légal (référence classée)')
w=X[X.tl.notna()&(X.rart!=X.tl)]
g=w.groupby(['ref','lib_s']).agg(lignes=('tot','size'),premiere=('date','min'),derniere=('date','max'),taux_app=('rart',lambda s:sorted(s.unique())),taux_legal=('tl','first'))
p(g.to_string())
for r in g.index.get_level_values(0).unique():
    a=X[X.ref==r]
    p(f'  réf {r} : taux appliqués sur toute la période {sorted(a.rart.unique())} ; lignes {len(a)} ; première vente {a.date.min()} ; dernière {a.date.max()} ; dernière date de données {X.date.max()}')
p('\n== B-16 b. Dénombrements de références')
p('  réf. distinctes par exercice (C) :',X.groupby('ex').ref.nunique().to_dict(),' ; sur 3 exercices :',X.ref.nunique(),' ; (réf., libellé) distincts :',X[['ref','lib_s']].drop_duplicates().shape[0])
p('  réf. de C avec taux appliqué unique :',int((X.groupby('ref').rart.nunique()==1).sum()),'/',X.ref.nunique())
p('  B3_articles (lot 2.5, classification légale) : lignes',len(A),' colonnes',list(A.columns)[:8])
p('  réf. de B :',B.ref.nunique(),' ; réf. B ∪ C :',len(set(B.ref)|set(X.ref)),' ; réf. de B absentes de C :',sorted(set(B.ref)-set(X.ref))[:10])
p('  réf. de C sur les 17 notes de série 2 seulement :',sorted(set(X[X.id.isin(H[(H.serie==2)].id)].ref)-set(X[~X.id.isin(H[(H.serie==2)].id)].ref)))
# ---- B-18
p('\n== B-18. Prix de carte : DEL contre totaux de notes, par tranche ; montants DEL décalés de ±0,10 € (1 000 tirages, graine 20261123)')
bins=[0,500,1000,2000,5000,10000,10**9]; lab=['≤5','5-10','10-20','20-50','50-100','>100']
rows=[]
rng=np.random.default_rng(20261123)
for ex in ['2022-2023','2023-2024','2024-2025']:
    cat=set(v for v in CC[CC.ex==ex].pu.map(c) if v>0)
    d=E[(E.ex==ex)&(E.typEven=='DEL')&(E.amount_c>0)&(E.amount_c<100000)].amount_c
    n=H[(H.ex==ex)&(H.serie==1)&(H.tot_ttc_c!=0)].tot_ttc_c
    for x,lb in [(d,'DEL'),(n,'notes')]:
        cut=pd.cut(x,bins,labels=lab)
        for t in lab:
            s=x[cut==t]; rows.append((ex,lb,t,len(s),round(s.isin(cat).mean()*100,1) if len(s) else np.nan))
    sh=[]
    dv=d.values
    for _ in range(1000):
        s=dv+rng.choice([-10,10],len(dv)); sh.append(np.isin(s,list(cat)).mean())
    p(f'  {ex} : DEL = PU {np.isin(dv,list(cat)).mean()*100:.1f} % ; DEL ± 0,10 € = PU : moyenne {np.mean(sh)*100:.1f} %, max {np.max(sh)*100:.1f} %')
R=pd.DataFrame(rows,columns=['ex','série','tranche','n','% = PU']).pivot_table(index=['ex','tranche'],columns='série',values=['n','% = PU'],sort=False)
p(R.to_string())
out.close()
out=open('scripts/lot6-evenement-reglement/out/t06_tva_prix.txt','a')
p('Témoin standardisé : taux des notes par tranche, pondéré par la répartition des DEL (tranches où n notes ≥ 1)')
for ex in ['2022-2023','2023-2024','2024-2025']:
    r=R.loc[ex]; w=r[('n','DEL')]; t=r[('% = PU','notes')].fillna(0)
    p(f'  {ex} : {float((w*t).sum()/w.sum()):.1f} % (DEL {float((w*r[("% = PU","DEL")]).sum()/w.sum()):.1f} %)')
out.close()
