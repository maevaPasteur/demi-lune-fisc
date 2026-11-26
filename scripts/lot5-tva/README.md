# Recalcul des pièces « TVA » (n° 161 à 165, errata des pièces n° 38, 85, 86, 87, 88)

Ces scripts régénèrent, à partir des annexes de caisse remises par le service et des pièces TVA antérieures, les dix
classeurs suivants :

| Pièce | Fichier produit | Script final |
|---|---|---|
| n° 161 | `161-R2-decalage-champ-taux-annexes-C-97769-lignes.xlsx` | `b4_piece1.py` |
| n° 162 | `162-R2-classification-legale-323-references-incidence-ticket-par-ticket.xlsx` | `b4_piece2.py` |
| n° 163 | `163-R2-etalons-rappel-autonome-reconstitution.xlsx` | `b4_piece3.py` |
| n° 164 | `164-R2-colonne-E-du-service-32047-lignes-ventilees.xlsx` | `b4_piece4.py` |
| n° 165 | `165-R2-export-natif-reglements-etat-9-55-lignes-37-notes.xlsx` | `b4_piece5.py` |
| n° 38 | `38-R3-rf-anomalies-tva-erratum.xlsx` | `b4_errata.py` |
| n° 85 | `85-R3-tva-bouclage-journaux-G-29588-lignes-identite-VAT-base-erratum.xlsx` | `b4_errata.py` |
| n° 86 | `86-R3-tva-rapprochement-caisse-tickets-comptabilite-erratum.xlsx` | `b4_errata.py` |
| n° 87 | `87-R3-tva-colonnes-E-et-F-annexes-C-corrections-de-taux-erratum.xlsx` | `b4_errata.py` |
| n° 88 | `88-R3-taux-tva-par-article-et-lignes-signalees-erratum.xlsx` | `b4_errata.py` |

Les pièces publiées sont les fichiers recalculés sous LibreOffice ; ces scripts les reproduisent à la mise en forme près.

Les classeurs 161 à 165 sont écrits par openpyxl avec des formules sans valeurs en cache ; `b4_recalc.py` les recalcule
sous LibreOffice (UNO, `calculateAll`) dans `cache/recalc/`. Les errata sont produits directement par LibreOffice :
copie de la pièce d'origine, ajout d'un onglet « Erratum R2 » en tête, recalcul et enregistrement au format xlsx.

## Environnement

- Python 3.13 (testé en 3.13.1), avec : `pandas==2.3.3` (recommandé), `numpy` (testé en 2.5.5), `openpyxl` (3.1.5),
  `xlrd` (2.0.2), `scipy` (1.18.1, test du khi-deux de `s08_erreurs_fiches_et_manipulation.py`).
- LibreOffice (`soffice`, testé en 26.8.3) : les étapes `b4_errata.py` et `b4_recalc.py` s'exécutent comme macros Python
  dans l'interpréteur intégré à LibreOffice (module `uno`), dans un profil propre à la chaîne (`cache/lo-profil/`).
