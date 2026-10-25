// =============================================================================
// RÉPONSE 2 - Contre-analyse des propositions de rectification PERSONNELLES
//             du 19 octobre 2026 (M. Thierry PASTEUR et Mme Ghislaine BEHEM).
// -----------------------------------------------------------------------------
// Chaque page est AUTO-SUFFISANTE : la position du service y est exposée, puis
// réfutée avec ses pièces et ses calculs, sans renvoi à un autre onglet.
// Le contenu vit dans src/data/reponse2/<slug>.json (chargé par import.meta.glob).
// =============================================================================

import type { Section } from './analyses'

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
      'Deux propositions de rectification personnelles notifiées à M. PASTEUR et à Mme BEHEM, qui recopient les griefs et la reconstitution du 18/05/2026 et imposent les distributions entre leurs mains.',
  },
  {
    id: 'rejet',
    numero: 2,
    titre: 'Le rejet de comptabilité',
    sousTitre:
      'Les griefs de rejet, repris à l’identique, sont réfutés un par un, dans l’ordre du courrier, pièces et calculs à l’appui.',
  },
  {
    id: 'reconstitution',
    numero: 3,
    titre: 'La méthode de reconstitution',
    sousTitre:
      'Le coefficient circulaire, les doses figées et les pertes ignorées : chaque poste est repris et corrigé sur les données réelles de la caisse et des factures.',
  },
  {
    id: 'taxation',
    numero: 4,
    titre: 'La taxation personnelle de Thierry et Ghislaine',
    sousTitre:
      'Distributions (art. 109), désignation (art. 117) et maître de l’affaire, majoration d’assiette de 25 %, majoration de 40 %, chiffrage de chaque associé : le cœur du nouveau, démonté avec la jurisprudence vérifiée.',
  },
]

export type Statut = 'demonte' | 'partiel' | 'a-etayer'

export interface Point {
  slug: string
  bloc: BlocId
  numero?: string
  parent?: string
  refCourrier: string
  titre: string
  positionService: string
  reponseCourte: string
  enjeu?: string
  statut: Statut
}

const C19 = 'Proposition personnelle du 19/10/2026'

