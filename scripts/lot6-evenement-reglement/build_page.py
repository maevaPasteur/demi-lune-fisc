"""Assemble la page du site « Les fichiers Événement et Règlement » (point 2.6).

Usage : python3 build_page.py <sections.json produit par md_to_page.py> <page.json à écrire>
"""
import json
import sys

src, out = sys.argv[1:3]
d = json.load(open(src, encoding='utf-8'))

L6 = 'pieces-lot6/'
P = {
    '72': (L6 + '72-R3-suppressions-DEL-rapprochement-ventilation-en-euros-3-exercices-erratum.xlsx',
           'Annexe n° 72 : ventilation en euros des 21 302 lignes « DEL », quatre lignes aberrantes et test du prix exact, avec un onglet « Erratum R2 » (catégorie « multiple » ; témoin) (XLSX)'),
    '89': (L6 + '89-R3-fichiers-E-F-C-reconciliation-DEL-reglements-CA-quantites-TVA-3-exercices-erratum.xlsx',
           'Annexe n° 89 : réconciliation des fichiers E, F et C sur trois exercices (événements « DEL », règlements, chiffre d’affaires, contrôle prix × quantité, remises, colonnes E et F), classeur à formules, avec un onglet « Erratum R2 » (XLSX)'),
    '90': (L6 + '90-R3-compteur-perpetuel-deux-series-quatre-montants-B-dans-C-erratum.xlsx',
           'Annexe n° 90 : les compteurs perpétuels de la caisse (onglets 1 à 7), avec un onglet « Erratum R2 » portant sur l’onglet 7 (XLSX)'),
    '91': (L6 + '91-R3-reconciliation-annexes-A-B-C-F-G-H-quantites-exemple-14-04-2022-erratum.xlsx',
           'Annexe n° 91 : réconciliation des annexes (chiffre d’affaires par annexe, quantités B contre C, exemple du 14 avril 2022, lignes de C absentes de B), avec un onglet « Erratum R2 » portant sur les onglets 1 et 6 (XLSX)'),
    '87': ('pieces-lot5/87-R3-tva-colonnes-E-et-F-annexes-C-corrections-de-taux-erratum.xlsx',
           'Annexe n° 87 : colonnes E et F et taux par article, avec un onglet « Erratum R2 » (XLSX)'),
    '167': (L6 + '167-R2-tracabilite-DEL-rattachement-Z-note-tables-videes-placebos.xlsx',
            'Annexe n° 167 : rattachement des 21 302 suppressions au ticket Z et à la note, placebos ; part des 2 359 tables vidées rattachée au-delà du hasard, selon le témoin (XLSX)'),
    '168': (L6 + '168-R2-partie-X-modes-de-reglement-encaissements-et-CA-3-exercices.xlsx',
            'Annexe n° 168 : partie X par mode et par exercice ; décomposition des encaissements comptables ; règles de reclassement testées ; chiffre d’affaires à périmètre égal (XLSX)'),
    '169': (L6 + '169-R2-export-natif-reglements-colonnes-retirees-sy_uk-etat.xlsx',
            'Annexe n° 169 : les vingt-deux colonnes de l’export natif des règlements et les onze retirées par le service ; sy_uk ; etat ; concordance des annexes C et H par identifiant (XLSX)'),
    '170': (L6 + '170-R2-quantites-B-C-7146-lignes-regle-6272-7037-109.xlsx',
            'Annexe n° 170 : les 7 146 lignes de quantité différente, règle de la quantité commandée et témoins ; partages et suppressions (XLSX)'),
    '171': (L6 + '171-R2-seconde-serie-17-tickets-et-55-reglements-etat-9.xlsx',
            'Annexe n° 171 : 17 tickets de la seconde série et deux règles de reprise ; 55 règlements « etat = 9 » et doublons ; rapprochement jour par jour (XLSX)'),
    '165': ('pieces-lot5/165-R2-export-natif-reglements-etat-9-55-lignes-37-notes.xlsx',
            'Annexe n° 165 : export natif des règlements, colonne « etat » (XLSX)'),
    '163': ('pieces-lot5/163-R2-etalons-rappel-autonome-reconstitution.xlsx',
            'Annexe n° 163 : rapprochements caisse, comptabilité et TVA légale ; bases HT ; rappel autonome et variantes ; décomposition de la TVA reconstituée ; errata des pièces 36, 37, 39, 40 et 41 (XLSX)'),
    '155': ('pieces-lot2/155-R3-tables-videes-traces-egalites-paiements-separes.xlsx',
            'Annexe n° 155 : population des 2 359 tables vidées, tickets à 0,00 € et seconde série, égalités au centime et contrôles du hasard, paiements séparés, part rattachée'),
    '156': ('pieces-lot2/156-R3-tableau-p40-37-tickets-17-tickets-au-centime.xlsx',
            'Annexe n° 156 : tableau de la page 40 recalculé au centime, 37 tickets à 0,00 € porteurs de règlements, 17 tickets non nuls de la seconde série, contenu des minutes qui précèdent la clôture des 37 tickets et modes de règlement'),
}
CA = 'caisse-enregistreuse/'
caisse = []
for lettre, nom, ex in [('E', 'tpvevenement', 'journal des événements'), ('F', 'reglements', 'règlements'),
                        ('B', 'prix-vente-quantite', 'prix de vente et quantités'), ('C', 'detail-tickets', 'détail des tickets'),
                        ('G', 'journal-tva', 'journal de TVA'), ('H', 'liste-tickets', 'liste des tickets')]:
    for k, e in enumerate(['2022-2023', '2023-2024', '2024-2025'], 1):
        caisse.append({'fichier': f'{CA}ANNEXE-{lettre}{k}_{nom}_{e}.xls', 'label': f'Annexe {lettre}-{k} du service : {ex} {e} (XLS)'})


