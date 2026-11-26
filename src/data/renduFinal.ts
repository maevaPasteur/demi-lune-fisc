// =============================================================================
// RENDU FINAL - Réponse point par point à la proposition de rectification
// -----------------------------------------------------------------------------
// Objectif : pour CHAQUE grief du rapport du fisc
// (public/documents/rapports-des-finances-publiques/Proposition_1_Lettre.pdf,
// synthèse dans .../synthese/*.md), produire une sous-page « avocat » :
//   - ce que soutient l'administration (avec page du rapport),
//   - notre réponse argumentée,
//   - le CALCUL EXACT (chiffres issus des modules data, jamais en dur ici),
//   - les FICHIERS exacts (pièces téléchargeables),
//   - le RÉSULTAT (ce que ça fait tomber).
// Le rendu réutilise le moteur de sections de <AnalyseContent> (type Section).
// Les chiffres proviennent des modules calculés (analyseDel, complements…).
// =============================================================================

import type { Section } from './analyses'





// Contenu rédigé des sous-pages (généré par scripts/rendu-final-<slug>.py,
// chiffres reproductibles ; consommé tel quel comme Section[]).
import RFZeroEuro from './renduFinal/articles-a-zero-euro.json'
import RFQuantites from './renduFinal/quantites-anormales.json'
import RFInventaire from './renduFinal/inventaire-stocks.json'
import RFTables from './renduFinal/tables-trop-nombreuses.json'
import RFFichiersEF from './renduFinal/fichiers-evenement-reglement.json'
import RFTva from './renduFinal/anomalies-tva.json'
import RFConsoAchats from './renduFinal/consommation-superieure-achats.json'
import RFPrixMenu from './renduFinal/prix-menu-demi-lune.json'
import RFCoefficients from './renduFinal/coefficients-de-revente.json'
import RFReconstitution from './renduFinal/reconstitution-volumes-liquides.json'
import RFSurversement from './renduFinal/sur-versement-au-verre.json'
import RFBiereMousse from './renduFinal/pertes-biere-mousse.json'
import RFCremant from './renduFinal/pertes-cremant.json'
import RFDegustation from './renduFinal/degustation-au-verre.json'
import RFCuisine from './renduFinal/alcool-cuisine-doses-plats.json'
import RFOfferts from './renduFinal/offerts-remises-pertes.json'
import RFCoefficient from './renduFinal/coefficient-liquide-solide.json'





// --- Blocs du rapport (4 chapitres de la proposition de rectification) -------
export type BlocId = 'rejet' | 'reconstitution' | 'rappels' | 'sanctions'
export interface Bloc {
  id: BlocId
  numero: number
  titre: string
  sousTitre: string
}
export const blocs: Bloc[] = [
  {
    id: 'rejet',
    numero: 1,
    titre: 'Rejet de la comptabilité',
    sousTitre:
      'L’administration juge la comptabilité non probante (caisse : suppressions, articles à 0 €, quantités, inventaire, fichiers E/F, TVA, conso > achats, prix du Menu Demi Lune, coefficients).',
  },
  {
    id: 'reconstitution',
    numero: 2,
    titre: 'Reconstitution du chiffre d’affaires',
    sousTitre:
      'Le service reconstruit le CA à partir des volumes de liquides (doses, repères), puis extrapole la cuisine par un coefficient.',
  },
  {
    id: 'rappels',
    numero: 3,
    titre: 'Rappels et profit sur le trésor',
    sousTitre: 'Rappels de TVA collectée, d’IS, et profit sur le trésor (cascade).',
  },
  {
    id: 'sanctions',
    numero: 4,
    titre: 'Pénalités et amende',
    sousTitre:
      'Intérêts de retard (1727), majoration 40 % pour manquement délibéré (1729), amende 100 % sur distributions présumées (1759).',
  },
]

export type Statut = 'demonte' | 'partiel' | 'a-etayer'
export interface Grief {
  slug: string
  bloc: BlocId
  numero?: string // libellé de numérotation forcé dans la nav (ex. « 2.1.a » pour une sous-page)
  refRapport: string // ex. « Rapport p. 14-24 »
  titre: string
  griefFisc: string // résumé de l'accusation
  reponseCourte: string // verdict en une phrase
  enjeu?: string // € en jeu si identifiable
  statut: Statut
  sections: Section[]
}





