"""D-7 : journée du 9 septembre 2022. Combinaisons de 1 à 3 notes encaissées égales à chaque rafale de table vidée ;
attendu au hasard (densité des sommes de combinaisons dans ± 20 % du montant) ; décomposition des lignes DEL en prix de carte
(correspondance unique) et taux de TVA usuel ; événements E de 7 h à 11 h ; identifiant 51185 ; contrôle du 14 avril 2022 (C1 et B1).
Sortie : out/B1/D07.txt"""
import sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from B1_common import *
from itertools import combinations
C,E,F,H,A=load(); p=out('D07.txt')
B=pd.read_pickle('scripts/lot3-quantites/cache/B.pkl')
d='2022-09-09'
N=H[(H.date_ticket==d)&(H.serie==1)&(H.tc!=0)].sort_values('t'); Z=H[(H.date_ticket==d)&(H.tc==0)]
D=E[(E.dateEven==d)&(E.typEven=='DEL')]
raf=D.groupby('t').ac.sum()
vid={669:51153,688:51159,689:51160,690:51160,702:51167,718:51168,1132:51171,1216:51173,1217:51175}  # minute -> ticket à 0 € (11:29 rattachée à 11:30 par la société ; 18:52 -> n° 7 de 18:53)
combos=[]
v=list(zip(N.id,N.t,N.tc,N.no_ticket))
for k in (1,2,3):
    for c in combinations(v,k): combos.append((sum(x[2] for x in c),c))
sums=np.array([s for s,_ in combos])
p(f'Notes encaissées du jour : {len(N)} ; combinaisons de 1 à 3 notes : {len(combos)}')
for t,tid in vid.items():
    amt=raf[t]; hits=[c for s,c in combos if s==amt]
    lo,hi=int(amt*0.8),int(amt*1.2); dens=((sums>=lo)&(sums<=hi)).sum()/(hi-lo+1)
    lab=[]
    for c in hits:
        att=all(x[0]>tid and x[1]<=t for x in c); inv=all(x[1]>t for x in c)
        lab.append(('attestée' if att else ('inverse' if inv else 'mixte'),[f'n° {x[3]} ({x[2]/100:.2f} € ; {x[1]//60:02d}:{x[1]%60:02d} ; id {x[0]})' for x in c]))
    p(f'  rafale {t//60:02d}:{t%60:02d} ({amt/100:.2f} € ; ticket à 0 € id {tid}) : {len(hits)} combinaison(s) ; attendu au hasard {dens:.2f}')
    for l in lab: p('     ',l)
# 2. décomposition des lignes DEL en prix de la carte 2022-2023
C1=C[C.ex=='2022-2023'].copy(); C1['pc']=(C1.pu*100).round().astype(int)
pr=C1[C1.pc>0].groupby('pc').agg(libs=('libs',lambda s: sorted(set(s))),taux=('taux',lambda s: sorted(set(s))))
p('Lignes DEL du jour : montant ; article(s) de la carte 2022-2023 au même prix unitaire ; taux de TVA appliqués à ces articles dans C1')
nb_u=0; nb_m=0; nb_0=0
for t,g in D.groupby('t'):
    for ac in g.ac:
        if ac in pr.index:
            r=pr.loc[ac]; u=len(r.libs)==1; nb_u+=u; nb_m+=(not u)
            p(f'  {t//60:02d}:{t%60:02d} {ac/100:7.2f} € : {"UNIQUE " if u else ""}{r.libs[:5]}{" …" if len(r.libs)>5 else ""} ; taux {r.taux}')
        else:
            nb_0+=1; p(f'  {t//60:02d}:{t%60:02d} {ac/100:7.2f} € : aucun prix unitaire de la carte')
p(f'  correspondance unique {nb_u} ; plusieurs articles {nb_m} ; aucune {nb_0}')
# 3. événements E 7 h - 11 h
e=E[(E.dateEven==d)&(E.t<660)]; p('3. Événements E entre 0 h et 11 h :',e[['heureEven','typEven','id','amount']].values.tolist())
p('   ticket n° 1 à 0,00 € :',H[(H.date_ticket==d)&(H.no_ticket==1)&(H.tc==0)][['heure_ticket','id','no_z_report']].values.tolist(),' ; ids voisins :',H[H.id.between(51150,51154)][['id','date_ticket','heure_ticket','no_ticket','tot_ttc']].values.tolist())
# 4. identifiant 51185
p('4. Identifiant 51185 :',H[H.id==51185][['date_ticket','heure_ticket','no_ticket','tot_ttc']].values.tolist(),' ; F :',F[F.id==51185][['mod_regl','montant']].values.tolist())
p('   voisins :',H[H.id.between(51180,51190)].sort_values('id')[['id','date_ticket','heure_ticket','no_ticket','tot_ttc']].values.tolist())
# 5. 14 avril 2022
for n in (13,14):
    x=A[(A.date=='2022-04-14')&(A.no==n)].iloc[0]
    p(f'5. 14/04/2022 note n° {n} : C1 {C[C.id==x.id][["libs","qte","pu"]].values.tolist()} ; B1 {B[(B.date=="2022-04-14")&(B.ticket.astype(int)==n)][["lib","qte","pu"]].values.tolist()}')
Dd=E[(E.dateEven=='2022-04-14')&(E.typEven=='DEL')]; Zd=H[(H.date_ticket=='2022-04-14')&(H.tc==0)]
p(f'   DEL entre 12 h 26 et 13 h 34 : {int(Dd.t.between(746,814).sum())} ; tickets à 0 € : {int(Zd.t.between(746,814).sum())} ; voisins : DEL {sorted(set(Dd[Dd.t.between(700,860)].heureEven))} ; tickets à 0 € {sorted(Zd.heure_ticket)}')
