"""Annexe 175 (définitive) : les 2 359 tables vidées selon la chronologie (tableau 72 bis), reprise sur une note close dans les 60, 120 ou
240 minutes, profils des 160 et des 14 tables, 830 tickets sans article sans suppression à leur minute, 42 clôtures différées.
Sorties : pieces/175-R2-tables-videes-chronologie-et-ressaisie-differee.xlsx ; out/B4/04.txt"""
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from B4_common import *
NAME = '175-R2-tables-videes-chronologie-et-ressaisie-differee.xlsx'
C, E, F, H, A = load(); S = source()
log = open(O4 + '04.txt', 'w')
def p(*a): print(*a); print(*a, file=log)
hm = lambda t: f'{int(t) // 60:02d}:{int(t) % 60:02d}'
Pop = pd.read_csv(OUT2 + '04_tables.csv'); Pop = Pop.sort_values('N° de table').reset_index(drop=True)
R4 = pd.read_csv(O4 + '04a_reprise.csv')
N = H[(H.serie == 1) & (H.tc != 0)].sort_values(['date_ticket', 't', 'id']).reset_index(drop=True)
days = sorted(H.date_ticket.unique()); first_h = H.groupby('date_ticket').t.min()
D = E[E.typEven == 'DEL']; pk = set(zip(Pop.d, Pop.t))
Dt = D[[(d, t) in pk for d, t in zip(D.dateEven, D.t)]].sort_values(['dateEven', 't', 'id'])
CON = E[E.typEven == 'CON'].sort_values(['no_zEport', 't']); RPR = E[E.typEven == 'RPR'].sort_values(['dateEven', 't'])
p('tables', len(Pop), 'notes', len(N), 'DEL des minutes', len(Dt), 'CON', len(CON), 'RPR', len(RPR))
# 830 tickets : écart au DEL le plus proche du même Z, autres tickets sans article du même Z dans la fenêtre
Z = H[~H.dansC].copy(); dk = set(zip(D.dateEven, D.t)); Z['atm'] = [(d, t) in dk for d, t in zip(Z.date_ticket, Z.t)]
W8 = Z[~Z.atm].sort_values(['date_ticket', 't', 'id']).copy()
DZ = {z: g.t.values for z, g in D.groupby('no_zEport')}; ZZ = {z: g.t.values for z, g in Z.groupby('no_z_report')}
W8['ecart'] = [np.abs(DZ[z] - t).min() if z in DZ else np.nan for z, t in zip(W8.no_z_report, W8.t)]
for k in (1, 2, 5):
    W8[f'aut{k}'] = [int(((np.abs(ZZ[z] - t) <= k) & (ZZ[z] != t)).sum()) for z, t in zip(W8.no_z_report, W8.t)]
p('830', len(W8))
# 14 tables (c) : jour suivant et première note
ND = {d: g for d, g in N.groupby('date_ticket')}
c14 = Pop[Pop.cat == 'c'].copy(); info = []
for _, r in c14.iterrows():
    g = ND[r.d]; last = g.sort_values('t').iloc[-1]
    nxt = [dd for dd in sorted(ND) if dd > r.d][0]; gn = ND[nxt].sort_values('t').iloc[0]
    art = '; '.join(f'{l} x{q:g}' for l, q in C[C.id == gn.id][['libs', 'qte']].values)
    info.append(dict(tab=r['N° de table'], last_h=last.heure_ticket, last_id=int(last.id), nxt=nxt, nxt_h=gn.heure_ticket, nxt_id=int(gn.id), nxt_v=gn.tot_ttc, art=art))
