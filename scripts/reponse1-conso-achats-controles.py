#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reponse1-conso-achats-controles.py

Piece de la reponse au courrier DDFiP 39 du 04/09/2026, partie I
"Consommation vendue superieure aux achats" (p. 48 a 53).

Produit public/documents/pieces-reponse-1/R1-conso-achats-controles.xlsx :
  1. "Controle arithmetique" : chaque cellule "Volumes Disparus" des QUATRE
     tableaux opposes par le service (p. 48/51/52/53) est recalculee a partir
     des deux colonnes qui la precedent, selon la formule que le service
     applique lui-meme : (Disponibles - Vendues) / Disponibles.
     Source des valeurs imprimees : src/data/reponse1/consommation-superieure-achats.json
     (transcription fidele du courrier, chapitre 1).
  2. "Anomalies" : les seules lignes ou la valeur imprimee ne se deduit pas
     des deux colonnes affichees.
  3. "Bilan matiere famille" : rapprochement caisse / factures / inventaire
     agrege par famille de boissons.
  4. "Bilan matiere produit" : le meme detail, produit par produit.
  5. "Calvados verre vs cuisine" : separation de la dose SERVIE au verre et de
     la dose utilisee EN CUISINE, plat par plat.

Sources (lecture seule) :
  - src/data/reponse1/consommation-superieure-achats.json
  - src/data/boissonsPageData.json  (disparuParBoisson : achats factures,
    conso caisse + cuisine, stock inventaire)
  - public/documents/vins-boissons/conso-exacte-carte.xlsx  (detail par plat)