def f(k):
    return {'fichier': P[k][0], 'label': P[k][1]}


kpis = {'kind': 'kpis', 'items': [
    {'label': 'Suppressions « DEL » rattachées à leur ticket Z', 'valeur': '21 302 / 21 302',
     'sub': '23 339 événements, identifiants 36681 à 60019 sans trou ; 62,77 % à la minute de clôture d’une seule note', 'couleur': 'teal', 'highlight': True},
    {'label': 'Colonne de contrôle du service, annexe C', 'valeur': '0,04 / 44,58 / 131,08 €',
     'sub': 'contre 17 561 / 20 011 / 20 115 € pour l’annexe B', 'couleur': 'teal', 'highlight': True},
    {'label': 'Lignes de quantité différente expliquées', 'valeur': '7 037 / 7 146',
     'sub': 'quantité commandée pour la table ; 6 272 selon la règle stricte ; 109 sans explication', 'couleur': 'teal'},
    {'label': 'Lignes signalées par les colonnes E et F', 'valeur': '94,75 %',
     'sub': 'procèdent d’un champ des annexes C décalé d’une ligne (point 2.5.6 b)', 'couleur': 'teal'},
    {'label': 'Partie X, excédent de 2023-2024', 'valeur': '5 355,78 €',
     'sub': '1,2 % de l’exercice ; contrepartie au FEC que le service détient', 'couleur': 'orange'},
]}

docs_fin = {'kind': 'documents', 'titre': 'Toutes les pièces de la page', 'fichiers':
            [f(k) for k in ['89', '90', '91', '72', '87', '167', '168', '169', '170', '171', '165', '163', '155', '156']]
            + [{'fichier': 'contentieux/Reponse_fisc_aux_observations_04-09-2026.pdf', 'label': 'Réponse du service du 04/09/2026 (grief G, p. 38 à 46)'}]
            + caisse}

# pièces au fil des sous-points (renvois du texte)
par_point = {
    '2.6.3': ['169', '165', '89', '72', '167', '155'],
    '2.6.4': ['90', '89', '165', '169', '171', '168', '155'],
    '2.6.5': ['90', '91', '170', '89'],
    '2.6.6': ['89', '87', '163'],
}

sections = []
current = None
for s in d['sections']:
    if s['kind'] == 'titre' and s.get('numero', '').startswith('2.6.'):
        if current in par_point:
            sections.append({'kind': 'documents', 'fichiers': [f(k) for k in par_point[current]]})
        current = s['numero']
    if s['kind'] == '__kpis__':
        sections.append(kpis)
        continue
    sections.append(s)
    if s['kind'] == 'titre' and s['texte'].startswith('Pièces annexées'):
        pass
# documents finaux après la liste des pièces annexées et avant les références
out_sections = []
for k, s in enumerate(sections):
    if s['kind'] == 'paragraphe' and s['texte'].startswith('Références juridiques'):
        out_sections.append(docs_fin)
    out_sections.append(s)

page = {
    'meta': {
        'slug': 'fichiers-evenement-reglement',
        'source': 'Proposition du 18/05/2026, parties VIII, IX (imprimée « XI »), X, XII et XIII (p. 23 à 29) ; réponse du service du 04/09/2026, lettre G (p. 38 à 46) ; propositions personnelles du 19/10/2026.',
        'limites': [
            'Le décalage d’un champ des annexes C est un constat sur les fichiers remis par le service ; son origine n’est pas établie (point 2.5.6 b).',
            'La part des tables vidées rattachée à des notes encaissées au-delà du hasard dépend du témoin retenu : 7 030,75 à 9 319,68 € (3,9 à 5,2 % du montant des tables) avec des témoins proches dans le temps ; avec des témoins éloignés de plusieurs semaines, l’estimation monte jusqu’à 28 %, que la société ne retient pas. Le fond relève du point 2.2.',
            'L’excédent de 5 355,78 € des encaissements comptables sur le chiffre d’affaires comptabilisé de 2023-2024 (1,2 % de l’exercice) est tiré des montants de la proposition (p. 25 et 26) ; sa contrepartie figure au FEC, que le service détient.',
            'La règle de la quantité commandée explique 7 037 des 7 146 lignes dont la quantité diffère entre les annexes B et C (6 272 selon la seule règle des quinze minutes) ; 109 restent sans explication.',
        ],
    },
    'entete': {'reponseCourte': d['reponseCourte'], 'statut': 'demonte'},
    'sections': out_sections,
}
json.dump(page, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('sections', len(out_sections))
