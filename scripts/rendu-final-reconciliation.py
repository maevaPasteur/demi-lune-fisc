#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rendu-final-reconciliation.py
Pour chaque journée-type (échantillon déjà sélectionné), construit le croisement
demandé, SANS produit/table sur les suppressions (on relie par le TEMPS) :
  - D : journal des suppressions (D1, D2… : heure, montant).
  - tables : ventes regroupées par note (= table-addition) : T1, T2…, heure, total,
             lignes nommées A1, A2… (libellé, qté, prix, montant).
  - M : journal des modifications de prix (M1… : heure, article, prix vs prix de
        référence de la période, table concernée).
Puis on enrichit chaque table : nombre de suppressions attribuées (par proximité
horaire = juste avant la clôture de la table), les modifications de prix qui la
concernent, et si elle est PARTAGÉE (notes de même total/même minute, ou qtés 0,5).

Merge dans src/data/renduFinalCalculs.json (clé echantillon[*].reconciliation).
"""
import xlrd, json, os, collections, re

ICI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(ICI, ".."))
CAISSE = os.path.join(ROOT, "public/documents/caisse-enregistreuse/")
EXOS = ["2022-2023", "2023-2024", "2024-2025"]
C = {e: CAISSE + f"ANNEXE-C{i}_detail-tickets_{e}.xls" for i, e in enumerate(EXOS, 1)}
E = {e: CAISSE + f"ANNEXE-E{i}_tpvevenement_{e}.xls" for i, e in enumerate(EXOS, 1)}


def periode(d):
    return "C" if d < "2022-07-23" else ("B" if d < "2023-04-17" else "A")


def to_min(h):
    try:
        return int(h[:2]) * 60 + int(h[3:5])
    except Exception:
        return -1


# 1) Charger toutes les notes + construire les prix de référence par (libellé, période).
notes_par_jour = collections.defaultdict(lambda: collections.defaultdict(lambda: {"h": "99:99", "tot": 0.0, "lignes": []}))
prix_seen = collections.defaultdict(collections.Counter)
for ex in EXOS:
    sh = xlrd.open_workbook(C[ex]).sheet_by_index(0)
    for r in range(1, sh.nrows):
        d = str(sh.cell_value(r, 0))[:10]
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", d):
            continue
        no = str(sh.cell_value(r, 2)).replace(".0", "")
        h = str(sh.cell_value(r, 1))[:5]
        lib = str(sh.cell_value(r, 10)).strip()
        try:
            q = float(sh.cell_value(r, 11))
        except ValueError:
            q = 0
        try:
            pu = round(float(sh.cell_value(r, 13)), 2)
        except ValueError:
            pu = 0.0
        n = notes_par_jour[d][no]
        n["h"] = min(n["h"], h)
        try:
            n["tot"] = float(sh.cell_value(r, 5))
        except ValueError:
            pass
        if lib:
            n["lignes"].append({"lib": lib, "qte": q, "pu": pu})
            prix_seen[(lib, periode(d))][pu] += 1

REF = {k: set(p for p, n in c.items() if n >= 5 and p > 0) for k, c in prix_seen.items()}
# Ensemble de TOUS les prix d'articles vus (pour reconnaître « montant = prix d'1 article »).
ALLPRIX = set()
for c in prix_seen.values():
    for p, n in c.items():
        if p > 0:
            ALLPRIX.add(p)

# Statuts mutuellement exclusifs, déterminés par le MONTANT (fait) + coïncidence temporelle.
STATUTS = {
    "faute_frappe": "Faute de frappe — montant ≥ 1 000 €",
    "retrait_article": "Retrait d’un article — montant = prix exact d’un article",
    "partage_forfait": "Partage / forfait — montant composé, à la minute d’une table partagée ou d’un forfait",
    "a_expliquer": "À expliquer — montant composé, sans table partagée ni forfait à la même minute",
}


def dels_du_jour(date):
    ex = next(e for e in EXOS if date <= e[5:] + "-12-31" and date >= e[:4] + "-01-01") if False else None
    # déterminer l'exercice fiscal : avr N -> mars N+1
    y, m = int(date[:4]), int(date[5:7])
    base = y if m >= 4 else y - 1
    ex = f"{base}-{base+1}"
    sh = xlrd.open_workbook(E[ex]).sheet_by_index(0)
    out = []
    for r in range(1, sh.nrows):
        if str(sh.cell_value(r, 3)).strip() != "DEL":
            continue
        if str(sh.cell_value(r, 1))[:10] != date:
            continue
        try:
            mt = float(sh.cell_value(r, 8))
        except ValueError:
            mt = 0.0
        out.append({"heure": str(sh.cell_value(r, 2))[:5], "montant": round(mt, 2)})
    out.sort(key=lambda x: x["heure"])
    return out


def reconciliation(date):
    nts = notes_par_jour[date]
    per = periode(date)
    # tables triées par heure puis n°
    ordre = sorted(nts.keys(), key=lambda no: (nts[no]["h"], int(no) if no.isdigit() else 0))
    # twins : (heure, total) partagé par >=2 notes
    grp = collections.defaultdict(list)
    for no in ordre:
        grp[(nts[no]["h"], round(nts[no]["tot"], 2))].append(no)

    suppressions = [{"nom": f"D{i+1}", **d} for i, d in enumerate(dels_du_jour(date))]
    modifications = []
    tables = []
    a_counter = 0
    for ti, no in enumerate(ordre, 1):
        n = nts[no]
        lignes = []
        modifs_table = []
        for li in n["lignes"]:
            a_counter += 1
            nomA = f"A{a_counter}"
            ref = REF.get((li["lib"], per), set())
            modif = li["pu"] > 0 and li["qte"] > 0 and ref and li["pu"] not in ref
            lignes.append({"nom": nomA, "lib": li["lib"], "qte": round(li["qte"], 2),
                           "pu": li["pu"], "montant": round(li["pu"] * li["qte"], 2),
                           "modifie": bool(modif)})
            if modif:
                nomM = f"M{len(modifications)+1}"
                modifications.append({"nom": nomM, "heure": n["h"], "table": f"T{ti}",
                                      "article": li["lib"], "prix": li["pu"],
                                      "prix_ref": sorted(ref)[:3]})
                modifs_table.append(nomM)
        partagee = len(grp[(n["h"], round(n["tot"], 2))]) > 1 or \
            any(abs(li["qte"] - round(li["qte"])) > 0.01 for li in n["lignes"])
        jumelles = [f"T{ordre.index(x)+1}" for x in grp[(n["h"], round(n["tot"], 2))] if x != no]
        tables.append({"nom": f"T{ti}", "note": no, "heure": n["h"],
                       "total": round(n["tot"], 2), "partagee": partagee,
                       "jumelles": jumelles, "lignes": lignes,
                       "modifications": modifs_table, "suppressions": []})

    # Rattachement table le plus proche dans le TEMPS (hypothèse) + indice de confiance.
    for d in suppressions:
        dm = to_min(d["heure"])
        gaps = sorted((abs(to_min(t["heure"]) - dm), t["nom"], t) for t in tables)
        if gaps and gaps[0][0] <= 60:
            best = gaps[0][2]
            best["suppressions"].append(d["nom"])
            d["table"] = best["nom"]
            d["confiance"] = "ambigu" if len(gaps) > 1 and gaps[1][0] - gaps[0][0] <= 1 else "probable"
        else:
            d["table"] = None
            d["confiance"] = None
    for t in tables:
        t["nb_suppressions"] = len(t["suppressions"])

    # Heures des tables partagées / à forfait (pour la coïncidence des suppressions composées).
    pf_heures = [to_min(t["heure"]) for t in tables if t["partagee"] or t["modifications"]]

    def concomitantes(heure, win=2):
        hm = to_min(heure)
        return [d["nom"] for d in suppressions if abs(to_min(d["heure"]) - hm) <= win]

    # Événements justificatifs (chaînes explicites suppressions -> opération).
    evenements = []
    for t in tables:
        if t["modifications"]:
            ds = concomitantes(t["heure"])
            evenements.append({"type": "forfait", "tables": [t["nom"]], "total": t["total"],
                               "modifications": t["modifications"], "suppressions": ds,
                               "explication": f"{t['nom']} ({t['heure']}, {t['total']:.2f} €) facturée avec un prix modifié ({', '.join(t['modifications'])}) — passage à un forfait sans détail. Suppressions à la même minute : {', '.join(ds) or 'aucune'}."})
    vus = set()
    for (h, tot), nos in grp.items():
        if len(nos) > 1 and tot > 0:
            tn = sorted((f"T{ordre.index(x)+1}" for x in nos), key=lambda s: int(s[1:]))
            if tuple(tn) in vus:
                continue
            vus.add(tuple(tn))
            ds = concomitantes(h)
            evenements.append({"type": "partage", "tables": tn, "total": round(tot * len(nos), 2),
                               "modifications": [], "suppressions": ds,
                               "explication": f"Addition partagée sur {', '.join(tn)} ({h}, {round(tot, 2):.2f} € chacune) pour paiement séparé. Suppressions à la même minute : {', '.join(ds) or 'aucune'}."})
    evenements.sort(key=lambda e: e["explication"])

    # Statut de CHAQUE suppression (montant = fait ; coïncidence = hypothèse). 4 statuts exclusifs.
    def coincide(d):
        dm = to_min(d["heure"])
        return any(abs(dm - h) <= 2 for h in pf_heures)
    bilan = {k: {"n": 0, "somme": 0.0} for k in STATUTS}
    for d in suppressions:
        m = d["montant"]
        if m >= 1000:
            st = "faute_frappe"
        elif round(m, 2) in ALLPRIX:
            st = "retrait_article"
        elif coincide(d):
            st = "partage_forfait"
        else:
            st = "a_expliquer"
        d["statut"] = st
        bilan[st]["n"] += 1
        bilan[st]["somme"] += m
    for k in bilan:
        bilan[k]["somme"] = round(bilan[k]["somme"], 2)
    restantes = [d["nom"] for d in suppressions if d["statut"] == "a_expliquer"]
    total_somme = round(sum(d["montant"] for d in suppressions), 2)
    nb_partagees = sum(1 for t in tables if t["partagee"])

    return {"suppressions": suppressions, "modifications": modifications, "tables": tables,
            "evenements": evenements, "bilan_rattachement": bilan, "restantes": restantes,
            "total_somme": total_somme, "nb_tables_partagees": nb_partagees}


# 2) Merge dans le JSON
dest = os.path.join(ROOT, "src/data/renduFinalCalculs.json")
data = json.load(open(dest, encoding="utf-8"))
ech = data["paiements_fractionnes"]["echantillon"]
for j in ech:
    j["reconciliation"] = reconciliation(j["date"])
json.dump(data, open(dest, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

j0 = ech[0]
rc = j0["reconciliation"]
print(f"{j0['date']} : {len(rc['suppressions'])} suppressions (D), "
      f"{len(rc['tables'])} tables (T), {len(rc['modifications'])} modifications (M)")
ds_attr = sum(1 for d in rc["suppressions"] if d.get("table"))
print(f"  suppressions attribuées à une table (proximité) : {ds_attr}/{len(rc['suppressions'])}")
print(f"  tables partagées : {sum(1 for t in rc['tables'] if t['partagee'])} | "
      f"tables avec prix modifié : {sum(1 for t in rc['tables'] if t['modifications'])}")
ex = next((t for t in rc["tables"] if t["modifications"]), rc["tables"][0])
print(f"  ex table {ex['nom']} (n°{ex['note']}, {ex['heure']}, {ex['total']}€) : "
      f"{ex['nb_suppressions']} suppr {ex['suppressions']}, modifs {ex['modifications']}, partagée={ex['partagee']}")
