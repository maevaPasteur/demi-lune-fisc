"""B4 : construit 163 (étalons, bases, rappel autonome, reconstitution, base HT et IS, errata des CSV 36 à 41).
Sources : annexes G-1 à G-3 (loadG), proposition p. 26, 53, 54 et annexes 7 (OCR et scan), 162 (TVA légale)."""
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import json
from common import *
from pieces_common import *
T=pd.read_pickle(CA+'B5_tickets.pkl')
EXP={}; w=wb()
M=['163. Étalons de la TVA et du chiffre d\'affaires, bases HT, rappel autonome, reconstitution du service, base HT et IS, errata des pièces CSV',
 'Sources : annexes G-1 à G-3 (journal de TVA, onglet « Journal G », 29 588 lignes) ; proposition de rectification, p. 26 (comptes 706000, 706300, 706800, 445710), p. 53 (TVA reconstituée, rappel, bases HT rehaussées) et annexes 7 (Proposition_3_Annexes_Boissons.pdf) ; 162, onglet « Synthèse » (TVA légalement due). Scripts : b1_b7_b8_b14.py, b2_reconstitution_reglements.py, c1_materialite.py ; ce classeur : b4_piece3.py.',
 '§ Conventions',
 'Les cellules en entrée (comptes de la p. 26, données de la p. 53, lignes des annexes 7, TVA légale de 162) sont des valeurs avec leur source ; tout le reste est formule.',
 'TVA liquidée : Σ tax_amount du journal G par taux. Base HT de la caisse : palier TTC − tax_amount, le palier valant VAT_base + taux lu en euros (161, onglet « Paliers lignes G »).',
 'TVA légalement due : 162 (articles au taux légal, arrondi de la caisse par palier ; indéterminés au taux appliqué).',
 'Reconstitution : la TVA reconstituée 2022-2023 est lue sur l\'annexe 7-1 (p. 58 de l\'annexe) ; pour 2023-2024 et 2024-2025, la décomposition liquides / solides est reconstituée à partir des lignes de réduction de 5 % imprimées, et signalée comme reconstituée.']
check_dash(M); methode(w,M)
wE=w.create_sheet('Étalons'); wB=w.create_sheet('Bases'); wR=w.create_sheet('Rappel autonome'); wC=w.create_sheet('Reconstitution'); wI=w.create_sheet('Base HT et IS'); wX=w.create_sheet('Errata CSV')
# ---------- Journal G
G=loadG(); G['r']=G['taux_tva%'].astype(int); G=G.sort_values(['ex','rowG']).reset_index(drop=True)
G['first']=(~G.duplicated('tk')).astype(int); NG=len(G)
wg=w.create_sheet('Journal G')
header(wg,['exercice','ligne G (rowG)','date','heure','n° ticket','Z','taux','VAT_base','tax_amount','tot_ttc','première ligne du ticket','palier TTC = VAT_base + taux','base HT caisse = palier − tax_amount','TTC du ticket compté une fois'],[10,8,11,7,7,6,6,10,10,10,7,11,11,11])
for i,r in G.iterrows():
    k=2+i; wg.append([r.ex,int(r.rowG),r.dateTicket,r.heureTicket,int(r.noTicket),int(r.no_zReport),int(r.r),r.VAT_base_c/100,r.tax_amount_c/100,r.tot_ttc_c/100,int(r["first"]),f'=H{k}+G{k}',f'=L{k}-I{k}',f'=IF(K{k}=1,J{k},0)'])
GR=lambda col: f"'Journal G'!${col}$2:${col}${1+NG}"
ex_=lambda e:f'"{e}"'
def sheet_line(ws,row,lab,fs,cum=None,fmt=EUR,exp=None,src=None):
    row[0]+=1; k=row[0]
    ws.append([lab]+[cell(ws,f,fmt=fmt) for f in fs]+[cell(ws,cum if cum is not None else f'=SUM(B{k}:D{k})',fmt=fmt),src])
    if exp:
        for cl,v in zip('BCDE',exp):
            if v is not None: EXP[(ws.title,f'{cl}{k}')]=v
    return k
