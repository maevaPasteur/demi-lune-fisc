#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REPONSE 1 - Biere pression : freinte technique du fut et assiette des abattements.

Repond a la reponse du service du 04/09/2026, point 2 (p. 61) et partie O
(p. 82-83), ou le service additionne deux taux de 15 % pour revendiquer
"un taux total de 30 % sur la biere".

Ce script refait, EN LITRES, la descente du fut achete au volume facturable,
puis rejoue la methode du service avec SES PROPRES parametres, lus dans les
"Annexes finales" de la proposition de rectifications :
  - abattement biere de 15 % sur le VOLUME de fut disponible
    (l'annexe le libelle "conso personnel + pertes")
  - abattements de fin de methode : 5 % remise + 5 % pertes + 5 % conso
    personnel, calcules sur le CA LIQUIDES en euros
  - coefficient liquide -> solide de 3,10

Sources (lecture seule, reproductible) :
  src/data/calculsBoissons/achatsBoissonsParPeriode.json  (factures FCBS)
  src/data/calculsBoissons/itemsCaisse.json               (ventes caisse)
  src/data/reconstitution-administration.json             (methode du service)

Sortie :
  public/documents/pieces-reponse-1/R1-biere-freinte.xlsx
  + une synthese JSON sur la sortie standard.
"""

import json
import os

ICI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(ICI, ".."))
DATA = os.path.join(ROOT, "src", "data")
PIECES = os.path.join(ROOT, "public", "documents", "pieces-reponse-1")
EXOS = ["2022-2023", "2023-2024", "2024-2025"]
EXL = {"2022-2023": "2022-23", "2023-2024": "2023-24", "2024-2025": "2024-25"}

PRODUIT_FUT = "FUT AFFLIGEM BLADE 8 L 6,7°"
CONTENANCE_FUT_L = 8.0

# --- Freinte technique : taux verifies en ligne ----------------------------
# Bar-i (audits d'inventaire) : rendement de fut optimal 95 %, courant "about
# 90 %", en perte technique pure hors offerts. Le Bihan Boissons : "une perte
# de 10% par fut". OA Formation : "Biere : 10-20 %". Modern Restaurant
# Management : "average waste at 20 percent per keg" (borne haute, non sourcee).
# Le "Draught Beer Quality Manual" de la Brewers Association ne donne AUCUN
# taux : il documente des mecanismes, pas un pourcentage.
# ASSIETTE : le taux est applique au volume de biere REELLEMENT SORTI DU FUT
# (part biere lue en caisse, 1 219,2 L), et NON a la contenance des verres
# (1 292,9 L), qui comprend 73,7 L de limonade, de grenadine et de Picon jamais
# sortis du fut. Correction apportee au memoire du 10/07/2026 : 129 L -> 121,9 L.
FREINTE_RETENUE = 0.10      # taux retenu, borne basse de la convergence
FREINTE_HAUTE = 0.20        # borne haute des sources, NON demandee
# Volume residuel admis dans un fut vide, chiffre CONSTRUCTEUR du fut Blade 8 L.
# ATTENTION A LA PORTEE : la phrase "Le volume residuel acceptable s'eleve a
# 1,5 % (120 ml)" figure au chap. 6.3 "Derangement, causes possibles et
# remedes", p. 28, en regard du probleme "Le volume de biere reste dans le fut
# vide est trop eleve". C'est un SEUIL DE TOLERANCE (un maximum acceptable),
# pas une perte moyenne mesuree. Applique aux 262 futs, il donne donc un
# MAJORANT de ce poste, non une mesure. Le materiel n'a AUCUNE ligne a
# nettoyer : le tube de soutirage est integre au fut et jete avec lui (fiche
# technique Heineken : "Cleaning cycle: No. Disposable line in keg").
RESIDU_FUT_L = 0.120        # litres par fut de 8 L
RESIDU_PCT = 0.015
# Duree de vie utile d'un fut PERCE, chiffre CONSTRUCTEUR : manuel Heineken
# Blade, chap. 1.2, p. 7 : "Un fut qui a ete insere et ouvert doit rester dans
# l'appareil [...] jusqu'a avoir vide le fut ou jusqu'a ce que la duree de vie
# utile de 30 jours ait expire". Les deux autres occurrences (chap. 6.3, p. 26
# et 28) sont des REMEDES CONDITIONNES a un defaut constate (mousse reduite,
# gout desagreable), et non une regle de rebut automatique au 30e jour.
VIE_UTILE_J = 30

# --- Libelles de caisse portant de la biere du fut (annexes C1/C2/C3) -------
# Colonne 11 "Lib_ticket", colonne 12 "Qte", colonne 1 "Date Ticket".
LIB_CAISSE = {
    "pression": 25.0, "Pinte": 50.0, "Panaché": 12.5,
    "Picon bière": 23.0, "Pinte Picon": 46.0, "Monaco": 12.5,
}
ANNEXES_C = {
    "2022-2023": "ANNEXE-C1_detail-tickets_2022-2023.xls",
    "2023-2024": "ANNEXE-C2_detail-tickets_2023-2024.xls",
    "2024-2025": "ANNEXE-C3_detail-tickets_2024-2025.xls",
}

# --- Part biere reelle de chaque article de caisse (cl) ---------------------
# Le panache et le Monaco sont moitie biere ; le Picon biere contient 2 cl de
# Picon (4 cl en pinte) : seule la part biere sort du fut Affligem.
FORMAT_BIERE = {
    "Pression 25cl":    ("Pression 25 cl", 25, 25.0, 1),
    "Pinte 50cl":       ("Pression 50 cl (pinte)", 50, 50.0, 2),
    "Panaché 25cl": ("Panaché 25 cl", 25, 12.5, 3),
    "Demi+Picon 25cl":  ("Picon bière 25 cl", 25, 23.0, 4),
    "Pinte+Picon 50cl": ("Picon bière 50 cl", 50, 46.0, 5),
    "Monaco 25cl":      ("Monaco 25 cl", 25, 12.5, 6),
}


def fr(x, dec=0):
    s = f"{x:,.{dec}f}".replace(",", " ").replace(".", ",")
    return s


# --------------------------------------------------------------------------
def lire_achats():
    d = json.load(open(os.path.join(DATA, "calculsBoissons",
                                    "achatsBoissonsParPeriode.json"), encoding="utf-8"))
    for a in d["achats"]:
        if a["produit"] == PRODUIT_FUT:
            # La quantite des factures FCBS est exprimee EN LITRES pour le fut
            # (facture n 467442 : colis 3, quantite 24, pu 3,59 EUR = 3 futs de 8 L).
            return ({e: a["par_periode"][e]["quantite"] for e in EXOS},
                    {e: a["par_periode"][e]["montant_ht"] for e in EXOS})
    raise SystemExit("Fut Affligem introuvable dans les achats")


def lire_ventes():
    d = json.load(open(os.path.join(DATA, "calculsBoissons",
                                    "itemsCaisse.json"), encoding="utf-8"))
    agg = {}
    for x in d["items"]:
        if x.get("nom_canonique") != "Fût Affligem":
            continue
        fmt = x.get("format_service")
        if fmt not in FORMAT_BIERE:
            continue
        a = agg.setdefault(fmt, {e: 0.0 for e in EXOS})
        for e in EXOS:
            a[e] += x["quantite"].get(e, 0) or 0
    lignes = []
    for fmt, q in sorted(agg.items(), key=lambda kv: FORMAT_BIERE[kv[0]][3]):
        lib, verre, biere, _ = FORMAT_BIERE[fmt]
        lignes.append({
            "produit": lib, "verre_cl": verre, "biere_cl": biere,
            "qte": {e: q[e] for e in EXOS},
            "l_biere": {e: q[e] * biere / 100.0 for e in EXOS},
        })
    servi = {e: sum(r["l_biere"][e] for r in lignes) for e in EXOS}
    return lignes, servi


def lire_calendrier():
    """Volume de biere servi JOUR PAR JOUR, lu dans les annexes C (detail des
    tickets remis par le service). Sert a dater les mises en perce."""
    import xlrd
    jour = {}
    dossier = os.path.join(ROOT, "public", "documents", "caisse-enregistreuse")
    for e in EXOS:
        wb = xlrd.open_workbook(os.path.join(dossier, ANNEXES_C[e]))
        sh = wb.sheet_by_index(0)
        for r in range(1, sh.nrows):
            d = str(sh.cell_value(r, 0))[:10]
            if len(d) != 10:
                continue
            lib = str(sh.cell_value(r, 10)).strip()
            cl = LIB_CAISSE.get(lib)
            if cl is None:
                continue
            jour[d] = jour.get(d, 0.0) + (sh.cell_value(r, 11) or 0) * cl / 100.0
    return jour


def simuler_perces(jour, volume_total_l):
    """Rejoue, fut par fut, le calendrier des mises en perce.

    Hypothese la plus favorable au service : la TOTALITE du fut achete passe
    par le bec (2 096 L), le tirage de chaque jour etant proportionnel aux
    ventes de biere enregistrees ce jour-la dans les annexes C. Un fut percé
    est remplace des qu'il est vide ; s'il n'est pas vide au bout des 30 jours
    de duree de vie utile fixes par le constructeur, il est remplace et son
    solde est perdu.
    """
    import datetime
    servi = sum(jour.values())
    k = volume_total_l / servi
    jours = sorted(jour)
    d0 = datetime.date.fromisoformat(jours[0])
    d1 = datetime.date.fromisoformat(jours[-1])
    reste, ouvert, perces, residu = CONTENANCE_FUT_L, d0, 1, 0.0
    perimes = []
    d = d0
    while d <= d1:
        v = jour.get(d.isoformat(), 0.0) * k
        while v > 0:
            if v >= reste:
                v -= reste
                residu += RESIDU_FUT_L
                perces += 1
                reste, ouvert = CONTENANCE_FUT_L - RESIDU_FUT_L, d
            else:
                reste -= v
                v = 0
        # Le controle de peremption ne se fait qu'un JOUR DE SERVICE : pendant
        # les fermetures d'hiver, personne ne perce de fut ; le fut en place au
        # dernier service est mis au rebut a la reouverture s'il a depasse les
        # 30 jours de duree de vie utile.
        if (d.isoformat() in jour and (d - ouvert).days >= VIE_UTILE_J
                and reste > RESIDU_FUT_L + 0.001):
            perimes.append((ouvert.isoformat(), d.isoformat(),
                            round(reste - RESIDU_FUT_L, 2)))
            residu += RESIDU_FUT_L
            perces += 1
            reste, ouvert = CONTENANCE_FUT_L - RESIDU_FUT_L, d
        d += datetime.timedelta(days=1)
    return {
        "servi_calendrier_l": servi,
        "premier_jour": jours[0], "dernier_jour": jours[-1],
        "jours_avec_vente_biere": len(jour),
        "futs_perces": perces,
        "residu_l": residu,
        "perimes": perimes,
        "perte_peremption_l": sum(p[2] for p in perimes),
    }


def volumes_par_mois(jour):
    mois = {}
    for d, v in jour.items():
        mois[d[:7]] = mois.get(d[:7], 0.0) + v
    return mois


def lire_methode_service():
    d = json.load(open(os.path.join(DATA, "reconstitution-administration.json"),
                       encoding="utf-8"))
    m = d["methode"]
    biere = next(i for i in d["ingredients"] if i["ref"] == "Bière")
    dispo_l = biere["volumeDisponibleCl"] / 100.0
    taux_biere = biere["deductions"]["consoPersonnelPertesPct"]
    net_l = biere["deductions"]["volumeNetCl"] / 100.0
    part_valorisee = sum(r["proportion"] for r in biere["repartitionCocktails"]
                         if r.get("prixMoyen"))
    ca_ttc = biere["caReconstitue"]["ttc"]
    prix_l_ttc = ca_ttc / (net_l * part_valorisee)
    ab = m["abattements"]
    return {
        "dispo_l": dispo_l, "futs": round(dispo_l / CONTENANCE_FUT_L),
        "taux_biere": taux_biere, "net_l": net_l,
        "ab_remise": ab["remise"], "ab_pertes": ab["pertes"],
        "ab_perso": ab["consommationPersonnel"],
        "ab_fin": ab["remise"] + ab["pertes"] + ab["consommationPersonnel"],
        "coef_liq_sol": m["rapportLiquideSolidePour1Euro"],
        "prix_l_ttc": prix_l_ttc,
        "synthese": d["synthese"],
    }


# --------------------------------------------------------------------------
def main():
    achats_l, achats_ht = lire_achats()
    ventes, servi = lire_ventes()
    sv = lire_methode_service()
    calendrier = lire_calendrier()
    mois = volumes_par_mois(calendrier)

    tb = sv["taux_biere"]          # 0,15 sur le VOLUME de fut
    tf = sv["ab_fin"]              # 0,15 sur le CA LIQUIDES, en fin de methode
    prix = sv["prix_l_ttc"]        # EUR TTC de CA liquides par litre de biere
    ampli = 1.0 + sv["coef_liq_sol"]   # liquides + solides extrapoles

    lignes_cascade, lignes_taux, lignes_fin = [], [], []
    tot = dict.fromkeys(
        ["achat", "futs", "servi", "residu", "fr_ret", "fr10_fut", "fr20_fut",
         "ab1", "net1", "ab2", "ret", "p_remise", "p_pertes", "p_perso"], 0.0)

    for e in EXOS:
        a = achats_l[e]
        nb = a / CONTENANCE_FUT_L
        residu = nb * RESIDU_FUT_L
        # Freinte retenue : 10 % de la biere REELLEMENT SORTIE DU FUT.
        fr_ret = servi[e] * FREINTE_RETENUE
        # Pour memoire uniquement : ce que le meme taux donnerait sur le fut.
        fr10_fut, fr20_fut = a * FREINTE_RETENUE, a * FREINTE_HAUTE
        ab1 = a * tb
        net1 = a - ab1
        ab2 = net1 * tf
        ret = ab1 + ab2
        lignes_cascade.append([
            EXL[e], round(nb), round(a, 1), round(servi[e], 1), "10 %",
            round(fr_ret, 1), round(residu, 2),
        ])
        lignes_taux.append([
            EXL[e], round(a, 1), round(ab1, 1), round(net1, 1), round(ab2, 1),
            round(ret, 1), round(100 * ret / a, 2), 30.0,
            round(100 * ret / a - 30.0, 2),
        ])
        lignes_fin.append([
            EXL[e], round(net1, 1), round(net1 * sv["ab_remise"], 1),
            round(net1 * sv["ab_pertes"], 1), round(net1 * sv["ab_perso"], 1),
            round(ab2, 1),
        ])
        for k, v in (("achat", a), ("futs", nb), ("servi", servi[e]),
                     ("residu", residu), ("fr_ret", fr_ret),
                     ("fr10_fut", fr10_fut), ("fr20_fut", fr20_fut),
                     ("ab1", ab1), ("net1", net1), ("ab2", ab2), ("ret", ret),
                     ("p_remise", net1 * sv["ab_remise"]),
                     ("p_pertes", net1 * sv["ab_pertes"]),
                     ("p_perso", net1 * sv["ab_perso"])):
            tot[k] += v

    lignes_cascade.append([
        "TOTAL 3 exercices", round(tot["futs"]), round(tot["achat"], 1),
        round(tot["servi"], 1), "10 %", round(tot["fr_ret"], 1),
        round(tot["residu"], 2)])
    # --- Onglet ventes ----------------------------------------------------
    lignes_ventes = []
    for r in ventes:
        row = [r["produit"], r["verre_cl"], r["biere_cl"]]
        for e in EXOS:
            row += [round(r["qte"][e], 1), round(r["l_biere"][e], 1)]
        row += [round(sum(r["qte"].values()), 1), round(sum(r["l_biere"].values()), 1)]
        lignes_ventes.append(row)
    row = ["TOTAL bière servie au verre", "", ""]
    for e in EXOS:
        row += [round(sum(r["qte"][e] for r in ventes), 1), round(servi[e], 1)]
    row += [round(sum(sum(r["qte"].values()) for r in ventes), 1), round(tot["servi"], 1)]
    lignes_ventes.append(row)

    # --- Onglet euros -----------------------------------------------------
    # ATTENTION : le prix de 16,38 EUR/L n'est PAS ecrit tel quel dans les
    # annexes. Il s'obtient en rapportant le CA biere reconstitue (7 180,52 EUR
    # TTC) a la seule fraction de la ligne biere que les annexes valorisent sous
    # ce paragraphe (42,27 % de pression + 39,33 % de pinte = 81,60 % du volume
    # net), le solde (Picon biere, panache, Monaco) etant valorise sous d'autres
    # paragraphes. Rapporte au volume net entier, le prix ressort a 13,37 EUR/L.
    # Aucun ecart en litres n'est donc converti en euros dans les pages de
    # reponse : la partie O se traite en litres.
    lignes_euro = [
        ["CA liquides TTC avant abattements, exercice des annexes finales",
         165065.33, "EUR", "bloc de synthese des annexes finales"],
        ["Chacun des trois forfaits de 5 % de fin de methode",
         8253.27, "EUR", "5 % de 165 065,33 EUR TTC (remise, pertes, conso personnel)"],
        ["Total du second abattement (15 %) sur cet exercice",
         24759.81, "EUR", "8 253,27 EUR x 3"],
        ["Le meme forfait de 5 % chiffre par le service p. 72, 73 et 89",
         35133.26, "EUR",
         "meme taux, mesure apres amplification cuisine et sur le premier "
         "exercice : 8 917,07 EUR de liquides (proposition p. 52) x 3,94 "
         "(1 + coefficient de revente 2,94). Ce n'est pas un autre forfait."],
        ["Coefficient liquides -> solides applique par le service",
         sv["coef_liq_sol"], "x", "CA solides = CA liquides apres abattements x 3,10"],
        ["Taux reel retire par le service sur le fut",
         round(100 * tot["ret"] / tot["achat"], 2), "%",
         "1 - 0,85 x 0,85 = 27,75 %, et non 30 %. Les annexes appliquent deja "
         "cette composition (63 200 cl - 9 480 cl = 53 720 cl, puis les "
         "forfaits sur le CA) : la correction ne modifie aucun montant."],
        ["1er abattement du service, en litres de fut",
         round(tot["ab1"], 1), "L", "15 % des 2 096 L achetes"],
        ["2e abattement du service, en equivalent-litres de fut",
         round(tot["ab2"], 1), "L", "15 % du volume net, dont 89,1 L seulement "
         "au titre des pertes"],
        ["Freinte retenue par la defense",
         round(tot["fr_ret"], 1), "L",
         "10 % de la biere reellement sortie du fut (1 219,2 L lus en caisse)"],
    ]

    # --- Calendrier des mises en perce et regle des 30 jours --------------
    # Deux hypotheses de tirage, pour encadrer honnetement la regle des 30 jours.
    # A) la plus favorable au service : la TOTALITE du fut achete passe par le
    #    bec (2 096 L), donc les futs tournent vite et peu atteignent 30 jours.
    # B) la plus defavorable au service : seul le volume LU EN CAISSE sort du
    #    fut, donc les futs restent percés plus longtemps.
    sim = simuler_perces(calendrier, tot["achat"])
    sim_caisse = simuler_perces(calendrier, sum(calendrier.values()))
    plancher_l = tot["residu"] + sim["perte_peremption_l"]
    # La colonne "jours pour vider un fut" de la version precedente etait
    # fausse : elle etalait le volume du mois sur 30 jours de CALENDRIER alors
    # que l'etablissement n'ouvrait que quelques jours. Elle est remplacee par
    # le debit reel par jour d'ouverture, seule grandeur verifiable ici. Ce
    # n'est pas ce debit qui fait perimer un fut, mais les FERMETURES d'hiver
    # (45, 53 puis 58 jours d'affilee sans aucun service) : voir l'onglet 7.
    lignes_mois = []
    for m in sorted(mois):
        j = sum(1 for d in calendrier if d.startswith(m))
        lignes_mois.append([m, round(mois[m], 1), j,
                            round(mois[m] / j, 2) if j else 0])
    lignes_perimes = [[p[0], p[1], p[2]] for p in sim["perimes"]]
    lignes_perimes.append(["TOTAL", f"{len(sim['perimes'])} fûts",
                           round(sim["perte_peremption_l"], 1)])
    lignes_plancher = [
        ["Volume résiduel admis dans un fût vide, jeté avec le fût",
         round(tot["residu"], 1), "majorant documenté",
         "262 fûts x 120 ml. Manuel Heineken Blade, ch. 6.3 « Dérangement, "
         "causes possibles et remèdes », p. 28 : « le volume résiduel "
         "acceptable s'élève à 1,5 % (120 ml) ». C'est un SEUIL DE TOLÉRANCE, "
         "donc un maximum admis, et non une perte moyenne mesurée sur nos fûts"],
        ["Fûts non écoulés dans la durée de vie utile de 30 jours",
         round(sim["perte_peremption_l"], 1), "simulé",
         f"{len(sim['perimes'])} fûts, datés sur le calendrier des annexes C "
         "(hivers de fermeture) ; hypothèse la plus favorable au service "
         "(tout le fût acheté passe par le bec). Dans l'hypothèse inverse "
         f"(seul le volume lu en caisse sort du fût) : "
         f"{len(sim_caisse['perimes'])} fûts et "
         f"{fr(sim_caisse['perte_peremption_l'], 1)} L"],
        ["Total des deux seuls postes chiffrés par le constructeur",
         round(plancher_l, 1), "documenté",
         f"soit {fr(100 * plancher_l / tot['achat'], 2)} % du fût acheté. Ce "
         "total ne comprend NI la mousse retirée au service, NI le moussage "
         "d'un fût mal pré-refroidi, NI la bière perdue au montage et au "
         "retrait des fûts, que le manuel décrit sans les chiffrer : ce n'est "
         "donc pas un taux de freinte et il ne peut pas être comparé au taux "
         "du service"],
        ["Freinte retenue par la défense (10 % de la bière réellement sortie "
         "du fût, 1 219,2 L lus en caisse)",
         round(tot["fr_ret"], 1), "estimé",
         "sources professionnelles convergentes, borne basse. Assiette "
         "corrigée : le mémoire du 10/07/2026 appliquait ce taux à la "
         "contenance des verres (1 292,9 L), qui comprend 73,7 L de limonade, "
         "de grenadine et de Picon jamais sortis du fût. 129 L -> "
         f"{fr(tot['fr_ret'], 1)} L, soit "
         f"{fr(100 * tot['fr_ret'] / tot['achat'], 2)} % du fût acheté"],
        ["Pour mémoire : le même taux de 10 % appliqué au fût acheté",
         round(tot["fr10_fut"], 1), "non retenu",
         "assiette que nous ne retenons pas, bien que ce soit celle des "
         "sources ; elle donnerait 209,6 L au lieu de "
         f"{fr(tot['fr_ret'], 1)} L"],
        ["Pour mémoire : borne haute des sources (20 % du fût)",
         round(tot["fr20_fut"], 1), "non retenu",
         "Modern Restaurant Management et OA Formation ; nous ne la demandons "
         "pas"],
        ["Premier abattement accordé par le service (15 % du fût)",
         round(tot["ab1"], 1), "service",
         "annexes finales : « consommation personnel et pertes »"],
    ]

    onglets = [
        ("1. Futs achetes et biere servie",
         ["Article de caisse", "Contenance verre (cl)", "Part bière (cl)"]
         + [c for e in EXOS for c in (f"{EXL[e]} qté", f"{EXL[e]} L bière")]
         + ["Total qté", "Total L bière"],
         lignes_ventes, [30, 16, 14] + [12] * 6 + [12, 14]),
        ("2. La freinte retenue",
         ["Exercice", "Nombre de fûts de 8 L achetés", "Fûts achetés (L)",
          "Bière réellement sortie du fût, lue en caisse (L)",
          "Taux retenu",
          "Freinte retenue (L) = 10 % de la bière sortie du fût",
          "dont résidu de fin de fût, au seuil du constructeur (L)"],
         lignes_cascade, [20, 18, 15, 24, 12, 26, 24]),
        ("3. Les deux taux du service",
         ["Exercice", "Fûts achetés (L)",
          "1er abattement : 15 % du fût (L)", "Volume net après (L)",
          "2e abattement : 15 % du net, en litres équivalents (L)",
          "Total retiré (L)", "Taux réel sur le fût (%)",
          "Taux revendiqué p. 61 et 83 (%)", "Écart (points)"],
         lignes_taux, [20, 15, 18, 15, 22, 14, 16, 16, 12]),
        ("4. Le 15 % de fin de methode",
         ["Exercice", "Base : volume net après le 1er abattement (L)",
          "Remise 5 % (L)", "Pertes 5 % (L)", "Conso personnel 5 % (L)",
          "Total 15 % (L)"],
         lignes_fin, [20, 24, 14, 14, 16, 14]),
        ("5. Les deux abattements",
         ["Grandeur", "Valeur", "Unité", "Source ou calcul"],
         lignes_euro, [58, 14, 14, 62]),
        ("6. Calendrier de la biere",
         ["Mois", "Bière servie au verre (L)", "Jours avec vente de bière",
          "Litres par jour avec vente de bière"],
         lignes_mois, [12, 20, 18, 20]),
        ("7. Futs perimes a 30 jours",
         ["Fût percé le", "Périmé le", "Solde perdu (L)"],
         lignes_perimes, [16, 16, 16]),
        ("8. Les niveaux en presence",
         ["Poste", "Litres", "Nature", "Source et portée exacte"],
         lignes_plancher, [56, 12, 18, 76]),
    ]

    chemin = os.path.join(PIECES, "R1-biere-freinte.xlsx")
    ecrire_xlsx(chemin, "Bière pression : freinte technique du fût et assiette des abattements",
                "SARL LA DEMI LUNE. Sources : factures FCBS, caisse (annexes C), "
                "annexes finales de la proposition de rectifications. "
                "Script : scripts/reponse1-biere-freinte.py",
                onglets)

    synth = {
        "achats_l": {e: achats_l[e] for e in EXOS}, "achats_total_l": tot["achat"],
        "futs_total": round(tot["futs"]), "servi_l": servi, "servi_total_l": tot["servi"],
        "residu_l": tot["residu"],
        "freinte_retenue_par_exercice_l": {
            e: round(servi[e] * FREINTE_RETENUE, 2) for e in EXOS},
        "pour_memoire_10pct_du_fut_l": tot["fr10_fut"],
        "pour_memoire_20pct_du_fut_l": tot["fr20_fut"],
        "service_ab1_l": tot["ab1"], "service_ab2_l": tot["ab2"],
        "service_total_retire_l": tot["ret"],
        "service_taux_reel_pct": 100 * tot["ret"] / tot["achat"],
        "fin_methode": {"remise_l": tot["p_remise"], "pertes_l": tot["p_pertes"],
                        "perso_l": tot["p_perso"]},
        "dispo_service_l": sv["dispo_l"], "futs_service": sv["futs"],
        "calendrier": {
            "servi_annexes_c_l": round(sim["servi_calendrier_l"], 1),
            "jours_avec_vente_biere": sim["jours_avec_vente_biere"],
            "premier_jour": sim["premier_jour"], "dernier_jour": sim["dernier_jour"],
            "futs_perces_simules": sim["futs_perces"],
            "futs_perimes_30j": len(sim["perimes"]),
            "perte_peremption_l": round(sim["perte_peremption_l"], 1),
            "peremption_hypothese_caisse": {
                "futs": len(sim_caisse["perimes"]),
                "litres": round(sim_caisse["perte_peremption_l"], 1),
            },
            "mois_les_plus_faibles": sorted(mois.items(), key=lambda kv: kv[1])[:5],
        },
        "postes_constructeur_l": round(plancher_l, 1),
        "postes_constructeur_pct_fut": round(100 * plancher_l / tot["achat"], 2),
        "contenance_servie_l": round(
            sum(r["qte"][e] * r["verre_cl"] / 100.0 for r in ventes for e in EXOS), 2),
        "part_non_biere_l": round(
            sum(r["qte"][e] * (r["verre_cl"] - r["biere_cl"]) / 100.0
                for r in ventes for e in EXOS), 2),
        "freinte_retenue_l": round(tot["fr_ret"], 2),
        "freinte_retenue_pct_fut": round(100 * tot["fr_ret"] / tot["achat"], 2),
        "freinte_memoire_10_07_2026_l": 129.0,
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
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cell.border = border
        for ln in lignes:
            ws.append(ln)
        for r in range(hrow + 1, hrow + 1 + len(lignes)):
            for c in range(1, len(colonnes) + 1):
                cell = ws.cell(row=r, column=c)
                cell.border = border
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
