"""B0 point 3 : tickets sans article clôturés à la minute d'un DEL du même Z ; 37 tickets porteurs de règlements.
Sortie : out/s03_zero_del.txt, out/s03_zero.csv"""
import pandas as pd, numpy as np
O='scripts/lot7-tables-virtuelles/out/'
H=pd.read_pickle(O+'B0cache/H2.pkl'); E=pd.read_pickle(O+'B0cache/E.pkl'); F=pd.read_pickle(O+'B0cache/F.pkl')
out=open(O+'B0_s03_zero_del.txt','w')
def p(*a): print(*a); print(*a,file=out)
def tm(h): a,b=h.split(':'); return int(a)*60+int(b)
E['t']=E.heureEven.map(tm); H['t']=H.heure_ticket.map(tm)
D=E[E.typEven=='DEL']
Z=H[~H.dansC].copy()
keys=set(zip(D.no_zEport,D.t)); keysd=set(zip(D.dateEven,D.t))
Z['m0']=[ (z,t) in keys for z,t in zip(Z.no_z_report,Z.t)]
Z['m0_date']=[ (d,t) in keysd for d,t in zip(Z.date_ticket,Z.t)]
Z['m1']=[ any((z,t+k) in keys for k in (-1,0,1)) for z,t in zip(Z.no_z_report,Z.t)]
Z['m1p']=[ any((z,t+k) in keys for k in (-1,0)) for z,t in zip(Z.no_z_report,Z.t)]
p('Tickets sans article :',len(Z))
p('  clôturés à la minute d\'un DEL du même Z :',Z.m0.groupby(Z.ex).sum().to_dict(),' total',Z.m0.sum(),f'({Z.m0.mean()*100:.1f} %)')
p('  même critère sur la date au lieu du Z :',Z.m0_date.sum())
p('  à la minute ou une minute avant (DEL t-1 ou t) :',Z.m1p.sum(),' ; à +/- 1 minute :',Z.m1.sum())
p('  Z des tickets sans article tous présents dans E ? ',Z.no_z_report.isin(E.no_zEport).all())
# règlements
Fs=F.groupby('id').montant.sum()
Z['regl']=Z.id.map(Fs).fillna(0)
R=Z[Z.regl.abs()>0.004]
p('Tickets sans article portant des règlements :',len(R),' montant',round(R.regl.sum(),2),' par exercice',R.groupby('ex').regl.agg(['size','sum']).round(2).to_dict())
p('  dont clôturés à la minute d\'un DEL du même Z :',R.m0.sum(),' ; à +/-1 min :',R.m1.sum())
p(R[['date_ticket','heure_ticket','no_ticket','id','no_z_report','regl','m0','m1']].to_string())
# tables vidées au sens du lot 2.2 (155-R3 version C : 2 359 tables) : cache lot26 si disponible
try:
    tv=pd.read_pickle('scripts/lot6-evenement-reglement/cache/b5_tables_videes.pkl'); p('cache lot26 b5_tables_videes :',type(tv), getattr(tv,'shape',None)); 
    if hasattr(tv,'columns'): p(list(tv.columns)[:30])
except Exception as e: p('cache tables vidées :',e)
# zéros avec article (2) + tous les zéros H : règlements
Hz=H[np.isclose(H.tot_ttc,0)].copy(); Hz['regl']=Hz.id.map(Fs).fillna(0)
p('Tous tickets H à 0,00 € portant règlements :',(Hz.regl.abs()>0.004).sum(),round(Hz.regl.sum(),2))
Z.to_csv(O+'B0_s03_zero.csv',index=False)
out.close()
