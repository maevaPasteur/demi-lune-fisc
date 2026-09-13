#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REPONSE 1 - Biere pression : la freinte etablie par la matiere, et l'assiette
du taux lue dans les propres pieces du service.

Complete scripts/reponse1-biere-freinte.py, qui traite l'assiette des deux
abattements. Ce script-ci repond au reproche de la page 61 ("sans apporter de
justifications probantes") en ne produisant que des grandeurs COMPTEES :

  1. Les doses de biere que le SERVICE retient article par article, lues dans
     la proposition de rectifications p. 50 et dans le bloc "i) INGREDIENT :
     BIERE" des annexes finales (p. 203 du PDF des annexes, 2e des 3 pages).
  2. L'assiette du taux de freinte sous ces doses, sous les notres, et sous la
     lecture des seules lignes de la section "Bieres" des annexes D.
  3. Le bloc biere des annexes finales, rejoue ligne a ligne.
  4. Le nombre d'EVENEMENTS-FUT (mises en perce) et d'EVENEMENTS-VERRE, comptes
     sur les factures du fournisseur et sur le detail des tickets (annexes C).
  5. Ce que vaut, en euros, un point de freinte dans le modele du service.

Aucune dose n'est deduite d'un bilan matiere : les doses ont une origine, elle
est citee. Aucune valeur de perte par evenement n'est retenue : le script
produit une grille, pas un chiffre.

Sources (lecture seule) :
  public/documents/caisse-enregistreuse/ANNEXE-C{1,2,3}_detail-tickets_*.xls
  src/data/calculsBoissons/achatsBoissonsParPeriode.json
  src/data/reconstitution-administration.json

Sortie :
  public/documents/pieces-reponse-1/R1-biere-matiere-et-assiette.xlsx
  + une synthese JSON sur la sortie standard.
"""

import json
import os
import datetime

ICI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(ICI, ".."))
DATA = os.path.join(ROOT, "src", "data")
CAISSE = os.path.join(ROOT, "public", "documents", "caisse-enregistreuse")
PIECES = os.path.join(ROOT, "public", "documents", "pieces-reponse-1")
EXOS = ["2022-2023", "2023-2024", "2024-2025"]
EXL = {"2022-2023": "2022-2023", "2023-2024": "2023-2024", "2024-2025": "2024-2025"}

PRODUIT_FUT = "FUT AFFLIGEM BLADE 8 L 6,7°"
FUT_L = 8.0
FUT_STANDARD_L = 30.0          # format du tirage traditionnel, pour comparaison
RESIDU_FUT_L = 0.120           # manuel Blade, ch. 6.3, p. 28 : 1,5 % (120 ml)

ANNEXES_C = {
    "2022-2023": "ANNEXE-C1_detail-tickets_2022-2023.xls",
    "2023-2024": "ANNEXE-C2_detail-tickets_2023-2024.xls",
    "2024-2025": "ANNEXE-C3_detail-tickets_2024-2025.xls",
}

# --- Les six articles de caisse qui tirent sur le fut ----------------------
# dose_service : centilitres de BIERE par article, tels que le service les
#   ecrit lui-meme (proposition de rectifications p. 50, liste "Ingredient :
#   BIERE", et colonne "Dose (en centilitres)" du bloc biere des annexes
#   finales). La proposition marque d'un (*) le Panache et le Monaco : pour ces
#   deux articles, la dose vient "d'internet [...] a defaut".
# dose_nous : la dose que la defense retient (memoire du 10/07/2026 et cascade
#   des 10 622 L) : panache et Monaco a moitie biere, Picon biere a 4 cl de
#   Picon (8 cl a la pinte).
ARTICLES = [
    # (libelle caisse, libelle lisible, contenance verre cl, dose service, dose nous)
    ("pression",    "Pression 25 cl",          25, 25, 25.0),
    ("Pinte",       "Pinte 50 cl",             50, 50, 50.0),
    ("Panaché",     "Panaché 25 cl",           25, 11, 12.5),
    ("Monaco",      "Monaco 25 cl",            25, 15, 12.5),
    ("Picon bière", "Picon bière 25 cl",       25, 22, 21.0),
    ("Pinte Picon", "Picon bière 50 cl",       50, 44, 42.0),
]
# Le Monaco 2022-2023 est classe par l'annexe D1 hors de la section "Bieres"
# (en-tete "LIQUIDE - TVA 10 %") : la lecture par section l'omet.
HORS_SECTION_BIERES = [("Monaco", "2022-2023")]

# --- Bloc "i) INGREDIENT : BIERE" des annexes finales ----------------------
# Releve fait sur l'image de la 2e page des annexes finales (page 203).
# Les quantites vendues y sont celles de l'exercice 2024-2025 (662 pressions,
# 308 pintes, 97 panaches, 74 Monaco, 59 pintes Picon, 124 Picon biere apres
# arrondi du 123,5 de la caisse).
ANNEXE_FINALE = {
    "futs": 79,
    "volume_disponible_cl": 63200,
    "abattement_libelle": "Proportion BIERE pour consommation personnel, pertes...(15%)",
    "abattement_cl": 9480,
    "net_cl": 53720,
    "caisse": [
        # (article, qte vendue portee par l'annexe, dose cl, volume cl porte, proportion)
        ("Picon bière (S) 3 cl picon et 22 cl bière", 124, 22, 2728, 0.0697),
        ("Panaché (11 cl bière) (J) + 13 cl de Limonade", 97, 11, 767, 0.0196),
        ("Monaco (15 cl bière) (K) + 5 cl de limonade et 2 cl de sirop grenadine",
         74, 15, 1110, 0.0284),
        ("Pinte Picon (T) (6 cl picon et 44 cl bière)", 59, 44, 2596, 0.0663),
        ("Pression (25 cl)", 662, 25, 16550, 0.4227),
        ("Pinte (50 cl)", 308, 50, 15400, 0.3933),
    ],
    "total_cl": 39151,
    "volumes_disparus_pct": 0.2712,
    "valorise": [
        # (article, proportion, dose cl, prix moyen TTC, CA TTC porte par l'annexe)
        ("Pression (25 cl)", 0.4227, 25, 4.19, 3804.52),
        ("Pinte (50 cl)", 0.3933, 50, 8.00, 3376.00),
    ],
    "ca_ttc": 7180.52,
}


def fr(x, dec=0):
    return f"{x:,.{dec}f}".replace(",", " ").replace(".", ",")


# --------------------------------------------------------------------------
def lire_achats():
    d = json.load(open(os.path.join(DATA, "calculsBoissons",
                                    "achatsBoissonsParPeriode.json"), encoding="utf-8"))
    for a in d["achats"]:
        if a["produit"] == PRODUIT_FUT:
            return {e: a["par_periode"][e]["quantite"] for e in EXOS}
    raise SystemExit("Fût Affligem introuvable dans les achats")


def lire_annexes_c():
    """Detail des tickets remis par le service. Retourne, par exercice :
    les quantites par article, le volume de biere servi jour par jour, le
    nombre de tickets comportant de la biere, et le nombre de lignes."""
    import xlrd
    libelles = {a[0] for a in ARTICLES}
    qte = {e: {a[0]: 0.0 for a in ARTICLES} for e in EXOS}
    jour_nous = {e: {} for e in EXOS}
    jour_serv = {e: {} for e in EXOS}
    tickets = {e: set() for e in EXOS}
    lignes = {e: 0 for e in EXOS}
    dose_nous = {a[0]: a[4] for a in ARTICLES}
    dose_serv = {a[0]: a[3] for a in ARTICLES}
    for e in EXOS:
        wb = xlrd.open_workbook(os.path.join(CAISSE, ANNEXES_C[e]))
        sh = wb.sheet_by_index(0)
        for r in range(1, sh.nrows):
            lib = str(sh.cell_value(r, 10)).strip()
            if lib not in libelles:
                continue
            q = sh.cell_value(r, 11) or 0
            d = str(sh.cell_value(r, 0))[:10]
            if len(d) != 10:
                continue
            qte[e][lib] += q
            lignes[e] += 1
            tickets[e].add((d, str(sh.cell_value(r, 2))))
            jour_nous[e][d] = jour_nous[e].get(d, 0.0) + q * dose_nous[lib] / 100.0
            jour_serv[e][d] = jour_serv[e].get(d, 0.0) + q * dose_serv[lib] / 100.0
    return qte, jour_nous, jour_serv, tickets, lignes


def volumes(qte, cle):
    """cle = 3 (dose service) ou 4 (dose defense)."""
    out = {}
    for e in EXOS:
        out[e] = sum(qte[e][a[0]] * a[cle] for a in ARTICLES) / 100.0
    return out


def volume_section_bieres(qte):
    """Lecture par section : le Monaco 2022-2023, que l'annexe D1 classe hors
    de la section « Bières », n'y est pas compte."""
    out = {}
    for e in EXOS:
        s = 0.0
        for a in ARTICLES:
            if (a[0], e) in HORS_SECTION_BIERES:
                continue
            s += qte[e][a[0]] * a[4]
        out[e] = s / 100.0
    return out


def calendrier(jour):
    """Statistiques de service, par exercice, sur le volume journalier."""
    out = {}
    for e in EXOS:
        j = jour[e]
        v = sorted(j.values())
        jours = sorted(j)
        d0 = datetime.date.fromisoformat(jours[0])
        d1 = datetime.date.fromisoformat(jours[-1])
        # plus longue interruption continue entre deux jours de service
        trous, prev = [], None
        for x in jours:
            dx = datetime.date.fromisoformat(x)
            if prev is not None and (dx - prev).days > 1:
                trous.append(((prev).isoformat(), dx.isoformat(), (dx - prev).days - 1))
            prev = dx
        trous.sort(key=lambda t: -t[2])
        n = len(v)
        out[e] = {
            "premier": jours[0], "dernier": jours[-1],
            "jours_avec_biere": n,
            "total_l": sum(v),
            "moyenne_l": sum(v) / n,
            "mediane_l": v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2,
            "max_l": v[-1],
            "jours_sous_1l": sum(1 for x in v if x < 1.0),
            "jours_sous_8l": sum(1 for x in v if x < FUT_L),
            "plus_longue_fermeture": trous[0] if trous else None,
            "duree_exercice_j": (d1 - d0).days + 1,
        }
    return out


# --------------------------------------------------------------------------
def main():
    achats_l = lire_achats()
    qte, jour_nous, jour_serv, tickets, lignes = lire_annexes_c()
    v_serv = volumes(qte, 3)
    v_nous = volumes(qte, 4)
    v_sect = volume_section_bieres(qte)
    v_verre = {e: sum(qte[e][a[0]] * a[2] for a in ARTICLES) / 100.0 for e in EXOS}
    cal = calendrier(jour_nous)

    tot_achat = sum(achats_l.values())
    tot_futs = tot_achat / FUT_L
    tot_serv = sum(v_serv.values())
    tot_nous = sum(v_nous.values())
    tot_sect = sum(v_sect.values())
    tot_unites = sum(qte[e][a[0]] for e in EXOS for a in ARTICLES)
    tot_tickets = sum(len(tickets[e]) for e in EXOS)
    tot_lignes = sum(lignes.values())

    # ---------------------------------------------------------------- onglets
    o_doses = []
    for lib, nom, verre, ds, dn in ARTICLES:
        src = ("proposition p. 50 : « conformément aux recettes obtenues des "
               "dirigeants ou de la carte des boissons »")
        if lib in ("Panaché", "Monaco"):
            src = ("proposition p. 50 : article marqué (*), dose venue « ou "
                   "d'internet (*), à défaut »")
        o_doses.append([nom, verre, ds, dn, round(dn - ds, 1), src])
    o_doses.append(["TOTAL, appliqué aux quantités des annexes C (L)", "",
                    round(tot_serv, 1), round(tot_nous, 1),
                    round(tot_nous - tot_serv, 1),
                    "l'assiette que nous retenons est la plus basse des trois lectures"])

    o_assiette = []
    for e in EXOS:
        o_assiette.append([EXL[e], round(sum(qte[e][a[0]] for a in ARTICLES), 1),
                           round(v_verre[e], 1), round(v_serv[e], 1),
                           round(v_nous[e], 1), round(v_sect[e], 1)])
    o_assiette.append(["TOTAL 3 exercices", round(tot_unites, 1),
                       round(sum(v_verre.values()), 1), round(tot_serv, 1),
                       round(tot_nous, 1), round(tot_sect, 1)])

    o_annexe = []
    af = ANNEXE_FINALE
    for art, q, dose, vol, prop in af["caisse"]:
        calc = q * dose
        o_annexe.append([art, q, dose, vol, calc, round(vol - calc),
                         f"{100 * prop:.2f} %".replace(".", ",")])
    o_annexe.append(["TOTAL porté par l'annexe", "", "", af["total_cl"],
                     sum(q * d for _, q, d, _, _ in af["caisse"]),
                     af["total_cl"] - sum(q * d for _, q, d, _, _ in af["caisse"]),
                     "100,00 %"])

    ecart_net = af["net_cl"] - af["total_cl"]
    o_cascade_serv = [
        ["Fûts portés par l'annexe", af["futs"], "fûts",
         "« Fut Affligem Blade 800 cl », colonne « Quantités disponibles »"],
        ["Volume disponible", af["volume_disponible_cl"], "cl",
         "79 x 800 cl"],
        ["Abattement bière", -af["abattement_cl"], "cl", af["abattement_libelle"]],
        ["Quantités nettes", af["net_cl"], "cl", "63 200 - 9 480"],
        ["Volume de bière lu en caisse par le service", af["total_cl"], "cl",
         "somme de la colonne « Quantités (en centilitres) » du bloc bière"],
        ["Écart", ecart_net, "cl",
         "53 720 - 39 151. C'est ce que le service impute à une dissimulation"],
        ["Volumes disparus portés par l'annexe", "27,12 %", "",
         f"contrôle : {ecart_net} / {af['net_cl']} = "
         f"{100 * ecart_net / af['net_cl']:.2f} %".replace(".", ",")],
        ["Chiffre d'affaires bière reconstitué", af["ca_ttc"], "EUR TTC",
         "pression et pinte seules ; Picon bière, pinte Picon, panaché et "
         "Monaco sont valorisés sous les paragraphes Picon et Limonade"],
    ]

    # Sensibilite : ce que vaut un point de freinte dans le modele du service.
    # Prix par centilitre net, tire des deux seules lignes valorisees.
    eur_par_cl = sum(p * d_prop / dose for _, d_prop, dose, p, _ in af["valorise"])
    sv = json.load(open(os.path.join(DATA, "reconstitution-administration.json"),
                        encoding="utf-8"))
    coef = sv["methode"]["rapportLiquideSolidePour1Euro"]
    ab_fin = sum(sv["methode"]["abattements"].values())
    ampli = (1 - ab_fin) * (1 + coef)
    point_cl = af["volume_disponible_cl"] / 100.0     # 1 % du volume disponible
    point_eur = point_cl * eur_par_cl
    o_sensi = [
        ["Prix moyen du centilitre net, dans le modèle du service",
         round(eur_par_cl, 6), "EUR TTC/cl",
         "42,27 % à 4,19 EUR les 25 cl et 39,33 % à 8,00 EUR les 50 cl"],
        ["Contrôle : quantités nettes x ce prix",
         round(af["net_cl"] * eur_par_cl, 2), "EUR TTC",
         f"à comparer au CA bière porté par l'annexe, {fr(af['ca_ttc'], 2)} EUR "
         "(l'écart tient aux arrondis à l'unité inférieure)"],
        ["Un point de freinte en plus, en volume", round(point_cl, 1), "cl",
         "1 % des 63 200 cl disponibles"],
        ["Un point de freinte en plus, en CA liquides", round(point_eur, 2),
         "EUR TTC", "sur l'exercice que les annexes finales documentent"],
        ["Le même point, après abattements de fin de méthode et extrapolation "
         "solides", round(point_eur * ampli, 2), "EUR TTC",
         f"x (1 - 15 %) x (1 + {coef}) = x {ampli:.3f}".replace(".", ",")],
        ["Les cinq points qui sépareraient 15 % de 20 %",
         round(5 * point_eur * ampli, 2), "EUR TTC",
         "sur ce seul exercice. Nous ne les demandons pas"],
    ]

    # Evenements comptes
    o_evt = []
    for e in EXOS:
        nb = achats_l[e] / FUT_L
        o_evt.append([EXL[e], round(achats_l[e], 1), round(nb),
                      round(v_nous[e], 1), round(v_nous[e] / nb, 2),
                      round(100 * nb / v_nous[e], 1),
                      round(achats_l[e] / FUT_STANDARD_L, 1),
                      round(nb - achats_l[e] / FUT_STANDARD_L, 1)])
    o_evt.append(["TOTAL 3 exercices", round(tot_achat, 1), round(tot_futs),
                  round(tot_nous, 1), round(tot_nous / tot_futs, 2),
                  round(100 * tot_futs / tot_nous, 1),
                  round(tot_achat / FUT_STANDARD_L, 1),
                  round(tot_futs - tot_achat / FUT_STANDARD_L, 1)])

    o_grille = []
    for x in (5, 10, 15, 20, 25):
        p8 = tot_futs * x / 100.0
        p30 = (tot_achat / FUT_STANDARD_L) * x / 100.0
        o_grille.append([f"{x} cl", round(p8, 1),
                         f"{100 * p8 / 1205.0:.2f} %".replace(".", ","),
                         f"{100 * p8 / tot_achat:.2f} %".replace(".", ","),
                         round(p30, 1),
                         f"{100 * p30 / 1205.0:.2f} %".replace(".", ",")])

    o_cal = []
    for e in EXOS:
        c = cal[e]
        f = c["plus_longue_fermeture"]
        o_cal.append([EXL[e], c["premier"], c["dernier"], c["jours_avec_biere"],
                      round(c["total_l"], 1), round(c["moyenne_l"], 2),
                      round(c["mediane_l"], 2), round(c["max_l"], 2),
                      c["jours_sous_1l"], c["jours_sous_8l"],
                      f"{f[2]} j ({f[0]} au {f[1]})" if f else ""])
    tj = sorted(v for e in EXOS for v in jour_nous[e].values())
    o_cal.append(["TOTAL 3 exercices", cal[EXOS[0]]["premier"],
                  cal[EXOS[-1]]["dernier"], len(tj), round(sum(tj), 1),
                  round(sum(tj) / len(tj), 2),
                  round(tj[len(tj) // 2], 2), round(tj[-1], 2),
                  sum(1 for v in tj if v < 1.0),
                  sum(1 for v in tj if v < FUT_L), ""])

    o_postes = [
        ["Premier abattement, 15 % du volume de fût",
         "pertes sur bière, consommation du personnel, offerts",
         "proposition de rectifications p. 51 : « une part de 15 % "
         "supplémentaire sur le volume de bière acheté et disponible qui a été "
         "retranchée [...] notamment de tenir compte, spécifiquement pour la "
         "bière : des pertes sur bière, de la consommation du personnel, des "
         "offerts »",
         round(tot_achat * 0.15, 1)],
        ["Le même, tel que les annexes finales le libellent",
         "consommation du personnel et pertes",
         "annexes finales, ligne « Proportion BIERE pour consommation "
         "personnel, pertes...(15%) »", round(tot_achat * 0.15, 1)],
        ["Le même, tel que la réponse du 04/09/2026 le qualifie p. 83",
         "perte de bière seule",
         "« le service avait, auparavant, déjà appliqué un taux spécifique sur "
         "perte de bière de 15 % »", round(tot_achat * 0.15, 1)],
        ["Second abattement, 15 % du chiffre d'affaires liquides",
         "remise 5 %, pertes 5 %, consommation du personnel 5 %",
         "proposition p. 51, trois forfaits énumérés séparément, et annexes "
         "finales, 8 253,27 EUR chacun", round(tot_achat * 0.85 * 0.15, 1)],
    ]

    onglets = [
        ("1. Doses du service",
         ["Article de caisse", "Contenance du verre (cl)",
          "Dose de bière retenue par le service (cl)",
          "Dose retenue par la défense (cl)", "Écart (cl)",
          "Origine de la dose du service"],
         o_doses, [30, 14, 18, 18, 10, 70]),
        ("2. Assiette",
         ["Exercice", "Unités de vente (annexes C)",
          "Contenance des verres (L)", "Bière sous les doses du service (L)",
          "Bière sous les doses de la défense (L)",
          "Bière lue dans la seule section « Bières » des annexes D (L)"],
         o_assiette, [20, 16, 18, 22, 22, 26]),
        ("3. Bloc bière des annexes",
         ["Article, tel que l'annexe l'écrit", "Quantité vendue portée",
          "Dose (cl)", "Volume porté (cl)", "Quantité x dose (cl)",
          "Écart (cl)", "Proportion portée"],
         o_annexe, [60, 14, 10, 14, 14, 10, 14]),
        ("4. Cascade du service",
         ["Grandeur", "Valeur", "Unité", "Où elle est lue, et contrôle"],
         o_cascade_serv, [42, 14, 10, 80]),
        ("5. Ce que vaut un point",
         ["Grandeur", "Valeur", "Unité", "Détail"],
         o_sensi, [52, 14, 14, 70]),
        ("6. Événements-fût",
         ["Exercice", "Fût acheté (L)", "Fûts de 8 L", "Bière servie (L)",
          "Litres servis par fût acheté", "Mises en perce pour 100 L servis",
          "Mises en perce si fûts de 30 L", "Mises en perce en plus"],
         o_evt, [20, 14, 12, 14, 16, 18, 16, 14]),
        ("7. Grille par événement",
         ["Perte par événement-fût", "Sur 262 fûts de 8 L (L)",
          "% de la bière servie (1 205,0 L)", "% du fût acheté",
          "Si l'exploitation tournait en 30 L (L)", "% de la bière servie"],
         o_grille, [22, 18, 20, 16, 22, 18]),
        ("8. Calendrier",
         ["Exercice", "Premier service", "Dernier service",
          "Jours avec vente de bière", "Bière servie (L)", "Moyenne par jour (L)",
          "Médiane par jour (L)", "Maximum d'un jour (L)", "Jours sous 1 L",
          "Jours sous 8 L (un fût)", "Plus longue fermeture"],
         o_cal, [20, 14, 14, 14, 14, 14, 14, 14, 12, 14, 30]),
        ("9. Postes des abattements",
         ["Abattement", "Postes qu'il couvre, selon la pièce",
          "Citation et référence", "Équivalent en litres de fût"],
         o_postes, [34, 34, 80, 16]),
    ]

    chemin = ecrire_xlsx(
        os.path.join(PIECES, "R1-biere-matiere-et-assiette.xlsx"),
        "Bière pression : la freinte établie par la matière, et l'assiette du taux",
        "Réponse au reproche des pages 61 et 83. Toutes les grandeurs sont "
        "comptées sur les factures du fournisseur, sur le détail des tickets "
        "remis par le service (annexes C1 à C3) et sur ses annexes finales. "
        "Aucune dose n'est déduite d'un bilan matière. Script : "
        "scripts/reponse1-biere-matiere.py",
        onglets)

    synth = {
        "futs": round(tot_futs), "achat_l": tot_achat,
        "assiette_doses_service_l": round(tot_serv, 2),
        "assiette_doses_defense_l": round(tot_nous, 2),
        "assiette_section_bieres_l": round(tot_sect, 2),
        "assiette_retenue_l": 1205.0,
        "contenance_verres_l": round(sum(v_verre.values()), 2),
        "unites_de_vente": round(tot_unites, 1),
        "tickets_avec_biere": tot_tickets,
        "lignes_de_caisse": tot_lignes,
        "litres_servis_par_fut": round(tot_nous / tot_futs, 2),
        "perces_pour_100_l": round(100 * tot_futs / tot_nous, 2),
        "perces_si_30l": round(tot_achat / FUT_STANDARD_L, 1),
        "jours_avec_biere": len(tj),
        "jours_sous_1l": sum(1 for v in tj if v < 1.0),
        "jours_atteignant_un_fut": sum(1 for v in tj if v >= FUT_L),
        "mediane_jour_l": round(tj[len(tj) // 2], 2),
        "max_jour_l": round(tj[-1], 2),
        "annexe_finale_ecart_cl": ecart_net,
        "annexe_finale_controle_pct": round(100 * ecart_net / af["net_cl"], 2),
        "point_de_freinte_eur_liquides": round(point_eur, 2),
        "point_de_freinte_eur_amplifie": round(point_eur * ampli, 2),
        "piece": os.path.relpath(chemin, ROOT),
    }
    print(json.dumps(synth, ensure_ascii=False, indent=1))


def ecrire_xlsx(path, titre, sous_titre, onglets):
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter

    wb = openpyxl.Workbook()
    white_bold = Font(bold=True, color="FFFFFF")
    head = PatternFill("solid", fgColor="0F766E")
    sub = PatternFill("solid", fgColor="E6F4F1")
    thin = Side(style="thin", color="CBD5E1")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    right = Alignment(horizontal="right")

    first = True
    for nom, colonnes, lignes, largeurs in onglets:
        ws = wb.active if first else wb.create_sheet(nom)
        if first:
            ws.title = nom
            first = False
        ws.append([titre])
        ws["A1"].font = Font(bold=True, size=13)
        ws.append([sous_titre])
        ws["A2"].font = Font(italic=True, size=9, color="64748B")
        ws.append([])
        hrow = 4
        ws.append(colonnes)
        for c in range(1, len(colonnes) + 1):
            cell = ws.cell(row=hrow, column=c)
            cell.font = white_bold
            cell.fill = head
            cell.alignment = Alignment(horizontal="center", vertical="center",
                                       wrap_text=True)
            cell.border = border
        for ln in lignes:
            ws.append(ln)
        for r in range(hrow + 1, hrow + 1 + len(lignes)):
            for c in range(1, len(colonnes) + 1):
                cell = ws.cell(row=r, column=c)
                cell.border = border
                cell.alignment = Alignment(wrap_text=True, vertical="top")
                if isinstance(cell.value, (int, float)):
                    cell.alignment = right
        if lignes and str(lignes[-1][0]).upper().startswith("TOTAL"):
            for c in range(1, len(colonnes) + 1):
                ws.cell(row=hrow + len(lignes), column=c).font = Font(bold=True)
                ws.cell(row=hrow + len(lignes), column=c).fill = sub
        for i, w in enumerate(largeurs, start=1):
            ws.column_dimensions[get_column_letter(i)].width = w
        ws.freeze_panes = f"A{hrow + 1}"

    os.makedirs(os.path.dirname(path), exist_ok=True)
    wb.save(path)
    return path


if __name__ == "__main__":
    main()
