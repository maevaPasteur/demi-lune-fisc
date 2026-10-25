// =============================================================================
// RÉPONSE 2 - Contre-analyse des propositions de rectification PERSONNELLES
//             du 19 octobre 2026 (M. Thierry PASTEUR et Mme Ghislaine BEHEM).
// -----------------------------------------------------------------------------
// Sources : deux propositions de rectification (modèle 2120-SD) datées du
//   19/10/2026, signées Pierre DROUARD (DDFiP du Jura), notifiées à chaque
//   co-gérant à titre personnel. Elles reprennent mot pour mot le rejet de
//   comptabilité et la méthode de reconstitution de la proposition « société »
//   du 18/05/2026, puis imposent les recettes réputées dissimulées en revenus
//   de capitaux mobiliers (RCM) entre les mains des deux associés.
//
// PARTI PRIS DE CET ONGLET : centré sur le NOUVEAU. Les griefs de rejet et la
// reconstitution, identiques à ceux déjà réfutés pièce par pièce dans la
// « Réponse 1 », sont rappelés en synthèse (argument décisif + renvoi). Le cœur
// de la Réponse 2 est la taxation personnelle : distributions, désignation
// 117, majoration d'assiette de 25 %, majoration 40 %, chiffrage par associé.
//
// Le contenu rédigé de chaque page vit dans src/data/reponse2/<slug>.json
// (format { meta, entete, sections } identique à la Réponse 1) et est chargé
// ici par import.meta.glob : ajouter un JSON suffit, aucun import à écrire.
// =============================================================================

import type { Section } from './analyses'

// --- Blocs (parties de la Réponse 2) -----------------------------------------
export type BlocId = 'offensive' | 'rejet' | 'reconstitution' | 'taxation'

export interface Bloc {
  id: BlocId
  numero: number
  titre: string
  sousTitre: string
}

export const blocs: Bloc[] = [
  {
    id: 'offensive',
    numero: 1,
    titre: 'La nouvelle offensive du 19 octobre 2026',
    sousTitre:
      'Deux propositions de rectification personnelles notifiées à M. PASTEUR et à Mme BEHEM. Ce qu’elles contiennent, ce qu’elles ne contiennent pas, et pourquoi tout y est dérivé de la reconstitution « société ».',
  },
  {
    id: 'rejet',
    numero: 2,
    titre: 'Le rejet de comptabilité, repris à l’identique',
    sousTitre:
      'Les treize griefs de rejet sont recopiés de la proposition du 18/05/2026, dans le même ordre. Chacun est réfuté, pièce à l’appui, dans la Réponse 1 : rappel de l’argument décisif et renvoi.',
  },
  {
    id: 'reconstitution',
    numero: 3,
    titre: 'La reconstitution, reprise à l’identique',
    sousTitre:
      'La méthode (volumes ÷ doses figées, puis cuisine = liquides × coefficient) est inchangée. Son vice central — la circularité du coefficient — est rappelé ici et détaillé en Réponse 1.',
  },
  {
    id: 'taxation',
    numero: 4,
    titre: 'La taxation personnelle de Thierry et Ghislaine',
    sousTitre:
      'Le cœur du nouveau : distributions réputées (art. 109 CGI), désignation des bénéficiaires (art. 117), majoration d’assiette de 25 % (art. 158-7-2°), majoration de 40 % (art. 1729), intérêts, et chiffrage par associé — chaque euro vérifié et recalculé.',
  },
]

export type Statut = 'demonte' | 'partiel' | 'a-etayer'

export interface Point {
  slug: string
  bloc: BlocId
  /** Numérotation forcée dans le sommaire (ex. « 4.1 »). */
  numero?: string
  /** Slug de la page parente, pour les sous-pages. */
  parent?: string
  /** Référence dans les propositions personnelles du 19/10/2026. */
  refCourrier: string
  titre: string
  /** Résumé de la position que le service soutient sur ce point. */
  positionService: string
  /** Notre verdict en une phrase. */
  reponseCourte: string
  enjeu?: string
  statut: Statut
}

