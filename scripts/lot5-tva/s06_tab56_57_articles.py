"""s06 : tableaux 56 et 57 (colonnes E/F des annexes C) ; TVA selon taux fichier / corrigés / article ; liste des articles par taux."""
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
CC=pd.read_pickle(CA+'C_taux2.pkl'); G=loadG()
P=P26
tv=lambda t,r: t*r/(100+r)
for ex in EX+['3ex']:
    x=CC if ex=='3ex' else CC[CC.ex==ex]; i=EX.index(ex) if ex in EX else None
    A=tv(x.tot,x.rf).sum(); B=tv(x.tot,x.rc).sum(); R=tv(x.tot,x.rart).sum(); Fsum=x.Fs.sum()
    Bcol=A+Fsum
    c445=sum(P['445710']) if i is None else P['445710'][i]
    g=G if ex=='3ex' else G[G.ex==ex]
    print(f'{ex}: lignes signalées 10/20 {(x.Es=="10 % / 20 %").sum()} ; 20/10 {(x.Es=="20 % / 10 %").sum()} ; total {(x.Es!="").sum()}')
    print(f'   A (taux fichier, Σ TTC×r/(100+r) non arrondi) {A:,.4f} ; B (taux corrigés) {B:,.4f} ; A+ΣF {Bcol:,.4f} ; ΣF {Fsum:,.5f} ; R (taux article par décalage) {R:,.4f}')
    print(f'   B arrondi {round(B,2)} ; B−445710 {round(B,2)-c445:.2f} ; R − Σ tax_amount G {R-g.tax_amount_c.sum()/100:.4f} ; Σ tax_amount G {g.tax_amount_c.sum()/100:.2f}')
    print(f'   lignes arrondies au centime puis sommées : A {sum(round(v+1e-9,2) for v in tv(x.tot,x.rf)):.2f} B {sum(round(v+1e-9,2) for v in tv(x.tot,x.rc)):.2f} R {sum(round(v+1e-9,2) for v in tv(x.tot,x.rart)):.2f}')
    # tableau 57
    v=x[x.tot!=0] ; refs=x.ref.nunique()
    both_f=(x.groupby('ref').rf.nunique()>1).sum(); both_c=(x.groupby('ref').rc.nunique()>1).sum(); both_a=(x.groupby('ref').rart.nunique()>1).sum()
    print(f'   refs vendues {refs} (refs à TTC≠0 : {v.ref.nunique()}) ; aux deux taux : fichier {both_f} ({100*both_f/refs:.1f} %) ; corrigé {both_c} ({100*both_c/refs:.1f} %) ; article {both_a}')
    if ex!='3ex':
        print('   refs aux deux taux après correction :', x.groupby('ref').filter(lambda s:s.rc.nunique()>1).groupby(['ref']).agg(lib=('lib_s','first'),n10=('rc',lambda s:(s==10).sum()),n20=('rc',lambda s:(s==20).sum())).to_dict('index'))
# erreurs du service par article
d=CC[CC.rc!=CC.rart]
print('\nlignes où le taux corrigé du service ≠ taux article :',len(d),' ; par exercice', d.ex.value_counts().to_dict())
print(d.groupby(['ref','lib_s','rart','rc']).size().sort_values(ascending=False).head(25).to_string())
print('  incidence TVA (taux service − taux article) :', {ex:round((tv(d[d.ex==ex].tot,d[d.ex==ex].rc)-tv(d[d.ex==ex].tot,d[d.ex==ex].rart)).sum(),2) for ex in EX})
# liste articles à 20 %
art=CC.groupby('ref').agg(lib=('lib_s',lambda s:s.value_counts().index[0]),taux=('rart','first'),n=('rart','size'),ttc=('tot','sum')).sort_values(['taux','ttc'],ascending=[True,False])
art.to_csv(OUT+'s06_articles_taux.csv')
print('\narticles à 20 % :',(art.taux==20).sum(),' ; à 10 % :',(art.taux==10).sum())
print(art[art.taux==20].lib.tolist())
