# Argumentaire juridique : les 430 763 € de lignes supprimées en caisse ne constituent pas des recettes dissimulées

Note de travail à l'attention de l'avocat fiscaliste
Affaire : SARL Demi Lune (restaurant, Jura) - contrôle fiscal, exercices 01/04/2022 au 31/03/2025
Objet : qualification des suppressions de lignes en caisse (événements DEL, journal certifié ANNEXE-E)

---

## 1. Résumé exécutif (la thèse)

Le service brandit 430 763 € de « lignes supprimées » en caisse (21 302 lignes sur 3 exercices, soit 34 % du CA déclaré) comme des ventes occultées. Cette qualification est erronée. Les suppressions sont un journal technique d'événements (corrections de saisie, ré-encaissements, agrégations de menus), distinct des tickets payés, jamais inclus dans aucun total de chiffre d'affaires. Trois exports certifiés indépendants convergent sur un CA de ~1,276 M€ sans jamais mobiliser ces suppressions ; sur 9 sessions de caisse, le montant supprimé dépasse le CA réellement encaissé du jour, ce qui est arithmétiquement impossible pour de vraies ventes ; et le CA déclaré égale les encaissements au centime, eux-mêmes bancarisés à 98,7 %. Le test légal pertinent n'est pas la traçabilité par article (rendue impossible par les mécanismes légitimes eux-mêmes), mais l'exhaustivité de la recette : argent reçu = argent déclaré = argent bancarisé. Cette égalité est vérifiée.

---

## 2. Le grief du service

Le service constate, dans le journal d'événements certifié (ANNEXE-E), 430 763 € de lignes supprimées (champ « DEL »), représentant 34 % du CA déclaré, présentes dans 656 des 659 sessions de caisse. Il en infère un système d'occultation : des ventes auraient été encaissées puis effacées pour minorer la recette. Compte tenu du taux (34 %) et du caractère systématique, le service est susceptible de rejeter la comptabilité (art. L. 193 LPF, charge de la preuve renversée sur le contribuable) et de reconstituer le CA par coefficient.

La présente note vise deux objectifs distincts qu'il convient de ne pas confondre :
- démontrer que les suppressions ne sont pas des recettes dissimulées (exhaustivité de la recette déclarée) ;
- préparer, à titre subsidiaire, le terrain de la reconstitution, le service pouvant rejeter la comptabilité indépendamment de la démonstration d'exhaustivité.

---

## 3. Démonstration en cinq niveaux

### Niveau 1 - Erreurs de quantité : la preuve arithmétique sur le haut de pile

Chaque événement DEL correspond à une ligne dont le montant est le prix carte multiplié par une quantité. Neuf lignes concentrent 140 221 €, soit 32,6 % du total des suppressions, et résultent manifestement d'erreurs de saisie de quantité, supprimées immédiatement en plein service. Les quatre plus grosses :

- 68 993,10 € (26/07/2022, 18h51) ;
- 44 955,00 € = 45 € (menu Demi Lune) × 999 (21/06/2023) ;
- 19 600,00 € (07/08/2022) ;
- 4 455,00 € = 45 € (menu Demi Lune) × 99 (15/08/2024).

Auxquelles s'ajoutent cinq lignes plus modestes (810 = 45 × 18 ; 481 = 13 × 37 ; 409,20 = 18,60 × 22 ; 408 = 34 × 12 ; 109,80 = 6,10 × 18).

La logique : 9999 est la valeur maximale du champ quantité ; 999 et 99 en sont les déclinaisons. Ces saisies, faites puis annulées dans la même minute, ne correspondent à aucun repas servi ni encaissé. À elles seules, ces 9 lignes retirent un tiers du montant brut de toute prétention d'occultation.

