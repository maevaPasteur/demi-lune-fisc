"""Pièces n° 158, 159 et 160 : classeurs sourcés et recalculables (formules visibles pour tout calcul).
Lit la pièce n° 77 régénérée par r3_pieces_a.py (onglet « Tables »)."""
import os, sys, re, itertools, openpyxl; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
from collections import defaultdict
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter as L
N158='158-R2-quantites-fractionnaires-note-d-origine-annexe-B-et-concordance-C-H-G-F.xlsx'
N159='159-R2-partages-non-aboutis-63-cas-note-d-origine-et-montant-maximal.xlsx'
N160='160-R2-quantites-fractionnaires-test-placebo-600-tirages.xlsx'
N77='77-R3-quantites-fractionnaires-recomposition-5062-articles-866-tables.xlsx'
B=Font(bold=True)
def sheet(wb,name,header,rows,widths=None):
    ws=wb.create_sheet(name); ws.append(header)
    for c in ws[1]: c.font=B; c.alignment=Alignment(wrap_text=True,vertical='top')
    for r in rows: ws.append(list(r))
    ws.freeze_panes='A2'
    for j,h in enumerate(header,1): ws.column_dimensions[L(j)].width=(widths or {}).get(j,max(10,min(40,len(str(h))+2)))
    return ws
def method(wb,lines,name='Méthode'):
    ws=wb.create_sheet(name)
    for i,t in enumerate(lines,1):
        c=ws.cell(i,1,t); c.alignment=Alignment(wrap_text=True,vertical='top'); c.font=Font(bold=bool(t) and not t.endswith('.') and len(t)<70)
    ws.column_dimensions['A'].width=140
def synth(ws,rows,start=1):
    for i,r in enumerate(rows,start):
        for j,v in enumerate(r,1):
            c=ws.cell(i,j,v)
            if j==1 and isinstance(v,str) and (v.isupper() or v.startswith('Indicateur')): c.font=B
    ws.column_dimensions['A'].width=95
    for col in 'BCDEFG': ws.column_dimensions[col].width=18
hm=lambda t: f"{int(t)//60:02d}:{int(t)%60:02d}"
Cr,F,E,Fid,tabs,nd,A=load()
CC=pd.read_pickle(C+'CC.pkl'); H=pd.read_pickle(C+'H.pkl'); G=pd.read_pickle(C+'G.pkl'); H['id']=pd.to_numeric(H.id,errors='coerce')
Cn=CC.drop_duplicates('id').set_index('id')
# =====================================================================  158
wb=openpyxl.Workbook(); wb.remove(wb.active); wb.create_sheet('Synthèse')
O=pd.read_pickle(C+'cloture_note_W60.pkl')
note2tab={i:k for k,(ex,d,ids) in enumerate(tabs) if len(ids)>=2 for i in ids}
grp_of={r.id:set([r.id,*r.S]) for r in O[O.found].itertuples()}
q=defaultdict(float)
for r in Cr.itertuples(): q[(r.id,r.libn,r.pu100)]+=r.qteC
dayart=defaultdict(set)
for r in Cr.itertuples(): dayart[(r.date,r.libn,r.pu100)].add(r.id)
Lb=Cr[Cr.inB & ((Cr.qte-Cr.qteC).abs()>1e-6)].sort_values(['ex','date','ticket','rowC'])
R1=[]; nday=0
for r in Lb.itertuples():
    g=grp_of.get(r.id) or (set(tabs[note2tab[r.id]][2]) if r.id in note2tab else None)
    src='groupe à 60 min au plus' if r.id in grp_of else 'table (annexe n° 77)'
    s=sum(q.get((i,r.libn,r.pu100),0) for i in g if i!=r.id) if g else None
    if g is None or abs(r.qteC+s-r.qte)>=0.011:
        oth=[i for i in dayart[(r.date,r.libn,r.pu100)] if i!=r.id]; found=None
        for k in (1,2,3):
            for comb in itertools.combinations(oth,k):
                if abs(r.qteC+sum(q[(i,r.libn,r.pu100)] for i in comb)-r.qte)<0.011: found=comb; break
            if found: break
        if found: g=set(found)|{r.id}; s=sum(q[(i,r.libn,r.pu100)] for i in found); src='journée (partenaire identifié)'; nday+=1
    R1.append((r.ex,r.date,int(r.ticket),int(r.id),r.lib_s,float(r.pu),float(r.qte),float(r.qteC),round(float(s),4) if s is not None else None,
               ' ; '.join(map(str,sorted(g))) if g else '',src,(int(r.id==min([r.id]+[i for i in g if q.get((i,r.libn,r.pu100),0)>0])) if g else 0),float(r.tot),round(float(r.B),2)))
ws=sheet(wb,'Lignes B ≠ C (7 146)',['Exercice','Date','N° note','Id note','Article','PU (€)','Qté annexe B','Qté annexe C (même note)','Σ Qté annexe C, autres notes du groupe','Notes du groupe (id)','Rattachement','Note = plus petit id des notes portant l\'article dans le groupe (1/0)','Total TTC (identique B et C) (€)','Col. B du service « écart » (€)','Contrôle : Qté B = Qté C + Σ autres (1/0)'],
         [x+(f'=IF(ABS(G{i}-(H{i}+I{i}))<0.011,1,0)',) for i,x in enumerate(R1,2)],{5:24,10:30,11:26})
n1=len(R1)+1
neg=pd.read_pickle(C+'B02_neg.pkl').sort_values(['ex','date','ticket','rowB'])
lab={'a':"(a) note d'origine, article refermé (Qté B = entier cible)",'b':"(b) note d'origine, autre quantité entière (deux partages réunis ou scindés)",'r':"(r) note d'origine, article non refermé (8 tables)",
     'c1':'(c1) contrepartie en montant à 30 min au plus, même table','c2':'(c2) contrepartie en montant à 30 min au plus, autre note','d':'(d) contrepartie en montant sur la journée','e':'(e) aucune contrepartie','m':'(m) remise (Qté B = Qté C)'}
