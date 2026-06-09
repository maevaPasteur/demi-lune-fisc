# K — Sous-attribution par catégorie (soft, sirop, spiritueux, macvin)

**Hypothèse testée :** l'écart achats−ventes des catégories à fort taux (soft 68 %, sirop 75 %, spiritueux 68 %, macvin 59 %) s'explique en partie par une **sous-attribution** : du volume réellement vendu mais non capté dans le « vendu », parce qu'il part dans des boissons composées non rattachées, ou à dose réelle > dose carte.

**Verdict : hypothèse VALIDÉE seulement pour le sirop. Marginale ailleurs.**
Sources : `data/disparitions.json`, `data/ventes-caisse.json` (3 exercices cumulés), `data/map-*.json`, `data/prix-carte.json`. Coût = PU achat HT moyen / contenance.

---

## Méthode

On distingue, par catégorie :
- **Sous-attribution VÉRIFIABLE** = volume qu'une recette de la carte impose mais que les `map-*.json` ne créditent pas (ingrédient « vide ») ou créditent à dose < carte → ce volume **réduit légitimement l'écart**.
- **Reste inexpliqué** = écart résiduel après correction (= disparition réelle / surstock / conso interne, traités par d'autres hypothèses).

Attention double-comptage : les cocktails de `map-cocktails.json` (Vouivre, Père Grégoire, Chat perché, Tequila Sunrise, Balidou, Rêve Bleu, Maëva, Rabasse, Café Irlandais…) **créditent déjà** leurs spiritueux/macvin dans le « vendu » de `disparitions.json`. On ne les recompte pas.

---

## 1. SOFT — écart 252 954 cl (2 530 L, 68 %)

**Conclusion : la sous-attribution est négligeable (14 L, 0,6 % de l'écart).**

- Les sodas sont attribués en méthode **« direct »** (`map-eaux-softs.json`) : 1 boîte 33 cl = 1 service, le « Coca (25 cl) » caisse crédite **les 33 cl** entiers de la boîte. → **aucun gain** à attendre d'un ratio boîte/service : le volume acheté est déjà entièrement compté par service vendu.
- Seul long drink soda de la carte : **Whisky-Coca** (bouton 0351, **70 ventes**), dont la part Coca (~20 cl) n'est pas attribuée à la catégorie soft → **14 L, ~28 €**.
- Tequila Sunrise / Balidou / Rêve Bleu utilisent du **jus** (catégorie jus) + sirop, pas de soda → rien à reverser au soft.

Le vrai problème soft est volumétrique et brut : **Coca 5 952 boîtes achetées vs 1 255 services caisse** (4 697 boîtes « manquantes »), idem Fuze Tea, Orangina, Fanta. Ce n'est **pas** de la sous-attribution.

| | Volume | Coût HT |
|---|---|---|
| Sous-attribution vérifiable | **14 L** | **28 €** |
| Reste inexpliqué | 2 516 L (68 % des achats) | — |

---

## 2. SIROP — écart 12 629 cl (126 L, 75 %)

**Conclusion : sous-attribution RÉELLE et significative — 46 L, ~192 €, soit 37 % de l'écart corrigé.**

Deux corrections légitimes :
1. **Dose réelle de sirop > carte.** « Sirop à l'eau », « Diabolo », « Monaco » sont attribués à **2 cl** dans `map-eaux-softs.json` (hypothèse standard, non écrite sur la carte qui ne donne que le volume total 25 cl). Dose métier réaliste **3,5 cl** → **+1,5 cl** sur 1 295 services (748 + 350 + 196) = **1 942 cl**.
2. **Sirop des cocktails non crédité à la catégorie sirop.** Kittykir (framboise), Tequila Sunrise (grenadine), Balidou (framboise), Rêve Bleu (curaçao bleu), Rosé Pamp (pamplemousse) — 1 332 ventes — embarquent ~2 cl de sirop chacun, non rattachés = **2 664 cl**.

| | Volume | Coût HT |
|---|---|---|
| Sous-attribution vérifiable | **46,1 L** | **192 €** |
| Reste inexpliqué | 80 L (47 % des achats) | — |

Note : grenadine déjà sur-vendue (vendu > acheté) ; les parfums Monin framboise/pêche/orange/cerise/menthe… (≈14 L chacun) restent à 0 vendu = candidats sous-attribution diffuse non chiffrable bouton par bouton, mais la correction ci-dessus la matérialise.

---

## 3. SPIRITUEUX / DIGESTIF — écart 46 156 cl (462 L, 68 %)

**Conclusion : sous-attribution limitée — 29 L, ~258 €, via le Kir (6 % de l'écart).**

- **Crème de cassis 15° (591008)** : achat 9 000 cl, vendu 2 120 cl, écart 6 880 cl. Elle n'est créditée qu'à **La Vouivre (1 cl)** dans `map-cocktails.json`. Or les boutons **Kir Bourgogne (1 369), Kir Princier (90), Kir Pamplemousse (7)** ont des ingrédients **VIDES** : la part cassis (~2 cl/Kir) n'est **pas** attribuée → **2 932 cl = 29,3 L, ~258 €** (43 % de l'écart cassis).
- Tous les autres spiritueux des cocktails (tequila, passoä, vodka, soho, anis/sapin, clan campbell) sont **déjà** crédités via `map-cocktails.json` → pas de gain net.
- Porto rouge (12 825 cl achetés, 780 cl attribuables au bouton Porto 6 cl), Calvados, Aperol (2 100 cl, 0 vendu, aucun bouton Spritz), absinthes : écarts **massifs non liés à une recette** → disparition/surstock réel, hors sous-attribution.

| | Volume | Coût HT |
|---|---|---|
| Sous-attribution vérifiable (Kir cassis) | **29,3 L** | **258 €** |
| Reste inexpliqué | 432 L (64 % des achats) | — |

---

## 4. MACVIN — écart 47 607 cl (476 L, 59 %)

**Conclusion : AUCUNE sous-attribution résiduelle. L'écart est un surstock sur 2 références.**

- Cocktails (Vouivre 5,5 cl × 2 120, Père Grégoire 3 cl × 1 608, Chat perché 6 cl × 1 664 = 26 470 cl) **et** Macvin au verre (bouton 0003, 1 092 ventes) sont **déjà** dans le vendu (33 018 cl). Rien de plus à reverser côté caisse.
- L'écart résiduel se concentre sur **2 références sur-achetées et quasi non vendues** : Rolet (251 L) + Jacobin (179 L) = **430 L des 476 L** (90 %). La réf réellement débitée (Tissot) est équilibrée (307 L achetés / 278 L vendus).
- → Relève de la **substitution de référence / constitution de stock** (cf. hypothèses C et J), pas d'une sous-attribution de dose. Usage cuisine éventuel déjà couvert par hypothèse D.

| | Volume | Coût HT |
|---|---|---|
| Sous-attribution vérifiable | **0 L** | **0 €** |
| Reste inexpliqué | 476 L (dont 430 L = surstock Rolet + Jacobin) | — |

---

## Synthèse chiffrée

| Catégorie | Écart initial | Sous-attribution vérifiable | Coût HT | Reste inexpliqué |
|---|---|---|---|---|
| Soft | 2 530 L (68 %) | 14 L (0,6 %) | 28 € | 2 516 L (68 %) |
| Sirop | 126 L (75 %) | **46 L (37 %)** | 192 € | 80 L (47 %) |
| Spiritueux | 462 L (68 %) | 29 L (6 %) | 258 € | 432 L (64 %) |
| Macvin | 476 L (59 %) | 0 L | 0 € | 476 L (59 %) |
| **TOTAL** | | **89 L** | **478 €** | |

**Lecture défense :** la sous-attribution est une correction **honnête mais modeste (478 € HT)**. Elle est réelle et bien documentée pour le **sirop** (dose carte sous-estimée 2 cl vs 3,5 cl + sirop des cocktails) et le **Kir** (crème de cassis non rattachée). Elle ne « sauve » **pas** les écarts soft et macvin, qui relèvent d'autres mécanismes (surstock 2 réfs macvin, conso interne / disparition brute sodas). À ne PAS surjouer face au contrôle : présenter ces 478 € comme une correction de méthode vérifiable, pas comme l'explication des écarts.
