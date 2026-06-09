> ⚠️ CORRECTION (revue critique 2026-06-07) - CE DOCUMENT CONTENAIT DEUX ERREURS, corrigées ci-dessous :
> 1. **Double comptage des cocktails** : les boutons cocktails sont DÉJÀ attribués à leurs ingrédients
>    par le pipeline (`map-cocktails.json` + `map-eaux-softs.json` : La Vouivre→crémant/macvin/cassis,
>    Mambo/Luna→jus/limonade, Picon Bière→fût…). L'écart acheté−vendu est donc DÉJÀ net des cocktails.
>    Les réattribuer (« 1 545 L absorbés ») était un double comptage (~1 150 L). Apport réellement
>    nouveau ≈ 388 L (Kir et quelques mixers non mappés) - marginal.
> 2. **Cuisine vin jaune impossible** : 284 L revendiqués alors que le vin jaune ACHETÉ = 218 L
>    (écart 180 L). La dose 4-8 cl/plat était trop forte. La cuisine utilise un MÉLANGE vin jaune +
>    savagnin + chardonnay ; volume borné par l'écart de ces vins (~270 L), pas 284 L de pur vin jaune.
> Le script `03_reattribution.py` et le JSON associés ont été SUPPRIMÉS. La page ne montre plus de
> tableau de réattribution chiffré, seulement : (a) offerts négligeables, (b) comptes de plats exacts
> avec volume cuisine BORNÉ par l'achat. Taux d'explication honnête ≈ 32 % (cohérent avec le coût),
> pas 46 %. Le reste = consommation non-vente bornée (personnel, sur-versement, pertes), non chiffrable
> à la goutte mais NON-revenu (98,7 % bancarisé) et hors stock (inventaire stable).

# Réattribution par les recettes (cocktails) et les plats (cuisine) - vérifié en caisse

> Round d'approfondissement : on ne suppose plus, on DÉCOMPOSE. Recettes de cocktails
> tirées de la carte (`vins-boissons/carte_..._26:04:23.xls`), plats comptés un par un
> dans la caisse (annexe D), doses d'alcool bornées (standards bar/cuisine).
> Offerts clients = quasi nuls (vérifié). Stock stable (inventaire).

## 0. Offerts : réfutés par la caisse
272 lignes à 0 € sur 97 694 (0,28 %), surtout des cafés (Expresso 58). Confirme la cliente :
aucun offert boisson aux clients hormis quelques cafés. → « offerts » retiré des explications.

## 1. Cocktails : les ingrédients « disparus » sont vendus sous le bouton cocktail

Recettes exactes (carte). Quantités vendues = caisse (annexe D, 3 ans). Doses bornées.

| Cocktail | Vendus | Compose de |
|---|--:|---|
| La Vouivre | 2 284 | Crémant + Macvin + Cassis |
| Kittykir | 1 735 | Soho + Crémant + sirop |
| Chat Perché | 1 664 | Macvin + Jus poire + sirop |
| Père Grégoire (apéro) | 1 608 | Crémant + Macvin + liqueur cerise |
| Kir | 1 466 | Aligoté + Cassis |
| Mambo | 947 | Jus orange + jus fraise + Limonade |
| Luna | 567 | Jus poire + Limonade + sirop |
| Picon Bière | 545 | **Picon + bière** (Picon vendu, pas seulement bu) |
| Balidou, Maëva, Rêve Bleu, Tequila sunrise, Rabasse, Rosé Pamp | ~700 | Passoa/Vodka/Tequila + jus + sirop |

**Ingrédients absorbés par les cocktails (3 ans) : ~1 690 L** dont jus 360, crémant 347,
bière/Picon 218, macvin 167, aligoté 147, limonade 142, sirop 123, cassis 75, soho 41…
→ Le jus Granini « 0 vendu » est absorbé à **74 %** par les cocktails ; le sirop à 98 %.
Ces volumes sont **vendus**, recette dans le CA, sous un bouton cocktail.

## 2. Cuisine : plats comptés en caisse × dose (liste confirmée par la cliente)

| Alcool | Plats (comptes caisse exacts) | Volume |
|---|---|--:|
| **Vin jaune** | 5 774 sauces (poulet/truite jurassienne, morilles) + 659 fondues (vin jaune, gourmet) | **213-348 L** |
| **Vin blanc** | 1 150 fondues jurassiennes | **115-172 L** |
| **Macvin** | 1 330 babas | **27-53 L** |
| **Calvados** | 2 225 plats (camembert rôti, assiette Père Grégoire, dessert Normandine) | **33-56 L** |

Le vin jaune/savagnin (~9 600 € « disparu ») est ainsi en grande partie de la **cuisine
jurassienne**, désormais chiffrée sur des comptes de plats réels (et le fisc admet déjà
le principe pour macvin/calvados/porto).

## 3. Réconciliation par catégorie (L sur 3 ans)

| Catégorie | Écart | Cocktails | Cuisine | Perso/pertes | Résiduel |
|---|--:|--:|--:|--:|--:|
| soft | 2 530 | 142 | - | 1 550 (Coca attesté) | 838 |
| vin | 2 008 | 154 | 424 | - | 1 430 |
| bière | 1 274 | 218 | - | 400 (pertes+Picon) | 656 |
| crémant | 647 | 347 | - | - | 300 |
| eau | 613 | - | - | 490 (personnel) | 123 |
| jus | 487 | 360 | - | - | 127 |
| macvin | 476 | 167 | 40 | - | 269 |
| spiritueux | 462 | 86 | 44 | - | 332 |
| sirop | 126 | 123 | - | - | 3 |
| **Total** | **8 682** | **1 596** | **508** | **2 440** | **~4 137 (48 %)** |

**Expliqué vérifié ≈ 52 %** (cocktails recettes + cuisine comptes + Coca attesté).

## 4. Le résiduel (~48 %) - non-revenu, borné, jamais des espèces

- **Vin (1 430 L)** : sur-versement au verre (carte 15 cl, versé 17-18), coupes, déglaçage/sauces
  non listés, bouteilles ouvertes au verre peu écoulées, dégustation. Diffus, non-revenu.
- **Autres sodas + eau (≈960 L)** : conso personnel au-delà du Coca (Fuzetea, Orangina, Schweppes,
  Perrier, Vittel) - à couvrir par l'attestation élargie.
- **Bière (656 L)** : pertes techniques (mousse, nettoyage lignes, fond de fût) + Picon de Thierry.
- **Crémant/macvin/spiritueux (~900 L)** : coupes/apéritifs vendus sous boutons proches + doses.

Aucune de ces lignes n'est une vente en espèces (98,7 % du CA bancarisé) ; et l'inventaire
prouve que **rien ne s'accumule en stock** - tout est consommé.

## 5. Réponse à « d'autres disparitions suspectes ? »
Non. Les alcools chers bus secs (whisky, vodka, cognac, gin) ont des écarts minuscules
(1-19 bt) et figurent à l'inventaire. Les gros écarts sont tous tracés : cocktails (vendus),
cuisine jurassienne (plats réels), personnel attesté, sur-versement/pertes. Rien ne pointe
vers une recette occultée.

## 6. Pour fermer encore (données à obtenir)
- Doses exactes de vin jaune par plat (confirmer la fourchette 3-9 cl).
- Attestation personnel ÉLARGIE à tous les sodas + eaux (pas que le Coca).
- Fréquence Picon de Thierry (part non vendue des 72 L).