R2=[(r.ex,r.date,int(r.ticket),int(r.id),r.lib_s,float(r.pu),float(r.qte),float(r.qteC),float(r.tot),round(float(r.B),2),lab[r.cat]) for r in neg.itertuples()]
sheet(wb,'Écarts négatifs (7 149)',['Exercice','Date','N° note','Id note','Article','PU (€)','Qté annexe B','Qté annexe C','Total TTC (€)','Col. B du service « écart » (€)','Contrepartie réglée'],R2,{5:24,11:60})
n2=len(R2)+1
# concordance
fr=sorted(set(Cr[Cr.fracC].id))
Hc=H.groupby('id').size(); Hi=H.dropna(subset=['id']).drop_duplicates('id').set_index('id'); Fm=F.groupby('id').montant.sum(); Fn=F.groupby('id').size()
Gk=G.groupby(['dateTicket','noTicket','heureTicket','no_zReport']).agg(ttc=('tot_ttc','first'),tva=('tot_tva','first'),n=('tot_ttc','size'))
R3=[]
for i in fr:
    c=Cn.loc[i]; key=(c.date,int(c.ticket),c.heure,int(c.z)); g=Gk.loc[key] if key in Gk.index else None; h=Hi.loc[i]
    R3.append((int(i),c.ex,c.date,int(c.ticket),c.heure,int(c.z),float(c.tot_ttc),float(h.tot_ttc),float(g.ttc),round(float(Fm[i]),2),float(c.tot_tva),float(h.tot_tva),float(g.tva),int(Hc[i]),int(Fn[i]),int(g.n)))
sheet(wb,'Concordance 1 913 notes',['Id note','Exercice','Date','N° note','Heure','Z','TTC annexe C (€)','TTC annexe H (€)','TTC annexe G (€)','Σ règlements annexe F (€)','TVA annexe C (€)','TVA annexe H (€)','TVA annexe G (€)','Occurrences de l\'id dans H','Lignes de règlement F','Lignes du ticket dans G (une par taux)','Contrôle TTC C = H = G = F (1/0)','Contrôle TVA C = H = G (1/0)','Contrôle id unique dans H (1/0)'],
      [x+(f'=IF(AND(ABS(G{i}-H{i})<0.005,ABS(G{i}-I{i})<0.005,ABS(G{i}-J{i})<0.005),1,0)',f'=IF(AND(ABS(K{i}-L{i})<0.005,ABS(K{i}-M{i})<0.005),1,0)',f'=IF(N{i}=1,1,0)') for i,x in enumerate(R3,2)])
n3=len(R3)+1
# tables
negn=set(Cr[Cr.B< -0.005].id)
X=Cr.merge(CC[['rowC','ex','tva']],on=['rowC','ex'],how='left')
_w=openpyxl.load_workbook(P+N77,read_only=True)
rowmap={(r[1],frozenset(int(x) for x in re.findall(r'\d+',r[3]))):i for i,r in enumerate(_w['Tables'].iter_rows(min_row=2,values_only=True),2)}
R4=[]
for k,(ex,d,ids) in enumerate(tabs):
    if len(ids)<2: continue
    ids=sorted(ids); o=ids[0]; oth=ids[1:]; x=X[X.id.isin(ids)]
    neg_ids=[i for i in ids if i in negn]
    g=x.groupby(['libn','pu100','tva']).qteC.sum()
    theo=sum(round(p/100*qq*t/(100+t),2) for (l,p,t),qq in g.items()); split=sum(round(t_*tt/(100+t_),2) for t_,tt in zip(x.tva,x.tot))
    R4.append((rowmap[(d,frozenset(int(Cn.loc[i].ticket) for i in ids))],ex,d,' + '.join(f'n° {int(Cn.loc[i].ticket)}' for i in sorted(ids,key=lambda i:Fid.t[i])),' ; '.join(map(str,ids)),len(ids),o,int(Cn.loc[o].ticket),
               Cn.loc[ids].z.nunique(),Cn.loc[ids].date.nunique(),int(Fid.t[o]),int(max(Fid.t[i] for i in oth)),int(len(neg_ids)==1),int(len(neg_ids)==1 and neg_ids[0]==o),
               round(float(sum(Fm[i] for i in ids)),2),round(float((x.pu*x.qteC).sum()),2),round(split,2),round(theo,2)))
R4.sort(key=lambda x:x[0])
hdr=['Ligne de l\'onglet « Tables » de l\'annexe n° 77','Exercice','Date','Notes (ordre de règlement)','Id des notes','Nb notes','Id note d\'origine (plus petit id)','N° note d\'origine','Nb de Z distincts','Nb de dates distinctes',
     'Règlement note d\'origine (minutes depuis 0 h)','Dernier règlement des autres notes (minutes)','Une seule note porte des écarts négatifs dans B (1/0)','Cette note est la note d\'origine (1/0)',
     'Σ règlements annexe F (€)','Prix de carte Σ PU × Qté C (€)','TVA des parts, ligne à ligne (€)','TVA d\'une note unique théorique (€)',
     'Note d\'origine réglée la dernière ou à la même minute (min)','Écart règlements − prix de carte (€)','Écart TVA parts − note unique (€)']
sheet(wb,'Tables (866)',hdr,[x+(f'=K{i}-L{i}',f'=O{i}-P{i}',f'=Q{i}-R{i}') for i,x in enumerate(R4,2)],{4:30,5:30})
n4=len(R4)+1
# conservation
A2=A.copy(); A2['pu100']=(A2.pu*100).round().astype(int); A2['libn']=A2.lib.map(norm)
lines=defaultdict(list)
for i_,r in zip(Cr.index,Cr.itertuples()): lines[(r.id,r.libn,r.pu100)].append(i_)
R5=[]
for r in A2[A2.ref].itertuples():
    LL=[i_ for k in r.ids for i_ in lines.get((k,r.libn,r.pu100),[])]
    cl=[i_ for i_ in LL if Cr.at[i_,'B']< -0.005 and abs(Cr.at[i_,'qte']-round(Cr.at[i_,'qte']))<1e-9 and abs(Cr.at[i_,'qte']-round(r.somme))<0.011]
    if not cl: continue
    c0=cl[0]
    R5.append((r.ex,r.date,' ; '.join(map(str,sorted(r.ids))),r.lib,float(r.pu),round(float(sum(Cr.at[i_,'qteC'] for i_ in LL)),4),float(Cr.at[c0,'qte']),int(Cr.at[c0,'id']),
               round(float(sum(Cr.at[i_,'tot'] for i_ in LL)),2)))
