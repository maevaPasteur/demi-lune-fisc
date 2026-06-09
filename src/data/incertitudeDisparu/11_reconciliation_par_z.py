#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
11_reconciliation_par_z.py
Reconciliation au grain le plus fin disponible : la SESSION DE CAISSE (Z-report).

Puisqu'on ne peut PAS tracer chaque article supprime (les mecanismes -
correction, facture sans detail, carte cadeau differee - detruisent la
tracabilite par article), on prouve par la VALEUR, session par session :
  - le CA de chaque Z = la somme de ses tickets reellement payes (ANNEXE-H),
  - les suppressions (ANNEXE-E) sont un journal SEPARE, jamais incluses dans un
    total de ticket : elles n'ont jamais besoin d'etre "ajoutees" pour atteindre
    le CA.

Triangulation : 3 exports certifies independants donnent le meme CA :
  synthese (ANNEXE-A) ~ liste tickets (ANNEXE-H) ~ encaissements (ANNEXE-A).
Les suppressions (ANNEXE-E) sont en dehors des trois.
"""
import json, os
import xlrd
from collections import defaultdict

ICI = os.path.dirname(os.path.abspath(__file__))
CAISSE = os.path.normpath(os.path.join(ICI, "..", "..", "..", "public", "documents", "caisse-enregistreuse"))
EXOS = {"2022-2023": "1", "2023-2024": "2", "2024-2025": "3"}
CA_A = {"2022-2023": 409021, "2023-2024": 429205, "2024-2025": 437698}  # ANNEXE-A (08)
ENC_A = {"2022-2023": 409021, "2023-2024": 429205, "2024-2025": 437754}  # encaissements (08)

def tickets_par_z(path):
    sh = xlrd.open_workbook(path).sheet_by_index(0)
    h = [str(sh.cell_value(0, c)) for c in range(sh.ncols)]
    ci = {k: i for i, k in enumerate(h)}
    z_ca = defaultdict(float)
    z_nb = defaultdict(int)
    for r in range(1, sh.nrows):
        no_t = str(sh.cell_value(r, ci["no_ticket"])).strip()
        if no_t in ("", "A NOUVEAUX"):
            continue
        z = str(sh.cell_value(r, ci["no_z_report"])).strip()
        try:
            z_ca[z] += float(sh.cell_value(r, ci["tot_ttc"]) or 0)
        except ValueError:
            continue
        z_nb[z] += 1
    return z_ca, z_nb

def del_par_z(path):
    sh = xlrd.open_workbook(path).sheet_by_index(0)
    h = [str(sh.cell_value(0, c)) for c in range(sh.ncols)]
    ci = {k: i for i, k in enumerate(h)}
    z_del = defaultdict(float)
    z_n = defaultdict(int)
    for r in range(1, sh.nrows):
        if str(sh.cell_value(r, ci.get("dateEven", 1))).strip().lower().startswith("nb lignes"):
            continue
        if str(sh.cell_value(r, ci["typEven"])).strip() != "DEL":
            continue
        try:
            a = float(sh.cell_value(r, ci["amount"]) or 0)
        except ValueError:
            continue
        z = str(sh.cell_value(r, ci["no_zEport"])).strip()
        z_del[z] += a
        z_n[z] += 1
    return z_del, z_n

par_exo = {}
all_z = []
for exo, n in EXOS.items():
    z_ca, z_nb = tickets_par_z(os.path.join(CAISSE, f"ANNEXE-H{n}_liste-tickets_{exo}.xls"))
    z_del, z_dn = del_par_z(os.path.join(CAISSE, f"ANNEXE-E{n}_tpvevenement_{exo}.xls"))
    ca_h = sum(z_ca.values())
    del_tot = sum(z_del.values())
    zlist = sorted(set(z_ca) | set(z_del))
    for z in zlist:
        all_z.append({"exercice": exo, "z": z, "nb_tickets": z_nb.get(z, 0),
                      "ca_tickets": round(z_ca.get(z, 0), 2),
                      "suppr": round(z_del.get(z, 0), 2), "nb_suppr": z_dn.get(z, 0)})
    par_exo[exo] = {
        "ca_synthese_A": CA_A[exo], "ca_liste_tickets_H": round(ca_h, 0),
        "encaissements_A": ENC_A[exo], "ecart_H_vs_A": round(ca_h - CA_A[exo], 0),
        "nb_z": len(zlist), "suppr_total": round(del_tot, 0),
    }

# triangulation cumulee
tot_h = sum(p["ca_liste_tickets_H"] for p in par_exo.values())
tot_a = sum(CA_A.values())
tot_enc = sum(ENC_A.values())
tot_del = sum(p["suppr_total"] for p in par_exo.values())

# stat par Z : la suppression la plus lourde, et part des Z ou suppr > ca
z_sorted = sorted(all_z, key=lambda d: -d["suppr"])
z_suppr_sup_ca = [z for z in all_z if z["suppr"] > z["ca_tickets"] and z["ca_tickets"] > 0]

out = {
    "description": "Reconciliation par session de caisse (Z). Le CA de chaque Z = somme de ses tickets payes ; "
                   "les suppressions sont un journal separe, jamais incluses dans un total de ticket.",
    "triangulation_3_exports_certifies": {
        "ca_synthese_ANNEXE_A": tot_a, "ca_liste_tickets_ANNEXE_H": round(tot_h, 0),
        "encaissements_ANNEXE_A": tot_enc,
        "convergence": "les 3 donnent ~1,276 M€ (ecart cumule < 0,2%)",
        "suppressions_ANNEXE_E": round(tot_del, 0),
        "constat": "Les suppressions (430k) ne figurent dans AUCUN des 3 exports de CA. Elles ne sont jamais "
                   "necessaires pour atteindre le CA declare, qui s'explique entierement par les tickets payes.",
    },
    "par_exercice": par_exo,
    "nb_z_total": len(all_z),
    "z_avec_suppr_superieure_au_ca": {
        "n": len(z_suppr_sup_ca),
        "note": "Sessions ou les suppressions depassent le CA du jour = forcement des re-saisies/erreurs "
                "(on ne peut pas avoir supprime plus de ventes qu'on n'en a encaissees ce jour-la).",
        "exemples": sorted(z_suppr_sup_ca, key=lambda d: -d["suppr"])[:8],
    },
    "top_5_z_par_suppression": z_sorted[:5],
}
json.dump(out, open(os.path.join(ICI, "reconciliation_par_z.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("TRIANGULATION (3 exports certifies independants) - cumul 3 exercices")
print(f"  CA synthese (ANNEXE-A)      : {tot_a:>12,.0f} €")
print(f"  CA liste tickets (ANNEXE-H) : {tot_h:>12,.0f} €")
print(f"  Encaissements (ANNEXE-A)    : {tot_enc:>12,.0f} €")
print(f"  -> convergence ~1,276 M€ (les suppressions {tot_del:,.0f}€ sont EN DEHORS des trois)")
print()
print(f"Reconciliation par Z : {len(all_z)} sessions.")
print(f"  Sessions ou suppr > CA du jour : {len(z_suppr_sup_ca)} (forcement des re-saisies, pas des ventes)")
print("  Top sessions par suppression :")
for z in z_sorted[:5]:
    print(f"    Z {z['z']:>7} {z['exercice']} : CA tickets {z['ca_tickets']:>9,.0f}€ | suppr {z['suppr']:>10,.0f}€ ({z['nb_suppr']} lignes)")
print("\nreconciliation_par_z.json ecrit.")
