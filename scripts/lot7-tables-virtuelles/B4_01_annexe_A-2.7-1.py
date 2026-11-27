"""Annexe 172 (définitive) : pointage des 37 tickets à 0,00 € porteurs de règlements (état 9).
Sorties : pieces/172-R2-pointage-37-tickets-reglements-etat-9.xlsx ; out/B4/01.txt"""
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from B4_common import *
from itertools import combinations
NAME = '172-R2-pointage-37-tickets-reglements-etat-9.xlsx'
C, E, F, H, A = load(); S = source(); S['id'] = S.id.astype(int)
log = open(O4 + '01.txt', 'w')
def p(*a): print(*a); print(*a, file=log)
F['t'] = F.heureTicket.map(tm); F['mc'] = (F.montant * 100).round().astype(int)
e9 = set(S[S.etat.astype(str) == '9'].id)
F['etat'] = np.where(F.id.isin(e9), 9, 0)
days = sorted(F[F.etat == 9].dateTicket.unique()); p('journées', len(days))
Fd = F[F.dateTicket.isin(days)].copy().sort_values(['dateTicket', 'heureTicket', 'id', 'ligneXLS', 'ex'])
Fd['rang'] = Fd.groupby('id').cumcount() + 1
# lignes de même montant sur une note de la première série du même Z (fenêtre -90 / +180 min) : règle du script B2_02
R02 = pd.read_csv(OUT2 + '02_lignes.csv')
dbl = R02[R02.i_meme_ligne == 1][['id', 'mode', 'montant']]
Fd['double'] = 0
for _, r in dbl.iterrows():
    ix = Fd[(Fd.id == r.id) & (Fd.mod_regl == r['mode']) & (Fd.montant.round(2) == round(r.montant, 2)) & (Fd.double == 0)].index[:1]
    Fd.loc[ix, 'double'] = 1
p('lignes double', int(Fd.double.sum()), Fd[Fd.double == 1].montant.sum())
# DEL des minutes de clôture des 37 tickets
T37 = H[H.id.isin(e9)].sort_values(['date_ticket', 'heure_ticket', 'id'])
keys = set(zip(T37.date_ticket, T37.t))
D = E[(E.typEven == 'DEL')].copy()
Dk = D[[(d, t) in keys for d, t in zip(D.dateEven, D.t)]].sort_values(['dateEven', 't', 'id'])
# tables vidées (2 359)
Pop = pd.read_csv(OUT2 + '01_tables.csv')
# notes de la première série des 35 journées (pour la recherche de contrepartie des soldes ronds)
N1 = H[(H.serie == 1) & (H.tc != 0) & H.date_ticket.isin(days)].sort_values(['date_ticket', 'heure_ticket', 'id'])
# somme de 2 ou 3 lignes en espèces du jour égale à la différence (valeur calculée ici)
Cn = pd.read_csv(OUT2 + '02_tickets.csv')
F1 = F[F.id.isin(set(H[(H.serie == 1) & (H.tc != 0)].id))]
esp23 = {}
for _, r in Cn.iterrows():
    d = int(r['diff'])
    if d > 0 and d % 1000 == 0:
        day = str(pd.to_datetime(r['Date']).date())
        esp = F1[(F1.dateTicket == day) & (F1.mod_regl == 'ESP')].mc.values.tolist()
        esp23[int(r.id)] = 'oui' if any(sum(c) == d for k in (2, 3) if len(esp) >= k for c in combinations(esp, k)) else 'non'
