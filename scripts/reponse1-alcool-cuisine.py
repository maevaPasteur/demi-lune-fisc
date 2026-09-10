#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
R1 - Alcool de cuisine : controles de la reponse DDFiP du 04/09/2026 (p. 65-70 et p. 87-88).

Produit public/documents/pieces-reponse-1/R1-alcool-cuisine-controles.xlsx :
  1. Controle arithmetique des 4 tableaux du service (Calvados D / Vin jaune E / Porto G / Macvin Q)
  2. Alcool de cuisine par plat et par sauce, a la carte, quantites lues en caisse (ANNEXE-D)
  3. Alcool de cuisine par alcool et par exercice (carte + menus)
  4. Confrontation aux achats factures (FCBS) et au "volume disponible" du service
  5. Solde reellement demande, apres plafonnement aux achats et deduction de ce que le service retranche deja

Sources (lecture seule) :
  src/data/calculsBoissons/itemsCaisse.json            (ANNEXE-D, quantites vendues par exercice)
  src/data/calculsBoissons/platsAlcool.json            (doses par plat)
  src/data/calculsBoissons/saucesAlcool.json           (doses par sauce)
  src/data/calculsBoissons/menusCompositionAlcool.json (doses x probabilite dans les menus)
  src/data/calculsBoissons/consoAlcoolMenus.json       (alcool des menus par exercice)
  src/data/calculsBoissons/consoTotaleParBoisson.json  (cumul, dont achats par exercice)
  public/documents/vins-boissons/_pipeline_conso_alcool.py (mapping libelle caisse -> plat/dose)
