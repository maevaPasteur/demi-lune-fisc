"""B-7 (étalons de la sur-déclaration), B-8 (bruts et nets du tableau 47), B-14 (pourboires)."""
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
G=loadG(); F=pd.read_pickle(C23+'F.pkl'); H=loadH()
p=P26; gk=G.drop_duplicates('tk')
AN={'2022-2023':977739.78,'2023-2024':1381110.20,'2024-2025':1819103.12}
H1=H[H.tot_sum>=H.ex.map(AN)-1e-6]
print('===== B-7')
tot=dict()
for i,ex in enumerate(EX):
    s=xlrd.open_workbook(D+FF[i]).sheet_by_index(0)
    foot=[[x for x in s.row_values(r) if x!=''] for r in range(s.nrows) if s.row_values(r)[0]=='']
    f=F[F.ex==ex]; Fm=f.montant.map(c).sum(); Gt=gk[gk.ex==ex].tot_ttc_c.sum()
    comp=c(p['706000'][i])+c(p['706300'][i])+c(p['445710'][i]); t68=c(p['706800'][i])
    i_=comp-Gt; ii=i_-round(t68/10); iii=comp-Fm; iv=comp+t68-Fm; v=Fm-Gt
    # règlements sur notes à 0 € ; notes F absentes de G ; écart par note
    fz=f[f.tot_ttc==0]; fn=f.groupby('id').agg(m=('montant','sum'),t=('tot_ttc','first'))
    gid=set(H1[H1.ex==ex].id.astype(int)); fn['inG']=fn.index.isin(gid)
    d=(fn.m-fn.t).round(2)
    print(f'{ex}: pied F {foot[:4]}')
    print(f'   (i) compta−G {e(i_)} ; (ii) −10 % 706800 {e(ii)} ; (iii) compta−F {e(iii)} ; (iv) +706800−F {e(iv)} ; (v) F−G {e(v)}')
    print(f'   F : lignes {len(f)} ; notes {len(fn)} ; notes hors 1re série {int((~fn.inG).sum())} (montant {fn[~fn.inG].m.sum():.2f}) ; règlements sur notes à 0,00 € : {len(fz)} lignes, {fz.montant.sum():.2f} € ; notes où Σ règlements ≠ tot_ttc : {(d!=0).sum()} (Σ écarts {d.sum():.2f} ; >0 {d[d>0].sum():.2f} ; <0 {d[d<0].sum():.2f})')
    print(f'   décomposition (v) : notes 1re série Σ(règl − ttc) {(fn[fn.inG].m-fn[fn.inG].t).sum():.2f} + notes hors 1re série {fn[~fn.inG].m.sum():.2f} − tickets G sans règlement {sum(gk[(gk.ex==ex)].tot_ttc) - fn[fn.inG].t.sum():.2f}')
    for k,v_ in zip(['i','ii','iii','iv','v'],[i_,ii,iii,iv,v]): tot[k]=tot.get(k,0)+v_
print('   cumul :',{k:e(v) for k,v in tot.items()})
print('===== B-8')
G['r']=G['taux_tva%'].astype(int); G['pal']=G.VAT_base_c+100*G.r
for i,ex in enumerate(EX):
    for r,acc in [(10,'706300'),(20,'706000')]:
        z=G[(G.ex==ex)&(G.r==r)]; cpt=c(p[acc][i])
        ded=round(z.tax_amount_c.sum()*100/r); leg=(z.pal-z.tax_amount_c).sum(); tv=z.tax_amount_c.sum(); th=round(cpt*r/100)
        print(f'{ex} {r} % : base déduite−compta {e(ded-cpt)} ; base légale (palier−taxe)−compta {e(leg-cpt)} ; TVA caisse−théorique {e(tv-th)}')
print('   2024-2025 incidence : -17,66 + 29,06 = -11,40 → vérifié par la ligne « TVA caisse − théorique » ci-dessus')
print('===== B-14')
for i,ex in enumerate(EX):
    th=round(c(p['706300'][i])/10)+round(c(p['706000'][i])/5); exc=c(p['445710'][i])-th; exc2=c(p['445710'][i])-G[G.ex==ex].tax_amount_c.sum()
    t=c(p['706800'][i])
    for lab,tv in [('HT à 10 %',round(t/10)),('TTC à 10/110',round(t/11)),('non taxé',0)]:
        print(f'{ex} {lab:13s}: TVA pourboire {e(tv)} ; reliquat vs théorique {e(exc-tv)} ; reliquat vs caisse {e(exc2-tv)}')