export const points: Point[] = [
  // ----------------------------------------------------------- BLOC 1 --
  {
    slug: 'cadre-19-octobre', bloc: 'offensive',
    refCourrier: C19 + ' (PASTEUR & BEHEM)',
    titre: 'Deux propositions personnelles, aucun fait nouveau',
    positionService: '',
    reponseCourte:
      'Ces deux courriers recopient une reconstitution déjà réfutée et n’examinent pas notre défense ; toute la taxation personnelle est dérivée et tombe avec la reconstitution.',
    enjeu: 'Impôts personnels ≈ 369 648 € (PASTEUR 196 945 € + BEHEM 172 703 €)',
    statut: 'partiel',
  },
  // ----------------------------------------------------------- BLOC 2 --
  {
    slug: 'inventaire-de-stocks', bloc: 'rejet',
    refCourrier: C19 + ' — Inventaire de stocks', titre: 'Inventaire de stocks jugé non conforme',
    positionService: '',
    reponseCourte:
      'La contenance n’est exigée par aucun texte (R. 123-177 demande existence et valeur, présentes) ; les inventaires sont datés par les pièces et se vérifient au centime. Aucune gravité établie.',
    statut: 'demonte',
  },
  {
    slug: 'suppressions-de-notes', bloc: 'rejet',
    refCourrier: C19 + ' — Suppressions « DEL »', titre: 'Les suppressions de notes (« DEL »)',
    positionService: '',
    reponseCourte:
      'Aucune recette n’y disparaît : la quasi-totalité des notes « DEL » se raccorde par date, heure, montant et ticket Z ; ce sont des partages, re-saisies et forfaits, non des recettes effacées.',
    enjeu: 'Pilier n° 1 du rejet', statut: 'demonte',
  },
  {
    slug: 'quantites-inferieures-a-un', bloc: 'rejet',
    refCourrier: C19 + ' — Quantités < 1', titre: 'Les quantités inférieures à 1',
    positionService: '',
    reponseCourte:
      'Ce sont des partages d’addition (1/N convives) qui reconstituent au centime le total encaissé ; l’exemple « table 13 » du service a sa moitié sur la note 14.',
    statut: 'demonte',
  },
  {
    slug: 'articles-a-zero-euro', bloc: 'rejet',
    refCourrier: C19 + ' — Articles à 0 €', titre: 'Les articles à prix 0 €',
    positionService: '',
    reponseCourte:
      '272 lignes sur 97 769 (0,28 %), encaissé 0,00 € : une ligne à prix nul ne peut, par construction, sortir aucune recette.',
    statut: 'demonte',
  },
  {
    slug: 'erreurs-de-tva', bloc: 'rejet',
    refCourrier: C19 + ' — TVA', titre: 'Les erreurs de TVA',
    positionService: '',
    reponseCourte:
      'Une seule colonne d’affichage de l’éditeur est erronée ; la TVA réellement encaissée boucle avec le CA à 10,68 € près sur trois ans et colle à la comptabilité.',
    statut: 'demonte',
  },
  {
    slug: 'fichiers-evenement-reglement', bloc: 'rejet',
    refCourrier: C19 + ' — Fichiers E et F', titre: 'Les fichiers Événement et Règlement',
    positionService: '',
    reponseCourte:
      'Même CA à l’euro près d’un export à l’autre ; l’écart ne porte que sur le comptage des parts partagées. L’Excel de travail n’est pas l’archive certifiée.',
    statut: 'demonte',
  },
  {
    slug: 'tables-virtuelles', bloc: 'rejet',
    refCourrier: C19 + ' — Tables virtuelles', titre: 'Les tables « virtuelles »',
    positionService: '',
    reponseCourte:
      'Un numéro de note n’est pas une table ; la suppression de la table d’origine évite le double comptage et protège le CA, elle ne le réduit pas.',
    statut: 'demonte',
  },
  {
    slug: 'consommation-superieure-achats', bloc: 'rejet',
    refCourrier: C19 + ' — Conso > achats', titre: 'La consommation vendue supérieure aux achats',
    positionService: '',
    reponseCourte:
      'Sur 203 pourcentages, le titre n’est vérifié nulle part après regroupement des libellés ; 17 ne sont pas reproductibles ; le Calvados boucle à 73,0 L entrés = 73,0 L sortis. Bilan matière excédentaire.',
    enjeu: 'Le grief le plus factuel', statut: 'demonte',
  },
  {
    slug: 'instabilite-prix-menus', bloc: 'rejet',
    refCourrier: C19 + ' — Prix des menus', titre: 'L’instabilité des prix des menus',
    positionService: '',
    reponseCourte:
      'Le prix catalogue (45 €) est stable ; les prix variables sont des forfaits « sans détail » (factures globales), tous horodatés et portés au CA.',
    statut: 'demonte',
  },
  {
    slug: 'coefficient-de-revente', bloc: 'rejet',
    refCourrier: C19 + ' — Coefficient', titre: 'Le coefficient de revente jugé trop bas',
    positionService: '',
    reponseCourte:
      'Produit par produit la marge est normale (vins ×3,5 ; spiritueux ×7 à ×13) ; sur l’alcool réellement revendu ×3,85. Le « 3,05 » du service est fabriqué par sa reconstitution.',
    statut: 'demonte',
  },
  // ----------------------------------------------------------- BLOC 3 --
  {
    slug: 'reconstitution-cadre', bloc: 'reconstitution',
    refCourrier: C19 + ' — Méthode', titre: 'La méthode de reconstitution',
    positionService: '',
    reponseCourte:
      'Le coefficient est le ratio de la propre caisse du restaurant ; 75 % du redressement est une « cuisine fantôme » jamais mesurée ; effet de levier ×4.',
    statut: 'demonte',
  },
  {
    slug: 'sur-versement', bloc: 'reconstitution',
    refCourrier: C19 + ' — Sur-versement', titre: 'Le sur-versement au verre',
    positionService: '',
    reponseCourte:
      'Sans doseur, le verre servi dépasse la dose figée du service ; aux taux mesurés (bornes basses), c’est de l’alcool bu mais non vendu, pas une recette.',
    statut: 'demonte',
  },
  {
    slug: 'perte-de-biere', bloc: 'reconstitution',
    refCourrier: C19 + ' — Perte de bière', titre: 'La perte de bière (mousse et tirage)',
    positionService: '',
    reponseCourte:
      'La freinte technique du fût (mousse, purge, nettoyage, fond de fût) dépasse les 15 % que le service admet lui-même ; la bière n’est pas vendue à 85 %.',
    statut: 'demonte',
  },
  {
    slug: 'perte-de-cremant', bloc: 'reconstitution',
    refCourrier: C19 + ' — Perte de crémant', titre: 'La perte de crémant',
    positionService: '',
    reponseCourte:
      'Compté jour par jour : le crémant sur-versé et la bouteille éventée jetée chaque soir font un volume qui ne produit aucune vente, pourtant compté comme vendu.',
    statut: 'demonte',
  },
  {
    slug: 'degustation-offerte', bloc: 'reconstitution',
    refCourrier: C19 + ' — Dégustation', titre: 'La dégustation offerte',
    positionService: '',
    reponseCourte:
      'Comptée note par note (2 cl par vin nommé et par note) : du vin offert et jamais vendu, lu dans la caisse, que la reconstitution convertit à tort en verres vendus.',
    statut: 'demonte',
  },
  {
    slug: 'alcool-de-cuisine', bloc: 'reconstitution',
    refCourrier: C19 + ' — Alcool de cuisine', titre: 'L’alcool de cuisine',
    positionService: '',
    reponseCourte:
      'L’alcool incorporé en cuisine (sauces, flambages, babas) part dans les plats, jamais dans un verre vendu ; le service n’en déduit qu’une fraction.',
    statut: 'demonte',
  },
  {
    slug: 'alcool-plats-menus', bloc: 'reconstitution',
    refCourrier: C19 + ' — Alcool des menus', titre: 'L’alcool cuit dans les plats des menus',
    positionService: '',
    reponseCourte:
      'Chiffré plat par plat × probabilité de choix (jamais la dose entière pour une option facultative) : de l’alcool cuit, pas un verre servi.',
    statut: 'demonte',
  },
  {
    slug: 'variation-de-stock', bloc: 'reconstitution',
    refCourrier: C19 + ' — Variation de stock', titre: 'La variation de stock',
    positionService: '',
    reponseCourte:
      'Le « volume disponible » du service est gonflé par une variation de stock qui ne se vérifie pas sur les inventaires datés.',
    statut: 'demonte',
  },
  {
    slug: 'ventes-sans-achat', bloc: 'reconstitution',
    refCourrier: C19 + ' — Ventes sans achat', titre: 'Les « ventes sans achat »',
    positionService: '',
    reponseCourte:
      'Les produits vendus sans achat identifié prouvent un défaut de paramétrage de la caisse, pas une recette occultée : c’est l’inverse d’une dissimulation.',
    statut: 'demonte',
  },
  {
    slug: 'abattements-et-pertes', bloc: 'reconstitution',
    refCourrier: C19 + ' — Abattements', titre: 'Les abattements et pertes forfaitaires',
    positionService: '',
    reponseCourte:
      'Les forfaits de 5 % + 5 % + 5 % sont des planchers : la consommation sans vente itemisée les dépasse largement.',
    statut: 'demonte',
  },
  {
    slug: 'extrapolation-cuisine', bloc: 'reconstitution',
    refCourrier: C19 + ' — Extrapolation', titre: 'L’extrapolation cuisine (coefficient liquide → solide)',
    positionService: '',
    reponseCourte:
      'La cuisine n’est jamais mesurée : CA solides = CA liquides × coefficient. Le coefficient quadruple toute sur-estimation des boissons et fabrique 354 921 € de cuisine fantôme.',
    statut: 'demonte',
  },
  // ----------------------------------------------------------- BLOC 4 --
  {
    slug: 'distributions-principe', bloc: 'taxation', numero: '4.1',
    refCourrier: C19 + ', « En matière de distributions »',
    titre: '4.1 — Le principe : des distributions sans existence propre',
    positionService: '',
    reponseCourte:
      'Pas de recette occultée établie, pas de distribution : la somme distribuée est le décalque du CA reconstitué et disparaît avec lui.',
    enjeu: 'Base des RCM imposés', statut: 'partiel',
  },
  {
    slug: 'designation-117-maitre-affaire', bloc: 'taxation', numero: '4.2',
    refCourrier: C19 + ' ; désignation du 16/06/2026',
    titre: '4.2 — La désignation (art. 117) et le « maître de l’affaire »',
    positionService: '',
    reponseCourte:
      'La désignation régulière (par avocat) écarte le 1759 mais ne vaut pas reconnaissance ; la maîtrise étant partagée entre deux foyers distincts, la présomption tombe et la clé 50/50 n’est pas démontrée (CAA Versailles n° 21VE01600).',
    statut: 'a-etayer',
  },
  {
    slug: 'majoration-25-pourcent', bloc: 'taxation', numero: '4.3',
    refCourrier: C19 + ', art. 158-7-2° du CGI',
    titre: '4.3 — La majoration d’assiette de 25 %',
    positionService: '',
    reponseCourte:
      'Elle tombe avec la distribution ; valide pour l’IR, elle a bien été exclue de l’assiette sociale (vérifié, conforme à la QPC 2017-643/650). Le prélèvement total atteint 73 % à 84 % : effet confiscatoire.',
    statut: 'partiel',
  },
  {
    slug: 'manquement-delibere-personnel', bloc: 'taxation', numero: '4.4',
    refCourrier: C19 + ', art. 1729 et 1727 du CGI',
    titre: '4.4 — La majoration de 40 % et les intérêts',
    positionService: '',
    reponseCourte:
      'Charge de la preuve sur l’administration (L. 195 A) ; motivation dupliquée à l’identique entre les deux foyers ; caisse NF 525 et bancarisation 98,7 % ; exercice 2022 hors période.',
    statut: 'partiel',
  },
  {
    slug: 'pasteur-chiffrage', bloc: 'taxation', numero: '4.5',
    refCourrier: 'Proposition personnelle PASTEUR du 19/10/2026',
    titre: '4.5 — Le chiffrage de M. Thierry PASTEUR',
    positionService: '',
    reponseCourte:
      'Supplément vérifié de 196 945 € sur trois ans, soit un taux effectif de l’ordre de 84 % sur la somme réputée distribuée. Entièrement dérivé de la reconstitution.',
    enjeu: '196 945 €', statut: 'partiel',
  },
  {
    slug: 'behem-chiffrage', bloc: 'taxation', numero: '4.6',
    refCourrier: 'Proposition personnelle BEHEM du 19/10/2026',
    titre: '4.6 — Le chiffrage de Mme Ghislaine BEHEM',
    positionService: '',
    reponseCourte:
      'Supplément vérifié de 172 703 € sur trois ans, soit un taux effectif de l’ordre de 73 %. Base distribuée identique à celle de M. PASTEUR (50/50).',
    enjeu: '172 703 €', statut: 'partiel',
  },
  {
    slug: 'synthese-et-demande', bloc: 'taxation', numero: '4.7',
    refCourrier: 'Synthèse de la Réponse 2',
    titre: '4.7 — Exposition réelle et demandes',
    positionService: '',
    reponseCourte:
      'Exposition réelle ≈ 582 796 € (société 213 148 € + associés 369 648 €), entièrement suspendue au sort de la reconstitution. Demandes : Commission départementale et décharge.',
    enjeu: 'Total en jeu ≈ 582 796 €', statut: 'a-etayer',
  },
]

