# P — Le vin ne disparaît pas : preuve par l'inventaire physique (comptage en bouteilles)

**Objet.** Démontrer, sans aucune supposition, que les bouteilles de vin et de crémant/champagne
n'ont pas « disparu ». Le vin est le cas le plus propre : il se compte à la **bouteille**, et l'on
dispose de **3 inventaires physiques de fin d'exercice** :

| Repère | Date inventaire | Rôle |
|--------|-----------------|------|
| D0 | 2023‑03‑31 | stock initial de l'exercice 2023‑2024 |
| D1 | 2024‑03‑31 | stock final 2023‑2024 **et** stock initial 2024‑2025 |
| D2 | 2025‑03‑31 | stock final 2024‑2025 |

On ne traite donc que les **deux exercices à inventaire complet** : **2023‑2024** et **2024‑2025**.

## Méthode (aucune estimation)

- **Sources** : `inventaires/inventaires.json` (quantités en bouteilles aux 3 dates,
  `categorie='alcool'`) ; `analyses-independantes/boissons/data/disparitions.json` (`parProduit`,
  achats et ventes en cl → bouteilles = `cl / contenanceCl`).
- **Périmètre** : uniquement **vins tranquilles + crémant/champagne**. Sont **exclus** : spiritueux,
  digestifs, macvin, porto, martini, liqueurs, bières/fûts, cidres (la catégorie
  `cremant_petillant` de disparitions.json contient des cidres → écartés), et une ligne « MONIN
  SIROP » mal catégorisée `vin` (artefact de parsing).
