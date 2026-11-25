# Recalcul des pièces « quantités fractionnaires » (n° 77, 78, 8, 158, 159, 160)

Ces scripts régénèrent, à partir des annexes de caisse remises par le service, les six classeurs suivants :

| Pièce | Fichier produit | Script final |
|---|---|---|
| n° 77 | `77-R3-quantites-fractionnaires-recomposition-5062-articles-866-tables.xlsx` | `r3_pieces_a.py` |
| n° 78 | `78-R3-quantites-fractionnaires-chiffrage-service-62487-87-recompose-et-note-d-origine-annexe-B.xlsx` | `r3_pieces_a.py` |
| n° 8 | `08-R3-quantites-anormales-erratum.xlsx` | `r3_pieces_a.py` |
| n° 158 | `158-R2-quantites-fractionnaires-note-d-origine-annexe-B-et-concordance-C-H-G-F.xlsx` | `r3_pieces_b.py` |
| n° 159 | `159-R2-partages-non-aboutis-63-cas-note-d-origine-et-montant-maximal.xlsx` | `r3_pieces_b.py` |
| n° 160 | `160-R2-quantites-fractionnaires-test-placebo-600-tirages.xlsx` | `r3_pieces_b.py` |

Les pièces publiées sont les fichiers recalculés sous LibreOffice ; ces scripts les reproduisent à la mise en forme près.

