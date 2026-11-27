"""Annexe 173 (définitive) : libellés comptés comme couverts, couverts et occupation par service, variantes (tableau 73 bis),
couverts identifiables des tables vidées, variante de calendrier, étalement des services (onglet Rotation).
Sorties : pieces/173-R2-libelles-comptes-comme-couverts-et-occupation.xlsx ; out/B4/02.txt ; out/B4/02_notes_DPc.csv (couverts par note,
définition retenue, réutilisé pour les données du site)"""
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from B4_common import *
NAME = '173-R2-libelles-comptes-comme-couverts-et-occupation.xlsx'
C, E, F, H, A = load(); P = plats()
log = open(O4 + '02.txt', 'w')
def p(*a): print(*a); print(*a, file=log)
s2 = set(H[H.serie == 2].id); z0n = set(H[(H.serie == 1) & (H.tc == 0)].id); EXCL = s2 | z0n
Cx = C[~C.id.isin(EXCL)].copy(); Cx['svc'] = np.where(Cx.heure.map(tm) < 1080, 'midi', 'soir')
L7 = pd.read_csv(OUT2 + '07_libelles.csv'); cats = pd.read_csv(OUT + 'D05_categories.csv')[['lib', 'categorie']]
DPc = set(L7[L7.DP_corrigee == 1].lib); DPl = set(L7[L7.DP == 1].lib); DPs = DPc - {'PAYSANNE'}
p('libellés : société', len(P), 'DPc', len(DPc), 'DP', len(DPl), 'DPc sans PAYSANNE', len(DPs))
# ---------- Libellés
Lg = pd.read_pickle('scripts/lot5-tva/cache/B3_articles.pkl'); nat = dict(zip(Lg.ref.astype(str), Lg.nature))
Cx['nat'] = Cx.ref.astype(str).map(nat)
lib = Cx.groupby('libs').agg(pu=('pu', 'median'), notes=('id', 'nunique'), qte=('qte', 'sum'),
                             nat=('nat', lambda s: s.mode()[0] if s.notna().any() else 'indéterminé')).reset_index().rename(columns={'libs': 'lib'})
lib = lib.merge(L7[['lib', 'part_avec_autre_plat']], on='lib', how='left').merge(cats, on='lib', how='left')
LARGE = {'Croûtes Morilles', 'MACHON GOURMET', 'Chèvre  chaud', 'Feuilleté Forestier', 'Escargots de Bourgog', 'Assortiment charcute', 'Jamhon Persillé', 'Jambon sec'}
ING = {'Œuf', 'Jambon Blanc', 'Jambon Sec', 'Jambon sec', 'Comté', 'Champignons frais', 'Fromage de Chèvre', 'Bacon', 'Ratatouille', 'Morbier', 'Bleu de Gex', 'Oignons',
       'Pommes de Terre', 'Noix', 'Miel', 'Tomates', 'Crème Fraîche', 'Cancoillotte', 'PIGNONS PIN', 'ECLATS NOISETTES', 'Amandes grillées', 'Saucisse de Morteau',
       'SAUCE JURASSIENNE', 'Sauce Forestière', 'Sauce Morilles', 'Salade Verte', 'Beurre', 'Beurre Salé', 'Emmental', 'Raclette', 'Lardons', 'Poulet', 'Saumon'}
DESS = ['crêpe', 'crepe', 'glace', 'coupe', 'creme brulee', 'baba', 'pavlova', 'dessert', 'churros', 'crumble', 'chantilly', 'coulis', 'sauce choco', 'flambée',
        'poire au sirop', 'pommes cuites', 'banane', 'nutella', 'confiture', 'caramel', 'chocolat', 'crême de marrons', 'salidou', 'noix de coco', 'dames vertes']
ACC = P - DPc
def motif(r):
    l = r.lib
    if l in ACC: return 'accompagnement (prix médian < 10 € et au moins 90 % des notes avec un autre plat compté)'
    if l in P:
        c = str(r.categorie)
        return {'plat': 'plat', 'menu ou formule': 'menu ou formule', 'menu enfant': 'menu enfant', 'galette (inférence)': 'galette', 'fondue': 'plat (fondue)', 'salade': 'plat (salade)'}.get(c, c)
    if 'boisson' in str(r.nat) or 'bière' in str(r.nat): return 'boisson'
    if l in LARGE: return 'entrée ou planche'
    if l in ING: return 'ingrédient ou supplément de galette'
    if any(k in l.lower() for k in DESS): return 'dessert'
    return 'autre aliment non compté (dessert, accompagnement ou supplément, non distingués)'
