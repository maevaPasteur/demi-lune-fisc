#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
10_del_justification.py
Justification approfondie des suppressions (DEL), au-dela des 4 geantes.

Deux apports :
A) BALAYAGE DES ERREURS DE QUANTITE a toutes les echelles : chaque DEL = 1 ligne
   = prix x quantite. En lecture "le moins d'articles possible" (plus grand prix
   carte qui divise le montant), si la quantite reste >= SEUIL_TYPO, c'est une
   faute de frappe (aucune table ne commande 12+ menus identiques).
B) PREUVE POSITIVE PAR LA DISTRIBUTION : les montants supprimes epousent la
   meme grille de prix que les VENTES reelles (mêmes menus 45/34/29,90, mêmes
   verres 3,90...). Donc les suppressions sont de VRAIS articles du menu
   (re-encaisses/corriges/consolides), pas des ecritures fabriquees.

Honnete : les suppressions a quantite 2-6 de prix-menu = vraies tables, PAS des
typos. On ne sur-revendique pas.
"""
import json, os
import xlrd
from collections import Counter

ICI = os.path.dirname(os.path.abspath(__file__))
CAISSE = os.path.normpath(os.path.join(ICI, "..", "..", "..", "public", "documents", "caisse-enregistreuse"))
EXOS = {"2022-2023": "1", "2023-2024": "2", "2024-2025": "3"}
SEUIL_TYPO = 12  # quantite a partir de laquelle une ligne unique est invraisemblable

# grille de prix reels = prix unitaires recurrents dans les VENTES (ANNEXE-B)
prixc = Counter()
ventes_prix = Counter()
for n, exo in [("1", "2022-2023"), ("2", "2023-2024"), ("3", "2024-2025")]:
    sh = xlrd.open_workbook(os.path.join(CAISSE, f"ANNEXE-B{n}_prix-vente-quantite_{exo}.xls")).sheet_by_index(0)
    for r in range(1, sh.nrows):
        try:
            p = round(float(sh.cell_value(r, 7)), 2)
            q = float(sh.cell_value(r, 5))
        except (ValueError, TypeError):
            continue
        if p > 0:
            prixc[p] += 1
            ventes_prix[p] += q
grille = sorted([p for p, c in prixc.items() if c >= 20], reverse=True)

def min_articles(A):
    for p in grille:
        q = A / p
        if abs(q - round(q)) < 0.005 and round(q) >= 1:
            return p, int(round(q))
    return None, None

# --- balayage DEL ---
typos = []
del_prix = Counter()     # distribution des montants supprimes (ligne unique, qte=1)
tot_del = 0.0
n_del = 0
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
            a = float(sh.cell_value(r, ci["amount"]) or 0)
        except ValueError:
            continue
        if a <= 0:
            continue
        tot_del += a
        n_del += 1
        p, q = min_articles(a)
        if q and q >= SEUIL_TYPO:
            typos.append({"exercice": exo, "date": str(sh.cell_value(r, ci["dateEven"])).strip(),
                          "montant": round(a, 2), "prix": p, "quantite": q})
        if p and q == 1:
            del_prix[p] += 1

typos.sort(key=lambda d: -d["montant"])
typo_somme = round(sum(t["montant"] for t in typos), 2)

# --- preuve par distribution : top prix dans VENTES vs dans SUPPRESSIONS (ligne unique) ---
tot_v = sum(ventes_prix.values())
tot_d = sum(del_prix.values())
top = sorted(ventes_prix, key=lambda p: -ventes_prix[p])[:12]
distribution = [{"prix": p, "part_ventes_pct": round(100 * ventes_prix[p] / tot_v, 1),
                 "part_suppr_pct": round(100 * del_prix.get(p, 0) / tot_d, 1)} for p in top]

out = {
    "description": "Justification des suppressions : (A) erreurs de quantite a toutes echelles, "
                   "(B) preuve positive que les suppressions epousent la grille de prix des ventes reelles.",
    "seuil_typo_quantite": SEUIL_TYPO,
    "A_erreurs_quantite": {
        "n": len(typos), "somme_eur": typo_somme,
        "pct_du_total_del": round(100 * typo_somme / tot_del, 1),
        "lignes": typos,
    },
    "B_distribution_prix": {
        "note": "Les memes prix dominent ventes et suppressions => suppressions = vrais articles du menu.",
        "top_prix": distribution,
    },
}
json.dump(out, open(os.path.join(ICI, "del_justification.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print(f"A) ERREURS DE QUANTITE (quantite >= {SEUIL_TYPO}) : {len(typos)} lignes = {typo_somme:,.0f} € "
      f"({100*typo_somme/tot_del:.0f}% du total DEL)")
for t in typos:
    print(f"   {t['montant']:>10,.2f} €  = {t['prix']} x {t['quantite']}   ({t['date']})")
print()
print("B) DISTRIBUTION DES PRIX : ventes vs suppressions (ligne unique)")
print(f"   {'prix':>7} {'%ventes':>9} {'%suppr':>9}")
for d in distribution:
    print(f"   {d['prix']:>7} {d['part_ventes_pct']:>8}% {d['part_suppr_pct']:>8}%")
print("\ndel_justification.json ecrit.")
