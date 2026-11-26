"""Contrôle des errata R3 (lot 2.6) : chaque cellule des onglets d'origine (valeur en cache et formule) est-elle inchangée ?"""
import openpyxl, math, sys
S='public/documents/caisse-enregistreuse/'; D='public/documents/pieces-lot6/'
P=[('72-R2-suppressions-DEL-rapprochement-ventilation-en-euros-3-exercices.xlsx','72-R3-suppressions-DEL-rapprochement-ventilation-en-euros-3-exercices-erratum.xlsx'),
   ('89-R2-fichiers-E-F-C-reconciliation-DEL-reglements-CA-quantites-TVA-3-exercices.xlsx','89-R3-fichiers-E-F-C-reconciliation-DEL-reglements-CA-quantites-TVA-3-exercices-erratum.xlsx'),
   ('90-R1-compteur-perpetuel-deux-series-quatre-montants-B-dans-C.xlsx','90-R3-compteur-perpetuel-deux-series-quatre-montants-B-dans-C-erratum.xlsx'),
   ('91-R1-reconciliation-annexes-A-B-C-F-G-H-quantites-exemple-14-04-2022.xlsx','91-R3-reconciliation-annexes-A-B-C-F-G-H-quantites-exemple-14-04-2022-erratum.xlsx')]
def grid(fn,data_only):
    wb=openpyxl.load_workbook(fn,read_only=True,data_only=data_only); out={}
    for ws in wb.worksheets:
        d={}
        for i,r in enumerate(ws.iter_rows(values_only=True),1):
            for j,v in enumerate(r,1):
                if v is not None and v!='': d[(i,j)]=v
        out[ws.title]=d
    return out
def same(a,b):
    if isinstance(a,(int,float)) and isinstance(b,(int,float)) and not isinstance(a,bool): return math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-9)
    return a==b
for o,n in P:
    O=grid(S+o,True); N=grid(D+n,True); OF=grid(S+o,False); NF=grid(D+n,False)
    print('==',n); print('   onglet 1 :',list(N)[0],'; onglets d\'origine dans l\'ordre :',list(N)[1:]==list(O))
    vdiff=fdiff=filled=ncell=0; ex=[]
    for sh in O:
        o_,n_,of,nf=O[sh],N.get(sh,{}),OF[sh],NF.get(sh,{})
        for k in set(o_)|set(n_)|set(of)|set(nf):
            ncell+=1; fo,fn_=of.get(k),nf.get(k)
            isf=isinstance(fo,str) and fo.startswith('=')
            if isf and (not isinstance(fn_,str) or fn_.replace(' ','')!=fo.replace(' ','')): fdiff+=1; ex.append(('formule',sh,k,fo,fn_))
            if k in o_:
                if not same(o_[k],n_.get(k)): vdiff+=1; ex.append(('valeur',sh,k,o_[k],n_.get(k)))
            elif k in n_:
                if isf: filled+=1
                else: vdiff+=1; ex.append(('ajout',sh,k,None,n_[k]))
    print(f'   cellules comparées {ncell} ; valeurs modifiées {vdiff} ; formules modifiées {fdiff} ; formules sans valeur à l\'origine, calculées {filled}')
    for x in ex[:8]: print('  ',x)
    print('   tirets cadratins dans l\'onglet ajouté :',sum(1 for v in N['Erratum R2'].values() if isinstance(v,str) and '—' in v))
    print('   cellules en erreur dans tout le classeur :',sum(1 for sh in N for v in N[sh].values() if isinstance(v,str) and v.startswith(('#','Err:'))))
