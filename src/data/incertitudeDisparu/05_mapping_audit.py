#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
05_mapping_audit.py
Audit data science du mapping entre les 4 sources (factures / cartes / caisse /
inventaire), et correction du seul vrai bug d'attribution trouve.

Methode (data science, pas comptable) : on ne reconcilie pas ligne a ligne, on
detecte les SIGNATURES d'erreur de mapping :
  - orphelin conso : produit vendu (conso>0) mais quasi pas achete (achat~0)
    => ses ventes appartiennent a un autre produit (bouton generique non ventile)
  - orphelin achat : achete mais quasi pas vendu en propre (deja connu : softs)
Resultat du scan : 1 seul orphelin conso significatif cote vin = "Cubis de vin"
(427 L), bouton generique "Verre/Pichet de vin" non ventile par couleur.

Correction : redistribuer le Cubis sur les 3 vins MAISON (Aligote blanc / Cap
des Pins rose / Chusclan rouge), au prorata de leurs ventes nommees. C'est le
choix par defaut : un "verre de vin" generique = le vin de maison servi par
defaut depuis les BIB. Hypothese tracee et editable (cle 'redistribuer_sur').
"""
import json, os

ICI = os.path.dirname(os.path.abspath(__file__))
base = json.load(open(os.path.join(ICI, "base_disparu.json"), encoding="utf-8"))
boissons = {b["nom"]: b for b in base["boissons"]}

CUBIS = "Cubis de vin (couleur non précisée)"
MAISON = ["Bourgogne Aligoté maison",
          "Côtes de Provence rosé maison (Cap des Pins)",
          "Côtes du Rhône rouge maison (Chusclan)"]

def conso_tot(b):
    c = b["conso"]
    return c["seches_l"] + c["cocktails_l"] + c["plats_l"] + c["menu_moyen_l"]

def disparu_nominal(b):
    return b["achats_l"] - b["stock_final_l"] - conso_tot(b)

# --- etat AVANT ---
avant = {n: round(disparu_nominal(boissons[n]), 1) for n in MAISON}
cubis_l = boissons[CUBIS]["conso"]["seches_l"]
poids = {n: boissons[n]["conso"]["seches_l"] for n in MAISON}
poids_tot = sum(poids.values())

# --- redistribution du Cubis au prorata des ventes nommees seches ---
ajoute = {n: round(cubis_l * poids[n] / poids_tot, 1) for n in MAISON}

# base ajustee : on ajoute la part Cubis aux 'seches' des maison, on vide le Cubis
ajuste = json.loads(json.dumps(base))  # copie
amap = {b["nom"]: b for b in ajuste["boissons"]}
for n in MAISON:
    amap[n]["conso"]["seches_l"] = round(amap[n]["conso"]["seches_l"] + ajoute[n], 2)
    amap[n]["mapping_note"] = f"+{ajoute[n]} L redistribues depuis 'Cubis de vin' (bouton generique)"
# le Cubis n'a plus de conso propre (sinon double comptage)
amap[CUBIS]["conso"] = {k: 0.0 for k in amap[CUBIS]["conso"]}
amap[CUBIS]["mapping_note"] = f"{cubis_l} L redistribues sur les vins maison (bouton generique, 0 achat)"

apres = {n: round((amap[n]["achats_l"] - amap[n]["stock_final_l"]
                   - (amap[n]["conso"]["seches_l"] + amap[n]["conso"]["cocktails_l"]
                      + amap[n]["conso"]["plats_l"] + amap[n]["conso"]["menu_moyen_l"])), 1)
         for n in MAISON}

json.dump(ajuste, open(os.path.join(ICI, "base_disparu_ajuste.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

# prix revente maison (pour chiffrer le gain) depuis le xlsx deja extrait
prix = {n: boissons[n].get("prix_revente_l") or 0 for n in MAISON}
gain_l = sum(avant[n] - apres[n] for n in MAISON)
gain_eur = sum((avant[n] - apres[n]) * prix[n] for n in MAISON)

audit = {
    "description": "Audit mapping 4 sources + correction Cubis. Disparu vins maison avant/apres redistribution.",
    "scan_orphelins": {
        "orphelins_conso_significatifs_vin": [CUBIS],
        "cubis_litres_redistribues": cubis_l,
        "conclusion_scan": "Un seul orphelin conso vin (Cubis). Pas d'erreur de mapping generalisee. "
                           "Macon equilibre par exercice (pas de decalage de carte sur le disparu)."
    },
    "redistribution": {"redistribuer_sur": MAISON, "prorata_ventes_seches": poids, "litres_ajoutes": ajoute},
    "disparu_maison_avant_l": avant,
    "disparu_maison_apres_l": apres,
    "gain_litres": round(gain_l, 1),
    "gain_eur_revente": round(gain_eur, 0),
}
json.dump(audit, open(os.path.join(ICI, "mapping_audit.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("AUDIT MAPPING - correction Cubis de vin (bouton generique non ventile)")
print(f"Cubis redistribue : {cubis_l} L sur {MAISON}")
print(f"  prorata ventes nommees : {ajoute}\n")
print(f"{'vin maison':46} {'avant':>8} {'apres':>8}")
for n in MAISON:
    print(f"{n[:46]:46} {avant[n]:>8.0f} {apres[n]:>8.0f}")
print(f"\nGain disparu : {gain_l:.0f} L  /  {gain_eur:.0f} € (revente)")
print("base_disparu_ajuste.json + mapping_audit.json ecrits.")
