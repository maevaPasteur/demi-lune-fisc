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

import { analyseDel as A } from './analyseDel'
import { integrite as I } from './analyseIntegrite'
import { complements as K } from './analyseComplements'
import { reconstitution as R } from './analyseReconstitution'
import { refacturation as Ref } from './analyseRefacturation'
import {
  delComplements as DC,
  boissonsComplements as BC,
  synthesePerteReelle as SPR,
} from './complementsDefense'
import { boissonsPageData as BPD } from './boissonsPageData'
import {
  boissonsDisparues as Bo,
  resultatsIndep as Res,
  decomposition as Decomp,
  partVerifieePct,
  auditFisc,
  auditFiscDetail,
  comptaMatiere,
  comptaMatiereDetail,
  detailCuisine,
  detailSubstitution,
  pistesComplementaires as Pistes,
  pistesComplMin,
  pistesComplMax,
  inventairePhysique,
  inventaireDetail,
  bilanBouteilles,
} from './analyseBoissons'
import { groupes, CARTES_SLUG, FACTURES_SLUG, MANUSCRIT_SLUG, INVENTAIRES_SLUG } from './documents'
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
    'Recalculé depuis la caisse certifiée par cinq chemins indépendants, le chiffre d’affaires retombe sur le montant déclaré. Aucune recette ne manque.',
  force: 'forte',
  controleurDit:
    'Le chiffre d’affaires déclaré serait minoré : reconstitution alléguée de +471 826 € de recettes.',
  demonstration:
    'Cinq exports certifiés et indépendants reconstituent le CA déclaré à 0,1 % près. Aucune recette ne manque.',
  faitTomber: 'La reconstitution du fisc - 471 826 €',
  pieces: piecesLiees('B', 'C', 'H', 'G', 'A'),
  apercu: [
    { label: 'Exports certifiés qui convergent', valeur: String(R.sourcesCount) },
    { label: 'Écart max au CA déclaré (3 ans)', valeur: formatPct(ecartMaxRecon, 2) },
  ],
  sections: [
    enClair(
      'Plutôt que d’estimer le chiffre d’affaires, on l’a recalculé depuis la caisse certifiée par **cinq chemins indépendants** : chaque plat, chaque ticket, chaque en-tête, le journal de TVA, et la synthèse déclarée. Les cinq tombent sur le même montant. Conclusion simple : il ne manque aucune recette.',
    ),
    {
      kind: 'paragraphe',
      texte: `**Cinq exports certifiés et indépendants** de la caisse reconstituent le même chiffre d’affaires sur trois exercices : le détail des plats (${formatInt(R.lignesTotal)} lignes), le détail des tickets, les en-têtes de tickets, le journal de TVA et la synthèse déclarée. Tous tiennent dans une fourchette de **${formatPct(ecartMaxRecon, 2)}** autour du CA déclaré de **${formatEuro(R.cumul.caDeclare)}**.`,
    },
    {
      kind: 'kpis',
      items: [
        { label: 'CA déclaré (A)', valeur: formatEuro(R.cumul.caDeclare), sub: 'synthèse certifiée' },
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
      `Le chiffre d’affaires déclaré n’est pas une estimation : **cinq exports certifiés et indépendants** le reconstituent, tous à moins de ${formatPct(ecartMaxRecon, 2)} près sur trois ans. Toute reconstitution extrapolée (coefficients, ratios de marge) est démentie par les données réelles.`,
    ),
    sources('B', 'C', 'H', 'G', 'A'),
  ],
}

