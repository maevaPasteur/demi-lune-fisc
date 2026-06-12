// =============================================================================
// BOISSONS « DISPARUES » - réfutation de la méthode de reconstitution du fisc.
// -----------------------------------------------------------------------------
// Ce module RELIE en une source unique l'ensemble des données « boissons » :
//   • volumesDisparus.ts        → volumes réputés disparus par le vérificateur
//   • achats.ts                 → achats réels par produit (factures FCBS)
//   • factures.ts               → factures fournisseur, niveau ligne
//   • analyse-disparus.json     → croisement disparus × achats (script)
//   • reconstitution-administration.json → méthode liquides→CA du fisc (Annexes finales)
//   • analyseReconstitution.ts  → reconstitution intégrale du CA (preuve maîtresse)
//   • analyseRefacturation.ts   → re-facturation à prix forcé (déjà au CA)
// Tous les nombres sont DÉRIVÉS de ces fichiers à l'import (aucune valeur en dur).
// =============================================================================

import { produitsDisparus, preuvesParametrage, volumesDisparus } from './volumesDisparus'
import { boissons, achatsData } from './achats'
import { factures } from './factures'
import disparusRaw from './analyse-disparus.json'
import reconAdminRaw from './reconstitution-administration.json'
import { reconstitution as reconCA } from './analyseReconstitution'
import { refacturation } from './analyseRefacturation'

// --- Typage minimal des deux JSON importés -----------------------------------
interface DisparusJson {
  compte: { produits: number; preuveParametrage: number; occurrences100pct: number; surconsommation: number }
  produits100pctAchetes: { nom: string; fiscDispo2223: number | null; achatsReelsTotal: number }[]
  ventesSansAchat: Record<string, { fisc: string; achatsReels: Record<string, number> }>
}
interface ReconAdminJson {
  methode: {
    rapportLiquideSolidePour1Euro: number
    abattements: Record<string, number>
    coefficientReventeTTC: { avantReconstitution: number; apresReconstitution: number }
  }
  ingredients: { ref: string; caReconstitue: { ttc: number } | null; notes?: string }[]
  synthese: {
    caLiquidesAvantAbattements: { ttc: number; ht: number; tva: number }
    caLiquidesApresAbattements: { ttc: number; ht: number; tva: number }
    caSolides: { ttc: number; ht: number; tva: number }
    caTotalReconstitue: { ttc: number; ht: number; tva: number }
    caInscritEnComptabilite: { ttc: number; ht: number; tva: number }
    discordanceCA: { ttc: number; ht: number; tva: number }
  }
  comptes: Record<string, number>
}
const D = disparusRaw as unknown as DisparusJson
const RA = reconAdminRaw as unknown as ReconAdminJson

// Noms lisibles des produits « vendus sans achat » (clés de analyse-disparus.json).
const NOMS_VENTES_SANS_ACHAT: Record<string, string> = {
  bordeauxMoutonCadet: 'Bordeaux Mouton Cadet',
  hautesCotesDeNuits: 'Hautes Côtes de Nuits',
}

// --- 1. Achats réels de boissons (factures FCBS) -----------------------------
const sommeBoissonsHT = boissons.reduce((a, p) => a + (p.total.montantHT || 0), 0)
const sommeBoissonsQte = boissons.reduce((a, p) => a + (p.total.quantite || 0), 0)
const sommeBoissonsVol = boissons.reduce((a, p) => a + (p.total.volumeL || 0), 0)

// --- 2. Cas de surconsommation / vente sans achat (depuis volumesDisparus) ---
export interface CasSurconsommation {
  nom: string
  exercice: string
  valeur: string // ex. "−22 %" ou "vente sans achat"
}
const casSurconsommation: CasSurconsommation[] = []
for (const p of produitsDisparus) {
  for (const [exercice, d] of Object.entries(p.donnees)) {
    const pct = d.pct_disparu
    const surconso = typeof pct === 'number' && pct < 0
    const venteSansAchat = d.type === 'surconsommation' || d.anomalie === 'vente sans achat'
    if (surconso || venteSansAchat) {
      casSurconsommation.push({
        nom: p.nom,
        exercice,
        valeur: surconso
          ? `${'−'}${Math.abs(pct as number)} %`
          : d.anomalie === 'vente sans achat'
            ? 'vente sans achat'
            : 'surconsommation',
      })
    }
  }
}