// --- Chargement du contenu rédigé : src/data/reponse2/<slug>.json ------------
interface PageDoc {
  meta?: Record<string, unknown>
  entete?: { positionService?: string; reponseCourte?: string; enjeu?: string; statut?: Statut }
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

const enrichi = (pt: Point): Point => {
  const e = docs[pt.slug]?.entete
  return e ? { ...pt, ...e } : pt
}

export const pointParSlug = (slug: string): Point | undefined => {
  const pt = points.find((x) => x.slug === slug)
  return pt ? enrichi(pt) : undefined
}

export const pointsParBloc = (bloc: BlocId): Point[] =>
  points.filter((pt) => pt.bloc === bloc).map(enrichi)

export const sousPages = (slug: string): Point[] => points.filter((pt) => pt.parent === slug)

export const numeroDuPoint = (slug: string): string => {
  const pt = points.find((x) => x.slug === slug)
  if (!pt) return ''
  if (pt.numero) return pt.numero
  const bloc = blocs.find((b) => b.id === pt.bloc)
  if (!bloc) return ''
  let n = 0
  for (const x of pointsParBloc(pt.bloc)) {
    if (x.numero) continue
    n += 1
    if (x.slug === slug) return `${bloc.numero}.${n}`
  }
  return ''
}

export const voisins = (slug: string): { prec?: Point; suiv?: Point } => {
  const i = points.findIndex((pt) => pt.slug === slug)
  if (i < 0) return {}
  return { prec: points[i - 1], suiv: points[i + 1] }
}
