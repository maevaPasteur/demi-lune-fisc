// =============================================================================
// BIBLIOTHÈQUE PDF - cartes des vins + factures fournisseur par année
// Source : pdf-bibliotheque.json (généré par scripts/index-pdf-bibliotheque.cjs).
// =============================================================================
import raw from './pdf-bibliotheque.json'

export interface CartePdf {
  titre: string
  description: string
  fichier: string
  format: 'PDF'
}

export interface PieceAnnee {
  label: string
  type: 'facture' | 'releve' | 'autre'
  fichier: string
}

export interface FacturesAnnee {
  annee: string
  nb: number
  pieces: PieceAnnee[]
}

export interface InventaireAnnee {
  annee: string
  pdf: string | null
  csv: string | null
}

export interface BibliothequePdf {
  source: string
  cartes: CartePdf[]
  facturesParAnnee: FacturesAnnee[]
  inventaires: InventaireAnnee[]
}

export const bibliothequePdf = raw as unknown as BibliothequePdf
export const cartes: CartePdf[] = bibliothequePdf.cartes
export const facturesParAnnee: FacturesAnnee[] = bibliothequePdf.facturesParAnnee
export const inventaires: InventaireAnnee[] = bibliothequePdf.inventaires ?? []
