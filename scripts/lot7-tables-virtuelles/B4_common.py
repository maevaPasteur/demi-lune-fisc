"""Construction des annexes 172 à 175 : outils communs (empreintes SHA-256, onglet « Méthode », écriture d'onglets, styles).
Graine des tirages : 20261123. Les tirages eux-mêmes sont faits par les scripts cités dans chaque onglet « Méthode » ; leurs résultats sont
reportés en valeurs."""
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from B2_common import *
import hashlib, os, openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter as CL
PC = 'scripts/lot7-tables-virtuelles/out/pieces/'
O4 = O + 'B4/'
os.makedirs(O4, exist_ok=True)
D0 = 'scripts/lot7-tables-virtuelles/cache/entrees/'
NATIF = 'public/documents/caisse-enregistreuse/SOURCE-reglement-brut_2022-2025.xls'
SRC = {
    'C': ['17-annexe-c1-2022-2023.xls', '18-annexe-c2-2023-2024.xls', '19-annexe-c3-2024-2025.xls'],
    'H': ['ANNEXE-H1_liste-tickets_2022-2023.xls', 'ANNEXE-H2_liste-tickets_2023-2024.xls', 'ANNEXE-H3_liste-tickets_2024-2025.xls'],
    'E': ['14-annexe-e1-2022-2023.xls', '15-annexe-e2-2023-2024.xls', '16-annexe-e3-2024-2025.xls'],
    'F': ['20-annexe-f1-2022-2023.xls', '21-annexe-f2-2023-2024.xls', '22-annexe-f3-2024-2025.xls'],
    'B': ['24-annexe-b1-2022-2023.xls', '25-annexe-b2-2023-2024.xls', '26-annexe-b3-2024-2025.xls'],
}
LOT27 = D0 + 'lot27/'
PIECES = {
    '11': LOT27 + '11-rf-encaissements-couverts.xlsx',
    '92': LOT27 + '92-R2-tables-virtuelles-rangs-de-note-659-journees-tickets-zero-occupation.xlsx',
    '155': VC + F155,
    '156': VC + F156,
    '157': LOT27 + '157-R4-conversions-au-forfait-133-suites.xlsx',
}
_sha = {}
def sha(path):
    if path not in _sha:
        _sha[path] = hashlib.sha256(open(path, 'rb').read()).hexdigest()
    return _sha[path]
def src_rows(keys, pieces=(), natif=False):
    """Lignes (fichier, rôle, SHA-256) pour l'onglet Méthode."""
    role = {'C': 'annexes C : lignes d articles des additions', 'H': 'annexes H : liste des tickets (date, heure, n°, Z, totaux)',
            'E': 'annexes E : journal des événements (DEL, CON, RPR, TIR)', 'F': 'annexes F : lignes de règlement',
            'B': 'annexes B : quantités commandées par ticket'}
    prole = {'11': 'pièce 11 : liste des encaissements et couverts produite le 10 juillet 2026',
             '92': 'annexe n° 92 : rangs de note, journées, tickets à 0,00 €, occupation',
             '155': 'annexe n° 155 (R3) : tables vidées, traces, égalités, paiements séparés',
             '156': 'annexe n° 156 (R3) : tableau de la page 40, 37 tickets, 17 tickets',
             '157': 'annexe n° 157 (R4) : conversions au forfait, 133 suites'}
    piece = {'C': ((17, 'C-1'), (18, 'C-2'), (19, 'C-3')), 'H': ((30, 'H-1'), (31, 'H-2'), (32, 'H-3')), 'E': ((14, 'E-1'), (15, 'E-2'), (16, 'E-3')),
             'F': ((20, 'F-1'), (21, 'F-2'), (22, 'F-3')), 'B': ((24, 'B-1'), (25, 'B-2'), (26, 'B-3'))}
    out = []
    for k in keys:
        for f, (n, a) in zip(SRC[k], piece[k]):
            out.append((f, f'{role[k]} ; annexe {a} du service, produite sous l annexe n° {n} de la réponse (fichier lu sous son nom de travail)', sha(D0 + f)))
    if natif:
        out.append((os.path.basename(NATIF), 'export natif des règlements (colonnes etat et sy_uk), mêmes lignes que les annexes F', sha(NATIF)))
    for p in pieces:
        out.append((os.path.basename(PIECES[p]), prole[p], sha(PIECES[p])))
    return out
