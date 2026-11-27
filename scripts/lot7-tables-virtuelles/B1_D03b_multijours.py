"""D-3 (6) : notes ouvertes un jour et closes un jour ultérieur. Critère : id inférieur au plus grand id des tickets clos
une journée antérieure (si id = ordre d'ouverture, la note existait avant la fin de cette journée). Jour d'ouverture estimé :
la dernière journée dont un ticket porte un id inférieur au sien. Contrôle par le préfixe de sy_uk (jour de session).
Sortie : out/B1/D03b.txt, D03b_multijours.csv"""
import sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from B1_common import *
C,E,F,H,A=load(); S=source(); S['id']=S.id.astype(int); p=out('D03b.txt')
Hd=H.sort_values(['date_ticket','id']).copy()
days=sorted(H.date_ticket.unique())
mx=H.groupby('date_ticket').id.max().reindex(days).cummax().shift(1)   # plus grand id clos avant la journée
Hd['maxprev']=Hd.date_ticket.map(mx)
mj=Hd[Hd.id<Hd.maxprev].copy()
# jour d'ouverture estimé : dernière journée d < date de clôture dont un ticket a un id < id (borne sup) ; et première journée dont le max id dépasse id
dmax=H.groupby('date_ticket').id.max().reindex(days)
def jour_ouv(i,dc):
    prev=[d for d in days if d<dc and dmax[d]>i]
    return prev[0] if prev else ''
mj['jour_ouv_est']=[jour_ouv(i,d) for i,d in zip(mj.id,mj.date_ticket)]
u=S.drop_duplicates('id').set_index('id')
mj['jour_prefixe_syuk']=mj.id.map(lambda i: (pd.Timestamp('2012-09-25')+pd.Timedelta(days=int(u.loc[i,'pre']))).strftime('%Y-%m-%d') if i in u.index else '')
mj['ex_ouv']=mj.jour_ouv_est.map(lambda d: ex_of(d) if d else ''); mj['ex_clo']=mj.date_ticket.map(ex_of)
mj['articles']=mj.id.map(lambda i: '; '.join(f'{l} x{q:g}' for l,q in C[C.id==i][['libs','qte']].values))
mj['regl']=mj.id.map(lambda i: '; '.join(f'{a} {b:.2f}' for a,b in F[F.id==i][['mod_regl','montant']].values))
mj['delai_j']=(pd.to_datetime(mj.date_ticket)-pd.to_datetime(mj.jour_ouv_est)).dt.days
p(f'Notes closes après une journée où un ticket d id supérieur était déjà clos : {len(mj)} ; non nulles {int((mj.tc!=0).sum())} pour {mj.tot_ttc.sum():.2f} € ; série 2 à 0 € {int((mj.tc==0).sum())} ; exercice d ouverture estimé ≠ exercice de clôture : {int((mj.ex_ouv!=mj.ex_clo).sum())}')
p('  délai (jours entre la journée d ouverture estimée et la clôture) :',mj.delai_j.value_counts().sort_index().to_dict())
p('  rang de clôture : ',mj.no_ticket.value_counts().sort_index().to_dict())
p(mj[['id','jour_ouv_est','jour_prefixe_syuk','date_ticket','heure_ticket','no_ticket','serie','tot_ttc','ex_ouv','ex_clo','regl','articles']].to_string())
mj.to_csv(OUT+'D03b_multijours.csv',index=False)