c14 = pd.DataFrame(info)
M42 = pd.read_csv(OUT2 + '08_42.csv'); MJ = pd.read_csv(OUT + 'D03b_multijours.csv')[['id', 'maxprev']]
M42 = M42.merge(MJ, on='id', how='left')
# ================================================================ classeur
wb = openpyxl.Workbook()
methode(wb, 'Annexe n° 175 : les tables vidées selon la chronologie, et leur reprise sur une note encaissée',
  ['L identifiant d un ticket est attribué à sa création, avant sa clôture ; seul l ordre des clôtures se lit dans les fichiers. Cette annexe classe les 2 359 tables vidées selon les notes encaissées que la chronologie permet de leur associer (onglet « Chronologie »).',
   'Elle mesure, pour chaque table, si toutes ses lignes supprimées se retrouvent sur une même note encaissée du jour close dans les 60, 120 ou 240 minutes suivant le vidage, contre le même calcul refait un autre jour d ouverture à la même minute (onglet « Reprise ») ; la synthèse forme le tableau 72 bis (onglet « Synthese »).',
   'Elle décrit les 160 tables vidées avant la première note du jour, les 14 tables vidées après la dernière, les 830 tickets sans article clos sans suppression à leur minute et les 42 tickets à clôture différée.'],
  'B4_04_annexe_175.py',
  ['Table vidée : l une des 2 359 minutes de l annexe n° 155, onglet « Population » (recalculées dans l annexe n° 174) ; son ticket est le plus petit identifiant sans article clos à cette minute ; son montant est la somme des lignes « DEL » de la minute.',
   'Notes encaissées : tickets de la première série de total non nul (16 605), onglet « Sources_notes ».',
   'Classes : (a) aucune note encaissée du jour close au plus tard à la minute du vidage ; (c) sinon, aucune note d identifiant supérieur close au plus tard à la minute, et aucune note close à la minute ou après ; (b) aucune note d identifiant supérieur close au plus tard à la minute, mais une note close à la minute ou après ; reste : une note d identifiant supérieur (créée après la table) est close au plus tard à la minute du vidage (ordre de la page 18 possible).',
   'Reprise (inclusion totale) : chaque ligne « DEL » positive de la table est appariée, sans remise, à une ligne distincte d une même note encaissée du même ticket Z, close entre la minute du vidage et 60, 120 ou 240 minutes après, dont le montant ou le prix unitaire égale la ligne « DEL » ; valeurs lues dans les annexes C, puis dans les annexes B. Avec contrainte d identifiant : la note a un identifiant supérieur à celui de la table. À 80 % : au moins 80 % des lignes sont appariées.',
   'Même calcul un autre jour d ouverture : les mêmes lignes appliquées aux notes du 1er, 2e, 3e, 5e et 8e jour d ouverture suivant, à la même minute, sans contrainte d identifiant ; moyenne des décalages disponibles.',
   'Témoin : notes encaissées pour lesquelles aucune autre note d identifiant supérieur n est close au plus tard à leur minute.',
   '830 tickets : tickets sans article sans ligne « DEL » à leur minute. Tolérance de k minutes : une ligne « DEL » du même ticket Z à k minutes au plus, sans autre ticket sans article du même Z dans l intervalle. Classement du reste, dans cet ordre : dans les 30 minutes après une mise en route de la caisse (« CON » du même Z), premier ticket de la journée, à la minute d un événement « RPR », à la minute d une note encaissée de même rang, sinon résidu.',
   'Clôtures différées : tickets dont l identifiant est inférieur au plus grand identifiant d un ticket clos lors d une journée d ouverture précédente ; la borne de création est la dernière journée d ouverture où un identifiant supérieur était déjà clos, ou la date du préfixe sy_uk de l export natif ; test des prix : prix unitaire de chaque article comparé aux prix pratiqués pour le même libellé dans les 15 jours d ouverture autour de la création et autour de la clôture.'],
  src_rows(['H', 'E', 'C', 'B'], pieces=['155'], natif=True),
  ['Synthese : tableau 72 bis et chiffres du point 2.7.2 f ; Chronologie : 2 359 tables ; Reprise : 2 359 tables, trois fenêtres ;', 'Profil 160 et Tables 14 : tables des classes (a) et (c) ; Tickets 830 ; Clotures differees : 42 tickets ;',
   'Sources_notes (avec la colonne de calcul du témoin), Sources_jours, Sources_DEL, Sources_CON, Sources_RPR : valeurs lues dans les annexes H et E.'],
  ['Les fichiers ne lient pas une ligne supprimée à la note qui l aurait reprise : la reprise est mesurée par l égalité des montants, et comparée au même calcul un autre jour.',
   'L appariement des lignes (onglet « Reprise ») est calculé par le script et reporté en valeurs ; les agrégats sont des formules.',
   'L heure de clôture n est pas l heure de création ; seul l ordre des clôtures est observable.'],
  autres_scripts=['B4_04a_reprise.py (appariement des lignes, cinq décalages ; règle de B2_05_C5_ressaisie.py)', 'B2_01_vC_passerelle_egalites.py (146 égalités au centime, colonne « Égalité »)',
                  'B2_08_C12_42tickets.py et B1_D03b_multijours.py (42 clôtures différées, test des prix)'])
wsy = wb.create_sheet('Synthese')
# Sources_jours
wjo = wb.create_sheet('Sources_jours'); header(wjo, ['Date', 'Première clôture du jour, annexes H (min)', 'Première ligne (Sources_notes)', 'Notes encaissées du jour'])
nN = len(N) + 1; nJ = len(days) + 1
RN = lambda c: f'Sources_notes!${c}$2:${c}${nN}'
for i, d in enumerate(days, start=2):
    wjo.cell(i, 1, d).font = BLUE; wjo.cell(i, 2, int(first_h[d])).font = BLUE
    wjo.cell(i, 3, f'=IFERROR(MATCH(A{i},{RN("B")},0)+1,0)'); wjo.cell(i, 4, f'=COUNTIF({RN("B")},A{i})')
RJ = lambda c: f'Sources_jours!${c}$2:${c}${nJ}'
# Sources_notes
wn = wb.create_sheet('Sources_notes')
header(wn, ['Id', 'Date', 'Heure', 'Minute', 'Z', 'Rang', 'Total TTC', 'Première ligne du jour', 'Dernière ligne du jour',
            'Témoin (calcul) : aucune note d identifiant supérieur close au plus tard à sa minute (1 = oui)'], [8, 11, 7, 7, 7, 6, 9, 9, 9, 22])
