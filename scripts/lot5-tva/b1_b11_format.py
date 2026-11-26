"""B-11 : mise en forme des colonnes de G (xlrd formatting_info) pour distinguer colonnes natives / ajoutées."""
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import xlrd
from common import GF
for f in GF:
    wb=xlrd.open_workbook(f,formatting_info=True); s=wb.sheet_by_index(0)
    def desc(r,cx):
        xf=wb.xf_list[s.cell_xf_index(r,cx)]; fo=wb.font_list[xf.font_index]; fmt=wb.format_map[xf.format_key].format_str
        pat=xf.background.pattern_colour_index; 
        return f'{repr(s.cell_value(r,cx))[:28]:30s} police={fo.name},{fo.height//20}pt,gras={fo.bold},coul={fo.colour_index} fond={pat} fmt={fmt!r} bord={xf.border.left_line_style}{xf.border.right_line_style}'
    print('#####',os.path.basename(f),'lignes',s.nrows,'colonnes',s.ncols,'; largeurs', {cx:s.colinfo_map[cx].width for cx in range(s.ncols) if cx in s.colinfo_map})
    for r in [0,1,2,3,4]:
        for cx in range(0,s.ncols):
            if r in (0,2) or cx>=11: print(f'  L{r+1} C{cx+1}: {desc(r,cx)}')
    for r in range(s.nrows-8,s.nrows):
        vals=[(cx,s.cell_value(r,cx)) for cx in range(s.ncols) if s.cell_value(r,cx)!='']
        if vals: print(f'  pied L{r+1}:',[(cx+1,v,desc(r,cx).split('police=')[1][:60]) for cx,v in vals])
    print('  fusions :',s.merged_cells[:20])
