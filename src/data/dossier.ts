// =============================================================================
// SOURCE DE DONNÉES UNIQUE DU DOSSIER
// Tous les chiffres et textes de synthèse du dossier vivent ici. Aucune valeur
// ne doit être écrite en dur dans le JSX : la page lit exclusivement ce fichier.
//
// MISE À JOUR 10/2026 : après la désignation des bénéficiaires du 16/06/2026
// (art. 117 CGI), l'amende de 100 % (art. 1759, 471 826 €) est ABANDONNÉE et
// REMPLACÉE par la taxation personnelle des deux co-gérants (propositions de
// rectification personnelles du 19/10/2026). L'exposition se lit désormais en
// deux étages : société (213 148 €) + associés (369 648 €).
// =============================================================================

/** Un poste de redressement / pénalité notifié par l'administration. */
export interface PostePenalite {
  poste: string
  montant: number
}

// --- Rappel : ce qui a été INITIALEMENT notifié (proposition du 18/05/2026) --
/** Détail des sommes initialement notifiées (droits, intérêts, majorations, 1759). */
export const penalitesInitiales: PostePenalite[] = [
  { poste: 'Droits IS', montant: 97510 },
  { poste: 'Intérêts de retard IS', montant: 4661 },
  { poste: 'Majoration 1729 IS (40 %)', montant: 39004 },
  { poste: 'Droits TVA', montant: 49547 },
  { poste: 'Intérêts de retard TVA', montant: 2607 },
  { poste: 'Majoration 1729 TVA (40 %)', montant: 19819 },
  { poste: 'Amende 1759 (100 % distributions)', montant: 471826 },
]

/** Total initialement notifié = 684 974 € (calculé, jamais saisi en dur). */
export const totalPenalites: number = penalitesInitiales.reduce(
  (somme, ligne) => somme + ligne.montant,
  0,
)

/** Montant de l'amende 1759 abandonnée après désignation des bénéficiaires. */
export const amende1759: number = 471826

// --- Étage 1 : la société (maintenu) -----------------------------------------
/** Droits et majorations maintenus au niveau de la SARL (hors amende 1759). */
export const societe: PostePenalite[] = [
  { poste: 'Droits IS', montant: 97510 },
  { poste: 'Intérêts de retard IS', montant: 4661 },
  { poste: 'Majoration 1729 IS (40 %)', montant: 39004 },
  { poste: 'Droits TVA', montant: 49547 },
  { poste: 'Intérêts de retard TVA', montant: 2607 },
  { poste: 'Majoration 1729 TVA (40 %)', montant: 19819 },
]

export const totalSociete: number = societe.reduce((s, l) => s + l.montant, 0)

// --- Étage 2 : les associés (taxation personnelle, 19/10/2026) ---------------
export interface Associe {
  nom: string
  /** Supplément d'impôt notifié par année (IR + prélèvements sociaux). */
  annees: { annee: string; montant: number }[]
}

export const associes: Associe[] = [
  {
    nom: 'M. Thierry PASTEUR',
    annees: [
      { annee: '2023', montant: 83391 },
      { annee: '2024', montant: 56724 },
      { annee: '2025', montant: 56830 },
    ],
  },
  {
    nom: 'Mme Ghislaine BEHEM',
    annees: [
      { annee: '2023', montant: 73859 },
      { annee: '2024', montant: 48124 },
      { annee: '2025', montant: 50720 },
    ],
  },
]

/** Total par associé. */
export const totalParAssocie = (a: Associe): number =>
  a.annees.reduce((s, x) => s + x.montant, 0)

/** Total de la taxation personnelle des deux associés = 369 648 €. */
export const totalAssocies: number = associes.reduce(
  (s, a) => s + totalParAssocie(a),
  0,
)

/** Exposition réelle actuelle = société + associés = 582 796 €. */
export const totalActuel: number = totalSociete + totalAssocies

/**
 * Compatibilité : certaines pages lisent encore `penalites`. On y expose le
 * détail « société » (les postes réellement maintenus en droits et majorations).
 */
export const penalites: PostePenalite[] = societe

/** Déroulé du contrôle : dates de vérification, durée et période vérifiée. */
export interface Controle {
  debut: string
  fin: string
  duree: string
  periodeDebut: string
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
  /** Date ISO (AAAA-MM-JJ). */
  dateLimite: string
}

export const delai: Delai = {
  label:
    'Observations sur les propositions personnelles du 19/10/2026 (délai de 30 jours, prorogeable)',
  dateLimite: '2026-11-19',
}

/** Étapes de la cascade procédurale (de la cause à la conséquence). */
export const cascade: string[] = [
  'Proposition société (18/05/2026)',
  'Observations (08/07/2026)',
  'Réponse du fisc (04/09/2026)',
  'Désignation des bénéficiaires (16/06/2026)',
  'Propositions personnelles (19/10/2026)',
  'Commission départementale (demandée)',
]
