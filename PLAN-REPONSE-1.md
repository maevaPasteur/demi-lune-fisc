# Plan d'action — rendre `/reponse-1/` opposable

État au 12/09/2026. Source : `AUDIT-SOURCES.md` (1 523 références) et `AUDIT-ADVERSE.md`
(661 failles sur 36 pages : 183 bloquantes, 339 sérieuses, 139 mineures), plus
`AUDIT-ADVERSE-p28.md` (25 failles, page auditée après coup).

---

## 0. Ce que « irréfutable » veut dire ici

Un objectif de zéro faille est hors d'atteinte, et le viser produirait des pages qui
sur-affirment, c'est-à-dire exactement ce que l'audit reproche. La cible opérationnelle est
différente et elle est atteignable :

1. **Zéro affirmation fausse.** Aucun chiffre non recalculé, aucune source non ouverte, aucune
   décision dont la portée est forcée.
2. **Zéro contradiction** entre deux pages, entre une page et sa pièce jointe, entre une page et
   les données publiées.
3. **Zéro angle mort** sur un argument que le service a effectivement écrit.
4. **Toute concession est portée par nous**, chiffrée, et retournée quand elle peut l'être.

Une page qui concède proprement est opposable. Une page qui affirme trop ne l'est pas.

---

## 1. Contrainte de plate-forme, à connaître avant de dimensionner

Cinquante agents simultanés ne sont pas possibles : **le plafond est de 20 agents concurrents**,
et il est global (un chef de file et ses sous-agents comptent dans le même quota). Trois
enseignements des vagues précédentes :

- un agent dont le transcript devient long **se bloque** (chien de garde à 600 s) : préférer
  beaucoup d'agents courts à peu d'agents longs, un livrable par agent ;
- les dépassements de quota **tuent toute la vague** : plafonner à **16 agents concurrents** pour
  garder de la marge ;
- deux agents qui écrivent le même fichier se détruisent mutuellement : **un fichier n'a qu'un seul
  propriétaire à un instant donné**.

Le plan mobilise donc **environ 130 exécutions d'agents réparties en 9 vagues de 12 à 16**, ce qui
est plus rapide et bien plus sûr que 50 agents lancés ensemble.

---

## 2. Règles d'exécution, valables pour tous les agents

**Propriété exclusive.** Chaque agent reçoit la liste des fichiers qu'il peut écrire. Il n'écrit
rien d'autre. Une page = un propriétaire par vague.

**Fichiers partagés, interdits sauf ticket explicite** : `src/data/reponse1.ts`,
`scripts/reponse1-cascade-coherence.py`, `src/data/analyseBoissons.ts`, `src/data/renduFinal/**`,
`public/documents/inventaires/**`, `public/documents/caisse-enregistreuse/**` (lecture seule
absolue).

**Tout chiffre est produit par un script** versionné dans `scripts/`, idempotent, relançable.
Aucune valeur saisie à la main dans un JSON.

**Registre.** Chaque agent inscrit son résultat dans `scratchpad/REGISTRE.tsv`
(`vague, agent, page, faille, statut, valeur_retenue, fichiers_touchés`). C'est la source unique
pour la vague suivante.

**Contrôles avant de rendre** : `python3 scripts/reponse1-controle.py` sans anomalie,
`npx tsc --noEmit` propre, JSON valides, zéro tiret cadratin, pièces jointes existantes.

**Contraintes de session** : budget WebSearch épuisé, `legifrance.gouv.fr` renvoie 403. Utiliser
`codes.droit.org` (codes consolidés, texte en vigueur et identifiant LEGIARTI), `juricaf.org`
(jurisprudence, texte intégral) et `bofip.impots.gouv.fr`. Ce qui ne peut être ouvert est classé
non vérifiable, jamais affirmé.

---

## 3. Phase A — Débloquer les décisions (préalable, 0 agent)

Huit points ne relèvent pas de la rédaction et **bloquent 14 pages**. Tant qu'ils ne sont pas
tranchés, toute réécriture des pages concernées est du travail à refaire.

### A.1 Arbitrages de l'avocat

