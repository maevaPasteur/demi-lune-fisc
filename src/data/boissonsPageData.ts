// =============================================================================
// DONNÉES EXACTES de la page /analyses/boissons-disparues
// Source unique : boissonsPageData.json (généré par
// src/data/incertitudeDisparu/15_donnees_page_boissons.py, reproductible).
// =============================================================================
import raw from './boissonsPageData.json'

export interface DisparuBoisson {
  nom: string
  categorie: string
  achat_l: number
  conso_l: number
  stock_l: number
  disparu_l: number
  prix_achat: number | null
  prix_revente: number | null
  cout_disparu: number
  ca_disparu: number
}

export interface Cocktail {
  cocktail: string
  volume_cl: number
  recette: { nom: string; cl: number; alcool: boolean }[]
  qte_3ans: number
  alcool_l_3ans: number
}

export interface PlatCuisine {
  plat: string
  type: string
  alcool: string
  dose_cl: number
}

export interface MenuLigne {
  menu: string
  service: string
  option: string
  obligatoire: boolean
  alcool: string
  dose_cl: number
  proba_pct: number
  cl_moyen: number
}

export interface ContoPeriode {
  caisse_l: number
  cuisine_l: number
  menu_l: number
  personnel_l: number
  total_l: number
  cout: number
  ca: number
}

export interface LigneConsoP {
  poste: string
  litres: number | null
  coutAchat?: number
  caEquivalent?: number
  cout_achat_eur?: number
  ca_equivalent_eur?: number
  base: string
}

export interface BoissonsPageData {
  disparuParBoisson: DisparuBoisson[]
  cocktails: Cocktail[]
  cuisine: PlatCuisine[]
  cuisineParAlcool: { alcool: string; litres_3ans: number; cout: number }[]
  menusParPeriode: Record<string, { dates: string; lignes: MenuLigne[] }>
  menuAlcoolParPeriode: Record<string, { alcool: string; litres: number }[]>
  personnel: {
    lignes: { poste: string; litres: number | null; cout_achat_eur: number; ca_equivalent_eur: number; base: string }[]
    total_litres: number
    total_cout_eur: number
    total_ca_eur: number
  }
  offerts: {
    avertissement: string
    lignes: { poste: string; litres: number | null; cout_achat_eur: number; ca_equivalent_eur: number; base: string }[]
    total_cout_eur: number
    total_ca_eur: number
  }
  consoParPeriode: Record<string, ContoPeriode>
  synthese: {
    achat_alcool_l: number
    achat_alcool_cout: number
    conso_totale_l: number
    disparu_brut_l: number
    disparu_net_l: number
    disparu_brut_cout: number
    disparu_brut_ca: number
    perte_reelle_l: number
    perte_reelle_pct: number
    perte_exploitation_l?: number
    perte_exploitation_pct?: number
    cascade: { poste: string; litres: number }[]
    fisc_ca_reconstitue: number
    fisc_coef: number
    ca_declare: number
  }
}

export const boissonsPageData = raw as unknown as BoissonsPageData
