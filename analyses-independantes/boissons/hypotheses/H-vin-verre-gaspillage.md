# H - Vin au verre : bouteille ouverte (oxydation) & sur-versement

**Objet.** Expliquer une part de l'écart VIN (catégorie la plus lourde) par deux mécanismes
opérationnels propres au service du vin au verre :
1. **« Bouteille ouverte »** - pour servir un vin au verre peu demandé, on ouvre une 75 cl ;
   si peu de verres partent, le reste s'oxyde et est perdu (ou repassé en personnel/cuisine).
2. **Sur-versement** - la dose réellement servie au verre dépasse la dose carte (15 cl tranquille).

> **Convention de lecture.** [EXACT] = lu dans les données. [ESTIMATION] = hypothèse de
> gaspillage / sur-versement, donnée en fourchette (bas / central / haut). Ces deux effets ne
> sont **pas** un constat comptable mais une explication métier chiffrée et bornée.

---

## 0. Rappel de l'écart VIN - [EXACT]

Source : `data/disparitions.json` → `parCategorie.vin.total` (3 exercices cumulés).

| Mesure | Valeur |
|---|---|
| Acheté | 566 104 cl = **5 661 L** |
| Vendu (au tarif/dose carte) | 365 334 cl = **3 653 L** |
| Écart | 200 770 cl = **2 008 L** = **35,5 %** |
| Valorisé coût HT | **22 617 € HT** |
| Coût d'achat moyen | **11,27 €/L** |

Volumes de vin tranquille servis « au verre » (hors crémant 12 cl, catégorie séparée),
boutons caisse × dose carte, cumul 3 ex - [EXACT] (`prix-carte-par-bouton.json` × `ventes-caisse.json`) :

