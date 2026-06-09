# Enquête disparition du Macvin — notes de travail

Dossier de défense fiscale Demi Lune. Objet : expliquer l'écart achats vs consommation du **Macvin**.

## Point de départ (avant corrections)
- Achats fournisseur (net, 3 exercices fiscaux 01/04/2022→31/03/2025) : **806 L** (≈ 1075 bouteilles 75cl ; 800 L blanc + 6 L rosé).
- Conso enregistrée (ventes caisse + cocktails + cuisine + menus, scénario moyen) : **396 L**.
- Stock final 31/03/2025 : ~0 L. Stock d'ouverture 31/03/2022 : indisponible → **0** (NE PAS inventer : un stock d'ouverture > 0 *augmenterait* le disparu).
- **Disparu = 410 L ≈ 548 bouteilles ≈ 33 500 €** à la revente (61,25 €/bouteille).

## 10 pistes explorées (10 agents parallèles) — synthèse
1. **Verre sec (dose)** : 6 cl actuel ; ~1090 verres/3 ans = 65 L. Monter à 7-8 cl → +11 à +22 L. **DÉCISION : dose laissée à 6 cl** (consigne exploitant).
2. **Cocktails (doses estimées)** : Vouivre/Chat Perché/Grégoire. La Vouivre (~2120 ventes) est le levier dominant. **DÉCISION : Vouivre macvin 1→3 cl, Père Grégoire macvin 2→4 cl** (Chat Perché reste 6 cl). → +75 L de conso.
3. **Menus** : assiette franc-comtoise (4cl) + baba macvin (4cl), proba de choix estimée. Marge +17 à +28 L en proba haute. Plafonné (baba macvin disparu en carte A après 17/04/2023).
4. **Plats à la carte** : assiette FC + baba. ⚠️ Le « Baba » générique = **5 parfums** (macvin/soho/poire/marc/baileys) mais modélisé **100 % macvin** → conso plats SUREVALUÉE ; corriger vers ~1/5 *augmenterait* le disparu de ~40 L. À trancher avec l'exploitant.
5. **Stock d'ouverture 2022** : REJETÉ (l'inventer augmenterait le disparu ; reste à 0). Anomalie détectée : stock clôture 2023-2024 = 9 bouteilles (inventaire réel) non reporté dans le JSON (mis à 0) — sans effet sur le cumul, à fiabiliser.
6. **Non livré / avoirs / carnet** : le 806 L est **déjà net** (avoirs déduits, lignes sans montant exclues). ~0 L à retirer (max théorique 13,5 L, 2 « en manque » oct-nov 2023 à confirmer sur pièces).
7. **Fiabilisation achats** : la thèse « 566 L » est FAUSSE (oubliait Jacobin + Lornet). Vrai = 800 L blanc + 6 L rosé, **toutes 75cl**. Écart inchangé.
8. **Offerts + personnel + casse** : seuls **3,2 L** d'offerts tracés à 0 € en caisse (preuve qu'ils ne sont quasi jamais saisis). Estimation offerts/perso/casse : **38 / 76 / 142 L** (bas/moyen/haut).
9. **Répartition temporelle** : disparu STABLE (~45/54/53 %/an) → signature d'un **biais de doses systématique**, pas d'un détournement ponctuel. Argument défensif fort.
10. **Calcul inverse (dose-cible)** : pour annuler l'écart il faudrait **DOUBLER toutes les doses** (×2,0-2,25) = invraisemblable. Même sous doses généreuses, **résidu irréductible ≈ 120 à 285 L** → les doses seules n'expliquent pas tout.

## Corrections APPLIQUÉES (recettes, dans `_pipeline_boissons_complet.py`, dict COCKTAILS)
- **La Vouivre** (12 cl) : Crémant 10→**8**, Macvin 1→**3**, Crème de cassis 1 (volume maintenu à 12).
- **Apéritif du Père Grégoire** (6 cl) : Crémant 2→**1**, Macvin 2→**4**, Liqueur de cerise 2→**1** (volume maintenu à 6).
- Verre sec macvin : **inchangé 6 cl**. Stock d'ouverture 2022 : **inchangé 0**.

## État APRÈS corrections (chaîne régénérée : boissons_complet → achats → rapprochement → total)
- Conso macvin : 396 → **471 L** (macvin via cocktails 153 → **228 L**).
- Achats : 806 L (inchangé).
- **Disparu macvin : 410 → 335 L ≈ 447 bouteilles ≈ 27 400 €** à la revente.

## Reste à faire / pistes ouvertes
- Trancher le **split du Baba par parfum** (exploitant) — corrigerait la surévaluation plats (effet : +disparu).
- Documenter les **offerts/personnel** (38-142 L) pour les déduire de façon défendable.
- Fiabiliser le **stock de clôture 2023-2024 (9 bt)** dans le pipeline.
- Résidu irréductible attendu après tout : **~150-250 L** (piste 10) — noyau à justifier ou assumer.

## Fichiers/pipelines
- Recettes & conso : `_pipeline_boissons_complet.py` (COCKTAILS) → `src/data/calculsBoissons/consoTotaleParBoisson.json`, `cocktailsConsoComposition.json`.
- Achats : `_pipeline_achats.py`. Rapprochement : `_pipeline_rapprochement.py` (+ inventaires). Cumul/valorisation : `_pipeline_total.py` → `rapprochementDisparuTotal.xlsx`. Carnet : `_pipeline_carnet.py`.
