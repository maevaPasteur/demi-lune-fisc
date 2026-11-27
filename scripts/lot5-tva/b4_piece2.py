"""B4 : construit 162 (classification légale des 323 références ; incidence ticket par ticket).
Sources : cache B3_articles.pkl (b1_classif.py), C_b3.pkl (taux appliqué, taux légal), B5_tickets.pkl (b1_calculs.py), cartes de la cliente."""
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import json
from common import *
from pieces_common import *
CC=pd.read_pickle(CA+'C_b3.pkl'); A=pd.read_pickle(CA+'B3_articles.pkl'); T=pd.read_pickle(CA+'B5_tickets.pkl')
gid=set(T.index); CC['s1']=[(a,b) in gid for a,b in zip(CC.ex,CC.id)]
CC['tc']=CC.tot.map(c); CC['tl0']=CC.tl.fillna(CC.rart); CC['tl20']=CC.tl.fillna(20)
EXP={}; w=wb()
M=['162. Classification légale des 323 références vendues et incidence de l\'erreur de paramétrage, ticket par ticket',
 'Sources : annexes C-1 à C-3 (taux appliqué : voir 161) ; annexes G-1 à G-3 et H-1 à H-3 (tot_tva) ; cartes de la cliente (onglet « Sources ») ; proposition, p. 46 à 50. Scripts : b1_classif.py, b1_calculs.py ; ce classeur : b4_piece2.py.',
 '§ Règle de taux légal',
 'Boissons alcooliques, y compris les bières titrant plus de 0,5 % vol et les « mélanges [...] tels que les panachés » : 20 % (BOI-TVA-LIQ-30-10-10, § 130, version du 02/08/2023). Aliments, plats, desserts, boissons non alcooliques : 10 % (CGI, art. 279, m). Alcool intégré à un plat : 10 % (BOI-TVA-LIQ-30-20-10-20, § 80, repris de la R2, non relu pendant le lot).',
 'Trois références sont de nature non établie (VOUIVRE réf. 1949, CHOUKA réf. 2078, Griottines réf. 2017) : elles sont comptées au taux appliqué ; l\'onglet « Indéterminés » donne leur sensibilité à 20 %.',
 '§ Calcul',
 'Périmètre : notes de la première série (16 605 tickets du journal de TVA G). Pour chaque ticket, les lignes C sont groupées par taux (palier TTC) ; la TVA du palier est ROUND(palier × taux / (100 + taux) ; 2), arrondi de la caisse par palier ; la TVA du ticket est la somme des deux paliers.',
 'TVA appliquée recalculée : paliers au taux appliqué. TVA légale : paliers au taux légal (indéterminés au taux appliqué). Variante : indéterminés à 20 %.',
 'Les paliers sont des sommes de lignes C calculées par le script (jointure), les TVA, écarts et totaux sont des formules.',
 'Effet de taux net = TVA légale − TVA appliquée recalculée. Arrondi propre de la caisse = TVA appliquée recalculée − tot_tva (Σ tot_tva = Σ tax_amount du journal G).',
 'La « TVA manquante » de l\'onglet « Articles » est TTC × (taux légal / (100 + taux légal) − taux appliqué / (100 + taux appliqué)), sans arrondi par palier : elle sert à la décomposition par article du tableau 57 quater ; la somme exacte par ticket est dans « Tickets ».']
