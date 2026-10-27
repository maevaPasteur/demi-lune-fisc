// =============================================================================
// RÉPONSE 2 - Contre-analyse des propositions de rectification PERSONNELLES
//             du 19 octobre 2026 (M. Thierry PASTEUR et Mme Ghislaine BEHEM).
// -----------------------------------------------------------------------------
// Chaque page est AUTO-SUFFISANTE : la position du service y est exposée, puis
// réfutée avec ses pièces et ses calculs, sans renvoi à un autre onglet.
// Le contenu vit dans src/data/reponse2/<slug>.json (chargé par import.meta.glob).
// =============================================================================

import type { Section } from './analyses'

export type BlocId = 'offensive' | 'rejet' | 'reconstitution' | 'taxation'

export interface Bloc {
  id: BlocId
  numero: number
  titre: string
  sousTitre: string
}

export const blocs: Bloc[] = [
  {
    id: 'offensive',
    numero: 1,
    titre: 'La nouvelle offensive du 19 octobre 2026',
    sousTitre:
      'Deux propositions de rectification personnelles notifiées à M. PASTEUR et à Mme BEHEM, qui recopient les griefs et la reconstitution du 18/05/2026 et imposent les distributions entre leurs mains.',
  },
  {
    id: 'rejet',
    numero: 2,
    titre: 'Le rejet de comptabilité',
    sousTitre:
      'Les griefs de rejet, repris à l’identique, sont réfutés un par un, dans l’ordre du courrier, pièces et calculs à l’appui.',
  },
  {
    id: 'reconstitution',
    numero: 3,
    titre: 'La méthode de reconstitution',
    sousTitre:
      'Le coefficient circulaire, les doses figées et les pertes ignorées : chaque poste est repris et corrigé sur les données réelles de la caisse et des factures.',
  },
  {
    id: 'taxation',
    numero: 4,
    titre: 'La taxation personnelle de Thierry et Ghislaine',
    sousTitre:
      'Distributions (art. 109), désignation (art. 117) et maître de l’affaire, majoration d’assiette de 25 %, majoration de 40 %, chiffrage de chaque associé : le cœur du nouveau, démonté avec la jurisprudence vérifiée.',
  },
]

export type Statut = 'demonte' | 'partiel' | 'a-etayer'

export interface Point {
  slug: string
  bloc: BlocId
  numero?: string
  parent?: string
  refCourrier: string
  titre: string
  positionService: string
  reponseCourte: string
  enjeu?: string
  statut: Statut
}

const C19 = 'Proposition personnelle du 19/10/2026'

