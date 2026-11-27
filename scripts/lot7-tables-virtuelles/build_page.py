"""Assemble la page du site « Tables virtuelles » (point 2.7).

Usage : python3 build_page.py <sections.json (md_to_page.py)> <page.json existante> <données des couverts.json> <page.json à écrire>
Les composants interactifs de la page existante (grilles, plans, graphiques) sont repris à la place des figures ;
les données des graphiques de couverts viennent du fichier de données (définition retenue), la figure 31 reste celle du 10 juillet 2026.
"""
import copy
import json
import sys

src, old_page, donnees, out = sys.argv[1:5]
d = json.load(open(src, encoding='utf-8'))
old = json.load(open(old_page, encoding='utf-8'))
dat = json.load(open(donnees, encoding='utf-8'))


def find(kind, pred=lambda s: True):
    r = [copy.deepcopy(s) for s in old['sections'] if s['kind'] == kind and pred(s)]
    assert r, kind
    return r


def titre_has(t):
    return lambda s: t in (s.get('titre') or '')


R1, R2, L2, L6, L7 = 'pieces-reponse-1/', 'pieces-reponse-2/', 'pieces-lot2/', 'pieces-lot6/', 'pieces-lot7/'
P = {
    '92': (R2 + 'R2-tables-virtuelles-numeros.xlsx',
           'Annexe n° 92 : numéros de note sur les 659 journées (suite 1 … n), rangs 1 à 57, profil mensuel, tickets à 0,00 € et minute de la suppression « DEL », compteur d’événements, journée du 9 septembre 2022, couverts et occupation selon la liste de la réponse du 10 juillet 2026 (onglets à formules) (XLSX)'),
    '93': (R1 + 'R1-numeros-de-note-par-jour.xlsx',
           'Annexe n° 93 : numéros de note, additions, couverts, services, espace ouvert et occupation, jour par jour (659 lignes), et journées d’exemple, dans la version de la réponse du 10 juillet 2026 (couverts selon la liste de la réponse du 10 juillet 2026) (XLSX)'),
    '94': (R2 + 'R2-menus-prix.xlsx',
           'Annexe n° 94 : rafales « DEL » du 9 septembre 2022 et 61 conversions au forfait (XLSX)'),
    '172': (L7 + '172-R2-pointage-37-tickets-reglements-etat-9.xlsx',
            'Annexe n° 172 : pointage des 37 tickets à 0,00 € porteurs de règlements, par journée et par mode, avec la grille à compléter sur les remises bancaires (XLSX)'),
    '173': (L7 + '173-R2-libelles-comptes-comme-couverts-et-occupation.xlsx',
            'Annexe n° 173 : les 324 libellés des annexes C et leur classement comme couvert ; couverts, occupation, variantes et étalement des services (XLSX)'),
    '174': (L7 + '174-R2-passerelle-tickets-tables-videes-reglements.xlsx',
            'Annexe n° 174 : passerelle entre tickets, additions, tickets à 0,00 €, tables vidées et règlements ; numérotation de la seconde série (XLSX)'),
    '175': (L7 + '175-R2-tables-videes-chronologie-et-ressaisie-differee.xlsx',
            'Annexe n° 175 : chronologie des 2 359 tables vidées et ressaisie différée ; 830 tickets sans suppression à leur minute ; 42 clôtures différées (XLSX)'),
    '150': (R2 + 'R2-plan-de-la-salle.png',
            'Annexe n° 150 : plan de la salle intérieure (14 tables, 46 places), établi d’après le plan manuscrit de la gérante, non coté (PNG)'),
    '151': (R2 + 'R2-plan-de-la-terrasse.png',
            'Annexe n° 151 : plan de la terrasse (15 tables, 48 places), établi d’après le plan manuscrit de la gérante, non coté (PNG)'),
    '72': (L6 + '72-R3-suppressions-DEL-rapprochement-ventilation-en-euros-3-exercices-erratum.xlsx',
           'Annexe n° 72 : ventilation en euros des 21 302 lignes « DEL » et test du prix exact, avec un onglet « Erratum R2 » (XLSX)'),
    '155': (L2 + '155-R3-tables-videes-traces-egalites-paiements-separes.xlsx',
            'Annexe n° 155 : population des 2 359 tables vidées, tickets à 0,00 € et seconde série, égalités au centime et contrôles du hasard, paiements séparés, part rattachée (XLSX)'),
    '156': (L2 + '156-R3-tableau-p40-37-tickets-17-tickets-au-centime.xlsx',
            'Annexe n° 156 : tableau de la page 40 recalculé au centime, 37 tickets à 0,00 € porteurs de règlements, 17 tickets non nuls de la seconde série (XLSX)'),
    '157': (L2 + '157-R4-conversions-au-forfait-133-suites.xlsx',
            'Annexe n° 157 : 133 conversions au forfait recherchées sur les fichiers originaux (règle stricte, nombre non exhaustif) (XLSX)'),
    '11': ('pieces-defense/RF-encaissements-couverts.xlsx',
           'Annexe n° 11 : encaissements et couverts, pièce de la réponse du 10 juillet 2026, dans sa version de juillet (XLSX)'),
    '12': ('pieces-defense/RF-couverts-par-service.xlsx',
           'Annexe n° 12 : couverts par service, pièce de la réponse du 10 juillet 2026, dans sa version de juillet (XLSX)'),
}
CA = 'caisse-enregistreuse/'
caisse = []
for lettre, nom, ex in [('C', 'detail-tickets', 'détail des tickets'), ('E', 'tpvevenement', 'journal des événements'),
                        ('H', 'liste-tickets', 'liste des tickets')]:
    for k, e in enumerate(['2022-2023', '2023-2024', '2024-2025'], 1):
        caisse.append({'fichier': f'{CA}ANNEXE-{lettre}{k}_{nom}_{e}.xls', 'label': f'Annexe {lettre}-{k} du service : {ex} {e} (XLS)'})


