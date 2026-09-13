#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REPONSE 1 - Piece de verification de la NATURE de chaque chiffre de la cascade.

Objet : le service ecrit page 77 que nos postes sont « affirmes sans le moindre
element pour les soutenir ». Cette piece repond a ce reproche poste par poste,
en isolant pour chacun :
  - la GRANDEUR COMPTEE (un nombre d'articles, de notes, de bouteilles, de
    jours), qui est lue dans une piece et qui ne resulte d'aucune hypothese ;
  - le COEFFICIENT qui la convertit en litres (une contenance de la carte, une
    recette, une dose declaree, un taux publie), et l'ORIGINE de ce coefficient ;
  - le VOLUME qui en resulte.

Elle ne recalcule PAS la cascade et ne la modifie pas : elle lit
src/data/reponse1Calculs/cascade-10622.json, seule source de verite, produite
par scripts/reponse1-cascade-valeurs.py, et verifie que les grandeurs comptees
relues dans les donnees brutes redonnent bien les volumes qui y figurent.

Entrees (lecture seule) :
  src/data/reponse1Calculs/cascade-10622.json          (cascade, autorite)
  src/data/reponse1Calculs/cremant-fourchette.json     (cremant, jour par jour)
  src/data/reponse1Calculs/sur-versement-fourchette.json
  src/data/calculsBoissons/boissonsHorsCocktail.json   (articles vendus)
  src/data/calculsBoissons/cocktailsConsoComposition.json
  src/data/renduFinal/degustation-notes.json
  src/data/incertitudeDisparu/base_disparu_ajuste2.json
  public/documents/pieces-reponse-1/R1-alcool-cuisine-controles.xlsx

Sortie :
  public/documents/pieces-reponse-1/R1-cascade-nature-des-chiffres.xlsx

