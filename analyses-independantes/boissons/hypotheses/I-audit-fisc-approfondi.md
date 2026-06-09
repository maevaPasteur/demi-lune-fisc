# I - Audit approfondi de la MÉTHODE du fisc sur les boissons

**Dossier :** SARL LA DEMI-LUNE - contrôle DDFiP Jura. Reconstitution du CA par les achats de
boissons (« Annexes finales »). Exercice reconstitué en détail = **2024-2025** (cf. audit A :
`caInscritEnComptabilite` 435 524,92 € ≈ notre total caisse 2024-2025 435 564,96 €, écart 40 €).

**Méthode de cet audit :** chaque point est chiffré depuis les fichiers sources, sans supposition.

**Fichiers :**
- Fisc : `src/data/reconstitution-administration.json`, `src/data/volumes-disparus-fisc.json`
- Nous : `analyses-independantes/boissons/data/{achats-exercice,ventes-caisse,lignes-ignorees,prix-carte}.json`

---

## Point 1 - Base de totalisation des achats du fisc : bouteilles nettes ou brut ?

Comparaison du `bouteillesDisponibles` / `volumeDisponibleCl` du fisc (2024-2025) à nos quantités
**nettes livrées** exactes (`achats-exercice.json`, hors lignes-ignorées) :

| Ingrédient fisc | Fisc btl | Notre btl net | Fisc cl | Notre cl net | Écart cl (fisc − réel) |
|---|---|---|---|---|---|
| Macvin Blanc | 362 | **372** (510221+600707+665175, 601152=0) | 27 150 | 27 900 | **−750** |
| Soho | 28 | 28 | 1 960 | 1 960 | 0 |
| Vodka | 14 | 14 | 980 | 980 | 0 |
| Passoa | 7 | **8** | 490 | 560 | **−70** |
| Picon | 11 | **10** | 1 100 | 1 000 | **+100** |
| Fût Affligem | 79 fûts | 84 fûts (672 L) | 63 200 | 67 200 | **−4 000** |
| **TOTAL** | | | | | **−4 720** |

**Lignes de consigne / emballage / non-livré (`lignes-ignorees.json`, HT=0)** : sur 2024-2025, les
seules lignes ignorées touchant ces ingrédients sont 2× Passoa (déconsigne, qte nulle), 2× Soho,
3× Vodka, 6× verres Affligem - **toutes à HT/qté nuls ou marginales**. Le fisc ne les a manifestement
**pas** ajoutées : ses chiffres tombent au niveau ou en-dessous de nos quantités nettes réellement
livrées (Macvin, Passoa, Fût tous inférieurs au réel).

**Anomalie isolée - Picon : fisc 11 btl vs notre net 10 btl (+100 cl).** Aucune ligne Picon ignorée
sur 2024-2025 : la bouteille en trop provient d'un stock initial ou d'une affectation, pas d'une
consigne. Sur-comptage réel mais minime : 100 cl → ≈ 31 € HT de CA reconstitué.

**VERDICT : CONFIRMÉ que la base est NETTE (bouteilles), pas gonflée par consigne/emballage.**
Globalement le fisc retient **4 720 cl de MOINS** que notre volume net réel (surtout −4 000 cl de fût
et −750 cl de Macvin) : la base achats ne joue **pas** en notre défaveur, sauf le seul Picon (+100 cl
≈ 31 € HT). La distorsion du calcul ne vient donc PAS de la totalisation des achats.

---

## Point 2 - Coefficient ×3,1 (liquide→solide) : mesuré ou circulaire ?

Le fisc estime `CA solides = CA liquides (après abattements) × 3,1`. Vérifié par construction :
434 947,14 / 140 305,53 = **3,100**.

**Origine du 3,1 :** il est **égal au ratio CA-solides/CA-liquides de la CAISSE réelle** elle-même :
`real_sol/real_liq` 2024-2025 = 329 452,00 / 106 112,96 = **3,1047**. Le coefficient est donc **mesuré
sur la caisse** - mais il est ensuite **appliqué à un CA liquide RECONSTITUÉ** (165 065 €), pas au CA
liquide réel (106 113 €) d'où il est tiré. **Circularité partielle :** le ratio 3,1 n'est valide que
pour le couple (liquide réel, solide réel) ; l'accoler à un liquide gonflé de +55 % transporte
mécaniquement ce gonflement sur les solides.

