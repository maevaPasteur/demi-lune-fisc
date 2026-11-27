"""D-3 (hypothèse d'identifiants consommés par d'autres objets) : position des identifiants manquants par rapport aux
redémarrages du logiciel, repérés par le préfixe de sy_uk (jour de session). Taux de manquants dans les intervalles
de changement de session contre l'intérieur des sessions ; premier id de journée. Sortie : out/B1/D03c.txt"""
import sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from B1_common import *
C,E,F,H,A=load(); S=source(); S['id']=S.id.astype(int); p=out('D03c.txt')
ids=set(H.id); lo,hi=min(ids),max(ids); miss=set(range(lo,hi+1))-ids
u=S.drop_duplicates('id').sort_values('id')[['id','pre']].reset_index(drop=True)
u['nid']=u.id.shift(-1); u['npre']=u.pre.shift(-1)
inner=u[(u.npre==u.pre)]; bound=u[(u.npre!=u.pre)&u.nid.notna()]
def rate(df):
    tot=0; m=0
    for a,b in zip(df.id,df.nid.astype(int)):
        rng_=range(a+1,b); tot+=len(rng_); m+=sum(1 for x in rng_ if x in miss)
    return m,tot
mi,ti=rate(inner); mb,tb=rate(bound)
p(f'Intervalles entre deux notes consécutives de l export : même session {len(inner)} ; changement de session {len(bound)}')
p(f'  ids intermédiaires (tickets H sans règlement ou manquants) : dans une session {ti}, dont manquants {mi} ({mi/ti*100:.1f} %) ; aux changements de session {tb}, dont manquants {mb} ({mb/tb*100:.1f} %)')
nb=[sum(1 for x in range(a+1,int(b)) if x in miss) for a,b in zip(bound.id,bound.nid)]
p('  manquants par changement de session :',pd.Series(nb).value_counts().sort_index().to_dict())
# première note du jour : l'id qui la précède manque-t-il ?
Hs=H.sort_values('id'); firsts=Hs.groupby('date_ticket').id.min()
p(f'  plus petit id de chaque journée : précédé d un id manquant {sum((i-1) in miss for i in firsts)} journées sur {len(firsts)}')
# manquants à cheval sur deux journées : coïncident-ils avec un changement de session ?
M=pd.read_csv(OUT+'D03_manquants.csv')
cross=M[~M.intra]; p(f'  manquants à cheval sur deux journées : {len(cross)} ; dont dans un intervalle de changement de session : {int(cross.session.isna().sum())}')
# événements E à la reprise : CON (connexion) du jour
con=E[E.typEven=='CON'].groupby('dateEven').size(); p(f'  CON par journée : {con.value_counts().sort_index().to_dict()} ; changements de préfixe {len(bound)} ; journées {H.date_ticket.nunique()}')
