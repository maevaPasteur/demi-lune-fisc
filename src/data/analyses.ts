// =============================================================================
// CATALOGUE DES ANALYSES (modèle de contenu)
// -----------------------------------------------------------------------------
// Chaque analyse est décrite par une suite de "sections" (paragraphe, KPIs,
// tableau, graphique, alerte, note) rendues génériquement par <AnalyseContent>.
// Les CHIFFRES proviennent exclusivement de analyseDel.ts / analyseIntegrite.ts
// / analyseComplements.ts (source unique, recalculée par script) - aucune valeur
// n'est saisie en dur dans les pages. Le texte d'argumentation vit ici (couche
// données), pas dans les composants. Emphase: encadrer un fragment de **gras**.
// =============================================================================


import { integrite as I } from './analyseIntegrite'
import { complements as K } from './analyseComplements'
import { reconstitution as R } from './analyseReconstitution'

import { boissonsPageData as BPD } from './boissonsPageData'
import {
  comptaMatiere,
  inventairePhysique,
} from './analyseBoissons'
import { groupes, CARTES_SLUG, FACTURES_SLUG, INVENTAIRES_SLUG } from './documents'
import {
  formatEuro,
  formatEuroPrecis,
  formatInt,
  formatPct,
} from '../utils/format'

// --- Types du modèle de section ----------------------------------------------
export interface KpiItem {
  label: string
  valeur: string
  sub?: string
  highlight?: boolean
  couleur?: string
}
export interface Cellule {
  v: string
  align?: 'left' | 'right' | 'center'
  fw?: number
  badge?: 'ok' | 'ko'
  href?: string // fichier à télécharger ou lien externe -> Anchor (nouvel onglet)
  to?: string // route interne (ex. /rendu-final/...) -> Link SPA
}
export interface Colonne {
  label: string
  align?: 'left' | 'right' | 'center'
}
export type LigneGraphique = Record<string, string | number>

// Table partagée reconstituée (addition d'origine répartie sur N notes de même total).
export interface PartageTable {
  heure: string
  nb_notes: number
  total_par_note: number
  total_table: number
  notes: string[]
  articles: { lib: string; qte: number }[]
  fractionne: boolean
}
// Une suppression du jour : heure, montant, article(s) au même prix, nature.
export interface SuppressionLigne {
  heure: string
  montant: number
  articles: string[]
  nature: string
}
// Ventilation à 100 % des suppressions d'une journée, par nature.
export interface BilanSuppressions {
  faute_frappe: { n: number; somme: number }
  article: { n: number; somme: number }
  compose: { n: number; somme: number }
}
// Croisement d'une journée : suppressions (D), ventes par table (T+lignes A), modifications (M).
export interface ReconLigne { nom: string; lib: string; qte: number; pu: number; montant: number; modifie: boolean }
export interface ReconTable {
  nom: string; note: string; heure: string; total: number
  partagee: boolean; jumelles: string[]
  lignes: ReconLigne[]; modifications: string[]; suppressions: string[]; nb_suppressions: number
}
export interface ReconSuppression { nom: string; heure: string; montant: number; table: string | null; statut: string; confiance: string | null }
export interface ReconModif { nom: string; heure: string; table: string; article: string; prix: number; prix_ref: number[] }
export interface ReconEvenement { type: string; tables: string[]; total: number; modifications: string[]; suppressions: string[]; explication: string }
export interface Reconciliation {
  suppressions: ReconSuppression[]
  modifications: ReconModif[]
  tables: ReconTable[]
  evenements: ReconEvenement[]
  bilan_rattachement: Record<string, { n: number; somme: number }>
  restantes: string[]
  total_somme: number
  nb_tables_partagees: number
}
// Journée avec ses tables partagées (pour la popin de justification des suppressions).
export interface JourPartage {
  date: string
  nb_notes: number
  nb_partages: number
  nb_notes_partagees: number
  nb_suppressions: number
  suppr_somme: number
  bilan: BilanSuppressions
  partages_valeur: number
  menus_forfait: { notes: number; somme: number }
  suppressions: SuppressionLigne[]
  suppr_par_heure: { heure: string; n: number }[]
  partages: PartageTable[]
  reconciliation: Reconciliation
}

// Justification détaillée d'une composante de décomposition (méthode + tableau + sources).
export interface ComposanteDetail {
  methode: string
  colonnes: string[]
  lignes: string[][]
  totalLabel: string
  totalValeur: string
  sources: { label: string }[]
  note?: string
}