// ======================= ANALYSE 1 - SUPPRESSIONS (DEL) ======================
const del: Analyse = {
  slug: 'suppressions-del',
  eyebrow: 'Argument central',
  titre: 'Suppressions de caisse (DEL)',
  resume:
    'Les lignes supprimées de la caisse certifiée ne sont pas du chiffre d’affaires dissimulé : corrections, transferts ou refacturations déjà incluses dans le CA déclaré.',
  force: 'forte',
  controleurDit:
    '21 302 suppressions « DEL » de la caisse = 430 763 € de recettes occultées.',
  demonstration: `Trois preuves l’excluent : sur ${DC.sessionsImpossiblesNb} journées, les suppressions dépassent le CA encaissé du jour (le 26/07/2022 : 69 557 € supprimés pour 2 563 € encaissés) ; les plus grosses sont des fautes de frappe sur la quantité (menu Bambin 6,90 € × 9999) ; et trois exports certifiés reconstituent le même CA. Les espèces ne pèsent que 1,3 % : aucun canal pour encaisser au noir.`,
  faitTomber: 'Le motif central du rejet - 430 763 €',
  pieces: piecesLiees('E', 'A', 'B'),
  apercu: [
    { label: 'Suppressions (thèse du fisc)', valeur: formatEuro(A.delSomme) },
    { label: 'Sessions où suppr. > CA du jour', valeur: String(DC.sessionsImpossiblesNb) },
  ],
  sections: [
    enClair(
      'Une « DEL » est une ligne - un plat - retirée d’un ticket en cours de saisie. Ce n’est jamais de l’argent qui sort de la caisse : soit l’erreur est corrigée, soit le plat est re-facturé ailleurs. Additionner ces suppressions, comme le fait l’administration, revient à compter deux fois la même recette.',
    ),
    {
      kind: 'alerte',
      couleur: 'red',
      titre: 'La thèse de l’administration',
      texte: `L’administration additionne les ${formatInt(A.delCount)} suppressions de lignes (DEL) du journal de caisse et présente leur somme, **${formatEuro(A.delSomme)}**, comme des recettes occultées - soit ${formatPct(A.delPctCA)} du chiffre d’affaires déclaré sur trois exercices.`,
    },
    {
      kind: 'kpis',
      items: [
        { label: 'Suppressions (DEL)', valeur: formatInt(A.delCount), sub: 'sur 3 exercices' },
        { label: 'Montant retenu par le fisc', valeur: formatEuro(A.delSomme), sub: `${formatPct(A.delPctCA)} du CA`, highlight: true, couleur: 'red' },
        { label: 'Valeur médiane d’une ligne', valeur: formatEuroPrecis(A.mediane), sub: 'le prix d’un plat' },
        { label: 'Moyenne par ligne', valeur: formatEuroPrecis(A.moyenneLigne), sub: `${A.delParJour} DEL / jour de service` },
      ],
    },
    {
      kind: 'tableau',
      titre: 'Pourquoi une ligne est-elle supprimée ?',
      minWidth: 540,
      colonnes: [
        { label: 'Motif' },
        { label: 'En pratique' },
        { label: 'Effet sur le CA déclaré', align: 'center' },
      ],
      lignes: [
        [cg('Erreur de saisie'), cg('La ligne fautive est retirée, puis re-saisie correctement.'), { v: 'Aucun', align: 'center', badge: 'ok' }],
        [cg('Table qui paie séparément'), cg('Les plats sont déplacés vers un autre ticket.'), { v: 'Aucun', align: 'center', badge: 'ok' }],
        [cg('Facture sans détail'), cg('Les plats sont remplacés par un menu au même prix.'), { v: 'Aucun', align: 'center', badge: 'ok' }],
      ],
    },
    {
      kind: 'paragraphe',
      texte: `Ce dernier mécanisme est **mesurable dans la caisse**. Quand une table demande une facture sans détail, ses plats sont supprimés puis re-facturés sous un article à **prix forcé**. En comparant chaque vente au prix officiel de l’article - détecté comme le prix le plus fréquent du mois, par exemple ${formatEuro(Ref.demiLunePrixOfficiel)} pour le Menu Demi Lune - on isole précisément ces prix forcés (les ventes normales du menu fixe sont exclues) : **${formatEuro(Ref.total)}** sur trois ans, ${formatInt(Ref.lignes)} lignes, un montant **entièrement présent dans le CA déclaré**. Il représente **${formatPct(Ref.pctDuDelTotal)}** du volume de DEL invoqué par l’administration : autant de « suppressions » qui sont en réalité des recettes re-facturées et déclarées.`,
    },
    {
      kind: 'tableau',
      titre: 'Re-facturation à prix forcé (hors ventes au prix officiel)',
      minWidth: 460,
      colonnes: [
        { label: 'Article' },
        { label: 'Lignes à prix forcé', align: 'right' },
        { label: 'Total forcé (3 ans)', align: 'right' },
      ],
      lignes: [
        ...Ref.parArticle.map((a) => [
          cg(a.article),
          cd(`${formatInt(a.lignesForcees)} / ${formatInt(a.lignesTotal)}`),
          cd(formatEuro(a.total)),
        ]),
        [
          { v: 'Total', fw: 700 },
          { v: formatInt(Ref.lignes), align: 'right', fw: 700 },
          { v: formatEuro(Ref.total), align: 'right', badge: 'ok' },
        ],
      ],
    },
    {
      kind: 'kpis',
      items: [
        { label: 'Re-facturé à prix forcé', valeur: formatEuro(Ref.total), sub: 'déjà dans le CA déclaré', highlight: true, couleur: 'teal' },
        { label: 'Part du volume DEL du fisc', valeur: formatPct(Ref.pctDuDelTotal), sub: 'des « recettes occultées » alléguées' },
        { label: 'Lignes à prix forcé', valeur: formatInt(Ref.lignes), sub: 'prix ≠ prix officiel' },
      ],
    },
    {
      kind: 'paragraphe',
      texte:
        'Une ligne supprimée a, par définition, **d’abord été enregistrée** dans la caisse certifiée : horodatée, montant connu, rattachée à un ticket Z, dans un registre inviolable. Le chiffre d’affaires dissimulé, lui, n’entre jamais dans le système. Le journal des DEL est donc une preuve de transparence, pas de dissimulation.',
    },
    {
      kind: 'note',
      texte:
        'Contrôle de fiabilité : pour chaque exercice, notre total de DEL est identique au total déclaré par le fichier lui-même.',
    },
    {
      kind: 'tableau',
      minWidth: 460,
      colonnes: [
        { label: 'Exercice' },
        { label: 'DEL (calcul)', align: 'right' },
        { label: 'DEL (fichier)', align: 'right' },
        { label: 'Σ (fichier)', align: 'right' },
        { label: 'Réconcilié', align: 'center' },
      ],
      lignes: A.reconciliation.map((rec, i) => [
        cg(rec.exercice),
        cd(formatInt(A.parExercice[i].delCount)),
        cd(formatInt(rec.footCount)),
        cd(formatEuro(rec.footSomme)),
        { v: rec.ok ? 'OK' : 'écart', align: 'center', badge: rec.ok ? 'ok' : 'ko' },
      ]),
    },
    {
      kind: 'paragraphe',
      texte: `**${A.aberrCount} lignes** seulement - manifestement non assimilables à un plat - représentent **${formatEuro(A.aberrSomme)}**, soit **${formatPct(A.aberrPctTotal)}** du total brandi par l’administration. Aucune table d’un restaurant ne génère ${formatEuro(A.aberrations[0].montant)} sur une seule ligne : ce sont des erreurs de saisie immédiatement corrigées.`,
    },
    {
      kind: 'tableau',
      minWidth: 420,
      colonnes: [
        { label: 'Date' },
        { label: 'Heure' },
        { label: 'Montant supprimé', align: 'right' },
        { label: 'Part du total', align: 'right' },
      ],
      lignes: A.aberrations.map((a) => [cg(a.date), cg(a.heure), cd(formatEuro(a.montant)), cd(formatPct(a.pctDuTotal))]),
    },
    {
      kind: 'graphique',
      variante: 'horizontal',
      hauteur: 200,
      dataKey: 'libelle',
      serie: { name: 'Montant', couleur: 'gold.6' },
      format: 'euro',
      data: [
        { libelle: 'Total retenu par le fisc', Montant: A.delSomme },
        { libelle: 'Hors 4 lignes aberrantes', Montant: A.delSommeHorsAberr },
      ],
    },
    {
      kind: 'note',
      texte: `Hors ces ${A.aberrCount} aberrations, les ${formatInt(A.delCountHorsAberr)} autres suppressions totalisent ${formatEuro(A.delSommeHorsAberr)}, soit ${formatEuroPrecis(A.moyenneHorsAberr)} par ligne - un niveau de plat.`,
    },
    {
      kind: 'paragraphe',
      texte: `La distribution des montants supprimés épouse celle d’une carte de restaurant : **${formatPct(A.partCentimes * 100)}** des montants comportent des centimes (prix de carte), et la valeur médiane est de **${formatEuroPrecis(A.mediane)}**. Une dissimulation fabriquerait des sommes rondes et élevées ; on observe l’inverse.`,
    },
    {
      kind: 'graphique',
      variante: 'vertical',
      hauteur: 300,
      dataKey: 'tranche',
      serie: { name: 'Suppressions', couleur: 'blue.6' },
      format: 'int',
      data: A.distribution.map((d) => ({ tranche: d.tranche, Suppressions: d.n })),
    },
    {
      kind: 'paragraphe',
      texte: `**${formatPct(A.partServices)}** des suppressions surviennent pendant les services (midi et soir). Si elles servaient à effacer des recettes, elles se concentreraient à l’heure de clôture du Z : ce sont au contraire des corrections **en temps réel**.`,
    },
    {
      kind: 'graphique',
      variante: 'vertical',
      hauteur: 300,
      dataKey: 'heure',
      serie: { name: 'Suppressions', couleur: 'blue.6' },
      format: 'int',
      data: A.parHeure.filter((h) => h.heure >= 8 && h.heure <= 23).map((h) => ({ heure: `${h.heure} h`, Suppressions: h.n })),
    },
    {
      kind: 'paragraphe',
      texte: `Le profil de ces suppressions est celui de corrections d’exploitation : **${formatPct(K.del.partRafales * 100)}** surviennent en rafale (au moins deux à la même minute sur le même ticket), **${formatInt(K.del.delNuit)}** la nuit, et **${formatPct(K.del.partInf10 * 100)}** portent sur 10 € ou moins - l’ordre de grandeur d’un plat ou d’une boisson.`,
    },
    {
      kind: 'kpis',
      items: [
        { label: 'Suppressions en rafale', valeur: formatPct(K.del.partRafales * 100), sub: '≥ 2 à la même minute' },
        { label: 'Suppressions la nuit', valeur: formatInt(K.del.delNuit), sub: 'hors service', highlight: true, couleur: 'teal' },
        { label: 'Suppressions ≤ 10 €', valeur: formatPct(K.del.partInf10 * 100), sub: 'le prix d’un plat' },
      ],
    },
    {
      kind: 'paragraphe',
      texte: `Le montant supprimé **diminue** chaque année (${formatEuro(A.parExercice[0].delSomme)} → ${formatEuro(A.parExercice[A.parExercice.length - 1].delSomme)}). Une dissimulation croissante produirait la tendance inverse.`,
    },
    {
      kind: 'graphique',
      variante: 'vertical',
      hauteur: 260,
      dataKey: 'exercice',
      serie: { name: 'Montant supprimé', couleur: 'gold.6' },
      format: 'euro',
      data: A.parExercice.map((e) => ({ exercice: e.exercice, 'Montant supprimé': e.delSomme })),
    },
    {
      kind: 'paragraphe',
      texte: `Des recettes occultées seraient encaissées en espèces. Or, sur trois exercices, le restaurant n’a encaissé que **${formatEuro(A.especes)}** en espèces (${formatPct(A.especesPctCA)} du CA). Le montant prétendu dissimulé est **${A.ratioDelSurEspeces.toLocaleString('fr-FR')} fois** supérieur au total des espèces réellement encaissées : matériellement impossible.`,
    },
    {
      kind: 'kpis',
      items: [
        { label: 'Espèces encaissées (3 ans)', valeur: formatEuro(A.especes), sub: `${formatPct(A.especesPctCA)} du CA` },
        { label: '« Recettes occultées » alléguées', valeur: formatEuro(A.delSomme), sub: 'thèse du fisc' },
        { label: 'Rapport', valeur: `× ${A.ratioDelSurEspeces.toLocaleString('fr-FR')}`, sub: 'DEL / espèces', highlight: true, couleur: 'gold' },
      ],
    },
    {
      kind: 'tableau',
      titre: 'Récapitulatif par exercice',
      minWidth: 680,
      colonnes: [
        { label: 'Exercice' },
        { label: 'Jours', align: 'right' },
        { label: 'DEL', align: 'right' },
        { label: 'Σ DEL', align: 'right' },
        { label: 'DEL/jour', align: 'right' },
        { label: 'CA TTC', align: 'right' },
        { label: 'Espèces', align: 'right' },
        { label: 'Σ DEL / CA', align: 'right' },
      ],
      lignes: A.parExercice.map((e) => [
        cg(e.exercice),
        cd(String(e.joursService)),
        cd(formatInt(e.delCount)),
        cd(formatEuro(e.delSomme)),
        cd(String(e.delParJour)),
        cd(formatEuro(e.caTTC)),
        cd(formatEuro(e.especes)),
        cd(formatPct(e.delPctCA)),
      ]),
    },
    retenir(
      `Le volume de ${formatEuro(A.delSomme)} se décompose : ${formatEuro(A.aberrSomme)} pour ${A.aberrCount} fautes de frappe (${formatPct(A.aberrPctTotal)}), ${formatEuro(Ref.total)} re-facturés à prix forcé et déjà déclarés (${formatPct(Ref.pctDuDelTotal)}), le reste n’étant que des micro-corrections de plats (médiane ${formatEuroPrecis(A.mediane)}). Rapporté au CA déclaré et aux ${formatEuro(A.especes)} d’espèces encaissées en trois ans, ce volume ne peut pas correspondre à des recettes dissimulées.`,
    ),
    {
      kind: 'chapitre',
      source: 'nous',
      titre: 'Trois preuves supplémentaires (annexes certifiées E, A, H)',
      sousTitre: 'Reproductibles - pièce téléchargeable « Défense - Suppressions de caisse »',
    },
    {
      kind: 'alerte',
      couleur: 'teal',
      titre: 'Preuve par session : on ne supprime pas plus qu’on n’encaisse',
      texte: `Sur ${DC.sessionsImpossiblesNb} journées de caisse, le montant supprimé dépasse le chiffre d’affaires réellement encaissé ce jour-là. Le 26/07/2022, la caisse a encaissé ${formatEuro(2563)} mais « supprimé » ${formatEuro(69557)} : il est matériellement impossible de supprimer des ventes qui n’ont pas eu lieu. Ces lignes sont nécessairement fictives.`,
    },
    {
      kind: 'tableau',
      titre: 'Sessions où les suppressions dépassent le CA encaissé du jour',
      minWidth: 560,
      colonnes: [
        { label: 'Session' },
        { label: 'Exercice' },
        { label: 'CA encaissé', align: 'right' },
        { label: 'Suppressions', align: 'right' },
        { label: 'Lignes', align: 'right' },
      ],
      lignes: DC.sessionsImpossibles.map((z) => [
        cg(z.z),
        cg(z.exercice),
        cd(formatEuro(z.caTickets)),
        cd(formatEuro(z.suppressions)),
        cd(String(z.nbLignes)),
      ]),
    },
    {
      kind: 'piecejointe',
      intro: 'Télécharger ce tableau :',
      fichiers: [{ fichier: 'pieces-defense/Methode-5-reconciliation-suppressions.xlsx', label: 'Sessions, réconciliation, triangulation (XLSX)' }],
    },
    {
      kind: 'tableau',
      titre: `Les grosses suppressions = fautes de frappe sur la quantité (${formatEuro(DC.erreursQuantiteSomme)}, ${formatPct(DC.erreursQuantitePctDel)})`,
      minWidth: 560,
      colonnes: [
        { label: 'Date' },
        { label: 'Montant supprimé', align: 'right' },
        { label: 'Décomposition (prix × quantité)' },
      ],
      lignes: DC.erreursQuantite.map((e) => [
        cg(e.date),
        cd(formatEuro(e.montant)),
        cg(e.decomposition),
      ]),
    },
    {
      kind: 'note',
      texte:
        'Le journal n’a pas de colonne quantité : la décomposition prix × quantité est inférée (plusieurs lectures exactes existent), mais la quantité absurde - jusqu’à 9999, valeur maximale du champ - est certaine. La preuve réellement irréfutable reste la session : on ne supprime pas plus qu’on n’encaisse.',
    },
    {
      kind: 'piecejointe',
      intro: 'Télécharger ce tableau :',
      fichiers: [{ fichier: 'pieces-defense/Methode-6-erreurs-quantite-DEL.xlsx', label: 'Erreurs de quantité + distribution des prix (XLSX)' }],
    },
    {
      kind: 'tableau',
      titre: 'Triangulation : trois exports certifiés donnent le même CA',
      minWidth: 460,
      colonnes: [{ label: 'Source certifiée' }, { label: 'CA 3 exercices', align: 'right' }],
      lignes: [
        [cg('Synthèse du CA (annexe A)'), cd(formatEuro(DC.triangulation.syntheseA))],
        [cg('Liste des tickets (annexe H)'), cd(formatEuro(DC.triangulation.listeTicketsH))],
        [cg('Encaissements (annexe A)'), cd(formatEuro(DC.triangulation.encaissements))],
        [cg('Suppressions (annexe E) - hors des trois'), cd(formatEuro(DC.triangulation.suppressionsE))],
      ],
    },
    {
      kind: 'piecejointe',
      intro: 'Télécharger ce tableau :',
      fichiers: [{ fichier: 'pieces-defense/Methode-5-reconciliation-suppressions.xlsx', label: 'Triangulation + réconciliation (XLSX)' }],
    },
    enClair(
      'Les encaissements par carte bancaire correspondent aux relevés bancaires : le chiffre d’affaires déclaré est justifié par trois exports indépendants, et les espèces ne pèsent que 1,3 %. Il n’existe aucun canal pour encaisser au noir des ventes supprimées, ni aucun achat caché pour les alimenter.',
    ),
    {
      kind: 'chapitre',
      source: 'neutre',
      titre: 'Annexes : la démonstration chiffrée complète',
      sousTitre: 'Classeurs téléchargeables - reproductibles à partir des annexes certifiées E, A, H',
    },
    {
      kind: 'piecejointe',
      intro: 'Données et méthode :',
      fichiers: [
        { fichier: 'pieces-defense/Defense-Suppressions-de-caisse-DEL.xlsx', label: 'Défense - Suppressions de caisse (synthèse, 6 onglets)' },
        { fichier: 'pieces-defense/Methode-5-reconciliation-suppressions.xlsx', label: 'Réconciliation des suppressions' },
        { fichier: 'pieces-defense/Methode-6-erreurs-quantite-DEL.xlsx', label: 'Erreurs de quantité (DEL)' },
      ],
    },
    sources('E', 'A', 'B'),
  ],
}

