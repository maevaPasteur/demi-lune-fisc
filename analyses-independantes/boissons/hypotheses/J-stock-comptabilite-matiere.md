# Hypothèse J — Le « stock » n'explique pas le résiduel : preuve par la comptabilité matière du fisc

**Question critique.** Notre décomposition attribue ~39 000 € HT (sur 58 060 € HT d'écart « boissons disparues ») à un poste « stock ». Or le fisc dispose de sa propre comptabilité matière. **Vérification : le stock explique-t-il vraiment ce résiduel ?** Réponse : **non**. Le stock boissons est quasi stable sur les 3 exercices ; la comptabilité matière du fisc le démontre lui-même.

---

## 1. La variation de stock boissons du fisc est NÉGLIGEABLE (stock stable)

Source : lettre du fisc, **Proposition_1_Lettre.txt, p.34, lignes 2137-2140** (tableau « XVII – COMPTABILITÉ NON SINCÈRE / COEFFICIENTS »), repris identiquement p.35 (lignes 2168-2171, tableau post-reconstitution). Compte **310200 – Variation stocks Boissons**.

| Exercice clos | Achats Boissons (601200) | Variation stock Boissons (310200) | Poids \|var\|/achats |
|---|---:|---:|---:|
| 31/03/2023 | 48 237,09 € | **− 800,83 €** | 1,66 % |
| 31/03/2024 | 46 384,45 € | **− 1 029,67 €** | 2,22 % |
| 31/03/2025 | 47 098,84 € | **− 273,41 €** | 0,58 % |
| **Total 3 ans** | **141 720,38 €** | **− 2 103,91 €** | **1,48 %** |

(Le chiffre 2024-2025 = −273,41 € recoupe exactement `reconstitution-administration.json` → `comptes.variationStockBoissons_310200`.)

**Conclusion §1 : la variation de stock cumulée est de −2 104 € sur 141 720 € d'achats, soit 1,48 %.** Le stock est **stable** (il diminue même légèrement : déstockage net, donc consommation > achats). Aucune année ne dépasse 2,2 %. Le « stock » ne peut mécaniquement pas absorber un résiduel de ~39 000 €.

---

## 2. Identité comptable : achats + variation = consommation → quasi tout est consommé

Identité PCG : **coût des matières consommées = achats + variation de stock** (variation = stock initial − stock final, telle qu'inscrite avec son signe au 310200).

Vérification sur la propre ligne « Coût d'achats des matières des produits vendus » du fisc (p.34, l.2140) :

- Achats Denrées + Boissons + var. Denrées + var. Boissons =
  - 2022-2023 : 175 710,96 − 800,83 + 526,38 = **175 436,51 €** = ligne fisc (exact).
  - 2024-2025 : 189 227,95 − 430,25 − 273,41 = 188 524,29 € ≈ **188 544,29 €** fisc (écart 20 €, arrondi OCR ; recoupe `coutMatieresRevendues`).

Donc pour les boissons seules :
**Consommation boissons (fisc) = 141 720,38 − 2 103,91 = 139 616,47 € sur 3 ans.**

Autrement dit, **98,5 % des achats boissons sont comptabilisés comme CONSOMMÉS**, pas stockés. Le fisc lui-même acte qu'il n'y a (quasi) pas de stock résiduel à expliquer.

**Conséquence directe pour notre décomposition : le résiduel ne peut PAS être du stock.** Si la marchandise n'est ni en stock (var. ≈ 0) ni vendue à la caisse (notre écart), alors elle a été **consommée sans recette enregistrée en caisse** : sur-versement de doses, pertes techniques, consommation personnel, usage cuisine. C'est de la **consommation**, pas du stockage.

---

## 3. Incohérence interne du fisc : sa matière équilibre, mais il invoque des « volumes disparus »

Le fisc tient **deux discours contradictoires** :

- **(a) Approche comptabilité matière (p.34-35) :** achats + variation stock = coût des matières consommées (188 544 € en 2024-2025). Cette équation **est équilibrée** : toute la matière achetée est traitée comme consommée. Aucune fuite, aucune disparition résiduelle — le stock final colle.
- **(b) Approche reconstitution par doses (`reconstitution-administration.json`) :** il affirme par ailleurs des « volumes disparus » massifs (Macvin 52,4 %, Vodka 61,4 %, bière 27,1 %…), définis comme `(volume disponible − volume vendu) / volume disponible`.

Ces deux approches **ne sont pas cohérentes**. En (a), la matière est intégralement consommée et le stock est stable ; il n'y a **rien qui « disparaît »** au sens d'un manquant inexpliqué. La « disparition » de (b) n'est donc **pas** un trou de stock : c'est l'**écart entre le volume consommé et le volume facturé en caisse au tarif théorique par dose**. C'est un **artefact de la reconstitution** par doses + coefficient (rapport liquide/solide 3,1 ; coefficient de revente porté de 2,31 à 3,051), pas une matière physiquement absente. Le fisc transforme une consommation réelle (versée, perdue, offerte, cuisinée) en « recette dissimulée » par le seul jeu du coefficient — alors que sa propre comptabilité matière, équilibrée, prouve que la matière n'a pas disparu.

---

## 4. Conclusion : ce que devient le « stock » comme explication

- **Le « stock » s'effondre comme explication du résiduel.** Variation cumulée −2 104 € (1,48 % des achats) : marginal, et de surcroît négatif (déstockage). Au mieux quelques centaines d'euros sur une année, pas ~39 000 €.
- **Impact sur notre décomposition : retirer/quasi-annuler la ligne « stock ».** Le résiduel ~39 000 € HT doit être **redistribué vers les postes de consommation réelle** : sur-versement de doses (vin au verre, spiritueux), pertes techniques bière (purge/mousse — cf. hypothèse G), consommation personnel/offerts (cf. hypothèse D), usages cuisine/dessert (Macvin, absinthe, vin jaune — déjà partiellement reconnus par le fisc lui-même). Ces postes expliquent une consommation sans recette caisse **sans aucune dissimulation de CA**.
- **Argument de défense fort :** opposer au fisc **sa propre comptabilité matière équilibrée** (p.34-35), qui prouve que la matière est consommée et le stock stable — donc qu'il n'y a pas de « disparition » physique, et que sa reconstitution par doses/coefficient mesure un écart méthodologique, pas un manquant.

---

### Sources
- `public/documents/.../Proposition_1_Lettre.txt`, p.34 (l.2134-2141) et p.35 (l.2166-2172) — tableaux coefficients, compte 310200 sur les **3 exercices** ; p.36 (l.2188-2193) « Les stocks de liquides » (inventaires obtenus, base de la méthode).
- `src/data/reconstitution-administration.json` → `comptes` (var. stock boissons −273,41 € ; coûtMatièresRevendues 188 544,29 € pour 2024-2025) et `ingredients[].volumesDisparusPct`.
- `analyses-independantes/boissons/data/disparitions.json` → `global` (écart 58 059,52 € HT au coût ; achats périmètre 126 752,49 €).
