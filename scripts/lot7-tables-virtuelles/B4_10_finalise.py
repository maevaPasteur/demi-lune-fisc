"""Finalisation des annexes 172 à 175 : remplace chaque classeur de pieces/ par sa version recalculée sous LibreOffice (formules et
valeurs), puis contrôle : cellules en erreur, valeurs des cellules citées par la section 2.7 et par la spécification, absence de tiret
cadratin ou demi-cadratin et de vocabulaire interne, empreintes et tailles. Sortie : out/B4/10_controle.txt"""
import os, shutil, hashlib, re, openpyxl, json
PC = 'scripts/lot7-tables-virtuelles/out/pieces/'; RC = 'scripts/lot7-tables-virtuelles/out/B4/recalc/'
out = open('scripts/lot7-tables-virtuelles/out/B4/10_controle.txt', 'w')
def p(*a): print(*a); print(*a, file=out)
F1 = '172-R2-pointage-37-tickets-reglements-etat-9.xlsx'; F2 = '173-R2-libelles-comptes-comme-couverts-et-occupation.xlsx'
F3 = '174-R2-passerelle-tickets-tables-videes-reglements.xlsx'; F4 = '175-R2-tables-videes-chronologie-et-ressaisie-differee.xlsx'
for f in (F1, F2, F3, F4):
    assert os.path.getmtime(RC + f) > os.path.getmtime(PC + f), f'{f} : version recalculée plus ancienne que la construction'
    shutil.copy(RC + f, PC + f)
