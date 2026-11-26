"""Mission 4 : construit 169-R2 (export natif des règlements : colonnes retirées, sy_uk, etat ; identité avec F ; concordance C / H).
Sources : SOURCE-reglement-brut_2022-2025.xls (cache SOURCE.pkl, s07), annexes F-1 à F-3 (F.pkl), annexes C-1 à C-3 (lot23 CC.pkl), annexes H-1 à H-3 (H.pkl).
Mesures d'origine : s07, t01 (B-2), v01 (C10-3, C10-4)."""
import sys, json; sys.path.insert(0,'scripts/lot5-tva')
import pandas as pd
from pieces_common import cell, header, methode, check_dash, wb, EUR, INT
CA='scripts/lot6-evenement-reglement/cache/'; FN='public/documents/pieces-lot6/169-R2-export-natif-reglements-colonnes-retirees-sy_uk-etat.xlsx'
S=pd.read_pickle(CA+'SOURCE.pkl').reset_index(drop=True); F=pd.read_pickle(CA+'F.pkl').reset_index(drop=True); H=pd.read_pickle(CA+'H.pkl').reset_index(drop=True)
C=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/CC.pkl'); Cn=C.drop_duplicates('id').reset_index(drop=True)
FCOLS=['dateTicket','heureTicket','no_ticket','dat_z','no_zReport','tot_ttc','tot_tva','tot_remGlobale','id','mod_regl','montant']
MAP={'date_ticket':'dateTicket','heure_ticket':'heureTicket','no_ticket':'no_ticket','dat_z':'dat_z','no_z_report':'no_zReport','tot_ttc':'tot_ttc','tot_tva':'tot_tva','tot_rem_globale':'tot_remGlobale','id':'id','mod_regl':'mod_regl','montant':'montant'}
w=wb(); EXP={}
M=['169-R2. Export natif des règlements de la caisse : colonnes retirées par le service (dont sy_uk et etat), identité avec les annexes F, concordance des annexes C et H',
 'Sources : fichier SpreadsheetML SOURCE-reglement-brut_2022-2025.xls (19 334 lignes, 22 colonnes, lu tel quel) ; annexes F-1 à F-3 du service (19 334 lignes, 11 colonnes) ; annexes C-1 à C-3 (en-tête de note de la première ligne de chaque note, 16 624 notes) ; annexes H-1 à H-3 (19 903 notes). Ce classeur : scripts/b5_A3.py ; mesures d\'origine : s07, t01, v01.',
 '§ Conventions',
 'sy_uk compte 18 chiffres, au-delà de la précision d\'un nombre de tableur : il est porté en texte (colonne d\'origine) et en deux nombres exacts de 9 chiffres (partie haute, partie basse), sur lesquels portent les formules.',
 'Identité avec F : pour chaque ligne, dans l\'ordre des fichiers (F-1, F-2, F-3 bout à bout), égalité de l\'identifiant, de la date, de l\'heure, du numéro, du Z, du mode, du montant et du total TTC.',
 'Concordance C / H : pour chaque note de l\'annexe C, recherche de son identifiant dans l\'annexe H et égalité de la date, de l\'heure, du numéro, du Z, de la date du Z et du total TTC.',
 'Le détail des 55 lignes « etat = 9 » (37 notes, 1 958,26 €) est à l\'annexe 165 et à l\'annexe 171, onglet « Etat 9 ».']
check_dash(M); methode(w,M)
SY=w.create_sheet('Synthèse')
wc=w.create_sheet('Colonnes'); header(wc,['n°','colonne de l\'export natif','colonne de l\'annexe F','retirée par le service (1/0)'],[5,18,18,12])
for j,cn in enumerate(S.columns,1):
    k=1+j; wc.append([j,cn,MAP.get(cn),f'=IF(ISBLANK(C{k}),1,0)'])
wl=w.create_sheet('Identité F'); N=len(S)
cols=['ligne','id (natif)','sy_uk (texte)','sy_uk partie haute','sy_uk partie basse','etat','mode (natif)','montant (natif)','tot_ttc (natif)','date (natif)','heure (natif)','n° (natif)','Z (natif)',
      'id (F)','mode (F)','montant (F)','tot_ttc (F)','date (F)','heure (F)','n° (F)','Z (F)','identité de la ligne (1/0)']
header(wl,cols,[6,8,20,11,11,5,6,9,9,11,6,5,6,8,6,9,9,11,6,5,6,8])
for i in range(N):
    s=S.iloc[i]; f=F.iloc[i]; k=2+i; u=str(s.sy_uk)
    wl.append([i+1,int(s.id),u,int(u[:9]),int(u[9:]),int(s.etat),s.mod_regl,round(float(s.montant),2),round(float(s.tot_ttc),2),s.date_ticket,s.heure_ticket,int(s.no_ticket),int(s.no_z_report),
               int(f.id),f.mod_regl,f.montant_c/100,f.tot_ttc_c/100,f.dateTicket,f.heureTicket,int(f.no_ticket),int(f.no_zReport),
               f'=IF(AND(B{k}=N{k},G{k}=O{k},ROUND(H{k}-P{k},2)=0,ROUND(I{k}-Q{k},2)=0,J{k}=R{k},K{k}=S{k},L{k}=T{k},M{k}=U{k}),1,0)'])
