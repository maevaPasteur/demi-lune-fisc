# Point 2.6 : scripts de recalcul des pièces 167 à 171 et des errata 72, 89, 90 et 91

Les pièces publiées sont les fichiers de `public/documents/pieces-lot6/`. Ces scripts les reproduisent, à la mise en forme et à la numérotation près.

## Entrées
- Fichiers de caisse remis au service : `public/documents/caisse-enregistreuse/ANNEXE-*` (annexes B, C, E, F, G, H) et `SOURCE-reglement-brut_2022-2025.xls` (export natif des règlements).
- Pièces d'origine des errata : annexes 72, 89, 90 et 91 ; annexe 155 (`public/documents/pieces-lot2/`).
- Caches intermédiaires des lots 2.3 et 2.5 (`cache/lot23/`, `cache/lot25/`), reconstruits par les scripts de ces lots (`scripts/lot3-quantites/`, `scripts/lot5-tva/`).

## Ordre d'exécution
1. `s01` à `s15` (structure des fichiers, événements, séries, règlements, quantités, TVA, prix, chaînage) ;
2. `t01` à `t07` (partie X, quantités B et C, jours, seconde série, arrondis, prix, années civiles) ;
3. `u01` à `u03`, puis `v01`, `v01b`, `v02` à `v04` ;
4. `a1_reprise155.py`, `a2_civil.py` ;
5. `b5_A1.py` à `b5_A5.py` (pièces 167 à 171 ; `b5_A4_prep.py` avant `b5_A4.py`), `b5_tables_videes.py`, `b5_errata.py`, `b5_errata_check.py`.

Graine aléatoire : 20261123. Les sorties texte vont dans `out/`, les caches dans `cache/` (ignorés par git).

`md_to_page.py` et `build_page.py` construisent la page du site `src/data/reponse2/fichiers-evenement-reglement.json` à partir du texte de la section 2.6.
