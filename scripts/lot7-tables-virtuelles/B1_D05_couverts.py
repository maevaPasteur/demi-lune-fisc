"""D-5 : couverts, définitions, variantes. Classification « plat / menu » reconstituée (B0_s09) : la pièce
« 10-rf-teme-classification.xlsx » citée par le service (réponse p. 36, « 10-rf-teme-claccification.xlex » à l'OCR) n'est pas dans le dossier.
Catégories attribuées par le libellé et le prix (inférence). Sorties : out/B1/D05.txt, D05_categories.csv, D05_tableau74.csv"""
import sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from B1_common import *
C,E,F,H,A=load(); P=plats(); p=out('D05.txt')
S92=pd.read_pickle(Q+'S92.pkl'); P11=pd.read_pickle(Q+'P11.pkl'); P12=pd.read_pickle(Q+'P12.pkl'); J93=pd.read_pickle(Q+'J93.pkl')
# 1. réconciliation
p('1. Totaux de couverts')
p(f'   pièce 11 (par note, 16 607 notes, valeurs exactes) : {P11.cv.sum():.2f} ; pièce 12 (par journée) : {P12.tot.sum():.2f}')
mm=P12.melt(id_vars=['date'],value_vars=['midi','soir'],var_name='service',value_name='cv')
p(f'   pièce 92 : somme des couverts par service arrondis (arrondi au pair) : {S92.cv.sum()} ; arrondi au pair de chaque service de la pièce 12 : {int(mm.cv.round().sum())}')
p(f'   pièce 93 : somme de la colonne « Couverts » par journée : {J93.Couverts.sum()} ; arrondi au pair de chaque journée de la pièce 12 : {int(P12.tot.round().sum())} ; arrondi demi supérieur par journée : {int(np.floor(P12.tot+0.5).sum())}')
nF=F.groupby('id').montant.sum(); Fnz=F[F.tot_ttc!=0]
p(f'   additions : Id distincts de C {A.id.nunique()} ; couples (date, n°) de C {A.drop_duplicates(["date","no"]).shape[0]} ; notes de la pièce 11 {len(P11)} (= notes de première série portant au moins une ligne C : {len(A[~A.id.isin(H[H.serie==2].id)])})')
p(f'   candidats pour 16 608 (pièce 13, « Notes (règlements) ») : Id distincts de F {F.id.nunique()} ; Id de F de total non nul {Fnz.id.nunique()} ; couples (date, n°) de F {F.drop_duplicates(["dateTicket","no_ticket"]).shape[0]} ; couples (date, n°) de F de total non nul {Fnz.drop_duplicates(["dateTicket","no_ticket"]).shape[0]}')
# 2. catégories
MENU={"Menu 'Demi Lune'","Menu 'Galette'",'Menu Bourguignon','Menu Franc-Comtois','Menu Végétarien','Menu du Dahu','Menu du jour','Formule Express','FORMULE EXPRESS','Formule à 11','Formule à 12.5','Formule à 14','Plat du jour'}
ENF={"Menu 'Enfant'",'Menu Bambin'}
FON={'Fondue Forestière','Fondue Jurassienne','Fondue des Gourmets','FONDUE VIN JAUNE'}
SAL={'Salade Régionale','Salade Végétarienne','Salade Franc-Comptoi'}
GAL={'Galette nature','GALETTE FORESTIERE','Complète','BARBEULENET','CABRICHOU','CANCOINE','DADOULET','DAHU','ECRESSI','FOULETOT','FRELEE','LIGOUSE','LOURNETTE','NIOLERIES','NOIRAUD','PAYSANNE','PEUTE','TANTELIN','VERDELET'}
def cat(l):
    for n,s in [('menu ou formule',MENU),('menu enfant',ENF),('fondue',FON),('salade',SAL),('galette (inférence)',GAL)]:
        if l in s: return n
    return 'plat'