def head(ws,title,cols=('Grandeur (€)','Ex. 31/03/2023','Ex. 31/03/2024','Ex. 31/03/2025','Cumul 3 ex.','Source')):
    ws.column_dimensions['A'].width=72
    for cl in 'BCDE': ws.column_dimensions[cl].width=15
    ws.column_dimensions['F'].width=60
    ws.append([cell(ws,title,bold=True)]); ws.append([cell(ws,h,bold=True,fill=True) for h in cols])
# ---------- Étalons : entrées p. 26 puis T46, T48
row=[0]; head(wE,'Comptes de la proposition, p. 26 (entrées)'); row[0]=2
k706=sheet_line(wE,row,'706000 Restaurant 20 %',P26['706000'],src='proposition, p. 26')
k7063=sheet_line(wE,row,'706300 Restaurant 10 %',P26['706300'],src='proposition, p. 26')
k7068=sheet_line(wE,row,'706800 Pourboire',P26['706800'],src='proposition, p. 26')
k445=sheet_line(wE,row,'445710 TVA collectée',P26['445710'],src='proposition, p. 26',exp=[42614.45,46464.79,46005.45,135084.69])
kTOT=sheet_line(wE,row,'Total chiffre d\'affaires TTC imprimé',P26['TOT'],src='proposition, p. 26')
ksum=sheet_line(wE,row,'Somme des quatre comptes',[f'={c}{k706}+{c}{k7063}+{c}{k7068}+{c}{k445}' for c in 'BCD'],src='formule')
sheet_line(wE,row,'Total imprimé − somme des comptes (anomalie de la p. 26)',[f'=ROUND({c}{kTOT}-{c}{ksum},2)' for c in 'BCD'],exp=[0,0.03,0,0.03],src='formule ; seule l\'année 2023-2024 diffère, de 0,03 €')
wE.append([]); row[0]+=1
wE.append([cell(wE,'Tableau 46. Rapprochement de la TVA, périmètre par périmètre',bold=True)]); row[0]+=1
k10=sheet_line(wE,row,'TVA liquidée, caisse, 10 % (tax_amount)',[f'=SUMIFS({GR("I")},{GR("A")},{ex_(e)},{GR("G")},10)' for e in EX],exp=[29611.10,31917.44,31852.20,93380.74],src='Journal G')
k20=sheet_line(wE,row,'TVA liquidée, caisse, 20 % (tax_amount)',[f'=SUMIFS({GR("I")},{GR("A")},{ex_(e)},{GR("G")},20)' for e in EX],exp=[12941.66,14482.64,14074.43,41498.73],src='Journal G')
kliq=sheet_line(wE,row,'Sous-total TVA liquidée (10 % + 20 %)',[f'={c}{k10}+{c}{k20}' for c in 'BCD'],exp=[42552.76,46400.08,45926.63,134879.47])
kt10=sheet_line(wE,row,'TVA théorique, base 706300 × 10 %',[f'=ROUND({c}{k7063}*0.1,2)' for c in 'BCD'],exp=[29610.59,31917.93,31834.54,93363.06])
kt20=sheet_line(wE,row,'TVA théorique, base 706000 × 20 %',[f'=ROUND({c}{k706}*0.2,2)' for c in 'BCD'],exp=[12942.50,14483.31,14103.49,41529.30])
kth=sheet_line(wE,row,'Sous-total TVA théorique (10 % + 20 %)',[f'={c}{kt10}+{c}{kt20}' for c in 'BCD'],exp=[42553.09,46401.24,45938.03,134892.36])
sheet_line(wE,row,'Écart à périmètre égal (liquidée − théorique)',[f'={c}{kliq}-{c}{kth}' for c in 'BCD'],exp=[-0.33,-1.16,-11.40,-12.89])
sheet_line(wE,row,'TVA collectée comptabilisée (445710)',[f'={c}{k445}' for c in 'BCD'],exp=[42614.45,46464.79,46005.45,135084.69])
kexc=sheet_line(wE,row,'Excédent du 445710 hors ventilation 10/20',[f'={c}{k445}-{c}{kth}' for c in 'BCD'],exp=[61.36,63.55,67.42,192.33])
kpb=sheet_line(wE,row,'dont TVA à 10 % sur le compte 706800 « Pourboire », si les pourboires sont taxables',[f'=ROUND({c}{k7068}*0.1,2)' for c in 'BCD'],exp=[59.80,59.78,65.66,185.24])
sheet_line(wE,row,'dont reliquat',[f'={c}{kexc}-{c}{kpb}' for c in 'BCD'],exp=[1.56,3.77,1.76,7.09])
sheet_line(wE,row,'Écart brut 445710 − TVA liquidée (= 12,89 + 192,33)',[f'={c}{k445}-{c}{kliq}' for c in 'BCD'],exp=[61.69,64.71,78.82,205.22])
kleg=sheet_line(wE,row,'TVA légalement due, articles au taux légal (entrée : 162, « Synthèse », ligne 23)',[T.loc[e].leg.sum()/100 for e in EX],exp=[42770.29,46606.01,46152.80,135529.10],src='162, onglet « Synthèse »')
kaut=sheet_line(wE,row,'445710 − TVA légalement due',[f'={c}{k445}-{c}{kleg}' for c in 'BCD'],exp=[-155.84,-141.22,-147.35,-444.41])
kl20=sheet_line(wE,row,'TVA légale, indéterminés à 20 % (entrée : 162, « Synthèse », ligne 32)',[T.loc[e].l20.sum()/100 for e in EX],src='162, onglet « Synthèse »')
wE.append([]); row[0]+=1
wE.append([cell(wE,'Tableau 48. Chiffre d\'affaires TTC : tickets du journal de TVA contre comptabilité',bold=True)]); row[0]+=1
kttc=sheet_line(wE,row,'Σ TTC des tickets (annexes G)',[f'=SUMIFS({GR("N")},{GR("A")},{ex_(e)})' for e in EX],exp=[403370.42,437992.92,434827.86,1276191.20],src='Journal G')
kcpt=sheet_line(wE,row,'Comptabilité hors pourboire (706300 + 706000 + 445710)',[f'={c}{k7063}+{c}{k706}+{c}{k445}' for c in 'BCD'],exp=[403432.83,438060.65,434868.35,1276361.83])
kec=sheet_line(wE,row,'Écart compta − caisse',[f'={c}{kcpt}-{c}{kttc}' for c in 'BCD'],exp=[62.41,67.73,40.49,170.63])
k=sheet_line(wE,row,'En %',[f'={c}{kec}/{c}{kttc}' for c in 'BCD'],cum=f'=E{kec}/E{kttc}',fmt=PCT)
for cl,v in zip('BCDE',[0.015,0.015,0.009,0.013]): EXP[('Étalons',f'{cl}{k}')]=('pct3',v)
sheet_line(wE,row,'Pourboire 706800 (hors caisse)',[f'={c}{k7068}' for c in 'BCD'],exp=[598.04,597.75,656.57,1852.36])
# ---------- Bases (T47)
row=[0]; head(wB,'Tableau 47. Base d\'imposition par exercice et par taux',('Exercice','Taux','VAT_base (service)','Base HT de la caisse = palier TTC − tax_amount','Comptabilité (706300 / 706000)','Écart VAT_base − comptabilité','Écart caisse − comptabilité'))
for cl,wd in zip('ABCDEFG',[12,8,16,18,16,16,16]): wB.column_dimensions[cl].width=wd
exp47=[(269445.43,296104.33,296105.87,-26660.44,-1.54),(-11645.01,64713.33,64712.51,-76357.52,0.82),(296113.00,319175.56,319179.31,-23066.31,-3.75),(-1680.08,72417.28,72416.55,-74096.63,0.73),(296625.31,318523.11,318345.43,-21720.12,177.68),(572.55,70378.12,70517.47,-69944.92,-139.35)]
kB=[]
for j,e in enumerate(EX):
    for t,(rt,acc) in enumerate([(10,k7063),(20,k706)]):
        k=3+len(kB); kB.append(k); c='BCD'[j]
        wB.append([e,rt,cell(wB,f'=SUMIFS({GR("H")},{GR("A")},{ex_(e)},{GR("G")},{rt})',fmt=EUR),cell(wB,f'=SUMIFS({GR("M")},{GR("A")},{ex_(e)},{GR("G")},{rt})',fmt=EUR),cell(wB,f"='Étalons'!{c}{acc}",fmt=EUR),cell(wB,f'=C{k}-E{k}',fmt=EUR),cell(wB,f'=D{k}-E{k}',fmt=EUR)])
        for cl,v in zip('CDEFG',exp47[len(kB)-1]): EXP[('Bases',f'{cl}{k}')]=v