"""
import os
import json
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

ICI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(ICI, ".."))
SRC = os.path.join(ROOT, "src/data/reponse1/consommation-superieure-achats.json")
BDJ = os.path.join(ROOT, "src/data/boissonsPageData.json")
CARTE = os.path.join(ROOT, "public/documents/vins-boissons/conso-exacte-carte.xlsx")
OUTDIR = os.path.join(ROOT, "public/documents/pieces-reponse-1")
OUT = os.path.join(OUTDIR, "R1-conso-achats-controles.xlsx")

GRAS = Font(bold=True)
GBLANC = Font(bold=True, color="FFFFFF")
ENTETE = PatternFill("solid", fgColor="0F766E")
ROUGE = PatternFill("solid", fgColor="FEE2E2")
CENTRE = Alignment(horizontal="center", vertical="center", wrap_text=True)
GAUCHE = Alignment(horizontal="left", vertical="center", wrap_text=True)
BORD = Border(*(4 * (Side(style="thin", color="D1D5DB"),)))

# ---------------------------------------------------------------------------
# 1. Controle arithmetique des quatre tableaux du service
# ---------------------------------------------------------------------------
DOC = json.load(open(SRC, encoding="utf-8"))
SECTIONS = DOC["sections"]

TABLEAUX = {
    "Vins (p. 48, repris p. 52)": "Vins : le tableau opposé",
    "Articles vendus à la dose (p. 51)": "Articles vendus à la dose",
    "Articles Complexes (p. 52)": "« Articles Complexes »",
    "Articles vendus à l’unité (p. 53)": "Articles vendus à l’unité",
}
EXOS = ["31/03/2023", "31/03/2024", "31/03/2025"]


def num(s):
    s = str(s).replace(" ", " ").replace("\xa0", " ").strip()
    if s == "":
        return None
    s = s.replace("%", "").replace(" ", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def fr(v, dec=2):
    if v is None:
        return ""
    return f"{v:,.{dec}f}".replace(",", " ").replace(".", ",")


def trouver(fragment):
    for s in SECTIONS:
        if s.get("kind") == "tableau" and fragment in s.get("titre", ""):
            return s
    raise SystemExit("tableau introuvable : " + fragment)


controles = []
for nom, frag in TABLEAUX.items():
    tab = trouver(frag)
    for ligne in tab["lignes"]:
        libelle = ligne[0]["v"]
        for k, exo in enumerate(EXOS):
            dispo = num(ligne[1 + 3 * k]["v"])
            vend = num(ligne[2 + 3 * k]["v"])
            pct = num(ligne[3 + 3 * k]["v"])
            if pct is None:
                continue
            if dispo is None or vend is None:
                controles.append([nom, libelle, exo, dispo, vend, pct, None, None,
                                  "ANOMALIE", "Colonne « quantites vendues » laissee vide : "
                                  "le pourcentage imprime ne se rattache a aucune quantite"])
                continue
            if dispo == 0 and not vend:
                st = "ANOMALIE" if pct else "Ligne vide"
                controles.append([nom, libelle, exo, dispo, vend, pct, None, None, st,
                                  "0 disponible et 0 vendue : le service imprime "
                                  f"{fr(pct)} % de « volumes disparus »" if pct else
                                  "Ligne entierement a zero, sans portee"])
                continue
            if dispo == 0:
                controles.append([nom, libelle, exo, dispo, vend, pct, None, None, "ANOMALIE",
                                  "Disponibles = 0 pour des ventes reelles : le rapport n’est "
                                  "pas defini et le service imprime 0,00 %, la ou sa propre "
                                  "logique donnerait l’ecart maximal"])
                continue
            rec = round((dispo - vend) / dispo * 100, 2)
            ok = abs(rec - pct) <= 0.6
            controles.append([nom, libelle, exo, dispo, vend, pct, rec,
                              None if ok else round(pct - rec, 2),
                              "Conforme" if ok else "ANOMALIE",
                              "Conforme" if ok else
                              "Le pourcentage imprime ne se deduit pas des deux colonnes "
                              "affichees en face de lui"])

anomalies = [c for c in controles if c[8] == "ANOMALIE"]
nb_ok = sum(1 for c in controles if c[8] == "Conforme")
nb_vide = sum(1 for c in controles if c[8] == "Ligne vide")

# ---------------------------------------------------------------------------
# 2. Bilan matiere par famille : caisse / factures / inventaire
# ---------------------------------------------------------------------------
BD = json.load(open(BDJ, encoding="utf-8"))
ROWS = BD["disparuParBoisson"]

FAMILLES = {
    "vin": "Vins tranquilles",
    "vin_rouge": "Vins tranquilles",
    "vin_blanc": "Vins tranquilles",
    "vin_rose": "Vins tranquilles",
    "petillant": "Cremant et champagne",
    "vin_de_liqueur": "Vins de liqueur (Macvin)",
    "biere": "Bieres",
    "cidre": "Cidres",
    "aperitif": "Aperitifs",
    "liqueur": "Liqueurs",
    "eau_de_vie": "Eaux-de-vie et digestifs",
    "spiritueux": "Spiritueux",
}
ORDRE = ["Vins tranquilles", "Cremant et champagne", "Vins de liqueur (Macvin)",
         "Bieres", "Cidres", "Aperitifs", "Liqueurs", "Eaux-de-vie et digestifs",
         "Spiritueux"]

agg = {}
for r in ROWS:
    f = FAMILLES.get(r.get("categorie"), "Autres")
    a = agg.setdefault(f, {"n": 0, "achat": 0.0, "conso": 0.0, "stock": 0.0})
    a["n"] += 1
    a["achat"] += r.get("achat_l", 0.0)
    a["conso"] += r.get("conso_l", 0.0)
    a["stock"] += r.get("stock_l", 0.0)

fam_rows = []
t_achat = t_conso = t_stock = 0.0
t_n = 0
for f in ORDRE + sorted(set(agg) - set(ORDRE)):
    if f not in agg:
        continue
    a = agg[f]
    net = a["achat"] - a["conso"] - a["stock"]
    fam_rows.append([f, a["n"], round(a["achat"], 1), round(a["conso"], 1),
                     round(a["stock"], 1), round(net, 1),
                     round(net / a["achat"] * 100, 1) if a["achat"] else None,
                     "Excedent d’achat" if net >= 0 else "Deficit apparent"])
    t_achat += a["achat"]
    t_conso += a["conso"]
    t_stock += a["stock"]
    t_n += a["n"]
t_net = t_achat - t_conso - t_stock
fam_rows.append(["TOTAL", t_n, round(t_achat, 1), round(t_conso, 1), round(t_stock, 1),
                 round(t_net, 1), round(t_net / t_achat * 100, 1), "Excedent d’achat"])

prod_rows = []
for r in sorted(ROWS, key=lambda x: -(x.get("achat_l", 0) - x.get("conso_l", 0) - x.get("stock_l", 0))):
    net = r.get("achat_l", 0) - r.get("conso_l", 0) - r.get("stock_l", 0)
    prod_rows.append([FAMILLES.get(r.get("categorie"), "Autres"), r["nom"],
                      round(r.get("achat_l", 0), 1), round(r.get("conso_l", 0), 1),
                      round(r.get("stock_l", 0), 1), round(net, 1)])

# ---------------------------------------------------------------------------
# 3. Calvados : dose servie au verre contre dose utilisee en cuisine
# ---------------------------------------------------------------------------
wbc = openpyxl.load_workbook(CARTE, data_only=False)
wsc = wbc["Conso exacte carte"]
calva = {}
for row in wsc.iter_rows(min_row=2, values_only=True):
    if not row or len(row) < 11:
        continue
    alcool = str(row[8] or "")
    if "alvados" not in alcool:
        continue
    usage = str(row[5] or "")
    produit = str(row[2] or "").strip()
    qte = row[6] or 0
    dose = row[7] or 0
    cl = row[10] or 0
    if not isinstance(qte, (int, float)) or not isinstance(cl, (int, float)):
        continue
    cle = (usage, produit, dose, alcool)
    c = calva.setdefault(cle, {"qte": 0.0, "cl": 0.0})
    c["qte"] += qte
    c["cl"] += cl

calva_rows = []
verre_cl = cuisine_cl = 0.0
for (usage, produit, dose, alcool), v in sorted(
        calva.items(), key=lambda kv: (kv[0][0], -kv[1]["cl"])):
    au_verre = usage.startswith("Au verre")
    if au_verre:
        verre_cl += v["cl"]
    else:
        cuisine_cl += v["cl"]
    calva_rows.append([
        "Dose SERVIE (vente au verre)" if au_verre else "Dose EN CUISINE (flambage, rotissage)",
        produit, alcool, dose, round(v["qte"], 1), round(v["cl"], 1),
        round(v["cl"] / 100.0, 2),
        round(v["cl"] / 200.0, 2) if not au_verre else round(v["cl"] / 100.0, 2),
    ])
calva_rows.append(["TOTAL dose servie au verre", "", "", "", "", round(verre_cl, 1),
                   round(verre_cl / 100.0, 2), round(verre_cl / 100.0, 2)])
calva_rows.append(["TOTAL dose en cuisine", "", "", "", "", round(cuisine_cl, 1),
                   round(cuisine_cl / 100.0, 2), round(cuisine_cl / 200.0, 2)])

# ---------------------------------------------------------------------------
# Ecriture
# ---------------------------------------------------------------------------
TITRE = ("La Demi-Lune : controles de la partie I de la reponse du service du 04/09/2026 "
         "(consommation vendue superieure aux achats, p. 48 a 53)")


def feuille(wb, i, nom, sous_titre, headers, rows, widths, rouge_si=None):
    ws = wb.active if i == 0 else wb.create_sheet()
    ws.title = nom[:31]
    ws.append([TITRE])
    ws["A1"].font = GRAS
    ws.append([sous_titre])
    ws["A2"].alignment = GAUCHE
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=max(1, len(headers)))
    ws.row_dimensions[2].height = 34
    ws.append([])
    hr = ws.max_row + 1
    ws.append(headers)
    for c in range(1, len(headers) + 1):
        cell = ws.cell(row=hr, column=c)
        cell.font = GBLANC
        cell.fill = ENTETE
        cell.alignment = CENTRE
        cell.border = BORD
    for row in rows:
        r = ws.max_row + 1
        ws.append(row)
        rouge = rouge_si(row) if rouge_si else False
        for c in range(1, len(headers) + 1):
            cell = ws.cell(row=r, column=c)
            cell.border = BORD
            if rouge:
                cell.fill = ROUGE
    for j, w in enumerate(widths, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(j)].width = w
    ws.freeze_panes = "A" + str(hr + 1)


wb = openpyxl.Workbook()

H_CTRL = ["Tableau du service", "Designation (libelle du courrier)", "Exercice clos",
          "Quantites Disponibles (imprime)", "Quantites Vendues (imprime)",
          "Volumes Disparus % (imprime)", "% recalcule = (Disponibles - Vendues) / Disponibles",
          "Ecart (imprime - recalcule)", "Statut", "Diagnostic"]
feuille(wb, 0, "Controle arithmetique",
        f"Chaque pourcentage « Volumes Disparus » imprime par le service est recalcule a partir "
        f"des deux colonnes qui le precedent, avec la formule que le service applique lui-meme. "
        f"{len(controles)} cellules controlees, {nb_ok} conformes, {nb_vide} lignes entierement "
        f"a zero, {len(anomalies)} non reproductibles.",
        H_CTRL, controles, [30, 40, 14, 16, 16, 16, 20, 16, 12, 62],
        rouge_si=lambda r: r[8] == "ANOMALIE")

feuille(wb, 1, "Anomalies",
        "Les seules lignes pour lesquelles le pourcentage imprime ne se deduit pas des deux "
        "colonnes affichees en face de lui.",
        H_CTRL, anomalies, [30, 40, 14, 16, 16, 16, 20, 16, 12, 62],
        rouge_si=lambda r: True)

H_FAM = ["Famille de boissons", "Nb de produits", "Achats factures (L)",
         "Consommation caisse + cuisine (L)", "Variation d’inventaire (L)",
         "Bilan matiere net (L)", "Bilan / achats (%)", "Lecture"]
feuille(wb, 2, "Bilan matiere famille",
        f"Bilan matiere = achats (factures fournisseur, nets des avoirs) - consommation "
        f"(caisse + cuisine mesurees) - variation d’inventaire. Total : {fr(t_achat, 1)} L achetes, "
        f"{fr(t_conso, 1)} L consommes, {fr(t_stock, 1)} L de stock, soit {fr(t_net, 1)} L nets.",
        H_FAM, fam_rows, [30, 14, 18, 22, 20, 18, 16, 22])

H_PROD = ["Famille", "Produit", "Achats factures (L)", "Conso caisse + cuisine (L)",
          "Inventaire (L)", "Bilan net (L)"]
feuille(wb, 3, "Bilan matiere produit",
        "Le meme bilan, produit par produit, trie du plus excedentaire au plus deficitaire.",
        H_PROD, prod_rows, [26, 42, 18, 22, 16, 16])

H_CAL = ["Usage", "Libelle de caisse", "Alcool", "Dose (cl)", "Quantite (3 exercices)",
         "Volume a 4 cl (cl)", "Volume a 4 cl (L)", "Volume a 2 cl en cuisine (L)"]
feuille(wb, 4, "Calvados verre vs cuisine",
        f"La dose de 4 cl communiquee au verificateur est une dose de FLAMBAGE. Sur trois "
        f"exercices, la caisse ne vend que {fr(verre_cl / 100.0, 2)} L de Calvados au verre ; "
        f"{fr(cuisine_cl / 100.0, 1)} L partent en cuisine (plats et desserts flambes ou rotis).",
        H_CAL, calva_rows, [34, 26, 24, 10, 16, 16, 16, 18])

os.makedirs(OUTDIR, exist_ok=True)
wb.save(OUT)

print("Ecrit :", OUT)
print(f"  cellules % controlees : {len(controles)}  conformes : {nb_ok}  "
      f"lignes vides : {nb_vide}  anomalies : {len(anomalies)}")
for a in anomalies:
    print("   -", a[0], "|", a[1], "|", a[2], "| imprime", a[5], "| recalcule", a[6])
print(f"  bilan matiere : achats {round(t_achat,1)} L  conso {round(t_conso,1)} L  "
      f"stock {round(t_stock,1)} L  net {round(t_net,1)} L")
for r in fam_rows:
    print("   ", r)
print(f"  Calvados : verre {round(verre_cl/100.0,2)} L  cuisine {round(cuisine_cl/100.0,1)} L "
      f"(a 2 cl : {round(cuisine_cl/200.0,1)} L)")
for r in calva_rows:
    print("   ", r)
