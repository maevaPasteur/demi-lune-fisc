"""Chargement des annexes C-1 à C-3 complètes (source primaire des quantités), sortie cache/CC.pkl ; contrôles vs reconstitution Crec, LC (78), SC (89), F, B."""
import xlrd, pandas as pd, numpy as np
from collections import Counter
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import C, EX, annexe
cols=['date','heure','ticket','datz','z','tot_ttc','tot_tva','tot_rem','id','ref','lib','qte','unite','pu','disc','tva','tot','A','Bs','Cs','Ds','Es','Fs','Gs']
Cs=[]; foots={}
for ex,f in zip(EX,[annexe('C',k) for k in (1,2,3)]):
    s=xlrd.open_workbook(f).sheet_by_index(0)
    rows=[]
    for r in range(1,s.nrows):
        v=s.row_values(r)
        if v[2]=='TOTAL': foots[ex]=v; continue
        if v[0]=='': continue
        rows.append(v)
    df=pd.DataFrame(rows,columns=cols); df['ex']=ex; df['rowC']=np.arange(len(df))+2
    for c in ['ticket','z','id']: df[c]=df[c].astype(float).astype(int)
    for c in ['Cs','Ds','Es','Fs','Gs']: df[c]=pd.to_numeric(df[c].replace('',np.nan),errors='coerce') if c!='Es' else df[c]
    Cs.append(df)
    print(ex,'lignes',len(df),'pied',[foots[ex][i] for i in [11,16,17,18,19,20,21,22]])
CC=pd.concat(Cs,ignore_index=True); CC['lib_s']=CC.lib.astype(str).str.strip()
CC['frac']=(CC.qte-CC.qte.round()).abs()>1e-9
CC.to_pickle(C+'CC.pkl'); pd.to_pickle(foots,C+'C_foot.pkl')
for ex,g in CC.groupby('ex'):
    f=foots[ex]
    print(ex,'ΣQté',round(g.qte.sum(),2),'(pied',f[11],') ΣTTC',round(g.tot.sum(),2),'(pied',f[16],') ΣA',round(g.A.sum(),3),' ΣC',round(g.Cs.sum(),2),'(pied',f[19],') ΣD',round(g.Ds.sum(),2),'(pied',f[20],')',
      '| ids',g.id.nunique(),' (date,ticket)',g[['date','ticket']].drop_duplicates().shape[0],' lignes frac',g.frac.sum(),' notes frac',g[g.frac].id.nunique(),
      ' max ligne',g.tot.max(),' max qté',g.qte.max(),' max Tot_ttc note',g.tot_ttc.max())
r2=lambda x:int(round(float(x)*100))
SC=pd.read_pickle(C+'SC.pkl'); LC=pd.read_pickle(C+'LC.pkl'); Cr=pd.read_pickle(C+'Crec.pkl'); F=pd.read_pickle(C+'F.pkl')
for ex in EX:
    c=CC[CC.ex==ex]; s=SC[SC.ex==ex]
    m1=Counter(zip(c.pu.map(r2),c.qte.map(r2),c.tot.map(r2))); m2=Counter(zip(s.puC.map(r2),s.qteC.map(r2),s.caC.map(r2)))
    print(ex,'C vs 89 Sources_C (PU,Qté,TTC) : only C',sum((m1-m2).values()),' only 89',sum((m2-m1).values()))
    k1=Counter(zip(c.date,c.ticket,c.lib_s,c.pu.map(r2),c.qte.map(r2),c.tot.map(r2))); cr=Cr[Cr.ex==ex]
    k2=Counter(zip(cr.date,cr.ticket,cr.lib.str.strip(),cr.pu.map(r2),cr.qteC.map(r2),cr.tot.map(r2)))
    print('   C vs reconstitution Crec (date,ticket,lib,PU,QtéC,TTC): only C',sum((k1-k2).values()),' only Crec',sum((k2-k1).values()))
    # B lines keyed with B qty
    k3=Counter(zip(cr.date,cr.ticket,cr.lib.str.strip(),cr.pu.map(r2),cr.tot.map(r2))); k4=Counter(zip(c.date,c.ticket,c.lib_s,c.pu.map(r2),c.tot.map(r2)))
    oc=k4-k3
    print('   C vs B (date,ticket,lib,PU,TTC): only B',sum((k3-k4).values()),' only C',sum(oc.values()),' montant only C',round(sum(k[4]*v for k,v in oc.items())/100,2))
    lc=LC[LC.ex==ex]; cf=c[c.frac]
    k5=Counter(zip(cf.date,cf.ticket,cf.id,cf.lib_s,cf.pu.map(r2),cf.qte.map(r2),cf.tot.map(r2),cf.Cs.map(r2),cf.Ds.map(r2)))
    k6=Counter(zip(lc.date.astype(str),lc.note.astype(int),lc.id.astype(int),lc.lib.astype(str).str.strip(),lc.pu.map(r2),lc.qte.map(r2),lc.enc.map(r2),lc.colC.map(r2),lc.colD.map(r2)))
    print('   C frac vs 78 Lignes C (toutes colonnes) : only C',sum((k5-k6).values()),' only 78',sum((k6-k5).values()))
# id/heure C vs F
Fid=F.groupby('id').agg(h=('heureTicket','first'),d=('dateTicket','first'),tk=('no_ticket','first'),totF=('tot_ttc','first'))
n=CC.drop_duplicates('id').set_index('id')
j=n.join(Fid,how='left')
print('ids C absents de F :',j.h.isna().sum(),' heure C≠F :',(j.h.notna()&(j.heure!=j.h)).sum(),' date≠',(j.d.notna()&(j.date!=j.d)).sum(),' ticket≠',(j.tk.notna()&(j.ticket!=j.tk)).sum(),' Tot_ttc≠',(j.totF.notna()&((j.tot_ttc-j.totF).abs()>0.005)).sum())
print(j[j.h.isna()][['ex','date','heure','ticket','tot_ttc']].to_string())
print('ids F absents de C :',len(set(Fid.index)-set(n.index)))
# Tot_ttc vs somme lignes
s=CC.groupby('id').agg(t=('tot','sum'),tt=('tot_ttc','first'))
print('notes C : Σ lignes ≠ Tot_ttc :',((s.t-s.tt).abs()>0.005).sum())
