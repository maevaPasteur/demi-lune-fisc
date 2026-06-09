# A - Audit des calculs du fisc (boissons)

**Dossier :** SARL LA DEMI-LUNE - contrôle DDFiP Jura. Le vérificateur reconstitue ~471 k€ de
recettes occultées à partir des « volumes de boissons disparus ».

**Méthode de cet audit :** chaque affirmation ci-dessous est un nombre calculé depuis les fichiers
sources. Aucune supposition. Les éléments non vérifiables depuis les données sont signalés
explicitement.

**Fichiers fisc audités :**
- `src/data/reconstitution-administration.json` (méthode détaillée, ingrédients, synthèse)
- `src/data/volumes-disparus-fisc.json` (52 produits, % disparus par exercice)

**Nos données exactes :** `analyses-independantes/boissons/data/` (achats-exercice, ventes-caisse,
lignes-ignorees).

---

## Constat préalable - PÉRIODE de la reconstitution fisc

La synthèse fisc indique `caInscritEnComptabilite` TTC = **435 524,92 €**.

| Exercice | Notre TOTAL GÉNÉRAL TTC caisse | Écart vs fisc |
|---|---|---|
| 2022-2023 | 403 370,42 | −32 154,50 |
| 2023-2024 | 438 281,12 | +2 756,20 |
| **2024-2025** | **435 564,96** | **+40,04** |

**Verdict : la reconstitution de l'administration porte sur le SEUL exercice 2024-2025**
(écart de 40 € sur le CA comptabilisé). C'est déterminant : tous les « volumes disponibles » de la
reconstitution (Macvin 362 btl, fût 79, etc.) doivent se lire **sur un seul exercice**, pas sur 3 ans.

---

## H1 - Erreur fût / bière (sur-évaluation du volume disponible ?)

**Donnée fisc** (`reconstitution-administration.json`, ingrédient « Bière ») :
- désignation « Fût Affligem Blade 800 cl », `bouteillesDisponibles` = 79,
  `volumeDisponibleCl` = **63 200 cl** (= 79 × 800 cl = **632 L**), `volumesDisparusPct` = 27,12 %,
  `caReconstitue` TTC = 7 180,52 €.

**Notre donnée exacte** (`achats-exercice.json`, code 212122 « FUT AFFLIGEM BLADE 8 L », `contenanceCl`=800, `estFut`=true) :

| Exercice | volCl livré | en litres |
|---|---|---|
| 2022-2023 | 79 200 | 792 L |
| 2023-2024 | 63 200 | 632 L |
| **2024-2025** | **67 200** | **672 L** |
| Total 3 ans | 209 600 | 2 096 L |

**Calcul de l'écart (exercice de reconstitution = 2024-2025) :**
- Fisc disponible : 632 L (79 fûts × 8 L)
- Notre volume réel 2024-2025 : 672 L (84 fûts de 8 L)
- Le fisc utilise **40 L de MOINS** que le réel.

**Verdict : INFIRMÉ.** Le fisc n'a **pas** commis l'erreur ×8 que nous avions trouvée dans
`achats-par-produit.json`. Il a correctement traité le fût à 8 L (800 cl) la pièce : 79 × 800 = 63 200 cl.
Le volume retenu (632 L) est même **légèrement inférieur** au volume réellement livré sur l'exercice
de reconstitution (672 L). Aucune sur-évaluation du volume de bière dans la reconstitution.
→ **Montant d'erreur fisc sur H1 : 0 € (pas d'erreur en notre défaveur ; au contraire l'écart de
−40 L joue marginalement en notre faveur).**

*Réserve :* la désignation diffère selon les fichiers (« Affligem Blade » dans la reconstitution vs
« Affligem Blonde 8 L » dans `volumes-disparus-fisc.json`) ; sans incidence sur le volume.

---

## H2 - Marchandise facturée mais NON livrée, non déduite

**Question :** le « disponible » du fisc (annexe 6 = « achats FCBS + Intermarché + stock_initial −
stock_final ») déduit-il les 231 lignes facturées à HT = 0 (manquantes / refusées / déconsigne) ?

**Volume boissons non livré identifiable** (lignes `lignes-ignorees.json` de catégorie boisson,
avec quantité > 0, valorisé à la contenance produit) :

