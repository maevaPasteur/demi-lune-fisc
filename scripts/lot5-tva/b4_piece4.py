"""B4 : construit 164 (les 32 047 lignes signalées par la colonne E du service, ventilées). Source : C_b3.pkl (b3_c1_c3.py)."""
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import json
from common import *
from pieces_common import *
CC=pd.read_pickle(CA+'C_b3.pkl'); A=pd.read_pickle(CA+'B3_articles.pkl')
EXP={}; w=wb()
M=['164. La colonne E « Erreur Taux TVA dans Base Envoyée Faux/Correct » des annexes C-1 à C-3 : les 32 047 lignes signalées, ventilées',
 'Sources : annexes C-1 à C-3, colonnes E et F ajoutées par le service ; taux appliqué : 161 ; taux légal : 162. Script : b3_c1_c3.py ; ce classeur : b4_piece4.py.',
 '§ Définitions',
 'Taux du service : pour une ligne signalée, le taux de droite de la colonne E (« 10 % / 20 % » : le service tient 20 % pour correct ; « 20 % / 10 % » : 10 %) ; pour une ligne non signalée, le taux de la colonne 16, que le service conserve.',
 'Catégories des lignes signalées (formule, onglet « Lignes signalées », colonne K) :',
 '  Artefact : la caisse a appliqué le taux légal et le service retient ce même taux ; la colonne 16 portait le taux de la ligne précédente.',
 '  Erreur réelle bien redressée : la caisse n\'a pas appliqué le taux légal et le service retient le taux légal.',
 '  Erreur réelle mal redressée : la caisse n\'a pas appliqué le taux légal et le service retient le taux appliqué (la colonne 16 portait le taux légal).',
 '  Erreur du service : la caisse a appliqué le taux légal et le service retient un autre taux.',
 '  Indéterminé : référence de nature non établie (162, onglet « Indéterminés »).',
 'Lignes non signalées retenues (onglet « Non signalées ») : erreur réelle non signalée (taux appliqué différent du taux légal) ; taux du fichier faux repris (la caisse a appliqué le taux légal, la colonne 16 porte l\'autre taux et le service la conserve) ; indéterminé à taux du fichier différent du taux appliqué.',
 'Réconciliation : les lignes où le taux du service diffère du taux appliqué sont les lignes signalées dont la colonne 16 portait déjà le taux appliqué, plus les lignes non signalées dont la colonne 16 diffère du taux appliqué.']
check_dash(M); methode(w,M)
S=w.create_sheet('Synthèse')
x=CC[CC.flag].reset_index(drop=True); NS=len(x); assert NS==32047
ws=w.create_sheet('Lignes signalées')
header(ws,['exercice','rowC','ref','libellé','Tot_rem_Ttc','taux col. 16','taux du service (colonne E)','taux appliqué','taux légal (vide si indéterminé)','F du service','catégorie','col. 16 = taux appliqué','taux du service ≠ taux appliqué','E du service (texte)'],[10,7,7,28,10,7,9,7,9,10,26,8,8,12])
cat=lambda k: f'=IF(I{k}="","Indéterminé",IF(H{k}=I{k},IF(G{k}=I{k},"Artefact","Erreur du service"),IF(G{k}=I{k},"Erreur réelle bien redressée","Erreur réelle mal redressée")))'
for i,r in x.iterrows():
    k=2+i; ws.append([r.ex,int(r.rowC),r.ref,r.lib_s,float(r.tot),int(r.rf),int(r.Ecor),int(r.rart),None if pd.isna(r.tl) else int(r.tl),float(r.Fs),cat(k),f'=IF(F{k}=H{k},1,0)',f'=IF(G{k}<>H{k},1,0)',r.Es])
y=CC[~CC.flag & ((~CC.ind & ~CC.app_ok) | (CC.rf!=CC.rart))].reset_index(drop=True); NN=len(y)
wn=w.create_sheet('Non signalées')
header(wn,['exercice','rowC','ref','libellé','Tot_rem_Ttc','taux col. 16 (repris par le service)','taux appliqué','taux légal (vide si indéterminé)','catégorie','col. 16 ≠ taux appliqué','col. 16 (taux du service) ≠ taux légal'],[10,7,7,28,10,9,7,9,34,8,8])
catn=lambda k: f'=IF(H{k}="","Indéterminé, col. 16 ≠ appliqué",IF(G{k}<>H{k},"Erreur réelle non signalée","Taux du fichier faux repris"))'
for i,r in y.iterrows():
    k=2+i; wn.append([r.ex,int(r.rowC),r.ref,r.lib_s,float(r.tot),int(r.rf),int(r.rart),None if pd.isna(r.tl) else int(r.tl),catn(k),f'=IF(F{k}<>G{k},1,0)',f'=IF(H{k}="","",IF(F{k}<>H{k},1,0))'])
