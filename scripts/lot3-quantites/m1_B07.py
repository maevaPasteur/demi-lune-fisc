"""Chargement de l'annexe H (cache/H.pkl), puis tickets clôturés à 0,00 € (annexes H) autour des tables 77, contre témoin (graine 20261123)."""
import os, sys, xlrd; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
rng=np.random.default_rng(20261123)
Cr,F,E,Fid,tabs,nd,A=load()
H=[]
for ex,f in zip(EX,['ANNEXE-H1_liste-tickets_2022-2023.xls','ANNEXE-H2_liste-tickets_2023-2024.xls','ANNEXE-H3_liste-tickets_2024-2025.xls']):
    s=xlrd.open_workbook(CAISSE+f).sheet_by_index(0); hdr=s.row_values(0)
    rows=[s.row_values(r) for r in range(1,s.nrows) if str(s.row_values(r)[0])[:2]=='20']
    h=pd.DataFrame(rows,columns=hdr); h['ex']=ex; H.append(h)
H=pd.concat(H,ignore_index=True); H['t']=H.heure_ticket.map(tmin); H['no']=H.no_ticket.astype(float).astype(int)
H.to_pickle(C+'H.pkl')
print('tickets H',H.groupby('ex').size().to_dict(),' dont tot_ttc = 0 :',H[H.tot_ttc==0].groupby('ex').size().to_dict(),' total',(H.tot_ttc==0).sum())
print('Σ tot_ttc H',H.groupby('ex').tot_ttc.sum().round(2).to_dict())
Z=H[H.tot_ttc==0]; Zd={d:g for d,g in Z.groupby('date_ticket')}
frac_ids=set(Cr[Cr.fracC].id); notes_day={d:g for d,g in Cr.drop_duplicates('id').groupby('date')}
rows=[]; ctl=[]
for k,(ex,d,ids) in enumerate(tabs):
    if len(ids)<2: continue
    ts=[Fid.t[i] for i in ids]; tks=set(nd.tk[i] for i in ids)
    z=Zd.get(d, Z.iloc[0:0]); w=z[(z.t>=min(ts)-30)&(z.t<=max(ts))]
    rows.append(dict(ex=ex,n0=len(w),n0_meme_no=int(w.no.isin(tks).sum())))
    nd0=notes_day[d]; cand=nd0[(~nd0.id.isin(frac_ids))&((nd0.t-min(ts)).abs()<=60)&nd0.id.isin(Fid.index)]
    if len(cand):
        j=cand.id.values[rng.integers(len(cand))]; tj=Fid.t[j]; tk=nd0[nd0.id==j].ticket.iloc[0]
        w2=z[(z.t>=tj-30)&(z.t<=tj)]; ctl.append(dict(ex=ex,n0=len(w2),n0_meme_no=int((w2.no==tk).sum())))
R=pd.DataFrame(rows); Q=pd.DataFrame(ctl)
print('tables : moyenne tickets 0 € dans [1re−30 ; dernière]',round(R.n0.mean(),3),' part ≥1',round((R.n0>0).mean()*100,1),'% ; dont même n° qu une note de la table : moyenne',round(R.n0_meme_no.mean(),3),' part ≥1',round((R.n0_meme_no>0).mean()*100,1),'%')
print('témoin : moyenne',round(Q.n0.mean(),3),' part ≥1',round((Q.n0>0).mean()*100,1),'% ; même n° : moyenne',round(Q.n0_meme_no.mean(),3),' part ≥1',round((Q.n0_meme_no>0).mean()*100,1),'% (n',len(Q),')')
print(R.groupby('ex').agg(m=('n0','mean'),p=('n0',lambda s:(s>0).mean()),mn=('n0_meme_no','mean')).round(3), Q.groupby('ex').agg(m=('n0','mean'),p=('n0',lambda s:(s>0).mean()),mn=('n0_meme_no','mean')).round(3))
# même fenêtre pour toutes les notes encaissées : base