Réserve de méthode importante (à intégrer avant production) : la décomposition prix × quantité est inférée, la source ANNEXE-E ne comportant pas de colonne quantité/produit exploitable en l'état. Sur la ligne de 68 993,10 €, nos deux jeux de calcul divergent sur la décomposition (6,90 € × 9999 d'un côté ; 9,90 € × 6 969 de l'autre). Cette contradiction interne doit être levée avant toute communication : il faut produire le ticket d'origine ou le log NF525 détaillé établissant la quantité réelle. Le montant total (140 221 €) et l'argument de fond (erreur de saisie immédiatement corrigée) restent valides quelle que soit la décomposition retenue, mais l'incohérence sur une ligne phare serait exploitée si elle subsistait.

Source : scripts 09_aberrations_del.py, 10_del_justification.py ; aberrations_del.json, del_justification.json.

### Niveau 2 - Preuve par session : les suppressions dépassent le CA du jour

C'est la preuve la plus forte car elle est insensible à toute hypothèse de méthode. Sur 9 sessions de caisse (Z) parmi 659, le montant supprimé excède le CA réellement encaissé ce jour-là. Exemple :

- Z 3015, 26/07/2022 : CA des tickets payés = 2 563,40 € ; suppressions = 69 556,60 €.
- Z 3216, 21/06/2023 : CA = 1 686,40 € ; suppressions = 45 280,30 €.
- Z 3026 : CA = 2 209,60 € ; suppressions = 20 087,90 €.

On ne peut pas supprimer plus de ventes qu'on n'en a encaissées dans la journée. Ces lignes sont donc, par construction, fictives (erreurs de saisie ou ré-écritures), et non des recettes soustraites. Cette démonstration ne repose sur aucune décomposition prix × quantité : elle compare deux totaux issus de la même source certifiée.

Source : script 11_reconciliation_par_z.py ; reconciliation_par_z.json.

### Niveau 3 - Preuve par distribution : ce sont de vrais articles du menu

Les prix des lignes supprimées épousent la grille de prix des ventes réelles (3,90 € : 8,7 % des ventes vs 8,6 % des suppressions ; 18,60 € : 6,3 % vs 6,0 % ; 8,90 € : 3,1 % vs 3,0 %). Les suppressions ne forment donc pas une catégorie cachée de produits parallèles : ce sont les mêmes articles du menu, saisis puis corrigés ou ré-encaissés.

Avertissement stratégique, à manier avec prudence : cet argument est à double tranchant. Il établit que les lignes supprimées sont de vrais articles (de taille repas), ce qui, isolé, sert le service autant que la défense. Il ne doit jamais être produit seul. Sa seule valeur est de montrer qu'il n'existe pas de famille de produits « occultes », et il n'a de force qu'étroitement couplé au verrou paiement du niveau 5 : ces vrais articles ont bien été ré-encaissés et déclarés (la corrélation prix le confirme), et l'argent correspondant figure dans les encaissements bancarisés. Présenté ainsi (vrais articles → ré-encaissés → bancarisés), il ferme la boucle ; présenté autrement, il l'ouvre.

Source : script 10_del_justification.py ; del_justification.json.

### Niveau 4 - Triangulation : trois exports certifiés convergent sans les suppressions

Trois sources certifiées et indépendantes donnent le même CA à moins de 0,2 % près en cumulé :

- synthèse ANNEXE-A : 1 275 924 € ;
- liste des tickets ANNEXE-H : 1 277 216 € ;
- encaissements ANNEXE-A : 1 275 980 €.

Les 430 763 € de suppressions ne figurent dans aucun de ces trois exports. Le CA déclaré s'explique intégralement par les tickets payés, sans qu'il soit jamais nécessaire de mobiliser les lignes supprimées. Si celles-ci avaient été des recettes encaissées et soustraites, l'une au moins de ces trois sources aurait dû les porter.