cats=pd.DataFrame({'lib':sorted(P)}); cats['categorie']=cats.lib.map(cat)
st=C[C.libs.isin(P)].groupby('libs').agg(lignes=('qte','size'),quantite=('qte','sum'),pu_median=('pu','median'),notes=('id','nunique'))
cats=cats.merge(st,left_on='lib',right_index=True); cats['qte_moy_par_note']=(cats.quantite/cats.notes).round(2)
cats.to_csv(OUT+'D05_categories.csv',index=False)
p('2. Catégories (quantités totales, quantité moyenne par note qui porte l article) :'); p(cats.groupby('categorie').agg(libelles=('lib','size'),quantite=('quantite','sum'),notes=('notes','sum')).round(1).to_string())
# base par note
s2=set(H[H.serie==2].id)
X=C[C.libs.isin(P)&~C.id.isin(s2)].copy(); X['cat']=X.libs.map(cat)
Q_=X.pivot_table(index='id',columns='cat',values='qte',aggfunc='sum',fill_value=0)
a=A[~A.id.isin(s2)].set_index('id'); Q_=Q_.reindex(a.index,fill_value=0)
a['v0']=Q_.sum(axis=1)
a['v2']=Q_.sum(axis=1)-C[C.libs.isin({'Salade Franc-Comptoi','Saucisse de Morteau','Steak haché'})&~C.id.isin(s2)].groupby('id').qte.sum().reindex(a.index).fillna(0)
a['v2b']=a.v2-C[(C.libs=='Galette nature')&~C.id.isin(s2)].groupby('id').qte.sum().reindex(a.index).fillna(0)
a['v3']=Q_.max(axis=1)
a['mois']=a.date.str[5:7].astype(int); a['jour']=a.date.str[8:10].astype(int)
def occ(col,midi=(0,18*60),soir=18*60,terr=lambda m,j: m in (5,6,7,8),zero=False,lab=''):
    b=a.copy()
    b['svc']=np.where((b.t>=midi[0])&(b.t<midi[1]),'midi',np.where(b.t>=soir,'soir','hors'))
    s=b[b.svc!='hors'].groupby(['date','svc']).agg(cv=(col,'sum'),mois=('mois','first'),jour=('jour','first'),n=(col,'size')).reset_index()
    if zero:
        allx=pd.MultiIndex.from_product([sorted(a.date.unique()),['midi','soir']],names=['date','svc']).to_frame(index=False)
        s=allx.merge(s,on=['date','svc'],how='left'); s['cv']=s.cv.fillna(0); s['mois']=s.date.str[5:7].astype(int); s['jour']=s.date.str[8:10].astype(int)
    s['pl']=[48 if terr(m,j) else 46 for m,j in zip(s.mois,s.jour)]
    s['o']=s.cv/s.pl*100
    hors=b[b.svc=='hors'][col].sum()
    p(f'   {lab} : services {len(s)} ; couverts {s.cv.sum():.0f} (hors service {hors:.0f}) ; moyenne {s.cv.mean():.1f} ; occupation {s.o.mean():.1f} % ; > 100 % : {int((s.o>100).sum())} ; maximum {s.o.max():.0f} %')
    return s
p('3. Variantes (17 tickets de seconde série exclus ; pourcentages non arrondis)')
s0=occ('v0',lab='V0 société (midi < 18 h, soir ≥ 18 h)')
s1=occ('v0',midi=(11*60,14*60+30),lab='V1 midi limité aux notes closes de 11 h à 14 h 30 (14 h 30 à 18 h et avant 11 h hors service)')
occ('v2',lab='V2 sans entrée ni accompagnement (Salade franc-comtoise, Saucisse de Morteau, Steak haché)')
occ('v2b',lab='V2 bis V2 et sans « Galette nature »')
occ('v3',lab='V3 couverts d une note plafonnés au maximum des catégories (proxy « personnes », borne basse)')
occ('v3',midi=(11*60,14*60+30),lab='V1 + V3')
s4=occ('v0',zero=True,lab='V4 demi-journées sans aucune note réintégrées à 0 %')
occ('v0',terr=lambda m,j: m in (5,6,7,8) or (m==9 and j<=15),lab='V5 première quinzaine de septembre en terrasse')
# activité des demi-journées sans note
z=s4[s4.n.isna()]; Dl=E[E.typEven=='DEL']; Hz=H[H.tc==0]
act=[(d,sv,int(((Dl.dateEven==d)&((Dl.t<1080) if sv=='midi' else (Dl.t>=1080))).sum()),int(((Hz.date_ticket==d)&((Hz.t<1080) if sv=='midi' else (Hz.t>=1080))).sum())) for d,sv in zip(z.date,z.svc)]
act=pd.DataFrame(act,columns=['date','svc','DEL','tickets0'])
p(f'   demi-journées sans note : {len(z)} (soirs {int((z.svc=="soir").sum())}, midis {int((z.svc=="midi").sum())}) ; avec au moins un DEL {int((act.DEL>0).sum())} ; avec un ticket à 0,00 € {int((act.tickets0>0).sum())} ; jours de semaine {pd.to_datetime(z.date).dt.day_name().value_counts().to_dict()}')
# 4. douze services du tableau 74
T=S92.sort_values(['occ','cv'],ascending=False).head(12)
rows=[]
for _,r in T.iterrows():
    b=a[(a.date==r.date)&((a.t<1080) if r.service=='midi' else (a.t>=1080))]
    rows.append(dict(date=r.date,service=r.service,couverts=r.cv,occ=r.occ,notes=len(b),premiere=min(b.heure),derniere=max(b.heure),
        notes_14h30_18h=int(((b.t>=870)&(b.t<1080)).sum()),notes_avant_11h=int((b.t<660).sum()),plus_grosse_note=b.v0.max(),
        couverts_V1=b[(b.t>=660)&(b.t<870)].v0.sum() if r.service=='midi' else b.v0.sum(),couverts_V3=b.v3.sum()))
T74=pd.DataFrame(rows); T74.to_csv(OUT+'D05_tableau74.csv',index=False); p('4. Douze services du tableau 74 :'); p(T74.to_string())
# 5. janvier et février
d=pd.Series(sorted(A.date.unique())); m=d.str[5:7]
p(f'5. Journées d ouverture en janvier {int((m=="01").sum())} ({", ".join(d[m=="01"])}) ; en février {int((m=="02").sum())} ({", ".join(d[m=="02"])})')
p('   jours de semaine des 659 journées :',pd.to_datetime(d).dt.day_name().value_counts().to_dict())
