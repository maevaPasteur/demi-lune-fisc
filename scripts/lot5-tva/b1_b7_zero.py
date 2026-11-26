"""B-7 (v) : détail des règlements portés sur des notes à 0,00 € (F), rapprochement avec H (série) et C."""
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
F=pd.read_pickle(C23+'F.pkl'); H=loadH(); CC=loadC()
AN={'2022-2023':977739.78,'2023-2024':1381110.20,'2024-2025':1819103.12}
H['serie']=np.where(H.tot_sum>=H.ex.map(AN)-1e-6,1,2)
fz=F[F.tot_ttc==0].copy()
fz=fz.merge(H[['id','serie','tot_sum','tot_tax_sum']].assign(id=H.id.astype(int)),on='id',how='left')
fz['lignesC']=fz.id.map(CC.groupby('id').size()); fz['ttcC']=fz.id.map(CC.groupby('id').tot.sum())
pd.set_option('display.width',250)
print(fz[['ex','dateTicket','heureTicket','no_ticket','no_zReport','id','mod_regl','montant','serie','tot_sum','lignesC','ttcC']].to_string())
print(fz.groupby(['ex','mod_regl']).montant.agg(['size','sum']).round(2).to_string())
# notes payées le même jour dans la 1re série au même montant ?
