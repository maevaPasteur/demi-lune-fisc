# Synthèse - les suppressions de caisse (DEL) ne sont pas de l'occultation

Trace de bout en bout de l'analyse. Tout est reproductible (`/tmp/xlsenv/bin/python <script>.py` depuis `src/data/incertitudeDisparu/`). Document analytique ; la version juridique est `ARGUMENTAIRE-AVOCAT-suppressions.md`.

## Le grief

Le fisc relève ~**430 763 €** de « lignes supprimées » (événements `DEL`) dans la caisse certifiée sur 3 exercices (2022-2025), soit **34 % du CA déclaré**, et les présente comme des ventes dissimulées.

## Sources de données (caisse certifiée NF525)

| Annexe | Contenu | Usage |
|---|---|---|
| E1/E2/E3 (tpvevenement) | journal d'événements : suppressions `DEL` (date, heure, Z, caissier, montant) | total et nature des suppressions |
| A1/A2/A3 (synthèse CA) | CA déclaré, encaissements par mode, « Lignes supprimées » | CA, espèces, transparence |
| H1/H2/H3 (liste tickets) | un ticket = une ligne (total TTC, Z) | CA par ticket / par Z |
| B1/B2/B3 (prix-vente-quantité) | ventes ligne par ligne | grille de prix réels |
| inventaires | stock physique | verrou approvisionnement |

> Piège corrigé : chaque fichier E a une ligne de pied « Nb lignes » qui contient le total. La compter double le résultat (→ 861 k€ faux). Le vrai total, pied de page exclu, est **430 763 €** (= ce qu'affiche déjà `analyseDel.ts`). Voir `08_*.py`, fonction `deletions()`.

## La démonstration, en 5 niveaux

### 1. Erreurs de quantité (`09`, `10`) - 140 221 € = 33 % du total
Chaque ligne supprimée = un seul produit × sa quantité. 9 lignes ont une quantité absurde. Les 4 géantes, au centime près :

| Montant | Décomposition |
|---|---|
| 68 993,10 € | 6,90 € (menu Bambin) × **9999** |
| 44 955,00 € | 45,00 € (Demi Lune) × **999** |
| 19 600,00 € | 19,60 € × **1000** |
| 4 455,00 € | 45,00 € (Demi Lune) × **99** |

9999 = valeur maximale du champ quantité. Fautes de frappe supprimées dans la minute, en plein service, entourées de suppressions normales (3-20 €). + 5 lignes moyennes (810 = 45×18, etc.).

### 2. Preuve par session de caisse (`11`) - la plus forte
Sur **9 sessions (Z)**, les suppressions **dépassent le CA encaissé du jour**. Exemple : le 26/07/2022, CA réel **2 563 €**, suppressions **69 557 €**. On ne peut pas supprimer plus de ventes qu'on n'en a encaissées : ces lignes sont *forcément fictives*.

### 3. Preuve par distribution (`10`)
Les prix des lignes supprimées épousent ceux des ventes réelles (3,90 € : 8,7 % des ventes vs 8,6 % des suppressions ; 18,60 € : 6,3 % vs 6,0 % ; etc.). Les suppressions sont donc de **vrais articles du menu** (re-encaissés/corrigés), pas une catégorie cachée. Une dissimulation de bouteilles chères déformerait la distribution ; elle ne l'est pas.

### 4. Triangulation - 3 exports certifiés indépendants (`11`)
- Synthèse (ANNEXE-A) : 1 275 924 €
- Liste tickets (ANNEXE-H) : 1 277 216 €
- Encaissements (ANNEXE-A) : 1 275 980 €

Convergence à < 0,2 %. Les suppressions (430 k€) ne figurent dans **aucun** des trois.

### 5. Double verrou (`08`)
- **Paiement** : CA déclaré = encaissements au centime ; espèces = **1,3 %** (17 042 €) ; 98,7 % bancarisé. Aucun canal pour encaisser au noir.
- **Approvisionnement** : 430 k€ de ventes cachées exigeraient 430 k€ d'achats cachés ; les achats boissons se réconcilient avec la conso + perte normale, stock stable.

## Le retournement de la charge de la preuve

Les mécanismes légitimes (correction = autre article ; facture sans détail = plats remplacés par un menu agrégé ; carte cadeau = payée des mois avant) **détruisent la traçabilité par article par conception**. Tracer chaque plat est donc impossible et **non requis** : le test légal est « argent reçu = déclaré = bancarisé », vérifié. Pour soutenir l'occultation, c'est au fisc d'exhiber un canal d'encaissement (inexistant : 1,3 % d'espèces) **et** un canal d'approvisionnement (inexistant : achats réconciliés). La reconstitution du fisc n'a pas de mécanisme.

## Réserves honnêtes

- Diagnostic macro et par session, pas ligne à ligne (impossible, cf. ci-dessus).
- ANNEXE-H vs A diffèrent de ±1-2 % par an (coupures d'exercice, Z à cheval sur le 31/03) mais convergent à < 0,2 % en cumulé.
- Les cartes cadeau ne sont pas isolables dans les données (pas de mode ni de produit dédié) : on ne décompose pas par mécanisme, on prouve par la valeur.

## Réconciliation avec le disparu boissons (`12`)

Le fisc pourrait retourner nos deux analyses l'une contre l'autre (disparu boissons ~76 k€ + suppressions 430 k€). Elles ne s'additionnent pas :
- **Double comptage** : le disparu = achats factures − conso sonnée. Toute boisson vendue au noir puis supprimée n'est pas sonnée → elle est *déjà* dans le disparu. Les deux reconstitutions du fisc sont mutuellement exclusives.
- **Plafond par les achats** : le maximum de boissons vendables au noir = le disparu = **76 k€ revente = 24 % du CA boissons = perte normale CHR**, avec causes de conso documentées.
- **Échelle** : 430 k€ de DEL = 1,4× le CA boissons déclaré (318 k€) → ne peut pas être des ventes de boissons cachées (il faudrait autant d'achats cachés, démentis par le stock stable).
- **Distribution** : les DEL épousent le menu complet (nourriture + boissons), pas une catégorie → re-encaissements.
- **Côté nourriture** : si les ~290 k€ de DEL normales étaient de la nourriture cachée, il faudrait ~87 k€ d'achats nourriture non comptabilisés, vérifiable sur les comptes d'achats.

CA déclaré : boissons 318 026 € / nourriture 957 898 € (3 exercices).

## Scripts et sorties

`08_reconciliation_suppressions.py` → `reconciliation_suppressions.json` ; `09_aberrations_del.py` → `aberrations_del.json` ; `10_del_justification.py` → `del_justification.json` ; `11_reconciliation_par_z.py` → `reconciliation_par_z.json`. Revue et vérification : `REDTEAM-suppressions.md`, `VERIFICATION-chiffres.md`.