export const points: Point[] = [
  // ----------------------------------------------------------- BLOC 1 --
  {
    slug: 'cadre-19-octobre', bloc: 'offensive',
    refCourrier: C19 + ' (PASTEUR & BEHEM)',
    titre: 'Deux propositions personnelles, une liquidation nouvelle sur la même reconstitution',
    positionService: '',
    reponseCourte:
      'Les deux propositions du 19/10/2026 recopient la reconstitution société et y greffent une liquidation personnelle (× 1,25, barème annoncé au PFU, prélèvements sociaux, 1727, 1729 recopié de la société) de 369 648 € sans prouver aucune appréhension : l\'exposition réelle est de 582 796 €, et chaque euro retranché à la reconstitution en retire mécaniquement aux trois contribuables.',
    enjeu: 'Exposition réelle 582 796 € (société 213 148 € + associés 369 648 €)',
    statut: 'partiel',
  },
  // ----------------------------------------------------------- BLOC 2 --
  {
    slug: 'inventaire-de-stocks', bloc: 'rejet',
    refCourrier: C19 + ' - Inventaire de stocks', titre: 'Inventaire de stocks jugé non conforme',
    positionService: '',
    reponseCourte:
      'La contenance qu’on reproche n’est exigée par aucun texte (R. 123-177 demande l’existence et la valeur, présentes sur chaque ligne), les états photographiés par le vérificateur se vérifient au centime (6 rapprochements nuls sur 6, variation 2023-2024 identique à son compte 310200), aucun euro n’est rattaché au grief et la gravité n’est ni démontrée ni mesurée ; reste non établie par pièce tierce la date du relevé des boissons pour 2025 et 2023.',
    statut: 'partiel',
  },
  {
    slug: 'suppressions-de-notes', bloc: 'rejet',
    refCourrier: C19 + ' - Suppressions « DEL »', titre: 'Les suppressions de notes (« DEL »)',
    positionService: '',
    reponseCourte:
      'Le grief est un montant, 430 763,15 € de lignes « DEL » sur trois exercices, et il se défait en euros : 99,6 à 99,7 % de chaque exercice a la forme d’un prix de la carte ou de son multiple, 32,0 % tient dans quatre fautes de frappe sur la quantité impossibles à encaisser, le totalisateur perpétuel inaltérable progresse sans une seule rupture sur 16 605 tickets, les 89 exemples datés sont vérifiés 89 sur 89, et 98 à 99 % des encaissements sont bancarisés ; les lignes « DEL » sont les traces de correction que le BOFiP invoqué impose, et le service ne désigne aucune vente encaissée non déclarée.',
    enjeu: 'Pilier n° 1 du rejet', statut: 'demonte',
  },
  {
    slug: 'quantites-inferieures-a-un', bloc: 'rejet',
    refCourrier: C19 + ' - Quantités < 1', titre: 'Les quantités inférieures à 1',
    positionService: '',
    reponseCourte:
      'Sur les fichiers du service, 5 012 des 5 062 articles fractionnés (99,0 %) se referment sur un entier, 1 849 notes sur 1 849 sont encaissées, la note de clôture de l’annexe B relie les parts pour 4 949 articles, « l’autre moitié » de la table 13 est imprimée p. 21 de la proposition, et le chiffrage de 62 487,87 € est une formule qui compte le prix entier d’articles payés une fois (95,7 % sur des lignes refermées) ; le résidu concédé est de 50 articles sur 8 tables, 264,98 € au maximum.',
    statut: 'demonte',
  },
  {
    slug: 'articles-a-zero-euro', bloc: 'rejet',
    refCourrier: C19 + ' - Articles à 0 €', titre: 'Les articles à prix 0 €',
    positionService: '',
    reponseCourte:
      'Le grief est qualitatif et sans montant : 272 lignes à 0 € sur 97 769 (0,28 %), 138 notes sur 16 607, 0,00 € porté, que la réponse écrite de la gérante invoquée par le service explique (prix modulé à la ligne, 0 € en étant la borne), dont les extraits du service confirment le décompte au demi-article près, et que le service reconnaît lui-même « non significatives ».',
    statut: 'demonte',
  },
  {
    slug: 'erreurs-de-tva', bloc: 'rejet',
    refCourrier: C19 + ' - TVA', titre: 'Les erreurs de TVA',
    positionService: '',
    reponseCourte:
      'La colonne lue par le service (VAT_base) vaut, sur 16 605 tickets sur 16 605, le TTC du palier de taux moins le taux lu comme un montant en euros : c’est une colonne d’affichage, pas la base d’imposition. La colonne de la taxe (tax_amount) ne porte aucune valeur négative sur les 29 588 lignes des trois journaux et concorde à 12,89 € près (0,01 %) avec la TVA sur les bases comptabilisées ; le surplus de 192,33 € du compte 445710 est la TVA sur les pourboires. Le grief ne porte aucun rappel chiffré.',
    statut: 'demonte',
  },
  {
    slug: 'fichiers-evenement-reglement', bloc: 'rejet',
    refCourrier: C19 + ' - Fichiers E et F', titre: 'Les fichiers Événement et Règlement',
    positionService: '',
    reponseCourte:
      'Les quatre montants que le service oppose sont quatre lectures des compteurs de la caisse qui se déduisent l\'un de l\'autre au centime sur les trois exercices, aucune ligne n\'a disparu entre les deux remises, les quantités de l\'annexe C restituent son chiffre d\'affaires à 0,04 / 44,58 / 131,08 € près contre 17 561 / 20 011 / 20 115 € pour l\'annexe B, les colonnes de TVA invoquées sont celles du service et ramènent la taxe à 19,68 € de la TVA reversée, et le motif du format Excel (p. 46) ne repose sur aucun texte applicable aux exercices vérifiés, la loi n\'attachant au format d\'une copie de contrôle que l\'amende de l\'article 1729 H, non appliquée.',
    statut: 'demonte',
  },
  {
    slug: 'tables-virtuelles', bloc: 'rejet',
    refCourrier: C19 + ' - Tables virtuelles', titre: 'Les tables « virtuelles »',
    positionService: '',
    reponseCourte:
      'Le numéro porté par l’export de caisse est un rang d’addition quotidien (1, 2, 3 … n), pas un numéro de table : vérifié par formule sur les 659 journées des trois exercices (16 624 additions, 16 607 numéros, 659 journées sur 659 sans trou, numéros de terrasse 101-125 jamais présents), et lisible jusque dans l’extrait du 09/09/2022 produit par le service (25 notes numérotées 1 à 25 pour 18 numéros à l’écran) ; la table « virtuelle » est une note de règlement séparé dont le service admet la logique, et la suppression de la table d’origine laisse une trace datée dans l’annexe E et un ticket à 0,00 € dans l’annexe H (3 281 tickets, 0,00 € encaissé, 2 449 clôturés à la minute exacte d’un « DEL »), de sorte que le grief F ne révèle aucun couvert ni aucune recette et que le service ne lui rattache aucun euro.',
    statut: 'demonte',
  },
  {
    slug: 'consommation-superieure-achats', bloc: 'rejet',
    refCourrier: C19 + ' - Conso > achats', titre: 'La consommation vendue supérieure aux achats',
    positionService: '',
    reponseCourte:
      'Sur les 203 pourcentages du service, le titre « consommation vendue supérieure aux achats » n\'est vérifié que par quatre écarts mineurs, chacun expliqué sur pièce ; produit par produit, 12 boissons sur 65 consomment plus qu\'elles n\'achètent (708,3 L), dont 11 par regroupement de libellés ou plancher d\'achats, et le Calvados seul reste discuté, son écart étant une dose de cuisine (93 L retranchés d\'un disponible de 73 L) et non une recette ; au total, l\'établissement a acheté 3 057,6 L de plus qu\'il n\'a servi (28,8 %).',
    enjeu: 'Le grief le plus factuel', statut: 'partiel',
  },
  {
    slug: 'instabilite-prix-menus', bloc: 'rejet',
    refCourrier: C19 + ' - Prix des menus', titre: 'L’instabilité des prix des menus',
    positionService: '',
    reponseCourte:
      'Le prix d\'un repas est libre (art. L. 410-2 c. com.), le prix de carte du Menu Demi Lune est unique et stable à 45,00 € sur les trois exercices, la « multitude de prix » est la conversion de tablées au forfait dont le total est conservé au centime (61 notes, 6 728,50 € supprimés = 6 728,49 € encaissés), le tableau du service est mal daté et à 60,7 % au prix de carte, les glaces sont un changement de tarif du 05/05/2023, et le service, qui juge le mécanisme « logique », n\'a jamais chiffré ce grief.',
    statut: 'demonte',
  },
  {
    slug: 'coefficient-de-revente', bloc: 'rejet',
    refCourrier: C19 + ' - Coefficient', titre: 'Le coefficient de revente jugé trop bas',
    positionService: '',
    reponseCourte:
      'L’opération du service, 3,85 × (1 - 0,15) = 3,2725, est exacte et concédée (la reconstitution reste 42 207 € sous ce repère sur trois ans), mais elle suppose 85 % des achats d’alcool revendus là où le bilan matière des 10 622 L en établit 60,77 % (6 455 L) : la même opération donne alors 2,383251, le niveau même des coefficients déclarés (2,30 / 2,39 / 2,31), de sorte que le repère ne mesure pas la modération de la reconstitution mais reconduit le taux de perte de 15 % qui en est déjà un paramètre.',
    statut: 'partiel',
  },
  // ----------------------------------------------------------- BLOC 3 --
  {
    slug: 'reconstitution-cadre', bloc: 'reconstitution',
    refCourrier: C19 + ' - Méthode', titre: 'La méthode de reconstitution',
    positionService: '',
    reponseCourte:
      'La méthode du service enchaîne cinq paramètres dont deux seulement sont lus dans l\'exploitation (prix moyens, rapport liquides/solides) et trois sont posés de l\'extérieur (doses de carte figées, forfaits de 5 + 5 + 5 %, extrapolation de la cuisine) : il en résulte 354 921 € de cuisine jamais mesurée, soit 75,2 % du rehaussement de 471 826 €, et un facteur de 3,94 à 4,10 qui multiplie chaque euro de liquides sur-évalué ; la défense concède l\'arithmétique du repère de 3,2725 (− 42 207 € sur trois ans) mais pas sa valeur de preuve, le même calcul donnant 2,383251 avec la part revendue mesurée de 60,77 %.',
    statut: 'partiel',
  },
  {
    slug: 'sur-versement', bloc: 'reconstitution',
    refCourrier: C19 + ' - Sur-versement', titre: 'Le sur-versement au verre',
    positionService: '',
    reponseCourte:
      'Le taux moyen de 17,60 % que le service applique au pichet et à la bouteille fabrique des contenants (58,80 cl, 88,20 cl, « pichet de 25 cl ») absents de notre mémoire, où le pichet est déjà à 0 % ; ramenée à la valeur centrale des mesures publiées (verre 18,28 cl, cocktails +41,7 %, spiritueux +0,7 % au lieu de +20 %) et bornée par le stock (27,1 % de ce qu\'il autoriserait), la demande unique est de 460,6 L sur trois exercices, soit 1 633 verres de 15 cl comptés en trop, 3 643 € de CA liquides et 12 199 € de CA total reconstitué en trop sur le seul exercice 2022-2023 (10 973 € / 37 500 € sur trois exercices), face à un service qui n\'oppose aucune mesure.',
    statut: 'partiel',
  },
  {
    slug: 'perte-de-biere', bloc: 'reconstitution',
    refCourrier: C19 + ' - Perte de bière', titre: 'La perte de bière (mousse et tirage)',
    positionService: '',
    reponseCourte:
      'Le service retranche déjà 15 % du volume de fût disponible (326,4 L sur trois exercices, lus sur ses annexes 6 et 7) et notre freinte technique défendable (10 % de la bière sortie du fût, 121,3 L) reste en deçà sur chacun des trois exercices : aucun dégrèvement n\'est demandé au titre de la seule freinte, mais le motif du refus tombe (le cumul des deux taux fait 27,75 % et non 30 %, et aucun des deux n\'est une freinte) et l\'assiette de 1 213,3 L est fixée pour le bilan matière.',
    statut: 'partiel',
  },
  {
    slug: 'perte-de-cremant', bloc: 'reconstitution',
    refCourrier: C19 + ' - Perte de crémant', titre: 'La perte de crémant',
    positionService: '',
    reponseCourte:
      'Aux seules doses, libellés et volumes du service (p. 62 et 84), le décompte bouteille par bouteille de 643 journées de caisse montre que 248,1 L de fond de bouteille, sans aucun sur-versement, expliquent 84,6 % de l’écart de 293,1 L imputé à des recettes occultes (reste 45,0 L), soit une réduction d’au moins 7 819 € HT de chiffre d’affaires liquides reconstitué, sous la seule hypothèse, non mesurée de part et d’autre, que la bouteille entamée n’est pas reportée au lendemain.',
    statut: 'partiel',
  },
  {
    slug: 'degustation-offerte', bloc: 'reconstitution',
    refCourrier: C19 + ' - Dégustation', titre: 'La dégustation offerte',
    positionService: '',
    reponseCourte:
      'Les motifs du service (globalisation sur 3 ans, 198 L au BIB, 500 L en bouteilles, « toutes les notes ») tombent ou ne portent que sur un périmètre que nous retirons nous-mêmes, mais la caisse ne trace que 1,85 L de vin nommé à 0 € : les 97,42 L demandés (dont 75,96 L au verre) restent une hypothèse à 2 cl non mesurée, suspendue à une attestation de salle à produire.',
    statut: 'a-etayer',
  },
  {
    slug: 'alcool-de-cuisine', bloc: 'reconstitution',
    refCourrier: C19 + ' - Alcool de cuisine', titre: 'L’alcool de cuisine',
    positionService: '',
    reponseCourte:
      'Après plafonnement aux achats facturés et déduction, exercice par exercice, de ce que le service retranche déjà, 72,68 L d’alcool cuit dans les plats de la carte restent comptés comme des verres vendus (porto 52,90, vin jaune 12,90, Grand Marnier 5,96, Bailey’s 0,92), soit environ 5 113 € de CA liquides TTC et, après abattements et coefficient du service, environ 17 466 € de total reconstitué ; ravelin, macvin, Calvados et crème de cassis sont déjà couverts et nous ne demandons rien à leur titre.',
    statut: 'partiel',
  },
  {
    slug: 'alcool-plats-menus', bloc: 'reconstitution',
    refCourrier: C19 + ' - Alcool des menus', titre: 'L’alcool cuit dans les plats des menus',
    positionService: '',
    reponseCourte:
      'Après déduction de ce que le service retranche déjà, l’alcool cuit dans les plats des menus se ramène à 20,53 L de desserts de menu que ses annexes 7 ne déduisent nulle part (Bailey’s 14,36 L, liqueur de poire 4,07 L, marc 2,10 L), soit environ 2 737 € de CA liquides TTC comptés à tort comme des verres vendus au comptoir ; deux des trois volumes « disponibles » qu’il oppose sont démentis par sa propre annexe n° 6, et la valorisation au prix du verre, objet du point 6, n’est pas discutée dans sa réponse.',
    statut: 'partiel',
  },
  {
    slug: 'variation-de-stock', bloc: 'reconstitution',
    refCourrier: C19 + ' - Variation de stock', titre: 'La variation de stock',
    positionService: '',
    reponseCourte:
      'Le point 9 est retiré (gain 0 € : la variation 2023-2024 de −1 029,67 € du service est exactement la différence de nos inventaires datés, et les « environ 2 162 € » du mémoire reposaient sur une convention de signe inversée), mais les propres comptes du service établissent un stock de boissons plat sur trois exercices (variation cumulée −2 103,91 € = 1,48 % de 141 720,38 € d\'achats, 98,52 % consommés), bâti sur les inventaires mêmes qu\'il déclare non conformes, au moyen d\'un tableau de coefficients qui ne s\'additionne pas (+ 2 000,00 € et + 20,00 €).',
    statut: 'partiel',
  },
  {
    slug: 'ventes-sans-achat', bloc: 'reconstitution',
    refCourrier: C19 + ' - Ventes sans achat', titre: 'Les « ventes sans achat »',
    positionService: '',
    reponseCourte:
      'Le point 10 ne porte aucun euro (le service l\'écrit p. 74) et ses deux exemples sont contredits par les propres annexes du service (Bordeaux : 11 achetées, 10 disponibles pour 9 vendues ; Nuits blanc : 42 disponibles pour 7 vendues), tandis que les 12 950 cl de « Beaune blanc » sont 150 cl de Beaune blanc plus 256 pichets de rosé maison (12 800 cl) portés par un code de caisse réaffecté le 05/05/2023, et les tableaux de la page 75 impriment sous l\'exercice 1 les volumes de 2024-2025 et répètent 2023-2024 sous l\'exercice 3 ; reste une bouteille de Bordeaux (75 cl, 30 € HT au plus) sortie sans vente, que nous assumons.',
    statut: 'partiel',
  },
  {
    slug: 'abattements-et-pertes', bloc: 'reconstitution',
    refCourrier: C19 + ' - Abattements', titre: 'Les abattements et pertes forfaitaires',
    positionService: '',
    reponseCourte:
      'Ramené en litres, le forfait de 15 % (1 593 L) couvre et dépasse la consommation sans vente que nous documentons (1 158 L brut, 697,4 L net hors sur-versement déjà facturé), de sorte que ce point ne réduit pas le redressement ; ce qui tombe, c’est l’emploi que le service fait de ce forfait unique, opposé six fois dans huit pages, et ses comparaisons « 13 fois / 3 fois », qui mêlent 26 216,19 € de cuisine extrapolée par exercice à des chiffres de boissons.',
    statut: 'partiel',
  },
  {
    slug: 'extrapolation-cuisine', bloc: 'reconstitution',
    refCourrier: C19 + ' - Extrapolation', titre: 'L’extrapolation cuisine (coefficient liquide → solide)',
    positionService: '',
    reponseCourte:
      'Le service ne mesure jamais la cuisine : il multiplie le CA liquides reconstitué par le rapport liquides/solides lu au bas de ses annexes D (2,94 / 3,02 / 3,10), mesuré sur la caisse qu\'il rejette par ailleurs ; appliqué à un CA liquides majoré de 32 à 48 %, ce rapport fabrique 354 921 € de cuisine extrapolée en plus des 959 561 € enregistrés plat par plat, soit 75,2 % du rehaussement de 471 826 €, sans un couvert ni un achat alimentaire de plus ; le levier 1 + rapport que le service qualifie de « double compte » est celui qu\'il applique lui-même p. 71-72 (8 917,07 € × 3,94 = 35 133,26 €), et le test de la p. 93 (3,2725) ne valide pas le partage liquides/cuisine.',
    statut: 'partiel',
  },
  // ----------------------------------------------------------- BLOC 4 --
  {
    slug: 'distributions-principe', bloc: 'taxation', numero: '4.1',
    refCourrier: C19 + ', « En matière de distributions »',
    titre: '4.1 - Le principe : des distributions sans existence propre',
    positionService: '',
    reponseCourte:
      'La distribution n\'existe que par la reconstitution : 235 913 € par foyer = moitié des discordances TTC, sans flux, compte courant ni enrichissement ; si la reconstitution tombe, les 369 648 € de suppléments personnels tombent, si elle est réduite la base baisse d\'autant ; en tout état de cause la TVA rappelée (24 963 € par foyer, 49 926 € pour les deux) sort de la base (CE n° 491690) et la clé de 50/50 entre deux co-gérants n\'est pas prouvée (CE n° 388887).',
    enjeu: 'Base des RCM imposés (235 913 € par foyer)', statut: 'partiel',
  },
  {
    slug: 'designation-117-maitre-affaire', bloc: 'taxation', numero: '4.2',
    refCourrier: C19 + ' ; désignation du 16/06/2026',
    titre: '4.2 - La désignation (art. 117) et le « maître de l’affaire »',
    positionService: '',
    reponseCourte:
      'La désignation du 16/06/2026 (par avocat, 29 jours après la demande) prive l\'amende de 100 % de son fait générateur (471 826 €), sans fixer aucune proportion ; les propositions du 19/10/2026 répartissent ensuite 235 913 € par foyer d\'après le seul capital et attribuent « toute latitude » aux deux co-gérants, ce qui exclut la présomption réservée au « seul maître de l\'affaire » (CE n° 388887) et laisse au service une preuve d\'appréhension par foyer qu\'il n\'apporte pas, la part TVA (24 963 € par foyer, art. 109-1-2°) exigeant de surcroît la preuve d\'une mise à disposition (CE n° 433827).',
    statut: 'partiel',
  },
  {
    slug: 'majoration-25-pourcent', bloc: 'taxation', numero: '4.3',
    refCourrier: C19 + ', art. 158-7-2° du CGI',
    titre: '4.3 - La majoration d’assiette de 25 %',
    positionService: '',
    reponseCourte:
      'Le coefficient 1,25 est une règle d\'assiette légale (art. 158-7-2°, CC 2019-793 QPC), que le service a correctement tenue hors des prélèvements sociaux (vérifié sur les six foyers-années) et exactement liquidée (barème reproduit à l\'euro) : il ne dégage aucune réduction propre, et coûte 64 122 € aux deux foyers (45 802 € d\'impôt + 18 320 € de majoration) qui tombent avec la reconstitution qu\'il multiplie ; seul reste à vérifier le nombre de parts 2025 de M. PASTEUR (1,9 annoncé, 1,5 liquidé : 2 023 €).',
    statut: 'partiel',
  },
  {
    slug: 'manquement-delibere-personnel', bloc: 'taxation', numero: '4.4',
    refCourrier: C19 + ', art. 1729 et 1727 du CGI',
    titre: '4.4 - La majoration de 40 % et les intérêts',
    positionService: '',
    reponseCourte:
      'La majoration de 40 % (162 532 € : 58 823 € société, 54 914 € PASTEUR, 48 795 € BEHEM) repose sur une motivation copiée trois fois qui vise l\'IS et la TVA alors qu\'elle sanctionne l\'IR de chaque foyer, et sur une « latitude de dissimuler » qui n\'est pas un acte : la preuve du manquement délibéré de chaque intéressé (art. 1729 a CGI, L. 195 A LPF) n\'est pas rapportée ; les intérêts (16 143 €) suivent les droits.',
    statut: 'partiel',
  },
  {
    slug: 'pasteur-chiffrage', bloc: 'taxation', numero: '4.5',
    refCourrier: 'Proposition personnelle PASTEUR du 19/10/2026',
    titre: '4.5 - Le chiffrage de M. Thierry PASTEUR',
    positionService: '',
    reponseCourte:
      'Le supplément de 196 945 € se recalcule à l\'euro près à partir de la reconstitution société (base 235 913 € = TTC ÷ 2, × 1,25, barème avec quotient plafonné, PS sans le 1,25, intérêts 0,20 %, 40 %) : il n\'a aucune autonomie et tombe avec elle (0 / 39 056 / 85 683 / 138 735 € selon que la reconstitution est annulée ou réduite de 75 / 50 / 25 %) ; la majoration de 40 % du foyer, 54 914 € (IR 38 292 € + PS 16 622 €), est motivée par un texte écrit pour l\'IS et la TVA de la société et doit être déchargée.',
    enjeu: '196 945 €', statut: 'partiel',
  },
  {
    slug: 'behem-chiffrage', bloc: 'taxation', numero: '4.6',
    refCourrier: 'Proposition personnelle BEHEM du 19/10/2026',
    titre: '4.6 - Le chiffrage de Mme Ghislaine BEHEM',
    positionService: '',
    reponseCourte:
      'Le supplément de 172 703 € notifié à Mme BEHEM est recalculé et reproduit à l\'euro près (42 lignes, 0 écart) ; il n\'a aucune base propre (discordance TTC de la reconstitution ÷ 2), il est liquidé sur la seule part HT (210 950 €) contre 235 913 € annoncés, il porte deux totaux pour 2024 (48 124 / 50 334 €), et sa majoration de 40 % (48 795 €) est motivée par renvoi à l\'IS et à la TVA de la société pour des exercices « 2022 et 2023 ».',
    enjeu: '172 703 €', statut: 'partiel',
  },
  {
    slug: 'synthese-et-demande', bloc: 'taxation', numero: '4.7',
    refCourrier: 'Synthèse de la Réponse 2',
    titre: '4.7 - Exposition réelle et demandes',
    positionService: '',
    reponseCourte:
      'Après la désignation du 16/06/2026, l\'exposition réelle est de 582 796 € (société 213 148 € + associés 369 648 €), et non 684 974 €. Tout dépend de la reconstitution : si elle tombe, tout tombe ; si elle est réduite, l\'exposition baisse d\'autant. Nous demandons la Commission sur les seules questions de fait de la reconstitution, et la décharge contentieuse pour le reste.',
    enjeu: 'Total en jeu 582 796 €', statut: 'partiel',
  },
]