export type Section =
  | { kind: 'paragraphe'; texte: string }
  // Titre intermédiaire (sous-section), plus léger qu'un 'chapitre'.
  // Avec 'numero' (ex. "2.1") il est plus grand et préfixé ; sans, il est plus discret.
  | { kind: 'titre'; texte: string; numero?: string }
  | { kind: 'alerte'; couleur: string; titre: string; texte: string }
  | { kind: 'kpis'; items: KpiItem[] }
  // Panneau encadré (fond gris) regroupant un titre et une rangée de KPI.
  // Sert à présenter un second niveau de lecture sous une première rangée de KPI.
  | { kind: 'panneauKpis'; titre?: string; sousTitre?: string; items: KpiItem[] }
  | { kind: 'tableau'; titre?: string; minWidth?: number; colonnes: Colonne[]; lignes: Cellule[][] }
  // Grille de tuiles « table » (plan de salle) : chaque case = une table avec son
  // numéro et son type (réelle / virtuelle), rendue avec une icône.
  | {
      kind: 'grilleTables'
      titre?: string
      sousTitre?: string
      // variante 'plan' = plan de salle (réelle/virtuelle/inexistante) ;
      // variante 'notes' = cartes par numéro de note avec le total d'encaissements.
      variante?: 'plan' | 'notes'
      tables: {
        numero: string
        type?: 'reelle' | 'virtuelle' | 'inexistante' | 'rare'
        total?: number
        couverts?: number
        note?: string
      }[]
      // Pied de carte : nombre de tables réellement utilisées et total de couverts.
      resume?: { tables: number; couverts: number }
    }
  // Graphique multi-lignes (ex. couverts/semaine, 1 ligne par exercice).
  // L'axe X est numérique (semaine de l'exercice) ; moisTicks place les
  // étiquettes de mois (Avril → Mars) aux semaines de début de mois.
  | {
      kind: 'graphiqueLignes'
      titre?: string
      sousTitre?: string
      hauteur: number
      dataKey: string
      series: { name: string; couleur: string }[]
      data: LigneGraphique[]
      format: 'euro' | 'int'
      moisTicks?: { tick: number; label: string }[]
      // Tooltip personnalisé : si défini, l'en-tête du tooltip affiche le champ
      // `periode` du point survolé (ex. « 01/11 - 07/11 ») suivi de ce sous-titre,
      // au lieu de la valeur brute de l'axe X (le numéro de semaine).
      tooltipSousTitre?: string
    }
  | {
      kind: 'graphique'
      variante: 'vertical' | 'horizontal'
      hauteur: number
      dataKey: string
      serie: { name: string; couleur: string }
      data: LigneGraphique[]
      format: 'euro' | 'int'
    }
  | { kind: 'note'; texte: string }
  // Bande de chapitre : marque visuellement « qui parle » (le fisc vs notre analyse).
  | { kind: 'chapitre'; source: 'fisc' | 'nous' | 'neutre'; titre: string; sousTitre?: string; numero?: number }
  // Décomposition d'un montant en composantes (barre + cartes), avec source de preuve
  // et une justification détaillée dépliable (méthode + tableau de données + sources).
  | {
      kind: 'decomposition'
      total: number
      items: {
        cle: string
        label: string
        montantHT: number
        source: 'fisc' | 'nous' | 'attente'
        preuve: string
        plancher?: boolean
        detail?: ComposanteDetail
      }[]
    }
  | { kind: 'sources'; items: { slug: string; label: string }[] }
  // Pièce(s) téléchargeable(s) - lien direct vers un fichier de public/documents.
  | { kind: 'piecejointe'; intro?: string; fichiers: { fichier: string; label: string }[] }
  | {
      kind: 'argument'
      titre: string
      page?: string
      accusation: string
      faille: string
      cote: string
      preuves: { to: string; label: string }[]
      pieces: { to: string; label: string }[]
      detail?: ComposanteDetail
    }
  // Encart de TRAVAIL INTERNE (jamais destiné au fisc) : note/action pour
  // l'exploitant, le comptable ou l'avocat (pièce manquante, vérif à faire…).
  // Rendu visuellement distinct (bordure pointillée) et filtrable d'un bloc.
  | { kind: 'interne'; audience: 'restaurant' | 'comptable' | 'avocat'; titre: string; texte: string }
  // Barre de composition horizontale (100 %) : segments proportionnels colorés
  // par catégorie (mesuré / calculé / estimé / résiduel), + légende chiffrée.
  // Sert à visualiser une réconciliation (cascade, bancarisation) SANS trucage
  // d'axe : tout part de 0 et somme au total affiché.
  | {
      kind: 'barreComposition'
      titre?: string
      sousTitre?: string
      unite: string
      total?: number
      segments: { label: string; valeur: number; categorie: 'mesure' | 'calcul' | 'estime' | 'residuel' | 'neutre' | 'alerte' }[]
      legende?: boolean
    }
  // Graphique à barres empilées (Mantine BarChart), plusieurs séries. Axe à 0.
  | {
      kind: 'graphiqueEmpile'
      titre?: string
      hauteur: number
      dataKey: string
      series: { name: string; couleur: string }[]
      data: LigneGraphique[]
      type?: 'stacked' | 'default'
      format: 'euro' | 'int'
    }
  // Justification des suppressions : tableau de journées + œil ouvrant une popin
  // qui reconstitue les TABLES PARTAGÉES du jour (article par article).
  | { kind: 'joursPartages'; intro?: string; jours: JourPartage[] }
  // Suppressions par CAS : chaque exemple est une fiche montrant les suppressions
  // (date/heure/montant) puis l'encaissement correspondant (note, contenu détaillé).
  | { kind: 'casSuppressions'; cas: CasSuppression[] }
  // Couverts moyens/jour par semaine (cycle mars->février), 1 ligne/exercice,
  // avec bandes de capacité à 58 % colorées par saison (terrasse / intérieur).
  | {
      kind: 'couvertsCapacite'
      titre?: string
      sousTitre?: string
      dataKey: string
      series: { name: string; couleur: string }[]
      midi: LigneGraphique[]
      soir: LigneGraphique[]
      moisTicks?: { tick: number; label: string }[]
      zones: { x1: number; x2: number; seuil: number; espace: 'interieur' | 'terrasse' }[]
      seuilInterieur: number
      seuilTerrasse: number
      capaciteInterieur: number
      capaciteTerrasse: number
      occupationMois?: {
        mois: string
        espace: string
        pct: number | null
        pctMidi: number | null
        pctSoir: number | null
      }[]
      occupationMoyenne?: number
      moyenneFrance?: number
      ecartMoyenneFrancePct?: number
    }
  // Couverts par jour pour une saison (3 mois) : à gauche deux courbes empilées
  // (soir en haut, midi en bas, 1 ligne par exercice), à droite la moyenne de
  // couverts par midi/soir, mois par mois ET exercice par exercice (services à 0 exclus).
  | {
      kind: 'saisonCouverts'
      titre: string
      sousTitre?: string
      dataKey: string
      series: { name: string; couleur: string }[]
      soir: LigneGraphique[]
      midi: LigneGraphique[]
      moisTicks?: { tick: number; label: string }[]
      stats: {
        mois: string
        parExercice: { exo: string; midis: number; soirs: number; moyMidi: number; moySoir: number }[]
      }[]
    }

export interface CasItem {
  lib: string
  qte: number
  pu: number
  montant: number
  highlight?: boolean
}
export interface CasNote {
  label: string
  heure: string
  total: number
  items: CasItem[]
  highlight?: string
}
export interface CasExemple {
  date: string
  article?: string
  suppressions: { heure: string; montant: number; devient?: string; tables?: string[] }[]
  notes: CasNote[]
}
export interface CasSuppression {
  id: string
  titre: string
  preuve: string
  description: string
  exemples: CasExemple[]
}

export interface Analyse {
  slug: string
  eyebrow: string
  titre: string
  resume: string
  force: 'forte' | 'moyenne'
  apercu: KpiItem[]
  sections: Section[]
  // Carte "levier" de la liste /analyses (facultatif).
  controleurDit?: string
  demonstration?: string
  faitTomber?: string
  pieces?: { to: string; label: string }[]
}

// Helpers de cellule.
const cg = (v: string): Cellule => ({ v })
const cd = (v: string): Cellule => ({ v, align: 'right' })
// Écart signé en % ("+0,017 %", "−0,005 %") et en euros, pour les tableaux.
const ecPct = (v: number): string => (v > 0 ? '+' : '') + formatPct(v, 3)
const ecEuro = (v: number): string => (v >= 0 ? '+' : '') + formatEuro(v)
const enClair = (texte: string): Section => ({ kind: 'alerte', couleur: 'blue', titre: 'En clair', texte })
const retenir = (texte: string): Section => ({ kind: 'alerte', couleur: 'teal', titre: 'Ce qu’il faut retenir', texte })
// Liens vers les pièces du dossier (pages /documents/:slug), résolus par lettre
// d'annexe - le slug d'URL et le titre viennent de documents.ts (source unique).
const sources = (...lettres: string[]): Section => ({
  kind: 'sources',
  items: lettres
    .map((l) => groupes.find((g) => g.lettre === l))
    .filter((g): g is (typeof groupes)[number] => Boolean(g))
    .map((g) => ({ slug: g.slug, label: `Annexe ${g.lettre} - ${g.titre}` })),
})
// Liens "pièces liées" (vers /documents/:slug), résolus par lettre d'annexe.
const piecesLiees = (...lettres: string[]): { to: string; label: string }[] =>
  lettres
    .map((l) => groupes.find((g) => g.lettre === l))
    .filter((g): g is (typeof groupes)[number] => Boolean(g))
    .map((g) => ({ to: `/documents/${g.slug}`, label: `Annexe ${g.lettre}` }))

