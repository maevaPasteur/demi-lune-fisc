"""Chargement commun (série B2) ; reprend B1_common et ajoute la version C des pièces 155-R3 et 156-R3 (site, 26/11)."""
import sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from B1_common import *
import openpyxl
VC='scripts/lot7-tables-virtuelles/cache/entrees/lot27/vC/'; OUT2=O+'B2/'
def out2(name):
    f=open(OUT2+name,'w')
    def p(*a):
        print(*a); print(*a,file=f); f.flush()
    return p
def sheet(fname,sh,hdr_row=0):
    wb=openpyxl.load_workbook(VC+fname,read_only=True,data_only=True)
    rows=list(wb[sh].iter_rows(values_only=True))
    return pd.DataFrame(rows[hdr_row+1:],columns=[str(c) for c in rows[hdr_row]])
F155='155-R3-tables-videes-traces-egalites-paiements-separes.xlsx'
F156='156-R3-tableau-p40-37-tickets-17-tickets-au-centime.xlsx'
