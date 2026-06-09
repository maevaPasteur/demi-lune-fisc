// =============================================================================
// INVENTAIRES — typage + chargeur + sélecteurs d'analyse
// Source : public/documents/inventaires/inventaires.json
// (généré par scripts/inventaires-to-json.cjs depuis les CSV).
// Périmètre : boissons sans alcool + alcools/vins (stocks de clôture au 31/03).
// =============================================================================
import raw from '../../public/documents/inventaires/inventaires.json'

export type CategorieInventaire = 'boisson_sans_alcool' | 'alcool'
export type Fiabilite = 'exact' | 'a_verifier'

export interface LigneInventaire {
  produit: string
  categorie: CategorieInventaire
  quantite: number | null
  prixUnitaireHT: number | null
  valeurHT: number | null
  fiabilite: Fiabilite
  page: number | null
  /** true = ligne "résidu d'écart" (valeur connue, produit non identifié). */
  residuel: boolean
}

export interface TotauxInventaire {
  sansAlcoolHT: number
  alcoolHT: number
  totalHT: number
}

export interface Inventaire {
  /** Date de clôture (AAAA-MM-JJ). */
  date: string
  /** Exercice dont c'est le stock de clôture (ex. "2022-2023"). */
  exercice: string
  pdf: string
  csv: string
  nbLignes: number
  totaux: TotauxInventaire
  lignes: LigneInventaire[]
}

export interface InventairesData {
  objet: string
  source: string
  avertissement: string
  unites: string
  inventaires: Inventaire[]
}

export const inventairesData = raw as unknown as InventairesData
export const inventaires: Inventaire[] = inventairesData.inventaires
export const datesInventaire: string[] = inventaires.map((i) => i.date)

/** Inventaire par date de clôture (ex. "2024-03-31"). */
export const inventaireParDate = (date: string): Inventaire | undefined =>
  inventaires.find((i) => i.date === date)

/** Inventaire par exercice de clôture (ex. "2023-2024"). */
export const inventaireParExercice = (exercice: string): Inventaire | undefined =>
  inventaires.find((i) => i.exercice === exercice)

/** Toutes les lignes, aplaties avec la date/exercice (vue cross-inventaire). */
export const lignesParInventaire = inventaires.flatMap((i) =>
  i.lignes.map((l) => ({ ...l, date: i.date, exercice: i.exercice })),
)

/**
 * Quantités d'un produit (recherche par motif sur le libellé) à chaque date.
 * Pratique pour la réconciliation : ex. quantitesParProduit(/macvin/i).
 */
export function quantitesParProduit(motif: RegExp): Record<string, number> {
  const out: Record<string, number> = {}
  for (const inv of inventaires) {
    const q = inv.lignes
      .filter((l) => motif.test(l.produit))
      .reduce((a, l) => a + (l.quantite || 0), 0)
    out[inv.date] = q
  }
  return out
}
