#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
02_montecarlo.py
Propagation d'incertitude (Monte Carlo) sur le DISPARU boissons.

Idee centrale (data science) : le pipeline actuel calcule
    disparu = achats - stock - conso
ou la conso est construite avec des doses NOMINALES, zero perte, zero conso
personnel : autrement dit en supposant une incertitude NULLE sur ces postes.
On remplace ce "zero incertitude" par les fourchettes documentees de
parametres.json, et on propage. Sortie = une DISTRIBUTION du disparu, pas un
point. Si la barre d'erreur est enorme, le chiffre ponctuel du fisc n'a pas de
sens statistique.

Pure Python (random.triangular), graine fixe -> 100% reproductible.
Les softs/eaux (conso_complete=False) sont EXCLUS du disparu reel et reportes
a part : leur ecart est un trou de donnees (vente directe non enregistree dans
la source caisse), pas une disparition.
"""
import json, os, random, statistics, sys

ICI = os.path.dirname(os.path.abspath(__file__))
# base d'entree : argv[1] si fourni (ex: base_disparu_ajuste.json), sinon defaut
BASE_FILE = sys.argv[1] if len(sys.argv) > 1 else "base_disparu.json"
OUT_FILE = sys.argv[2] if len(sys.argv) > 2 else "resultats_montecarlo.json"
base = json.load(open(os.path.join(ICI, BASE_FILE), encoding="utf-8"))
P = json.load(open(os.path.join(ICI, "parametres.json"), encoding="utf-8"))
prm = P["parametres"]
CATV = set(P["categorisation"]["surversement_vin"])
CATS = set(P["categorisation"]["surversement_spiritueux"])
N = P["n_iterations"]
random.seed(P["seed"])

def tri(p):
    """tirage triangulaire (min, mode, max) avec garde si degenere."""
    a, m, b = p["min"], p["mode"], p["max"]
    return m if a == b else random.triangular(a, b, m)

def tri_vals(a, m, b):
    if a == b:
        return m
    if m < a: m = a
    if m > b: m = b
    return random.triangular(a, b, m)

def norm(s):
    return (s or "").lower().replace("û", "u").replace("ô", "o")

# --- separation fiable (alcool vendu en caisse) / non fiable (softs vente seule) ---
fiables = [x for x in base["boissons"] if x.get("conso_complete") is True]
non_fiables = [x for x in base["boissons"] if x.get("conso_complete") is False]
autres = [x for x in base["boissons"]
          if x.get("conso_complete") is None]  # ni Oui ni Non (ex: Cubis sans prix)

def est_fut(x):
    return x["categorie"] == "biere" and "fut" in norm(x.get("unite_achat"))

# --- disparu NOMINAL (pipeline actuel : mult=1, perte=0, perso=0, menu=moyen) ---
def disparu_nominal(x):
    c = x["conso"]
    conso = c["seches_l"] + c["cocktails_l"] + c["plats_l"] + c["menu_moyen_l"]
    return x["achats_l"] - x["stock_final_l"] - conso

nominal_l = {x["nom"]: disparu_nominal(x) for x in fiables}
nominal_total_l = sum(nominal_l.values())
nominal_total_eur = sum(nominal_l[x["nom"]] * (x.get("prix_revente_l") or 0) for x in fiables)
achats_total_l = sum(x["achats_l"] for x in fiables)

# --- Monte Carlo ---
tot_l_samples = []
tot_eur_samples = []
tot_pos_l_samples = []          # somme des disparus positifs uniquement (approche fisc)
par_cat_l = {}                  # accumulateur moyen par categorie
par_prod_l = {x["nom"]: [] for x in fiables}

for _ in range(N):
    # parametres globaux tires UNE fois (correles entre produits d'une meme categorie)
    sv = tri(prm["surversement_vin"])
    ss = tri(prm["surversement_spiritueux"])
    pb = tri(prm["perte_biere_fut"])
    dc = tri(prm["dose_cocktail"])
    dk = tri(prm["dose_cuisine"])
    po = tri(prm["personnel_offerts_alcool"])

    s_l = 0.0
    s_eur = 0.0
    s_pos = 0.0
    for x in fiables:
        c = x["conso"]
        cat = x["categorie"]
        # sur-versement applique au vendu "seches"
        if cat in CATV:
            pour = sv
        elif cat in CATS:
            pour = ss
        else:
            pour = 1.0   # biere pression : servi precis, la perte est additive (ci-dessous)
        conso = (c["seches_l"] * pour
                 + c["cocktails_l"] * dc
                 + c["plats_l"] * dk
                 + tri_vals(c["menu_bas_l"], c["menu_moyen_l"], c["menu_haut_l"])
                 + x["achats_l"] * po)
        if est_fut(x):
            conso += x["achats_l"] * pb
        cs = x.get("conso_staff_l")   # conso personnel/owner itemisee (Picon, Macvin)
        if cs:
            conso += tri_vals(cs["bas"], cs["moyen"], cs["haut"])
        disp = x["achats_l"] - x["stock_final_l"] - conso
        s_l += disp
        s_pos += max(disp, 0.0)
        s_eur += disp * (x.get("prix_revente_l") or 0)
        par_prod_l[x["nom"]].append(disp)
        par_cat_l.setdefault(cat, [0.0, 0])
    tot_l_samples.append(s_l)
    tot_eur_samples.append(s_eur)
    tot_pos_l_samples.append(s_pos)

def pct(xs, q):
    xs = sorted(xs)
    k = (len(xs) - 1) * q
    f = int(k)
    return xs[f] if f + 1 >= len(xs) else xs[f] + (xs[f + 1] - xs[f]) * (k - f)

def resume(xs):
    return {
        "p2.5": round(pct(xs, 0.025), 1),
        "p50": round(pct(xs, 0.5), 1),
        "mean": round(statistics.fmean(xs), 1),
        "p97.5": round(pct(xs, 0.975), 1),
        "min": round(min(xs), 1),
        "max": round(max(xs), 1),
    }

# disparu par produit : moyenne MC
prod_moy = {n: round(statistics.fmean(v), 1) for n, v in par_prod_l.items()}

# trou de donnees softs (non fiables) : disparu nominal, NON compte dans le reel
trou_softs_l = sum(disparu_nominal(x) for x in non_fiables)
trou_softs_eur = sum(disparu_nominal(x) * (x.get("prix_revente_l") or 0) for x in non_fiables)

# benchmark : disparu en % des achats alcool
disp_pct_achats = resume([s / achats_total_l * 100 for s in tot_l_samples])

out = {
    "description": "Resultats Monte Carlo du disparu boissons. Litres et euros (valorises au prix de revente carte). "
                   "Disparu = achats - stock_final - conso_avec_incertitude, cumule 3 exercices, alcool a conso fiable uniquement.",
    "n_iterations": N,
    "seed": P["seed"],
    "n_produits_fiables": len(fiables),
    "achats_alcool_fiable_l": round(achats_total_l, 1),
    "disparu_nominal_pipeline_actuel": {
        "litres": round(nominal_total_l, 1),
        "euros_revente": round(nominal_total_eur, 1),
        "commentaire": "Valeur du pipeline actuel = hypothese implicite d'incertitude NULLE (doses nominales, 0 perte, 0 conso perso, menu=moyen)."
    },
    "disparu_montecarlo_litres": resume(tot_l_samples),
    "disparu_montecarlo_euros_revente": resume(tot_eur_samples),
    "disparu_positifs_seuls_litres": resume(tot_pos_l_samples),
    "disparu_en_pct_des_achats": disp_pct_achats,
    "trou_donnees_softs_non_fiables": {
        "n_produits": len(non_fiables),
        "litres": round(trou_softs_l, 1),
        "euros_revente": round(trou_softs_eur, 1),
        "produits": [x["nom"] for x in non_fiables],
        "commentaire": "Ventes directes non enregistrees dans la source caisse (softs/eaux). A NE PAS compter comme disparition."
    },
    "produits_sans_flag": [x["nom"] for x in autres],
    "disparu_moyen_par_produit_l": dict(sorted(prod_moy.items(), key=lambda kv: -kv[1])),
}
json.dump(out, open(os.path.join(ICI, OUT_FILE), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

# --- impression ---
print("=" * 64)
print("DISPARU BOISSONS - propagation d'incertitude (Monte Carlo)")
print("=" * 64)
print(f"Produits alcool a conso fiable : {len(fiables)}  |  achats {achats_total_l:.0f} L")
print(f"Softs/eaux exclus (trou de donnees) : {len(non_fiables)} produits "
      f"= {trou_softs_l:.0f} L / {trou_softs_eur:.0f} € (PAS une disparition)")
print()
n = out["disparu_nominal_pipeline_actuel"]
print(f"Disparu NOMINAL (pipeline actuel, 0 incertitude) : "
      f"{n['litres']:.0f} L  /  {n['euros_revente']:.0f} € (revente)")
print()
mc = out["disparu_montecarlo_litres"]
mce = out["disparu_montecarlo_euros_revente"]
print("Disparu MONTE CARLO (incertitude propagee) :")
print(f"  litres  : p50={mc['p50']:.0f}   IC95% [{mc['p2.5']:.0f} ; {mc['p97.5']:.0f}]   (min {mc['min']:.0f} / max {mc['max']:.0f})")
print(f"  euros   : p50={mce['p50']:.0f}   IC95% [{mce['p2.5']:.0f} ; {mce['p97.5']:.0f}]")
dp = out["disparu_en_pct_des_achats"]
print(f"  % achats: p50={dp['p50']:.1f}%   IC95% [{dp['p2.5']:.1f}% ; {dp['p97.5']:.1f}%]")
b = P["benchmark_metier"]["shrinkage_bar_pct_ca"]
print(f"  (benchmark perte CHR normale : {b[0]*100:.0f}-{b[1]*100:.0f}%)")
print()
print(f"{OUT_FILE} ecrit.")