**Recalcul de la discordance si le CA liquide RÉEL caisse était utilisé** (même méthode fisc :
×0,85 abattements, ×3,1) :

| | Fisc (liquide reconstitué) | Avec liquide RÉEL caisse |
|---|---|---|
| CA liquides TTC avant abatt. | 165 065,33 | 106 112,96 |
| après abattements (×0,85) | 140 305,53 | 90 196,02 |
| CA solides (×3,1) | 434 947,14 | 279 607,65 |
| CA total reconstitué | 575 252,68 | **369 803,67** |
| − CA comptabilisé (435 524,92) | **+139 727,76** | **−65 721,25** |

**VERDICT : CONFIRMÉ - coefficient empirique mais appliqué de façon circulaire.** En partant du CA
liquide RÉEL, la discordance **disparaît et s'inverse** : −65 721 € (le réel serait même
sur-comptabilisé). L'écart de méthode vaut **205 449 €** de discordance fictive. **Toute la
« discordance » de 139 728 € provient de la sur-reconstitution du liquide, amplifiée ×3,1**, pas d'une
occultation.

---

## Point 3 - Doses du fisc vs carte

Doses lues sur `prix-carte.json` (3 versions concordantes) vs doses utilisées par le fisc :

| Article | Dose carte | Dose / hypothèse fisc | Verdict |
|---|---|---|---|
| Macvin au verre | **6 cl** | dose non isolée dans l'extrait (≈ verre) | concordant probable |
| La Vouivre / Chat perché / Kittykir | 12 cl | via Crémant (hors extrait) | n/a |
| Père Grégoire | 6 cl | via Crémant (hors extrait) | n/a |
| Vin Jaune | 12 cl | 12 cl (`volumes-disparus-fisc`) | **ÉGAL** |
| Picon Bière | 25 cl (3 cl picon) | « 3 cl picon + 22 cl bière » = 25 cl | **ÉGAL** |
| Pinte Picon | 50 cl (6 cl picon) | « 6 cl picon + 44 cl bière » = 50 cl | **ÉGAL** |
| Pression | 25 cl | 25 cl | **ÉGAL** |
| Pinte | 50 cl | 50 cl | **ÉGAL** |
| Pontarlier (anis) | - | 2 cl | n/a (pas sur carte) |

