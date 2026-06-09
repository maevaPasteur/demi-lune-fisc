// =============================================================================
// FACTURES FOURNISSEUR - typage + chargeur
// Source : factures-fournisseur.json (généré par scripts/factures-to-json.cjs
// depuis public/documents/vins-boissons/fournisseur). Niveau « ligne de facture ».
// Pour l'analyse par produit, voir ./achats.ts.
// =============================================================================
import raw from './factures-fournisseur.json'

/** Une ligne-article d'une facture (montants signés : avoirs en négatif). */
export interface LigneFacture {
  code: string
  accise: boolean // produit soumis à accises (marqueur « * »)
  designation: string
  conditionnement: string
  colis: number | null
  quantite: number | null // unités (colonne COLS)
  puBrut: number | null
  remise: number | null
  puNet: number | null
  montantHT: number | null
  tva: string | null // code TVA : "1" = 20 %, "2" = 5,5 %
}

export interface TvaDetail {
  tva: string
  taux: number | null
  ht: number | null
  tva_montant: number | null
}

export interface TotauxFacture {
  totalHT: number | null
  totalTVA: number | null
  totalTTC: number | null
  totalFacture: number | null
  ancienSolde: number | null
  tvaDetail: TvaDetail[]
}

export interface Facture {
  fichier: string
  annee: number
  type?: 'facture' | 'avoir'
  numero: string | null
  dateFacture: string | null
  dateCommande: string | null
  dateLivraison: string | null
  nClient: string | null
  nCommande: string | null
  nBonLivraison: string | null
  lignes: LigneFacture[]
  totaux: TotauxFacture
}

export interface FacturesData {
  fournisseur: string
  source: string
  nbFactures: number
  factures: Facture[]
}

export const facturesData = raw as unknown as FacturesData
export const factures: Facture[] = facturesData.factures

/** Exercices présents dans le jeu de données (années des factures). */
export const exercices: number[] = [...new Set(factures.map((f) => f.annee))].sort()