k=3+len(kB); wB.append(['Cumul 3 exercices','10 % + 20 %']+[cell(wB,f'=SUM({cl}3:{cl}{k-1})',fmt=EUR) for cl in 'CDEFG'])
for cl,v in zip('CDEFG',[849431.20,1141311.73,1141277.14,-291845.94,34.59]): EXP[('Bases',f'{cl}{k}')]=v
kBT=k
wB.append([]); wB.append(['Pour mémoire, par exercice : base HT de la caisse (10 % + 20 %) − comptabilité'])
k2=kBT+3
wB.append(['caisse − comptabilité','']+[cell(wB,f'=G{kB[2*j]}+G{kB[2*j+1]}',fmt=EUR) for j in range(3)]+[cell(wB,f'=SUM(C{k2}:E{k2})',fmt=EUR)])
for cl,v in zip('CDEF',[-0.72,-3.02,38.33,34.59]): EXP[('Bases',f'{cl}{k2}')]=v
# ---------- Rappel autonome (T57 quinquies)
row=[0]; head(wR,'Tableau 57 quinquies. Le rappel autonome contre le compte 445710 et son absorption par le rappel notifié'); row[0]=2
krec=sheet_line(wR,row,'TVA reconstituée (proposition, p. 53 ; entrée)',[63035.55,61318.80,60657.04],src='proposition, p. 53')
knot=sheet_line(wR,row,'Rappel notifié (TVA reconstituée − 445710, p. 53)',[f"={c}{krec}-'Étalons'!{c}{k445}" for c in 'BCD'],exp=[20421.10,14854.01,14651.59,49926.70])
sheet_line(wR,row,'dont TVA reconstituée − TVA légalement due des ventes de la caisse',[f"={c}{krec}-'Étalons'!{c}{kleg}" for c in 'BCD'],exp=[20265.26,14712.79,14504.24,49482.29])
kra=sheet_line(wR,row,'dont TVA légalement due − 445710 (rappel autonome)',[f"='Étalons'!{c}{kleg}-'Étalons'!{c}{k445}" for c in 'BCD'],exp=[155.84,141.22,147.35,444.41])
ki=sheet_line(wR,row,'Rappel autonome, références indéterminées à 20 %',[f"='Étalons'!{c}{kl20}-'Étalons'!{c}{k445}" for c in 'BCD'],exp=[175.80,213.34,234.48,623.62])
sheet_line(wR,row,'Rappel autonome, pourboires taxables à 10 %',[f"={c}{kra}+'Étalons'!{c}{kpb}" for c in 'BCD'],exp=[215.64,201.00,213.01,629.65])
sheet_line(wR,row,'Rappel autonome, les deux hypothèses',[f"={c}{ki}+'Étalons'!{c}{kpb}" for c in 'BCD'],exp=[235.60,273.12,300.14,808.86])
wR.append([]); row[0]+=1
wR.append([cell(wR,'Décomposition du rappel autonome',bold=True)]); row[0]+=1
sheet_line(wR,row,'effet de taux net (162, ligne 24 ; entrée)',[(T.loc[e].leg.sum()-T.loc[e].app.sum())/100 for e in EX],exp=[216.83,205.06,225.32,647.21],src='162, onglet « Synthèse »')
sheet_line(wR,row,'arrondi propre de la caisse (162, ligne 21 ; entrée)',[(T.loc[e].app.sum()-T.loc[e].tot_tva.sum())/100 for e in EX],exp=[0.70,0.87,0.85,2.42],src='162, onglet « Synthèse »')
sheet_line(wR,row,'TVA liquidée − 445710',[f"='Étalons'!{c}{kliq}-'Étalons'!{c}{k445}" for c in 'BCD'],exp=[-61.69,-64.71,-78.82,-205.22])
kd=row[0]
sheet_line(wR,row,'contrôle : somme des trois termes − rappel autonome',[f'=ROUND({c}{kd-2}+{c}{kd-1}+{c}{kd}-{c}{kra},2)' for c in 'BCD'],exp=[0,0,0,0])
# ---------- Reconstitution
wC.column_dimensions['A'].width=40
for cl,wd in zip('BCDEFG',[16,16,10,14,14,60]): wC.column_dimensions[cl].width=wd
wC.append([cell(wC,'Annexes 7 de la proposition : lignes des bières reconstituées (lues)',bold=True)])
wC.append([cell(wC,h,bold=True,fill=True) for h in ['Article','Exercice','TTC reconstitué','Taux','TVA lue','TVA = TTC / 6','Source (ligne de l\'OCR de Proposition_3_Annexes_Boissons, ou page)']])
rows=[('Pinte (50 cl)','2022-2023',3721.96,620.33,'OCR, ligne 2893'),('Panaché','2022-2023',740.28,123.38,'OCR, ligne 2711'),('Monaco','2022-2023',340.56,56.76,'OCR, ligne 2712'),
      ('Pinte (50 cl)','2023-2024',3218.83,536.47,'OCR, ligne 3922'),('Panaché','2023-2024',665.18,110.86,'OCR, ligne 3737'),('Monaco','2023-2024',357.76,59.63,'OCR, ligne 3738 (lu « 50,63 ») ; 59,63 lu sur le scan'),
      ('Pinte (50 cl)','2024-2025',3376.00,562.67,'annexes finales, p. 2 (lu sur le scan)'),('Panaché','2024-2025',558.60,93.10,'OCR, ligne 4723'),('Monaco','2024-2025',424.20,None,'OCR, ligne 4724 (TVA illisible à l\'OCR)')]