X = {  # (onglet, cellule) : (valeur attendue, décimales de comparaison)
 F1: {('Synthèse', 'B2'): 37, ('Synthèse', 'B3'): 55, ('Synthèse', 'B4'): 1958.26, ('Synthèse', 'B5'): 1590.26, ('Synthèse', 'B6'): 260, ('Synthèse', 'B7'): 90, ('Synthèse', 'B8'): 18,
      ('Synthèse', 'B9'): 32.45, ('Synthèse', 'B10'): 1607.38, ('Synthèse', 'B11'): 318.43, ('Synthèse', 'B12'): 35, ('Synthèse', 'B13'): 36, ('Synthèse', 'B14'): 35,
      ('Synthèse', 'B15'): 2715.02, ('Synthèse', 'B16'): 11, ('Synthèse', 'B17'): 820, ('Synthèse', 'B18'): 0.43, ('Synthèse', 'B19'): '[0 ; 2]', ('Synthèse', 'B20'): 0,
      ('Synthèse', 'B21'): 7, ('Synthèse', 'B22'): 5, ('Synthèse', 'B23'): 0.25, ('Synthèse', 'B24'): '[0 ; 1]', ('Synthèse', 'B25'): 40.0, ('Synthèse', 'B26'): 1867,
      ('Synthèse', 'B27'): 7, ('Synthèse', 'B28'): 453.34, ('Synthèse', 'B29'): 1817.59, ('Synthèse', 'B30'): 0, ('Synthèse', 'B31'): 1539.65, ('Synthèse', 'B32'): 277.94,
      ('Pointage', 'E37'): 1590.26, ('Pointage', 'I37'): 260, ('Pointage', 'M37'): 90, ('Pointage', 'Q37'): 18, ('CA_comptable', 'D5'): 1817.59},
 F2: {('Synthèse', 'B2'): 1269, ('Synthèse', 'B3'): (36368.5, 1), ('Synthèse', 'B4'): (28.66, 2), ('Synthèse', 'B5'): (61.00, 2), ('Synthèse', 'B6'): (61.18, 2), ('Synthèse', 'B7'): 33,
      ('Synthèse', 'B8'): (141.7, 1), ('Synthèse', 'B9'): (3.0, 1), ('Synthèse', 'B10'): (53.71, 2), ('Synthèse', 'B11'): (71.03, 2), ('Synthèse', 'B12'): 54,
      ('Synthèse', 'B13'): (24.71, 2), ('Synthèse', 'B14'): (34.10, 2), ('Synthèse', 'B15'): 735, ('Synthèse', 'B16'): 534, ('Synthèse', 'B17'): 7, ('Synthèse', 'B18'): 26,
      ('Synthèse', 'B19'): (61.52, 2), ('Synthèse', 'B20'): (60.15, 2), ('Synthèse', 'B21'): (61.35, 2), ('Synthèse', 'B22'): (26.68, 2), ('Synthèse', 'B23'): (27.84, 2),
      ('Synthèse', 'B26'): (37343.7, 1), ('Synthèse', 'C26'): (62.64, 2), ('Synthèse', 'D26'): 42, ('Synthèse', 'E26'): (146, 0),
      ('Synthèse', 'B27'): (36368.5, 1), ('Synthèse', 'C27'): (61.00, 2), ('Synthèse', 'D27'): 33, ('Synthèse', 'E27'): (141.7, 1),
      ('Synthèse', 'B28'): (35908.5, 1), ('Synthèse', 'C28'): (60.24, 2), ('Synthèse', 'D28'): 31, ('Synthèse', 'E28'): (140, 0),
      ('Synthèse', 'B29'): (33013.5, 1), ('Synthèse', 'C29'): (55.38, 2), ('Synthèse', 'D29'): 11, ('Synthèse', 'E29'): (123, 0),
      ('Synthèse', 'B30'): (30242.2, 1), ('Synthèse', 'C30'): (50.74, 2), ('Synthèse', 'D30'): 3, ('Synthèse', 'E30'): (106, 0),
      ('Synthèse', 'B31'): (38063.7, 1), ('Synthèse', 'C31'): (63.85, 2), ('Synthèse', 'D31'): 47, ('Synthèse', 'E31'): (146, 0),
      ('Synthèse', 'B33'): 2661, ('Synthèse', 'B34'): (65.46, 2), ('Synthèse', 'B35'): 51, ('Synthèse', 'B36'): (60.82, 2), ('Synthèse', 'B37'): (-7.3, 1), ('Synthèse', 'C37'): (5.9, 1),
      ('Rotation', 'Y2'): 42, ('Rotation', 'Y3'): 21, ('Rotation', 'Y4'): 141, ('Rotation', 'Y5'): (67, 0), ('Rotation', 'Y6'): (90, 0), ('Rotation', 'Y7'): (102, 0),
      ('Rotation', 'Y8'): 36, ('Rotation', 'Y9'): 6, ('Rotation', 'Y10'): (58, 0), ('Rotation', 'Y11'): (78, 0), ('Rotation', 'Y12'): (111, 0)},
 F3: {**{('Passerelle', f'B{r}'): v for r, v in zip(range(2, 45), [19903, 6848, 6630, 6425, 3281, 3279, 2, 0, 16624, 2449, 2362, 3, 2359, 180003.94, 830, 37, 1958.26, 37, 21302,
        430763.15, 0, 17, 1190, 1096, 995, 1188, 1096, 995, 953, 795, 701, 922, 776, 661, 235, 301, 294, 2, 28, 7, 637, 659, 645])},
      ('Passerelle', 'C33'): 67238.64, ('Passerelle', 'C34'): 60381.00, ('Passerelle', 'C35'): 52384.30, ('Passerelle', 'C42'): 637, ('Passerelle', 'C43'): 659, ('Passerelle', 'C44'): 659},
 F4: {('Synthese', 'B2'): 1509, ('Synthese', 'C2'): 128070.08, ('Synthese', 'D2'): 74, ('Synthese', 'E2'): (27.2, 1),
      ('Synthese', 'B3'): 676, ('Synthese', 'C3'): 42933.36, ('Synthese', 'D3'): 100, ('Synthese', 'E3'): (56.45, 2),
      ('Synthese', 'B4'): 160, ('Synthese', 'C4'): 7978.70, ('Synthese', 'D4'): 47, ('Synthese', 'E4'): (23.25, 2),
      ('Synthese', 'B5'): 14, ('Synthese', 'C5'): 1021.80, ('Synthese', 'D5'): 0, ('Synthese', 'E5'): (0.2, 1),
      ('Synthese', 'B6'): 2359, ('Synthese', 'C6'): 180003.94, ('Synthese', 'D6'): 221, ('Synthese', 'E6'): (107.1, 1),
      ('Synthese', 'B8'): (113.9, 1), ('Synthese', 'B9'): (5246.72, 2), ('Synthese', 'B10'): (23.75, 2), ('Synthese', 'B11'): (967.42, 2), ('Synthese', 'B12'): 169,
      ('Synthese', 'B13'): 5178.25, ('Synthese', 'B14'): 33, ('Synthese', 'B15'): 6595, ('Synthese', 'B16'): 16605, ('Synthese', 'B17'): (39.7, 1), ('Synthese', 'B18'): 2185,
      ('Synthese', 'B19'): 171003.44,
      ('Profil 160', 'M2'): 160, ('Profil 160', 'M4'): 3, ('Profil 160', 'M5'): 143, ('Profil 160', 'M6'): 14, ('Profil 160', 'M8'): (17.5, 1), ('Profil 160', 'M9'): 45.10,
      ('Profil 160', 'M10'): 21.50, ('Profil 160', 'M11'): (66.475, 3), ('Profil 160', 'M12'): 34, ('Profil 160', 'M13'): 536.20, ('Profil 160', 'M14'): (136, 6), ('Profil 160', 'M15'): (21, 6),
      ('Profil 160', 'M16'): 9, ('Profil 160', 'M17'): 47, ('Profil 160', 'M18'): (23.25, 2), ('Profil 160', 'M19'): (23.75, 2), ('Profil 160', 'M20'): (967.42, 2),
      ('Tables 14', 'T2'): 14, ('Tables 14', 'T3'): 1021.80, ('Tables 14', 'T4'): 0, ('Tables 14', 'T5'): 0, ('Tables 14', 'T6'): (0.2, 1),
      **{('Tickets 830', f'W{r}'): v for r, v in zip(range(2, 18), [830, 665, 613, 548, 282, 64, 29, 15, 2, 438, 0, 59, 76, 45, 191, 67])},
      **{('Clotures differees', f'X{r}'): v for r, v in zip(range(2, 18), [42, 42, 29, 2150.30, 13, 9, 429.65, 1, 546, 2, 3, 0, 49.80, 1, 76.40, 1])}}}
