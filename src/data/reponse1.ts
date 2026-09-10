// =============================================================================
// RÉPONSE 1 - Contre-analyse de la « Réponse aux observations du contribuable »
// -----------------------------------------------------------------------------
// Source : src/data/Direction_finances_réponse_observations_controle_fiscal_04_09_26.pdf
//   (DDFiP du Jura, Brigade départementale de vérifications, 4 septembre 2026,
//    48 feuillets / 96 pages, réponse au courrier THIVEND AVOCAT du 10/07/2026).
//
// L'architecture de cet onglet REPREND EXACTEMENT celle du courrier :
//   PROCEDURE                                        -> bloc 1
//   POINTS DU REJET DE LA COMPTABILITE CONTESTES     -> bloc 2 (A à K, + U)
//   Reconstitution du chiffre d'affaires (L à T)     -> bloc 3
//   C- CONSEQUENCES FINANCIERES ET PENALITES         -> bloc 4
// Une page par point du courrier ; les 11 sous-points de la partie « L » sont
// des sous-pages (numérotation 3.1.1 … 3.1.11).
//
// Le CONTENU rédigé de chaque page vit dans src/data/reponse1/<slug>.json
// (format { meta, sections } identique au Rendu final) et est chargé ici par
// import.meta.glob : ajouter un JSON suffit, aucun import à écrire.
// =============================================================================

import type { Section } from './analyses'

// --- Blocs (parties du courrier du 04/09/2026) -------------------------------
export type BlocId = 'procedure' | 'rejet' | 'reconstitution' | 'consequences'

export interface Bloc {
  id: BlocId
  numero: number
  titre: string
  sousTitre: string
}

export const blocs: Bloc[] = [
  {
    id: 'procedure',
    numero: 1,
    titre: 'Procédure',
    sousTitre:
      'Encadrés « PROCEDURE » et « L’article L-47-A-II du Livre des Procédures Fiscales » (p. 2 du courrier) : le service constate que la réponse n’a pas abordé ces points.',
  },
  {
    id: 'rejet',
    numero: 2,
    titre: 'Points du rejet de la comptabilité contestés',
    sousTitre:
      'Encadré « POINTS DU REJET DE LA COMPTABILITE CONTESTES » (p. 3 à 58), parties A à K, complété par la partie U (p. 93) sur les motifs que le service estime laissés sans réponse.',
  },
  {
    id: 'reconstitution',
    numero: 3,
    titre: 'Reconstitution du chiffre d’affaires',
    sousTitre:
      'Parties L à T (p. 59 à 92) : le cadre général de la reconstitution, les onze points chiffrés contestés par la réponse, puis la méthode « cascade » et chacun de ses postes.',
  },
  {
    id: 'consequences',
    numero: 4,
    titre: 'Conséquences financières et pénalités',
    sousTitre:
      'Encadré « C- CONSEQUENCES FINANCIERES ET PENALITES » (p. 94-95) : rappels et profit sur le Trésor, majoration de 40 %, amende de 100 % (art. 1759 CGI) et intérêts de retard.',
  },
]

export type Statut = 'demonte' | 'partiel' | 'a-etayer'

export interface Point {
  slug: string
  bloc: BlocId
  /** Numérotation forcée dans le sommaire (ex. « 3.1.3 » pour une sous-page). */
  numero?: string
  /** Lettre de la partie dans le courrier du 04/09/2026 (A, B, … U). */
  lettre?: string
  /** Slug de la page parente, pour les sous-pages. */
  parent?: string
  /** Pagination dans le courrier de réponse du 04/09/2026. */
  refCourrier: string
  titre: string
  /** Résumé de la position que le service maintient sur ce point. */
  positionService: string
  /** Notre verdict en une phrase. */
  reponseCourte: string
  enjeu?: string
  statut: Statut
}

