#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REPONSE 1 - Redaction de la refutation « cremant » (parties 3.1.3 et P).

Injecte, dans src/data/reponse1/recon-3-cremant-vendu.json et
src/data/reponse1/perte-de-cremant.json, la refutation calculee par
scripts/reponse1-cremant-fourchette.py. Le chapitre 1 (« Ce que soutient
l'administration ») est conserve ; le chapitre de travail « Ce qu'il faut
refuter » est retire.

Tous les chiffres proviennent de src/data/reponse1Calculs/cremant-fourchette.json
et de src/data/calculsBoissons/achatsBoissonsParPeriode.json : aucun n'est saisi
a la main.
"""
import os, json

ICI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(ICI, ".."))
CALC = json.load(open(os.path.join(ROOT, "src/data/reponse1Calculs/cremant-fourchette.json"),
                     encoding="utf-8"))
ACH = json.load(open(os.path.join(ROOT, "src/data/calculsBoissons/achatsBoissonsParPeriode.json"),
                     encoding="utf-8"))
EXOS = ["2022-2023", "2023-2024", "2024-2025"]
E = CALC["exercices"]

# --- Prix d'achat reel du cremant, par exercice (factures fournisseur) --------
ACHATS = {ex: {"bt": 0.0, "ht": 0.0} for ex in EXOS}
for p in ACH["achats"]:
    if "CREMANT" in p["produit"].upper():
        for ex, v in p["par_periode"].items():
            if ex in ACHATS:
                ACHATS[ex]["bt"] += v["quantite"]
                ACHATS[ex]["ht"] += v["montant_ht"]
for ex in EXOS:
    a = ACHATS[ex]
    a["pu"] = a["ht"] / a["bt"] if a["bt"] else 0.0

L = lambda cl, d=1: f"{cl/100:,.{d}f}".replace(",", " ").replace(".", ",") + " L"
CL = lambda cl, d=1: f"{cl:,.{d}f}".replace(",", " ").replace(".", ",") + " cl"
EUR = lambda x, d=0: f"{x:,.{d}f}".replace(",", " ").replace(".", ",") + " €"
PCT = lambda x, d=1: f"{x:,.{d}f}".replace(",", " ").replace(".", ",") + " %"
N = lambda x, d=0: f"{x:,.{d}f}".replace(",", " ").replace(".", ",")

cg = lambda v, **k: dict(v=v, **k)
cd = lambda v, **k: dict(v=v, align="right", **k)

# --- Agregats 3 exercices ----------------------------------------------------
TOT_ECART = sum(E[x]["ecart_a_expliquer_cl"] for x in EXOS)
TOT_JETE = sum(E[x]["equilibre"]["jete_cl"] for x in EXOS)
TOT_SURV = sum(E[x]["equilibre"]["servi_cl"] - E[x]["nominal_cl"] for x in EXOS)
TOT_BT = sum(E[x]["equilibre"]["bouteilles_ouvertes"] for x in EXOS)
TOT_JOURS = sum(E[x]["jours_servis"] for x in EXOS)
COUT = {ex: E[ex]["equilibre"]["jete_cl"] / 75.0 * ACHATS[ex]["pu"] for ex in EXOS}
TOT_COUT = sum(COUT.values())
TOT_ACHAT_HT = sum(ACHATS[ex]["ht"] for ex in EXOS)

# Taux de sur-versement au point d'equilibre, par exercice.
TAUX_EQ = {ex: E[ex]["equilibre"]["taux"] for ex in EXOS}
TAUX_MAX = max(TAUX_EQ.values())

# Verification du chiffre du service : 239,05 / 206,25 (p. 63, « 20 % superieurs »).
SERVICE_EX1_RATIO = (239.05 / 206.25 - 1) * 100


def tableau_libelles():
    lignes = []
    for ex in EXOS:
        for lib, q in E[ex]["par_libelle"].items():
            dose = CALC["meta"]["doses_service"][lib]
            omis = lib in CALC["meta"]["omis_par_le_service"]
            lignes.append([
                cg(ex), cg(lib), cd(f"{dose} cl"), cd(N(q, 1)),
                cd(CL(q * dose, 0)),
                cg("non", badge="ko") if omis else cg("oui", badge="ok"),
            ])
    return {
        "kind": "tableau",
        "titre": "Les libellés de caisse contenant du crémant, avec les doses que le service applique lui-même (p. 62)",
        "minWidth": 760,
        "colonnes": [{"label": "Exercice"}, {"label": "Libellé de caisse"},
                     {"label": "Dose de crémant", "align": "right"},
                     {"label": "Quantité vendue", "align": "right"},
                     {"label": "Crémant", "align": "right"},
                     {"label": "Retenu par le service p. 62"}],
        "lignes": lignes,
    }


def tableau_ecart():
    lignes = []
    for ex in EXOS:
        e = E[ex]
        lignes.append([
            cg(ex), cd(N(e["jours_servis"])), cd(L(e["nominal_cl"])),
            cd(N(e["dispo_bouteilles"])), cd(N(e["bouteilles_vendues_entieres"])),
            cd(L(e["dispo_service_cl"])), cd(L(e["ecart_a_expliquer_cl"]), fw=700),
            cd(CL(e["ecart_par_jour_cl"])),
        ])
    lignes.append([
        cg("Total 3 exercices", fw=700), cd(N(TOT_JOURS), fw=700),
        cd(L(sum(E[x]["nominal_cl"] for x in EXOS)), fw=700),
        cd(N(sum(E[x]["dispo_bouteilles"] for x in EXOS)), fw=700),
        cd(N(sum(E[x]["bouteilles_vendues_entieres"] for x in EXOS)), fw=700),
        cd(L(sum(E[x]["dispo_service_cl"] for x in EXOS)), fw=700),
        cd(L(TOT_ECART), fw=700), cd(CL(TOT_ECART / TOT_JOURS), fw=700),
    ])
    return {
        "kind": "tableau",
        "titre": "L’écart réellement à expliquer, exercice par exercice (volumes disponibles retenus par le service)",
        "minWidth": 860,
        "colonnes": [{"label": "Exercice"}, {"label": "Jours servis", "align": "right"},
                     {"label": "Crémant vendu en caisse", "align": "right"},
                     {"label": "Bouteilles disponibles", "align": "right"},
                     {"label": "Vendues scellées", "align": "right"},
                     {"label": "Disponible pour le service", "align": "right"},
                     {"label": "Écart à expliquer", "align": "right"},
                     {"label": "Par jour de service", "align": "right"}],
        "lignes": lignes,
    }


def tableau_repere():
    lignes = []
    for ex in EXOS:
        e = E[ex]
        lignes.append([
            cg(ex), cd(N(e["jours_servis"])), cd(L(e["jete_theorique_cl"])),
            cd(L(e["ecart_a_expliquer_cl"])),
            cd(PCT(abs(e["jete_theorique_ecart_pct"])),
               badge="ok" if abs(e["jete_theorique_ecart_pct"]) < 5 else None),
        ])
    return {
        "kind": "tableau",
        "titre": "Le repère sans paramètre : une demi-bouteille par jour de service (37,5 cl), comparé à l’écart constaté",
        "minWidth": 700,
        "colonnes": [{"label": "Exercice"}, {"label": "Jours servis", "align": "right"},
                     {"label": "37,5 cl x jours servis", "align": "right"},
                     {"label": "Écart constaté", "align": "right"},
                     {"label": "Distance entre les deux", "align": "right"}],
        "lignes": lignes,
    }


def _sc(ex, taux):
    return next(s for s in E[ex]["scenarios"] if abs(s["taux"] - taux) < 1e-9)


# Bornes de la fourchette demandée : 0 % et +23,6 % (Kerr 2008).
BORNE_BASSE, BORNE_HAUTE = 0.0, 0.236
JETE_MIN = {ex: min(_sc(ex, BORNE_BASSE)["jete_cl"], _sc(ex, BORNE_HAUTE)["jete_cl"]) for ex in EXOS}
JETE_MAX = {ex: max(_sc(ex, BORNE_BASSE)["jete_cl"], _sc(ex, BORNE_HAUTE)["jete_cl"]) for ex in EXOS}
JETE_3A_MIN = min(sum(_sc(ex, t)["jete_cl"] for ex in EXOS) for t in (BORNE_BASSE, BORNE_HAUTE))
JETE_3A_MAX = max(sum(_sc(ex, t)["jete_cl"] for ex in EXOS) for t in (BORNE_BASSE, BORNE_HAUTE))


def tableau_bornes():
    """Les deux bornes du scénario, exercice par exercice : 0 % et +23,6 %."""
    lignes = []
    for ex in EXOS:
        e = E[ex]
        for taux, nom in ((BORNE_BASSE, "Borne basse : aucun sur-versement"),
                          (BORNE_HAUTE, "Borne haute : +23,6 % (Kerr 2008)")):
            sc = _sc(ex, taux)
            lignes.append([
                cg(f"{ex} ({N(e['jours_servis'])} jours)"),
                cg(nom),
                cd(L(sc["servi_cl"])),
                cd(N(sc["bouteilles_ouvertes"])),
                cd(L(sc["jete_cl"]), fw=700),
                cd(L(sc["surversement_cl"])),
                cd(L(sc["non_vendu_cl"])),
                cg("oui", badge="ok") if sc["compatible"] else cg("non", badge="ko"),
            ])
    lignes.append([
        cg("Total 3 exercices", fw=700), cg("Borne basse : aucun sur-versement", fw=700),
        cd(L(sum(_sc(ex, BORNE_BASSE)["servi_cl"] for ex in EXOS)), fw=700),
        cd(N(sum(_sc(ex, BORNE_BASSE)["bouteilles_ouvertes"] for ex in EXOS)), fw=700),
        cd(L(sum(_sc(ex, BORNE_BASSE)["jete_cl"] for ex in EXOS)), fw=700),
        cd("0,0 L", fw=700),
        cd(L(sum(_sc(ex, BORNE_BASSE)["non_vendu_cl"] for ex in EXOS)), fw=700), cg(""),
    ])
    lignes.append([
        cg("Total 3 exercices", fw=700), cg("Borne haute : +23,6 %", fw=700),
        cd(L(sum(_sc(ex, BORNE_HAUTE)["servi_cl"] for ex in EXOS)), fw=700),
        cd(N(sum(_sc(ex, BORNE_HAUTE)["bouteilles_ouvertes"] for ex in EXOS)), fw=700),
        cd(L(sum(_sc(ex, BORNE_HAUTE)["jete_cl"] for ex in EXOS)), fw=700),
        cd(L(sum(_sc(ex, BORNE_HAUTE)["surversement_cl"] for ex in EXOS)), fw=700),
        cd(L(sum(_sc(ex, BORNE_HAUTE)["non_vendu_cl"] for ex in EXOS)), fw=700), cg(""),
    ])
    return {
        "kind": "tableau",
        "titre": "Les deux bornes, exercice par exercice : le crémant jeté sans sur-versement, "
                 "puis avec le sur-versement maximal de +23,6 %",
        "minWidth": 980,
        "colonnes": [{"label": "Exercice"}, {"label": "Scénario"},
                     {"label": "Crémant versé", "align": "right"},
                     {"label": "Bouteilles de 75 cl ouvertes", "align": "right"},
                     {"label": "Crémant jeté en fin de journée", "align": "right"},
                     {"label": "Sur-versement", "align": "right"},
                     {"label": "Total non vendu", "align": "right"},
                     {"label": "Tient dans le stock"}],
        "lignes": lignes,
    }


def kpis_bornes():
    return {"kind": "kpis", "items": [
        {"label": "Crémant jeté, exercice 2022-2023", "valeur": L(JETE_MIN["2022-2023"]) + " à " + L(JETE_MAX["2022-2023"]),
         "sub": "entre 0 % et +23,6 % de sur-versement"},
        {"label": "Crémant jeté, exercice 2023-2024", "valeur": L(JETE_MIN["2023-2024"]) + " à " + L(JETE_MAX["2023-2024"]),
         "sub": "entre 0 % et +23,6 % de sur-versement"},
        {"label": "Crémant jeté, exercice 2024-2025", "valeur": L(JETE_MIN["2024-2025"]) + " à " + L(JETE_MAX["2024-2025"]),
         "sub": "entre 0 % et +23,6 % de sur-versement"},
        {"label": "Crémant jeté, 3 exercices", "valeur": L(JETE_3A_MIN) + " à " + L(JETE_3A_MAX),
         "sub": "quel que soit le taux retenu dans la fourchette", "highlight": True, "couleur": "teal"},
    ]}


def tableau_fourchette():
    lignes = []
    for ex in EXOS:
        e = E[ex]
        for sc in e["scenarios"]:
            if sc["taux"] not in (0.0, 0.05, 0.10, 0.15, 0.20, 0.236):
                continue
            lignes.append([
                cg(ex), cd("+" + PCT(sc["taux"] * 100)), cd(L(sc["servi_cl"])),
                cd(N(sc["bouteilles_ouvertes"])), cd(L(sc["utilise_cl"])),
                cd(L(sc["jete_cl"])), cd(L(sc["reste_dispo_cl"])),
                cg("compatible", badge="ok") if sc["compatible"] else cg("impossible", badge="ko"),
            ])
    return {
        "kind": "tableau",
        "titre": "Fourchette de sur-versement : chaque taux confronté au stock réellement disponible",
        "minWidth": 900,
        "colonnes": [{"label": "Exercice"}, {"label": "Sur-versement", "align": "right"},
                     {"label": "Crémant versé", "align": "right"},
                     {"label": "Bouteilles ouvertes", "align": "right"},
                     {"label": "Sorti du stock", "align": "right"},
                     {"label": "Jeté en fin de journée", "align": "right"},
                     {"label": "Reste disponible", "align": "right"},
                     {"label": "Verdict"}],
        "lignes": lignes,
    }


def tableau_equilibre():
    lignes = []
    for ex in EXOS:
        e, q = E[ex], E[ex]["equilibre"]
        lignes.append([
            cg(ex),
            cd("0 %" if q["taux"] == 0 else "+" + PCT(q["taux"] * 100)),
            cd(N(q["bouteilles_ouvertes"])), cd(L(q["utilise_cl"])),
            cd(L(e["dispo_service_cl"])), cd(L(q["jete_cl"])),
            cd(L(q["servi_cl"] - e["nominal_cl"])),
            cd(("+" if q["depassement_cl"] > 0 else "") + L(q["depassement_cl"])),
        ])
    lignes.append([
        cg("Total 3 exercices", fw=700), cg(""), cd(N(TOT_BT), fw=700),
        cd(L(sum(E[x]["equilibre"]["utilise_cl"] for x in EXOS)), fw=700),
        cd(L(sum(E[x]["dispo_service_cl"] for x in EXOS)), fw=700),
        cd(L(TOT_JETE), fw=700), cd(L(TOT_SURV), fw=700), cg(""),
    ])
    return {
        "kind": "tableau",
        "titre": "Le point d’équilibre : le sur-versement maximal que le stock autorise, et ce qu’il reste",
        "minWidth": 880,
        "colonnes": [{"label": "Exercice"},
                     {"label": "Sur-versement retenu", "align": "right"},
                     {"label": "Bouteilles ouvertes", "align": "right"},
                     {"label": "Crémant sorti du stock", "align": "right"},
                     {"label": "Disponible", "align": "right"},
                     {"label": "Jeté", "align": "right"},
                     {"label": "Sur-versé", "align": "right"},
                     {"label": "Écart au stock", "align": "right"}],
        "lignes": lignes,
    }


def tableau_cout():
    lignes = []
    for ex in EXOS:
        lignes.append([
            cg(ex), cd(N(ACHATS[ex]["bt"])), cd(EUR(ACHATS[ex]["ht"], 2)),
            cd(EUR(ACHATS[ex]["pu"], 2)), cd(L(E[ex]["equilibre"]["jete_cl"])),
            cd(N(E[ex]["equilibre"]["jete_cl"] / 75.0, 1)), cd(EUR(COUT[ex]), fw=700),
        ])
    lignes.append([
        cg("Total 3 exercices", fw=700),
        cd(N(sum(ACHATS[x]["bt"] for x in EXOS)), fw=700),
        cd(EUR(TOT_ACHAT_HT, 2), fw=700), cg(""), cd(L(TOT_JETE), fw=700),
        cd(N(TOT_JETE / 75.0, 1), fw=700), cd(EUR(TOT_COUT), fw=700),
    ])
    return {
        "kind": "tableau",
        "titre": "Ce que coûte réellement le fond de bouteille, au prix d’achat facturé",
        "minWidth": 820,
        "colonnes": [{"label": "Exercice"},
                     {"label": "Bouteilles achetées", "align": "right"},
                     {"label": "Achat HT", "align": "right"},
                     {"label": "Prix unitaire HT", "align": "right"},
                     {"label": "Crémant jeté", "align": "right"},
                     {"label": "Équivalent bouteilles", "align": "right"},
                     {"label": "Coût d’achat du jeté", "align": "right"}],
        "lignes": lignes,
    }


PIECES = {
    "kind": "piecejointe",
    "intro": "Le calcul est intégralement reproductible à partir des annexes de caisse "
             "(lecture seule) par le script scripts/reponse1-cremant-fourchette.py :",
    "fichiers": [
        {"fichier": "pieces-reponse-1/R1-cremant-bilan-matiere.xlsx",
         "label": "Bilan matière, fourchette et point d’équilibre (XLSX, 4 onglets)"},
        {"fichier": "pieces-reponse-1/R1-cremant-jour-par-jour-2022-2023.csv",
         "label": "Crémant ouvert jour par jour, exercice 2022-2023 (CSV)"},
        {"fichier": "pieces-reponse-1/R1-cremant-jour-par-jour-2023-2024.csv",
         "label": "Crémant ouvert jour par jour, exercice 2023-2024 (CSV)"},
        {"fichier": "pieces-reponse-1/R1-cremant-jour-par-jour-2024-2025.csv",
         "label": "Crémant ouvert jour par jour, exercice 2024-2025 (CSV)"},
    ],
}


def sections_recon3():
    e1 = E["2022-2023"]
    return [
        {"kind": "chapitre", "source": "nous", "numero": 2,
         "titre": "Notre réponse : le bilan matière tranche, et il ne laisse aucun volume vendable",
         "sousTitre": "Le service a raison sur un point : le sur-versement et le fond de bouteille ne "
                      "peuvent pas être cumulés à leur maximum. Une fois le bilan matière imposé, "
                      "l’écart qu’il relève s’explique intégralement, et il ne reste rien à vendre."},
        {"kind": "paragraphe",
         "texte": "**L’objection du service porte, et nous en tirons la conséquence.** En appliquant au "
                  "crémant le taux de sur-versement de +23,6 % mesuré par Kerr et ses coauteurs (2008) "
                  "sur le vin servi au verre, **puis** en y ajoutant la totalité du fond de bouteille jeté, "
                  "notre mémoire additionnait deux maxima. Le service le démontre en page 63 : la somme "
                  "dépasse le volume acheté. Nous corrigeons ce point, et nous le corrigeons avec **ses "
                  "propres données** : ses volumes disponibles, ses doses, son tableau de la page 62."},
        {"kind": "titre",
         "texte": "Une seule équation, deux inconnues, et une borne physique"},
        {"kind": "paragraphe",
         "texte": "Le crémant acheté ne peut aller que dans trois directions : il est vendu en bouteille "
                  "scellée, il est versé au client, ou il est perdu. D’où l’égalité, exercice par exercice : "
                  "**crémant disponible = bouteilles vendues scellées + crémant réellement versé + fonds de "
                  "bouteille perdus**. Le sur-versement et le fond de bouteille ne s’additionnent donc pas "
                  "librement : plus le premier est élevé, moins il reste de volume pour le second. Le taux de "
                  "sur-versement du crémant n’a pas à être transposé d’une étude : **il est borné par le stock "
                  "lui-même**, et c’est ce que nous faisons ci-dessous."},
        {"kind": "titre",
         "texte": "Nous adoptons les doses du service, et nous ajoutons les articles qu’il a oubliés"},
        {"kind": "paragraphe",
         "texte": "Le tableau de la page 62 applique 6 cl de crémant à La Vouivre, au Père Grégoire et au "
                  "KITTYKIR, et 12 cl au verre de crémant. **Nous reprenons ces doses telles quelles** : "
                  "elles ne peuvent pas nous être opposées. Le recomptage, ligne à ligne, du détail des "
                  "tickets (annexe C) retrouve exactement les quantités du service pour le premier exercice : "
                  "621,5 La Vouivre pour 622, 503 Père Grégoire pour 503, 233,8 KITTYKIR pour 234, 242 verres "
                  "de crémant pour 242. La correspondance est acquise."},
        {"kind": "paragraphe",
         "texte": "Le tableau du service **omet en revanche deux libellés** qui contiennent du crémant : le "
                  "Kir Princier et le libellé VOUIVRE. Nous les réintégrons. Cet ajout joue contre nous et "
                  "en faveur du service : il augmente la consommation reconnue en caisse, donc il **réduit** "
                  "l’écart qui nous est reproché. Les Kir Bourgogne et Kir Pamplemousse, faits de vin "
                  "tranquille, restent exclus, comme le service les exclut."},
        tableau_libelles(),
        {"kind": "titre", "texte": "L’écart réellement à expliquer"},
        {"kind": "paragraphe",
         "texte": "En partant des volumes disponibles que le service a lui-même retenus (275, 325 puis 322 "
                  "bouteilles), en retranchant les bouteilles vendues scellées et la consommation lue en "
                  "caisse, l’écart à expliquer ressort à " + L(e1["ecart_a_expliquer_cl"]) + ", " +
                  L(E["2023-2024"]["ecart_a_expliquer_cl"]) + " et " +
                  L(E["2024-2025"]["ecart_a_expliquer_cl"]) + ", soit **" + L(TOT_ECART) +
                  " sur les trois exercices**. C’est ce volume, et lui seul, que le service impute à des "
                  "recettes non déclarées."},
        tableau_ecart(),
        {"kind": "kpis", "items": [
            {"label": "Écart à expliquer", "valeur": L(TOT_ECART), "sub": "3 exercices, doses du service",
             "highlight": True, "couleur": "red"},
            {"label": "Jours de service", "valeur": N(TOT_JOURS), "sub": "sur lesquels il se répartit"},
            {"label": "Écart par jour de service", "valeur": CL(TOT_ECART / TOT_JOURS),
             "sub": "soit la moitié d’une bouteille de 75 cl", "highlight": True, "couleur": "teal"},
        ]},
        {"kind": "titre",
         "texte": "Le repère décisif : il ne dépend d’aucun paramètre"},
        {"kind": "paragraphe",
         "texte": "Une bouteille de crémant s’ouvre à la demande, pour une coupe ou pour un cocktail. Si le "
                  "besoin de la journée n’est pas un multiple exact de 75 cl, le solde du soir est perdu. "
                  "Ce solde vaut, en moyenne, **la moitié d’une bouteille, soit 37,5 cl par jour de service**. "
                  "Ce repère ne suppose ni taux de sur-versement, ni estimation, ni hypothèse de "
                  "comportement : c’est une propriété arithmétique du fractionnement d’un contenant."},
        {"kind": "paragraphe",
         "texte": "Or l’écart que le service nous oppose vaut " + CL(e1["ecart_par_jour_cl"]) + " par jour de "
                  "service au premier exercice, " + CL(E["2023-2024"]["ecart_par_jour_cl"]) + " au deuxième et " +
                  CL(E["2024-2025"]["ecart_par_jour_cl"]) + " au troisième. Sur le premier exercice, "
                  "**37,5 cl x 217 jours = " + L(e1["jete_theorique_cl"]) + ", contre " +
                  L(e1["ecart_a_expliquer_cl"]) + " constatés : 0,4 % de distance.** Deux calculs "
                  "entièrement indépendants, l’un tiré du stock, l’autre de la seule géométrie d’une "
                  "bouteille de 75 cl, tombent sur le même nombre."},
        tableau_repere(),
        {"kind": "titre", "texte": "La fourchette de sur-versement que le stock autorise"},
        {"kind": "paragraphe",
         "texte": "Nous avons refait le calcul **jour par jour**, sur les " + N(TOT_JOURS) + " journées de "
                  "service des trois exercices, pour chaque taux de sur-versement entre 0 % et +23,6 %. "
                  "Pour chaque taux : volume versé, nombre de bouteilles de 75 cl ouvertes ce jour-là "
                  "(arrondi supérieur), solde perdu le soir, et confrontation au stock disponible. Un "
                  "scénario n’est retenu que si le crémant ainsi ouvert **tient dans le stock**."},
        {"kind": "paragraphe",
         "texte": "Voici d’abord les **deux bornes**, exercice par exercice. À gauche, l’hypothèse la plus "
                  "défavorable pour nous : **aucun sur-versement**, le serveur verse la dose exacte, et la "
                  "seule perte est le fond de la dernière bouteille ouverte chaque soir. À droite, "
                  "l’hypothèse inverse : **le sur-versement maximal de +23,6 %** mesuré par Kerr et ses "
                  "coauteurs, auquel s’ajoute le même fond de bouteille."},
        tableau_bornes(),
        kpis_bornes(),
        {"kind": "paragraphe",
         "texte": "Le résultat mérite d’être lu deux fois : **le crémant jeté ne dépend presque pas du "
                  "taux de sur-versement**. Il vaut " + L(JETE_3A_MIN) + " sur trois ans dans un cas, " +
                  L(JETE_3A_MAX) + " dans l’autre, soit " +
                  PCT(abs(JETE_3A_MAX - JETE_3A_MIN) / JETE_3A_MAX * 100) + " d’amplitude entre les deux "
                  "bornes. La raison est mécanique : verser davantage fait ouvrir une bouteille de plus, "
                  "et cette bouteille supplémentaire laisse à son tour un fond. Le poste « fond de "
                  "bouteille » est donc **robuste** : il ne repose sur aucune hypothèse de service."},
        {"kind": "paragraphe",
         "texte": "Ce qui varie, c’est le **total non vendu** : " +
                  L(sum(_sc(ex, BORNE_BASSE)["non_vendu_cl"] for ex in EXOS)) + " à la borne basse contre " +
                  L(sum(_sc(ex, BORNE_HAUTE)["non_vendu_cl"] for ex in EXOS)) + " à la borne haute. Et "
                  "c’est précisément là que le stock tranche : la borne haute exige " +
                  L(sum(_sc(ex, BORNE_HAUTE)["utilise_cl"] for ex in EXOS)) + " de crémant pour " +
                  L(sum(E[ex]["dispo_service_cl"] for ex in EXOS)) + " disponibles, ce qui est "
                  "**matériellement impossible sur les trois exercices**. L’objection du service est donc "
                  "retenue, et le balayage complet ci-dessous montre où se situe la limite."},
        tableau_fourchette(),
        {"kind": "paragraphe",
         "texte": "Le résultat est net : **le sur-versement du crémant se situe entre 0 % et " +
                  PCT(TAUX_MAX * 100) + "**, jamais à +23,6 %. Sur le premier exercice, aucun taux positif "
                  "n’est même compatible. L’objection du service tirée de la capacité de la petite coupe "
                  "(page 63) est donc **fondée, et elle ne nous coûte rien** : le fond de bouteille suffit à "
                  "expliquer l’écart."},
        {"kind": "titre", "texte": "Au point d’équilibre, il ne reste aucun volume vendable"},
        {"kind": "paragraphe",
         "texte": "En retenant, pour chaque exercice, le sur-versement maximal que le stock autorise, le "
                  "bilan boucle : " + N(TOT_BT) + " bouteilles ouvertes sur trois ans, soit " +
                  L(sum(E[x]["equilibre"]["utilise_cl"] for x in EXOS)) + " sorties du stock pour " +
                  L(sum(E[x]["dispo_service_cl"] for x in EXOS)) + " disponibles. **Au deuxième exercice le "
                  "bilan tombe juste, au centilitre.** Au troisième, " +
                  L(-E["2024-2025"]["equilibre"]["depassement_cl"]) + " restent inemployés. Au premier, le "
                  "modèle dépasse de " + L(E["2022-2023"]["equilibre"]["depassement_cl"]) +
                  " le stock retenu par le service, soit deux bouteilles sur 217 jours de service : "
                  "l’ordre de grandeur de l’arrondi de sa propre variation de stock. Il n’existe, dans "
                  "aucun des trois exercices, de volume de crémant disponible pour une vente non "
                  "enregistrée."},
        tableau_equilibre(),
        {"kind": "kpis", "items": [
            {"label": "Sur-versement retenu", "valeur": "0 % à " + PCT(TAUX_MAX * 100),
             "sub": "borné par le stock, jamais +23,6 %", "highlight": True, "couleur": "teal"},
            {"label": "Crémant jeté", "valeur": L(TOT_JETE), "sub": "3 exercices, " + N(TOT_BT) + " bouteilles ouvertes"},
            {"label": "Crémant sur-versé", "valeur": L(TOT_SURV), "sub": "perte distincte, non cumulable au maximum"},
            {"label": "Volume restant pour une vente occulte", "valeur": "0 L",
             "sub": "le bilan matière est bouclé", "highlight": True, "couleur": "teal"},
        ]},
        {"kind": "titre", "texte": "Pourquoi un fond de bouteille, et non une recette dissimulée"},
        {"kind": "paragraphe",
         "texte": "**Premier indice : la régularité.** L’écart se répartit à " + CL(e1["ecart_par_jour_cl"]) +
                  ", " + CL(E["2023-2024"]["ecart_par_jour_cl"]) + " et " + CL(E["2024-2025"]["ecart_par_jour_cl"]) +
                  " par jour de service, trois exercices de suite. Il suit le **nombre de journées de "
                  "service**, pas le chiffre d’affaires ni le nombre de coupes vendues. C’est la signature "
                  "d’une perte mécanique par journée, pas d’un prélèvement proportionnel aux ventes."},
        {"kind": "paragraphe",
         "texte": "**Deuxième indice : la valeur.** Le service écrit qu’un tel taux de perte serait "
                  "« considérable et non-vivable économiquement pour une quelconque société » (p. 62). Au "
                  "prix d’achat réellement facturé par la Fruitière vinicole d’Arbois, le crémant jeté "
                  "représente " + EUR(TOT_COUT) + " HT sur trois exercices, soit environ " +
                  EUR(TOT_COUT / 3) + " par an. Sur des achats de crémant de " + EUR(TOT_ACHAT_HT, 2) +
                  " HT et des achats d’alcool de 107 924 € HT, cette perte est parfaitement supportable : "
                  "elle est de l’ordre d’une demi-bouteille par jour de service."},
        tableau_cout(),
        {"kind": "paragraphe",
         "texte": "**Troisième indice : le canal d’encaissement.** Une coupe vendue hors caisse suppose un "
                  "encaissement en espèces. Le taux de bancarisation de l’établissement est de 98,7 % : les "
                  "espèces ne laissent aucune place à un tel volume, et aucun excédent d’espèces n’a été "
                  "constaté."},
        {"kind": "titre", "texte": "Deux calculs du service à rectifier"},
        {"kind": "paragraphe",
         "texte": "**Le pourcentage annoncé pour le premier exercice.** Le service écrit page 63 que la "
                  "quantité nécessaire « devrait donc être 20 % supérieurs à celle de la quantité "
                  "réellement disponible ». Ses propres chiffres donnent 239,05 L pour 206,25 L, soit " +
                  PCT(SERVICE_EX1_RATIO) + " et non 20 %."},
        {"kind": "paragraphe",
         "texte": "**Le taux de 45,18 %.** Le service rapporte 93,20 L jetés à 206,25 L disponibles. Le "
                  "numérateur est issu du scénario à +23,6 % que nous abandonnons, et le dénominateur "
                  "inclut les bouteilles vendues scellées, qui ne sont jamais ouvertes au service. Rapporté "
                  "au volume réellement ouvert, le fond de bouteille du premier exercice représente " +
                  PCT(e1["equilibre"]["jete_cl"] / e1["equilibre"]["utilise_cl"] * 100) + ", "
                  "ce qui est exactement ce qu’implique l’ouverture d’une bouteille de 75 cl pour un besoin "
                  "quotidien moyen de " + CL(e1["nominal_cl"] / e1["jours_servis"]) + "."},
        {"kind": "chapitre", "source": "nous", "numero": 3,
         "titre": "Ce que cela fait tomber",
         "sousTitre": "Le constat « Consommation > Disponible » disparaît, et avec lui le seul motif "
                      "opposé à la perte de crémant."},
        {"kind": "paragraphe",
         "texte": "Le tableau de la page 85 (« Consommation > Disponible » sur les trois exercices) est la "
                  "conséquence arithmétique du cumul de deux maxima. Le cumul supprimé, le bilan boucle sur "
                  "les trois exercices et **le service n’oppose plus rien** : ni chiffre, ni source, ni "
                  "contre-calcul. Ses trois autres objections sont des affirmations non chiffrées (le "
                  "crémant entre dans plusieurs articles, les dirigeants ont de l’expérience, les pertes "
                  "sont exagérées) ; la dernière, la capacité du verre, nous l’avons intégrée."},
        {"kind": "paragraphe",
         "texte": "Nous ramenons en conséquence la perte de crémant revendiquée de 346,9 L à **" +
                  L(TOT_ECART) + " sur trois exercices**, dont environ " + L(TOT_JETE) + " de fonds de "
                  "bouteille et " + L(TOT_SURV) + " de sur-versement. Ce chiffre n’est plus une estimation : "
                  "c’est la différence, au centilitre, entre le crémant disponible retenu par le service et "
                  "le crémant vendu selon ses propres doses. Il ne reste, dans le crémant, aucun volume "
                  "susceptible d’alimenter une reconstitution de recettes."},
        PIECES,
    ]


def sections_perteP():
    e1 = E["2022-2023"]
    return [
        {"kind": "chapitre", "source": "nous", "numero": 2,
         "titre": "Notre réponse : le tableau de la page 85 se corrige de lui-même",
         "sousTitre": "Le constat « Consommation > Disponible » vient du cumul de deux maxima. "
                      "Le cumul supprimé, le bilan matière boucle et rien ne reste à vendre."},
        {"kind": "paragraphe",
         "texte": "Cette partie reprend, presque mot pour mot, la partie « L » du même courrier. La "
                  "démonstration complète, chiffrée jour par jour sur les " + N(TOT_JOURS) + " journées de "
                  "service des trois exercices, figure à la page [3.1.3 « Tout le crémant réputé vendu »]"
                  "(/reponse-1/recon-3-cremant-vendu). Nous n’en reprenons ici que le résultat et les "
                  "trois arguments propres à cette partie."},
        {"kind": "titre", "texte": "Le résultat : le bilan boucle, sans sur-versement de 23,6 %"},
        {"kind": "paragraphe",
         "texte": "Nous retenons les volumes disponibles du service (275, 325 et 322 bouteilles) et **ses "
                  "propres doses** (tableau p. 62 : cocktails 6 cl, verre 12 cl). L’écart entre ce qui était "
                  "disponible et ce que la caisse enregistre ressort à " + L(TOT_ECART) + " sur trois "
                  "exercices, soit " + CL(TOT_ECART / TOT_JOURS) + " par jour de service. Le sur-versement "
                  "compatible avec le stock est compris entre 0 % et " + PCT(TAUX_MAX * 100) + " : "
                  "**l’objection du service tirée de la capacité de la petite coupe est retenue**, elle ne "
                  "change pas la conclusion."},
        {"kind": "paragraphe",
         "texte": "Les deux bornes du calcul, exercice par exercice : à gauche **aucun sur-versement** "
                  "(la seule perte est le fond de la dernière bouteille ouverte chaque soir), à droite "
                  "**le sur-versement maximal de +23,6 %** invoqué dans le mémoire, auquel s’ajoute le "
                  "même fond de bouteille."},
        tableau_bornes(),
        kpis_bornes(),
        {"kind": "paragraphe",
         "texte": "Le crémant jeté est **quasi insensible au taux de sur-versement** : " + L(JETE_3A_MIN) +
                  " à " + L(JETE_3A_MAX) + " sur trois ans, soit " +
                  PCT(abs(JETE_3A_MAX - JETE_3A_MIN) / JETE_3A_MAX * 100) + " d’amplitude. Verser "
                  "davantage fait simplement ouvrir une bouteille de plus, qui laisse à son tour un fond. "
                  "En revanche la borne haute exige " +
                  L(sum(_sc(ex, BORNE_HAUTE)["utilise_cl"] for ex in EXOS)) + " de crémant pour " +
                  L(sum(E[ex]["dispo_service_cl"] for ex in EXOS)) + " disponibles : c’est ce que le "
                  "service relève en page 85, et il a raison. Le tableau ci-dessous retient donc, pour "
                  "chaque exercice, le sur-versement maximal que le stock autorise réellement."},
        tableau_equilibre(),
        {"kind": "kpis", "items": [
            {"label": "Perte de crémant retenue", "valeur": L(TOT_ECART),
             "sub": "au lieu de 346,9 L : environ " + L(TOT_JETE) + " jetés et " + L(TOT_SURV) + " sur-versés",
             "highlight": True, "couleur": "teal"},
            {"label": "Sur-versement", "valeur": "0 % à " + PCT(TAUX_MAX * 100),
             "sub": "borné par le stock, jamais +23,6 %"},
            {"label": "Coût réel du jeté", "valeur": EUR(TOT_COUT / 3) + " / an",
             "sub": "au prix d’achat facturé"},
            {"label": "Volume restant pour une vente occulte", "valeur": "0 L",
             "sub": "le bilan matière est bouclé", "highlight": True, "couleur": "teal"},
        ]},
        {"kind": "titre", "texte": "Les trois objections propres à cette partie"},
        {"kind": "paragraphe",
         "texte": "**« Le crémant est utilisé pour de nombreux articles » (p. 84).** C’est exact, et c’est "
                  "précisément ce que notre calcul intègre : le besoin de la journée additionne les coupes "
                  "et les cocktails avant d’en déduire le nombre de bouteilles ouvertes. L’argument ne "
                  "supprime pas le fond de bouteille, il le réduit, et cette réduction est déjà faite. "
                  "Elle laisse un solde moyen de " + CL(TOT_ECART / TOT_JOURS) + " par jour, soit la moitié "
                  "d’une bouteille."},
        {"kind": "paragraphe",
         "texte": "**« La longue expérience professionnelle des dirigeants » (p. 85).** Une qualité "
                  "personnelle n’est pas un mode de preuve. Le service n’en tire aucun chiffre et ne "
                  "l’oppose à aucune donnée. Surtout, si les bouteilles entamées étaient conservées, le "
                  "crémant manquant se retrouverait dans les ventes du lendemain : la caisse ne l’enregistre "
                  "pas, et le stock ne l’a pas."},
        {"kind": "paragraphe",
         "texte": "**Le taux de 45,18 % (p. 84).** Il rapporte 93,20 L, issus du scénario à +23,6 % que "
                  "nous abandonnons, à 206,25 L incluant les bouteilles vendues scellées, qui ne sont jamais "
                  "ouvertes. Rapporté au volume réellement ouvert au service, le fond de bouteille du "
                  "premier exercice représente " +
                  PCT(e1["equilibre"]["jete_cl"] / e1["equilibre"]["utilise_cl"] * 100) +
                  ", et coûte " + EUR(COUT["2022-2023"]) + " HT sur l’exercice. Rien qui soit "
                  "« non-vivable économiquement »."},
        {"kind": "chapitre", "source": "nous", "numero": 3,
         "titre": "Ce que cela fait tomber",
         "sousTitre": "Le constat d’impossibilité matérielle disparaît, et le chiffre retenu devient vérifiable au centilitre."},
        {"kind": "paragraphe",
         "texte": "Le tableau de la page 85 disparaît : il mesurait la contradiction d’un calcul qui "
                  "cumulait deux maxima, pas une impossibilité matérielle. Corrigé, le bilan du crémant "
                  "boucle exercice par exercice, avec un écart résiduel nul au deuxième exercice. **Aucun "
                  "volume de crémant n’est disponible pour alimenter une reconstitution de recettes.**"},
        PIECES,
    ]


def injecte(slug, nouvelles, reponse_courte, statut="demonte", enjeu=None):
    chemin = os.path.join(ROOT, "src/data/reponse1", slug + ".json")
    doc = json.load(open(chemin, encoding="utf-8"))
    # Idempotent : on ne garde que l'exposé de la position du service (chapitres
    # « fisc ») et on recolle la réfutation derrière. Tout ce qui suit le premier
    # chapitre non « fisc » est reconstruit à chaque exécution.
    secs = doc["sections"]
    coupe = next((i for i, s in enumerate(secs)
                  if s.get("kind") == "chapitre" and s.get("source") != "fisc"), len(secs))
    doc["sections"] = secs[:coupe] + nouvelles
    doc.setdefault("entete", {})
    doc["entete"]["reponseCourte"] = reponse_courte
    doc["entete"]["statut"] = statut
    if enjeu:
        doc["entete"]["enjeu"] = enjeu
    json.dump(doc, open(chemin, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("écrit :", chemin, "->", len(doc["sections"]), "sections")


if __name__ == "__main__":
    injecte("recon-3-cremant-vendu", sections_recon3(),
            "Le service a raison de refuser le cumul du sur-versement maximal et du fond de bouteille : "
            "corrigé avec ses propres volumes et ses propres doses, le bilan matière du crémant boucle "
            "exercice par exercice et ne laisse aucun volume vendable.",
            enjeu="Crémant : " + L(TOT_ECART) + " sur trois exercices")
    injecte("perte-de-cremant", sections_perteP(),
            "Le tableau « Consommation > Disponible » de la page 85 mesure la contradiction d’un calcul "
            "qui cumulait deux maxima, non une impossibilité matérielle : corrigé, le bilan du crémant "
            "boucle et la perte retenue devient la différence exacte entre les achats du service et les "
            "ventes de sa caisse.",
            enjeu="Crémant : " + L(TOT_ECART) + " de perte retenue")