sheet(wb,'Conservation (4 949 articles)',['Exercice','Date','Notes de la table (id)','Article','PU (€)','Σ des parts (Qté annexe C, toutes notes)','Qté annexe B de la note d\'origine','Id note d\'origine','Σ encaissé sur les parts (annexe C) (€)','Écart de quantité (B − Σ parts)','PU × Qté B (€)','Écart en euros (PU × Qté B − encaissé)'],
      [x+(f'=G{i}-F{i}',f'=E{i}*G{i}',f'=K{i}-I{i}') for i,x in enumerate(R5,2)],{3:30,4:24})
n5=len(R5)+1
# Z
zd=CC.groupby('z').datz.first(); sets={'C':set(CC.z.astype(int)),'E':set(E.no_zEport.dropna().astype(int)),'F':set(F.no_zReport.astype(int)),'G':set(G.no_zReport.astype(int)),'H':set(H.no_z_report.dropna().astype(int))}
zs=sorted(sets['C'])
R6=[(z,zd[z])+tuple(int(z in sets[k]) for k in 'CEFGH') for z in zs]
sheet(wb,'Z (659)',['N° Z','Date','Présent annexe C','Présent annexe E','Présent annexe F','Présent annexe G','Présent annexe H','Suite du Z précédent (1/0)','Présent dans les 5 annexes (1/0)'],
      [x+(('' if i==2 else f'=IF(A{i}=A{i-1}+1,1,0)'),f'=IF(SUM(C{i}:G{i})=5,1,0)') for i,x in enumerate(R6,2)])
n6=len(R6)+1
# DEL par minute (c1_C1g, même graine)
rng=np.random.default_rng(20261123)
frac=set(Cr[Cr.fracC].id); Ed={d:g for d,g in E.groupby('dateEven')}
Nd={d:g.sort_values('t') for d,g in Cr[Cr.id.isin(Fid.index)&~Cr.id.isin(frac)].drop_duplicates('id').groupby('date')}
def ndel(d,t0,t1):
    g=Ed.get(d); return 0 if g is None else int(((g.t>=t0)&(g.t<=t1)&(g.typEven=='DEL')).sum())
R7=[]
for ex,d,ids in tabs:
    if len(ids)<2 or len([i for i in ids if i in negn])!=1: continue
    ts=sorted(Fid.t[i] for i in ids); k=len(ids)
    row=['table',ex,d,k,hm(ts[0]),hm(ts[-1]),ts[-1]-ts[0]+1,ndel(d,ts[0],ts[-1])]; R7.append(row)
    nd_=Nd.get(d)
    if nd_ is None: continue
    st=[j for j in range(len(nd_)-k+1) if abs(nd_.t.iloc[j]-ts[0])<=60]
    if not st: continue
    j=st[rng.integers(len(st))]; tt=nd_.t.iloc[j:j+k].tolist()
    R7.append(['témoin',ex,d,k,hm(tt[0]),hm(tt[-1]),tt[-1]-tt[0]+1,ndel(d,tt[0],tt[-1])])
