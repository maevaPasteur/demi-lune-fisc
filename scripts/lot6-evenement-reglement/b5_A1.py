"""Mission 4 : construit 167-R2 (traçabilité des DEL : rattachement au Z, note unique, placebos, tables vidées).
Sources : annexes E1-E3 (cache E.pkl, s02), annexes H1-H3 (cache H.pkl, s06), annexes C1-C3 (cache lot23 CC.pkl : nombre de lignes par note),
annexe 155-R3 (onglet « Reprise »), cache b5_tables_videes.pkl (b5_tables_videes.py, mêmes graines que u02 et u02b).
Placebo « heure + 60 à 180 min » : tirage de s04 reproduit (graine 20261123, permutation P2 puis entiers)."""
import sys, json, datetime as dt; sys.path.insert(0,'scripts/lot5-tva')
import pandas as pd, numpy as np
from pieces_common import cell, header, methode, check_dash, wb, EUR, PCT2, INT
CA='scripts/lot6-evenement-reglement/cache/'; OUTD='public/documents/pieces-lot6/'
FN=OUTD+'167-R2-tracabilite-DEL-rattachement-Z-note-tables-videes-placebos.xlsx'
E=pd.read_pickle(CA+'E.pkl').reset_index(drop=True); H=pd.read_pickle(CA+'H.pkl').reset_index(drop=True)
CC=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/CC.pkl'); nC=CC.groupby('id').size()
TV=pd.read_pickle(CA+'b5_tables_videes.pkl')
# tirage P3 de s04, reproduit
DEL=E[E.typEven=='DEL']
base=pd.DataFrame({'ex':DEL.ex,'a':DEL.amount_c})
rng=np.random.default_rng(20261123)
base['a']=base.groupby('ex').a.transform(lambda s: rng.permutation(s.values))
off=rng.integers(60,181,len(base)); OFF=dict(zip(DEL.index,off))
d0=dt.date(1899,12,30); ser=lambda s: (dt.date.fromisoformat(s)-d0).days
w=wb()
M=['167-R2. Traçabilité des suppressions « DEL » : rattachement au ticket Z et à la note, placebos, tables vidées',
 'Onglets : « Z », « Note unique » et « Placebos » (dénombrements par exercice, formules sur « Sources_E ») ; « Tables vidées » ; « Jours » ; « Sources_H » ; « Sources_E ». Sources : annexes E-1 à E-3 du service (tpvevenement, 23 339 lignes), annexes H-1 à H-3 (liste des tickets, 19 903 notes), annexes C-1 à C-3 (nombre de lignes par note), annexe n° 155-R3 (onglet « Reprise »). Ce classeur : scripts/b5_A1.py ; mesures d\'origine : s02, s04, s05, u02, u02b ; valeurs par table : b5_tables_videes.py. Graine 20261123 pour tout tirage.',
 '§ Conventions',
 'Dates en numéros de série (calendrier 1900). Minute = heure × 60 + minute (colonne heure à la minute des annexes). Clé = date × 10^8 + Z × 10^4 + minute.',
 'Les onglets « Sources_ » portent les valeurs des annexes ; toutes les colonnes de calcul et toute la « Synthèse » sont des formules. Seules exceptions, en valeurs et signalées : le nombre de lignes de l\'annexe C par note (agrégat de C-1 à C-3), le décalage tiré du placebo « heure + 60 à 180 min », et les moyennes de placebo par table de l\'onglet « Tables vidées » (30 ou 200 réplications, impossibles à écrire en formules).',
 '§ Définitions',
 'Rattachement au Z : la date et le n° de Z de la ligne E existent ensemble dans l\'annexe H (onglet « Jours » : 659 couples).',
 'Note unique : exactement une note de l\'annexe H (deux séries) du même jour et du même Z est close à la minute du DEL (s04, règle R1). Plusieurs : deux notes ou plus. Aucune : zéro.',
 'Ticket à 0,00 € sans article : note de l\'annexe H à total nul, sans aucune ligne dans l\'annexe C.',
 'Placebo « même heure à J + 7 » : même minute, sept jours plus tard, Z du jour cible ; ne sont testés que les DEL dont le jour cible est un jour d\'ouverture (20 446). Placebo « heure + 60 à 180 min » : même jour, même Z, minute décalée d\'un entier tiré uniformément entre 60 et 180.',
 'Tables vidées : 2 359 tables de l\'annexe 155 (180 003,94 €). « Annexe » : colonnes obs et autre de l\'onglet « Reprise » de l\'annexe 155 (affectation exclusive). Autres lignes : réimplémentation B des trois critères (u02), affectation exclusive (1) égalité > (2) table entière > (3) lignes au même prix, placebo = table déplacée selon la variante, moyenne des réplications.',
 'Excès = Σ observé − Σ placebo. Part du montant des tables = excès / Σ V. f = excès / (Σ V − Σ placebo), part corrigée de ce que le hasard retrouverait.']