// =============================================================================
// CATALOGUE DES AUTRES GRIEFS (structure validée d'abord, rédaction ensuite)
// Chaque entrée porte déjà : rattachement au rapport, résumé du grief, angle de
// réponse. Le détail chiffré sera rédigé au même standard que l'exemple.
// =============================================================================
const enChantier = (angle: string): Section[] => [
  {
    kind: 'alerte',
    couleur: 'blue',
    titre: 'Angle de réponse retenu',
    texte: angle,
  },
]

const autresGriefs: Grief[] = [
  // ---- BLOC 1 : REJET DE COMPTABILITÉ ----
  {
    slug: 'articles-a-zero-euro',
    bloc: 'rejet',
    refRapport: 'Proposition p. 16-22 (rejet 1/3)',
    titre: 'Articles à prix 0 € (offerts / gratuits)',
    griefFisc: 'Des lignes vendues à 0 € seraient le signe de ventes sorties du chiffre d’affaires.',
    reponseCourte:
      'Page historique. Les formules de juillet 2026 sur les lignes à 0 € (« consommation du personnel », « offerts purs ou essais », 8 010 €) sont rectifiées dans la réponse actuelle, point 2.4.2 c).',
    statut: 'partiel',
    sections: RFZeroEuro.sections as unknown as Section[],
  },
  {
    slug: 'quantites-anormales',
    bloc: 'rejet',
    refRapport: 'Proposition p. 18-20 (rejet 1/3)',
    titre: 'Quantités « anormales »',
    griefFisc: 'Des quantités élevées ou atypiques sur certaines lignes traduiraient des anomalies.',
    reponseCourte:
      'Les quantités atypiques sont des fautes de frappe corrigées (mêmes lignes que les grosses suppressions) : elles sont annulées le jour même et n’entrent pas dans le CA.',
    statut: 'partiel',
    sections: RFQuantites.sections as unknown as Section[],
  },
  {
    slug: 'inventaire-stocks',
    bloc: 'rejet',
    refRapport: 'Proposition p. 14-16 (rejet 1/3)',
    titre: 'Inventaire de stocks (jugé absent ou incomplet)',
    griefFisc: 'L’absence d’inventaire détaillé empêcherait de contrôler la comptabilité matière.',
    reponseCourte:
      'L’inventaire physique des 3 fins d’exercice est disponible et détaillé ; il montre un stock stable, ce qui ferme le bilan matière.',
    statut: 'partiel',
    sections: RFInventaire.sections as unknown as Section[],
  },
  {
    slug: 'tables-trop-nombreuses',
    bloc: 'rejet',
    refRapport: 'Proposition p. 11 + p. 18-19',
    titre: 'Trop de tables / tables « virtuelles »',
    griefFisc:
      'La caisse comporte des tables « virtuelles » et autorise la suppression d’une table et de tous ses articles ; ces modifications ne seraient pas vérifiables, rendant la comptabilité non probante.',
    reponseCourte:
      'Un numéro de note n’est pas une table (14 tables intérieures réelles ; les n° 13/16/17/18 n’existent pas). La table « virtuelle » est une note de règlement séparé, et la suppression de la table d’origine évite de compter le repas deux fois : elle protège le CA, elle ne le réduit pas.',
    statut: 'demonte',
    sections: RFTables.sections as unknown as Section[],
  },
  {
    slug: 'fichiers-evenement-reglement',
    bloc: 'rejet',
    refRapport: 'Proposition p. 22-24 (rejet 1/3) — annexes E et F',
    titre: 'Fichiers Événement (E) et Règlement (F)',
    griefFisc: 'Les journaux d’événements et de règlements présenteraient des anomalies techniques.',
    reponseCourte:
      'Les journaux sont au contraire ce qui permet de prouver que CA = encaissements ; leurs « événements » sont des corrections d’exploitation tracées.',
    statut: 'partiel',
    sections: RFFichiersEF.sections as unknown as Section[],
  },
  {
    slug: 'anomalies-tva',
    bloc: 'rejet',
    refRapport: 'Proposition p. 22-28 (rejet 1/3 et 2/3) — annexe G',
    titre: 'Incohérences de TVA',
    griefFisc: 'Des incohérences de ventilation de TVA entacheraient la comptabilité.',
    reponseCourte:
      'La ventilation 10 %/20 % suit la nature des produits (sur place / à emporter, solide / liquide) ; les écarts relevés sont marginaux et explicables.',
    statut: 'a-etayer',
    sections: RFTva.sections as unknown as Section[],
  },
  {
    slug: 'consommation-superieure-achats',
    bloc: 'rejet',
    refRapport: 'Proposition p. 31-34 (rejet 3/3)',
    titre: 'Consommation vendue supérieure aux achats',
    griefFisc: 'Pour certains produits, les quantités vendues dépasseraient les achats, signe de ventes non comptabilisées.',
    reponseCourte:
      'Ces écarts viennent d’un étiquetage de caisse (libellés génériques / boutons mutualisés), pas de ventes cachées : le produit est acheté sous un autre nom.',
    statut: 'partiel',
    sections: RFConsoAchats.sections as unknown as Section[],
  },
  {
    slug: 'prix-menu-demi-lune',
    bloc: 'rejet',
    refRapport: 'Proposition p. 34-36 (rejet 3/3)',
    titre: 'Instabilité des prix du « Menu Demi Lune »',
    griefFisc: 'La variation du prix du menu Demi Lune traduirait une comptabilité non sincère.',
    reponseCourte:
      'Le prix varie parce que le menu est facturé hors prix catalogue (formules, remises, prix personnalisés) ; ces lignes sont tracées et exclues du calcul d’alcool.',
    statut: 'a-etayer',
    sections: RFPrixMenu.sections as unknown as Section[],
  },
  {
    slug: 'coefficients-de-revente',
    bloc: 'rejet',
    refRapport: 'Proposition p. 34-37 (rejet 3/3)',
    titre: 'Le coefficient de revente jugé trop bas',
    griefFisc: 'Le coefficient de revente déclaré (≈ 2,30) serait « manifestement très bas et hors des usages de la profession » (≈ 3+), révélant une minoration.',
    reponseCourte:
      'Sur l’alcool réellement revendu, le coefficient atteint × 3,85 (au-dessus du seuil profession) ; produit par produit, la marge est normale (× 3 à × 5). Le coefficient apparent bas vient des 36 % d’alcool jamais revendu (cuisine, sur-versement, pertes) et non d’une recette cachée.',
    statut: 'demonte',
    sections: RFCoefficients.sections as unknown as Section[],
  },
  // ---- BLOC 2 : RECONSTITUTION DU CA ----
  {
    slug: 'reconstitution-volumes-liquides',
    bloc: 'reconstitution',
    refRapport: 'Proposition p. 37-53 (méthode) — annexes Boissons',
    titre: 'Reconstitution du CA par les volumes de liquides',
    griefFisc:
      'À partir des achats de boissons et de doses standard, le service reconstitue un CA « liquides » puis l’extrapole à la cuisine (× coefficient), d’où une minoration alléguée.',
    reponseCourte:
      'Recalculé sur les achats et la caisse réels, le manquant retombe à la perte normale d’un bar ; en réinjectant les vraies ventes dans la formule du fisc, la discordance s’inverse.',
    enjeu: 'Cœur de la reconstitution : ≈ 422 k€ de CA HT redressé (3 ans), amende 1759 ≈ 472 k€',
    statut: 'partiel',
    sections: RFReconstitution.sections as unknown as Section[],
  },
  {
    slug: 'sur-versement-au-verre',
    bloc: 'reconstitution',
    refRapport: 'Proposition p. 37-44 (méthode 1/2) — doses au verre',
    titre: 'Sur-versement au verre',
    griefFisc: 'La méthode retient des doses théoriques exactes, sans tenir compte du sur-versement réel.',
    reponseCourte:
      'Sans doseur, le verre de vin servi à la main dépasse la dose, aux taux mesurés par la littérature : vin +23,6 % et cocktails +42 % (Kerr 2008), spiritueux +20 % (Wansink, BMJ 2005). Le pichet (rempli au contenant, pré-mesuré) est exclu par prudence : il reste 720 L d’alcool consommé et jamais vendu sur 3 ans.',
    statut: 'partiel',
    sections: RFSurversement.sections as unknown as Section[],
  },
  {
    slug: 'pertes-biere-mousse',
    bloc: 'reconstitution',
    refRapport: 'Proposition p. 44-53 (méthode 2/2) — pertes',
    titre: 'Pertes de bière (mousse et tirage)',
    griefFisc: 'La reconstitution ignore les pertes de bière pression (mousse, fonds de fût, rinçage).',
    reponseCourte:
      'La freinte technique du fût (mousse, purge, fond de fût, nettoyage des lignes) est documentée à 5–20 % (rendement-fût ~95 %). Sur 1 293 L tirés, le mode CHR de 10 % fait 129 L : l’abattement de 15 % que le fisc applique lui-même à la bière est juste, pas généreux.',
    statut: 'partiel',
    sections: RFBiereMousse.sections as unknown as Section[],
  },
  {
    slug: 'pertes-cremant',
    bloc: 'reconstitution',
    refRapport: 'Proposition p. 44-53 (méthode 2/2) — pertes',
    titre: 'Pertes de crémant (bouteilles ouvertes non terminées)',
    griefFisc: 'Le crémant acheté est supposé intégralement vendu au verre.',
    reponseCourte:
      'Deux pertes distinctes, calculées jour par jour sur les tickets (annexe C, verre + cocktails) : le crémant sur-versé (+23,6 %) = 87 L, et la bouteille éventée jetée chaque soir = 260 L. Au total 347 L de crémant qui ne produit aucune vente — que la reconstitution compte pourtant comme vendu.',
    statut: 'partiel',
    sections: RFCremant.sections as unknown as Section[],
  },
  {
    slug: 'degustation-au-verre',
    bloc: 'reconstitution',
    refRapport: 'Proposition p. 37-44 (méthode 1/2)',
    titre: 'Dégustation offerte (goûter du vin)',
    griefFisc: 'Tout le vin acheté est supposé vendu.',
    reponseCourte:
      'Compté note par note dans le détail des tickets (annexe C) : 2 cl offerts une fois par vin nommé et par note, soit 6 590 dégustations = 132 L de vin offert et jamais vendu sur 3 ans, verre de Saint Joseph compris ; 103 L une fois retirés les vins servis en cubi et les bouteilles vendues entières. Chiffre lu dans la caisse, pratique attestée par la gérante (attestation n° 147).',
    statut: 'partiel',
    sections: RFDegustation.sections as unknown as Section[],
  },
  {
    slug: 'alcool-cuisine-doses-plats',
    bloc: 'reconstitution',
    refRapport: 'Proposition p. 37-44 — repères cuisine et menus',
    titre: 'Alcool incorporé en cuisine et dans les menus (doses des plats)',
    griefFisc: 'La part d’alcool partant en cuisine (sauces, flambages, desserts) et dans les plats des menus est sous-évaluée par le service.',
    reponseCourte:
      'En appliquant les doses confirmées par les dirigeants (celles que le fisc reprend) à toute la carte, la cuisine à la carte consomme 566 L et les menus 228 L de plus (pondérés par la probabilité de choix, plat par plat) : 794 L d’alcool acheté qui part dans les plats, jamais dans un verre vendu.',
    statut: 'partiel',
    sections: RFCuisine.sections as unknown as Section[],
  },
  {
    slug: 'offerts-remises-pertes',
    bloc: 'reconstitution',
    refRapport: 'Proposition p. 44-48 (méthode 2/2)',
    titre: 'Offerts, remises et pertes (taux retenus)',
    griefFisc: 'Le service applique des abattements minimaux (pertes 5 %, personnel 5 %, 15 % sur la pression).',
    reponseCourte:
      'Les forfaits de 5 %+5 %+5 % sont des planchers : itemisée, la consommation sans vente (chef, offerts, sur-versement, crémant, dégustation, freinte bière) dépasse 1 000 L hors cuisine/menus, et la perte d’exploitation totale (28,7 %) dépasse les 22 % validés par la CAA Paris (17/03/2021).',
    statut: 'partiel',
    sections: RFOfferts.sections as unknown as Section[],
  },
  {
    slug: 'coefficient-liquide-solide',
    bloc: 'reconstitution',
    refRapport: 'Proposition p. 44-53 (méthode 2/2)',
    titre: 'Extrapolation de la cuisine (coefficient liquide → solide)',
    griefFisc: 'Le CA « solides » (cuisine) est obtenu en multipliant le CA liquides reconstitué par un coefficient.',
    reponseCourte:
      'La cuisine n’est jamais mesurée : le CA solides = CA liquides × 2,94 / 3,02 / 3,10. Le coefficient est une loupe qui multiplie ~3 fois toute sur-évaluation des liquides ; corrigés, les volumes font passer le total reconstitué sous le CA déclaré.',
    statut: 'partiel',
    sections: RFCoefficient.sections as unknown as Section[],
  },
  // ---- BLOC 3 : RAPPELS ----
  {
    slug: 'rappels-tva',
    bloc: 'rappels',
    refRapport: 'Proposition p. 53-66 (rappels)',
    titre: 'Rappels de TVA collectée',
    griefFisc: 'La TVA est rappelée sur le CA reconstitué (≈ 49 547 € de droits).',
    reponseCourte: 'Le rappel s’effondre avec la reconstitution dont il dépend : pas de CA minoré, pas de TVA rappelée.',
    enjeu: '≈ 71 973 € (droits + majorations)',
    statut: 'partiel',
    sections: enChantier('Montrer que le rappel de TVA est purement dérivé de la reconstitution réfutée au bloc 2.'),
  },
  {
    slug: 'rappels-is',
    bloc: 'rappels',
    refRapport: 'Proposition p. 53-66 (rappels)',
    titre: 'Rappels d’impôt sur les sociétés',
    griefFisc: 'L’IS est rappelé sur le bénéfice reconstitué (≈ 97 510 € de droits).',
    reponseCourte: 'Même dépendance : sans minoration de recettes établie, la base IS rectifiée disparaît.',
    enjeu: '≈ 141 175 € (droits + majorations)',
    statut: 'partiel',
    sections: enChantier('Lier la chute du rappel IS à la réfutation de la reconstitution et au CA déclaré confirmé.'),
  },
  {
    slug: 'profit-sur-le-tresor',
    bloc: 'rappels',
    refRapport: 'Proposition p. 53-66 — art. L-77 LPF',
    titre: 'Profit sur le trésor',
    griefFisc: 'Le service applique la cascade « profit sur le trésor » sur les rappels.',
    reponseCourte: 'Mécanisme accessoire aux rappels : il tombe avec eux.',
    statut: 'partiel',
    sections: enChantier('Rappeler le caractère purement accessoire du profit sur le trésor.'),
  },
  // ---- BLOC 4 : SANCTIONS ----
  {
    slug: 'majoration-40-manquement-delibere',
    bloc: 'sanctions',
    refRapport: 'Proposition p. 53-66 — art. 1729 CGI',
    titre: 'Majoration de 40 % (manquement délibéré)',
    griefFisc: 'La majoration de 40 % suppose un manquement délibéré.',
    reponseCourte:
      'Le caractère délibéré n’est pas établi : la comptabilité est cohérente (CA = encaissements), les écarts relèvent de l’exploitation, pas d’une intention de dissimuler.',
    statut: 'partiel',
    sections: enChantier(
      'Contester l’intention : démontrer la sincérité (CA = encaissements, bancarisation 98,7 %) pour écarter le manquement délibéré.',
    ),
  },
  {
    slug: 'amende-1759-distributions',
    bloc: 'sanctions',
    refRapport: 'Proposition p. 53-66 — art. 1759 (116/117 CGI)',
    titre: 'Amende de 100 % sur distributions présumées',
    griefFisc:
      'Faute de désignation des bénéficiaires des recettes présumées distribuées, l’administration applique une amende de 100 % (≈ 471 826 €).',
    reponseCourte:
      'Sans recettes occultées établies, il n’y a pas de distribution : l’amende, qui représente l’essentiel de l’enjeu, est sans objet.',
    enjeu: '≈ 471 826 € — le plus gros poste',
    statut: 'partiel',
    sections: enChantier(
      'Rappeler que l’amende 1759 présuppose des distributions ; sans CA minoré établi, sa base disparaît. Traiter aussi le délai de désignation (art. 117).',
    ),
  },
  {
    slug: 'interets-de-retard',
    bloc: 'sanctions',
    refRapport: 'Proposition p. 53-66 — art. 1727 CGI',
    titre: 'Intérêts de retard',
    griefFisc: 'Des intérêts de retard sont appliqués aux droits rappelés.',
    reponseCourte: 'Accessoires aux rappels : ils suivent leur sort.',
    statut: 'partiel',
    sections: enChantier('Caractère accessoire des intérêts de retard.'),
  },
]

export const griefs: Grief[] = [...autresGriefs]

export function griefParSlug(slug: string): Grief | undefined {
  return griefs.find((g) => g.slug === slug)
}

export function griefsParBloc(bloc: BlocId): Grief[] {
  return griefs.filter((g) => g.bloc === bloc)
}