RL=lambda c:f"'Identité F'!${c}$2:${c}${1+N}"
U=S.drop_duplicates('id').sort_values('id').reset_index(drop=True); NU=len(U)
wu=w.create_sheet('sy_uk'); header(wu,['id','sy_uk (texte)','partie haute','partie basse','lignes de cet id','lignes de ce sy_uk','lignes de cet id et de ce sy_uk','notes de ce sy_uk (dans cet onglet)','croissant avec id (1/0)'],[8,20,11,11,8,8,8,8,8])
for i,x in U.iterrows():
    k=2+i; u=str(x.sy_uk)
    wu.append([int(x.id),u,int(u[:9]),int(u[9:]),f'=COUNTIF({RL("B")},A{k})',f'=COUNTIFS({RL("D")},C{k},{RL("E")},D{k})',f'=COUNTIFS({RL("B")},A{k},{RL("D")},C{k},{RL("E")},D{k})',
               f'=COUNTIFS($C$2:$C${1+NU},C{k},$D$2:$D${1+NU},D{k})',(f'=IF(OR(C{k}>C{k-1},AND(C{k}=C{k-1},D{k}>D{k-1})),1,0)' if k>2 else 1)])
RU=lambda c:f"sy_uk!${c}$2:${c}${1+NU}"
wx=w.create_sheet('etat'); header(wx,['valeur de etat','lignes','montant (€)','notes (premières lignes)'],[12,10,12,12])
for v in [0,9]: wx.append([v,f'=COUNTIF({RL("F")},{v})',f'=SUMIF({RL("F")},{v},{RL("H")})',f'=SUMPRODUCT(({RL("F")}={v})*({RL("B")}<>OFFSET({RL("B")},-1,0)))'])
wh=w.create_sheet('Sources_H'); NH=len(H)
header(wh,['id','date','heure','n°','date du Z','Z','tot_ttc','série'],[8,11,6,5,11,6,9,5])
for x in H.itertuples(): wh.append([int(x.id),x.date_ticket,x.heure_ticket,int(x.no_ticket),x.dat_z,int(x.no_z_report),x.tot_ttc_c/100,int(x.serie)])
wn=w.create_sheet('Concordance C-H'); NC=len(Cn)
header(wn,['id (C)','date','heure','n°','date du Z','Z','tot_ttc','rang dans H','concordance (1/0)'],[8,11,6,5,11,6,9,8,8])
for i,x in Cn.iterrows():
    k=2+i; R=f'Sources_H!$A$2:$A${1+NH}'
    def ix(c): return f'INDEX(Sources_H!${c}$2:${c}${1+NH},H{k})'
    wn.append([int(x.id),x.date,x.heure,int(x.ticket),x.datz,int(x.z),round(float(x.tot_ttc),2),f'=MATCH(A{k},{R},0)',
               f'=IF(AND(B{k}={ix("B")},C{k}={ix("C")},D{k}={ix("D")},E{k}={ix("E")},F{k}={ix("F")},ROUND(G{k}-{ix("G")},2)=0),1,0)'])
RN=lambda c:f"'Concordance C-H'!${c}$2:${c}${1+NC}"
SY.column_dimensions['A'].width=85; SY.column_dimensions['B'].width=16; SY.column_dimensions['C'].width=16
SY.append([cell(SY,'Synthèse : chaque chiffre est une formule ; colonne C, chiffre cité par la section 2.6',bold=True)])
it=[('Colonnes de l\'export natif','=COUNTA(Colonnes!$B$2:$B$23)',22),('Colonnes de l\'annexe F','=COUNTA(Colonnes!$C$2:$C$23)',11),('Colonnes retirées par le service','=SUM(Colonnes!$D$2:$D$23)',11),
 ('sy_uk retirée (1 = oui)','=SUMIF(Colonnes!$B$2:$B$23,"sy_uk",Colonnes!$D$2:$D$23)',1),('etat retirée (1 = oui)','=SUMIF(Colonnes!$B$2:$B$23,"etat",Colonnes!$D$2:$D$23)',1),
 ('Lignes de l\'export natif',f'=COUNT({RL("A")})',19334),('Lignes identiques à F, ligne à ligne',f'=SUM({RL("V")})',19334),
 ('Lignes à etat = 9',f'=COUNTIF({RL("F")},9)',55),('Lignes à etat = 0',f'=COUNTIF({RL("F")},0)',19279),('Montant des lignes à etat = 9 (€)',f'=SUMIF({RL("F")},9,{RL("H")})',1958.26),
 ('Notes distinctes de l\'export (id)',f'=COUNT({RU("A")})',16642),('Valeurs distinctes de sy_uk',f'=SUMPRODUCT(1/{RU("H")})',16642),
 ('Notes dont toutes les lignes portent un seul sy_uk, propre à la note (bijection)',f'=SUMPRODUCT(({RU("E")}={RU("F")})*({RU("F")}={RU("G")})*({RU("H")}=1))',16642),
 ('Notes dont sy_uk croît avec l\'identifiant',f'=SUM({RU("I")})',16642),
 ('Notes de l\'annexe C',f'=COUNT({RN("A")})',16624),('Notes de C concordantes avec H (date, heure, n°, date du Z, Z, total TTC)',f'=SUM({RN("I")})',16624)]
for j,(a,f,e) in enumerate(it):
    k=2+j; SY.append([a,cell(SY,f,fmt=EUR if isinstance(e,float) else INT),str(e).replace('.',',')]); EXP[f'B{k}']=e
w.save(FN); json.dump({'file':FN,'sheet':'Synthèse','exp':EXP},open('scripts/lot6-evenement-reglement/out/.exp_A3.json','w'),ensure_ascii=False); print('écrit',FN,len(EXP))
