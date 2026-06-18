#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rendu-final-calculs.py
Consolide, depuis les annexes de caisse certifiées (A->H) et les recettes,
TOUS les chiffres utilisés par l'onglet "Rendu final" (réponse au fisc).
Sortie : src/data/renduFinalCalculs.json (importé par renduFinal.ts).
100 % reproductible, aucune valeur saisie à la main.

Sources annexes : public/documents/caisse-enregistreuse/ANNEXE-{C,E,F}{1,2,3}.xls
  C = détail tickets (date, no_ticket, lib, qté, prix) ; E = événements (DEL) ;
  F = règlements (mode + montant).
Recettes : src/data/calculsBoissons/{itemsCaisse,cocktailsComposition}.json
"""
import xlrd, json, math, collections, os

ICI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(ICI, ".."))
CAISSE = os.path.join(ROOT, "public/documents/caisse-enregistreuse/")
CALC = os.path.join(ROOT, "src/data/calculsBoissons/")
EXOS = ["2022-2023", "2023-2024", "2024-2025"]
C = {e: CAISSE + f"ANNEXE-C{i}_detail-tickets_{e}.xls" for i, e in enumerate(EXOS, 1)}
E = {e: CAISSE + f"ANNEXE-E{i}_tpvevenement_{e}.xls" for i, e in enumerate(EXOS, 1)}
F = {e: CAISSE + f"ANNEXE-F{i}_reglements_{e}.xls" for i, e in enumerate(EXOS, 1)}


def sheet(fn):
    return xlrd.open_workbook(fn).sheet_by_index(0)


# --------------------------------------------------------------------------- #
# 1. CRÉMANT JETÉ — reste de bouteille (75cl) jeté chaque jour (ne se garde pas)
#    Servi = verre 10cl + cocktails (Vouivre 8, Kittykir 9, Kir Princier 10).
#    Sur-versement +20 % (BMJ 2005) sur les versements à la main.
# --------------------------------------------------------------------------- #
CREMANT_POURS = {"Crémant": 10, "Crément / Jura VERRE": 10, "La Vouivre": 8,
                 "VOUIVRE": 8, "KITTYKIR": 9, "Kittykir": 9, "Kir Princier": 10}
BOTTLE = 75.0
OVERPOUR = 1.20


def cremant_jete(overpour):
    per = {}
    for ex, fn in C.items():
        sh = sheet(fn)
        day = collections.defaultdict(float)
        for r in range(1, sh.nrows):
            lib = str(sh.cell_value(r, 10)).strip()
            if lib in CREMANT_POURS:
                try:
                    q = float(sh.cell_value(r, 11))
                except ValueError:
                    q = 0
                if q > 0:
                    day[str(sh.cell_value(r, 0))[:10]] += q * CREMANT_POURS[lib] * overpour
        served = sum(day.values())
        bottles = sum(math.ceil(v / BOTTLE) for v in day.values() if v > 0)
        thrown = bottles * BOTTLE - served
        per[ex] = {"jours": sum(1 for v in day.values() if v > 0),
                   "servi_l": round(served / 100, 1),
                   "bouteilles": bottles,
                   "jete_l": round(thrown / 100, 1)}
    return per


# --------------------------------------------------------------------------- #
# 2. ABSINTHE (crème brûlée) — 8 cl / litre, 1 L = 7 parts -> 8/7 cl par part.
# --------------------------------------------------------------------------- #
def absinthe():
    n = 0.0
    for ex, fn in C.items():
        sh = sheet(fn)
        for r in range(1, sh.nrows):
            lib = str(sh.cell_value(r, 10)).strip().lower()
            if "brulee" in lib or "brûlée" in lib or "brulée" in lib or "brûlee" in lib:
                try:
                    q = float(sh.cell_value(r, 11))
                except ValueError:
                    q = 0
                if q > 0:
                    n += q
    return {"cremes_brulees": round(n), "absinthe_l": round(n * 8 / 7 / 100, 1)}


# --------------------------------------------------------------------------- #
# 3. DÉGUSTATION OFFERTE — 2 cl par note et par vin NOMMÉ servi au verre/pichet.
#    (génériques "vin/rosé" et bouteilles exclus ; 1 dégustation par note/vin.)
# --------------------------------------------------------------------------- #
TASTE = {
    "PICHET ALIGOTE 50cL": "Aligoté", "Verre ALIGOTE": "Aligoté",
    "Pichet CHUSLAN": "Chusclan", "Pichet CdR CHUSCLAN": "Chusclan",
    "VERRE CHUSCLAN": "Chusclan", "Verre CHUSCLAN": "Chusclan",
    "Arbois Chardonnay Le": "Arbois Chardonnay",
    "Chablis Le Verre": "Chablis", "Pichet Chablis": "Chablis",
    "Gewurztraminer Le ve": "Gewurztraminer", "PICHET GEWURZTRAMINE": "Gewurztraminer",
    "MACON VERRE": "Mâcon", "PICHET MACON": "Mâcon",
    "Saint Véran Verre": "Saint Véran", "PICHET SAINT VERAN": "Saint Véran",
    "Savagnin verre": "Savagnin", "PICHET SAVAGNIN": "Savagnin",
    "Arbois Trousseau Le": "Arbois Trousseau", "PiCHET TROUSSEAU": "Arbois Trousseau",
    "H.C.DE BEAUNE  VERRE": "HC de Beaune", "VERRE H.C.DE BEAUNE": "HC de Beaune",
    "PICHET C.DE BEAUNE R": "HC de Beaune", "PICHET C.DE BEAUNE B": "HC de Beaune",
    "PICHET HCB": "HC de Beaune", "PICHET MOULIN A VENT": "Moulin à Vent",
    "pichet Saint Joseph": "Saint Joseph",
}
DOSE_DEG = 2.0


def degustation():
    per = {}
    wine = collections.Counter()
    for ex, fn in C.items():
        sh = sheet(fn)
        combos = set()
        for r in range(1, sh.nrows):
            lib = str(sh.cell_value(r, 10)).strip()
            if lib in TASTE:
                try:
                    q = float(sh.cell_value(r, 11))
                except ValueError:
                    q = 0
                if q > 0:
                    combos.add((str(sh.cell_value(r, 0))[:10], str(sh.cell_value(r, 2)), TASTE[lib]))
        per[ex] = {"degustations": len(combos), "offert_l": round(len(combos) * DOSE_DEG / 100, 1)}
        for (_, _, w) in combos:
            wine[w] += 1
    return per, {w: {"degustations": n, "offert_l": round(n * DOSE_DEG / 100, 1)}
                 for w, n in wine.most_common()}


# --------------------------------------------------------------------------- #
# 4. MENUS À PRIX PERSONNALISÉ (hors catalogue) = factures sans détail.
# --------------------------------------------------------------------------- #
def menus_custom():
    m = json.load(open(os.path.join(CALC, "menusVentesParPrix.json"), encoding="utf-8"))
    g = {"oui_q": 0.0, "oui_eur": 0.0, "tot_q": 0.0}
    par = {}
    for pd in m["periodes"].values():
        for menu, md in pd.get("menus", {}).items():
            for l in md.get("lignes", []):
                q = l.get("quantite", 0) or 0
                prix = l.get("prix", 0) or 0
                mod = str(l.get("prix_modifie", "")).upper() == "OUI"
                d = par.setdefault(menu, {"oui_q": 0.0, "oui_eur": 0.0, "tot_q": 0.0})
                g["tot_q"] += q
                d["tot_q"] += q
                if mod:
                    g["oui_q"] += q
                    g["oui_eur"] += q * prix
                    d["oui_q"] += q
                    d["oui_eur"] += q * prix
    par = {k: {"custom_q": round(v["oui_q"]), "total_q": round(v["tot_q"]),
               "custom_eur": round(v["oui_eur"]),
               "pct": round(100 * v["oui_q"] / v["tot_q"], 1) if v["tot_q"] else 0}
           for k, v in par.items() if v["oui_q"] > 0}
    return {"custom_q": round(g["oui_q"]), "total_q": round(g["tot_q"]),
            "custom_eur": round(g["oui_eur"]),
            "pct": round(100 * g["oui_q"] / g["tot_q"], 1),
            "par_menu": dict(sorted(par.items(), key=lambda x: -x[1]["custom_q"]))}


# --------------------------------------------------------------------------- #
# 5. BANCARISATION (F) par mode + taux de paiements fractionnés (note multi-règlements)
# --------------------------------------------------------------------------- #
def bancarisation():
    montant = collections.defaultdict(float)
    nb = collections.Counter()
    tickets = collections.defaultdict(int)
    tot = 0.0
    for ex, fn in F.items():
        sh = sheet(fn)
        for r in range(1, sh.nrows):
            mod = str(sh.cell_value(r, 9)).strip()
            if not mod:
                continue
            try:
                mt = float(sh.cell_value(r, 10))
            except ValueError:
                mt = 0
            montant[mod] += mt
            nb[mod] += 1
            tot += mt
            key = (ex, str(sh.cell_value(r, 0))[:10], str(sh.cell_value(r, 2)), str(sh.cell_value(r, 4)))
            tickets[key] += 1
    modes = {mod: {"reglements": nb[mod], "pct": round(100 * montant[mod] / tot, 2)}
             for mod in montant}
    multi = sum(1 for v in tickets.values() if v > 1)
    banc = sum(montant[m] for m in montant if m.upper() != "ESP")
    return {"par_mode": dict(sorted(modes.items(), key=lambda x: -x[1]["pct"])),
            "bancarise_pct": round(100 * banc / tot, 2),
            "especes_pct": round(100 * montant.get("ESP", 0) / tot, 2),
            "notes_total": len(tickets), "notes_fractionnees": multi,
            "notes_fractionnees_pct": round(100 * multi / len(tickets), 1)}


# --------------------------------------------------------------------------- #
# 6. GROSSES SUPPRESSIONS (E) — décomposition prix x quantité contre le catalogue.
# --------------------------------------------------------------------------- #
def aberrations():
    it = json.load(open(os.path.join(CALC, "itemsCaisse.json"), encoding="utf-8"))
    prix = []
    for p in it["items"]:
        for ex, pu in (p.get("prix_unitaire") or {}).items():
            if pu and pu > 0:
                prix.append((p["produit"], round(pu, 2)))
    # plus grosses DEL (on EXCLUT les lignes de synthèse "Nb lignes" / sous-totaux :
    # seules les vraies suppressions datées YYYY-MM-DD sont retenues)
    import re
    dels = []
    for ex, fn in E.items():
        sh = sheet(fn)
        for r in range(1, sh.nrows):
            if str(sh.cell_value(r, 3)).strip() == "DEL":
                date = str(sh.cell_value(r, 1))[:10]
                if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
                    continue  # ligne de total/synthèse, pas une suppression réelle
                try:
                    amt = float(sh.cell_value(r, 8))
                except ValueError:
                    amt = 0
                dels.append({"exercice": ex, "date": date,
                             "heure": str(sh.cell_value(r, 2)), "montant": round(amt, 2)})
    dels.sort(key=lambda d: -d["montant"])
    top = dels[:4]
    for d in top:
        cands = []
        for nom, pu in prix:
            q = d["montant"] / pu
            if abs(q - round(q)) < 0.02 and round(q) >= 50:
                cands.append({"produit": nom, "prix": pu, "quantite": round(q)})
        # dédoublonne par (prix,quantité)
        seen = set()
        uniq = []
        for c in cands:
            k = (c["prix"], c["quantite"])
            if k not in seen:
                seen.add(k)
                uniq.append(c)
        uniq.sort(key=lambda c: -c["prix"])
        d["decomposition"] = uniq[:4]
    amts = [d["montant"] for d in dels]
    compte = {
        "total": len(dels),
        "somme": round(sum(amts)),
        "sup_1000": sum(1 for m in amts if m >= 1000),
        "sup_500": sum(1 for m in amts if m >= 500),
        "sup_200": sum(1 for m in amts if m >= 200),
        "sup_50": sum(1 for m in amts if m >= 50),
        "mediane": round(sorted(amts)[len(amts) // 2], 2) if amts else 0,
    }
    return {"top": top, "compte": compte}


# --------------------------------------------------------------------------- #
out = {
    "_source": "scripts/rendu-final-calculs.py — recalcul depuis annexes caisse A->H",
    "cremant_jete": {
        "avec_surversement_20": cremant_jete(OVERPOUR),
        "nominal": cremant_jete(1.0),
        "bouteille_cl": BOTTLE,
    },
    "absinthe": absinthe(),
    "degustation": dict(zip(("par_exercice", "par_vin"), degustation())),
    "degustation_dose_cl": DOSE_DEG,
    "menus_custom": menus_custom(),
    "bancarisation": bancarisation(),
    "aberrations": aberrations(),
}


def somme(d, key):
    return round(sum(v[key] for v in d.values()), 1)


cj = out["cremant_jete"]["avec_surversement_20"]
out["cremant_jete"]["total_jete_l"] = somme(cj, "jete_l")
out["cremant_jete"]["total_servi_l"] = somme(cj, "servi_l")
out["cremant_jete"]["total_bouteilles"] = sum(v["bouteilles"] for v in cj.values())
out["degustation"]["total_offert_l"] = somme(out["degustation"]["par_exercice"], "offert_l")
out["degustation"]["total_degustations"] = sum(v["degustations"] for v in out["degustation"]["par_exercice"].values())

dest = os.path.join(ROOT, "src/data/renduFinalCalculs.json")
json.dump(out, open(dest, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("écrit:", dest)
print("crémant jeté 3 ans:", out["cremant_jete"]["total_jete_l"], "L")
print("absinthe:", out["absinthe"])
print("dégustation:", out["degustation"]["total_offert_l"], "L")
print("menus custom:", out["menus_custom"]["custom_q"], "=", out["menus_custom"]["custom_eur"], "€")
print("bancarisé:", out["bancarisation"]["bancarise_pct"], "% / espèces", out["bancarisation"]["especes_pct"], "%")
print("notes fractionnées:", out["bancarisation"]["notes_fractionnees_pct"], "%")