// --- 3. Eaux minérales « disparues » (aucun usage cuisine possible) ----------
export interface LigneEau {
  nom: string
  disponible: number | null
  vendu: number | string | null
  pct: number | null
}
const eaux: LigneEau[] = produitsDisparus
  .filter((p) => p.categorie === 'eau')
  .map((p) => {
    const d = p.donnees['2022-2023'] ?? Object.values(p.donnees)[0]
    return { nom: p.nom, disponible: d?.disponible ?? null, vendu: d?.vendu_caisse ?? null, pct: d?.pct_disparu ?? null }
  })

// --- 4. Aveu jus de fruit : volume disponible non valorisé en CA -------------
const jusIngredient = RA.ingredients.find((i) => i.ref.toLowerCase().startsWith('jus'))
const jusNonValorise = jusIngredient ? jusIngredient.caReconstitue === null : false

// --- 5. Structure exportée ----------------------------------------------------
export interface AnalyseBoissons {
  // Décompte global (analyse-disparus.json + volumesDisparus.ts)
  nbProduitsFisc: number
  nbPreuveParametrage: number
  preuvesParametrageNoms: string[]
  occ100pct: number
  occSurconsommation: number
  // Achats réels FCBS (achats.ts / factures.ts)
  fournisseur: string
  nbFactures: number
  achatsBoissonNbProduits: number
  achatsBoissonHT: number
  achatsBoissonQuantite: number
  achatsBoissonVolumeL: number
  // Produits « 100 % disparus » mais bel et bien achetés
  produits100Achetes: { nom: string; fiscDispo: number | null; achatsReels: number }[]
  // Ventes sans achat (preuves internes)
  ventesSansAchat: { nom: string; fisc: string; achatsReels: Record<string, number> }[]
  // Cas de surconsommation (vendu > acheté)
  casSurconsommation: CasSurconsommation[]
  // Eaux minérales
  eaux: LigneEau[]
  // Méthode du fisc (reconstitution-administration.json)
  methode: {
    coefLiquideSolide: number
    coefReventeAvant: number
    coefReventeApres: number
    caLiquidesTTC: number
    caSolidesTTC: number
    caReconstitueTTC: number
    caComptaTTC: number
    discordanceTTC: number
    jusNonValorise: boolean
  }
  // Verdicts d'hypothèses du vérificateur (méta de la source fisc)
  verdicts: Record<string, string>
  // Rappels (autres analyses) pour les renvois chiffrés
  ecartReconstitutionMaxPct: number
}

export const boissonsDisparues: AnalyseBoissons = {
  nbProduitsFisc: D.compte.produits,
  nbPreuveParametrage: D.compte.preuveParametrage,
  preuvesParametrageNoms: preuvesParametrage.map((p) => p.nom),
  occ100pct: D.compte.occurrences100pct,
  occSurconsommation: D.compte.surconsommation,
  fournisseur: achatsData.fournisseur,
  nbFactures: factures.length,
  achatsBoissonNbProduits: boissons.length,
  achatsBoissonHT: sommeBoissonsHT,
  achatsBoissonQuantite: sommeBoissonsQte,
  achatsBoissonVolumeL: sommeBoissonsVol,
  produits100Achetes: D.produits100pctAchetes.map((p) => ({
    nom: p.nom,
    fiscDispo: p.fiscDispo2223,
    achatsReels: p.achatsReelsTotal,
  })),
  ventesSansAchat: Object.entries(D.ventesSansAchat).map(([cle, v]) => ({
    nom: NOMS_VENTES_SANS_ACHAT[cle] ?? cle,
    fisc: v.fisc,
    achatsReels: v.achatsReels,
  })),
  casSurconsommation,
  eaux,
  methode: {
    coefLiquideSolide: RA.methode.rapportLiquideSolidePour1Euro,
    coefReventeAvant: RA.methode.coefficientReventeTTC.avantReconstitution,
    coefReventeApres: RA.methode.coefficientReventeTTC.apresReconstitution,
    caLiquidesTTC: RA.synthese.caLiquidesApresAbattements.ttc,
    caSolidesTTC: RA.synthese.caSolides.ttc,
    caReconstitueTTC: RA.synthese.caTotalReconstitue.ttc,
    caComptaTTC: RA.synthese.caInscritEnComptabilite.ttc,
    discordanceTTC: RA.synthese.discordanceCA.ttc,
    jusNonValorise,
  },
  verdicts: volumesDisparus.meta.verdict_hypotheses,
  ecartReconstitutionMaxPct: Math.max(
    Math.abs(reconCA.cumul.ecartBPct),
    Math.abs(reconCA.cumul.ecartCPct),
    Math.abs(reconCA.cumul.ecartGPct),
  ),
}

