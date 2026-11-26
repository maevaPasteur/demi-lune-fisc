"""B4 : recalcul LibreOffice (UNO : calculateAll puis enregistrement au format xlsx) des pièces 161 à 165.

Exécution habituelle : comme macro (fonction recalcule) dans l'interpréteur Python intégré à LibreOffice, voir executer.sh.
Elle recalcule chaque classeur 161-… à 165-… de cache/pieces/ et l'enregistre, avec ses valeurs, dans cache/recalc/.
La variable d'environnement LOT5_ICI donne le dossier scripts/lot5-tva.
Variante : python b4_recalc.py FICHIER… avec un interpréteur disposant du module uno (LibreOffice démarré en écoute par connect)."""
import sys, os, time, subprocess, glob, uno
from com.sun.star.beans import PropertyValue
ICI=os.environ.get('LOT5_ICI') or os.path.dirname(os.path.abspath(__file__))
def pv(n,v): p=PropertyValue(); p.Name=n; p.Value=v; return p
def connect():
    subprocess.Popen(['soffice','--headless','--invisible','--norestore','--nologo','--accept=socket,host=localhost,port=2002;urp;'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    ctx=uno.getComponentContext(); res=ctx.ServiceManager.createInstanceWithContext('com.sun.star.bridge.UnoUrlResolver',ctx)
    for _ in range(60):
        try: c=res.resolve('uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext'); break
        except Exception: time.sleep(1)
    return c.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop',c)
def recalc(desk,src,dst=None):
    doc=desk.loadComponentFromURL(uno.systemPathToFileUrl(os.path.abspath(src)),'_blank',0,(pv('Hidden',True),))
    doc.calculateAll()
    doc.storeToURL(uno.systemPathToFileUrl(os.path.abspath(dst or src)),(pv('FilterName','Calc MS Excel 2007 XML'),))
    doc.close(True)
def recalcule(*args):
    """Point d'entrée de la macro LibreOffice."""
    desk=XSCRIPTCONTEXT.getDesktop(); out=os.path.join(ICI,'cache','recalc'); os.makedirs(out,exist_ok=True); log=[]
    for f in sorted(glob.glob(os.path.join(ICI,'cache','pieces','16[1-5]-*.xlsx'))):
        t=time.time(); recalc(desk,f,os.path.join(out,os.path.basename(f))); log.append(f'recalculé {os.path.basename(f)} {time.time()-t:.1f} s')
    with open(os.path.join(ICI,'cache','log','b4_recalc.txt'),'w',encoding='utf-8') as fh: fh.write('\n'.join(log)+'\n')
g_exportedScripts=(recalcule,)
if __name__=='__main__':
    d=connect()
    for f in sys.argv[1:]:
        t=time.time(); recalc(d,f); print('recalculé',f,round(time.time()-t,1),'s')
    try: d.terminate()
    except Exception: pass
