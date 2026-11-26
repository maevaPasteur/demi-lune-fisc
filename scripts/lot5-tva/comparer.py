"""Compare, cellule par cellule et onglet par onglet, les pièces régénérées avec des pièces de référence.

Usage : python comparer.py DOSSIER_REFERENCE [--synthese]

Pour chaque classeur .xlsx du dossier de référence, le classeur de même nom est cherché dans cache/recalc/ (pièces 161 à 165
recalculées par b4_recalc.py), puis dans cache/pieces/ (errata 38, 85 à 88, enregistrés par LibreOffice avec leurs valeurs).
Un classeur régénéré dont les formules n'ont pas de valeur en cache est d'abord recalculé par LibreOffice
(soffice --headless --convert-to xlsx) dans cache/recalc/.
Les références sont lues en valeurs (cache de formules, openpyxl data_only=True).
Onglets comparés : tous (option --synthese : seulement les onglets dont le nom contient « Synthèse », plus « Erratum R2 » ;
pour la pièce 163, qui n'a pas d'onglet « Synthèse », ses onglets de tableaux, c'est-à-dire tous sauf « Méthode » et « Journal G »).
Nombres : égaux au centime (écart absolu < 0,005 et même arrondi à deux décimales). Textes : identiques.
Une cellule vide et une chaîne vide sont tenues pour égales."""
import os, sys, glob, subprocess, numbers, openpyxl

ICI = os.path.dirname(os.path.abspath(__file__))
REF = sys.argv[1]
SYNTH = '--synthese' in sys.argv[2:]
PIECES = os.path.join(ICI, 'cache', 'pieces'); RECALC = os.path.join(ICI, 'cache', 'recalc')
os.makedirs(RECALC, exist_ok=True)

def sans_cache(f):
    """Vrai si une formule du classeur n'a pas de valeur en cache."""
    wf = openpyxl.load_workbook(f, read_only=True); wv = openpyxl.load_workbook(f, read_only=True, data_only=True)
    for a, b in zip(wf.worksheets, wv.worksheets):
        for ra, rb in zip(a.iter_rows(values_only=True), b.iter_rows(values_only=True)):
            for x, y in zip(ra, rb):
                if isinstance(x, str) and x.startswith('=') and y is None: return True
    return False

def regenere(nom):
    r = os.path.join(RECALC, nom)
    if os.path.exists(r): return r
    p = os.path.join(PIECES, nom)
    if not os.path.exists(p): return None
    if not sans_cache(p): return p
    subprocess.run(['soffice', '--headless', '--calc', '--convert-to', 'xlsx', '--outdir', RECALC, p],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return r

def grille(ws):
    return [list(r) for r in ws.iter_rows(values_only=True)]

num = lambda v: isinstance(v, numbers.Number) and not isinstance(v, bool)
vide = lambda v: v is None or v == ''
total = 0
for fr in sorted(glob.glob(os.path.join(REF, '*.xlsx'))):
    nom = os.path.basename(fr); fg = regenere(nom)
    if fg is None:
        print(f'{nom} : ABSENT des pièces régénérées'); total += 1; continue
    wr = openpyxl.load_workbook(fr, read_only=True, data_only=True); wg = openpyxl.load_workbook(fg, read_only=True, data_only=True)
    onglets = [n for n in wr.sheetnames if not SYNTH or 'Synthèse' in n or 'Synthese' in n or n == 'Erratum R2']
    if SYNTH and not onglets: onglets = [n for n in wr.sheetnames if n not in ('Méthode', 'Journal G')]
    ecarts = []; n = 0
    if wr.sheetnames != wg.sheetnames: ecarts.append(('(classeur)', '', wr.sheetnames, wg.sheetnames))
    for sh in onglets:
        if sh not in wg.sheetnames:
            ecarts.append((sh, '', 'onglet', 'absent')); continue
        a, b = grille(wr[sh]), grille(wg[sh])
        for r in range(max(len(a), len(b))):
            ra = a[r] if r < len(a) else []; rb = b[r] if r < len(b) else []
            for k in range(max(len(ra), len(rb))):
                x = ra[k] if k < len(ra) else None; y = rb[k] if k < len(rb) else None
                if vide(x) and vide(y): continue
                n += 1
                if num(x) and num(y):
                    if abs(x - y) >= 0.005 or round(x, 2) != round(y, 2): ecarts.append((sh, f'{openpyxl.utils.get_column_letter(k+1)}{r+1}', x, y))
                elif x != y:
                    ecarts.append((sh, f'{openpyxl.utils.get_column_letter(k+1)}{r+1}', x, y))
    print(f'{nom} : {len(onglets)} onglet(s) ; {n} cellules comparées ; {len(ecarts)} écart(s)')
    for e in ecarts[:40]: print('    onglet', repr(e[0]), 'cellule', e[1], 'attendu', repr(e[2]), 'obtenu', repr(e[3]))
    total += len(ecarts)
print('ÉCARTS AU TOTAL :', total)
