# 8. Cartographie des annexes A à H

> Source : Annexes A–H (52 pages scannées). Données détaillées disponibles proprement dans les fichiers .xls du dossier documents.

## Avertissement de lecture

Le PDF OCR (`Proposition_2_Annexes_A-H.txt`, 2 707 lignes / 52 pages) est composé presque exclusivement de **tableaux scannés**, dont une grande partie a été océrisée à l'envers ou en colonnes désalignées. Le découpage réel observé dans l'OCR est le suivant :

- **Pages 1–3** : tableaux de synthèse Annexes A / B / C (par exercice : -V/2022-2023, CA/2023-2024, etc.) — **fortement dégradés / illisibles**.
- **Page 4** : totaux « ANNEXE C » (CA liquides/solides + TVA théorique) — partiellement lisible.
- **Pages 5–8** : tableaux par **modes de règlement** (CB, ESP, CHQ, TR…) — partiellement lisibles.
- **Pages 10–46** : Annexes **D-1 / D-2 / D-3** (détail produit par exercice 2022-2023, 2023-2024, 2024-2025) — **lisibles**, avec totaux en fin de chaque sous-annexe.
- **Pages 47–50** : « ANNEXE N°1 » = tableau **volumes / stocks** par article (4 dates d'inventaire) — lisible.
- **Pages 51–52** : « ANNEXE N°2 » = quasi vide à l'OCR.

Le PDF ne porte donc pas d'étiquettes explicites « E / F / G / H ». La correspondance ci-dessous s'appuie sur la **nomenclature des fichiers .xls propres** déjà présents dans `public/documents/` (chaque annexe existe en 3 versions : suffixe `1` = 2022-2023, `2` = 2023-2024, `3` = 2024-2025).

---

## Annexe A — Synthèse du chiffre d'affaires par exercice

- **Objet** : synthèse du CA reconstitué, ventilé par exercice.
- **Période** : 3 exercices (A-1 : 2022-2023 ; A-2 : 2023-2024 ; A-3 : 2024-2025).
- **OCR** : pages 1–3, **fortement dégradé** (texte renversé, colonnes illisibles). Quelques montants isolés apparaissent mais ne sont pas fiables.
- **Données propres** : `ANNEXE-A1_synthese-CA_2022-2023.xls`, `ANNEXE-A2_synthese-CA_2023-2024.xls`, `ANNEXE-A3_synthese-CA_2024-2025.xls`.
- **Chiffres-clés** : non récupérables de façon fiable depuis l'OCR — se reporter aux .xls.

## Annexe B — Prix de vente et quantités (par article)

- **Objet** : tableau prix de vente / quantités vendues par article.
- **Période** : 3 exercices (B-1 / B-2 / B-3).
- **OCR** : pages 1–3, **fortement dégradé** (mêmes tableaux renversés que l'annexe A).
- **Données propres** : `ANNEXE-B1_prix-vente-quantite_2022-2023.xls`, `ANNEXE-B2_...2023-2024.xls`, `ANNEXE-B3_...2024-2025.xls` (gros fichiers, ~7,4 à 7,8 Mo chacun).
- **Chiffres-clés** : non lisibles depuis l'OCR — se reporter aux .xls.

## Annexe C — Détail des tickets

- **Objet** : détail des tickets (lignes de vente).
- **Période** : 3 exercices (C-1 / C-2 / C-3).
- **OCR** : pages 3–4, **fortement dégradé**. La page 4 contient un bloc de **totaux « ANNEXE C »** partiellement lisible, structuré comme les totaux des annexes D (TTC CA liquides 10 %, liquides 20 %, solides 10 %, total général, TVA théorique 10 % et 20 %). Les valeurs y sont toutefois trop bruitées pour être reprises sans risque (ex. lignes « TOTAL TTC CA LIQUIDES », « TOTAL GENERAL TTC », « TOTAL TVA THEORIQUE SUR DONNEES ARTICLES 10/20 % » visibles mais montants illisibles « (?) »).
- **Données propres** : `ANNEXE-C1_detail-tickets_2022-2023.xls`, `ANNEXE-C2_...2023-2024.xls`, `ANNEXE-C3_...2024-2025.xls` (très volumineux, ~13,4 à 14 Mo chacun).
- **Chiffres-clés** : à reprendre depuis les .xls.

## Annexe D — Synthèse par produit (prix unitaire, quantité, total TTC)

- **Objet** : synthèse par produit avec, pour chaque référence, `Ref_prd`, `Lib_ticket`, prix unitaire (`Uprice_wt`), prix moyen, quantité (`Qte`) et total TTC (`Tot_rem Tte`). Articles ventilés en LIQUIDE TVA 10 %, LIQUIDE TVA 20 %, SOLIDE TVA 10 %.
- **Période** : 3 exercices.
  - **D-1 = 2022-2023** (pages 11–19)
  - **D-2 = 2023-2024** (pages 23–33)
  - **D-3 = 2024-2025** (pages 37–45)
- **OCR** : **lisible** (c'est la partie la plus exploitable du document). Les lignes de détail produit sont globalement déchiffrables ; quelques totaux de lignes individuelles restent bruités.
- **Données propres** : `ANNEXE-D1_synthese-produit_2022-2023.xls`, `ANNEXE-D2_...2023-2024.xls`, `ANNEXE-D3_...2024-2025.xls`.
- **Totaux et chiffres-clés lisibles (bas de chaque sous-annexe)** :

  **D-1 (2022-2023)** — page 19 :
  - TOTAL TTC CA LIQUIDES 10 % : 20 514,18 €
  - TOTAL TTC CA LIQUIDES 20 % : 81 911,20 €
  - TOTAL TTC CA SOLIDES 10 % : 300 747,04 €
  - TOTAL GÉNÉRAL TTC : 403 370,42 €
  - TOTAL TVA THÉORIQUE SUR DONNÉES ARTICLES 10 % : 29 205,57 €
  - TOTAL TVA THÉORIQUE SUR DONNÉES ARTICLES 20 % : 13 651,87 €
  - Rapport pour 1 € de CA liquide = 2,94 € de CA solide (?)

  **D-2 (2023-2024)** — page 33 :
  - TOTAL TTC CA LIQUIDES 10 % : 20 010,27 €
  - TOTAL TTC CA LIQUIDES 20 % : 88 909,01 €
  - TOTAL TTC CA SOLIDES 10 % : 329 361,84 €
  - TOTAL GÉNÉRAL TTC : 438 281,12 €
  - TOTAL TVA THÉORIQUE SUR DONNÉES ARTICLES 10 % : 31 761,10 €
  - TOTAL TVA THÉORIQUE SUR DONNÉES ARTICLES 20 % : 14 818,17 € (OCR « 29 % » sur l'intitulé, manifestement « 20 % » (?))
  - Rapport pour 1 € de CA liquide = 3,02 € de CA solide (?)

  **D-3 (2024-2025)** — page 45 :
  - TOTAL TTC CA LIQUIDES 10 % : 19 723,21 €
  - TOTAL TTC CA LIQUIDES 20 % : 86 389,75 €
  - TOTAL TTC CA SOLIDES 10 % : 329 452,00 €
  - TOTAL GÉNÉRAL TTC : 435 564,96 €
  - TOTAL TVA THÉORIQUE SUR DONNÉES ARTICLES 10 % : 31 743,20 €
  - TOTAL TVA THÉORIQUE SUR DONNÉES ARTICLES 20 % : 14 398,29 €
  - Rapport pour 1 € de CA liquide = 3,10 € de CA solide (?)

## Annexe E — Fichier événement TPV (tpvevenement)

- **Objet** : fichier des événements de caisse (TPV) — inclut typiquement les ouvertures/clôtures et, selon l'intitulé du .xls, les **suppressions/annulations** d'opérations.
- **Période** : 3 exercices (E-1 / E-2 / E-3).
- **OCR** : **non identifiable de façon fiable** dans le texte océrisé (pas d'étiquette « E » ; vraisemblablement non reproduit ou fondu dans les pages mal scannées 1–9). À considérer comme **trop dégradé / absent** de l'OCR.
- **Données propres** : `ANNEXE-E1_tpvevenement_2022-2023.xls`, `ANNEXE-E2_...2023-2024.xls`, `ANNEXE-E3_...2024-2025.xls`.
- **Chiffres-clés** : à reprendre depuis les .xls.

## Annexe F — Fichier des règlements (modes de paiement)

- **Objet** : ventilation par **mode de règlement** (CB/CARTE, ESP/espèces, CHQ/chèque, TR/tickets restaurant, etc.), avec nombre de lignes et montants. Les pages 5–8 de l'OCR présentent des blocs « Nb lignes » par code de règlement (codes visibles : « DB », « ESP », « TR », « CON », « TX »…) puis des TOTAUX par mode (TOTAL CB, TOTAL CHQ, TOTAL ESP, TOTAL TR, TOTAL GÉNÉRAL).
- **Période** : 3 exercices (F-1 / F-2 / F-3).
- **OCR** : **partiellement lisible** (codes de règlement reconnaissables, mais montants et libellés fortement bruités). Quelques valeurs apparaissent (ex. page 5 : lignes « Nb lignes » avec nombres ~6 943 / ~8 014 (?) ; page 6 : blocs « TOTAL … » par mode dont un « TOTAL CB » de l'ordre de 39x xxx € et « TOTAL GÉNÉRAL » ~4xx xxx € (?)). **Aucun chiffre fiable** : tous marqués « (?) ».
- **Données propres** : `ANNEXE-F1_reglements_2022-2023.xls`, `ANNEXE-F2_...2023-2024.xls`, `ANNEXE-F3_...2024-2025.xls`, ainsi que la source brute `SOURCE-reglement-brut_2022-2025.xls`.
- **Chiffres-clés** : à reprendre exclusivement depuis les .xls (OCR non fiable).

## Annexe G — Journal de TVA

- **Objet** : journal de TVA (bases HT, TVA collectée, ventilation par taux 10 % / 20 %).
- **Période** : 3 exercices (G-1 / G-2 / G-3).
- **OCR** : **non identifiable de façon fiable** (pas d'étiquette « G » dans le texte ; probablement parmi les pages-tableaux renversées 1–9). À considérer comme **trop dégradé / absent** de l'OCR.
- **Données propres** : `ANNEXE-G1_journal-tva_2022-2023.xls`, `ANNEXE-G2_...2023-2024.xls`, `ANNEXE-G3_...2024-2025.xls`.
- **Chiffres-clés** : à reprendre depuis les .xls.

## Annexe H — Liste des tickets

- **Objet** : liste des tickets (en-tête de chaque ticket : n°, date, montant, mode de règlement). Les pages 7–8 de l'OCR comportent des fragments de tableaux à colonnes « jour / mois / année / n° ticket / caissier / règlement », cohérents avec une liste de tickets, mais l'attribution exacte à « H » plutôt qu'à « C/F » n'est pas certaine à l'OCR.
- **Période** : 3 exercices (H-1 / H-2 / H-3).
- **OCR** : **fortement dégradé** ; structure entrevue mais valeurs illisibles.
- **Données propres** : `ANNEXE-H1_liste-tickets_2022-2023.xls`, `ANNEXE-H2_...2023-2024.xls`, `ANNEXE-H3_...2024-2025.xls`.
- **Chiffres-clés** : à reprendre depuis les .xls.

---

## Éléments complémentaires repérés dans l'OCR (hors A–H)

- **« ANNEXE N°1 » (pages 47–50)** : tableau **volumes / stocks par article** (catégories BIÈRES, CIDRE, ALCOOLS FORTS, VINS, SODAS/EAU/SIROPS, CAFÉ…), avec volume unitaire en centilitres et stocks indiqués aux **4 dates d'inventaire 31/03/2022, 31/03/2023, 31/03/2024, 31/03/2025** (colonnes « Volume / Stocks / Indiqué Oui/Non »). Lisible.
  - Ligne **TOTAL** (page 50, bruitée) : 728 (?) / 825 (?) | 823 | 983 | 884 — valeurs à confirmer « (?) ».
- **« ANNEXE N°2 » (pages 51–52)** : intitulé présent mais **contenu vide à l'OCR** (seul un « 13 » résiduel apparaît).