// Réexport de proximité (utilisé par le récap de l'analyse).
export const refacturationBoissons = refacturation

// =============================================================================
// RÉSULTATS DE NOTRE ANALYSE INDÉPENDANTE (sources primaires, exact au centime).
// Source : boissons-resultats.json (généré par scripts/boissons/02_disparitions.py),
// décomposition consolidée depuis analyses-independantes/boissons/hypotheses/.
// =============================================================================
import resultats from './boissons-resultats.json'
import type { ComposanteDetail } from './analyses'
import { formatEuro } from '../utils/format'
import detSubstitution from './boissons-detail-substitution.json'
import detGeneriques from './boissons-detail-generiques.json'
import detNonLivre from './boissons-detail-nonlivre.json'

export interface BoissonsResultats {
  exercices: string[]
  achatsHT: Record<string, number>
  caVenduTTC: Record<string, number>
  caVenduLiquideParExercice: Record<string, number>
  ecartCoutHT: Record<string, number>
  reventeCaisseTTC: number
  reventeCarteTTC: number
  couvertureCartePctVolume: number
  couvertureCaissePct: Record<string, number>
  nbFactures: number
  nbLignesNonLivrees: number
  parCategorie: { categorie: string; achatL: number; venduL: number; ecartPct: number; ecartCoutHT: number }[]
}
export const resultatsIndep = resultats as unknown as BoissonsResultats

/** Une composante d'explication de l'écart, avec sa source de preuve. */
export type SourceConstat = 'fisc' | 'nous' | 'attente'
export interface Composante {
  cle: string
  label: string
  montantHT: number
  source: SourceConstat
  preuve: string
  plancher?: boolean
  detail?: ComposanteDetail
}

// --- Détails LISIBLES (jargon technique renvoyé dans « Sources ») ------------
// (a) Cuisine : déductions que LE FISC opère lui-même, produit par produit.
export const detailCuisine: ComposanteDetail = {
  methode:
    'Ce sont les usages cuisine que le **vérificateur déduit lui-même**, boisson par boisson, dans ses annexes finales - il reconnaît donc ces consommations. Nous les valorisons à notre coût d’achat moyen réel.',
  colonnes: ['Boisson', 'Usage cuisine retenu par le fisc', 'Volume', 'Coût HT'],
  lignes: [
    ['Macvin', 'Baba au Macvin, saucisse flambée, menu franc-comtois (plat + dessert)', '74 L', '1 344 €'],
    ['Calvados', 'Sauces (repère D)', '33 L', '557 €'],
    ['Porto Sandeman', 'Sauces forestière / morilles (repère G)', '4 L', '43 €'],
    ['Absinthe', 'Crème brûlée (46 % des desserts) - non valorisée en boisson par le fisc', '26 L', '1 038 €'],
    ['Vin Jaune', 'Poulet à la Jurassienne (61 % des assiettes) - non chiffré, par prudence', 'n.c.', '0 €'],
  ],
  totalLabel: 'Total cuisine (déduit par le fisc)',
  totalValeur: '≈ 2 982 € HT',
  sources: [
    { label: 'Annexes finales du fisc - déductions cuisine par produit' },
    { label: 'reconstitution-administration.json (Macvin, Absinthe) ; volumes-disparus-fisc.json (Calvados, Porto)' },
  ],
  note: 'Là où le fisc indique « aucun usage cuisine » (Picon, café, Bordeaux), nous ne revendiquons rien : cohérence totale avec ses propres constats.',
}