// --- Les 37 pages, dans l'ordre exact du courrier ---------------------------
export const points: Point[] = [
  // ---------------------------------------------------------------- BLOC 1 --
  {
    slug: 'procedure-l47-a-ii',
    bloc: 'procedure',
    refCourrier: 'Réponse du 04/09/2026, p. 2',
    titre: 'Procédure et article L. 47 A-II du LPF',
    positionService:
      'Le service relève que la société n’a émis aucune observation sur la partie « Procédure », et que la réponse « n’aborde pas spécifiquement » l’article L. 47 A-II du LPF, se concentrant sur le détail des fichiers.',
    reponseCourte:
      'Le silence sur un point de procédure ne vaut pas acquiescement, et l’absence d’observation en phase contradictoire ne prive d’aucun moyen ultérieur.',
    statut: 'a-etayer',
  },
  // ---------------------------------------------------------------- BLOC 2 --
  {
    slug: 'suppressions-de-notes',
    bloc: 'rejet',
    lettre: 'A',
    refCourrier: 'Réponse du 04/09/2026, p. 3 à 17',
    titre: 'A — Les suppressions de notes (lignes « DEL »)',
    positionService:
      'Le service estime que les exemples produits n’expliquent qu’une infime partie des 21 302 lignes « DEL », et que l’absence d’identifiant unique commun entre le fichier « tpvenement » et les fichiers Règlement / Ticket ligne / Ticket / TVA interdit tout rapprochement certain.',
    reponseCourte: '',
    enjeu: 'Pilier n° 1 du rejet de comptabilité',
    statut: 'a-etayer',
  },
  {
    slug: 'factures-sans-detail',
    bloc: 'rejet',
    lettre: 'B',
    refCourrier: 'Réponse du 04/09/2026, p. 18 à 20',
    titre: 'B — Les factures sans détail (menus à prix personnalisé)',
    positionService:
      'Le service juge l’argument des menus à prix personnalisé « tardif », puis oppose les obligations d’archivage et de traçabilité du BOI-TVA-DECLA-30-10-30 : l’identifiant unique du fichier « tpvenement » n’étant repris nulle part ailleurs, la traçabilité fait défaut.',
    reponseCourte: '',
    statut: 'a-etayer',
  },
  {
    slug: 'articles-a-zero-euro',
    bloc: 'rejet',
    lettre: 'C',
    refCourrier: 'Réponse du 04/09/2026, p. 21 à 27',
    titre: 'C — Les articles à prix 0 € (offert / gratuit)',
    positionService: '',
    reponseCourte: '',
    statut: 'a-etayer',
  },
  {
    slug: 'quantites-anormales',
    bloc: 'rejet',
    lettre: 'D',
    refCourrier: 'Réponse du 04/09/2026, p. 28 à 29',
    titre: 'D — Les quantités anormales',
    positionService: '',
    reponseCourte: '',
    statut: 'a-etayer',
  },
  {
    slug: 'inventaires-de-stocks',
    bloc: 'rejet',
    lettre: 'E',
    refCourrier: 'Réponse du 04/09/2026, p. 30 à 34',
    titre: 'E — Les inventaires de stocks',
    positionService: '',
    reponseCourte: '',
    statut: 'a-etayer',
  },
  {
    slug: 'tables-virtuelles',
    bloc: 'rejet',
    lettre: 'F',
    refCourrier: 'Réponse du 04/09/2026, p. 35 à 37',
    titre: 'F — Trop de tables / les tables « virtuelles »',
    positionService: '',
    reponseCourte: '',
    statut: 'a-etayer',
  },
  {
    slug: 'fichiers-evenement-reglement',
    bloc: 'rejet',
    lettre: 'G',
    refCourrier: 'Réponse du 04/09/2026, p. 38 à 45',
    titre: 'G — Les fichiers Événement et Règlement',
    positionService: '',
    reponseCourte: '',
    statut: 'a-etayer',
  },
  {
    slug: 'incoherences-de-tva',
    bloc: 'rejet',
    lettre: 'H',
    refCourrier: 'Réponse du 04/09/2026, p. 46 à 47',
    titre: 'H — Les incohérences de TVA',
    positionService: '',
    reponseCourte: '',
    statut: 'a-etayer',
  },
  {
    slug: 'consommation-superieure-achats',
    bloc: 'rejet',
    lettre: 'I',
    refCourrier: 'Réponse du 04/09/2026, p. 48 à 53',
    titre: 'I — La consommation vendue supérieure aux achats',
    positionService: '',
    reponseCourte: '',
    statut: 'a-etayer',
  },
  {
    slug: 'prix-du-menu-demi-lune',
    bloc: 'rejet',
    lettre: 'J',
    refCourrier: 'Réponse du 04/09/2026, p. 54 à 55',
    titre: 'J — L’instabilité des prix du « menu Demi Lune »',
    positionService: '',
    reponseCourte: '',
    statut: 'a-etayer',
  },
  {
    slug: 'coefficient-de-revente',
    bloc: 'rejet',
    lettre: 'K',
    refCourrier: 'Réponse du 04/09/2026, p. 56 à 58',
    titre: 'K — Le coefficient de revente jugé trop bas',
    positionService: '',
    reponseCourte: '',
    statut: 'a-etayer',
  },
  {
    slug: 'motifs-de-rejet-absents',
    bloc: 'rejet',
    lettre: 'U',
    refCourrier: 'Réponse du 04/09/2026, p. 93',
    titre: 'U — Les motifs de rejet « absents » de la réponse',
    positionService: '',
    reponseCourte: '',
    statut: 'a-etayer',
  },
  // ---------------------------------------------------------------- BLOC 3 --
  {
    slug: 'reconstitution-cadre-general',
    bloc: 'reconstitution',
    lettre: 'L',
    refCourrier: 'Réponse du 04/09/2026, p. 59',
    titre: 'L — La reconstitution du chiffre d’affaires',
    positionService: '',
    reponseCourte: '',
    statut: 'a-etayer',
  },
  {
    slug: 'recon-1-doses-figees',
    bloc: 'reconstitution',
    parent: 'reconstitution-cadre-general',
    numero: '3.1.1',
    refCourrier: 'Réponse du 04/09/2026, p. 60',
    titre: '1 — Doses figées au centilitre (zéro sur-versement)',
    positionService: '',
    reponseCourte: '',
    statut: 'a-etayer',
  },
  {
    slug: 'recon-2-perte-biere',
    bloc: 'reconstitution',
    parent: 'reconstitution-cadre-general',
    numero: '3.1.2',
    refCourrier: 'Réponse du 04/09/2026, p. 61',
    titre: '2 — Zéro perte sur la bière',
    positionService: '',
    reponseCourte: '',
    statut: 'a-etayer',
  },
  {
    slug: 'recon-3-cremant-vendu',
    bloc: 'reconstitution',
    parent: 'reconstitution-cadre-general',
    numero: '3.1.3',
    refCourrier: 'Réponse du 04/09/2026, p. 62 à 63',
    titre: '3 — Tout le crémant réputé vendu',
    positionService: '',
    reponseCourte: '',
    statut: 'a-etayer',
  },
  {
    slug: 'recon-4-degustation',
    bloc: 'reconstitution',
    parent: 'reconstitution-cadre-general',
    numero: '3.1.4',
    refCourrier: 'Réponse du 04/09/2026, p. 64',
    titre: '4 — Aucune dégustation offerte',
    positionService: '',
    reponseCourte: '',
    statut: 'a-etayer',
  },
  {
    slug: 'recon-5-alcool-cuisine',
    bloc: 'reconstitution',
    parent: 'reconstitution-cadre-general',
    numero: '3.1.5',
    refCourrier: 'Réponse du 04/09/2026, p. 65 à 68',
    titre: '5 — L’alcool de cuisine sous-déduit',
    positionService: '',
    reponseCourte: '',
    statut: 'a-etayer',
  },
  {
    slug: 'recon-6-alcool-plats-menus',
    bloc: 'reconstitution',
    parent: 'reconstitution-cadre-general',
    numero: '3.1.6',
    refCourrier: 'Réponse du 04/09/2026, p. 68 à 70',
    titre: '6 — L’alcool cuit dans les plats des menus',
    positionService: '',
    reponseCourte: '',
    statut: 'a-etayer',
  },
  {
    slug: 'recon-7-conso-personnel',
    bloc: 'reconstitution',
    parent: 'reconstitution-cadre-general',
    numero: '3.1.7',
    refCourrier: 'Réponse du 04/09/2026, p. 70 à 71',
    titre: '7 — La consommation du personnel plafonnée à 5 %',
    positionService: '',
    reponseCourte: '',
    statut: 'a-etayer',
  },
  {
    slug: 'recon-8-abattements',
    bloc: 'reconstitution',
    parent: 'reconstitution-cadre-general',
    numero: '3.1.8',
    refCourrier: 'Réponse du 04/09/2026, p. 71 à 73',
    titre: '8 — Les abattements 5 % + 5 % + 5 %',
    positionService: '',
    reponseCourte: '',
    statut: 'a-etayer',
  },
  {
    slug: 'recon-9-variation-de-stock',
    bloc: 'reconstitution',
    parent: 'reconstitution-cadre-general',
    numero: '3.1.9',
    refCourrier: 'Réponse du 04/09/2026, p. 74',
    titre: '9 — Le « volume disponible » gonflé par une variation de stock erronée',
    positionService: '',
    reponseCourte: '',
    statut: 'a-etayer',
  },
  {
    slug: 'recon-10-ventes-sans-achat',
    bloc: 'reconstitution',
    parent: 'reconstitution-cadre-general',
    numero: '3.1.10',
    refCourrier: 'Réponse du 04/09/2026, p. 74 à 75',
    titre: '10 — Les « ventes sans achat » présentées comme recettes occultées',
    positionService: '',
    reponseCourte: '',
    statut: 'a-etayer',
  },
  {
    slug: 'recon-11-coefficient-liquide-solide',
    bloc: 'reconstitution',
    parent: 'reconstitution-cadre-general',
    numero: '3.1.11',
    refCourrier: 'Réponse du 04/09/2026, p. 76',
    titre: '11 — Le coefficient liquide → solide',
    positionService: '',
    reponseCourte: '',
    statut: 'a-etayer',
  },
  {
    slug: 'cascade-10622-litres',
    bloc: 'reconstitution',
    lettre: 'M',
    refCourrier: 'Réponse du 04/09/2026, p. 76 à 77',
    titre: 'M — Notre méthode : la cascade des 10 622 L',
    positionService: '',
    reponseCourte: '',
    statut: 'a-etayer',
  },
  {
    slug: 'sur-versement-au-verre',
    bloc: 'reconstitution',
    lettre: 'N',
    refCourrier: 'Réponse du 04/09/2026, p. 78 à 81',
    titre: 'N — Le sur-versement au verre',
    positionService: '',
    reponseCourte: '',
    statut: 'a-etayer',
  },
  {
    slug: 'perte-de-biere',
    bloc: 'reconstitution',
    lettre: 'O',
    refCourrier: 'Réponse du 04/09/2026, p. 82 à 83',
    titre: 'O — La perte de bière (mousse et tirage)',
    positionService: '',
    reponseCourte: '',
    statut: 'a-etayer',
  },
  {
    slug: 'perte-de-cremant',
    bloc: 'reconstitution',
    lettre: 'P',
    refCourrier: 'Réponse du 04/09/2026, p. 84 à 85',
    titre: 'P — La perte de crémant (bouteille ouverte non terminée)',
    positionService: '',
    reponseCourte: '',
    statut: 'a-etayer',
  },
  {
    slug: 'degustation-offerte',
    bloc: 'reconstitution',
    lettre: 'Q',
    refCourrier: 'Réponse du 04/09/2026, p. 85 à 86',
    titre: 'Q — La dégustation offerte (goûter du vin)',
    positionService: '',
    reponseCourte: '',
    statut: 'a-etayer',
  },
  {
    slug: 'alcool-de-cuisine',
    bloc: 'reconstitution',
    lettre: 'R',
    refCourrier: 'Réponse du 04/09/2026, p. 87 à 88',
    titre: 'R — L’alcool de cuisine (566 L)',
    positionService: '',
    reponseCourte: '',
    statut: 'a-etayer',
  },
  {
    slug: 'abattements-et-pertes-itemisees',
    bloc: 'reconstitution',
    lettre: 'S',
    refCourrier: 'Réponse du 04/09/2026, p. 89',
    titre: 'S — Les abattements forfaitaires et les pertes itemisées',
    positionService: '',
    reponseCourte: '',
    statut: 'a-etayer',
  },
  {
    slug: 'extrapolation-cuisine',
    bloc: 'reconstitution',
    lettre: 'T',
    refCourrier: 'Réponse du 04/09/2026, p. 90 à 92',
    titre: 'T — L’extrapolation cuisine',
    positionService: '',
    reponseCourte: '',
    statut: 'a-etayer',
  },
  // ---------------------------------------------------------------- BLOC 4 --
  {
    slug: 'rappels-et-profit-sur-le-tresor',
    bloc: 'consequences',
    lettre: 'A',
    refCourrier: 'Réponse du 04/09/2026, p. 94',
    titre: 'A — Rappels et profit sur le Trésor',
    positionService: '',
    reponseCourte: '',
    statut: 'a-etayer',
  },
  {
    slug: 'penalites-et-amendes',
    bloc: 'consequences',
    lettre: 'B',
    refCourrier: 'Réponse du 04/09/2026, p. 94 à 95',
    titre: 'B — Pénalités et amendes (majoration de 40 %)',
    positionService: '',
    reponseCourte: '',
    statut: 'a-etayer',
  },
  {
    slug: 'amende-100-distributions',
    bloc: 'consequences',
    lettre: 'C',
    refCourrier: 'Réponse du 04/09/2026, p. 95',
    titre: 'C — L’amende de 100 % sur distributions présumées',
    positionService: '',
    reponseCourte: '',
    statut: 'a-etayer',
  },
  {
    slug: 'interets-de-retard',
    bloc: 'consequences',
    lettre: 'D',
    refCourrier: 'Réponse du 04/09/2026, p. 95',
    titre: 'D — Les intérêts de retard',
    positionService: '',
    reponseCourte: '',
    statut: 'a-etayer',
  },
]

