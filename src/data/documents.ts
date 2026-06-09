// =============================================================================
// CATALOGUE DES PIÈCES DU DOSSIER (public/documents)
// La liste est générée à partir des métadonnées d'annexes × périodes, afin de
// rester la source unique : pour ajouter une période ou une annexe, on touche
// uniquement les tableaux ci-dessous.
// =============================================================================

export interface Document {
  id: string // ex. "A1"
  annexe: string // "A" … "H" ou "SOURCE"
  numero: number // 1, 2, 3 (0 pour la source)
  titre: string
  description: string
  niveau: string
  periode: string // "2022-2023"
  fichier: string // chemin relatif sous public/documents (sous-dossier autorisé)
  format: 'ODS' | 'XLS' | 'PDF'
}

interface MetaAnnexe {
  lettre: string
  slug: string
  ext: 'ods' | 'xls'
  titre: string
  description: string
  niveau: string
}

const periodes = [
  { numero: 1, exercice: '2022-2023' },
  { numero: 2, exercice: '2023-2024' },
  { numero: 3, exercice: '2024-2025' },
]

const annexes: MetaAnnexe[] = [
  {
    lettre: 'A',
    slug: 'synthese-CA',
    ext: 'xls',
    titre: 'Synthèse du chiffre d’affaires',
    description:
      'Synthèse globale du CA par exercice : nombre de tickets, remboursements, ' +
      'annulations, lignes supprimées, et ventilation TVA (20 % / 10 % → HT, TVA, TTC).',
    niveau: 'Résumé · 1 page/an',
  },
  {
    lettre: 'B',
    slug: 'prix-vente-quantite',
    ext: 'xls',
    titre: 'Prix de vente × quantité',
    description:
      'Chaque ligne vendue (date, caisse, ticket, réf, produit, quantité, prix TTC, ' +
      'total) avec une colonne de contrôle d’écart.',
    niveau: 'Très détaillé · ~31 000-33 000 lignes/an',
  },
  {
    lettre: 'C',
    slug: 'detail-tickets',
    ext: 'xls',
    titre: 'Détail des tickets',
    description:
      'Détail des tickets (24 colonnes) : date, heure, n° ticket, total TTC / TVA / ' +
      'remise, produit, quantité.',
    niveau: 'Très détaillé · ~32 000-33 000 lignes/an',
  },
  {
    lettre: 'D',
    slug: 'synthese-produit',
    ext: 'xls',
    titre: 'Synthèse par produit',
    description:
      'Synthèse par produit, regroupée par taux de TVA : réf, libellé, prix moyen, ' +
      'quantité totale, total remisé.',
    niveau: 'Résumé produit · ~600-730 lignes/an',
  },
  {
    lettre: 'E',
    slug: 'tpvevenement',
    ext: 'xls',
    titre: 'Journal des événements de caisse',
    description:
      'Journal des événements de caisse (tpvevenement) : connexions, suppressions de ' +
      'lignes, reprises… avec montant et caissier.',
    niveau: 'Détaillé · ~7 000-9 000 lignes/an',
  },
  {
    lettre: 'F',
    slug: 'reglements',
    ext: 'xls',
    titre: 'Règlements par ticket',
    description:
      'Règlements : mode de paiement par ticket (CB, espèces…) avec montant.',
    niveau: 'Détaillé · ~6 400-6 500 lignes/an',
  },
  {
    lettre: 'G',
    slug: 'journal-tva',
    ext: 'xls',
    titre: 'Journal de TVA (3924-A)',
    description:
      'Journal de TVA (réf « 3924-A ») : chaque ticket avec TVA, cumul progressif et ' +
      'report « À nouveau ».',
    niveau: 'Détaillé · ~9 500-10 000 lignes/an',
  },
  {
    lettre: 'H',
    slug: 'liste-tickets',
    ext: 'xls',
    titre: 'Liste des tickets',
    description:
      'Liste des tickets (en-têtes) : date, heure, n° ticket, caissier, totaux ' +
      'TTC / TVA cumulés.',
    niveau: 'Détaillé · ~6 400-6 900 lignes/an',
  },
]

// Sous-dossier dédié aux exports de la caisse enregistreuse (annexes A-H + source brute).
const dossierCaisse = 'caisse-enregistreuse'