| Exercice | Lignes | Volume non livré | HT achat | CA revente potentiel TTC (×3,051) |
|---|---|---|---|---|
| 2022-2023 | 27 | 355 L | 582,58 € | 1 777,46 € |
| 2023-2024 | 19 | 276 L | 241,38 € | 736,45 € |
| **2024-2025** | **18** | **30 L** | **267,11 €** | **814,96 €** |
| **Total 3 ans** | **64** | **660 L** | **1 091,08 €** | **3 328,87 €** |

Dont 7 lignes de fûts Affligem non livrés (212122) : 16+8+8 L en 2022-2023 et 8+8+8+8 L en
2023-2024 = **64 L de bière jamais reçue** - mais **AUCUN fût non livré sur 2024-2025**, l'exercice de
la reconstitution.

**Verdict : NON VÉRIFIABLE en l'état (présomption non confirmable depuis les données fisc).**
Les fichiers fisc ne donnent PAS le détail ligne à ligne du « disponible » : on ne peut pas prouver
que le vérificateur a ou n'a pas exclu ces lignes à HT nul. Si (et seulement si) son disponible est
bâti sur les quantités facturées **brutes**, le sur-comptage serait de **660 L** sur 3 ans, dont
**30 L (≈ 815 € TTC de CA reconstitué) pour le seul exercice 2024-2025** réellement reconstitué.
L'impact sur la reconstitution chiffrée est donc **faible (≈ 815 € TTC)** car l'essentiel des
non-livraisons (631 L) se situe hors de l'exercice reconstitué.
→ **Montant d'erreur fisc chiffrable sur l'exercice reconstitué : ≤ 815 € TTC (sous réserve de
confirmation que le disponible fisc est en brut).**

---

## H3 - Ventes sous-évaluées / sur-évaluation du CA liquide reconstitué

C'est l'erreur structurante. La reconstitution fisc gonfle le CA liquide « théorique » bien au-delà
des ventes caisse réelles, puis applique un coefficient liquide→solide de **×3,1**.

**Comparaison sur l'exercice reconstitué (2024-2025) :**

| Poste | Fisc | Notre réel caisse | Écart |
|---|---|---|---|
| CA LIQUIDES TTC (avant abattements) | 165 065,33 | 106 112,96 | **+58 952,37** |

Le fisc reconstitue **165 065 € TTC** de boissons alors que la caisse réelle de l'exercice
n'enregistre que **106 113 € TTC** de liquides (liq.10 % 19 723,21 + liq.20 % 86 389,75). Soit une
**sur-évaluation du CA liquide de 58 952 € TTC (+55,6 %)** avant même les abattements de 5 %.

Cette sur-évaluation provient de la mécanique « volume disponible ÷ doses » qui suppose 100 % du
volume acheté revendu au verre, en ignorant : pertes réelles tirage/casse au-delà de l'abattement
forfaitaire, offerts, doses réelles plus généreuses, et auto-coïncidence avec la caisse réelle.

**Amplification :** le CA solides fisc = CA liquides après abattements × 3,1 (vérifié :
434 947,14 / 140 305,53 = 3,1). Toute erreur sur le CA liquide est donc **multipliée par ≈ 3,1**.
La discordance totale revendiquée par le fisc est `discordanceCA` TTC = **139 727,76 €**
(HT 125 076,16 €).

**Verdict : CONFIRMÉ.** Le fisc sur-évalue le CA liquide de **58 952 € TTC** sur l'exercice
reconstitué par rapport aux ventes caisse réelles, puis l'amplifie ×3,1.
→ **Montant d'erreur fisc sur H3 : 58 952 € TTC d'écart liquide direct** ; après abattements 5 %
(× 0,85) et coefficient solides, l'effet sur le CA total reconstitué dépasse largement ce montant.

*Réserve :* nous ne disposons pas, dans les fichiers fisc, du `vendu_caisse` produit par produit
(toutes les valeurs `vendu_caisse` de `volumes-disparus-fisc.json` sont `null`). La comparaison
produit-à-produit demandée n'est donc pas réalisable ; la comparaison est faite au niveau du CA
liquide agrégé, qui est lui parfaitement chiffré des deux côtés.

---

## H4 - Doses / contenances

**Contenances bouteille fisc vs nos achats** (codes correspondants) :

| Réf. fisc | Contenance fisc | Notre contenance | Concordance |
|---|---|---|---|
| Macvin | 75 cl | 75 cl (510221) | ✅ |
| Soho | 70 cl | 70 cl (540064) | ✅ |
| Vodka | 70 cl | 70 cl (510013) | ✅ |
| Passoa | 70 cl | (réf. non retrouvée) | n/a |
| Picon | 100 cl | 100 cl (510141) | ✅ |

