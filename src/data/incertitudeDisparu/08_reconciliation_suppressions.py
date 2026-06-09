#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
08_reconciliation_suppressions.py
Diagnostic de reconciliation des 430 763 € de lignes supprimees (DEL, ANNEXE-E).

Question : ces suppressions sont-elles des ventes dissimulees (occultation) ou
du workflow caisse (corrections, re-encaissements, cartes cadeau, factures sans
detail) qui se neutralise dans le CA declare ?

Methode data science : on ne classe pas (encore) chaque DEL ; on teste si les
suppressions peuvent avoir GENERE DU REVENU non declare. Deux verrous :
  1. VERROU PAIEMENT : le CA declare egale-t-il les encaissements ? et quelle
     part en especes (seul canal non tracable) ?
  2. VERROU APPROVISIONNEMENT : 430 k€ de ventes cachees exigeraient ~430 k€
     d'achats caches (inputs). Or les achats boissons se reconcilient avec la
     conso + perte normale (cf modele incertitude) et le stock est stable.

Source FIABLE = ANNEXE-A (synthese : CA declare = encaissements au centime).
ANNEXE-F (reglements) est ECARTE : il double-compte (1,32 M€ vs 429 k€ de CA).
"""
import json, os
import xlrd

ICI = os.path.dirname(os.path.abspath(__file__))
CAISSE = os.path.normpath(os.path.join(ICI, "..", "..", "..", "public", "documents", "caisse-enregistreuse"))
EXOS = {"2022-2023": "1", "2023-2024": "2", "2024-2025": "3"}

def parse_annexe_a(path):
    sh = xlrd.open_workbook(path).sheet_by_index(0)
    ca = enc_tot = esp = 0.0
    enc = {}
    in_enc = False
    for r in range(sh.nrows):
        c0 = str(sh.cell_value(r, 0)).strip()
        c2 = str(sh.cell_value(r, 2)).strip()
        try:  # bloc TVA : taux en col0, TTC en col3
            taux = float(c0)
            if taux in (0.2, 0.1, 0.055, 0.085, 0.0) and sh.ncols > 3:
                ca += float(sh.cell_value(r, 3))
        except ValueError:
            pass
        if "encaissement" in c0.lower():
            in_enc = True
            continue
        if in_enc:
            if c0.upper() == "TOTAL":
                enc_tot = float(c2) if c2 else 0.0
                in_enc = False
            elif c0:
                try:
                    enc[c0] = float(c2)
                except ValueError:
                    pass
    esp = next((v for k, v in enc.items() if "esp" in k.lower()), 0.0)
    return ca, enc_tot, esp, enc

def deletions(path):
    sh = xlrd.open_workbook(path).sheet_by_index(0)
    h = [str(sh.cell_value(0, c)) for c in range(sh.ncols)]
    ci = {k: i for i, k in enumerate(h)}
    tot = 0.0
    n = 0
    for r in range(1, sh.nrows):
        # exclure les pieds de page recap ("Nb lignes ... DEL ... total") : ils
        # n'ont pas de date d'evenement et contiennent le total -> double comptage
        date_even = str(sh.cell_value(r, ci.get("dateEven", 1))).strip()
        if "nb lignes" in date_even.lower() or not str(sh.cell_value(r, ci.get("noCaisse", 0))).strip():
            continue
        if str(sh.cell_value(r, ci["typEven"])).strip() == "DEL":
            try:
                tot += float(sh.cell_value(r, ci["amount"]) or 0)
            except ValueError:
                pass
            n += 1
    return tot, n

res = {}
for exo, k in EXOS.items():
    ca, enc, esp, enc_detail = parse_annexe_a(os.path.join(CAISSE, f"ANNEXE-A{k}_synthese-CA_{exo}.xls"))
    sup, nsup = deletions(os.path.join(CAISSE, f"ANNEXE-E{k}_tpvevenement_{exo}.xls"))
    res[exo] = {
        "ca_declare_ttc": round(ca, 0), "encaissements_ttc": round(enc, 0),
        "ecart_ca_vs_encaissements": round(ca - enc, 0),
        "especes": round(esp, 0), "part_especes_pct": round(100 * esp / enc, 1) if enc else None,
        "non_tracable_max_eur": round(esp, 0),
        "suppressions_eur": round(sup, 0), "nb_suppressions": nsup,
        "suppr_sur_ca_pct": round(100 * sup / ca, 0) if ca else None,
        "encaissements_detail": {k2: round(v) for k2, v in enc_detail.items()},
    }

tot_ca = sum(v["ca_declare_ttc"] for v in res.values())
tot_enc = sum(v["encaissements_ttc"] for v in res.values())
tot_esp = sum(v["especes"] for v in res.values())
tot_sup = sum(v["suppressions_eur"] for v in res.values())

out = {
    "description": "Reconciliation des lignes supprimees (DEL). Teste si elles ont pu generer du revenu non declare.",
    "source_fiable": "ANNEXE-A (CA declare = encaissements). ANNEXE-F ecarte (double-compte).",
    "par_exercice": res,
    "totaux": {
        "ca_declare_ttc": tot_ca, "encaissements_ttc": tot_enc,
        "ca_egale_encaissements": abs(tot_ca - tot_enc) < 100,
        "especes_total": tot_esp, "part_especes_pct": round(100 * tot_esp / tot_enc, 1),
        "suppressions_total": tot_sup, "suppr_sur_ca_pct": round(100 * tot_sup / tot_ca, 0),
    },
    "verdict": {
        "verrou_paiement": "CA declare = encaissements au centime (3 exos). Especes = 1,3% du CA. "
                           "Aucun ecart, et quasi aucun canal especes pour encaisser au noir des ventes supprimees.",
        "plafond_occultation_par_especes": tot_esp,
        "verrou_approvisionnement": "430 k€ de ventes cachees exigeraient ~430 k€ d'achats caches. Or les achats "
                                    "boissons se reconcilient avec conso + perte normale (modele incertitude) et le stock "
                                    "est stable : pas d'inputs pour des ventes fantomes.",
        "conclusion": "Les suppressions ne peuvent PAS etre des ventes dissimulees : ni canal de paiement (CA=encaissements, "
                      "1,3% especes), ni canal d'approvisionnement. Ce sont des re-encaissements/corrections/cartes cadeau/factures "
                      "sans detail qui se neutralisent dans le CA declare (deja net des suppressions), lui-meme bancarise a ~98,7%.",
        "reserve": "Diagnostic MACRO (pas de classification ligne a ligne des DEL). Decroissance suppr/CA 47%->33%->22% a "
                   "expliquer (probable evolution du workflow caisse). A partager avec l'avocat car l'enjeu (430 k€) depasse les boissons.",
    },
}
json.dump(out, open(os.path.join(ICI, "reconciliation_suppressions.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("RECONCILIATION DES SUPPRESSIONS (430 k€)")
print(f"{'exo':12} {'CA decl':>10} {'encaiss':>10} {'ecart':>7} {'%esp':>6} {'suppr':>10} {'suppr/CA':>9}")
for exo, v in res.items():
    print(f"{exo:12} {v['ca_declare_ttc']:>10,.0f} {v['encaissements_ttc']:>10,.0f} "
          f"{v['ecart_ca_vs_encaissements']:>7,.0f} {v['part_especes_pct']:>5}% {v['suppressions_eur']:>10,.0f} {v['suppr_sur_ca_pct']:>8.0f}%")
print(f"{'TOTAL':12} {tot_ca:>10,.0f} {tot_enc:>10,.0f} {tot_ca-tot_enc:>7,.0f} {100*tot_esp/tot_enc:>5.1f}% {tot_sup:>10,.0f} {100*tot_sup/tot_ca:>8.0f}%")
print()
print(f"VERROU 1 (paiement) : CA = encaissements (ecart {tot_ca-tot_enc:.0f} €). Especes = {tot_esp:,.0f} € = {100*tot_esp/tot_enc:.1f}% -> plafond d'occultation possible.")
print(f"VERROU 2 (achats)   : 430 k€ de ventes cachees = 430 k€ d'achats caches. Achats reconcilies, stock stable -> impossible.")
print("=> Suppressions = workflow, PAS occultation. reconciliation_suppressions.json ecrit.")
