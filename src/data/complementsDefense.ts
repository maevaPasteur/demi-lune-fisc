// =============================================================================
// COMPLÉMENTS DE DÉFENSE - findings produits par les scripts d'analyse
// src/data/incertitudeDisparu/ (08-12), à partir des annexes certifiées A/B/E/H.
// Données saisies depuis les sorties JSON de ces scripts (reproductibles).
// Pièces téléchargeables : /documents (section « Pièces de défense »).
// =============================================================================

export interface ZImpossible {
  z: string
  exercice: string
  caTickets: number
  suppressions: number
  nbLignes: number
}

export interface ErreurQuantite {
  date: string
  montant: number
  decomposition: string
}

export interface DistributionPrix {
  prix: number
  partVentes: number
  partSuppr: number
}

// --- Suppressions DEL : nouvelles preuves (scripts 09, 10, 11) ----------------
export const delComplements = {
  // Triangulation de 3 exports certifiés indépendants (script 11)
  triangulation: {
    syntheseA: 1275924,
    listeTicketsH: 1277216,
    encaissements: 1275980,
    suppressionsE: 430763,
  },
  // Sessions Z où les suppressions dépassent le CA encaissé du jour (script 11)
  sessionsImpossiblesNb: 9,
  sessionsImpossibles: [
    { z: '3015', exercice: '2022-2023', caTickets: 2563, suppressions: 69557, nbLignes: 37 },
    { z: '3216', exercice: '2023-2024', caTickets: 1686, suppressions: 45280, nbLignes: 24 },
    { z: '3026', exercice: '2022-2023', caTickets: 2210, suppressions: 20088, nbLignes: 41 },
    { z: '3474', exercice: '2024-2025', caTickets: 2302, suppressions: 5155, nbLignes: 44 },
  ] as ZImpossible[],
  // Erreurs de quantité à toutes échelles (script 10) : 9 lignes
  erreursQuantiteNb: 9,
  erreursQuantiteSomme: 140221,
  erreursQuantitePctDel: 32.6,
  erreursQuantite: [
    { date: '2022-07-26', montant: 68993.1, decomposition: '6,90 € (menu Bambin) × 9999' },
    { date: '2023-06-21', montant: 44955, decomposition: '45,00 € (menu Demi Lune) × 999' },
    { date: '2022-08-07', montant: 19600, decomposition: '19,60 € × 1000' },
    { date: '2024-08-15', montant: 4455, decomposition: '45,00 € (menu Demi Lune) × 99' },
    { date: '2024-01-05', montant: 810, decomposition: '45,00 € × 18' },
    { date: '2022-10-05', montant: 481, decomposition: '13,00 € × 37' },
  ] as ErreurQuantite[],
  // Distribution des prix : ventes vs suppressions (script 10)
  distribution: [
    { prix: 3.9, partVentes: 8.7, partSuppr: 8.6 },
    { prix: 18.6, partVentes: 6.3, partSuppr: 6.0 },
    { prix: 5.9, partVentes: 5.5, partSuppr: 4.7 },
    { prix: 8.9, partVentes: 3.1, partSuppr: 3.0 },
    { prix: 19.9, partVentes: 2.5, partSuppr: 2.8 },
    { prix: 17.6, partVentes: 2.2, partSuppr: 2.7 },
  ] as DistributionPrix[],
}

// --- Synthèse perte réelle : conso personnel + offerts + cascade (script 14) --
export interface LigneConso {
  poste: string
  litres: number | null
  coutAchat: number
  caEquivalent: number
  base: string
}

export const synthesePerteReelle = {
  // Consommation du personnel et de l'owner (litres, coût d'achat, CA équivalent)
  personnel: {
    lignes: [
      { poste: 'Coca - serveur Chris-Elian (4/j) + gérante Ghislaine (2/j)', litres: 1311, coutAchat: 2583, caEquivalent: 15496, base: '6 cannettes/jour × 662 j' },
      { poste: 'Limonade - tout le staff', litres: 165, coutAchat: 155, caEquivalent: 2574, base: '1 limonade 25 cl/jour' },
      { poste: 'Jus de fruit - tout le staff', litres: 397, coutAchat: 1231, caEquivalent: 6193, base: '3 jus 20 cl/jour' },
      { poste: 'Sirop à l’eau - tout le staff', litres: 40, coutAchat: 284, caEquivalent: 480, base: '3 sirops/jour' },
      { poste: 'Macvin - chef Thierry', litres: 99, coutAchat: 1797, caEquivalent: 8085, base: '2,5 verres 6 cl/jour' },
      { poste: 'Picon - chef Thierry', litres: 44, coutAchat: 457, caEquivalent: 6490, base: '~1,7 Picon Bière/jour' },
    ] as LigneConso[],
    totalLitres: 2056,
    totalCout: 6506,
    totalCa: 39319,
  },
  // Offerts aux clients (non sonnés) - estimations bornées
  offerts: {
    avertissement: 'Estimations bornées : les offerts ne sont pas enregistrés en caisse, par nature. À confirmer par l’exploitante.',
    lignes: [
      { poste: 'Apéritifs offerts (~1/jour)', litres: 39.7, coutAchat: 596, caEquivalent: 3641, base: '1 apéritif 6 cl/jour × 662 j' },
      { poste: 'Cafés offerts (~3/jour)', litres: null, coutAchat: 496, caEquivalent: 4369, base: '3 cafés/jour × 662 j' },
    ] as LigneConso[],
    totalCout: 1092,
    totalCa: 8010,
  },
  // Cascade : où va l'alcool acheté (litres, 3 exercices)
  cascade: {
    achatsAlcool: 10657,
    postes: [
      { poste: 'Vendu au verre (caisse)', litres: 5569 },
      { poste: 'Vendu en cocktails (caisse)', litres: 998 },
      { poste: 'Cuisine (fondues, babas, flambage)', litres: 566 },
      { poste: 'Alcool des menus (non détaillé en caisse)', litres: 228 },
      { poste: 'Consommation du chef (Picon + Macvin)', litres: 143 },
      { poste: 'Apéritifs offerts aux clients', litres: 40 },
      { poste: 'Sur-versement au verre (~8 %)', litres: 446 },
      { poste: 'Stock final (inventaire)', litres: 213 },
    ],
    perteReelle: 2454,
    perteReellePct: 23.0,
  },
}

// --- Boissons : recalcul Monte Carlo + réconciliation avec les DEL (12) -------
export const boissonsComplements = {
  disparuRevenuMedian: 76113,
  disparuRevenuIc: [62262, 87321] as [number, number],
  disparuPctAchats: 21.5,
  caBoissonsDeclare: 318026,
  caNourritureDeclare: 957898,
  delTotal: 430763,
}