check_dash(M); methode(w,M)
S=w.create_sheet('Synthèse')
# ---------- Sources
src=[('Carte « vins et boissons » du 26/04/2023, PDF (carte_vins-boissons_2023-04-26_actuelle.pdf, 4 pages), page 2, rubrique « Bières »','Pression Affligem, Bière blonde d\'abbaye Belge : 25cl 4,20 € ; 50cl 8,00 €'),
 ('idem, page 2, rubrique « Bières »','Panaché Bière + Limonade : 25cl 4,20 € ; 50cl 8,00 €'),('idem, page 2, rubrique « Bières »','Picon Bière : 4,80 € ; 9,00 €'),
 ('idem, page 2, rubrique « Apéritifs Maison »','La Vouivre 12 cl 5,90 € : Crémant du Jura, Macvin et Crème de Cassis'),
 ('idem, page 2, rubrique « Apéritifs Maison »','Apéritif du Père Grégoire 6 cl 5,90 € : Crémant du Jura, Macvin et Liqueur cerise'),
 ('idem, page 2, rubrique « Apéritifs Maison »','Chat Perché 12 cl 5,90 € : Macvin, Jus de Poire et Sirop de Châtaigne'),
 ('Carte du 26/04/2023, classeur (carte_vins-boissons_26:04:23_aujourdhui.xls), onglet « Vins & boissons », ligne 12','Spritz jurassien : 4 cl Aperol, Crémant du Jura et Perrier, 9,00 €'),
 ('Carte « vins et boissons » du 20/07/2021, PDF (carte_vins-boissons_2021-07-20.pdf, 4 pages), page 2, rubrique « Bières »','Pression Affligem : 25cl 3,90 € ; 50cl 7,80 €'),
 ('idem, page 2, rubrique « Bières »','Panaché Bière + Limonade : 25cl 3,90 € ; 50cl 7,80 €'),('idem, page 2, rubrique « Bières »','Picon Bière : 4,50 € ; 8,90 €'),
 ('idem, page 2, rubrique « Apéritifs Maison »','La Vouivre 12 cl 5,20 € ; Apéritif du Père Grégoire 6 cl 4,90 € ; Chat Perché 12 cl 5,20 € (mêmes compositions qu\'en 2021)'),
 ('Pages 3 et 4 des deux PDF','Vins : colonnes « Verre 15cl », « Pichet 50cl », « Bouteille 75cl » ; aucune bière ni aucun apéritif maison'),
 ('Proposition de rectification, p. 50 (reconstitution)','« Pinte (50 cl de bière) » ; « Monaco (15 cl bière) » ; « Panaché (11 cl bière) »'),
 ('Remarque','Les fichiers des annexes n° 152 et 153 du courrier (152-carte-des-vins-du-20-07-2021-verre-pichet-bouteille.pdf, 153-carte-des-vins-du-26-04-2023-verre-pichet-bouteille.pdf) ne figurent pas dans le dossier de la cliente ; il n\'a pas été vérifié qu\'ils reproduisent la page 2 des cartes ci-dessus.')]
wsrc=w.create_sheet('Sources'); header(wsrc,['Source','Extrait'],[80,100])
for a,b in src: wsrc.append([a,b])
# ---------- Articles
w_a=w.create_sheet('Articles')
hd=['ref','libellé(s)','lignes (toutes séries)','Σ Qte','PU médian','première vente','dernière vente','taux appliqué','nature','source de la classification','taux légal','concordance']
for ex in EX: hd+=[f'{ex} lignes 1re série',f'{ex} TTC 1re série',f'{ex} TVA manquante 1re série']
hd+=['lignes mal paramétrées (toutes séries)']
header(w_a,hd,[7,26,8,8,7,10,10,7,26,40,7,8]+[8,11,10]*3+[9])
A=A.reset_index(drop=True); NA=len(A)
for i,r in A.iterrows():
    k=2+i; z=CC[(CC.ref==r.ref)&CC.s1]; tl=None if r.taux_legal in ('',None) or pd.isna(r.taux_legal) else int(r.taux_legal)
    row=[r.ref,r.libelles,int(r.lignes),float(r.qte),float(r.pu_median),str(r.premiere)[:10],str(r.derniere)[:10],int(r.t_suiv),r.nature,r.source,tl,r.concordant]
    for j,ex in enumerate(EX):
        y=z[z.ex==ex]; cl=[L(13+3*j),L(14+3*j)]
        row+=[int(len(y)),round(float(y.tot.sum()),2),f'=IF(ISNUMBER(K{k}),{cl[1]}{k}*(K{k}/(100+K{k})-H{k}/(100+H{k})),0)']
    row+=[f'=IF(AND(ISNUMBER(K{k}),K{k}<>H{k}),C{k},0)']
    w_a.append(row)
