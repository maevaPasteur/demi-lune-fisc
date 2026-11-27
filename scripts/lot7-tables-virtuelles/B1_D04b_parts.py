"""D-4 (complément) : règlements à parts égales des 37 tickets ; autres règlements du même jour, même mode, même montant de part, à ± 30 min.
Sortie : out/B1/D04b.txt"""
import sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from B1_common import *
C,E,F,H,A=load(); p=out('D04b.txt')
F['t']=F.heureTicket.map(tm); F['mc']=(F.montant*100).round().astype(int)
R=pd.read_csv(OUT+'D04_37.csv')
for _,r in R.iterrows():
    fl=F[F.id==r.id]; t=tm(r.heure)
    for m_,mc in fl[['mod_regl','mc']].drop_duplicates().values:
        o=F[(F.dateTicket==r.date)&(F.id!=r.id)&(F.mc==mc)&((F.t-t).abs()<=30)]
        if len(o): p(f'{r.date} {r.heure} id {r.id} : règlement {m_} {mc/100:.2f} € ; contenu {r.contenu:.2f} € ; autres lignes de même montant à ± 30 min :',o[['heureTicket','no_ticket','id','mod_regl','montant','tot_ttc']].values.tolist())
# hasard : mêmes lignes transportées aux jours d'ouverture suivants (même heure)
days=sorted(H.date_ticket.unique()); di={d:i for i,d in enumerate(days)}
obs=0; exp=[]; amt=0
for _,r in R.iterrows():
    fl=F[F.id==r.id]; t=tm(r.heure)
    for m_,mc in fl[['mod_regl','mc']].values:
        o=F[(F.dateTicket==r.date)&(F.id!=r.id)&(F.mc==mc)&(F.mod_regl==m_)&((F.t-t).abs()<=30)]
        if len(o): obs+=1; amt+=mc/100
        e=[]
        for k in (1,2,3,5,8):
            if di[r.date]+k<len(days):
                d2=days[di[r.date]+k]; e.append(int(len(F[(F.dateTicket==d2)&(F.mc==mc)&(F.mod_regl==m_)&((F.t-t).abs()<=30)])>0))
        exp.append(np.mean(e))
p(f'Lignes de règlement des 37 tickets ayant une ligne de même mode et même montant sur une autre note à ± 30 min : {obs} sur {len(exp)} ({amt:.2f} €) ; attendu au hasard (transport aux jours d ouverture suivants) : {sum(exp):.2f}')
