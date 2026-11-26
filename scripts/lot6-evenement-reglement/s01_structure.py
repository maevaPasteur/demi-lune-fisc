"""Lot 2.6 / M0-5 et M0-1 : structure des fichiers remis (format, métadonnées OLE, en-têtes, pieds, colonnes ajoutées).
Sortie : out/s01_structure.txt"""
import olefile, xlrd, os, hashlib, sys
D='public/documents/caisse-enregistreuse/'
SRC='/mnt/user-data/uploads/demi-lune-comptabilite/public/documents/caisse-enregistreuse/SOURCE-reglement-brut_2022-2025.xls'
FILES={'E':['14-annexe-e1-2022-2023.xls','15-annexe-e2-2023-2024.xls','16-annexe-e3-2024-2025.xls'],
 'C':['17-annexe-c1-2022-2023.xls','18-annexe-c2-2023-2024.xls','19-annexe-c3-2024-2025.xls'],
 'F':['20-annexe-f1-2022-2023.xls','21-annexe-f2-2023-2024.xls','22-annexe-f3-2024-2025.xls'],
 'B':['24-annexe-b1-2022-2023.xls','25-annexe-b2-2023-2024.xls','26-annexe-b3-2024-2025.xls'],
 'G':['ANNEXE-G1_journal-tva_2022-2023.xls','ANNEXE-G2_journal-tva_2023-2024.xls','ANNEXE-G3_journal-tva_2024-2025.xls'],
 'H':['ANNEXE-H1_liste-tickets_2022-2023.xls','ANNEXE-H2_liste-tickets_2023-2024.xls','ANNEXE-H3_liste-tickets_2024-2025.xls']}
out=open('scripts/lot6-evenement-reglement/out/s01_structure.txt','w')
def p(*a):
    print(*a); print(*a,file=out)
for k,fl in FILES.items():
    for f in fl:
        path=D+f
        md5=hashlib.md5(open(path,'rb').read()).hexdigest()
        ole=olefile.OleFileIO(path); m=ole.get_metadata()
        streams=['/'.join(s) for s in ole.listdir()]
        p(f'===== {k} {f}  taille {os.path.getsize(path)}  md5 {md5}')
        p('  flux OLE :',streams)
        for a in ['title','author','last_saved_by','creating_application','create_time','last_saved_time','company','codepage']:
            p(f'  {a}: {getattr(m,a,None)!r}')
        wb=xlrd.open_workbook(path,formatting_info=False)
        p('  BIFF version',wb.biff_version,' feuilles',[(s.name,s.nrows,s.ncols) for s in wb.sheets()])
        s=wb.sheet_by_index(0)
        p('  en-tête :',s.row_values(0))
        p('  ligne 2 :',s.row_values(1))
        # dernières lignes non vides
        for r in range(max(0,s.nrows-4),s.nrows):
            p(f'  ligne {r+1} :',s.row_values(r))
        # formules ? xlrd ne lit pas les formules ; on compte les types de cellules de la dernière ligne
        p('  types cellules dernière ligne :',[s.cell_type(s.nrows-1,c) for c in range(s.ncols)])
# Export natif
p('===== SOURCE natif',SRC,os.path.getsize(SRC),hashlib.md5(open(SRC,'rb').read()).hexdigest())
head=open(SRC,'rb').read(3000).decode('utf-8','replace')
p(head[:3000])
out.close()