# ---------- Tickets
key=['ex','id']; s1=CC[CC.s1]
def pal(col):
    x=s1.assign(p10=np.where(s1[col]==10,s1.tc,0),p20=np.where(s1[col]==20,s1.tc,0)).groupby(key).agg(p10=('p10','sum'),p20=('p20','sum'))
    return x
pa,pl,p2=pal('rart'),pal('tl0'),pal('tl20')
info=s1.groupby(key).agg(date=('date','first'),ticket=('ticket','first'),heure=('heure','first'),ttc=('tot_ttc','first'),mal=('tl0',lambda s: 0))
mal=s1.assign(m=s1.tl0!=s1.rart).groupby(key).m.any()
TT=info.join(pa).join(pl,rsuffix='_l').join(p2,rsuffix='_2').join(T[['tot_tva','app','leg','l20']]).join(mal)
TT=TT.reset_index().sort_values(['ex','date','heure','ticket']).reset_index(drop=True); NT=len(TT); assert NT==16605
wt=w.create_sheet('Tickets')
header(wt,['exercice','Id note','date','heure','n° ticket','tot_ttc','palier 10 %, taux appliqué','palier 20 %, taux appliqué','palier 10 %, taux légal','palier 20 %, taux légal','palier 10 %, indéterminés à 20 %','palier 20 %, indéterminés à 20 %',
 'TVA appliquée recalculée','TVA légale','TVA légale, indéterminés à 20 %','tot_tva (H, = Σ tax_amount G)','effet de taux net (légale − appliquée)','arrondi propre de la caisse (appliquée − tot_tva)','ticket touché (effet ≠ 0)','ticket portant un article mal paramétré'],[10,8,11,7,7,9]+[10]*6+[10,10,10,10,10,10,7,7])
tv=lambda a,b: f'ROUND({a}/11,2)+ROUND({b}/6,2)'
for i,r in TT.iterrows():
    k=2+i
    wt.append([r.ex,int(r.id),r.date,r.heure,int(r.ticket),float(r.ttc),r.p10/100,r.p20/100,r.p10_l/100,r.p20_l/100,r.p10_2/100,r.p20_2/100,
      f'={tv(f"G{k}",f"H{k}")}',f'={tv(f"I{k}",f"J{k}")}',f'={tv(f"K{k}",f"L{k}")}',r.tot_tva/100,f'=N{k}-M{k}',f'=M{k}-P{k}',f'=IF(ROUND(Q{k},2)<>0,1,0)',int(bool(r.m))])
# contrôle python des formules : ROUND(p/11,2) en euros = arrondi par palier en centimes
chk=lambda p10,p20: (np.floor(p10/11+0.5)+np.floor(p20/6+0.5)).astype(int)
for a,b,col in [('p10','p20','app'),('p10_l','p20_l','leg'),('p10_2','p20_2','l20')]:
    print(col,'formule = cache B5 :',int((chk(TT[a],TT[b])==TT[col]).sum()),'/',NT)
# ---------- Indéterminés
wi=w.create_sheet('Indéterminés')
header(wi,['ref','libellé','taux appliqué']+[f'{ex} TTC 1re série' for ex in EX]+[f'{ex} TVA en plus si 20 % (sans arrondi)' for ex in EX],[7,22,8]+[11]*6)
ind=A[A.concordant=='?'].reset_index(drop=True)
for i,r in ind.iterrows():
    k=2+i; z=CC[(CC.ref==r.ref)&CC.s1]
    wi.append([r.ref,r.libelles,int(r.t_suiv)]+[round(float(z[z.ex==ex].tot.sum()),2) for ex in EX]+[f'=IF(C{k}=20,0,{L(4+j)}{k}*(20/120-C{k}/(100+C{k})))' for j in range(3)])