p('esp23', esp23)
# ---------------------------------------------------------------- classeur
wb = openpyxl.Workbook()
methode(wb, 'Annexe n° 172 : pointage des 37 tickets à 0,00 € porteurs de règlements (état 9)',
  ['Les annexes H comptent 37 tickets clôturés à 0,00 € sans ligne d article qui portent pourtant des lignes de règlement dans les annexes F (55 lignes, 1 958,26 €). L export natif des règlements les marque d un état 9.',
   'Cette annexe donne, journée par journée et mode par mode, les règlements de ces 35 journées avec et sans l état 9, pour pointage sur les remises de carte et les bordereaux (onglet « Pointage »), et, ticket par ticket, le contenu de la table vidée à la minute de clôture comparé au règlement (onglet « Tickets »).',
   'La grille est à compléter des remises du terminal de paiement et des bordereaux de titres-restaurant et de chèques-vacances de ces 35 journées : le verdict s affiche alors par formule.'],
  'B4_01_annexe_172.py',
  ['État 9 : valeur 9 de la colonne etat de l export natif des règlements ; elle porte sur 55 lignes, celles des 37 tickets.',
   'Première série : lignes de règlement des notes encaissées (hors état 9). Total « sans » : règlements hors état 9 ; total « avec » : règlements avec état 9.',
   'Contenu de la table : somme des lignes « DEL » de la minute de clôture du ticket, même date et même minute (règle de l annexe n° 156, onglet « Contenu_37 », colonne H).',
   'Multiple de 10 € : différence positive (contenu moins règlement) multiple exact de 10,00 €.',
   'Part exacte : une ligne de règlement ou le règlement total égale le contenu multiplié par k / n (n de 2 à 8, k de 1 à n − 1), à 0,01 € près ; « au centime » : égalité exacte.',
   'Ligne de même montant : ligne état 9 dont le montant figure, au même mode, sur une note de la première série du même ticket Z close entre 90 minutes avant et 180 minutes après (information).',
   'Valeurs attendues au hasard : 1 000 permutations des règlements (multiples de 10 €) ou des contenus (parts exactes) entre les 37 tickets, graine 20261123.',
   'Taux de base : notes de la première série réglées en plusieurs lignes dont le total moins une ligne est un multiple de 10 €.',
   'Exercices : 1er avril au 31 mars.'],
  src_rows(['F', 'H', 'E'], pieces=['156'], natif=True),
  ['Pointage : une ligne par journée (lignes 2 à 36), totaux ligne 37 ; colonnes à remplir T à W ; verdicts X à AA.',
   'Tickets : une ligne par ticket (lignes 2 à 38).', 'CA_comptable : règlements état 9 non couverts par l écart entre la comptabilité et les tickets.',
   'Synthèse : chiffres repris par la section 2.7.', 'Sources_F : lignes de règlement des 35 journées ; Sources_DEL : lignes « DEL » des minutes de clôture des 37 tickets ;',
   'Sources_notes : notes de la première série des 35 journées ; Sources_tables_videes : les 2 359 tables vidées (date, minute) ; Sources_CA_comptable : valeurs de l annexe n° 156, onglet « CA_comptable ».'],
  ['Le contenu d une table vidée est lu sur les lignes « DEL » de sa minute : les fichiers ne portent ni le libellé ni la quantité des articles retirés.',
   'Les remises bancaires et les bordereaux ne sont pas dans les fichiers de caisse : le verdict reste vide tant qu ils ne sont pas saisis.'],
  autres_scripts=['B2_02_C1_reglements37.py (valeurs attendues au hasard, taux de base, lignes de même montant)'])
