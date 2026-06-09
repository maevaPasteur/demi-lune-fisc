# Pourquoi les boissons « disparaissent » - explications vérifiées

> Question : le restaurant n'a jamais encaissé en espèces des centaines de milliers
> d'euros de boissons. D'où vient l'écart apparent achats − ventes ? Chaque piste
> ci-dessous est **vérifiée par calcul** sur les données exactes (pas de supposition).
> Détail dans `hypotheses/` ; chiffres reproductibles via `scripts/boissons/`.

## 1. Se placer sur le bon terrain : le PRIX DE VENTE

⚠️ **Ne jamais opposer le coût (58 060 €) au CA supposé du fisc** : ce sont deux grandeurs
différentes (et au taux de marge d'un bar, 58 060 € de coût = ~218 000 € de ventes - donc
ce « petit » chiffre se retourne contre nous). Le fisc raisonne en **chiffre d'affaires**,
donc on le réfute **au prix de vente**.

| L'écart de boisson (8 622 L sur 3 ans), chiffré… | Montant | Usage |
|---|--:|---|
| … **au prix de vente** (le terrain du fisc) | **199 490 - 218 167 € TTC** | C'est CE chiffre qu'on explique |
| … au coût d'achat (pour mémoire) | 58 060 € HT | Ce que la marchandise a coûté |

**Comparaison à armes égales (prix de vente) :** le fisc retient **139 728 €** de discordance
pour 2024-2025 ; le manquant réel de boissons ne vaut, au prix de vente, qu'environ
**66 500 - 72 700 €/an**. Le fisc retient ~**2× plus** en l'**extrapolant × 3,1** sur une
cuisine jamais mesurée - et ce manquant lui-même n'est pas du CA caché (§ 2).

## 2. Où va, physiquement, ce volume manquant ? (parts vérifiées)

> Les parts ci-dessous valent quel que soit le chiffrage (coût ou prix de vente) ; les
> montants € sont donnés au coût d'achat pour mémoire.

| # | Explication | Montant (coût HT) | Part | Comment c'est vérifié |
|---|---|--:|--:|---|
| D1 | **Cuisine** (déduite par le fisc) | **2 982 €** | **5,1 %** | Déductions cuisine que le fisc chiffre **lui-même**, produit par produit : Macvin 7 406 cl (baba, saucisse flambée, menu FC), Calvados 3 310 cl (sauces), Porto 398 cl, Absinthe (crème brûlée), Vin Jaune (poulet jurassien, non chiffré par prudence). → `D-cuisine-personnel.md` |
| D2 | **Pertes, casse & conso personnel** | **13 283 €** | **22,9 %** | Abattements **standard aux taux du fisc** (pertes 5 % + personnel 5 % = 10 % ; bière 15 %), appliqués à nos achats réels. *Plancher* (remise 5 % et offerts non comptés). |
| E | **Facturé mais non livré** | **~2 500 €** | **~4,3 %** | 231 lignes de facture à 0 € = marchandise manquante/refusée ; **carnet manuscrit corrobore à 100 %** (125/125 dates). *Plancher* (136 lignes sans quantité). → `E-commande-vs-livraison.md` |
| | **Sous-total VÉRIFIÉ (chiffres du fisc)** | **≈ 18 765 €** | **≈ 32 %** | |
| G | **Pertes techniques bière** (fond de fût, nettoyage des lignes, mousse) | 774 - 1 366 € | ~2 % | *Estimation* aux taux standards CHR. 16-28 % de l'écart bière. → `G-pertes-techniques-biere.md` |
| H | **Vin au verre : sur-versement + bouteilles ouvertes** | 2 455 - 4 910 € | 4-8 % | *Estimation bornée* : dose carte = minimum ; 9 vins/11 < 5 verres/sem. → `H-vin-verre-gaspillage.md` |
| M | **Abattements jurisprudence** (offerts + pertes + casse + personnel 22-25 % vs les 10 % du fisc) | +14 600 - 18 400 € | +25-32 % | *Argument juridique* (CAA Paris 17/03/2021, à confirmer en source primaire) ; + la **remise 5 % que le fisc applique aussi** et qu'on avait oubliée (+6 338 €). → `M-abattements-jurisprudence.md` |
| L | **Sur-versement au verre** (+15 %, défendable) | ~10 300 € | ~18 % | *Estimation* ; ne ferme l'écart d'aucune catégorie à elle seule. → `L-dose-implicite.md` |
| ? | **Résiduel : consommation hors-vente non chiffrée** | reste | reste | **PAS du stock** (cf. J ci-dessous) : offerts, casse, personnel et sur-versement au-delà des taux du fisc. |