sheet(wb,'Suppressions par minute',['Échantillon','Exercice','Date','Nb notes','Premier règlement','Dernier règlement','Durée (min, bornes incluses)','Événements DEL dans l\'intervalle'],R7)
n7=len(R7)+1
s=wb['Synthèse']; LB="'Lignes B ≠ C (7 146)'"; EN="'Écarts négatifs (7 149)'"; CO="'Concordance 1 913 notes'"; TB="'Tables (866)'"; CS="'Conservation (4 949 articles)'"; ZZ="'Z (659)'"; SM="'Suppressions par minute'"
exs=['2022-2023','2023-2024','2024-2025']
def per(f): return [f(e) for e in exs]
rows=[["NOTE D'ORIGINE DANS L'ANNEXE B ET CONCORDANCE DES NOTES À FRACTION DANS LES ANNEXES C, H, G ET F (formules sur les onglets de la présente pièce)"],[],
 ['Indicateur']+exs+['3 exercices'],
 ['1. Lignes communes B / C dont la quantité diffère']+per(lambda e:f'=COUNTIF({LB}!$A$2:$A${n1},"{e}")')+[f'=COUNTA({LB}!$A$2:$A${n1})'],
 ['   dont Qté B = Qté C de la note + Σ des parts des autres notes du groupe (contrôle = 1)']+per(lambda e:f'=COUNTIFS({LB}!$A$2:$A${n1},"{e}",{LB}!$O$2:$O${n1},1)')+[f'=SUM({LB}!$O$2:$O${n1})'],
 ['   dont la note porte le plus petit identifiant des notes du groupe qui portent l\'article']+per(lambda e:f'=COUNTIFS({LB}!$A$2:$A${n1},"{e}",{LB}!$L$2:$L${n1},1)')+[f'=SUM({LB}!$L$2:$L${n1})'],
 ['   dont rattachement sur la journée (partenaire identifié)']+per(lambda e:f'=COUNTIFS({LB}!$A$2:$A${n1},"{e}",{LB}!$K$2:$K${n1},"journée (partenaire identifié)")')+[f'=COUNTIF({LB}!$K$2:$K${n1},"journée (partenaire identifié)")'],
 ['2. Lignes de l\'annexe B à écart négatif']+per(lambda e:f'=COUNTIF({EN}!$A$2:$A${n2},"{e}")')+[f'=COUNTA({EN}!$A$2:$A${n2})'],
 ['   dont sans contrepartie réglée (catégorie e)']+per(lambda e:f'=COUNTIFS({EN}!$A$2:$A${n2},"{e}",{EN}!$K$2:$K${n2},"{lab["e"]}")')+[f'=COUNTIF({EN}!$K$2:$K${n2},"{lab["e"]}")'],
 ['   dont remises (catégorie m), nombre']+per(lambda e:f'=COUNTIFS({EN}!$A$2:$A${n2},"{e}",{EN}!$K$2:$K${n2},"{lab["m"]}")')+[f'=COUNTIF({EN}!$K$2:$K${n2},"{lab["m"]}")'],
 ['   remises, montant (€)']+per(lambda e:f'=-SUMIFS({EN}!$J$2:$J${n2},{EN}!$A$2:$A${n2},"{e}",{EN}!$K$2:$K${n2},"{lab["m"]}")')+[f'=-SUMIF({EN}!$K$2:$K${n2},"{lab["m"]}",{EN}!$J$2:$J${n2})'],
 ['   parts déjà réglées par les autres notes (hors remises), montant (€)']+per(lambda e:f'=-SUMIF({EN}!$A$2:$A${n2},"{e}",{EN}!$J$2:$J${n2})+SUMIFS({EN}!$J$2:$J${n2},{EN}!$A$2:$A${n2},"{e}",{EN}!$K$2:$K${n2},"{lab["m"]}")')+[f'=-SUM({EN}!$J$2:$J${n2})+SUMIF({EN}!$K$2:$K${n2},"{lab["m"]}",{EN}!$J$2:$J${n2})'],
 ['   pied de page de l\'annexe B porté par le service (€) (constantes : annexes B-1 à B-3)',-17561.00,-20011.12,-20115.28,'=SUM(B13:D13)'],
 ['   arrondis nets : pied du service + parts + remises (€)']+[f'={c}13+{c}12+{c}11' for c in 'BCDE'],
 ['3. Notes à quantité fractionnaire']+per(lambda e:f'=COUNTIF({CO}!$B$2:$B${n3},"{e}")')+[f'=COUNTA({CO}!$A$2:$A${n3})'],
 ['   TTC identique dans C, H, G et Σ F']+per(lambda e:f'=COUNTIFS({CO}!$B$2:$B${n3},"{e}",{CO}!$Q$2:$Q${n3},1)')+[f'=SUM({CO}!$Q$2:$Q${n3})'],
 ['   TVA identique dans C, H et G']+per(lambda e:f'=COUNTIFS({CO}!$B$2:$B${n3},"{e}",{CO}!$R$2:$R${n3},1)')+[f'=SUM({CO}!$R$2:$R${n3})'],
 ['   identifiant présent une seule fois dans H']+per(lambda e:f'=COUNTIFS({CO}!$B$2:$B${n3},"{e}",{CO}!$S$2:$S${n3},1)')+[f'=SUM({CO}!$S$2:$S${n3})'],
 ['4. Tables partagées (annexe n° 77)']+per(lambda e:f'=COUNTIF({TB}!$B$2:$B${n4},"{e}")')+[f'=COUNTA({TB}!$A$2:$A${n4})'],
 ['   tables sur un seul Z']+per(lambda e:f'=COUNTIFS({TB}!$B$2:$B${n4},"{e}",{TB}!$I$2:$I${n4},1)')+[f'=COUNTIF({TB}!$I$2:$I${n4},1)'],
 ['   tables sur une seule date']+per(lambda e:f'=COUNTIFS({TB}!$B$2:$B${n4},"{e}",{TB}!$J$2:$J${n4},1)')+[f'=COUNTIF({TB}!$J$2:$J${n4},1)'],
 ['   tables dont une seule note porte des écarts négatifs dans B']+per(lambda e:f'=COUNTIFS({TB}!$B$2:$B${n4},"{e}",{TB}!$M$2:$M${n4},1)')+[f'=SUM({TB}!$M$2:$M${n4})'],
 ['   dont cette note est la note d\'origine (plus petit identifiant)']+per(lambda e:f'=COUNTIFS({TB}!$B$2:$B${n4},"{e}",{TB}!$N$2:$N${n4},1)')+[f'=SUM({TB}!$N$2:$N${n4})'],
 ['   dont la note d\'origine est réglée la dernière ou à la même minute']+per(lambda e:f'=COUNTIFS({TB}!$B$2:$B${n4},"{e}",{TB}!$M$2:$M${n4},1,{TB}!$S$2:$S${n4},">=0")')+[f'=COUNTIFS({TB}!$M$2:$M${n4},1,{TB}!$S$2:$S${n4},">=0")'],
 ['   écart règlements − prix de carte, somme (€)']+per(lambda e:f'=SUMIF({TB}!$B$2:$B${n4},"{e}",{TB}!$T$2:$T${n4})')+[f'=SUM({TB}!$T$2:$T${n4})'],
 ['   écart règlements − prix de carte, plus grand écart d\'une table, en valeur absolue (€)','','','',f'=MAX(MAX({TB}!$T$2:$T${n4}),-MIN({TB}!$T$2:$T${n4}))'],
 ['   écart TVA des parts − TVA d\'une note unique, somme (€)']+per(lambda e:f'=SUMIF({TB}!$B$2:$B${n4},"{e}",{TB}!$U$2:$U${n4})')+[f'=SUM({TB}!$U$2:$U${n4})'],
 ['   écart TVA, plus grand écart d\'une table, en valeur absolue (€)','','','',f'=MAX(MAX({TB}!$U$2:$U${n4}),-MIN({TB}!$U$2:$U${n4}))'],
 ['5. Articles refermés dont la note d\'origine porte la quantité entière exacte']+per(lambda e:f'=COUNTIF({CS}!$A$2:$A${n5},"{e}")')+[f'=COUNTA({CS}!$A$2:$A${n5})'],
 ['   Σ des parts (quantités annexe C)']+per(lambda e:f'=SUMIF({CS}!$A$2:$A${n5},"{e}",{CS}!$F$2:$F${n5})')+[f'=SUM({CS}!$F$2:$F${n5})'],
 ['   Σ des quantités de la note d\'origine (annexe B)']+per(lambda e:f'=SUMIF({CS}!$A$2:$A${n5},"{e}",{CS}!$G$2:$G${n5})')+[f'=SUM({CS}!$G$2:$G${n5})'],
 ['6. Z de l\'annexe C (premier : 2938, 14/04/2022 ; dernier : 3596, 30/03/2025)','','','',f'=COUNTA({ZZ}!$A$2:$A${n6})'],
 ['   Z qui suivent immédiatement le précédent (sans trou)','','','',f'=SUM({ZZ}!$H$3:$H${n6})'],
 ['   Z présents dans les cinq annexes C, E, F, G et H','','','',f'=SUM({ZZ}!$I$2:$I${n6})'],
 ['7. Suppressions « DEL » par minute pendant les partages (835 tables)','','','',f'=SUMIF({SM}!$A$2:$A${n7},"table",{SM}!$H$2:$H${n7})/SUMIF({SM}!$A$2:$A${n7},"table",{SM}!$G$2:$G${n7})'],
 ['   témoin : notes non fractionnaires consécutives du même jour, même nombre de notes','','','',f'=SUMIF({SM}!$A$2:$A${n7},"témoin",{SM}!$H$2:$H${n7})/SUMIF({SM}!$A$2:$A${n7},"témoin",{SM}!$G$2:$G${n7})'],
]
synth(s,rows)
s['E36'].number_format='0.000'; s['E37'].number_format='0.000'
method(wb,['Objet',
 "Établir sur les fichiers du service (1) que la note d'origine d'une table partagée conserve dans l'annexe B la quantité commandée pour toute la table, (2) que les 1 913 notes à quantité fractionnaire concordent au centime dans les annexes C, H, G et F, TVA comprise, (3) que les notes d'une table appartiennent au même Z et à la même date et que la séquence des Z est continue.",'',
 'Sources primaires',
 "Annexes B-1 à B-3 (extraction du 13/02/2026, prix de vente / quantité ; annexes n° 24 à 26), C-1 à C-3 (détail des tickets ; n° 17 à 19), E-1 à E-3 (événements ; n° 14 à 16), F-1 à F-3 (règlements ; n° 20 à 22), G-1 à G-3 (journal de TVA ; n° 33 à 35), H-1 à H-3 (liste des tickets ; n° 30 à 32). Les tables sont celles de l'annexe n° 77 (même ordre).",'',
 "Rattachement des annexes B et C",
 "L'annexe B n'a pas d'identifiant. Chaque ligne B est rattachée à la ligne C de même date, même n° de note, même article et même montant TTC (97 694 lignes communes, montant identique ligne à ligne ; les 75 lignes propres à l'annexe C sont celles des 17 notes de la seconde série du compteur de l'annexe H, sans règlement).",'',
 "Onglet « Lignes B ≠ C (7 146) »",
 "Lignes communes dont la quantité B diffère de la quantité C. Le groupe de la note est d'abord la table de l'annexe n° 77 ou le groupe des notes partenaires à 60 minutes au plus portant le même article ; à défaut (11 lignes), le ou les partenaires du même jour dont les quantités complètent exactement la ligne. Contrôle par formule (colonne O) : Qté B = Qté C de la note + Σ des Qté C du même article sur les autres notes du groupe. La colonne L vérifie que la note qui porte la quantité de la table est la plus petite du groupe (note d'origine).",'',
 "Onglet « Écarts négatifs (7 149) »",
 "Toutes les lignes de l'annexe B dont l'écart calculé par le service (col. B) est négatif, avec leur contrepartie réglée : parts du même article sur les autres notes de la table (a, b, r), contrepartie en montant sur une autre note à 30 minutes au plus ou sur la journée (c1, c2, d), remise (m). Le pied de page du service totalise ces écarts ; la « Synthèse » le décompose (lignes 11 à 14).",'',
 "Onglet « Concordance 1 913 notes »",
 "Pour chaque note à quantité fractionnaire : TTC et TVA dans les annexes C et H (par identifiant), G (par date, n°, heure et Z, l'annexe G n'ayant pas d'identifiant) et Σ des règlements F (par identifiant). Contrôles par formule (colonnes Q à S).",'',
 "Onglet « Tables (866) »",
 "Une ligne par table de l'annexe n° 77 : note d'origine (plus petit identifiant), Z et dates, heure de règlement de la note d'origine et des autres notes (minutes depuis minuit, annexe F), note portant les écarts négatifs dans B, règlements comparés au prix de carte (Σ PU × Qté C), TVA ligne à ligne des parts comparée à la TVA d'une note unique (PU × Σ Qté × t / (100 + t), arrondie à l'article).",'',
 "Onglet « Conservation (4 949 articles) »",
 "Articles refermés dont la note d'origine porte, dans l'annexe B, la quantité entière exacte : Σ des parts (annexe C) comparée à la quantité de la note d'origine (annexe B), en quantité et en euros.",'',
 "Onglet « Z (659) »","Présence de chaque Z dans les cinq annexes et continuité de la séquence.",'',
 "Onglet « Suppressions par minute »",
 "Événements DEL entre le premier et le dernier règlement des 835 tables dont une seule note porte des écarts négatifs, comparés à un témoin apparié : même jour, autant de notes non fractionnaires consécutives, première note à 60 minutes au plus de la première note de la table (tirage au hasard, graine 20261123).",'',
 'Reproductibilité',"Script : scripts/r3_pieces_b.py (reprend c1_C1.py, c1_C1g.py et m1_B02.py). Toutes les valeurs de la « Synthèse » sont des formules sur les onglets de la présente pièce."])
