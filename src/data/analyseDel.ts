// =============================================================================
// ANALYSE DES SUPPRESSIONS DE CAISSE (DEL) - journaux tpvevenement E1/E2/E3
// -----------------------------------------------------------------------------
// Objet : démontrer chiffres à l'appui que les lignes supprimées (DEL) de la
// caisse certifiée ne correspondent PAS à du chiffre d'affaires dissimulé.
//
// PROVENANCE : 100 % calculé par script depuis les 3 fichiers
// public/documents/caisse-enregistreuse/ANNEXE-E{1,2,3}_tpvevenement_*.xls (registre certifié).
// Lignes de pied de page (« Nb lignes ») exclues. Chaque total DEL est
// RÉCONCILIÉ avec le total interne déclaré par le fichier (champ `reconciliation`,
// tous `ok: true`). Montants en euros TTC.
// CA TTC et espèces : annexes A1/A2/A3 (synthèse certifiée), par libellé.
//
// NE PAS éditer à la main : régénéré par le script d'analyse.
// =============================================================================

export interface DelAberration {
  exercice: string
  date: string
  heure: string
  montant: number
  /** Part de cette seule ligne dans le total DEL des 3 ans (%). */
  pctDuTotal: number
}

export interface DelExercice {
  exercice: string
  joursService: number
  delCount: number
  delSomme: number
  delCountHorsAberr: number
  delSommeHorsAberr: number
  moyenneLigne: number
  mediane: number
  delParJour: number
  euroParJour: number
  caTTC: number
  especes: number
  /** Σ DEL en % du CA TTC déclaré de l'exercice. */
  delPctCA: number
}

export interface DelTranche {
  tranche: string
  n: number
  pct: number
}

export interface DelHeure {
  heure: number
  n: number
}

export interface DelReconciliation {
  exercice: string
  footCount: number
  footSomme: number
  ok: boolean
}

export interface AnalyseDel {
  // Totaux 3 exercices
  delCount: number
  delSomme: number // = montant brandi par le fisc
  joursService: number
  moyenneLigne: number
  mediane: number
  delParJour: number
  euroParJour: number
  /** Part des montants DEL comportant des centimes (≠ .00) - preuve de prix de carte. */
  partCentimes: number
  // Croisements (annexes A)
  caTTC: number
  especes: number
  especesPctCA: number
  delPctCA: number
  /** Σ DEL / total espèces encaissées sur 3 ans. */
  ratioDelSurEspeces: number
  // Aberrations (lignes manifestement non assimilables à un plat)
  seuilAberration: number
  aberrations: DelAberration[]
  aberrCount: number
  aberrSomme: number
  aberrPctTotal: number
  delCountHorsAberr: number
  delSommeHorsAberr: number
  moyenneHorsAberr: number
  /** Part des DEL survenant pendant les services (11-15h, 18-23h), en %. */
  partServices: number
  // Séries
  parExercice: DelExercice[]
  distribution: DelTranche[]
  parHeure: DelHeure[]
  reconciliation: DelReconciliation[]
}

