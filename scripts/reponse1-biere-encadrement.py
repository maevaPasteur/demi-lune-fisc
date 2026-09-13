#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REPONSE 1 - Biere pression : la freinte bornee PAR LA MATIERE, exercice par exercice.

Le service ecrit page 61 que la defense soutient des pertes plus importantes
"sans apporter de justifications probantes". Ce script ne cherche pas a opposer
un taux de reference a un autre : il BORNE la freinte avec les seules grandeurs
du dossier, exercice par exercice.

  borne basse DOCUMENTEE  <=  freinte retenue  <=  ce que le service accorde deja

  - borne basse : les deux seuls postes que le constructeur du materiel chiffre
    (volume residuel admis dans un fut vide, 1,5 % soit 120 ml ; duree de vie
    utile de 30 jours d'un fut perce), le second date fut par fut sur le detail
    des tickets que le service a lui-meme extrait (annexes C1 a C3) ;
  - freinte retenue : 10 % de la biere REELLEMENT SORTIE DU FUT, volume lu en
    caisse article par article (part biere reelle des articles mixtes) ;
  - borne haute : le premier abattement du service, 15 % du fut achete, lu dans
    les annexes finales de la proposition de rectifications.

Le meme onglet donne, sur la seule ligne biere, ce que represente le second
abattement de fin de methode (3 forfaits de 5 %), poste par poste.

AUCUNE valeur n'est figee ici : les grandeurs sont reprises telles quelles du
script proprietaire scripts/reponse1-biere-freinte.py, importe comme module,
afin que les deux pieces ne puissent pas diverger.

Sortie : public/documents/pieces-reponse-1/R1-biere-encadrement-freinte.xlsx
"""

import datetime
import importlib.util
import json
import os

ICI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(ICI, ".."))
PIECES = os.path.join(ROOT, "public", "documents", "pieces-reponse-1")

spec = importlib.util.spec_from_file_location(
    "biere_freinte", os.path.join(ICI, "reponse1-biere-freinte.py"))
bf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bf)

EXOS, EXL = bf.EXOS, bf.EXL


def calendrier_par_exercice():
    """Volume de biere servi jour par jour, en gardant l'exercice de chaque jour."""
    import xlrd
    jour, exo_du_jour = {}, {}
    dossier = os.path.join(ROOT, "public", "documents", "caisse-enregistreuse")
    for e in EXOS:
        wb = xlrd.open_workbook(os.path.join(dossier, bf.ANNEXES_C[e]))
        sh = wb.sheet_by_index(0)
        for r in range(1, sh.nrows):
            d = str(sh.cell_value(r, 0))[:10]
            if len(d) != 10:
                continue
            lib = str(sh.cell_value(r, 10)).strip()
            cl = bf.LIB_CAISSE.get(lib)
            if cl is None:
                continue
            jour[d] = jour.get(d, 0.0) + (sh.cell_value(r, 11) or 0) * cl / 100.0
            exo_du_jour[d] = e
    return jour, exo_du_jour


def fermetures_hiver():
    """Jours SANS AUCUN TICKET, lus sur la totalite du detail remis par le
    service (annexes C1 a C3, toutes lignes confondues et non les seules
    ventes de biere). Seules les interruptions d'au moins 20 jours sont
    retenues : ce sont les fermetures d'hiver."""
    import xlrd
    tous = set()
    dossier = os.path.join(ROOT, "public", "documents", "caisse-enregistreuse")
    for e in EXOS:
        sh = xlrd.open_workbook(
            os.path.join(dossier, bf.ANNEXES_C[e])).sheet_by_index(0)
        for r in range(1, sh.nrows):
            d = str(sh.cell_value(r, 0))[:10]
            if len(d) == 10 and d[4] == "-":
                tous.add(d)
    jours = sorted(datetime.date.fromisoformat(d) for d in tous)
    out = []
    for a, b in zip(jours, jours[1:]):
        n = (b - a).days - 1
        if n >= 20:
            out.append((a, b, n))
    return jours, out


def exercice_de(date_iso, exo_du_jour, jours_tries):
    """Exercice d'une date, rattachee au jour de service le plus proche."""
    if date_iso in exo_du_jour:
        return exo_du_jour[date_iso]
    prec = [d for d in jours_tries if d <= date_iso]
    return exo_du_jour[prec[-1]] if prec else exo_du_jour[jours_tries[0]]


def main():
    achats_l, _ = bf.lire_achats()
    ventes, servi = bf.lire_ventes()
    sv = bf.lire_methode_service()
    jour, exo_du_jour = calendrier_par_exercice()
    jours_tries = sorted(jour)

    achat_total = sum(achats_l[e] for e in EXOS)
    sim = bf.simuler_perces(jour, achat_total)

    # --- repartition par exercice --------------------------------------
    futs = {e: achats_l[e] / bf.CONTENANCE_FUT_L for e in EXOS}
    residu = {e: futs[e] * bf.RESIDU_FUT_L for e in EXOS}
    perim = {e: 0.0 for e in EXOS}
    perim_n = {e: 0 for e in EXOS}
    lignes_perimes = []
    for ouvert, perime, litres in sim["perimes"]:
        e = exercice_de(perime, exo_du_jour, jours_tries)
        perim[e] += litres
        perim_n[e] += 1
        lignes_perimes.append([EXL[e], ouvert, perime,
                               (datetime.date.fromisoformat(perime)
                                - datetime.date.fromisoformat(ouvert)).days,
                               round(litres, 2)])
    lignes_perimes.append(["TOTAL", "", "", "",
                           round(sum(perim.values()), 2)])

    tb, tf = sv["taux_biere"], sv["ab_fin"]

    # --- onglet 1 : l'encadrement --------------------------------------
    enc, tot = [], dict.fromkeys(
        ["achat", "servi", "basse", "fr", "ab1"], 0.0)
    for e in EXOS:
        basse = residu[e] + perim[e]
        fr = servi[e] * bf.FREINTE_RETENUE
        ab1 = achats_l[e] * tb
        enc.append([
            EXL[e], round(futs[e]), round(achats_l[e], 1), round(servi[e], 1),
            round(basse, 1), round(100 * basse / achats_l[e], 2),
            round(fr, 1), round(100 * fr / achats_l[e], 2),
            round(ab1, 1), 15.0,
            "oui" if basse <= fr <= ab1 else "NON",
        ])
        for k, v in (("achat", achats_l[e]), ("servi", servi[e]),
                     ("basse", basse), ("fr", fr), ("ab1", ab1)):
            tot[k] += v
    enc.append([
        "TOTAL 3 exercices", round(sum(futs.values())), round(tot["achat"], 1),
        round(tot["servi"], 1),
        round(tot["basse"], 1), round(100 * tot["basse"] / tot["achat"], 2),
        round(tot["fr"], 1), round(100 * tot["fr"] / tot["achat"], 2),
        round(tot["ab1"], 1), 15.0,
        "oui" if tot["basse"] <= tot["fr"] <= tot["ab1"] else "NON"])

    # --- onglet 2 : l'assiette, article par article ---------------------
    ass = []
    for r in ventes:
        row = [r["produit"], r["verre_cl"], r["biere_cl"],
               round(r["verre_cl"] - r["biere_cl"], 1)]
        for e in EXOS:
            row.append(round(r["l_biere"][e], 1))
        row.append(round(sum(r["l_biere"].values()), 1))
        ass.append(row)
    ass.append(["TOTAL : assiette de la freinte", "", "", ""]
               + [round(servi[e], 1) for e in EXOS] + [round(tot["servi"], 1)])
    contenance = sum(r["qte"][e] * r["verre_cl"] / 100.0
                     for r in ventes for e in EXOS)
    ass.append(["Pour memoire : contenance des verres servis", "", "", ""]
               + [round(sum(r["qte"][e] * r["verre_cl"] / 100.0 for r in ventes), 1)
                  for e in EXOS] + [round(contenance, 1)])

    # --- onglet 8 : l'assiette confrontee a l'annexe du service -------
    # Bloc "i) -INGREDIENT : BIERE" des Annexes Finales de la proposition
    # (page 2, folio imprime 203), tableau "DONNEES ISSUES LOGICIEL DE CAISSE",
    # colonnes "Quantites Vendues" et "Quantites (en centilitres)". L'exercice
    # couvert par ces annexes est le dernier exercice verifie (clos le
    # 31/03/2025) : le bloc de synthese de la page 3 en porte le chiffre
    # d'affaires liquides (165 065,33 EUR TTC).
    ANNEXE = {
        "Pression 25cl":    ("25 cl de biere", 662, 16550),
        "Pinte 50cl":       ("50 cl de biere", 308, 15400),
        "Demi+Picon 25cl":  ("« 3 cl picon et 22 cl biere »", 124, 2728),
        "Pinte+Picon 50cl": ("« 6 cl picon et 44 cl biere »", 59, 2596),
        "Panaché 25cl":     ("« 11 cl biere » + 13 cl de limonade", 97, 767),
        "Monaco 25cl":      ("« 15 cl biere » + 5 cl de limonade et 2 cl de "
                             "sirop grenadine", 74, 1110),
    }
    E3 = "2024-2025"
    conf, t_ann, t_nous = [], 0, 0.0
    qte = {}
    for x in json.load(open(os.path.join(ROOT, "src", "data", "calculsBoissons",
                                         "itemsCaisse.json"), encoding="utf-8"))["items"]:
        if x.get("nom_canonique") == "Fût Affligem":
            f = x.get("format_service")
            if f in ANNEXE:
                qte[f] = qte.get(f, 0.0) + (x["quantite"].get(E3, 0) or 0)
    for f, (compo, q_ann, cl_ann) in ANNEXE.items():
        lib, verre, biere, _ = bf.FORMAT_BIERE[f]
        cl_nous = qte.get(f, 0.0) * biere
        conf.append([lib, compo, q_ann, round(qte.get(f, 0.0), 1),
                     cl_ann, round(cl_nous, 1), round(cl_nous - cl_ann, 1)])
        t_ann += cl_ann
        t_nous += cl_nous
    conf.append(["TOTAL de la ligne biere", "part biere seule", "", "",
                 t_ann, round(t_nous, 1), round(t_nous - t_ann, 1)])
    conf.append(["Ecart en % du total de l'annexe", "", "", "", "",
                 "", round(100 * (t_nous - t_ann) / t_ann, 3)])

    # --- onglet 3 : ce que le constructeur chiffre ----------------------
    cons = [
        ["Volume du fut", "8 litres", "Caracteristiques techniques, p. 32",
         "Fut Affligem Blade 800 cl, designation reprise telle quelle par les "
         "annexes finales du service"],
        ["Volume residuel acceptable dans un fut vide", "1,5 % (120 ml)",
         "Ch. 6.3 Depannage, p. 28",
         "« Le volume residuel acceptable s'eleve a 1,5 % (120 ml) ». C'est un "
         "SEUIL DE TOLERANCE, donc un maximum admis, et non une perte moyenne "
         "mesuree sur nos futs : applique aux futs achetes, il donne un "
         "MAJORANT de ce seul poste"],
        ["Duree de vie utile d'un fut perce", "30 jours", "Ch. 1.2, p. 7",
         "« Un fut qui a ete insere et ouvert doit rester dans l'appareil "
         "[...] jusqu'a avoir vide le fut ou jusqu'a ce que la duree de vie "
         "utile de 30 jours ait expire »"],
        ["Pre-refroidissement exige avant la mise en perce", "16 heures ou plus",
         "Ch. 6.3 Depannage, p. 26",
         "« Avant utilisation, les futs doivent etre stockes dans une piece "
         "fraiche et obscure, puis 16 heures ou plus au refrigerateur »"],
        ["Debit d'un fut qui n'a pas ete pre-refroidi", "environ 1 litre par heure",
         "Ch. 6.3 Depannage, p. 26",
         "« Refroidir un fut non froid dans le Blade va prendre plus de 16 "
         "heures. Au bout de 3 a 4 heures, vous etes en mesure de soutirer vos "
         "deux premieres bieres. Apres cela, vous pouvez soutirer environ 1 "
         "litre de biere par heure ». A comparer au debit nominal de 1,6 l/min"],
        ["Nettoyage des lignes", "sans objet sur ce materiel",
         "Fiche technique Heineken",
         "Le tube de soutirage est integre au fut et jete avec lui "
         "(« Cleaning cycle: No. Disposable line in keg »). Le poste "
         "« nettoyage des lignes tous les 14 j » que notre memoire du "
         "10/07/2026 portait a 5 % du fut ne correspond PAS a ce materiel : "
         "nous l'abandonnons"],
        ["Mousse retiree au service, moussage d'un fut mal pre-refroidi, biere "
         "perdue au montage et au retrait du fut", "non chiffre",
         "Le manuel decrit ces phenomenes sans leur affecter de pourcentage",
         "C'est pourquoi la somme des deux postes chiffres par le constructeur "
         "ne peut pas etre presentee comme un taux de freinte : elle en est "
         "une borne basse"],
    ]

    # --- onglet 4 : le second abattement sur la seule ligne biere -------
    sec = []
    for e in EXOS:
        net = achats_l[e] * (1 - tb)
        sec.append([EXL[e], round(net, 1),
                    round(net * sv["ab_remise"], 1),
                    round(net * sv["ab_pertes"], 1),
                    round(net * sv["ab_perso"], 1),
                    round(net * tf, 1),
                    round(servi[e] * bf.FREINTE_RETENUE, 1),
                    round(net * sv["ab_pertes"] - servi[e] * bf.FREINTE_RETENUE, 1)])
    net_t = tot["achat"] * (1 - tb)
    sec.append(["TOTAL 3 exercices", round(net_t, 1),
                round(net_t * sv["ab_remise"], 1),
                round(net_t * sv["ab_pertes"], 1),
                round(net_t * sv["ab_perso"], 1),
                round(net_t * tf, 1), round(tot["fr"], 1),
                round(net_t * sv["ab_pertes"] - tot["fr"], 1)])

    # --- onglet 5 : les deux taux, composition et non addition ----------
    comp = [
        ["Premier taux, applique au VOLUME de fut", f"{100 * tb:.0f} %",
         round(tot["achat"] * tb, 1),
         "annexes finales : 63 200 cl de volume disponible, 9 480 cl retires, "
         "53 720 cl de volume net. Le taux porte sur des centilitres"],
        ["Second taux, applique au CHIFFRE D'AFFAIRES liquides",
         f"{100 * tf:.0f} %", round(tot["achat"] * (1 - tb) * tf, 1),
         "3 forfaits de 5 % au bas de la reconstitution, toutes boissons "
         "confondues : remise, pertes, consommation du personnel. Le taux "
         "porte sur des euros ; la colonne litres est une conversion en "
         "equivalent-fut, pour comparaison"],
        ["Total reellement retire du fut",
         f"{100 * (1 - (1 - tb) * (1 - tf)):.2f} %",
         round(tot["achat"] * (1 - (1 - tb) * (1 - tf)), 1),
         "1 - 0,85 x 0,85. Deux abattements successifs se composent : le "
         "second ne s'applique qu'au solde laisse par le premier"],
        ["Taux revendique par le service p. 61 et p. 83", "30 %",
         round(tot["achat"] * 0.30, 1),
         "« un taux total de 30 % sur la biere » (p. 61) ; « en cumulant les "
         "deux taux de sa methode de reconstitution » (p. 83). L'ecart avec le "
         "taux reellement retire est de "
         f"{tot['achat'] * (0.30 - (1 - (1 - tb) * (1 - tf))):.1f} L sur trois "
         "exercices"],
    ]

    jours_ouverts, fermetures = fermetures_hiver()
    lignes_ferm = []
    for a, b, n in fermetures:
        jan = [d for d in jours_ouverts
               if d.year == b.year and d.month == 1]
        lb = sum(jour.get(d.isoformat(), 0.0) for d in jan)
        lignes_ferm.append([
            f"{a.year - 1}-{a.year}", a.isoformat(), b.isoformat(), n,
            len(jan), round(lb, 2)])

    onglets = [
        ("1. Encadrement par exercice",
         ["Exercice", "Futs de 8 L achetes", "Futs achetes (L)",
          "Biere sortie du fut, lue en caisse (L)",
          "Borne basse documentee par le constructeur (L)",
          "en % du fut", "Freinte retenue (L)", "en % du fut",
          "1er abattement accorde par le service (L)", "en % du fut",
          "Encadrement verifie"],
         enc, [20, 14, 14, 20, 22, 12, 14, 12, 20, 12, 14]),
        ("2. Assiette lue en caisse",
         ["Article de caisse", "Contenance du verre (cl)", "Part biere (cl)",
          "Part NON issue du fut (cl)"]
         + [f"{EXL[e]} (L de biere)" for e in EXOS] + ["Total (L de biere)"],
         ass, [34, 16, 14, 16, 16, 16, 16, 18]),
        ("3. Chiffres du constructeur",
         ["Grandeur", "Valeur", "Emplacement dans le manuel", "Portee exacte"],
         cons, [46, 24, 30, 86]),
        ("4. Futs perimes dates",
         ["Exercice", "Fut perce le", "Perime le", "Jours", "Solde perdu (L)"],
         lignes_perimes, [16, 16, 16, 10, 16]),
        ("5. Le second abattement",
         ["Exercice", "Base : volume net apres le 1er abattement (L)",
          "Remise 5 % (L)", "Pertes 5 % (L)", "Conso personnel 5 % (L)",
          "Total 15 % (L)", "Freinte retenue (L)",
          "Composante pertes moins freinte (L)"],
         sec, [20, 24, 14, 14, 18, 14, 16, 22]),
        ("6. Les deux taux",
         ["Etape", "Taux", "Litres de fut sur 3 exercices", "Assiette et source"],
         comp, [46, 12, 18, 92]),
        ("7. Fermetures d hiver",
         ["Hiver", "Dernier jour avec un ticket", "Premier jour de reouverture",
          "Jours consecutifs sans aucun ticket",
          "Jours avec un ticket en janvier",
          "Biere servie en janvier (L)"],
         lignes_ferm, [14, 22, 22, 22, 20, 18]),
        ("8. Assiette vs annexe service",
         ["Article de caisse", "Composition ecrite dans l'annexe du service",
          "Quantites vendues, annexe", "Quantites vendues, notre lecture",
          "Part biere, annexe (cl)", "Part biere, notre lecture (cl)",
          "Ecart (cl)"],
         conf, [28, 46, 18, 20, 18, 20, 14]),
    ]

    chemin = os.path.join(PIECES, "R1-biere-encadrement-freinte.xlsx")
    bf.ecrire_xlsx(
        chemin,
        "Biere pression : la freinte bornee par la matiere, exercice par exercice",
        "SARL LA DEMI LUNE. Sources : factures FCBS, detail des tickets remis "
        "par le service (annexes C1 a C3), annexes finales de la proposition de "
        "rectifications, manuel d'utilisation Heineken Blade. "
        "Script : scripts/reponse1-biere-encadrement.py",
        onglets)

    print(json.dumps({
        "achats_l": achats_l, "achats_total_l": tot["achat"],
        "servi_total_l": round(tot["servi"], 2),
        "borne_basse_par_exercice_l": {e: round(residu[e] + perim[e], 2) for e in EXOS},
        "borne_basse_totale_l": round(tot["basse"], 2),
        "borne_basse_pct_fut": round(100 * tot["basse"] / tot["achat"], 2),
        "residu_par_exercice_l": {e: round(residu[e], 2) for e in EXOS},
        "peremption_par_exercice_l": {e: round(perim[e], 2) for e in EXOS},
        "peremption_par_exercice_futs": perim_n,
        "freinte_par_exercice_l": {e: round(servi[e] * bf.FREINTE_RETENUE, 2) for e in EXOS},
        "freinte_totale_l": round(tot["fr"], 2),
        "ab1_par_exercice_l": {e: round(achats_l[e] * tb, 2) for e in EXOS},
        "ab1_total_l": round(tot["ab1"], 2),
        "composante_pertes_du_second_abattement_l": round(net_t * sv["ab_pertes"], 2),
        "encadrement_verifie_par_exercice": {
            e: bool(residu[e] + perim[e] <= servi[e] * bf.FREINTE_RETENUE
                    <= achats_l[e] * tb) for e in EXOS},
        "assiette_exercice_des_annexes": {
            "annexe_cl": t_ann, "notre_lecture_cl": round(t_nous, 1),
            "ecart_cl": round(t_nous - t_ann, 1),
            "ecart_pct": round(100 * (t_nous - t_ann) / t_ann, 3)},
        "jours_avec_ticket": len(jours_ouverts),
        "fermetures_hiver": [[a.isoformat(), b.isoformat(), n]
                             for a, b, n in fermetures],
        "piece": os.path.relpath(chemin, ROOT),
    }, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
