#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
01_extraction.py
Construit la base d'entree du modele d'incertitude (base_disparu.json).

Joint deux sources DEJA produites par le pipeline calculsBoissons :
  - consoTotaleParBoisson.json      -> decomposition de la conso par composante
                                       (boissons seches / cocktails / plats / menu bas-moy-haut)
                                       + achats (L) + stock final + taille contenant
  - rapprochementDisparuTotal.xlsx  -> prix achat €/L, prix revente €/L,
                                       et le drapeau "Conso complete ?" (Oui / Non vente seule)

AUCUN recalcul ici : on ne fait que rassembler les grandeurs existantes, en
litres cumules sur les 3 exercices. Tout produit non apparie est signale.
"""
import json, os
import openpyxl

ICI = os.path.dirname(os.path.abspath(__file__))
CALC = os.path.normpath(os.path.join(ICI, "..", "calculsBoissons"))

# ---------- 1. consoTotaleParBoisson.json : composantes de conso + achats + stock ----------
conso = json.load(open(os.path.join(CALC, "consoTotaleParBoisson.json"), encoding="utf-8"))

def litres_stock_final(b):
    taille = b.get("taille_achat_cl") or 0
    inv = b.get("inventaire_fin_contenants_par_periode") or {}
    # stock final = clôture du dernier exercice (31/03/2025)
    return (inv.get("2024-2025") or 0) * taille / 100.0 if taille else 0.0

base = {}
for b in conso["boissons"]:
    nom = b["nom_canonique"]
    seches = cocktails = plats = 0.0
    for ex, v in b["par_periode"].items():
        de = v.get("detail_exact_l", {})
        seches += de.get("boissons_seches", 0.0)
        cocktails += de.get("ingredients_cocktails", 0.0)
        plats += de.get("plats_desserts", 0.0)
    menu = b["total_3_exercices"]["menu_estime_l"]  # bas / moyen / haut
    achats = sum(x for x in (b.get("achats_litres_par_periode") or {}).values() if x)
    base[nom] = {
        "nom": nom,
        "categorie": b["categorie"],
        "taille_achat_cl": b.get("taille_achat_cl"),
        "unite_achat": b.get("unite_achat"),
        "achats_l": round(achats, 2),
        "stock_final_l": round(litres_stock_final(b), 2),
        "conso": {
            "seches_l": round(seches, 2),          # vendu au verre / a l'unite (caisse)
            "cocktails_l": round(cocktails, 2),     # ingredient de cocktail
            "plats_l": round(plats, 2),             # cuisine (plats/desserts)
            "menu_bas_l": round(menu["bas"], 2),    # alcool des menus (caisse ne detaille pas)
            "menu_moyen_l": round(menu["moyen"], 2),
            "menu_haut_l": round(menu["haut"], 2),
        },
    }

# ---------- 2. rapprochementDisparuTotal.xlsx : prix + drapeau conso complete ----------
wb = openpyxl.load_workbook(os.path.join(CALC, "rapprochementDisparuTotal.xlsx"))
ws = wb.active
rows = list(ws.iter_rows(values_only=True))
# l'entete reelle est la 1re ligne qui contient "Boisson"
hdr_i = next(i for i, r in enumerate(rows) if r and r[0] == "Boisson")
hdr = rows[hdr_i]
col = {name: j for j, name in enumerate(hdr)}

def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None

apparies, non_apparies_xlsx = 0, []
for r in rows[hdr_i + 1:]:
    if not r or not r[0]:
        continue
    nom = r[0]
    if nom not in base:
        non_apparies_xlsx.append(nom)
        continue
    cc = (r[col["Conso complète ?"]] or "")
    base[nom]["prix_achat_l"] = num(r[col["Prix achat €/L"]])
    base[nom]["prix_revente_l"] = num(r[col["Prix revente €/L"]])
    base[nom]["conso_complete"] = str(cc).strip().lower().startswith("oui")
    base[nom]["conso_complete_brut"] = str(cc).strip()
    apparies += 1

# produits presents dans conso mais absents du xlsx (pas de prix / pas de flag)
sans_prix = [n for n, v in base.items() if "prix_achat_l" not in v]

out = {
    "description": "Base d'entree du modele d'incertitude (Monte Carlo). Litres cumules 3 exercices. "
                   "conso_complete=False => ventes directes non enregistrees dans la source caisse "
                   "(softs/eaux) : leur 'disparu' est un trou de donnees, pas une disparition.",
    "n_boissons": len(base),
    "apparies_xlsx": apparies,
    "non_apparies_xlsx": non_apparies_xlsx,
    "sans_prix": sans_prix,
    "boissons": list(base.values()),
}
json.dump(out, open(os.path.join(ICI, "base_disparu.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print(f"base_disparu.json ecrit : {len(base)} boissons, {apparies} appariees au xlsx.")
if non_apparies_xlsx:
    print(f"  xlsx sans match conso ({len(non_apparies_xlsx)}):", non_apparies_xlsx)
if sans_prix:
    print(f"  conso sans prix xlsx ({len(sans_prix)}):", sans_prix)
n_incomplet = sum(1 for v in base.values() if v.get("conso_complete") is False)
print(f"  conso NON complete (softs/eaux, a exclure du disparu reel): {n_incomplet}")