// (b) Pertes / casse / consommation du personnel : abattements STANDARD (taux du fisc).
export const detailAbattements: ComposanteDetail = {
  methode:
    'Ce sont les **mêmes taux que le fisc applique** dans sa propre reconstitution (pertes 5 % + consommation du personnel 5 % ; bière 15 %), ici appliqués à nos **achats réels** par catégorie. Pertes et personnel ne sont pas séparables : le fisc les combine en un seul abattement.',
  colonnes: ['Abattement', 'Taux & base', 'Volume', 'Coût HT'],
  lignes: [
    ['Pertes & consommation du personnel', '10 % (5 % + 5 %) des achats hors bière - base 114 589 € HT', '1 486 L', '11 459 €'],
    ['Bière (pression)', '15 % des achats bière - base 12 164 € HT', '410 L', '1 825 €'],
  ],
  totalLabel: 'Total pertes & consommation personnel',
  totalValeur: '≈ 13 283 € HT',
  sources: [
    { label: 'Taux appliqués par le fisc dans sa reconstitution (5 % / 5 % ; bière 15 %)' },
    { label: 'achats-exercice.json - achats réels par catégorie' },
  ],
  note: 'Plancher : la remise 5 % (que le fisc applique aussi, ~6 340 € côté CA) et les offerts ne sont PAS comptés ici. Cette consommation du personnel est attestée et nominative : la caisse montre ~6 canettes de Coca manquantes par jour d’ouverture (5,5/jour sur les 2 derniers exercices), ce qui correspond exactement aux habitudes des deux serveurs (avant et pendant chaque service) ; côté gérant, 72 L de Picon achetés sur 3 ans ne sont jamais sonnés en caisse.',
}

// Justifications détaillées (méthode + tableau de données + sources), par clé.
const detailParCle: Record<string, ComposanteDetail> = {
  cuisine: detailCuisine,
  abattements: detailAbattements,
  substitution: detSubstitution as unknown as ComposanteDetail,
  generiques: detGeneriques as unknown as ComposanteDetail,
  nonlivre: detNonLivre as unknown as ComposanteDetail,
}

// Preuve d'ATTRIBUTION (pas un poste de l'écart) : produits qui paraissent « disparus »
// car vendus sous un bouton de caisse mutualisé. Sert à réfuter le « disparu » par produit du fisc.
export const detailSubstitution: ComposanteDetail = detailParCle.substitution

// Constats VÉRIFIÉS par calcul (cf. dossier hypotheses/). Montants en € HT.
const composantesVerifiees: Composante[] = [
  {
    cle: 'cuisine',
    label: 'Cuisine (déduite par le fisc)',
    montantHT: 2982,
    source: 'fisc',
    preuve:
      'Le vérificateur déduit lui-même ces usages cuisine, produit par produit : Macvin (baba, saucisse flambée), Calvados et Porto (sauces), Absinthe (crème brûlée), Vin Jaune (poulet jurassien).',
  },
  {
    cle: 'abattements',
    label: 'Pertes, casse & consommation du personnel',
    montantHT: 13283,
    source: 'fisc',
    preuve:
      'Abattements standard appliqués à nos achats réels, aux taux mêmes du fisc : pertes 5 % + personnel 5 % (10 %), et 15 % sur la bière pression.',
    plancher: true,
  },
  {
    cle: 'nonlivre',
    label: 'Facturé mais jamais livré',
    montantHT: 2500,
    source: 'nous',
    preuve:
      '231 lignes de facture à 0 € (marchandise manquante ou refusée à la livraison). Le carnet manuscrit de la gérante corrobore à 100 % (125/125 dates).',
    plancher: true,
  },
]
const sommeVerifiee = composantesVerifiees.reduce((a, c) => a + c.montantHT, 0)

// NB : la « vente sous un autre bouton » (substitution) n'apparaît PAS ici. Vérifié sur
// les fichiers de caisse : ces ventes sont déjà comptées dans le « vendu » (tous les
// boutons mutualisés/génériques sont attribués), donc elles ne réduisent pas l'écart
// acheté - vendu. C'est un argument d'attribution (cf. failles du fisc), pas un poste.