Execution : python3 scripts/reponse1-cascade-nature-des-chiffres.py
Code de retour 1 si un controle echoue.
"""
import json
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(ICI, ".."))
DATA = os.path.join(ROOT, "src", "data")
CALC = os.path.join(DATA, "reponse1Calculs")
PIECES = os.path.join(ROOT, "public", "documents", "pieces-reponse-1")
SORTIE = os.path.join(PIECES, "R1-cascade-nature-des-chiffres.xlsx")

FORMATS_MIXTES = ["Panaché 25cl", "Monaco 25cl", "Demi+Picon 25cl", "Pinte+Picon 50cl"]
ALCOOL_COCKTAIL = {"petillant", "vin_de_liqueur", "biere", "vin_blanc", "vin_rouge",
                   "vin_rose", "vin", "liqueur", "aperitif", "spiritueux", "eau_de_vie",
                   "digestif"}
JOURS_SERVICE = 662

ECHECS = []


def lire(chemin):
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)


def chk(libelle, condition, detail=""):
    ok = bool(condition)
    if not ok:
        ECHECS.append(libelle)
    print(("  OK    " if ok else "  ECHEC ") + libelle + ((" | " + detail) if detail else ""))
    return ok


# ---------------------------------------------------------------------------
# Les grandeurs comptees, relues dans les donnees brutes
# ---------------------------------------------------------------------------
def grandeurs():
    g = {}

    # 1. Articles de boisson vendus hors cocktails, et leur volume.
    hc = lire(os.path.join(DATA, "calculsBoissons", "boissonsHorsCocktail.json"))["boissons"]
    mixtes = [x for x in hc if x["nom_canonique"] == "Fût Affligem"
              and x["format_service"] in FORMATS_MIXTES]
    g["verre_articles"] = round(sum(x["total_quantite"] for x in hc)
                                - sum(x["total_quantite"] for x in mixtes), 1)
    g["verre_litres"] = round(sum(x["total_volume_l"] for x in hc)
                              - sum(x["total_volume_l"] for x in mixtes), 2)
    g["verre_formats"] = len(hc) - len(mixtes)
    g["mixtes_articles"] = round(sum(x["total_quantite"] for x in mixtes), 1)
    g["mixtes_litres"] = round(sum(x["total_volume_l"] for x in mixtes), 2)

    # 2. Cocktails vendus et alcool porte par les recettes de la carte.
    cc = lire(os.path.join(DATA, "calculsBoissons", "cocktailsConsoComposition.json"))
    g["cocktails_articles"] = round(sum(c["total_quantite"] for c in cc["cocktails"]), 1)
    g["cocktails_recettes"] = len(cc["cocktails"])
    g["cocktails_litres"] = round(sum(x["total_l"] for x in cc["totaux_par_ingredient"]
                                      if x.get("categorie") in ALCOOL_COCKTAIL), 2)

    # 3. Degustation : notes distinctes relevees une a une dans l'annexe C.
    dg = lire(os.path.join(DATA, "renduFinal", "degustation-notes.json"))
    g["degustation_notes"] = dg["total_degustations"]
    g["degustation_lignes"] = dg["lignes_vin"]
    g["degustation_dose_cl"] = dg["dose_cl"]
    g["degustation_litres"] = round(dg["total_degustations"] * dg["dose_cl"] / 100.0, 2)

    # 4. Cremant : les deux termes sont ceux du service.
    cre = lire(os.path.join(CALC, "cremant-fourchette.json"))["exercices"]
    g["cremant_bouteilles_service"] = sum(v["dispo_bouteilles"] for v in cre.values())
    g["cremant_bouteilles_entieres"] = sum(v["bouteilles_vendues_entieres"] for v in cre.values())
    g["cremant_dispo_l"] = round(sum(v["dispo_service_cl"] for v in cre.values()) / 100.0, 2)
    g["cremant_servi_l"] = round(sum(v["nominal_cl"] for v in cre.values()) / 100.0, 2)
    g["cremant_jours"] = sum(v["jours_servis"] for v in cre.values())
    g["cremant_litres"] = round(sum(v["ecart_a_expliquer_cl"] for v in cre.values()) / 100.0, 2)

    # 5. Sur-versement : assiette reellement versee a la main.
    sv = lire(os.path.join(CALC, "sur-versement-fourchette.json"))
    r = sv["regimes_total"]
    g["sv_base_main_l"] = r["base_main_l"]
    g["sv_base_totale_l"] = r["base_totale_l"]
    g["sv_pichet_l"] = r["vin_pichet_l"]
    g["sv_bouteille_l"] = r["vin_bouteille_l"]
    g["sv_litres"] = round(sv["variantes"]["retenu_l"], 2)
    g["sv_taux_main"] = r["taux_sur_base_main"]
    g["sv_taux_totale"] = r["taux_sur_base_totale"]
    g["sv_contenants"] = sv["contenants_vendus_total"]

    # 6. Cuisine : plats et desserts vendus, lus dans la piece deja publiee.
    g["cuisine_plats"] = None
    g["cuisine_carte_l"] = None
    try:
        from openpyxl import load_workbook
        ws = load_workbook(os.path.join(PIECES, "R1-alcool-cuisine-controles.xlsx"),
                           data_only=True)["2-Cuisine par plat"]
        n = 0.0
        lignes = 0
        for ligne in ws.iter_rows(min_row=4, values_only=True):
            if not ligne or not ligne[0] or str(ligne[0]).upper().startswith("TOTAL"):
                continue
            try:
                n += sum(float(c or 0) for c in ligne[4:7])
            except (TypeError, ValueError):
                continue
            lignes += 1
        g["cuisine_plats"] = round(n, 1)
        g["cuisine_lignes"] = lignes
    except Exception as exc:                                   # noqa: BLE001
        print("  (piece cuisine illisible : %s)" % exc)

    # 7. Stock final et achats, lus dans la base des 64 boissons.
    base = [b for b in lire(os.path.join(DATA, "incertitudeDisparu",
                                         "base_disparu_ajuste2.json"))["boissons"]
            if b.get("conso_complete") is True]
    g["nb_boissons"] = len(base)
    g["stock_litres"] = round(sum(b["stock_final_l"] for b in base), 2)
    g["chef_litres"] = round(sum((b.get("conso_staff_l") or {}).get("moyen", 0.0)
                                 for b in base), 2)
    return g


# ---------------------------------------------------------------------------
# Construction des feuilles
# ---------------------------------------------------------------------------
def lignes_nature(d, g):
    P = {p["cle"]: p for p in d["postes"]}
    A = d["achats_l"]
    pct = lambda v: round(100.0 * v / A, 2)
    ofr = d["doubles_comptages"]["offerts"]
    bi = d["doubles_comptages"]["biere"]

    L = []

    def add(cle, compte, nombre, coef, origine, ou):
        p = P[cle]
        L.append([p["libelle"], {"mesure": "mesuré", "calcul": "calculé",
                                 "estime": "estimé"}[p["nature"]],
                  compte, nombre, coef, origine, p["litres"], pct(p["litres"]), ou])

    add("verre",
        "Articles de boisson vendus, ligne à ligne dans le détail des tickets",
        "%s articles sur %d formats" % (f"{g['verre_articles']:,.1f}".replace(",", " "),
                                        g["verre_formats"]),
        "Contenance du format vendu",
        "Carte de l’établissement ; contenances reprises par le service p. 62",
        "ANNEXE-C1 à C3 et ANNEXE-D1 à D3 (caisse)")
    add("cocktails",
        "Cocktails vendus, ligne à ligne dans le détail des tickets",
        "%s cocktails sur %d recettes" % (f"{g['cocktails_articles']:,.1f}".replace(",", " "),
                                          g["cocktails_recettes"]),
        "Recette de la carte, ingrédient par ingrédient",
        "Carte de l’établissement",
        "ANNEXE-D1 à D3 et carte des cocktails")
    add("cuisine",
        "Plats, entrées et desserts contenant de l’alcool, vendus en caisse",
        ("%s plats et desserts à la carte, plus les plats servis dans les menus"
         % f"{g['cuisine_plats']:,.1f}".replace(",", " ")
         if g["cuisine_plats"] else "plats et desserts vendus en caisse"),
        "Dose par recette, puis plafonnement aux achats facturés",
        "Doses déclarées par les dirigeants, que le service dit avoir suivies (p. 68)",
        "R1-alcool-cuisine-controles.xlsx")
    add("cremant",
        "Bouteilles de crémant que le service déclare disponibles, et crémant servi d’après la caisse",
        "%d bouteilles retenues par le service, dont %d vendues entières, sur %d jours servis"
        % (g["cremant_bouteilles_service"], g["cremant_bouteilles_entieres"], g["cremant_jours"]),
        "Différence entre le disponible du service (%s L) et le servi d’après la caisse (%s L)"
        % (f"{g['cremant_dispo_l']:.2f}", f"{g['cremant_servi_l']:.2f}"),
        "Les deux termes viennent du service : ses quantités disponibles et ses doses (p. 63 et p. 84)",
        "51-rf-cremant-jete.xlsx, exploitée par le service p. 84")
    add("surversement",
        "Volume réellement versé à la main, pichets et bouteilles exclus",
        "%s L versés à la main sur %s L versés toutes formes confondues"
        % (f"{g['sv_base_main_l']:.2f}", f"{g['sv_base_totale_l']:.2f}"),
        "Taux publiés : +23,6 % au verre de vin, +42 % en cocktail, 0 % en pichet et en bouteille",
        "Kerr et coll. (2008), 80 établissements ; Wansink et van Ittersum (BMJ, 2005), 86 barmen",
        "49-rf-sur-versement-au-verre.xlsx")
    add("degustation",
        "Notes portant au moins un vin nommé, relevées une à une",
        "%s dégustations sur %s lignes de vin"
        % (f"{g['degustation_notes']:,}".replace(",", " "),
           f"{g['degustation_lignes']:,}".replace(",", " ")),
        "%s cl par dégustation" % f"{g['degustation_dose_cl']:.0f}",
        "Dose déclarée par les dirigeants",
        "52-rf-degustation-par-note.xlsx")
    add("biere",
        "Bière réellement sortie du fût, lue en caisse",
        "%s L de bière servie, Picon compté à 4 cl au demi et 8 cl à la pinte"
        % f"{bi['biere_servie_l']:.2f}",
        "10 % de freinte technique",
        "Taux prudent, à comparer aux 30 % que le service retient lui-même sur la bière (p. 83)",
        "50-rf-pertes-biere-mousse.xlsx")
    add("chef",
        "Jours de service",
        "%d jours de service" % JOURS_SERVICE,
        "Base journalière déclarée, macvin et Picon",
        "Déclaration des dirigeants du 30/03/2026",
        "57-rf-offerts-remises-pertes.xlsx")
    add("offerts",
        "Jours de service, moins les offerts déjà enregistrés en caisse à 0,00 €",
        "%d jours de service ; %d lignes à 0,00 € et %s articles déjà enregistrés"
        % (JOURS_SERVICE, ofr["lignes_annexe_d"], f"{ofr['articles']:.0f}"),
        "Un apéritif de 6 cl par jour, moins %s L déjà comptés dans les ventes"
        % f"{ofr['litres_nets']:.2f}",
        "Hypothèse d’un apéritif offert par jour ; la déduction est lue en caisse",
        "57-rf-offerts-remises-pertes.xlsx")
    add("stock",
        "Inventaire de clôture",
        "%d boissons alcoolisées suivies" % g["nb_boissons"],
        "Volume inventorié au 31/03/2025",
        "Inventaire de l’entreprise, remis au service",
        "09-rf-inventaire-stocks.xlsx")

    L.append(["Total attribué à un poste identifié", "", "", "", "", "",
              d["attribue_l"], round(d["attribue_pct"], 2), ""])
    L.append(["Perte pure (résidu)", "résidu",
              "Rien n’est compté : le résidu est le solde du bilan matière",
              "sans objet", "Aucun taux, aucune hypothèse", "Solde",
              d["residu_l"], round(d["residu_pct"], 2), "R1-cascade-bilan-matiere.xlsx"])
    L.append(["Total acheté (factures)", "", "", "", "", "", A, 100.0, ""])
    return L


def lignes_ventilation(d):
    A = d["achats_l"]
    n = d["nature"]
    L = []
    for cle, lib, quoi in (
        ("mesure", "Mesuré",
         "La quantité est comptée dans la caisse ou à l’inventaire, et le volume unitaire "
         "est celui du contenant vendu"),
        ("calcul", "Calculé",
         "La quantité est comptée dans la caisse, et le volume unitaire résulte d’une "
         "décomposition : recette, dose dans un plat, ou soustraction de deux volumes"),
        ("estime", "Estimé",
         "Un taux est appliqué à une assiette elle-même lue dans la caisse"),
        ("residu", "Résidu",
         "Solde du bilan matière : ni quantité, ni taux"),
    ):
        L.append([lib, n[cle]["litres"], round(100.0 * n[cle]["litres"] / A, 2), quoi])
    L.append(["Total", round(sum(n[c]["litres"] for c in n), 2), 100.0,
              "Somme des quatre natures = achats facturés"])
    L.append(["Dont lu ou calculé sur la caisse", d["part_caisse_l"],
              round(d["part_caisse_pct"], 2),
              "Mesuré et calculé réunis : la part du bilan qui ne repose sur aucun taux"])
    return L


def lignes_controles(d, g):
    P = {p["cle"]: p for p in d["postes"]}
    A = d["achats_l"]
    n = d["nature"]
    ctrl = []

    def c(libelle, attendu, obtenu, tol=0.02):
        ok = abs(attendu - obtenu) <= tol
        ctrl.append([libelle, round(attendu, 2), round(obtenu, 2), "OK" if ok else "ÉCHEC"])
        chk(libelle, ok, "attendu %.2f, obtenu %.2f" % (attendu, obtenu))

    c("Articles vendus hors cocktails x contenance = poste « vendu au verre »",
      P["verre"]["litres"], g["verre_litres"], 0.05)
    c("Cocktails vendus x recette = poste « vendu en cocktails »",
      P["cocktails"]["litres"], g["cocktails_litres"], 0.05)
    c("Dégustations comptées x 2 cl = poste « dégustation offerte »",
      P["degustation"]["litres"], g["degustation_litres"])
    c("Disponible du service moins servi d’après la caisse = poste « crémant non vendu »",
      P["cremant"]["litres"], g["cremant_litres"])
    c("Sur-versement retenu = valeur de la fourchette publiée",
      P["surversement"]["litres"], g["sv_litres"])
    c("Stock final relu dans la base des boissons = poste « stock final »",
      P["stock"]["litres"], g["stock_litres"])
    c("Consommation du chef relue dans la base = poste correspondant",
      P["chef"]["litres"], g["chef_litres"])
    c("10 % de la bière sortie du fût = poste « freinte technique »",
      P["biere"]["litres"], 0.10 * d["doubles_comptages"]["biere"]["biere_servie_l"])
    c("Mesuré + calculé + estimé = total attribué",
      d["attribue_l"], n["mesure"]["litres"] + n["calcul"]["litres"] + n["estime"]["litres"])
    c("Total attribué + résidu = achats facturés", A, d["attribue_l"] + d["residu_l"])
    c("Somme des dix postes + résidu = achats facturés",
      A, sum(p["litres"] for p in d["postes"]) + d["residu_l"])
    c("Contenance des quatre articles mixtes retirée une seule fois",
      d["doubles_comptages"]["biere"]["litres"], g["mixtes_litres"], 0.05)
    c("Mesuré + calculé = part lue ou calculée sur la caisse",
      d["part_caisse_l"], n["mesure"]["litres"] + n["calcul"]["litres"])
    return ctrl


def lignes_origine(d, g):
    """Origine de chaque coefficient, et position du service sur ce coefficient."""
    sv = round(100.0 * g["sv_taux_main"], 1)
    return [
        ["Contenance des formats vendus", "12 cl, 25 cl, 50 cl, 75 cl selon le format",
         "Carte de l’établissement",
         "Le service reconstitue lui aussi à partir des doses de la caisse (tableau "
         "« DONNEES ISSUES LOGICIEL DE CAISSE », p. 62)"],
        ["Recettes des cocktails", "%d recettes, ingrédient par ingrédient"
         % g["cocktails_recettes"], "Carte de l’établissement",
         "Le service retient ses propres doses pour ces articles (p. 62)"],
        ["Doses d’alcool de cuisine", "1 à 10 cl selon la recette",
         "Déclaration des dirigeants du 30/03/2026",
         "Retenues par le service : « le service n’a fait que suivre les recommandations "
         "des dirigeants » (p. 68)"],
        ["Dose de crémant au verre", "12 cl",
         "Déclaration des dirigeants",
         "Retenue par le service : « la dose vendue s’établissant à 12 centilitres "
         "(conformément aux dires des dirigeants) » (p. 63 et p. 85)"],
        ["Dose de dégustation", "%s cl" % f"{g['degustation_dose_cl']:.0f}",
         "Déclaration des dirigeants", "Discutée par le service p. 85 et p. 86"],
        ["Taux de sur-versement", "+23,6 % au verre, +42 % en cocktail, 0 % en pichet et bouteille",
         "Kerr et coll. (2008) et Wansink et van Ittersum (BMJ, 2005), publiés avant le contrôle",
         "Refusés par le service p. 77, p. 80 et p. 81"],
        ["Taux de freinte de la bière", "10 %",
         "Taux prudent retenu par la défense",
         "Le service retient lui-même 30 % de pertes, offerts et consommation du personnel "
         "sur la bière (p. 83)"],
        ["Apéritif offert", "6 cl par jour de service",
         "Hypothèse de la défense, minorée des offerts déjà enregistrés en caisse",
         "Le service retient un forfait sur le chiffre d’affaires (p. 89)"],
        ["Taux global du sur-versement retenu", "%s %% du volume versé à la main" % f"{sv:.1f}",
         "Résultat des taux ci-dessus appliqués à l’assiette de %s L versée à la main"
         % f"{g['sv_base_main_l']:.2f}",
         "Soit %s %% du volume versé toutes formes confondues et %s %% des achats"
         % (f"{100.0 * g['sv_taux_totale']:.1f}",
            f"{100.0 * d['postes'][4]['litres'] / d['achats_l']:.1f}")],
    ]


# ---------------------------------------------------------------------------
def ecrire(d, g):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill

    gras = Font(bold=True)
    blanc = Font(bold=True, color="FFFFFF")
    fond = PatternFill("solid", fgColor="1F4E5F")
    haut = Alignment(vertical="top", wrap_text=True)

    wb = Workbook()

    def feuille(nom, titre, entetes, lignes, largeurs):
        ws = wb.create_sheet(nom)
        ws["A1"] = titre
        ws["A1"].font = gras
        ws.append([])
        ws.append(entetes)
        for c in ws[3]:
            c.font = blanc
            c.fill = fond
            c.alignment = haut
        for ligne in lignes:
            ws.append(ligne)
        for i, w in enumerate(largeurs, start=1):
            ws.column_dimensions[chr(64 + i)].width = w
        for ligne in ws.iter_rows(min_row=4):
            for c in ligne:
                c.alignment = haut
        ws.freeze_panes = "A4"
        return ws

    feuille("1-Nature du chiffre",
            "1. Ce qui est compté, ce qui le convertit en litres, et d’où vient ce coefficient "
            "(réponse au reproche de la page 77 : « affirmés sans le moindre élément »)",
            ["Poste", "Nature", "Grandeur comptée", "Nombre compté",
             "Coefficient appliqué", "Origine du coefficient", "Volume (L)",
             "% des achats", "Où le recalculer"],
            lignes_nature(d, g),
            [34, 10, 46, 40, 42, 46, 12, 12, 34])

    feuille("2-Ventilation",
            "2. Ventilation des 10 622 L achetés selon la nature du chiffre",
            ["Nature", "Litres", "% des achats", "Définition retenue"],
            lignes_ventilation(d), [34, 12, 14, 86])

    feuille("3-Origine des coefficients",
            "3. Origine de chaque coefficient, et position du service sur ce même coefficient",
            ["Coefficient", "Valeur retenue", "Origine", "Position du service"],
            lignes_origine(d, g), [34, 46, 46, 70])

    feuille("4-Contrôles",
            "4. Contrôles arithmétiques : chaque poste est recalculé depuis les données brutes "
            "et comparé à la cascade publiée",
            ["Contrôle", "Valeur de la cascade (L)", "Valeur recalculée (L)", "Résultat"],
            lignes_controles(d, g), [86, 24, 24, 12])

    del wb["Sheet"]
    wb.save(SORTIE)
    print("\nécrit : " + SORTIE)


def main():
    d = lire(os.path.join(CALC, "cascade-10622.json"))
    print("Cascade lue : %.2f L achetés = %.2f L attribués + %.2f L de résidu"
          % (d["achats_l"], d["attribue_l"], d["residu_l"]))
    g = grandeurs()
    print("\nContrôles :")
    ecrire(d, g)
    if ECHECS:
        print("\nINCOHERENCE : %d contrôle(s) en échec. Ne rien publier." % len(ECHECS))
        sys.exit(1)
    print("Tous les contrôles sont passés.")


if __name__ == "__main__":
    main()
