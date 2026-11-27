"""D-8 : conversions au forfait et TVA. (1) Prix et taux appliqués (annexe C, colonne 16) des articles « forfait » ;
(2) pour les 133 suites de la pièce 157-R4 : taux légal identifiable de chaque ligne DEL (prix unitaire de la carte de l'exercice
dont tous les articles ont le même taux légal, classification A-2.5-2 du lot 2.5), TVA théorique du détail contre TVA de la note forfait.
Sorties : out/B1/D08.txt, D08_conversions.csv"""
import sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from B1_common import *
import openpyxl
C,E,F,H,A=load(); p=out('D08.txt')
Lg=pd.read_pickle('scripts/lot5-tva/cache/B3_articles.pkl'); leg=dict(zip(Lg.ref.astype(str),pd.to_numeric(Lg.taux_legal,errors='coerce')))
C['ref']=C.ref.astype(str); C['tl']=C.ref.map(leg); C['pc']=(C.pu*100).round().astype(int)
FORF=["Menu 'Demi Lune'",'Menu du jour','Plat du jour','Formule Express','FORMULE EXPRESS','Formule à 11','Formule à 12.5','Formule à 14']
p('1. Prix unitaires et taux appliqués (annexe C) des articles forfait, par exercice')
for l in FORF:
    x=C[C.libs==l]
    if not len(x): continue
    for ex,g in x.groupby('ex'):
        top=g.groupby(['pu','taux']).qte.sum().sort_values(ascending=False).head(4)
        p(f'   {l} {ex} : lignes {len(g)} ; PU distincts {g.pu.nunique()} (min {g.pu.min():.2f}, max {g.pu.max():.2f}) ; taux appliqués {g.groupby("taux").size().to_dict()} ; taux légal (A-2.5-2) {sorted(set(g.tl.dropna()))} ; principaux (PU, taux) : {[(a,b,round(c,1)) for (a,b),c in top.items()]}')
# carte : prix -> ensemble des taux légaux
rate={ex:g[g.pc>0].groupby('pc').tl.apply(lambda s: set(s.dropna())) for ex,g in C.groupby('ex')}
wb=openpyxl.load_workbook('scripts/lot7-tables-virtuelles/cache/entrees/lot27/157-R4-conversions-au-forfait-133-suites.xlsx',data_only=True,read_only=True)
def sheet(n):
    rows=list(wb[n].iter_rows(values_only=True)); return pd.DataFrame(rows[1:],columns=rows[0])
Su=sheet('Suites').dropna(subset=['Note rapprochée (id)']); Su=Su[pd.to_numeric(Su['Suite n°'],errors='coerce').notna()]
DL=sheet('DEL_lignes'); DL=DL[pd.to_numeric(DL['Suite n°'],errors='coerce').notna()]
p(f'2. Pièce 157-R4 : suites {len(Su)} ; lignes DEL {len(DL)}')
rows=[]
for _,s in Su.iterrows():
    n=int(s['Suite n°']); ex=s['Exercice'] if isinstance(s['Exercice'],str) else ex_of(str(s['Date'])[:10])
    ex=ex_of(str(s['Date'])[:10])
    dl=DL[DL['Suite n°']==n]
    tva_lo=tva_hi=0.0; ident=0; ttc_id=0.0; n20=0
    for m in dl['Montant']:
        ac=int(round(m*100)); rs=rate[ex].get(ac,set())
        if len(rs)==1:
            r=list(rs)[0]; ident+=1; ttc_id+=m; v=m*r/(100+r); tva_lo+=v; tva_hi+=v; n20+=(r==20)
        else:
            tva_lo+=m*10/110; tva_hi+=m*20/120
    nid=int(s['Note rapprochée (id)']); nl=C[C.id==nid]
    tva_note=(nl.tot_lig*nl.taux/(100+nl.taux)).sum()
    rows.append(dict(suite=n,date=str(s['Date'])[:10],minute=s['Minute'],ex=ex,note=nid,montant=float(s['Montant supprimé']),total_note=float(s['Total de la note']),
        lignes=len(dl),lignes_taux_identifiable=ident,lignes_20=n20,ttc_identifiable=round(ttc_id,2),tva_detail_basse=round(tva_lo,2),tva_detail_haute=round(tva_hi,2),
        tva_note=round(tva_note,2),taux_note='/'.join(map(str,sorted(set(nl.taux)))),articles_note='; '.join(f'{a} x{q:g} à {u:.2f} ({t:g} %)' for a,q,u,t in nl[['libs','qte','pu','taux']].values)))
R=pd.DataFrame(rows); R.to_csv(OUT+'D08_conversions.csv',index=False)
for ex,g in R.groupby('ex'):
    p(f'   {ex} : conversions {len(g)} ; montant {g.montant.sum():.2f} € ; lignes {g.lignes.sum()} dont taux légal identifiable {g.lignes_taux_identifiable.sum()} ({g.lignes_taux_identifiable.sum()/g.lignes.sum()*100:.1f} %) ; TVA du détail [{g.tva_detail_basse.sum():.2f} ; {g.tva_detail_haute.sum():.2f}] € contre TVA des notes forfait {g.tva_note.sum():.2f} € ; écart [{g.tva_detail_basse.sum()-g.tva_note.sum():.2f} ; {g.tva_detail_haute.sum()-g.tva_note.sum():.2f}] €')
p(f'   total : TVA du détail [{R.tva_detail_basse.sum():.2f} ; {R.tva_detail_haute.sum():.2f}] € ; TVA des notes {R.tva_note.sum():.2f} € ; écart [{R.tva_detail_basse.sum()-R.tva_note.sum():.2f} ; {R.tva_detail_haute.sum()-R.tva_note.sum():.2f}] €')
p(f'   conversions comportant au moins une ligne DEL dont le prix ne correspond qu à des articles à 20 % et dont la note est entièrement à 10 % : {int(((R.lignes_20>0)&(R.taux_note=="10.0")).sum())} ; lignes concernées {int(R[(R.taux_note=="10.0")].lignes_20.sum())}')
p(f'   taux des notes forfait : {R.taux_note.value_counts().to_dict()}')
# montant des lignes identifiées à 20 % dans des conversions dont la note est entièrement à 10 %
tot=0.0; n=0
for _,s in Su.iterrows():
    nn=int(s['Suite n°']); ex=ex_of(str(s['Date'])[:10])
    nl=C[C.id==int(s['Note rapprochée (id)'])]
    if set(nl.taux)!={10.0}: continue
    for m in DL[DL['Suite n°']==nn]['Montant']:
        rs=rate[ex].get(int(round(m*100)),set())
        if rs=={20.0}: tot+=m; n+=1
p(f'   lignes identifiées à 20 % remplacées par un forfait à 10 % : {n} lignes, {tot:.2f} € TTC ; TVA en moins sur ces lignes {tot*(20/120-10/110):.2f} €')
# TVA payée en trop : notes forfait à 20 %
x=R[R.taux_note=='20.0']; p(f'   notes forfait entièrement à 20 % : {len(x)} ; montant {x.total_note.sum():.2f} € ; TVA en plus par rapport à 10 % : {x.total_note.sum()*(20/120-10/110):.2f} €')
