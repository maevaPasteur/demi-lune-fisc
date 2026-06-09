#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
12_reconciliation_disparu_vs_del.py
Reconcilie NOS DEUX analyses pour empecher le fisc de les retourner l'une contre
l'autre : le DISPARU boissons (~76 k€, modele Monte Carlo) et les SUPPRESSIONS
DEL (430 k€). Demontre qu'elles mesurent des choses differentes, ne s'additionnent
pas, et qu'aucune ne soutient une occultation de 430 k€.

Faits chiffres :
- CA declare boissons = 318 026 € / nourriture = 957 898 € (ANNEXE-A, 3 exos).
- Disparu boissons (alcool) = mediane ~76 k€ au prix de revente (resultats_montecarlo_ajuste2.json) ;
  softs reconcilies (script 07).
- Suppressions DEL = 430 763 €.
"""
import json, os

ICI = os.path.dirname(os.path.abspath(__file__))

# disparu boissons (alcool) depuis le Monte Carlo
mc = json.load(open(os.path.join(ICI, "resultats_montecarlo_ajuste2.json"), encoding="utf-8"))
disparu_alcool = mc["disparu_montecarlo_euros_revente"]["p50"]
disparu_ic = [mc["disparu_montecarlo_euros_revente"]["p2.5"], mc["disparu_montecarlo_euros_revente"]["p97.5"]]

CA_BOISSONS = 318026.0
CA_NOURRITURE = 957898.0
DEL_TOTAL = 430763.0
DEL_TYPOS = 140221.0           # erreurs de quantite (script 10)
DEL_SESSIONS_IMPOSSIBLES = 148000.0  # ordre de grandeur des 9 Z ou suppr > CA

args = {
    "1_double_comptage": {
        "principe": "Le disparu boissons = achats (factures) - conso (sonnee en caisse). Toute vente de boisson "
                    "faite au noir puis supprimee n'est PAS sonnee -> elle est DEJA comptee dans le disparu. "
                    "Le fisc ne peut donc pas la recompter dans les suppressions : disparu et DEL ne s'additionnent pas.",
        "consequence": "Les deux reconstitutions possibles du fisc (disparu ~76k, suppressions ~430k) sont "
                       "MUTUELLEMENT EXCLUSIVES. Il doit en choisir une, pas les sommer.",
    },
    "2_plafond_approvisionnement_boissons": {
        "disparu_alcool_revente_eur": disparu_alcool, "ic95": disparu_ic,
        "ca_boissons_declare_eur": CA_BOISSONS,
        "disparu_en_pct_du_ca_boissons": round(100 * disparu_alcool / CA_BOISSONS, 1),
        "principe": "Le maximum de boissons qui pourrait avoir ete vendu au noir = le disparu = ce qui a ete achete "
                    "mais pas sonne. Ce plafond est ~76k de revente sur 3 ans = ~24% du CA boissons, soit la perte "
                    "NORMALE d'un bar (15-25%), avec causes de conso documentees (sur-versement, conso Thierry, offerts, cuisine).",
    },
    "3_del_ne_peut_etre_des_ventes_boissons": {
        "del_total_eur": DEL_TOTAL, "ca_boissons_declare_eur": CA_BOISSONS,
        "ratio_del_sur_ca_boissons": round(DEL_TOTAL / CA_BOISSONS, 1),
        "principe": f"Si les 430k de DEL etaient des ventes de boissons dissimulees, le restaurant aurait vendu "
                    f"{DEL_TOTAL/CA_BOISSONS:.1f}x son CA boissons declare en boissons au noir, exigeant autant d'achats "
                    f"caches. Or les achats boissons se reconcilient avec la conso + perte normale (stock stable). Impossible.",
    },
    "4_distribution_menu_complet": {
        "principe": "Les prix des lignes supprimees epousent ceux des ventes du MENU COMPLET (nourriture + boissons "
                    "au prorata), pas une categorie boissons isolee (script 10). Donc les DEL = re-encaissements de "
                    "commandes normales mixtes, pas la dissimulation d'une categorie.",
        "ca_nourriture_declare_eur": CA_NOURRITURE,
    },
    "5_si_del_etaient_de_la_nourriture": {
        "principe": "Pour que le solde de DEL 'normales' (~290k) soit des ventes de NOURRITURE cachees, il faudrait "
                    "des achats de nourriture caches correspondants (~290k x ratio matiere ~30% = ~87k de factures "
                    "fournisseurs nourriture non comptabilisees). Verifiable sur les comptes d'achats nourriture.",
    },
}

out = {
    "description": "Reconciliation disparu boissons (76k) vs suppressions DEL (430k) : axes differents, non additionnables.",
    "synthese": "Le disparu boissons est un ecart de VOLUME (achats factures - conso caisse) = perte de conso normale. "
                "Les DEL sont un journal d'EVENEMENTS caisse = workflow. Le disparu capture deja toute vente non sonnee, "
                "donc on ne peut pas l'additionner aux DEL. Et le seul ancrage par les achats (le disparu, ~76k = 24% du "
                "CA boissons = norme CHR) plafonne toute occultation boissons tres en dessous des 430k de DEL.",
    "arguments": args,
}
json.dump(out, open(os.path.join(ICI, "reconciliation_disparu_vs_del.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("RECONCILIATION : disparu boissons (~76k) vs suppressions DEL (430k)")
print(f"  CA declare : boissons {CA_BOISSONS:,.0f}€ | nourriture {CA_NOURRITURE:,.0f}€")
print(f"  Disparu boissons (revente) : {disparu_alcool:,.0f}€ (IC {disparu_ic[0]:,.0f}-{disparu_ic[1]:,.0f}) = "
      f"{100*disparu_alcool/CA_BOISSONS:.0f}% du CA boissons = norme CHR")
print()
print("  1. DOUBLE COMPTAGE : une vente boisson au noir+supprimee est DEJA dans le disparu (non sonnee).")
print("     -> disparu et DEL NON additionnables ; le fisc doit choisir UNE base.")
print(f"  2. PLAFOND ACHATS : le max de boissons vendables au noir = le disparu = {disparu_alcool/1000:.0f}k = perte normale.")
print(f"  3. DEL = {DEL_TOTAL/CA_BOISSONS:.1f}x le CA boissons declare -> ne peut pas etre des ventes boissons cachees (pas d'achats).")
print("  4. Les DEL epousent le MENU COMPLET (nourriture+boissons), pas une categorie -> re-encaissements.")
print("  5. Si DEL = nourriture cachee -> ~87k d'achats nourriture caches, verifiable sur les comptes.")
print("\nreconciliation_disparu_vs_del.json ecrit.")
