# Point 2.7 : scripts de recalcul des pièces 172 à 175 et des données de la page « Tables virtuelles »

Les pièces publiées sont les fichiers fournis (`public/documents/pieces-lot7/`) ; ces scripts les reproduisent à la mise en forme et à la numérotation près.

## Entrées
- Fichiers de caisse remis au service : `public/documents/caisse-enregistreuse/` (annexes B, C, E, F, G, H) et `SOURCE-reglement-brut_2022-2025.xls` (export natif des règlements).
- Pièces 11, 12, 92, 93, 94, 155, 156 et 157 du dépôt.
- Caches intermédiaires des lots 2.3, 2.5 et 2.6 (`scripts/lot3-quantites/cache/`, `scripts/lot5-tva/cache/`, `scripts/lot6-evenement-reglement/cache/`), reconstruits par les scripts de ces lots.

`prepare_entrees.py` crée `cache/entrees/` (liens vers ces fichiers, sous les noms attendus) et les dossiers de sortie.

## Ordre d'exécution (depuis la racine du dépôt)
1. `prepare_entrees.py` ;
2. `B0_s00_load.py` (lecture des fichiers d'origine), puis `B0_s01` à `B0_s14` (rangs, tickets, suppressions, événements, prix, couverts, occupation, journées, tables vidées) ;
3. `B1_D01` à `B1_D13` (identifiants, chronologie, 37 tickets, couverts, 9 septembre 2022, jours exceptionnels) ;
4. `B2_01` à `B2_11` (passerelle, règlements, pointage, profils, ressaisie, couverts, 42 tickets, versions de travail des annexes, recalcul) ;
5. `B4_01` à `B4_04` (pièces 172 à 175 ; `B4_04a_reprise.py` avant `B4_04`), `B4_06_site_couverts.py` (données des graphiques de la page), `B4_09_recalc.py` (recalcul LibreOffice), `B4_10_finalise.py`.

Graine aléatoire : 20261123. Les sorties vont dans `out/`, les caches dans `cache/` (ignorés par git).
