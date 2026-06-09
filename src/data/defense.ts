// =============================================================================
// STRATÉGIE DE DÉFENSE (couche juridique)
// -----------------------------------------------------------------------------
// Synthèse des 5 modules d'analyse de la proposition de rectification, organisée
// par FRONT. Chaque argument relie une accusation (avec n° de page) à notre
// réponse, et renvoie vers les PREUVES chiffrées (/analyses) et les PIÈCES
// (/documents). Les cotes et estimations relèvent de l'opinion juridique
// (« à valider par l'avocat ») ; les chiffres de caisse, eux, sont vérifiés.
// Réutilise le modèle de section et le renderer des Analyses.
// =============================================================================

import { analyseParSlug, type Analyse, type Cellule, type Section } from './analyses'
import { groupes } from './documents'
import { totalPenalites } from './dossier'
import { formatEuro } from '../utils/format'

// Montants documentés (proposition de rectification / Modules 4 et 5).
const ENJEU = totalPenalites // 684 974 €
const SANCTIONS = 537917 // majoration 1729 + pénalité 1759
const P1759 = 471826 // pénalité art. 1759 (distributions présumées)
const GARANTI = 330278 // gain net minimum garanti par la désignation 117
const MAJ1729 = 58823 // majoration 1729 (IS + TVA)
const ESPERANCE_DU = 78380 // espérance pondérée du reste à payer (estimation Module 5)
const ECONOMIE = 606594 // économie attendue moyenne (estimation Module 5)

// --- Helpers ------------------------------------------------------------------
type Lien = { to: string; label: string }
const preuve = (slug: string): Lien => ({
  to: `/analyses/${slug}`,
  label: analyseParSlug(slug)?.titre ?? slug,
})
const piece = (lettre: string): Lien => {
  const g = groupes.find((x) => x.lettre === lettre)
  return g ? { to: `/documents/${g.slug}`, label: `Annexe ${g.lettre}` } : { to: '/documents', label: `Annexe ${lettre}` }
}
const enClair = (texte: string): Section => ({ kind: 'alerte', couleur: 'blue', titre: 'En clair', texte })
const retenir = (texte: string): Section => ({ kind: 'alerte', couleur: 'teal', titre: 'Ce qu’il faut retenir', texte })
const argument = (
  titre: string,
  page: string,
  accusation: string,
  faille: string,
  cote: string,
  preuves: Lien[] = [],
  pieces: Lien[] = [],
): Section => ({ kind: 'argument', titre, page, accusation, faille, cote, preuves, pieces })
const cg = (v: string): Cellule => ({ v })
const cd = (v: string): Cellule => ({ v, align: 'right' })

// --- Bandeau « à valider par l'avocat » (réutilisé) ---------------------------
const avertissementAvocat: Section = {
  kind: 'alerte',
  couleur: 'gray',
  titre: 'Analyse juridique - à valider par l’avocat',
  texte:
    'Les arguments, cotes et estimations ci-dessous synthétisent l’analyse du dossier et relèvent de l’appréciation du conseil. Les chiffres issus de la caisse (section Analyses) sont, eux, recalculés et vérifiés.',
}

// ======================= STRATÉGIE (page d'accueil de la Défense) =============
export const strategieSections: Section[] = [
  avertissementAvocat,
  enClair(
    'La défense se mène sur plusieurs fronts en parallèle. Deux gisements dominent : **éliminer la pénalité 1759** (action immédiate, sous 30 jours) et **faire tomber toute l’imposition** par la nullité de procédure, si le rejet de comptabilité est invalidé.',
  ),
  {
    kind: 'alerte',
    couleur: 'red',
    titre: 'À faire sous 30 jours - délai non prorogeable',
    texte: `Désigner les bénéficiaires « sous toutes réserves » (art. 117 CGI) **élimine la pénalité 1759 de ${formatEuro(P1759)}** sans valoir aveu et sans affaiblir la défense au fond. Gain net minimum garanti : **${formatEuro(GARANTI)}**.`,
  },
  {
    kind: 'kpis',
    items: [
      { label: 'Enjeu global notifié', valeur: formatEuro(ENJEU), sub: 'droits + sanctions' },
      { label: 'Sanctions (1729 + 1759)', valeur: formatEuro(SANCTIONS), sub: '77 % de l’enjeu' },
      { label: 'Pénalité 1759 évitable', valeur: formatEuro(P1759), sub: 'désignation 30 j', highlight: true, couleur: 'red' },
      { label: 'Gain garanti (désignation)', valeur: formatEuro(GARANTI), sub: 'quel que soit le fond', highlight: true, couleur: 'teal' },
    ],
  },
]