export const analyseDel: AnalyseDel = {
  "delCount": 21302,
  "delSomme": 430763.15,
  "joursService": 659,
  "moyenneLigne": 20.22,
  "mediane": 8.7,
  "delParJour": 32.3,
  "euroParJour": 653.66,
  "partCentimes": 0.799,
  "caTTC": 1275978.87,
  "especes": 17042.16,
  "especesPctCA": 1.34,
  "delPctCA": 33.76,
  "ratioDelSurEspeces": 25.3,
  "seuilAberration": 1000.0,
  "aberrations": [
    {
      "exercice": "2022-2023",
      "date": "2022-07-26",
      "heure": "18:51",
      "montant": 68993.1,
      "pctDuTotal": 16.0
    },
    {
      "exercice": "2023-2024",
      "date": "2023-06-21",
      "heure": "17:06",
      "montant": 44955.0,
      "pctDuTotal": 10.4
    },
    {
      "exercice": "2022-2023",
      "date": "2022-08-07",
      "heure": "18:29",
      "montant": 19600.0,
      "pctDuTotal": 4.6
    },
    {
      "exercice": "2024-2025",
      "date": "2024-08-15",
      "heure": "11:16",
      "montant": 4455.0,
      "pctDuTotal": 1.0
    }
  ],
  "aberrCount": 4,
  "aberrSomme": 138003.1,
  "aberrPctTotal": 32.0,
  "delCountHorsAberr": 21298,
  "delSommeHorsAberr": 292760.05,
  "moyenneHorsAberr": 13.75,
  "partServices": 96.6,
  "parExercice": [
    {
      "exercice": "2022-2023",
      "joursService": 221,
      "delCount": 8014,
      "delSomme": 193005.09,
      "delCountHorsAberr": 8012,
      "delSommeHorsAberr": 104411.99,
      "moyenneLigne": 24.08,
      "mediane": 8.0,
      "delParJour": 36.3,
      "euroParJour": 873.33,
      "caTTC": 409020.76,
      "especes": 3649.46,
      "delPctCA": 47.19
    },
    {
      "exercice": "2023-2024",
      "joursService": 220,
      "delCount": 6943,
      "delSomme": 140686.55,
      "delCountHorsAberr": 6942,
      "delSommeHorsAberr": 95731.55,
      "moyenneLigne": 20.26,
      "mediane": 8.9,
      "delParJour": 31.6,
      "euroParJour": 639.48,
      "caTTC": 429204.51,
      "especes": 8013.65,
      "delPctCA": 32.78
    },
    {
      "exercice": "2024-2025",
      "joursService": 218,
      "delCount": 6345,
      "delSomme": 97071.51,
      "delCountHorsAberr": 6344,
      "delSommeHorsAberr": 92616.51,
      "moyenneLigne": 15.3,
      "mediane": 8.9,
      "delParJour": 29.1,
      "euroParJour": 445.28,
      "caTTC": 437753.6,
      "especes": 5379.05,
      "delPctCA": 22.17
    }
  ],
  "distribution": [
    {
      "tranche": "0-5 €",
      "n": 5978,
      "pct": 28.1
    },
    {
      "tranche": "5-10 €",
      "n": 6314,
      "pct": 29.6
    },
    {
      "tranche": "10-20 €",
      "n": 5590,
      "pct": 26.2
    },
    {
      "tranche": "20-30 €",
      "n": 1345,
      "pct": 6.3
    },
    {
      "tranche": "30-50 €",
      "n": 1492,
      "pct": 7.0
    },
    {
      "tranche": "50-100 €",
      "n": 522,
      "pct": 2.5
    },
    {
      "tranche": "> 100 €",
      "n": 59,
      "pct": 0.3
    }
  ],
  "parHeure": [
    {
      "heure": 0,
      "n": 0
    },
    {
      "heure": 1,
      "n": 0
    },
    {
      "heure": 2,
      "n": 0
    },
    {
      "heure": 3,
      "n": 0
    },
    {
      "heure": 4,
      "n": 0
    },
    {
      "heure": 5,
      "n": 0
    },
    {
      "heure": 6,
      "n": 0
    },
    {
      "heure": 7,
      "n": 0
    },
    {
      "heure": 8,
      "n": 5
    },
    {
      "heure": 9,
      "n": 5
    },
    {
      "heure": 10,
      "n": 276
    },
    {
      "heure": 11,
      "n": 2324
    },
    {
      "heure": 12,
      "n": 4930
    },
    {
      "heure": 13,
      "n": 1557
    },
    {
      "heure": 14,
      "n": 26
    },
    {
      "heure": 15,
      "n": 3
    },
    {
      "heure": 16,
      "n": 55
    },
    {
      "heure": 17,
      "n": 386
    },
    {
      "heure": 18,
      "n": 1990
    },
    {
      "heure": 19,
      "n": 5087
    },
    {
      "heure": 20,
      "n": 4239
    },
    {
      "heure": 21,
      "n": 415
    },
    {
      "heure": 22,
      "n": 3
    },
    {
      "heure": 23,
      "n": 1
    }
  ],
  "reconciliation": [
    {
      "exercice": "2022-2023",
      "footCount": 8014,
      "footSomme": 193005.09,
      "ok": true
    },
    {
      "exercice": "2023-2024",
      "footCount": 6943,
      "footSomme": 140686.55,
      "ok": true
    },
    {
      "exercice": "2024-2025",
      "footCount": 6345,
      "footSomme": 97071.51,
      "ok": true
    }
  ]
}
