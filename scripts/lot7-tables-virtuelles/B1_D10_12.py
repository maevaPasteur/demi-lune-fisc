"""D-10 (tickets sans article sans DEL à leur minute), D-11 (passage entre populations), D-12 (test 1..n sur la première série seule ;
test 1..m sur la seconde série ; trois tickets à 0 € « sans ticket encaissé de même date et même n° »). Sortie : out/B1/D10_12.txt"""
import sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from B1_common import *
C,E,F,H,A=load(); p=out('D10_12.txt')
D=E[E.typEven=='DEL']; dk=set(zip(D.dateEven,D.t))
Z=H[~H.dansC].copy(); Z['atmin']=[(d,t) in dk for d,t in zip(Z.date_ticket,Z.t)]
W=Z[~Z.atmin].copy()
p(f'D-10. Tickets sans article sans DEL à leur minute : {len(W)} (par exercice {W.groupby("ex").size().to_dict()})')
DZ={z:g.t.values for z,g in D.groupby('no_zEport')}
def delta(z,t):
    v=DZ.get(z)
    if v is None or len(v)==0: return np.nan,np.nan
    b=v[v<t]; a=v[v>t]
    return (t-b.max() if len(b) else np.nan),(a.min()-t if len(a) else np.nan)
W[['avant','apres']]=[delta(z,t) for z,t in zip(W.no_z_report,W.t)]
W['proche']=W[['avant','apres']].min(axis=1)
def cl(x): return 'aucun DEL ce jour' if pd.isna(x) else ('1 à 5 min' if x<=5 else ('6 à 30 min' if x<=30 else 'plus de 30 min'))
p('   DEL le plus proche du même Z :',W.proche.map(cl).value_counts().to_dict())
p('   dont DEL à 1 minute exactement (avant / après) :',int((W.avant==1).sum()),'/',int((W.apres==1).sum()))
ot=E[E.typEven!='DEL']; ok=set(zip(ot.dateEven,ot.t))
p('   autre événement E à la même minute :',int(sum((d,t) in ok for d,t in zip(W.date_ticket,W.t))),' ; types :',ot[[ (d,t) in set(zip(W.date_ticket,W.t)) for d,t in zip(ot.dateEven,ot.t)]].typEven.value_counts().to_dict())
N=H[(H.serie==1)&(H.tc!=0)]; fl=N.groupby('date_ticket').t.agg(['min','max'])
W['pos']=[('avant la première note' if t<fl.loc[d,'min'] else ('après la dernière note' if t>fl.loc[d,'max'] else 'pendant le service')) if d in fl.index else 'jour sans note' for d,t in zip(W.date_ticket,W.t)]
p('   position dans la journée :',W.pos.value_counts().to_dict(),' ; avant 10 h :',int((W.t<600).sum()))
Dm=D.groupby(['dateEven','t']).ac.sum().reset_index(); hk=set(zip(H.date_ticket,H.t))
Dm['orph']=[(d,t) not in hk for d,t in zip(Dm.dateEven,Dm.t)]
p(f'   DEL de minutes sans aucun ticket H clos (ni table vidée ni note) : {int(Dm.orph.sum())} minutes, {Dm[Dm.orph].ac.sum()/100:.2f} € (hors lignes ≥ 1 000 € : {Dm[Dm.orph&(Dm.ac<100000)].ac.sum()/100:.2f} €, dont les minutes contenant une ligne ≥ 1 000 € sont exclues en entier)')
p('   « Articles déplacés » : le journal E ne connaît que les types',sorted(E.typEven.unique()),' ; aucun fichier remis ne porte un type d événement de transfert. Les annexes C ne portent ni lien de transfert ni heure de ligne.')
# D-11
p('\nD-11. Passages entre populations')
tv=tv2359(); p(f'   lot 2.2 version C : {len(tv)} tables, {tv.V.sum()/100:.2f} € ; minutes distinctes {tv[["d","t"]].drop_duplicates().shape[0]}')
Zm=Z[Z.atmin]; p(f'   pièce 92 : {len(Zm)} tickets sur {Zm[["date_ticket","t"]].drop_duplicates().shape[0]} minutes ; montant des DEL de ces minutes {Dm[[ (d,t) in set(zip(Zm.date_ticket,Zm.t)) for d,t in zip(Dm.dateEven,Dm.t)]].ac.sum()/100:.2f} € (dont 2 minutes portant une ligne ≥ 1 000 € : 68 993,10 € le 26/07/2022 18:51 ; les autres lignes ≥ 1 000 € ne tombent pas sur une minute de ticket à 0 €)')
# D-12
p('\nD-12. Tests de numérotation')
s2=set(H[H.serie==2].id); a1=A[~A.id.isin(s2)]
ok=0; bad=[]
for d,g in a1.groupby('date'):
    n=g.no.values; m=len(n)
    if n.min()==1 and n.max()==m and len(set(n))==m and n.sum()==m*(m+1)//2: ok+=1
    else: bad.append(d)
p(f'   (a) première série seule (16 607 notes, 17 tickets de seconde série retirés) : journées « suite 1..n » {ok} sur {a1.date.nunique()} ; autres : {bad[:10]}')
z2=H[H.serie==2]; ok2=0; holes=[]
for d,g in z2.groupby('date_ticket'):
    n=sorted(g.no_ticket.values); m=len(n)
    if n==list(range(1,m+1)): ok2+=1
    else: holes.append((d,sorted(set(range(1,max(n)+1))-set(n)),[x for x in n if n.count(x)>1]))
p(f'   (b) seconde série (tickets à 0 € et 17 non nuls) : journées avec au moins un ticket {z2.date_ticket.nunique()} ; « suite 1..m » {ok2} ; autres {len(holes)}')
for h in holes[:40]: p('      ',h)
zz=H[H.tc==0]; enc=set(zip(H[H.tc!=0].date_ticket,H[H.tc!=0].no_ticket))
un=zz[[ (d,n) not in enc for d,n in zip(zz.date_ticket,zz.no_ticket)]]
p('   (c) tickets à 0,00 € sans ticket encaissé de même date et même n° :',un[['date_ticket','heure_ticket','no_ticket','id','serie','dansC']].values.tolist())
for _,r in un.iterrows():
    p('      ',r.date_ticket,': rangs encaissés du jour',sorted(H[(H.date_ticket==r.date_ticket)&(H.tc!=0)].no_ticket)[-3:],' ; rangs à 0 € du jour',sorted(zz[zz.date_ticket==r.date_ticket].no_ticket))