wb.save(P+N158); print('158 :',n1-1,n2-1,n3-1,n4-1,n5-1,n6-1,n7-1,'journée',nday)
# =====================================================================  159
wb=openpyxl.Workbook(); wb.remove(wb.active); wb.create_sheet('Synthèse')
c2=pd.read_csv(OUT+'C2_cas.csv'); b1=pd.read_csv(OUT+'Bc1_cas.csv'); assert (c2.date.values==b1.date.values).all()
R=[]
for a,b in zip(c2.itertuples(),b1.itertuples()):
    R.append(('note isolée' if a.type=='note isolée' else "table à articles non refermés",a.ex,a.date,str(a.ref),str(a.ids),a.heure_notes,b.mode,b.DEL_de,b.DEL_a,int(b.decal_min),int(b.decal_max),int(a.n_del),float(a.somme),
              int(a.ticket0>0),int(a.ticket0_id_inf>0),a.ticket0_info if isinstance(a.ticket0_info,str) else '',int(bool(a.memeZ)),int(a.Z_DEL) if a.Z_DEL==a.Z_DEL else '',str(a.Z_notes),int(a.temoin_t0>0),int(a.placebo_t0>0),
              int(b.R1),int(b.R2),int(b.T1),int(b.T2),int(b.Z),int(b.J_jour)))
hdr=['Type','Exercice','Date','N° de note(s)','Id note(s) payée(s)','Heure(s) de règlement','Mode','Premier DEL apparié','Dernier DEL apparié','Décalage min (min, DEL − règlement)','Décalage max (min)','Nb DEL appariés','Montant supprimé (€)',
     'Ticket à 0 € trouvé dans H (1/0)','dont id inférieur à la note payée (1/0)','Ticket à 0 € (id, n°, heure, Z)','Même Z que les notes (1/0)','Z des DEL','Z des notes','Témoin : ticket à 0 € trouvé (1/0)','Placebo J + 7 : ticket à 0 € trouvé (1/0)',
     'Règlement : mêmes articles ressaisis (R1)','Règlement : même total ressaisi (R2)','Règlement : même total sur une note réglée (T1)','Règlement : somme de notes (T2)','Règlement : parmi les 37 règlements sans note (Z)','Coïncidence de total sur la journée, antérieure au DEL (J)',
     'Règlement retrouvé (R1 à Z) (1/0)']
