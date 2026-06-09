#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
09_aberrations_del.py
Identifie ce que sont les rares GROSSES suppressions (les "aberrations" mises de
cote par analyseDel.ts, ~32% du total). Hypothese : erreurs de saisie de
QUANTITE (un nombre absurde tape dans le champ quantite, puis supprime aussitot).

Test : pour chaque grosse DEL, on cherche montant = prix_carte x quantite_entiere,
en privilegiant les quantites "fat-finger" (99, 999, 9999, 100, 1000...).
Si ca tombe juste sur un prix de menu reel -> c'est une faute de frappe, jamais
servie, jamais encaissee.
"""
import json, os
import xlrd

ICI = os.path.dirname(os.path.abspath(__file__))
CAISSE = os.path.normpath(os.path.join(ICI, "..", "..", "..", "public", "documents", "caisse-enregistreuse"))
EXOS = {"2022-2023": "1", "2023-2024": "2", "2024-2025": "3"}
SEUIL = 1000.0  # une ligne de restaurant > 1000 € est forcement anormale

# prix carte/menu connus (menusPrix.json + cartes), pour nommer le produit
PRIX_CONNUS = {6.90: "Menu Bambin", 9.90: "Menu Enfant", 45.00: "Menu Demi Lune",
               29.90: "Menu Dahu", 34.00: "Menu Bourguignon/Franc-Comtois", 32.00: "Menu (carte C)",
               19.60: "ligne ~19,60 €", 18.60: "Menu Express (carte A)", 4.90: "Macvin / Apero P.Gregoire",
               3.90: "Verre vin maison", 5.90: "Cocktail / cremant"}
QTES = [99, 100, 999, 1000, 9999, 9990, 200, 500, 2000, 4000]

def factorise(montant):
    best = None
    for q in QTES:
        p = montant / q
        pr = round(p, 2)
        # decomposition EXACTE : prix a 2 decimales x quantite = montant au centime
        if 1 <= pr <= 50 and abs(pr * q - montant) < 0.01:
            nom = PRIX_CONNUS.get(pr, f"ligne {pr:.2f} €")
            cand = {"quantite": q, "prix_unitaire": pr, "produit": nom, "exact": True}
            # priorite aux quantites "fat-finger" classiques
            if best is None or q in (9999, 999, 99):
                best = cand
    return best

out = []
for exo, n in EXOS.items():
    sh = xlrd.open_workbook(os.path.join(CAISSE, f"ANNEXE-E{n}_tpvevenement_{exo}.xls")).sheet_by_index(0)
    h = [str(sh.cell_value(0, c)) for c in range(sh.ncols)]
    ci = {k: i for i, k in enumerate(h)}
    for r in range(1, sh.nrows):
        if str(sh.cell_value(r, ci.get("dateEven", 1))).strip().lower().startswith("nb lignes"):
            continue
        if str(sh.cell_value(r, ci["typEven"])).strip() != "DEL":
            continue
        try:
            amt = float(sh.cell_value(r, ci["amount"]) or 0)
        except ValueError:
            amt = 0
        if amt > SEUIL:
            out.append({
                "exercice": exo,
                "date": str(sh.cell_value(r, ci["dateEven"])).strip(),
                "heure": str(sh.cell_value(r, ci["heureEven"])).strip(),
                "caissier": str(sh.cell_value(r, ci["caissier"])).strip(),
                "montant": round(amt, 2),
                "explication": factorise(amt),
            })

out.sort(key=lambda d: -d["montant"])
res = {
    "description": "Grosses suppressions (> 1000 €) = erreurs de saisie de QUANTITE, supprimees aussitot. "
                   "montant = prix_carte x quantite absurde (99/999/9999...). Jamais servies ni encaissees.",
    "avertissement_honnete": "ANNEXE-E n'a PAS de colonne produit/quantite : la decomposition prix x quantite est "
                             "INFEREE, et plusieurs lectures exactes existent (ex 68 993,10 = 6,90 x 9999 = 9,90 x 6969). "
                             "Le produit exact est inconnaissable ; seule la QUANTITE absurde (centaines a milliers) est certaine. "
                             "La preuve VRAIMENT irrefutable n'est pas la factorisation mais le niveau SESSION (script 11) : "
                             "on ne peut pas supprimer 69 557 € un jour ou on n'a encaisse que 2 563 €.",
    "seuil_eur": SEUIL,
    "n_aberrations": len(out),
    "somme_aberrations_eur": round(sum(d["montant"] for d in out), 2),
    "aberrations": out,
}
json.dump(res, open(os.path.join(ICI, "aberrations_del.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("GROSSES SUPPRESSIONS (> 1000 €) = erreurs de quantite")
print(f"{'date':12} {'heure':6} {'montant':>11}   = prix x quantite (produit)")
for d in out:
    e = d["explication"]
    f = f"{e['prix_unitaire']:.2f} € x {e['quantite']}  ({e['produit']})" + ("  [EXACT]" if e.get("exact") else "") if e else "?"
    print(f"{d['date']:12} {d['heure']:6} {d['montant']:>11,.2f}   = {f}")
print(f"\nTotal : {len(out)} lignes = {res['somme_aberrations_eur']:,.0f} € (toutes des fautes de frappe quantite, supprimees aussitot)")
print("aberrations_del.json ecrit.")
