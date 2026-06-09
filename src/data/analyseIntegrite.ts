// =============================================================================
// ANALYSE D'INTÉGRITÉ DE LA CAISSE CERTIFIÉE - données calculées par script
// -----------------------------------------------------------------------------
// CONTINUITÉ : numérotation des tickets-Z (no_zEport) et des événements (id) du
// journal certifié (annexes E1/E2/E3). 0 trou = aucune journée/aucun événement
// effacé (principe NF525).
// BANCARISATION : ventilation des encaissements par mode de paiement (annexes
// A1/A2/A3), qui se réconcilie exactement au CA TTC déclaré.
// Recalculé et vérifié indépendamment. NE PAS éditer à la main.
// =============================================================================

export interface ContinuiteExercice {
  exercice: string
  zMin: number; zMax: number; zCount: number; zAttendu: number; zTrous: number
  idMin: number; idMax: number; idCount: number; idAttendu: number; idTrous: number
  evenements: number
  ticketsIntraZTrous: number
  avoirs: number
}

export interface Continuite {
  parExercice: ContinuiteExercice[]
  zGlobalMin: number; zGlobalMax: number; zTotal: number; zTotalTrous: number
  idGlobalMin: number; idGlobalMax: number; idTotal: number; idTotalTrous: number
  evenementsTotal: number
  ticketsIntraZTrousTotal: number
  avoirsTotal: number
  zChaineInterExercices: boolean
  idChaineInterExercices: boolean
}

export interface ModePaiement { mode: string; montant: number; pct: number }

export interface BancarisationExercice {
  exercice: string
  ca: number
  modes: ModePaiement[]
  especes: number; especesPct: number
  cb: number; cbPct: number
}

export interface Bancarisation {
  parExercice: BancarisationExercice[]
  caTotal: number
  especesTotal: number; especesPct: number
  cbTotal: number; cbPct: number
  modesTotal: ModePaiement[]
  tracablePct: number
}

export interface AnalyseIntegrite {
  continuite: Continuite
  bancarisation: Bancarisation
}

export const integrite: AnalyseIntegrite = {
  "continuite": {
    "parExercice": [
      {
        "exercice": "2022-2023",
        "zMin": 2938,
        "zMax": 3158,
        "zCount": 221,
        "zAttendu": 221,
        "zTrous": 0,
        "idMin": 36681,
        "idMax": 45387,
        "idCount": 8707,
        "idAttendu": 8707,
        "idTrous": 0,
        "evenements": 8707,
        "ticketsIntraZTrous": 0,
        "avoirs": 0
      },
      {
        "exercice": "2023-2024",
        "zMin": 3159,
        "zMax": 3378,
        "zCount": 220,
        "zAttendu": 220,
        "zTrous": 0,
        "idMin": 45388,
        "idMax": 53043,
        "idCount": 7656,
        "idAttendu": 7656,
        "idTrous": 0,
        "evenements": 7656,
        "ticketsIntraZTrous": 0,
        "avoirs": 0
      },
      {
        "exercice": "2024-2025",
        "zMin": 3379,
        "zMax": 3596,
        "zCount": 218,
        "zAttendu": 218,
        "zTrous": 0,
        "idMin": 53044,
        "idMax": 60019,
        "idCount": 6976,
        "idAttendu": 6976,
        "idTrous": 0,
        "evenements": 6976,
        "ticketsIntraZTrous": 0,
        "avoirs": 0
      }
    ],
    "zGlobalMin": 2938,
    "zGlobalMax": 3596,
    "zTotal": 659,
    "zTotalTrous": 0,
    "idGlobalMin": 36681,
    "idGlobalMax": 60019,
    "idTotal": 23339,
    "idTotalTrous": 0,
    "evenementsTotal": 23339,
    "ticketsIntraZTrousTotal": 0,
    "avoirsTotal": 0,
    "zChaineInterExercices": true,
    "idChaineInterExercices": true
  },
  "bancarisation": {
    "parExercice": [
      {
        "exercice": "2022-2023",
        "ca": 409020.76,
        "modes": [
          {
            "mode": "Carte Bancaire",
            "montant": 371789.81,
            "pct": 90.9
          },
          {
            "mode": "Espèce",
            "montant": 3649.46,
            "pct": 0.89
          },
          {
            "mode": "Ticket restaurant",
            "montant": 12486.22,
            "pct": 3.05
          },
          {
            "mode": "Chèque",
            "montant": 6876.06,
            "pct": 1.68
          },
          {
            "mode": "Chèque vacances",
            "montant": 14219.21,
            "pct": 3.48
          }
        ],
        "especes": 3649.46,
        "especesPct": 0.89,
        "cb": 371789.81,
        "cbPct": 90.9
      },
      {
        "exercice": "2023-2024",
        "ca": 429204.51,
        "modes": [
          {
            "mode": "Carte Bancaire",
            "montant": 391087.59,
            "pct": 91.12
          },
          {
            "mode": "Espèce",
            "montant": 8013.65,
            "pct": 1.87
          },
          {
            "mode": "Ticket restaurant",
            "montant": 10495.37,
            "pct": 2.45
          },
          {
            "mode": "Chèque",
            "montant": 3578.5,
            "pct": 0.83
          },
          {
            "mode": "Chèque vacances",
            "montant": 16029.4,
            "pct": 3.73
          }
        ],
        "especes": 8013.65,
        "especesPct": 1.87,
        "cb": 391087.59,
        "cbPct": 91.12
      },
      {
        "exercice": "2024-2025",
        "ca": 437753.6,
        "modes": [
          {
            "mode": "Carte Bancaire",
            "montant": 399911.38,
            "pct": 91.36
          },
          {
            "mode": "Espèce",
            "montant": 5379.05,
            "pct": 1.23
          },
          {
            "mode": "Ticket restaurant",
            "montant": 11120.36,
            "pct": 2.54
          },
          {
            "mode": "Chèque",
            "montant": 4931.45,
            "pct": 1.13
          },
          {
            "mode": "Chèque vacances",
            "montant": 16411.36,
            "pct": 3.75
          }
        ],
        "especes": 5379.05,
        "especesPct": 1.23,
        "cb": 399911.38,
        "cbPct": 91.36
      }
    ],
    "caTotal": 1275978.87,
    "especesTotal": 17042.16,
    "especesPct": 1.34,
    "cbTotal": 1162788.78,
    "cbPct": 91.13,
    "modesTotal": [
      {
        "mode": "Carte Bancaire",
        "montant": 1162788.78,
        "pct": 91.13
      },
      {
        "mode": "Espèce",
        "montant": 17042.16,
        "pct": 1.34
      },
      {
        "mode": "Ticket restaurant",
        "montant": 34101.95,
        "pct": 2.67
      },
      {
        "mode": "Chèque",
        "montant": 15386.01,
        "pct": 1.21
      },
      {
        "mode": "Chèque vacances",
        "montant": 46659.97,
        "pct": 3.66
      }
    ],
    "tracablePct": 98.66
  }
}