> **CONSTAT MAJEUR (J) - il n'y a AUCUNE disparition physique.** La propre comptabilité matière
> du fisc (compte 310200) donne une **variation de stock boissons de - 2 104 € sur 3 ans**
> (- 801 / - 1 030 / - 273), soit 1,5 % des achats : le stock est **stable**. Par l'identité
> comptable `achats + variation de stock = consommation`, **98,5 % des achats ont été consommés**.
> Le « résiduel » n'est donc **pas du stock** (mon ancienne hypothèse, fausse) : c'est de la
> **consommation sans recette** (cuisine, offerts, pertes, sur-versement). L'inventaire ne fera
> que **confirmer** ce stock stable. L'enjeu réel n'est pas « où sont passées les bouteilles »
> (elles ont été consommées) mais « quelle recette cette consommation aurait dû générer » - et
> le fisc la sur-évalue par son coefficient × 3,1 (cf. failles, inversion).

> **CORRECTION (vérifiée sur les fichiers de caisse) - la « substitution » n'est PAS un poste de l'écart.**
> « Vente sous un autre bouton » (10 871 €) et « boutons génériques » (3 134 €) étaient un
> **double comptage** : tous les boutons mutualisés/génériques sont **déjà attribués** dans notre
> « vendu ». Ces ventes restent un **argument d'attribution** contre le « disparu par produit »
> du fisc (cf. failles), mais pas un poste de l'écart.

> **Piste écartée - boisson comprise dans un menu** : vérifié, **aucune** boisson n'est incluse dans un menu/formule. Piste supprimée.

**Aucune de ces lignes n'est une vente en espèces.** La boisson est soit **consommée hors-vente**
(cuisine, pertes, personnel), soit **jamais reçue** (E), soit **encore en stock**. Et lorsqu'elle
est vendue (y compris sous un bouton mutualisé), **sa recette est déjà dans le CA déclaré**.

> Distinction stricte : D/C/B/E = **vérifié exact** (calcul sur les données) ; G/H/F =
> **estimations bornées** aux taux de la profession, à confirmer par l'exploitant ;
> stock = **à chiffrer avec l'inventaire**.

## 3. Les failles du calcul du fisc (auditées - `A-audit-fisc.md`, `I-audit-fisc-approfondi.md`)

- **La discordance est à ~147 % un artefact de méthode (vérifié au centime).** Le fisc
  reconstitue **165 065 € TTC** de CA *liquide* (2024-2025) contre **106 113 €** réellement
  encaissés (**+55,6 %**), puis **amplifie × 3,1** sur des « solides » jamais mesurés. En
  réinjectant le **vrai** CA liquide dans sa **propre formule** (× 3,1, abattement 15 %),
  le total reconstitué tombe à **369 804 €**, **sous** le CA déclaré (435 525 €) : la
  discordance de **+139 728 €** s'**inverse à −65 721 €** → **aucune occultation**.
- **Ce qu'il NE faut PAS plaider (vérifié)** : la base d'achats du fisc est *nette* (sans
  consigne/emballage) et ses doses sont *égales* à la carte - pas d'erreur de ce côté.
  Le défaut est le **coefficient × 3,1 appliqué à un liquide reconstitué gonflé**, abattu
  de 15 % seulement quand l'écart réel est de 35,7 %.
- **Cuisine ignorée dans la conclusion alors qu'il la chiffre ailleurs** : le fisc déduit
  la cuisine produit par produit (§ D) mais conclut quand même à l'occultation.
- **Ses 2 preuves « vente sans achat »** (Mouton Cadet, HC Nuits) sont, par ses propres
  mots, un **artefact de paramétrage caisse** (H1 « confirmée ») - donc un problème
  d'étiquetage, pas une recette cachée.
- Ce que le fisc n'a **pas** mal fait (vérifié, à ne pas plaider) : pas d'erreur de fût
  ×8 (il retient 632 L de bière ≈ nos 672 L), doses cohérentes. *L'erreur ×8 était dans
  notre source `achats-par-produit.json`, corrigée - voir `VERIFICATION.md`.*

## 4. L'argument matériel décisif

Même en supposant tout le volume « manquant » vendu (ce qui est faux), il faudrait un
canal d'encaissement. Or **98,7 % du chiffre d'affaires est encaissé par moyens
traçables** (carte, titres-restaurant, chèques - cf. analyse *bancarisation*). Il
n'existe matériellement pas de canal espèces pour des dizaines de milliers d'euros.

## 5. Prochaine étape pour fermer l'écart à 100 %

Le seul poste non encore chiffré est le **stock (inventaire)**. Dès qu'il sera fourni :
`disponible = stock initial + achats − stock final` (au lieu de `= achats`). On attend
qu'il **absorbe l'essentiel des ~44 % résiduels** et ramène la « disparition » réelle
à la cuisine + pertes + remises - soit **zéro recette occultée**.