def f(k):
    return {'fichier': P[k][0], 'label': P[k][1]}


# composants repris
kpis_rang = find('kpis', lambda s: s['items'][0]['valeur'] == '659')[0]
grille_rangs = find('grilleTables', lambda s: s.get('variante') == 'notes')[0]
grille_rangs['sousTitre'] = grille_rangs['sousTitre'].replace('Pièce R2, onglet', 'Annexe n° 92, onglet')
graph_mois = find('graphique')[0]
note_mois = find('note', lambda s: s['texte'].startswith('Additions moyennes par journée'))[0]
note_mois['texte'] = note_mois['texte'].replace('(pièce R2, onglet', '(annexe n° 92, onglet')
schema_4e = find('schema', titre_has('4e étape'))[0]
schema_4e['titre'] = 'La « 4ème étape potentielle » décrite par le vérificateur (proposition, p. 18), et les deux traces qu’elle laisse dans les annexes du service'
images = find('images')[0]
images['titre'] = 'Plans de la salle et de la terrasse, établis d’après les plans manuscrits de la gérante, non cotés (annexes n° 150 et 151)'
images['images'][0]['legende'] = 'Salle intérieure : 14 tables, 46 places (n° 1 à 12, 14 et 15) ; les n° 13, 16, 17 et 18 n’y figurent pas.'
images['images'][0]['alt'] = 'Plan de la salle intérieure : 14 tables numérotées 1 à 12, 14 et 15, 46 places'
images['images'][1]['legende'] = 'Terrasse : 15 tables, 48 places (n° 102 à 115 et n° 126) ; les n° 101 et 116 à 125 n’y figurent pas.'
images['images'][1]['alt'] = 'Plan de la terrasse : 15 tables numérotées 102 à 115 et 126, 48 places'
images['legende'] = 'Plans non cotés. Cliquer sur un plan pour l’ouvrir en plein format.'
plans = find('grilleTables', lambda s: s.get('variante') == 'plan')
plans[0]['sousTitre'] = 'Grille établie d’après le plan de l’annexe n° 150 : 14 tables et 46 places (n° 1 à 12, 14 et 15). Les n° 13, 16, 17 et 18, que le vérificateur a vus à l’écran pour la salle, n’y figurent pas.'
plans[1]['sousTitre'] = 'Grille établie d’après le plan de l’annexe n° 151 : 15 tables et 48 places (n° 102 à 115 et n° 126). Les n° 101 et 116 à 125 n’y figurent pas. La gérante atteste que les n° 116 et 117 sont des tables de l’intérieur sorties en terrasse les seuls jours exceptionnels, sans place supplémentaire (annexe n° 149, point 4).'
for pl in plans:
    for t in pl['tables']:
        if t.get('type') == 'rare':
            t['note'] = 'Table de l’intérieur sortie en terrasse les seuls jours exceptionnels, sans place supplémentaire (annexe n° 149, point 4)'
        elif t.get('note') == 'N’existe pas':
            t['note'] = 'Ne figure pas sur le plan'
DS = dat['sections']
lignes = copy.deepcopy(DS['58'])
lignes['titre'] = 'Couverts par semaine, définition retenue : superposition des trois exercices (avril → mars)'
lignes['sousTitre'] = 'Une ligne par exercice ; couverts comptés dans les notes encaissées selon la définition retenue (annexe n° 173, onglet « Services »).'
saisons = [copy.deepcopy(DS[k]) for k in ('60', '61', '62', '63')]
for s in saisons:
    s['sousTitre'] = 'Couverts par jour, définition retenue : service du soir (en haut) et du midi (en bas), une ligne par exercice. À droite, la moyenne de couverts par midi et par soir, mois par mois et exercice par exercice ; seuls les services ayant eu des couverts comptent dans la moyenne.'
