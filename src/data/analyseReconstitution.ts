// =============================================================================
// RECONSTITUTION INTÉGRALE DU CA - calculée par script (source unique).
// CINQ exports CERTIFIÉS et INDÉPENDANTS de la caisse comparés au CA déclaré :
//   B = somme des lignes prix×quantité ; C = tickets dédupliqués par identifiant ;
//   H = en-têtes de tickets ; G = delta du cumul du journal de TVA ; A = CA déclaré.
// remises (par exercice) = somme des lignes facturées SOUS le tarif (annexes B).
// ecartFisc = "écart inexpliqué" revendiqué par l'administration au motif 2
//   (proposition de rectification p.15-16) - INPUT DOCUMENTÉ, non calculé.
// Pieds de page exclus. Montants TTC. NE PAS éditer à la main.
// =============================================================================

export interface ReconExercice {
  exercice: string
  caDeclare: number
  reconstitutionB: number
  reconstitutionC: number
  reconstitutionH: number
  reconstitutionG: number
  /** Remises calculées depuis l'annexe B (lignes sous le tarif). */
  remises: number
  /** Écart "inexpliqué" revendiqué par le fisc (motif 2, proposition). */
  ecartFisc: number
}

export interface ReconCumul {
  caDeclare: number
  reconstitutionB: number; ecartB: number; ecartBPct: number
  reconstitutionC: number; ecartC: number; ecartCPct: number
  reconstitutionH: number; ecartH: number; ecartHPct: number
  reconstitutionG: number; ecartG: number; ecartGPct: number
}

export interface AnalyseReconstitution {
  parExercice: ReconExercice[]
  cumul: ReconCumul
  sourcesCount: number
  lignesTotal: number
  ticketsTotal: number
  surfacturationCount: number
  remisesCount: number
  remisesSomme: number
  pctExact: number
  /** Total des écarts "inexpliqués" revendiqués par le fisc (motif 2). */
  ecartFiscTotal: number
}

export const reconstitution: AnalyseReconstitution = {
  "parExercice": [
    {
      "exercice": "2022-2023",
      "caDeclare": 409020.76,
      "reconstitutionB": 403370.42,
      "reconstitutionC": 403370.42,
      "reconstitutionH": 403370.42,
      "reconstitutionG": 403324.72,
      "remises": 17561.64,
      "ecartFisc": 17561.0
    },
    {
      "exercice": "2023-2024",
      "caDeclare": 429204.51,
      "reconstitutionB": 437992.92,
      "reconstitutionC": 438281.12,
      "reconstitutionH": 438281.12,
      "reconstitutionG": 437881.12,
      "remises": 20011.4,
      "ecartFisc": 20011.12
    },
    {
      "exercice": "2024-2025",
      "caDeclare": 437753.6,
      "reconstitutionB": 434827.86,
      "reconstitutionC": 435564.96,
      "reconstitutionH": 435564.96,
      "reconstitutionG": 434709.26,
      "remises": 20115.5,
      "ecartFisc": 20115.28
    }
  ],
  "cumul": {
    "caDeclare": 1275978.87,
    "reconstitutionB": 1276191.2,
    "ecartB": 212.33,
    "ecartBPct": 0.017,
    "reconstitutionC": 1277216.5,
    "ecartC": 1237.63,
    "ecartCPct": 0.097,
    "reconstitutionH": 1277216.5,
    "ecartH": 1237.63,
    "ecartHPct": 0.097,
    "reconstitutionG": 1275915.1,
    "ecartG": -63.77,
    "ecartGPct": -0.005
  },
  "sourcesCount": 5,
  "lignesTotal": 97694,
  "ticketsTotal": 19903,
  "surfacturationCount": 0,
  "remisesCount": 7148,
  "remisesSomme": 57688.54,
  "pctExact": 92.7,
  "ecartFiscTotal": 57687.4
}