sheet(wb,'Cas (63)',hdr,[x+(f'=IF(SUM(V{i}:Z{i})>0,1,0)',) for i,x in enumerate(R,2)],{5:30,16:34})
nc=len(R)+1
t1=pd.read_csv(OUT+'Bc1_temoin.csv')
sheet(wb,'Témoin règlement (63)',['Type du cas apparié','Exercice','Catégorie','R1','R2','T1','T2','Z','J (journée)','Règlement retrouvé (R1 à Z) (1/0)'],
      [('note isolée' if r.type=='note isolée' else 'table à articles non refermés',r.ex,r.cat,int(r.R1),int(r.R2),int(r.T1),int(r.T2),int(r.Z),int(r.J_jour),f'=IF(SUM(D{i}:H{i})>0,1,0)') for i,r in enumerate(t1.itertuples(),2)])
n4_=pd.read_csv(OUT+'B04_notes.csv')
pairs={('2024-04-04',2),('2024-04-04',3),('2022-08-27',6),('2022-08-27',20),('2025-01-04',25),('2025-01-04',27)}
def cls(r):
    if (r.date,r.ticket) in pairs: return 'paire de notes jumelles, toutes deux réglées, à plus de 15 min'
    if (r.date,r.ticket)==('2022-10-23',17): return 'miroir partiel : la ligne fractionnaire a son DEL'
    if (r.date,r.ticket) in {('2023-04-12',14),('2024-08-01',6)}: return 'aucune contrepartie retrouvée (reliquat)'
    k,n=map(int,r.DEL_miroir.split('/')); assert k==n==r.lignes,(r.date,r.ticket); return 'moitié dont le miroir identique est supprimé'
def dec(s):
    m=re.findall(r'-?\d+',str(s)); return f'{m[0]} à {m[1]} min' if len(m)>=2 else ''
R=[(r.ex,r.date,int(r.ticket),int(r.id),r.heure,float(r.totF),r.mode,int(r.lignes),int(r.lignes_frac),float(r.enc_frac),r.DEL_miroir,dec(r.DEL_decalage),int(r.contrepartie_jour),r.ecart_min_contrepartie if r.ecart_min_contrepartie==r.ecart_min_contrepartie else '',cls(r)) for r in n4_.itertuples()]
sheet(wb,'Notes isolées (64)',['Exercice','Date','N° note','Id note','Heure de règlement','Total réglé annexe F (€)','Mode','Lignes','Lignes fractionnaires','Montant des lignes fractionnaires (€)','Lignes à DEL miroir (±0,02 €, [t − 5 ; t + 30] min)','Décalage des DEL (min)','Notes du jour portant les mêmes articles','Écart à la note jumelle (min)','Classement'],R,{15:55})
ni=len(R)+1
c5=pd.read_csv(OUT+'C5_brut.csv')  # valeurs non arrondies (scripts/r3_C5_brut.py) ; affichage à 2 décimales
lab5={5:'5 minutes',10:'10 minutes',15:'15 minutes (règle retenue)',20:'20 minutes',30:'30 minutes',60:'60 minutes'}
R=[(lab5.get(int(r.fenetre),'Journée') if str(r.fenetre).isdigit() else 'Journée',r['2022-2023 TTC'],r['2022-2023 HT'],r['2023-2024 TTC'],r['2023-2024 HT'],r['2024-2025 TTC'],r['2024-2025 HT'],r.miroir,r.miroir_partiel,r.sans_trace,r.residu_DEL,r.residu_sans_DEL) for _,r in c5.iterrows()]
ws=sheet(wb,'Montant par fenêtre',['Fenêtre de regroupement','2022-2023 TTC (€)','2022-2023 HT (€)','2023-2024 TTC (€)','2023-2024 HT (€)','2024-2025 TTC (€)','2024-2025 HT (€)','Notes à moitié supprimée (miroir) (€)','Miroir partiel (€)','Notes sans trace (€)','Parts supprimées des tables (DEL appariés) (€)','Articles des tables sans DEL (€)','Total TTC (€)','Total HT (€)','Contrôle : composition = total TTC (1/0)'],
         [x+(f'=B{i}+D{i}+F{i}',f'=C{i}+E{i}+G{i}',f'=IF(ABS(SUM(H{i}:L{i})-M{i})<0.005,1,0)') for i,x in enumerate(R,2)],{1:28})
nf=len(R)+1; ws.cell(nf+1,1,'Maximum, toutes fenêtres').font=B; ws.cell(nf+1,13,f'=MAX(M2:M{nf})'); ws.cell(nf+1,14,f'=MAX(N2:N{nf})')
for row in ws.iter_rows(min_row=2,max_row=nf+1,min_col=2,max_col=14):
    for c in row: c.number_format='#,##0.00'
rel=[('12/04/2023 n° 14 (id 54082) : complément des parts égales, sans contrepartie',23.40,20.86),('01/08/2024 n° 6 (id 63749) : idem',35.65,32.03),
     ('23/10/2022 n° 17 : lignes entières non miroir (Menu Franc-Comtois 34,00 ; Camembert rôti 18,60 ; Jus de fruit 3,90) ; la ligne fractionnaire (Pichet Savagnin 0,5, 14,00 €) a son DEL',0.00,0.00),
     ('3 articles des tables sans DEL : Camembert rôti 9,30 et Expresso 1,10 (14/05/2023) ; Croûtes Morilles 8,45 (01/07/2023) ; TVA 10 %',18.85,17.14)]