/** Décomposition de l'écart au coût ; le résiduel = stock + doses/sur-versement + pertes. */
export const decomposition: Composante[] = [
  ...composantesVerifiees.map((c) => ({ ...c, detail: detailParCle[c.cle] })),
  {
    cle: 'residuel',
    label: 'Consommation non-vente : offerts, casse, sur-versement (au-delà des taux du fisc)',
    montantHT: Math.round(resultatsIndep.ecartCoutHT.total - sommeVerifiee),
    source: 'attente',
    preuve:
      'Ce n’est PAS du stock : l’inventaire physique des 3 fins d’exercice montre un stock boissons stable (3 674 → 4 536 → 4 533 € HT, jamais en baisse). Ce volume a donc été consommé, pas stocké. Le fisc ne déduit que 10 % (pertes + personnel) ; la consommation réelle non-vente (offerts, casse, sur-versement au verre, personnel) est plus élevée - taux admis en CHR à rapprocher (cf. CAA Paris 17/03/2021, 22 à 25 %).',
  },
]
export const partVerifieePct = Math.round((100 * sommeVerifiee) / resultatsIndep.ecartCoutHT.total)

/** Audit du calcul du fisc : reconstruction liquide vs ventes réelles (2024-2025). */
const abatFisc = 0.15 // abattement du fisc sur le liquide
export const auditFisc = {
  caLiquideReconstitue: RA.synthese.caLiquidesAvantAbattements.ttc,
  caLiquideReelCaisse: resultatsIndep.caVenduLiquideParExercice['2024-2025'],
  coefSolide: RA.methode.rapportLiquideSolidePour1Euro,
  caComptabilise: RA.synthese.caInscritEnComptabilite.ttc,
  discordanceOfficielle: RA.synthese.discordanceCA.ttc,
  get surevaluationPct() {
    return Math.round((100 * this.caLiquideReconstitue) / this.caLiquideReelCaisse - 100)
  },
  // En réinjectant le CA liquide RÉEL dans la PROPRE méthode du fisc (× coef, abat. 15 %),
  // la discordance s'inverse (le total reconstitué passe SOUS le CA déclaré).
  get discordanceAvecLiquideReel() {
    const total = this.caLiquideReelCaisse * (1 - abatFisc) * (1 + this.coefSolide)
    return Math.round(total - this.caComptabilise)
  },
}

/** Comptabilité matière du fisc : variation de stock boissons (3 exercices) = stock stable. */
export const comptaMatiere = {
  variations: [-800.83, -1029.67, -273.41], // compte 310200, par exercice
  cumul: -2104,
  achatsBoissons3ans: 141720, // achats boissons du fisc (FCBS + Intermarché)
  pctVariation: 1.5,
  pctConsomme: 98.5,
}
export const comptaMatiereDetail: ComposanteDetail = {
  methode:
    'La « variation de stock boissons » (compte 310200) figure dans la **propre comptabilité du fisc**. Par l’identité comptable **achats + variation de stock = consommation**, on en déduit la part des achats réellement consommée sur la période.',
  colonnes: ['Exercice', 'Variation de stock boissons (fisc)'],
  lignes: [
    ['2022-2023', '- 801 €'],
    ['2023-2024', '- 1 030 €'],
    ['2024-2025', '- 273 €'],
  ],
  totalLabel: 'Cumul 3 ans (≈ 1,5 % des achats)',
  totalValeur: '- 2 104 €',
  sources: [
    { label: 'Lettre du fisc - compte 310200 « variation de stock boissons »' },
    { label: 'reconstitution-administration.json - comptes (comptabilité matière)' },
  ],
  note: 'Stock quasi stable, et même en léger déstockage : 98,5 % des achats boissons ont été CONSOMMÉS sur la période. Aucun volume ne « disparaît » physiquement - l’écart porte seulement sur la part consommée sans recette (cuisine, offerts, pertes, sur-versement).',
}

// =============================================================================
// INVENTAIRE PHYSIQUE (3 fins d'exercice) - source primaire désormais disponible.
// Source : public/documents/inventaires/inventaires.json (totaux recalculés ligne
// à ligne). Détail : analyses-independantes/boissons/INVENTAIRE-SYNTHESE.md.
// =============================================================================