for i,(a,e,t,v,s) in enumerate(rows):
    k=3+i; wC.append([a,e,cell(wC,t,fmt=EUR),cell(wC,0.2,fmt='0.00%'),cell(wC,v,fmt=EUR),cell(wC,f'=ROUND(C{k}/6,2)',fmt=EUR),s])
    EXP[('Reconstitution',f'F{k}')]=round(t/6+1e-9,2)
wC.append([]); wC.append([cell(wC,'Décomposition de la TVA reconstituée : liquides à 20 % / 10 % selon l\'article, solides à 10 %',bold=True)])
wC.append([cell(wC,h,bold=True,fill=True) for h in ['Grandeur (€)','2022-2023','2023-2024','2024-2025','Statut','','Source']])
b=wC.max_row if hasattr(wC,'max_row') else None
base=3+len(rows)+3   # première ligne de données du second bloc
R={}
def rl(name,vals,statut,src,fmt=EUR):
    k=base+len(R); R[name]=k; wC.append([name]+[cell(wC,v,fmt=fmt) for v in vals]+[statut,'',src]); return k
rl('TTC reconstitué (p. 53)',[597265.42,577522.00,575252.68],'lu','proposition, p. 53')
rl('TVA reconstituée (p. 53)',[63035.55,61318.80,60657.04],'lu','proposition, p. 53')
rl('Réduction de 5 % du CA liquides, TTC (une des trois lignes REMISE, PERTES, CONSOMMATION DU PERSONNEL)',[8917.07,8450.72,8253.27],'lu','OCR lignes 2930-2932 (2022-2023), 3994-3996 (2023-2024) ; 2024-2025 repris de B2 (b2_reconstitution_reglements.py), absent de l\'OCR')
rl('TVA de cette réduction',[1324.68,1286.88,1242.14],'lu','idem')
k1=rl('CA liquides avant réductions = réduction / 5 %',[f'={c}{base+2}/0.05' for c in 'BCD'],'formule','')
k2=rl('CA liquides après les trois réductions',[f'={c}{k1}-3*{c}{base+2}' for c in 'BCD'],'formule','')
k3=rl('CA solides = TTC reconstitué − CA liquides',[f'={c}{base}-{c}{k2}' for c in 'BCD'],'formule','')
rl('rapport solides / liquides (coefficient de la reconstitution : 2,94 / 3,02 / 3,10)',[f'={c}{k3}/{c}{k2}' for c in 'BCD'],'formule','proposition (coefficients)',fmt='0.0000')
k5=rl('TVA des liquides lue (annexe 7-1, p. 58 de l\'annexe)',[22519.62,None,None],'lu (2022-2023 seulement)','annexe 7-1, p. 58 ; OCR ligne 2934')
k6=rl('TVA des solides à 10 % lue (annexe 7-1, p. 58 de l\'annexe)',[40515.93,None,None],'lu (2022-2023 seulement)','annexe 7-1, p. 58 ; OCR ligne 2959')
k7=rl('Somme lue (2022-2023)',[f'=B{k5}+B{k6}',None,None],'formule','')
EXP[('Reconstitution',f'B{k7}')]=63035.55
k8=rl('TVA des liquides reconstituée = TVA de la réduction / 5 % × 85 %',[f'={c}{base+3}/0.05*0.85' for c in 'BCD'],'reconstitué','')
k9=rl('TVA des solides reconstituée = CA solides / 11',[f'={c}{k3}/11' for c in 'BCD'],'reconstitué','')
k10=rl('Somme reconstituée − TVA reconstituée (p. 53)',[f'=ROUND({c}{k8}+{c}{k9}-{c}{base+1},2)' for c in 'BCD'],'reconstitué','écarts d\'arrondi')
for cl,v in zip('BCD',[-0.06,-0.04,-0.02]): EXP[('Reconstitution',f'{cl}{k10}')]=v
# ---------- Base HT et IS
row=[0]; head(wI,'Base HT comptabilisée − base HT légale (point 2.5.6 c ; tableau 57 quinquies, dernière ligne)'); row[0]=2
kc=sheet_line(wI,row,'Base HT comptabilisée (706000 + 706300)',[f"='Étalons'!{c}{k706}+'Étalons'!{c}{k7063}" for c in 'BCD'],exp=[360818.38,391595.86,388862.90,1141277.14])
kl=sheet_line(wI,row,'Base HT légale = Σ TTC des tickets − TVA légalement due',[f"='Étalons'!{c}{kttc}-'Étalons'!{c}{kleg}" for c in 'BCD'],exp=[360600.13,391386.91,388675.06,1140662.10])
kx=sheet_line(wI,row,'Base HT comptabilisée − base HT légale',[f'={c}{kc}-{c}{kl}' for c in 'BCD'],exp=[218.25,208.95,187.84,615.04])
ka=sheet_line(wI,row,'TVA légalement due − TVA liquidée (TVA non liquidée)',[f"='Étalons'!{c}{kleg}-'Étalons'!{c}{kliq}" for c in 'BCD'],exp=[217.53,205.93,226.17,649.63])
sheet_line(wI,row,'dont arrondi propre de la caisse',[f"='Rappel autonome'!{c}{kd-1}" for c in 'BCD'],exp=[0.70,0.87,0.85,2.42])
kh=sheet_line(wI,row,'Base HT de la caisse (Σ TTC − Σ tax_amount) − comptabilité',[f"='Étalons'!{c}{kttc}-'Étalons'!{c}{kliq}-{c}{kc}" for c in 'BCD'],exp=[-0.72,-3.02,38.33,34.59])
sheet_line(wI,row,'contrôle : TVA non liquidée − écart caisse − comptabilité − écart de base',[f'=ROUND({c}{ka}-{c}{kh}-{c}{kx},2)' for c in 'BCD'],exp=[0,0,0,0])
# ---------- Errata CSV
wX.column_dimensions['A'].width=10; wX.column_dimensions['B'].width=34; wX.column_dimensions['C'].width=44; wX.column_dimensions['D'].width=44; wX.column_dimensions['E'].width=50
wX.append([cell(wX,'Errata des pièces CSV 36 à 41 (contenu d\'origine inchangé ; corrections à lire avec les pièces)',bold=True)])
wX.append([cell(wX,h,bold=True,fill=True) for h in ['Pièce','Endroit','Texte ou valeur de la pièce','Correction','Justification']])
er=[('36','en-tête, colonnes 4 et 5','Colonne « base HT » du fichier (BUGGEE) ; TVA reellement encaissee (CORRECTE)','VAT_base (base HT d\'affichage, = palier TTC − taux) ; tax_amount (TVA liquidée par la caisse)','VAT_base suit une formule exacte (161, « Paliers lignes G ») ; « encaissée » remplacé par « liquidée »'),
 ('37','en-tête','Colonne « base HT » (BUGGEE) ; TVA encaissee (CORRECTE) ; Base correcte = TVA / taux','VAT_base ; tax_amount (TVA liquidée) ; base HT = palier − taxe','La base HT de la caisse est palier − tax_amount'),
 ('37','ligne 10 %, colonne 4','14,30','14,27 (= 15,70 − 1,43)','palier 10 % 15,70 € − taxe 1,43 €'),('37','ligne 20 %, colonne 4','4,35','4,33 (= 5,20 − 0,87)','palier 20 % 5,20 € − taxe 0,87 €'),('37','ligne TOTAL, colonne 4','18,65','18,60 (= 14,27 + 4,33)','HT du ticket : 20,90 − 2,30 = 18,60 €, déjà écrit dans le libellé de la ligne'),
 ('39','en-tête, colonne 7','CA TTC reellement encaisse','Σ TTC des tickets du journal G (tot_ttc)','les règlements sont dans F, non dans G'),
 ('40','en-tête, colonnes 2, 3 et 5','Base HT 10 % (= TVA/taux) ; Base HT 20 % (= TVA/taux) ; + TVA encaissee','base déduite de tax_amount (tax_amount / taux) ; + Σ tax_amount (TVA liquidée)','lecture de la pièce 40 conservée, intitulés précisés (tableau 53)'),
 ('41','en-tête, colonne 6','TVA encaissee (nous)','TVA liquidée (Σ tax_amount)','vocabulaire'),
 ('41','en-tête, colonne 9 et valeurs','Base HT (nous) : 360 819,30 / 391 587,60 / 388 894,15','base HT de la caisse = palier − tax_amount : 360 817,66 / 391 592,84 / 388 901,23 (onglet « Bases »)','la base « TVA / taux » n\'est pas la base de la caisse'),
 ('41','colonne 11 (Ecart base HT)','0,92 / −8,26 / 31,25 ; total 23,91','caisse − comptabilité : −0,72 / −3,02 / +38,33 ; total +34,59','onglet « Bases », dernière ligne ; le total 23,91 € n\'est plus invoqué (tableau 47 : 34,59 €)')]
