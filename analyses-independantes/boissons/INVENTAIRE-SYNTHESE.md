# Inventaire physique : ce qu'il prouve sur les « boissons disparues »

> Source : `public/documents/inventaires/inventaires.json` (3 stocks de clôture :
> 2023-03-31, 2024-03-31, 2025-03-31). Croisé avec achats FCBS, ventes caisse,
> rapport du fisc. Tout est recalculé ligne à ligne, sans supposition.
> Détail par catégorie : `hypotheses/O,P,Q,R,S`.

## 1. Le stock est plat : aucune cave cachée (preuve directe)

| Date | Stock boissons HT (recalculé = déclaré) |
|---|--:|
| 2023-03-31 | 3 674,17 € |
| 2024-03-31 | 4 536,41 € |
| 2025-03-31 | 4 533,22 € |

Cumul **2023 → 2025 = +859 € (jamais en baisse)**. Un exploitant qui détournerait
des bouteilles verrait son stock chuter ; qui les accumulerait le verrait gonfler.
Ici il est stable → **les bouteilles achetées ont été consommées, pas stockées, pas
« disparues » d'une réserve**. Par l'identité `achats + variation stock = consommation`,
~98-100 % des achats sont consommés.

## 2. Le fisc a retenu un MAUVAIS stock (erreur chiffrée)

Sa variation comptable (compte 310200) est de **signe inverse** à la réalité physique :

| Exercice | Variation physique (inventaire) | Variation livre (fisc) | Erreur |
|---|--:|--:|--:|
| 2023-2024 | **+862,24 €** | −1 029,67 € | **+1 891,91 €** |
| 2024-2025 | −3,19 € | −273,41 € | +270,22 € |

Formule du fisc (annexe 6, lettre l. 1767-1768) : `disponible = achats + stock initial −
stock final`. **Sous-estimer le stock final gonfle mécaniquement le « disponible »**, donc
les « disparus » et le CA reconstitué. À recouper avec le comptable (perimètre 310200).

## 3. Les « disparus » précis du fisc tombent pièce par pièce (hypothèse S)

- **7 bières « 100 % disparues »** (1664, Heineken, Grimbergen, Mort Subite, White Rabbit,
  Hefeweizen, Bleue du Mont Blanc) : absentes des 3 inventaires ET vendu caisse = 0 →
  **codes de vente jamais paramétrés**, pas des bouteilles évaporées. Seules bières réelles :
  Rouget Blanche/Ambrée + fût Affligem, présentes aux 3 dates avec écarts normaux.
- **2 « ventes sans achat »** = confusions de code prouvées par l'inventaire :
  - « Mouton Cadet » n'existe nulle part ; le vrai bordeaux = Château Grand Renom
    (code 661236, 1 bt en stock au 31/03/2023).
  - « Hautes Côtes de Nuits » = en réalité un BLANC Lupé-Cholet 2017 acheté en 2022-2023
    (0 achat 2023-2024), distinct de la Haute Côte de Beaune rouge bien stockée (6 bt 2023, 8 bt 2025).
- **Apéritifs/spiritueux à fort pct** (Porto, Picon, Macvin, Martini, Calvados, Pontarlier) :
  stock physique présent aux 3 dates ; les « disparus » (parfois négatifs : vendu > acheté,
  arithmétiquement impossible) = stock initial/final ignoré + dose cuisine déjà admise.

## 4. Le grief de rejet du fisc est levé

Le fisc rejetait la comptabilité matière pour « inventaire incomplet » (lettre l. 771-772,
797-804). L'inventaire désormais **détaillé ligne par ligne** (produit/quantité/PU/valeur,
totaux exacts) répond à ce grief.

## 5. Ce que l'inventaire ne fait PAS (honnêteté)

Il ne fait **pas** disparaître la consommation non sonnée. Bilan matière vérifié (alcools-bouteille) :

| Exercice | Dispo (SI + achats) | Vendu caisse | Stock final réel | Conso hors-vente |
|---|--:|--:|--:|--:|
| 2023-2024 | 370 + 3 307 bt | −2 049 bt | 414 bt | **≈ 1 214 bt** |
| 2024-2025 | 414 + 3 020 bt | −1 941 bt | 322 bt | **≈ 1 171 bt** |

Soit **~1 200 bt d'alcool/an** + Coca (**5 952 achetées / 1 255 vendues / 118 stock → ~1 555/an**)
consommés **sans recette**. L'inventaire **prouve qu'ils ne sont pas en stock** (pas planqués),
mais ne prouve pas seul le **canal** (cuisine + offerts + personnel/famille + sur-versement vs
vente non sonnée). Ce résiduel renvoie aux explications déjà chiffrées :
- **Vins** (P) : l'écart sorties − ventes (~26 %) = cuisine concentrée sur crémant (kir/coupes,
  +175/+189 bt) et vin jaune (sauce morilles, +86/+101 bt) + ~12 % de ventes sous boutons
  génériques (verre/pichet) déjà encaissées. Hors cuisine et sous-attribution → ≈ 0 inexpliqué.
- **Spiritueux** (Q) : Absinthe se referme à la crème brûlée près ; Soho, Cassis, Pastis, Martini,
  Get, Marc se referment à la bouteille ; Calvados/Macvin/Porto ont un vendu-caisse aberrant
  (encaissé sous cocktail/kir/menu). Résiduel ~729 bt → sous-attribution boutons + doses.
- **Coca/sodas** (R) : l'inventaire CONFIRME le trou (stock plat 92→116→118) sans le refermer.
  Conso hors-vente (personnel/famille/offerts) **à documenter par attestation** ; non frauduleux
  car 98,7 % du CA est bancarisé (aucun canal espèces).

## 6. Conclusion

L'inventaire démontre **(a)** zéro bouteille planquée (stock plat), **(b)** que le fisc a gonflé
ses « disparus » par un stock faux (+1 892 € en 2023-2024) et des confusions de code, **(c)** que
son motif de rejet (« inventaire incomplet ») tombe. Il **ne convertit pas en zéro** la consommation
non sonnée (~1 200 bt alcool + ~1 555 Coca/an), qui reste expliquée par les canaux légitimes
(cuisine + offerts + personnel/famille + sur-versement) et adossée à la bancarisation 98,7 %.
Le point faible documentaire restant = les sodas (attestation gérante à obtenir).