// ======================= FRONT - PÉNALITÉS (action urgente) ===================
const penalites: Analyse = {
  slug: 'penalites',
  eyebrow: 'Action urgente',
  titre: 'Pénalités : l’action 30 jours et la décharge',
  resume:
    'La pénalité 1759 (471 826 €) s’élimine par une désignation sous 30 jours. La majoration 1729 (58 823 €) est probablement déchargeable, faute de preuve d’intention.',
  force: 'forte',
  apercu: [
    { label: 'Pénalité 1759 (évitable)', valeur: formatEuro(P1759) },
    { label: 'Gain garanti', valeur: formatEuro(GARANTI) },
  ],
  sections: [
    {
      kind: 'alerte',
      couleur: 'red',
      titre: 'Action sous 30 jours - non prorogeable',
      texte: `Désigner les bénéficiaires « sous toutes réserves » (art. 117 CGI) **élimine la pénalité 1759 de ${formatEuro(P1759)}**. Gain net minimum garanti : **${formatEuro(GARANTI)}**, quel que soit le sort du fond.`,
    },
    enClair(
      'Pourquoi désigner alors qu’on prouve l’absence d’occultation ? Parce que la 1759 est **mécanique** : sans réponse sous 30 jours, elle s’applique automatiquement, **indépendamment du fond**. La désignation « **sous toutes réserves** » neutralise ce piège **sans valoir aveu** et **sans affaiblir** la défense. Si on gagne au fond, il n’y a ni pénalité ni impôt sur les associés. C’est un filet de sécurité, pas une reconnaissance.',
    ),
    argument(
      'Pénalité 1759 - distributions présumées',
      'p. 58',
      'À défaut de désignation des bénéficiaires sous 30 jours, pénalité de 100 % (471 826 €).',
      'La **désignation « sous toutes réserves »** (admise par la jurisprudence) éteint mécaniquement la pénalité **sans reconnaître** la moindre distribution. Contrepartie maximale, si le fond est perdu : ~141 548 € d’IR/PS pour les associés - soit **330 278 € économisés au pire**.',
      'très forte - sous condition d’action',
    ),
    argument(
      'Majoration 1729 - manquement délibéré',
      'p. 57-58',
      'Majoration de 40 % (58 823 € sur IS + TVA) pour manquement délibéré.',
      'La motivation **reprend les motifs du rejet sans démontrer l’intention** (CE 11/02/2021 : double preuve exigée). S’y ajoutent la **coopération constante** des dirigeants, l’**impossibilité arithmétique**, le **logiciel certifié**, et une **erreur d’intitulé** (exercice 2022 hors période). Décharge probable, indépendante du sort du principal.',
      'forte',
      [preuve('bancarisation')],
    ),
    {
      kind: 'note',
      texte: 'Intérêts de retard (art. 1727, 7 268 €) : suivent mécaniquement le sort du principal, sans moyen autonome.',
    },
    retenir(
      `Deux gisements : éliminer la 1759 (${formatEuro(P1759)}) par action immédiate, et décharger la 1729 (${formatEuro(MAJ1729)}) au contentieux. La désignation sous 30 jours est la mesure la plus rentable du dossier.`,
    ),
  ],
}

