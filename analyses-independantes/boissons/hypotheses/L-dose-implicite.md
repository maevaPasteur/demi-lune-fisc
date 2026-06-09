# Hypothèse L — Dose implicite : le sur-versement explique-t-il l'écart ?

**Question.** Le « vendu » de boissons est reconstitué à partir des **doses de la carte**
(verre de vin 15 cl, digestif 4 cl, etc.). Si l'on verse en réalité plus que la carte,
le « vendu » est sous-estimé et l'écart achats−ventes se réduit. **Quelle part de l'écart
un sur-versement RÉALISTE peut-il expliquer ?**

**Méthode.** Pour chaque catégorie :
`dose_implicite = dose_carte × (acheté / vendu)`.
Le ratio `acheté/vendu` est **indépendant de la dose choisie** : c'est lui qui fixe le
sur-versement nécessaire pour fermer **totalement** l'écart.
`sur-versement nécessaire (%) = (acheté/vendu − 1) × 100`.
Données : `disparitions.json` (totaux 3 exercices 2022→2025). Coût/cl = achatHT/achatCl.

**Barème de plausibilité.** +10 à +20 % = courant et défendable ; jusqu'à ~50 % =
sur-versement + autre cause ; **au-delà de +50 % = sur-versement insuffisant** (irréaliste :
un verre de vin « 15 cl » servi à 23 cl, un digestif « 4 cl » servi à 13 cl, ne se défendent pas).

---

## 1. Dose implicite par catégorie

| Catégorie | Dose carte (cl) | Dose implicite (cl) | Sur-versement nécessaire | Verdict |
|---|---:|---:|---:|---|
| Vin | 15,0 | **23,2** | **+55 %** | sur-versement insuffisant |
| Macvin | 6,0 | **14,7** | **+144 %** | sur-versement insuffisant |
| Spiritueux / digestif | 4,0 | **12,6** | **+215 %** | sur-versement insuffisant |
| Crémant / pétillant | 12,0 | **24,3** | **+103 %** | sur-versement insuffisant |
| Bière | 25,0 | **46,8** | **+87 %** | sur-versement insuffisant |
| Soft | 25,0 | **77,9** | **+212 %** | sur-versement insuffisant |
| Jus | 12,0 | **23,6** | **+97 %** | sur-versement insuffisant |
| Eau | 25,0 | **41,2** | **+65 %** | sur-versement insuffisant |
| Sirop | 2,0 | **7,9** | **+294 %** | sur-versement insuffisant |

**Constat sans complaisance : AUCUNE catégorie ne tient.** Même la plus favorable (vin)
exige un verre servi à **23 cl au lieu de 15** (+55 %), au-delà du seuil défendable.
Pour les bouteilles/contenances fermées (bière, soft, eau, crémant) le « sur-versement »
n'a même pas de sens physique : une bière de 25 cl ne peut pas être servie à 47 cl.
Les ratios de soft (+212 %), spiritueux (+215 %) et sirop (+294 %) sont absurdes.

> Note dose carte : valeurs représentatives par catégorie. Le verdict ne dépend PAS du
> choix de la dose : le ratio acheté/vendu (donc le %) est invariant. Seule la dose
> implicite en cl bouge avec la dose retenue.

## 2. Classement

- **Écart explicable par sur-versement seul (≤ +20 %)** : *aucune catégorie*.
- **Sur-versement + autre cause (≤ +50 %)** : *aucune catégorie* (la plus basse, vin, est à +55 %).
- **Sur-versement insuffisant (> +50 %)** : **les 9 catégories.**

## 3. Part de l'écart réellement explicable par un sur-versement DÉFENDABLE

On suppose le sur-versement appliqué au volume effectivement vendu
(dose réelle = carte × (1+p) ⇒ volume consommé en plus = vendu × p), plafonné à l'écart.

| Scénario | Volume expliqué | Coût HT expliqué | % du coût de l'écart | Reste inexpliqué (coût HT) |
|---|---:|---:|---:|---:|
| +10 % (prudent) | 898 L | **6 854 €** | 11,8 % | 51 361 € |
| +15 % (médian) | 1 346 L | **10 281 €** | 17,7 % | 47 934 € |
| +20 % (généreux) | 1 795 L | **13 707 €** | 23,5 % | 44 508 € |

**Détail par catégorie au scénario défendable +15 % :**