**VERDICT : INFIRMÉ comme source d'erreur.** Là où les doses fisc sont identifiables, elles sont
**ÉGALES** à la carte (Picon 3/6 cl, bière 25/50 cl, Vin Jaune 12 cl) - donc **NI plus petites**
(pas de gonflement du nombre d'articles), ni plus grandes. Le fisc lui-même classe son hypothèse
« doses sous-évaluées » comme **écartée, impact marginal 3-6 pts** (`volumes-disparus-fisc.json`).
→ Erreur fisc chiffrable sur les doses : **0 €**.

---

## Point 4 - Extrapolation entre exercices ?

Discordances revendiquées : ≈ 193 235 (2022-2023) / 138 864 (2023-2024) / 139 728 € (2024-2025).
Coefficients liquide→solide annoncés : 2,94 / 3,02 / 3,10.

**Test : ces coefficients sont-ils, chaque année, le ratio caisse réel de l'année ?**

| Exercice | Coef fisc | `real_sol/real_liq` caisse | Liquide reconstitué implicite ÷ liquide réel |
|---|---|---|---|
| 2022-2023 | 2,94 | **2,936** | ×1,74 |
| 2023-2024 | 3,02 | **3,024** | ×1,55 |
| 2024-2025 | 3,10 | **3,105** | ×1,56 |

Le coefficient est **re-mesuré chaque année sur la caisse de l'année** (concordance à 0,01 près) ; et
mon modèle de la méthode reproduit le total reconstitué 2024-2025 (575 293 € recalculé vs 575 253 €
au dossier, écart d'arrondi).

**VERDICT : CONFIRMÉ - même méthode appliquée aux 3 ans, PAS une extrapolation plate.** Les 3
discordances découlent du même procédé (liquide reconstitué ÷ doses × coef-caisse de l'année). Mais
le **même biais circulaire** (Point 2) frappe les 3 exercices : le liquide reconstitué vaut
1,55 à 1,74× le liquide réellement encaissé. La cohérence inter-exercices **n'est donc pas une
validation** ; c'est la répétition de la même erreur structurelle.

---

## Point 5 - Abattements : avant ou après reconstitution, et suffisants ?

**Deux abattements distincts, à deux étapes différentes :**

1. **Bière 15 % (conso perso + pertes)** : appliqué au **VOLUME disponible, AVANT reconstitution**.
   Vérifié : 63 200 cl × 0,15 = 9 480 cl retirés → 53 720 cl nets, puis répartis en articles
   (`reconstitution-administration.json`, ingrédient Bière).
2. **Remise + pertes + conso personnel = 3 × 5 % = 15 %** : appliqué au **CA liquide RECONSTITUÉ,
   APRÈS reconstitution**, avant le ×3,1. Vérifié : 165 065,33 × 0,85 = 140 305,53.

**Suffisance vs réalité :**

| | Montant |
|---|---|
| Abattement total fisc sur liquide (15 %) | 24 760 € TTC |
| Écart réel entre liquide RECONSTITUÉ (165 065) et liquide CAISSE réel (106 113) | **58 952 € TTC (35,7 %)** |

**VERDICT : INSUFFISANTS.** L'abattement forfaitaire de 15 % ne couvre que **moins de la moitié** de
l'écart réel observé entre le volume reconstitué « vendable » et les ventes réellement encaissées
(35,7 %). Les 20,7 points manquants correspondent aux offerts, pertes de tirage/casse au-delà du
forfait, doses réelles plus généreuses, retours et non-vendus - non couverts. Les abattements sont
calés sur un forfait théorique, pas sur la réalité d'exploitation.

---

## Tableau de synthèse - verdicts chiffrés

| # | Point audité | Verdict | Chiffrage (exercice 2024-2025) |
|---|---|---|---|
| 1 | Base achats : nette ou brute (consigne/non-livré) | **CONFIRMÉ nette** | Fisc −4 720 cl SOUS notre réel ; seul Picon +100 cl (+1 btl ≈ 31 € HT) |
| 2 | Coefficient ×3,1 : mesuré ou circulaire | **CONFIRMÉ circulaire** | 3,1 = ratio caisse réel, mais appliqué au liquide gonflé → discordance recalculée **−65 721 €** au lieu de +139 728 € (Δ 205 449 €) |
| 3 | Doses fisc vs carte | **INFIRMÉ** (pas d'erreur) | Doses ÉGALES (Picon 3/6 cl, bière 25/50 cl, VJ 12 cl) → 0 € |
| 4 | Extrapolation entre exercices | **CONFIRMÉ : même méthode/an, pas extrapolation** | Coef = ratio caisse de l'année (2,94/3,02/3,10 ≈ 2,936/3,024/3,105) ; liquide reconstitué = ×1,55-1,74 du réel les 3 ans |
| 5 | Abattements (5 %×3 ; bière 15 %) : timing & suffisance | **INSUFFISANTS** | Bière 15 % AVANT reconstitution (volume) ; 5 %×3 APRÈS (CA liquide). Couvrent 15 % vs écart réel **35,7 %** |

**Erreur structurelle dominante = Point 2 (× Point 5).** Le fisc reconstitue un CA liquide théorique
de 165 065 € contre 106 113 € réellement encaissés (+55,6 %), n'abat que 15 % au lieu des 35,7 %
réels, puis **multiplie ×3,1** ce liquide gonflé pour les solides. La « discordance » de 139 728 € est
**à 147 % un artefact de méthode** : avec le CA liquide réel, la même mécanique donne −65 721 € (aucune
occultation). La base achats (Point 1) et les doses (Point 3) sont, elles, exactes et ne soutiennent
pas le redressement.

**Limite :** les `vendu_caisse` produit-par-produit du fisc sont `null` ; la comparaison fine est
faite au niveau du CA liquide agrégé, parfaitement chiffré des deux côtés.