// --- Les pages, dans l'ordre exact des propositions du 19/10/2026 ------------
export const points: Point[] = [
  // ---------------------------------------------------------------- BLOC 1 --
  {
    slug: 'cadre-19-octobre',
    bloc: 'offensive',
    refCourrier: 'Propositions personnelles du 19/10/2026 (PASTEUR & BEHEM)',
    titre: 'Deux propositions personnelles, aucun fait nouveau',
    positionService:
      'Le 19 octobre 2026, le service notifie à M. Thierry PASTEUR et à Mme Ghislaine BEHEM deux propositions de rectification personnelles. Elles reprennent le rejet de comptabilité et la méthode de reconstitution de la proposition « société » du 18/05/2026, puis imposent entre leurs mains, en revenus de capitaux mobiliers, les recettes réputées dissimulées.',
    reponseCourte:
      'Ces deux courriers n’apportent aucun fait nouveau : ils recopient une reconstitution déjà réfutée pièce par pièce (Réponse 1) et n’examinent ni nos observations du 8 juillet ni la propre réponse du service du 4 septembre. Toute la taxation personnelle est dérivée : elle tombe avec la reconstitution.',
    enjeu: 'Impôts personnels ≈ 369 648 € (PASTEUR 196 945 € + BEHEM 172 703 €)',
    statut: 'partiel',
  },
  // ---------------------------------------------------------------- BLOC 2 --
  {
    slug: 'rejet-synthese',
    bloc: 'rejet',
    refCourrier: 'Propositions du 19/10/2026, partie « REJET DE LA COMPTABILITE »',
    titre: 'Les treize griefs de rejet, recopiés et déjà réfutés',
    positionService:
      'Les propositions reproduisent, dans le même ordre, les griefs de rejet du 18/05/2026 : inventaire, suppressions « DEL », quantités inférieures à 1, articles à 0 €, erreurs de TVA, fichiers Événement et Règlement, nombre d’articles, chiffres d’affaires, consommation vendue supérieure aux achats, instabilité des prix des menus et coefficient de revente.',
    reponseCourte:
      'Chaque grief est réfuté, pièce à l’appui, dans la Réponse 1. Ci-dessous, dans l’ordre exact du courrier, l’argument décisif et le renvoi vers la contre-analyse complète.',
    statut: 'demonte',
  },
  // ---------------------------------------------------------------- BLOC 3 --
  {
    slug: 'reconstitution-synthese',
    bloc: 'reconstitution',
    refCourrier: 'Propositions du 19/10/2026, partie « METHODE DE RECONSTITUTION »',
    titre: 'La reconstitution et son vice de circularité',
    positionService:
      'La méthode est identique : les volumes de boissons disponibles sont divisés par des doses figées pour obtenir un CA « liquides » reconstitué, puis le CA « cuisine » est obtenu en multipliant ce CA liquides par un coefficient (2,94 / 3,02 / 3,10).',
    reponseCourte:
      'Le coefficient est, au centième près, le ratio de la propre caisse du restaurant : le service ne peut pas la juger fausse sur les montants et fiable sur le ratio. Près des trois quarts du redressement sont une « cuisine fantôme » jamais mesurée. Détail en Réponse 1.',
    statut: 'demonte',
  },
  // ---------------------------------------------------------------- BLOC 4 --
  {
    slug: 'distributions-principe',
    bloc: 'taxation',
    numero: '4.1',
    refCourrier: 'Propositions du 19/10/2026, « En matière de distributions »',
    titre: '4.1 — Le principe : des distributions sans existence propre',
    positionService:
      'Sur le fondement de l’article 109-1 du CGI et des « conditions d’exploitation », le service considère les recettes HT réputées dissimulées (172 814 € / 124 010 € / 125 076 €) comme des revenus distribués, répartis par moitié entre les deux co-gérants.',
    reponseCourte:
      'Pas de recette occultée établie, pas de distribution. La somme distribuée est l’exact reflet du chiffre d’affaires reconstitué : elle n’a aucune existence autonome et disparaît avec lui.',
    enjeu: 'Assiette des RCM imposés aux deux foyers',
    statut: 'partiel',
  },
  {
    slug: 'designation-117-maitre-affaire',
    bloc: 'taxation',
    numero: '4.2',
    refCourrier: 'Propositions du 19/10/2026, désignation du 16/06/2026',
    titre: '4.2 — La désignation (art. 117) et le « maître de l’affaire »',
    positionService:
      'Le service se prévaut de la désignation des bénéficiaires faite par courrier du 16 juin 2026 et de la qualité de co-gérants pour présumer l’appréhension des sommes par chacun, à hauteur de 50 %.',
    reponseCourte:
      'La désignation faite dans le délai de l’article 117 est conservatoire et ne vaut pas reconnaissance du redressement. Aucun flux financier n’est tracé, et la présomption du « maître de l’affaire » se concilie mal avec un partage par moitié entre deux dirigeants.',
    statut: 'a-etayer',
  },
  {
    slug: 'majoration-25-pourcent',
    bloc: 'taxation',
    numero: '4.3',
    refCourrier: 'Propositions du 19/10/2026, art. 158-7-2° du CGI',
    titre: '4.3 — La majoration d’assiette de 25 %',
    positionService:
      'Le service majore de 25 % l’assiette des distributions (coefficient 1,25, art. 158-7-2° du CGI) : les bases de 96 617 € / 69 432 € / 69 864 € par foyer sont portées à 120 771 € / 86 790 € / 87 330 €.',
    reponseCourte:
      'Cette majoration suit le sort de la distribution : sans distribution, pas d’assiette à majorer. Son cumul avec la majoration de 40 % de l’article 1729 sur les mêmes sommes est contestable.',
    statut: 'a-etayer',
  },
  {
    slug: 'manquement-delibere-personnel',
    bloc: 'taxation',
    numero: '4.4',
    refCourrier: 'Propositions du 19/10/2026, art. 1729 et 1727 du CGI',
    titre: '4.4 — La majoration de 40 % et les intérêts',
    positionService:
      'Le service applique la majoration de 40 % (art. 1729) aux rappels et des intérêts de retard (art. 1727), en invoquant la qualité de co-gérant et le caractère répétitif des minorations. L’intitulé vise « les exercices clos au 31 mars 2022 et 31 mars 2023 ».',
    reponseCourte:
      'Le manquement délibéré doit être prouvé par l’administration (art. L. 195 A du LPF). La caisse est certifiée NF 525 et la bancarisation atteint 98,7 %. La mention de l’exercice clos au 31 mars 2022, hors période vérifiée, entache la motivation.',
    statut: 'partiel',
  },
  {
    slug: 'pasteur-chiffrage',
    bloc: 'taxation',
    numero: '4.5',
    refCourrier: 'Proposition personnelle PASTEUR du 19/10/2026',
    titre: '4.5 — Le chiffrage de M. Thierry PASTEUR',
    positionService:
      'Supplément d’impôt notifié à M. Pasteur : 83 391 € (2023) + 56 724 € (2024) + 56 830 € (2025) = 196 945 €.',
    reponseCourte:
      'Chiffrage vérifié ligne à ligne : il découle intégralement des distributions majorées de 25 %, imposées au barème, augmentées de la CSG/CRDS, du prélèvement de solidarité et de la majoration de 40 %. Recalcul reproductible en pièce jointe.',
    enjeu: '196 945 €',
    statut: 'partiel',
  },
  {
    slug: 'behem-chiffrage',
    bloc: 'taxation',
    numero: '4.6',
    refCourrier: 'Proposition personnelle BEHEM du 19/10/2026',
    titre: '4.6 — Le chiffrage de Mme Ghislaine BEHEM',
    positionService:
      'Supplément d’impôt notifié à Mme Behem : 73 859 € (2023) + 48 124 € (2024) + 50 720 € (2025) = 172 703 €.',
    reponseCourte:
      'Même mécanique que pour M. Pasteur, vérifiée ligne à ligne. L’écart entre les deux foyers ne tient qu’à leurs autres revenus : la base distribuée est strictement identique (50 / 50). Recalcul en pièce jointe.',
    enjeu: '172 703 €',
    statut: 'partiel',
  },
  {
    slug: 'synthese-et-demande',
    bloc: 'taxation',
    numero: '4.7',
    refCourrier: 'Synthèse Réponse 2',
    titre: '4.7 — Exposition réelle et demandes',
    positionService:
      'Après désignation des bénéficiaires, l’amende de 100 % (art. 1759, 471 826 €) est abandonnée et remplacée par la taxation personnelle des deux associés.',
    reponseCourte:
      'Exposition réelle ≈ 582 796 € : société 213 148 € + associés 369 648 €, le tout entièrement suspendu au sort de la reconstitution. Nous demandons la saisine de la Commission et la décharge des rectifications.',
    enjeu: 'Total en jeu ≈ 582 796 €',
    statut: 'a-etayer',
  },
]

