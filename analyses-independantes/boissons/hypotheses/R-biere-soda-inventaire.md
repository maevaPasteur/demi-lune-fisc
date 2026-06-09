# R — Bière & Soda : réconciliation par l'inventaire physique

**Question :** en intégrant les inventaires physiques réels (3 dates), l'identité
`stock_initial + achats − ventes − consommation = stock_final` boucle-t-elle ? Le « trou » Coca disparaît-il ?

**Méthode.** Aucune supposition. On apparie, produit par produit, l'inventaire physique
(`public/documents/inventaires/inventaires.json`, 3 dates : 2023-03-31, 2024-03-31, 2025-03-31)
avec les achats/ventes par exercice (`analyses-independantes/boissons/data/disparitions.json`,
fût via `achats-exercice.json`). On ne raisonne que sur les **2 exercices à inventaire d'ouverture ET de clôture** :
2023-2024 (31/03/2023 → 31/03/2024) et 2024-2025 (31/03/2024 → 31/03/2025).

Pour chaque produit/exercice : `SF_théorique = SI + achats − ventes`, puis
`consommation_hors_vente = SF_théorique − SF_réel (inventaire)`.

> Le fichier disparitions suppose explicitement stock initial = stock final = 0 (caveat n°4).
> L'inventaire corrige ce point : c'est tout l'objet de cette note.

---

## 1. Verdict honnête : l'inventaire NE referme PAS le trou soda — il le confirme

Le stock physique de Coca est **quasi plat** sur 3 ans alors que les achats explosent :

| Date inventaire | Coca-Cola 33cl en stock |
|---|---|
| 31/03/2023 | **92** canettes |
| 31/03/2024 | **116** |
| 31/03/2025 | **118** |

- Achats 3 ans (factures) : **5 952** canettes (196 416 cl, 3 861 € HT, 115 lignes de facture).
- Ventes caisse 3 ans : **1 255** canettes.
- Variation de stock réelle : **+26** canettes seulement.
- **Résiduel non vendu / non stocké = 5 952 − 1 255 − 26 = 4 671 canettes** sur 3 ans (~1 557/an).

L'inventaire prouve que ces ~4 670 canettes ne dorment PAS en réserve : il n'y a jamais plus de
~118 canettes en stock. Achetées, non passées en caisse, absentes des rayons → **consommées hors-vente**
(personnel, famille, offerts, pertes). C'est le point dur et il faut le dire tel quel : **le sort du
Coca ne se justifie pas par du stock.**

### Coca par exercice complet (en canettes)

| Exercice | SI | + achats | − ventes | = SF_théo | SF_réel | conso hors-vente |
|---|---|---|---|---|---|---|
| 2023-2024 | 92 | 1 488 | 399 | 1 181 | **116** | **1 065** |
| 2024-2025 | 116 | 1 752 | 403 | 1 465 | **118** | **1 347** |

---

## 2. Autres sodas (canettes/bouteilles, exercices complets)

| Produit | Ex. | SI | +achats | −ventes | SF_théo | SF_réel | conso HV |
|---|---|---|---|---|---|---|---|
| Fanta 33cl | 2023-24 | 23 | 72 | 36 | 59 | 26 | 33 |
| Fanta 33cl | 2024-25 | 26 | 144 | 40 | 130 | 41 | 89 |
| Orangina 33cl | 2023-24 | 13 | 144 | 71 | 86 | 50 | 36 |
| Orangina 33cl | 2024-25 | 50 | 144 | 73 | 122 | 46 | 76 |
| Schweppes 33cl | 2023-24 | 34 | 120 | 72 | 82 | 52 | 30 |
| Schweppes 33cl | 2024-25 | 52 | 96 | 71 | 77 | 27 | 50 |
| Fuzetea 33cl | 2023-24 | 26 | 456 | 204 | 279 | 39 | 240 |
| Fuzetea 33cl | 2024-25 | 39 | 288 | 198 | 130 | 57 | 73 |
| Limonade 1L | 2023-24 | 14 | 228 | 133 | 110 | 15 | 95 |
| Limonade 1L | 2024-25 | 15 | 216 | 133 | 98 | 23 | 75 |

Même schéma partout : le stock réel reste bas et stable, le résiduel hors-vente est systématique.

---