lib['motif'] = lib.apply(motif, axis=1)
lib['c_DPc'] = lib.lib.isin(DPc).astype(int); lib['c_92'] = lib.lib.isin(P).astype(int); lib['c_DP'] = lib.lib.isin(DPl).astype(int); lib['c_DPs'] = lib.lib.isin(DPs).astype(int)
lib = lib.sort_values(['c_92', 'qte'], ascending=[False, False]).reset_index(drop=True)
gn = C[C.libs == 'Galette nature'].id.unique(); gs = C[C.id.isin(gn)].groupby('id').libs.apply(set)
n_ing = int(sum(1 for i in gn if len(gs[i] & ING) > 0)); p('Galette nature (toutes les additions des annexes C)', len(gn), n_ing)
gnp = Cx[Cx.libs == 'Galette nature'].id.unique(); p('Galette nature (périmètre des notes encaissées)', len(gnp), int(sum(1 for i in gnp if len(gs[i] & ING) > 0)))
lib['ing'] = np.where(lib.lib == 'Galette nature', n_ing, np.nan); lib['ngal'] = np.where(lib.lib == 'Galette nature', len(gn), np.nan)
p('motifs', lib.motif.value_counts().to_dict())
# ---------- Lignes
G = Cx.groupby(['date', 'svc', 'libs']).qte.sum().reset_index()
# ---------- bornes par note
MENU = {"Menu 'Demi Lune'", "Menu 'Galette'", 'Menu Bourguignon', 'Menu Franc-Comtois', 'Menu Végétarien', 'Menu du Dahu', 'Menu du jour', 'Formule Express', 'FORMULE EXPRESS',
        'Formule à 11', 'Formule à 12.5', 'Formule à 14', 'Plat du jour'}
ENF = {"Menu 'Enfant'", 'Menu Bambin'}; FON = {'Fondue Forestière', 'Fondue Jurassienne', 'Fondue des Gourmets', 'FONDUE VIN JAUNE'}; SAL = {'Salade Régionale', 'Salade Végétarienne', 'Salade Franc-Comptoi'}
GAL = {'Galette nature', 'GALETTE FORESTIERE', 'Complète', 'BARBEULENET', 'CABRICHOU', 'CANCOINE', 'DADOULET', 'DAHU', 'ECRESSI', 'FOULETOT', 'FRELEE', 'LIGOUSE', 'LOURNETTE',
       'NIOLERIES', 'NOIRAUD', 'PAYSANNE', 'PEUTE', 'TANTELIN', 'VERDELET'}
def cat(l):
    for n, s in [('menu', MENU), ('enfant', ENF), ('fondue', FON), ('salade', SAL), ('galette', GAL)]:
        if l in s: return n
    return 'plat'