for i, r in enumerate(N.itertuples(), start=2):
    for j, v in enumerate((int(r.id), r.date_ticket, r.heure_ticket, int(r.t), int(r.no_z_report), int(r.no_ticket), round(r.tot_ttc, 2)), start=1): wn.cell(i, j, v).font = BLUE
    wn.cell(i, 8, f'=INDEX({RJ("C")},MATCH(B{i},{RJ("A")},0))'); wn.cell(i, 9, f'=H{i}+INDEX({RJ("D")},MATCH(B{i},{RJ("A")},0))-1')
    wn.cell(i, 10, f'=IF(COUNTIFS(INDEX($A:$A,H{i}):INDEX($A:$A,I{i}),">"&A{i},INDEX($D:$D,H{i}):INDEX($D:$D,I{i}),"<="&D{i})=0,1,0)')
# Sources_DEL
wd = wb.create_sheet('Sources_DEL'); header(wd, ['Id événement', 'Date', 'Heure', 'Minute', 'Z', 'Montant'])
put_df(wd, Dt[['id', 'dateEven', 'heureEven', 't', 'no_zEport', 'amount']]); nD = len(Dt) + 1
RD = lambda c: f'Sources_DEL!${c}$2:${c}${nD}'
wco = wb.create_sheet('Sources_CON'); header(wco, ['Id événement', 'Date', 'Heure', 'Minute', 'Z'])
put_df(wco, CON[['id', 'dateEven', 'heureEven', 't', 'no_zEport']]); nCO = len(CON) + 1
wrp = wb.create_sheet('Sources_RPR'); header(wrp, ['Id événement', 'Date', 'Heure', 'Minute', 'Z'])
put_df(wrp, RPR[['id', 'dateEven', 'heureEven', 't', 'no_zEport']]); nRP = len(RPR) + 1
# Chronologie
wc = wb.create_sheet('Chronologie')
hc = ['N° de table', 'Date', 'Minute du vidage', 'Heure', 'Z', 'Id du ticket', 'Montant (DEL de la minute)', 'Lignes DEL positives', 'Première ligne du jour (Sources_notes)',
      'Notes encaissées du jour', 'Notes closes au plus tard à la minute', 'dont d identifiant supérieur', 'Notes closes à la minute ou après', 'Classe',
      'Première note du jour (min)', 'Dernière note du jour (min)', 'Délai jusqu à la première note du jour (min)', 'Depuis la dernière mise en route « CON » du même Z (min)',
      'Égalité au centime (146 égalités, 1 = oui)', 'Note d identifiant supérieur close au plus tard à la minute (1 = oui)', 'Note close à la minute ou après (1 = oui)']
header(wc, hc, [8, 11, 8, 7, 7, 8, 10, 8, 9, 8, 9, 9, 9, 8, 9, 9, 10, 10, 10, 10, 10])
RNg = lambda c, i: f'INDEX(Sources_notes!${c}:${c},I{i}):INDEX(Sources_notes!${c}:${c},I{i}+J{i}-1)'
for i, r in enumerate(Pop.itertuples(), start=2):
    for j, v in enumerate((int(r[1]), r.d, int(r.t), hm(r.t), int(r.z), int(r.tid)), start=1): wc.cell(i, j, v).font = BLUE
    wc.cell(i, 7, f'=SUMIFS({RD("F")},{RD("B")},B{i},{RD("D")},C{i})')
    wc.cell(i, 8, f'=COUNTIFS({RD("B")},B{i},{RD("D")},C{i},{RD("F")},">0")')
    wc.cell(i, 9, f'=IFERROR(INDEX({RJ("C")},MATCH(B{i},{RJ("A")},0)),0)'); wc.cell(i, 10, f'=IFERROR(INDEX({RJ("D")},MATCH(B{i},{RJ("A")},0)),0)')
    wc.cell(i, 11, f'=IF(J{i}=0,0,COUNTIFS({RNg("D", i)},"<="&C{i}))')
    wc.cell(i, 12, f'=IF(J{i}=0,0,COUNTIFS({RNg("D", i)},"<="&C{i},{RNg("A", i)},">"&F{i}))')
    wc.cell(i, 13, f'=IF(J{i}=0,0,COUNTIFS({RNg("D", i)},">="&C{i}))')
    wc.cell(i, 14, f'=IF(K{i}=0,"(a)",IF(L{i}=0,IF(M{i}=0,"(c)","(b)"),"reste"))')
    wc.cell(i, 15, f'=IF(J{i}=0,"",INDEX(Sources_notes!$D:$D,I{i}))'); wc.cell(i, 16, f'=IF(J{i}=0,"",INDEX(Sources_notes!$D:$D,I{i}+J{i}-1))')
    wc.cell(i, 17, f'=IF(J{i}=0,"",O{i}-C{i})')
    wc.cell(i, 18, f'=IF(COUNTIFS(Sources_CON!$E$2:$E${nCO},E{i},Sources_CON!$D$2:$D${nCO},"<="&C{i})=0,"",C{i}-_xlfn.MAXIFS(Sources_CON!$D$2:$D${nCO},Sources_CON!$E$2:$E${nCO},E{i},Sources_CON!$D$2:$D${nCO},"<="&C{i}))')
    wc.cell(i, 19, int(bool(r.egal_30)) if hasattr(r, 'egal_30') else None).font = BLUE
    wc.cell(i, 20, f'=IF(L{i}>0,1,0)'); wc.cell(i, 21, f'=IF(M{i}>0,1,0)')