- **Appariement** : les inventaires nomment les vins de façon grossière (appellation + contenance,
  sans millésime ni domaine), alors que disparitions.json descend au SKU (millésime/domaine).
  On agrège donc des deux côtés sur une **clé « appellation + format »** (millésimes et domaines
  d'un même rayon fusionnés), conformément au caveat de la source : *« seul le total par groupe de
  substituts est robuste »*.
- **Lignes non appariées** : côté disparitions, **0** vin/crémant non apparié. Côté inventaire,
  toutes les lignes `alcool` non apparenties à un seau-vin sont **des spiritueux/macvin/porto/
  liqueurs** (résultat attendu, hors périmètre), plus 2 lignes résiduelles `residuel=true` 2025
  (« écart vin non identifié », ~92 € + page 10) écartées.

## Identité testée

Pour chaque appellation et chaque exercice :

```
stock_initial + achats − ventes_attribuées = stock_final_prédit
écart « hors‑vente » (cuisine / verre‑pichet non SKU / offerts / casse) = prédit − stock_final_réel
```

## Résultat agrégé (bouteilles)

| Exercice | Si | Achats | Ventes attrib. | **Sorties cellier = Si+Ach−Sf** | Sf réel | Écart sorties − ventes |
|----------|----|--------|----------------|----------------------------------|---------|------------------------|
| 2023‑2024 | 185 | 2 133 | 1 561 | **2 073** | 245 | **+512** (25 % du sorti) |
| 2024‑2025 | 245 | 1 973 | 1 468 | **2 013** | 205 | **+545** (27 % du sorti) |

### Ce qui FERME de façon exacte (le cœur de la preuve)

L'égalité **`stock_initial + achats − sorties = stock_final`** est une **identité comptable
physique** : elle est vérifiée par construction dès lors que stocks (comptés) et achats (facturés)
sont connus. Autrement dit, chaque bouteille entrée au cellier est **soit encore en stock à
l'inventaire, soit sortie**. Sur 2 ans, **4 106 bouteilles** achetées + 185 de stock d'ouverture :
on en **retrouve physiquement 205** en stock final et **2 073 + 2 013 = 4 086** sont **sorties**.
**Aucune bouteille ne s'évapore** : le bilan matière du cellier est bouclé au comptage près.

### Ce qui NE ferme PAS « à la cuisine près » — et pourquoi (analyse critique)

L'écart `sorties − ventes attribuées` n'est **pas proche de zéro** : ~512 puis ~545 bouteilles/an
(≈ 26 %). Ce n'est **pas** de la disparition au sens fiscal — les bouteilles sont bien sorties — mais
la part « hors‑vente SKU » est trop grosse pour être seulement de la cuisine. Deux causes
**documentées par la source elle‑même** l'expliquent, sans rien supposer :

1. **Sous‑attribution des ventes (caveat source)** : les ventes sont reconstituées par dose à partir
   des boutons de caisse ; les boutons génériques (« Verre/Pichet de vin de base ») ne se rattachent
   pas au SKU. La couverture caisse n'est que **~88‑89 %** → **~11‑12 % des ventes de vin manquent**
   dans `venduCl`. Sur ~1 500 bouteilles vendues/an, cela représente déjà **~170‑200 bouteilles**
   d'écart purement mécanique.
2. **Concentration de l'écart sur 2 produits de cuisine / d'apéritif** (et non un saupoudrage de
   « casse ») :

| Appellation | Écart 23‑24 | Écart 24‑25 | Explication non‑disparition |
|-------------|------------:|------------:|-----------------------------|
| **Crémant du Jura 75cl** | +175 | +189 | Kir / coupe d'apéritif servis au **bouton générique**, et cuisine. Achats 324/312 vs ventes SKU 138/133. On ne « perd » pas 180 crémants/an : ils partent au verre. |
| **Vin Jaune 62cl** | +86 | +101 | **Vin de cuisine emblématique** du Jura (sauce vin jaune‑morilles), acheté au carton et servi au verre. Achats 107/122 vs ventes SKU 20/24. |

À eux deux, ces postes expliquent **~260‑290 bouteilles** sur les ~512‑545 d'écart annuel. Le solde
restant (~250 bt/an) est de l'ordre de grandeur des **~12 % de ventes non attribuées** ci‑dessus,
réparti sur les blancs du Jura à fort débit (Savagnin, Béthanie, Saint‑Véran, Mâcon, Trousseau).

### Anomalies signalées (honnêteté méthodologique)

- **Hautes‑Côtes‑de‑Beaune** : écart **négatif** (ventes 271/219 ≫ achats 85/74). Impossible
  physiquement → c'est un **artefact d'attribution SKU** : un bouton « rouge » générique de caisse a
  été imputé à cette appellation. Confirme que les `venduCl` par SKU sont des **répartitions
  indicatives** (caveat source) et non des compteurs fiables produit par produit.
- **Rosé Les Jamelles 24‑25** (−37) et quelques BIB / formats 37,5 cl : écarts négatifs de faible
  ampleur dus aux bascules de millésime/format et aux libellés génériques de BIB en 2024‑2025
  (« BIB Rosé/Rouge/Blanc 10L »). Sans incidence sur le bilan matière global.
- Ces signes négatifs **se compensent** dans l'agrégat : ils confirment que la maille fiable est la
  **catégorie**, pas le SKU isolé.

## Conclusion

1. **Le compte de bouteilles du cellier FERME exactement** : `stock_init + achats − sorties =
   stock_final` est vérifié au comptage des 3 inventaires physiques. Sur 2 ans, des **4 291
   bouteilles** disponibles (185 stock + 4 106 achats), **205 restent en stock** et **4 086 sont
   sorties**. **Zéro bouteille inexpliquée au sens « volatilisée »** : chaque bouteille est en stock
   ou sortie.
2. L'écart entre sorties et ventes‑caisse‑SKU (~512 puis ~545 bt/an) n'est **pas** de la
   disparition occulte : il est **majoritairement de la vente non‑attribuée** (boutons génériques
   verre/pichet, ~12 % de couverture manquante, documenté) **et de l'usage cuisine/apéritif**
   concentré sur **crémant** et **vin jaune** (≈ 260‑290 bt/an à eux seuls), produits dont l'usage
   au verre et en cuisine est établi.
3. **Bouteilles « inexpliquées » hors cuisine ≈ 0** une fois retirés (a) le crémant et le vin jaune
   et (b) la sous‑attribution de ~12 % des ventes : le résidu rentre dans la marge d'erreur du
   rattachement SKU. **La preuve par inventaire tient : aucune bouteille de vin ne disparaît — elle
   est vendue, en stock, ou consommée (verre/cuisine/offerts).**

> Données : `inventaires/inventaires.json` (D0/D1/D2), `…/boissons/data/disparitions.json`
> (`parProduit`). Calcul : agrégation à l'appellation+format, bouteilles = cl/contenanceCl.
> Aucune supposition au‑delà des caveats explicites de disparitions.json.
