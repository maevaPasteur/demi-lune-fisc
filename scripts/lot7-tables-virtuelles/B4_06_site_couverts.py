"""Données du site (src/data/reponse2/tables-virtuelles.json) : sections 58 (graphiqueLignes, couverts par semaine et par exercice) et 60 à 63
(saisonCouverts, couverts par jour, soir et midi, moyennes mensuelles), recalculées avec la définition retenue (annexe 173 : 36 368,5 couverts),
selon les conventions de la page, établies en reproduisant d'abord à l'identique les données publiées à partir de la liste de juillet (pièce 11).
Valeurs des indicateurs (kpis) des sections 45 et 71. Sorties : out/B4/site-donnees-couverts-definition-retenue.json ; out/B4/06.txt"""
import sys, json, copy; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from B1_common import *
SITE = 'src/data/reponse2/tables-virtuelles.json'
OUT4 = O + 'B4/'
log = open(OUT4 + '06.txt', 'w')
def p(*a): print(*a); print(*a, file=log)
S = json.load(open(SITE))['sections']
EXOS = ['2022-2023', '2023-2024', '2024-2025']
PANELS = {60: [3, 4, 5], 61: [6, 7, 8], 62: [9, 10, 11], 63: [12, 1, 2]}
MOIS = {3: 'Mars', 4: 'Avril', 5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août', 9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre', 1: 'Janvier', 2: 'Février'}
def week(d):
    d = pd.Timestamp(d); y = d.year if d.month >= 4 else d.year - 1
    return min((d - pd.Timestamp(y, 4, 1)).days // 7 + 1, 52)       # semaine 53 (30 et 31 mars) rattachée à la semaine 52
def build(notes):
    """notes : DataFrame id, date, t, cv (couverts par note). Renvoie les sections 58 et 60 à 63 au format de la page."""
    n = notes.copy(); n['svc'] = np.where(n.t < 1080, 'midi', 'soir'); n['ex'] = n.date.map(ex_of)
    out = {}
    s58 = copy.deepcopy(S[58]); n['w'] = n.date.map(week)
    g = n.groupby(['w', 'ex']).cv.sum()
    s58['data'] = [dict(semaine=w, **{e: int(round(g.get((w, e), 0))) for e in EXOS}) for w in range(1, 53)]
    out[58] = s58
    sv = n.groupby(['date', 'svc']).cv.sum().reset_index(); sv['ex'] = sv.date.map(ex_of); sv['m'] = sv.date.str[5:7].astype(int); sv['j'] = sv.date.str[8:10].astype(int)
    for i, ms in PANELS.items():
        s = copy.deepcopy(S[i]); ticks = [t['tick'] for t in s['moisTicks']]
        for svc in ('soir', 'midi'):
            rows = []
            for r in s[svc]:
                rows.append({'jour': r['jour']})
            idx = {r['jour']: r for r in rows}
            x = sv[(sv.svc == svc) & sv.m.isin(ms) & (sv.cv > 0)]
            for r in x.itertuples():
                j = ticks[ms.index(r.m)] + r.j - 1
                idx[j][r.ex] = int(round(r.cv))
            s[svc] = [dict(sorted(r.items(), key=lambda kv: (kv[0] != 'jour', EXOS.index(kv[0]) if kv[0] in EXOS else -1))) for r in rows]
        st = []
        for m in ms:
            pe = []
            for e in EXOS:
                g2 = sv[(sv.m == m) & (sv.ex == e) & (sv.cv > 0)]; mi = g2[g2.svc == 'midi'].cv; so = g2[g2.svc == 'soir'].cv
                pe.append(dict(exo=e, midis=len(mi), soirs=len(so), moyMidi=int(round(mi.mean())) if len(mi) else 0, moySoir=int(round(so.mean())) if len(so) else 0))
            st.append(dict(mois=MOIS[m], parExercice=pe))
        s['stats'] = st
        out[i] = s
    return out, sv
# 1) contrôle des conventions : la liste de juillet (pièce 11) redonne exactement les données publiées
P11 = pd.read_pickle(Q + 'P11.pkl')
old, _ = build(P11[['id', 'date', 't', 'cv']])
for i in (58, 60, 61, 62, 63):
    p(f'section {i} : reproduction à l identique des données publiées avec la pièce 11 : {json.dumps(old[i], ensure_ascii=False) == json.dumps(S[i], ensure_ascii=False)}')
# 2) définition retenue
NN = pd.read_csv(OUT4 + '02_notes_DPc.csv').rename(columns={'dpc': 'cv'})
new, sv = build(NN[['id', 'date', 't', 'cv']])
w = pd.DataFrame(new[58]['data']).set_index('semaine')
p(f'contrôle des totaux : notes {len(NN)} ; couverts {NN.cv.sum():.2f} (annexe 173, Synthèse!B3 : 36 368,51) ; services {len(sv)} (B2 : 1 269) ; '
  f'somme des semaines arrondies {int(w.values.sum())} ; somme des jours arrondis {sum(v for i in (60, 61, 62, 63) for s in ("soir", "midi") for r in new[i][s] for k, v in r.items() if k != "jour")}')
p('   par exercice (non arrondi) :', NN.assign(ex=NN.date.map(ex_of)).groupby('ex').cv.sum().round(2).to_dict(), ' ; semaines arrondies :', w.sum().to_dict())
p(f'   services à 0 couvert (exclus des panneaux) : {int((sv.cv == 0).sum())} ; services comptés dans les panneaux : {int((sv.cv > 0).sum())}')
oc = sv.merge(pd.read_pickle(Q + 'S92.pkl')[['date', 'service', 'places']].rename(columns={'service': 'svc'}), on=['date', 'svc'])
oc['o'] = oc.cv / oc.places * 100
p(f'   occupation (contrôle) : moyenne {oc.o.mean():.2f} % ; au-delà de 100 % {int((oc.o > 100).sum())} ; max {oc.o.max():.1f} % ; par service {oc.cv.mean():.2f}')
# jours d ouverture en janvier et février (pour la phrase « le restaurant ferme janvier et février »)
H = pd.read_pickle(Q + 'H2.pkl'); dd = pd.Series(sorted(H.date_ticket.unique()))
jf = dd[dd.str[5:7].isin(['01', '02'])]
p(f'journées d ouverture en janvier : {int((jf.str[5:7] == "01").sum())} ; en février : {int((jf.str[5:7] == "02").sum())} ; dates : {jf.tolist()}')
# 3) indicateurs
k45 = copy.deepcopy(S[45]); it = k45['items']
it[0]['valeur'] = f'{oc.o.mean():.1f} %'.replace('.', ',')
it[3]['valeur'] = '36 368,5'; it[3]['sub'] = f'{oc.cv.mean():.1f} par service en moyenne'.replace('.', ',')
it[4]['valeur'] = str(int((oc.o > 100).sum())); it[4]['sub'] = f'{(oc.o > 100).mean() * 100:.1f} % : la rotation de table, déjà comptée'.replace('.', ',')
res = {'source': 'définition retenue des couverts (annexe n° 173, onglet « Synthèse » : 36 368,5 couverts, occupation moyenne 61,0 %, 33 services au-delà de 100 %)',
       'conventions': 'mêmes clés et mêmes conventions que la page : semaine = jours depuis le 1er avril de l exercice divisés par 7, plus 1, la semaine 53 rattachée à la 52 ; '
                      'jour = rang du jour dans le trimestre du panneau ; midi = note close avant 18 h ; services à 0 couvert absents des panneaux et exclus des moyennes ; arrondi à l entier (règle de Python, au pair le plus proche pour les demi-unités), comme dans la page.',
       'sections': {str(i): new[i] for i in (58, 60, 61, 62, 63)},
       'kpis': {'45': k45, '71': copy.deepcopy(S[71])},
       'section_49_inchangee': 'la section 49 (couvertsCapacite) reste telle que produite le 10 juillet 2026 (figure 31)'}
json.dump(res, open(OUT4 + 'site-donnees-couverts-definition-retenue.json', 'w'), ensure_ascii=False, indent=1)
p('écrit', OUT4 + 'site-donnees-couverts-definition-retenue.json')
p('kpis 45 :', json.dumps(k45['items'], ensure_ascii=False))
