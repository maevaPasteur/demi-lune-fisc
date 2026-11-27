"""Recalcul LibreOffice headless (UNO) d'une annexe : copie dans out/B4/recalc/, calculateAll, enregistrement xlsx (formules et valeurs),
décompte des cellules en erreur. Usage : python3 -I B4_09_recalc.py <nom de fichier dans pieces/> [port]. Sortie : out/B4/recalc/<nom>.txt"""
import os, sys, time, subprocess, shutil, uno, openpyxl
from com.sun.star.beans import PropertyValue
SRC = 'scripts/lot7-tables-virtuelles/out/pieces/'; DST = 'scripts/lot7-tables-virtuelles/out/B4/recalc/'; os.makedirs(DST, exist_ok=True)
f = sys.argv[1]; port = sys.argv[2] if len(sys.argv) > 2 else '2011'
def pv(n, v): p = PropertyValue(); p.Name = n; p.Value = v; return p
prof = f'/tmp/lo_profile_{port}'
proc = subprocess.Popen(['soffice', f'-env:UserInstallation=file://{prof}', '--headless', '--invisible', '--norestore', '--nologo',
                         f'--accept=socket,host=localhost,port={port};urp;'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
ctx = uno.getComponentContext(); res = ctx.ServiceManager.createInstanceWithContext('com.sun.star.bridge.UnoUrlResolver', ctx)
for _ in range(120):
    try: c = res.resolve(f'uno:socket,host=localhost,port={port};urp;StarOffice.ComponentContext'); break
    except Exception: time.sleep(1)
d = c.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', c)
t = time.time(); cp = DST + f; shutil.copy(SRC + f, cp)
doc = d.loadComponentFromURL(uno.systemPathToFileUrl(cp), '_blank', 0, (pv('Hidden', True),)); doc.calculateAll()
doc.storeToURL(uno.systemPathToFileUrl(cp), (pv('FilterName', 'Calc MS Excel 2007 XML'),)); doc.close(True)
try: d.terminate()
except Exception: pass
proc.wait(timeout=60)
wb = openpyxl.load_workbook(cp, data_only=True)
errs = [(ws.title, x.coordinate, x.value) for ws in wb.worksheets for row in ws.iter_rows() for x in row
        if isinstance(x.value, str) and (x.value.startswith('#') or x.value.startswith('Err:'))]
wf = openpyxl.load_workbook(cp)
nform = sum(1 for ws in wf.worksheets for row in ws.iter_rows() for x in row if isinstance(x.value, str) and x.value.startswith('='))
out = open(DST + f + '.txt', 'w')
print(f'{f} : recalculé en {time.time() - t:.0f} s ; formules {nform} ; cellules en erreur {len(errs)} ; {errs[:20]}', file=out)
print(open(DST + f + '.txt').read() if False else f'{f} : {time.time() - t:.0f} s ; formules {nform} ; erreurs {len(errs)} {errs[:10]}')
