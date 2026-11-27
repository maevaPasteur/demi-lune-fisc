"""B0 point 9 : extraction lisible (formules et valeurs recalculées) des onglets cités par le texte. Sortie : out/s07_dump_<pièce>.txt"""
import openpyxl, sys
R='scripts/lot7-tables-virtuelles/out/B0_pieces_recalc/'; S='scripts/lot7-tables-virtuelles/cache/entrees/lot27/'
f=sys.argv[1]; sheets=sys.argv[2].split('|'); maxr=int(sys.argv[3]) if len(sys.argv)>3 else 60
fo=openpyxl.load_workbook(S+f); fv=openpyxl.load_workbook(R+f,data_only=True)
out=open('scripts/lot7-tables-virtuelles/out/B0_s07_dump_'+f[:6]+'.txt','a')
for sh in sheets:
    wf=fo[sh]; wv=fv[sh]
    print(f'===== {f} / {sh} ({wf.max_row} x {wf.max_column})',file=out)
    for r in range(1,min(maxr,wf.max_row)+1):
        cells=[]
        for c in range(1,wf.max_column+1):
            x=wf.cell(r,c); v=wv.cell(r,c).value
            if x.value is None: continue
            if isinstance(x.value,str) and x.value.startswith('='): cells.append(f'{x.coordinate}:{x.value} -> {v!r}')
            else: cells.append(f'{x.coordinate}:{v!r}')
        if cells: print(' | '.join(cells),file=out)
out.close()
