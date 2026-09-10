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
FREINTE_RETENUE = 0.10      # taux retenu, borne basse de la convergence
FREINTE_HAUTE = 0.20        # borne haute documentee
# Volume residuel non tirable, chiffre CONSTRUCTEUR du fut Blade 8 L :
# manuel Heineken Blade, chap. Depannage : "Le volume residuel acceptable
# s'eleve a 1,5 % (120 ml)". Le materiel n'a AUCUNE ligne a nettoyer : le tube
# de soutirage est integre au fut et jete avec lui (fiche technique Heineken :
# "Cleaning cycle: No. Disposable line in keg").
RESIDU_FUT_L = 0.120        # litres par fut de 8 L
RESIDU_PCT = 0.015

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

    tb = sv["taux_biere"]          # 0,15 sur le VOLUME de fut
    tf = sv["ab_fin"]              # 0,15 sur le CA LIQUIDES, en fin de methode
    prix = sv["prix_l_ttc"]        # EUR TTC de CA liquides par litre de biere
    ampli = 1.0 + sv["coef_liq_sol"]   # liquides + solides extrapoles

    lignes_cascade, lignes_taux, lignes_fin = [], [], []
    tot = dict.fromkeys(
        ["achat", "futs", "servi", "residu", "fr10", "fr20",
         "ab1", "net1", "ab2", "ret", "p_remise", "p_pertes", "p_perso"], 0.0)

    for e in EXOS:
        a = achats_l[e]
        nb = a / CONTENANCE_FUT_L
        residu = nb * RESIDU_FUT_L
        fr10, fr20 = a * FREINTE_RETENUE, a * FREINTE_HAUTE
        ab1 = a * tb
        net1 = a - ab1
        ab2 = net1 * tf
        ret = ab1 + ab2
        lignes_cascade.append([
            EXL[e], round(a, 1), round(nb), round(residu, 2), round(fr10, 1),
            round(a - fr10, 1), round(fr20, 1), round(a - fr20, 1),
            round(servi[e], 1),
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
                     ("residu", residu), ("fr10", fr10), ("fr20", fr20),
                     ("ab1", ab1), ("net1", net1), ("ab2", ab2), ("ret", ret),
                     ("p_remise", net1 * sv["ab_remise"]),
                     ("p_pertes", net1 * sv["ab_pertes"]),
                     ("p_perso", net1 * sv["ab_perso"])):
            tot[k] += v

    lignes_cascade.append([
        "TOTAL 3 exercices", round(tot["achat"], 1), round(tot["futs"]),
        round(tot["residu"], 2), round(tot["fr10"], 1),
        round(tot["achat"] - tot["fr10"], 1), round(tot["fr20"], 1),
        round(tot["achat"] - tot["fr20"], 1), round(tot["servi"], 1)])
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
    par_litre_liq = prix * (1 - tf)
    par_litre_tot = par_litre_liq * ampli          # 1 L de fut -> CA total reconstitue
    par_litre_fin = prix * ampli                   # 1 L retire en fin de methode
    ecart_addition_l = tot["achat"] * (0.30 - tot["ret"] / tot["achat"])
    lignes_euro = [
        ["Prix moyen TTC du litre de bière retenu par le service",
         round(prix, 2), "EUR/L", "annexes finales : CA bière reconstitué / volume valorisé"],
        ["Abattements de fin de méthode appliqués au CA liquides",
         round(100 * tf, 1), "%", "5 % remise + 5 % pertes + 5 % conso personnel"],
        ["Coefficient liquides -> solides appliqué par le service",
         sv["coef_liq_sol"], "x", "CA solides = CA liquides après abattements x 3,10"],
        ["CA total reconstitué TTC entraîné par 1 litre de fût",
         round(par_litre_tot, 2), "EUR/L", "= prix du litre x (1 - 15 %) x (1 + 3,10)"],
        ["Valeur du 1er abattement (15 % du fût), 3 exercices",
         round(tot["ab1"] * par_litre_tot, 0), "EUR",
         f"{fr(tot['ab1'],1)} L x {fr(par_litre_tot,2)} EUR/L"],
        ["Valeur du 2e abattement (15 % en fin de méthode) sur la seule bière",
         round(tot["ab2"] * par_litre_fin, 0), "EUR",
         f"{fr(tot['ab2'],1)} L x {fr(par_litre_fin,2)} EUR/L"],
        ["Taux réel retiré par le service sur le fût",
         round(100 * tot["ret"] / tot["achat"], 2), "%", "et non 30 % : 1 - 0,85 x 0,85"],
        ["Écart entre le taux revendiqué (30 %) et le taux réel", 2.25, "points de fût",
         f"soit {fr(ecart_addition_l,1)} L sur 3 exercices"],
        ["Écart en CA total reconstitué TTC",
         round(ecart_addition_l * par_litre_tot, 0), "EUR",
         "aux paramètres du service (prix du litre et coefficient 3,10)"],
        ["Freinte retenue par la défense (10 % de la contenance servie)",
         129.0, "L", "soit 6,2 % du fût acheté, donc moins que les 15 % du service"],
        ["Volume résiduel jeté avec les fûts (262 x 120 ml)",
         round(tot["residu"], 2), "L", "manuel Heineken Blade : 1,5 % (120 ml) par fût"],
    ]

    onglets = [
        ("1. Futs achetes et biere servie",
         ["Article de caisse", "Contenance verre (cl)", "Part bière (cl)"]
         + [c for e in EXOS for c in (f"{EXL[e]} qté", f"{EXL[e]} L bière")]
         + ["Total qté", "Total L bière"],
         lignes_ventes, [30, 16, 14] + [12] * 6 + [12, 14]),
        ("2. Du fut achete au facturable",
         ["Exercice", "Fûts achetés (L)", "Nombre de fûts de 8 L",
          "Volume résiduel non tirable 1,5 % (L) - manuel Heineken Blade",
          "Freinte au taux retenu 10 % (L)", "Volume facturable à 10 % (L)",
          "Freinte à la borne haute 20 % (L)", "Volume facturable à 20 % (L)",
          "Bière servie en caisse (L)"],
         lignes_cascade, [20, 15, 16, 22, 16, 16, 16, 16, 16]),
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
        ("5. Litres et euros",
         ["Grandeur", "Valeur", "Unité", "Source ou calcul"],
         lignes_euro, [58, 14, 14, 52]),
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
        "residu_l": tot["residu"], "freinte_10_l": tot["fr10"],
        "freinte_20_l": tot["fr20"],
        "facturable_10_l": tot["achat"] - tot["fr10"],
        "facturable_20_l": tot["achat"] - tot["fr20"],
        "service_ab1_l": tot["ab1"], "service_ab2_l": tot["ab2"],
        "service_total_retire_l": tot["ret"],
        "service_taux_reel_pct": 100 * tot["ret"] / tot["achat"],
        "fin_methode": {"remise_l": tot["p_remise"], "pertes_l": tot["p_pertes"],
                        "perso_l": tot["p_perso"]},
        "prix_l_ttc": prix, "ca_par_litre_ttc": par_litre_tot,
        "ca_par_litre_fin": par_litre_fin,
        "valeur_ab1_eur": tot["ab1"] * par_litre_tot,
        "valeur_ab2_eur": tot["ab2"] * par_litre_fin,
        "ecart_addition_l": ecart_addition_l,
        "ecart_addition_eur": ecart_addition_l * par_litre_tot,
        "dispo_service_l": sv["dispo_l"], "futs_service": sv["futs"],
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
