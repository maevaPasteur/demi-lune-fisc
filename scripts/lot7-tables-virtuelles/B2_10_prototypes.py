"""Versions de travail des annexes 173 (libellés comptés comme couverts, recalcul par formules) et 174 (passerelle des
populations, par formules sur les annexes C, H, E, F). Écrits dans scripts/lot7-tables-virtuelles/out/pieces/ ; recalcul LibreOffice et contrôle en B2_11."""
import sys; sys.path.insert(0,"scripts/lot7-tables-virtuelles")
from B2_common import *
import openpyxl, hashlib
from openpyxl.styles import Font
C,E,F,H,A=load(); S=source(); S['id']=S.id.astype(int)
PC='scripts/lot7-tables-virtuelles/out/pieces/'
BLUE=Font(color='1F4E9A')
def sha(f): return hashlib.sha256(open('scripts/lot7-tables-virtuelles/cache/entrees/'+f,'rb').read()).hexdigest()
SRC=['17-annexe-c1-2022-2023.xls','18-annexe-c2-2023-2024.xls','19-annexe-c3-2024-2025.xls','ANNEXE-H1_liste-tickets_2022-2023.xls','ANNEXE-H2_liste-tickets_2023-2024.xls','ANNEXE-H3_liste-tickets_2024-2025.xls','14-annexe-e1-2022-2023.xls','15-annexe-e2-2023-2024.xls','16-annexe-e3-2024-2025.xls','20-annexe-f1-2022-2023.xls','21-annexe-f2-2023-2024.xls','22-annexe-f3-2024-2025.xls']
SH={f:sha(f) for f in SRC}
# ---------- 173
L=pd.read_csv(OUT2+'07_libelles.csv'); cats=pd.read_csv(OUT+'D05_categories.csv')[['lib','categorie']]
s2=set(H[H.serie==2].id); z0n=set(H[(H.serie==1)&(H.tc==0)].id)
Cx=C[~C.id.isin(s2|z0n)].copy(); Cx['svc']=np.where(Cx.heure.map(tm)<1080,'midi','soir')
lib=Cx.groupby('libs').agg(pu=('pu','median'),notes=('id','nunique'),qte=('qte','sum')).reset_index().rename(columns={'libs':'lib'})
lib=lib.merge(L[['lib','part_avec_autre_plat','DP_corrigee']],on='lib',how='left').merge(cats,on='lib',how='left')
P=plats(); lib['compte_societe']=lib.lib.isin(P).astype(int); lib['compte_DP']=lib.DP_corrigee.fillna(0).astype(int)
lib['categorie']=lib.categorie.fillna('non compté par la société')
lib=lib.sort_values(['compte_societe','qte'],ascending=[False,False]).reset_index(drop=True)
G=Cx.groupby(['date','svc','libs']).qte.sum().reset_index()
S92=pd.read_pickle(Q+'S92.pkl')
wb=openpyxl.Workbook(); ws=wb.active; ws.title='Lisez-moi'
for i,t in enumerate(['Version de travail : annexe 173, libellés comptés comme couverts, avec recalcul par formules.',
  'Sources : annexes C-1 à C-3 (lignes d articles), H-1 à H-3 (séries). SHA-256 : '+' ; '.join(f'{k} {v[:16]}…' for k,v in SH.items() if k.startswith(('17','18','19','ANNEXE-H'))),
  'Périmètre : notes de la première série portant des lignes (16 605) ; exclus : 17 tickets non nuls de la seconde série (non réglés) et 2 notes entièrement à 0,00 €.',
  'Onglet Libellés : une ligne par libellé ; colonne G « Compté » modifiable (1 = compté, 0 = non) ; valeur proposée : définition D-P corrigée (out/B2/07.txt). Colonne H : choix de la pièce 92 (pour comparaison).',
  'Onglet Lignes : quantités par journée, service (midi : clôture avant 18 h) et libellé ; colonne E = quantité × « Compté » (formule).',
  'Onglet Services : couverts (SOMME.SI.ENS), places (46 de septembre à avril, 48 de mai à août : règle de la pièce 92, modifiable colonne D), occupation.',
  'Onglet Synthèse : couverts, occupation moyenne, rapport des sommes, services au-delà de 100 %, maximum, par espace.',
  'Construction définitive après la clôture du débat. Aucune affirmation sur le certificat de caisse.']):
    ws.cell(i+1,1,t)
w=wb.create_sheet('Libellés'); hdr=['Libellé','PU médian','Catégorie','Notes','Quantité','Part des notes avec un autre plat compté','Compté (modifiable)','Compté pièce 92']
w.append(hdr)
for r in lib.itertuples(): w.append([r.lib,round(r.pu,2),r.categorie,int(r.notes),round(r.qte,2),None if pd.isna(r.part_avec_autre_plat) else round(r.part_avec_autre_plat,3),int(r.compte_DP),int(r.compte_societe)])
nlib=len(lib)+1
w=wb.create_sheet('Lignes'); w.append(['Date','Service','Libellé','Quantité','Quantité comptée'])
for i,r in enumerate(G.itertuples(),start=2):
    w.append([r.date,r.svc,r.libs,round(r.qte,4),f"=D{i}*IFERROR(VLOOKUP(C{i},Libellés!$A$2:$G${nlib},7,0),0)"])
