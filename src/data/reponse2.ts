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
    titre: 'Deux propositions personnelles, une liquidation nouvelle sur la même reconstitution',
    positionService: '',
    reponseCourte:
      'Les deux courriers recopient à l’identique la reconstitution du 18/05 et y greffent une liquidation personnelle nouvelle (RCM ×1,25, barème, prélèvements sociaux, majorations) ; toute cette taxation est dérivée et tombe avec la reconstitution.',
    enjeu: 'Exposition réelle 582 796 € (société 213 148 € + associés 369 648 €)',
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
      'Le prix catalogue (45 €) est unique ; le prix est libre (art. L. 410-2 c. com.) et aucune recette n’est alléguée manquante. La variabilité est la conversion de tablées au forfait, démontrée au centime sur les annexes du service pour 2022-2023 (16 notes, 1 492,80 €). Le rattachement reste partiel au-delà (45,5 % des ventes hors catalogue ; 2 rafales sur 14 au 09/09/2022) et la traçabilité des suppressions relève du grief A.',
    statut: 'partiel',
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
      'Au titre de la seule freinte, aucun dégrèvement : la perte technique défendable (39 L en 2024-2025) est inférieure au 1er abattement déjà appliqué par le service (95 L du volume disponible). La page démonte le motif du refus (cumul réel 27,75 % et non 30 %, aucun des deux 15 % n’étant une perte pure) et fixe l’assiette (1 213 L) pour le bilan matière.',
    statut: 'partiel',
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
      'Une ligne de vin nommé prouve une vente, non une larme offerte : sur 3 exercices la caisse ne trace que 7 lignes à 0 € (1,85 L), des verres/pichets entiers. Les 97,42 L sont une hypothèse (6 292 ventes × 2 cl, dose jamais mesurée) dont 75,96 L dépendent d’une attestation de salle non produite.',
    statut: 'a-etayer',
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
      'Le service reconnaît que ce grief ne fonde aucun euro, et ses tableaux p. 75 sont faux (12 950 cl de blanc pour 150 enregistrés, exercices 2 et 3 identiques). Restent une bouteille de Bordeaux et 375 cl de blanc que nous assumons comme défauts de caisse, sans CA occulté démontré ; la comparaison achats/ventes n’exclut pas à elle seule des achats hors facture (L. 192 al. 2 LPF).',
    statut: 'partiel',
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
      'La distribution n’a aucune source autonome : elle est le décalque du CA reconstitué (235 913 € par foyer). Si la reconstitution tombe, elle disparaît ; si elle est réduite, la base distribuée baisse d’autant (moyen subsidiaire chiffré).',
    enjeu: 'Base des RCM imposés (235 913 € par foyer)', statut: 'partiel',
  },
  {
    slug: 'designation-117-maitre-affaire', bloc: 'taxation', numero: '4.2',
    refCourrier: C19 + ' ; désignation du 16/06/2026',
    titre: '4.2 — La désignation (art. 117) et le « maître de l’affaire »',
    positionService: '',
    reponseCourte:
      'La désignation régulière (par avocat) écarte l’amende de 1759 (471 826 €) sans valoir reconnaissance. Deux concubins = deux foyers distincts (art. 6) et, au mieux, deux co-maîtres : le service doit prouver la part de chacun (CE n° 388887 ; CAA Versailles n° 21VE01600), non la déduire du capital. Soulevé à titre conservatoire.',
    statut: 'partiel',
  },
  {
    slug: 'majoration-25-pourcent', bloc: 'taxation', numero: '4.3',
    refCourrier: C19 + ', art. 158-7-2° du CGI',
    titre: '4.3 — La majoration d’assiette de 25 %',
    positionService: '',
    reponseCourte:
      'Sur l’IR le coefficient de 1,25 est valide : la réduction viendra de la chute de la distribution. L’exclusion du 1,25 de l’assiette sociale (QPC 2017-643/650) reste à vérifier, pièce non produite. Le caractère confiscatoire (hors sanction : 59 % à 67 %) est subsidiaire et fragile.',
    statut: 'a-etayer',
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
      'Supplément de 196 945 € notifié par le service (non recalculable faute du revenu du foyer), décalque de la reconstitution. Taux effectif global 83,5 % ; hors majoration de 40 %, 67,3 %. Tombe avec la reconstitution.',
    enjeu: '196 945 €', statut: 'a-etayer',
  },
  {
    slug: 'behem-chiffrage', bloc: 'taxation', numero: '4.6',
    refCourrier: 'Proposition personnelle BEHEM du 19/10/2026',
    titre: '4.6 — Le chiffrage de Mme Ghislaine BEHEM',
    positionService: '',
    reponseCourte:
      'Supplément de 172 703 € notifié par le service (2024 illisible sur le PDF scanné), décalque de la reconstitution. Taux effectif global 73,2 % ; hors majoration de 40 %, 58,8 %. Tombe avec la reconstitution.',
    enjeu: '172 703 €', statut: 'a-etayer',
  },
  {
    slug: 'synthese-et-demande', bloc: 'taxation', numero: '4.7',
    refCourrier: 'Synthèse de la Réponse 2',
    titre: '4.7 — Exposition réelle et demandes',
    positionService: '',
    reponseCourte:
      'Exposition réelle 582 796 € (société 213 148 € + associés 369 648 €), et non 684 974 €, entièrement suspendue à la reconstitution. Commission sur les seules questions de fait de la reconstitution ; décharge contentieuse pour les RCM, l’IR et les pénalités.',
    enjeu: 'Total en jeu 582 796 €', statut: 'partiel',
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
