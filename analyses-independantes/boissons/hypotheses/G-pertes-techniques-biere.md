# Hypothèse G - Pertes techniques sur la bière pression (Affligem)

**Objet** : expliquer une part de l'écart bière (achat > vente) par les pertes
techniques **structurellement non vendables** de la bière à la pression. Une fraction
de chaque fût ne peut jamais être servie (fond de fût, purges de nettoyage, mousse au
tirage). Ces volumes sont achetés mais ne génèrent aucune vente.

> **Nature des chiffres**
> - **EXACT** = nos volumes issus des données comptables (achats, écart bière).
> - **ESTIMATION** = application de **taux standards documentés de la profession CHR**,
>   exprimés en **fourchette basse / haute**. Aucune affirmation exacte sur les pertes :
>   uniquement des **bornes**, à **confirmer par l'exploitant** (fréquence réelle de
>   nettoyage, nombre de lignes de tirage).

---

## 1. Données EXACTES (base de calcul)

Source : `data/achats-exercice.json` (code **212122 - FUT AFFLIGEM BLADE 8 L 6,7°**,
`estFut=true`) et `data/disparitions.json` (catégorie `biere`).

| Donnée EXACTE | Valeur |
|---|---|
| Volume Affligem pression acheté (3 exercices) | **2 096 L** |
| → en fûts physiques de 8 L (2 096 ÷ 8) | **262 fûts** |
| Coût d'achat réel de la pression | 8 302,40 € HT → **3,96 €/L** |
| Écart bière total (toutes bières) | **1 274,4 L** - **46,6 %** - **5 668,96 € HT** |

Détail pression par exercice (EXACT) :

| Exercice | Litres | Fûts 8 L | € HT |
|---|---|---|---|
| 2022-2023 | 792 L | 99 | 2 866,32 |
| 2023-2024 | 632 L | 79 | 2 579,92 |
| 2024-2025 | 672 L | 84 | 2 856,16 |
| **Total** | **2 096 L** | **262** | **8 302,40** |

> Note méthodologique : dans le fichier d'achats, la ligne Affligem est comptée **en
> litres** (volCl = qte × 100). Le volume pression réel sur 3 ans est donc **2 096 L**,
> soit **262 fûts** de 8 L - et non « ~270 fûts / 2 160 L » comme estimé initialement.
> Le restaurant est ouvert ~10 mois/an (fermeture janvier-février).

---

## 2. Postes de pertes techniques (ESTIMATION par taux standards)

### Poste 1 - Fond de fût (mousse résiduelle + lie + dernières pintes troubles)
La fin de chaque fût n'est pas servable : pression qui tombe, mousse, dépôt, pintes
troubles tirées puis jetées.
- **Taux standard retenu : 0,3 à 0,5 L par fût** (perte de fin de fût communément
  admise en CHR ; ordre de grandeur cohérent avec les pertes « fond de fût + tirage »
  estimées par les brasseurs/installateurs de tirage pression, généralement chiffrées
  à **2-5 % du volume du fût**, soit 0,16-0,40 L pour un 8 L, ici borné prudemment
  jusqu'à 0,5 L).
- Appliqué aux **262 fûts EXACTS** :
  - Borne basse : 262 × 0,3 = **78,6 L**
  - Borne haute : 262 × 0,5 = **131,0 L**

### Poste 2 - Nettoyage des lignes de tirage
En CHR, les lignes (tuyaux) sont nettoyées ~**1 fois par semaine** (recommandation
hygiène brasseurs/installateurs : nettoyage hebdomadaire). Chaque nettoyage purge la
bière présente dans la ligne + les premières pintes après remontée.
- **Taux standard retenu : 0,5 à 1 L par ligne et par nettoyage.**
- Hypothèse **1 ligne pression**, **~40 semaines/an** (cohérent avec ~10 mois
  d'ouverture), **× 3 ans = 120 nettoyages**.
  - Borne basse : 120 × 0,5 = **60,0 L**
  - Borne haute : 120 × 1,0 = **120,0 L**
- ⚠️ **À confirmer par l'exploitant** : fréquence réelle et nombre de lignes
  (2 lignes ou nettoyage plus fréquent ⇒ poste à doubler).

### Poste 3 - Mousse / coulage au tirage (col, réglage, débordement)
Pertes courantes au service : excès de mousse, col, premiers cl qui coulent.
- **Taux standard retenu : 3 à 5 % du volume tiré.**
- Appliqué au volume pression EXACT (2 096 L) :
  - Borne basse : 2 096 × 3 % = **62,9 L**
  - Borne haute : 2 096 × 5 % = **104,8 L**

---

## 3. Fourchette totale

| Poste | Bas (L) | Haut (L) |
|---|---|---|
| 1. Fond de fût (0,3-0,5 L × 262 fûts) | 78,6 | 131,0 |
| 2. Nettoyage lignes (0,5-1 L × 120) | 60,0 | 120,0 |
| 3. Mousse / coulage (3-5 % × 2 096 L) | 62,9 | 104,8 |
| **TOTAL pertes techniques** | **≈ 201 L** | **≈ 356 L** |

**Valorisation :**
- Au coût d'achat conventionnel **3,84 €/L** : **≈ 774 € à 1 366 € HT** sur 3 ans.
- Au coût d'achat réel de la pression **3,96 €/L** : **≈ 798 € à 1 409 € HT**.

**Poids de l'explication :**
- En **% de l'écart bière** (1 274,4 L) : **≈ 16 % à 28 %**.
- En **% de l'écart total** (58 060 € HT), valorisé à 3,84 €/L :
  **≈ 1,3 % à 2,4 %**.

---

## 4. Limites et points à confirmer (exploitant)

- Ce sont des **ESTIMATIONS** fondées sur des **taux standards de la profession CHR**
  (fond de fût 0,3-0,5 L/fût ≈ 2-5 % du fût ; nettoyage hebdomadaire 0,5-1 L/ligne ;
  mousse/coulage 3-5 % du volume tiré). **Sources de taux à documenter formellement**
  (préconisations brasseur Affligem/Heineken, installateur de tirage pression, guides
  hygiène CHR) avant production au contrôle.
- **Variables clés à faire confirmer par l'exploitant** : nombre réel de lignes de
  tirage, fréquence réelle de nettoyage, nombre de semaines d'exploitation effectives.
  Avec 2 lignes ou un nettoyage bi-hebdomadaire, le poste 2 (et donc le total) augmente
  sensiblement.
- Hypothèse ne portant **que sur la pression Affligem** ; les bières bouteille (La
  Rouget, etc.) ne sont pas concernées par ces pertes techniques.