x = Cx[Cx.libs.isin(P)].assign(c=lambda d: d.libs.map(cat))
v3 = x.groupby(['id', 'c']).qte.sum().groupby('id').max()
pl = x.groupby('id').qte.sum(); en = Cx[Cx.libs.isin(LARGE)].groupby('id').qte.sum()
lg = pd.concat([pl, en], axis=1).fillna(0).max(axis=1)
Nn = A[~A.id.isin(EXCL)].copy(); Nn['svc'] = np.where(Nn.t < 1080, 'midi', 'soir')
Nn['v3'] = Nn.id.map(v3).fillna(0); Nn['lg'] = Nn.id.map(lg).fillna(0)
Nn['dpc'] = Nn.id.map(Cx[Cx.libs.isin(DPc)].groupby('id').qte.sum()).fillna(0)
Nn = Nn.sort_values(['date', 't', 'id'])
Nn[['id', 'date', 'heure', 't', 'svc', 'ex', 'dpc']].to_csv(O4 + '02_notes_DPc.csv', index=False)
p('notes', len(Nn), 'DPc', Nn.dpc.sum(), 'V3', Nn.v3.sum(), 'large', Nn.lg.sum())
# ---------- DEL identifiables comme plats (définition retenue) dans les 2 359 tables vidées
D = E[E.typEven == 'DEL']; xd = D[(D.ac > 0) & (D.ac < 100000)].copy()
C['pc'] = (C.pu * 100).round().astype(int)
carte = {ex: g[g.pc > 0].groupby('pc').libs.apply(set) for ex, g in C.groupby('ex')}
xd['libs_prix'] = [', '.join(sorted(carte[ex][ac])) if ac in carte[ex].index else '' for ex, ac in zip(xd.ex, xd.ac)]
xd['plat'] = [(ac in carte[ex].index) and carte[ex][ac] <= DPc for ex, ac in zip(xd.ex, xd.ac)]
Pop = pd.read_csv(OUT2 + '04_tables.csv'); pk = set(zip(Pop.d, Pop.t))
xd = xd[np.array([(d, t) in pk for d, t in zip(xd.dateEven, xd.t)]) & xd.plat.values].copy()
xd['svc'] = np.where(xd.t < 1080, 'midi', 'soir'); xd = xd.sort_values(['dateEven', 't', 'id'])
p('DEL plats', len(xd))
# ---------- services (pièce 92), rotation (pièce 11)
S92 = pd.read_pickle(Q + 'S92.pkl')
P11 = pd.read_pickle(Q + 'P11.pkl'); P11['svc'] = np.where(P11.t < 1080, 'midi', 'soir'); P11 = P11.sort_values(['date', 'svc', 't', 'id']).reset_index(drop=True)
CP = [('2022-07-14', '14 juillet', ''), ('2023-07-14', '14 juillet', ''), ('2024-07-14', '14 juillet', ''),
      ('2022-09-30', 'Week-end gourmand du Chat Perché', 'https://www.cdt-jura.fr/wp-content/uploads/2022/07/jura-tourisme-DP-automne-2022.pdf'),
      ('2022-10-01', 'Week-end gourmand du Chat Perché', 'idem'), ('2022-10-02', 'Week-end gourmand du Chat Perché', 'idem'),
      ('2023-09-30', 'Week-end gourmand du Chat Perché', 'https://www.doledujura.fr/fileadmin/sortir-a-dole-agenda-2023/05.septembre-octobre-2023/Sortir_%C3%A0_Dole_-_Septembre_Octobre_2023_NET.pdf'),
      ('2023-10-01', 'Week-end gourmand du Chat Perché', 'idem'),
      ('2024-09-27', 'Week-end gourmand du Chat Perché', 'https://doledujura.fr/fileadmin/sortir-a-dole-agenda-2024/05.septembre-octobre-2024/SAD_52.pdf'),
      ('2024-09-28', 'Week-end gourmand du Chat Perché', 'idem'), ('2024-09-29', 'Week-end gourmand du Chat Perché', 'idem')]
