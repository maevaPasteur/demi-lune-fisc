# Vérifications d'exactitude - boissons disparues

> Contrôles menés sur les données et le calcul. Objectif : **zéro supposition, exact au centime**.
> Tout est reproductible (`scripts/boissons/01_extraction.py` + `02_disparitions.py`).

## 1. Biais d'unité par produit (coût au litre) - RÉSOLU

Test : pour chaque produit, `coût/L = HT / volume`. Un coût/L sous le minimum
plausible de sa catégorie trahit un volume sur-compté.

- **Constat initial** : le « FUT AFFLIGEM » ressortait à ~0,45 €/L (impossible).
- **Cause** : `achats-par-produit.json` multipliait `quantité × 800 cl`. Or sur la
  facture (n° 467442), un fût se lit `colis=3` (3 fûts), `quantité=24` (= **24 litres**,
  3 × 8 L), `puNet=3,59 €/L`, `HT=86,16 €` → **28,72 €/fût** : la quantité est en **litres**.
- **Correctif** : pour un fût, `volume = quantité × 100 cl` (et non × 800) ; coût/cl = `HT/volume`.
- **Après correctif** : plus aucun alcool sous 1 €/L. Bornes hautes plausibles
  (Vin Jaune 43-49 €/L, Champagne Ruinart 57,8 €/L). **La pression est incluse**
  (~270 fûts / 2 160 L sur 3 ans), valorisée 3 706 € au coût.

## 2. Autres formats facturés « au sous-multiple » - AUCUN

Test : pour toutes les lignes avec `colis` renseigné, ratio `quantité / colis`.

- Tous les ratios = tailles de carton standard : **24, 12, 6, 20, 18** (bouteilles/canettes par colis)
  → `quantité` = nombre de bouteilles, `volume = quantité × contenance` correct.
- **Seuls** les deux fûts (212120, 212122) ont un ratio **8** (= litres/fût) → déjà traité.
- **Conclusion : le fût était le seul cas de biais d'unité.**

## 3. Lignes non facturées (HT vide/0) - EXCLUES du volume

Test : lignes de facture sans `montantHT`.

- **231 lignes** à HT vide/0 : marchandise **manquante / refusée** (`M/SE MANQUANTE S/ CAMION`,
  `M/SE REFUSÉE PAR CLIENT`), **déconsigne** (`Ci-dessous Déconsigne`) ou échantillon.
- Elles ne correspondent à **aucune réception réelle** → elles ne comptent désormais
  **ni en coût ni en volume** (les avoirs à HT négatif, eux, sont conservés).
- Trace : `data/lignes-ignorees.json`. Ces lignes **corroborent** le carnet manuscrit
  (facturé non livré / refusé).
- **Contrôle** : le total des achats HT reste **137 971 €** (identique à `achats-par-produit.json`),
  car ces lignes valaient déjà 0 €. Seul le volume « disponible » est assaini.

## 4. Réconciliation des ventes caisse - EXACTE AU CENTIME

Test : mes totaux parsés vs les lignes `TOTAL CA LIQUIDES 10 %/20 %` internes aux fichiers D.

| Exercice | CA 10 % (moi vs fichier) | CA 20 % (moi vs fichier) |
|---|---|---|
| 2022-2023 | 20 514,18 = 20 514,18 | 81 911,20 = 81 911,20 |
| 2023-2024 | 20 010,27 = 20 010,27 | 88 909,01 = 88 909,01 |
| 2024-2025 | 19 723,21 = 19 723,21 | 86 389,75 = 86 389,75 |

- **Bug trouvé et corrigé** : une ligne-prix de continuation à **référence vide**
  (D2, ligne 73 : `36 € × 51 = 1 835,98 €`) était ignorée. Le parseur **reporte
  désormais la référence** du produit précédent. Les 6 totaux tombent **au centime**.

## 5. Matériel non-liquide - CONSERVÉ, volume nul

- 10 lignes verrerie / kits / pailles (≈ 283 € HT) : **conservées et documentées**
  (`type:"materiel"` dans `disparitions.json`), volume de boisson nul (ce ne sont pas
  des liquides). **Rien n'est exclu.**

## 6. Les 3 cartes (changements de prix) - PRISES EN COMPTE

Il existe **3 cartes** : 08/02/2021, 20/07/2021, 26/04/2023.

- **Doses identiques** sur les 3 cartes (Macvin 6 cl, verre 12 cl, Pastis 2 cl…) →
  l'attribution des **volumes** ne dépend pas de la version : aucun impact.
- **Prix différents** : 08/02/21 et 26/04/23 bas (Vouivre 5,20 €), 20/07/21 haut (5,90 €).
  Sur la période contrôlée : **2022-2023** relève de la carte du **20/07/2021**, puis
  **2023-2025** de la carte du **26/04/2023**.
- **Traitement** : la valorisation à la revente n'utilise pas un prix figé mais le
  **prix réellement encaissé en caisse, calculé PAR EXERCICE** (`prix_vente_cl` par année).
  C'est plus exact que la carte : ça capte l'évolution réelle des prix (ex. Macvin
  0,80 €/cl en 2022-2023 → ~0,99 €/cl ensuite ; Porto 0,70 → 0,82 €/cl).
- **Correctif appliqué** : la valorisation était auparavant moyennée sur 3 ans ; elle
  est désormais **par exercice** puis sommée.

## Chiffres finaux (3 exercices, bornes avant déductions)

| Indicateur | Cumul |
|---|--:|
| Achats boissons HT | **126 752,49 €** |
| CA boissons vendu TTC (caisse) | **317 457,62 €** |
| Disparition au coût d'achat HT (borne basse) | **58 059,52 €** |
| Disparition à la revente théorique TTC (borne haute) | **218 166,89 €** |
| Couverture du CA caisse attribuée | 88 - 90 % |

> Bornes **avant** déduction de la consommation du personnel, des offerts, des
> pertes/casse, des usages cuisine et de l'inventaire. Ces déductions seront des
> **paramètres de simulation** (voir `00-METHODOLOGIE.md`).