Réserve honnête : ANNEXE-H et ANNEXE-A diffèrent de ±1 à 2 % par exercice (-5 651 € en 2022-2023 ; +9 076 € en 2023-2024 ; -2 133 € en 2024-2025), du fait des coupures d'exercice (sessions Z à cheval sur le 31/03). Ces écarts se compensent et le cumul converge à moins de 0,2 %. Cet écart annuel doit être présenté et expliqué de manière proactive, faute de quoi il serait présenté contre nous comme une instabilité de la donnée.

Source : script 11_reconciliation_par_z.py ; reconciliation_par_z.json.

### Niveau 5 - Le double verrou : encaissement et approvisionnement

Pour qu'une vente occultée existe, il faut deux canaux : un canal pour encaisser l'argent et un canal pour s'approvisionner en marchandise vendue. Aucun n'est ouvert.

**Verrou encaissement.** Le CA déclaré égale les encaissements au centime sur les trois exercices. Les espèces ne représentent que 1,3 % du CA (17 042 €) ; 98,7 % est bancarisé. Il n'existe donc pas de canal espèces dimensionné pour absorber 430 763 € de ventes parallèles.

Limite à reconnaître et à corriger : l'égalité « CA déclaré = encaissements » est en partie tautologique (les deux grandeurs sont produites par la caisse). Et la bancarisation à 98,7 % est, en l'état du dossier, affirmée mais non encore prouvée par les relevés bancaires réels. Le verrou ne devient une preuve d'exhaustivité opposable qu'après production des relevés bancaires des trois exercices et rapprochement des encaissements déclarés avec les crédits effectivement constatés en banque. Cette pièce est à demander au client en priorité. De plus, le plafond de 1,3 % ne ferme que le cash : il faut démontrer que les canaux non-espèces (CB, titres-restaurant, chèques-vacances) sont intégralement tracés et rapprochés, à défaut de quoi le canal d'occultation ne serait pas plafonné à 1,3 %.

**Verrou approvisionnement.** 430 763 € de ventes cachées supposeraient un approvisionnement caché de même ampleur. Or les achats se reconcilient pour l'essentiel avec la consommation déclarée augmentée des pertes normales, à stock stable.