# ================================================================ classeur
wb = openpyxl.Workbook()
methode(wb, 'Annexe n° 173 : libellés comptés comme couverts, couverts et occupation de l espace ouvert',
  ['Cette annexe compte les couverts note par note dans le détail des annexes C, service par service, et les rapporte aux places de l espace ouvert.',
   'Chaque libellé des annexes C est classé (onglet « Libellés », colonne G modifiable) ; les couverts et l occupation se recalculent par formules (onglets « Lignes », « Services », « Synthèse »).',
   'Elle donne aussi les variantes de définition (tableau 73 bis), les couverts identifiables dans les tables vidées, une variante de calendrier et l étalement dans le temps des services les plus chargés (onglet « Rotation »).'],
  'B4_02_annexe_173.py',
  ['Couvert (définition retenue) : plat principal, menu, formule ou menu enfant figurant sur une note encaissée de la première série ; les quantités partagées s additionnent (0,5 + 0,5 = 1).',
   'Sont exclus les boissons, entrées, planches et desserts, et les cinq libellés de prix médian inférieur à 10 € présents avec un autre plat compté dans au moins 90 % des notes qui les portent : Saucisse de Morteau, Steak haché, NOIRAUD, Salade Franc-Comptoi, VERDELET (54 libellés comptés).',
   'Galette nature : comptée ; additions des annexes C qui la portent et, parmi elles, celles qui portent aussi au moins un ingrédient de galette, colonnes L et M de l onglet « Libellés » (toutes séries ; 887 et 880 sur les seules notes encaissées de la première série). Ingrédients cherchés : ' + ', '.join(sorted(ING)) + '.',
   'Périmètre : notes encaissées de la première série portant des lignes ; exclus : les 17 tickets non nuls de la seconde série (non réglés) et les 2 notes entièrement à 0,00 €.',
   'Service : midi si la note est close avant 18 h, soir sinon. Espace ouvert (règle de l annexe n° 92) : terrasse, 48 places, de mai à août ; intérieur, 46 places, les autres mois.',
   'Calendrier de juillet (variante) : terrasse de mai au 15 septembre, et les services des 14 juillet et des week-ends gourmands du Chat Perché (onglet « Sources_calendrier »).',
   'Occupation d un service : couverts / places × 100. Occupation moyenne : moyenne des taux des 1 269 services ; rapport des sommes : total des couverts / total des places.',
   'Liste de la réponse de juillet : les 59 libellés comptés par la société (annexe n° 92), colonne H de l onglet « Libellés » ; notes encaissées seules.',
   'Exclusion de tout libellé presque toujours accompagné : la règle des 90 % appliquée sans condition de prix (colonne J).',
   'Borne basse : par note, la plus grande des sommes de quantités par catégorie de plats (menus, menus enfants, fondues, salades, galettes, autres plats), liste de juillet.',
   'Borne haute : par note, le plus grand du nombre de plats de la liste de juillet et du nombre d entrées et planches (' + ', '.join(sorted(LARGE)) + ').',
   'Couverts identifiables des tables vidées : lignes « DEL » positives (moins de 1 000 €) des 2 359 tables vidées dont le montant égale un prix pratiqué dans l exercice par des libellés tous comptés (définition retenue) ; une ligne vaut un couvert.',
   'Rotation : pour chaque service, maxima des couverts des notes closes dans une fenêtre glissante de 60, 90 ou 120 minutes, avec la liste et les couverts de la pièce 11 et les places de l annexe n° 92.',
   'Motif (colonne I) : pour les libellés non comptés, classement par la nature de l article (boisson) ou par le libellé (inférence).'],
  src_rows(['C', 'H', 'E'], pieces=['11', '92', '155']),
  ['Synthèse : B2 à B23 (définition retenue), A25:E31 (tableau 73 bis), B33 à B37 (tables vidées, calendrier, écarts au repère).',
   'Libellés : 324 libellés ; Lignes : quantités par journée, service et libellé ; Services : 1 269 services ; Bornes_par_note : couverts par note des deux bornes ;',
   'DEL_plats : lignes « DEL » identifiables comme plats ; Rotation et Rotation_notes : étalement des services ; Sources_calendrier : dates du 14 juillet et du Chat Perché.'],
  ['Le classement d un libellé est une définition : il est modifiable (colonne G) et son effet se lit dans « Services » et « Synthèse ». Les bornes et les tables vidées sont calculées avec la définition retenue et ne suivent pas une modification de la colonne G.',
   'L heure de clôture d une note n est pas l heure d arrivée des clients.',
   'Les jours de pluie, où le service revient à l intérieur, ne sont pas identifiables dans les fichiers.',
   'Le repère de 58 % (Observatoire FIDUCIAL 2025, restauration traditionnelle) est un point de comparaison dont la définition n est pas publiée.'],
  autres_scripts=['B2_07_C9_couverts_DP.py (classement D-P et D-P corrigée des 59 libellés, catégories des bornes)', 'B1_D13_jours_exc.py (dates publiques du Chat Perché)'])
# --- Synthèse (onglet 2), rempli plus bas
wsy = wb.create_sheet('Synthèse')
# --- Libellés
wl = wb.create_sheet('Libellés')
header(wl, ['Libellé', 'PU médian', 'Catégorie (59 libellés de la société)', 'Notes', 'Quantité', 'Part des notes avec un autre plat compté', 'Compté (modifiable : 1 ou 0)',
            'Compté, liste de la réponse de juillet (annexe n° 92)', 'Motif', 'Compté, exclusion de tout libellé presque toujours accompagné', 'Compté, « Paysanne » classée parmi les entrées',
            'Additions des annexes C portant ce libellé (toutes séries)', 'dont portant aussi un ingrédient de galette', 'Part (%)'], [24, 9, 22, 8, 10, 12, 12, 14, 40, 14, 14, 14, 14, 9])
for i, r in enumerate(lib.itertuples(), start=2):
    vals = [r.lib, round(r.pu, 2), None if pd.isna(r.categorie) else r.categorie, int(r.notes), round(r.qte, 2),
            None if pd.isna(r.part_avec_autre_plat) else round(r.part_avec_autre_plat, 3), int(r.c_DPc), int(r.c_92), r.motif, int(r.c_DP), int(r.c_DPs)]
    for j, v in enumerate(vals, start=1):
        c = wl.cell(i, j, v)
        if j != 7: c.font = BLUE
    if not pd.isna(r.ing):
        wl.cell(i, 12, int(r.ngal)).font = BLUE; wl.cell(i, 13, int(r.ing)).font = BLUE; wl.cell(i, 14, f'=M{i}/L{i}*100'); wl[f'N{i}'].number_format = '0.0'
