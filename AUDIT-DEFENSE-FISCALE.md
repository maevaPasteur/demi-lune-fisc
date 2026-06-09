# Audit de défense fiscale — La Demi-Lune

Synthèse des arguments chiffrés contre la thèse de dissimulation de recettes.

> Méthode : 23 agents d'analyse parallèles sur les exports certifiés de la caisse (annexes A–H + export brut), chaque chiffre « fort » **recalculé indépendamment** (vérification adversariale) et réconcilié avec les totaux internes des fichiers. Montants TTC.


## 1. Arguments confirmés, classés par force

### 1. Reconstitution exhaustive ticket-par-ticket de la caisse certifiée NF525 = CA déclaré (aucune place pour des recettes occultes)
- **Force** : forte · **Vérification** : confirme
- **Chiffres clés** : CA reconstitué cumulé sur 3 exercices : par les en-têtes de tickets (Annexe H) = 1 277 216,50 € ; par le détail dédupliqué par identifiant de ticket (Annexe C, clé Id) = 1 277 216,50 € (identique au centime) ; par prix×quantité ligne-à-ligne (Annexe B) = 1 276 191,20 €. CA TTC déclaré (Annexe A) = 1 275 978,87 €. Écart net H vs déclaré = +1 237,63 € (+0,097 %). La caisse certifiée totalise donc LÉGÈREMENT PLUS que le CA déclaré — l'inverse exact d'une dissimulation. Par exercice (H) : 403 370,42 / 438 281,12 / 435 564,96 €.
- **Sources** : ANNEXE-H1/H2/H3 (liste-tickets), ANNEXE-C1/C2/C3 (détail-tickets, clé Id col.8), ANNEXE-B1/B2/B3 (prix-vente-quantité), ANNEXE-A1/A2/A3 (CA déclaré).

### 2. Continuité parfaite de la numérotation certifiée : aucune journée ni aucun ticket ni aucun événement supprimé
- **Force** : forte · **Vérification** : confirme
- **Chiffres clés** : 659 rapports Z consécutifs sans aucun trou (2022-2023 : Z 2938→3158 = 221 ; 2023-2024 : Z 3159→3378 = 220 ; 2024-2025 : Z 3379→3596 = 218), chaîne continue MÊME entre exercices (3158→3159, 3378→3379). 0 trou dans la numérotation des tickets à l'intérieur de chacun des 659 Z (séquence 1..N complète). 0 trou dans le compteur séquentiel d'événements de la caisse (Annexe E, champ id : 36681→60019 = 23 339 événements consécutifs, 0 manquant). Triple concordance E/H/C sur les bornes de Z.
- **Sources** : ANNEXE-E1/E2/E3 (tpvevenement, no_zEport + id), ANNEXE-H1/H2/H3 (no_z_report + no_ticket), ANNEXE-C1/C2/C3 (No_z).

### 3. Chiffre d'affaires quasi intégralement bancarisé : la part d'espèces (seul canal dissimulable) est dérisoire
- **Force** : forte · **Vérification** : confirme
- **Chiffres clés** : Sur les règlements certifiés (Annexe F), cumul 3 exercices : Carte Bancaire = 1 165 933,41 € soit 91,22 % ; Espèces = 17 333,18 € soit 1,356 % du total ; 98,64 % du CA est encaissé par moyens traçables (CB + titres-restaurant + chèques-vacances + chèques). Aucun règlement espèces > 236,60 € sur 3 ans (médiane 8,60 €). Pour dissimuler ne serait-ce que 100 000 € en liquide, il aurait fallu un volume d'espèces ~6 fois supérieur au total réellement encaissé.
- **Sources** : ANNEXE-F1/F2/F3 (règlements par mode), SOURCE-reglement-brut_2022-2025.xls, ANNEXE-A (espèces déclarées).

### 4. La caisse ne facture JAMAIS au-dessus du tarif catalogue : aucun mécanisme de recette ajoutée
- **Force** : forte · **Vérification** : confirme
- **Chiffres clés** : Sur ~97 700 lignes de vente (33 220 + 32 745 + 31 729), nombre de lignes où le montant facturé dépasse le tarif théorique (prix×quantité) : 0 en 2022-2023, 0 en 2023-2024, 0 en 2024-2025. 100 % des écarts non nuls sont des réductions consenties (menus à prix forfaitaire, partages de table), totalisant ~17 562 / 20 011 / 20 116 € soit ~4,3-4,6 % du CA — qui DIMINUENT le CA, ne le gonflent jamais. ~93 % des lignes ont un écart strictement nul.
- **Sources** : ANNEXE-B1/B2/B3 (test Total_TTC > Prix×Qté).