/** Toutes les annexes, déclinées par période (A1…H3). */
export const documents: Document[] = annexes.flatMap((a) =>
  periodes.map((p) => ({
    id: `${a.lettre}${p.numero}`,
    annexe: a.lettre,
    numero: p.numero,
    titre: a.titre,
    description: a.description,
    niveau: a.niveau,
    periode: p.exercice,
    fichier: `${dossierCaisse}/ANNEXE-${a.lettre}${p.numero}_${a.slug}_${p.exercice}.${a.ext}`,
    format: a.ext.toUpperCase() as 'ODS' | 'XLS',
  })),
)

/** Export brut source d'où sont tirées les annexes. */
export const source: Document = {
  id: 'SOURCE',
  annexe: 'SOURCE',
  numero: 0,
  titre: 'Export brut des règlements (source)',
  description:
    'Export brut source des règlements / paiements sur toute la période ' +
    '(19 335 lignes) - la matière première d’où sortent les annexes.',
  niveau: 'Données brutes',
  periode: '2022-2025',
  fichier: `${dossierCaisse}/SOURCE-reglement-brut_2022-2025.xls`,
  format: 'XLS',
}

/**
 * Carnet manuscrit de la mère de la gérante : relevé des anomalies du
 * fournisseur de boissons (facturé non livré, manques, avoirs, reprises),
 * transcrit dans un tableur. Pièce clé : prouve que le « facturé » ne reflète
 * pas le « livré » - donc que le « disponible » du fisc est surévalué.
 */
export const carnetManuscrit: Document = {
  id: 'MANU',
  annexe: 'MANUSCRIT',
  numero: 0,
  titre: 'Carnet manuscrit - anomalies fournisseur boissons',
  description:
    'Relevé manuscrit tenu à la livraison (facturé non livré, manques, ' +
    'avoirs, reprises), transcrit en tableur : 218 lignes couvrant avril 2022 ' +
    '→ mars 2025, à partir de 30 photos. À croiser avec les factures FCBS.',
  niveau: 'Transcription · 218 lignes',
  periode: '2022-2025',
  fichier: 'vins-boissons/analyse-manuscrite/analyse-manuscrite-boissons.xls',
  format: 'XLS',
}

/**
 * Rapports / réponses au format PDF, rangés dans un sous-dossier dédié de
 * public/documents. Le champ `fichier` contient donc un chemin relatif.
 */
const dossierRapports = 'rapports-des-finances-publiques'

export const rapports: Document[] = [
  {
    id: 'R1',
    annexe: 'RAPPORT',
    numero: 1,
    titre: 'Proposition 1 - Lettre',
    description:
      'Lettre de réponse à la proposition de rectification.',
    niveau: 'Document PDF',
    periode: '2022-2025',
    fichier: `${dossierRapports}/Proposition_1_Lettre.pdf`,
    format: 'PDF',
  },
  {
    id: 'R2',
    annexe: 'RAPPORT',
    numero: 2,
    titre: 'Proposition 2 - Annexes A à H',
    description: 'Annexes A à H accompagnant la réponse.',
    niveau: 'Document PDF',
    periode: '2022-2025',
    fichier: `${dossierRapports}/Proposition_2_Annexes_A-H.pdf`,
    format: 'PDF',
  },
  {
    id: 'R3',
    annexe: 'RAPPORT',
    numero: 3,
    titre: 'Proposition 3 - Annexes Boissons',
    description:
      'Annexes relatives à la reconstitution par les achats de boissons.',
    niveau: 'Document PDF',
    periode: '2022-2025',
    fichier: `${dossierRapports}/Proposition_3_Annexes_Boissons.pdf`,
    format: 'PDF',
  },
  {
    id: 'R4',
    annexe: 'RAPPORT',
    numero: 4,
    titre: 'Proposition 4 - Annexes finales',
    description: 'Annexes finales de la réponse.',
    niveau: 'Document PDF',
    periode: '2022-2025',
    fichier: `${dossierRapports}/Proposition_4_Annexes_Finales.pdf`,
    format: 'PDF',
  },
]

/**
 * Pièces de défense - analyses chiffrées produites pour l'avocat et le fisc.
 * Classeurs XLSX data-lourds, chaque chiffre sourcé et reproductible (scripts
 * src/data/incertitudeDisparu, à partir des annexes certifiées A/B/E/H).
 */
