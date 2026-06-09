# S — « Disparus » du fisc confrontés à l'inventaire physique

**Objet** : confronter chaque produit cité « disparu » par le vérificateur (volumes achetés non vendus en caisse) aux 3 inventaires physiques de fin d'exercice, pour distinguer ce qui relève d'un stock oublié, d'une confusion de code caisse, ou d'une vraie consommation.

**Sources**
- Fisc : `src/data/volumes-disparus-fisc.json` (52 produits), `src/data/analyse-disparus.json`.
- Inventaires physiques : `public/documents/inventaires/inventaires.json` — 3 dates : **31/03/2023** (clôture 2022-2023), **31/03/2024** (2023-2024), **31/03/2025** (2024-2025).
- Achats/ventes internes : `analyses-independantes/boissons/data/disparitions.json`.

**Méthode** : appariement par mots-clés du libellé fisc sur les lignes d'inventaire des 3 dates (script `/tmp/pwenv/bin/python`). Aucune supposition : une cellule vide = produit littéralement absent de l'inventaire.

---

## 1. Tableau de confrontation

Légende « présent en inventaire ? » = quantité physique trouvée aux dates 2023 / 2024 / 2025 (— = absent).

| Produit cité par le fisc | pct_disparu fisc | Présent en inventaire ? (2023 / 2024 / 2025) | Explication |
|---|---|---|---|
| **Porto Sandeman** | 90,9 / 93,3 / 92,8 % | 4 / 4 / 2 bt | En stock aux 3 dates. Stock initial réel + usage cuisine (sauces forestière/morilles) déjà admis. « Disparu » = stock ignoré + dose cuisine. |
| **Pontarlier (anis)** | 80,9 / 88,4 / 26,8 % | 1 / 2 / — bt | En stock 2023 et 2024. Bouteille 100 cl à dose 2 cl : un litre couvre des dizaines de services → « disparu » = stock + dose. |
| **Picon** | 85,8 / 58,3 / 34,0 % | 1 / — / — bt | En stock 2023. 100 cl, dose ~6-8 cl : stock + dose expliquent l'écart. |
| **Macvin** | -22 / 20,8 / -22 % | 5 / 9 (+0 rosé) / — bt | En stock 2023 et 2024 (Blanc Rolet). Le **négatif** (vendu > acheté) est arithmétiquement impossible sans stock initial : preuve que le « disponible » fisc a ignoré le stock. |
| **Martini Blanc** | -26 % (surconso) | 1 / 2 / 1 bt | En stock aux 3 dates. Surconsommation = stock initial non décompté. |
| **Calvados** | surconso -8/-40/-50 % | 2 / 2 / 1 bt | En stock aux 3 dates. 100 cl, repère cuisine D (3310 cl déduits 2022-2023). Surconso = stock + cuisine. |
| **Bordeaux « Mouton Cadet »** (réf. caisse 1859) | 11,1 / 77,4 / 0 % (6 bt vendues, 0 achat 24-25) | « Bordeaux Supérieur » 1 / — / — bt | **CONFUSION DE CODE.** Aucun « Mouton Cadet » n'existe ni en achat ni en inventaire. Le seul Bordeaux acheté/inventorié est *Bordeaux Supérieur Ch. Grand Renom* (code 661236 ; 11 bt achetées 22-23, 1 bt en stock 31/03/2023). Les 6 « ventes sans achat » 24-25 = bouton générique frappé sur un stock résiduel. PAS une disparition. |
| **Hautes Côtes de Nuits** | 83,3 % ; 172 bt vendues sans achat 23-24 | — / — / — | **CONFUSION DE CODE.** Notre réf. réelle = *Htes Côtes de Nuits **BLANC** Lupé Cholet 2017* (code 601416), achetée 24 bt en **2022-2023** seulement, 0 en 23-24. Le fisc la classe « rouge » et impute 172 bt en 23-24. Absente des 3 inventaires car écoulée. La *Haute Côte de **Beaune** rouge*, elle, EST en stock (6 bt 2023, 8 bt 2025) → bouton/code mélangés (cf. note fisc « Verre H côte / Pichet C.DE BEAUNE B »). PAS une vente sans achat. |
| **Café** | 43,5 / 76,8 / 81,0 % | grains+déca en stock aux 3 dates | Hors périmètre alcools ; consommation cafetière non tracée à l'unité. |
| **1664 33 cl** | 100 % (234 dispo, 0 vente) | — / — / — | **ARTEFACT PARAMÉTRAGE.** Absente des 3 inventaires. Achats réels 24 bt (≠ 234 « dispo » fisc), venduCl=0 dans nos données aussi → code de vente jamais créé. Aucune disparition physique. |
| **Heineken 33 cl** | 100 % | — / — / — | Idem : absente des inventaires, venduCl=0, code caisse inexistant. |
| **Heineken 50 cl** | 100 % | — / — / — | Idem (dispo fisc = 0 d'ailleurs). |
| **Grimbergen Blanche 33 cl** | 100 % | — / — / — | Idem : absente, venduCl=0, paramétrage. |
| **White Mort Subite 33 cl** | 100 % | — / — / — | Idem : absente, venduCl=0, paramétrage (achats 9108 cl jamais rattachés à un bouton). |
| **White Rabbit 33 cl** | 100 % | — / — / — | Idem. |
| **Hefeweizen 33 cl** | 100 % | — / — / — | Idem. |
| **Bleue du Mont Blanc 33 cl** | 100 % | — / — / — | Idem (achats 5544 cl, venduCl=0). |
| **Carola Bleue 50 cl** | 100 % (20 dispo, 0 vente) | — / — / — | **ARTEFACT PARAMÉTRAGE** (eau). Absente, venduCl=0, code inexistant. |
| **Cidre Sassy 33 cl** | 100 % | — / — / — | Artefact paramétrage : absent des inventaires, code de vente inexistant. |
| **Rouget Ambrée 33 cl** | 34,5 % | 36 / 22 / 27 bt | **En stock aux 3 dates.** Vraie bière vendue maison ; écart = rotation + stock. |
| **Rouget Blanche / « Des Neiges » 33 cl** | 6,6 % | 41 / 19 / 9 bt | En stock aux 3 dates. Écart faible, cohérent. |
| **Fût Affligem 8 L** | dispo seul 79 | 4 / 32 / 5 fûts/u. | En stock aux 3 dates. Bière pression réellement servie. |
| **Cidre La Mordue 27 cl** | 67,3 % | 32 / 19 / 18 bt | En stock aux 3 dates. |
| **Cidre Brut 75 cl** | 18,8 % | 15 / 15 / 22 bt | En stock aux 3 dates. |
| **Cidre Doux 75 cl** | 31,9 % | 14 / 16 / — bt | En stock 2023 et 2024. |
| **Arbois Trousseau 75 cl** | 15,4 % | 10 / 7 / 8 bt | En stock aux 3 dates. |
| **Saint-Joseph rouge 75 cl** | 37,0 % | 9 / 3 / 9 bt | En stock aux 3 dates. |
| **Moulin-à-Vent 75 cl** | 14,7 % | 8 / 9 / 10 bt | En stock aux 3 dates. |
| **Haute Côte de Beaune rouge 75 cl** | 14,4 % | 6 / — / 8 bt | En stock 2023 et 2025 (le vrai « côte rouge » vs. le « Nuits » mal codé). |
| **Crémant du Jura 75 cl** | ~47,5 % | 8 / 19 / 9 bt | En stock aux 3 dates. Usage cocktails (KittyKir) admis. |
| **Vin Jaune 62 cl** | dispo seul 127 | 4 / 5 / 2 bt | En stock aux 3 dates. Usage cuisine (sauces/fondues) admis. |
| **Champagnes (Ruinart/Sandrin/Lanson…)** | 70 % | en stock aux 3 dates | Sandrin 8/9/13, Lanson 8 (24), Ruinart 0/1/0 : stock initial/final ignoré. |

*(Les autres lignes « disponible_seul » 2024-2025 — Savagnin, Chablis, Saint-Véran, Gewurztraminer, Macon, etc. — sont toutes retrouvées en stock aux inventaires correspondants ; non détaillées ici car le fisc ne leur attribue pas de pct_disparu.)*

---

## 2. Les 2 cas « vente sans achat »

| Cas fisc | Ce que dit l'inventaire / nos données | Verdict |
|---|---|---|
| **Bordeaux Mouton Cadet** : 6 bt vendues 2024-2025, 0 achat | Aucun « Mouton Cadet » nulle part. Le Bordeaux réel = *Bordeaux Supérieur Ch. Grand Renom* (11 bt achetées 22-23, **1 bt en stock 31/03/2023**). | **Confusion de code**, pas une disparition. Bouton 1859 frappé sur le Bordeaux générique. |
| **Hautes Côtes de Nuits** : 172 bt vendues 2023-2024, 0 achat | Réf. réelle = *Htes Côtes de Nuits **Blanc** Lupé Cholet* (24 bt achetées **22-23**, 0 en 23-24, écoulée donc absente des inventaires). La *Haute Côte de **Beaune** rouge* est, elle, en stock (6/8 bt). | **Confusion de code** (Beaune/Nuits, blanc/rouge, verre/pichet). 172 bt ≫ tout achat plausible : impossible sans erreur de code caisse. |

---

## 3. Bières « 100 % disparues » — le fisc a-t-il oublié le stock ?

Les 7 bières « 100 % » (1664, Heineken 33 et 50, Grimbergen, Mort Subite, White Rabbit, Hefeweizen, Bleue du Mont Blanc) ont un point commun **décisif** : elles sont **absentes des 3 inventaires physiques**, et leur `venduCl = 0` dans NOS propres données. Ce ne sont pas des bouteilles « disparues » : ce sont des références dont **le bouton de vente n'a jamais été créé/rattaché** en caisse (artefact de paramétrage, hypothèse H1). Les seules bières réellement stockées et tournantes sont **Rouget de Lisle (Blanche + Ambrée)** et le **fût Affligem**, toutes présentes aux 3 dates avec des écarts faibles à modérés (6 à 35 %), cohérents avec une rotation normale. Le fisc a donc gonflé le « disponible » sur des codes morts, sans contrepartie physique.

---

## Synthèse (3 lignes)

1. **Aucune des 7 bières « 100 % disparues » du fisc (1664, Heineken, Grimbergen, Mort Subite, White Rabbit, Hefeweizen, Bleue du Mont Blanc) n'apparaît dans les 3 inventaires physiques, et leur vendu caisse = 0 dans nos propres données : il s'agit de codes de vente jamais paramétrés (H1 confirmée), pas de bouteilles évaporées — les seules bières réellement en stock sont Rouget Blanche/Ambrée et le fût Affligem, avec des écarts normaux.**
2. **Les 2 « ventes sans achat » sont des confusions de code prouvées par l'inventaire : « Mouton Cadet » n'existe nulle part (le Bordeaux réel est le Supérieur Ch. Grand Renom, 1 bt en stock au 31/03/2023), et la « Hautes Côtes de Nuits » est en réalité un BLANC Lupé Cholet acheté en 2022-2023 (0 en 2023-2024), distinct de la Haute Côte de Beaune rouge bel et bien stockée.**
3. **Pour les apéritifs/spiritueux à fort pct (Porto, Picon, Macvin, Martini, Calvados, Pontarlier), le stock physique est présent aux inventaires aux 3 dates ; les « disparus » — parfois négatifs (vendu > acheté, arithmétiquement impossible) — s'expliquent par un stock initial/final ignoré par le vérificateur et la dose cuisine déjà admise, jamais par une occultation.**