"""
import ast, json, os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/"
JS = BASE + "src/data/calculsBoissons/"
OUT = BASE + "public/documents/pieces-reponse-1/"
EXOS = ["2022-2023", "2023-2024", "2024-2025"]
LAB = {"2022-2023": "Exercice 1", "2023-2024": "Exercice 2", "2024-2025": "Exercice 3"}


def J(n):
    return json.load(open(JS + n, encoding="utf-8"))


# --------------------------------------------------------------------------
# mapping libelle caisse -> (alcool, dose cl) : lu dans le pipeline existant
# --------------------------------------------------------------------------
src = open(BASE + "public/documents/vins-boissons/_pipeline_conso_alcool.py", encoding="utf-8").read()
tree = ast.parse(src)
FOOD = None
for node in tree.body:
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "FOOD":
        FOOD = ast.literal_eval(node.value)
assert FOOD, "FOOD introuvable"

SAUCES = {s["nom"] for s in J("saucesAlcool.json")["sauces"]}
SAUCE_ITEMS = {"SAUCE JURASSIENNE", "Sauce Forestière", "Sauce Morilles"}
DESSERT_ITEMS = {"Baba", "Baba au Macvin", "IVRESSE", "FOLIE", "GRAPPINS", "VOGEOTTE",
                 "BASILIC", "Crêpe Flambée", "Flambée"}
ENTREE_ITEMS = {"Croûtes Morilles", "Feuilleté Forestier", "PAYSANNE", "MACHON GOURMET"}

items = {}
for it in J("itemsCaisse.json")["items"]:
    items.setdefault(it["produit"], {e: 0.0 for e in EXOS})
    for e in EXOS:
        items[it["produit"]][e] += it["quantite"].get(e, 0.0)

# --------------------------------------------------------------------------
# 2. alcool de cuisine par plat / par sauce, a la carte
# --------------------------------------------------------------------------
plats_rows = []
carte = {}  # alcool -> {exo: cl}
for libelle, doses in FOOD.items():
    q = items.get(libelle)
    if not q:
        continue
    for (alc, dose, _est) in doses:
        parts = [(alc, 1.0)]
        if alc == "Grand Marnier ou Calvados":  # flambage : repartition 50/50, convention du dossier
            parts = [("Grand Marnier", 0.5), ("Calvados", 0.5)]
        for (a, coef) in parts:
            vol = {e: q[e] * dose * coef for e in EXOS}
            typ = ("Sauce" if libelle in SAUCE_ITEMS else
                   "Dessert" if libelle in DESSERT_ITEMS else
                   "Entrée" if libelle in ENTREE_ITEMS else "Plat")
            plats_rows.append({"libelle": libelle, "type": typ, "alcool": a, "dose": dose * coef,
                               "qte": q, "vol": vol})
            d = carte.setdefault(a, {e: 0.0 for e in EXOS})
            for e in EXOS:
                d[e] += vol[e]
plats_rows.sort(key=lambda r: (-sum(r["vol"].values()), r["libelle"]))

# menus (deja calcules : dose x probabilite x menus vendus)
menus = {}
cam = J("consoAlcoolMenus.json")
ALIAS = {"Crème de cassis": "Crème de Cassis", "Marc de bourgogne": "Marc de Bourgogne",
         "Baileys": "Bailey's", "Vin jaune": "Arbois Vin Jaune", "Liqueur de poire": "Liqueur de Poire"}
CANON = {"Vin jaune": "Arbois Vin Jaune", "Crème de cassis": "Crème de Cassis",
         "Baileys": "Bailey's", "Marc de bourgogne": "Marc de Bourgogne"}
for e in EXOS:
    for a in cam["exercices"][e]["alcools"]:
        nom = ALIAS.get(a["alcool"], a["alcool"])
        menus.setdefault(nom, {x: 0.0 for x in EXOS})[e] += a["cl_moyen"]
carte = {ALIAS.get(k, k): v for k, v in carte.items()}

# achats factures (FCBS) par exercice, en cl
achats = {}
dispo_service = {}
for b in J("consoTotaleParBoisson.json")["boissons"]:
    al = b.get("achats_litres_par_periode") or {}
    if al:
        achats[b["nom_canonique"]] = {e: al.get(e, 0.0) * 100 for e in EXOS}

# "volume disponible" imprime par le service (cl), p. 65 a 67
dispo_service = {
    "Calvados": {"2022-2023": 3100, "2023-2024": 2200, "2024-2025": 2000},
    "Arbois Vin Jaune": {"2022-2023": 7409, "2023-2024": 6758, "2024-2025": 7874},
    "Porto": {"2022-2023": 2730, "2023-2024": 4760, "2024-2025": 4480},
    "Macvin": {"2022-2023": 24000, "2023-2024": 28350, "2024-2025": 27150},
}

# --------------------------------------------------------------------------
# 1. controle arithmetique des tableaux du service
# --------------------------------------------------------------------------
# imprime = colonne "volume consomme" (part plats) ; plats = colonne "donnees de la caisse"
TABLEAUX = [
    {"alcool": "Calvados", "page": "p. 65", "repere": "D", "dose_annoncee": "4 cl par plat",
     "lignes": [{"exo": "2022-2023", "plats": [(997, 4)], "imprime": 3310, "verre": 0},
                {"exo": "2023-2024", "plats": [(880, 4)], "imprime": 3002, "verre": 0},
                {"exo": "2024-2025", "plats": [(873, 4)], "imprime": 3005, "verre": 0}],
     "repere_courrier": 93},
    {"alcool": "Arbois Vin Jaune", "page": "p. 66", "repere": "E", "dose_annoncee": "1 cl / 10 cl",
     "lignes": [{"exo": "2022-2023", "plats": [(1507, 1), (221, 10)], "imprime": 3717, "verre": 1044},
                {"exo": "2023-2024", "plats": [(1449, 1), (247, 10)], "imprime": 3693, "verre": 1224},
                {"exo": "2024-2025", "plats": [(1748, 1), (189, 10)], "imprime": 3748, "verre": 1476}],
     "repere_courrier": 111},
    {"alcool": "Porto", "page": "p. 67", "repere": "G", "dose_annoncee": "1 cl par plat",
     "lignes": [{"exo": "2022-2023", "plats": [(478, 1)], "imprime": 398, "verre": 213},
                {"exo": "2023-2024", "plats": [(745, 1)], "imprime": 583, "verre": 282},
                {"exo": "2024-2025", "plats": [(783, 1)], "imprime": 556, "verre": 282}],
     "repere_courrier": 15},
    {"alcool": "Macvin", "page": "p. 67", "repere": "Q", "dose_annoncee": "4 cl par plat",
     "lignes": [{"exo": "2022-2023", "plats": [(2400, 4)], "imprime": 7774, "verre": 8610},
                {"exo": "2023-2024", "plats": [(2510, 4)], "imprime": 8832, "verre": 10120},
                {"exo": "2024-2025", "plats": [(2714, 4)], "imprime": 7406, "verre": 9398}],
     "repere_courrier": 240},
]

controle = []
for t in TABLEAUX:
    som_imp = som_rec = 0
    for l in t["lignes"]:
        rec = sum(n * d for n, d in l["plats"])
        nb = sum(n for n, _ in l["plats"])
        ecart = l["imprime"] - rec
        controle.append({
            "alcool": t["alcool"], "repere": t["repere"], "page": t["page"], "exo": l["exo"],
            "dose": t["dose_annoncee"], "detail": " + ".join(f"{n} x {d} cl" for n, d in l["plats"]),
            "recalcule": rec, "imprime": l["imprime"], "ecart": ecart,
            "ecart_pct": (ecart / rec * 100) if rec else 0,
            "dose_implicite": (l["imprime"] / nb) if nb else 0,
            "verre": l["verre"], "verre_div6": (l["verre"] / 6) if l["verre"] else 0,
            "dispo": dispo_service[t["alcool"]][l["exo"]],
        })
        som_imp += l["imprime"]
        som_rec += rec
    controle.append({"alcool": t["alcool"], "repere": t["repere"], "page": "p. 69", "exo": "TOTAL 3 ans",
                     "dose": t["dose_annoncee"], "detail": f"repère {t['repere']} annoncé p. 69 : {t['repere_courrier']} L",
                     "recalcule": som_rec, "imprime": som_imp, "ecart": som_imp - som_rec,
                     "ecart_pct": (som_imp - som_rec) / som_rec * 100, "dose_implicite": 0,
                     "verre": sum(l["verre"] for l in t["lignes"]), "verre_div6": 0,
                     "dispo": sum(dispo_service[t["alcool"]][l["exo"]] for l in t["lignes"])})

# --------------------------------------------------------------------------
# 5. solde par alcool
# --------------------------------------------------------------------------
# volumes que le service dit avoir deja retranches, par exercice (cl)
#  - D/E/G/Q : colonne "volume consomme" de ses propres tableaux, p. 65 a 67
#  - creme de cassis : part "desserts" du volume unique des cremes, p. 69
#  - ravelin : part "cuisine" retranchee du volume unique des vins en BIB, p. 69 ;
#    nulle sur l'exercice 1, ou aucun BIB de ravelin n'a ete achete (achats en bouteilles)
DEJA = {
    "Calvados": {"2022-2023": 3310, "2023-2024": 3002, "2024-2025": 3005},
    "Arbois Vin Jaune": {"2022-2023": 3717, "2023-2024": 3693, "2024-2025": 3748},
    "Porto": {"2022-2023": 398, "2023-2024": 583, "2024-2025": 556},
    "Macvin": {"2022-2023": 7774, "2023-2024": 8832, "2024-2025": 7406},
    "Crème de Cassis": {"2022-2023": 1064, "2023-2024": 1132, "2024-2025": 1132},
    "Ravelin": {"2022-2023": 0, "2023-2024": 16257, "2024-2025": 15554},
}
NOTE_DEJA = {
    "Calvados": "repère D (3 310 + 3 002 + 3 005 cl), p. 65 et 69 : le service retranche déjà plus que le volume qu’il dit disponible",
    "Arbois Vin Jaune": "repère E (3 717 + 3 693 + 3 748 cl), p. 66 et 69",
    "Porto": "repère G (398 + 583 + 556 cl), p. 67 et 69",
    "Macvin": "repère Q (7 774 + 8 832 + 7 406 cl), p. 67 et 69 : déjà supérieur à notre demande",
    "Crème de Cassis": "part desserts du volume unique des crèmes (10,64 + 11,32 + 11,32 L), p. 69 : déjà supérieure à notre demande",
    "Ravelin": "part cuisine du volume unique des BIB (162,32 / 162,57 / 155,54 L), p. 69 ; nulle sur l’exercice 1, où le ravelin est acheté en bouteilles et non en BIB",
    "Bailey's": "aucun retranchement identifié dans la réponse du service",
    "Grand Marnier": "aucun retranchement identifié ; demande plafonnée aux achats facturés",
    "Marc de Bourgogne": "aucun retranchement identifié ; achats facturés 9,8 L contre 70 cl retenus par le service",
    "Liqueur de Poire": "aucun retranchement identifié ; achats facturés 16,8 L contre 140 cl retenus par le service",
}

alcools = sorted(set(list(carte) + list(menus)), key=lambda a: -(sum(carte.get(a, {}).values()) + sum(menus.get(a, {}).values())))
solde = []
for a in alcools:
    c = carte.get(a, {e: 0.0 for e in EXOS})
    m = menus.get(a, {e: 0.0 for e in EXOS})
    ac = achats.get(a, {e: 0.0 for e in EXOS})
    dem = {e: c[e] + m[e] for e in EXOS}
    plaf = {e: min(dem[e], ac[e]) for e in EXOS}
    dj = DEJA.get(a, {e: 0.0 for e in EXOS})
    deja = sum(dj.values())
    reste = sum(max(0.0, plaf[e] - dj[e]) for e in EXOS)
    solde.append({"alcool": a, "carte": c, "menus": m, "demande": dem, "achats": ac,
                  "plafonne": plaf, "deja": deja, "reste": reste, "note": NOTE_DEJA.get(a, "")})

# --------------------------------------------------------------------------
# ecriture xlsx
# --------------------------------------------------------------------------
HEAD = PatternFill("solid", fgColor="1F4E78")
HF = Font(bold=True, color="FFFFFF", size=10)
BAD = PatternFill("solid", fgColor="FCE4E4")
OK = PatternFill("solid", fgColor="E4F3E8")
thin = Side("thin", color="BFBFBF")
B = Border(thin, thin, thin, thin)


def sheet(wb, title, titre, cols, widths, first=False):
    ws = wb.active if first else wb.create_sheet()
    ws.title = title
    ws.cell(1, 1, titre).font = Font(bold=True, size=12)
    for j, h in enumerate(cols, 1):
        c = ws.cell(3, j, h)
        c.fill = HEAD
        c.font = HF
        c.border = B
        c.alignment = Alignment("center", "center", wrap_text=True)
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[ws.cell(1, i).column_letter].width = w
    ws.freeze_panes = "A4"
    return ws


def put(ws, r, vals, fmts=None, fill=None):
    for j, v in enumerate(vals, 1):
        c = ws.cell(r, j, v)
        c.border = B
        if fmts and fmts[j - 1]:
            c.number_format = fmts[j - 1]
        if fill and fill(j):
            c.fill = fill(j)


wb = Workbook()

# --- feuille 1
ws = sheet(wb, "1-Contrôle tableaux", "1. Contrôle arithmétique des tableaux du service (réponse du 04/09/2026, p. 65 à 67)",
           ["Alcool", "Repère", "Page", "Exercice", "Dose annoncée par le service",
            "Nombre de plats x dose (colonnes du service)", "Volume recalculé (cl)",
            "Volume imprimé par le service (cl)", "Écart (cl)", "Écart (%)",
            "Dose implicite du tableau (cl)", "Colonne « vente au verre de 6 cl » (cl)",
            "Nombre de verres à 6 cl", "Volume disponible imprimé (cl)"],
           [18, 8, 8, 12, 18, 26, 13, 15, 11, 10, 14, 15, 12, 14], first=True)
r = 4
for x in controle:
    tot = x["exo"].startswith("TOTAL")
    put(ws, r, [x["alcool"], x["repere"], x["page"], LAB.get(x["exo"], x["exo"]), x["dose"], x["detail"],
                x["recalcule"], x["imprime"], x["ecart"], round(x["ecart_pct"], 1),
                round(x["dose_implicite"], 2) if x["dose_implicite"] else "",
                x["verre"] or "", round(x["verre_div6"], 2) if x["verre_div6"] else "", x["dispo"]],
        [None] * 6 + ["#,##0", "#,##0", "#,##0", "0.0", "0.00", "#,##0", "0.00", "#,##0"],
        fill=(lambda j: BAD if j in (9, 10) else None) if x["ecart"] else (lambda j: OK if j in (9, 10) else None))
    if tot:
        for j in range(1, 15):
            ws.cell(r, j).font = Font(bold=True)
    r += 1
ws.cell(r + 1, 1, "Lecture : la colonne « volume consommé » du service, cumulée sur trois exercices, donne exactement les repères D (93 L), E (111 L), G (15 L) et Q (240 L) annoncés p. 69.")
ws.cell(r + 2, 1, "Un écart négatif signifie que le service a retranché de sa reconstitution moins d’alcool de cuisine que ses propres colonnes ne le commandent.")

# --- feuille 2
ws = sheet(wb, "2-Cuisine par plat", "2. Alcool de cuisine à la carte : dose par plat ou par sauce x quantités vendues (caisse, ANNEXE-D)",
           ["Libellé caisse", "Type", "Alcool", "Dose (cl)"] +
           [f"Qté {LAB[e]}" for e in EXOS] + [f"Volume {LAB[e]} (cl)" for e in EXOS] + ["Total 3 ans (L)"],
           [26, 10, 18, 9, 12, 12, 12, 14, 14, 14, 14])
r = 4
for x in plats_rows:
    put(ws, r, [x["libelle"], x["type"], x["alcool"], x["dose"]] +
        [round(x["qte"][e], 1) for e in EXOS] + [round(x["vol"][e], 1) for e in EXOS] +
        [round(sum(x["vol"].values()) / 100, 2)],
        [None] * 3 + ["0.0"] + ["#,##0.0"] * 6 + ["#,##0.00"])
    r += 1
put(ws, r, ["TOTAL", "", "", ""] + ["", "", ""] +
    [round(sum(x["vol"][e] for x in plats_rows), 1) for e in EXOS] +
    [round(sum(sum(x["vol"].values()) for x in plats_rows) / 100, 2)],
    [None] * 7 + ["#,##0.0"] * 3 + ["#,##0.00"])
for j in range(1, 12):
    ws.cell(r, j).font = Font(bold=True)

# --- feuille 3
ws = sheet(wb, "3-Cuisine par alcool", "3. Alcool de cuisine par alcool et par exercice : carte + plats des menus (litres)",
           ["Alcool"] + [f"Carte {LAB[e]}" for e in EXOS] + ["Carte 3 ans"] +
           [f"Menus {LAB[e]}" for e in EXOS] + ["Menus 3 ans", "Total 3 ans"],
           [20, 12, 12, 12, 12, 12, 12, 12, 12, 12])
r = 4
for s in solde:
    put(ws, r, [s["alcool"]] + [round(s["carte"][e] / 100, 2) for e in EXOS] +
        [round(sum(s["carte"].values()) / 100, 2)] +
        [round(s["menus"][e] / 100, 2) for e in EXOS] + [round(sum(s["menus"].values()) / 100, 2)] +
        [round((sum(s["carte"].values()) + sum(s["menus"].values())) / 100, 2)],
        [None] + ["#,##0.00"] * 9)
    r += 1
put(ws, r, ["TOTAL"] + [round(sum(s["carte"][e] for s in solde) / 100, 2) for e in EXOS] +
    [round(sum(sum(s["carte"].values()) for s in solde) / 100, 2)] +
    [round(sum(s["menus"][e] for s in solde) / 100, 2) for e in EXOS] +
    [round(sum(sum(s["menus"].values()) for s in solde) / 100, 2)] +
    [round(sum(sum(s["carte"].values()) + sum(s["menus"].values()) for s in solde) / 100, 2)],
    [None] + ["#,##0.00"] * 9)
for j in range(1, 11):
    ws.cell(r, j).font = Font(bold=True)

# --- feuille 4
ws = sheet(wb, "4-Achats vs cuisine", "4. Confrontation aux achats facturés (fournisseur Franche-Comté Boissons Services) et au « volume disponible » du service",
           ["Alcool"] + [f"Achats {LAB[e]} (L)" for e in EXOS] + ["Achats 3 ans (L)"] +
           [f"Cuisine demandée {LAB[e]} (L)" for e in EXOS] + ["Cuisine demandée 3 ans (L)"] +
           ["Volume disponible du service, 3 ans (L)", "Achats - volume disponible (L)", "Demande > achats ?"],
           [20, 13, 13, 13, 13, 15, 15, 15, 15, 17, 15, 15])
r = 4
for s in solde:
    ds = dispo_service.get(s["alcool"])
    dsv = sum(ds.values()) / 100 if ds else ""
    dep = any(s["demande"][e] > s["achats"][e] + 0.01 for e in EXOS)
    put(ws, r, [s["alcool"]] + [round(s["achats"][e] / 100, 2) for e in EXOS] +
        [round(sum(s["achats"].values()) / 100, 2)] +
        [round(s["demande"][e] / 100, 2) for e in EXOS] +
        [round(sum(s["demande"].values()) / 100, 2), dsv,
         round(sum(s["achats"].values()) / 100 - dsv, 2) if dsv != "" else "",
         "oui" if dep else "non"],
        [None] + ["#,##0.00"] * 10 + [None],
        fill=(lambda j: BAD if j == 12 else None) if dep else (lambda j: OK if j == 12 else None))
    r += 1

# --- feuille 5
ws = sheet(wb, "5-Solde demandé", "5. Volume réellement demandé après plafonnement aux achats facturés et déduction de ce que le service retranche déjà (litres, 3 exercices)",
           ["Alcool", "Demande initiale (mémoire du 10/07/2026)", "Plafonnée aux achats facturés",
            "Déjà retranché par le service", "Solde demandé", "Observation"],
           [20, 18, 18, 18, 14, 62])
r = 4
for s in solde:
    put(ws, r, [s["alcool"], round(sum(s["demande"].values()) / 100, 2),
                round(sum(s["plafonne"].values()) / 100, 2), round(s["deja"] / 100, 2),
                round(s["reste"] / 100, 2), s["note"]],
        [None] + ["#,##0.00"] * 4 + [None])
    ws.cell(r, 6).alignment = Alignment(wrap_text=True, vertical="top")
    r += 1
put(ws, r, ["TOTAL", round(sum(sum(s["demande"].values()) for s in solde) / 100, 2),
            round(sum(sum(s["plafonne"].values()) for s in solde) / 100, 2),
            round(sum(s["deja"] for s in solde) / 100, 2),
            round(sum(s["reste"] for s in solde) / 100, 2), ""],
    [None] + ["#,##0.00"] * 4 + [None])
for j in range(1, 7):
    ws.cell(r, j).font = Font(bold=True)

os.makedirs(OUT, exist_ok=True)
wb.save(OUT + "R1-alcool-cuisine-controles.xlsx")
print("-> public/documents/pieces-reponse-1/R1-alcool-cuisine-controles.xlsx")

# --------------------------------------------------------------------------
# recapitulatif console
# --------------------------------------------------------------------------
print("\n== 1. controle arithmetique ==")
for x in controle:
    print(f"{x['alcool']:18} {LAB.get(x['exo'],x['exo']):12} recalcule {x['recalcule']:7.0f}  imprime {x['imprime']:7.0f}"
          f"  ecart {x['ecart']:7.0f} ({x['ecart_pct']:5.1f}%)  dose implicite {x['dose_implicite']:.2f}")
tot_ec = sum(x["ecart"] for x in controle if x["exo"].startswith("TOTAL"))
print(f"   ecart cumule sur les 4 tableaux : {tot_ec:.0f} cl = {tot_ec/100:.1f} L")

print("\n== 3/5. par alcool (L, 3 ans) ==")
for s in solde:
    print(f"{s['alcool']:20} carte {sum(s['carte'].values())/100:7.1f}  menus {sum(s['menus'].values())/100:6.1f}"
          f"  achats {sum(s['achats'].values())/100:7.1f}  plafonne {sum(s['plafonne'].values())/100:7.1f}"
          f"  deja {s['deja']/100:6.1f}  solde {s['reste']/100:6.1f}")
print(f"{'TOTAL':20} carte {sum(sum(s['carte'].values()) for s in solde)/100:7.1f}"
      f"  menus {sum(sum(s['menus'].values()) for s in solde)/100:6.1f}"
      f"  plafonne {sum(sum(s['plafonne'].values()) for s in solde)/100:7.1f}"
      f"  solde {sum(s['reste'] for s in solde)/100:6.1f}")