NI=len(ind)
wi.append([]); wi.append(['Sensibilité ticket par ticket (onglet « Tickets ») : TVA légale, indéterminés à 20 %, moins TVA légale'])
ki=NI+4
TR=lambda col: f"'Tickets'!${col}$2:${col}${1+NT}"
wi.append(['','','']+[f'=SUMIFS({TR("O")},{TR("A")},"{ex}")-SUMIFS({TR("N")},{TR("A")},"{ex}")' for ex in EX]+[f'=SUM(D{ki}:F{ki})'])
# ---------- Synthèse
S.column_dimensions['A'].width=70
for cl in 'BCDE': S.column_dimensions[cl].width=16
S.append([cell(S,'Tableau 57 quater et ratios du point 2.5.6 c, par formules (première série, 16 605 tickets du journal de TVA)',bold=True)])
S.append([cell(S,h,bold=True,fill=True) for h in ['Grandeur','Ex. 31/03/2023','Ex. 31/03/2024','Ex. 31/03/2025','Cumul 3 ex.']])
row=[2]
AR=lambda col: f"'Articles'!${col}$2:${col}${1+NA}"
def line(lab,fs,cum=None,fmt=EUR,exp=None):
    row[0]+=1; k=row[0]
    S.append([lab]+[cell(S,f,fmt=fmt) for f in fs]+[cell(S,cum if cum else f'=SUM(B{k}:D{k})',fmt=fmt)])
    if exp:
        for cl,v in zip('BCDE',exp):
            if v is not None: EXP[f'{cl}{k}']=v
    return k
arts=[('1989','Pinte (10 % au lieu de 20 %)',[(254,2172.29,164.57),(248,2254.90,170.83),(255,2424.00,183.64)]),('0099','Panaché (10 % au lieu de 20 %)',[(126,585.00,44.32),(99,426.90,32.34),(91,407.00,30.83)]),
      ('0354','Monaco (10 % au lieu de 20 %)',[(68,263.25,19.94),(55,232.80,17.64),(61,310.80,23.55)]),('1816','1 Boule Glace (20 % au lieu de 10 %)',[(76,158.00,-11.97),(56,189.50,-14.36),(48,157.50,-11.93)]),
      ('2119','Crêpe marron chantilly (20 % au lieu de 10 %)',[(0,0,0),(2,17.80,-1.35),(1,8.90,-0.67)])]
kart=[]
for ref,lab,ev in arts:
    for t,(nm,fm) in enumerate([('lignes',INT),('TTC',EUR),('TVA manquante (sans arrondi par palier)',EUR)]):
        fs=[f'=SUMIFS({AR(L(13+3*j+t))},{AR("A")},"{ref}")' for j in range(3)]
        k=line(f'{lab} : {nm}',fs,fmt=fm,exp=[e[t] for e in ev]+[None]);
        if t==2: kart.append(k)
k=line('Somme des TVA manquantes par article (sans arrondi par palier)',[f'=SUM({",".join(f"{c}{x}" for x in kart)})' for c in 'BCD'])
for cl,v in zip("BCDE",[216.86,205.10,225.41,None]):
    if v: EXP[f'{cl}{k}']=v