// ===================== ANALYSE 0 - RECONSTITUTION DU CA ======================
// Écart maximal (en valeur absolue) des reconstitutions au CA déclaré, sur le cumul.
const ecartMaxRecon = Math.max(
  Math.abs(R.cumul.ecartBPct),
  Math.abs(R.cumul.ecartCPct),
  Math.abs(R.cumul.ecartHPct),
  Math.abs(R.cumul.ecartGPct),
)
const reconstitution: Analyse = {
  slug: 'reconstitution-ca',
  eyebrow: 'Preuve maîtresse',
  titre: 'Reconstitution intégrale du chiffre d’affaires',
  resume:
    'Recalculé depuis la caisse par cinq chemins indépendants, le chiffre d’affaires retombe sur le montant déclaré. Les cinq exports concordent avec le montant déclaré ; les règlements portés sur 37 tickets à 0,00 € sont exposés à part (réponse, point 2.2.5 c).',
  force: 'forte',
  controleurDit:
    'Le chiffre d’affaires déclaré serait minoré : reconstitution alléguée de +471 826 € de recettes.',
  demonstration:
    'Cinq exports indépendants reconstituent le CA déclaré à 0,1 % près. Les cinq exports concordent avec le montant déclaré ; les règlements portés sur 37 tickets à 0,00 € sont exposés à part (réponse, point 2.2.5 c).',
  faitTomber: 'La reconstitution du fisc - 471 826 €',
  pieces: piecesLiees('B', 'C', 'H', 'G', 'A'),
  apercu: [
    { label: 'Exports qui convergent', valeur: String(R.sourcesCount) },
    { label: 'Écart max au CA déclaré (3 ans)', valeur: formatPct(ecartMaxRecon, 2) },
  ],
  sections: [
    enClair(
      'Plutôt que d’estimer le chiffre d’affaires, on l’a recalculé depuis la caisse par **cinq chemins indépendants** : chaque plat, chaque ticket, chaque en-tête, le journal de TVA, et la synthèse déclarée. Les cinq tombent sur le même montant. Les règlements portés sur 37 tickets à 0,00 € sont exposés à part (réponse, point 2.2.5 c).',
    ),
    {
      kind: 'paragraphe',
      texte: `**Cinq exports indépendants** de la caisse reconstituent le même chiffre d’affaires sur trois exercices : le détail des plats (${formatInt(R.lignesTotal)} lignes), le détail des tickets, les en-têtes de tickets, le journal de TVA et la synthèse déclarée. Tous tiennent dans une fourchette de **${formatPct(ecartMaxRecon, 2)}** autour du CA déclaré de **${formatEuro(R.cumul.caDeclare)}**.`,
    },
    {
      kind: 'kpis',
      items: [
        { label: 'CA déclaré (A)', valeur: formatEuro(R.cumul.caDeclare), sub: 'synthèse déclarée' },
        { label: 'Détail des plats (B)', valeur: formatEuro(R.cumul.reconstitutionB), sub: ecPct(R.cumul.ecartBPct) },
        { label: 'Tickets, détail = en-têtes (C = H)', valeur: formatEuro(R.cumul.reconstitutionC), sub: ecPct(R.cumul.ecartCPct) },
        { label: 'Journal de TVA (G)', valeur: formatEuro(R.cumul.reconstitutionG), sub: ecPct(R.cumul.ecartGPct), highlight: true, couleur: 'teal' },
      ],
    },
    {
      kind: 'tableau',
      titre: 'Cinq reconstitutions indépendantes',
      minWidth: 720,
      colonnes: [
        { label: 'Source' },
        { label: '2022-2023', align: 'right' },
        { label: '2023-2024', align: 'right' },
        { label: '2024-2025', align: 'right' },
        { label: 'Cumul 3 ans', align: 'right' },
        { label: 'Écart', align: 'right' },
      ],
      lignes: [
        [cg('CA déclaré (A)'), ...R.parExercice.map((e) => cd(formatEuro(e.caDeclare))), { v: formatEuro(R.cumul.caDeclare), align: 'right', fw: 700 }, cd('-')],
        [cg('Détail plats (B)'), ...R.parExercice.map((e) => cd(formatEuro(e.reconstitutionB))), cd(formatEuro(R.cumul.reconstitutionB)), cd(ecPct(R.cumul.ecartBPct))],
        [cg('Détail tickets (C)'), ...R.parExercice.map((e) => cd(formatEuro(e.reconstitutionC))), cd(formatEuro(R.cumul.reconstitutionC)), cd(ecPct(R.cumul.ecartCPct))],
        [cg('En-têtes tickets (H)'), ...R.parExercice.map((e) => cd(formatEuro(e.reconstitutionH))), cd(formatEuro(R.cumul.reconstitutionH)), cd(ecPct(R.cumul.ecartHPct))],
        [cg('Journal de TVA (G)'), ...R.parExercice.map((e) => cd(formatEuro(e.reconstitutionG))), cd(formatEuro(R.cumul.reconstitutionG)), cd(ecPct(R.cumul.ecartGPct))],
      ],
    },
    {
      kind: 'paragraphe',
      texte: `Les écarts annuels (quelques milliers d’euros) sont de **signe alterné** (${R.parExercice.map((e) => ecEuro(e.reconstitutionH - e.caDeclare)).join(' / ')}) et se compensent sur le cumul. Une minoration systématique irait toujours dans le même sens : ce n’est pas le cas. Ils tiennent au seul décalage des journées à cheval sur la clôture du 31 mars.`,
    },
    {
      kind: 'paragraphe',
      texte: `Sur ces **${formatInt(R.lignesTotal)} lignes de vente**, **${formatInt(R.surfacturationCount)}** n’a été facturée au-dessus du tarif catalogue. La caisse ne possède aucun mécanisme qui *ajoute* de la recette : les seuls écarts au tarif sont des **remises** (${formatInt(R.remisesCount)} lignes, ${formatEuro(R.remisesSomme)} sur 3 ans) qui *diminuent* le chiffre d’affaires.`,
    },
    {
      kind: 'kpis',
      items: [
        { label: 'Lignes facturées au-dessus du tarif', valeur: formatInt(R.surfacturationCount), sub: `sur ${formatInt(R.lignesTotal)} lignes`, highlight: true, couleur: 'teal' },
        { label: 'Remises consenties (3 ans)', valeur: formatEuro(R.remisesSomme), sub: 'baissent le CA' },
        { label: 'Lignes au tarif exact', valeur: formatPct(R.pctExact), sub: 'aucune majoration' },
      ],
    },
    {
      kind: 'paragraphe',
      texte: `Le fisc qualifie d’« écarts inexpliqués » (motif n°2 du rejet) des sommes chiffrées à **${formatEuro(R.ecartFiscTotal)}** sur trois ans. **Ce sont, au centime près, nos remises** - les réductions consenties (plats partagés, recettes modifiées), documentées par la gérante. Rien d’« inexpliqué ».`,
    },
    {
      kind: 'tableau',
      titre: '« Écarts inexpliqués » du fisc = nos remises documentées',
      minWidth: 520,
      colonnes: [
        { label: 'Exercice' },
        { label: 'Écart « inexpliqué » (fisc)', align: 'right' },
        { label: 'Nos remises (annexe B)', align: 'right' },
      ],
      lignes: [
        ...R.parExercice.map((e) => [cg(e.exercice), cd(formatEuro(e.ecartFisc)), cd(formatEuro(e.remises))]),
        [
          { v: 'Cumul 3 ans', fw: 700 },
          { v: formatEuro(R.ecartFiscTotal), align: 'right', fw: 700 },
          { v: formatEuro(R.remisesSomme), align: 'right', badge: 'ok' },
        ],
      ],
    },
    retenir(
      `Le chiffre d’affaires déclaré n’est pas une estimation : **cinq exports indépendants** le reconstituent, tous à moins de ${formatPct(ecartMaxRecon, 2)} près sur trois ans. Toute reconstitution extrapolée (coefficients, ratios de marge) est démentie par les données réelles.`,
    ),
    sources('B', 'C', 'H', 'G', 'A'),
  ],
}

// ======================= ANALYSE 1 - SUPPRESSIONS (DEL) ======================