nl=len(G)+1
w=wb.create_sheet('Services'); w.append(['Date','Service','Mois','Places','Couverts','Occupation (%)','Au-delà de 100 % (1 = oui)'])
sv=S92[['date','service']].copy(); sv['m']=sv.date.str[5:7].astype(int)
for i,r in enumerate(sv.itertuples(),start=2):
    w.append([r.date,r.service,r.m,48 if r.m in (5,6,7,8) else 46,f"=SUMIFS(Lignes!$E$2:$E${nl},Lignes!$A$2:$A${nl},A{i},Lignes!$B$2:$B${nl},B{i})",f"=E{i}/D{i}*100",f"=IF(F{i}>100,1,0)"])
ns=len(sv)+1
w=wb.create_sheet('Synthèse')
rows=[('Services',f"=COUNTA(Services!A2:A{ns})"),('Couverts',f"=SUM(Services!E2:E{ns})"),('Couverts par service',f"=B3/B2"),
 ('Occupation moyenne (moyenne des taux, %)',f"=AVERAGE(Services!F2:F{ns})"),('Occupation (rapport des sommes, %)',f"=SUM(Services!E2:E{ns})/SUM(Services!D2:D{ns})*100"),
 ('Services au-delà de 100 %',f"=SUM(Services!G2:G{ns})"),('Occupation maximale (%)',f"=MAX(Services!F2:F{ns})"),('Écart au repère de 58 % (points)',"=B5-58"),
 ('Occupation intérieur (%)',f'=AVERAGEIF(Services!D2:D{ns},46,Services!F2:F{ns})'),('Occupation terrasse (%)',f'=AVERAGEIF(Services!D2:D{ns},48,Services!F2:F{ns})'),
 ('Libellés comptés',f"=SUM(Libellés!G2:G{nlib})")]
w.append(['Indicateur','Valeur'])
for a,b in rows: w.append([a,b])
wb.save(PC+'173-travail-libelles-couverts.xlsx')
# ---------- 174
D=E[E.typEven=='DEL']; Dm=D.groupby(['dateEven','heureEven']).agg(n=('ac','size'),s=('amount','sum'),mx=('amount','max')).reset_index()
Fr=F.merge(S.drop_duplicates(['id','mod_regl','montant'])[['id']].drop_duplicates(),on='id',how='left')
e9=set(S[S.etat.astype(str)=='9'].id)
Hh=H.sort_values(['date_ticket','heure_ticket','id']).reset_index(drop=True)
wb=openpyxl.Workbook(); ws=wb.active; ws.title='Lisez-moi'
for i,t in enumerate(['Version de travail : annexe 174, passerelle des populations de la section 2.7, par formules sur les annexes C, H, E, F.',
  'Sources (SHA-256) : '+' ; '.join(f'{k} {v[:16]}…' for k,v in SH.items()),
  'Onglets source (valeurs, en bleu) : H (19 903 tickets, triés par date, heure, id), C_ids (16 624 identifiants de l annexe C), DEL_minutes (6 579 minutes de lignes DEL : nombre, somme, maximum, calculés sur l annexe E), F (19 334 lignes de règlement ; colonne etat de l export natif).',
  'Onglet H, colonnes calculées : lignes C (NB.SI), DEL à la même minute (NB.SI.ENS), sans article, nouvelle minute (pour le décompte des minutes), règlements (SOMME.SI), état 9.',
  'Onglet Passerelle : chaque chiffre du texte par formule. Construction définitive après la clôture du débat. Aucune affirmation sur le certificat de caisse.']):
    ws.cell(i+1,1,t)