## 3. Fût Affligem — réconciliation en litres (1 fût = 8 L)

L'inventaire compte des **fûts** : 4 (2023), 5 (2025). La ligne 2024-03-31 « Fût Affligem Blade 8L »
porte `qte=32` **`fiabilité=a_verifier`** : lu comme **4 fûts (32 L)** — cohérent avec 2023/2025 et
avec la réalité d'exploitation (un restaurant ne stocke pas 32 fûts = 256 L d'une seule bière). Achats
en litres facturés (`achats-exercice.json`, ~3,6–4,3 €/L) ; ventes pression converties en litres.

| Exercice | SI | + achats | − ventes | SF_théo | SF_réel | conso hors-vente |
|---|---|---|---|---|---|---|
| 2023-2024 | 32 L (4 fûts) | 632 L | 381 L | 283 L | 32 L (4 fûts) | **~251 L** |
| 2024-2025 | 32 L (4 fûts) | 672 L | 385 L | 319 L | 40 L (5 fûts) | **~279 L** |

Le fût ne se cache pas non plus en stock (toujours 4-5 fûts) : ~250-280 L/an de bière pression
achetée n'apparaissent ni en caisse ni en inventaire.

---

## 4. Bilan par catégorie (volume, exercices complets)

Inventaire valorisé en cl, fût 2024-03-31 corrigé à 4 fûts.

| Catégorie | Ex. | SI (cl) | +achats | −ventes | SF_théo | SF_réel | conso HV (L) |
|---|---|---|---|---|---|---|---|
| Bière | 2023-24 | 5 741 | 76 992 | 46 359 | 36 374 | 4 553 | **~318** |
| Bière | 2024-25 | 4 553 | 92 356 | 47 171 | 49 738 | 5 188 | **~446** |
| Soft | 2023-24 | 7 604 | 108 872 | 39 036 | 77 440 | 10 839 | **~666** |
| Soft | 2024-25 | 10 839 | 115 364 | 39 183 | 87 020 | 11 837 | **~752** |
| Eau | 2023-24 | 7 727 | 51 448 | 30 766 | 28 408 | 4 950 | **~235** |
| Eau | 2024-25 | 4 950 | 51 064 | 30 207 | 25 807 | 8 387 | **~174** |
| Jus | 2023-24 | 2 325 | 24 900 | 16 940 | 10 285 | 5 375 | **~49** |
| Jus | 2024-25 | 5 375 | 30 900 | 16 214 | 20 062 | 5 300 | **~148** |
| Sirop | 2023-24 | 1 400 | 5 960 | 1 420 | 5 940 | 1 180 | **~48** |
| Sirop | 2024-25 | 1 180 | 4 860 | 1 501 | 4 539 | 740 | **~38** |

---

## 5. Conclusion — ce que l'inventaire prouve réellement

1. **Il ne reste quasiment rien en stock** dans aucune catégorie : les stocks de clôture sont faibles et
   stables d'une année sur l'autre. La défense « les boissons s'accumulent en réserve » ne tient pas.
2. Donc, une fois le stock réel pris en compte, **l'écart achats − ventes ne se réduit presque pas** : il
   se transforme intégralement en **consommation hors-vente** (personnel, repas famille, offerts, pertes,
   casse, cuisine). C'est un poste réel et chiffrable, ce n'est PAS une disparition au sens fraude de TVA
   si — et seulement si — ces usages sont justifiés et documentés.
3. **Le soda est le point sensible et il faut l'assumer :** ~4 670 canettes de Coca sur 3 ans
   (~1 555/an) sont achetées, non vendues et non stockées. Aucun stock ne les explique. La seule défense
   crédible est de documenter la consommation hors-vente (note de personnel, boissons offertes,
   familiales), pas de prétendre qu'elles dorment en réserve.
4. Le fût Affligem se réconcilie proprement en litres (4-5 fûts en permanence) ; l'écart ~250-280 L/an
   est de même nature.

**Caveats données.** Fût 2024-03-31 `a_verifier` (lu 4 fûts) ; lignes soda 2024/2025 marquées
`a_verifier` (pages manuscrites) ; ventes attribuées par dose de carte (caveat disparitions) ; café/thé
hors périmètre fournisseur boissons. Aucune ligne inventoriée écartée hors résiduels sans produit.