### 5. Intégrité interne totale de la caisse certifiée : réconciliations à 0,00 € sur toutes les sources
- **Force** : forte · **Vérification** : confirme
- **Chiffres clés** : Réconciliation interne de CHAQUE export = ses propres pieds de page, écart 0,00 € : Annexe A (somme TVA-TTC = somme par mode d'encaissement = somme familles = CA déclaré), Annexe H, Annexe B, Annexe C, Annexe F (par mode ET total général), Annexe G. Journal de TVA (Annexe G) : cumul progressif strictement monotone (0 décrément réel), chaîne 'À NOUVEAUX' inter-exercices exacte au centime (clôture G1 = ouverture G2 = 1 381 110,20 € ; clôture G2 = ouverture G3 = 1 819 103,12 €). TVA collectée cumulée = 134 879,47 € (validée par triple recoupement). Un CA réellement minoré laisserait des écarts entre ces blocs indépendants.
- **Sources** : ANNEXE-A1/A2/A3, ANNEXE-G1/G2/G3 (journal-tva), ANNEXE-H/B/C/F.

### 6. Concordance ticket-à-ticket (et non seulement des totaux) entre exports certifiés
- **Force** : forte · **Vérification** : confirme
- **Chiffres clés** : 2022-2023 : 5 660 tickets appariés par identifiant entre Annexe H et Annexe C, 5 660/5 660 avec un tot_ttc strictement identique (écart absolu maximum = 0,0000 €). Les seuls tickets non appariés (présents dans H uniquement) valent TOUS 0,00 € (tickets d'ouverture/vides), somme nulle. Aucun ticket 'fantôme' porteur de recette.
- **Sources** : ANNEXE-H1 vs ANNEXE-C1 (jointure par id de ticket).

### 7. Volume des DEL en BAISSE tandis que le CA croît, et profil de micro-corrections incompatible avec une fraude
- **Force** : forte · **Vérification** : confirme
- **Chiffres clés** : Nombre de DEL : 8 014 (2022-2023) → 6 943 (2023-2024) → 6 345 (2024-2025), soit -21 % de lignes, pendant que le CA progresse de +7 % (409 020,76 → 437 753,60 €). Médiane d'une DEL ~8-9 € (prix d'une crêpe/boisson) ; ~57-59 % des DEL ≤ 10 € ; 84-88 % des DEL surviennent en rafales à la même minute sur le même Z (corrections groupées) ; 92-95 % pendant les services, 0 la nuit. Une dissimulation croîtrait avec l'activité : c'est l'inverse qui est observé.
- **Sources** : ANNEXE-E1/E2/E3 (tpvevenement, typEven='DEL', horodatage, groupage).

### 8. Ventilation TVA et mix produits stables, cohérents avec une crêperie ~30 couverts (pas de manipulation sélective)
- **Force** : moyenne · **Vérification** : confirme
- **Chiffres clés** : Part TTC au taux 10 % (restauration sur place) stable : 80,50 % / 80,29 % / 80,51 % (cumul 80,44 %). Ratio CA solide/liquide = 2,94 / 3,02 / 3,11, recoupant le coefficient interne calculé par la caisse elle-même (2,936). Quantités de boissons (canal le plus difficile à dissimuler) quasi plates : 16 543,5 / 16 451,8 / 15 930,5 unités (-3,7 % max). Ticket moyen régulier et haussier (~71-80 €). Une minoration sélective déséquilibrerait ces ratios.
- **Sources** : ANNEXE-A (ventilation TVA), ANNEXE-D1/D2/D3 (synthèse-produit, sections LIQUIDE/SOLIDE), ANNEXE-C (panier moyen).

## 2. Réconciliations inter-annexes (tous les exports convergent vers le même CA)

- 2022-2023 : convergence des QUATRE exports certifiés au centime près : Annexe H = Annexe C (dédup par Id) = Annexe B = Annexe G = 403 370,42 € (4 sources indépendantes identiques).
- 2023-2024 : Annexe H = Annexe C = 438 281,12 € d'un côté ; Annexe B = Annexe G = 437 992,92 € de l'autre. Écart entre les deux groupes = 288,20 € (0,066 %), au niveau ligne-produit (regroupements de libellés), NON du CA caché.
- 2024-2025 : Annexe H = Annexe C = 435 564,96 € ; Annexe B = Annexe G = 434 827,86 €. Écart = 737,10 € (0,17 %), même origine d'agrégation ligne-produit.
- Cumul 3 exercices : Annexe H = Annexe C (clé Id) = 1 277 216,50 € ; Annexe B = Annexe G = 1 276 191,20 € ; SOURCE-reglement-brut (etat=0) = 1 276 191,20 € ; CA déclaré Annexe A = 1 275 978,87 €. Tous les exports convergent dans une fourchette de +0,017 % à +0,097 % au-dessus du CA déclaré.
- Annexe F (règlements) vs SOURCE-reglement-brut : réconciliation à 0,00 € par exercice ET par mode de paiement (TOTAL GENERAL F = somme ligne-à-ligne du fichier brut : 403 402,87 / 439 600,30 / 435 146,29 €).
- Chaîne 'À NOUVEAUX' du journal de TVA (Annexe G) : clôture cumulée d'un exercice = ouverture de l'exercice suivant, au centime (1 381 110,20 € puis 1 819 103,12 € en TTC, idem en TVA) — continuité comptable parfaite, aucune insertion/suppression possible entre exercices.
- Espèces : Annexe F = 17 333,18 € vs Annexe A déclaré = 17 042,16 € (écart +291,02 € / +1,7 %, la caisse enregistre LÉGÈREMENT PLUS que le déclaré).

## 3. Signaux anti-occultation

- Continuité 100 % des rapports Z : 659 Z consécutifs (2938→3596), 0 trou, chaînés sans rupture entre les 3 exercices — aucune journée de caisse supprimée, pas de caisse parallèle.
- Continuité 100 % du compteur d'événements (Annexe E, champ id) : 23 339 événements consécutifs (36681→60019), 0 manquant — chaque opération, y compris chaque suppression de ligne (DEL), est journalisée et conservée, jamais effacée de la base.
- Continuité intra-Z : séquence de tickets 1..N complète dans chacun des 659 Z, 0 trou — aucun ticket validé soustrait.
- Part d'espèces dérisoire : 1,356 % du CA (17 333,18 € sur 3 ans) ; 91,22 % en CB traçable et rapprochable des relevés bancaires ; aucun règlement espèces > 236,60 €, médiane 8,60 €.
- Cumul progressif du journal de TVA (Annexe G) strictement monotone : 0 décrément réel sur les valeurs uniques — il est mathématiquement impossible d'avoir retiré une recette du flux sans créer une discontinuité, qui n'existe pas.
- Reconstitution directe (Annexe B) : 0 ligne facturée au-dessus du tarif catalogue sur ~97 700 lignes ; la caisse n'a aucun mécanisme produisant de la recette ajoutée.
- Sens de l'écart favorable : sur 3 ans, la caisse certifiée totalise +1 237,63 € de PLUS que le CA déclaré (et +212,33 € en reconstitution B/G) ; les écarts annuels sont de signes ALTERNÉS (-, +, -), signature d'un simple décalage de césure d'exercice (tickets à cheval sur le 31/03-01/04), non d'une minoration systématique (qui irait toujours dans le même sens).
- Annexe A (caisse certifiée) chiffre elle-même : Remboursements = 0 et Tickets annulés = 0 sur chacun des 3 exercices.
- Caissier unique 'LUNA' à 100 % des 19 903 tickets : aucune session/compte parallèle non identifié.

## 4. ⚠️ Chiffres à NE PAS utiliser tels quels (interceptés par la vérification)

- DEL = 1 047,60 € / 67 lignes sur 3 ans (ligne 'Lignes supprimées' de l'Annexe A) : NE PAS présenter comme le 'total des DEL'. Le journal d'événements certifié NF525 (Annexe E, typEven='DEL') enregistre un volume brut de DEL de 193 005,09 + 140 686,55 + 97 071,51 = 430 763,15 € sur 21 302 événements (réconcilié au centime avec les pieds de page de E). C'est 411× le chiffre de l'Annexe A, et c'est précisément la base des 'centaines de milliers d'euros' invoquée par l'administration. La ligne 'Lignes supprimées' de A est une métrique étroite/résiduelle (probablement DEL nettes sur tickets finalisés) à requalifier comme telle, jamais comme volume total des suppressions. Citer 1 047,60 € comme 'total DEL' ferait s'effondrer la défense à la première contradiction sur l'Annexe E.
- 'HT+TVA=TTC à 0,00 sur chaque ligne chaque année' (Annexe A) : INEXACT. La ligne TVA 20 % de 2024-2025 porte un arrondi interne de 0,01 € (85 294,12 calculé vs 85 294,11 au fichier). Négligeable mais à nuancer pour un usage juridique.
- Réconciliation #2 du lot G ('delta-cumul = cellule Différence du pied de page, gap 0,00') : INFIRMÉE. Écart réel de +45,70 / +111,80 / +118,60 € (TTC) entre le delta du cumul et la cellule 'Différence' imprimée. Formuler le CA fiable comme delta-cumul = somme des lignes = somme des colonnes de taux, sans invoquer la cellule 'Différence'.
- Égalité 'Annexe F = Annexe A à l'identique' (piste croisée #1 du lot A) : INFIRMÉE. F (règlements) ≠ A (CA) : totaux F = 403 402,87 / 439 600,30 / 435 146,29 € vs CA-A, écarts -5 618 / +10 396 / -2 607 € (bidirectionnels) ; espèces F plus élevées que A. F est un périmètre 'règlements' distinct du périmètre 'CA' — à expliquer (pourboires CB, multi-règlements, césure), PAS à présenter comme une concordance au centime.
- L'écart quasi-nul reconstitution/déclaré (+0,017 % en B/G ; +0,097 % en H) ne vaut QU'AU CUMUL TRIENNAL. Par exercice les écarts sont réels et de plusieurs milliers d'euros (H vs CA : -5 650 / +9 077 / -2 189 €). Ne JAMAIS présenter le quasi-zéro comme valable année par année (l'administration exploiterait le +9 077 € de 2023-2024) : le présenter explicitement comme résultat cumulé sur 3 ans, dû à la césure des journées de bordure.
- Sous-total 'CA SOLIDES 10 %' du pied de page de l'Annexe D1 : bug d'export de -198,00 € (et -18 € sur la TVA 10 % affichée), sans impact sur le TOTAL GENERAL. À mentionner comme lapsus de l'export certifié de l'administration (qui SOUS-estime, non surestime), pas comme une anomalie du contribuable.
- 'Lignes supprimées' = mêmes 'DEL' que celles visées par l'administration : à confirmer formellement via la documentation éditeur de la caisse (sémantique de etat=9 et du mécanisme DEL) avant tout usage.

## 5. Axes d'attaque recommandés

1. NE JAMAIS minimiser le volume des DEL à 1 047,60 € : assumer frontalement le volume brut certifié de 430 763,15 € (Annexe E) et le NEUTRALISER par sa nature. Démonstration : (a) une DEL n'est pas du CA — c'est une correction de saisie, un transfert de plats vers un autre ticket, ou une refacturation en menu, déjà inclus dans le CA déclaré ; (b) 32 % du volume brut (138 003 €) tient à seulement 4 lignes techniques aberrantes (jusqu'à 68 993 € = 42,3 jours de recette moyenne, matériellement impossibles à assimiler à des ventes) ; (c) DEL nettes ~292 760 € à profil de micro-corrections (médiane 8-9 €, rafales à la même minute, 0 la nuit). Surtout : la convergence parfaite des exports vers le CA déclaré ne laisse arithmétiquement AUCUNE place à 430 k€ de recettes cachées.
2. Opposer la reconstitution directe exhaustive (Annexe B/C/H = CA déclaré à 0,017-0,097 % près sur 1,276 M€ et ~98 000 lignes) à toute 'reconstitution' extrapolée de l'administration. Une reconstitution par coefficients (marge, ratio matières, boissons) est démentie par les données certifiées elles-mêmes ; exiger que l'administration confronte sa méthode au ticket moyen réel (71-80 €), au nombre de tickets réels (5 660/5 534/5 430) et aux quantités de boissons stables (Annexe D).
3. Faire de la continuité NF525 le socle d'intégrité : 659 Z sans trou, 23 339 événements sans trou, chaîne 'À NOUVEAUX' exacte entre exercices, cumul de TVA strictement monotone. Argumenter qu'une suppression de recettes briserait nécessairement ces compteurs inaltérables ; demander à l'administration d'identifier la moindre discontinuité (il n'y en a aucune).
4. Démontrer l'impossibilité matérielle d'une occultation en espèces : 91,22 % du CA en CB (1 165 933 €) intégralement rapprochable des remises en banque, espèces à 1,356 % (17 333 €), aucun règlement espèces > 236,60 €. Produire les relevés bancaires et les remboursements des émetteurs (Edenred/ANCV pour TR+CHV ≈ 81 k€) comme preuves tierces indépendantes de l'exhaustivité.
5. Sécuriser chaque chiffre avant dépôt en corrigeant les formulations infirmées : présenter le quasi-zéro de reconstitution comme CUMULÉ (jamais annuel) ; ne pas présenter Annexe F comme égale à Annexe A (périmètres règlements vs CA) ; abandonner la réconciliation à la cellule 'Différence' du journal G ; nuancer le 'HT+TVA=TTC à 0,00 chaque ligne'. Toute imprécision opposable doit être retirée pour préserver la crédibilité de l'ensemble.
6. Demander formellement à l'administration la documentation éditeur de la caisse certifiée définissant la sémantique exacte des DEL et de etat=9, et exiger qu'elle trace, pour un échantillon de DEL, le ticket de refacturation correspondant — afin de matérialiser item par item qu'aucun montant n'échappe au CA et de renverser la charge de la démonstration.
