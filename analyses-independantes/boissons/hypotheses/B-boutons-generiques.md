# Hypothèse B - Boutons de caisse GÉNÉRIQUES (volume vendu non rattaché au SKU acheté)

**Thèse.** Une partie de l'écart achats−ventes ne traduit aucune disparition physique : elle vient
de **boutons de caisse génériques / composites** qui encaissent du volume **sans l'imputer au produit
fournisseur précis**. Le moteur de disparition (`02_disparitions.py`) ne crédite alors au stock acheté
qu'une **fraction** du volume réellement servi (la dose « principale » de la carte), laissant le reste
du liquide consommé compté comme « disparu ». Trois familles de boutons sont concernées :

1. **Boutons « de base » vin au verre / pichet** (`Verre de vin`, `Pichet 50/75 cl`, `Verre/Pichet Aligoté, Mâcon, Chusclan, Rosé`) : volume bien servi, mais rattaché au seul BIB de base.
2. **Boutons soft/sirop/jus génériques** (`Jus de Fruit`, `Limonade`, `Sirop à l'eau`, `Diabolo`, `Monaco`) : seule une **dose partielle** est imputée (ex. `Sirop à l'eau` = **2 cl** de sirop imputés, le reste = eau/limonade hors fournisseur ; `Diabolo` idem).
3. **Apéritifs composites** (`Mambo`, `Luna` sans alcool 25 cl ; `La Vouivre`, `Chat perché`, `Père Grégoire`, `KittyKir`, `Balidou`) : recettes **estimées** (confiance *basse/moyenne*) → soda, jus, sirop et crèmes/liqueurs **sous-crédités**.

Vérifié par python (`/tmp/pwenv/bin/python`) en croisant `ventes-caisse.json` × `map-*.json`
(champ `ingredients[].clParUnite`) × `achats-exercice.json` × `disparitions.json`.

---

## 1. Boutons génériques identifiés - quantité et CA par exercice (cumul 3 ans)

| Bouton (réf.) | 2022-23 | 2023-24 | 2024-25 | Qté cumul | CA TTC cumul |
|---|--:|--:|--:|--:|--:|
| **Vin au verre / pichet (boutons « de base »)** | | | | | |
| Pichet 50cl vin (2121) | 512 | 141 | 79 | **731** | 7 096 € |
| Pichet 75cl vin (0307) | 118 | 13 | 0 | **132** | 1 752 € |
| Verre CHUSCLAN (0309) | 311 | 32 | 19 | **362** | 1 315 € |
| Verre ALIGOTE (2112) | 0 | 163 | 182 | **345** | 1 346 € |
| PICHET ALIGOTE 50cL (2113) | 0 | 150 | 165 | **315** | 3 290 € |
| MACON VERRE (2110) | 0 | 162 | 159 | **320** | 2 019 € |
| PICHET MACON (2125) | 0 | 46 | 44 | **90** | 1 901 € |
| Pichet CdR CHUSCLAN (2114) | 0 | 74 | 68 | **142** | 1 354 € |
| Verre Rosé (2116) | 0 | 136 | 155 | **291** | 1 135 € |
| Verre CHUSCLAN (2115) | 0 | 100 | 84 | **185** | 720 € |
| **Soft / sirop / jus génériques** | | | | | |
| Jus de Fruit (0368) | 416 | 360 | 342 | **1118** | 4 533 € |
| Limonade (25cl) (0108) | 203 | 200 | 217 | **620** | 2 402 € |
| Sirop à l'eau (0352) | 240 | 245 | 263 | **748** | 1 638 € |
| Diabolo (25cl) (0110) | 133 | 120 | 97 | **350** | 1 353 € |
| Monaco (0354) | 66 | 56 | 74 | **196** | 807 € |
| **Apéritifs sans alcool (composites 25 cl)** | | | | | |
| Mambo (1996) | 290 | 342 | 315 | **947** | 6 129 € |
| Luna (1997) | 164 | 192 | 211 | **567** | 3 366 € |
| **Apéritifs « MAISON » (cocktails composites, recette estimée)** | | | | | |
| La Vouivre (0357) | 622 | 794 | 704 | **2120** | 11 955 € |
| Chat perché (1995) | 494 | 613 | 557 | **1664** | 9 292 € |
| Père Gregoire (0333) | 503 | 559 | 546 | **1608** | 8 818 € |
| KITTYKIR (0001) | 234 | 288 | 345 | **867** | 4 489 € |
| BALIDOU (0002) | 67 | 95 | 91 | **253** | 2 223 € |
| **TOTAL boutons génériques** | | | | **13975** | **78 931 €** |

> Ces boutons concentrent un volume de service important mais **mutualisé/composite** : le rattachement par SKU est par construction imparfait (cf. `00-METHODOLOGIE.md`, constat n°4 ; caveat `disparitions.json`).

---

## 2. Volume réellement vendu via ces boutons mais compté « disparu » (par catégorie à fort écart)