LS=lambda col: f"'Lignes signalées'!${col}$2:${col}${1+NS}"
NSr=lambda col: f"'Non signalées'!${col}$2:${col}${1+NN}"
# Références
refs=sorted(set(x.ref)|set(y.ref)); NR=len(refs); lib=A.set_index('ref').libelles
wr=w.create_sheet('Références')
cats=['Artefact','Erreur réelle bien redressée','Erreur réelle mal redressée','Erreur du service','Indéterminé']
catsn=['Erreur réelle non signalée','Taux du fichier faux repris']
header(wr,['ref','libellé']+[f'signalées : {c}' for c in cats]+[f'non signalées : {c}' for c in catsn],[7,30]+[10]*7)
for i,ref in enumerate(refs):
    k=2+i; wr.append([ref,lib.get(ref,'')]+[f'=COUNTIFS({LS("C")},A{k},{LS("K")},"{c}")' for c in cats]+[f'=COUNTIFS({NSr("C")},A{k},{NSr("I")},"{c}")' for c in catsn])
# Synthèse
S.column_dimensions['A'].width=60
for cl in 'BCDE': S.column_dimensions[cl].width=16
S.append([cell(S,'Tableau 57 ter, par formules (trois exercices)',bold=True)])
S.append([cell(S,h,bold=True,fill=True) for h in ['Catégorie','Lignes','% des lignes signalées','TTC (€)','Colonne F du service (€)']])
exp=[(30364,94.75,449015.38,-9701.34),(626,1.95,5104.49,386.70),(87,0.27,336.45,-25.49),(822,2.56,7613.18,-232.53),(148,0.46,2100.30,147.92)]
for j,cn in enumerate(cats):
    k=3+j; S.append([cn,cell(S,f'=COUNTIF({LS("K")},A{k})',fmt=INT),cell(S,f'=B{k}/B$8',fmt=PCT2),cell(S,f'=SUMIFS({LS("E")},{LS("K")},A{k})',fmt=EUR),cell(S,f'=SUMIFS({LS("J")},{LS("K")},A{k})',fmt=EUR)])
    e=exp[j]; EXP.update({f'B{k}':e[0],f'C{k}':('pct2',e[1]),f'D{k}':e[2],f'E{k}':e[3]})
S.append(['Total signalé',cell(S,'=SUM(B3:B7)',fmt=INT),cell(S,'=SUM(C3:C7)',fmt=PCT2),cell(S,'=SUM(D3:D7)',fmt=EUR),cell(S,'=SUM(E3:E7)',fmt=EUR)]); EXP.update({'B8':32047,'C8':('pct2',100),'E8':-9424.74})
S.append(['contrôle : lignes de l\'onglet « Lignes signalées »',cell(S,f'=COUNTA({LS("A")})',fmt=INT)]); EXP['B9']=32047
S.append(['Part des artefacts dans le total de la colonne F',cell(S,'=E3/E8',fmt=PCT1)]); EXP['B10']=('pct1',102.9)
S.append([])
S.append([cell(S,'Lignes non signalées',bold=True)])
for j,cn in enumerate(catsn+['Indéterminé, col. 16 ≠ appliqué']):
    k=13+j; S.append([cn,cell(S,f'=COUNTIF({NSr("I")},A{k})',fmt=INT),None,cell(S,f'=SUMIFS({NSr("E")},{NSr("I")},A{k})',fmt=EUR)])
EXP.update({'B13':730,'D13':4211.90,'B14':1152})
S.append([])
S.append([cell(S,'Réconciliation : lignes où le taux du service diffère du taux appliqué',bold=True)])
S.append(['lignes signalées dont la colonne 16 portait déjà le taux appliqué (signalées à tort)',cell(S,f'=SUMPRODUCT(({LS("L")}=1)*({LS("M")}=1))',fmt=INT)]); EXP['B18']=1593
S.append(['lignes non signalées dont la colonne 16 diffère du taux appliqué',cell(S,f'=COUNTIF({NSr("J")},1)',fmt=INT)]); EXP['B19']=1736
S.append(['total',cell(S,'=B18+B19',fmt=INT)]); EXP['B20']=3329
S.append(['contrôle : lignes signalées où le taux du service diffère du taux appliqué',cell(S,f'=COUNTIF({LS("M")},1)',fmt=INT)]); EXP['B21']=1593
S.append([])
S.append([cell(S,'Lignes de nature déterminée où le taux du service diffère du taux légal',bold=True)])
S.append(['lignes signalées (erreur du service + erreur réelle mal redressée)',cell(S,f'=COUNTIF({LS("K")},"Erreur du service")+COUNTIF({LS("K")},"Erreur réelle mal redressée")',fmt=INT)]); EXP['B24']=909
S.append(['lignes non signalées (colonne 16 conservée, différente du taux légal)',cell(S,f'=COUNTIF({NSr("K")},1)',fmt=INT)]); EXP['B25']=1314
S.append(['total',cell(S,'=B24+B25',fmt=INT)]); EXP['B26']=2223
w.save(PIECES+'164-R2-colonne-E-du-service-32047-lignes-ventilees.xlsx')
json.dump({'file':PIECES+'164-R2-colonne-E-du-service-32047-lignes-ventilees.xlsx','sheet':'Synthèse','exp':EXP},open(OUT+'b4/exp_164.json','w'),ensure_ascii=False); print('ok',NS,NN,NR)