Les classeurs produits contiennent des formules sans valeurs en cache (openpyxl n'en calcule pas) : un tableur, ou
`soffice --headless --convert-to xlsx`, les recalcule à l'ouverture.

## Environnement

- Python 3.13 (testé), avec : `pandas==2.3.3`, `numpy` (testé en 2.5.5), `openpyxl` (3.1.5), `xlrd` (2.0.2).
- `git` (relecture de pièces antérieures retirées de `public/`, voir « Entrées »).
- LibreOffice (`soffice`) pour recalculer les formules, uniquement pour la comparaison (`comparer.py`).

```sh
python3.13 -m venv scripts/lot3-quantites/cache/venv
scripts/lot3-quantites/cache/venv/bin/pip install "pandas==2.3.3" numpy openpyxl xlrd
```

## Entrées

Tous les chemins sont calculés depuis la racine du dépôt (`common.py`).

- Annexes de caisse, `public/documents/caisse-enregistreuse/` : `ANNEXE-B1` à `B3` (prix de vente / quantité),
  `C1` à `C3` (détail des tickets), `E1` à `E3` (événements), `F1` à `F3` (règlements), `G1` à `G3` (journal de TVA),
  `H1` à `H3` (liste des tickets), au format `.xls`.
- Pièces antérieures, reprises telles quelles puis mises à jour :
  - `public/documents/pieces-reponse-2/R2-quantites-recomposition.xlsx` (pièce n° 77, version R2) ;
  - `public/documents/pieces-reponse-2/R2-quantites-chiffrage-service.xlsx` (pièce n° 78, version R2 ; son onglet
    « Lignes C » sert aussi d'entrée à `s00_load.py`) ;
  - `public/documents/pieces-reponse-2/R2-fichiers-EF-reconciliation.xlsx` (pièce n° 89, onglets « Sources_C-1 » à « Sources_C-3 ») ;
  - `public/documents/pieces-defense/RF-quantites-anormales.xlsx` (pièce n° 8 du 10/07/2026).

  Si l'un de ces fichiers n'est plus dans `public/`, `common.entree()` en extrait la dernière version enregistrée dans
  l'historique git vers `cache/entrees/`.

## Ordre d'exécution

`executer.sh` lance la chaîne complète dans cet ordre (journal de chaque script dans `cache/log/`) :

```sh
PYTHON=scripts/lot3-quantites/cache/venv/bin/python sh scripts/lot3-quantites/executer.sh
```

| # | Script | Lit | Écrit (dans `cache/`) |
|---|---|---|---|
| 1 | `s00_load.py` | annexes B, E, F ; pièces n° 78 et 89 (R2) | `B.pkl`, `B_foot_*.pkl`, `E.pkl`, `F.pkl`, `SC.pkl`, `LC.pkl` |
| 2 | `s03_B_ecarts.py` | `B.pkl` | `B.pkl` (colonnes de typologie) |
| 3 | `s05_buildC.py` | `B.pkl`, `LC.pkl`, `SC.pkl`, `F.pkl` | `Crec.pkl` (reconstitution) |
| 4 | `s30_loadC.py` | annexes C | `CC.pkl`, `C_foot.pkl` |
| 5 | `s31_C_as_primary.py` | `CC.pkl`, `Crec.pkl` | `Crec_reconstit.pkl`, `Crec.pkl` (annexe C primaire + colonnes B) |
| 6 | `s06_recompo.py` | `Crec.pkl`, `F.pkl` | `recompo_base.pkl`, `NOTES.pkl`, `Fid2.pkl` |
| 7 | `s10_cloture_note.py` | idem | `cloture_note_W60.pkl` |
| 8 | `m1_B07.py` | annexes H | `H.pkl` |
| 9 | `c1_loadG.py` | annexes G | `G.pkl`, `G_foot.pkl` |
| 10 | `m1_B02.py` | cache | `B02_neg.pkl`, `out/B02_*.csv` |
| 11 | `m1_B04.py` | cache | `out/B04_notes.csv`, `out/B04_lignes.csv`, `out/B04_synthese.csv` |
| 12 | `m2_Bc1.py` | cache | `out/Bc1_cas.csv`, `out/Bc1_temoin.csv` |
| 13 | `c1_C2.py` | cache, `H.pkl`, `G.pkl` | `out/C2_cas.csv`, `out/C2_*.csv` |
| 14 | `m1_B09.py` | cache | `out/B09_tirages_a.csv`, `_b`, `_c`, `out/B09_synthese.csv` |
| 15 | `r3_C5_brut.py` | cache (`s06_recompo`, `s07_sensibilite` importés) | `out/C5_brut.csv` |
| 16 | `r3_pieces_a.py` | pièces n° 77, 78, 8 antérieures ; `CC.pkl`, `E.pkl` | `pieces/77-…`, `pieces/78-…`, `pieces/08-…` |
| 17 | `r3_pieces_b.py` | cache, `out/*.csv`, `pieces/77-…` | `pieces/158-…`, `pieces/159-…`, `pieces/160-…` |

`common.py` (chemins, normalisation des libellés, chargement) et `s07_sensibilite.py` (calcul des articles par table)
sont des modules importés. `s31_C_as_primary.py` ne recopie `Crec.pkl` dans `Crec_reconstit.pkl` que si ce dernier
n'existe pas ; `executer.sh` le supprime avant chaque exécution complète.

## Sorties

- `cache/` : tables intermédiaires (`.pkl`), `cache/out/` (`.csv`), `cache/log/` (journaux), `cache/pieces/` (les six
  classeurs régénérés). Le dossier `cache/` n'est pas versionné ; rien n'est écrit dans `public/`.

## Aléa

Tous les tirages (témoins, placebos, 600 tirages de la pièce n° 160) utilisent `numpy.random.default_rng(20261123)`,
avec une graine réinitialisée dans chaque script : graine 20261123.

L'appariement glouton des parts aux événements DEL (`r3_C5_brut.py`) dépend de l'ordre des articles d'une table :
`s07_sensibilite.arts()` les parcourt dans l'ordre de première apparition (et non plus dans l'ordre d'un ensemble Python,
qui varie avec `PYTHONHASHSEED`). Sans ce correctif, une table du 11/03/2023 (Rêve Bleu à 20 %, Tequila Sunrise à 10 %,
deux DEL de 2,97 et 2,96 €) faisait varier de 0,0008 € le HT 2022-2023 de l'onglet « Montant par fenêtre » de la
pièce n° 159. `executer.sh` fixe en outre `PYTHONHASHSEED=0`.

## Vérification

```sh
scripts/lot3-quantites/cache/venv/bin/python scripts/lot3-quantites/comparer.py DOSSIER_DES_PIECES_PUBLIEES
```

recalcule les pièces régénérées sous LibreOffice (`cache/recalc/`) et compare, cellule par cellule, les onglets de
synthèse (« Synthèse… », « Montant par fenêtre » ; « Erratum » pour la pièce n° 8) avec les pièces publiées :
nombres au centime près, textes à l'identique.