Réserve majeure, à traiter avant toute production (voir § 5) : notre propre modèle Monte Carlo (resultats_montecarlo_ajuste2.json) chiffre un « disparu alcool » médian de 76 113 € (intervalle de confiance 62 262 - 87 321 €, soit 21,5 % des achats d'alcool valorisés au prix de revente), plus 35 690 € de softs non bilantés. Tant que ce disparu n'est pas justifié, le verrou approvisionnement n'est pas opposable et constitue même une reconstitution par les achats clé en main pour le service. Affirmer « pas d'inputs pour des ventes fantômes » serait, en l'état, contredit par notre propre travail. Cet argument ne doit donc pas être produit tant que le disparu n'est pas explicité.

Source : pipeline incertitudeDisparu (scripts 02, 06, 07) ; resultats_montecarlo_ajuste2.json, softs_balance.json, staff_conso.json.

---

## 4. Le renversement de la charge probatoire

Une fois purgées les réserves ci-dessus, l'architecture de la défense consiste à demander au service de produire ce qu'une occultation suppose nécessairement :

1. Un canal d'encaissement. Si 430 763 € de ventes ont été encaissées puis effacées, où est l'argent ? Les espèces sont à 1,3 % et 98,7 % est bancarisé. Le service doit identifier le flux financier de sortie. À défaut, l'argent n'a jamais existé.

2. Un canal d'approvisionnement. Vendre suppose acheter. Le service doit identifier les achats correspondants. Le disparu alcool, une fois justifié (casse, pertes, doses réelles, offerts, consommation du personnel), ne laisse pas matière à 430 763 € de ventes fantômes.

3. Une cohérence par session. Le service doit expliquer comment on aurait pu supprimer 69 557 € de ventes un jour où la caisse n'a encaissé que 2 563 €.

Le journal de suppressions, en lui-même, ne prouve aucune recette : c'est un log technique d'une caisse certifiée NF525, par nature exhaustif et transparent. La transparence du log (les suppressions sont enregistrées et même reportées dans ANNEXE-A à la ligne « Lignes supprimées ») plaide pour la régularité, non pour la dissimulation : on ne dissimule pas ce que l'on enregistre et déclare.

---

## 5. Réponses anticipées aux objections du service

**Objection 1 - « Le disparu alcool de 62 à 94 k€ de votre propre modèle est une reconstitution prête à l'emploi. »**
C'est l'objection la plus sérieuse. À ce stade, elle n'est pas écartée. Notre modèle (médiane 76 113 €) suppose une incertitude nulle (doses nominales, zéro perte, zéro consommation du personnel, menu = prix moyen) dans son scénario nominal, et la fourchette traduit la sensibilité à ces hypothèses. Avant tout débat, il faut justifier ce disparu par des éléments concrets : doses réellement servies, casse et pertes, offerts commerciaux, consommation du personnel, fiabilisation des softs (35 690 € de softs non bilantés sont un trou de donnée, pas une disparition). Tant que ce travail n'est pas fait, le verrou approvisionnement reste en réserve. Il convient d'attaquer ce point de front, séparément du débat sur les suppressions, car le service le mobilisera quelle que soit la qualité de la démonstration sur les DEL. Recouper l'ordre de grandeur du disparu (62-94 k€) avec le solde de DEL « normales » inexpliquées (~290 k€, voir objection 4) est un exercice à mener nous-mêmes avant le service.

**Objection 2 - « La comptabilité doit être rejetée (L. 193 LPF) au taux de 34 %, puis reconstituée par coefficient. »**
À traiter à titre subsidiaire et en parallèle. Notre démonstration porte sur l'exhaustivité (l'argent reçu est déclaré) ; elle n'interdit pas au service de rejeter la forme. Il faut donc préparer une défense sur le terrain de la reconstitution elle-même : contester le coefficient de marge retenu, opposer un coefficient réaliste documenté (notamment sur les liquides et vins du Jura, avec leurs pertes et offerts propres), et démontrer que la méthode de reconstitution du service est radicalement viciée ou excessivement sommaire (jurisprudence constante exigeant une méthode tenant compte des conditions réelles d'exploitation). Ne pas raisonner uniquement « caisse exacte ».

**Objection 3 - « Vos cartes cadeau sont invoquées mais non prouvées. »**
Objection fondée en l'état. Les cartes cadeau ne sont pas identifiables dans les données (aucun mode de règlement ni produit dédié). Un mécanisme exonérant invoqué mais non chiffrable est lu contre le contribuable et alimente le rejet de comptabilité plutôt qu'il ne l'écarte. Recommandation : soit retirer cet argument, soit l'étayer par des pièces externes (souches de cartes, écritures au compte « avances clients » / produits constatés d'avance, dates d'achat antérieures aux suppressions). Ne pas le produire en l'état.

**Objection 4 - « Le cœur des suppressions reste inexpliqué ligne à ligne. »**
À reconnaître. Après les 9 erreurs de quantité (140 221 €), il subsiste environ 290 409 € de DEL de taille normale (5-100 €, taille repas) sans explication individuelle. Les arguments macro (distribution, par session) ne les rattachent pas une à une à un mécanisme. Notre position : la traçabilité par article est détruite par conception par les mécanismes légitimes eux-mêmes (une correction = un autre article ré-ajouté ; une facture sans détail = des plats remplacés par un menu agrégé ; une carte cadeau = payée des mois avant), de sorte que tracer chaque ligne est impossible et non requis ; le test légal est l'exhaustivité de la recette, vérifiée par les niveaux 2, 4 et 5. Cette position de droit est solide, mais elle ne dispense pas de qualifier statistiquement ce solde de 290 k€ (part dans la bande des prix-menu, fréquence des ré-encaissements immédiats dans la même session) pour montrer qu'il relève des mêmes mécanismes que les lignes documentées.