nlib = len(lib) + 1
# --- Lignes
wn = wb.create_sheet('Lignes')
header(wn, ['Date', 'Service', 'Libellé', 'Quantité', 'Quantité comptée (définition, colonne G)', 'Quantité comptée, liste de juillet', 'Quantité comptée, exclusion de tout libellé accompagné', 'Quantité comptée, « Paysanne » entrée'], [11, 8, 24, 9, 14, 14, 14, 14])
LR = f'Libellés!$A$2:$K${nlib}'
for i, r in enumerate(G.itertuples(), start=2):
    wn.cell(i, 1, r.date).font = BLUE; wn.cell(i, 2, r.svc).font = BLUE; wn.cell(i, 3, r.libs).font = BLUE; wn.cell(i, 4, round(r.qte, 4)).font = BLUE
    for j, col in ((5, 7), (6, 8), (7, 10), (8, 11)):
        wn.cell(i, j, f'=D{i}*IFERROR(VLOOKUP(C{i},{LR},{col},0),0)')
nl = len(G) + 1
# --- Bornes_par_note
wbn = wb.create_sheet('Bornes_par_note')
header(wbn, ['Id', 'Date', 'Heure', 'Service', 'Borne basse (par note)', 'Borne haute (par note)'])
put_df(wbn, Nn[['id', 'date', 'heure', 'svc', 'v3', 'lg']]); nb = len(Nn) + 1
# --- DEL_plats
wd = wb.create_sheet('DEL_plats')
header(wd, ['Id événement', 'Date', 'Heure', 'Minute', 'Service', 'Exercice', 'Montant de la ligne', 'Libellés pratiqués à ce prix dans l exercice'], [10, 11, 8, 8, 8, 10, 10, 60])
put_df(wd, xd[['id', 'dateEven', 'heureEven', 't', 'svc', 'ex', 'amount', 'libs_prix']]); ndl = len(xd) + 1
# --- Sources_calendrier
wcal = wb.create_sheet('Sources_calendrier'); header(wcal, ['Date', 'Événement', 'Source publique'], [12, 34, 100])
for i, (d, e, u) in enumerate(CP, start=2):
    for j, v in enumerate((d, e, u), start=1): wcal.cell(i, j, v).font = BLUE
ncal = len(CP) + 1
# --- Services
wsv = wb.create_sheet('Services')
hs = ['Date', 'Service', 'Mois', 'Exercice', 'Espace ouvert', 'Places', 'Couverts (définition, colonne G)', 'Occupation (%)', 'Au-delà de 100 % (1 = oui)',
      'Couverts, liste de juillet', 'Occupation, liste de juillet (%)', 'Couverts, exclusion de tout libellé accompagné', 'Occupation (%)', 'Couverts, « Paysanne » entrée', 'Occupation (%)',
      'Couverts, borne basse', 'Occupation (%)', 'Couverts, borne haute', 'Occupation (%)', 'Couverts identifiables des tables vidées', 'Occupation si aucun n était ressaisi (%)',
      'Espace, calendrier de juillet', 'Places, calendrier de juillet', 'Occupation, calendrier de juillet (%)']
