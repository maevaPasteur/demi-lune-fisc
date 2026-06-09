// =============================================================================
// VOLUMES DISPARUS - données du vérificateur (DDFiP Jura)
// Source : volumes-disparus-fisc.json (transmis par le contrôle fiscal).
// Convention : pct_disparu > 0 = « disparu » (présomption d'occultation) ;
// < 0 = « surconsommation » (vente sans achat → impossible sans erreur caisse).
// =============================================================================
import raw from './volumes-disparus-fisc.json'

export type Fiabilite =
  | 'exact'
  | 'a_verifier_inversion'
  | 'approx'
  | 'disponible_seul'
  | 'non_chiffre'

/** Données d'un produit pour un exercice (champs variables selon la source). */
export interface DonneeExercice {
  disponible?: number | null
  vendu_caisse?: number | string | null
  pct_disparu?: number | null
  fiabilite?: Fiabilite
  type?: string
  anomalie?: string
  // variantes en cl / champs spécifiques
  disponible_cl?: number
  vendu_cl?: number
  reconstitue_cl?: number
  valorise_ca?: boolean
  surconsommation_cl?: number
  pct_des_disponibles?: number
  note?: string
  detail_disponible?: Record<string, number>
}

export interface ProduitDisparu {
  nom: string
  categorie: string
  reference_caisse?: string
  usage_cuisine_deduit_par_verificateur?: boolean
  preuve_parametrage?: boolean
  note?: string
  donnees: Record<string, DonneeExercice>
}

export interface VolumesDisparusData {
  meta: {
    dossier: string
    objet: string
    formule_verificateur: string
    convention_signe: Record<string, string>
    exercices: string[]
    sources: Record<string, string>
    fiabilite_valeurs: Record<string, string>
    unites: string
    avertissements: string[]
    verdict_hypotheses: Record<string, string>
  }
  produits: ProduitDisparu[]
}

export const volumesDisparus = raw as unknown as VolumesDisparusData
export const produitsDisparus: ProduitDisparu[] = volumesDisparus.produits
export const exercicesFisc: string[] = volumesDisparus.meta.exercices

/** Produits que le vérificateur lui-même reconnaît comme artefact de paramétrage. */
export const preuvesParametrage: ProduitDisparu[] = produitsDisparus.filter(
  (p) => p.preuve_parametrage,
)