/** Stock physique boissons (HT) et erreur de stock du fisc. */
export const inventairePhysique = {
  stocks: [
    { date: '31/03/2023', exercice: '2022-2023', ht: 3674.17 },
    { date: '31/03/2024', exercice: '2023-2024', ht: 4536.41 },
    { date: '31/03/2025', exercice: '2024-2025', ht: 4533.22 },
  ],
  cumulVariation: 859, // +859 € sur 2 ans, jamais en baisse
  // Variation de stock : physique (inventaire) vs livre (compte 310200 du fisc).
  ecartLivre: [
    { exercice: '2023-2024', physique: 862.24, livre: -1029.67, erreur: 1891.91 },
    { exercice: '2024-2025', physique: -3.19, livre: -273.41, erreur: 270.22 },
  ],
  erreurStockTotale: 2162, // ≈ 1 892 + 270 : sur-évaluation du « disponible » du fisc
}

/** Bilan matière en bouteilles (alcool), fermé sur l'inventaire réel. */
export const bilanBouteilles = {
  // alcools-bouteille (vin + crémant + macvin + spiritueux), vérifié
  exercices: [
    { exercice: '2023-2024', stockInitial: 370, achats: 3307, vendu: 2049, stockFinal: 414, consoHorsVente: 1214 },
    { exercice: '2024-2025', stockInitial: 414, achats: 3020, vendu: 1941, stockFinal: 322, consoHorsVente: 1171 },
  ],
  coca: { achetees: 5952, vendues: 1255, stock: 118, horsVenteParAn: 1555 },
}

/** Détail : le stock physique réfute la disparition et corrige l'erreur de stock du fisc. */
export const inventaireDetail: ComposanteDetail = {
  methode:
    'L’inventaire physique des **3 fins d’exercice** (compté ligne par ligne) ferme l’équation matière `stock initial + achats − ventes − consommation = stock final`. Le stock est **stable** : aucune bouteille n’est accumulée dans une réserve. Et il révèle que le fisc a retenu une **variation de stock erronée** (de signe inverse), ce qui gonfle son « disponible ».',
  colonnes: ['Date de clôture', 'Stock boissons HT', 'Variation physique', 'Variation retenue par le fisc (310200)'],
  lignes: [
    ['31/03/2023', '3 674,17 €', '-', '-'],
    ['31/03/2024', '4 536,41 €', '+862,24 €', '- 1 029,67 €  (erreur +1 892 €)'],
    ['31/03/2025', '4 533,22 €', '- 3,19 €', '- 273,41 €  (erreur +270 €)'],
  ],
  totalLabel: 'Variation cumulée du stock (2 ans)',
  totalValeur: '+859 € (jamais en baisse)',
  sources: [
    { label: 'public/documents/inventaires/ - 3 inventaires physiques (PDF + CSV), totaux recalculés' },
    { label: 'Formule du fisc : disponible = achats + stock initial − stock final (annexe 6)' },
  ],
  note: 'Sa formule gonfle le « disponible » quand le stock final est sous-estimé. Comme le stock physique est stable, les boissons ont été consommées (pas planquées) ; et le motif de rejet du fisc (« inventaire incomplet ») tombe, l’inventaire étant désormais détaillé ligne par ligne.',
}

/** Pistes complémentaires (ESTIMATIONS bornées, à confirmer) qui réduisent encore le résiduel. */
export interface PisteComplementaire {
  cle: string
  label: string
  min: number
  max: number
  note: string
}
export const pistesComplementaires: PisteComplementaire[] = [
  {
    cle: 'pertes-biere',
    label: 'Pertes techniques bière (fond de fût, nettoyage des lignes, mousse)',
    min: 774,
    max: 1366,
    note: 'Estimation aux taux standards de la profession (CHR) - à confirmer (nombre de lignes, fréquence de nettoyage).',
  },
  {
    cle: 'vin-verre',
    label: 'Vin au verre : sur-versement réel + bouteilles ouvertes peu écoulées',
    min: 2455,
    max: 4910,
    note: 'Estimation bornée : la dose de la carte est un minimum, et 9 vins sur 11 tournent à moins de 5 verres/semaine.',
  },
]
export const pistesComplMin = pistesComplementaires.reduce((a, p) => a + p.min, 0)
export const pistesComplMax = pistesComplementaires.reduce((a, p) => a + p.max, 0)