header(wsv, hs, [11, 8, 6, 10, 10, 7] + [11] * 18)
rg = lambda sh, c, n: f'{sh}!${c}$2:${c}${n}'
for i, r in enumerate(S92[['date', 'service']].itertuples(), start=2):
    wsv.cell(i, 1, r.date).font = BLUE; wsv.cell(i, 2, r.service).font = BLUE
    wsv.cell(i, 3, f'=VALUE(MID(A{i},6,2))')
    wsv.cell(i, 4, f'=IF(A{i}<"2023-04-01","2022-2023",IF(A{i}<"2024-04-01","2023-2024","2024-2025"))')
    wsv.cell(i, 5, f'=IF(AND(C{i}>=5,C{i}<=8),"terrasse","intérieur")')
    wsv.cell(i, 6, f'=IF(E{i}="terrasse",48,46)')
    for j, lc in ((7, 'E'), (10, 'F'), (12, 'G'), (14, 'H')):
        wsv.cell(i, j, f'=SUMIFS({rg("Lignes", lc, nl)},{rg("Lignes", "A", nl)},$A{i},{rg("Lignes", "B", nl)},$B{i})')
    for j, bc in ((16, 'E'), (18, 'F')):
        wsv.cell(i, j, f'=SUMIFS({rg("Bornes_par_note", bc, nb)},{rg("Bornes_par_note", "B", nb)},$A{i},{rg("Bornes_par_note", "D", nb)},$B{i})')
    wsv.cell(i, 8, f'=G{i}/F{i}*100'); wsv.cell(i, 9, f'=IF(H{i}>100,1,0)')
    for j in (11, 13, 15, 17, 19): wsv.cell(i, j, f'={CL(j - 1)}{i}/$F{i}*100')
    wsv.cell(i, 20, f'=COUNTIFS({rg("DEL_plats", "B", ndl)},$A{i},{rg("DEL_plats", "E", ndl)},$B{i})')
    wsv.cell(i, 21, f'=(G{i}+T{i})/F{i}*100')
    wsv.cell(i, 22, f'=IF(OR(AND(C{i}>=5,C{i}<=8),AND(C{i}=9,VALUE(RIGHT(A{i},2))<=15),COUNTIF({rg("Sources_calendrier", "A", ncal)},A{i})>0),"terrasse","intérieur")')
    wsv.cell(i, 23, f'=IF(V{i}="terrasse",48,46)'); wsv.cell(i, 24, f'=G{i}/W{i}*100')
ns = len(S92) + 1
for c in ['H', 'K', 'M', 'O', 'Q', 'S', 'U', 'X']: fmt(wsv, c, PCT)
# --- Synthèse
header(wsy, ['Indicateur (définition retenue sauf mention)', 'Valeur', 'Valeur (suite)'], [78, 14, 14])
SV = lambda c: rg('Services', c, ns)
rows = {2: ('Services', f'=COUNTA({SV("A")})'), 3: ('Couverts', f'=SUM({SV("G")})'), 4: ('Couverts par service', '=B3/B2'),
        5: ('Occupation moyenne (moyenne des taux, %)', f'=AVERAGE({SV("H")})'), 6: ('Occupation (rapport des sommes, %)', f'=SUM({SV("G")})/SUM({SV("F")})*100'),
        7: ('Services au-delà de 100 % des places', f'=SUM({SV("I")})'), 8: ('Occupation maximale (%)', f'=MAX({SV("H")})'),
        9: ('Écart de l occupation moyenne au repère de 58 % (points)', '=B5-58'),
        10: ('Occupation moyenne, intérieur (%)', f'=AVERAGEIF({SV("E")},"intérieur",{SV("H")})'), 11: ('Occupation moyenne, terrasse (%)', f'=AVERAGEIF({SV("E")},"terrasse",{SV("H")})'),
        12: ('Libellés comptés (colonne G de l onglet Libellés)', f'=SUM(Libellés!G2:G{nlib})'),
        13: ('Couverts par service, intérieur', f'=AVERAGEIF({SV("E")},"intérieur",{SV("G")})'), 14: ('Couverts par service, terrasse', f'=AVERAGEIF({SV("E")},"terrasse",{SV("G")})'),
        15: ('Services, intérieur', f'=COUNTIF({SV("E")},"intérieur")'), 16: ('Services, terrasse', f'=COUNTIF({SV("E")},"terrasse")'),
        17: ('Services au-delà de 100 %, intérieur', f'=COUNTIFS({SV("E")},"intérieur",{SV("I")},1)'), 18: ('Services au-delà de 100 %, terrasse', f'=COUNTIFS({SV("E")},"terrasse",{SV("I")},1)'),
        19: ('Occupation moyenne 2022-2023 (%)', f'=AVERAGEIF({SV("D")},"2022-2023",{SV("H")})'), 20: ('Occupation moyenne 2023-2024 (%)', f'=AVERAGEIF({SV("D")},"2023-2024",{SV("H")})'),
        21: ('Occupation moyenne 2024-2025 (%)', f'=AVERAGEIF({SV("D")},"2024-2025",{SV("H")})'),
        22: ('Repère de 58 % appliqué à l intérieur (46 places), couverts', '=46*0.58'), 23: ('Repère de 58 % appliqué à la terrasse (48 places), couverts', '=48*0.58')}
for r, (a, b) in rows.items(): wsy.cell(r, 1, a); wsy.cell(r, 2, b)
for j, h in enumerate(['Tableau 73 bis : définition', 'Couverts', 'Occupation moyenne (%)', 'Services au-delà de 100 %', 'Maximum (%)'], start=1):
    c = wsy.cell(25, j, h); c.font = BOLD; c.fill = HFILL
