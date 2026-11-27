"""C-2 : (1) écart comptable contre règlements état 9 ; (2) règlements F de première série contre notes, journée par journée ;
(3) version de travail de l'annexe 172 (pointage) ; (4) ordre de grandeur des droits. Sorties : out/B2/03.txt, pieces/172-travail-pointage-37-tickets.xlsx"""
import sys; sys.path.insert(0,"scripts/lot7-tables-virtuelles")
from B2_common import *
C,E,F,H,A=load(); S=source(); S['id']=S.id.astype(int); p=out2('03.txt')
F['mc']=(F.montant*100).round().astype(int)
CA=sheet(F156,'CA_comptable'); p('(1) 156-R3, onglet CA_comptable (comptes de la proposition, p. 26) :'); p(CA.to_string())
ec={'2022-2023':6241,'2023-2024':6773,'2024-2025':4049}; e9={'2022-2023':3245,'2023-2024':160738,'2024-2025':31843}
for e in ec: p(f'   {e} : écart {ec[e]/100:.2f} € ; état 9 {e9[e]/100:.2f} € ; l écart {"peut" if ec[e]>=e9[e] else "ne peut pas"} contenir les règlements état 9 (manque au moins {max(0,e9[e]-ec[e])/100:.2f} €)')
# (2) par journée
n1=H[(H.serie==1)&(H.tc!=0)]; tot_n=n1.groupby('date_ticket').tc.sum()
st=set(S[S.etat.astype(str)=='9'].id)
F['e9']=F.id.isin(st)
fd=F[~F.e9].groupby('dateTicket').mc.sum(); f9=F[F.e9].groupby('dateTicket').mc.sum()
J=pd.DataFrame({'notes':tot_n,'F_hors9':fd,'F9':f9}).fillna(0).astype(int)
J['F_tout']=J.F_hors9+J.F9
eq=(J.notes==J.F_tout); p(f'(2) journées : {len(J)} ; règlements F (toutes lignes) = notes de première série au centime : {int(eq.sum())} ; autres : {int((~eq).sum())}')
oth=J[~eq]; p(f'    pour ces journées, écart F − notes = règlements état 9 du jour : {int((oth.F_tout-oth.notes==oth.F9).sum())} / {len(oth)} ; journées avec état 9 : {int((J.F9>0).sum())}')
p(f'    règlements F hors état 9 = notes : {int((J.F_hors9==J.notes).sum())} / {len(J)}')
d='2022-09-09'; p(f'    09/09/2022 : tickets à 0,00 € porteurs de règlements {int(F[(F.dateTicket==d)&F.e9].id.nunique())} ; F {J.loc[d,"F_tout"]/100:.2f} € ; notes {J.loc[d,"notes"]/100:.2f} €')
# (3) version de travail 172
days37=sorted(F[F.e9].dateTicket.unique())
rows=[]
for day in days37:
    z=int(H[H.date_ticket==day].no_z_report.mode()[0])
    r={'Date':day,'Ticket Z':z}
    for m,lab in [('CB','CB'),('TR','TR'),('CHV','CHV'),('ESP','ESP')]:
        s=F[(F.dateTicket==day)&(F.mod_regl==m)&~F.e9].mc.sum()/100; s9=F[(F.dateTicket==day)&(F.mod_regl==m)&F.e9].mc.sum()/100
        r[f'{lab} première série']=s; r[f'{lab} état 9']=s9; r[f'{lab} total sans']=s; r[f'{lab} total avec']=round(s+s9,2)
    rows.append(r)
P=pd.DataFrame(rows); p(f'(3) version de travail 172 : {len(P)} journées (37 tickets sur {len(days37)} dates)')
with pd.ExcelWriter('scripts/lot7-tables-virtuelles/out/pieces/172-travail-pointage-37-tickets.xlsx',engine='openpyxl') as xw:
    pd.DataFrame({'Lisez-moi':[
     'Version de travail : annexe 172, pointage des 37 tickets à 0,00 € porteurs de règlements (état 9).',
     'Sources : annexes F-1 à F-3 (règlements), export natif des règlements (colonne etat), annexes H-1 à H-3 (date, ticket Z). Script : scripts/B2_03_C2_pointage.py.',
     'Une ligne par journée portant au moins une ligne état 9. Pour chaque mode : total de la première série (hors état 9), total état 9, total « sans » et total « avec ».',
     'Colonnes à remplir par la cliente : remise TPE du jour (relevé du terminal ou de la banque), bordereau CRT (titres-restaurant), bordereau ANCV (chèques-vacances), espèces remises.',
     'Verdict (formule) : « sans » si la remise égale le total sans état 9 ; « avec » si elle égale le total avec ; « autre » sinon ; vide tant que la remise n est pas saisie.',
     'Aucune affirmation n est faite sur le certificat de caisse.']}).to_excel(xw,sheet_name='Lisez-moi',index=False)
    P.to_excel(xw,sheet_name='Pointage',index=False)
import openpyxl
wb=openpyxl.load_workbook('scripts/lot7-tables-virtuelles/out/pieces/172-travail-pointage-37-tickets.xlsx'); ws=wb['Pointage']
nc=ws.max_column
for j,h in enumerate(['Remise TPE du jour (à remplir)','Bordereau CRT (à remplir)','Bordereau ANCV (à remplir)','Verdict CB (formule)'],start=nc+1): ws.cell(1,j,h)
from openpyxl.utils import get_column_letter as L_
hdr=[c.value for c in ws[1]]; csans=L_(hdr.index('CB total sans')+1); cavec=L_(hdr.index('CB total avec')+1); crem=L_(nc+1)
for r in range(2,ws.max_row+1):
    ws.cell(r,nc+4,f'=IF({crem}{r}="","",IF(ABS({crem}{r}-{csans}{r})<0.005,"sans",IF(ABS({crem}{r}-{cavec}{r})<0.005,"avec","autre")))')
wb.save('scripts/lot7-tables-virtuelles/out/pieces/172-travail-pointage-37-tickets.xlsx')
# (4) droits
for lab,ttc in [('1 958,26 €',195826),('1 504,92 € (hors 7 lignes de double possible)',150492)]:
    for r in (10,20):
        ht=ttc/(1+r/100); p(f'(4) {lab} au taux de {r} % : HT {ht/100:.2f} € ; TVA {(ttc-ht)/100:.2f} € ; HT / base rectifiée 421 899 € = {ht/100/421899*100:.3f} % ; TTC / CA de caisse 1 276 191,20 € = {ttc/100/1276191.20*100:.3f} %')
# taux moyen des notes de première série des journées concernées (annexes H : tot_tva / (tot_ttc - tot_tva))
n=H[(H.serie==1)&(H.tc!=0)&H.date_ticket.isin(days37)]; tx=n.tot_tva.sum()/(n.tot_ttc.sum()-n.tot_tva.sum())
p(f'    taux moyen des notes des journées concernées (H) : {tx*100:.2f} % ; appliqué à 1 958,26 € : TVA {1958.26*tx/(1+tx):.2f} €, HT {1958.26/(1+tx):.2f} € ; à 1 504,92 € : TVA {1504.92*tx/(1+tx):.2f} €')