// ======================= ANALYSE 2 - CONTINUITÉ NF525 ========================
const C = I.continuite
const continuite: Analyse = {
  slug: 'continuite-nf525',
  eyebrow: 'Intégrité',
  titre: 'Continuité des tickets de la caisse',
  resume:
    'La numérotation séquentielle et ininterrompue des tickets Z et des événements établit qu’aucune journée et aucun événement ne manquent dans les fichiers ; elle ne dit rien, à elle seule, des tables vidées, refermées dans une seconde série de tickets.',
  force: 'forte',
  controleurDit:
    'Les suppressions prouveraient une caisse manipulable, des recettes effaçables.',
  demonstration:
    '659 tickets-Z et 23 339 événements numérotés sans aucun trou. Aucune journée, aucun ticket, aucun événement n’a pu être effacé.',
  faitTomber: 'La continuité des tickets de la caisse',
  pieces: piecesLiees('E', 'H'),
  apercu: [
    { label: 'Tickets-Z sans trou', valeur: formatInt(C.zTotal) },
    { label: 'Événements sans trou', valeur: formatInt(C.idTotal) },
  ],
  sections: [
    enClair(
      'Chaque journée de service se clôture par un « ticket Z » numéroté qui fige les recettes du jour. Les rapports Z sont numérotés à la suite. Il suffit donc de vérifier que la numérotation ne comporte aucun trou - et c’est le cas, du premier au dernier jour.',
    ),
    {
      kind: 'paragraphe',
      texte:
        'La caisse numérote ses tickets-Z et chacun de ses événements de façon **séquentielle et inaltérable**. Un seul numéro manquant trahirait une journée ou une opération effacée. Sur trois exercices : **aucun trou**.',
    },
    {
      kind: 'kpis',
      items: [
        { label: 'Tickets-Z', valeur: formatInt(C.zTotal), sub: `${C.zGlobalMin} → ${C.zGlobalMax}` },
        { label: 'Trous dans les Z', valeur: formatInt(C.zTotalTrous), sub: 'séquence complète', highlight: true, couleur: 'teal' },
        { label: 'Événements journalisés', valeur: formatInt(C.idTotal), sub: `${C.idGlobalMin} → ${C.idGlobalMax}` },
        { label: 'Trous dans les événements', valeur: formatInt(C.idTotalTrous), sub: 'aucun effacement', highlight: true, couleur: 'teal' },
      ],
    },
    {
      kind: 'paragraphe',
      texte: `La continuité ne s’arrête pas aux journées : **à l’intérieur de chaque Z, la numérotation des tickets est complète** (de 1 à N, sans saut) - aucun ticket validé n’a été soustrait. Et **aucun ticket d’avoir ni de remboursement** n’apparaît sur trois ans.`,
    },
    {
      kind: 'kpis',
      items: [
        { label: 'Trous dans les n° de tickets (intra-Z)', valeur: formatInt(C.ticketsIntraZTrousTotal), sub: 'séquence 1…N complète', highlight: true, couleur: 'teal' },
        { label: 'Tickets d’avoir / remboursement', valeur: formatInt(C.avoirsTotal), sub: 'sur 3 exercices', highlight: true, couleur: 'teal' },
      ],
    },
    {
      kind: 'paragraphe',
      texte: `Un seul et même opérateur (**${K.caissier.nom}**) a saisi les **${formatInt(K.caissier.nbTickets)} tickets** des trois exercices : aucune session ni caisse parallèle non identifiée.`,
    },
    ...(C.zChaineInterExercices && C.idChaineInterExercices
      ? [
          {
            kind: 'paragraphe' as const,
            texte:
              'La numérotation se **poursuit sans rupture d’un exercice à l’autre** : le dernier ticket-Z d’un exercice précède immédiatement le premier du suivant. Impossible d’insérer ou de retirer une journée entre deux exercices.',
          },
        ]
      : []),
    {
      kind: 'tableau',
      titre: 'Détail par exercice',
      minWidth: 760,
      colonnes: [
        { label: 'Exercice' },
        { label: 'Tickets-Z', align: 'right' },
        { label: 'Trous Z', align: 'right' },
        { label: 'Trous tickets', align: 'right' },
        { label: 'Avoirs', align: 'right' },
        { label: 'Événements', align: 'right' },
        { label: 'Trous évts', align: 'right' },
      ],
      lignes: C.parExercice.map((e) => [
        cg(e.exercice),
        cd(`${e.zMin} → ${e.zMax}`),
        { v: formatInt(e.zTrous), align: 'right', badge: e.zTrous === 0 ? 'ok' : 'ko' },
        { v: formatInt(e.ticketsIntraZTrous), align: 'right', badge: e.ticketsIntraZTrous === 0 ? 'ok' : 'ko' },
        { v: formatInt(e.avoirs), align: 'right', badge: e.avoirs === 0 ? 'ok' : 'ko' },
        cd(formatInt(e.evenements)),
        { v: formatInt(e.idTrous), align: 'right', badge: e.idTrous === 0 ? 'ok' : 'ko' },
      ]),
    },
    retenir(
      'Une recette dissimulée briserait forcément l’un de ces compteurs inaltérables (un ticket-Z ou un événement manquant). Aucun n’est rompu : la comptabilité de caisse est complète, sans journée ni opération effacée.',
    ),
    sources('E', 'H'),
  ],
}

// ======================= ANALYSE 3 - BANCARISATION ===========================
const B = I.bancarisation
const bancarisation: Analyse = {
  slug: 'bancarisation',
  eyebrow: 'Impossibilité matérielle',
  titre: 'Un chiffre d’affaires bancarisé',
  resume:
    'Le CA est encaissé quasi intégralement par moyens traçables. La part d’espèces est marginale.',
  force: 'forte',
  controleurDit: 'Les recettes auraient été occultées en espèces.',
  demonstration:
    '98,7 % du chiffre d’affaires est encaissé par des moyens traçables ; les espèces ne pèsent que 1,3 %.',
  faitTomber: 'L’impossibilité matérielle de l’occultation',
  pieces: piecesLiees('A', 'F'),
  apercu: [
    { label: 'Encaissé traçable', valeur: formatPct(B.tracablePct) },
    { label: 'Part des espèces', valeur: formatPct(B.especesPct) },
  ],
  sections: [
    enClair(
      `On ne peut pas cacher un paiement par carte : il laisse une trace à la banque. Seules les espèces sont dissimulables. La question est donc simple : combien d’espèces le restaurant a-t-il encaissé ? À peine ${formatPct(B.especesPct)} de son chiffre d’affaires.`,
    ),
    {
      kind: 'paragraphe',
      texte: `Le restaurant n’encaisse quasiment qu’en monnaie traçable : **${formatPct(B.tracablePct)}** du chiffre d’affaires passe par des moyens traçables (carte, titres-restaurant, chèques), et les espèces ne pèsent que **${formatPct(B.especesPct)}** du CA, soit ${formatEuro(B.especesTotal)} sur trois ans.`,
    },
    {
      kind: 'kpis',
      items: [
        { label: 'CA encaissé traçable', valeur: formatPct(B.tracablePct), sub: 'carte, titres, chèques', highlight: true, couleur: 'teal' },
        { label: 'Part des espèces', valeur: formatPct(B.especesPct), sub: `${formatEuro(B.especesTotal)} sur 3 ans` },
        { label: 'CA total (3 ans)', valeur: formatEuro(B.caTotal), sub: 'règlements enregistrés' },
      ],
    },
    {
      kind: 'graphique',
      variante: 'horizontal',
      hauteur: 260,
      dataKey: 'mode',
      serie: { name: 'Montant', couleur: 'gold.6' },
      format: 'euro',
      data: B.modesTotal.map((m) => ({ mode: m.mode, Montant: m.montant })),
    },
    {
      kind: 'tableau',
      titre: 'Détail par exercice',
      minWidth: 520,
      colonnes: [
        { label: 'Exercice' },
        { label: 'CA TTC', align: 'right' },
        { label: 'Espèces', align: 'right' },
        { label: 'Part espèces', align: 'right' },
        { label: 'Part CB', align: 'right' },
      ],
      lignes: B.parExercice.map((e) => [
        cg(e.exercice),
        cd(formatEuro(e.ca)),
        cd(formatEuro(e.especes)),
        cd(formatPct(e.especesPct)),
        cd(formatPct(e.cbPct)),
      ]),
    },
    {
      kind: 'paragraphe',
      texte: `Le détail le confirme : sur les **${formatInt(K.especes.nb)} règlements en espèces** des trois exercices, le plus élevé atteint **${formatEuro(K.especes.max)}** et la moitié sont inférieurs à **${formatEuroPrecis(K.especes.mediane)}**.`,
    },
    {
      kind: 'kpis',
      items: [
        { label: 'Plus gros règlement espèces (3 ans)', valeur: formatEuro(K.especes.max), sub: 'jamais dépassé' },
        { label: 'Règlement espèces médian', valeur: formatEuroPrecis(K.especes.mediane), sub: 'moitié des paiements en-dessous' },
        { label: 'Nombre de règlements espèces', valeur: formatInt(K.especes.nb), sub: 'sur 3 exercices' },
      ],
    },
    {
      kind: 'paragraphe',
      texte: `À la traçabilité bancaire s’ajoute une preuve **indépendante du restaurant** : **${formatEuro(K.tracableTiers)}** de titres-restaurant et chèques-vacances, remboursés directement par des organismes tiers (Edenred, ANCV) - donc impossibles à minorer.`,
    },
    retenir(
      `${formatPct(B.tracablePct)} du chiffre d’affaires est encaissé par des moyens traçables et vérifiables auprès de tiers (banque, Edenred, ANCV). Le seul canal dissimulable - les espèces - est marginal (${formatPct(B.especesPct)} du CA) et plafonné à de très petits montants.`,
    ),
    sources('A', 'F'),
  ],
}