| Catégorie | Écart total | Coût HT écart | Expliqué +15 % (L) | Expliqué +15 % (€) | % du gap |
|---|---:|---:|---:|---:|---:|
| Vin | 2 008 L | 22 617 € | 548 | 6 173 € | 27 % |
| Macvin | 476 L | 8 638 € | 50 | 899 € | 10 % |
| Spiritueux / digestif | 462 L | 7 353 € | 32 | 513 € | 7 % |
| Crémant / pétillant | 647 L | 5 800 € | 94 | 846 € | 15 % |
| Bière | 1 274 L | 5 669 € | 219 | 974 € | 17 % |
| Soft | 2 530 L | 4 693 € | 179 | 333 € | 7 % |
| Jus | 487 L | 1 651 € | 75 | 256 € | 16 % |
| Eau | 613 L | 1 082 € | 142 | 251 € | 23 % |
| Sirop | 126 L | 712 € | 6 | 36 € | 5 % |
| **TOTAL** | **8 622 L** | **58 215 €** | **1 346** | **10 281 €** | **17,7 %** |

**Fourchette retenue : 7 000 € à 14 000 € de coût HT** (≈ 12 à 24 % de l'écart valorisé au
coût) selon que l'on retient +10 % ou +20 %. Au point médian +15 % : **≈ 10 300 € HT, soit
moins d'un cinquième de l'écart de 58 215 € HT.**

## 4. Critique : où le sur-versement NE suffit PAS, et qu'est-ce que ça implique

Le sur-versement ne suffit **nulle part**. Après application généreuse de +15 %, le résidu
inexpliqué reste massif et concentré :

- **Vin — 16 444 € (73 % du gap).** Plus gros poste en valeur. Un sur-versement même large
  ne couvre qu'un quart. Le reste pointe vers : **pichets/bouteilles servis non saisis**,
  vin de cuisine (sauces au vin jaune, marinades, déglaçage — usage réel en cuisine jurassienne),
  offerts/dégustations, et **sous-attribution** des boutons génériques (« Verre/Pichet de base »).
- **Macvin (90 %) et spiritueux/digestif (93 %).** Résidus quasi intégraux (7 740 € et 6 840 €).
  Ce sont des produits **chers au cl** : l'enjeu fiscal est ici. Le sur-versement est marginal ;
  l'écart traduit surtout **offerts maison / tournées non enregistrées**, usage cuisine
  (macvin en cuisine, eaux-de-vie de flambage) et **constitution de stock** (cave de spiritueux,
  pas d'inventaire — caveat explicite).
- **Bière (83 %) et soft/eau (93 % / 77 %).** Contenances **fermées** : le sur-versement est
  physiquement impossible. L'écart vient donc **mécaniquement d'ailleurs** — offerts, pertes/casse,
  consommation personnel, eau de carafe non vendue, et surtout l'absence d'inventaire (stock
  tampon de canettes/bouteilles/fûts). Pour le soft, le caveat « boutons génériques » indique
  aussi une **forte sous-attribution caisse**.
- **Sirop (95 %).** Petit en valeur (712 €) mais ratio absurde (+294 %) : dose 2 cl irréaliste,
  usage cuisine (desserts, cocktails maison) et attribution faible (« sirop à l'eau » générique).

**Implication centrale pour la défense.** L'hypothèse « doses réelles > carte » est **réelle mais
mineure** : elle absorbe au mieux ~18 % (10 300 €), jusqu'à ~24 % (13 700 €) en étant généreux,
de l'écart au coût. **Plus de 75 % de l'écart (≈ 45 000 € HT) doit s'expliquer par d'autres
causes légitimes NON déduites dans le modèle** (caveats du fichier) : absence d'inventaire =
constitution de stock (un écart positif n'est pas une disparition), **usages cuisine**, offerts/
consommation personnel/pertes-casse, et **sous-attribution caisse** des boutons génériques
(couverture caisse ~88 %). Le sur-versement est un argument d'appoint, pas le pilier : le pilier
défensif est la combinaison stock + cuisine + offerts + imperfection d'attribution.

---

*Source : `analyses-independantes/boissons/data/disparitions.json`. Calculs : `/tmp/pwenv/bin/python`.
Totaux cumulés des 3 exercices 2022-2023 → 2024-2025. Écart total 8 622 L / 58 215 € HT au coût.*
