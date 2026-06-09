// =============================================================================
// SOURCE DE DONNÉES UNIQUE DU DOSSIER
// Tous les chiffres et textes du dossier vivent ici. Aucune valeur ne doit être
// écrite en dur dans le JSX : la page lit exclusivement ce fichier.
// =============================================================================

/** Un poste de redressement / pénalité notifié par l'administration. */
export interface PostePenalite {
  poste: string
  montant: number
}

/** Détail des sommes notifiées (droits, intérêts, majorations, pénalités). */
export const penalites: PostePenalite[] = [
  { poste: 'Droits IS', montant: 97510 },
  { poste: 'Intérêts de retard IS', montant: 4661 },
  { poste: 'Majoration 1729 IS (40 %)', montant: 39004 },
  { poste: 'Droits TVA', montant: 49547 },
  { poste: 'Intérêts de retard TVA', montant: 2607 },
  { poste: 'Majoration 1729 TVA (40 %)', montant: 19819 },
  { poste: 'Pénalité 1759 (100 % distributions)', montant: 471826 },
]

/** Total des sommes en jeu - calculé, jamais saisi en dur. */
export const totalPenalites: number = penalites.reduce(
  (somme, ligne) => somme + ligne.montant,
  0,
)

/** Déroulé du contrôle : dates de vérification, durée et période vérifiée. */
export interface Controle {
  /** Début des opérations de vérification (JJ/MM/AAAA). */
  debut: string
  /** Fin des opérations de vérification (JJ/MM/AAAA). */
  fin: string
  /** Durée constatée du contrôle. */
  duree: string
  /** Premier jour de la période vérifiée (JJ/MM/AAAA). */
  periodeDebut: string
  /** Dernier jour de la période vérifiée (JJ/MM/AAAA). */
  periodeFin: string
}

export const controle: Controle = {
  debut: '12/01/2026',
  fin: '12/05/2026',
  duree: '4 mois',
  periodeDebut: '01/04/2022',
  periodeFin: '31/03/2025',
}

/** Échéance procédurale critique à surveiller. */
export interface Delai {
  label: string
  /** Date ISO (AAAA-MM-JJ). Laissée en placeholder, à compléter. */
  dateLimite: string
}

export const delai: Delai = {
  label: 'Désignation Art. 117 CGI (30 j non prorogeables)',
  dateLimite: 'AAAA-MM-JJ', // <-- à renseigner
}

/** Étapes de la cascade procédurale (de la cause à la conséquence). */
export const cascade: string[] = [
  'Procédure',
  'Rejet de comptabilité',
  'Méthode de reconstitution',
  'Pénalités',
]