// --- Catalogue + accès --------------------------------------------------------
// ===================================================================
// ANALYSE BOISSONS DISPARUES - refondue (data-analyst, tout chiffré)
// Données exactes : src/data/boissonsPageData.json (script 15).
// ===================================================================
const eurB = (n: number) => (n ? formatEuro(n) : '-')
const litresB = (n: number | null) => (n != null ? `${formatInt(n)} L` : '-')
const Pp = BPD.consoParPeriode

const recetteStr = (c: (typeof BPD.cocktails)[number]) =>
  c.recette.map((r) => `${r.nom} ${r.cl} cl`).join(' + ')

const ORDRE_CARTES: { carte: string; titre: string }[] = [
  { carte: 'C', titre: 'Période 1 (carte C)' },
  { carte: 'B', titre: 'Période 2 (carte B)' },
  { carte: 'A', titre: 'Période 3 (carte A, actuelle)' },
]

const menusSections: Section[] = ORDRE_CARTES.flatMap(({ carte, titre }) => {
  const c = BPD.menusParPeriode[carte]
  if (!c) return []
  return [
    {
      kind: 'tableau' as const,
      titre: `${titre} - ${c.dates}`,
      minWidth: 760,
      colonnes: [
        { label: 'Menu' },
        { label: 'Service' },
        { label: 'Option alcoolisée' },
        { label: 'Alcool' },
        { label: 'Dose', align: 'right' as const },
        { label: 'Choisi par', align: 'right' as const },
        { label: 'Alcool / menu', align: 'right' as const },
      ],
      lignes: c.lignes.map((l) => [
        cg(l.menu),
        cg(l.service),
        cg(l.obligatoire ? `${l.option} (toujours)` : l.option),
        cg(l.alcool),
        cd(`${l.dose_cl} cl`),
        cd(`${l.proba_pct} %`),
        cd(`${l.cl_moyen.toFixed(1)} cl`),
      ]),
    },
  ]
})

const consoPeriodeSection: Section = {
  kind: 'tableau',
  titre: 'Consommation totale par exercice : caisse + cuisine + menus + personnel',
  minWidth: 720,
  colonnes: [
    { label: 'Source de consommation' },
    { label: '2022-2023', align: 'right' },
    { label: '2023-2024', align: 'right' },
    { label: '2024-2025', align: 'right' },
    { label: 'Total 3 ans', align: 'right' },
  ],
  lignes: [
    ['Vendu en caisse (verre + cocktails)', 'caisse_l'],
    ['Cuisine (plats, sauces, desserts)', 'cuisine_l'],
    ['Alcool des menus (non détaillé en caisse)', 'menu_l'],
    ['Consommation du personnel', 'personnel_l'],
  ].map(([lab, key]) => [
    cg(lab as string),
    cd(litresB(Pp['2022-2023'][key as keyof typeof Pp['2022-2023']] as number)),
    cd(litresB(Pp['2023-2024'][key as keyof typeof Pp['2023-2024']] as number)),
    cd(litresB(Pp['2024-2025'][key as keyof typeof Pp['2024-2025']] as number)),
    cd(litresB(Pp.total[key as keyof typeof Pp.total] as number)),
  ]).concat([
    [
      cg('TOTAL CONSOMMÉ'),
      cd(litresB(Pp['2022-2023'].total_l)),
      cd(litresB(Pp['2023-2024'].total_l)),
      cd(litresB(Pp['2024-2025'].total_l)),
      cd(litresB(Pp.total.total_l)),
    ],
    [
      cg('Coût d’achat (factures)'),
      cd(eurB(Pp['2022-2023'].cout)),
      cd(eurB(Pp['2023-2024'].cout)),
      cd(eurB(Pp['2024-2025'].cout)),
      cd(eurB(Pp.total.cout)),
    ],
    [
      cg('CA à la revente (carte)'),
      cd(eurB(Pp['2022-2023'].ca)),
      cd(eurB(Pp['2023-2024'].ca)),
      cd(eurB(Pp['2024-2025'].ca)),
      cd(eurB(Pp.total.ca)),
    ],
  ]),
}

// --- Données des graphiques (mêmes chiffres que les tableaux, rien de saisi) ---
// Catégorie d'un poste de la cascade : transparence mesuré / calculé / estimé.
const cascadeCat = (poste: string): 'mesure' | 'calcul' | 'estime' => {
  if (/chef|offert|sans recette|sur-versement|dégustation|degustation|crémant|cremant|freinte/i.test(poste)) return 'estime'
  if (/cuisine|menus/i.test(poste)) return 'calcul'
  return 'mesure' // vendu au verre, cocktails, stock final (inventaire)
}
const cascadeSegments = [
  ...BPD.synthese.cascade.map((p) => ({ label: p.poste, valeur: p.litres, categorie: cascadeCat(p.poste) })),
  {
    label: 'Perte résiduelle (casse, évaporation, mousse)',
    valeur: BPD.synthese.perte_reelle_l,
    categorie: 'residuel' as const,
  },
]
// Consommation par exercice, décomposée (barres empilées) - depuis consoParPeriode.
const consoEmpileData = (['2022-2023', '2023-2024', '2024-2025'] as const).map((ex) => ({
  exercice: ex,
  'Vendu en caisse': Pp[ex].caisse_l,
  Cuisine: Pp[ex].cuisine_l,
  Menus: Pp[ex].menu_l,
  Personnel: Pp[ex].personnel_l,
}))
// Stock physique boissons aux 3 inventaires (HT) - depuis les inventaires datés.
const stockInventaireData = inventairePhysique.stocks.map((s) => ({
  exercice: s.exercice,
  'Stock boissons (HT)': Math.round(s.ht),
}))