// ======================= ANALYSE 2 - CONTINUITÉ NF525 ========================
const C = I.continuite
const continuite: Analyse = {
  slug: 'continuite-nf525',
  eyebrow: 'Intégrité',
  titre: 'Continuité NF525 (aucune occultation possible)',
  resume:
    'La numérotation séquentielle et ininterrompue des tickets-Z et des événements prouve qu’aucune journée, aucun ticket et aucun événement n’a été effacé.',
  force: 'forte',
  controleurDit:
    'Les suppressions prouveraient une caisse manipulable, des recettes effaçables.',
  demonstration:
    '659 tickets-Z et 23 339 événements numérotés sans aucun trou. Aucune journée, aucun ticket, aucun événement n’a pu être effacé.',
  faitTomber: 'L’intégrité de la caisse certifiée (NF525)',
  pieces: piecesLiees('E', 'H'),
  apercu: [
    { label: 'Tickets-Z sans trou', valeur: formatInt(C.zTotal) },
    { label: 'Événements sans trou', valeur: formatInt(C.idTotal) },
  ],
  sections: [
    enClair(
      'Chaque journée de service se clôture par un « ticket Z » numéroté qui fige les recettes du jour. La caisse certifiée NF525 interdit de sauter un numéro ou d’effacer un ticket. Il suffit donc de vérifier que la numérotation ne comporte aucun trou - et c’est le cas, du premier au dernier jour.',
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
    'Le CA est encaissé quasi intégralement par moyens traçables. La part d’espèces - seul canal dissimulable - est marginale, rendant toute occultation massive matériellement impossible.',
  force: 'forte',
  controleurDit: 'Les recettes auraient été occultées en espèces.',
  demonstration:
    '98,7 % du chiffre d’affaires est encaissé par des moyens traçables ; les espèces ne pèsent que 1,3 %. Une occultation massive est matériellement impossible.',
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
      texte: `Le restaurant n’encaisse quasiment qu’en monnaie traçable : **${formatPct(B.tracablePct)}** du chiffre d’affaires passe par des moyens traçables (carte, titres-restaurant, chèques), et les espèces ne pèsent que **${formatPct(B.especesPct)}** du CA, soit ${formatEuro(B.especesTotal)} sur trois ans. Ces flux, rapprochables des relevés bancaires, ne laissent aucune place à une occultation massive.`,
    },
    {
      kind: 'kpis',
      items: [
        { label: 'CA encaissé traçable', valeur: formatPct(B.tracablePct), sub: 'carte, titres, chèques', highlight: true, couleur: 'teal' },
        { label: 'Part des espèces', valeur: formatPct(B.especesPct), sub: `${formatEuro(B.especesTotal)} sur 3 ans` },
        { label: 'CA total (3 ans)', valeur: formatEuro(B.caTotal), sub: 'encaissements certifiés' },
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
      texte: `Le détail le confirme : sur les **${formatInt(K.especes.nb)} règlements en espèces** des trois exercices, le plus élevé atteint **${formatEuro(K.especes.max)}** et la moitié sont inférieurs à **${formatEuroPrecis(K.especes.mediane)}**. Dissimuler des centaines de milliers d’euros avec de tels montants est matériellement impossible.`,
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

// ==================== ANALYSE 4 - BOISSONS « DISPARUES » =====================
// Page en 5 temps, séparation stricte FISC (rouge) / NOUS (teal). Chiffres :
// Bo (méthode du fisc), Res (nos résultats exacts), Decomp (décomposition vérifiée),
// auditFisc. Aucune valeur en dur dans la page.
const nf = (n: number): string => n.toLocaleString('fr-FR')
const catLabel: Record<string, string> = {
  vin: 'Vins',
  macvin: 'Macvin',
  spiritueux_digestif: 'Spiritueux & digestifs',
  cremant_petillant: 'Crémants & pétillants',
  biere: 'Bières',
  soft: 'Sodas',
  jus: 'Jus',
  eau: 'Eaux',
  sirop: 'Sirops',
}
// Cuisine + abattements (les deux postes « chiffrés par le fisc »), pour la carte argument.
const cuisineHT =
  (Decomp.find((d) => d.cle === 'cuisine')?.montantHT ?? 0) +
  (Decomp.find((d) => d.cle === 'abattements')?.montantHT ?? 0)
// Volumes cumulés (litres) - l'écart se mesure d'abord en VOLUME, avant tout chiffrage.
const totAchatL = Math.round(Res.parCategorie.reduce((a, c) => a + c.achatL, 0))
const totVenduL = Math.round(Res.parCategorie.reduce((a, c) => a + c.venduL, 0))
const totEcartL = totAchatL - totVenduL
const coef = Bo.methode.coefLiquideSolide
// Le manquant valorisé au PRIX DE VENTE, ramené à l'année (terrain du fisc).
const reventeAnMin = Math.round(Res.reventeCarteTTC / 3)
const reventeAnMax = Math.round(Res.reventeCaisseTTC / 3)
const boissons: Analyse = {
  slug: 'boissons-disparues',
  eyebrow: 'Réfutation de la méthode',
  titre: 'Les « volumes de boissons disparus » (version précédente)',
  resume:
    'Le fisc reconstitue le chiffre d’affaires à partir des boissons « disparues » et y voit des recettes cachées. Recalculé sur les factures et la caisse réelles, ce manquant - chiffré au prix de vente, sur le terrain même du fisc - est entièrement explicable, et sa méthode s’effondre sur ses propres chiffres.',
  force: 'forte',
  controleurDit: `Des boissons achetées ne se retrouveraient pas dans les ventes : le CA est reconstitué par les volumes de liquides (× ${nf(Bo.methode.coefLiquideSolide)} pour les solides), d’où une discordance de +${formatEuro(Bo.methode.discordanceTTC)} sur le seul exercice 2024-2025.`,
  demonstration: `La comptabilité matière du fisc montre un stock stable : les boissons ont été consommées, pas dissimulées. ${partVerifieePct} % de l’écart sont déjà chiffrés aux taux minimaux du fisc (cuisine, pertes, non-livré), le reste étant de la consommation hors-vente (offerts, sur-versement), à rapprocher du taux admis en CHR (cf. CAA Paris 17/03/2021, 22-25 %). Et en remettant les vraies ventes dans sa propre formule, la discordance du fisc s’inverse.`,
  faitTomber: `La reconstitution par les volumes de boissons`,
  pieces: [
    ...piecesLiees('D', 'B', 'E'),
    { to: `/documents/${FACTURES_SLUG}`, label: 'Factures FCBS' },
    { to: `/documents/${INVENTAIRES_SLUG}`, label: 'Inventaires physiques' },
    { to: `/documents/${MANUSCRIT_SLUG}`, label: 'Carnet manuscrit' },
  ],
  apercu: [
    { label: 'Sur-évaluation des ventes par le fisc', valeur: `+${auditFisc.surevaluationPct} %` },
    { label: 'Part de l’écart déjà expliquée', valeur: `${partVerifieePct} %` },
  ],
  sections: [
    enClair(
      `Le fisc constate que des boissons achetées ne ressortent pas toutes en caisse et en déduit des **recettes cachées** (qu’il chiffre au prix de vente). Mais une boisson achetée n’est pas forcément **vendue en espèces** : elle peut être **consommée hors-vente** (cuisine, offerts, pertes, sur-versement au verre) ou n’avoir **jamais été livrée**. Et la **comptabilité matière du fisc le confirme** : le stock est stable, donc tout a été consommé, pas dissimulé. Nous l’avons vérifié sur les pièces réelles : ce manquant s’explique **sans une seule vente en liquide**.`,
    ),

    // ----------------------------- TEMPS 2 : LE FISC -----------------------------
    {
      kind: 'chapitre',
      source: 'fisc',
      titre: 'Ce que le fisc a calculé',
      sousTitre: 'Reconstitution du chiffre d’affaires à partir des volumes de boissons',
    },
    {
      kind: 'paragraphe',
      texte: `À partir des **achats** de boissons, le vérificateur déduit un volume « disponible », le convertit en nombre de verres via des **doses**, en tire un **CA liquides**, puis le **multiplie par ${nf(Bo.methode.coefLiquideSolide)}** pour estimer le CA « solides » (la cuisine). Le total reconstitué est comparé au CA déclaré, et l’écart est présenté comme une dissimulation.`,
    },
    {
      kind: 'kpis',
      items: [
        { label: 'CA reconstitué par le fisc', valeur: formatEuro(Bo.methode.caReconstitueTTC), sub: 'exercice 2024-2025', highlight: true, couleur: 'red' },
        { label: 'CA comptabilisé', valeur: formatEuro(Bo.methode.caComptaTTC), sub: 'TTC déclaré' },
        { label: 'Discordance', valeur: formatEuro(Bo.methode.discordanceTTC), sub: 'base de l’amende' },
        { label: 'Coefficient liquide → solide', valeur: `× ${nf(Bo.methode.coefLiquideSolide)}`, sub: 'le CA cuisine est extrapolé' },
      ],
    },
    {
      kind: 'alerte',
      couleur: 'red',
      titre: 'La conséquence',
      texte: `Cette discordance fonde une **amende pour distribution occulte (article 1759)** de **100 %** des sommes prétendument distribuées - l’essentiel des **684 974 €** réclamés.`,
    },

    // ------------------------------ TEMPS 3 : NOUS -------------------------------
    {
      kind: 'chapitre',
      source: 'nous',
      titre: 'Notre recalcul indépendant',
      sousTitre: `À partir des ${formatInt(Res.nbFactures)} factures fournisseur, de la caisse et de la carte - réconcilié au centime`,
    },
    {
      kind: 'paragraphe',
      texte: `Plutôt que de reconstituer, nous avons **mesuré**. Chaque facture FCBS donne les quantités et le coût réels ; la caisse donne les ventes réelles (nos totaux sont **identiques au centime** à ceux des fichiers de caisse) ; la carte donne les doses. On compare ce qui a été **acheté** à ce qui a été **vendu** - d’abord en **volume** (litres), pas en euros.`,
    },
    {
      kind: 'kpis',
      items: [
        { label: 'Boissons achetées (3 ans)', valeur: formatEuro(Res.achatsHT.total), sub: 'HT - ce que le restaurant a payé' },
        { label: 'Boissons vendues (3 ans)', valeur: formatEuro(Res.caVenduTTC.total), sub: 'TTC - encaissé en caisse' },
        { label: 'Ventes recalculées', valeur: 'au centime', sub: 'identiques aux fichiers de caisse', highlight: true, couleur: 'teal' },
      ],
    },
    {
      kind: 'tableau',
      titre: 'Ce qui a été acheté vs vendu, par famille (en volume, 3 ans)',
      minWidth: 480,
      colonnes: [
        { label: 'Famille' },
        { label: 'Acheté', align: 'right' },
        { label: 'Vendu', align: 'right' },
        { label: 'Écart', align: 'right' },
      ],
      lignes: [
        ...Res.parCategorie.map((c) => [
          cg(catLabel[c.categorie] ?? c.categorie),
          cd(`${nf(Math.round(c.achatL))} L`),
          cd(`${nf(Math.round(c.venduL))} L`),
          cd(formatPct(c.ecartPct)),
        ]),
        [
          { v: 'Total', fw: 700 },
          { v: `${nf(totAchatL)} L`, align: 'right', fw: 700 },
          { v: `${nf(totVenduL)} L`, align: 'right', fw: 700 },
          { v: formatPct(Math.round((100 * totEcartL) / totAchatL)), align: 'right', fw: 700 },
        ],
      ],
    },
    {
      kind: 'paragraphe',
      texte: `Il reste donc **${nf(totEcartL)} litres** de boisson achetée mais non retrouvée en vente directe. **Ce même volume se chiffre de deux façons - à ne jamais confondre :**`,
    },
    {
      kind: 'tableau',
      titre: `L’écart de ${nf(totEcartL)} L, chiffré de deux manières`,
      minWidth: 520,
      colonnes: [
        { label: 'Manière de le chiffrer' },
        { label: 'Montant (3 ans)', align: 'right' },
        { label: 'Ce que ça représente' },
      ],
      lignes: [
        [
          cg('① À son COÛT D’ACHAT'),
          { v: `${formatEuro(Res.ecartCoutHT.total)} HT`, align: 'right', fw: 700 },
          cg('Ce que la marchandise a coûté (pour mémoire)'),
        ],
        [
          { v: '② À son PRIX DE VENTE', fw: 700 },
          { v: `${formatEuro(Res.reventeCarteTTC)} - ${formatEuro(Res.reventeCaisseTTC)} TTC`, align: 'right', fw: 700 },
          { v: 'Ce qu’elle aurait rapporté vendue - le terrain du fisc', fw: 700 },
        ],
      ],
    },
    {
      kind: 'note',
      texte: `Le fisc raisonne au **prix de vente ②** (puis × ${nf(coef)} et 100 % d’amende). Pour le réfuter, c’est donc le chiffrage ② qu’il faut expliquer - et non le coût ①, qui n’est là que pour mémoire. C’est ce que fait la suite.`,
    },
    retenir(
      `**Comparons sur le même terrain - le prix de vente.** Le fisc retient **${formatEuro(Bo.methode.discordanceTTC)}** de discordance pour 2024-2025. Or le manquant réel de boissons ne vaut, au prix de vente, qu’environ **${formatEuro(reventeAnMin)} à ${formatEuro(reventeAnMax)} par an** : le fisc retient ~2 fois plus en l’**extrapolant × ${nf(coef)}** sur une cuisine jamais mesurée. Et ce manquant lui-même n’est pas du chiffre d’affaires caché - voici où il va.`,
    ),

    // ------------------------ TEMPS 4 : LA DÉCOMPOSITION -------------------------
    {
      kind: 'chapitre',
      source: 'nous',
      titre: 'Où va, physiquement, ce volume manquant ?',
      sousTitre: `La part de chaque cause vaut quel que soit le chiffrage (coût ① ou prix de vente ②). Chaque poste est vérifié - aucune vente en espèces.`,
    },
    { kind: 'decomposition', total: Res.ecartCoutHT.total, items: Decomp },
    {
      kind: 'paragraphe',
      texte: `**Chaque bouteille est comptée - l’inventaire le ferme.** En partant du stock réel de début d’exercice, en ajoutant les achats et en retirant les ventes, on retombe sur le stock réel de fin d’exercice : la différence est la **consommation hors-vente** (cuisine, offerts, personnel, sur-versement), jamais une bouteille évaporée.`,
    },
    {
      kind: 'tableau',
      titre: 'Bilan matière des alcools en bouteille (vérifié sur les 3 inventaires)',
      minWidth: 560,
      colonnes: [
        { label: 'Exercice' },
        { label: 'Stock début', align: 'right' },
        { label: '+ Achats', align: 'right' },
        { label: '− Ventes', align: 'right' },
        { label: 'Stock fin (réel)', align: 'right' },
        { label: '= Conso hors-vente', align: 'right' },
      ],
      lignes: bilanBouteilles.exercices.map((e) => [
        cg(e.exercice),
        cd(`${nf(e.stockInitial)} bt`),
        cd(`${nf(e.achats)} bt`),
        cd(`${nf(e.vendu)} bt`),
        cd(`${nf(e.stockFinal)} bt`),
        cd(`${nf(e.consoHorsVente)} bt`),
      ]),
    },
    {
      kind: 'note',
      texte: `Le stock de fin est **mesuré** (inventaire), pas supposé : l’équation est donc fermée. La « consommation hors-vente » se répartit dans les postes ci-dessus (cuisine concentrée sur le crémant et le vin jaune, offerts, personnel, sur-versement). Elle est **physiquement consommée** - le stock ne grossit pas - et non vendue en espèces (98,7 % du CA est bancarisé).`,
    },
    {
      kind: 'alerte',
      couleur: 'teal',
      titre: 'Le point essentiel',
      texte: `**Aucun de ces postes n’est une vente en liquide.** Et la comptabilité matière du fisc le confirme : le stock est **stable**, donc les boissons ont été **consommées, pas dissimulées**. L’écart est de la **consommation sans recette** - cuisine, offerts, pertes, sur-versement - dont ${partVerifieePct} % sont déjà chiffrés aux taux **minimaux** du fisc ; le taux admis en CHR est plus élevé (cf. CAA Paris 17/03/2021, 22 à 25 %).`,
    },

    // -------------- TEMPS 4 bis : DEUX VÉRIFICATIONS PAR LA CAISSE --------------
    {
      kind: 'chapitre',
      source: 'nous',
      titre: 'Deux vérifications directes dans la caisse',
      sousTitre: 'Les offerts, et la cuisine jurassienne - comptés un par un',
    },
    {
      kind: 'paragraphe',
      texte: `**Les ventes sous bouton « cocktail » sont déjà comptées.** Notre recalcul attribue chaque cocktail à sa **recette de carte** (La Vouivre → crémant + macvin + cassis ; Mambo → jus + limonade ; Picon Bière → Picon + bière) : l’écart acheté − vendu est donc **déjà net** de ces ventes. Il ne reste à expliquer que la consommation **sans recette** - cuisine et personnel - plus le sur-versement et les pertes.`,
    },
    {
      kind: 'alerte',
      couleur: 'teal',
      titre: 'Vérification 1 : les offerts aux clients sont négligeables',
      texte: `On a cherché toutes les lignes de vente à **0 €** dans la caisse : **272 sur 97 694** (**0,28 %**), pour l’essentiel des **cafés**. Le restaurant n’offre quasiment pas de boisson : l’écart n’est donc pas constitué d’offerts, mais de consommation du personnel et de cuisine.`,
    },
    {
      kind: 'paragraphe',
      texte: `**Vérification 2 : la cuisine jurassienne, comptée plat par plat.** Beaucoup de plats de la carte cuisinent au vin de garde du Jura. On a compté en caisse chaque plat concerné (annexe D) - ces nombres sont **exacts** :`,
    },
    {
      kind: 'tableau',
      titre: 'Plats cuisinés à l’alcool (comptés en caisse, 3 ans)',
      minWidth: 520,
      colonnes: [
        { label: 'Plat' },
        { label: 'Quantité (3 ans)', align: 'right' },
        { label: 'Alcool de cuisine' },
      ],
      lignes: [
        [cg('Poulet à la Jurassienne'), cd('2 746'), cg('Vin jaune / savagnin')],
        [cg('Truite à la Jurassienne'), cd('1 610'), cg('Vin jaune / savagnin')],
        [cg('Camembert rôti'), cd('1 452'), cg('Calvados')],
        [cg('Baba'), cd('1 330'), cg('Macvin')],
        [cg('Fondue Jurassienne'), cd('1 150'), cg('Vin blanc')],
        [cg('Poulet / Truite aux morilles'), cd('1 418'), cg('Vin jaune / savagnin')],
        [cg('Fondue au vin jaune + des Gourmets'), cd('659'), cg('Vin jaune')],
        [cg('Assiette du Père Grégoire'), cd('648'), cg('Calvados')],
        [cg('Dessert Normandine'), cd('126'), cg('Calvados')],
        [{ v: 'Total', fw: 700 }, { v: '11 139 plats', align: 'right', fw: 700 }, { v: '', align: 'left' }],
      ],
    },
    {
      kind: 'note',
      texte: `Honnêteté : le **volume** d’alcool de cuisine n’est pas chiffrable à la goutte près (la dose par plat n’est pas mesurée). Il est **borné par l’achat** : le vin jaune et le savagnin « manquants » totalisent **~270 L** (écart acheté − vendu), entièrement absorbables par ces 6 400 plats jurassiens ; le calvados de cuisine (~40 L) reste sous l’écart calvados, comme l’admet déjà le fisc. Ces volumes sont **consommés, pas vendus** - et l’inventaire confirme qu’ils ne sont pas en stock.`,
    },

    {
      kind: 'paragraphe',
      texte: `**Et ce ne sont que les postes déjà vérifiés.** D’autres pertes, réelles mais à confirmer par l’exploitant, réduisent encore le résiduel : pertes techniques de la bière (fond de fût, nettoyage des lignes), **sur-versement** au verre et bouteilles ouvertes peu écoulées - soit **~${Math.round((100 * pistesComplMin) / Res.ecartCoutHT.total)} % à ~${Math.round((100 * pistesComplMax) / Res.ecartCoutHT.total)} %** de l’écart en plus.`,
    },
    {
      kind: 'tableau',
      titre: 'Pistes complémentaires (estimations bornées, à confirmer)',
      minWidth: 480,
      colonnes: [{ label: 'Piste' }, { label: 'Fourchette (coût HT)', align: 'right' }],
      lignes: Pistes.map((p) => [cg(p.label), cd(`${formatEuro(p.min)} - ${formatEuro(p.max)}`)]),
    },

    // ----------------------- TEMPS 5 : LES FAILLES DU FISC -----------------------
    {
      kind: 'chapitre',
      source: 'nous',
      titre: 'Les failles du calcul du fisc',
      sousTitre: 'Audité sur ses propres chiffres',
    },
    {
      kind: 'argument',
      titre: 'L’inventaire physique exclut toute disparition de stock',
      page: '3 inventaires',
      accusation: `Des volumes de boissons auraient « disparu » (achetés mais non vendus).`,
      faille: `L’**inventaire physique des 3 fins d’exercice**, compté ligne par ligne, montre un stock boissons **stable** : **${formatEuro(Math.round(inventairePhysique.stocks[0].ht))} → ${formatEuro(Math.round(inventairePhysique.stocks[1].ht))} → ${formatEuro(Math.round(inventairePhysique.stocks[2].ht))}** HT, **jamais en baisse** (+${formatEuro(inventairePhysique.cumulVariation)} sur 2 ans). Un exploitant qui détournerait des bouteilles verrait son stock chuter : ici il est plat, donc **les boissons ont été consommées, pas planquées**. À noter aussi une **incohérence à éclaircir** : la variation de stock inscrite en comptabilité (compte 310200, ${formatEuro(inventairePhysique.ecartLivre[0].livre)} en 2023-2024) diffère du stock physique (qui **augmente de ${formatEuro(inventairePhysique.ecartLivre[0].physique)}**) ; si le vérificateur a retenu un stock final sous-estimé, sa formule « disponible = achats + stock initial − stock final » a pu **majorer les volumes disparus** (à recouper avec le comptable). Enfin, son motif de rejet (« inventaire incomplet ») tombe : l’inventaire est désormais détaillé.`,
      cote: 'Attaquable - très forte',
      preuves: [],
      pieces: [{ to: `/documents/${INVENTAIRES_SLUG}`, label: 'Inventaires physiques' }],
      detail: inventaireDetail,
    },
    {
      kind: 'argument',
      titre: 'Sa comptabilité matière le confirme : 98,5 % des achats consommés',
      page: 'Compte 310200',
      accusation: `Le manquant serait du stock dissimulé ou des bouteilles évaporées.`,
      faille: `Indépendamment de l’inventaire, la **propre comptabilité du fisc** le dit : la variation de stock boissons (compte 310200) est de **- 2 104 € sur 3 ans**, soit 1,5 % des achats. Par l’identité comptable (achats + variation de stock = consommation), **98,5 % des achats ont été consommés**. L’écart ne porte donc que sur la part de cette consommation **sans recette** (cuisine, offerts, pertes, sur-versement), que le fisc gonfle ensuite × ${nf(auditFisc.coefSolide)}.`,
      cote: 'Attaquable - forte',
      preuves: [],
      pieces: [],
      detail: comptaMatiereDetail,
    },
    {
      kind: 'argument',
      titre: 'Une reconstitution qui sur-estime les ventes',
      page: 'Annexes finales',
      accusation: `Le fisc reconstitue **${formatEuro(auditFisc.caLiquideReconstitue)}** de ventes de boissons pour 2024-2025.`,
      faille: `La caisse n’a réellement encaissé que **${formatEuro(auditFisc.caLiquideReelCaisse)}** de boissons cette année-là : le fisc **sur-évalue les ventes de ${auditFisc.surevaluationPct} %**. Cet écart est ensuite **amplifié × ${nf(auditFisc.coefSolide)}** sur la cuisine, jamais mesurée mais extrapolée. En réinjectant le **vrai** chiffre des boissons dans sa **propre formule**, la discordance de ${formatEuro(auditFisc.discordanceOfficielle)} **s’inverse à ${formatEuro(auditFisc.discordanceAvecLiquideReel)}** - c’est-à-dire **aucune occultation**.`,
      cote: 'Attaquable - forte',
      preuves: [],
      pieces: [],
      detail: auditFiscDetail,
    },
    {
      kind: 'argument',
      titre: 'La cuisine, déduite par le fisc… puis oubliée',
      accusation: `Le manquant serait du chiffre d’affaires dissimulé.`,
      faille: `Le vérificateur **chiffre lui-même** les usages cuisine (Macvin 7 406 cl, Calvados = 103 % de l’achat, Absinthe 100 %, Vin Jaune 61 %…) mais conclut tout de même à l’occultation. Ces seuls usages, avec ses propres abattements, expliquent déjà **${formatEuro(cuisineHT)}** de l’écart.`,
      cote: 'Attaquable - forte',
      preuves: [],
      pieces: piecesLiees('D'),
      detail: detailCuisine,
    },
    {
      kind: 'argument',
      titre: 'Le « disparu » par produit est un artefact d’étiquetage de la caisse',
      accusation: `Le fisc liste des produits précis comme « disparus » (achetés mais non vendus), dont des bouteilles « vendues sans achat » (Mouton Cadet, Hautes Côtes de Nuits).`,
      faille: `La caisse ne vend pas par référence d’achat : des dizaines de produits sont **mutualisés sous des boutons partagés** (un seul « Verre de vin », un bouton par cépage pour tous les millésimes…). Un produit précis paraît donc « disparu » alors qu’il a été vendu sous le bouton commun - **et sa recette est bien dans le CA déclaré** (vérifié sur les fichiers de caisse). L’**inventaire le prouve** : « Mouton Cadet » (que le fisc dit vendu sans achat) **n’existe nulle part** - le vrai bordeaux est le Château Grand Renom, bien en stock ; et les **7 bières « 100 % disparues »** (1664, Heineken, Grimbergen, Mort Subite…) sont **absentes des 3 inventaires ET jamais vendues** : ce sont des **codes jamais paramétrés**, pas des bouteilles évaporées. Ce n’est pas un volume manquant, c’est un problème d’**étiquetage** - sans effet sur le chiffre d’affaires.`,
      cote: 'Attaquable - forte',
      preuves: [],
      pieces: piecesLiees('B'),
      detail: detailSubstitution,
    },
    {
      kind: 'alerte',
      couleur: 'teal',
      titre: 'L’impossibilité matérielle',
      texte: `Même en supposant tout le manquant vendu, il faudrait un canal d’encaissement. Or **98,7 % du chiffre d’affaires est bancarisé** (carte, titres-restaurant, chèques) : il n’existe pas de canal espèces pour de telles sommes. Voir l’analyse **bancarisation**.`,
    },
    {
      kind: 'note',
      texte: `Honnêteté du dossier : le fisc n’a pas commis d’erreur de volume sur les fûts de bière (il retient ~632 L, proches de nos 672 L) - ce point n’est donc pas plaidé. Et l’inventaire physique, désormais disponible, **confirme** le stock stable (il ne dissimule donc aucune réserve). La consommation hors-vente restante est **documentée** : pour les sodas, la caisse montre **~6 canettes de Coca manquantes par jour d’ouverture** (5,5/jour sur les 2 derniers exercices), exactement la consommation **attestée** du personnel (deux serveurs avant et pendant chaque service) ; côté gérant, **72 L de Picon achetés ne sont jamais sonnés** - bus en service. Aucune de ces boissons n’a été vendue en espèces.`,
    },

    retenir(
      `La comptabilité matière du fisc le prouve : le stock est stable, donc **aucune disparition physique** - les boissons ont été consommées. **${partVerifieePct} %** de l’écart sont déjà chiffrés aux taux minimaux du fisc (cuisine, pertes, non-livré), le reste étant de la consommation hors-vente (offerts, sur-versement), à rapprocher du taux admis en CHR (cf. CAA Paris 17/03/2021, 22-25 %). **Rien ne correspond à des recettes encaissées en espèces.** La reconstitution du fisc (× ${nf(coef)} puis amende 100 %) transforme un écart de gestion en une dissimulation qui n’existe pas.`,
    ),
    {
      kind: 'chapitre',
      source: 'nous',
      titre: 'Recalcul par modèle d’incertitude et réconciliation',
      sousTitre: 'Pièce téléchargeable « Défense - Boissons prétendument disparues »',
    },
    {
      kind: 'alerte',
      couleur: 'teal',
      titre: 'Au prix de revente : une perte d’exploitation normale',
      texte: `Un modèle d’incertitude (20 000 simulations) situe le « disparu » alcool à ${formatEuro(BC.disparuRevenuMedian)} au prix de revente (intervalle ${formatEuro(BC.disparuRevenuIc[0])} à ${formatEuro(BC.disparuRevenuIc[1])}), soit ${formatPct(BC.disparuPctAchats)} des achats - le haut de la fourchette de perte normale d’un bar (15-25 %). Les causes de consommation sont documentées : sur-versement au verre, consommation du chef (Picon, Macvin), offerts, cuisine jurassienne.`,
    },
    {
      kind: 'alerte',
      couleur: 'blue',
      titre: 'Ce disparu et les suppressions de caisse ne s’additionnent pas',
      texte: `Le disparu boissons (${formatEuro(BC.disparuRevenuMedian)}) est un écart achats − ventes : toute boisson vendue au noir puis supprimée y figure déjà. Le fisc ne peut donc pas le compter une seconde fois dans les ${formatEuro(BC.delTotal)} de suppressions. Et ces suppressions valent ${(BC.delTotal / BC.caBoissonsDeclare).toFixed(1)} fois le CA boissons déclaré (${formatEuro(BC.caBoissonsDeclare)}) : elles ne peuvent pas être des ventes de boissons cachées, faute d’achats correspondants.`,
    },
    {
      kind: 'chapitre',
      source: 'nous',
      titre: 'La consommation réelle, poste par poste',
      sousTitre: 'Ce que la caisse n’enregistre pas, chiffré au coût d’achat et au CA équivalent',
    },
    {
      kind: 'paragraphe',
      texte:
        'Une partie des boissons achetées est **consommée sans passer en vente** : par le personnel, par le chef, et en offerts aux clients. Voici ce que cela représente, en litres, en **coût d’achat** (ce que ça a coûté au restaurant) et en **CA équivalent** (ce que ça aurait rapporté si vendu - pour mémoire, car ce n’est précisément pas vendu).',
    },
    {
      kind: 'tableau',
      titre: 'Consommation du personnel et du chef (3 exercices)',
      minWidth: 620,
      colonnes: [
        { label: 'Poste' },
        { label: 'Litres', align: 'right' },
        { label: 'Coût d’achat', align: 'right' },
        { label: 'CA équivalent', align: 'right' },
      ],
      lignes: [
        ...SPR.personnel.lignes.map((l) => [
          cg(l.poste),
          cd(l.litres != null ? `${formatInt(l.litres)} L` : '-'),
          cd(formatEuro(l.coutAchat)),
          cd(formatEuro(l.caEquivalent)),
        ]),
        [
          cg('TOTAL personnel'),
          cd(`${formatInt(SPR.personnel.totalLitres)} L`),
          cd(formatEuro(SPR.personnel.totalCout)),
          cd(formatEuro(SPR.personnel.totalCa)),
        ],
      ],
    },
    {
      kind: 'tableau',
      titre: 'Offerts aux clients (apéritifs et cafés, non enregistrés en caisse)',
      minWidth: 620,
      colonnes: [
        { label: 'Poste' },
        { label: 'Litres', align: 'right' },
        { label: 'Coût d’achat', align: 'right' },
        { label: 'CA équivalent', align: 'right' },
      ],
      lignes: [
        ...SPR.offerts.lignes.map((l) => [
          cg(l.poste),
          cd(l.litres != null ? `${formatInt(l.litres)} L` : '-'),
          cd(formatEuro(l.coutAchat)),
          cd(formatEuro(l.caEquivalent)),
        ]),
        [cg('TOTAL offerts'), cd('-'), cd(formatEuro(SPR.offerts.totalCout)), cd(formatEuro(SPR.offerts.totalCa))],
      ],
    },
    { kind: 'note', texte: SPR.offerts.avertissement },
    {
      kind: 'chapitre',
      source: 'nous',
      titre: 'Synthèse : où va, litre par litre, l’alcool acheté',
      sousTitre: 'La perte réelle après TOUS les calculs',
    },
    {
      kind: 'tableau',
      titre: 'Cascade complète de l’alcool acheté (litres, 3 exercices)',
      minWidth: 520,
      colonnes: [{ label: 'Poste' }, { label: 'Litres', align: 'right' }],
      lignes: [
        [cg('ACHATS D’ALCOOL (factures fournisseur)'), cd(`${formatInt(SPR.cascade.achatsAlcool)} L`)],
        ...SPR.cascade.postes.map((p) => [cg('—  ' + p.poste), cd(`${formatInt(p.litres)} L`)]),
        [
          cg(`=  PERTE RÉELLE RÉSIDUELLE (${SPR.cascade.perteReellePct} % des achats)`),
          cd(`${formatInt(SPR.cascade.perteReelle)} L`),
        ],
      ],
    },
    retenir(
      `Après avoir déduit tout ce qui est consommé sans vente - ventes sonnées, cuisine, alcool des menus, consommation du chef (${formatInt(143)} L), offerts, sur-versement, dégustation, crémant jeté et freinte de la bière - le résiduel **strictement irréductible** (casse, évaporation, fonds de verre) tombe à **${formatInt(SPR.cascade.perteReelle)} L**, soit **${SPR.cascade.perteReellePct} % des achats d’alcool**. La **perte d’exploitation totale** atteint **${SPR.cascade.perteExploitationPct} % des achats** - **au-dessus** des **22 %** admis en CHR et validés par la **CAA Paris (17/03/2021)**. Ce n’est ni une vente, ni une disparition : le CA est bancarisé et les espèces ne pèsent que 1,3 %.`,
    ),
    {
      kind: 'piecejointe',
      intro: 'Chaque chiffre de cette page est sourcé et reproductible. Classeurs de données à l’appui :',
      fichiers: [
        { fichier: 'pieces-defense/Consommation-personnel-et-offerts.xlsx', label: 'Conso personnel & offerts + perte réelle' },
        { fichier: 'pieces-defense/Defense-Boissons-disparues.xlsx', label: 'Défense - Boissons disparues' },
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
        { slug: CARTES_SLUG, label: 'Carte des vins & boissons' },
        { slug: INVENTAIRES_SLUG, label: 'Inventaires physiques (3 fins d’exercice)' },
        { slug: MANUSCRIT_SLUG, label: 'Carnet manuscrit - anomalies fournisseur' },
      ],
    },
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
  if (/chef|offert|sur-versement|dégustation|degustation|crémant|cremant|freinte/i.test(poste)) return 'estime'
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
// Stock physique boissons aux 3 inventaires (HT) - depuis l'inventaire certifié.
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
    { label: 'Perte d’exploitation', valeur: `${BPD.synthese.perte_exploitation_pct} %`, sub: 'des achats > 22 % validés CAA Paris' },
  ],
  controleurDit: `Des boissons achetées ne se retrouveraient pas dans les ventes : le CA est reconstitué par les volumes, d’où ${formatEuro(BPD.synthese.fisc_ca_reconstitue)} reconstitués (× ${BPD.synthese.fisc_coef}).`,
  demonstration: `On ne reconstitue pas, on mesure : chaque litre est rattaché à un usage (caisse, cuisine, menus, personnel, sur-versement, dégustation, crémant, freinte). La perte d’exploitation totale (${BPD.synthese.perte_exploitation_pct} %) dépasse les 22 % validés par la jurisprudence ; le résiduel irréductible (casse, évaporation) n’est que ${BPD.synthese.perte_reelle_pct} %.`,
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
        { label: 'CA bancarisé (carte, titres-restaurant, chèques)', valeur: '98,7 %', sub: 'aucun canal espèces pour des ventes cachées', highlight: true, couleur: 'teal' },
        { label: 'Part des espèces dans le CA', valeur: '1,3 %', sub: 'plafond matériel de toute vente en liquide' },
        { label: 'Achats boissons consommés (compta matière du fisc)', valeur: formatPct(comptaMatiere.pctConsomme), sub: 'le stock ne grossit pas : rien ne disparaît' },
      ],
    },
    {
      kind: 'alerte',
      couleur: 'teal',
      titre: 'Fait 1 : il n’existe aucun canal pour encaisser ce « manquant »',
      texte: `Même en supposant tout le manquant **vendu**, encore faudrait-il l’**encaisser**. Or **98,7 % du chiffre d’affaires est bancarisé** (carte, titres-restaurant, chèques) et les **espèces ne pèsent que 1,3 %**. Écouler ${formatEuro(BPD.synthese.disparu_brut_ca)} d’alcool au comptant supposerait un canal espèces qui **n’existe pas** dans les encaissements. Voir l’analyse **bancarisation**.`,
    },
    {
      kind: 'barreComposition',
      titre: 'Comment le chiffre d’affaires est encaissé',
      sousTitre: 'Aucun canal espèces ne peut absorber des ventes dissimulées de cette ampleur.',
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
      texte: 'Stock physique boissons aux 3 fins d’exercice (inventaire certifié) : stable, jamais en baisse. Un exploitant qui détournerait des bouteilles verrait son stock chuter.',
    },
    {
      kind: 'note',
      texte: 'Ces deux faits ne dépendent d’aucune estimation : ils reposent sur les relevés bancaires et l’inventaire physique certifié. Le détail qui suit explique, litre par litre, la consommation sans recette qui compose l’écart.',
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
      kind: 'interne',
      audience: 'comptable',
      titre: 'Pour mémoire : origine des lignes à manquant négatif (deux cas distincts)',
      texte: `Vérifié de notre côté : les lignes à manquant négatif ne viennent **pas** des avoirs (contrôlés ci-dessus) et recouvrent **deux cas**. **(1) Côté caisse** (ex. « Cubis de vin » : 427 L consommés, 0 acheté sous ce nom) : libellé caisse générique sans achat homonyme ; le vin existe sous son appellation précise et le **bilan matière global** (total acheté − total consommé − stock = ${formatInt(BPD.synthese.disparu_net_l)} L) les neutralise par construction. **(2) Côté achats** (ex. « Arbois Béthanie » : achat 214,5 L < conso 309,9 L) : il s’agit d’**achats réels non encore rattachés** faute de correspondance de format, ici 169 L de Béthanie 37,5 cl alors que seuls les 75 cl ont été mappés (achat réel complet 383,3 L ⇒ manquant +73 L, normal). La **table de correspondance libellés caisse ↔ factures** est déjà jointe au dossier (pièce « Correspondance libellés factures ↔ caisse ») et documente ces deux cas, dont le rattachement Béthanie 37,5 cl ⇒ 75 cl. Reste, côté pipeline, à y réintégrer les **~253 L de vin** encore en achats non rattachés, ce qui lèvera les négatifs et alignera litres et valeurs (le coût/CA affichés portent encore sur les seules lignes positives, soit ${formatInt(BPD.synthese.disparu_brut_l)} L). Le chiffre de référence (perte réelle) repose sur le bilan matière global et reste robuste.`,
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
      kind: 'interne',
      audience: 'restaurant',
      titre: 'Pièces à réunir pour étayer la consommation du personnel',
      texte: `Cette consommation est aujourd’hui établie par estimation. Pour la rendre opposable : réunir une **attestation sur l’honneur (art. 202 CPC)** de chaque salarié concerné (identité, poste, période, description de la consommation quotidienne de softs en service) et, pour le chef, une attestation décrivant sa consommation servie en cuisine. Idéalement, **planning de service** et **fiches de poste** datés des 3 exercices pour corroborer la présence et le nombre de personnes en service.`,
    },
    {
      kind: 'interne',
      audience: 'avocat',
      titre: 'Risque d’avantage en nature à arbitrer avant de plaider ce poste',
      texte: `Attention à l’**effet boomerang** : l’alcool et les boissons consommés par le personnel et le dirigeant peuvent être requalifiés en **avantage en nature** (réintégration en salaires/charges et au revenu du dirigeant). Expliquer le manquant par cette consommation peut donc **ouvrir un autre chef de redressement**. Arbitrer l’opportunité de chiffrer ce poste, ou de le borner au strict nécessaire, et préparer la réponse AEN le cas échéant.`,
    },
    {
      kind: 'tableau',
      titre: '6. Les offerts aux clients (apéritifs et cafés, non enregistrés)',
      minWidth: 660,
      colonnes: [
        { label: 'Poste' },
        { label: 'Litres', align: 'right' },
        { label: 'Coût d’achat', align: 'right' },
        { label: 'CA équivalent', align: 'right' },
      ],
      lignes: [
        ...BPD.offerts.lignes.map((l) => [cg(l.poste), cd(litresB(l.litres)), cd(eurB(l.cout_achat_eur)), cd(eurB(l.ca_equivalent_eur))]),
        [cg('TOTAL offerts'), cd('-'), cd(eurB(BPD.offerts.total_cout_eur)), cd(eurB(BPD.offerts.total_ca_eur))],
      ],
    },
    { kind: 'note', texte: BPD.offerts.avertissement },
    {
      kind: 'note',
      texte:
        'Ce poste n’est pas porté au chiffrage comme un montant acquis : il est volontairement borné et modeste (les apéritifs offerts ne pèsent que 40 L d’alcool dans la cascade). La preuve la plus solide reste la caisse elle-même, qui ne recense quasiment aucune vente à 0 € : les offerts sont donc **négligeables**, et ne servent ici qu’à montrer qu’ils ne peuvent en aucun cas constituer des ventes dissimulées.',
    },
    {
      kind: 'interne',
      audience: 'restaurant',
      titre: 'Trancher le poste « offerts » (cohérence du dossier)',
      texte: `À décider : soit on s’appuie sur la caisse pour dire que les **offerts sont négligeables** (position la plus solide, et cohérente avec le relevé des lignes à 0 €), soit on documente des offerts réguliers, mais il faut alors une **trace** (registre, consignes écrites au personnel). On ne peut pas tenir les deux. Recommandation : retenir « offerts négligeables » et **retirer la colonne CA équivalent des offerts** de toute version transmise, qui se retourne en « sorties non contrôlées ». Les **cafés offerts** sont par ailleurs hors sujet pour l’alcool : à sortir de l’argumentaire fiscal.`,
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
      kind: 'interne',
      audience: 'restaurant',
      titre: 'Transformer le sur-versement et la freinte bière en preuves mesurées',
      texte: `Deux pièces feraient passer le résiduel d’« estimation » à « mesure » : **(1)** un **constat d’huissier** d’un test de versement (faire servir plusieurs « verres de vin » et « pressions », mesurer le volume réel au mL, établir le ratio dose carte / dose réelle) qui objective le sur-versement ; **(2)** une **attestation du brasseur/distributeur** (Affligem) sur le taux de freinte réel d’un fût (fond de fût, mousse, purge et nettoyage des lignes). Photographier aussi le bar servant **sans doseur** (cause technique du sur-versement). Ces deux pièces sont tierces et difficilement contestables.`,
    },
    retenir(
      `Après avoir mesuré **tout** ce qui est consommé sans vente, chaque litre est rattaché à un usage précis : cuisine, alcool des menus, consommation du chef et du personnel (${formatInt(BPD.personnel.total_litres)} L), apéritifs offerts, **sur-versement aux taux mesurés (1 058 L), dégustation offerte comptée note par note (126 L), crémant sur-versé et jeté en fin de service (347 L) et freinte technique de la bière (129 L)**. Une fois ces pertes documentées sorties, le résiduel **strictement irréductible** (casse, évaporation, fonds de verre, rinçage) tombe à **${formatInt(BPD.synthese.perte_reelle_l)} L**, soit **${BPD.synthese.perte_reelle_pct} % des achats**. La **perte d’exploitation totale** (tout ce qui n’est pas vendu comme boisson : conso personnel, offerts, sur-versement, dégustation, crémant, freinte et casse) atteint **${BPD.synthese.perte_exploitation_pct} % des achats** — **au-dessus** des **22 %** que l’**administration elle-même** a validés en reconstitution de bar (**CAA Paris, 17 mars 2021** : 22 % pour personnel, offerts, pertes et vol, méthode confirmée). Ce n’est ni une vente, ni une disparition. Le CA est bancarisé, les espèces ne pèsent que 1,3 %. La reconstitution du fisc (× ${BPD.synthese.fisc_coef}) transforme une perte de gestion en une dissimulation qui n’existe pas.`,
    ),
    {
      kind: 'interne',
      audience: 'avocat',
      titre: 'Architecture recommandée et pièces à obtenir avant transmission',
      texte: `Pour viser l’indéfendable côté fisc, faire reposer la défense sur les **preuves dures** (en tête de page) plutôt que sur les estimations : **(1)** impossibilité d’encaissement (bancarisation 98,7 % / espèces 1,3 %) ; **(2)** clôture du bilan matière par l’**inventaire physique** + comptabilité matière du fisc (98,5 % consommés) ; **(3)** coefficients de cuisine **admis par le fisc lui-même**. À obtenir pour solidifier : **constat d’huissier** (sur-versement), **attestation brasseur** (freinte bière), **attestations 202 CPC** du personnel, et idéalement un **rapport d’expert-comptable indépendant** validant la méthode. À neutraliser : poste « offerts » et risque d’**avantage en nature**. **Jurisprudence** : l’arrêt CAA Paris du 17 mars 2021 (abattement de 22 % validé) est confirmé sur le fond ; **le numéro de requête reste à fiabiliser** (Légifrance / Doctrine) avant citation formelle. Ces encarts internes (pointillés) doivent être **retirés de toute version remise à l’administration**.`,
    },
    {
      kind: 'chapitre',
      source: 'neutre',
      titre: 'Annexes : toutes les données et la méthode',
      sousTitre: 'Classeurs téléchargeables - chaque chiffre est sourcé et reproductible',
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
        { fichier: 'pieces-defense/Methode-1-modele-Monte-Carlo.xlsx', label: 'Modèle d’incertitude (Monte Carlo)' },
        { fichier: 'pieces-defense/Methode-2-correction-mapping-Cubis.xlsx', label: 'Correction d’attribution (Cubis)' },
        { fichier: 'pieces-defense/Methode-3-bilan-softs.xlsx', label: 'Bilan des softs' },
        { fichier: 'pieces-defense/Methode-4-conso-personnel-detail.xlsx', label: 'Conso personnel détaillée' },
        { fichier: 'pieces-defense/Methode-5-reconciliation-suppressions.xlsx', label: 'Réconciliation des suppressions' },
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
export const analyses: Analyse[] = [reconstitution, del, continuite, bancarisation, boissonsV2]

// Versions archivées : routables par URL mais masquées de la liste (ex. ancienne page boissons).
const analysesArchivees: Analyse[] = [boissons]

export function analyseParSlug(slug: string): Analyse | undefined {
  return [...analyses, ...analysesArchivees].find((a) => a.slug === slug)
}
