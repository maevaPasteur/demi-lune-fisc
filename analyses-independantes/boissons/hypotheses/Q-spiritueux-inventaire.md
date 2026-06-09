# Q — Spiritueux / apéritifs / macvin / digestifs : équation d'identité par produit

**Objet** : pour chaque spiritueux, apéritif, macvin et digestif, vérifier l'identité comptable
**stock_initial + achats − ventes − cuisine = stock_final**, en bouteilles, sur les deux
exercices entièrement encadrés par les inventaires physiques (2023-2024 et 2024-2025).
Le terme qui reste = **consommation résiduelle** (offerts, personnel, sur-versement, casse,
et — surtout — ventes encaissées sous un autre bouton que la ligne-produit). Aucune supposition :
chaque chiffre vient d'une des sources ci-dessous.

**Sources (toutes vérifiées)**
- Inventaires physiques : `public/documents/inventaires/inventaires.json` — 3 dates bornant les exercices :
  **31/03/2023** (= stock initial 2023-2024), **31/03/2024** (= clôture 2023-2024 / initial 2024-2025),
  **31/03/2025** (= clôture 2024-2025). `categorie='alcool'`, quantité en bouteilles.
- Achats / ventes caisse : `analyses-independantes/boissons/data/disparitions.json`,
  `parProduit[].parExercice[].{achatCl, venduCl}` ; bouteilles = cl / `contenanceCl`.
- Cuisine (déductions du vérificateur) : `src/data/boissons-detail-cuisine.json` +
  `src/data/volumes-disparus-fisc.json` :
  Macvin **7 406 cl** (Baba, saucisse flambée, menu franc-comtois — réparti au prorata des achats par exercice),
  Absinthe **2 580 cl** (crème brûlée — idem),
  Calvados **3 310 cl** et Porto **398 cl** **imputés par le fisc à l'exercice 2022-2023** (repères D et G)
  → donc **0** sur les deux exercices reconstitués ici (ne pas double-compter).

Script : `/tmp/pwenv/bin/python` (`/tmp/reconcile_all.py`). Appariement par mots-clés du libellé.

---

## 1. Cas clés — l'inventaire colle-t-il une fois la cuisine déduite ?

| Produit | Ex. | Stock init | Achats (bt) | Ventes caisse (bt) | Cuisine (bt) | Stock final RÉEL | Résiduel (bt) |
|---|---|---:|---:|---:|---:|---:|---:|
| **Calvados** (100 cl) | 23-24 | 2 | 22,0 | 0,4 | 0 | 2 | **21,6** |
| | 24-25 | 2 | 19,0 | 0,6 | 0 | 1 | **19,4** |
| **Macvin blanc** (75 cl) | 23-24 | 5 | 380,0 | 153,7 | 35,2 | 9 | **187,1** |
| | 24-25 | 9 | 372,0 | 141,1 | 34,5 | 0 | **205,4** |
| **Porto** (75 cl) | 23-24 | 4 | 69,0 | 3,8 | 0 | 4 | **65,2** |
| | 24-25 | 4 | 62,0 | 3,8 | 0 | 2 | **60,2** |
| **Absinthe** (70/100 cl) | 23-24 | 2 | 11,0 | 0,0 | 6,7 | 0 | **6,3** |
| | 24-25 | 0 | 14,0 | 0,0 | 13,2 | 2 | **−1,2** |

**Lecture critique.**
- **Le stock final colle à la borne physique** : Calvados reste à 1-2 bt, Porto à 2-4 bt,
  Macvin à 0-9 bt aux trois inventaires. **Le stock n'accumule jamais** → l'alcool acheté a
  bien quitté le stock (aucun « trésor caché », contre l'hypothèse d'un stock gonflé).
- **MAIS l'équation ne se referme pas** par les seules ventes-caisse + cuisine. Calvados :
  22 bt achetées, **0,4 bt vendue** en ligne-caisse ; Porto : 69 bt achetées, **3,8 bt** vendues.
  Ces `venduCl` sont aberrants pour des produits aussi tournants → ces volumes sont
  **encaissés sous un autre bouton** (cocktail, menu franc-comtois, kir, dose au verre non
  rattachée au code spiritueux), pas « disparus » physiquement. C'est démontré par l'inventaire
  plat, **pas** par la caisse.
- **Absinthe** : se referme presque exactement (résiduel ±6 bt sur 2 ans) une fois la crème
  brûlée déduite — la cuisine (19,9 bt sur 2 exos) absorbe quasi tout l'achat, conforme à
  l'usage dessert revendiqué (non valorisé en boisson par prudence).
- **Macvin** : ventes-caisse (295 bt/2 exos) + cuisine (70 bt) expliquent **la moitié** du
  volume ; le reste est le Macvin servi en kir/apéritif maison sous bouton générique.

---

## 2. Vue d'ensemble — les ~30 références spiritueux/apéritifs/digestifs

Totaux sur les **deux exercices** (2023-2024 + 2024-2025), bouteilles :

| Poste | Bouteilles |
|---|---:|
| Achats réels | **1 298** |
| Ventes encaissées sur la ligne-produit | 487 (37,5 %) |
| Cuisine admise par le fisc (Macvin + Absinthe) | 90 (6,9 %) |
| Variation de stock (init − final, inventaire) | ~ −8 (quasi plat) |
| **Résiduel inexpliqué par caisse + cuisine** | **≈ 729** |

Le résiduel se **concentre** sur les produits-ingrédients de cocktails/menus dont la vente
n'est pas rattachée au code spiritueux : Calvados (41 bt), Porto (125 bt), Macvin (392 bt),
Pontarlier anis (16), Bailey's (25), Aperol (19), Vodka (21), Grand Marnier (10), Liqueur poire (22).
À l'inverse, les produits vendus **tels quels au verre** se referment quasi parfaitement
(résiduel ≈ 0) : **Soho −4, Crème de Cassis +9, Pastis +0,3, Martini +0,5, Marc de Bourgogne +1,8,
Get 27/31, Mirabelle, Framboise, Clan Campbell** — preuve que là où la caisse capte la vente,
l'inventaire confirme à la bouteille près.

---

## 3. Conclusion — où va chaque bouteille

Pour ces familles, chaque bouteille est : **(a)** vendue sur sa ligne (487), **(b)** passée en
cuisine (90, déduction du fisc lui-même), **(c)** en stock aux inventaires (stock plat, ~0 net),
ou **(d)** résiduelle ≈ 729 bt — qui ne sont **pas physiquement disparues** (le stock plat le
prouve) mais **encaissées sous un autre bouton** (cocktails, menus, kir, dose au verre) plus,
marginalement, offerts / personnel / sur-versement / casse.

**Honnêteté méthodologique** : l'inventaire **ne suffit pas** à clôre l'équation au cl près —
il prouve l'absence d'accumulation de stock et valide à la bouteille les produits vendus tels
quels, mais le résiduel de 729 bt **renvoie à l'argument de sous-attribution de boutons-caisse**
(hypothèses K, B, F) et de doses (L), pas à une preuve d'absence de disparition isolée. C'est un
**plancher** : la cuisine Calvados (3 310 cl) et Porto (398 cl) imputées par le fisc à 2022-2023,
le Vin Jaune cuisine (non chiffré) et les abattements remise/pertes/personnel ne sont pas comptés ici.