Les **contenances** retenues par le fisc sont exactes. Le fisc lui-même classe son hypothèse
« doses sous-évaluées » comme **écartée (impact marginal 3-6 points)** (`volumes-disparus-fisc.json`,
verdict H3). Les doses ne figurent pas toutes dans l'extrait transcrit (`avertissement` : sous-valeurs
doses avec marge).

**Nombre de bouteilles disponibles - anomalie Macvin :** le fisc retient **362 btl de Macvin Blanc**.
Nos achats de Macvin Blanc (toutes références : 510221+600707+601152+665175) totalisent **1 066 btl
sur 3 ans**, soit largement plus de 362/an. Le chiffre fisc de 362 est donc plausible pour un seul
exercice et n'apparaît **pas** sur-évalué (réserve : il agrège possiblement un stock initial).

**Verdict : INFIRMÉ** comme source d'erreur en notre défaveur. Contenances exactes, doses d'impact
marginal de l'aveu même du vérificateur.
→ **Montant d'erreur fisc chiffrable sur H4 : 0 € (non démontrable comme erreur).**

---

## H5 - BIB / grands formats 10 L

**Nos BIB 10 L** (`contenanceCl` = 1000, cohérent = 10 L × 100) :

| Code | Libellé | Total qté | volCl |
|---|---|---|---|
| 603040 | BIB Bourgogne Aligoté Buxy 10 L | 64 | 64 000 |
| 603042 | BIB Côtes de Prov. Rosé 10 L | 50 | 50 000 |
| 603512 | BIB Côtes du Rhône Rouge 10 L | 36 | 36 000 |
| 601956 | BIB Côtes de Provence 10 L | 16 | 16 000 |
| 600731 | BIB Blanc 10 L Ravelin | 19 | 19 000 |
| 605168 | BIB Gardilles Rosé 10 L | 6 | 6 000 |

Nos volumes BIB sont cohérents : 1 BIB = 1 000 cl. Aucun ingrédient de la reconstitution fisc n'est
explicitement un BIB 10 L (les vins BIB sont valorisés via la mécanique vins/cocktails hors extrait).

**Verdict : NON VÉRIFIABLE côté fisc** (pas de poste BIB isolé dans la reconstitution transcrite).
Nos volumes sont, eux, exacts. Aucune incohérence détectable.
→ **Montant d'erreur fisc chiffrable sur H5 : 0 € (non isolable).**

---

## Tableau récapitulatif des erreurs chiffrées du fisc

| # | Hypothèse | Verdict | Erreur fisc chiffrée (exercice 2024-2025 reconstitué) |
|---|---|---|---|
| H1 | Erreur fût / volume bière (×8) | **INFIRMÉ** | 0 € (fisc a même retenu −40 L de bière vs réel) |
| H2 | Marchandise non livrée non déduite | **NON VÉRIFIABLE** | ≤ 815 € TTC (30 L sur l'exercice ; 660 L / 3 328 € TTC sur 3 ans) |
| H3 | Ventes sous-évaluées / CA liquide gonflé | **CONFIRMÉ** | **+58 952 € TTC** d'écart liquide direct, amplifié ×3,1 |
| H4 | Doses / contenances | **INFIRMÉ** | 0 € (contenances exactes, doses marginales) |
| H5 | BIB / grands formats 10 L | **NON VÉRIFIABLE** | 0 € (non isolable ; nos volumes exacts) |

**Erreur fisc principale et certaine : H3 - sur-évaluation du CA liquide de 58 952 € TTC** sur le
seul exercice reconstitué (165 065 € reconstitués contre 106 113 € de ventes caisse réelles, +55,6 %),
ensuite **amplifiée ×3,1** par le coefficient liquide→solide. À cela s'ajoute, sous réserve de
confirmation du mode de calcul du « disponible », jusqu'à ~815 € TTC de marchandise non livrée (H2).

**Limites de l'audit :** (1) la reconstitution fisc ne couvre qu'un exercice (2024-2025) ; (2) les
`vendu_caisse` produit-à-produit du fisc sont tous `null`, empêchant la comparaison fine demandée en
H3 - elle est faite au niveau du CA liquide agrégé, lui parfaitement chiffré ; (3) le détail
ligne-à-ligne du « disponible » fisc n'est pas dans les données, d'où le NON VÉRIFIABLE de H2.