check_dash(M); methode(w,M)
SY=w.create_sheet('Synthèse')
WZ=w.create_sheet('Z'); WN=w.create_sheet('Note unique'); WP=w.create_sheet('Placebos'); wt=w.create_sheet('Tables vidées')
# Jours
J=H.groupby('date_ticket').no_z_report.first().reset_index()
wj=w.create_sheet('Jours'); header(wj,['date (série)','date','Z du jour (annexe H)'],[12,12,10])
for r in J.itertuples(): wj.append([ser(r.date_ticket),r.date_ticket,int(r.no_z_report)])
NJ=len(J)
# Sources_H
wh=w.create_sheet('Sources_H')
header(wh,['id','exercice','date (série)','heure','minute','Z','tot_ttc','série','lignes C (agrégat)','clé','ticket à 0,00 € sans article'],[8,10,10,7,7,7,10,6,9,16,10])
for i,r in H.iterrows():
    k=2+i
    wh.append([int(r.id),r.ex,ser(r.date_ticket),r.heure_ticket,f'=VALUE(LEFT(D{k},2))*60+VALUE(MID(D{k},4,2))',int(r.no_z_report),float(r.tot_ttc),int(r.serie),int(nC.get(r.id,0)),
               f'=C{k}*100000000+F{k}*10000+E{k}',f'=IF(AND(G{k}=0,I{k}=0),1,0)'])
NH=len(H); RH=lambda c:f"Sources_H!${c}$2:${c}${1+NH}"
# Sources_E
we=w.create_sheet('Sources_E')
cols=['id','exercice','dateEven (série)','dateEven','heureEven','typEven','no_zEport','amount','continuité (id − id précédent)','minute','clé',
      'Z présent dans H (1/0)','notes closes à la minute','note unique : ticket à 0,00 € sans article','J+7 : date','J+7 : jour testé','J+7 : notes closes à la minute','P3 : décalage tiré (min)','P3 : notes closes à la minute']
header(we,cols,[7,9,9,10,6,6,6,9,8,7,15,7,7,8,9,6,7,7,7])
for i,r in E.iterrows():
    k=2+i; isdel=r.typEven=='DEL'
    row=[int(r.id),r.ex,ser(r.dateEven),r.dateEven,r.heureEven,r.typEven,int(r.no_zEport),float(r.amount),(f'=A{k}-A{k-1}' if k>2 else None),
         f'=VALUE(LEFT(E{k},2))*60+VALUE(MID(E{k},4,2))',f'=C{k}*100000000+G{k}*10000+J{k}']
    if isdel:
        row+=[f'=IF(COUNTIFS({RH("C")},C{k},{RH("F")},G{k})>0,1,0)',f'=COUNTIF({RH("J")},K{k})',f'=IF(M{k}=1,SUMIF({RH("J")},K{k},{RH("K")}),0)',
              f'=C{k}+7',f'=IF(COUNTIF(Jours!$A$2:$A${1+NJ},O{k})>0,1,0)',
              f'=IF(P{k}=1,COUNTIF({RH("J")},O{k}*100000000+VLOOKUP(O{k},Jours!$A$2:$C${1+NJ},3,0)*10000+J{k}),"")',
              int(OFF[i]),f'=COUNTIF({RH("J")},C{k}*100000000+G{k}*10000+J{k}+R{k})']
    we.append(row)
NE=len(E); RE=lambda c:f"Sources_E!${c}$2:${c}${1+NE}"

EXL=['2022-2023','2023-2024','2024-2025']
def bloc(ws,title,cols,rows):
    header(ws,[title]+EXL+['Total'],[70,12,12,12,12])
    for lab,f in rows:
        ws.append([lab]+[f(f'"{e}"') for e in EXL]+[f('"*"')])
DD=lambda ex: f'{RE("F")},"DEL",{RE("B")},{ex}'
bloc(WZ,'Rattachement des DEL au ticket Z (date et Z de la ligne E présents ensemble dans l\'annexe H)',None,[
 ('Lignes DEL',lambda ex:f'=COUNTIFS({DD(ex)})'),('DEL rattachés à leur Z',lambda ex:f'=COUNTIFS({DD(ex)},{RE("L")},1)'),
 ('Couples (date, Z) des jours d\'ouverture (onglet « Jours »)',lambda ex:f'=COUNTA(Jours!$A$2:$A${1+NJ})' if ex=='"*"' else '')])