// ======================= FRONT - PROCÉDURE (nullité L.52) =====================
const procedure: Analyse = {
  slug: 'procedure',
  eyebrow: 'Levier procédural',
  titre: 'Nullité de la procédure (délai L. 52)',
  resume:
    'Le contrôle a duré 4 mois alors que le plafond légal est de 3 mois. Si le rejet de comptabilité tombe, l’imposition est nulle - et non réparable.',
  force: 'forte',
  apercu: [
    { label: 'Durée du contrôle', valeur: '4 mois' },
    { label: 'Plafond légal (L. 52 I)', valeur: '3 mois' },
  ],
  sections: [
    enClair(
      'La vérification sur place est limitée à **3 mois** (L. 52 I LPF). Elle ne peut passer à 6 mois que si la comptabilité est rejetée pour graves irrégularités. Ici le contrôle a duré **4 mois** : si le rejet ne tient pas, le délai légal est dépassé.',
    ),
    argument(
      'Dépassement du délai de vérification sur place',
      'p. 8',
      'Le service invoque l’extension à 6 mois (L. 52 II 4°) au motif du rejet de comptabilité.',
      'Le contrôle a duré **4 mois** (12/01 → 12/05/2026), au-delà du plafond de **3 mois** (L. 52 I). L’extension à 6 mois est **entièrement conditionnée à la validité du rejet**. Si le rejet est invalidé, la durée excède le délai légal → **nullité de l’imposition** (L. 52), **non réparable** (L. 51).',
      'Conditionnel - effet maximal',
      [preuve('reconstitution-ca'), preuve('suppressions-del')],
    ),
    retenir(
      `Si le rejet de comptabilité est invalidé, c’est **toute l’imposition (${formatEuro(ENJEU)})** qui tombe pour vice de procédure, sans que l’administration puisse recommencer (L. 51).`,
    ),
  ],
}

// ======================= FRONT - REJET DE COMPTABILITÉ ========================
const rejet: Analyse = {
  slug: 'rejet-comptabilite',
  eyebrow: 'Attaque principale',
  titre: 'Le rejet de comptabilité est infondé',
  resume:
    'Aucun des sept motifs ne caractérise une « grave irrégularité ». Faire tomber le rejet fait tomber l’extension de délai (nullité) et prive la reconstitution de sa base.',
  force: 'forte',
  apercu: [
    { label: 'Motifs invoqués', valeur: '7' },
    { label: 'Graves irrégularités établies', valeur: '0' },
  ],
  sections: [
    enClair(
      'Le rejet n’est légal que s’il repose sur des **graves irrégularités** privant la comptabilité de valeur probante - et la charge de la preuve pèse sur l’administration. Pris un par un, les sept motifs sont faibles, souvent contredits par la proposition elle-même.',
    ),
    argument(
      'Motif 1 - Inventaires de stocks',
      'p. 14',
      'Inventaires « incomplets » sur les volumes de certaines boissons = irrégularité grave.',
      'Les inventaires **existent et sont détaillés** ; l’omission de quelques volumes n’est pas l’inventaire globalisé visé par la jurisprudence. **Contradiction interne** : ces mêmes inventaires sont jugés « assez précis » (p. 36) pour fonder la reconstitution.',
      'modérée à forte',
    ),
    argument(
      'Motif 2 - Écarts prix × quantité',
      'p. 15-16',
      'Écarts inexpliqués entre prix × quantité et total facturé (~57 687 € sur 3 ans).',
      'Ces écarts sont **exactement nos remises**, au centime près (réductions, plats partagés, recettes modifiées) ; **0 ligne facturée au-dessus du tarif**. Rien d’inexpliqué.',
      'modérée',
      [preuve('reconstitution-ca')],
      [piece('B')],
    ),
    argument(
      'Motif 3 - Documentation de la caisse',
      'p. 17',
      'Absence de documentation / manuel de la caisse.',
      'Un guide a été remis ; son inadéquation aux écrans relève de **l’éditeur** (AKEAD), pas du restaurant. La caisse est **certifiée NF525** (certificat du 01/12/2018), valable sur toute la période.',
      'forte',
    ),
    argument(
      'Motif 4 - Offerts / gratuits non saisis',
      'p. 17',
      'Offerts, gratuits et consommation du personnel non enregistrés en caisse.',
      'Aucune obligation d’enregistrer des opérations **sans chiffre d’affaires**. Le vérificateur les gère lui-même par un **abattement (15 %, p. 51)** - preuve que ce n’est pas une grave irrégularité.',
      'forte',
    ),
    argument(
      'Motif 5 - Suppressions DEL',
      'p. 18-19, 23',
      '21 302 suppressions « DEL » = 430 763 € de recettes occultées.',
      'Trois preuves chiffrées l’excluent. (1) Sur **9 journées, les suppressions dépassent le CA encaissé du jour** (le 26/07/2022 : 69 557 € supprimés pour 2 563 € encaissés) - on ne supprime pas des ventes qui n’ont pas eu lieu. (2) Les plus grosses (138 003 €) sont des **fautes de frappe sur la quantité** (ex. menu Bambin 6,90 € × 9999). (3) **Trois exports certifiés** (synthèse, tickets, encaissements) reconstituent le même CA, suppressions hors des trois. Espèces = 1,3 %, encaissements CB = relevés bancaires : **aucun canal d’occultation**.',
      'forte',
      [preuve('suppressions-del'), preuve('bancarisation')],
      [piece('E'), piece('F'), { to: '/documents', label: 'Pièce - Défense Suppressions (téléchargeable)' }],
    ),
    argument(
      'Motif 6 - Prix 0 € et erreurs de TVA',
      'p. 22-23',
      'Articles à 0 € et erreurs de taux de TVA = manipulation.',
      'Le vérificateur écrit lui-même « **manipulation non-identifiée** » (p. 23) : il reconnaît ne pas savoir d’où viennent ces erreurs. Les articles à 0 € sont des pratiques courantes (menus enfants, garnitures incluses) : **272 lignes sur 3 ans** (0,3 % des ventes).',
      'modérée à forte',
      [],
      [piece('C'), piece('G')],
    ),
    argument(
      'Motif 7 - « Volumes disparus » (boissons)',
      'p. 30-31',
      'Écarts achats/ventes de boissons = volumes « disparus ».',
      'Recalculé sur les pièces réelles, cet écart s’explique **sans aucune recette cachée** : cuisine (que le fisc chiffre lui-même), ventes encaissées **sous un autre bouton**, marchandise **non livrée**, et stock. Un **modèle d’incertitude** situe le « disparu » alcool à ~76 k€ au prix de revente = **21,5 % des achats**, la perte normale d’un bar (15-25 %). Et ce disparu **ne s’additionne pas** aux suppressions de caisse : une boisson vendue au noir puis supprimée y figure déjà. Les **pourcentages négatifs** (plus vendu qu’acheté) trahissent un paramétrage de caisse défaillant ; les **achats Intermarché ne sont pas investigués** (p. 53).',
      'forte',
      [preuve('boissons-disparues')],
      [piece('D'), { to: '/documents', label: 'Pièce - Défense Boissons disparues (téléchargeable)' }],
    ),
    retenir(
      'Aucun motif, isolément ou ensemble, ne caractérise une grave irrégularité. Le « faisceau d’indices » de l’administration est surtout un faisceau d’incertitudes - qu’elle reconnaît elle-même (« manipulation non-identifiée », « impossible de confirmer »).',
    ),
  ],
}