fmt(wc, 'G', EUR); nc = len(Pop) + 1
# Reprise
wr = wb.create_sheet('Reprise')
hr = ['N° de table', 'Classe', 'Montant']
cols = []
for Wn in (60, 120, 240):
    hr += [f'{Wn} min : C totale, id supérieur', f'{Wn} min : C 80 %, id supérieur', f'{Wn} min : B totale, id supérieur', f'{Wn} min : B 80 %, id supérieur',
           f'{Wn} min : C totale, sans contrainte', f'{Wn} min : C 80 %, sans contrainte', f'{Wn} min : B totale, sans contrainte', f'{Wn} min : B 80 %, sans contrainte'] + \
          [f'{Wn} min : C totale, autre jour (+{k})' for k in (1, 2, 3, 5, 8)] + [f'{Wn} min : C totale, autre jour (moyenne)', f'{Wn} min : moyenne × montant']
header(wr, hr, [8, 8, 9] + [9] * (len(hr) - 3))
RW = {Wn: R4[R4.W == Wn].set_index('table') for Wn in (60, 120, 240)}
KEYS = ['c_tot', 'c_80', 'b_tot', 'b_80', 'c_tot_sansid', 'c_80_sansid', 'b_tot_sansid', 'b_80_sansid'] + [f'c_tot_d{k}' for k in (1, 2, 3, 5, 8)]
for i, r in enumerate(Pop.itertuples(), start=2):
    wr.cell(i, 1, int(r[1])).font = BLUE; wr.cell(i, 2, f'=Chronologie!N{i}'); wr.cell(i, 3, f'=Chronologie!G{i}')
    c0 = 4
    for Wn in (60, 120, 240):
        x = RW[Wn].loc[int(r[1])]
        for k, key in enumerate(KEYS):
            v = x[key]; wr.cell(i, c0 + k, None if pd.isna(v) else int(v)).font = BLUE
        a, b = CL(c0 + 8), CL(c0 + 12)
        wr.cell(i, c0 + 13, f'=IF(COUNT({a}{i}:{b}{i})=0,"",AVERAGE({a}{i}:{b}{i}))')
        wr.cell(i, c0 + 14, f'=IF({CL(c0 + 13)}{i}="",0,{CL(c0 + 13)}{i}*C{i})')
        c0 += 15
nr = len(Pop) + 1
col240 = {k: CL(4 + 30 + j) for j, k in enumerate(KEYS + ['moy', 'moyV'])}
RR = lambda key: f'Reprise!${col240[key]}$2:${col240[key]}${nr}'
# Synthese
header(wsy, ['Tableau 72 bis : classe', 'Tables', 'Montant', 'Toutes les lignes sur une note du jour close dans les 4 heures', 'Même calcul un autre jour (moyenne de 5 décalages)'], [70, 10, 14, 22, 22])
CH = lambda c: f'Chronologie!${c}$2:${c}${nc}'
cls = [('reste', 'Une note créée après la table est close au plus tard à la minute du vidage : ordre de la page 18 possible (reste)'),
       ('(b)', 'Seules des notes closes après le vidage, ou créées avant la table, peuvent la reprendre ((b))'),
       ('(a)', 'Vidée avant la première note encaissée du jour ((a))'), ('(c)', 'Vidée après la dernière note du jour, sans note créée après elle close avant ((c))')]
for k, (c, lab) in enumerate(cls, start=2):
    wsy.cell(k, 1, lab).alignment = WRAP; wsy.cell(k, 6, c)
    wsy.cell(k, 2, f'=COUNTIF({CH("N")},F{k})'); wsy.cell(k, 3, f'=SUMIF({CH("N")},F{k},{CH("G")})')
    wsy.cell(k, 4, f'=SUMIFS({RR("c_tot_sansid")},Reprise!$B$2:$B${nr},F{k})'); wsy.cell(k, 5, f'=SUMIFS({RR("moy")},Reprise!$B$2:$B${nr},F{k})')
