"""B0 point 9 : recalcul LibreOffice headless (UNO, calculateAll) de COPIES des pièces 92, 93, 94, 157-R4 ;
comparaison cellule à cellule des valeurs en cache (fichier remis) et recalculées ; erreurs de formule.
Sorties : out/pieces_recalc/*.xlsx (copies recalculées), out/s06_recalc.txt"""
import sys, os, time, subprocess, shutil, uno, openpyxl, math
from com.sun.star.beans import PropertyValue
SRC='scripts/lot7-tables-virtuelles/cache/entrees/lot27/'; DST='scripts/lot7-tables-virtuelles/out/B0_pieces_recalc/'
FILES=['92-R2-tables-virtuelles-rangs-de-note-659-journees-tickets-zero-occupation.xlsx','93-R1-numeros-de-note-couverts-et-occupation-jour-par-jour.xlsx','94-R2-menus-prix-rafales-DEL-09-09-2022-et-61-conversions-au-forfait.xlsx','157-R4-conversions-au-forfait-133-suites.xlsx']
def pv(n,v): p=PropertyValue(); p.Name=n; p.Value=v; return p
def connect():
    subprocess.Popen(['soffice','--headless','--invisible','--norestore','--nologo','--accept=socket,host=localhost,port=2003;urp;'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    ctx=uno.getComponentContext(); res=ctx.ServiceManager.createInstanceWithContext('com.sun.star.bridge.UnoUrlResolver',ctx)
    for _ in range(90):
        try: c=res.resolve('uno:socket,host=localhost,port=2003;urp;StarOffice.ComponentContext'); break
        except Exception: time.sleep(1)
    return c.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop',c)
out=open('scripts/lot7-tables-virtuelles/out/B0_s06_recalc.txt','w')
def p(*a): print(*a); print(*a,file=out)
os.makedirs(DST,exist_ok=True)
d=connect()
for f in FILES:
    cp=DST+f; shutil.copy(SRC+f,cp); os.chmod(cp,0o644)
    doc=d.loadComponentFromURL(uno.systemPathToFileUrl(cp),'_blank',0,(pv('Hidden',True),))
    doc.calculateAll(); doc.storeToURL(uno.systemPathToFileUrl(cp),(pv('FilterName','Calc MS Excel 2007 XML'),)); doc.close(True)
    a=openpyxl.load_workbook(SRC+f,data_only=True); b=openpyxl.load_workbook(cp,data_only=True); fo=openpyxl.load_workbook(SRC+f)
    nform=ndiff=nerr=nnone=0; ex=[]
    for ws in fo.worksheets:
        wa=a[ws.title]; wb=b[ws.title]
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value,str) and c.value.startswith('='):
                    nform+=1; va=wa[c.coordinate].value; vb=wb[c.coordinate].value
                    if va is None: nnone+=1
                    if isinstance(vb,str) and vb.startswith('#') or isinstance(va,str) and va.startswith('#'):
                        nerr+=1; ex.append(('ERR',ws.title,c.coordinate,c.value[:80],va,vb))
                    elif va is not None:
                        same = (va==vb) or (isinstance(va,(int,float)) and isinstance(vb,(int,float)) and math.isclose(va,vb,rel_tol=1e-9,abs_tol=1e-9))
                        if not same: ndiff+=1; ex.append(('DIFF',ws.title,c.coordinate,c.value[:80],va,vb))
    p(f'{f} : formules {nform} ; sans valeur en cache {nnone} ; erreurs {nerr} ; écarts cache/recalcul {ndiff}')
    for e in ex[:30]: p('   ',e)
try: d.terminate()
except Exception: pass
out.close()