bloc(WN,'DEL selon le nombre de notes du même Z closes à la minute du DEL',None,[
 ('Une seule note',lambda ex:f'=COUNTIFS({DD(ex)},{RE("M")},1)'),('dont ticket à 0,00 € sans article',lambda ex:f'=SUMIFS({RE("N")},{RE("B")},{ex})'),
 ('Plusieurs notes',lambda ex:f'=COUNTIFS({DD(ex)},{RE("M")},">=2")'),('Aucune note',lambda ex:f'=COUNTIFS({DD(ex)},{RE("M")},0)')])
bloc(WP,'Placebos du rattachement à la note',None,[
 ('Même heure à J + 7 : DEL testés',lambda ex:f'=COUNTIFS({DD(ex)},{RE("P")},1)'),('Même heure à J + 7 : une seule note à la minute',lambda ex:f'=COUNTIFS({DD(ex)},{RE("Q")},1)'),
 ('Heure + 60 à 180 min : une seule note à la minute',lambda ex:f'=COUNTIFS({DD(ex)},{RE("S")},1)')])
# Tables vidées
tcols=['n° table (155)','exercice','date','minute','Z','V (€)','155 : obs (€)','155 : autre jour (€)','B : (1) égalité','B : (2) table entière','B : (3) lignes au même prix (€)','B : observé exclusif (€)',
       'placebo jours d\'ouverture +1/+3/+8 (€)','placebo ±1/±3/±8 jours d\'ouverture (€)','placebo ±1 semaine (€)','placebo ±2 semaines (€)','placebo ±1 à ±8 semaines (€)','contrôle exclusif = formule']
header(wt,tcols,[7,9,10,6,6,9,9,9,6,6,10,10,10,10,10,10,10,8])
TV=TV.sort_values('no').reset_index(drop=True)
for i,r in TV.iterrows():
    k=2+i
    wt.append([int(r.no),r.ex,r.d,int(r.t) if not isinstance(r.t,str) else r.t,int(r.z),r.V/100,float(r.obs),float(r.autre),int(bool(r.c1)),int(bool(r.c2)),r.c3/100,
               f'=IF(OR(I{k}=1,J{k}=1),F{k},K{k})',r.o138/100,r.o138pm/100,r.w1/100,r.w2/100,r.w1_8/100,f'=IF(ABS(L{k}-{r.excl/100!r})<0.005,1,0)'])
NT=len(TV); RT=lambda c:f"'Tables vidées'!${c}$2:${c}${1+NT}"
# Synthèse
SY.column_dimensions['A'].width=88; SY.column_dimensions['B'].width=18; SY.column_dimensions['C'].width=40
SY.append([cell(SY,'Synthèse : chaque chiffre est une formule ; colonne C, chiffre cité par la section 2.6',bold=True)])
EXP={}; rows=[]
D=f'{RE("F")},"DEL"'
it=[('§ Journal des événements (tableau 58 ; point 2.6.3 c)',None,None,None),
 ('Événements des annexes E',f'=COUNTA({RE("A")})',23339,INT),('Identifiant minimal',f'=MIN({RE("A")})',36681,INT),('Identifiant maximal',f'=MAX({RE("A")})',60019,INT),
 ('Identifiants manquants (Σ des sauts de continuité > 1)',f'=SUMPRODUCT((Sources_E!$I$3:$I${1+NE}>1)*(Sources_E!$I$3:$I${1+NE}-1))',0,INT),
 ('Lignes DEL',f'=COUNTIF({RE("F")},"DEL")',21302,INT),('Montant DEL (€)',f'=SUMIF({RE("F")},"DEL",{RE("H")})',430763.15,EUR),
 ('§ Rattachement au ticket Z (tableau 58 bis)',None,None,None),
 ('DEL rattachés à leur Z (même date, même Z dans H)',f'=SUM({RE("L")})',21302,INT),('Couples (date, Z) de l\'annexe H',f'=COUNTA(Jours!$A$2:$A${1+NJ})',659,INT),
 ('§ Rattachement à la note (tableau 58 bis)',None,None,None),
 ('DEL à la minute de clôture d\'une seule note du même Z',f'=COUNTIFS({D},{RE("M")},1)',13372,INT),('en % des DEL',f'=B{{r}}/B{{r6}}','62,77 %',PCT2),
 ('dont ticket à 0,00 € sans article',f'=SUM({RE("N")})',None,INT),('en % des rattachements uniques',f'=B{{r}}/B{{r12}}','85,0 %',PCT2),
 ('DEL à la minute de plusieurs notes',f'=COUNTIFS({D},{RE("M")},">=2")',1725,INT),('en % des DEL',f'=B{{r}}/B{{r6}}','8,10 %',PCT2),
 ('DEL sans clôture de note à la minute',f'=COUNTIFS({D},{RE("M")},0)',6205,INT),('en % des DEL',f'=B{{r}}/B{{r6}}','29,13 %',PCT2),
 ('§ Placebos',None,None,None),
 ('J + 7 : DEL testés (jour cible ouvert)',f'=COUNTIFS({D},{RE("P")},1)',20446,INT),('J + 7 : une seule note à la minute',f'=COUNTIFS({D},{RE("Q")},1)',2175,INT),('J + 7 : taux',f'=B{{r}}/B{{rm1}}','10,64 %',PCT2),
 ('heure + 60 à 180 min : une seule note à la minute',f'=COUNTIFS({D},{RE("S")},1)',453,INT),('heure + 60 à 180 min : taux',f'=B{{r}}/B{{r6}}','2,13 %',PCT2),
 ('§ Tables vidées (point 2.6.3 d)',None,None,None),
 ('Tables',f'=COUNT({RT("A")})',2359,INT),('Montant des tables Σ V (€)',f'=SUM({RT("F")})',180003.94,EUR),
 ('Contrôle : observé exclusif recalculé = valeur du script (tables conformes)',f'=SUM({RT("R")})',2359,INT)]