wsy.cell(6, 1, 'Total').font = BOLD
for c in 'BCDE': wsy.cell(6, ' BCDE'.index(c) + 1, f'=SUM({c}2:{c}5)')
wsy.cell(1, 6, 'Code de classe').font = BOLD
ex = [(8, 'Excès sur le hasard, toutes classes : tables', '=D6-E6'),
      (9, 'Excès sur le hasard, toutes classes : montant', f'=SUMIF({RR("c_tot_sansid")},1,Reprise!$C$2:$C${nr})-SUM({RR("moyV")})'),
      (10, 'Excès sur le hasard, classe (a) : tables', '=D4-E4'),
      (11, 'Excès sur le hasard, classe (a) : montant', f'=SUMIFS(Reprise!$C$2:$C${nr},{RR("c_tot_sansid")},1,Reprise!$B$2:$B${nr},"(a)")-SUMIFS({RR("moyV")},Reprise!$B$2:$B${nr},"(a)")'),
      (12, 'Tables reprises par une note créée après elles (contrainte d identifiant, 4 heures)', f'=SUM({RR("c_tot")})'),
      (13, 'Montant de ces tables', f'=SUMIF({RR("c_tot")},1,Reprise!$C$2:$C${nr})'),
      (14, 'dont tables figurant parmi les 146 égalités au centime', f'=SUMPRODUCT(({RR("c_tot")}=1)*({CH("S")}=1))'),
      (15, 'Témoin : notes encaissées sans note d identifiant supérieur close au plus tard à leur minute', f'=SUM({RN("J")})'),
      (16, 'Notes encaissées', f'=COUNTA({RN("A")})'), (17, 'Part du témoin (%)', '=B15/B16*100'),
      (18, 'Tables qu une note encaissée du jour peut, par la chronologie, avoir reprises (reste et (b))', '=B2+B3'),
      (19, 'Montant de ces tables', '=C2+C3'),
      (20, 'Contrôle : les 2 359 tables, montant (annexe n° 174, onglet « Passerelle », ligne 15 : 180 003,94 €)', '=C6')]
for r, a, b in ex:
    wsy.cell(r, 1, a).alignment = WRAP; wsy.cell(r, 2, b)
for r in (9, 11, 13, 19, 20): wsy[f'B{r}'].number_format = EUR
for r in (8, 10): wsy[f'B{r}'].number_format = '0.00'
wsy['B17'].number_format = '0.0'
for r in range(2, 7): wsy[f'C{r}'].number_format = EUR; wsy[f'E{r}'].number_format = '0.00'
# fenêtres 60 et 120 min (information)
wsy.cell(22, 1, 'Même mesure à 60 et 120 minutes (information)').font = BOLD
for k, Wn in enumerate((60, 120), start=23):
    base = 4 + (0 if Wn == 60 else 15)
    a = CL(base + 4); m = CL(base + 13)
    wsy.cell(k, 1, f'{Wn} min : tables reprises sans contrainte (B), autre jour (C), avec contrainte d identifiant (D)')
    wsy.cell(k, 2, f'=SUM(Reprise!${a}$2:${a}${nr})'); wsy.cell(k, 3, f'=SUM(Reprise!${m}$2:${m}${nr})'); wsy.cell(k, 4, f'=SUM(Reprise!${CL(base)}$2:${CL(base)}${nr})')
    wsy[f'C{k}'].number_format = '0.00'
# Profil 160
wp = wb.create_sheet('Profil 160')
hp = ['N° de table', 'Date', 'Minute du vidage', 'Montant', 'Lignes DEL positives', 'Délai jusqu à la première note du jour (min)', 'Depuis la dernière mise en route « CON » (min)',
      'Tables (a) du même jour', 'Reprise 4 h, sans contrainte (1 = oui)', 'Même calcul un autre jour', 'Même calcul × montant']
header(wp, hp, [8, 11, 9, 9, 9, 12, 12, 9, 10, 10, 10])
A160 = Pop[Pop.cat == 'a']
for i, r in enumerate(A160.itertuples(), start=2):
    wp.cell(i, 1, int(r[1])).font = BLUE
    m = f'MATCH(A{i},Chronologie!$A$2:$A${nc},0)'
    for j, col in ((2, 'B'), (3, 'C'), (4, 'G'), (5, 'H'), (6, 'Q'), (7, 'R')):
        wp.cell(i, j, f'=INDEX(Chronologie!${col}$2:${col}${nc},{m})')
    n160 = len(A160) + 1
    wp.cell(i, 8, f'=COUNTIF($B$2:$B${n160},B{i})')
    wp.cell(i, 9, f'=INDEX({RR("c_tot_sansid")},MATCH(A{i},Reprise!$A$2:$A${nr},0))'); wp.cell(i, 10, f'=INDEX({RR("moy")},MATCH(A{i},Reprise!$A$2:$A${nr},0))')
    wp.cell(i, 11, f'=INDEX({RR("moyV")},MATCH(A{i},Reprise!$A$2:$A${nr},0))')