// ======================= FRONT - MÉTHODE DE RECONSTITUTION =====================
const methode: Analyse = {
  slug: 'methode-reconstitution',
  eyebrow: 'Attaque subsidiaire',
  titre: 'La méthode de reconstitution est viciée',
  resume:
    'Même si le rejet tenait, la reconstitution des liquides s’effondre sur ses propres chiffres : son coefficient × 3,1 amplifie un chiffre d’affaires déjà surévalué - et la discordance s’inverse dès qu’on y remet les ventes réelles. Le CA réel est, par ailleurs, déjà prouvé au centime.',
  force: 'forte',
  apercu: [
    { label: 'Discordance alléguée', valeur: formatEuro(P1759) },
    { label: 'Reconstitution réelle', valeur: '= CA déclaré' },
  ],
  sections: [
    enClair(
      'Une reconstitution n’est admise qu’**après un rejet régulier** de la comptabilité, et doit reposer sur des données fiables. Or les **cinq exports certifiés reconstituent déjà le CA déclaré** : il n’y a aucun trou de 471 826 € à « reconstituer ».',
    ),
    argument(
      'Le coefficient repose sur des données… rejetées',
      'p. 52',
      'Environ 75 % du CA reconstitué vient d’un coefficient « liquides/solides » (× 2,94 à × 3,10) tiré de la caisse.',
      'Ce coefficient est **extrait des données de caisse** que l’administration déclare par ailleurs non probantes. On ne peut pas rejeter la caisse **et** s’en servir pour reconstituer.',
      'forte',
      [preuve('reconstitution-ca')],
    ),
    argument(
      'La discordance s’inverse avec les vrais chiffres',
      'Annexes finales',
      'Le manquant de boissons serait du chiffre d’affaires occulté (discordance + 139 728 € en 2024-2025).',
      'En reconstituant à partir des achats, le fisc obtient un CA liquide de **165 065 €** alors que la caisse n’a encaissé que **106 113 €** (+ 55,6 %), puis l’**amplifie × 3,1** sur une cuisine jamais mesurée. En réinjectant le **vrai** CA liquide dans sa **propre formule** (× 3,1, abattement 15 %), la discordance **s’inverse à −65 721 €** : aucune occultation. Recalcul boisson par boisson sur les pièces réelles.',
      'forte',
      [preuve('boissons-disparues')],
      [{ to: '/documents', label: 'Pièce - Boissons disparues (téléchargeable)' }],
    ),
    argument(
      'Abattement de 15 % insuffisant - la cuisine que le fisc chiffre puis oublie',
      'p. 51',
      'Abattement global de 15 % (offerts + pertes + personnel) pour les boissons.',
      'Le fisc déduit **lui-même** la cuisine produit par produit (Macvin 7 406 cl, **Calvados = 103 % de l’achat**, Absinthe 100 %, Vin Jaune 61 %…) mais maintient un abattement global de **15 %**. La jurisprudence admet **22 à 25 %** (CAA Paris 17/03/2021). Or notre mesure complète, boisson par boisson - après cuisine, alcool des menus et consommation du personnel - situe la **perte réelle à 23 % des achats d’alcool**, en plein dans cette fourchette. Les **achats Intermarché** ne sont pas non plus investigués (p. 53).',
      'modérée à forte',
      [preuve('boissons-disparues')],
      [{ to: '/documents', label: 'Pièce - Boissons disparues (téléchargeable)' }],
    ),
    argument(
      'Pourcentages négatifs = base défaillante',
      'p. 31',
      'Certaines boissons (Macvin, Martini) affichent des volumes « disparus » négatifs.',
      'Un pourcentage négatif signifie **plus vendu que disponible** : mathématiquement impossible si la méthode est correcte. C’est la preuve d’un **paramétrage défaillant** de la base.',
      'modérée à forte',
    ),
    argument(
      'Impossibilité arithmétique (espèces)',
      'p. 24',
      'La discordance reconstituée serait du chiffre d’affaires occulté.',
      'Pour occulter 193 234 € en 2023, il aurait fallu les encaisser en espèces - or les espèces de l’exercice ne sont que **3 798 €**. Aucun circuit parallèle n’est même allégué.',
      'très forte',
      [preuve('bancarisation')],
      [piece('F')],
    ),
    retenir(
      'Le CA déclaré est déjà adossé, au centime près, à cinq exports certifiés (voir « Reconstitution intégrale du CA »). Toute reconstitution extrapolée du fisc est démentie par les données réelles.',
    ),
  ],
}

