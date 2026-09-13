#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REPONSE 1 - PRODUCTEUR UNIQUE de la cascade des 10 622 L et de l'itemisation.

===========================================================================
CE FICHIER EST LA SEULE SOURCE DE VERITE DE LA CASCADE.
Aucun autre script ne doit figer un poste en dur. Les consommateurs
(reponse1-cascade-coherence.py, reponse1-abattements.py,
reponse1-coefficients.py, reponse1-cascade.py) lisent le JSON produit ici :
  src/data/reponse1Calculs/cascade-10622.json
===========================================================================

Deux doubles comptages ont ete etablis et sont corriges ici.

1. BIERE : 296,00 L comptes deux fois.
   Quatre libelles de caisse (Panache, Monaco, Picon biere, Pinte Picon)
   figurent SIMULTANEMENT dans mp.CAISSE2CANON (qui alimente le poste
   « vendu au verre » avec la CONTENANCE ENTIERE du verre, mappee sur
   « Fut Affligem ») et dans CAISSE_COCKTAIL (qui alimente le poste « vendu
   en cocktails » avec la recette : biere + limonade / grenadine / Picon).
   Le meme verre est donc compte une fois en entier et une seconde fois
   ingredient par ingredient. Verification : le poste « vendu au verre »
   porte 1 292,86 L de Fut Affligem et le poste cocktails 208,14 L de plus,
   soit 1 501,00 L de biere, quand la page « perte de biere » etablit que
   1 205,0 L seulement sont sortis du fut.
   Correction : retirer du poste « vendu au verre » la contenance des quatre
   articles mixtes (296,00 L). Leur alcool reel (208,14 L de biere +
   28,30 L de Picon) reste porte, une seule fois, par le poste cocktails.

2. OFFERTS : 25,75 L comptes deux fois.
   Le poste « aperitifs offerts » (39,72 L) suppose des offerts NON
   enregistres. Or extract_items() du pipeline additionne les quantites de
   l'annexe D sans regarder le prix unitaire : les lignes a 0,00 EUR sont
   deja dans « vendu au verre » et « vendu en cocktails ».
   Recompte ici, annexe D : 27,25 L d'alcool vendus a 0,00 EUR, dont 1,50 L
   de contenance d'articles mixtes deja retiree par la correction 1, soit
   25,75 L nets. Le poste tombe de 39,72 L a 13,97 L.

Un troisieme point est integre : la DOSE DE PICON. Deux doses circulaient,
2 cl / 4 cl (page « perte de biere ») et 4 cl / 8 cl (cocktailsComposition).
Seule la seconde boucle sur les achats : Picon achete 72,0 L = 28,30 L de
cocktails + 43,70 L de consommation du chef, au centilitre, stock nul.
La dose retenue est donc 4 cl au demi et 8 cl a la pinte, ce qui ramene
l'assiette de la freinte de 1 219,2 L a 1 205,0 L et la freinte a 10 % de
121,9 L a 120,5 L.

Entrees (lecture seule) :
  src/data/incertitudeDisparu/base_disparu_ajuste2.json
  src/data/calculsBoissons/boissonsHorsCocktail.json
  src/data/calculsBoissons/cocktailsComposition.json
  src/data/reponse1Calculs/cremant-fourchette.json
  src/data/reponse1Calculs/sur-versement-fourchette.json
  src/data/boissonsPageData.json                      (prix de revente)
  public/documents/caisse-enregistreuse/ANNEXE-D{1,2,3}*.xls
  public/documents/vins-boissons/_mapping_noms.py     (mapping caisse)

Sorties :
  src/data/reponse1Calculs/cascade-10622.json
  public/documents/pieces-reponse-1/R1-cascade-bilan-matiere.xlsx
  public/documents/pieces-reponse-1/R1-cascade-doubles-comptages.csv