// --- Chargement du contenu rédigé : src/data/reponse2/<slug>.json ------------
interface PageDoc {
  meta?: Record<string, unknown>
  entete?: { positionService?: string; reponseCourte?: string; enjeu?: string; statut?: Statut }
  sections?: Section[]
}

const modules = import.meta.glob('./reponse2/*.json', { eager: true }) as Record<
  string,
  { default: PageDoc }
>
const docs: Record<string, PageDoc> = {}
for (const [chemin, mod] of Object.entries(modules)) {
  const slug = chemin.replace('./reponse2/', '').replace('.json', '')
  docs[slug] = mod.default
}

export const sectionsDuPoint = (slug: string): Section[] => docs[slug]?.sections ?? []

const enrichi = (pt: Point): Point => {
  const e = docs[pt.slug]?.entete
  return e ? { ...pt, ...e } : pt
}

export const pointParSlug = (slug: string): Point | undefined => {
  const pt = points.find((x) => x.slug === slug)
  return pt ? enrichi(pt) : undefined
}

export const pointsParBloc = (bloc: BlocId): Point[] =>
  points.filter((pt) => pt.bloc === bloc).map(enrichi)

export const sousPages = (slug: string): Point[] => points.filter((pt) => pt.parent === slug)

export const numeroDuPoint = (slug: string): string => {
  const pt = points.find((x) => x.slug === slug)
  if (!pt) return ''
  if (pt.numero) return pt.numero
  const bloc = blocs.find((b) => b.id === pt.bloc)
  if (!bloc) return ''
  let n = 0
  for (const x of pointsParBloc(pt.bloc)) {
    if (x.numero) continue
    n += 1
    if (x.slug === slug) return `${bloc.numero}.${n}`
  }
  return ''
}

export const voisins = (slug: string): { prec?: Point; suiv?: Point } => {
  const i = points.findIndex((pt) => pt.slug === slug)
  if (i < 0) return {}
  return { prec: points[i - 1], suiv: points[i + 1] }
}