// ======================= FRONT - STRATÉGIE & CHIFFRAGE ========================
const strategie: Analyse = {
  slug: 'strategie',
  eyebrow: 'Feuille de route',
  titre: 'Stratégie & chiffrage',
  resume:
    'La défense en cinq piliers, un chiffrage prévisionnel par scénarios, le calendrier des 60 premiers jours et les pièges à éviter.',
  force: 'forte',
  apercu: [
    { label: 'Économie attendue (estim.)', valeur: '~88 %' },
    { label: 'Gain garanti (désignation)', valeur: formatEuro(GARANTI) },
  ],
  sections: [
    enClair(
      'Cinq piliers menés de front : **(1)** agir sous 30 jours (désignation 1759), **(2)** faire tomber le rejet de comptabilité, **(3)** attaquer la méthode de reconstitution, **(4)** décharger la majoration 1729, **(5)** dérouler les voies de recours. Le pilier 2, s’il aboutit, entraîne la **nullité de toute l’imposition** (via le délai L. 52).',
    ),
    {
      kind: 'alerte',
      couleur: 'gray',
      titre: 'Chiffrage - estimation à valider par l’avocat',
      texte:
        'Les probabilités et montants ci-dessous sont une projection raisonnée du dossier (Module 5), destinée à éclairer la décision. Ils relèvent de l’appréciation du conseil et ne valent pas certitude.',
    },
    {
      kind: 'kpis',
      items: [
        { label: 'Enjeu global notifié', valeur: formatEuro(ENJEU), sub: 'droits + sanctions' },
        { label: 'Reste à payer (espérance)', valeur: formatEuro(ESPERANCE_DU), sub: 'moyenne pondérée' },
        { label: 'Économie attendue', valeur: formatEuro(ECONOMIE), sub: '~88 % de l’enjeu', highlight: true, couleur: 'teal' },
        { label: 'Gain garanti (désignation)', valeur: formatEuro(GARANTI), sub: 'quel que soit le fond', highlight: true, couleur: 'teal' },
      ],
    },
    {
      kind: 'tableau',
      titre: 'Scénarios pondérés (estimation)',
      minWidth: 560,
      colonnes: [
        { label: 'Scénario' },
        { label: 'Probabilité', align: 'right' },
        { label: 'Reste à payer', align: 'right' },
        { label: 'Économie', align: 'right' },
      ],
      lignes: [
        [cg('A - Nullité de procédure (L. 52)'), cd('40 %'), cd('0 €'), cd('100 %')],
        [cg('B - Méthode radicalement viciée'), cd('20 %'), cd('0 €'), cd('100 %')],
        [cg('C - Réduction substantielle'), cd('25 %'), cd(formatEuro(118349)), cd('83 %')],
        [cg('D - Maintien hors 1759'), cd('15 %'), cd(formatEuro(325284)), cd('53 %')],
      ],
    },
    {
      kind: 'tableau',
      titre: 'Calendrier des 60 premiers jours',
      minWidth: 520,
      colonnes: [{ label: 'Échéance' }, { label: 'Action' }],
      lignes: [
        [cg('Jour 0'), cg('Réception de la proposition - départ des délais.')],
        [cg('J. 1 à 7'), cg('Mandater un avocat fiscaliste spécialisé.')],
        [cg('J. 7 à 14'), cg('Recueillir les pièces (avis, FEC, inventaires, statuts, factures…).')],
        [cg('J. 14 à 25'), cg('Préparer le courrier : prorogation L. 57 + désignation 117 « sous réserves ».')],
        [{ v: 'J. 25 à 30', fw: 700 }, { v: 'Envoyer le RAR (désignation 1759) - échéance critique, non prorogeable.', fw: 700 }],
        [cg('J. 30 à 60'), cg('Rédiger et envoyer les observations en réponse.')],
      ],
    },
    {
      kind: 'tableau',
      titre: 'Pièges à éviter',
      minWidth: 560,
      colonnes: [{ label: 'Piège' }, { label: 'Pourquoi' }],
      lignes: [
        [cg('Ne pas désigner sous 30 jours'), cg('La pénalité 1759 (471 826 €) s’applique mécaniquement, sans recours sur ce point.')],
        [cg('Désigner sans « sous toutes réserves »'), cg('Risque d’être interprété comme une reconnaissance des distributions.')],
        [cg('Reconnaître les faits dans la réponse'), cg('Toute acceptation, même partielle, affaiblit la défense au fond.')],
        [cg('Modifier la compta ou la caisse a posteriori'), cg('Qualifications pénales possibles (faux) ; aggrave gravement la situation.')],
        [cg('Communiquer avec le vérificateur sans avocat'), cg('Une déclaration spontanée mal formulée peut servir d’aveu.')],
        [cg('Verser les factures Intermarché en bloc'), cg('Sur les boissons à pourcentage positif, cela aggrave le redressement - trier ligne par ligne.')],
        [cg('Payer sans demander le sursis (L. 277)'), cg('Complique la récupération en cas de victoire contentieuse.')],
        [cg('Laisser passer le délai de réclamation (R. 196-1)'), cg('Forclusion de droit, irrémédiable.')],
      ],
    },
    retenir(
      `Deux certitudes immédiates : la désignation sous 30 jours sécurise ${formatEuro(GARANTI)}, et l’invalidation du rejet ferait tomber toute l’imposition. Le reste se joue au contentieux - d’où l’intérêt de mener les cinq piliers de front.`,
    ),
  ],
}

// --- Catalogue + accès --------------------------------------------------------
export const fronts: Analyse[] = [strategie, penalites, procedure, rejet, methode]

export function frontParSlug(slug: string): Analyse | undefined {
  return fronts.find((f) => f.slug === slug)
}
