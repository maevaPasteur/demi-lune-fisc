#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
03_sensibilite.py
Analyse de sensibilite (tornado). Quel parametre pilote le disparu ?

Methode : on fixe tous les parametres a leur mode, puis on fait varier UN seul
parametre de son min a son max (les autres au mode) et on mesure le balancement
du disparu total (en euros revente). Le parametre au plus grand balancement est
celui qui controle le resultat : c'est LUI qu'il faut documenter en priorite,
pas tout le reste.
"""
import json, os

ICI = os.path.dirname(os.path.abspath(__file__))
base = json.load(open(os.path.join(ICI, "base_disparu.json"), encoding="utf-8"))
P = json.load(open(os.path.join(ICI, "parametres.json"), encoding="utf-8"))
prm = P["parametres"]
CATV = set(P["categorisation"]["surversement_vin"])
CATS = set(P["categorisation"]["surversement_spiritueux"])

fiables = [x for x in base["boissons"] if x.get("conso_complete") is True]

def norm(s): return (s or "").lower().replace("û", "u").replace("ô", "o")
def est_fut(x): return x["categorie"] == "biere" and "fut" in norm(x.get("unite_achat"))

def disparu_total_eur(sv, ss, pb, dc, dk, po, menu_key):
    """menu_key in {bas, moyen, haut}"""
    tot = 0.0
    for x in fiables:
        c = x["conso"]; cat = x["categorie"]
        pour = sv if cat in CATV else (ss if cat in CATS else 1.0)
        conso = (c["seches_l"] * pour + c["cocktails_l"] * dc + c["plats_l"] * dk
                 + c[f"menu_{menu_key}_l"] + x["achats_l"] * po)
        if est_fut(x):
            conso += x["achats_l"] * pb
        disp = x["achats_l"] - x["stock_final_l"] - conso
        tot += disp * (x.get("prix_revente_l") or 0)
    return tot

# point de base : tous au mode, menu au moyen
M = {k: prm[k]["mode"] for k in ["surversement_vin", "surversement_spiritueux",
     "perte_biere_fut", "dose_cocktail", "dose_cuisine", "personnel_offerts_alcool"]}
base_eur = disparu_total_eur(M["surversement_vin"], M["surversement_spiritueux"],
                             M["perte_biere_fut"], M["dose_cocktail"], M["dose_cuisine"],
                             M["personnel_offerts_alcool"], "moyen")

ordre = ["surversement_vin", "surversement_spiritueux", "perte_biere_fut",
         "dose_cocktail", "dose_cuisine", "personnel_offerts_alcool"]
labels = {"surversement_vin": "Sur-versement vin/cidre",
          "surversement_spiritueux": "Sur-versement spiritueux",
          "perte_biere_fut": "Perte biere pression",
          "dose_cocktail": "Dose cocktails",
          "dose_cuisine": "Dose cuisine",
          "personnel_offerts_alcool": "Conso personnel/offerts"}

tornado = []
for k in ordre:
    lo = dict(M); lo[k] = prm[k]["min"]
    hi = dict(M); hi[k] = prm[k]["max"]
    e_lo = disparu_total_eur(lo["surversement_vin"], lo["surversement_spiritueux"], lo["perte_biere_fut"],
                             lo["dose_cocktail"], lo["dose_cuisine"], lo["personnel_offerts_alcool"], "moyen")
    e_hi = disparu_total_eur(hi["surversement_vin"], hi["surversement_spiritueux"], hi["perte_biere_fut"],
                             hi["dose_cocktail"], hi["dose_cuisine"], hi["personnel_offerts_alcool"], "moyen")
    tornado.append({"parametre": k, "label": labels[k],
                    "disparu_a_min_param_eur": round(e_lo, 0),
                    "disparu_a_max_param_eur": round(e_hi, 0),
                    "balancement_eur": round(abs(e_hi - e_lo), 0)})
# menu (bas vs haut)
e_mb = disparu_total_eur(M["surversement_vin"], M["surversement_spiritueux"], M["perte_biere_fut"],
                         M["dose_cocktail"], M["dose_cuisine"], M["personnel_offerts_alcool"], "bas")
e_mh = disparu_total_eur(M["surversement_vin"], M["surversement_spiritueux"], M["perte_biere_fut"],
                         M["dose_cocktail"], M["dose_cuisine"], M["personnel_offerts_alcool"], "haut")
tornado.append({"parametre": "menu", "label": "Alcool des menus (bas->haut)",
                "disparu_a_min_param_eur": round(e_mh, 0), "disparu_a_max_param_eur": round(e_mb, 0),
                "balancement_eur": round(abs(e_mb - e_mh), 0)})

tornado.sort(key=lambda d: -d["balancement_eur"])
out = {"description": "Tornado : balancement du disparu (€ revente) quand chaque parametre va de min a max, autres au mode.",
       "disparu_au_point_de_base_eur": round(base_eur, 0),
       "tornado": tornado}
json.dump(out, open(os.path.join(ICI, "sensibilite.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("ANALYSE DE SENSIBILITE (tornado) - disparu € revente")
print(f"point de base (tous au mode) : {base_eur:,.0f} €\n")
print(f"{'parametre':30} {'balancement €':>14}")
for t in tornado:
    print(f"{t['label']:30} {t['balancement_eur']:>14,.0f}")
print("\nsensibilite.json ecrit.")
