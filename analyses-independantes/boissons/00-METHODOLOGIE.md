# Analyse indépendante des « boissons disparues » - méthodologie

> Objectif : déterminer, **sans aucune reprise des chiffres du fisc**, et à partir
> des seules données primaires du dossier :
> 1. le **coût d'achat** unitaire de chaque boisson (factures fournisseur) ;
> 2. le **prix de vente** théorique (carte) et le **prix réellement encaissé** (caisse) ;
> 3. la **quantité achetée** vs la **quantité vendue** par exercice ;
> 4. la **valeur réelle des « disparitions »** (achat − vente), au coût d'achat ET au prix de vente.
>
> Ces calculs sont **scriptés et reproductibles** : ils seront ré-exécutés plus tard
> pour intégrer **l'inventaire** (encore indisponible) et pour **simuler** la
> consommation du personnel / les pertes.

## Sources primaires (aucune donnée du fisc)

| Source | Fichier(s) | Apporte |
|---|---|---|
| Factures fournisseur FCBS | `src/data/factures-fournisseur.json` (199 factures + relevés) → `achats-par-produit.json` | quantités achetées, coût HT, contenance, code produit |
| Caisse - synthèse par produit | `public/documents/ANNEXE-D{1,2,3}_synthese-produit_*.xls` | quantités vendues, prix encaissé, CA TTC, par exercice |
| Carte des vins & boissons | `public/documents/vins-boissons/carte_*.xls` (3 versions) | prix de vente affiché + **dose** (cl) par boisson |
| Carnet manuscrit | `public/documents/vins-boissons/analyse-manuscrite/analyse-manuscrite-boissons.xls` | anomalies de livraison (manques, avoirs, reprises) |

## Périmètre temporel

- **Exercices comptables** (clôture 31 mars) : `2022-2023` = 01/04/2022 → 31/03/2023, etc.
- La caisse (annexes D) est **déjà par exercice**.
- Les achats (factures) sont datés au jour : ils sont **re-ventilés par exercice**
  à partir de `dateFacture`. Les pièces hors période (avant 01/04/2022 / après
  31/03/2025) sont isolées dans un bucket `hors-periode`.

## Deux niveaux de comparaison (séparés volontairement)

- **Niveau 1 - DIRECT (zéro hypothèse).** Boissons achetées ET vendues **à l'unité
  fermée** (bouteilles de vin, bières 33/50 cl, sodas, eaux, cidres). Achat ⇄ vente
  se compare **bouteille pour bouteille**, sans aucune dose. C'est le socle
  incontestable.
- **Niveau 2 - DOSE (hypothèses documentées).** Boissons servies au verre / à la
  dose (fûts, spiritueux, apéritifs, cocktails, vins au pichet/verre). La conversion
  achat→vente passe par une **dose**, prise **sur la carte** (donc non interprétée :
  « Macvin 6 cl », « Vin Jaune 12 cl »…). Les cocktails consomment plusieurs
  ingrédients : ce niveau est explicitement **paramétrable** (doses, recettes) pour
  les simulations futures.

## Valorisation des écarts

