"""B4 : contrôle après recalcul : (1) aucune erreur de formule (valeurs en cache) ; (2) chaque cellule attendue de « Synthèse » égale le chiffre du texte ;
(3) aucun tiret cadratin dans aucune cellule.
Usage : python b4_check.py cache/out/b4/exp_16*.json ; le classeur contrôlé est la version recalculée par LibreOffice
(cache/recalc/, écrite par comparer.py ou b4_recalc.py) si elle existe, sinon le classeur de cache/pieces/."""
import os, sys, json, openpyxl
RECALC=os.path.join(os.path.dirname(os.path.abspath(__file__)),'cache','recalc')
ERR=('#DIV/0!','#N/A','#NAME?','#NULL!','#NUM!','#REF!','#VALUE!','Err:','#VALEUR','#NOM')
def check(fn,exp=None,sheet=None):
    wv=openpyxl.load_workbook(fn,data_only=True,read_only=True); wf=openpyxl.load_workbook(fn,read_only=True)
    nerr=0; nform=0; ndash=0; nnone=0
    for ws,wsf in zip(wv.worksheets,wf.worksheets):
        for rv,rf in zip(ws.iter_rows(values_only=True),wsf.iter_rows(values_only=True)):
            for v,f in zip(rv,rf):
                if isinstance(f,str) and f.startswith('='):
                    nform+=1
                    if v is None: nnone+=1
                if isinstance(v,str) and (v.startswith(ERR) or v.startswith('#')): nerr+=1; print('  ERREUR',ws.title,v,f)
                if isinstance(v,str) and '\u2014' in v: ndash+=1
                if isinstance(f,str) and '\u2014' in f: ndash+=1
    print(f'{fn.split("/")[-1]} : formules {nform} ; erreurs {nerr} ; formules sans valeur en cache {nnone} ; tirets cadratins {ndash}')
    bad=0
    if exp:
        ws=wv[sheet]; vals={}
        for row in ws.iter_rows():
            for c in row:
                if hasattr(c,'coordinate'): vals[c.coordinate]=c.value
        for k,e in exp.items():
            v=vals.get(k)
            if isinstance(e,list) or isinstance(e,tuple):
                kind,x=e; ok=v is not None and round(v*100,1 if kind=='pct1' else 2)==round(x,1 if kind=='pct1' else 2) if kind=='pct1' else (v is not None and abs(v*100-x)<0.0051) if kind=='pct2' else (v is not None and abs(v*100-x)<0.00051)
            else: ok=v is not None and abs(float(v)-e)<0.005
            if not ok: bad+=1; print('  ÉCART',sheet,k,'calculé',v,'attendu',e)
        print(f'  Synthèse : {len(exp)} cellules attendues, {bad} écart(s)')
    return nerr,bad,ndash
def check_only(fn,exp,sheet):
    wv=openpyxl.load_workbook(fn,data_only=True,read_only=True); ws=wv[sheet]; vals={}
    for row in ws.iter_rows():
        for c in row:
            if hasattr(c,'coordinate'): vals[c.coordinate]=c.value
    bad=0
    for k,e in exp.items():
        v=vals.get(k)
        if isinstance(e,(list,tuple)):
            kind,x=e; ok=v is not None and abs(v*100-x)<(0.051 if kind=='pct1' else 0.0051 if kind=='pct2' else 0.00051)
        else: ok=v is not None and abs(float(v)-e)<0.005
        if not ok: bad+=1; print('  ÉCART',sheet,k,'calculé',v,'attendu',e)
    print(f'  {sheet} : {len(exp)} cellules attendues, {bad} écart(s)')
if __name__=='__main__':
    for j in sys.argv[1:]:
        d=json.load(open(j,encoding='utf-8'))
        r=os.path.join(RECALC,os.path.basename(d['file']))
        if os.path.exists(r): d['file']=r
        if 'multi' in d:
            sheets={}
            for sh,k,v in d['multi']: sheets.setdefault(sh,{})[k]=v
            first=True
            for sh,ex in sheets.items():
                if first: check(d['file'],ex,sh); first=False
                else: check_only(d['file'],ex,sh)
        else: check(d['file'],d.get('exp'),d.get('sheet'))