kpis_couv = copy.deepcopy(dat['kpis']['45'])
kpis_couv['items'][1]['sub'] = 'Observatoire FIDUCIAL 2025 : point de comparaison, jamais un plafond'
kpis_couv['items'][4]['sub'] = '2,6 % des services, au plus 142 %'
kpis_del = copy.deepcopy(dat['kpis']['71'])
kpis_del['items'] = [kpis_del['items'][0], kpis_del['items'][1], kpis_del['items'][3]]
kpis_del['items'][1]['sub'] = 'hors les quatre lignes à quantité aberrante (point 2.2.2 c) ; annexe n° 72, onglet « prix exact »'
kpis_del['items'][2]['sub'] = '74,6 % ; 37 portent des règlements (1 958,26 €, point 2.2.5 c)'
capa = find('couvertsCapacite')[0]
alerte58 = {'kind': 'alerte', 'couleur': 'teal', 'titre': 'Le repère de 58 % est un point de comparaison, jamais un plafond',
            'texte': 'L’occupation mesurée se situe de 7,3 points en dessous à 5,9 points au-dessus de ce repère selon la définition des couverts (3,0 points au-dessus avec la définition retenue). Ce repère n’est jamais un plafond : rien dans la défense ne suppose que l’activité s’arrête à 58 %.'}


def figure(s):
    n, leg = s['num'], s['legende']
    note = {'kind': 'note', 'texte': leg}
    if n == '28':
        return [kpis_rang, note]
    if n == '29':
        return [grille_rangs, note, graph_mois, note_mois]
    if n == '29 bis':
        return [images, note]
    if n == '29 ter':
        return [plans[0], plans[1], note]
    if n == '30':
        return [kpis_couv, lignes] + saisons + [note]
    if n == '31':
        c = copy.deepcopy(capa)
        c['titre'] = 'Le graphique visé p. 36, tel que produit le 10 juillet 2026 avec la liste de couverts de juillet'
        c['sousTitre'] = leg.split(' : ', 1)[1] if ' : ' in leg else leg
        return [c, note, alerte58]
    raise ValueError(n)


par_point = {
    '2.7.2': ['92', '93', '174', '150', '151', '155', '156', '175', '172'],
    '2.7.3': ['173', '93', '92', '11', '12'],
    '2.7.4': ['72', '155', '157', '156'],
    '2.7.5': ['92', '94'],
    '2.7.6': ['157', '94', '72'],
}
docs_fin = {'kind': 'documents', 'titre': 'Toutes les pièces de la page', 'fichiers':
            [f(k) for k in ['92', '93', '94', '172', '173', '174', '175', '150', '151', '72', '155', '156', '157', '11', '12']]
            + [{'fichier': 'contentieux/Reponse_fisc_aux_observations_04-09-2026.pdf', 'label': 'Réponse du service du 04/09/2026 (grief F, p. 35 à 38)'}]
            + caisse}

sections = []
current = None
prev_titre = None
for s in d['sections']:
    if s['kind'] == 'titre' and s.get('numero', '').startswith('2.7.'):
        if current in par_point:
            sections.append({'kind': 'documents', 'fichiers': [f(k) for k in par_point[current]]})
        current = s['numero']
    if s['kind'] == '__figure__':
        sections.extend(figure(s))
        continue
    sections.append(s)
    if s['kind'] == 'liste' and prev_titre and prev_titre.startswith('b) Le grief décrit une fonction'):
        sections.append(schema_4e)
    if s['kind'] == 'liste' and prev_titre and prev_titre.startswith('b) Le volume des « DEL »'):
        sections.append(kpis_del)
    if s['kind'] == 'titre':
        prev_titre = s['texte']
    elif s['kind'] == 'liste':
        prev_titre = None
out_sections = []
for s in sections:
    if s['kind'] == 'paragraphe' and s['texte'].startswith('Références juridiques'):
        out_sections.append(docs_fin)
    out_sections.append(s)

page = {
    'meta': {
        'slug': 'tables-virtuelles',
        'source': 'Proposition du 18/05/2026 (p. 11, 18 à 21) ; réponse du service du 04/09/2026, partie F (p. 35 à 38) ; propositions personnelles du 19/10/2026.',
        'limites': [
            'Les couverts sont comptés sur les notes des annexes C selon une liste de libellés publiée (annexe n° 173) ; selon la définition des couverts, l’occupation va de 50,7 % à 63,9 % ; elle vaut 61,0 % pour la définition retenue.',
            'Les places reposent sur les plans établis d’après le plan manuscrit de la gérante, non cotés, et sur son attestation (annexes n° 149, 150 et 151).',
            'Le contenu d’origine des tables vidées ne figure dans aucun fichier remis ; la reprise sur une note encaissée n’est mesurée que statistiquement (annexe n° 175).',
            'Les règlements portés par les 37 tickets à 0,00 € sont exposés au point 2.2.5 c ; leur pointage sur les remises bancaires peut être fait avec la grille de l’annexe n° 172.',
        ],
    },
    'entete': {'statut': old['entete']['statut'], 'reponseCourte': d['reponseCourte']},
    'sections': out_sections,
}
json.dump(page, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('sections', len(out_sections))
