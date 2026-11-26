"""B4 : contrôle des errata : chaque cellule des onglets d'origine (valeur en cache et formule) est-elle inchangée ?"""
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import openpyxl, math
from common import PIECES, PIECE_38, PIECE_85, PIECE_86, PIECE_87, PIECE_88
P=[(PIECE_38,'38-R3-rf-anomalies-tva-erratum.xlsx'),(PIECE_85,'85-R3-tva-bouclage-journaux-G-29588-lignes-identite-VAT-base-erratum.xlsx'),(PIECE_86,'86-R3-tva-rapprochement-caisse-tickets-comptabilite-erratum.xlsx'),
   (PIECE_87,'87-R3-tva-colonnes-E-et-F-annexes-C-corrections-de-taux-erratum.xlsx'),(PIECE_88,'88-R3-taux-tva-par-article-et-lignes-signalees-erratum.xlsx')]
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
    O=grid(o,True); N=grid(PIECES+n,True)
    OF=grid(o,False); NF=grid(PIECES+n,False)
    print('==',n,'onglets :',list(N)[:1],'+',len(O),'onglets d\'origine ; ordre conservé :',list(N)[1:]==list(O))
    vdiff=fdiff=filled=0; ex=[]
    for sh in O:
        o_,n_,of,nf=O[sh],N.get(sh,{}),OF[sh],NF.get(sh,{})
        keys=set(o_)|set(n_)|set(of)|set(nf)
        for k in keys:
            fo,fn_=of.get(k),nf.get(k)
            isf=isinstance(fo,str) and fo.startswith('=')
            if isf and (not isinstance(fn_,str) or fn_.replace(' ','')!=fo.replace(' ','')): fdiff+=1; ex.append(('formule',sh,k,fo,fn_))
            if k in o_:
                if not same(o_[k],n_.get(k)): vdiff+=1; ex.append(('valeur',sh,k,o_[k],n_.get(k)))
            elif k in n_:
                if isf: filled+=1; 
                else: vdiff+=1; ex.append(('ajout',sh,k,None,n_[k]))
    print(f'   valeurs d\'origine modifiées : {vdiff} ; formules modifiées : {fdiff} ; formules sans valeur à l\'origine, calculées par LibreOffice : {filled}')
    for x in ex[:8]: print('  ',x)
    er=[(k,v) for k,v in N['Erratum R2'].items() if isinstance(v,str) and '\u2014' in v]; print('   tirets cadratins dans l\'onglet ajouté :',len(er))
    errs=sum(1 for sh in N for v in N[sh].values() if isinstance(v,str) and v.startswith(('#','Err:')))
    print('   cellules en erreur dans tout le classeur :',errs)