n160 = len(A160) + 1; fmt(wp, 'D', EUR, 2, n160)
P1 = [('Synthèse des 160 tables vidées avant la première note encaissée du jour', None),
      ('Tables', f'=COUNTA(A2:A{n160})'), ('Montant', f'=SUM(D2:D{n160})'),
      ('Vidées avant 10 h', f'=COUNTIF(C2:C{n160},"<600")'), ('Vidées entre 10 h et 12 h', f'=COUNTIFS(C2:C{n160},">=600",C2:C{n160},"<720")'),
      ('Vidées entre 12 h et 14 h', f'=COUNTIFS(C2:C{n160},">=720",C2:C{n160},"<840")'), ('Vidées à 14 h ou après', f'=COUNTIF(C2:C{n160},">=840")'),
      ('Délai médian jusqu à la première note encaissée du jour (min)', f'=MEDIAN(F2:F{n160})'),
      ('Montant médian', f'=MEDIAN(D2:D{n160})'), ('Premier quartile', f'=QUARTILE(D2:D{n160},1)'), ('Troisième quartile', f'=QUARTILE(D2:D{n160},3)'),
      ('Tables d une seule ligne DEL', f'=COUNTIF(E2:E{n160},1)'), ('Montant de ces tables', f'=SUMIF(E2:E{n160},1,D2:D{n160})'),
      ('Journées', f'=SUMPRODUCT(1/H2:H{n160})'), ('Journées à plusieurs tables', f'=SUMPRODUCT((H2:H{n160}>1)/H2:H{n160})'),
      ('Tables dans les 30 minutes qui suivent une mise en route « CON »', f'=COUNTIF(G2:G{n160},"<=30")'),
      ('Reprise sur une note close dans les 4 heures (sans contrainte d identifiant)', f'=SUM(I2:I{n160})'), ('Même calcul un autre jour', f'=SUM(J2:J{n160})'),
      ('Excès sur le hasard : tables', '=M17-M18'), ('Excès sur le hasard : montant', f'=SUMIF(I2:I{n160},1,D2:D{n160})-SUM(K2:K{n160})')]
for k, (a, b) in enumerate(P1, start=1):
    wp.cell(k, 12, a).font = BOLD if k == 1 else Font()
    if b: wp.cell(k, 13, b)
wp.column_dimensions['L'].width = 62
for k in (3, 9, 10, 11, 13, 20): wp[f'M{k}'].number_format = EUR
for k in (18, 19): wp[f'M{k}'].number_format = '0.00'
# Tables 14
wt = wb.create_sheet('Tables 14')
ht = ['N° de table', 'Date', 'Minute du vidage', 'Id du ticket', 'Montant', 'Lignes DEL positives', 'Dernière note du jour (heure)', 'Dernière note du jour (id)',
      'Notes d identifiant inférieur closes avant le vidage', 'Reprise 4 h, sans contrainte (1 = oui)', 'Reprise 4 h, avec contrainte (1 = oui)', 'Même calcul un autre jour',
      'Journée d ouverture suivante', 'Première note de cette journée (heure)', 'Id', 'Total', 'Articles de cette note']
header(wt, ht, [8, 11, 8, 8, 9, 8, 9, 9, 11, 10, 10, 10, 11, 9, 8, 9, 60])
for i, r in enumerate(c14.itertuples(), start=2):
    wt.cell(i, 1, int(r.tab)).font = BLUE
    m = f'MATCH(A{i},Chronologie!$A$2:$A${nc},0)'
    for j, col in ((2, 'B'), (3, 'C'), (4, 'F'), (5, 'G'), (6, 'H')): wt.cell(i, j, f'=INDEX(Chronologie!${col}$2:${col}${nc},{m})')
    wt.cell(i, 7, r.last_h).font = BLUE; wt.cell(i, 8, r.last_id).font = BLUE
    wt.cell(i, 9, f'=INDEX(Chronologie!$K$2:$K${nc},{m})')
    rm = f'MATCH(A{i},Reprise!$A$2:$A${nr},0)'
    wt.cell(i, 10, f'=INDEX({RR("c_tot_sansid")},{rm})'); wt.cell(i, 11, f'=INDEX({RR("c_tot")},{rm})'); wt.cell(i, 12, f'=INDEX({RR("moy")},{rm})')
    for j, v in ((13, r.nxt), (14, r.nxt_h), (15, r.nxt_id), (16, round(r.nxt_v, 2)), (17, r.art)): wt.cell(i, j, v).font = BLUE
n14 = len(c14) + 1; fmt(wt, 'E', EUR, 2, n14)
T1 = [('Synthèse des 14 tables vidées après la dernière note du jour', None), ('Tables', f'=COUNTA(A2:A{n14})'), ('Montant', f'=SUM(E2:E{n14})'),
      ('Vidées avant 20 h', f'=COUNTIF(C2:C{n14},"<1200")'), ('Reprises sur une note (4 h, sans contrainte)', f'=SUM(J2:J{n14})'), ('Même calcul un autre jour', f'=SUM(L2:L{n14})')]
for k, (a, b) in enumerate(T1, start=1):
    wt.cell(k, 19, a).font = BOLD if k == 1 else Font()
    if b: wt.cell(k, 20, b)
