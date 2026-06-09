#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
04_signature.py
Test de la signature du disparu : ressemble-t-il a un VOL (vente au noir) ou a
une ERREUR DE MESURE / perte d'exploitation ?

Logique : une vente au noir se concentre sur ce qui est CHER, REVENDABLE et
COMPTABLE A L'UNITE (spiritueux en bouteille, grands crus). Une erreur de
mesure / perte se concentre sur le VRAC servi au verre (vin maison en BIB,
pression). On classe le disparu (nominal pipeline) par sous-groupe et on
regarde ou il se loge.
"""
import json, os

ICI = os.path.dirname(os.path.abspath(__file__))
base = json.load(open(os.path.join(ICI, "base_disparu.json"), encoding="utf-8"))

def norm(s): return (s or "").lower().replace("û", "u").replace("ô", "o")

def disparu_nominal(x):
    c = x["conso"]
    conso = c["seches_l"] + c["cocktails_l"] + c["plats_l"] + c["menu_moyen_l"]
    return x["achats_l"] - x["stock_final_l"] - conso

def groupe(x):
    cat = x["categorie"]; u = norm(x.get("unite_achat")); nom = norm(x["nom"])
    if x.get("conso_complete") is False:
        return "0. SOFTS/EAUX (trou de donnees, hors disparu)"
    if "bib" in u or "cubis" in u or "maison" in nom or "bib" in nom:
        return "A. Vin maison VRAC (BIB) au verre"   # vrac, non revendable, sur-versement
    if cat in ("vin_blanc", "vin_rouge", "vin_rose", "vin", "petillant"):
        return "B. Vin/cremant bouteille"
    if cat == "biere" and "fut" in u:
        return "C. Biere PRESSION (fut)"
    if cat == "biere":
        return "D. Biere bouteille"
    if cat == "cidre":
        return "E. Cidre"
    if cat in ("spiritueux", "aperitif", "liqueur", "digestif", "vin_de_liqueur", "eau_de_vie"):
        return "F. Spiritueux/aperitifs (cher, revendable, a l'unite)"
    return "G. Autre"

agg = {}
for x in base["boissons"]:
    g = groupe(x)
    d = disparu_nominal(x)
    a = agg.setdefault(g, {"disparu_l": 0.0, "disparu_eur": 0.0, "achats_l": 0.0, "n": 0, "produits": []})
    a["disparu_l"] += d
    a["disparu_eur"] += d * (x.get("prix_revente_l") or 0)
    a["achats_l"] += x["achats_l"]
    a["n"] += 1
    if d > 0:
        a["produits"].append((x["nom"], round(d, 0)))

# disparu reel (alcool fiable) = tout sauf groupe softs
total_alcool_eur = sum(v["disparu_eur"] for g, v in agg.items() if not g.startswith("0."))

rows = []
for g, v in sorted(agg.items()):
    pos = sorted([p for p in v["produits"]], key=lambda t: -t[1])[:5]
    rows.append({"groupe": g, "n_produits": v["n"],
                 "disparu_l": round(v["disparu_l"], 0),
                 "disparu_eur_revente": round(v["disparu_eur"], 0),
                 "pct_disparu_alcool": (round(100 * v["disparu_eur"] / total_alcool_eur, 1)
                                        if not g.startswith("0.") and total_alcool_eur else None),
                 "taux_disparu_pct_achats": (round(100 * v["disparu_l"] / v["achats_l"], 1) if v["achats_l"] else None),
                 "top_produits": pos})

out = {"description": "Signature du disparu par sous-groupe. Vente au noir => concentre sur F (cher/revendable). "
                      "Erreur de mesure/perte => concentre sur A/C (vrac au verre, pression).",
       "total_disparu_alcool_eur_revente": round(total_alcool_eur, 0),
       "groupes": rows}
json.dump(out, open(os.path.join(ICI, "signature.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("SIGNATURE DU DISPARU (nominal) par sous-groupe")
print(f"{'groupe':48} {'disparu €':>10} {'% alc':>6} {'%achats':>8}")
for r in rows:
    pa = f"{r['pct_disparu_alcool']}" if r['pct_disparu_alcool'] is not None else "-"
    ta = f"{r['taux_disparu_pct_achats']}" if r['taux_disparu_pct_achats'] is not None else "-"
    print(f"{r['groupe'][:48]:48} {r['disparu_eur_revente']:>10,.0f} {pa:>6} {ta:>8}")
print("\nsignature.json ecrit.")