# Sources_F
ws = wb.create_sheet('Sources_F')
cols = ['Id', 'Date', 'Heure', 'N°', 'Z', 'Exercice', 'Mode', 'Montant', 'État (export natif)', 'Rang de la ligne dans le ticket', 'Même montant sur une note du même Z (1 = oui)']
header(ws, cols)
put_df(ws, Fd[['id', 'dateTicket', 'heureTicket', 'no_ticket', 'no_zReport', 'ex', 'mod_regl', 'montant', 'etat', 'rang', 'double']])
nF = len(Fd) + 1; fmt(ws, 'H', EUR)
# Sources_DEL
ws = wb.create_sheet('Sources_DEL'); header(ws, ['Id événement', 'Date', 'Heure', 'Minute', 'Z', 'Montant'])
put_df(ws, Dk[['id', 'dateEven', 'heureEven', 't', 'no_zEport', 'amount']]); nD = len(Dk) + 1; fmt(ws, 'F', EUR)
# Sources_notes
ws = wb.create_sheet('Sources_notes'); header(ws, ['Id', 'Date', 'Heure', 'N°', 'Z', 'Total TTC'])
put_df(ws, N1[['id', 'date_ticket', 'heure_ticket', 'no_ticket', 'no_z_report', 'tot_ttc']]); nN = len(N1) + 1; fmt(ws, 'F', EUR)
# Sources_tables_videes
ws = wb.create_sheet('Sources_tables_videes'); header(ws, ['N° de table', 'Date', 'Minute', 'Id du ticket (plus petit de la minute)', 'Montant'])
Pv = Pop[['N° de table', 'd', 't', 'tid', 'V']].copy(); Pv['V'] = Pv.V / 100
put_df(ws, Pv); nP = len(Pv) + 1; fmt(ws, 'E', EUR)
# Sources_CA_comptable
wbx = openpyxl.load_workbook(PIECES['156'], data_only=True); rows = list(wbx['CA_comptable'].iter_rows(values_only=True))
ws = wb.create_sheet('Sources_CA_comptable')
for i, r in enumerate(rows, start=1):
    for j, v in enumerate(r, start=1):
        c = ws.cell(i, j, round(v, 2) if isinstance(v, float) else v); c.font = BOLD if i == 1 else BLUE
ws.column_dimensions['A'].width = 70
ecart_row = [i for i, r in enumerate(rows, start=1) if r[0] and str(r[0]).startswith('Écart')][0]
# Pointage
wp = wb.create_sheet('Pointage', 1)
modes = [('CB', 'CB'), ('TR', 'TR'), ('CHV', 'CHV'), ('ESP', 'ESP')]
hdr = ['Date', 'Exercice', 'Ticket Z']
for m, _ in modes: hdr += [f'{m} première série (hors état 9)', f'{m} état 9', f'{m} total sans état 9', f'{m} total avec état 9']
hdr += ['Remise TPE du jour (à remplir)', 'Bordereau CRT, titres-restaurant (à remplir)', 'Bordereau ANCV, chèques-vacances (à remplir)', 'Espèces remises (à remplir)',
        'Verdict CB', 'Verdict TR', 'Verdict CHV', 'Verdict ESP']
header(wp, hdr, [12, 11, 9] + [13] * 16 + [16] * 4 + [11] * 4)
rF = lambda c: f'Sources_F!${c}$2:${c}${nF}'
for i, d in enumerate(days, start=2):
    wp.cell(i, 1, d)
    wp.cell(i, 2, f'=IF(A{i}<"2023-04-01","2022-2023",IF(A{i}<"2024-04-01","2023-2024","2024-2025"))')
    wp.cell(i, 3, f'=_xlfn.MINIFS({rF("E")},{rF("B")},A{i})')
    for k, (m, _) in enumerate(modes):
        c0 = 4 + 4 * k
        a, b, s, w = (CL(c0 + x) for x in range(4))
        wp.cell(i, c0, f'=SUMIFS({rF("H")},{rF("B")},$A{i},{rF("G")},"{m}",{rF("I")},0)')
        wp.cell(i, c0 + 1, f'=SUMIFS({rF("H")},{rF("B")},$A{i},{rF("G")},"{m}",{rF("I")},9)')
        wp.cell(i, c0 + 2, f'={a}{i}')
        wp.cell(i, c0 + 3, f'={a}{i}+{b}{i}')
    for k, (m, _) in enumerate(modes):
        rem = CL(20 + k); s = CL(4 + 4 * k + 2); w = CL(4 + 4 * k + 3)
        wp.cell(i, 24 + k, f'=IF({rem}{i}="","",IF(ABS({rem}{i}-{s}{i})<0.005,"sans",IF(ABS({rem}{i}-{w}{i})<0.005,"avec","autre")))')