const dossierPieces = 'pieces-defense'
export const piecesDefense: Document[] = [
  {
    id: 'D1',
    annexe: 'DEFENSE',
    numero: 1,
    titre: 'Défense - Suppressions de caisse (DEL)',
    description:
      'Démonstration chiffrée que les 430 763 € de lignes supprimées ne sont pas du CA dissimulé : ' +
      'erreurs de quantité, sessions où les suppressions dépassent le CA du jour, distribution des prix, ' +
      'triangulation de 3 exports certifiés, double verrou paiement/approvisionnement. 6 onglets.',
    niveau: 'Analyse chiffrée · 6 onglets',
    periode: '2022-2025',
    fichier: `${dossierPieces}/Defense-Suppressions-de-caisse-DEL.xlsx`,
    format: 'XLS',
  },
  {
    id: 'D2',
    annexe: 'DEFENSE',
    numero: 2,
    titre: 'Défense - Boissons prétendument disparues',
    description:
      'Recalcul indépendant du « disparu » boissons (modèle d’incertitude Monte Carlo) : ~76 k€ au prix de ' +
      'revente = perte normale d’un bar (15-25 %), causes de consommation documentées, et réconciliation avec ' +
      'les suppressions de caisse. 4 onglets.',
    niveau: 'Analyse chiffrée · 4 onglets',
    periode: '2022-2025',
    fichier: `${dossierPieces}/Defense-Boissons-disparues.xlsx`,
    format: 'XLS',
  },
  {
    id: 'D3',
    annexe: 'DEFENSE',
    numero: 3,
    titre: 'Consommation personnel & offerts + perte réelle',
    description:
      'Détail chiffré de la consommation du personnel et de l’owner (litres, coût d’achat, CA équivalent), ' +
      'des offerts aux clients, et la cascade complète « où va l’alcool acheté » jusqu’à la perte réelle ' +
      'résiduelle (23 % = perte normale d’un bar). 4 onglets.',
    niveau: 'Analyse chiffrée · 4 onglets',
    periode: '2022-2025',
    fichier: `${dossierPieces}/Consommation-personnel-et-offerts.xlsx`,
    format: 'XLS',
  },
  {
    id: 'D4',
    annexe: 'DEFENSE',
    numero: 4,
    titre: 'Boissons - détail complet (toutes les tables)',
    description:
      'Toutes les données exactes de la page « boissons disparues » : manquant boisson par boisson (coût + CA), ' +
      'cocktails, alcool de chaque plat, composition des menus par période avec probabilités, consommation du ' +
      'personnel, et consommation totale par exercice. 6 onglets.',
    niveau: 'Analyse chiffrée · 6 onglets',
    periode: '2022-2025',
    fichier: `${dossierPieces}/Boissons-detail-complet.xlsx`,
    format: 'XLS',
  },
]

/**
 * Slug d'URL stable dérivé d'un titre (sans accents ni caractères spéciaux).
 * Ex. « Synthèse du chiffre d’affaires » -> "synthese-du-chiffre-d-affaires".
 */
export function slugify(s: string): string {
  return s
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

/** Métadonnées d'annexe, regroupées pour l'affichage par bloc. */
export interface GroupeAnnexe {
  lettre: string
  slug: string
  titre: string
  description: string
  niveau: string
  documents: Document[]
}

export const groupes: GroupeAnnexe[] = annexes.map((a) => ({
  lettre: a.lettre,
  slug: slugify(a.titre),
  titre: a.titre,
  description: a.description,
  niveau: a.niveau,
  documents: documents.filter((d) => d.annexe === a.lettre),
}))

/** Retrouve une annexe par son slug d'URL (page détail). */
export const groupeParSlug = (slug: string): GroupeAnnexe | undefined =>
  groupes.find((g) => g.slug === slug)

/** Slugs d'URL des sections hors annexes (page détail dédiée). */
export const RAPPORTS_SLUG = 'rapport-des-finances-publiques'
export const SOURCE_SLUG = slugify(source.titre)
export const CARTES_SLUG = 'carte-des-vins'
export const FACTURES_SLUG = 'factures-fournisseur'
export const MANUSCRIT_SLUG = 'carnet-manuscrit-boissons'
export const INVENTAIRES_SLUG = 'inventaires'
export const PIECES_DEFENSE_SLUG = 'pieces-defense'

/** Titre d'une pièce à partir de son slug (annexe, rapport, source, carte, factures, inventaires). */
export function titreParSlug(slug: string): string | undefined {
  if (slug === RAPPORTS_SLUG) return 'Rapport des Finances Publiques'
  if (slug === SOURCE_SLUG) return source.titre
  if (slug === CARTES_SLUG) return 'Carte des vins'
  if (slug === FACTURES_SLUG) return 'Factures fournisseur'
  if (slug === MANUSCRIT_SLUG) return carnetManuscrit.titre
  if (slug === INVENTAIRES_SLUG) return 'Inventaires'
  return groupeParSlug(slug)?.titre
}