defs = [('Liste de la réponse de juillet (annexe n° 92), notes encaissées seules', 'J', 'K'),
        ('Définition retenue (plats principaux, menus, menus enfants)', 'G', 'H'),
        ('Définition retenue, « Paysanne » classée parmi les entrées', 'N', 'O'),
        ('Exclusion de tout libellé presque toujours accompagné d un autre plat', 'L', 'M'),
        ('Borne basse : par note, la seule catégorie de plats la plus nombreuse', 'P', 'Q'),
        ('Borne haute : entrées et planches comprises', 'R', 'S')]
for k, (lab, cc, oc) in enumerate(defs, start=26):
    wsy.cell(k, 1, lab); wsy.cell(k, 2, f'=SUM({SV(cc)})'); wsy.cell(k, 3, f'=AVERAGE({SV(oc)})'); wsy.cell(k, 4, f'=COUNTIF({SV(oc)},">100")'); wsy.cell(k, 5, f'=MAX({SV(oc)})')
rows2 = {33: ('Couverts identifiables des tables vidées (définition retenue)', f'=SUM({SV("T")})', None),
         34: ('Occupation moyenne si aucun de ces couverts n avait été ressaisi (%)', f'=AVERAGE({SV("U")})', None),
         35: ('Services au-delà de 100 % dans ce cas', f'=COUNTIF({SV("U")},">100")', None),
         36: ('Occupation moyenne, calendrier de juillet, 14 juillet et Chat Perché en terrasse (%)', f'=AVERAGE({SV("X")})', None),
         37: ('Écart au repère de 58 % (points) : borne basse (B), borne haute (C)', '=C30-58', '=C31-58')}
for r, (a, b, c) in rows2.items():
    wsy.cell(r, 1, a); wsy.cell(r, 2, b)
    if c: wsy.cell(r, 3, c)
for r in list(range(3, 12)) + list(range(13, 15)) + list(range(19, 24)) + [34, 36, 37]: wsy[f'B{r}'].number_format = '0.00'
wsy['C37'].number_format = '0.00'
for k in range(26, 32):
    wsy[f'B{k}'].number_format = '0.0'; wsy[f'C{k}'].number_format = '0.00'; wsy[f'E{k}'].number_format = '0.0'
# --- Rotation_notes (pièce 11)
wrn = wb.create_sheet('Rotation_notes')
header(wrn, ['Id', 'Date', 'Service', 'Minute de clôture', 'Couverts (pièce 11)', 'Clé du service', 'Première ligne du service', 'Dernière ligne du service',
             'Couverts clos dans les 60 min', 'dans les 90 min', 'dans les 120 min'], [8, 11, 8, 9, 9, 18, 9, 9, 10, 10, 10])
nrn = len(P11) + 1
for i, r in enumerate(P11.itertuples(), start=2):
    for j, v in enumerate((int(r.id), r.date, r.svc, int(r.t), float(r.cv)), start=1): wrn.cell(i, j, v).font = BLUE
    wrn.cell(i, 6, f'=B{i}&"|"&C{i}')
    wrn.cell(i, 7, f'=INDEX(Rotation!$N$2:$N${ns},MATCH(F{i},Rotation!$M$2:$M${ns},0))')
    wrn.cell(i, 8, f'=INDEX(Rotation!$O$2:$O${ns},MATCH(F{i},Rotation!$M$2:$M${ns},0))')
    for j, w in ((9, 60), (10, 90), (11, 120)):
        wrn.cell(i, j, f'=SUMIFS(INDEX($E:$E,$G{i}):INDEX($E:$E,$H{i}),INDEX($D:$D,$G{i}):INDEX($D:$D,$H{i}),">="&$D{i},INDEX($D:$D,$G{i}):INDEX($D:$D,$H{i}),"<"&($D{i}+{w}))')