nr = len(days) + 1; tr = nr + 1
wp.cell(tr, 1, 'Total'); wp.cell(tr, 1).font = BOLD
for c in range(4, 24): wp.cell(tr, c, f'=SUM({CL(c)}2:{CL(c)}{nr})')
for c in range(4, 24): fmt(wp, CL(c), EUR, 2, tr)
# Tickets
wt = wb.create_sheet('Tickets', 2)
th = ['Id du ticket', 'Date', 'Heure de clôture', 'Minute', 'Ticket Z', 'Exercice', 'Lignes de règlement (mode et montant)', 'Nombre de lignes', 'Règlement total',
      'Ligne 1', 'Ligne 2', 'Ligne 3', 'Ligne 4', 'Ligne 5', 'Ligne 6', 'Lignes « DEL » de la minute', 'Contenu de la table (DEL de la minute)', 'Différence (contenu − règlement)',
      'Différence positive (1 = oui)', 'Multiple de 10 € (1 = oui)', 'Part exacte k / n à 0,01 € (1 = oui)', 'Part exacte au centime (1 = oui)', 'Referme une table vidée (1 = oui)',
      'Lignes de même montant sur une note du même Z', 'Note du jour de ce total (multiples de 10 €)', 'Ligne de règlement du jour de ce montant (multiples de 10 €)', 'Somme de 2 ou 3 lignes en espèces du jour de ce montant (multiples de 10 €)']
header(wt, th, [10, 11, 9, 8, 8, 10, 30, 8, 11] + [9] * 6 + [9, 12, 12, 9, 9, 10, 10, 10, 10, 14, 14, 16])
def part(v, cref, tol):
    n = '{2,3,4,5,6,7,8}'; kmax = '{1,2,3,4,5,6,7}'
    k = f'ROUND(ROUND({v}*100,0)*{n}/ROUND({cref}*100,0),0)'
    return f'SUMPRODUCT((ABS(ROUND({v}*100,0)-ROUND({cref}*100,0)*{k}/{n})<={tol})*({k}>=1)*({k}<={kmax}))'
