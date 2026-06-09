// =============================================================================
// ACHATS PAR PRODUIT - typage + chargeur
// Source : achats-par-produit.json (généré par scripts/achats-par-produit.cjs).
// Niveau « produit (code) × exercice » : c'est l'unité de comparaison future
// avec l'inventaire et les ventes caisse (voir ./correspondances-produits à venir).
// =============================================================================
import raw from './achats-par-produit.json'

/** Catégories déduites du libellé (heuristique, ajustable dans le script). */
export type Categorie =
  | 'vin'
  | 'macvin'
  | 'cremant_petillant'
  | 'biere'
  | 'spiritueux_digestif'
  | 'soft'
  | 'jus'
  | 'eau'
  | 'sirop'
  | 'cafe_the'
  | 'alimentaire'
  | 'materiel'
  | 'autre'

/** Agrégat d'achats pour un exercice (ou total). */
export interface AchatAgrege {
  quantite: number // unités (net des avoirs)
  volumeL: number | null // contenance × quantité (null si contenance inconnue)
  montantHT: number
  nbLignes: number
  puMoyen?: number | null
}

export interface Produit {
  code: string
  libelle: string
  categorie: Categorie
  contenanceCl: number | null
  accise: boolean
  parAnnee: Record<string, AchatAgrege>
  total: AchatAgrege
}

export interface CategorieAgrege {
  nbProduits: number
  parAnnee: Record<string, { quantite: number; volumeL: number; montantHT: number }>
  total: { quantite: number; volumeL: number; montantHT: number }
}

export interface AchatsData {
  source: string
  fournisseur: string
  annees: number[]
  nbProduits: number
  parCategorie: Record<string, CategorieAgrege>
  produits: Produit[]
}

export const achatsData = raw as unknown as AchatsData
export const produits: Produit[] = achatsData.produits
export const annees: number[] = achatsData.annees
export const parCategorie = achatsData.parCategorie

/** Catégories considérées comme des boissons (exclut alimentaire/matériel/autre). */
export const CATEGORIES_BOISSON: Categorie[] = [
  'vin',
  'macvin',
  'cremant_petillant',
  'biere',
  'spiritueux_digestif',
  'soft',
  'jus',
  'eau',
  'sirop',
]

/** Produits « boissons » uniquement (pour l'analyse achats vs ventes/inventaire). */
export const boissons: Produit[] = produits.filter((p) =>
  CATEGORIES_BOISSON.includes(p.categorie),
)

/** Recherche d'un produit par son code fournisseur. */
export const produitParCode = (code: string): Produit | undefined =>
  produits.find((p) => p.code === code)