w=wb.create_sheet('C_ids'); w.append(['Id (annexe C)'])
for i in sorted(A.id): w.append([int(i)])
nC=A.id.nunique()+1
w=wb.create_sheet('DEL_minutes'); w.append(['Date','Heure','Lignes DEL','Somme','Ligne la plus forte'])
for r in Dm.itertuples(): w.append([r.dateEven,r.heureEven,int(r.n),round(r.s,2),round(r.mx,2)])
nD=len(Dm)+1
w=wb.create_sheet('F'); w.append(['Id','Mode','Montant','État (export natif)'])
for r in F.itertuples(): w.append([int(r.id),r.mod_regl,round(r.montant,2),9 if r.id in e9 else 0])
nF=len(F)+1
w=wb.create_sheet('H'); w.append(['Id','Date','Heure','N°','Z','Exercice','TTC','tot_sum','Lignes C','Sans article (1 = oui)','Lignes DEL à la minute','Sans article à la minute d un DEL','Nouvelle minute','Minute écartée (somme ≤ 0 ou ligne ≥ 1 000 €)','Règlements F','État 9','Série (1 = tot_sum ≥ 100 000)'])
for i,r in enumerate(Hh.itertuples(),start=2):
    w.append([int(r.id),r.date_ticket,r.heure_ticket,int(r.no_ticket),int(r.no_z_report),r.ex,round(r.tot_ttc,2),round(r.tot_sum,2),
      f"=COUNTIF(C_ids!$A$2:$A${nC},A{i})",f"=IF(I{i}=0,1,0)",f"=COUNTIFS(DEL_minutes!$A$2:$A${nD},B{i},DEL_minutes!$B$2:$B${nD},C{i})",
      f"=IF(AND(J{i}=1,K{i}>0),1,0)",f"=IF(L{i}=1,IF(COUNTIFS(B$1:B{i-1},B{i},C$1:C{i-1},C{i},L$1:L{i-1},1)=0,1,0),0)" if i>2 else f"=L{i}",
      f"=IF(M{i}=1,IF(OR(SUMIFS(DEL_minutes!$D$2:$D${nD},DEL_minutes!$A$2:$A${nD},B{i},DEL_minutes!$B$2:$B${nD},C{i})<=0,SUMIFS(DEL_minutes!$E$2:$E${nD},DEL_minutes!$A$2:$A${nD},B{i},DEL_minutes!$B$2:$B${nD},C{i})>=1000),1,0),0)",
      f"=SUMIF(F!$A$2:$A${nF},A{i},F!$C$2:$C${nF})",f"=IF(COUNTIFS(F!$A$2:$A${nF},A{i},F!$D$2:$D${nF},9)>0,1,0)",f"=IF(H{i}>=100000,1,2)"])
nH=len(Hh)+1
w=wb.create_sheet('Passerelle'); w.append(['Grandeur','Valeur (formule)','Texte de la section 2.7'])
R=f'H!$%s$2:$%s${nH}'
def rg(c): return R%(c,c)
items=[('Tickets des annexes H',f'=COUNTA({rg("A")})','19 903'),
 ('dont 2022-2023',f'=COUNTIF({rg("F")},"2022-2023")','6 848'),('dont 2023-2024',f'=COUNTIF({rg("F")},"2023-2024")','6 630'),('dont 2024-2025',f'=COUNTIF({rg("F")},"2024-2025")','6 425'),
 ('Tickets à 0,00 €',f'=COUNTIF({rg("G")},0)','3 281'),('Tickets sans article',f'=SUM({rg("J")})','3 279'),('Tickets à 0,00 € portant des lignes C (3 281 − 3 279)',f'=COUNTIFS({rg("G")},0,{rg("J")},0)','2'),
 ('Tickets non nuls sans ligne C',f'=COUNTIFS({rg("G")},"<>0",{rg("J")},1)','0 (« aucun ticket non nul de H absent de C »)'),
 ('Additions de l annexe C (identifiants)',f'=COUNTA(C_ids!A2:A{nC})','16 624'),
 ('Sans article à la minute d un DEL',f'=SUM({rg("L")})','2 449'),('Minutes correspondantes',f'=SUM({rg("M")})','2 362'),
 ('Minutes écartées (somme ≤ 0 ou ligne ≥ 1 000 €)',f'=SUM({rg("N")})','3'),('Tables vidées du lot 2.2 (minutes retenues)','=B12-B13','2 359'),
 ('Montant des minutes retenues',f'=SUMPRODUCT(({rg("M")}=1)*({rg("N")}=0)*SUMIFS(DEL_minutes!$D$2:$D${nD},DEL_minutes!$A$2:$A${nD},{rg("B")},DEL_minutes!$B$2:$B${nD},{rg("C")}))','180 003,94 €'),
 ('Sans article sans DEL à la minute','=B7-B11','830'),
 ('Tickets sans article portant des règlements',f'=COUNTIFS({rg("J")},1,{rg("O")},"<>0")','37'),('Montant de ces règlements',f'=SUMIFS({rg("O")},{rg("J")},1)','1 958,26 €'),
 ('dont tickets portant l état 9',f'=SUM({rg("P")})','37'),
 ('Lignes DEL',f'=SUM(DEL_minutes!C2:C{nD})','21 302'),('Montant DEL',f'=SUM(DEL_minutes!D2:D{nD})','430 763,15 €'),
 ('N° de note entre 101 et 126 (annexes H)',f'=COUNTIFS({rg("D")},">=101",{rg("D")},"<=126")','0 (« numéros de terrasse apparus »)'),
 ('Tickets non nuls de la seconde série',f'=COUNTIFS({rg("Q")},2,{rg("G")},"<>0")','17')]
for a,b,c in items: w.append([a,b,c])
wb.save(PC+'174-travail-passerelle.xlsx')
print('écrit')
