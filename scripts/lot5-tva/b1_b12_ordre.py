"""B-12 : clé de tri des fichiers G et H ; tickets au-delà de la dernière ligne."""
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
G=loadG(); H=loadH(); F=pd.read_pickle(C23+'F.pkl')
AN={'2022-2023':977739.78,'2023-2024':1381110.20,'2024-2025':1819103.12}
H['serie']=np.where(H.tot_sum>=H.ex.map(AN)-1e-6,1,2)
H1=H[H.serie==1]
m=G.drop_duplicates('tk').merge(H1[['ex','date_ticket','no_ticket','heure_ticket','id']],left_on=['ex','dateTicket','noTicket','heureTicket'],right_on=['ex','date_ticket','no_ticket','heure_ticket'])
for ex in EX:
    z=m[m.ex==ex]; d=np.diff(z.id.values)
    print(f'G {ex}: tickets {len(z)} ; id H croissant d\'un ticket au suivant : {(d>0).mean()*100:.3f} % ; ruptures {int((d<0).sum())}')
    h=H[H.ex==ex]; dh=np.diff(h.id.values.astype(float)); print(f'   H {ex}: lignes {len(h)} ; id croissant {(dh>0).mean()*100:.3f} % ; ruptures {int((dh<0).sum())} ; ordre (date, id) reproduit : {(h.sort_values(["date_ticket","id"],kind="mergesort").index.values==h.index.values).all()}')
    print(f'   G ordre (date, id H) reproduit : {(z.sort_values(["dateTicket","id"],kind="mergesort").index.values==z.index.values).all()}')
    # premier jour : exemple
    if ex=='2022-2023': print('   1er jour G :',z[z.dateTicket==z.dateTicket.min()][['noTicket','heureTicket','id','tot_sum']].head(14).values.tolist())
    last=G[G.ex==ex].iloc[-1]; aft=z[z.tot_sum>last.tot_sum]
    print('   tickets au compteur > dernière ligne :',aft[['dateTicket','heureTicket','noTicket','no_zReport','tot_ttc','tot_tva','id']].values.tolist())