Execution : python3 scripts/reponse1-cascade-valeurs.py
Ce script n'ecrit JAMAIS dans src/data/reponse1/ (les pages).
"""
import csv
import importlib.util
import json
import os
import re

ICI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(ICI, ".."))
DATA = os.path.join(ROOT, "src", "data")
CALC = os.path.join(DATA, "reponse1Calculs")
CAISSE = os.path.join(ROOT, "public", "documents", "caisse-enregistreuse")
VINS = os.path.join(ROOT, "public", "documents", "vins-boissons")
PIECES = os.path.join(ROOT, "public", "documents", "pieces-reponse-1")

EXOS = ["2022-2023", "2023-2024", "2024-2025"]
JOURS_SERVICE = 662
DOSE_APERITIF_CL = 6.0

# Avoirs FCBS stockes en quantite positive et comptes a tort en achat
# (cf. src/data/incertitudeDisparu/14_synthese_perte_reelle.py).
AVOIRS = {"Cidre Brut": 22.5, "Bourgogne Aligoté maison": 10.0, "Grand Marnier": 2.1}

# Les quatre libelles de caisse presents a la fois dans CAISSE2CANON et dans
# CAISSE_COCKTAIL. Les formats sont ceux de boissonsHorsCocktail.json.
FORMATS_MIXTES = ["Panaché 25cl", "Monaco 25cl", "Demi+Picon 25cl", "Pinte+Picon 50cl"]
LIBELLES_MIXTES = ["Panaché", "Monaco", "Picon bière", "Pinte Picon"]

# Alcool de cuisine et alcool des menus, plafonne aux achats factures.
# Le marc de Bourgogne fait exception : il est plafonne sur les trois exercices
# pris ensemble aux 210 cl sortis du stock (280 cl factures sous le code 550252,
# Jacoulot 45 degres, moins la bouteille inventoriee au 31/03/2025), et non aux
# 5,58 L calcules. Le marc du Jura (code 520096) est un autre produit ; tant que
# la gerante n'a pas dit lequel des deux entre dans le baba, la demande reste
# bornee aux achats du produit nomme. Concession assumee de 3,48 L.
# La premiere colonne (le calcule) n'est jamais modifiee par un plafonnement :
# elle reste le produit du nombre de plats par la dose, comme 119,07 L de
# Calvados en face de 73,00 L retenus.
# Producteur : scripts/reponse1-alcool-cuisine.py, feuille « 5-Solde demande »
# de R1-alcool-cuisine-controles.xlsx. Repris ici en dur parce que ce script
# ecrit au niveau module et ne peut donc pas etre importe ; la fonction
# verifier_cuisine() relit la piece publiee et signale toute divergence.
CUISINE_PLAFONNE = [
    ("Ravelin", 251.80, 251.80),
    ("Macvin", 177.51, 177.51),
    ("Arbois Vin Jaune", 124.48, 124.48),
    ("Calvados", 119.07, 73.00),
    ("Porto", 70.74, 68.27),
    ("Crème de Cassis", 18.67, 18.67),
    ("Bailey's", 15.28, 15.28),
    ("Grand Marnier", 7.42, 5.96),
    ("Marc de Bourgogne", 5.58, 2.10),
    ("Liqueur de Poire", 4.07, 4.07),
]

# Recapitulation par exercice du service (proposition du 18/05/2026, p. 52).
# « cinq_pct » = chacun des trois abattements de 5 % sur les liquides.
FORFAIT_5PCT = [8917.07, 8450.72, 8253.27]

VIN = {"vin_blanc", "vin_rouge", "vin_rose", "vin", "vin_de_liqueur"}
SPIRIT = {"aperitif", "liqueur", "eau_de_vie", "spiritueux", "digestif"}


# ---------------------------------------------------------------------------
# Lectures
# ---------------------------------------------------------------------------
def lire(chemin):
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)


def mapping_caisse():
    """Charge mp.CAISSE2CANON et CAISSE_COCKTAIL du pipeline boissons."""
    spec = importlib.util.spec_from_file_location("mpnoms", os.path.join(VINS, "_mapping_noms.py"))
    mp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mp)
    src = open(os.path.join(VINS, "_pipeline_boissons_complet.py"), encoding="utf-8").read()
    cc = eval(re.search(r"CAISSE_COCKTAIL=(\{.*?\})\n", src, re.S).group(1))
    return mp, cc


def base_alcool():
    base = lire(os.path.join(DATA, "incertitudeDisparu", "base_disparu_ajuste2.json"))
    return [b for b in base["boissons"] if b.get("conso_complete") is True]


def offerts_zero_euro(mp, cocktails_recettes, cocktails_map, noms_alcool):
    """Recompte, dans l'annexe D, l'alcool des lignes a prix unitaire nul.

    Renvoie (total_l, part_deja_retiree_par_la_correction_biere_l, detail)."""
    import xlrd

    fichiers = {
        "2022-2023": "ANNEXE-D1_synthese-produit_2022-2023.xls",
        "2023-2024": "ANNEXE-D2_synthese-produit_2023-2024.xls",
        "2024-2025": "ANNEXE-D3_synthese-produit_2024-2025.xls",
    }
    norm = lambda s: str(s).replace("\xa0", " ").strip()
    qte = {}
    nb_lignes = 0
    nb_articles = 0.0
    for exo, fn in fichiers.items():
        sh = xlrd.open_workbook(os.path.join(CAISSE, fn)).sheet_by_index(0)
        section = None
        for r in range(1, sh.nrows):
            a, b = norm(sh.cell_value(r, 0)), norm(sh.cell_value(r, 1))
            if a and not b and a != "Ref_prd":
                section = a
                continue
            if not (b and b != "Lib_ticket" and section):
                continue
            if "TOTAL" in section.upper() or "RAPPORT" in section.upper():
                continue
            f = lambda c: (float(sh.cell_value(r, c)) if str(sh.cell_value(r, c)).strip() else 0.0)
            try:
                q, pu, ca = f(4), f(2), f(5)
            except ValueError:
                continue
            if pu == 0 and ca == 0 and q:
                qte[b] = qte.get(b, 0.0) + q
                nb_lignes += 1
                nb_articles += q
    detail = {}
    mixte_l = 0.0
    for lab, q in qte.items():
        if lab in mp.CAISSE2CANON:
            canon, _fmt, vol = mp.CAISSE2CANON[lab]
            if canon in noms_alcool:
                v = q * vol / 100.0
                detail[("verre", canon)] = detail.get(("verre", canon), 0.0) + v
                if lab in LIBELLES_MIXTES:
                    mixte_l += v
        if lab in cocktails_map:
            for ig in cocktails_recettes[cocktails_map[lab]]["ingredients"]:
                if ig["categorie"] not in ("alcool", "biere"):
                    continue
                canon = mp.INGREDIENT2CANON.get(ig["nom"], ig["nom"])
                if canon in noms_alcool:
                    detail[("cocktail", canon)] = detail.get(("cocktail", canon), 0.0) + q * ig["cl"] / 100.0
    total = sum(detail.values())
    return total, mixte_l, detail, nb_lignes, nb_articles


def verifier_cuisine():
    """Relit R1-alcool-cuisine-controles.xlsx et signale toute divergence."""
    chemin = os.path.join(PIECES, "R1-alcool-cuisine-controles.xlsx")
    if not os.path.exists(chemin):
        return None
    try:
        from openpyxl import load_workbook
        ws = load_workbook(chemin, data_only=True)["5-Solde demandé"]
    except Exception:
        return None
    for ligne in ws.iter_rows(values_only=True):
        if ligne and str(ligne[0]).strip() == "TOTAL":
            return float(ligne[1]), float(ligne[2])
    return None


# ---------------------------------------------------------------------------
# Construction de la cascade
# ---------------------------------------------------------------------------
def construire():
    mp, cocktails_map = mapping_caisse()
    recettes = lire(os.path.join(DATA, "calculsBoissons", "cocktailsComposition.json"))["cocktails"]
    alc = base_alcool()
    noms_alcool = {b["nom"] for b in alc}

    achats = round(sum(b["achats_l"] for b in alc) - sum(AVOIRS.values()), 2)
    verre_brut = round(sum(b["conso"]["seches_l"] for b in alc), 2)
    cocktails = round(sum(b["conso"]["cocktails_l"] for b in alc), 2)
    plats = round(sum(b["conso"]["plats_l"] for b in alc), 2)
    menus = round(sum(b["conso"]["menu_moyen_l"] for b in alc), 2)
    stock = round(sum(b["stock_final_l"] for b in alc), 2)
    chef = round(sum((b.get("conso_staff_l") or {}).get("moyen", 0.0) for b in alc), 2)

    # --- double comptage 1 : contenance des quatre articles mixtes -----------
    hc = lire(os.path.join(DATA, "calculsBoissons", "boissonsHorsCocktail.json"))["boissons"]
    mixtes = []
    for x in hc:
        if x["nom_canonique"] == "Fût Affligem" and x["format_service"] in FORMATS_MIXTES:
            mixtes.append(x)
    double_biere = round(sum(x["total_volume_l"] for x in mixtes), 2)
    assert abs(double_biere - 296.0) < 0.05, double_biere

    # alcool reellement porte par ces quatre articles, via la recette
    alcool_mixte = {}
    for x in mixtes:
        lab = [l for l in LIBELLES_MIXTES if mp.CAISSE2CANON[l][1] == x["format_service"]][0]
        for ig in recettes[cocktails_map[lab]]["ingredients"]:
            if ig["categorie"] in ("alcool", "biere"):
                canon = mp.INGREDIENT2CANON.get(ig["nom"], ig["nom"])
                alcool_mixte[canon] = alcool_mixte.get(canon, 0.0) + x["total_quantite"] * ig["cl"] / 100.0

    verre = round(verre_brut - double_biere, 2)

    # --- double comptage 2 : offerts deja enregistres a 0 EUR ---------------
    zero_l, zero_mixte, zero_detail, zero_lignes, zero_articles = offerts_zero_euro(
        mp, recettes, cocktails_map, noms_alcool)
    zero_net = round(zero_l - zero_mixte, 2)
    offerts_hypothese = round(JOURS_SERVICE * DOSE_APERITIF_CL / 100.0, 2)
    offerts = round(max(0.0, offerts_hypothese - zero_net), 2)

    # --- cuisine et alcool des menus, plafonnes -----------------------------
    cuisine_calc = round(sum(c[1] for c in CUISINE_PLAFONNE), 2)
    cuisine = round(sum(c[2] for c in CUISINE_PLAFONNE), 2)
    assert abs(cuisine_calc - (plats + menus)) < 0.05, (cuisine_calc, plats + menus)
    ctrl = verifier_cuisine()
    if ctrl and (abs(ctrl[0] - cuisine_calc) > 0.05 or abs(ctrl[1] - cuisine) > 0.05):
        print("  ATTENTION : R1-alcool-cuisine-controles.xlsx donne %s / %s" % ctrl)

    # --- cremant borne par le stock -----------------------------------------
    cre = lire(os.path.join(CALC, "cremant-fourchette.json"))["exercices"]
    cremant = round(sum(x["ecart_a_expliquer_cl"] for x in cre.values()) / 100.0, 2)
    cremant_exo = {e: round(cre[e]["ecart_a_expliquer_cl"] / 100.0, 2) for e in EXOS}

    # --- sur-versement ------------------------------------------------------
    sv = lire(os.path.join(CALC, "sur-versement-fourchette.json"))
    surversement = round(sv["variantes"]["retenu_l"], 2)
    sv_exo = {e: 0.0 for e in EXOS}
    for b in sv["boissons"]:
        for lg in b["lignes"]:
            sv_exo[lg["exercice"]] += lg["surversement_retenu_l"]
    sv_exo = {e: round(v, 2) for e, v in sv_exo.items()}
    sv_regimes = sv["regimes_total"]

    # --- degustation --------------------------------------------------------
    degustation = 125.84
    degustation_exo = {"2022-2023": 35.36, "2023-2024": 45.14, "2024-2025": 45.34}
    assert abs(sum(degustation_exo.values()) - degustation) < 0.01

    # --- freinte biere, dose de Picon alignee sur 4 / 8 cl ------------------
    q = {x["format_service"]: x["total_quantite"] for x in hc if x["nom_canonique"] == "Fût Affligem"}
    qe = {x["format_service"]: {e: x["par_periode"][e]["quantite"] for e in EXOS}
          for x in hc if x["nom_canonique"] == "Fût Affligem"}
    part_biere_cl = {"Pression 25cl": 25.0, "Pinte 50cl": 50.0, "Panaché 25cl": 12.5,
                     "Monaco 25cl": 12.5, "Demi+Picon 25cl": 21.0, "Pinte+Picon 50cl": 42.0}
    biere_servie = round(sum(q[f] * c / 100.0 for f, c in part_biere_cl.items()), 2)
    biere_exo = {e: round(sum(qe[f][e] * c / 100.0 for f, c in part_biere_cl.items()), 2)
                 for e in EXOS}
    freinte_exo = {e: round(0.10 * biere_exo[e], 2) for e in EXOS}
    freinte = round(0.10 * biere_servie, 2)
    # controle : la biere servie doit etre egale a la pression et aux pintes
    # pures du poste « vendu au verre » corrige, plus la biere des cocktails.
    biere_pure = round((q["Pression 25cl"] * 25.0 + q["Pinte 50cl"] * 50.0) / 100.0, 2)
    assert abs(biere_pure + alcool_mixte["Fût Affligem"] - biere_servie) < 0.05

    postes = [
        dict(cle="verre", libelle="Vendu au verre", litres=verre, nature="mesure",
             source="Détail des tickets, annexes C1 à C3, hors panaché, Monaco et Picon "
                    "bière, dont l’alcool est porté par la ligne cocktails",
             page="Doses figées", slug="recon-1-doses-figees"),
        dict(cle="cocktails", libelle="Vendu en cocktails", litres=cocktails, nature="calcul",
             source="Cocktails vendus en caisse x recette de la carte",
             page="Doses figées", slug="recon-1-doses-figees"),
        dict(cle="cuisine", libelle="Cuisine et alcool des menus", litres=cuisine, nature="calcul",
             source="Plats et menus vendus en caisse x dose, plafonnés aux achats facturés",
             page="Alcool de cuisine", slug="recon-5-alcool-cuisine"),
        dict(cle="cremant", libelle="Crémant non vendu", litres=cremant, nature="calcul",
             source="Bilan matière jour par jour, borné par le stock retenu par le service",
             page="Crémant", slug="recon-3-cremant-vendu"),
        dict(cle="surversement", libelle="Sur-versement au verre", litres=surversement,
             nature="estime",
             source="Taux publiés appliqués au seul volume versé à la main, borné par le stock",
             page="Sur-versement", slug="sur-versement-au-verre"),
        dict(cle="degustation", libelle="Dégustation offerte", litres=degustation, nature="mesure",
             source="Notes relevées une à une dans l’annexe C : 6 292 dégustations de 2 cl",
             page="Dégustation", slug="degustation-offerte"),
        dict(cle="biere", libelle="Freinte technique de la bière", litres=freinte, nature="estime",
             source="10 %% de la bière réellement sortie du fût (%s L lus en caisse, "
                    "Picon à 4 cl et 8 cl)" % f"{biere_servie:.1f}".replace(".", ","),
             page="Perte de bière", slug="perte-de-biere"),
        dict(cle="chef", libelle="Consommation du chef", litres=chef, nature="estime",
             source="Base journalière déclarée x jours de service (macvin 99,3 L, Picon 43,7 L)",
             page="Consommation du personnel", slug="recon-7-conso-personnel"),
        dict(cle="offerts", libelle="Offerts non enregistrés en caisse", litres=offerts,
             nature="estime",
             source="Un apéritif de 6 cl par jour de service, déduction faite des %s L "
                    "d’alcool déjà enregistrés à 0,00 € dans la caisse"
                    % f"{zero_net:.2f}".replace(".", ","),
             page="Abattements", slug="recon-8-abattements"),
        dict(cle="stock", libelle="Stock final", litres=stock, nature="mesure",
             source="Inventaire de clôture", page="Variation de stock",
             slug="recon-9-variation-de-stock"),
    ]
    for p in postes:
        p["litres_arrondi"] = arrondi_prudent(p["litres"], p["nature"])

    attribue = round(sum(p["litres"] for p in postes), 2)
    residu = round(achats - attribue, 2)
    attribue_r = sum(p["litres_arrondi"] for p in postes)
    residu_r = int(round(achats)) - attribue_r

    return dict(
        achats=achats, postes=postes, attribue=attribue, residu=residu,
        attribue_arrondi=attribue_r, residu_arrondi=residu_r,
        verre_brut=verre_brut, double_biere=double_biere, mixtes=mixtes,
        alcool_mixte=alcool_mixte, biere_servie=biere_servie, biere_pure=biere_pure,
        zero_l=zero_l, zero_mixte=zero_mixte, zero_net=zero_net, zero_detail=zero_detail,
        zero_lignes=zero_lignes, zero_articles=zero_articles,
        offerts_hypothese=offerts_hypothese,
        cuisine_calc=cuisine_calc, plats=plats, menus=menus,
        cremant_exo=cremant_exo, sv_exo=sv_exo, sv_regimes=sv_regimes,
        degustation_exo=degustation_exo, biere_exo=biere_exo, freinte_exo=freinte_exo,
    )


def arrondi_prudent(v, nature):
    """Arrondi au litre. En cas d’égalité exacte (x,5) on arrondit vers le bas
    pour un poste estimé : un poste estimé ne doit jamais être majoré par un
    arrondi. Les autres postes suivent l’arrondi usuel."""
    if nature == "estime" and abs(v - int(v) - 0.5) < 1e-9:
        return int(v)
    return int(round(v + 1e-9))


# ---------------------------------------------------------------------------
# Valorisation en euros
# ---------------------------------------------------------------------------
def prix_de_revente():
    bpd = lire(os.path.join(DATA, "boissonsPageData.json"))
    bo = bpd["disparuParBoisson"]

    def moyenne(cats):
        n = d = 0.0
        for b in bo:
            if b.get("categorie") in cats and b.get("prix_revente"):
                n += b["conso_l"] * b["prix_revente"]
                d += b["conso_l"]
        return n / d

    unitaire = {b["nom"]: b.get("prix_revente") for b in bo}
    categorie = {b["nom"]: b.get("categorie") for b in bo}
    # prix moyen de l’alcool acheté, pondéré par les litres achetés : sert à
    # valoriser le résidu, qui n’est par construction affecté à aucun produit.
    n = d = 0.0
    for b in bo:
        if b.get("prix_revente") and b.get("achat_l"):
            n += b["achat_l"] * b["prix_revente"]
            d += b["achat_l"]
    return dict(vin=moyenne(VIN), spirit=moyenne(SPIRIT),
                cremant=unitaire["Crémant du Jura"], biere=unitaire["Fût Affligem"],
                moyen_achats=(n / d) if d else moyenne(VIN),
                unitaire=unitaire, categorie=categorie)


def valoriser(c, prix):
    """Itemisation en litres et en euros, sur les trois assiettes."""
    p = {x["cle"]: x for x in c["postes"]}
    pv, ps = prix["vin"], prix["spirit"]

    # sur-versement : prix pondéré par les régimes de service, méthode
    # inchangée depuis la pièce de juillet, appliquée au mix corrigé.
    r = c["sv_regimes"]
    sv_vin, sv_sp = r["sv_vin_l"], r["sv_spiritueux_l"] + r["sv_cocktails_l"]
    sv_eur = sv_vin * pv + sv_sp * ps
    sv_prix = sv_eur / (sv_vin + sv_sp)
    sv_eur = p["surversement"]["litres"] * sv_prix

    # chef et offerts : valorisation du fichier 56 remis au service
    bpd = lire(os.path.join(DATA, "boissonsPageData.json"))
    lignes = {l["poste"][:6]: l for l in bpd["personnel"]["lignes"]}
    chef_eur = lignes["Macvin"]["ca_equivalent_eur"] + lignes["Picon "]["ca_equivalent_eur"]
    ap = [l for l in bpd["offerts"]["lignes"] if l["litres"]][0]
    cafes = [l for l in bpd["offerts"]["lignes"] if not l["litres"]][0]
    prix_aperitif = ap["ca_equivalent_eur"] / ap["litres"]

    # clé de répartition par exercice des postes journaliers (jours de service)
    jours = [bpd["consoParPeriode"][e]["personnel_l"] for e in EXOS]

    def prorata(total, cles):
        s = sum(cles)
        return [total * k / s for k in cles]

    def mesure(d):
        return [d[e] for e in EXOS]

    item = [
        ("Consommation du chef (Picon et macvin)", p["chef"]["litres"], chef_eur,
         "valorisation du fichier 56 remis au service", prorata(p["chef"]["litres"], jours)),
        ("Offerts non enregistrés en caisse", p["offerts"]["litres"],
         p["offerts"]["litres"] * prix_aperitif,
         f"{prix_aperitif:.2f} €/L (prix de revente d’un apéritif)",
         prorata(p["offerts"]["litres"], jours)),
        ("Cafés offerts (sans volume d’alcool)", 0.0, cafes["ca_equivalent_eur"],
         "3 cafés par jour x 662 jours, fichier 56", [0.0, 0.0, 0.0]),
        ("Sur-versement au verre", p["surversement"]["litres"], sv_eur,
         f"{sv_prix:.2f} €/L (moyenne pondérée des régimes servis)",
         prorata(p["surversement"]["litres"], mesure(c["sv_exo"]))),
        ("Crémant non vendu", p["cremant"]["litres"], p["cremant"]["litres"] * prix["cremant"],
         f"{prix['cremant']:.2f} €/L", mesure(c["cremant_exo"])),
        ("Dégustation offerte", p["degustation"]["litres"], p["degustation"]["litres"] * pv,
         f"{pv:.2f} €/L (prix de revente moyen des vins)", mesure(c["degustation_exo"])),
        ("Freinte technique de la bière", p["biere"]["litres"], p["biere"]["litres"] * prix["biere"],
         f"{prix['biere']:.2f} €/L (fût Affligem)", mesure(c["freinte_exo"])),
    ]
    a_l = sum(x[1] for x in item)
    a_e = sum(x[2] for x in item)

    # cuisine et alcool des menus, produit par produit
    cuis = []
    for nom, _calc, plaf in CUISINE_PLAFONNE:
        pu = prix["unitaire"].get(nom)
        if not pu:
            pu = ps if prix["categorie"].get(nom) in SPIRIT else pv
        cuis.append((nom, plaf, plaf * pu, f"{pu:.2f} €/L"))
    b_l = a_l + sum(x[1] for x in cuis)
    b_e = a_e + sum(x[2] for x in cuis)

    # arrondis derives des POSTES arrondis, pour que toutes les additions du
    # dossier tombent juste : A + cuisine = B, A + residu = C, B + residu = D.
    pa = {x["cle"]: x["litres_arrondi"] for x in c["postes"]}
    a_r = pa["cremant"] + pa["surversement"] + pa["degustation"] + pa["biere"] + pa["chef"] + pa["offerts"]
    b_r = a_r + pa["cuisine"]
    c_r = a_r + c["residu_arrondi"]
    d_r = b_r + c["residu_arrondi"]

    res_l = c["residu"]
    res_e = res_l * prix["moyen_achats"]
    c_l = a_l + res_l
    c_e = a_e + res_e
    d_l = b_l + res_l
    d_e = b_e + res_e

    forfait_l = 0.15 * c["achats"]
    forfait_e = 3 * sum(FORFAIT_5PCT)

    return dict(
        itemisation=item, cuisine=cuis,
        assiettes=[
            dict(cle="A", libelle="Postes itemisés, hors cuisine et menus",
                 litres=a_l, arrondi=a_r, euros=a_e),
            dict(cle="B", libelle="Postes itemisés, cuisine et alcool des menus compris",
                 litres=b_l, arrondi=b_r, euros=b_e),
            dict(cle="C", libelle="Perte d’exploitation totale, hors cuisine et menus "
                                  "(postes itemisés et résidu de perte pure)",
                 litres=c_l, arrondi=c_r, euros=c_e),
            dict(cle="D", libelle="Alcool acheté et non vendu, cuisine et menus compris",
                 litres=d_l, arrondi=d_r, euros=d_e),
        ],
        forfait_l=forfait_l, forfait_eur=forfait_e,
        prix_surversement=sv_prix, prix_residu=prix["moyen_achats"],
        prix_vin=pv, prix_spirit=ps, prix_cremant=prix["cremant"], prix_biere=prix["biere"],
        prix_aperitif=prix_aperitif,
    )


# ---------------------------------------------------------------------------
# Ecritures
# ---------------------------------------------------------------------------
def ecrire_json(c, v):
    nat = {}
    for n in ("mesure", "calcul", "estime"):
        nat[n] = dict(
            litres=round(sum(p["litres"] for p in c["postes"] if p["nature"] == n), 2),
            litres_arrondi=sum(p["litres_arrondi"] for p in c["postes"] if p["nature"] == n))
    nat["residu"] = dict(litres=c["residu"], litres_arrondi=c["residu_arrondi"])
    caisse = round(nat["mesure"]["litres"] + nat["calcul"]["litres"], 2)
    caisse_r = nat["mesure"]["litres_arrondi"] + nat["calcul"]["litres_arrondi"]
    revendu = round(c["postes"][0]["litres"] + c["postes"][1]["litres"], 2)
    revendu_r = c["postes"][0]["litres_arrondi"] + c["postes"][1]["litres_arrondi"]

    doc = {
        "description": "Cascade des 10 622 L d'alcool achetés sur les trois exercices "
                       "vérifiés, et itémisation des abattements. SOURCE UNIQUE : produite "
                       "par scripts/reponse1-cascade-valeurs.py. Aucun autre script ni "
                       "aucune page ne doit figer ces valeurs.",
        "producteur": "scripts/reponse1-cascade-valeurs.py",
        "achats_l": c["achats"],
        "postes": [
            {"cle": p["cle"], "libelle": p["libelle"], "litres": p["litres"],
             "litres_arrondi": p["litres_arrondi"], "nature": p["nature"],
             "source": p["source"], "page": p["page"], "slug": p["slug"]}
            for p in c["postes"]],
        "attribue_l": c["attribue"], "attribue_arrondi_l": c["attribue_arrondi"],
        "attribue_pct": round(100 * c["attribue"] / c["achats"], 2),
        "residu_l": c["residu"], "residu_arrondi_l": c["residu_arrondi"],
        "residu_pct": round(100 * c["residu"] / c["achats"], 2),
        "nature": nat,
        "part_caisse_l": caisse,
        "part_caisse_arrondi_l": caisse_r,
        "part_caisse_pct": round(100 * caisse_r / c["achats"], 2),
        "revendu_l": revendu,
        "revendu_arrondi_l": revendu_r,
        "part_revendue_pct": round(100 * revendu / c["achats"], 4),
        "doubles_comptages": {
            "biere": {
                "litres": c["double_biere"],
                "explication": "Contenance des quatre articles mixtes (panaché, Monaco, "
                               "Picon bière, pinte Picon), comptée dans « vendu au verre » "
                               "alors que leur alcool est déjà porté par « vendu en cocktails ».",
                "verre_avant": c["verre_brut"], "verre_apres": c["postes"][0]["litres"],
                "alcool_reel": {k: round(x, 2) for k, x in c["alcool_mixte"].items()},
                "biere_servie_l": c["biere_servie"],
                "biere_pression_et_pintes_l": c["biere_pure"],
            },
            "offerts": {
                "litres_bruts": round(c["zero_l"], 2),
                "dont_articles_mixtes": round(c["zero_mixte"], 2),
                "litres_nets": c["zero_net"],
                "lignes_annexe_d": c["zero_lignes"], "articles": c["zero_articles"],
                "poste_avant": c["offerts_hypothese"], "poste_apres": c["postes"][8]["litres"],
            },
        },
        "cuisine": {
            "calcule_l": c["cuisine_calc"], "plafonne_l": c["postes"][2]["litres"],
            "carte_l": c["plats"], "menus_l": c["menus"],
            "supplement_demande_au_service_l": 173.38,
            "note": "173,38 L est le supplément demandé au service une fois déduits ses "
                    "propres retranchements (repères D, E, G, Q). Ce n’est pas un poste de "
                    "la cascade et il ne s’y ajoute jamais.",
        },
        "par_exercice": {
            "cremant_l": c["cremant_exo"], "surversement_l": c["sv_exo"],
            "degustation_l": c["degustation_exo"],
        },
        "forfait_15pct": {
            "litres": round(v["forfait_l"], 2),
            "euros_ca_boissons": round(v["forfait_eur"], 2),
            "detail_5pct_par_exercice": FORFAIT_5PCT,
        },
        "prix_de_revente_eur_par_l": {
            "vins": round(v["prix_vin"], 2), "spiritueux": round(v["prix_spirit"], 2),
            "cremant": round(v["prix_cremant"], 2), "biere": round(v["prix_biere"], 2),
            "aperitif_offert": round(v["prix_aperitif"], 2),
            "sur_versement_pondere": round(v["prix_surversement"], 2),
            "residu_moyenne_des_achats": round(v["prix_residu"], 2),
        },
        "itemisation": [
            {"poste": n, "litres": round(l, 2), "euros": round(e, 2), "base": b,
             "litres_par_exercice": {ex: round(val, 2) for ex, val in zip(EXOS, px)},
             "euros_par_exercice": {ex: round(e * val / l if l else e / 3.0, 2)
                                    for ex, val in zip(EXOS, px)}}
            for n, l, e, b, px in v["itemisation"]],
        "cuisine_valorisee": [
            {"alcool": n, "litres": round(l, 2), "euros": round(e, 2), "base": b}
            for n, l, e, b in v["cuisine"]],
        "assiettes": [
            {"cle": a["cle"], "libelle": a["libelle"],
             "litres": round(a["litres"], 2), "litres_arrondi": a["arrondi"],
             "pct_achats": round(100 * a["litres"] / c["achats"], 2),
             "euros": round(a["euros"], 2),
             "pct_du_forfait_en_volume": round(100 * a["litres"] / v["forfait_l"], 1),
             "pct_du_forfait_en_euros": round(100 * a["euros"] / v["forfait_eur"], 1),
             "ecart_euros_au_forfait": round(a["euros"] - v["forfait_eur"], 2)}
            for a in v["assiettes"]],
    }
    os.makedirs(CALC, exist_ok=True)
    chemin = os.path.join(CALC, "cascade-10622.json")
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    print("écrit :", chemin)
    return doc


def ecrire_csv(c):
    chemin = os.path.join(PIECES, "R1-cascade-doubles-comptages.csv")
    os.makedirs(PIECES, exist_ok=True)
    with open(chemin, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["SARL LA DEMI LUNE - controle des doubles comptages de la cascade des 10 622 L"])
        w.writerow(["Produit par scripts/reponse1-cascade-valeurs.py"])
        w.writerow([])
        w.writerow(["1. Biere : la contenance des articles mixtes etait comptee en plus de leur recette"])
        w.writerow(["Article de caisse", "Format", "Quantite 3 exercices",
                    "Contenance comptee dans 'vendu au verre' (L)",
                    "Alcool reel porte par 'vendu en cocktails' (L)"])
        recettes = lire(os.path.join(DATA, "calculsBoissons", "cocktailsComposition.json"))["cocktails"]
        mp, cocktails_map = mapping_caisse()
        tot_c = tot_a = 0.0
        for x in c["mixtes"]:
            lab = [l for l in LIBELLES_MIXTES if mp.CAISSE2CANON[l][1] == x["format_service"]][0]
            a = sum(x["total_quantite"] * ig["cl"] / 100.0
                    for ig in recettes[cocktails_map[lab]]["ingredients"]
                    if ig["categorie"] in ("alcool", "biere"))
            w.writerow([lab, x["format_service"], x["total_quantite"],
                        f"{x['total_volume_l']:.2f}", f"{a:.2f}"])
            tot_c += x["total_volume_l"]
            tot_a += a
        w.writerow(["TOTAL", "", "", f"{tot_c:.2f}", f"{tot_a:.2f}"])
        w.writerow(["Double comptage retire du poste 'vendu au verre'", "", "", f"{tot_c:.2f}", ""])
        w.writerow([])
        w.writerow(["Controle : biere reellement sortie du fut"])
        w.writerow(["Pression et pintes pures", f"{c['biere_pure']:.2f}"])
        w.writerow(["Biere des quatre articles mixtes", f"{c['alcool_mixte']['Fût Affligem']:.2f}"])
        w.writerow(["Total biere servie", f"{c['biere_servie']:.2f}"])
        w.writerow(["Freinte technique a 10 %", f"{0.10 * c['biere_servie']:.2f}"])
        w.writerow([])
        w.writerow(["2. Offerts : alcool deja enregistre a 0,00 EUR dans l'annexe D"])
        w.writerow(["Poste de la cascade", "Produit", "Litres"])
        for (poste, canon), val in sorted(c["zero_detail"].items(), key=lambda z: -z[1]):
            w.writerow(["vendu au verre" if poste == "verre" else "vendu en cocktails",
                        canon, f"{val:.2f}"])
        w.writerow(["TOTAL brut", "", f"{c['zero_l']:.2f}"])
        w.writerow(["dont contenance d'articles mixtes, deja retiree par la correction 1", "",
                    f"{c['zero_mixte']:.2f}"])
        w.writerow(["TOTAL net deja compte dans les ventes", "", f"{c['zero_net']:.2f}"])
        w.writerow(["Poste 'offerts' avant correction (1 aperitif de 6 cl x 662 jours)", "",
                    f"{c['offerts_hypothese']:.2f}"])
        w.writerow(["Poste 'offerts' apres correction", "", f"{c['postes'][8]['litres']:.2f}"])
    print("écrit :", chemin)


def ecrire_xlsx(c, v, doc):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    blanc = Font(bold=True, color="FFFFFF")
    gras = Font(bold=True)
    tete = PatternFill("solid", fgColor="0F766E")
    surligne = PatternFill("solid", fgColor="CCE7E2")
    trait = Side(style="thin", color="D8DEE4")
    bord = Border(left=trait, right=trait, top=trait, bottom=trait)
    droite = Alignment(horizontal="right")

    def entetes(ws, cols, ligne):
        ws.append(cols)
        for i in range(1, len(cols) + 1):
            cell = ws.cell(row=ligne, column=i)
            cell.font, cell.fill, cell.border = blanc, tete, bord
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    def largeurs(ws, l):
        for i, w in enumerate(l, 1):
            ws.column_dimensions[get_column_letter(i)].width = w

    A = c["achats"]
    ws = wb.active
    ws.title = "1. Cascade"
    ws.append(["Bilan matiere des 10 622 L d'alcool achetes sur les trois exercices verifies"])
    ws["A1"].font = Font(bold=True, size=13)
    ws.append(["Un litre achete est soit vendu, soit encore en stock, soit consomme sans vente, "
               "soit perdu. Le residu n'est pas choisi : c'est le solde de l'egalite. Version "
               "integrant les six corrections portees contre nous-memes : cremant borne par le "
               "stock, sur-versement separe par assiette, alcool de cuisine plafonne aux "
               "factures, assiette de la freinte ramenee a la biere reellement sortie du fut, "
               "retrait de la contenance des articles mixtes comptee deux fois, deduction des "
               "offerts deja enregistres a 0,00 EUR."])
    ws["A2"].font = Font(italic=True, size=9, color="64748B")
    ws.append([])
    cols = ["Poste", "Litres", "Part des achats", "Nature du chiffre", "Source",
            "Page de demonstration"]
    entetes(ws, cols, 4)
    for p in c["postes"]:
        ws.append([p["libelle"], p["litres_arrondi"], p["litres_arrondi"] / A,
                   {"mesure": "mesure", "calcul": "calcule", "estime": "estime"}[p["nature"]],
                   p["source"], p["page"]])
        r = ws.max_row
        for i in range(1, len(cols) + 1):
            ws.cell(row=r, column=i).border = bord
        ws.cell(row=r, column=2).alignment = droite
        ws.cell(row=r, column=3).number_format = "0,0 %"
    ws.append(["Total attribue a un poste identifie", c["attribue_arrondi"],
               c["attribue_arrondi"] / A, "", "", ""])
    ws.append(["Perte pure (casse, evaporation, fonds de verre, rincage)", c["residu_arrondi"],
               c["residu_arrondi"] / A, "residu", "Solde du bilan matiere : aucun taux, "
               "aucune hypothese", ""])
    ws.append(["Total achete (factures)", int(round(A)), 1.0, "", "", ""])
    for r in range(ws.max_row - 2, ws.max_row + 1):
        for i in range(1, len(cols) + 1):
            ws.cell(row=r, column=i).font = gras
            ws.cell(row=r, column=i).fill = surligne
            ws.cell(row=r, column=i).border = bord
        ws.cell(row=r, column=2).alignment = droite
        ws.cell(row=r, column=3).number_format = "0,0 %"
    largeurs(ws, [46, 12, 16, 18, 62, 28])
    ws.freeze_panes = "A5"

    ws2 = wb.create_sheet("2. Nature des postes")
    ws2.append(["Repartition des 10 622 L par nature du chiffre"])
    ws2["A1"].font = Font(bold=True, size=13)
    ws2.append([])
    entetes(ws2, ["Nature", "Litres", "Part des achats", "Definition"], 3)
    for lib, cle, d in [
        ("Mesure", "mesure", "Lu directement dans le detail des tickets ou dans l'inventaire"),
        ("Calcule", "calcul", "Quantite lue en caisse multipliee par une dose ou une recette"),
        ("Estime", "estime", "Taux publie applique a une base lue en caisse"),
        ("Residu", "residu", "Solde de l'egalite : aucun taux, aucune hypothese"),
    ]:
        n = doc["nature"][cle]["litres_arrondi"]
        ws2.append([lib, n, n / A, d])
        for i in range(1, 5):
            ws2.cell(row=ws2.max_row, column=i).border = bord
        ws2.cell(row=ws2.max_row, column=3).number_format = "0,0 %"
    ws2.append(["Part reposant sur la caisse (mesure et calcule)", doc["part_caisse_arrondi_l"],
                doc["part_caisse_pct"] / 100, "Postes lus ou calcules sur des quantites de caisse"])
    for i in range(1, 5):
        ws2.cell(row=ws2.max_row, column=i).font = gras
    ws2.cell(row=ws2.max_row, column=3).number_format = "0,0 %"
    largeurs(ws2, [42, 14, 16, 76])

    ws3 = wb.create_sheet("3. Doubles comptages")
    ws3.append(["Les deux doubles comptages retires de la cascade"])
    ws3["A1"].font = Font(bold=True, size=13)
    ws3.append([])
    entetes(ws3, ["Correction", "Litres", "Poste avant", "Poste apres", "Demonstration"], 3)
    for lig in [
        ["Contenance des quatre articles mixtes (panache, Monaco, Picon biere, pinte Picon)",
         c["double_biere"], c["verre_brut"], c["postes"][0]["litres"],
         "Ces quatre libelles figurent a la fois dans CAISSE2CANON (contenance entiere du "
         "verre, mappee sur le fut Affligem) et dans CAISSE_COCKTAIL (recette). Le poste "
         "'vendu au verre' portait %.2f L de fut et le poste cocktails %.2f L de plus, soit "
         "%.2f L de biere pour %.2f L reellement sortis du fut."
         % (1292.86, c["alcool_mixte"]["Fût Affligem"],
            1292.86 + c["alcool_mixte"]["Fût Affligem"], c["biere_servie"])],
        ["Offerts deja enregistres a 0,00 EUR dans l'annexe D",
         c["zero_net"], c["offerts_hypothese"], c["postes"][8]["litres"],
         "extract_items() additionne les quantites de l'annexe D sans regarder le prix "
         "unitaire : %d lignes a 0,00 EUR (%.1f articles) portent %.2f L d'alcool, dont "
         "%.2f L de contenance d'articles mixtes deja retiree ci-dessus, soit %.2f L nets "
         "deja compris dans les ventes."
         % (c["zero_lignes"], c["zero_articles"], c["zero_l"], c["zero_mixte"], c["zero_net"])],
    ]:
        ws3.append(lig)
        for i in range(1, 6):
            ws3.cell(row=ws3.max_row, column=i).border = bord
            ws3.cell(row=ws3.max_row, column=i).alignment = Alignment(vertical="top", wrap_text=True)
    ws3.append(["TOTAL retire des postes nommes et reporte au residu",
                round(c["double_biere"] + c["zero_net"], 2), "", "", ""])
    for i in range(1, 6):
        ws3.cell(row=ws3.max_row, column=i).font = gras
        ws3.cell(row=ws3.max_row, column=i).fill = surligne
    ws3.append([])
    ws3.append(["La correction ne libere aucun litre pour une vente dissimulee : les litres "
                "quittent des postes nommes pour aller dans la perte non ventilee. Ils ne "
                "deviennent pas une recette."])
    ws3.cell(row=ws3.max_row, column=1).font = Font(italic=True, color="64748B")
    largeurs(ws3, [56, 12, 14, 14, 96])

    ws4 = wb.create_sheet("4. Forfait vs itemisation")
    ws4.append(["Ce que le forfait de 15 % du service represente, et ce qu'il devrait couvrir"])
    ws4["A1"].font = Font(bold=True, size=13)
    ws4.append(["Trois assiettes possibles. Le choix de celle qui est produite appartient au "
                "conseil. Les euros valorisent chaque litre au prix de revente de la carte : "
                "c'est la grandeur que la reconstitution du service attribue a cet alcool."])
    ws4["A2"].font = Font(italic=True, size=9, color="64748B")
    ws4.append([])
    entetes(ws4, ["Assiette", "Litres", "Part des achats", "Part du forfait en volume",
                  "Euros de CA boissons", "Part du forfait en euros", "Ecart en euros"], 4)
    ws4.append(["Forfait de 15 % du service", round(v["forfait_l"], 1), 0.15, 1.0,
                round(v["forfait_eur"], 2), 1.0, 0.0])
    for i in range(1, 8):
        ws4.cell(row=ws4.max_row, column=i).font = gras
        ws4.cell(row=ws4.max_row, column=i).fill = surligne
        ws4.cell(row=ws4.max_row, column=i).border = bord
    for a in doc["assiettes"]:
        ws4.append([a["libelle"], a["litres_arrondi"], a["pct_achats"] / 100,
                    a["pct_du_forfait_en_volume"] / 100, a["euros"],
                    a["pct_du_forfait_en_euros"] / 100, a["ecart_euros_au_forfait"]])
        for i in range(1, 8):
            ws4.cell(row=ws4.max_row, column=i).border = bord
            ws4.cell(row=ws4.max_row, column=i).alignment = Alignment(vertical="top", wrap_text=True)
    for r in range(5, ws4.max_row + 1):
        for i in (3, 4, 6):
            ws4.cell(row=r, column=i).number_format = "0,0 %"
        for i in (5, 7):
            ws4.cell(row=r, column=i).number_format = "# ##0,00"
    ws4.append([])
    entetes(ws4, ["Detail de l'assiette A (postes itemises, hors cuisine et menus)", "Litres",
                  "Euros", "Base de valorisation", "", "", ""], ws4.max_row + 1)
    for n, l, e, b, _px in v["itemisation"]:
        ws4.append([n, round(l, 2), round(e, 2), b])
        for i in range(1, 5):
            ws4.cell(row=ws4.max_row, column=i).border = bord
        ws4.cell(row=ws4.max_row, column=3).number_format = "# ##0,00"
    ws4.append(["TOTAL assiette A", round(sum(x[1] for x in v["itemisation"]), 2),
                round(sum(x[2] for x in v["itemisation"]), 2), ""])
    for i in range(1, 5):
        ws4.cell(row=ws4.max_row, column=i).font = gras
        ws4.cell(row=ws4.max_row, column=i).fill = surligne
    ws4.append([])
    entetes(ws4, ["Alcool de cuisine et alcool des menus, plafonne aux achats factures", "Litres",
                  "Euros", "Base de valorisation", "", "", ""], ws4.max_row + 1)
    for n, l, e, b in v["cuisine"]:
        ws4.append([n, round(l, 2), round(e, 2), b])
        for i in range(1, 5):
            ws4.cell(row=ws4.max_row, column=i).border = bord
        ws4.cell(row=ws4.max_row, column=3).number_format = "# ##0,00"
    ws4.append(["TOTAL cuisine et menus", round(sum(x[1] for x in v["cuisine"]), 2),
                round(sum(x[2] for x in v["cuisine"]), 2), ""])
    for i in range(1, 5):
        ws4.cell(row=ws4.max_row, column=i).font = gras
        ws4.cell(row=ws4.max_row, column=i).fill = surligne
    ws4.append([])
    ws4.append(["Le residu de perte pure est valorise a %.2f EUR/L, moyenne des prix de revente "
                "ponderee par les litres achetes : le residu n'est par construction affecte a "
                "aucun produit, ce prix est donc une moyenne et non une mesure."
                % v["prix_residu"]])
    ws4.cell(row=ws4.max_row, column=1).font = Font(italic=True, color="64748B")
    largeurs(ws4, [62, 14, 18, 46, 18, 18, 18])

    chemin = os.path.join(PIECES, "R1-cascade-bilan-matiere.xlsx")
    os.makedirs(PIECES, exist_ok=True)
    wb.save(chemin)
    print("écrit :", chemin)


# ---------------------------------------------------------------------------
def main():
    c = construire()
    prix = prix_de_revente()
    v = valoriser(c, prix)
    doc = ecrire_json(c, v)
    ecrire_csv(c)
    ecrire_xlsx(c, v, doc)

    n = lambda x, d=1: f"{x:,.{d}f}".replace(",", " ").replace(".", ",")
    print()
    print("CASCADE DES 10 622 L (producteur unique)")
    print("-" * 78)
    for p in c["postes"]:
        print("  %-42s %8s L   (%s)" % (p["libelle"], n(p["litres"], 2), p["nature"]))
    print("  %-42s %8s L" % ("Total attribué", n(c["attribue"], 2)))
    print("  %-42s %8s L   %s %%" % ("Résidu de perte pure", n(c["residu"], 2),
                                     n(100 * c["residu"] / c["achats"])))
    print("  %-42s %8s L" % ("Total acheté", n(c["achats"], 2)))
    print("  contrôle arrondis : %d + %d = %d" % (c["attribue_arrondi"], c["residu_arrondi"],
                                                  c["attribue_arrondi"] + c["residu_arrondi"]))
    print()
    print("ASSIETTES")
    print("-" * 78)
    print("  Forfait 15 %%                              %8s L   %12s €"
          % (n(v["forfait_l"]), n(v["forfait_eur"], 2)))
    for a in doc["assiettes"]:
        print("  %-38s %8s L   %12s €   vol %5s %% du forfait, € %5s %%"
              % (a["cle"] + ". " + a["libelle"][:34], n(a["litres"]), n(a["euros"], 2),
                 n(a["pct_du_forfait_en_volume"]), n(a["pct_du_forfait_en_euros"])))
    print()
    print("  double comptage bière   : %s L" % n(c["double_biere"], 2))
    print("  double comptage offerts : %s L" % n(c["zero_net"], 2))
    print("  bière réellement servie : %s L, freinte 10 %% = %s L"
          % (n(c["biere_servie"], 2), n(0.10 * c["biere_servie"], 2)))
    print("  part des achats revendue : %s %%" % n(doc["part_revendue_pct"], 2))


if __name__ == "__main__":
    main()