Pour chaque produit / exercice : `écart_qté = acheté − vendu` (en unités et, si
pertinent, en cl). L'écart est valorisé de deux façons :
- au **coût d'achat HT** (`écart × coût d'achat unitaire`) → ce que la marchandise a coûté ;
- au **prix de vente** (carte ou prix moyen caisse) → le CA qu'elle représenterait si vendue.

## Hypothèses et limites (à lever plus tard)

- **Pas d'inventaire** : on suppose pour l'instant stock initial = stock final = 0.
  Un écart positif (acheté > vendu) peut donc refléter une **constitution de stock**
  et non une disparition. À corriger dès réception de l'inventaire.
- **Consommation du personnel / offerts / pertes / casse** : non encore déduits
  (paramètres de simulation à venir).
- **Usages cuisine** (vin de cuisine, macvin en sauce, etc.) : à traiter au niveau 2.
- Les anomalies du carnet manuscrit (manques, avoirs) indiquent que le **facturé ≠ livré** :
  elles servent à **corriger le « disponible »** au niveau 2.

## Artefacts produits (trace écrite)

| Fichier | Contenu |
|---|---|
| `data/achats-exercice.json` | achats FCBS re-ventilés par exercice et par produit |
| `data/ventes-caisse.json` | ventes caisse par produit/exercice (qté, prix, CA) |
| `data/prix-carte.json` | prix de vente + dose par boisson (3 versions de carte) |
| `data/anomalies.json` | carnet manuscrit parsé (qté, statut) |
| `data/correspondances.json` | table de correspondance achat ⇄ caisse (niveau 1 et 2) |
| `data/disparitions.json` | résultat final par produit/exercice |
| `RAPPORT-disparitions.md` | tableaux lisibles + totaux |

Tous générés par les scripts de `scripts/boissons/` (ré-exécutables) :
`01_extraction.py` (sources → JSON), puis `02_disparitions.py` (croisement → résultat + rapport).

## Constats de qualité de données (à connaître avant de réutiliser)

1. **Fûts de bière facturés au LITRE (vérifié sur facture).** Code `212122`
   « FUT AFFLIGEM BLADE 8 L » : sur la facture, `colis=3` (= 3 fûts), `quantité=24`
   (= 24 **litres** = 3 × 8 L), `puNet=3,59 €/L`, `HT=86,16 €` → **28,72 €/fût**, prix
   réel du liquide. La **consigne est hors lignes** (différence `totalFacture − totalTTC`).
   ⇒ Pour un fût, le volume = **quantité × 100 cl** (et NON × 800 cl) et le coût/cl =
   `HT / volume`. La bière pression est **bien incluse** (≈ 270 fûts / 2 160 L sur 3 ans).
   `achats-par-produit.json` se trompait (× 800) ; `01_extraction.py` recalcule le volume
   ligne à ligne (règle fût) - **rien n'est exclu**.
2. **Matériel non-liquide** (verrerie, kits, pailles, blocs-notes, sous-bocks ≈ 283 € HT) :
   **conservé et documenté** (`type:"materiel"`), avec un volume de boisson nul - ce ne
   sont pas des liquides, ils ne créent donc aucune « disparition ».
3. **Eaux « X CL CONSIGNE » = vraies boissons** (bouteilles consignées/retournables),
   conservées normalement.
4. **Boutons caisse génériques** (« Sirop à l'eau », « Jus de Fruit », « Verre/Pichet de
   vin de base ») : la vente n'est pas ventilée par SKU → l'écart par PRODUIT est
   sur-estimé pour ces familles ; **le bilan par CATÉGORIE est l'unité fiable**.
5. **Groupes de substituts** (même vin/spiritueux servi sous un bouton unique, plusieurs
   millésimes/domaines) : la vente est répartie proportionnellement entre les millésimes.
   Les chiffres **par millésime** sont donc indicatifs ; raisonner par **groupe/catégorie**.
6. **Doses** : prises sur la carte (`prix-carte.json`) - vin tranquille au verre = 15 cl,
   crémant/vin jaune = 12 cl, digestif = 4 cl, anisé = 2 cl, apéritif = 6 cl, demi = 25 cl,
   pinte = 50 cl. Modifiables dans les `map-*.json` (champ `doses_hypotheses`).

## Comment refaire le calcul plus tard (inventaire + simulations)

- **Inventaire** : ajouter, par produit/exercice, `stockInitialCl` et `stockFinalCl`, puis
  remplacer `disponible = achat` par `disponible = stockInitial + achat − stockFinal`
  dans `02_disparitions.py`. L'écart deviendra une vraie « disparition » et non un
  simple solde achats−ventes.
- **Simulations** (consommation personnel, offerts, pertes, casse, usage cuisine) :
  appliquer des **abattements paramétrables** par catégorie sur le volume disponible
  avant comparaison. Structure prévue pour brancher ces paramètres sans toucher aux
  extractions.
- Les recettes de cocktails (`map-cocktails.json`) et les doses (`map-*.json`) sont
  éditables : toute simulation de dose se fait là, puis on relance `02_disparitions.py`.