BAD = re.compile('[–—]'); INTERNE = re.compile(r'(?i)\bagent|vérificateur|simul|débat|risque|version de travail|coordinat|avocat|défense')
res = {}
for f in (F1, F2, F3, F4):
    wb = openpyxl.load_workbook(PC + f, data_only=True); wf = openpyxl.load_workbook(PC + f)
    err = [(ws.title, c.coordinate, c.value) for ws in wb.worksheets for row in ws.iter_rows() for c in row if isinstance(c.value, str) and (c.value.startswith('#') or c.value.startswith('Err:'))]
    nform = sum(1 for ws in wf.worksheets for row in ws.iter_rows() for c in row if isinstance(c.value, str) and c.value.startswith('='))
    txt = [(ws.title, c.coordinate, c.value) for ws in wf.worksheets for row in ws.iter_rows() for c in row if isinstance(c.value, str) and not c.value.startswith('=')]
    dash = [t for t in txt if BAD.search(t[2])]; inter = [t for t in txt if INTERNE.search(t[2])]
    h = hashlib.sha256(open(PC + f, 'rb').read()).hexdigest(); sz = os.path.getsize(PC + f)
    p(f'\n{f}\n  taille {sz} octets ; SHA-256 {h}\n  onglets : {wb.sheetnames}\n  formules {nform} ; cellules en erreur {len(err)} {err[:5]} ; tirets {len(dash)} {dash[:3]} ; vocabulaire interne {len(inter)} {inter[:3]}')
    p('  dimensions : ' + ' ; '.join(f'{ws.title} {ws.max_row} x {ws.max_column}' for ws in wb.worksheets))
    ok = 0
    for (sh, cell), exp in X[f].items():
        v = wb[sh][cell].value
        if isinstance(exp, tuple): e, d = exp; good = isinstance(v, (int, float)) and round(v, d) == round(e, d)
        elif isinstance(exp, str): e = exp; good = v == exp
        else: e = exp; good = isinstance(v, (int, float)) and abs(v - exp) < 0.005
        ok += good
        p(f'  {"OK " if good else "ÉCART"} {sh}!{cell} = {v!r} (attendu {e})')
    p(f'  cellules contrôlées {len(X[f])} ; conformes {ok}')
    res[f] = dict(taille=sz, sha256=h, onglets=wb.sheetnames, formules=nform, erreurs=len(err), controles=len(X[f]), conformes=ok)
json.dump(res, open('scripts/lot7-tables-virtuelles/out/B4/10_controle.json', 'w'), ensure_ascii=False, indent=1)
# tableau 74 lu dans l onglet Services
wb = openpyxl.load_workbook(PC + F2, data_only=True); rows = sorted([r for r in wb['Services'].iter_rows(min_row=2, values_only=True)], key=lambda r: -r[7])[:12]
p('\nTableau 74 (Services, tri sur la colonne H) : ' + ' ; '.join(f'{r[0]} {r[1]} {r[4]} {r[6]:g} {r[7]:.1f} %' for r in rows))
