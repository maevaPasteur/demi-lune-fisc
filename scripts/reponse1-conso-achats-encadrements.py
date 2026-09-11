#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reponse1-conso-achats-encadrements.py

Deuxieme piece de la reponse au courrier DDFiP 39 du 04/09/2026, partie I
"Consommation vendue superieure aux achats" (p. 48 a 53).

Produit public/documents/pieces-reponse-1/R1-conso-achats-encadrements.xlsx :

  1. "Eaux-de-vie encadrement" : le SEUL deficit du bilan matiere par famille
     (-45,1 L sur les eaux-de-vie et digestifs) est ferme exactement comme le
     Calvados l'a ete : en encadrant la dose de cuisine entre 2 et 3 cl et en
     constatant que le bilan de la famille change de signe a l'interieur de
     l'intervalle. La dose d'equilibre est calculee, elle n'est pas postulee.

  2. "Doses etendues" : reponse chiffree a l'affirmation du service (p. 50)
     selon laquelle etendre la correction de dose "a toutes les doses d'alcool"
     aurait "fortement accru" les ecarts. Poste par poste, avec les propres
     tableaux du service (p. 51 et 52), on montre que chacun des cinq postes
     qu'il cite est DEJA excedentaire (achete plus que vendu) et que reduire la
     dose ne peut qu'augmenter cet excedent, jamais faire apparaitre une
     consommation superieure aux achats.

  3. "Sens des ecarts" : sur les quatre tableaux opposes, decompte des cellules
     ou les quantites vendues depassent les quantites disponibles (seules
     cellules qui materialisent le grief de la partie I) et volume correspondant.