// --- Contenu rédigé : src/data/reponse2/<slug>.json --------------------------
interface PageDoc {
  meta?: Record<string, unknown>
  entete?: {
    positionService?: string
    reponseCourte?: string
    enjeu?: string
    statut?: Statut
  }
  sections?: Section[]
}

const modules = import.meta.glob('./reponse2/*.json', { eager: true }) as Record<
  string,
  { default: PageDoc }
>

const docs: Record<string, PageDoc> = {}
for (const [chemin, mod] of Object.entries(modules)) {
  const slug = chemin.replace('./reponse2/', '').replace('.json', '')
  docs[slug] = mod.default
}

export const sectionsDuPoint = (slug: string): Section[] => docs[slug]?.sections ?? []

const enrichi = (p: Point): Point => {
  const e = docs[p.slug]?.entete
  return e ? { ...p, ...e } : p
}

export const pointParSlug = (slug: string): Point | undefined => {
  const p = points.find((x) => x.slug === slug)
  return p ? enrichi(p) : undefined
}

export const pointsParBloc = (bloc: BlocId): Point[] =>
  points.filter((p) => p.bloc === bloc).map(enrichi)

export const sousPages = (slug: string): Point[] => points.filter((p) => p.parent === slug)

/** Numéro de sommaire (« 2.1 », « 4.3 »…). */
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

/** Page précédente / suivante dans l'ordre du courrier. */
export const voisins = (slug: string): { prec?: Point; suiv?: Point } => {
  const i = points.findIndex((p) => p.slug === slug)
  if (i < 0) return {}
  return { prec: points[i - 1], suiv: points[i + 1] }
}