**Objection 5 - « Un caissier unique (LUNA) pour 21 302 suppressions, présentes dans 656/659 sessions : manquement délibéré (40 %), voire manœuvres (80 %). »**
Le caractère systématique et le compte caissier unique seront exploités pour la qualification des pénalités. Contre-mesure : documenter le workflow réel du poste de caisse (compte de caisse partagé/identifiant unique de l'établissement et non d'une personne, organisation du service, raisons opérationnelles des corrections immédiates en coup de feu). Le caractère systématique des corrections est le signe d'un usage normal d'une caisse certifiée en restauration à fort volume, non d'un procédé d'occultation, dès lors que l'exhaustivité de la recette est par ailleurs établie.

---

## 6. Réserves honnêtes et pièces / scripts à l'appui

### Réserves assumées
- Diagnostic macro et par session, non ligne à ligne. ~290 409 € de DEL « normales » ne sont pas rattachées individuellement à un mécanisme.
- Décomposition prix × quantité inférée ; contradiction à lever sur la ligne de 68 993,10 € (6,90 × 9999 vs 9,90 × 6 969).
- Bancarisation 98,7 % affirmée, non encore prouvée par relevés ; égalité CA = encaissements partiellement tautologique.
- Canaux non-espèces (CB, titres-restaurant ~34 k€ cumulé, chèques-vacances ~47 k€ cumulé) à rapprocher.
- Disparu alcool 62-94 k€ + 35 690 € de softs : non encore justifié ; à traiter avant d'opposer le verrou approvisionnement.
- Cartes cadeau non prouvées : à retirer ou étayer.
- Écart ANNEXE-H vs ANNEXE-A de ±1-2 % par an (coupures d'exercice), convergent à < 0,2 % en cumulé.

### Pièces à obtenir en priorité (du client / de tiers)
1. Relevés bancaires des trois exercices (preuve d'exhaustivité ; rapprochement encaissements déclarés / crédits effectifs).
2. Log NF525 détaillé ou tickets d'origine des grosses suppressions (lever la contradiction sur la quantité).
3. Détail des encaissements par mode de règlement (CB, titres-restaurant, chèques-vacances) et leur rapprochement.
4. Éléments de justification du disparu alcool : fiches doses, pertes/casse, offerts, consommation du personnel.
5. Le cas échéant, pièces des cartes cadeau (souches, comptes d'avances clients, dates d'achat).

### Scripts et fichiers reproductibles (dossier incertitudeDisparu, venv /tmp/xlsenv/bin/python)
- 08_reconciliation_suppressions.py → reconciliation_suppressions.json (total DEL 430 763 € ; attention à exclure les lignes de pied de page « Nb lignes », sous peine d'un double comptage erroné à 861 k€).
- 09_aberrations_del.py → aberrations_del.json (grosses erreurs de quantité).
- 10_del_justification.py → del_justification.json (9 erreurs de quantité = 140 221 € ; distribution des prix).
- 11_reconciliation_par_z.py → reconciliation_par_z.json (preuve par session : 9 Z où suppr > CA ; triangulation 3 exports).
- 02_montecarlo.py / resultats_montecarlo_ajuste2.json (disparu alcool, à justifier).
- 06_conso_staff.py, 07_softs_reels.py → staff_conso.json, softs_balance.json (consommation du personnel, softs non bilantés).

---

### Principe clé à retenir
Les mécanismes légitimes (correction = autre article ajouté ; facture sans détail = plats remplacés par un menu agrégé ; carte cadeau = payée des mois avant) détruisent la traçabilité par article par conception. Tracer chaque article est donc impossible et non requis. Le test légal est : argent reçu = argent déclaré = argent bancarisé. Cette égalité est vérifiée au niveau macro et par session ; elle doit être verrouillée par les relevés bancaires.
