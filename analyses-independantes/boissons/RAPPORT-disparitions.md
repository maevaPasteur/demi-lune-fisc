# Disparitions de boissons - calcul indépendant (hors fisc)

> Croisement achats fournisseur ⇄ ventes caisse. Voir `00-METHODOLOGIE.md`. Généré par `scripts/boissons/02_disparitions.py`.

## Vue d’ensemble (3 exercices)

| Indicateur | 2022-2023 | 2023-2024 | 2024-2025 | Cumul |
|---|--:|--:|--:|--:|
| Achats boissons (HT) | 42 092 € | 42 210 € | 42 451 € | 126 752 € |
| CA boissons vendu (TTC, caisse) | 102 425 € | 108 919 € | 106 113 € | 317 458 € |
| **Disparitions au COÛT d’achat (HT) - borne basse** | **20 359 €** | **18 989 €** | **18 712 €** | **58 060 €** |
| Couverture du CA caisse attribuée | 88 % | 89 % | 90 % |  |

> **Disparitions valorisées à la REVENTE** (produits servis purs, par exercice) - au **prix encaissé caisse** : **218 167 € TTC** ; au **tarif carte** de chaque période : **199 490 € TTC** (couvre 79.1 % du volume d’écart).
> ⚠️ Bornes AVANT déduction de la consommation du personnel, des offerts, des pertes/casse, des usages cuisine et de l’inventaire (stock). Voir limites en bas.

## Bilan par catégorie (volume acheté vs vendu, cumul 3 ans)

| Catégorie | Acheté | Vendu (attribué) | Écart | Écart % | Disparition au coût HT |
|---|--:|--:|--:|--:|--:|
| vin | 5 661 L | 3 653 L | 2 008 L | 36 % | 22 617 € |
| macvin | 806 L | 330 L | 476 L | 59 % | 8 638 € |
| spiritueux_digestif | 676 L | 215 L | 462 L | 68 % | 7 353 € |
| cremant_petillant | 1 275 L | 629 L | 647 L | 51 % | 5 800 € |
| biere | 2 734 L | 1 460 L | 1 274 L | 47 % | 5 669 € |
| soft | 3 725 L | 1 196 L | 2 530 L | 68 % | 4 693 € |
| jus | 990 L | 503 L | 487 L | 49 % | 1 651 € |
| eau | 1 560 L | 947 L | 613 L | 39 % | 1 082 € |
| sirop | 169 L | 43 L | 126 L | 75 % | 712 € |

## Top produits par valeur de disparition (au coût HT, cumul)