ws=sheet(wb,'Reliquat sans trace',['Élément','TTC (€)','HT (€)'],rel,{1:110}); ws.append(['Total du reliquat',f'=SUM(B2:B5)',f'=SUM(C2:C5)']); ws['A6'].font=B
s=wb['Synthèse']; CA="'Cas (63)'"; TM="'Témoin règlement (63)'"; NI="'Notes isolées (64)'"; MF="'Montant par fenêtre'"; RL="'Reliquat sans trace'"
rows=[['PARTAGES NON ABOUTIS : 63 CAS (55 NOTES ISOLÉES ET 8 TABLES), TRACE DE CHAQUE ANNULATION ET MONTANT MAXIMAL (formules sur les onglets de la présente pièce)'],[],
 ['Indicateur']+exs+['3 exercices'],
 ['Notes isolées dont la moitié identique est supprimée']+per(lambda e:f'=COUNTIFS({CA}!$B$2:$B${nc},"{e}",{CA}!$A$2:$A${nc},"note isolée")')+[f'=COUNTIF({CA}!$A$2:$A${nc},"note isolée")'],
 ['Tables à parts supprimées']+per(lambda e:f'=COUNTIFS({CA}!$B$2:$B${nc},"{e}",{CA}!$A$2:$A${nc},"table à articles non refermés")')+[f'=COUNTIF({CA}!$A$2:$A${nc},"table à articles non refermés")'],
 ['Cas']+[f'={c}4+{c}5' for c in 'BCDE'],
 ['Montant supprimé (€ TTC)']+per(lambda e:f'=SUMIF({CA}!$B$2:$B${nc},"{e}",{CA}!$M$2:$M${nc})')+[f'=SUM({CA}!$M$2:$M${nc})'],
 ['Ticket à 0 € trouvé dans H dans [1er DEL − 2 ; dernier DEL + 2] min']+per(lambda e:f'=COUNTIFS({CA}!$B$2:$B${nc},"{e}",{CA}!$N$2:$N${nc},1)')+[f'=SUM({CA}!$N$2:$N${nc})'],
 ['   dont identifiant inférieur à celui de la note payée']+per(lambda e:f'=COUNTIFS({CA}!$B$2:$B${nc},"{e}",{CA}!$O$2:$O${nc},1)')+[f'=SUM({CA}!$O$2:$O${nc})'],
 ['   témoin : notes prises au hasard le même jour','','','',f'=SUM({CA}!$T$2:$T${nc})'],
 ['   placebo : même test une semaine plus tard (J + 7)','','','',f'=SUM({CA}!$U$2:$U${nc})'],
 ['Suppressions dans le même Z que les notes']+per(lambda e:f'=COUNTIFS({CA}!$B$2:$B${nc},"{e}",{CA}!$Q$2:$Q${nc},1)')+[f'=SUM({CA}!$Q$2:$Q${nc})'],
 ['Notes isolées à miroir identique ligne à ligne (onglet « Notes isolées (64) »)','','','',f'=COUNTIF({NI}!$O$2:$O${ni},"moitié dont le miroir identique est supprimé")'],
 ['Notes isolées dont les DEL tombent de 0 à 2 min après le règlement','','','',f'=COUNTIFS({CA}!$A$2:$A${nc},"note isolée",{CA}!$J$2:$J${nc},">=0",{CA}!$K$2:$K${nc},"<=2")'],
 ['Règlement de la part supprimée retrouvé (R1, R2, T1, T2, Z)','','','',f'=SUM({CA}!$AB$2:$AB${nc})'],
 ['   témoin (63 notes prises au hasard), même tests','','','',f'=SUM({TM}!$J$2:$J${nc})'],
 ['Tables partagées abouties (annexe n° 77, constantes)',294,300,272,'=SUM(B17:D17)'],
 ['Part des partages : cas / (tables abouties + cas)']+[f'={c}6/({c}17+{c}6)' for c in 'BCDE'],
 ['Notes (annexes C, par identifiant ; constante)','','','',16624],
 ['Part des notes','','','','=E6/E19'],
 ["Journées d'ouverture (constante)",'','','',659],
 ['Cas par journée','','','','=E6/E21'],
 [],
 ['MONTANT MAXIMAL (onglet « Montant par fenêtre »)'],
 ['Maximum toutes fenêtres, TTC (€)','','','',f'={MF}!M{nf+1}'],
 ['Maximum toutes fenêtres, HT (€)','','','',f'={MF}!N{nf+1}'],
 ['Reliquat sans trace, TTC (€) (2 notes et 3 articles)','','','',f'={RL}!B6'],
 ['Reliquat sans trace, HT (€)','','','',f'={RL}!C6'],
 ['Chiffre d\'affaires HT de caisse, 3 exercices (€) (constante : annexes C, TVA ligne à ligne)','','','',1132726.75],
 ['Maximum HT / chiffre d\'affaires HT','','','','=E26/E29'],
 ['Bases HT rehaussées par le service (€) (constante : proposition, 172 813 + 124 010 + 125 076)','','','',421899],
 ['Maximum HT / bases rehaussées','','','','=E26/E31'],
 ['Bases rehaussées / maximum HT','','','','=E31/E26'],
]
synth(s,rows)
for r_ in (18,20,30,32): s.cell(r_,2 if r_==18 else 5).number_format='0.00%'
for c_ in 'BCDE': s[f'{c_}18'].number_format='0.00%'
s['E22'].number_format='0.000'; s['E33'].number_format='0.0'
for r_ in (7,25,26,27,28,29,31): 
    for c_ in 'BCDE': s[f'{c_}{r_}'].number_format='#,##0.00'