Pour chaque catégorie, on chiffre le **liquide additionnel plausible** servi via les boutons génériques mais **non crédité** par le moteur (dose réaliste − dose déjà imputée), valorisé au coût d'achat HT et au prix de revente TTC (prix/cl observé en caisse). Le volume expliqué est **plafonné à l'écart de la catégorie**.

| Catégorie (écart %) | Écart total | dont expliqué (volume) | % du volume écart | Coût HT expliqué | Revente TTC expliquée |
|---|--:|--:|--:|--:|--:|
| Sirop (74,6 %) | 126 L | 95 L | 75 % | 534 € | 830 € |
| Soft (67,9 %) | 2 530 L | 413 L | 16 % | 767 € | 5 094 € |
| Jus (49,2 %) | 487 L | 182 L | 37 % | 616 € | 2 948 € |
| Spiritueux (68,2 %) | 462 L | 76 L | 17 % | 1 217 € | 5 233 € |
| **TOTAL (4 catégories)** | | | | **3 134 €** | **14 104 €** |

### Détail des doses non créditées retenues (conservatrices, traçables)

| Catégorie | Bouton | Qté | Dose non créditée | Volume | Coût HT | Revente TTC |
|---|---|--:|--:|--:|--:|--:|
| sirop | Monaco | 196 | 2 cl/u | 4 L | 22 € | 34 € |
| sirop | Mambo | 947 | 6 cl/u | 57 L | 320 € | 497 € |
| sirop | Luna | 567 | 6 cl/u | 34 L | 192 € | 298 € |
| soft | Monaco | 196 | 23 cl/u | 45 L | 84 € | 557 € |
| soft | Mambo | 947 | 19 cl/u | 180 L | 334 € | 2 217 € |
| soft | Luna | 567 | 19 cl/u | 108 L | 200 € | 1 328 € |
| soft | Diabolo (25cl) | 350 | 23 cl/u | 80 L | 149 € | 992 € |
| jus | Mambo | 947 | 10 cl/u | 95 L | 321 € | 1 536 € |
| jus | Luna | 567 | 10 cl/u | 57 L | 192 € | 920 € |
| jus | BALIDOU | 253 | 12 cl/u | 30 L | 103 € | 492 € |
| spiritueux_digestif | La Vouivre | 2120 | 2 cl/u | 42 L | 675 € | 2 904 € |
| spiritueux_digestif | KITTYKIR | 867 | 2 cl/u | 17 L | 276 € | 1 188 € |
| spiritueux_digestif | Chat perché | 1664 | 1 cl/u | 17 L | 265 € | 1 140 € |

> Prix de revente/cl par catégorie (boutons purs) : sirop 0.088 €/cl, soft 0.123 €/cl, jus 0.162 €/cl, spiritueux_digestif 0.685 €/cl. Doses additionnelles **volontairement basses** (bornes prudentes) ; le sirop/limonade/eau ajoutés au-delà du fournisseur boissons ne sont pas comptés ici.

---

## 3. Part de l'écart expliquée par les boutons génériques (PAS une disparition réelle)

| Référence | Écart total (dossier) | Expliqué par boutons génériques | Part |
|---|--:|--:|--:|
| **Au coût d'achat (HT)** | 58 060 € | 3 134 € | **5.4 %** |
| **À la revente (TTC, théorique)** | 218 167 € | 14 104 € | **6.5 %** |

**Lecture.** L'effet « boutons génériques » est **modéré en coût** (5.4 %) car les liquides
concernés (sirop, limonade, jus, soda) sont **bon marché au cl**, mais **plus visible à la revente**
(6.5 %), car ces mêmes volumes sont **encaissés** dans des boissons à forte valeur ajoutée.
Surtout, il **explique l'essentiel de l'écart « sirop » (≈ 75 % du volume)** : le bouton `Sirop à l'eau`
ne crédite que **2 cl** de sirop par vente, et les apéritifs sans alcool `Mambo`/`Luna` (1 514 ventes)
n'en créditent **aucun** - alors qu'ils consomment tout le sirop acheté.

**Cette hypothèse B est complémentaire de l'hypothèse C** (substitution intra-bouton sur les vins,
≈ 38 761 € TTC / 18,7 %) : B traite les **soft/sirop/jus/apéritifs composites**, C traite les **vins/spiritueux
mono-produit mutualisés**. Les deux mécanismes additionnés couvrent une part substantielle de l'écart
**sans aucune perte physique ni vente cash occulte** - l'écart résiduel relève de l'inventaire (stock),
de la consommation personnel/offerts et des pertes (hypothèses D/E).

> **Limites.** Doses non créditées = hypothèses bornées par la carte et plafonnées à l'écart de catégorie
> (jamais d'« explication » au-delà du volume réellement manquant). Les recettes des apéritifs MAISON
> sont en confiance *basse* dans `map-cocktails.json` : un crédit plus généreux (doses réelles) augmenterait
> mécaniquement la part expliquée. Chiffres ré-exécutables.