wt['T3'].number_format = EUR; wt['T6'].number_format = '0.00'; wt.column_dimensions['S'].width = 50
# Tickets 830
w8 = wb.create_sheet('Tickets 830')
h8 = ['Id', 'Date', 'Heure', 'Minute', 'Z', 'N°', 'Écart à la ligne DEL la plus proche du même Z (min)', 'Autres tickets sans article du même Z à ± 1 min', 'à ± 2 min', 'à ± 5 min',
      'Rattaché à ± 1 min (1 = oui)', 'Rattaché à ± 2 min', 'Rattaché à ± 5 min', 'Restant après ± 1 min', 'Restant après ± 2 min', 'Restant après ± 5 min',
      'Depuis la dernière « CON » du même Z (min)', 'Première clôture du jour (min)', 'Événement « RPR » à la minute', 'Note encaissée de même rang à la minute', 'Classement du reste']
header(w8, h8, [8, 11, 7, 7, 7, 5, 12, 10, 8, 8, 9, 9, 9, 9, 9, 9, 10, 10, 9, 9, 30])
for i, r in enumerate(W8.itertuples(), start=2):
    for j, v in enumerate((int(r.id), r.date_ticket, r.heure_ticket, int(r.t), int(r.no_z_report), int(r.no_ticket), None if pd.isna(r.ecart) else int(r.ecart), r.aut1, r.aut2, r.aut5), start=1):
        w8.cell(i, j, v).font = BLUE
    for j, (k, a) in enumerate(((1, 'H'), (2, 'I'), (5, 'J')), start=11): w8.cell(i, j, f'=IF(AND(G{i}<>"",G{i}<={k},{a}{i}=0),1,0)')
    w8.cell(i, 14, f'=IF(K{i}=1,0,1)'); w8.cell(i, 15, f'=IF(OR(K{i}=1,L{i}=1),0,1)'); w8.cell(i, 16, f'=IF(OR(K{i}=1,L{i}=1,M{i}=1),0,1)')
    w8.cell(i, 17, f'=IF(COUNTIFS(Sources_CON!$E$2:$E${nCO},E{i},Sources_CON!$D$2:$D${nCO},"<="&D{i})=0,"",D{i}-_xlfn.MAXIFS(Sources_CON!$D$2:$D${nCO},Sources_CON!$E$2:$E${nCO},E{i},Sources_CON!$D$2:$D${nCO},"<="&D{i}))')
    w8.cell(i, 18, f'=INDEX({RJ("B")},MATCH(B{i},{RJ("A")},0))')
    w8.cell(i, 19, f'=COUNTIFS(Sources_RPR!$B$2:$B${nRP},B{i},Sources_RPR!$D$2:$D${nRP},D{i})')
    w8.cell(i, 20, f'=COUNTIFS({RN("B")},B{i},{RN("D")},D{i},{RN("F")},F{i})')
    w8.cell(i, 21, f'=IF(P{i}=0,"",IF(AND(Q{i}<>"",N(Q{i})<=30),"dans les 30 min après un CON",IF(D{i}=R{i},"premier ticket de la journée",IF(S{i}>0,"à la minute d un RPR",IF(T{i}>0,"à la minute d une note de même rang","résidu")))))')
n8 = len(W8) + 1
K8 = [('Synthèse des 830 tickets sans article sans suppression à leur minute', None), ('Tickets', f'=COUNTA(A2:A{n8})'),
      ('Restants après tolérance de ± 1 min', f'=SUM(N2:N{n8})'), ('Restants après ± 2 min', f'=SUM(O2:O{n8})'), ('Restants après ± 5 min', f'=SUM(P2:P{n8})'),
      ('Rattachés à une suppression du même Z à 5 minutes au plus', '=W2-W5'),
      ('Restants : premier ticket de la journée', f'=COUNTIF(U2:U{n8},"premier ticket de la journée")'),
      ('Restants : dans les 30 min après un CON', f'=COUNTIF(U2:U{n8},"dans les 30 min après un CON")'),
      ('Restants : à la minute d un RPR', f'=COUNTIF(U2:U{n8},"à la minute d un RPR")'),
      ('Restants : à la minute d une note de même rang', f'=COUNTIF(U2:U{n8},"à la minute d une note de même rang")'),
      ('Restants : résidu', f'=COUNTIF(U2:U{n8},"résidu")'),
      ('Résidu : avant 10 h', f'=COUNTIFS(U2:U{n8},"résidu",D2:D{n8},"<600")'), ('Résidu : 10 h à 12 h', f'=COUNTIFS(U2:U{n8},"résidu",D2:D{n8},">=600",D2:D{n8},"<720")'),
      ('Résidu : 12 h à 14 h', f'=COUNTIFS(U2:U{n8},"résidu",D2:D{n8},">=720",D2:D{n8},"<840")'), ('Résidu : 14 h à 18 h', f'=COUNTIFS(U2:U{n8},"résidu",D2:D{n8},">=840",D2:D{n8},"<1080")'),
      ('Résidu : 18 h à 20 h', f'=COUNTIFS(U2:U{n8},"résidu",D2:D{n8},">=1080",D2:D{n8},"<1200")'), ('Résidu : 20 h et après', f'=COUNTIFS(U2:U{n8},"résidu",D2:D{n8},">=1200")')]