for i, r in enumerate(T37.itertuples(), start=2):
    lines = Fd[Fd.id == r.id]
    wt.cell(i, 1, int(r.id)); wt.cell(i, 2, r.date_ticket); wt.cell(i, 3, r.heure_ticket); wt.cell(i, 4, int(r.t)); wt.cell(i, 5, int(r.no_z_report))
    for c in range(1, 6): wt.cell(i, c).font = BLUE
    wt.cell(i, 6, f'=IF(B{i}<"2023-04-01","2022-2023",IF(B{i}<"2024-04-01","2023-2024","2024-2025"))')
    wt.cell(i, 7, ' ; '.join(f'{m} {v:.2f}'.replace('.', ',') for m, v in zip(lines.mod_regl, lines.montant))).font = BLUE
    wt.cell(i, 8, f'=COUNTIFS({rF("A")},A{i},{rF("I")},9)')
    wt.cell(i, 9, f'=SUMIFS({rF("H")},{rF("A")},A{i},{rF("I")},9)')
    for k in range(6):
        wt.cell(i, 10 + k, f'=IF(H{i}>={k + 1},SUMIFS({rF("H")},{rF("A")},$A{i},{rF("J")},{k + 1}),"")')
    wt.cell(i, 16, f'=COUNTIFS(Sources_DEL!$B$2:$B${nD},B{i},Sources_DEL!$D$2:$D${nD},D{i})')
    wt.cell(i, 17, f'=SUMIFS(Sources_DEL!$F$2:$F${nD},Sources_DEL!$B$2:$B${nD},B{i},Sources_DEL!$D$2:$D${nD},D{i})')
    wt.cell(i, 18, f'=ROUND(Q{i}-I{i},2)')
    wt.cell(i, 19, f'=IF(R{i}>0,1,0)')
    wt.cell(i, 20, f'=IF(AND(S{i}=1,MOD(ROUND(R{i}*100,0),1000)=0),1,0)')
    vals = [f'I{i}'] + [f'N(J{i})'.replace('J', CL(10 + k)) for k in range(6)]
    vals = [f'I{i}'] + [f'N({CL(10 + k)}{i})' for k in range(6)]
    for col, tol in ((21, '1.0000001'), (22, '0.0000001')):
        wt.cell(i, col, f'=IF(Q{i}<=0,0,IF(' + '+'.join(part(v, f'Q{i}', tol) for v in vals) + '>0,1,0))')
    wt.cell(i, 23, f'=IF(COUNTIFS(Sources_tables_videes!$B$2:$B${nP},B{i},Sources_tables_videes!$C$2:$C${nP},D{i})>0,1,0)')
    wt.cell(i, 24, f'=SUMIFS({rF("K")},{rF("A")},A{i},{rF("I")},9)')
    wt.cell(i, 25, f'=IF(T{i}=1,IF(SUMPRODUCT((Sources_notes!$B$2:$B${nN}=B{i})*(ROUND(Sources_notes!$F$2:$F${nN}*100,0)=ROUND(R{i}*100,0)))>0,"oui","non"),"")')
    wt.cell(i, 26, f'=IF(T{i}=1,IF(SUMPRODUCT(({rF("B")}=B{i})*(ROUND({rF("H")}*100,0)=ROUND(R{i}*100,0))*({rF("I")}=0))>0,"oui","non"),"")')
    if int(r.id) in esp23:
        c = wt.cell(i, 27, esp23[int(r.id)]); c.font = BLUE
nt = len(T37) + 1
for c in ['I', 'J', 'K', 'L', 'M', 'N', 'O', 'Q', 'R']: fmt(wt, c, EUR, 2, nt)
# CA_comptable
wc = wb.create_sheet('CA_comptable', 3)
header(wc, ['Exercice', 'Écart : comptabilité hors 706800 − tickets de la première série (annexe n° 156)', 'Règlements état 9', 'Règlements état 9 non couverts par l écart (au moins)'], [12, 40, 18, 30])
for i, (ex, col) in enumerate([('2022-2023', 'B'), ('2023-2024', 'C'), ('2024-2025', 'D')], start=2):
    wc.cell(i, 1, ex); wc.cell(i, 2, f'=ROUND(Sources_CA_comptable!{col}{ecart_row},2)')
    wc.cell(i, 3, f'=SUMIFS({rF("H")},{rF("F")},A{i},{rF("I")},9)'); wc.cell(i, 4, f'=MAX(0,ROUND(C{i}-B{i},2))')