| Produit | Cat. | Conf. | Acheté | Vendu | Écart bout. | Coût HT | Vente TTC |
|---|---|---|--:|--:|--:|--:|--:|
| MACVIN BLANC 75 CL 18° DOMAINE ROL | macvin | haute | 264 L | 13 L | 334.54 | 5 026 € | 24 929 € |
| CREMANT JURA BLANC 75 CL FRUITIERE | creman | basse | 675 L | 287 L | 517.69 | 4 272 € | 14 760 € |
| FUT AFFLIGEM BLADE 8 L 6,7° | biere | moyenne | 2 096 L | 1 196 L | 112.52 | 3 566 € | 14 636 € |
| MACVIN BLANC JACOBIN 75 CL FRUITIE | macvin | haute | 192 L | 13 L | 238.54 | 3 076 € | 14 210 € |
| ARBOIS SAVAGNIN 75 CL 2018 FRUITIE | vin | moyenne | 268 L | 72 L | 262.56 | 3 059 € | 10 350 € |
| BOITE COCA COLA 33 CL | soft | haute | 1 964 L | 414 L | 4696.83 | 3 046 € | 18 079 € |
| ARBOIS VIN JAUNE 62 CL 2016 FRUITI | vin | moyenne | 82 L | 4 L | 125.29 | 2 784 € | 8 015 € |
| BIB COTES DE PROV ROSE 10 L CAP DE | vin | basse | 500 L | 83 L | 41.75 | 2 202 € | 8 710 € |
| BIB BOURGOGNE ALIGOTE BUXY 10L LA  | vin | basse | 640 L | 281 L | 35.91 | 1 902 € | 7 595 € |
| ARBOIS VIN JAUNE 62 CL 2015 FRUITI | vin | moyenne | 65 L | 4 L | 98.29 | 1 880 € | 6 108 € |
| ARBOIS VIN JAUNE 62 CL 2017 FRUITI | vin | moyenne | 46 L | 4 L | 67.29 | 1 618 € | 4 093 € |
| PORTO SANDEMAN ROUGE 75CL 19°5 | spirit | haute | 128 L | 3 L | 167.55 | 1 350 € | 9 857 € |
| CALVADOS BEAUJOUR 100 CL 40° | spirit | haute | 73 L | 1 L | 71.56 | 1 204 € | 10 464 € |
| ARBOIS BLANC CUV BETHANIE 75CL FRU | vin | haute | 148 L | 60 L | 118.67 | 1 191 € | 3 726 € |
| ARBOIS TROUSSEAU 75 CL 2020 DOMAIN | vin | moyenne | 141 L | 55 L | 114.79 | 1 122 € | 3 640 € |
| ARBOIS TROUSSEAU 75 CL 2022 DOMAIN | vin | moyenne | 130 L | 55 L | 100.79 | 1 076 € | 3 781 € |
| MACON ROCHE BLANCHE 75 CL MACON BL | vin | moyenne | 136 L | 40 L | 128.12 | 1 065 € | 4 021 € |
| SAINT JOSEPH ROUGE 75 CL 2022 LES  | vin | moyenne | 76 L | 24 L | 70.54 | 973 € | 3 472 € |
| ARBOIS TROUSSEAU 75 CL 2023 DOMAIN | vin | moyenne | 120 L | 55 L | 86.79 | 956 € | 3 475 € |
| ARBOIS BLANC CUV BETHANIE 37,5 FRU | vin | haute | 85 L | 33 L | 138.38 | 925 € | 3 008 € |
| PERRIER 33 CL CONSIGNE | eau | haute | 412 L | 132 L | 849.5 | 902 € | 3 374 € |
| CHAMPAGNE R DE RUINART 75 CL | creman | basse | 21 L | 6 L | 20.67 | 895 € | 952 € |
| SAINT VERAN 75 CL 2022 CAVE DE PRI | vin | moyenne | 102 L | 31 L | 95.1 | 862 € | 3 814 € |
| MOULIN A VENT 75 CL 2018 DOMAINE D | vin | moyenne | 132 L | 79 L | 70.83 | 837 € | 2 884 € |
| SAINT JOSEPH ROUGE 75 CL 2019 LES  | vin | moyenne | 68 L | 24 L | 58.54 | 754 € | 1 995 € |
| SAINT JOSEPH ROUGE 75 CL 2021 LES  | vin | moyenne | 64 L | 24 L | 54.54 | 753 € | 2 336 € |
| PICON BIERE 100 CL 18° | biere | - | 72 L | 0 L | 72.0 | 748 € | - |
| GEWURZTRAMINER 75 CL SORCIERES DOM | vin | moyenne | 95 L | 39 L | 74.42 | 742 € | 2 669 € |
| SAINT VERAN BLANC 75 CL 2022 CAVE  | vin | moyenne | 84 L | 31 L | 71.1 | 705 € | 2 919 € |
| CIDRE LA MORDUE ORIGINAL 27 CL | creman | haute | 238 L | 92 L | 538.5 | 627 € | 2 430 € |

## Hypothèses & limites

- BIÈRE PRESSION INCLUSE : le fût (212122 « FUT AFFLIGEM ») est bien le LIQUIDE - quantité facturée en LITRES (colis×8 L, ~3,59 €/L = ~28,72 €/fût). Volume = litres×100 cl (et non ×800). La consigne est hors lignes (totalFacture − totalTTC).
- Aucune ligne exclue. 1 lignes 'matériel' (verrerie/kits, 283 € HT) conservées avec un volume de boisson nul (ce ne sont pas des liquides).
- Aucun inventaire : stock initial = stock final = 0 supposé. Un écart positif (acheté>vendu) peut être une constitution de stock, pas une disparition.
- Consommation du personnel, offerts, pertes, casse, usages cuisine NON déduits (paramètres de simulation à venir).
- Volume vendu attribué par dose/recette (doses de la carte). Confiance par produit : 'basse' = cocktail/recette estimée.
- Boutons caisse génériques (Sirop à l'eau, Jus de Fruit, Verre/Pichet de vin de base) : l'attribution par SKU est imparfaite → privilégier le bilan PAR CATÉGORIE.
- Couverture : ~88% du CA caisse liquide est attribué à un achat ; le reste = café/thé/expresso (hors fournisseur boissons) et libellés tronqués non identifiables.
- Valorisation au prix de vente : prix/cl observé en caisse, calculé PAR EXERCICE (reflète l'évolution des prix et les 3 cartes successives : carte 20/07/2021 pour 2022-2023, carte 26/04/2023 pour 2023-2025). Doses identiques sur les 3 cartes → volumes inchangés. Seuls les produits servis purs sont valorisés à la revente ; les ingrédients de cocktails au coût uniquement.
- Valorisation à la REVENTE (théorique) = 218 167 € TTC : borne HAUTE qui suppose tout le volume manquant vendu au prix carte. La borne BASSE  rigoureuse  est la valeur au COÛT d'achat (58 060 € HT).
- Chiffres PAR PRODUIT au sein d'un groupe de substituts (même vin/spiritueux servi sous un bouton unique, plusieurs millésimes/domaines) = RÉPARTITIONS indicatives ; seul le total PAR CATÉGORIE est robuste.