ex_=lambda e:f'"{e}"'
kliq=line('TVA liquidée par la caisse (Σ tot_tva = Σ tax_amount)',[f'=SUMIFS({TR("P")},{TR("A")},{ex_(e)})' for e in EX],exp=[42552.76,46400.08,45926.63,134879.47])
kapp=line('TVA recalculée au taux appliqué (arrondi de la caisse par palier)',[f'=SUMIFS({TR("M")},{TR("A")},{ex_(e)})' for e in EX],exp=[42553.46,46400.95,45927.48,134881.89])
karr=line('dont arrondi propre de la caisse (recalculée − liquidée)',[f'={c}{kapp}-{c}{kliq}' for c in 'BCD'],exp=[0.70,0.87,0.85,2.42])
line('Tickets où l\'arrondi propre de la caisse n\'est pas nul',[f'=COUNTIFS({TR("A")},{ex_(e)},{TR("R")},"<>0")' for e in EX],fmt=INT,exp=[None,None,None,242])
kleg=line('TVA légalement due (articles au taux légal, arrondi de la caisse par palier)',[f'=SUMIFS({TR("N")},{TR("A")},{ex_(e)})' for e in EX],exp=[42770.29,46606.01,46152.80,135529.10])
keff=line('Effet de taux net, arrondi par palier (légale − recalculée au taux appliqué)',[f'={c}{kleg}-{c}{kapp}' for c in 'BCD'],exp=[216.83,205.06,225.32,647.21])
line('TVA légalement due − TVA liquidée (= effet de taux + arrondi propre)',[f'={c}{kleg}-{c}{kliq}' for c in 'BCD'],exp=[217.53,205.93,226.17,649.63])
line('dont sous-liquidation (tickets à effet positif)',[f'=SUMIFS({TR("Q")},{TR("A")},{ex_(e)},{TR("Q")},">0")' for e in EX],exp=[227.24,219.30,236.32,682.86])
line('dont sur-liquidation (tickets à effet négatif)',[f'=SUMIFS({TR("Q")},{TR("A")},{ex_(e)},{TR("Q")},"<0")' for e in EX],exp=[-10.41,-14.24,-11.00,-35.65])
ktt=line('Tickets touchés (effet ≠ 0)',[f'=COUNTIFS({TR("A")},{ex_(e)},{TR("S")},1)' for e in EX],fmt=INT,exp=[498,439,431,1368])
line('Tickets portant un article mal paramétré',[f'=COUNTIFS({TR("A")},{ex_(e)},{TR("T")},1)' for e in EX],fmt=INT,exp=[None,None,None,1378])
kn=line('Tickets du journal de TVA',[f'=COUNTIF({TR("A")},{ex_(e)})' for e in EX],fmt=INT,exp=[5658,5529,5418,16605])
kttc=line('Σ TTC des tickets (tot_ttc)',[f'=SUMIFS({TR("F")},{TR("A")},{ex_(e)})' for e in EX],exp=[403370.42,437992.92,434827.86,1276191.20])
kl20=line('TVA légale, indéterminés à 20 %',[f'=SUMIFS({TR("O")},{TR("A")},{ex_(e)})' for e in EX])
S.append([]); row[0]+=1
S.append([cell(S,'Ratios (cumul trois exercices)',bold=True),cell(S,'Valeur',bold=True),cell(S,'Arrondi du texte',bold=True)]); row[0]+=1
def one(lab,f,fmt,exp=None):
    row[0]+=1; k=row[0]; S.append([lab,cell(S,f,fmt=fmt)])
    if exp is not None: EXP[f'B{k}']=exp
    return k
one('Bases HT rehaussées, proposition p. 53 (donnée d\'entrée)',421899.17,EUR)
kb=row[0]
one('Effet de taux net / TVA liquidée',f'=E{keff}/E{kliq}',PCT2,('pct2',0.48))
one('Effet de taux net / CA TTC des tickets',f'=E{keff}/E{kttc}',PCT,('pct3',0.051))
one('Effet de taux net / bases HT rehaussées',f'=E{keff}/B{kb}',PCT,('pct3',0.153))
k1=one('Lignes C d\'articles mal paramétrés (toutes séries)',f'=SUM({AR(L(22))})',INT,1443)
one('Lignes C (161)',97769,INT)
one('en % des lignes C',f'=B{k1}/B{k1+1}',PCT2,('pct2',1.48))
one('Références mal paramétrées (concordance « NON »)',f'=COUNTIF({AR("L")},"NON")',INT,5)
one('Références concordantes (« oui »)',f'=COUNTIF({AR("L")},"oui")',INT,315)
one('Références de nature non établie (« ? »)',f'=COUNTIF({AR("L")},"?")',INT,3)
one('Références',f'=COUNTA({AR("A")})',INT,323)
one('Tickets touchés / tickets',f'=E{ktt}/E{kn}',PCT2)
fn=PIECES+'162-R2-classification-legale-323-references-incidence-ticket-par-ticket.xlsx'
w.save(fn); json.dump({'file':fn,'sheet':'Synthèse','exp':EXP},open(OUT+'b4/exp_162.json','w'),ensure_ascii=False); print('écrit',fn)
