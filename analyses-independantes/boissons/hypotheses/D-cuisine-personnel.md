# Hypothèse D - Cuisine, personnel, offerts, pertes/casse

**Objet.** Expliquer une partie de l'écart achats − ventes de boissons par les usages **hors vente directe** : alcool **en cuisine** (sauces, flambages, desserts), **consommation du personnel**, **offerts**, **pertes/casse**.

**Force du dossier.** Ces postes ne sont pas une hypothèse de la défense : **le vérificateur les a lui‑même intégrés** dans sa reconstitution. On reprend ses propres chiffres et ses propres taux.

**Périmètre chiffré (nos données).**
- Écart de boissons valorisé au **coût HT** sur les 3 exercices (2022‑2025) : **58 059,52 €**.
  Source : `analyses-independantes/boissons/data/disparitions.json` → `global.valDisparitionCoutHT.total` (réconcilié à l'euro avec la somme des catégories).

---

## 1. Déductions « cuisine » CHIFFRÉES par le fisc lui‑même

Le fisc a retiré du volume « vendable » des quantités affectées à la cuisine/aux desserts, **avant** de reconstituer le CA. Sources :
`src/data/reconstitution-administration.json` (champ `ingredients[].deductions`) et `src/data/volumes-disparus-fisc.json` (`produits[].note`).

| Produit | Déduction cuisine fisc | Plats cités par le fisc (source) | = en L | % de NOS achats du produit |
|---|---|---|---|---|
| **Macvin blanc** | **7 406 cl** | Baba au Macvin (561 art., 2 244 cl) + Saucisse flambée (547 art., 2 188 cl) + Menu Franc‑Comtois plat 38,74 % (1 244 cl) + dessert 53,84 % (1 729 cl) - *reconstitution p.159* | 74,1 L | **26,5 %** des achats Macvin blanc de l'exercice (7 406 / 27 900 cl) ; 9,3 % des 3 exercices |
| **Calvados** | **3 310 cl** | Sauces, repère D (déduit 2022‑2023) | 33,1 L | **103 %** des achats Calvados 2022‑2023 (3 200 cl) - la cuisine absorbe **tout** l'achat de l'exercice |
| **Porto Sandeman** | **398 cl** | Sauces forestière / morilles, repère G (2022‑2023) | 4,0 L | 12,6 % des achats Porto 2022‑2023 (3 150 cl) |
| **Absinthe** | **100 % du volume** (`caReconstitue: null`) | Crème brûlée (46,16 % des desserts) - *« non valorisée en boisson »* | 25,8 L (nos 2 580 cl) | **100 %** - le fisc n'attribue **aucune** vente boisson à l'absinthe |
| **Vin Jaune** | part **61,26 %** affectée au plat | Poulet à la Jurassienne (61,26 % des assiettes), dose 12 cl, repère E | n.c. (cl non publié) | la part majoritaire du produit est, de l'aveu du fisc, un usage cuisine |
| **Pontarlier (anis)** | usage cuisine reconnu (`cuisine_deduit: true`) | Rabasse, repère F, dose 2 cl | n.c. | usage cuisine confirmé |

**Verdict du fisc lui‑même** (`volumes-disparus-fisc.json` → `meta.verdict_hypotheses.H2`) :
> *« H2 usage cuisine ÉCARTÉE pour Porto / Calvados / Vin jaune / Macvin (**déjà déduits**) et Picon / Café / Bordeaux (aucun usage cuisine) ».*

Lecture : si le fisc « écarte » H2 sur ces produits, c'est uniquement **parce qu'il les a déjà déduits** - preuve directe que l'usage cuisine est réel et reconnu par l'administration. (Pour Picon, Café, Bordeaux : pas d'usage cuisine, on ne le revendique pas - cohérence.)

**Valorisation au coût HT** (cuisine fisc × notre prix d'achat moyen € / cl) :

| Poste cuisine | cl | €/cl (achat) | € coût HT |
|---|---|---|---|
| Macvin (Baba, Saucisse, Menu FC) | 7 406 | 0,1815 | 1 344,22 |
| Calvados (sauces, repère D) | 3 310 | 0,1682 | 556,69 |
| Porto (forestière/morilles) | 398 | 0,1075 | 42,77 |
| Absinthe (crème brûlée, 100 %) | 2 580 | 0,4023 | 1 037,83 |
| Vin Jaune (61,26 % Poulet Jurassien) | non chiffré par le fisc → **non valorisé** (prudence) | - | - |
| **Sous‑total cuisine chiffré** | | | **2 981,51 €** |

---

## 2. Abattements standard que le fisc s'applique à lui‑même

Source des taux : `reconstitution-administration.json` → `methode.abattements` et `notesMethodologiques` :
> *« Remise, pertes et consommation du personnel abattues à **5 % chacune** ; bière : abattement spécifique de **15 %** (conso personnel + pertes). »*

Le fisc abat ces taux sur le volume disponible **avant** de reconstituer. On les applique à **nos achats HT réels** par catégorie. Taux retenu pour expliquer du **volume/coût disparu** : **pertes 5 % + conso personnel 5 % = 10 %** (la remise 5 % est un abattement de **prix**, pas de volume - non comptée ici, prudence) ; **bière = 15 %**.

| Catégorie | Achats HT (3 ex.) | Taux fisc | € expliqué |
|---|---|---|---|
| bière | 12 164 | 15 % | 1 825 |
| vin | 63 772 | 10 % | 6 377 |
| crémant/pétillant | 11 439 | 10 % | 1 144 |
| macvin | 14 630 | 10 % | 1 463 |
| spiritueux/digestif | 10 775 | 10 % | 1 077 |
| soft | 6 911 | 10 % | 691 |
| jus | 3 355 | 10 % | 335 |
| eau | 2 754 | 10 % | 275 |
| sirop | 954 | 10 % | 95 |
| **TOTAL** | **126 752** | | **13 283 €** |

> Note : la **remise 5 %** du fisc (un 3ᵉ abattement, sur le prix) ajouterait encore ~6 340 € au CA expliqué côté ventes ; volontairement exclue du chiffrage « volume/coût » ci‑dessus pour rester conservateur.

---

## 3. Conclusion - part de l'écart expliquée par les propres chiffres du fisc

Cumul **cuisine + abattements standard**, plafonné à l'écart de chaque catégorie (**aucun double comptage** : la cuisine et le 10 % d'une même catégorie sont additionnés puis bornés à l'écart constaté de cette catégorie) :

| Catégorie | Écart coût HT | Abat. + cuisine | % de l'écart catégorie |
|---|---|---|---|
| bière | 5 670 | 1 825 | 32,2 % |
| vin | 22 509 | 6 377 | 28,3 % |
| crémant/pétillant | 5 799 | 1 144 | 19,7 % |
| macvin | 8 640 | 2 807 | 32,5 % |
| spiritueux/digestif | 7 338 | 2 715 | 37,0 % |
| eau | 1 085 | 275 | 25,4 % |
| jus | 1 618 | 335 | 20,7 % |
| soft | 4 689 | 691 | 14,7 % |
| sirop | 712 | 95 | 13,4 % |
| **TOTAL** | **58 060 €** | **16 265 €** | **28,0 %** |

**Conclusion chiffrée.** En appliquant **uniquement les usages et les taux que le fisc retient lui‑même** (déductions cuisine déjà reconnues sur Macvin / Calvados / Porto / Absinthe ; abattements pertes + conso personnel de 5 % + 5 %, bière 15 %), on explique **16 265 € soit 28,0 % de l'écart coût HT** (58 060 €), sans aucune hypothèse non sourcée. Ce chiffre est **un plancher** : il n'inclut pas la remise 5 %, ni le Vin Jaune cuisine (61,26 % du Poulet Jurassien, non chiffré en cl par le fisc), ni les offerts. La cohérence interne du fisc est totale : là où il a déduit la cuisine, nous reprenons ses cl ; là où il dit « pas de cuisine » (Picon, Café, Bordeaux), nous ne revendiquons rien.

---

### Sources
- `src/data/reconstitution-administration.json` - `ingredients[].deductions`, `methode.abattements`, `notesMethodologiques`.
- `src/data/volumes-disparus-fisc.json` - `produits[].usage_cuisine_deduit_par_verificateur`, `produits[].note`, `meta.verdict_hypotheses.H2`.
- `analyses-independantes/boissons/data/disparitions.json` - `global.valDisparitionCoutHT`, `parCategorie[].valEcartCoutHT` / `achatHT`.
- `analyses-independantes/boissons/data/achats-exercice.json` - volumes et coûts d'achat HT réels par produit/exercice.
- `analyses-independantes/boissons/data/prix-carte.json` - confirme la présence des plats au Vin Jaune / « Jurassien » à la carte.
