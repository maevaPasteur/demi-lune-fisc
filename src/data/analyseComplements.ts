// =============================================================================
// COMPLÉMENTS D'ANALYSE - métriques calculées par script (source unique).
// del : profil des suppressions (rafales même minute, ≤10€, événements de nuit).
//   Source : annexes E1/E2/E3.
// especes : statistiques des règlements espèces (journal des règlements, annexe F).
// caissier : opérateur(s) sur l'ensemble des tickets (annexes H1/H2/H3).
// tracableTiers : encaissements remboursés par des tiers (titres-restaurant +
//   chèques-vacances), depuis les annexes A. NE PAS éditer à la main.
// =============================================================================

export interface Complements {
  del: { partRafales: number; partInf10: number; delNuit: number; delTotal: number }
  especes: { nb: number; max: number; mediane: number }
  caissier: { nom: string; nbTickets: number; nbDistincts: number }
  tracableTiers: number
}

export const complements: Complements = {
  "del": {
    "partRafales": 0.853,
    "partInf10": 0.578,
    "delNuit": 0,
    "delTotal": 21302
  },
  "especes": {
    "nb": 727,
    "max": 236.6,
    "mediane": 8.6
  },
  "caissier": {
    "nom": "LUNA",
    "nbTickets": 19903,
    "nbDistincts": 1
  },
  "tracableTiers": 64348.56
}
