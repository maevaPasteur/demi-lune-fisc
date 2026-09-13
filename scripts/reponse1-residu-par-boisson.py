#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TEMPORAIRE - lecture seule. Decompose le residu de 2 228,08 L produit par
scripts/reponse1-cascade-valeurs.py, boisson par boisson, en reprenant
exactement la meme arithmetique poste par poste.

Verse dans le depot la piece R1-residu-par-boisson.csv, qui rend auditables
les chiffres du residu publies par la page cascade-10622-litres.
"""
import json, os, csv, datetime, collections

ROOT = "/Users/maevapasteur/Documents/demi-lune-comptabilite"
RACINE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT  = os.path.join(RACINE, "public/documents/pieces-reponse-1")
L = lambda p: json.load(open(os.path.join(ROOT, p), encoding="utf-8"))

CASCADE = L("src/data/reponse1Calculs/cascade-10622.json")
BASE    = L("src/data/incertitudeDisparu/base_disparu_ajuste2.json")
SV      = L("src/data/reponse1Calculs/sur-versement-fourchette.json")
HC      = L("src/data/calculsBoissons/boissonsHorsCocktail.json")["boissons"]
DEG_PAGE= L("src/data/reponse1/degustation-offerte.json")

# --- constantes reprises TELLES QUELLES de scripts/reponse1-cascade-valeurs.py
AVOIRS = {"Cidre Brut": 22.5, "Bourgogne Aligoté maison": 10.0, "Grand Marnier": 2.1}
FORMATS_MIXTES = ["Panaché 25cl", "Monaco 25cl", "Demi+Picon 25cl", "Pinte+Picon 50cl"]
CUISINE_PLAFONNE = [
    ("Ravelin", 251.80, 251.80), ("Macvin", 177.51, 177.51),
    ("Arbois Vin Jaune", 124.48, 124.48), ("Calvados", 119.07, 73.00),
    ("Porto", 70.74, 68.27), ("Crème de Cassis", 18.67, 18.67),
    ("Bailey's", 15.28, 15.28), ("Grand Marnier", 7.42, 5.96),
    ("Marc de Bourgogne", 5.58, 2.10), ("Liqueur de Poire", 4.07, 4.07),
]
JOURS_SERVICE = 662
CA_DECLARE = 1278214.22

alc = [b for b in BASE["boissons"] if b.get("conso_complete") is True]
noms = [b["nom"] for b in alc]
idx = {b["nom"]: b for b in alc}

# ---------------------------------------------------------------- poste verre
# double comptage biere : contenance des 4 articles mixtes, sur le Fut Affligem
double_biere = round(sum(x["total_volume_l"] for x in HC
                         if x["nom_canonique"] == "Fût Affligem"
                         and x["format_service"] in FORMATS_MIXTES), 2)

# ------------------------------------------------------- poste sur-versement
sv_par_nom = {b["nom"]: b["cumul"]["retenu_l"] for b in SV["boissons"]}
sv_hors_base = {k: v for k, v in sv_par_nom.items() if k not in idx and v}

# --------------------------------------------------------- poste degustation
# tableau « Le même décompte, par exercice et par vin nommé », section 27 de
# src/data/reponse1/degustation-offerte.json (colonne « Volume offert »)
DEG_VERS_BASE = {
    "Savagnin": "Arbois Savagnin", "Arbois Trousseau": "Arbois Trousseau",
    "Saint Véran": "Saint Véran", "Aligoté": "Bourgogne Aligoté maison",
    "Chusclan": "Côtes du Rhône rouge maison (Chusclan)",
    "HC de Beaune": "Hautes Côtes de Beaune rouge",
    "Moulin à Vent": "Moulin à Vent", "Mâcon": "Macon",
    "Gewurztraminer": "Gewurztraminer", "Arbois Chardonnay": "Arbois Chardonnay",
    "Chablis": "Chablis", "Saint Joseph": "Saint Joseph Rouge",
}
deg = {}
for lig in DEG_PAGE["sections"][27]["lignes"]:
    v = [c["v"] if isinstance(c, dict) else c for c in lig]
    if v[0] == "TOTAL":
        continue
    deg[DEG_VERS_BASE[v[0]]] = float(v[5].replace(" L", "").replace(",", "."))

# ----------------------------------------------------------- postes globaux
P = {p["cle"]: p["litres"] for p in CASCADE["postes"]}

emplois = {n: collections.defaultdict(float) for n in noms}
for b in alc:
    n = b["nom"]; c = b["conso"]
    emplois[n]["verre"]      = c["seches_l"] - (double_biere if n == "Fût Affligem" else 0.0)
    emplois[n]["cocktails"]  = c["cocktails_l"]
    emplois[n]["chef"]       = (b.get("conso_staff_l") or {}).get("moyen", 0.0) or 0.0
    emplois[n]["stock"]      = b["stock_final_l"]
    emplois[n]["surversement"] = sv_par_nom.get(n, 0.0)
    emplois[n]["degustation"]  = deg.get(n, 0.0)
for n, _calc, plaf in CUISINE_PLAFONNE:
    emplois[n]["cuisine"] = plaf
emplois["Crémant du Jura"]["cremant"] = P["cremant"]
emplois["Fût Affligem"]["biere"]      = P["biere"]

achats = {n: idx[n]["achats_l"] - AVOIRS.get(n, 0.0) for n in noms}

# ---------------------------------------------------------------- controles
def ctrl(lib, calc, ref):
    ok = abs(calc - ref) < 0.02
    print("  %-30s %10.2f  ref %10.2f  %s" % (lib, calc, ref, "OK" if ok else "*** ECART"))
    return ok

print("CONTROLES POSTE PAR POSTE (somme par boisson vs cascade-10622.json)")
tot = lambda k: round(sum(e[k] for e in emplois.values()), 2)
ctrl("achats", round(sum(achats.values()), 2), CASCADE["achats_l"])
for k in ("verre", "cocktails", "cuisine", "cremant", "degustation", "biere", "chef", "stock"):
    ctrl(k, tot(k), P[k])
ctrl("surversement (ventilable)", tot("surversement"), P["surversement"] - sum(sv_hors_base.values()))
print("  sur-versement non ventilable :", {k: round(v, 2) for k, v in sv_hors_base.items()})
print("  offerts non ventilable       :", P["offerts"])
non_ventile = round(sum(sv_hors_base.values()) + P["offerts"], 2)

residu = {n: round(achats[n] - sum(emplois[n].values()), 2) for n in noms}
S = round(sum(residu.values()), 2)
print("\nSomme du residu par boisson        : %.2f L" % S)
print("Postes non ventilables par produit : %.2f L" % non_ventile)
print("Residu officiel (cascade)          : %.2f L" % CASCADE["residu_l"])
print("Controle : %.2f - %.2f = %.2f" % (S, non_ventile, round(S - non_ventile, 2)))

# --------------------------------------------------------------- familles
FAM = {"biere": "Bière", "vin_blanc": "Vin blanc", "vin_rouge": "Vin rouge",
       "vin_rose": "Rosé", "petillant": "Effervescent", "aperitif": "Apéritif",
       "liqueur": "Liqueur", "eau_de_vie": "Eau-de-vie", "spiritueux": "Spiritueux",
       "cidre": "Cidre", "vin": "Vin (couleur non précisée)",
       "vin_de_liqueur": "Vin de liqueur"}

rows = []
for n in noms:
    b = idx[n]
    rows.append(dict(nom=n, famille=FAM[b["categorie"]], achats=achats[n],
                     residu=residu[n], pa=b.get("prix_achat_l"), pv=b.get("prix_revente_l"),
                     pct=(100 * residu[n] / achats[n]) if achats[n] else None,
                     **{k: round(v, 2) for k, v in emplois[n].items()}))
rows.sort(key=lambda r: -r["residu"])

print("\nRESIDU PAR BOISSON (tri decroissant)")
print("%-46s %-24s %9s %9s %7s" % ("Boisson", "Famille", "Achats L", "Résidu L", "%ach"))
for r in rows:
    print("%-46s %-24s %9.2f %9.2f %7s" % (r["nom"], r["famille"], r["achats"], r["residu"],
          ("%.1f" % r["pct"]) if r["pct"] is not None else "n/a"))

print("\nPAR FAMILLE")
fam = collections.defaultdict(lambda: [0.0, 0.0, 0])
for r in rows:
    f = fam[r["famille"]]; f[0] += r["achats"]; f[1] += r["residu"]; f[2] += 1
print("%-26s %6s %10s %10s %8s %8s" % ("Famille", "n", "Achats L", "Résidu L", "%ach", "%résidu"))
for f, (a, rr, n_) in sorted(fam.items(), key=lambda x: -x[1][1]):
    print("%-26s %6d %10.2f %10.2f %7.1f%% %7.1f%%" % (f, n_, a, rr, 100*rr/a if a else 0, 100*rr/S))

print("\nCONCENTRATION")
pos = [r for r in rows if r["residu"] > 0]
neg = [r for r in rows if r["residu"] < 0]
sp = sum(r["residu"] for r in pos); sn = sum(r["residu"] for r in neg)
print("  %d boissons a residu positif : %.2f L ; %d a residu negatif : %.2f L"
      % (len(pos), sp, len(neg), sn))
for k in (1, 3, 5, 10, 20):
    print("  top %2d : %8.2f L = %5.1f %% du residu net (%5.1f %% du residu positif)"
          % (k, sum(r["residu"] for r in rows[:k]), 100*sum(r["residu"] for r in rows[:k])/S,
             100*sum(r["residu"] for r in rows[:k])/sp))
# Herfindahl sur les residus positifs
hhi = sum((r["residu"]/sp)**2 for r in pos)
print("  Herfindahl des residus positifs : %.4f (equivalent %.1f produits egaux)" % (hhi, 1/hhi))
print("  nb de boissons portant un residu >= 1 L : %d / %d"
      % (len([r for r in rows if r["residu"] >= 1]), len(rows)))

print("\nVALORISATION")
cout = sum(r["residu"] * (r["pa"] or 0) for r in rows)
cout_pos = sum(r["residu"] * (r["pa"] or 0) for r in pos)
sans_pa = [r["nom"] for r in rows if not r["pa"] and abs(r["residu"]) > 0.01]
print("  residu valorise au PRIX D'ACHAT           : %10.2f EUR" % cout)
print("  (residus positifs seuls)                   : %10.2f EUR" % cout_pos)
print("  boissons sans prix d'achat connu           :", sans_pa)
reve = sum(r["residu"] * r["pv"] for r in rows if r["pv"])
sans_pv = [(r["nom"], r["residu"]) for r in rows if not r["pv"] and abs(r["residu"]) > 0.01]
print("  residu valorise au prix de REVENTE (partiel, %d boissons sans prix): %10.2f EUR"
      % (len(sans_pv), reve))
print("  sans prix de revente :", [(n, round(v,1)) for n, v in sans_pv])
# prix moyen de revente pondere par les achats (meme convention que la cascade)
pm = CASCADE["prix_de_revente_eur_par_l"]["residu_moyenne_des_achats"]
print("  prix moyen de revente pondere par les achats (cascade) : %.2f EUR/L" % pm)
print("  residu total x ce prix moyen : %.2f EUR" % (CASCADE["residu_l"] * pm))

# ------------------------------------------------------- 353,2 L non rattaches
FACT = L("src/data/factures-fournisseur.json")
D0, D1 = datetime.date(2022, 4, 1), datetime.date(2025, 3, 31)
def bouteilles(cle):
    q = 0.0
    for f in FACT["factures"]:
        try:
            da = datetime.datetime.strptime(f.get("dateFacture") or "", "%d/%m/%Y").date()
        except ValueError:
            continue
        if not (D0 <= da <= D1):
            continue
        for l in f["lignes"]:
            des = (l.get("designation") or "").upper()
            if cle in des and "DECONSIGNE" not in des and "CARAMBAR" not in des:
                q += l.get("quantite") or 0
    return q
print("\n353,2 L D'ACHATS FACTURES NON RATTACHES (recompte depuis les factures FCBS)")
fa = {"Chablis": bouteilles("CHABLIS") * 0.75,
      "Gewurztraminer": bouteilles("GEWURZ") * 0.75,
      "Arbois Béthanie": bouteilles("BETHANIE 75") * 0.75 + bouteilles("BETHANIE 37,5") * 0.375}
tm = 0.0
for k, v in fa.items():
    m = v - idx[k]["achats_l"]
    tm += m
    print("  %-18s facture %7.2f L  bilan %7.2f L  manquant %7.2f L  (residu actuel %7.2f L)"
          % (k, v, idx[k]["achats_l"], m, residu[k]))
print("  TOTAL manquant : %.2f L" % tm)
print("  achats redresses : %.2f L ; residu redresse : %.2f L = %.2f %%"
      % (CASCADE["achats_l"] + tm, CASCADE["residu_l"] + tm,
         100 * (CASCADE["residu_l"] + tm) / (CASCADE["achats_l"] + tm)))

# ---------------------------------------- test decisif : CA et verres par jour
print("\nTEST DECISIF - si les %.2f L avaient ete vendus" % CASCADE["residu_l"])
# prix de revente moyen : 3 conventions
pv_ach = pm  # moyenne des prix de revente ponderee par les litres ACHETES (cascade)
# moyenne ponderee par le RESIDU lui-meme, sur les boissons qui ont un prix
num = sum(r["residu"] * r["pv"] for r in rows if r["pv"] and r["residu"] > 0)
den = sum(r["residu"] for r in rows if r["pv"] and r["residu"] > 0)
pv_res = num / den
print("  prix moyen pondere par les achats  : %.2f EUR/L" % pv_ach)
print("  prix moyen pondere par le residu+  : %.2f EUR/L (sur %.1f L couverts)" % (pv_res, den))
for lib, p in (("achats", pv_ach), ("résidu", pv_res)):
    ca = CASCADE["residu_l"] * p
    print("  -> %s : CA theorique %10.2f EUR = %.2f %% du CA declare (%.2f EUR/jour de service)"
          % (lib, ca, 100 * ca / CA_DECLARE, ca / JOURS_SERVICE))

# contenance moyenne d'un article vendu, lue dans boissonsHorsCocktail
tot_q = sum(x["total_quantite"] for x in HC)
tot_v = sum(x["total_volume_l"] for x in HC)
print("\n  CONTENANCE MOYENNE (src/data/calculsBoissons/boissonsHorsCocktail.json)")
print("  tous articles hors cocktails : %.0f articles, %.2f L -> %.2f cl/article"
      % (tot_q, tot_v, 100 * tot_v / tot_q))
alc_noms = set(noms)
hq = sum(x["total_quantite"] for x in HC if x["nom_canonique"] in alc_noms)
hv = sum(x["total_volume_l"] for x in HC if x["nom_canonique"] in alc_noms)
print("  articles alcoolises seuls    : %.0f articles, %.2f L -> %.2f cl/article"
      % (hq, hv, 100 * hv / hq))
# hors bouteilles et hors cubis : le verre unitaire
VERRE = [x for x in HC if x["nom_canonique"] in alc_noms
         and not any(s in x["format_service"].lower() for s in ("bouteille", "75cl", "cubi", "pichet", "magnum", "37"))]
vq = sum(x["total_quantite"] for x in VERRE); vv = sum(x["total_volume_l"] for x in VERRE)
print("  formats unitaires (ni bouteille ni pichet ni cubi) : %.0f articles, %.2f L -> %.2f cl"
      % (vq, vv, 100 * vv / vq))
print("  formats retenus :", sorted(set(x["format_service"] for x in VERRE)))
print()
for lib, cl in (("verre de vin 12 cl", 12.0), ("article moyen alcoolisé %.1f cl" % (100*hv/hq), 100*hv/hq),
                ("format unitaire moyen %.1f cl" % (100*vv/vq), 100*vv/vq),
                ("demi de bière 25 cl", 25.0)):
    n_art = CASCADE["residu_l"] * 100 / cl
    print("  %-38s -> %8.0f articles, soit %5.1f par jour de service" % (lib, n_art, n_art / JOURS_SERVICE))

# couverts / jour pour mise en perspective
print("\n  Pour memoire : %d jours de service." % JOURS_SERVICE)

# --------------------------------------------------------------- exports CSV
with open(os.path.join(OUT, "R1-residu-par-boisson.csv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["Boisson", "Famille", "Achats nets L", "Vendu au verre", "Cocktails",
                "Cuisine/menus", "Crémant", "Sur-versement", "Dégustation", "Freinte bière",
                "Chef", "Stock final", "Résidu L", "% des achats", "Prix achat EUR/L",
                "Coût du résidu EUR", "Prix revente EUR/L"])
    for r in rows:
        w.writerow([r["nom"], r["famille"], round(r["achats"], 2), r.get("verre", 0),
                    r.get("cocktails", 0), r.get("cuisine", 0), r.get("cremant", 0),
                    r.get("surversement", 0), r.get("degustation", 0), r.get("biere", 0),
                    r.get("chef", 0), r.get("stock", 0), r["residu"],
                    round(r["pct"], 1) if r["pct"] is not None else "",
                    r["pa"] or "", round(r["residu"] * (r["pa"] or 0), 2), r["pv"] or ""])
print("\necrit :", os.path.join(OUT, "R1-residu-par-boisson.csv"))
