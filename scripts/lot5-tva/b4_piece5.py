"""B4 : construit 165 (export natif des règlements SOURCE-reglement-brut_2022-2025.xls ; colonne « etat »). Source : cache SOURCE_reglement.pkl (b3_source_reglement.py)."""
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import json
from common import *
from pieces_common import *
S=pd.read_pickle(CA+'SOURCE_reglement.pkl').reset_index(drop=True); N=len(S)
starts=((S.id!=S.id.shift(1))&(S.etat=='9')).sum(); print('débuts de note etat 9 (ordre du fichier) :',starts,'notes distinctes',S[S.etat=='9'].id.nunique())
EXP={}; w=wb()
M=['165. Export natif des règlements de la caisse (SOURCE-reglement-brut_2022-2025.xls) : colonne « etat »',
 'Source : fichier SpreadsheetML de la cliente, caisse-enregistreuse/SOURCE-reglement-brut_2022-2025.xls, 19 334 lignes, 22 colonnes, lu tel quel (b3_source_reglement.py) ; comparé aux annexes F-1 à F-3 (19 334 lignes). Ce classeur : b4_piece5.py.',
 'Onglet « Lignes » : les 22 colonnes d\'origine dans l\'ordre du fichier (valeurs textuelles converties en nombres pour tot_ttc et montant), plus deux colonnes de formule : note à 0 € (tot_ttc = 0) et première ligne d\'une note à « etat » = 9.',
 'Onglet « Comparaison F » : résultat du rapprochement ligne à ligne par le script (valeurs).',
 'Le texte de la section 2.5 n\'y renvoie pas.']
check_dash(M); methode(w,M)
SY=w.create_sheet('Synthèse')
wl=w.create_sheet('Lignes')
cols=['no_caisse','date_ticket','heure_ticket','no_ticket','dat_z','no_z_report','caissier','cod_clt','tot_ttc','tot_tva','tot_sum','tot_tax_sum','tot_rem_globale','tot_rem_lig','etat','(null)','mf_number','mf_desc','id','sy_uk','mod_regl','montant']
header(wl,cols+['note à 0 € (tot_ttc = 0)','première ligne d\'une note à etat = 9'],[6,11,7,6,11,7,9,6,10,9,12,11,8,8,5,5,5,5,8,20,6,10,8,8])
num={'tot_ttc','tot_tva','tot_sum','tot_tax_sum','montant'}
for i,r in S.iterrows():
    k=2+i; v=[]
    for cn in cols:
        x=r[cn]
        if cn in num and x is not None: x=float(x)
        elif cn=='etat': x=int(x)
        elif cn=='id': x=int(x)
        v.append(x)
    v+=[f'=IF(I{k}=0,1,0)', f'=IF(AND(O{k}=9,S{k}<>S{k-1}),1,0)' if k>2 else f'=IF(O{k}=9,1,0)']
    wl.append(v)
R=lambda col: f"'Lignes'!${col}$2:${col}${1+N}"
SY.column_dimensions['A'].width=70; SY.column_dimensions['B'].width=16
SY.append([cell(SY,'Synthèse, par formules',bold=True)])
items=[('Lignes du fichier natif',f'=COUNTA({R("A")})',19334,INT),('Lignes à « etat » = 9',f'=COUNTIF({R("O")},9)',55,INT),('Lignes à « etat » = 0',f'=COUNTIF({R("O")},0)',19279,INT),
 ('Lignes de règlement sur des notes à 0 €',f'=COUNTIF({R("W")},1)',55,INT),('Lignes à « etat » = 9 sur des notes à 0 €',f'=COUNTIFS({R("O")},9,{R("W")},1)',55,INT),
 ('Lignes à « etat » = 9 sur des notes à TTC non nul',f'=COUNTIFS({R("O")},9,{R("W")},0)',0,INT),('Notes à « etat » = 9',f'=SUM({R("X")})',37,INT),
 ('Σ montants des lignes à « etat » = 9 (€)',f'=SUMIFS({R("V")},{R("O")},9)',1958.26,EUR),('Σ montants du fichier (€)',f'=SUM({R("V")})',1278149.46,EUR)]
for j,(a,f,e,fm) in enumerate(items):
    k=2+j; SY.append([a,cell(SY,f,fmt=fm)]); EXP[f'B{k}']=e
wc=w.create_sheet('Comparaison F'); header(wc,['contrôle','valeur'],[80,20])
for a,b in [('lignes du fichier natif absentes des annexes F (multiensemble id, date, heure, n°, mode, montant, tot_ttc)',0),('lignes des annexes F absentes du fichier natif',0),('ordre des lignes identique (F-1, F-2, F-3 mises bout à bout)','oui'),('Σ montants, fichier natif (€)',1278149.46),('Σ montants, annexes F (€)',1278149.46)]:
    wc.append([a,b])
fn=PIECES+'165-R2-export-natif-reglements-etat-9-55-lignes-37-notes.xlsx'; w.save(fn)
json.dump({'file':fn,'sheet':'Synthèse','exp':EXP},open(OUT+'b4/exp_165.json','w'),ensure_ascii=False); print('écrit',fn)
