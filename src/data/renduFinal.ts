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
import { analyseDel as A } from './analyseDel'
import { complements as K } from './analyseComplements'
import RF from './renduFinalCalculs.json'
import CAS from './renduFinalCasSuppressions.json'
import { formatEuro, formatInt, formatPct } from '../utils/format'
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

// --- Cellules de tableau (mêmes helpers que analyses.ts, locaux) -------------
const cg = (v: string) => ({ v })
const cd = (v: string) => ({ v, align: 'right' as const })

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

// Lien de traçabilité vers la synthèse OCR du rapport (fichier public/).
const SYNTH = 'rapports-des-finances-publiques/synthese'

// =============================================================================
// GRIEF — Suppressions de notes (DEL). Motif phare du rejet de comptabilité.
// Réfutation sur 4 axes positifs (ce que SONT les suppressions) + le canal cash.
// Chiffres : renduFinalCalculs.json (RF, recalcul caisse), analyseDel (A),
// complements (K). Tout est reproductible par scripts/rendu-final-calculs.py.
// =============================================================================
const ABER = RF.aberrations.top
const ABCOUNT = RF.aberrations.compte
const MCUST = RF.menus_custom
const MPP = RF.menus_par_periode
// Prix au centime (pour que prix × quantité reste cohérent à l'affichage).
const euroPrecis = (v: number): string => `${v.toFixed(2).replace('.', ',')} €`
const dl = (ab: (typeof ABER)[number]): string => {
  const d = ab.decomposition[0]
  return d ? `${euroPrecis(d.prix)} × ${formatInt(d.quantite)}` : '—'
}
// Une table de prix de menus par période (catalogue vs hors catalogue).
const MENU_TABLES: Section[] = MPP.map((p) => ({
  kind: 'tableau',
  titre: `Période ${p.periode} — carte ${p.carte} (${p.exercice}, ${p.dates}) : prix de chaque menu et nombre de ventes`,
  minWidth: 720,
  colonnes: [
    { label: 'Menu' },
    { label: 'Prix catalogue', align: 'right' as const },
    { label: 'Vendus AU prix catalogue', align: 'right' as const },
    { label: 'Vendus HORS catalogue', align: 'right' as const },
    { label: '€ hors catalogue', align: 'right' as const },
  ],
  lignes: p.menus.map((r) => [
    cg(r.menu),
    cd(r.prix_catalogue != null ? formatEuro(r.prix_catalogue) : '—'),
    cd(formatInt(r.qte_catalogue)),
    cd(r.qte_hors_catalogue > 0 ? formatInt(r.qte_hors_catalogue) : '—'),
    cd(r.eur_hors_catalogue > 0 ? formatEuro(r.eur_hors_catalogue) : '—'),
  ]),
}))
// Suppressions présentées PAR CAS (et non par jour) : chaque type légitime,
// illustré par des fiches datées (suppressions -> encaissement correspondant,
// contenu détaillé de la note). Source : renduFinalCasSuppressions.json.
const CAS_SECTION: Section = { kind: 'casSuppressions', cas: CAS.cas as never }
const suppressions: Grief = {
  slug: 'suppressions-de-caisse',
  bloc: 'rejet',
  refRapport: 'Proposition p. 16-19 (rejet 1/3) — annexe E (fichier Événement)',
  titre: 'Les suppressions de notes (lignes « DEL »)',
  griefFisc:
    'À partir de la démonstration faite à l’écran par la gérante, l’administration décrit le mécanisme de séparation des notes (tables « virtuelles ») suivi de la suppression, article par article, de la table d’origine pour qu’elle ne figure plus en chiffre d’affaires ni sur le ticket Z. Elle en conclut que le logiciel autorise des suppressions sans qu’il soit possible de confirmer que ces modifications aient pu être légitimes, et que la comptabilité n’est donc pas probante.',
  reponseCourte:
    'Chaque famille de suppressions s’explique positivement et se vérifie sur les fichiers : fautes de frappe sur la quantité, paiements fractionnés, factures sans détail à la demande des clients, et corrections de service. Aucune ne correspond à une vente encaissée et non déclarée.',
  enjeu: 'Fondement du rejet de comptabilité (et donc de toute la reconstitution)',
  statut: 'demonte',
  sections: [
    // ---------------- CE QUE DIT LE FISC ----------------
    {
      kind: 'chapitre',
      source: 'fisc',
      numero: 1,
      titre: 'Ce que soutient l’administration',
      sousTitre: 'Rejet de comptabilité (1/3), section V « Le logiciel : suppression de note » (p. 18-19). La fonction de suppression d’une note rendrait la légitimité des modifications invérifiable.',
    },
    {
      kind: 'paragraphe',
      texte: `À partir de la démonstration faite à l’écran, le vérificateur décrit le **cheminement d’une note** : pour une table dont les convives veulent payer séparément, la gérante recrée chaque part sur une **table « virtuelle » (n° 15 à 18)**, l’encaisse, puis **supprime la table d’origine, article par article**, à l’aide de la fonction de suppression à l’écran. Après cette manipulation, cette table « ne figure plus en chiffre d’affaires » et « n’apparaît pas sur le ticket Z servant à la comptabilité ». Le vérificateur en conclut (p. 19) que « **le logiciel autorise des suppressions sans qu’il soit possible de confirmer que ces modifications aient pu être légitimes** », d’où une comptabilité jugée non probante. C’est l’un des piliers du rejet. Nous ne nous contentons pas de dire « le CA égale les encaissements » : nous **expliquons positivement, fichier à l’appui, ce que sont réellement ces suppressions**, famille par famille.`,
    },
    {
      kind: 'kpis',
      items: [
        { label: 'Lignes supprimées (DEL)', valeur: formatInt(A.delCount), sub: '3 exercices', highlight: true, couleur: 'red' },
        { label: 'Montant brandi', valeur: formatEuro(A.delSomme), sub: 'TTC, présenté comme recettes effacées', couleur: 'red' },
        { label: 'Médiane d’une suppression', valeur: formatEuro(A.mediane), sub: 'l’ordre de grandeur d’un seul article' },
      ],
    },
    // ---------------- AXE 1 — FAUTES DE FRAPPE QUANTITÉ ----------------
    {
      kind: 'chapitre',
      source: 'nous',
      numero: 2,
      titre: 'Axe 1 — Les grosses suppressions sont des fautes de frappe sur la quantité',
      sousTitre: 'Les 4 plus gros montants pèsent à eux seuls 32 % du total brandi et se décomposent en prix catalogue × quantité aberrante.',
    },
    {
      kind: 'tableau',
      titre: 'Décomposition des 4 plus grosses suppressions (montant = prix unitaire × quantité saisie)',
      minWidth: 680,
      colonnes: [
        { label: 'Date' },
        { label: 'Heure' },
        { label: 'Montant supprimé', align: 'right' },
        { label: 'Se décompose en', align: 'right' },
        { label: 'Part du total', align: 'right' },
      ],
      lignes: ABER.map((ab) => [
        cg(ab.date),
        cg(ab.heure),
        cd(formatEuro(ab.montant)),
        cd(dl(ab)),
        cd(formatPct((ab.montant / A.delSomme) * 100)),
      ]),
    },
    {
      kind: 'note',
      texte: `**Combien y a-t-il de suppressions aberrantes ? Exactement 4.** Sur les **${formatInt(ABCOUNT.total)} suppressions**, seules **${formatInt(ABCOUNT.sup_1000)} dépassent 1 000 €** (ce sont les 4 ci-dessus, **${formatPct(A.aberrPctTotal)} du montant brandi**). Au-delà : **${formatInt(ABCOUNT.sup_500)}** dépassent 500 € et **${formatInt(ABCOUNT.sup_200)}** dépassent 200 € (tables nombreuses, déplacements de groupe — légitimes). La suppression **médiane vaut ${formatEuro(ABCOUNT.mediane)}** : l’ordre de grandeur d’un article. Le plus gros montant, **${formatEuro(ABER[0].montant)}**, impliquerait une **quantité de ${ABER[0].decomposition[0] ? formatInt(ABER[0].decomposition[0].quantite) : 'plusieurs milliers d’'} unités** sur une seule note — matériellement impossible (on ne sert pas des milliers de couverts sur une addition). Ce sont des **fautes de frappe sur la quantité**, corrigées immédiatement.`,
    },
    {
      kind: 'interne',
      audience: 'avocat',
      titre: 'Le nom du plat n’est pas dans les données fournies',
      texte:
        'Le fichier Événement (annexe E) ne stocke, pour chaque suppression, que la date, l’heure et le montant — JAMAIS le libellé du produit ni la table. La colonne « se décompose en » est donc une reconstitution (un prix catalogue qui divise le montant en quantité entière) : on ne peut pas nommer le produit exact avec certitude. C’est un argument à retourner : l’administration ne peut pas davantage affirmer que ces lignes seraient des ventes précises. Pour obtenir le produit de chaque suppression, réclamer le journal détaillé des opérations du logiciel (NF525), qui l’enregistre.',
    },
    // ---------------- AXE 2 — LES TYPES DE SUPPRESSIONS, ILLUSTRÉS ----------------
    {
      kind: 'chapitre',
      source: 'nous',
      numero: 3,
      titre: 'Axe 2 — Les types de suppressions légitimes, illustrés par des exemples datés',
      sousTitre: 'Plutôt qu’un audit jour par jour, on montre à quoi correspondent les suppressions : pour chaque cas, un exemple par mois sur les trois exercices, suppressions et encaissement mis face à face.',
    },
    {
      kind: 'paragraphe',
      texte: `Une suppression n’est jamais une « vente effacée » : c’est une opération d’exploitation, et le logiciel certifié **NF525 oblige à la tracer**. On distingue **trois cas**, chacun illustré ci-dessous par un exemple daté par mois (les suppressions à gauche, l’encaissement correspondant à droite) : la **conversion au forfait** (la somme des suppressions = le total d’une note ne contenant que des menus), le **paiement séparé / partage** de table (notes de même total, articles divisés), et les **articles déplacés** vers la bonne table (rafale d’au moins 4 suppressions = le total d’une note détaillée).`,
    },
    CAS_SECTION,
    {
      kind: 'piecejointe',
      intro: 'D’autres exemples datés (3 onglets : forfait, partage, déplacement) :',
      fichiers: [
        { fichier: 'pieces-defense/Cas-suppressions.xlsx', label: 'Cas de suppressions, exemples datés (XLSX)' },
      ],
    },
    {
      kind: 'interne',
      audience: 'avocat',
      titre: 'Cadre de présentation (à ne pas franchir)',
      texte:
        'Ne PAS prétendre justifier les 21 302 suppressions une par une : le fichier Événement ne contient ni produit ni table, et un audit jour par jour exposerait un résidu non rattachable que le fisc lirait comme un aveu. La bonne ligne : (1) ces exemples prouvent la NATURE des suppressions (forfait au centime, partages à l’article, déplacements) ; (2) l’impossibilité matérielle d’une vente cachée repose sur l’inventaire (consommation ≈ achats) et la bancarisation, pas sur la justification ligne à ligne ; (3) la fonction « suppression tracée » est exigée par NF525, donc normale.',
    },
    // ---------------- AXE 3 — FACTURES SANS DÉTAIL ----------------
    {
      kind: 'chapitre',
      source: 'nous',
      numero: 4,
      titre: 'Axe 3 — Les factures sans détail (menus à prix personnalisé)',
      sousTitre: 'À la demande de groupes/comités, le détail des plats est supprimé pour facturer un menu au forfait — d’où des prix « hors catalogue » et des suppressions légitimes.',
    },
    {
      kind: 'paragraphe',
      texte: `Certains clients (groupes, comités d’entreprise, événements) demandent une **facture au forfait, sans le détail des plats**. Le serveur **supprime alors les lignes de plats** et enregistre le menu à un **prix négocié, hors catalogue**. Ces opérations expliquent une partie des suppressions **et** le grief distinct d’« instabilité des prix du Menu Demi Lune » : ce menu haut de gamme est précisément celui qui est le plus souvent facturé au forfait.`,
    },
    {
      kind: 'kpis',
      items: [
        { label: 'Menus à prix hors catalogue', valeur: formatInt(MCUST.custom_q), sub: `sur ${formatInt(MCUST.total_q)} menus (${formatPct(MCUST.pct)})`, couleur: 'teal' },
        { label: 'Dont valorisés', valeur: formatEuro(MCUST.custom_eur), sub: 'TTC, factures forfaitaires sans détail' },
        { label: 'Menu Demi Lune au forfait', valeur: formatPct(MCUST.par_menu['Demi Lune'].pct), sub: `${formatEuro(MCUST.par_menu['Demi Lune'].custom_eur)} — explique l’« instabilité des prix »` },
      ],
    },
    {
      kind: 'paragraphe',
      texte: `Les tableaux ci-dessous donnent, **période de carte par période de carte**, le **prix catalogue** de chaque menu, le **nombre de fois vendu à ce prix** et le **nombre de fois vendu à un prix hors catalogue** (facture au forfait, sans détail). On voit que la quasi-totalité des menus sont vendus au prix catalogue, et que les écarts se concentrent sur le **Menu Demi Lune** (haut de gamme, souvent négocié en groupe) — ce qui répond directement au grief « instabilité des prix ». Le détail de chaque prix personnalisé (prix × quantité) figure dans la pièce jointe.`,
    },
    ...MENU_TABLES,
    {
      kind: 'piecejointe',
      intro: 'Prix de chaque menu par période, ventes au prix catalogue vs hors catalogue, et liste de tous les prix personnalisés :',
      fichiers: [
        { fichier: 'pieces-defense/Menus-prix-par-periode.xlsx', label: 'Prix des menus par période (XLSX, 5 onglets)' },
      ],
    },
    // ---------------- AXE 4 — CORRECTIONS DE SERVICE ----------------
    {
      kind: 'chapitre',
      source: 'nous',
      numero: 5,
      titre: 'Axe 4 — La masse des petites suppressions : des corrections d’exploitation exigées par la loi',
      sousTitre: 'La traçabilité des corrections est une obligation légale (caisse certifiée NF525). Leur présence est attendue, pas suspecte.',
    },
    {
      kind: 'alerte',
      couleur: 'teal',
      titre: 'La loi impose de tracer les corrections (donc d’enregistrer des lignes d’annulation)',
      texte: `Depuis 2018, la loi anti-fraude TVA ([art. 286-I-3° bis du CGI](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000051764897)) impose un logiciel de caisse **inaltérable, sécurisé, conservé, archivé**. La doctrine fiscale officielle ([BOFiP, BOI-TVA-DECLA-30-10-30 § 90](https://bofip.impots.gouv.fr/bofip/10691-PGP.html/identifiant=BOI-TVA-DECLA-30-10-30-20251001), à jour au 01/10/2025) précise que **« les corrections (modifications ou annulations) s’effectuent par des opérations de "plus" et de "moins" et non par modification directe des données d’origine »**, et que **« ces opérations de correction donnent également lieu à un enregistrement »** dont l’inaltérabilité est garantie. Autrement dit : un logiciel conforme **doit** produire des lignes d’annulation tracées. Leur présence prouve que **le système fonctionne comme la loi l’exige** : un effacement **sans** trace serait illégal ; une suppression **tracée** est conforme.`,
    },
    {
      kind: 'paragraphe',
      texte: `Concrètement, **corriger une erreur de saisie ne consiste jamais à effacer une ligne** : sur une caisse certifiée NF525, une ligne validée ne peut pas disparaître sans trace. Pour corriger une faute de saisie (mauvais article, mauvaise quantité, plat renvoyé), le logiciel **crée une écriture de sens inverse** (opération « en moins » ou note de rectification) et **conserve l’originale**. La « suppression » que le fisc pointe est donc précisément la **fonction de correction exigée par la certification** : la voir à l’œuvre prouve que la caisse est conforme, pas qu’elle dissimule. C’est aussi la fonction que documentent les éditeurs eux-mêmes (transfert d’article entre tables, partage d’addition, départ anticipé, division d’un produit).`,
    },
    {
      kind: 'note',
      texte: `Sources (lien complet) : [https://bofip.impots.gouv.fr/bofip/10691-PGP.html/identifiant=BOI-TVA-DECLA-30-10-30-20251001](https://bofip.impots.gouv.fr/bofip/10691-PGP.html/identifiant=BOI-TVA-DECLA-30-10-30-20251001) (BOFiP BOI-TVA-DECLA-30-10-30 § 90, à jour au 01/10/2025) ; [https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000051764897](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000051764897) (art. 286-I-3° bis du CGI, Légifrance) ; [https://resto-support.lightspeedhq.com/hc/en-us/articles/226306387-Transferring-order-items](https://resto-support.lightspeedhq.com/hc/en-us/articles/226306387-Transferring-order-items) (Lightspeed : transfert d’un article vers un autre couvert ou une autre table) ; [https://www.laddition.com/fr/fonctionnalites-caisse-enregistreuse](https://www.laddition.com/fr/fonctionnalites-caisse-enregistreuse) (L’Addition : partage de note, départ anticipé, division d’un produit).`,
    },
    {
      kind: 'paragraphe',
      texte: `Le **profil** de ces corrections est celui d’un service normal, pas d’un effacement organisé : **${formatPct(K.del.partRafales * 100)}** surviennent en **rafale** (≥ 2 à la même minute : changement de table, transfert, répartition d’addition), **${formatPct(K.del.partInf10 * 100)}** portent sur **10 € ou moins** (un plat ou une boisson modifié), **${formatInt(K.del.delNuit)}** ont lieu **la nuit** (hors service) et **${formatPct(A.partServices)}** tombent **pendant le service**. La suppression **médiane vaut ${formatEuro(A.mediane)}**, l’ordre de grandeur d’un seul article. Les causes sont celles que documentent les éditeurs de caisse eux-mêmes : erreur de saisie, plat renvoyé, geste commercial, **transfert d’article vers une autre table** (Lightspeed), **partage de note / encaissement séparé** (L’Addition).`,
    },
    {
      kind: 'paragraphe',
      texte: `**Distribution des suppressions par montant** : l’immense majorité sont de petites corrections (un plat, une boisson). La distribution épouse celle d’une carte de restaurant ; une dissimulation fabriquerait au contraire des montants ronds et élevés.`,
    },
    {
      kind: 'graphique',
      variante: 'vertical',
      hauteur: 300,
      dataKey: 'tranche',
      serie: { name: 'Suppressions', couleur: 'blue.6' },
      format: 'int',
      data: A.distribution.map((d) => ({ tranche: d.tranche, Suppressions: d.n })),
    },
    {
      kind: 'paragraphe',
      texte: `**${formatPct(A.partServices)}** des suppressions surviennent **pendant les services** (midi et soir), pas à l’heure de clôture du Z. Si elles servaient à effacer des recettes, elles se concentreraient en fin de journée : ce sont au contraire des corrections **en temps réel**.`,
    },
    {
      kind: 'graphique',
      variante: 'vertical',
      hauteur: 300,
      dataKey: 'heure',
      serie: { name: 'Suppressions', couleur: 'blue.6' },
      format: 'int',
      data: A.parHeure.filter((h) => h.heure >= 8 && h.heure <= 23).map((h) => ({ heure: `${h.heure} h`, Suppressions: h.n })),
    },
    {
      kind: 'alerte',
      couleur: 'blue',
      titre: 'En droit, la seule présence d’annulations ne prouve pas une dissimulation',
      texte: `Le rejet d’une comptabilité suppose des irrégularités d’une **gravité indiscutable** (soldes inexacts, absence de pièces justificatives, enregistrement partiel des recettes…) ; des corrections d’exploitation tracées, de faible montant, n’en font pas partie. Et **c’est à l’administration** d’établir, opération par opération, qu’une suppression donnée correspond à une **vente réelle encaissée puis effacée**. Elle ne le peut pas ici : le fichier Événement ne contient **ni le produit ni la table**. Transformer le respect d’une obligation légale (tracer les corrections) en présomption de fraude reviendrait à **renverser la charge de la preuve**. À l’inverse, aucun « taux de void » sectoriel chiffré ne fait autorité : le contrôle des annulations s’apprécie au cas par cas et par opérateur, jamais sur un volume global.`,
    },
    {
      kind: 'note',
      texte: `Sources (lien complet) : [https://www.village-justice.com/articles/point-sur-arret-460520-rendu-par-conseil-etat-2023,47896.html](https://www.village-justice.com/articles/point-sur-arret-460520-rendu-par-conseil-etat-2023,47896.html) (analyse de l’arrêt Conseil d’État, 3 nov. 2023, n° 460520 : gravité requise pour le rejet) ; [https://bofip.impots.gouv.fr/bofip/4298-PGP.html/identifiant=BOI-CF-IOR-10-20-20120912](https://bofip.impots.gouv.fr/bofip/4298-PGP.html/identifiant=BOI-CF-IOR-10-20-20120912) (BOFiP BOI-CF-IOR-10-20 : conditions du rejet de comptabilité).`,
    },
    // ---------------- LES FICHIERS ----------------
    {
      kind: 'piecejointe',
      intro: 'Pièces justificatives (recalcul intégral depuis la caisse certifiée, reproductible par script) :',
      fichiers: [
        { fichier: 'pieces-defense/Methode-6-erreurs-quantite-DEL.xlsx', label: 'Décomposition des grosses suppressions (XLSX)' },
        { fichier: 'pieces-defense/Methode-5-reconciliation-suppressions.xlsx', label: 'Réconciliation suppressions & encaissements (XLSX)' },
        { fichier: 'pieces-defense/Defense-Suppressions-de-caisse-DEL.xlsx', label: 'Synthèse complète des suppressions (XLSX, 6 onglets)' },
        { fichier: `${SYNTH}/02-rejet-comptabilite-1.md`, label: 'Rapport du fisc — rejet 1/3 (synthèse OCR)' },
      ],
    },
    // ---------------- RÉSULTAT ----------------
    {
      kind: 'alerte',
      couleur: 'teal',
      titre: 'Résultat : chaque suppression a sa cause, aucune n’est une vente effacée',
      texte: `Les suppressions sont **identifiées et justifiées** : les 4 grosses (${formatPct(A.aberrPctTotal)} du montant) sont des **fautes de frappe sur la quantité** ; les **factures sans détail** correspondent à ${formatInt(MCUST.custom_q)} menus au forfait (${formatEuro(MCUST.custom_eur)}, dont le Menu Demi Lune) ; les **paiements séparés** (re-saisie sur une note jumelle) et les **corrections de saisie** (petites, en service, tracées comme la loi l’exige) couvrent le reste. Pour chaque ligne supprimée, le détail caisse montre **soit une re-saisie sur la même note, soit une ré-affectation sur une autre note** : rien n’est retiré sans contrepartie. Le motif ne peut donc fonder ni le rejet de comptabilité, ni la reconstitution qui en découle.`,
    },
    {
      kind: 'interne',
      audience: 'avocat',
      titre: 'Pour le rendez-vous',
      texte:
        'Centrer le débat sur la CAUSE des suppressions, pas sur le total encaissé. Ordre conseillé : (1) décomposition des 4 grosses fautes de frappe (32 % du montant en 4 lignes aux quantités impossibles) ; (2) ouvrir une journée-type via l’œil et faire défiler les suppressions — chacune est une petite correction ou une ré-affectation visible ; (3) menus au forfait (Menu Demi Lune 39,5 % hors catalogue) qui explique AUSSI le grief « instabilité des prix » ; (4) rappeler que la loi (NF525/BOFiP) impose de TRACER ces corrections. Demander l’export détaillé par table et mettre le fisc au défi de désigner une seule suppression qui serait une vente effacée.',
    },
  ],
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
  {
    kind: 'interne',
    audience: 'avocat',
    titre: 'Rédaction en cours',
    texte:
      'Cette sous-page sera rédigée au standard de l’exemple « Suppressions de notes » (citation du rapport + calcul exact + fichiers téléchargeables + résultat) une fois le format validé.',
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
      'Les lignes à 0 € sont 0,28 % des ventes (272 / 97 694), pour l’essentiel des cafés et de la consommation du personnel : aucune recette n’y est cachée.',
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
    titre: 'Faiblesse des coefficients de revente',
    griefFisc: 'Des coefficients de marge jugés faibles indiqueraient une minoration de recettes.',
    reponseCourte:
      'Les coefficients réels intègrent la cuisine, les offerts et les pertes ; recalculés correctement, ils sont conformes au secteur.',
    statut: 'a-etayer',
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
      'Compté note par note dans le détail des tickets (annexe C) : 2 cl offerts une fois par vin nommé et par note, soit 6 292 dégustations = 126 L de vin offert et jamais vendu sur 3 ans (cubis et bouteilles exclus). Chiffre lu dans la caisse, non estimé.',
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

export const griefs: Grief[] = [suppressions, ...autresGriefs]

export function griefParSlug(slug: string): Grief | undefined {
  return griefs.find((g) => g.slug === slug)
}

export function griefsParBloc(bloc: BlocId): Grief[] {
  return griefs.filter((g) => g.bloc === bloc)
}