- **Verre 15 cl : 706 L** · **Pichet 50/75 cl : 1 473 L** · **total verre+pichet : 2 179 L**
  (soit 12,5 % de l'achat vin au verre seul, 38,5 % verre+pichet).

---

## 1. Hypothèse « BOUTEILLE OUVERTE » (oxydation / repasse) - [ESTIMATION]

### 1.1 Le mécanisme & les vins concernés - [EXACT]
Une 75 cl = **5 verres** de 15 cl. Un vin tranquille ouvert reste « marchand » ~2 à 4 jours.
Si un bouton « verre » tourne lentement, la dernière bouteille ne se vide pas avant oxydation :
le résidu est perdu ou repassé (personnel/cuisine) - non enregistré comme « vendu ».

Rotation par bouton « verre » (verres/semaine, moyenne 3 ex, base 50 sem./an) - [EXACT] :

| Bouton verre | dose | verres/sem | jours pour vider 1 btl |
|---|---|---|---|
| Savagnin verre | 15 | 10,3 | 3,4 (rapide) |
| Saint Véran Verre | 15 | 5,5 | 6,4 |
| H.C. de Beaune verre | 15 | 2,4 | 14 |
| Verre de vin (génér.) | 15 | 2,4 | 15 |
| Verre Aligoté | 15 | 2,3 | 15 |
| Mâcon verre | 15 | 2,1 | 16 |
| Verre Rosé | 15 | 1,9 | 18 |
| Beaujolais Moulin verre | 15 | 1,9 | 18 |
| Verre Chusclan | 15 | 1,2 | 28 |
| Chablis le verre | 15 | 1,0 | 36 |
| Verre H.C. de Beaune (2e) | 15 | 0,3 | 128 |

→ **9 des 11 références « verre » tournent à moins de 5 verres/sem.** : une bouteille ouverte met
2 à 18+ semaines à se vider, donc plusieurs « ouvertures » par an avec résidu oxydé à chaque cycle.

### 1.2 Hypothèse de perte explicite
Perte exprimée en % du volume servi, **graduée selon la rotation** (plus c'est lent, plus la part
de la bouteille perdue est forte) :

| Rotation | Taux de gaspillage appliqué (bas / central / haut) |
|---|---|
| ≥ 7 verres/sem (vide à temps) | 0 % / 3 % / 8 % |
| 2-7 verres/sem | 5 % / 12 % / 20 % |
| 0,5-2 verres/sem | 12 % / 25 % / 40 % |
| < 0,5 verre/sem | 20 % / 40 % / 70 % |

### 1.3 Résultat - [ESTIMATION]

| Scénario | Volume perdu (3 ex) | Valorisé coût HT | % écart vin |
|---|---|---|---|
| Bas | 38 L | **425 €** | 1,9 % |
| **Central** | **102 L** | **1 153 €** | **5,1 %** |
| Haut | 210 L | **2 361 €** | 10,4 % |

> Note de borne : un modèle purement « fenêtre de fraîcheur » (toute bouteille ouverte non vidée
> en F jours perd son résidu) donne, pour F = 3-4 j, 1 700-2 400 L - supérieur à l'écart vin total
> et donc **physiquement implausible** (il supposerait qu'on ouvre une bouteille neuve par verre).
> On le retient seulement comme rappel que, sur les boutons très lents, l'effet par-bouteille peut
> être massif ; la fourchette retenue ci-dessus reste prudente.

---

## 2. Hypothèse SUR-VERSEMENT (sensibilité) - [ESTIMATION]

Si la dose réelle dépasse la dose carte (15 cl tranquille), le volume **réellement consommé** est
supérieur au volume « vendu » comptabilisé : l'écart diminue d'autant. On applique la surverse au
**volume tranquille servi au verre + pichet = 2 179 L** (base carte, 3 ex) - [EXACT].

| Sur-versement | Volume suppl. expliqué | Nouvel écart vin | Réduction de l'écart | € HT expliqués |
|---|---|---|---|---|
| 0 % (réf.) | 0 L | 2 008 L (35,5 %) | - | 0 € |
| **+10 %** | **218 L** | **1 790 L** | **−10,9 %** | **2 455 €** |
| +15 % | 327 L | 1 681 L | −16,3 % | 3 683 € |
| +20 % | 436 L | 1 572 L | −21,7 % | 4 910 € |

→ Une surverse plausible (verre « généreux » +10 à +20 %) explique **218 à 436 L / 2 455 à 4 910 € HT**,
soit **11 à 22 %** de l'écart vin.

---

## 3. Conclusion - part de l'écart potentiellement expliquée [ESTIMATION]

Cumul des deux effets (bornes cohérentes bas/central/haut) :

| Scénario | H1 bouteille ouverte | H2 sur-versement | **Total** | **% écart VIN (22 617 €)** | % disparition totale (58 060 €) |
|---|---|---|---|---|---|
| Bas | 425 € | 2 455 € (+10 %) | **2 880 €** | **13 %** | 5 % |
| **Central** | 1 153 € | 3 683 € (+15 %) | **4 836 €** | **21 %** | 8 % |
| Haut | 2 361 € | 4 910 € (+20 %) | **7 271 €** | **32 %** | 13 % |

**Lecture défense.** En scénario central, ces deux mécanismes purement opérationnels - sans
soustraction occulte - expliquent **~21 % de l'écart vin** (et jusqu'à **~32 %** en hypothèse haute).
Le **sur-versement** est le levier dominant (l'assiette verre+pichet est large) ; la **bouteille
ouverte** est secondaire mais réelle et bien documentée par la faible rotation de 9 boutons « verre ».

⚠️ **EXACT vs ESTIMATION** : seuls l'écart vin (§0), les rotations et les volumes servis sont des
données. Les taux de gaspillage (§1.2) et la surverse (§2) sont des **hypothèses bornées**, à
présenter comme telles ; elles n'établissent pas un fait mais réduisent la part « inexpliquée ».

---
*Sources : `data/disparitions.json`, `data/ventes-caisse.json`, `data/prix-carte.json`,
`data/prix-carte-par-bouton.json`. Calculs : `/tmp/pwenv/bin/python`.*
