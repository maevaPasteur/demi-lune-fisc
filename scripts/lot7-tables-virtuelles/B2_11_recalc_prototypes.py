"""Recalcul LibreOffice headless (UNO) de copies des versions de travail 172 à 174 et contrôle des valeurs. Sortie : out/B2/11.txt, out/B2/recalc/"""
import os, time, subprocess, shutil, uno, openpyxl
from com.sun.star.beans import PropertyValue
SRC='scripts/lot7-tables-virtuelles/out/pieces/'; DST='scripts/lot7-tables-virtuelles/out/B2/recalc/'; os.makedirs(DST,exist_ok=True)
def pv(n,v): p=PropertyValue(); p.Name=n; p.Value=v; return p
subprocess.Popen(['soffice','--headless','--invisible','--norestore','--nologo','--accept=socket,host=localhost,port=2005;urp;'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
ctx=uno.getComponentContext(); res=ctx.ServiceManager.createInstanceWithContext('com.sun.star.bridge.UnoUrlResolver',ctx)
for _ in range(90):
    try: c=res.resolve('uno:socket,host=localhost,port=2005;urp;StarOffice.ComponentContext'); break
    except Exception: time.sleep(1)
d=c.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop',c)
out=open('scripts/lot7-tables-virtuelles/out/B2/11.txt','w')
for f in sorted(os.listdir(SRC)):
    if not f.startswith('A-2.7'): continue
    t=time.time(); cp=DST+f; shutil.copy(SRC+f,cp)
    doc=d.loadComponentFromURL(uno.systemPathToFileUrl(cp),'_blank',0,(pv('Hidden',True),)); doc.calculateAll()
    doc.storeToURL(uno.systemPathToFileUrl(cp),(pv('FilterName','Calc MS Excel 2007 XML'),)); doc.close(True)
    wb=openpyxl.load_workbook(cp,data_only=True)
    err=sum(1 for ws in wb.worksheets for row in ws.iter_rows() for x in row if isinstance(x.value,str) and x.value.startswith(('#','Err:')))
    print(f'{f} : recalculé en {time.time()-t:.0f} s ; cellules en erreur {err}',file=out)
    for n in ('Synthèse','Passerelle'):
        if n in wb.sheetnames:
            for r in wb[n].iter_rows(values_only=True): print('   ',r,file=out)
    out.flush()
try: d.terminate()
except Exception: pass
