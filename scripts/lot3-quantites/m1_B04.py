"""Les 64 notes isolées, note par note et ligne par ligne ; contreparties dans la journée ; DEL miroirs. Sorties : cache/out/B04_*.csv."""
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
Cr,F,E,Fid,tabs,nd,A=load()
D=E[E.typEven=='DEL']
iso=[x[0] for ex,d,x in tabs if len(x)==1]
Cr['neg']=Cr.B< -0.005
notes=[]; L=[]
for i in iso:
    x=Cr[Cr.id==i]; d=x.date.iloc[0]; t=Fid.t[i]; xf=x[x.fracC]
    # contrepartie : autre note du jour, même article et PU, fraction qui complète à un entier (avec la fraction de cette note)
    day=Cr[(Cr.date==d)&(Cr.id!=i)]
    cp=[]; 
    for r in xf.itertuples():
        o=day[(day.libn==r.libn)&(day.pu100==r.pu100)&day.fracC]
        ok=o[((o.qteC+r.qteC)-(o.qteC+r.qteC).round()).abs()<0.02]
        cp.append((ok.t-t).abs().min() if len(ok) else np.nan)
        L.append(dict(ex=r.ex,date=d,ticket=r.ticket,id=i,lib=r.lib_s,qC=r.qteC,qB=r.qte,tot=r.tot,ecartB=r.B,pu=r.pu,
                      comp_ceil=round((math.ceil(r.qteC-1e-9)-r.qteC)*r.pu,4),comp_B=max(0,(r.qte-r.qteC)*r.pu),contrepartie_min=cp[-1]))
    # DEL miroir : toutes les lignes de la note retrouvées en DEL de même montant dans [t-5 ; t+30]
    g=D[(D.dateEven==d)&(D.t>=t-5)&(D.t<=t+30)]; used=set(); n=0; dt=[]
    for a in x.tot:
        c=[j for j in g.index[(g.amount-a).abs()<=0.02] if j not in used]
        if c: used.add(c[0]); n+=1; dt.append(g.at[c[0],'t']-t)
    notes.append(dict(ex=x.ex.iloc[0],date=d,ticket=x.ticket.iloc[0],id=i,heure=Fid.heure[i],totF=Fid.tot[i],mode=Fid.mods[i],lignes=len(x),lignes_frac=len(xf),
        enc_frac=round(xf.tot.sum(),2),comp_ceil=round(sum((math.ceil(q-1e-9)-q)*p for q,p in zip(xf.qteC,xf.pu)),2),
        comp_B=round(sum(max(0,(qb-qc)*p) for qb,qc,p in zip(xf.qte,xf.qteC,xf.pu)),2),neg_B=int(x.neg.sum()),
        contrepartie_jour=int(np.isfinite(cp).sum()) if cp else 0,ecart_min_contrepartie=np.nanmin(cp) if np.isfinite(cp).any() else np.nan,
        DEL_miroir=f'{n}/{len(x)}',DEL_decalage=(min(dt),max(dt)) if dt else None))
N=pd.DataFrame(notes).sort_values(['date','ticket']); Ld=pd.DataFrame(L)
N.to_csv(OUT+'B04_notes.csv',index=False); Ld.to_csv(OUT+'B04_lignes.csv',index=False)
pd.set_option('display.width',260); print(N.to_string(index=False))
N['miroir_complet']=N.DEL_miroir.map(lambda s: s.split('/')[0]==s.split('/')[1])
N['cp']=N.contrepartie_jour>0
S=N.groupby('ex').agg(notes=('id','size'),lignes=('lignes','sum'),lignes_frac=('lignes_frac','sum'),totF=('totF','sum'),enc_frac=('enc_frac','sum'),comp_ceil=('comp_ceil','sum'),
   comp_B=('comp_B','sum'),notes_negB=('neg_B',lambda s:(s>0).sum()),notes_contrepartie=('cp','sum'),notes_miroir_DEL=('miroir_complet','sum'))
S.loc['Total']=S.sum(); print(S.round(2).to_string()); S.round(2).to_csv(OUT+'B04_synthese.csv')
