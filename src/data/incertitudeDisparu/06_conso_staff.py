#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
06_conso_staff.py
Estimation de la consommation du personnel / owner, bornee et justifiee par les
donnees (pas un chiffre en l'air). Source cliente (2026-06-09) :
  - Chris-Elian (serveur) : 4 Coca/jour ; Ghislaine (gerante) : 2 Coca/jour.
  - Tout le staff : cafe, sirop, jus de fruit.
  - Thierry (chef/owner) : BEAUCOUP de Picon Biere et de Macvin (quantite exacte
    inconnue -> on l'estime).
  - Quelques digestifs/aperos offerts aux clients (peu).

Methode data science : on ne devine pas un volume, on l'ancre sur une signature
mesurable des donnees, et on le borne.
  - PICON : achete 72 L, vendu 28 L (uniquement en Picon Biere), 0 vendu seul,
    pas de prix de revente => le residu 44 L est de facto la conso de Thierry.
    Verif de plausibilite : 44 L / 4 cl (picon dans un Picon Biere) = 1100 Picon
    Biere sur 3 ans = 1,7/jour. Coherent avec "beaucoup de Picon Biere".
    => conso staff Picon = 44 L (toute la disparition Picon), bornee par l'achat.
  - MACVIN : disparu 335 L. On NE met PAS tout sur Thierry (335/662j = 8,5
    verres/jour, invraisemblable). On borne par un taux owner plausible :
    2 a 3 verres de 6 cl/jour => 79 a 119 L sur 662 jours (central 2,5 = 99 L).
    Le reste du disparu macvin = sur-versement cocktails/verre + apero offert +
    residu irreductible (deja documente dans l'enquete macvin).

Softs (Coca/jus/sirop/cafe) : documentes ici car ils expliquent le TROU DE
DONNEES softs (deja hors disparu alcool), pas le disparu alcool.
"""
import json, os

ICI = os.path.dirname(os.path.abspath(__file__))
base = json.load(open(os.path.join(ICI, "base_disparu_ajuste.json"), encoding="utf-8"))

# jours d'ouverture par exercice (verifie caisse, 1 Z/jour, annexe H ; attestation)
JOURS = {"2022-2023": 222, "2023-2024": 221, "2024-2025": 219}
J = sum(JOURS.values())  # 662

# ---------- SOFTS : documentation du trou de donnees (hors disparu alcool) ----------
coca_cl = 33.0
coca_staff_cans_jour = 4 + 2  # Chris 4 + Ghislaine 2
coca_staff_l = coca_staff_cans_jour * J * coca_cl / 100.0

# ---------- ALCOOL : conso staff itemisee (entre dans le disparu) ----------
# PICON : tout le disparu (borne par achat - vendu)
picon = next(x for x in base["boissons"] if x["nom"] == "Picon")
picon_disparu = picon["achats_l"] - picon["stock_final_l"] - sum(
    picon["conso"][k] for k in ("seches_l", "cocktails_l", "plats_l", "menu_moyen_l"))
picon_staff = {"bas": round(picon_disparu * 0.85, 1), "moyen": round(picon_disparu, 1),
               "haut": round(picon_disparu, 1)}
picon_par_jour = picon_disparu / 0.04 / J  # nb de Picon Biere/jour (4cl picon)

# MACVIN : taux owner plausible 2 a 3 verres de 6 cl/jour
macvin_verre_cl = 6.0
mac_bas = round(2.0 * macvin_verre_cl / 100 * J, 1)   # 2 verres/j
mac_moy = round(2.5 * macvin_verre_cl / 100 * J, 1)   # 2,5 verres/j
mac_haut = round(3.0 * macvin_verre_cl / 100 * J, 1)  # 3 verres/j
macvin = next(x for x in base["boissons"] if x["nom"] == "Macvin")
macvin_disparu = macvin["achats_l"] - macvin["stock_final_l"] - sum(
    macvin["conso"][k] for k in ("seches_l", "cocktails_l", "plats_l", "menu_moyen_l"))
macvin_staff = {"bas": mac_bas, "moyen": mac_moy, "haut": mac_haut}

# ---------- injection dans une base ajuste2 (champ conso_staff_l par produit) ----------
import copy
base2 = copy.deepcopy(base)
b2 = {x["nom"]: x for x in base2["boissons"]}
b2["Picon"]["conso_staff_l"] = picon_staff
b2["Macvin"]["conso_staff_l"] = macvin_staff
b2["_meta_staff"] = {"jours_ouverture": JOURS, "total_jours": J}
json.dump(base2, open(os.path.join(ICI, "base_disparu_ajuste2.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

staff = {
    "description": "Conso personnel/owner estimee, bornee et justifiee. ALCOOL entre dans le disparu (Picon, Macvin) ; SOFTS documentent le trou de donnees softs.",
    "jours_ouverture_total": J,
    "source": "Cliente 2026-06-09 (doses_cliente/)",
    "softs_hors_disparu_alcool": {
        "coca_staff": {
            "detail": "Chris-Elian 4/j + Ghislaine 2/j = 6 Coca/jour",
            "litres_3ans": round(coca_staff_l, 0),
            "rappel_disparu_coca_l": 1950,
            "part_expliquee_pct": round(100 * coca_staff_l / 1950, 0),
            "commentaire": "Ces 2 personnes a elles seules expliquent la majorite du trou Coca ; le reste = autres staff occasionnels + offerts clients. Cafe/sirop/jus staff expliquent les autres trous softs."
        }
    },
    "alcool_dans_disparu": {
        "Picon_Thierry": {
            "litres_3ans": picon_staff,
            "equiv_par_jour": f"{picon_par_jour:.1f} Picon Biere/jour",
            "justification": "Picon achete 72 L, jamais vendu seul (0 prix revente), seul usage caisse = Picon Biere (28 L). Le residu 44 L = conso Thierry, borne par l'achat. 1,7 Picon Biere/jour, coherent avec 'beaucoup de Picon Biere'.",
            "disparu_picon_l": round(picon_disparu, 1),
            "ferme_le_disparu_picon": True
        },
        "Macvin_Thierry": {
            "litres_3ans": macvin_staff,
            "equiv_par_jour": "2 a 3 verres de 6 cl/jour (central 2,5)",
            "justification": "Disparu macvin 335 L. Tout attribuer a Thierry = 8,5 verres/jour, invraisemblable. Borne owner plausible 2-3 verres/jour => 79-119 L. Le reste du disparu macvin (~220 L) = sur-versement cocktails/verre + apero offert + residu irreductible (enquete macvin).",
            "disparu_macvin_l": round(macvin_disparu, 1),
            "part_disparu_macvin_expliquee_pct": [round(100*mac_bas/macvin_disparu), round(100*mac_haut/macvin_disparu)]
        }
    },
    "offerts": "Quelques digestifs/aperos offerts (peu) : modelises par le parametre personnel_offerts_alcool residuel."
}
json.dump(staff, open(os.path.join(ICI, "staff_conso.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print(f"Jours d'ouverture (3 exos) : {J}")
print(f"SOFTS Coca staff : 6/jour x {J} = {coca_staff_l:.0f} L = {100*coca_staff_l/1950:.0f}% du trou Coca (1950 L)")
print(f"PICON Thierry : {picon_disparu:.0f} L = {picon_par_jour:.1f} Picon Biere/jour -> ferme le disparu Picon")
print(f"MACVIN Thierry : {mac_bas:.0f}-{mac_haut:.0f} L (2-3 verres/j) = {100*mac_bas/macvin_disparu:.0f}-{100*mac_haut/macvin_disparu:.0f}% du disparu macvin ({macvin_disparu:.0f} L)")
print("staff_conso.json + base_disparu_ajuste2.json ecrits.")