Sources (lecture seule) :
  - src/data/boissonsPageData.json (disparuParBoisson : achats factures,
    conso caisse + cuisine, variation d'inventaire, 65 produits)
  - src/data/reponse1/consommation-superieure-achats.json (chapitre 1 :
    transcription fidele des quatre tableaux du courrier, p. 48, 51, 52 et 53)
"""
import os
import json
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

ICI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(ICI, ".."))
SRC = os.path.join(ROOT, "src/data/reponse1/consommation-superieure-achats.json")
BDJ = os.path.join(ROOT, "src/data/boissonsPageData.json")
OUTDIR = os.path.join(ROOT, "public/documents/pieces-reponse-1")
OUT = os.path.join(OUTDIR, "R1-conso-achats-encadrements.xlsx")

GRAS = Font(bold=True)
GBLANC = Font(bold=True, color="FFFFFF")
ENTETE = PatternFill("solid", fgColor="0F766E")
ROUGE = PatternFill("solid", fgColor="FEE2E2")
VERT = PatternFill("solid", fgColor="DCFCE7")
CENTRE = Alignment(horizontal="center", vertical="center", wrap_text=True)
GAUCHE = Alignment(horizontal="left", vertical="center", wrap_text=True)
BORD = Border(*(4 * (Side(style="thin", color="D1D5DB"),)))

DOC = json.load(open(SRC, encoding="utf-8"))
SECTIONS = DOC["sections"]
BD = json.load(open(BDJ, encoding="utf-8"))
ROWS = BD["disparuParBoisson"]
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


def fr(v, dec=1):
    if v is None:
        return ""
    return f"{v:,.{dec}f}".replace(",", " ").replace(".", ",")


def trouver(fragment):
    for s in SECTIONS:
        if s.get("kind") == "tableau" and fragment in s.get("titre", ""):
            return s
    raise SystemExit("tableau introuvable : " + fragment)


# ---------------------------------------------------------------------------
# 1. Eaux-de-vie : encadrement de la dose de cuisine
# ---------------------------------------------------------------------------
EDV = [r for r in ROWS if r.get("categorie") == "eau_de_vie"]
CAL = next(r for r in EDV if r["nom"] == "Calvados")
AUTRES = [r for r in EDV if r["nom"] != "Calvados"]

ACH_FAM = sum(r["achat_l"] for r in EDV)
CONSO_FAM = sum(r["conso_l"] for r in EDV)
STOCK_FAM = sum(r["stock_l"] for r in EDV)
BILAN_FAM = ACH_FAM - CONSO_FAM - STOCK_FAM

# Calvados : separation dose SERVIE au verre / dose EN CUISINE (annexes C1 a C3,
# reprises dans la feuille "Calvados verre vs cuisine" de R1-conso-achats-controles).
VERRE_L = 1.44                      # 36 doses de 4 cl vendues au verre en 3 exercices
DOSE_SERVICE = 4.0                  # dose communiquee au verificateur
CUISINE_L_4CL = CAL["conso_l"] - VERRE_L   # tout le reste, compte a 4 cl par plat


def conso_calvados(dose):
    """Consommation totale de Calvados (L) pour une dose de cuisine donnee."""
    return VERRE_L + CUISINE_L_4CL * dose / DOSE_SERVICE


def bilan_famille(dose):
    conso = CONSO_FAM - CAL["conso_l"] + conso_calvados(dose)
    return ACH_FAM - conso - STOCK_FAM, conso


# dose d'equilibre : celle qui annule le bilan de la famille
DOSE_EQ_FAM = ((ACH_FAM - STOCK_FAM - (CONSO_FAM - CAL["conso_l"]) - VERRE_L)
               / CUISINE_L_4CL * DOSE_SERVICE)
# dose d'equilibre du seul Calvados, meme base
DOSE_EQ_CAL = ((CAL["achat_l"] - CAL["stock_l"] - VERRE_L) / CUISINE_L_4CL * DOSE_SERVICE)

edv_rows = []
for dose, libelle in [(4.0, "4 cl : dose retenue par le service (p. 49)"),
                      (3.0, "3 cl : borne haute"),
                      (round(DOSE_EQ_FAM, 2), "dose d’equilibre de la famille (calculee)"),
                      (2.0, "2 cl : borne basse")]:
    bilan, conso = bilan_famille(dose)
    edv_rows.append([libelle, dose, round(conso_calvados(dose), 1), round(conso, 1),
                     round(ACH_FAM, 1), round(STOCK_FAM, 1), round(bilan, 1),
                     "Deficit : impossible, la famille aurait consomme "
                     "plus qu’elle n’a achete" if bilan < -0.05 else
                     ("Bilan ferme" if abs(bilan) <= 0.05 else "Excedent d’achat")])

edv_detail = []
for r in sorted(EDV, key=lambda x: -x["achat_l"]):
    net = r["achat_l"] - r["conso_l"] - r["stock_l"]
    edv_detail.append([r["nom"], round(r["achat_l"], 1), round(r["conso_l"], 1),
                       round(r["stock_l"], 1), round(net, 1)])
edv_detail.append(["TOTAL famille", round(ACH_FAM, 1), round(CONSO_FAM, 1),
                   round(STOCK_FAM, 1), round(BILAN_FAM, 1)])
# la famille hors Calvados
ach_a = sum(r["achat_l"] for r in AUTRES)
con_a = sum(r["conso_l"] for r in AUTRES)
sto_a = sum(r["stock_l"] for r in AUTRES)
edv_detail.append(["dont famille hors Calvados", round(ach_a, 1), round(con_a, 1),
                   round(sto_a, 1), round(ach_a - con_a - sto_a, 1)])

# ---------------------------------------------------------------------------
# 2. Les cinq postes que le service dit qu’il aurait fallu corriger (p. 50)
# ---------------------------------------------------------------------------
T_DOSE = trouver("Articles vendus à la dose")
T_CPLX = trouver("« Articles Complexes »")
T_VINS = trouver("Vins : le tableau opposé")


def somme_lignes(tab, libelles):
    """Totalise, sur les trois exercices, les colonnes disponibles / vendues."""
    d = v = 0.0
    trouves = []
    for ligne in tab["lignes"]:
        lib = ligne[0]["v"]
        if lib in libelles:
            trouves.append(lib)
            for k in range(3):
                dd = num(ligne[1 + 3 * k]["v"])
                vv = num(ligne[2 + 3 * k]["v"])
                d += dd or 0.0
                v += vv or 0.0
    manquants = set(libelles) - set(trouves)
    if manquants:
        raise SystemExit("libelles introuvables : " + ", ".join(sorted(manquants)))
    return d, v


POSTES = [
    ("le vin jaune", T_DOSE, ["Vin jaune"], "p. 51, tableau « Articles vendus à la dose »"),
    ("le vin pour les sauces et le vin pour la cuisine", T_VINS, ["VINS EN BIB"],
     "p. 48 et 52, ligne « VINS EN BIB » (les cubis dont le service retranche lui-même "
     "la part cuisine, p. 69)"),
    ("le vin pour tous les cocktails (4 cl retenus)", T_CPLX,
     ["CREMANT", "MACVIN", "SOHO", "VODKA", "PASSOA", "TEQUILA", "PICON",
      "LIMONADE", "JUS DE FRUIT"],
     "p. 52, tableau « Articles Complexes » (les ingrédients de cocktail du service)"),
    ("les sirops (4 cl retenus)", T_DOSE, ["SIROP A L’EAU"],
     "p. 51, tableau « Articles vendus à la dose »"),
]

postes_rows = []
tot_d = tot_v = 0.0
for nom, tab, libs, src in POSTES:
    d, v = somme_lignes(tab, libs)
    tot_d += d
    tot_v += v
    ecart = d - v
    ecart_moitie = d - v / 2.0
    postes_rows.append([
        nom, src, round(d), round(v), round(ecart),
        round(ecart / d * 100, 2) if d else None,
        round(v / 2.0), round(ecart_moitie),
        round(ecart_moitie / d * 100, 2) if d else None,
        "Excedent d’achat, avant comme apres" if ecart > 0 and ecart_moitie > 0 else "A EXAMINER",
    ])
ecart_t = tot_d - tot_v
ecart_t2 = tot_d - tot_v / 2.0
postes_rows.append(["TOTAL des postes cites par le service", "",
                    round(tot_d), round(tot_v), round(ecart_t),
                    round(ecart_t / tot_d * 100, 2), round(tot_v / 2.0), round(ecart_t2),
                    round(ecart_t2 / tot_d * 100, 2), "Excedent d’achat, avant comme apres"])

# ---------------------------------------------------------------------------
# 3. Sens des ecarts : ou la consommation depasse-t-elle vraiment les achats ?
# ---------------------------------------------------------------------------
# Les quatre tableaux ne sont pas homogenes : la colonne « Format Quantites » du
# courrier indique des CENTILITRES (vins, articles a la dose, articles complexes),
# des GRAMMES (la seule ligne CAFE) et des UNITES (articles vendus a l’unite).
# Les volumes ne sont donc totalises qu’a l’interieur de chaque unite de mesure.
TOUS = [
    ("Vins (p. 48 et 52)", "Vins : le tableau opposé", "cl"),
    ("Articles vendus à la dose (p. 51)", "Articles vendus à la dose", "cl"),
    ("Articles Complexes (p. 52)", "« Articles Complexes »", "cl"),
    ("Articles vendus à l’unité (p. 53)", "Articles vendus à l’unité", "unité"),
]
sens_rows = []
n_pos = n_neg = n_nul = 0
dispo_u = {"cl": 0.0, "unité": 0.0, "g": 0.0}
neg_u = {"cl": 0.0, "unité": 0.0, "g": 0.0}
neg_n = {"cl": 0, "unité": 0, "g": 0}
for nom, frag, unite in TOUS:
    tab = trouver(frag)
    for ligne in tab["lignes"]:
        lib = ligne[0]["v"]
        u = "g" if lib.strip().upper().startswith("CAFE") else unite
        for k, exo in enumerate(EXOS):
            d = num(ligne[1 + 3 * k]["v"])
            v = num(ligne[2 + 3 * k]["v"])
            if d is None and v is None:
                continue
            d = d or 0.0
            v = v or 0.0
            dispo_u[u] += d
            if v > d:
                n_neg += 1
                neg_u[u] += v - d
                neg_n[u] += 1
                sens_rows.append([nom, lib, exo, round(d), round(v), round(v - d), u,
                                  "Vendues > disponibles"])
            elif d > v:
                n_pos += 1
            else:
                n_nul += 1
for u in ("cl", "unité", "g"):
    sens_rows.append([f"TOTAL des cellules « vendues > disponibles » ({u})", "", "",
                      round(dispo_u[u]), "", round(neg_u[u]), u,
                      f"{neg_n[u]} cellules sur {n_pos + n_nul + n_neg} controlees"])

# ---------------------------------------------------------------------------
# 4. Achats factures non rattaches : notre propre bilan est un plancher
# ---------------------------------------------------------------------------
import datetime
FACT = json.load(open(os.path.join(ROOT, "src/data/factures-fournisseur.json"), encoding="utf-8"))
D0, D1 = datetime.date(2022, 4, 1), datetime.date(2025, 3, 31)
CIBLES = [
    ("Chablis", "CHABLIS", 75.0, "Chablis"),
    ("Gewurztraminer", "GEWURZ", 75.0, "Gewurztraminer"),
    ("Arbois Béthanie, demi-bouteilles 37,5 cl", "BETHANIE 37,5", 37.5, "Arbois Béthanie"),
    ("Arbois Béthanie, bouteilles 75 cl", "BETHANIE 75", 75.0, "Arbois Béthanie"),
]
BILAN = {r["nom"]: r for r in ROWS}
rat_rows = []
tot_manque = 0.0
for lib, cle, contenance, produit in CIBLES:
    q = 0.0
    for f in FACT["factures"]:
        try:
            da = datetime.datetime.strptime(f.get("dateFacture") or "", "%d/%m/%Y").date()
        except ValueError:
            continue
        if not (D0 <= da <= D1):
            continue
        for l in f["lignes"]:
            des = (l.get("designation") or "").upper()
            if cle in des and "DECONSIGNE" not in des and "CARAMBAR" not in des:
                q += l.get("quantite") or 0
    litres = q * contenance / 100.0
    rat_rows.append([lib, produit, round(q), contenance, round(litres, 1),
                     round(BILAN[produit]["achat_l"], 1)])
# volume facture non repris au poste achat du bilan, par produit
manques = []
for produit in ("Chablis", "Gewurztraminer", "Arbois Béthanie"):
    facture = sum(r[4] for r in rat_rows if r[1] == produit)
    retenu = BILAN[produit]["achat_l"]
    manques.append([produit, round(facture, 1), round(retenu, 1), round(facture - retenu, 1)])
    tot_manque += facture - retenu
manques.append(["TOTAL", round(sum(m[1] for m in manques), 1),
                round(sum(m[2] for m in manques), 1), round(tot_manque, 1)])

# ---------------------------------------------------------------------------
# 5. Annexe n 5 : les 78 factures Intermarche et leur taux de TVA
# ---------------------------------------------------------------------------
import re
OCR = os.path.join(ROOT, "public/documents/rapports-des-finances-publiques/synthese/"
                          "_ocr-brut/Proposition_3_Annexes_Boissons.txt")
inter_rows, inter_ok = [], []
for ligne in open(OCR, encoding="utf-8", errors="replace").read().split("\n"):
    if "INTERMARCHE" not in ligne.upper():
        continue
    m = re.findall(r"(\d{1,3}(?:[\s.]\d{3})*,\d{2})\s*€", ligne)
    v = [float(x.replace(" ", "").replace(".", "").replace(",", ".")) for x in m]
    date = (re.match(r"\s*(\d{2}/\d{2}/\d{4})", ligne) or [None, ""])[1] if re.match(
        r"\s*(\d{2}/\d{2}/\d{4})", ligne) else ""
    coherente = len(v) >= 3 and abs(v[0] + v[1] - v[2]) < 0.05
    ht = v[0] if v else None
    tva = v[1] if len(v) > 1 and coherente else None
    taux = (tva / ht * 100) if (ht and tva) else None
    inter_rows.append([date, ht, tva, v[2] if len(v) > 2 else None,
                       round(taux, 2) if taux else None,
                       "Oui" if coherente else "Trois montants non concordants a l’OCR"])
    if coherente:
        inter_ok.append((ht, tva))
INTER_N = len(inter_rows)
INTER_HT = sum(r[1] for r in inter_rows if r[1])
OK_HT = sum(a for a, b in inter_ok)
OK_TVA = sum(b for a, b in inter_ok)
TAUX_MOY = OK_TVA / OK_HT * 100
TAUX = sorted(b / a * 100 for a, b in inter_ok)
TAUX_MED = TAUX[len(TAUX) // 2]
inter_rows.append([f"TOTAL {INTER_N} factures", round(INTER_HT, 2), round(OK_TVA, 2), None,
                   round(TAUX_MOY, 2),
                   f"{len(inter_ok)} factures dont les trois montants se recoupent"])

# ---------------------------------------------------------------------------
# Ecriture
# ---------------------------------------------------------------------------
TITRE = ("La Demi-Lune : encadrements et sens des ecarts, partie I de la reponse du service "
         "du 04/09/2026 (consommation vendue superieure aux achats, p. 48 a 53)")


def feuille(wb, i, nom, sous_titre, headers, rows, widths, rouge_si=None, vert_si=None):
    ws = wb.active if i == 0 else wb.create_sheet()
    ws.title = nom[:31]
    ws.append([TITRE])
    ws["A1"].font = GRAS
    ws.append([sous_titre])
    ws["A2"].alignment = GAUCHE
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=max(1, len(headers)))
    ws.row_dimensions[2].height = 46
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
        for c in range(1, len(headers) + 1):
            cell = ws.cell(row=r, column=c)
            cell.border = BORD
            if rouge_si and rouge_si(row):
                cell.fill = ROUGE
            elif vert_si and vert_si(row):
                cell.fill = VERT
    for j, w in enumerate(widths, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(j)].width = w
    ws.freeze_panes = "A" + str(hr + 1)


wb = openpyxl.Workbook()

feuille(wb, 0, "Eaux-de-vie encadrement",
        f"Bilan de la famille « eaux-de-vie et digestifs » selon la dose de Calvados retenue en "
        f"cuisine. A 4 cl (dose du service) la famille afficherait {fr(BILAN_FAM)} L, "
        f"c’est-a-dire une consommation superieure aux achats, ce qui est materiellement "
        f"impossible. A 2 cl elle laisserait du Calvados inemploye, ce que l’inventaire dement. "
        f"Le bilan change de signe a l’interieur de l’intervalle : la dose est necessairement "
        f"comprise entre 2 et 3 cl, et le point d’equilibre de la famille se situe a "
        f"{fr(DOSE_EQ_FAM, 2)} cl (celui du seul Calvados, meme base, a {fr(DOSE_EQ_CAL, 2)} cl).",
        ["Hypothese de dose", "Dose (cl)", "Calvados consomme (L)",
         "Consommation de la famille (L)", "Achats factures (L)", "Variation d’inventaire (L)",
         "Bilan de la famille (L)", "Lecture"],
        edv_rows, [46, 10, 18, 22, 18, 20, 18, 42],
        rouge_si=lambda r: isinstance(r[6], (int, float)) and r[6] < -0.05)

feuille(wb, 1, "Eaux-de-vie detail",
        "Detail produit par produit de la famille, aux doses actuelles (Calvados a 4 cl). "
        "Hors Calvados, la famille est excedentaire.",
        ["Produit", "Achats factures (L)", "Conso caisse + cuisine (L)",
         "Variation d’inventaire (L)", "Bilan net (L)"],
        edv_detail, [34, 20, 24, 22, 16])

feuille(wb, 2, "Doses etendues",
        "Le service ecrit (p. 50) qu’etendre la correction de dose « a toutes les doses "
        "d’alcool » aurait « fortement accru » les ecarts. Poste par poste, avec ses propres "
        "tableaux : chacun des postes qu’il cite est deja excedentaire (il a ete achete plus "
        "qu’il n’a ete vendu). Reduire une dose diminue le volume compte comme vendu, donc "
        "augmente cet excedent : aucun de ces postes ne peut, par cette voie, faire apparaitre "
        "une consommation superieure aux achats.",
        ["Poste cite par le service (p. 50)", "Tableau d’origine",
         "Quantites disponibles (3 exercices)", "Quantites vendues (3 exercices)",
         "Excedent d’achat", "Excedent / disponible (%)",
         "Quantites vendues si la dose etait divisee par deux",
         "Excedent d’achat dans cette hypothese", "Excedent / disponible (%)", "Lecture"],
        postes_rows, [40, 46, 18, 18, 16, 16, 20, 18, 16, 34],
        vert_si=lambda r: r[9].startswith("Excedent"))

feuille(wb, 3, "Sens des ecarts",
        f"Sur les quatre tableaux opposes aux pages 48, 51, 52 et 53, chaque cellule est "
        f"classee selon le SENS de l’ecart. {n_pos} cellules montrent des quantites disponibles "
        f"superieures aux quantites vendues (du produit achete et non vendu), {n_nul} sont a "
        f"egalite ou vides, et {n_neg} seulement montrent des quantites vendues superieures aux "
        f"quantites disponibles : {fr(neg_u['cl'])} cl sur {fr(dispo_u['cl'])} cl disponibles "
        f"dans les trois tableaux en centilitres, et {fr(neg_u['unité'])} unites sur "
        f"{fr(dispo_u['unité'])} disponibles dans le tableau des articles vendus a l’unite.",
        ["Tableau du service", "Designation", "Exercice clos", "Quantites disponibles",
         "Quantites vendues", "Depassement", "Unite", "Sens de l’ecart"],
        sens_rows, [34, 40, 14, 18, 18, 16, 10, 34],
        rouge_si=lambda r: r[7] == "Vendues > disponibles")

feuille(wb, 4, "Achats non rattaches",
        "Trois libelles de notre propre bilan matiere portent un poste « achats » inferieur aux "
        "quantites que les factures Franche-Comte Boissons Services mentionnent sur la periode : "
        "les millesimes sont factures sous des designations distinctes et les demi-bouteilles "
        "ne sont pas rattachees au produit. Notre bilan est donc, lui aussi, un plancher : "
        f"{fr(tot_manque)} L d’achats factures n’y figurent pas.",
        ["Produit du bilan", "Volume lu sur les factures (L)", "Volume retenu au bilan (L)",
         "Ecart (L)"],
        [[m[0], m[1], m[2], m[3]] for m in manques], [34, 24, 22, 16])

feuille(wb, 5, "Achats non rattaches detail",
        "Detail des lignes de facture retenues (Franche-Comte Boissons Services, "
        "01/04/2022 au 31/03/2025).",
        ["Libelle de facture regroupe", "Produit du bilan", "Bouteilles", "Contenance (cl)",
         "Volume (L)", "Achat retenu au bilan pour le produit (L)"],
        rat_rows, [40, 26, 14, 16, 14, 26])

feuille(wb, 6, "Intermarche annexe 5",
        f"Les {INTER_N} factures Intermarche de l’annexe n 5 de la proposition de "
        f"rectifications (p. 25 et 26 des annexes boissons), pour "
        f"{fr(INTER_HT, 2)} € HT. Sur les {len(inter_ok)} factures dont les trois montants se "
        f"recoupent exactement (HT + TVA = TTC), le taux moyen de TVA ressort a "
        f"{fr(TAUX_MOY, 2)} % (mediane {fr(TAUX_MED, 2)} %, maximum {fr(TAUX[-1], 2)} %), tres "
        f"au-dessus des 5,5 % applicables aux boissons non alcooliques. Source : OCR de la "
        f"proposition, les montants etant recoupes par l’identite HT + TVA = TTC.",
        ["Date", "HT (€)", "TVA (€)", "TTC (€)", "Taux de TVA (%)", "Montants concordants"],
        inter_rows, [14, 14, 14, 14, 16, 40])

os.makedirs(OUTDIR, exist_ok=True)
wb.save(OUT)

print("Ecrit :", OUT)
print(f"  eaux-de-vie : achats {fr(ACH_FAM)} L  conso {fr(CONSO_FAM)} L  "
      f"stock {fr(STOCK_FAM)} L  bilan {fr(BILAN_FAM)} L")
for r in edv_rows:
    print("   ", r)
print(f"  dose d’equilibre famille {fr(DOSE_EQ_FAM,2)} cl ; Calvados seul {fr(DOSE_EQ_CAL,2)} cl")
print("  postes cites p. 50 :")
for r in postes_rows:
    print("   ", r)
print(f"  achats non rattaches : {fr(tot_manque)} L")
for m in manques:
    print("   ", m)
print(f"  Intermarche : {INTER_N} factures, {fr(INTER_HT,2)} € HT ; taux moyen "
      f"{fr(TAUX_MOY,2)} % sur {len(inter_ok)} factures concordantes (max {fr(TAUX[-1],2)} %)")
print(f"  sens des ecarts : {n_pos} positives, {n_nul} nulles, {n_neg} negatives ; "
      f"cl {fr(neg_u['cl'])}/{fr(dispo_u['cl'])} ; unites {fr(neg_u['unité'])}/{fr(dispo_u['unité'])}")
for r in sens_rows:
    print("   ", r)