const boissonsV2: Analyse = {
  slug: 'boissons-disparues',
  eyebrow: 'Réfutation chiffrée',
  titre: 'Les « boissons disparues », ligne par ligne',
  resume:
    'Boisson par boisson, plat par plat, cocktail par cocktail, menu par menu : on mesure exactement ce qui a été acheté et tout ce qui a été consommé (vendu, cuisine, menus, personnel). Le manquant réel tombe à la perte normale d’un bar, et le CA reconstitué par le fisc s’effondre.',
  force: 'forte',
  apercu: [
    { label: 'Boissons passées au crible', valeur: String(BPD.disparuParBoisson.length) },
    { label: 'Perte d’exploitation', valeur: `${BPD.synthese.perte_exploitation_pct} %`, sub: 'des achats (estimation du mémoire de juillet 2026, non revendiquée)' },
  ],
  controleurDit: `Des boissons achetées ne se retrouveraient pas dans les ventes : le CA est reconstitué par les volumes, d’où ${formatEuro(BPD.synthese.fisc_ca_reconstitue)} reconstitués (× ${BPD.synthese.fisc_coef}).`,
  demonstration: `On ne reconstitue pas, on mesure : chaque litre est rattaché à un usage (caisse, cuisine, menus, personnel, sur-versement, dégustation, crémant, freinte). La perte d’exploitation totale estimée en juillet 2026 (${BPD.synthese.perte_exploitation_pct} %) n’est plus revendiquée (point 3.10.2) ; le résiduel irréductible (casse, évaporation) n’est que ${BPD.synthese.perte_reelle_pct} %.`,
  faitTomber: 'La reconstitution par les volumes de boissons',
  pieces: [
    ...piecesLiees('D', 'B', 'E'),
    { to: `/documents/${FACTURES_SLUG}`, label: 'Factures FCBS' },
  ],
  sections: [
    // ---------------- PARTIE 1 : LE FISC ----------------
    {
      kind: 'chapitre',
      source: 'fisc',
      numero: 1,
      titre: 'Ce que le fisc a calculé',
      sousTitre: 'Reconstitution du chiffre d’affaires à partir des volumes de boissons',
    },
    {
      kind: 'paragraphe',
      texte: `À partir des **achats** de boissons, le vérificateur déduit un volume « disponible », le convertit en verres via des **doses**, en tire un **CA liquides**, puis le **multiplie par ${BPD.synthese.fisc_coef}** pour estimer le CA « solides » (la cuisine). Le total reconstitué est comparé au CA déclaré, et l’écart présenté comme une dissimulation.`,
    },
    {
      kind: 'kpis',
      items: [
        { label: 'CA reconstitué par le fisc', valeur: formatEuro(BPD.synthese.fisc_ca_reconstitue), sub: 'exercice 2024-2025', highlight: true, couleur: 'red' },
        { label: 'CA déclaré', valeur: formatEuro(BPD.synthese.ca_declare), sub: 'TTC' },
        { label: 'Coefficient liquide → solide', valeur: `× ${BPD.synthese.fisc_coef}`, sub: 'le CA cuisine est extrapolé' },
      ],
    },
    // ---------------- PARTIE 2 : LES DEUX FAITS DURS ----------------
    {
      kind: 'chapitre',
      source: 'nous',
      numero: 2,
      titre: 'Deux faits que le fisc ne peut pas contester',
      sousTitre: 'Avant tout calcul de détail : il n’existe ni canal pour encaisser ces ventes, ni disparition physique de stock.',
    },
    {
      kind: 'kpis',
      items: [
        { label: 'CA bancarisé (carte, titres-restaurant, chèques)', valeur: '98,7 %', sub: 'carte, titres-restaurant, chèques', highlight: true, couleur: 'teal' },
        { label: 'Part des espèces dans le CA', valeur: '1,3 %', sub: 'plafond matériel de toute vente en liquide' },
        { label: 'Achats boissons consommés (compta matière du fisc)', valeur: formatPct(comptaMatiere.pctConsomme), sub: 'le stock ne grossit pas : rien ne disparaît' },
      ],
    },
    {
      kind: 'alerte',
      couleur: 'teal',
      titre: 'Fait 1 : la part des espèces dans les règlements enregistrés',
      texte: `Même en supposant tout le manquant **vendu**, encore faudrait-il l’**encaisser**. Or **98,7 % du chiffre d’affaires est bancarisé** (carte, titres-restaurant, chèques) et les **espèces ne pèsent que 1,3 %**. Écouler ${formatEuro(BPD.synthese.disparu_brut_ca)} d’alcool au comptant supposerait un canal espèces qui **n’existe pas** dans les encaissements. Voir l’analyse **bancarisation**.`,
    },
    {
      kind: 'barreComposition',
      titre: 'Comment le chiffre d’affaires est encaissé',
      sousTitre: 'Part de chaque mode dans les règlements enregistrés.',
      unite: '%',
      total: 100,
      segments: [
        { label: 'Encaissé en banque (carte, titres-restaurant, chèques)', valeur: 98.7, categorie: 'mesure' },
        { label: 'Espèces', valeur: 1.3, categorie: 'alerte' },
      ],
    },
    {
      kind: 'alerte',
      couleur: 'teal',
      titre: 'Fait 2 : l’inventaire physique ferme le bilan matière',
      texte: `L’**inventaire physique des 3 fins d’exercice** montre un stock boissons **stable** : ${formatEuro(Math.round(inventairePhysique.stocks[0].ht))} → ${formatEuro(Math.round(inventairePhysique.stocks[1].ht))} → ${formatEuro(Math.round(inventairePhysique.stocks[2].ht))} HT, jamais en baisse. La **comptabilité matière du fisc lui-même** le confirme (compte 310200 : ${formatEuro(comptaMatiere.cumul)} sur 3 ans, soit ${formatPct(comptaMatiere.pctVariation)} des achats). Par l’identité **achats + variation de stock = consommation**, **${formatPct(comptaMatiere.pctConsomme)} des achats ont été consommés**. Rien ne s’est « évaporé » : tout a été **consommé** ; la seule question est de savoir **par qui** (clients payants, cuisine, pertes), jamais « encaissé en douce ».`,
    },
    {
      kind: 'graphique',
      variante: 'vertical',
      hauteur: 230,
      dataKey: 'exercice',
      serie: { name: 'Stock boissons (HT)', couleur: 'teal.6' },
      data: stockInventaireData,
      format: 'euro',
    },
    {
      kind: 'note',
      texte: 'Stock physique boissons aux 3 fins d’exercice (inventaires datés) : stable, jamais en baisse. Un exploitant qui détournerait des bouteilles verrait son stock chuter.',
    },
    {
      kind: 'note',
      texte: 'Ces deux faits ne dépendent d’aucune estimation : ils reposent sur les fichiers de règlement de la caisse et sur les inventaires datés. Le détail qui suit explique, litre par litre, la consommation sans recette qui compose l’écart.',
    },
    // ---------------- PARTIE 3 : NOTRE ANALYSE ----------------
    {
      kind: 'chapitre',
      source: 'nous',
      numero: 3,
      titre: 'Notre méthode : on mesure, on ne reconstitue pas',
      sousTitre: '199 factures fournisseur + caisse réelle + carte (doses) - chaque chiffre est exact et téléchargeable',
    },
    enClair(
      'Pour chaque boisson, on compare ce qui a été **acheté** (factures) à **tout** ce qui a été consommé : vendu en caisse, utilisé en cuisine, servi dans les menus, et bu par le personnel. Les tableaux ci-dessous donnent les chiffres exacts, sans aucun arrondi de famille.',
    ),
    {
      kind: 'tableau',
      titre: '1. Le manquant, boisson par boisson (Manquant = Acheté − Consommé − Stock fin)',
      minWidth: 820,
      colonnes: [
        { label: 'Boisson' },
        { label: 'Acheté', align: 'right' },
        { label: 'Consommé', align: 'right' },
        { label: 'Stock fin', align: 'right' },
        { label: 'Manquant', align: 'right' },
        { label: 'Coût d’achat', align: 'right' },
        { label: 'CA prétendument perdu', align: 'right' },
      ],
      lignes: BPD.disparuParBoisson.map((r) => [
        cg(r.nom),
        cd(litresB(r.achat_l)),
        cd(litresB(r.conso_l)),
        cd(litresB(r.stock_l)),
        cd(litresB(r.disparu_l)),
        cd(eurB(r.cout_disparu)),
        cd(eurB(r.ca_disparu)),
      ]),
    },
    {
      kind: 'note',
      texte: `**Lecture du tableau.** Pour chaque boisson, **Manquant = Acheté − Consommé − Stock fin** (le « Stock fin » est le stock physique encore en cave à l’inventaire 2024-2025 : il n’a pas disparu). Chaque ligne est donc reproductible à partir des colonnes affichées (à 0,1 L près, du fait des arrondis).`,
    },
    {
      kind: 'alerte',
      couleur: 'teal',
      titre: 'À lire avant le tableau : pourquoi une boisson peut sembler « disparue » alors qu’elle a bien été vendue',
      texte: `La caisse et les factures ne parlent pas le même langage. **Sur les factures, chaque vin porte son nom exact** (domaine, millésime). **En caisse, un seul bouton sert pour des dizaines de vins** : le serveur tape « Verre de vin », « Savagnin verre » ou « Macvin », sans préciser quelle bouteille précise. Le contrôleur, lui, compare facture par facture : il cherche « Arbois Savagnin 2018 » dans les ventes, ne le trouve pas sous ce nom (il a été sonné sous le bouton commun) et le déclare « disparu ». **Mais la vente est bien là, et sa recette est déjà dans le chiffre d’affaires déclaré.** Ce n’est pas une bouteille qui s’évapore : c’est un **problème d’étiquetage de la caisse**, sans le moindre euro caché. L’exemple ci-dessous le montre, et la liste complète est téléchargeable juste après.`,
    },
    {
      kind: 'tableau',
      titre: 'Exemple : ce qui est écrit sur la facture vs le bouton tapé en caisse',
      minWidth: 560,
      colonnes: [
        { label: 'Sur la facture (le vin précis acheté)' },
        { label: 'Sonné en caisse sous le bouton…' },
      ],
      lignes: [
        [cg('Arbois Savagnin 2018 (Fruitière Vinicole d’Arbois)'), cg('« Savagnin verre / pichet » (un seul bouton pour 6 millésimes)')],
        [cg('Saint Joseph rouge 2019, 2021 et 2022 (Ogier)'), cg('« C du Rhône St Joseph » (un seul bouton pour 7 millésimes)')],
        [cg('5 Macvin du Jura différents (Rolet, Lornet, Jacobin…)'), cg('« Macvin du Jura » (un seul bouton pour les 5)')],
        [cg('« Mouton Cadet » : 0 acheté sur la période'), cg('Bouton mal nommé : le vrai bordeaux acheté et en cave est le Château Grand Renom')],
      ],
    },
    {
      kind: 'note',
      texte: `**Comment lire cet exemple.** À gauche, le vin tel qu’il apparaît sur la facture du fournisseur. À droite, le bouton réellement utilisé en caisse pour le vendre. Comme plusieurs vins partagent un même bouton, le vin précis paraît « jamais vendu » dans les statistiques de caisse, alors qu’il a bien été servi et encaissé. **La preuve par l’inventaire** : les bouteilles soi-disant « disparues » sont soit bien en cave, soit n’ont jamais existé (codes de caisse créés mais jamais utilisés, comme certaines bières).`,
    },
    {
      kind: 'piecejointe',
      intro: 'Liste complète des correspondances libellés factures ↔ boutons de caisse (boutons mutualisés, boutons génériques et codes jamais paramétrés) :',
      fichiers: [{ fichier: 'pieces-defense/Boissons-6-correspondance-libelles.xlsx', label: 'Correspondance libellés factures ↔ caisse (XLSX)' }],
    },
    {
      kind: 'note',
      texte: `**Les manquants négatifs ne sont pas des disparitions** : une consommation supérieure aux achats sur une ligne (ex. « Cubis de vin » : 0 acheté, ~427 L consommés sous ce libellé caisse générique, alors que le vin correspondant est acheté sous son appellation précise) traduit un **décalage d’affectation**, pas une bouteille apparue de nulle part. Le total réel ne dépend pas de cet étiquetage : **Manquant net = total acheté − total consommé − stock** (bilan matière global), soit **${formatInt(BPD.synthese.disparu_net_l)} L**. Valorisé en **ne retenant que les lignes positives** (majorant théorique), le manquant ressort à ${formatEuro(BPD.synthese.disparu_brut_cout)} au coût d’achat et ${formatEuro(BPD.synthese.disparu_brut_ca)} au prix de revente, soit l’équivalent de ${formatInt(BPD.synthese.disparu_brut_l)} L (et non ${formatInt(BPD.synthese.disparu_net_l)} L) : ces montants sont donc un plafond. C’est le maximum avant de déduire la cuisine, les menus, le personnel et les offerts (tableaux suivants).`,
    },
    {
      kind: 'alerte',
      couleur: 'teal',
      titre: 'Avoirs et retours fournisseur : vérifiés ligne par ligne et corrigés',
      texte: `Nous avons contrôlé l’intégralité des **199 factures** (3 889 lignes), avoir par avoir. Les **40 retours** intégrés aux factures (quantités négatives) étaient **déjà déduits** des achats. Les **6 avoirs autonomes** (324,66 € HT) ont été traités un par un : le seul poste volumineux est une **consigne de fûts** (emballage repris, **sans volume de boisson**), et les **34,6 L de boissons** crédités (cidre, BIB aligoté, grand marnier) ont été **retirés des achats**. Chaque facture, sa date et sa mention (avoir, retour, déconsigne, article manquant…) sont détaillées dans la pièce jointe ci-dessous : le calcul est désormais **exact et traçable au document**.`,
    },
    {
      kind: 'piecejointe',
      intro: 'Pièce justificative (détail ligne à ligne des 199 factures, avec mentions et traitement) :',
      fichiers: [{ fichier: 'pieces-defense/Factures-avoirs-et-retours.xlsx', label: 'Factures : avoirs et retours (XLSX)' }],
    },
    {
      kind: 'tableau',
      titre: '2. Les cocktails : composition exacte et alcool consommé',
      minWidth: 720,
      colonnes: [
        { label: 'Cocktail' },
        { label: 'Recette (alcool)' },
        { label: 'Volume', align: 'right' },
        { label: 'Vendus (3 ans)', align: 'right' },
        { label: 'Alcool consommé', align: 'right' },
      ],
      lignes: BPD.cocktails.map((c) => [
        cg(c.cocktail),
        cg(recetteStr(c) || '-'),
        cd(`${c.volume_cl} cl`),
        cd(formatInt(c.qte_3ans)),
        cd(litresB(c.alcool_l_3ans)),
      ]),
    },
    {
      kind: 'note',
      texte:
        'La colonne « alcool consommé » ne compte que les alcools forts/vins du cocktail (total **789,5 L** sur 3 ans). Les cocktails sans alcool (Mambo, Luna) affichent 0. Pour le Panaché, le Monaco et le Picon-bière, la bière figure dans la recette mais est comptée une seule fois, dans la ligne « bière pression (fût) », pour éviter tout double comptage. C’est pourquoi la cascade de synthèse affiche un poste « cocktails » de **998 L** (789,5 L d’alcools + ~208 L de bière des cocktails) : la différence est la bière, déjà rattachée au fût. Les mixers (jus, limonade, sirop) relèvent du bilan des softs.',
    },
    {
      kind: 'piecejointe',
      intro: 'Télécharger ce tableau :',
      fichiers: [{ fichier: 'pieces-defense/Boissons-2-cocktails.xlsx', label: 'Cocktails - composition (XLSX)' }],
    },
    {
      kind: 'tableau',
      titre: '3. La cuisine : alcool de chaque plat, entrée, dessert et sauce',
      minWidth: 620,
      colonnes: [
        { label: 'Plat / préparation' },
        { label: 'Type' },
        { label: 'Alcool' },
        { label: 'Dose', align: 'right' },
      ],
      lignes: BPD.cuisine.map((p) => [cg(p.plat), cg(p.type), cg(p.alcool), cd(`${p.dose_cl} cl`)]),
    },
    {
      kind: 'tableau',
      titre: '3 bis. Ce que la cuisine consomme au total (litres, 3 ans)',
      minWidth: 440,
      colonnes: [{ label: 'Alcool' }, { label: 'Litres', align: 'right' }, { label: 'Coût d’achat', align: 'right' }],
      lignes: BPD.cuisineParAlcool.map((r) => [cg(r.alcool), cd(litresB(r.litres_3ans)), cd(eurB(r.cout))]),
    },
    {
      kind: 'piecejointe',
      intro: 'Télécharger ces tableaux :',
      fichiers: [{ fichier: 'pieces-defense/Boissons-3-cuisine.xlsx', label: 'Cuisine - alcool des plats (XLSX)' }],
    },
    {
      kind: 'paragraphe',
      texte:
        '**4. Les menus.** La caisse n’enregistre qu’un prix de menu, pas son contenu. On reconstitue l’alcool en croisant la **composition de chaque menu par période** avec la **probabilité** que le client choisisse l’option alcoolisée (1 entrée, 1 plat, 1 dessert max, jamais cumulés). « Choisi par » = part des clients prenant l’option ; « Alcool / menu » = dose × probabilité.',
    },
    ...menusSections,
    {
      kind: 'piecejointe',
      intro: 'Télécharger les menus par période :',
      fichiers: [{ fichier: 'pieces-defense/Boissons-4-menus-par-periode.xlsx', label: 'Menus par période (XLSX)' }],
    },
    {
      kind: 'tableau',
      titre: '5. La consommation du personnel et du chef (litres, coût, CA équivalent)',
      minWidth: 660,
      colonnes: [
        { label: 'Poste' },
        { label: 'Litres', align: 'right' },
        { label: 'Coût d’achat', align: 'right' },
        { label: 'CA équivalent', align: 'right' },
      ],
      lignes: [
        ...BPD.personnel.lignes.map((l) => [
          cg(l.poste),
          cd(litresB(l.litres)),
          cd(eurB(l.cout_achat_eur)),
          cd(eurB(l.ca_equivalent_eur)),
        ]),
        [cg('TOTAL personnel'), cd(litresB(BPD.personnel.total_litres)), cd(eurB(BPD.personnel.total_cout_eur)), cd(eurB(BPD.personnel.total_ca_eur))],
      ],
    },
    {
      kind: 'note',
      texte:
        'Les colonnes « coût d’achat » et « CA équivalent » sont indicatives : ces volumes sont consommés, donc précisément **non vendus**. Pour l’alcool, seuls les 143 L du chef (Macvin + Picon) entrent dans la cascade. Les softs (Coca, jus, sirop, 1 913 L) ne sont **pas** un manquant d’alcool : ils sont **bouclés indépendamment** par le bilan des softs (achats − ventes au ticket − stock = consommation du personnel par différence, à partir des seules pièces dures).',
    },
    {
      kind: 'tableau',
      titre: '6. Boissons et cafés servis sans recette, non saisis (estimation du mémoire de juillet 2026)',
      minWidth: 660,
      colonnes: [
        { label: 'Poste' },
        { label: 'Litres', align: 'right' },
        { label: 'Coût d’achat', align: 'right' },
        { label: 'CA équivalent', align: 'right' },
      ],
      lignes: [
        ...BPD.offerts.lignes.map((l) => [cg(l.poste), cd(litresB(l.litres)), cd(eurB(l.cout_achat_eur)), cd(eurB(l.ca_equivalent_eur))]),
        [cg('TOTAL'), cd('-'), cd(eurB(BPD.offerts.total_cout_eur)), cd(eurB(BPD.offerts.total_ca_eur))],
      ],
    },
    { kind: 'note', texte: BPD.offerts.avertissement },
    {
      kind: 'note',
      texte:
        'Ce poste n’est pas porté au chiffrage comme un montant acquis. Les boissons alcoolisées portées à 0,00 € en caisse (26,75 L), sorties sans recette déjà comptées dans les quantités vendues, sont retirées, quelle qu’en soit la cause, de l’estimation forfaitaire des boissons servies sans recette, hors dégustation et personnel, pour qu’aucun litre ne soit compté deux fois ; la caisse ne mesure pas les offerts, que l’usage est de ne pas saisir (point 2.4.8).',
    },
    {
      kind: 'piecejointe',
      intro: 'Télécharger ces tableaux :',
      fichiers: [{ fichier: 'pieces-defense/Consommation-personnel-et-offerts.xlsx', label: 'Personnel & offerts (XLSX)' }],
    },
    // ---------------- SYNTHÈSE ----------------
    {
      kind: 'chapitre',
      source: 'nous',
      titre: 'Synthèse : où va, litre par litre, l’alcool acheté',
      sousTitre: 'Toutes les sources de consommation réunies, par exercice',
    },
    consoPeriodeSection,
    {
      kind: 'graphiqueEmpile',
      titre: 'La consommation est structurée à l’identique chaque exercice (litres d’alcool)',
      hauteur: 260,
      dataKey: 'exercice',
      type: 'stacked',
      series: [
        { name: 'Vendu en caisse', couleur: 'teal.6' },
        { name: 'Cuisine', couleur: 'blue.5' },
        { name: 'Menus', couleur: 'indigo.4' },
        { name: 'Personnel', couleur: 'orange.5' },
      ],
      data: consoEmpileData,
      format: 'int',
    },
    {
      kind: 'note',
      texte:
        'Ce tableau porte sur l’alcool (cohérent avec le reste de la page). La consommation du personnel n’y figure que pour sa part alcool (Macvin et Picon du chef, 143 L) ; les softs du personnel (Coca, jus, sirop) relèvent du bilan des softs, entièrement bouclé par ailleurs. Les sodas et eaux ne sont donc pas un manquant.',
    },
    {
      kind: 'piecejointe',
      intro: 'Télécharger ce tableau :',
      fichiers: [{ fichier: 'pieces-defense/Boissons-5-conso-par-periode.xlsx', label: 'Consommation par exercice (XLSX)' }],
    },
    {
      kind: 'barreComposition',
      titre: `Où va l’alcool acheté (${formatInt(BPD.synthese.achat_alcool_l)} L sur 3 ans)`,
      sousTitre: 'Chaque litre acheté est rattaché à un usage. La couleur distingue le mesuré, le calculé et l’estimé.',
      unite: 'L',
      total: BPD.synthese.achat_alcool_l,
      segments: cascadeSegments,
      legende: true,
    },
    {
      kind: 'tableau',
      titre: 'Cascade finale : des achats à la perte réelle',
      minWidth: 480,
      colonnes: [{ label: 'Poste' }, { label: 'Litres', align: 'right' }],
      lignes: [
        [cg('ACHATS D’ALCOOL (factures)'), cd(litresB(BPD.synthese.achat_alcool_l))],
        ...BPD.synthese.cascade.map((p) => [cg('—  ' + p.poste), cd(litresB(p.litres))]),
        [cg(`=  PERTE RÉELLE (${BPD.synthese.perte_reelle_pct} % des achats)`), cd(litresB(BPD.synthese.perte_reelle_l))],
      ],
    },
    {
      kind: 'note',
      texte:
        'Ce résiduel n’est plus un « trou » : les pertes identifiables ont été **sorties en postes chiffrés** (sur-versement, dégustation, crémant jeté, freinte de la bière). Ce qu’il reste est la perte **strictement irréductible** d’un bar : **casse**, **évaporation** et **oxydation** des bouteilles ouvertes peu écoulées, **fonds de verre**. Ces pertes sont consommées ou détruites, jamais encaissées.',
    },
    {
      kind: 'chapitre',
      source: 'neutre',
      titre: 'Annexes : toutes les données et la méthode',
      sousTitre: 'Classeurs téléchargeables - chaque chiffre est sourcé',
    },
    {
      kind: 'piecejointe',
      intro: 'Données complètes de la page :',
      fichiers: [
        { fichier: 'pieces-defense/Boissons-detail-complet.xlsx', label: 'Boissons - détail complet (toutes les tables)' },
        { fichier: 'pieces-defense/Consommation-personnel-et-offerts.xlsx', label: 'Conso personnel & offerts + perte réelle' },
      ],
    },
    {
      kind: 'piecejointe',
      intro: 'Méthode et preuve de process (modèle, corrections, réconciliations) :',
      fichiers: [
        { fichier: 'pieces-defense/Methode-2-correction-mapping-Cubis.xlsx', label: 'Correction d’attribution (Cubis)' },
        { fichier: 'pieces-defense/Methode-3-bilan-softs.xlsx', label: 'Bilan des softs' },
        { fichier: 'pieces-defense/Methode-4-conso-personnel-detail.xlsx', label: 'Conso personnel détaillée' },
        { fichier: 'pieces-defense/Methode-6-erreurs-quantite-DEL.xlsx', label: 'Erreurs de quantité (DEL)' },
      ],
    },
    {
      kind: 'sources',
      items: [
        ...(['D', 'B', 'E'] as const)
          .map((l) => groupes.find((g) => g.lettre === l))
          .filter((g): g is (typeof groupes)[number] => Boolean(g))
          .map((g) => ({ slug: g.slug, label: `Annexe ${g.lettre} - ${g.titre}` })),
        { slug: FACTURES_SLUG, label: 'Factures fournisseur (FCBS) - achats réels' },
        { slug: CARTES_SLUG, label: 'Carte des vins & boissons - doses' },
        { slug: INVENTAIRES_SLUG, label: 'Inventaires physiques' },
      ],
    },
  ],
}

// Analyses affichées dans la liste /analyses.
export const analyses: Analyse[] = [reconstitution, continuite, bancarisation, boissonsV2]

// Versions archivées : routables par URL mais masquées de la liste (ex. ancienne page boissons).
const analysesArchivees: Analyse[] = []

export function analyseParSlug(slug: string): Analyse | undefined {
  return [...analyses, ...analysesArchivees].find((a) => a.slug === slug)
}