BOLD = Font(bold=True); BLUE = Font(color='1F4E9A'); TITLE = Font(bold=True, size=13)
HFILL = PatternFill('solid', fgColor='DDE6F0')
WRAP = Alignment(wrap_text=True, vertical='top')
def methode(wb, titre, objet, script, definitions, sources, onglets, limites, autres_scripts=()):
    ws = wb.active; ws.title = 'Méthode'
    r = 1
    ws.cell(r, 1, titre).font = TITLE; r += 2
    def block(h, lines):
        nonlocal r
        ws.cell(r, 1, h).font = BOLD; r += 1
        for l in lines:
            if isinstance(l, (tuple, list)):
                for j, v in enumerate(l, start=1):
                    c = ws.cell(r, j, v); c.alignment = WRAP
            else:
                c = ws.cell(r, 1, l); c.alignment = WRAP
            r += 1
        r += 1
    block('Objet', objet)
    block('Script et graine', [f'Script de construction : {script}.', 'Graine des tirages aléatoires : 20261123.']
          + [f'Résultats repris en valeurs du script : {s}.' for s in autres_scripts])
    block('Définitions', definitions)
    ws.cell(r, 1, 'Sources (empreinte SHA-256 du fichier lu)').font = BOLD; r += 1
    for j, h in enumerate(['Fichier', 'Contenu', 'SHA-256'], start=1):
        c = ws.cell(r, j, h); c.font = BOLD; c.fill = HFILL
    r += 1
    for f, rl, h in sources:
        ws.cell(r, 1, f); ws.cell(r, 2, rl).alignment = WRAP; ws.cell(r, 3, h); r += 1
    r += 1
    block('Onglets', onglets)
    block('Limites', limites)
    block('Conventions', ['Les onglets « Sources_… » portent des valeurs lues dans les fichiers ci-dessus (police bleue) ; les autres onglets calculent par formules.',
                          'Dates au format AAAA-MM-JJ ; minutes exprimées en minutes depuis 0 h (720 = 12 h 00) ; montants en euros TTC.',
                          'Classeur recalculé sous LibreOffice (mode sans interface) : aucune cellule en erreur.',
                          'Aucune affirmation n est faite sur le certificat du système de caisse.'])
    ws.column_dimensions['A'].width = 60; ws.column_dimensions['B'].width = 70; ws.column_dimensions['C'].width = 68
    return ws
def header(ws, cols, widths=None):
    for j, h in enumerate(cols, start=1):
        c = ws.cell(1, j, h); c.font = BOLD; c.fill = HFILL; c.alignment = WRAP
        ws.column_dimensions[CL(j)].width = (widths[j - 1] if widths else max(10, min(40, len(str(h)) + 2)))
    ws.freeze_panes = 'A2'
def put_df(ws, df, blue=True, start=2):
    """Écrit un DataFrame (valeurs) sous l'en-tête ; police bleue pour les sources."""
    for i, row in enumerate(df.itertuples(index=False), start=start):
        for j, v in enumerate(row, start=1):
            if isinstance(v, float) and np.isnan(v): v = None
            elif isinstance(v, (np.integer,)): v = int(v)
            elif isinstance(v, (np.floating,)): v = float(v)
            elif isinstance(v, (np.bool_,)): v = bool(v)
            c = ws.cell(i, j, v)
            if blue: c.font = BLUE
def fmt(ws, col, f, r0=2, r1=None):
    r1 = r1 or ws.max_row
    for r in range(r0, r1 + 1): ws[f'{col}{r}'].number_format = f
EUR = '#,##0.00'; PCT = '0.00'