method(wb,['Objet',
 "Examiner un à un les articles fractionnés que la recomposition de l'annexe n° 77 ne referme pas (64 notes isolées et 50 articles sur 8 tables), établir pour chaque cas la trace de l'annulation, rechercher tout règlement, et borner le montant en euros quelle que soit la règle de regroupement.",'',
 'Sources primaires',"Annexes C-1 à C-3 (n° 17 à 19), E-1 à E-3 (événements DEL ; n° 14 à 16), F-1 à F-3 (règlements ; n° 20 à 22), G-1 à G-3 (n° 33 à 35), H-1 à H-3 (tickets ; n° 30 à 32). Tables et notes isolées : annexe n° 77.",'',
 'Onglet « Notes isolées (64) »',
 "Chaque note isolée est classée : moitié dont le miroir identique est supprimé (toutes ses lignes, entières comprises, ont un DEL de même montant à ±0,02 € dans [t − 5 ; t + 30] min, appariement un pour un) ; paire de notes jumelles toutes deux réglées à plus de quinze minutes ; miroir partiel ; aucune contrepartie retrouvée.",'',
 'Onglet « Cas (63) »',
 "Les 55 notes à miroir supprimé et les 8 tables à parts supprimées. Pour chaque cas : notes payées, DEL appariés (chronologie : premier et dernier DEL, décalage par rapport au règlement), montant supprimé, ticket à 0 € de l'annexe H clôturé dans [premier DEL − 2 ; dernier DEL + 2] min (la note d'origine), Z. Contrôles : témoin (une note non fractionnaire du même jour, de nombre d'articles proche, tirée au hasard, graine 20261123) et placebo (même test à J + 7). Recherche de règlement de la part supprimée le même jour : mêmes articles ressaisis (R1), même total ressaisi (R2), même total sur une note réglée (T1), somme de notes (T2), l'un des 37 règlements portés sur un ticket à 0 € (Z) ; J signale une coïncidence de total antérieure au DEL, non retenue. Le même jeu de tests est appliqué au témoin (onglet « Témoin règlement (63) »).",'',
 'Onglet « Montant par fenêtre »',
 "Le montant des parts sans contrepartie réglée est recalculé pour chaque fenêtre de regroupement de l'annexe n° 77 (5 minutes à la journée). Sont exclues les parts dont la contrepartie est réglée (paires jumelles, tables refermées). Le maximum, toutes fenêtres, est retenu : 3 330,36 € TTC, soit 2 944,71 € HT (HT calculé au taux de chaque ligne).",'',
 'Onglet « Reliquat sans trace »',"Éléments sans miroir supprimé : 2 notes et 3 articles, 77,90 € TTC, soit 70,03 € HT.",'',
 'Reproductibilité',"Scripts : m1_B04.py, m2_Bc1.py, c1_C2.py, c1_C4C5.py et r3_pieces_b.py. Sorties : out/B04_notes.csv, Bc1_cas.csv, Bc1_temoin.csv, C2_cas.csv, C5.csv. Toutes les valeurs de la « Synthèse » sont des formules sur les onglets de la présente pièce, sauf les constantes signalées."])
wb.save(P+N159); print('159 écrit')
# =====================================================================  160
wb=openpyxl.Workbook(); wb.remove(wb.active); wb.create_sheet('Synthèse')
vn={'a':"(a) jour tiré dans l'exercice",'b':'(b) jour tiré dans le mois','c':'(c) heures permutées dans la journée réelle'}
cols=['tables','notes','articles','refermes','taux','residu']
for k in 'abc':
    t=pd.read_csv(OUT+f'B09_tirages_{k}.csv')
    sheet(wb,f'Tirages ({k})',['Tirage','Tables','Notes rattachées','Notes isolées','Articles fractionnés en table','Articles refermés','Taux de fermeture (%)','Complément arithmétique (€)','Contrôle : taux = refermés / articles (1/0)'],
          [(i-1,int(r.tables),int(r.notes),int(r.isolees),int(r.articles),int(r.refermes),float(r.taux),float(r.residu),f'=IF(ABS(F{i}/E{i}*100-G{i})<0.01,1,0)') for i,r in enumerate(t.itertuples(),2)])
s=wb['Synthèse']
rows=[['TEST PLACEBO : LA RÈGLE DE L\'ANNEXE N° 77 APPLIQUÉE AUX NOTES À FRACTION DÉPLACÉES AU HASARD (200 tirages par variante, graine 20261123)'],[],
      ['Variante / indicateur','Quantile 5 %','Médiane','Quantile 95 %','Minimum','Maximum','Réel (annexe n° 77)']]
real={'B':866,'C':1849,'G':99.012,'H':264.98}
for k in 'abc':
    sh=f"'Tirages ({k})'"
    for col,lab_ in (('B','tables'),('C','notes rattachées'),('G','taux de fermeture (%)'),('H','complément arithmétique (€)')):
        rg=f'{sh}!${col}$2:${col}$201'
        rows.append([f'{vn[k]} : {lab_}',f'=PERCENTILE({rg},0.05)',f'=MEDIAN({rg})',f'=PERCENTILE({rg},0.95)',f'=MIN({rg})',f'=MAX({rg})',real[col]])
rows+= [[],['Taux de fermeture maximal, 600 tirages (%)','','','','',"=MAX('Tirages (a)'!G2:G201,'Tirages (b)'!G2:G201,'Tirages (c)'!G2:G201)",99.012],
        ['Complément arithmétique, minimum et maximum sur 600 tirages (€)','','','',"=MIN('Tirages (a)'!H2:H201,'Tirages (b)'!H2:H201,'Tirages (c)'!H2:H201)","=MAX('Tirages (a)'!H2:H201,'Tirages (b)'!H2:H201,'Tirages (c)'!H2:H201)",264.98],
        ['Tirages dont le taux atteint le taux réel (99,0 %)','','','','',"=COUNTIF('Tirages (a)'!G2:G201,\">=99\")+COUNTIF('Tirages (b)'!G2:G201,\">=99\")+COUNTIF('Tirages (c)'!G2:G201,\">=99\")",'']]
synth(s,rows); s.column_dimensions['A'].width=70
method(wb,['Objet',"Vérifier que la règle de regroupement de l'annexe n° 77 ne fabrique pas le résultat : appliquée à des notes à fraction placées au hasard, elle ne doit pas refermer les articles.",'',
 'Règle appliquée',"Celle de l'annexe n° 77, inchangée : notes chaînées à quinze minutes au plus (≤ 15 min) et partageant au moins un article fractionné (même libellé normalisé, même prix) ; article refermé si la somme des fractions est à moins de 0,02 d'un entier ; complément arithmétique = (entier supérieur − somme) × prix unitaire.",'',
 'Tirages',"Les 1 913 notes à fraction sont déplacées avec toutes leurs lignes ; les autres notes ne sont pas utilisées. (a) chaque note reçoit un jour tiré au hasard dans son exercice, à la même heure ; (b) un jour tiré au hasard dans le même mois, à la même heure ; (c) la journée réelle est conservée, et les heures de règlement des notes à fraction du jour sont permutées au hasard entre elles. 200 tirages par variante, générateur numpy default_rng, graine 20261123.",'',
 'Quantiles',"Les quantiles de la « Synthèse » sont calculés par la fonction PERCENTILE (interpolation linéaire), identique à la méthode par défaut de numpy.",'',
 'Résultat',"Le taux de fermeture des notes réelles (99,0 %) est hors de l'enveloppe des 600 tirages : la variante la plus favorable au hasard (c) plafonne à 67,9 %.",'',
 'Reproductibilité',"Script : scripts/m1_B09.py (sorties out/B09_tirages_a.csv, B09_tirages_b.csv, B09_tirages_c.csv, B09_synthese.csv) ; mise en forme : scripts/r3_pieces_b.py."])
wb.save(P+N160); print('160 écrit')