for k, (a, b) in enumerate(K8, start=1):
    w8.cell(k, 22, a).font = BOLD if k == 1 else Font()
    if b: w8.cell(k, 23, b)
w8.column_dimensions['V'].width = 58
# Clotures differees
wq = wb.create_sheet('Clotures differees')
hq = ['Id', 'Clôture', 'Rang', 'Série', 'Z', 'Total', 'Règlements', 'Plus grand identifiant clos lors d une journée précédente', 'Identifiant antérieur (1 = oui)',
      'Borne de création', 'Date du préfixe sy_uk (export natif)', 'Délai (jours)', 'Position à la clôture', 'DEL de la minute (tickets à 0,00 €)',
      'Articles au prix des deux périodes', 'Au prix de la seule clôture', 'Au prix de la seule création', 'Ni l un ni l autre', 'Exercice de création', 'Exercice de clôture', 'Changement d exercice (1 = oui)']
header(wq, hq, [8, 16, 5, 5, 6, 9, 22, 12, 9, 11, 11, 7, 20, 10, 9, 9, 9, 9, 11, 11, 9])
for i, r in enumerate(M42.itertuples(), start=2):
    vals = (int(r.id), r.cloture, int(r.rang), int(r.serie), int(r.z), float(r.total), None if pd.isna(r.reglements) else r.reglements, int(r.maxprev))
    for j, v in enumerate(vals, start=1): wq.cell(i, j, v).font = BLUE
    wq.cell(i, 9, f'=IF(A{i}<H{i},1,0)')
    for j, v in ((10, r.creation_bornee), (11, None if pd.isna(r.prefixe_syuk) else r.prefixe_syuk), (12, int(r.delai_j)), (13, r.position),
                 (14, None if pd.isna(r.DEL_minute) else float(r.DEL_minute)), (15, int(r.both)), (16, int(r.close_only)), (17, int(r.create_only)), (18, int(r.neither)),
                 (19, r.ex_creation), (20, r.ex_cloture)):
        wq.cell(i, j, v).font = BLUE
    wq.cell(i, 21, f'=IF(S{i}<>T{i},1,0)')
nq = len(M42) + 1; fmt(wq, 'F', EUR, 2, nq); fmt(wq, 'N', EUR, 2, nq)
Q1 = [('Synthèse des 42 tickets à clôture différée', None), ('Tickets', f'=COUNTA(A2:A{nq})'), ('dont identifiant antérieur vérifié', f'=SUM(I2:I{nq})'),
      ('Non nuls', f'=COUNTIF(F2:F{nq},"<>0")'), ('Montant des non nuls', f'=SUMIF(F2:F{nq},"<>0",F2:F{nq})'), ('À 0,00 €', f'=COUNTIF(F2:F{nq},0)'),
      ('À 0,00 € clos à la minute d un DEL', f'=COUNTIFS(F2:F{nq},0,N2:N{nq},">0")'), ('Montant DEL de ces minutes', f'=SUMIFS(N2:N{nq},F2:F{nq},0)'),
      ('Délai minimal (jours)', f'=MIN(L2:L{nq})'), ('Délai maximal (jours)', f'=MAX(L2:L{nq})'), ('Changements d exercice', f'=SUM(U2:U{nq})'),
      ('Tickets non nuls portant au moins un article au prix de la seule clôture', f'=COUNTIFS(F2:F{nq},"<>0",P2:P{nq},">0")'),
      ('Tickets non nuls portant au moins un article au prix de la seule création', f'=COUNTIFS(F2:F{nq},"<>0",Q2:Q{nq},">0")'),
      ('Ticket 53572 : total', f'=SUMIF(A2:A{nq},53572,F2:F{nq})'), ('Ticket 53572 : articles au prix de la seule clôture', f'=SUMIF(A2:A{nq},53572,P2:P{nq})'),
      ('Ticket 54679 : total', f'=SUMIF(A2:A{nq},54679,F2:F{nq})'), ('Ticket 54679 : articles au prix de la seule clôture', f'=SUMIF(A2:A{nq},54679,P2:P{nq})')]
for k, (a, b) in enumerate(Q1, start=1):
    wq.cell(k, 23, a).font = BOLD if k == 1 else Font()
    if b: wq.cell(k, 24, b)
for k in (5, 8, 14, 16): wq[f'X{k}'].number_format = EUR
wq.column_dimensions['W'].width = 62
order = ['Méthode', 'Synthese', 'Chronologie', 'Reprise', 'Profil 160', 'Tables 14', 'Tickets 830', 'Clotures differees', 'Sources_notes', 'Sources_jours', 'Sources_DEL', 'Sources_CON', 'Sources_RPR']
wb._sheets = [wb[n] for n in order]
wb.save(PC + NAME); p('écrit', PC + NAME)
