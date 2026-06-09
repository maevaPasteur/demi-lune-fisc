#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
07_softs_reels.py
Ferme le bilan des SOFTS au grain le plus fin, au lieu de les exclure comme
"trou de donnees".

Le piege precedent : itemsCaisse vient d'ANNEXE-D (synthese produit) qui NE
contient PAS les softs. Mais chaque Coca/eau/jus vendu est une LIGNE DE TICKET
dans ANNEXE-B (= prix-vente-quantite, niveau ligne). On les recompte.

Bilan par soft : achat = vendu_reel (tickets) + conso_staff + stock + residu(offerts/casse).

Sources : ANNEXE-B1/B2/B3 (ventes ligne a ligne), consoTotaleParBoisson (achats),
inventaire CSV 31/03/2025 (stock), staff_conso (Coca 6/jour).
"""
import json, os, re
import xlrd
from collections import defaultdict

ICI = os.path.dirname(os.path.abspath(__file__))
DOC = os.path.normpath(os.path.join(ICI, "..", "..", "..", "public", "documents"))
CAISSE = os.path.join(DOC, "caisse-enregistreuse")
CALC = os.path.normpath(os.path.join(ICI, "..", "calculsBoissons"))

# --- 1. ventes reelles softs depuis ANNEXE-B (curated, evite faux positifs 'eau ') ---
FILES = {"2022-2023": "ANNEXE-B1_prix-vente-quantite_2022-2023.xls",
         "2023-2024": "ANNEXE-B2_prix-vente-quantite_2023-2024.xls",
         "2024-2025": "ANNEXE-B3_prix-vente-quantite_2024-2025.xls"}

# libelle caisse -> (categorie canonique, cl servis d'un soda direct)
SOFT_MAP = {
    "Coca (25cl)": ("Coca", 33), "Whisky-Coca": ("Coca", 33),  # le coca d'un whisky-coca = 1 canette
    "Limonade (25cl)": ("Limonade", 25), "Diabolo (25cl)": ("Limonade", 22),
    "Orangina (25cl)": ("Orangina", 25), "FANTA": ("Fanta", 33), "Schweppes": ("Schweppes", 33),
    "Jus de Fruit": ("Jus", 20),
    "Sirop a l'eau": ("Sirop", 2), "Sirop à l'eau": ("Sirop", 2),
    "Perrier 33cl": ("Eau", 33), "San Pelegrino": ("Eau", 33), "San Pelegrino 50cl": ("Eau", 50),
    "Vittel 50cl": ("Eau", 50), "Vittel litre": ("Eau", 100),
}
ventes = defaultdict(lambda: defaultdict(float))  # cat -> exo -> unites
ventes_coca_cans = defaultdict(float)
for exo, f in FILES.items():
    sh = xlrd.open_workbook(os.path.join(CAISSE, f)).sheet_by_index(0)
    for r in range(1, sh.nrows):
        lib = str(sh.cell_value(r, 4)).strip()
        if lib in SOFT_MAP:
            try:
                q = float(sh.cell_value(r, 5))
            except ValueError:
                q = 0
            cat, cl = SOFT_MAP[lib]
            ventes[cat][exo] += q * cl / 100.0  # litres vendus (direct)
            if cat == "Coca":
                ventes_coca_cans[exo] += q

# --- 2. achats softs (consoTotaleParBoisson) ---
d = json.load(open(os.path.join(CALC, "consoTotaleParBoisson.json"), encoding="utf-8"))
ACH_CAT = {"Coca": ["Coca"], "Limonade": ["Limonade"],
           "Jus": ["Jus d'orange", "Jus de pomme", "Jus d'ananas", "Jus de fraise", "Jus de framboise", "Jus de poire"],
           "Sirop": ["Sirop Châtaigne", "Sirop Framboise", "Sirop Grenadine", "Sirop Curaçao bleu", "Sirop Pamplemousse"]}
achats = defaultdict(float)
conso_cocktails = defaultdict(float)  # softs deja consommes en cocktail (dans le pipeline)
for b in d["boissons"]:
    for cat, noms in ACH_CAT.items():
        if b["nom_canonique"] in noms:
            achats[cat] += sum(x for x in (b.get("achats_litres_par_periode") or {}).values() if x)
            for ex, v in b["par_periode"].items():
                conso_cocktails[cat] += v.get("detail_exact_l", {}).get("ingredients_cocktails", 0.0)

# --- 3. stock final softs (inventaire CSV 2025-03-31), en litres ---
STOCK_CL = {"Coca-Cola 33cl": ("Coca", 33), "Schweppes Agrum 33cl": ("Schweppes", 33),
            "Fanta 33cl": ("Fanta", 33), "Orangina 33cl": ("Orangina", 33),
            "Limonade": ("Limonade", 100)}
stock = defaultdict(float)
stock_coca_cans = 0
inv = open(os.path.join(DOC, "inventaires", "inventaire_2025-03-31.csv"), encoding="utf-8").read().splitlines()
for line in inv:
    p = line.split(";")
    if len(p) < 3:
        continue
    nom = p[0].strip()
    try:
        qt = float(p[2])
    except (ValueError, IndexError):
        continue
    if nom in STOCK_CL:
        cat, cl = STOCK_CL[nom]
        stock[cat] += qt * cl / 100.0
        if cat == "Coca":
            stock_coca_cans += qt
    elif nom.startswith("Jus"):
        stock["Jus"] += qt * 1.0  # bouteilles 1L
    elif nom.startswith("Sirop"):
        stock["Sirop"] += qt * 1.0

# --- 4. staff (06_conso_staff) : Coca 6/jour + estimations cliente softs ---
JOURS = 662
coca_staff_cans = 6 * JOURS
coca_staff_l = coca_staff_cans * 0.33
# estimations cliente (2026-06-09) : 1 limonade/j, 3 sirops/j, 3 jus/j (tout le staff)
STAFF_SOFT_L = {
    "Limonade": 1 * JOURS * 0.25,   # 1 limonade 25cl/jour
    "Sirop": 3 * JOURS * 0.02,      # 3 sirops a l'eau/jour (~2cl sirop)
    "Jus": 3 * JOURS * 0.20,        # 3 jus 20cl/jour
}

# --- 5. bilan ---
# CAS PHARE : Coca en CANETTES (1 vente ~ 1 canette de 33cl)
coca_vendu_cans = sum(ventes_coca_cans.values())
coca_achat_cans = round(achats["Coca"] / 0.33)
coca_compte = coca_vendu_cans + coca_staff_cans + stock_coca_cans
coca_residu = coca_achat_cans - coca_compte
coca = {
    "achat_canettes": coca_achat_cans,
    "vendu_tickets_canettes": round(coca_vendu_cans),
    "staff_canettes": coca_staff_cans, "staff_detail": "6/jour (Chris 4 + Ghislaine 2) x 662 j",
    "stock_final_canettes": round(stock_coca_cans),
    "compte_nomme": round(coca_compte),
    "residu_offerts_casse_canettes": round(coca_residu),
    "pct_ferme": round(100 * coca_compte / coca_achat_cans, 1),
}

# BILAN AGREGE (litres) toutes categories softs avec achat connu
bilan = {}
for cat in ["Coca", "Limonade", "Jus", "Sirop"]:
    vendu = sum(ventes[cat].values())
    a = achats[cat]
    cock = conso_cocktails[cat]
    st = stock[cat]
    staff = coca_staff_l if cat == "Coca" else STAFF_SOFT_L.get(cat, 0.0)
    compte = vendu + cock + st + staff
    bilan[cat] = {"achat_l": round(a, 0), "vendu_direct_l": round(vendu, 0),
                  "conso_cocktails_l": round(cock, 0), "stock_l": round(st, 0),
                  "staff_l": round(staff, 0), "compte_nomme_l": round(compte, 0),
                  "residu_l": round(a - compte, 0),
                  "pct_ferme": round(100 * compte / a, 0) if a else None}

out = {
    "description": "Bilan des softs ferme au niveau ticket (ANNEXE-B), au lieu de l'exclure. "
                   "achat = vendu_tickets + conso_cocktails + staff + stock + residu(offerts/casse).",
    "constat": "Les ventes de softs existent ligne par ligne dans ANNEXE-B ; elles manquaient juste "
               "dans la synthese ANNEXE-D utilisee au depart. Le 'disparu softs' n'etait pas une "
               "disparition mais une source non lue.",
    "coca_canettes": coca,
    "bilan_agrege_litres": bilan,
    "note_eaux": "Eaux (Perrier/San Pellegrino/Vittel) vendues et en stock mais SANS achat dans la base "
                 "fournisseur boissons (achetees ailleurs) : non bilantables ici, mais bien vendues."
}
json.dump(out, open(os.path.join(ICI, "softs_balance.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("=" * 60)
print("BILAN COCA (canettes 33cl) — le cas phare")
print("=" * 60)
print(f"  Achat            : {coca['achat_canettes']:6d}")
print(f"  Vendu (tickets)  : {coca['vendu_tickets_canettes']:6d}")
print(f"  Staff (6/j)      : {coca['staff_canettes']:6d}")
print(f"  Stock final      : {coca['stock_final_canettes']:6d}")
print(f"  = compte nomme   : {coca['compte_nomme']:6d}  ({coca['pct_ferme']}% de l'achat)")
print(f"  residu (offerts/casse) : {coca['residu_offerts_casse_canettes']}")
print()
print("BILAN AGREGE (litres)")
print(f"{'cat':10} {'achat':>7} {'vendu':>7} {'cockt':>7} {'staff':>7} {'stock':>7} {'residu':>7} {'%ferme':>7}")
for cat, v in bilan.items():
    print(f"{cat:10} {v['achat_l']:>7.0f} {v['vendu_direct_l']:>7.0f} {v['conso_cocktails_l']:>7.0f} "
          f"{v['staff_l']:>7.0f} {v['stock_l']:>7.0f} {v['residu_l']:>7.0f} {str(v['pct_ferme']):>7}")
print("\nsofts_balance.json ecrit.")
