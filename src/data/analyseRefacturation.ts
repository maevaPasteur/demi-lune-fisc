// =============================================================================
// RE-FACTURATION VIA PRIX FORCÉS - calculé par script (source unique).
// Mécanisme « facture sans détail » : les plats d'une table sont supprimés (DEL)
// et re-facturés sous un article à PRIX FORCÉ. Méthode : pour chaque article et
// chaque mois, le « prix officiel » est le prix le plus fréquent (modal) ; une
// ligne est « forcée » si son prix unitaire diffère de ce prix officiel - ce qui
// EXCLUT les ventes normales des menus/formules à prix fixe. Seules les lignes
// forcées sont comptées. Ce total figure intégralement dans le CA déclaré.
// Articles confirmés par l'exploitant. Source : annexes B1/B2/B3. TTC.
// NE PAS éditer à la main.
// =============================================================================

export interface AnalyseRefacturation {
  /** Total des lignes à prix forcé (TTC), sur 3 exercices. */
  total: number
  lignes: number
  parExercice: { exercice: string; lignes: number; total: number }[]
  parArticle: { article: string; lignesTotal: number; lignesForcees: number; total: number }[]
  /** Prix officiel (palier) du Menu Demi Lune, détecté comme prix modal. */
  demiLunePrixOfficiel: number
  pctDuDelTotal: number
  pctDuDelHorsAberr: number
}

export const refacturation: AnalyseRefacturation = {
  "total": 22080.6,
  "lignes": 329,
  "parExercice": [
    {
      "exercice": "2022-2023",
      "lignes": 133,
      "total": 8103.29
    },
    {
      "exercice": "2023-2024",
      "lignes": 99,
      "total": 6568.8
    },
    {
      "exercice": "2024-2025",
      "lignes": 97,
      "total": 7408.51
    }
  ],
  "parArticle": [
    {
      "article": "Menu Demi Lune",
      "lignesTotal": 501,
      "lignesForcees": 175,
      "total": 14427.23
    },
    {
      "article": "Menu du jour",
      "lignesTotal": 129,
      "lignesForcees": 102,
      "total": 6215.59
    },
    {
      "article": "Formules",
      "lignesTotal": 910,
      "lignesForcees": 48,
      "total": 1274.48
    },
    {
      "article": "Plat du jour",
      "lignesTotal": 39,
      "lignesForcees": 4,
      "total": 163.3
    }
  ],
  "demiLunePrixOfficiel": 45.0,
  "pctDuDelTotal": 5.1,
  "pctDuDelHorsAberr": 7.5
}