- `git` (relecture d'une pièce antérieure qui ne serait plus dans `public/`, voir « Entrées »).

```sh
python3.13 -m venv scripts/lot5-tva/cache/venv
scripts/lot5-tva/cache/venv/bin/pip install "pandas==2.3.3" numpy openpyxl xlrd scipy
```

## Entrées

Tous les chemins sont calculés depuis la racine du dépôt (`common.py`).

- Annexes de caisse, `public/documents/caisse-enregistreuse/` : `ANNEXE-C1` à `C3` (détail des tickets), `E1` à `E3`
  (événements), `F1` à `F3` (règlements), `G1` à `G3` (journal de TVA), `H1` à `H3` (liste des tickets), au format `.xls`.
  Les annexes B ne sont pas lues par cette chaîne.
- Export natif des règlements : `public/documents/caisse-enregistreuse/SOURCE-reglement-brut_2022-2025.xls` (SpreadsheetML).
- Pièces antérieures :
  - `public/documents/pieces-defense/RF-anomalies-tva.xlsx` (pièce n° 38, source de l'erratum) et
    `RF-tva-1-extrait-fichier-caisse.csv` (pièce n° 36, lue par `s09_pieces.py`) ;
  - `public/documents/pieces-reponse-2/R2-tva-bouclage.xlsx` (pièce n° 85) ;
  - `public/documents/pieces-reponse-1/R1-tva-rapprochement.xlsx` (n° 86), `R1-tva-colonnes-ef.xlsx` (n° 87),
    `R1-taux-tva-et-encaissements.xlsx` (n° 88).

  Si l'un de ces fichiers n'est plus dans `public/`, `common.entree()` en extrait la dernière version enregistrée dans
  l'historique git vers `cache/entrees/`. `s00_charger.py` écrit les chemins retenus pour les errata dans
  `cache/entrees.json`, lu par `b4_errata.py`.
- Constantes de la proposition de rectification (comptes de la p. 26, données des p. 25, 53, 54, 63 à 65 et des
  annexes 7) : saisies dans `common.py` (`P26`, `P26G`), `b2_reconstitution_reglements.py`, `c1_materialite.py` et
  `b4_piece3.py`, avec leur page.

## Ordre d'exécution

`executer.sh` lance la chaîne complète dans cet ordre (journal de chaque script dans `cache/log/`) :

```sh
PYTHON=scripts/lot5-tva/cache/venv/bin/python sh scripts/lot5-tva/executer.sh
```

| # | Script | Lit | Écrit (dans `cache/`) |
|---|---|---|---|
| 1 | `s00_charger.py` | annexes C, G, H, F, E | `CC.pkl`, `G.pkl`, `H.pkl`, `F.pkl`, `E.pkl`, pieds de page, `entrees.json` |
| 2 | `s01_controle_sources.py` | annexes G, H, C ; tables | journal (contrôle des tables contre les `.xls`) |
| 3 | `s02_p26_origine.py` | `G.pkl`, `H.pkl` | journal |
| 4 | `s03_identite_vatbase.py` | `G.pkl` | `G_paliers.pkl` |
| 5 | `s04_decalage_taux_C.py` | `CC.pkl` | `C_taux.pkl` |
| 6 | `s05_validation_G.py` | `C_taux.pkl`, `G_paliers.pkl`, `G.pkl` | `C_taux2.pkl`, `C_vs_G_tickets.pkl` |
| 7 à 13 | `s06` à `s11` (dont `s08b_prix_caissier.py`) | `C_taux2.pkl`, tables ; `s09` lit les pièces 36, 38, 85 à 88 | journaux, `out/s06_articles_taux.csv` |
| 14 | `b1_classif.py` | `C_taux2.pkl` | `B3_articles.pkl`, `out/b1/B3_articles.csv` |
| 15 | `b1_calculs.py` | `C_taux2.pkl`, `B3_articles.pkl`, `G.pkl`, `H.pkl`, `F.pkl` | `B5_tickets.pkl` |
| 16 à 20 | `b1_b11_format.py`, `b1_b12_ordre.py`, `b1_b17_menus.py`, `b1_b7_b8_b14.py`, `b1_b7_zero.py` | tables, annexes G et F | journaux |
| 21 | `b2_reconstitution_reglements.py` | `B5_tickets.pkl`, `F.pkl` | journal |
| 22 | `b3_source_reglement.py` | export natif des règlements, `F.pkl` | `SOURCE_reglement.pkl` |
| 23 | `b3_c1_c3.py` | `C_taux2.pkl`, `B3_articles.pkl`, `B5_tickets.pkl`, `G.pkl` | `C_b3.pkl` |
| 24 | `b3_c6_c7.py` | `C_b3.pkl`, `B5_tickets.pkl`, `SOURCE_reglement.pkl`, tables | journal |
| 25 | `b3_c8_colonnes.py` | `CC.pkl`, `H.pkl`, `G.pkl` | journal |
| 26 | `c1_materialite.py` | constantes | `out/c1_materialite.txt` |
| 27 | `b4_prep.py` | `C_b3.pkl`, `B5_tickets.pkl` | journal (contrôles avant écriture) |
| 28 à 32 | `b4_piece1.py` à `b4_piece5.py` | `C_b3.pkl`, `B3_articles.pkl`, `B5_tickets.pkl`, `SOURCE_reglement.pkl`, tables | `pieces/161-…` à `pieces/165-…`, `out/b4/exp_161.json` à `exp_165.json` |
| 33 | `b4_errata.py` (macro LibreOffice) | pièces 38, 85 à 88 d'origine | `pieces/38-R3-…`, `pieces/85-R3-…` à `pieces/88-R3-…` |
| 34 | `b4_recalc.py` (macro LibreOffice) | `pieces/161-…` à `pieces/165-…` | `recalc/161-…` à `recalc/165-…` (valeurs calculées) |
| 35 | `b4_errata_check.py` | pièces d'origine et errata | journal : valeurs et formules des onglets d'origine inchangées |
| 36 | `b4_check.py` | `out/b4/exp_16*.json`, `recalc/` | journal : erreurs de formule, cellules attendues de « Synthèse », tirets cadratins |

`common.py` (chemins, constantes, chargement des tables) et `pieces_common.py` (écriture des classeurs) sont des modules
importés. Les deux macros sont copiées dans `cache/lo-profil/user/Scripts/python/` puis appelées par
`soffice --headless "vnd.sun.star.script:b4_errata.py$errata?language=Python&location=user"` (et `b4_recalc.py$recalcule`) ;
la variable d'environnement `LOT5_ICI` leur donne le dossier de la chaîne. `SOFFICE` désigne l'exécutable LibreOffice
(par défaut `soffice`).

Durée observée (Mac, Apple Silicon) : environ 2 min 45 s pour `executer.sh` (dont 1 minute pour les deux étapes
LibreOffice), 50 s pour `comparer.py` sur tous les onglets.

## Sorties

- `cache/` : tables intermédiaires (`.pkl`), `cache/out/` (`.csv`, `.txt`, `.json` des valeurs attendues),
  `cache/log/` (journaux), `cache/pieces/` (les dix classeurs régénérés), `cache/recalc/` (161 à 165 recalculés).
  Le dossier `cache/` n'est pas versionné ; rien n'est écrit dans `public/`.

## Aléa

Les tirages (placebos par permutation de `s04`, `s05`, `s08` ; jours témoins de `b3_c6_c7.py`) utilisent
`numpy.random.default_rng(20261123)`, avec une graine réinitialisée dans chaque script : graine 20261123. Aucun tirage
n'entre dans les classeurs produits. `executer.sh` fixe en outre `PYTHONHASHSEED=0`.

## Vérification

```sh
scripts/lot5-tva/cache/venv/bin/python scripts/lot5-tva/comparer.py DOSSIER_DES_PIECES_PUBLIEES [--synthese]
```

compare, cellule par cellule, tous les onglets (ou, avec `--synthese`, les onglets « Synthèse » et « Erratum R2 », et pour
la pièce 163, sans onglet « Synthèse », les onglets « Étalons » à « Errata CSV ») des
pièces régénérées avec les pièces publiées : nombres au centime près, textes à l'identique. Les pièces 161 à 165 sont
lues dans `cache/recalc/` ; un classeur dont les formules n'ont pas de valeur en cache est d'abord recalculé par
`soffice --headless --convert-to xlsx`.

Écart connu, propre à la version de LibreOffice : sur l'onglet « Lignes » de la pièce 161, la colonne X
(`ROUND(PU × Qte × 100 ; 0)` comparé à `ROUND(Tot_rem_Ttc × 100 ; 0)`) dépend de l'arrondi de 19,90 × 0,25 × 100, qui vaut
497,49999999999994 en virgule flottante. LibreOffice 26.8 l'arrondit à 498, la version utilisée pour la pièce publiée
à 497 : deux lignes (X32950, X53480) et le décompte de l'onglet « Autres colonnes » (C9 : 97 732 publié, 97 730
recalculé) diffèrent. L'onglet « Synthèse » n'est pas touché.