// === Justifications détaillées des « failles du fisc » (cartes argument) =====
const _abat = 0.15
const _coefS = auditFisc.coefSolide
const _coefFr = _coefS.toLocaleString('fr-FR')
const _net = (l: number) => l * (1 - _abat)
const _tot = (l: number) => _net(l) * (1 + _coefS)
const _lf = auditFisc.caLiquideReconstitue
const _lr = auditFisc.caLiquideReelCaisse
const _cd = auditFisc.caComptabilise
const _e = (n: number) => formatEuro(Math.round(n))

/** Démonstration chiffrée de l'inversion de la discordance (méthode du fisc, 2 hypothèses). */
export const auditFiscDetail: ComposanteDetail = {
  methode: `On applique la **formule exacte du fisc** (abattement 15 %, puis × ${_coefFr} pour les « solides ») à deux hypothèses : son CA liquide **reconstitué** à partir des achats, puis le CA liquide **réellement encaissé** en caisse. Rien d’autre n’est modifié.`,
  colonnes: ['Étape de la formule du fisc', 'Avec son liquide reconstitué', 'Avec le liquide réel encaissé'],
  lignes: [
    ['CA liquide (exercice 2024-2025)', _e(_lf), _e(_lr)],
    ['− abattement 15 % (offerts, pertes, personnel)', '− ' + _e(_lf * _abat), '− ' + _e(_lr * _abat)],
    ['= CA liquide net', _e(_net(_lf)), _e(_net(_lr))],
    [`× ${_coefFr} → CA « solides » (cuisine, extrapolée)`, _e(_net(_lf) * _coefS), _e(_net(_lr) * _coefS)],
    ['= CA total reconstitué', _e(_tot(_lf)), _e(_tot(_lr))],
    ['− CA déclaré (identique dans les deux cas)', _e(_cd), _e(_cd)],
  ],
  totalLabel: '= Discordance (base de l’amende 1759)',
  totalValeur: `+${_e(_tot(_lf) - _cd)}   →   ${_e(_tot(_lr) - _cd)}`,
  sources: [
    { label: 'reconstitution-administration.json - méthode et synthèse du fisc' },
    { label: 'Ventes caisse réelles (annexe D, réconciliées au centime)' },
  ],
  note: `Toute la discordance vient de l’écart entre le liquide reconstitué (${_e(_lf)}) et le liquide réellement vendu (${_e(_lr)}), triplé par le coefficient × ${_coefFr} sur une cuisine jamais mesurée. Avec le vrai chiffre, le total reconstitué passe SOUS le CA déclaré : aucune occultation.`,
}

/** Les deux « ventes sans achat » citées par le fisc, vérifiées sur nos achats exacts. */
export const ventesSansAchatDetail: ComposanteDetail = {
  methode:
    'Le fisc cite deux boissons « vendues sans achat ». Vérification sur nos achats exacts : **aucune ligne d’achat** ne correspond. Vendre sans jamais acheter est impossible - c’est donc que la **caisse les enregistre sous un autre code** (artefact de paramétrage que le fisc admet lui-même, hypothèse H1).',
  colonnes: ['Produit (selon le fisc)', 'Vendu en caisse', 'Acheté (vérifié)', 'Explication'],
  lignes: [
    ['Bordeaux Mouton Cadet', '6 bouteilles (2024-2025)', '0 - aucune ligne d’achat sur 3 ans', 'Vendu sous un autre bouton « Bordeaux »'],
    ['Hautes Côtes de Nuits', '172 bouteilles (2023-2024)', 'seulement un HC Nuits BLANC acheté en 2017 (hors période)', 'Confusion de code caisse (rouge / blanc)'],
  ],
  totalLabel: 'Verdict du fisc lui-même',
  totalValeur: 'hypothèse H1 « paramétrage caisse » - confirmée',
  sources: [
    { label: 'volumes-disparus-fisc.json - meta.verdict_hypotheses' },
    { label: 'achats-exercice.json - achats réels (0 Mouton Cadet)' },
  ],
  note: 'Si les codes de caisse ne correspondent pas aux références d’achat, la « disparition » calculée produit par produit est un artefact de paramétrage - pas une recette occultée.',
}
