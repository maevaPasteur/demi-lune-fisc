# Hypothèse C - Substitution de bouton caisse (mauvais étiquetage / confusion de code)

**Thèse.** Une partie de l'écart achats−ventes ne correspond pas à des bouteilles « disparues »
mais à des bouteilles **vendues sous un autre bouton caisse** : plusieurs codes d'achat
(millésimes / domaines différents d'une même appellation) sont encaissés sous **un seul bouton
générique**. Le moteur de disparition attribue alors le volume du bouton à un seul code et laisse
les autres codes à ~0 vendu → ils paraissent disparus alors qu'ils ont été vendus.

Vérifié par python (`/tmp/pwenv/bin/python`) en croisant :
`disparitions.json` (parProduit) × `map-*.json` (champ `ventes[].ingredients[].achatCode`) ×
`ventes-caisse.json` (volumes par bouton) × `src/data/volumes-disparus-fisc.json`.

---

## 1. Mécanisme confirmé par les données

Sur les **117** produits achetés à disparition > 60 %, **48** apparaissent comme ingrédient d'un
bouton caisse partagé avec d'autres codes (donc *sont* vendus, mais sous un bouton mutualisé).
Pour **23** d'entre eux, le volume « disparu » est effectivement absorbé par un code « frère »
**sur-vendu** sous le même bouton (vendu > acheté pour ce frère) - preuve directe du report de
vente d'un code sur un autre.

**Total expliqué par substitution intra-bouton : 791 L · 10 871 € HT (coût) · ≈ 38 761 € TTC (valeur de vente).**
À rapprocher de la disparition totale de **58 060 € HT** → **≈ 18,7 %** de l'écart valorisé s'explique
mécaniquement par la substitution de bouton, sans aucune perte physique.

---

## 2. Substitutions confirmées (code « disparu » absorbé par un frère sur-vendu sous le même bouton)

| Code | Produit acheté (millésime/domaine) | Bouton(s) caisse mutualisé(s) | Vol. récupéré | € HT |
|------|------------------------------------|-------------------------------|--------------:|-----:|
| 601164 | Arbois Savagnin 2018 Frut. Arbois | Arbois Savagnin / Savagnin verre / PICHET SAVAGNIN | 145,0 L | 2 252 |
| 601166 | Arbois Trousseau 2020 JL Tissot | Arbois Trousseau Bout./Verre / PICHET TROUSSEAU | 86,1 L | 1 122 |
| 601680 | Saint Joseph rouge 2022 | C du Rhône St Joseph / pichet Saint Joseph | 52,9 L | 973 |
| 661679 | Saint Joseph rouge 2019 | idem | 43,9 L | 754 |
| 601460 | Saint Joseph rouge 2021 | idem | 40,9 L | 753 |
| 601862 | Saint Véran blanc 2022 Lugny | Saint Véran / Saint Véran Verre / PICHET ST VERAN | 53,3 L | 705 |
| 601477 | Saint Véran 2022 Cave Prissé | idem | 55,1 L | 666 |
| 601401 | Chablis St Martin 2022 Laroche | Chablis / Chablis Le Verre / Pichet Chablis | 27,6 L | 485 |
| 601454 | Arbois Chardonnay 2020 JL Tissot | Arbois Chardonnay Le verre | 43,3 L | 450 |
| 601253 | Chablis St Martin 2021 Laroche | Chablis / Chablis Le Verre / Pichet Chablis | 25,1 L | 447 |
| 601304 | Arbois blanc Béthanie 37,5 cl | 1/2 Arbois Béthanie | 19,4 L | 345 |
| 661715 | Mâcon Roche Blanche 2022 | MACON VERRE / MACON bouteille / PICHET MACON | 30,7 L | 340 |
| 661457 | Arbois Vin Jaune 2017 | Vin jaune | 6,3 L | 244 |
| 603042 | BIB Côtes de Provence rosé 10 L | Verre Rosé / Pichet 50/75 / Verre de vin | 44,5 L | 235 |
| 601489 | Arbois Vin Jaune 2016 | Vin jaune | 6,3 L | 225 |
| 661576 | Arbois Vin Jaune 2015 | Vin jaune | 6,3 L | 194 |
| 403201 | Cidre doux Contemporaine 75 cl | Cidre Bouché Doux | 35,8 L | 138 |
| 510221 | Macvin blanc Domaine Rolet | Macvin du Jura | 6,4 L | 127 |
| 600731 | BIB blanc Ravelin 10 L | Pichet 50/75 / Verre de vin | 44,5 L | 125 |
| 665175 | Macvin Jura blanc F. Lornet | Macvin du Jura | 6,4 L | 123 |
| 601152 | Macvin blanc Jacobin | Macvin du Jura | 6,4 L | 109 |
| 580018 | Porto Sandeman rouge | Porto | 3,7 L | 40 |
| 630081 | Côtes de Provence rosé Minuty | Château Minuty | 1,1 L | 20 |
| | | **TOTAL** | **791 L** | **10 871** |

> Lecture : pour ces appellations, le bouton caisse est unique alors que la cave tourne sur
> plusieurs millésimes/domaines. La caissière encaisse au nom du bouton (ex. « C du Rhône St
> Joseph ») quel que soit le millésime servi → les millésimes non sélectionnés en caisse
> ressortent à 0 vendu, donc « disparus » à tort.

## 3. Substitutions plausibles (groupes où plusieurs codes partagent un bouton - écart résiduel intra-groupe)

Au niveau du **groupe de codes partageant un bouton**, l'écart par code se résorbe largement,
confirmant la mutualisation :

| Groupe / boutons | Codes | achat (cl) | vendu (cl) | écart groupe |
|------------------|------:|-----------:|-----------:|-------------:|
| Pichets/verres rouge & rosé génériques (Aligoté, Chusclan, Verre de vin…) | 9 | 205 142 | 87 056 | 57,6 % |
| Apéritifs maison génériques (Crémant, Kir, Macvin, La Vouivre, Père Grégoire…) | 10 | 167 065 | 75 065 | 55,1 % |
| Arbois Savagnin (verre/pichet/bouteille) | 6 | 51 600 | 42 947 | **16,8 %** |
| Arbois Trousseau (verre/pichet/bouteille) | 7 | 46 275 | 38 433 | **16,9 %** |
| Saint Véran (verre/pichet) | 8 | 32 925 | 24 542 | 25,5 % |
| Saint Joseph C. du Rhône (verre/pichet) | 7 | 23 850 | 16 515 | 30,8 % |
| Mâcon (verre/bouteille/pichet) | 5 | 19 800 | 12 122 | 36,6 % |
| Chablis (verre/pichet) | 7 | 10 350 | 7 370 | 28,8 % |

> Les écarts résiduels de groupe (Savagnin, Trousseau ~17 %) tombent dans la marge des autres
> hypothèses (doses, casse). Les deux gros groupes génériques restent élevés : la substitution
> y joue mais ne couvre pas tout (cf. hypothèses A/B/D).

---

## 4. Confirmation des 2 cas reconnus PAR LE FISC (vente sans achat = preuve H1 paramétrage)

Le fisc lui-même reconnaît deux **ventes sans achat** (`meta.verdict_hypotheses.H1 = CONFIRMEE`).
Vérification avec **nos** chiffres d'achat exacts :

| Cas fisc | Vente caisse constatée | Achat correspondant dans nos données | Verdict |
|----------|------------------------|--------------------------------------|---------|
| **Bordeaux Mouton Cadet** | bouton « BORD. MOUTON CADET » (réf. 1859, 33,82 €) ; fisc : 6 bouteilles 2024-2025 vendues sans achat ; nos relevés caisse : 9 vendus en 2022-2023 | **AUCUN achat « Mouton Cadet » dans l'exercice** (0 occurrence dans `achats-exercice.json`) | **Vente sans achat → paramétrage** |
| **Hautes Côtes de Nuits** | bouton « H.COTES DE NUITS » + report probable sur « H.C.DE BEAUNE VERRE » / « PICHET C.DE BEAUNE » ; fisc : 172 bouteilles (12 950 cl) vendues 2023-2024 sans achat | seul achat « Nuits » = **HTES CTES DE NUITS *BLANC* 75 cl Lupé-Cholet 2017**, 1 800 cl achetés en 2022-2023 seulement (rien en 2023-2024) | **Vente sans achat → paramétrage** |

Ces deux cas démontrent que le **bouton caisse ne correspond pas au produit physiquement servi** :
une vente est imputée à un libellé pour lequel aucune bouteille n'a été achetée. C'est la preuve
miroir de la substitution : si des ventes apparaissent **sans achat** sur certains boutons, alors
des **achats apparaissent sans vente** ailleurs - les deux phénomènes sont le même paramétrage.

---

## 5. Chiffrage récapitulatif

| Indicateur | Volume | € HT (coût) | € TTC (vente) |
|------------|-------:|------------:|--------------:|
| Disparition totale boissons (exercices cumulés) | - | 58 060 | 218 167 (théo.) |
| **Part expliquée par substitution de bouton (23 cas confirmés)** | **791 L** | **10 871** | **≈ 38 761** |
| Part de la disparition expliquée | - | **≈ 18,7 %** | - |
| Cas fisc vente-sans-achat (Mouton Cadet + HC Nuits) | preuve qualitative H1 « CONFIRMEE » | - | - |

**Conclusion.** La substitution de bouton est **prouvée** (23 cas chiffrés + 2 cas reconnus par le
fisc) et explique mécaniquement **≈ 18,7 % de l'écart valorisé** (10 871 € HT / 791 L) sans aucune
disparition physique. Elle ne couvre pas la totalité : le solde relève des autres hypothèses
(doses, casse/offerts, usage cuisine déjà déduit).