var=[('annexe 155 (obs − autre jour)','G','H','7 030,75 € ; f 11,70 %'),('jours d\'ouverture +1/+3/+8','L','M','7 977,25 €'),('jours d\'ouverture ±1/±3/±8','L','N','8 333,46 €'),
     ('±1 semaine','L','O','9 319,68 € ; f 14,82 %'),('±2 semaines','L','P','14 336,05 €'),('±1 à ±8 semaines','L','Q','21 018,48 € ; f 28,18 %')]
exp_var={'H':(7030.75,11.70),'M':(7977.25,None),'N':(8333.46,None),'O':(9319.68,14.82),'P':(14336.05,None),'Q':(21018.48,28.18)}
r=2; ref={}
for a,f,e,fm in it:
    if f is None: SY.append([cell(SY,a,bold=True)]); r+=1; continue
    if 'Lignes DEL'==a: ref['r6']=r
    if a.startswith('DEL à la minute de clôture'): ref['r12']=r
    f=f.replace('{r}',str(r-1)).replace('{r6}',str(ref.get('r6',0))).replace('{r12}',str(ref.get('r12',0))).replace('{rm1}',str(r-2))
    SY.append([a,cell(SY,f,fmt=fm),e if isinstance(e,str) else (None if e is None else e)])
    if isinstance(e,(int,float)): EXP[f'B{r}']=e
    elif isinstance(e,str) and '%' in e: EXP[f'B{r}']=['pct1' if e.count(',') and len(e.split(',')[1].split()[0])==1 else 'pct2',float(e.split()[0].replace(',','.'))]
    if a=='Tables': ref['rT']=r
    if a.startswith('Montant des tables'): ref['rV']=r
    r+=1
for lab,o,pc,txt in var:
    eu,fv=exp_var[pc]
    SY.append([f'Excès, {lab} (€)',cell(SY,f'=SUM({RT(o)})-SUM({RT(pc)})',fmt=EUR),txt]); EXP[f'B{r}']=eu; re_=r; r+=1
    SY.append([f'  part du montant des tables, {lab}',cell(SY,f'=B{re_}/B{ref["rV"]}',fmt=PCT2),None]); r+=1
    SY.append([f'  f, {lab}',cell(SY,f'=B{re_}/(B{ref["rV"]}-SUM({RT(pc)}))',fmt=PCT2),None])
    if fv: EXP[f'B{r}']=['pct2',fv]
    r+=1
for k in ['part du montant des tables, annexe 155','part du montant des tables, ±1 semaine']: pass
w.save(FN); json.dump({'file':FN,'sheet':'Synthèse','exp':EXP},open('scripts/lot6-evenement-reglement/out/.exp_A1.json','w'),ensure_ascii=False); print('écrit',FN,len(EXP),'attendus')