for i,x in enumerate(er):
    wX.append(list(x))
    if x[0]=='37' and x[3].startswith('='): pass
# lignes de calcul de la pièce 37
wX.append([]); wX.append([cell(wX,'Calcul des bases corrigées de la pièce 37 (ticket n° 2 du 14/04/2022)',bold=True)])
k0=len(er)+5
wX.append(['','','palier TTC','tax_amount','base HT = palier − taxe'])
wX.append(['37','Ligne 10 %',cell(wX,15.70,fmt=EUR),cell(wX,1.43,fmt=EUR),cell(wX,f'=C{k0+1}-D{k0+1}',fmt=EUR)]); EXP[('Errata CSV',f'E{k0+1}')]=14.27
wX.append(['37','Ligne 20 %',cell(wX,5.20,fmt=EUR),cell(wX,0.87,fmt=EUR),cell(wX,f'=C{k0+2}-D{k0+2}',fmt=EUR)]); EXP[('Errata CSV',f'E{k0+2}')]=4.33
wX.append(['37','TOTAL ticket',cell(wX,f'=C{k0+1}+C{k0+2}',fmt=EUR),cell(wX,f'=D{k0+1}+D{k0+2}',fmt=EUR),cell(wX,f'=E{k0+1}+E{k0+2}',fmt=EUR)]); EXP[('Errata CSV',f'E{k0+3}')]=18.60; EXP[('Errata CSV',f'C{k0+3}')]=20.90; EXP[('Errata CSV',f'D{k0+3}')]=2.30
fn=PIECES+'163-R2-etalons-rappel-autonome-reconstitution.xlsx'
w.save(fn)
json.dump({'file':fn,'multi':[[a,b,v] for (a,b),v in EXP.items()]},open(OUT+'b4/exp_163.json','w'),ensure_ascii=False); print('écrit',fn)
