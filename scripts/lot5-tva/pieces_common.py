"""Outils communs d'écriture des pièces 161 à 165 (openpyxl, mode write_only, formules visibles)."""
from openpyxl import Workbook
from openpyxl.cell import WriteOnlyCell
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter as L
from common import PIECES
BOLD=Font(bold=True); HFILL=PatternFill('solid',fgColor='DDDDDD'); WRAP=Alignment(wrap_text=True,vertical='top')
EUR='#,##0.00'; PCT='0.000%'; PCT1='0.0%'; PCT2='0.00%'; INT='#,##0'
def wb(): return Workbook(write_only=True)
def cell(ws,v,bold=False,fmt=None,fill=False,wrap=False):
    c=WriteOnlyCell(ws,value=v)
    if bold: c.font=BOLD
    if fmt: c.number_format=fmt
    if fill: c.fill=HFILL
    if wrap: c.alignment=WRAP
    return c
def header(ws,cols,widths=None):
    if widths:
        for i,w in enumerate(widths,1): ws.column_dimensions[L(i)].width=w
    ws.append([cell(ws,h,bold=True,fill=True,wrap=True) for h in cols])
def methode(w,lines,width=150):
    ws=w.create_sheet('Méthode'); ws.column_dimensions['A'].width=width
    for i,t in enumerate(lines):
        ws.append([cell(ws,t,bold=(i==0 or t.startswith('§')),wrap=True)])
    return ws
def check_dash(lines):
    for t in lines:
        if isinstance(t,str) and '\u2014' in t: raise ValueError('tiret cadratin : '+t)
