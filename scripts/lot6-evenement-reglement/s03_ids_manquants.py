"""Hors liste : 1 158 identifiants de notes absents de H dans l'intervalle 46621-67681.
Association jour par jour avec les RPR (reprises) du journal E ; placebo par permutation des jours (graine 20261123)."""
import pandas as pd, numpy as np
CA='scripts/lot6-evenement-reglement/cache/'
E=pd.read_pickle(CA+'E.pkl'); H=pd.read_pickle(CA+'H.pkl')
out=open('scripts/lot6-evenement-reglement/out/s03_ids_manquants.txt','w')
def p(*a):
    print(*a); print(*a,file=out)
Hs=H.sort_values('id').reset_index(drop=True)
ids=Hs.id.values
rows=[]
for k in range(1,len(ids)):
    g=ids[k]-ids[k-1]-1
    if g>0:
        a=Hs.iloc[k-1]; b=Hs.iloc[k]
        for m in range(ids[k-1]+1,ids[k]):
            rows.append((m,a.date_ticket,b.date_ticket,a.no_z_report,b.no_z_report,a.ex))
M=pd.DataFrame(rows,columns=['id','date_av','date_ap','z_av','z_ap','ex'])
M['meme_jour']=M.date_av==M.date_ap
p('ids manquants',len(M),' encadrés par deux notes du même jour',int(M.meme_jour.sum()),' par exercice',M.groupby('ex').size().to_dict())
# Attribution au jour de la note précédente (ids attribués à l'ouverture)
m_day=M.groupby('date_av').size()
r_day=E[E.typEven=='RPR'].groupby('dateEven').size()
z_day=H[H.tot_ttc_c==0].groupby('date_ticket').size()
n_day=H.groupby('date_ticket').size()
days=sorted(set(H.date_ticket))
T=pd.DataFrame({'manq':m_day.reindex(days,fill_value=0),'rpr':r_day.reindex(days,fill_value=0),'zero':z_day.reindex(days,fill_value=0),'notes':n_day.reindex(days,fill_value=0)})
p('jours',len(T),' Σ manquants',T.manq.sum(),' Σ RPR',T.rpr.sum(),' Σ tickets à 0',T.zero.sum())
p('jours où manquants == RPR :',int((T.manq==T.rpr).sum()),' ; corrélation manquants/RPR',round(T.manq.corr(T.rpr),3),' manquants/notes',round(T.manq.corr(T.notes),3),' manquants/tickets à 0',round(T.manq.corr(T.zero),3))
rng=np.random.default_rng(20261123); cs=[]; eq=[]
for i in range(1000):
    pr=rng.permutation(T.rpr.values); cs.append(np.corrcoef(T.manq.values,pr)[0,1]); eq.append(int((T.manq.values==pr).sum()))
p('placebo (1000 permutations des jours) : corrélation moyenne',round(np.mean(cs),3),' max',round(np.max(cs),3),' égalités moyennes',round(np.mean(eq),1),' max',int(np.max(eq)))
# régression simple manquants ~ notes
b=np.polyfit(T.notes,T.manq,1); p('manquants ≈',round(b[0],4),'× notes +',round(b[1],3))
p(T.describe().to_string())
out.close()