// --- Contenu rédigé : src/data/reponse1/<slug>.json --------------------------
interface PageDoc {
  meta?: Record<string, unknown>
  /** En-tête de page : peut surcharger le manifeste ci-dessus. */
  entete?: {
    positionService?: string
    reponseCourte?: string
    enjeu?: string
    statut?: Statut
  }
  sections?: Section[]
}

const modules = import.meta.glob('./reponse1/*.json', { eager: true }) as Record<
  string,
  { default: PageDoc }
>

const docs: Record<string, PageDoc> = {}
for (const [chemin, mod] of Object.entries(modules)) {
  const slug = chemin.replace('./reponse1/', '').replace('.json', '')
  docs[slug] = mod.default
}

export const sectionsDuPoint = (slug: string): Section[] => docs[slug]?.sections ?? []

/** Point enrichi par l'en-tête de son JSON (positionService, verdict, statut…). */
const enrichi = (p: Point): Point => {
  const e = docs[p.slug]?.entete
  return e ? { ...p, ...e } : p
}

/** Point enrichi de l'en-tête éventuellement surchargé par son JSON. */
export const pointParSlug = (slug: string): Point | undefined => {
  const p = points.find((x) => x.slug === slug)
  return p ? enrichi(p) : undefined
}

export const pointsParBloc = (bloc: BlocId): Point[] =>
  points.filter((p) => p.bloc === bloc).map(enrichi)

/** Sous-pages rattachées à une page principale. */
export const sousPages = (slug: string): Point[] => points.filter((p) => p.parent === slug)

/** Numéro de sommaire (« 2.3 », « 3.1.4 »…), calculé comme dans le Rendu final. */
export const numeroDuPoint = (slug: string): string => {
  const p = points.find((x) => x.slug === slug)
  if (!p) return ''
  if (p.numero) return p.numero
  const bloc = blocs.find((b) => b.id === p.bloc)
  if (!bloc) return ''
  let n = 0
  for (const x of pointsParBloc(p.bloc)) {
    if (x.numero) continue
    n += 1
    if (x.slug === slug) return `${bloc.numero}.${n}`
  }
  return ''
}

/** Page précédente / suivante dans l'ordre du courrier (navigation de bas de page). */
export const voisins = (slug: string): { prec?: Point; suiv?: Point } => {
  const i = points.findIndex((p) => p.slug === slug)
  if (i < 0) return {}
  return { prec: points[i - 1], suiv: points[i + 1] }
}