wc.cell(5, 1, 'Trois exercices'); [wc.cell(5, c, f'=SUM({CL(c)}2:{CL(c)}4)') for c in (2, 3, 4)]
for c in 'BCD': fmt(wc, c, EUR, 2, 5)
# Synthèse
wsy = wb.create_sheet('Synthèse', 4)
header(wsy, ['Grandeur', 'Valeur', 'Source ou formule'], [70, 16, 60])
T = 'Tickets!'
syn = [
 ('Tickets à 0,00 € porteurs de règlements (état 9)', f'=COUNTA({T}A2:A{nt})', 'Tickets'),
 ('Lignes de règlement état 9', f'=COUNTIF({rF("I")},9)', 'Sources_F'),
 ('Montant des règlements état 9', f'=SUMIF({rF("I")},9,{rF("H")})', 'Sources_F'),
 ('dont CB', f'=Pointage!E{tr}', 'Pointage, ligne des totaux'), ('dont TR', f'=Pointage!I{tr}', 'Pointage'), ('dont CHV', f'=Pointage!M{tr}', 'Pointage'), ('dont ESP', f'=Pointage!Q{tr}', 'Pointage'),
 ('dont 2022-2023', '=CA_comptable!C2', 'CA_comptable'), ('dont 2023-2024', '=CA_comptable!C3', 'CA_comptable'), ('dont 2024-2025', '=CA_comptable!C4', 'CA_comptable'),
 ('Journées portant au moins une ligne état 9', f'=COUNTA(Pointage!A2:A{nr})', 'Pointage'),
 ('Tickets qui referment une table vidée', f'=SUM({T}W2:W{nt})', 'Tickets, colonne W'),
 ('Tickets dont le contenu dépasse le règlement (différence positive)', f'=SUM({T}S2:S{nt})', 'Tickets, colonne S'),
 ('Somme de ces différences positives', f'=SUMIF({T}S2:S{nt},1,{T}R2:R{nt})', 'Tickets, colonne R'),
 ('Différences positives multiples exacts de 10 €', f'=SUM({T}T2:T{nt})', 'Tickets, colonne T'),
 ('Somme de ces différences', f'=SUMIF({T}T2:T{nt},1,{T}R2:R{nt})', 'Tickets, colonne R'),
 ('Multiples de 10 € attendus au hasard (moyenne de 1 000 permutations des règlements)', 0.43, 'valeur : script B2_02_C1_reglements37.py, graine 20261123'),
 ('Intervalle à 95 % de ces tirages', '[0 ; 2]', 'idem ; part des tirages au moins égaux à 11 : 0,000'),
 ('Multiples de 10 € ayant une contrepartie (note, ligne de règlement ou somme de 2 ou 3 lignes en espèces du même jour)', f'=COUNTIF({T}Y2:AA{nt},"oui")', 'Tickets, colonnes Y à AA'),
 ('Tickets réglés pour une part exacte k / n de leur contenu, à 0,01 € près', f'=SUM({T}U2:U{nt})', 'Tickets, colonne U'),
 ('dont au centime', f'=SUM({T}V2:V{nt})', 'Tickets, colonne V'),
 ('Parts exactes attendues au hasard (moyenne de 1 000 permutations des contenus)', 0.25, 'valeur : script B2_02_C1_reglements37.py, graine 20261123'),
 ('Intervalle à 95 % de ces tirages', '[0 ; 1]', 'idem'),
 ('Taux de base : notes de la première série réglées en plusieurs lignes dont le total moins une ligne est un multiple de 10 € (%)', 40.0, 'valeur : script B2_02_C1_reglements37.py'),
 ('Nombre de ces notes réglées en plusieurs lignes', 1867, 'idem'),
 ('Lignes état 9 de même montant sur une note du même Z (information)', f'=SUM({rF("K")})', 'Sources_F, colonne K'),
 ('Montant de ces lignes', f'=SUMIF({rF("K")},1,{rF("H")})', 'Sources_F'),
 ('Règlements état 9 non couverts par l écart comptable, exercice par exercice (au moins)', '=CA_comptable!D5', 'CA_comptable'),
 ('dont 2022-2023', '=CA_comptable!D2', ''), ('dont 2023-2024', '=CA_comptable!D3', ''), ('dont 2024-2025', '=CA_comptable!D4', ''),
]
for i, (a, b, c) in enumerate(syn, start=2):
    wsy.cell(i, 1, a).alignment = WRAP; x = wsy.cell(i, 2, b); wsy.cell(i, 3, c).alignment = WRAP
    if not isinstance(b, str) or not b.startswith('='): x.font = BLUE
for i, (a, b, c) in enumerate(syn, start=2):
    if any(w in a for w in ('Montant', 'Somme', 'dont CB', 'dont TR', 'dont CHV', 'dont ESP', 'dont 20', 'non couverts')): wsy[f'B{i}'].number_format = EUR
wb.save(PC + NAME); p('écrit', PC + NAME)