# --- Rotation
wr = wb.create_sheet('Rotation')
header(wr, ['Date', 'Service', 'Places (annexe n° 92)', 'Couverts (annexe n° 92)', 'Occupation (annexe n° 92, %)', 'Au-delà de 100 % (1 = oui)', 'Notes', 'Première clôture (min)',
            'Dernière clôture (min)', 'Étalement (min)', 'Maximum sur 60 min / places (%)', 'Maximum sur 90 min / places (%)', 'Clé du service', 'Première ligne (Rotation_notes)',
            'Dernière ligne (Rotation_notes)', 'Maximum sur 120 min / places (%)', 'Notes (au-delà de 100 %)', 'Étalement (au-delà de 100 %)', '60 min (au-delà de 100 %)',
            '90 min (au-delà de 100 %)', '120 min (au-delà de 100 %)', 'Fenêtre de 90 min au-dessus des places (1 = oui)'], [11, 8] + [10] * 20)
RN = lambda c: f'Rotation_notes!${c}$2:${c}${nrn}'
for i, r in enumerate(S92.itertuples(), start=2):
    for j, v in enumerate((r.date, r.service, int(r.places), int(r.cv), int(r.occ)), start=1): wr.cell(i, j, v).font = BLUE
    wr.cell(i, 6, f'=IF(E{i}>100,1,0)')
    wr.cell(i, 13, f'=A{i}&"|"&B{i}')
    wr.cell(i, 7, f'=COUNTIF({RN("F")},M{i})')
    wr.cell(i, 14, f'=IFERROR(MATCH(M{i},{RN("F")},0)+1,0)'); wr.cell(i, 15, f'=N{i}+G{i}-1')
    wr.cell(i, 8, f'=IF(G{i}=0,"",INDEX(Rotation_notes!$D:$D,N{i}))')
    wr.cell(i, 9, f'=IF(G{i}=0,"",INDEX(Rotation_notes!$D:$D,O{i}))'); wr.cell(i, 10, f'=IF(G{i}=0,"",I{i}-H{i})')
    for j, wc in ((11, 'I'), (12, 'J'), (16, 'K')):
        wr.cell(i, j, f'=IF(G{i}=0,0,MAX(INDEX(Rotation_notes!${wc}:${wc},N{i}):INDEX(Rotation_notes!${wc}:${wc},O{i}))/C{i}*100)')
    for j, src in ((17, 'G'), (18, 'J'), (19, 'K'), (20, 'L'), (21, 'P')): wr.cell(i, j, f'=IF(F{i}=1,{src}{i},"")')
    wr.cell(i, 22, f'=IF(L{i}>100,1,0)')
for c in ['K', 'L', 'P', 'S', 'T', 'U']: fmt(wr, c, '0.0')
nr = len(S92) + 1
syn = [('Synthèse de l étalement (liste et couverts de la pièce 11)', None),
       ('Services au-delà de 100 % (annexe n° 92)', f'=SUM(F2:F{nr})'), ('Médiane des notes de ces services', f'=MEDIAN(Q2:Q{nr})'),
       ('Médiane de l étalement de ces services (min)', f'=MEDIAN(R2:R{nr})'), ('Médiane du maximum sur 60 min / places (%)', f'=MEDIAN(S2:S{nr})'),
       ('Médiane du maximum sur 90 min / places (%)', f'=MEDIAN(T2:T{nr})'), ('Médiane du maximum sur 120 min / places (%)', f'=MEDIAN(U2:U{nr})'),
       ('Parmi eux, services sans fenêtre de 90 min au-dessus des places', f'=COUNTIFS(F2:F{nr},1,V2:V{nr},0)'),
       ('Services (sur 1 269) dont une fenêtre de 90 min dépasse les places', f'=SUM(V2:V{nr})'),
       ('Maximum sur 90 min / places, médiane des 1 269 services (%)', f'=PERCENTILE(L2:L{nr},0.5)'), ('idem, 9e décile (%)', f'=PERCENTILE(L2:L{nr},0.9)'),
       ('idem, maximum (%)', f'=MAX(L2:L{nr})'),
       ('Limite : l heure de clôture d une note n est pas l heure d arrivée des clients.', None)]
for k, (a, b) in enumerate(syn, start=1):
    wr.cell(k, 24, a).font = BOLD if k == 1 else Font()
    if b: wr.cell(k, 25, b); wr.cell(k, 25).number_format = '0.0'
wr.column_dimensions['X'].width = 62
# ordre des onglets : Méthode, Synthèse, Libellés, Lignes, Services, Rotation, puis sources et calculs auxiliaires
order = ['Méthode', 'Synthèse', 'Libellés', 'Lignes', 'Services', 'Rotation', 'Rotation_notes', 'Bornes_par_note', 'DEL_plats', 'Sources_calendrier']
wb._sheets = [wb[n] for n in order]
wb.save(PC + NAME); p('écrit', PC + NAME)
