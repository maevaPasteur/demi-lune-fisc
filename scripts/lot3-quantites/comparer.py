"""Compare les onglets de synthèse des pièces régénérées (cache/pieces/) avec ceux de pièces de référence.

Usage : python comparer.py DOSSIER_REFERENCE [DOSSIER_REGENERE]

Onglets comparés : tout onglet dont le nom contient « Synthèse » ou « Synthese », plus « Montant par fenêtre » ;
pour la pièce n° 8, qui n'a pas d'onglet de synthèse, l'onglet « Erratum ».
Les références sont lues en valeurs (cache de formules, openpyxl data_only=True). Les pièces régénérées sont d'abord
recalculées par LibreOffice (soffice --headless --convert-to xlsx) dans cache/recalc/, puis lues en valeurs.
Nombres : égaux au centime (écart absolu < 0,005 et même arrondi à deux décimales). Textes : identiques."""
import os, sys, glob, subprocess, numbers, openpyxl

ICI = os.path.dirname(os.path.abspath(__file__))
REF = sys.argv[1]
GEN = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ICI, 'cache', 'pieces')
RECALC = os.path.join(ICI, 'cache', 'recalc')
os.makedirs(RECALC, exist_ok=True)

def onglets(wb, nom):
    s = [n for n in wb.sheetnames if 'Synthèse' in n or 'Synthese' in n or n == 'Montant par fenêtre']
    return s or [n for n in wb.sheetnames if n == 'Erratum']

def recalcule(f):
    subprocess.run(['soffice', '--headless', '--calc', '--convert-to', 'xlsx', '--outdir', RECALC, f],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return os.path.join(RECALC, os.path.basename(f))

total_ecarts = 0
for fr in sorted(glob.glob(os.path.join(REF, '*.xlsx'))):
    nom = os.path.basename(fr); fg = os.path.join(GEN, nom)
    if not os.path.exists(fg):
        print(f'{nom} : ABSENT des pièces régénérées'); total_ecarts += 1; continue
    wr = openpyxl.load_workbook(fr, data_only=True); wg = openpyxl.load_workbook(recalcule(fg), data_only=True)
    n = 0; ecarts = []
    for sh in onglets(wr, nom):
        if sh not in wg.sheetnames:
            ecarts.append((sh, '', 'onglet', 'absent')); continue
        a, b = wr[sh], wg[sh]
        for r in range(1, max(a.max_row, b.max_row) + 1):
            for c in range(1, max(a.max_column, b.max_column) + 1):
                x, y = a.cell(r, c).value, b.cell(r, c).value
                if x is None and y is None: continue
                n += 1
                num = lambda v: isinstance(v, numbers.Number) and not isinstance(v, bool)
                if num(x) and num(y):
                    if abs(x - y) >= 0.005 or round(x, 2) != round(y, 2): ecarts.append((sh, a.cell(r, c).coordinate, x, y))
                elif x != y:
                    ecarts.append((sh, a.cell(r, c).coordinate, x, y))
    print(f'{nom} : onglets {onglets(wr, nom)} ; {n} cellules comparées ; {len(ecarts)} écart(s)')
    for e in ecarts: print('   ', e)
    total_ecarts += len(ecarts)
print('ÉCARTS AU TOTAL :', total_ecarts)