| # | Décision | Pages bloquées |
|---|---|---|
| 1 | Saisir ou non la commission. La page 1 le recommande ; 4 pages s'appuient sur l'absence de saisine pour écarter des arrêts défavorables ; la saisine déplace la charge de la preuve sur la société | 1, 14, 16, 28, 35 |
| 2 | Conserver ou retirer le KPI « 37 % du CA », qui est le critère exact de CAA Douai 25DA00174 | 35, 36 |
| 3 | Invoquer ou non le non-cumul intérêts/amende (art. 1727 et 1759), qui troque 7 268 € contre 471 826 € et présuppose l'amende applicable | 36, 37 |
| 4 | Signaler ou taire les deux erreurs corrigibles **à la hausse** par le service (380 € de TVA, un mois d'intérêts) | 34, 37 |
| 5 | Convention de présentation : chiffrer les postes avec ou sans le levier d'extrapolation cuisine | 22, 26, 32, 33 |
| 6 | Sort du rendu final : archive figée de ce qui a été envoyé le 10/07/2026, ou mise à jour | hors périmètre |

### A.2 Faits que seule la gérante peut établir

Origine et date des supports d'inventaire 2024 et 2025 · existence d'achats de Calvados et de
spiritueux chez Intermarché (78 factures détenues par le service) · dose réelle de flambage par
plat · contenance réelle des verres de service · report éventuel d'une bouteille de crémant au
lendemain · consommation du personnel · documentation SERVILOG présentée le 29/01/2026 · existence
d'un contrôle fiscal antérieur.

**Livrable** : un questionnaire unique, une page, à faire remplir. Sans lui, les pages 6, 10, 17,
19, 21, 23, 29 restent en l'état.

---

## 4. Phase B — Purger les 11 failles transversales (2 vagues, 48 agents)

C'est la phase la plus rentable : une faille transversale corrigée une fois vaut pour 4 à 12 pages.
La corriger page par page produirait 37 formulations divergentes, c'est-à-dire le problème qu'on
veut résoudre.

**Principe : séparer la décision de l'application.** Les normalisateurs ne touchent à aucune page ;
les applicateurs n'ont aucune décision à prendre.

### Vague B1 — 11 normalisateurs, lecture seule, strictement parallèles

Chacun produit une **fiche de normalisation** dans `scratchpad/normes/<theme>.md` : la valeur ou la
formulation unique retenue, sa démonstration, le script qui la produit, et la **liste exacte
page + section** des endroits à modifier.

| Agent | Thème transversal | Livrable attendu |
|---|---|---|
| B1-1 | Pièces jointes contredisant leur page | Inventaire exhaustif des écarts pièce/page, et sens de la correction |
| B1-2 | Un agrégat, trois valeurs selon la page | Table de référence : une valeur par agrégat, avec sa source |
| B1-3 | La dose change de page en page | Table des doses, une par produit, avec sa justification |
| B1-4 | Double emploi : le même litre réclamé deux fois | Cartographie des postes qui se recouvrent, et arbitrage |
| B1-5 | Jurisprudence défavorable, tronquée, ou les deux | Liste des décisions à retirer, à rectifier, à conserver |
| B1-6 | Angles morts systématiques | Les 7 arguments du service jamais traités, et où les traiter |
| B1-7 | Statut « demonte » sur des pages qui concèdent | Statut juste par page, argumenté |
| B1-8 | Le KPI travaille contre la page | Liste des KPI à retirer ou reformuler |
| B1-9 | Notes internes voyageant avec le document | Politique : purge, ou marquage non exportable |
| B1-10 | Renvoi à une pièce ne contenant pas ce qui est promis | Correspondance promesse/contenu, pièce par pièce |
| B1-11 | Le faux dilemme comme figure récurrente | Passages à reformuler |

### Vague B2 — 37 applicateurs, un par page, écriture exclusive

Chaque agent reçoit **sa** page et les 11 fiches. Il applique ce qui la concerne, sans rien
décider, et **ferme dans la foulée les failles bloquantes propres à sa page**. Il inscrit au
registre.

Ordonnancement en 3 sous-vagues de 12 à 13, par charge décroissante :
- B2-a : pages 6, 17, 19, 27, 9, 21, 2, 3, 4, 24, 30, 15 (les plus chargées)
- B2-b : pages 23, 13, 5, 7, 22, 26, 29, 18, 8, 10, 11, 12
- B2-c : pages 1, 14, 16, 20, 25, 28, 31, 32, 33, 34, 35, 36, 37

---

## 5. Phase C — Les 339 failles sérieuses (3 vagues, 37 agents)

Même découpage par page, même propriété exclusive, après stabilisation de la phase B. Chaque agent
traite la liste des sérieuses de sa page, dans l'ordre du rapport, et **assume par écrit** celles
qu'il choisit de ne pas traiter, avec le motif.

Priorité à trois familles, qui représentent l'essentiel du risque :
1. **Retournements** : ce que nous produisons et qui sert le service.
2. **Angles morts** : un argument écrit par le service et resté sans réponse.
3. **Sur-interprétations** : une source à qui l'on fait dire plus qu'elle ne dit.

Les failles **mineures** (139) ne sont pas traitées à ce stade : elles n'exposent pas le dossier et
leur correction consommerait le budget utile ailleurs.

---

## 6. Phase D — Vérification croisée (2 vagues, 40 agents)

### Vague D1 — nouvel audit adverse, 37 agents, un par page
Grille identique, agents neufs, sans mémoire du travail de correction. Objectif : mesurer la
baisse réelle du nombre de bloquantes, et détecter les failles **introduites** par les corrections.

### Vague D2 — 3 agents de contrôle
- **D2-1, sources** : toute référence ajoutée depuis le dernier audit, ouverte et vérifiée.
- **D2-2, cohérence** : tout agrégat partagé, comparé entre les 37 pages, les pièces jointes, les
  scripts et les données publiées. Sortie : matrice des valeurs.
- **D2-3, chaîne de production** : chaque script relancé deux fois, idempotence contrôlée, aucune
  pièce écrite par deux scripts différents.

**Critère de sortie** : zéro bloquante non assumée, zéro contradiction dans la matrice, contrôle et
typecheck propres, build propre.

---

## 7. Phase E — Gel et remise (1 vague, 4 agents)

- **E-1** : relance de `reponse1-cascade-coherence.py` et vérification que la cascade est identique
  partout.
- **E-2** : purge ou marquage des encarts internes selon la décision A.1-6.
- **E-3** : note de synthèse pour l'avocat : ce qui tient, ce qui est concédé, ce qui reste à
  produire, avec les pièces associées.
- **E-4** : vérification visuelle des 37 pages rendues, et contrôle des liens de téléchargement.

---

## 8. Ordonnancement et budget

| Vague | Agents | Concurrence | Dépend de |
|---|---|---|---|
| A | 0 | — | décisions humaines |
| B1 | 11 | 11 | A |
| B2-a / b / c | 12 + 12 + 13 | 13 max | B1 |
| C-a / b / c | 12 + 12 + 13 | 13 max | B2 |
| D1 (3 sous-vagues) | 37 | 13 max | C |
| D2 | 3 | 3 | D1 |
| E | 4 | 4 | D2 |
| **Total** | **≈ 129** | **≤ 16** | |

Les phases B et C peuvent démarrer sans A **uniquement** pour les 23 pages non bloquées par une
décision. Les 14 autres attendent.

---

## 9. Risques et parades

| Risque | Parade |
|---|---|
| Deux agents écrivent la même page | Propriété exclusive par vague, déclarée dans le prompt |
| Un agent corrige un chiffre et casse une autre page | Les agrégats partagés ne se corrigent qu'en phase B1, jamais en B2 ou C |
| Un agent invente une source faute d'accès | Legifrance inaccessible : seules trois sources autorisées, le reste est « non vérifiable » |
| Une correction crée une faille nouvelle | Phase D1, agents neufs, sans mémoire des corrections |
| Le quota de session saute en cours de vague | 16 agents maximum, registre écrit au fil de l'eau, reprise possible |
| Un agent long se bloque | Un livrable par agent, pas de sous-agents sauf en B1 |
