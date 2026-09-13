#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
R1 - Alcool de cuisine : ENCADREMENT des doses, alcool par alcool.

Produit public/documents/pieces-reponse-1/R1-alcool-cuisine-encadrement.xlsx :
  1. La colonne « volume disponible » du service reconstituee (achats FCBS + variation de stock)
  2. Encadrement de la dose de cuisine, alcool par alcool (borne basse culinaire / dose retenue /
     borne haute = seuil au-dela duquel le stock ne suit plus)
  3. Bilan matiere par alcool (achats, stock, verre, cocktails, cuisine, residu)
  4. Volume physiquement parti en cuisine (poste de la cascade) et supplement demande au service :
     deux grandeurs distinctes, etablies separement
  5. Achats factures des alcools secondaires, exercice par exercice, contre les volumes retenus p. 69-70

Sources (lecture seule) :
  src/data/calculsBoissons/itemsCaisse.json               quantites vendues par libelle (annexes de caisse)
  public/documents/vins-boissons/_pipeline_conso_alcool.py mapping libelle -> (alcool, dose)
  src/data/calculsBoissons/consoAlcoolMenus.json          alcool des plats des menus par exercice
  src/data/calculsBoissons/consoTotaleParBoisson.json     achats FCBS, verre, cocktails, inventaires
  src/data/factures-fournisseur.json                      factures FCBS (achats par code article)
  Proposition de rectifications, annexe n° 1, p. 49 et 50 : stocks au 31/03/2022 a 2025 et
     contenances retenues par le service (releves sur l'image, valeurs ci-dessous)
  Reponse DDFiP du 04/09/2026, p. 65 a 67 : colonne « Volume Disponible (en centilitres) »
"""
import ast, json, os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/"
JS = BASE + "src/data/calculsBoissons/"
OUT = BASE + "public/documents/pieces-reponse-1/"
EXOS = ["2022-2023", "2023-2024", "2024-2025"]
LAB = {"2022-2023": "Exercice 1", "2023-2024": "Exercice 2", "2024-2025": "Exercice 3"}
J = lambda n: json.load(open(JS + n, encoding="utf-8"))

# ---------------------------------------------------------------------------
# 1. Colonne « Volume Disponible » imprimee par le service (cl), p. 65 a 67
# ---------------------------------------------------------------------------
DISPO_SERVICE = {
    "Calvados":         {"2022-2023": 3100,  "2023-2024": 2200,  "2024-2025": 2000},
    "Arbois Vin Jaune": {"2022-2023": 7409,  "2023-2024": 6758,  "2024-2025": 7874},
    "Porto":            {"2022-2023": 2730,  "2023-2024": 4760,  "2024-2025": 4480},
    "Macvin":           {"2022-2023": 24000, "2023-2024": 28350, "2024-2025": 27150},
}

# Stocks et contenances de l'annexe n° 1 de la proposition (p. 49 et 50), en unites.
# (contenance_cl, stock 31/03/2022, 2023, 2024, 2025) ; None = case laissee vide par le service.
ANNEXE1 = {
    "Calvados":         (100.0, 1.0, 2.0, 2.0, 1.0),
    "Arbois Vin Jaune": (62.0, 1.5, 4.0, 2.0, 2.0),
    "Porto":            (70.0, 1.0, 4.0, 4.0, 2.0),
    "Macvin":           (75.0, 5.0, 5.0, 9.0, 13.0),
    "Grand Marnier":    (70.0, 1.0, 2.0, 1.0, 2.0),
}
# Achats FCBS par exercice, en bouteilles, pour la reconstitution de la colonne (voir plus bas :
# recalcules depuis src/data/factures-fournisseur.json, par code article).
CODES = {
    "Calvados":         ["510113"],
    "Arbois Vin Jaune": None,   # plusieurs codes : filtre par designation
    "Porto":            None,
    "Macvin":           None,
    "Ravelin BIB":      ["600731"],
    "Ravelin 99 cl":    ["600933"],
    "Ravelin 75 cl":    ["600867"],
    "Bailey's":         ["510133"],
    "Marc de Bourgogne": ["550252"],
    "Marc du Jura":     ["520096"],
    "Liqueur de Poire": ["591050"],
    "Grand Marnier":    ["510090"],
}

# ---------------------------------------------------------------------------
# 2. Achats FCBS facture par facture (par code ou par motif de designation)
# ---------------------------------------------------------------------------
FACT = json.load(open(BASE + "src/data/factures-fournisseur.json", encoding="utf-8"))["factures"]


def periode(df):
    j, m, a = df.split("/")
    iso = f"{a}-{m}-{j}"
    if iso < "2022-04-01":
        return None
    if iso <= "2023-03-31":
        return "2022-2023"
    if iso <= "2024-03-31":
        return "2023-2024"
    if iso <= "2025-03-31":
        return "2024-2025"
    return None


def achats(codes=None, motif=None, exclure=None):
    """Unites facturees par exercice (avoirs deduits, lignes non livrees exclues)."""
    q = {e: 0.0 for e in EXOS}
    lignes = []
    for f in FACT:
        p = periode(f["dateFacture"])
        if not p:
            continue
        for ln in f.get("lignes", []):
            if ln.get("montantHT") is None:
                continue
            des = (ln.get("designation") or "").upper()
            code = str(ln.get("code") or "")
            ok = (codes and code in codes) or (motif and all(m in des for m in motif))
            if ok and exclure and any(x in des for x in exclure):
                ok = False
            if ok:
                q[p] += ln.get("quantite") or 0
                lignes.append((p, f["dateFacture"], f.get("numero"), code,
                               ln.get("designation"), ln.get("quantite"), ln.get("montantHT")))
    return q, lignes


ACHATS_UNITES = {
    "Calvados":         (achats(motif=["CALVADOS"]), 100.0),
    "Arbois Vin Jaune": (achats(motif=["VIN JAUNE"]), 62.0),
    "Porto":            (achats(motif=["PORTO"]), 75.0),
    "Macvin":           (achats(motif=["MACVIN"]), 75.0),
    "Bailey's":         (achats(codes=["510133"]), 70.0),
    "Marc de Bourgogne": (achats(codes=["550252"]), 70.0),
    "Marc du Jura":     (achats(motif=["MARC DU JURA"]), 70.0),
    "Liqueur de Poire": (achats(codes=["591050"]), 70.0),
    "Grand Marnier":    (achats(codes=["510090"]), 70.0),
    "Ravelin BIB 10 L": (achats(codes=["600731"]), 1000.0),
    "Ravelin 99 cl":    (achats(codes=["600933"]), 99.0),
    "Ravelin 75 cl":    (achats(codes=["600867"]), 75.0),
}

# ---------------------------------------------------------------------------
# 3. Cuisine : plats vendus x dose des dirigeants (carte) + plats des menus
# ---------------------------------------------------------------------------
src = open(BASE + "public/documents/vins-boissons/_pipeline_conso_alcool.py", encoding="utf-8").read()
FOOD = None
for node in ast.parse(src).body:
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "FOOD":
        FOOD = ast.literal_eval(node.value)
assert FOOD, "FOOD introuvable"

items = {}
for it in J("itemsCaisse.json")["items"]:
    d = items.setdefault(it["produit"], {e: 0.0 for e in EXOS})
    for e in EXOS:
        d[e] += it["quantite"].get(e, 0.0)

ALIAS = {"Vin jaune": "Arbois Vin Jaune", "Crème de cassis": "Crème de Cassis",
         "Baileys": "Bailey's", "Marc de bourgogne": "Marc de Bourgogne",
         "Liqueur de poire": "Liqueur de Poire"}

carte = {}        # alcool -> {exo: cl}
portions = {}     # alcool -> dose -> {exo: nb portions}
detail = []
for libelle, doses in FOOD.items():
    q = items.get(libelle)
    if not q:
        continue
    for (alc, dose, _flag) in doses:
        parts = [(alc, 1.0)]
        if alc == "Grand Marnier ou Calvados":
            parts = [("Grand Marnier", 0.5), ("Calvados", 0.5)]
        for (a, coef) in parts:
            a = ALIAS.get(a, a)
            vol = {e: q[e] * dose * coef for e in EXOS}
            d = carte.setdefault(a, {e: 0.0 for e in EXOS})
            n = portions.setdefault(a, {}).setdefault(dose, {e: 0.0 for e in EXOS})
            for e in EXOS:
                d[e] += vol[e]
                n[e] += q[e] * coef
            detail.append({"libelle": libelle, "alcool": a, "dose": dose, "coef": coef,
                           "qte": q, "vol": vol})

menus = {}
cam = J("consoAlcoolMenus.json")
for e in EXOS:
    for a in cam["exercices"][e]["alcools"]:
        nom = ALIAS.get(a["alcool"], a["alcool"])
        menus.setdefault(nom, {x: 0.0 for x in EXOS})[e] += a["cl_moyen"]

# ---------------------------------------------------------------------------
# 4. Achats, verre, cocktails, inventaires (cumul deja consolide du dossier)
# ---------------------------------------------------------------------------
achats_l, verre, cocktails, inv_fin, taille = {}, {}, {}, {}, {}
for b in J("consoTotaleParBoisson.json")["boissons"]:
    n = b["nom_canonique"]
    al = b.get("achats_litres_par_periode") or {}
    if al:
        achats_l[n] = {e: al.get(e, 0.0) * 100 for e in EXOS}
    verre[n] = {e: b["par_periode"][e]["detail_exact_l"]["boissons_seches"] * 100 for e in EXOS}
    cocktails[n] = {e: b["par_periode"][e]["detail_exact_l"]["ingredients_cocktails"] * 100 for e in EXOS}
    taille[n] = b.get("taille_achat_cl") or 0
    inv = b.get("inventaire_fin_contenants_par_periode") or {}
    inv_fin[n] = {e: inv.get(e, 0.0) * taille[n] for e in EXOS}

# ---------------------------------------------------------------------------
# 5. Volumes que le service dit avoir deja retranches (cl), p. 65 a 69
# ---------------------------------------------------------------------------
DEJA = {
    "Calvados":         {"2022-2023": 3310, "2023-2024": 3002, "2024-2025": 3005},   # repere D
    "Arbois Vin Jaune": {"2022-2023": 3717, "2023-2024": 3693, "2024-2025": 3748},   # repere E
    "Porto":            {"2022-2023": 398,  "2023-2024": 583,  "2024-2025": 556},    # repere G
    "Macvin":           {"2022-2023": 7774, "2023-2024": 8832, "2024-2025": 7406},   # repere Q
    "Crème de Cassis":  {"2022-2023": 1064, "2023-2024": 1132, "2024-2025": 1132},   # part desserts, p. 69
    "Ravelin":          {"2022-2023": 0,    "2023-2024": 16257, "2024-2025": 15554}, # part cuisine des BIB, p. 69
}

# Correction : le rapprochement automatique du dossier n'avait pas rattache la ligne
# « LIQUEUR GOLDEN EIGHT 70 CL 25° » du 15/03/2024 (designation tronquee sur la facture n° 508974).
# Achats relus par code article 591050 : 2, 12 puis 11 bouteilles de 70 cl.
achats_l["Liqueur de Poire"] = {e: ACHATS_UNITES["Liqueur de Poire"][0][0][e] * 70.0 for e in EXOS}

# Correction : la ligne « Marc de Bourgogne » du cumul du dossier portait 980 cl, qui est
# un total de famille. Elle additionnait deux produits distincts, le marc de Bourgogne
# Jacoulot 45° (code article 550252, 4 bouteilles de 70 cl, 280 cl) et le marc du Jura
# Tissot 50° (code article 520096, 10 bouteilles, 700 cl). Seul le premier est en cause
# ici ; le second est vendu au verre. Achats relus par code article.
achats_l["Marc de Bourgogne"] = {e: ACHATS_UNITES["Marc de Bourgogne"][0][0][e] * 70.0 for e in EXOS}

# Plafonds retenus sur les trois exercices pris ensemble (cl). Le marc de Bourgogne n'est
# pas plafonne aux 280 cl factures mais aux 210 cl effectivement sortis du stock (280 cl
# achetes moins la bouteille inventoriee au 31/03/2025) : nous ne savons pas lequel des
# deux marcs entre dans le baba, et nous ne demandons donc rien au-dela de ce que le stock
# de marc de Bourgogne a pu fournir. La colonne « cuisine calculee » n'en est pas modifiee.
PLAFOND_3ANS = {"Marc de Bourgogne": 210.0}

ALCOOLS = ["Ravelin", "Macvin", "Arbois Vin Jaune", "Calvados", "Porto", "Crème de Cassis",
           "Bailey's", "Grand Marnier", "Marc de Bourgogne", "Liqueur de Poire"]

# ---------------------------------------------------------------------------
# 6. Deux grandeurs distinctes
#    A. volume physiquement parti en cuisine : plats x dose, plafonne exercice par exercice
#       au PLUS FAIBLE des deux volumes opposables (achats factures FCBS ; volume disponible
#       imprime par le service quand il existe)
#    B. supplement demande au service : A moins ce qu'il retranche deja, plancher a zero
# ---------------------------------------------------------------------------
lignes_solde = []
for a in ALCOOLS:
    c = carte.get(a, {e: 0.0 for e in EXOS})
    m = menus.get(a, {e: 0.0 for e in EXOS})
    ac = achats_l.get(a, {e: 0.0 for e in EXOS})
    ds = DISPO_SERVICE.get(a)
    calc = {e: c[e] + m[e] for e in EXOS}
    plafond = {e: ac[e] for e in EXOS}                       # regle retenue : achats factures FCBS
    plaf_svc = {e: ds[e] for e in EXOS} if ds else dict(ac)   # variante : colonne du service
    if a in PLAFOND_3ANS:
        # plafond global aux trois exercices : impute dans l'ordre des exercices
        reste_plaf = PLAFOND_3ANS[a]
        phys = {}
        for e in EXOS:
            phys[e] = min(calc[e], reste_plaf)
            reste_plaf -= phys[e]
    else:
        phys = {e: min(calc[e], plafond[e]) for e in EXOS}
    dj = DEJA.get(a, {e: 0.0 for e in EXOS})
    sup = {e: max(0.0, phys[e] - dj[e]) for e in EXOS}
    phys_svc = {e: min(calc[e], plaf_svc[e]) for e in EXOS}
    phys_min = {e: min(calc[e], plafond[e], plaf_svc[e]) for e in EXOS}
    if a in PLAFOND_3ANS:   # le plafond global prime sur les deux variantes
        phys_svc = dict(phys)
        phys_min = dict(phys)
    lignes_solde.append({"alcool": a, "carte": c, "menus": m, "calc": calc, "achats": ac,
                         "dispo": ds, "plafond": plafond, "phys": phys, "deja": dj, "sup": sup,
                         "phys_svc": phys_svc, "phys_min": phys_min})

TOT_PHYS = sum(sum(x["phys"].values()) for x in lignes_solde)
TOT_SUP = sum(sum(x["sup"].values()) for x in lignes_solde)
TOT_CALC = sum(sum(x["calc"].values()) for x in lignes_solde)

# ---------------------------------------------------------------------------
# 7. Encadrement : dose maximale compatible avec le volume disponible
# ---------------------------------------------------------------------------
# borne basse : reference culinaire publiee (renseignee alcool par alcool, cf. sources de la page)
BORNE_BASSE = {}   # rempli plus bas


def k_max(a):
    """Coefficient maximal applicable au jeu de doses des dirigeants avant que le stock ne suive plus."""
    x = next(z for z in lignes_solde if z["alcool"] == a)
    dispo = sum(x["dispo"].values()) if x["dispo"] else sum(x["achats"].values())
    dehors = sum(verre.get(a, {e: 0 for e in EXOS}).values()) + sum(cocktails.get(a, {e: 0 for e in EXOS}).values())
    if x["dispo"]:   # la colonne du service integre deja la variation de stock
        reste = dispo - dehors
    else:
        reste = dispo - dehors - inv_fin.get(a, {e: 0 for e in EXOS})[EXOS[-1]]
    calc = sum(x["calc"].values())
    return (reste / calc) if calc else 0.0, reste, dispo, dehors, calc



# ---------------------------------------------------------------------------
# 8. Ecriture du classeur
# ---------------------------------------------------------------------------
HEAD = PatternFill("solid", fgColor="1F4E78")
HF = Font(bold=True, color="FFFFFF", size=10)
BAD = PatternFill("solid", fgColor="FCE4E4")
OK = PatternFill("solid", fgColor="E4F3E8")
thin = Side("thin", color="BFBFBF")
B = Border(thin, thin, thin, thin)


def sheet(wb, title, titre, cols, widths, first=False):
    ws = wb.active if first else wb.create_sheet()
    ws.title = title
    ws.cell(1, 1, titre).font = Font(bold=True, size=12)
    for j, h in enumerate(cols, 1):
        c = ws.cell(3, j, h)
        c.fill = HEAD; c.font = HF; c.border = B
        c.alignment = Alignment("center", "center", wrap_text=True)
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[ws.cell(1, i).column_letter].width = w
    ws.freeze_panes = "A4"
    return ws


def put(ws, r, vals, fmts=None, fill=None, bold=False):
    for j, v in enumerate(vals, 1):
        c = ws.cell(r, j, v)
        c.border = B
        if bold:
            c.font = Font(bold=True)
        if fmts and j - 1 < len(fmts) and fmts[j - 1]:
            c.number_format = fmts[j - 1]
        if fill and fill(j):
            c.fill = fill(j)


def main():
    wb = Workbook()

    # --- 1. colonne « volume disponible » reconstituee -----------------------
    ws = sheet(wb, "1-Volume disponible", "1. La colonne « Volume Disponible » du service (p. 65 a 67), reconstituee : achats FCBS + variation de stock (annexe n° 1, p. 49 et 50)",
               ["Alcool", "Exercice", "Achats FCBS (unites)", "Contenance retenue (cl)",
                "Stock d ouverture (unites)", "Stock de cloture (unites)",
                "Unites disponibles", "Volume disponible recalcule (cl)",
                "Volume disponible imprime (cl)", "Ecart (cl)"],
               [20, 12, 14, 13, 14, 14, 13, 16, 16, 11], first=True)
    r = 4
    idx = {"2022-2023": (1, 2), "2023-2024": (2, 3), "2024-2025": (3, 4)}
    for a in ["Calvados", "Arbois Vin Jaune", "Porto", "Macvin"]:
        cont, *stk = ANNEXE1[a]
        (q, _l), c_fact = ACHATS_UNITES[a]
        for e in EXOS:
            i0, i1 = idx[e]
            u = q[e] + stk[i0 - 1] - stk[i1 - 1]
            rec = u * cont
            imp = DISPO_SERVICE[a][e]
            put(ws, r, [a, LAB[e], q[e], cont, stk[i0 - 1], stk[i1 - 1], u, round(rec), imp, round(rec - imp)],
                [None, None, "#,##0.0", "#,##0", "#,##0.0", "#,##0.0", "#,##0.0", "#,##0", "#,##0", "#,##0"],
                fill=(lambda j: OK if j == 10 else None) if abs(rec - imp) < 1 else (lambda j: BAD if j == 10 else None))
            r += 1
    ws.cell(r + 1, 1, "Formule revendiquee par le service lui-meme, p. 74 de la meme reponse : « Le volume disponible = achats + variation de stock (compte 310200) ».")
    ws.cell(r + 2, 1, "Achats = factures Franche-Comte Boissons Services uniquement ; les achats Intermarche, second fournisseur cite par la proposition, ne sont pas ventiles pour les spiritueux.")
    ws.cell(r + 3, 1, "Porto : le service convertit a 70 cl la bouteille, alors que les 173 bouteilles facturees sont toutes des 75 cl.")

    # --- 2. encadrement des doses -------------------------------------------
    ws = sheet(wb, "2-Encadrement doses", "2. Encadrement de la dose de cuisine, alcool par alcool : la dose retenue est-elle materiellement possible ?",
               ["Alcool", "Preparation et dose retenue (dirigeants, reprise par le service)",
                "Volume disponible 3 exercices (cl)", "Sorti autrement (verre, cocktails) (cl)",
                "Reste pour la cuisine (cl)", "Cuisine calculee aux doses retenues (cl)",
                "Coefficient maximal admissible", "Dose plafond correspondante (cl)",
                "La dose retenue tient-elle ?"],
               [20, 34, 16, 16, 15, 17, 13, 14, 16])
    r = 4
    for x in lignes_solde:
        a = x["alcool"]
        k, reste, dispo, dehors, calc = k_max(a)
        ds = sorted(portions.get(a, {}), reverse=True)
        lib = " ; ".join(f"{d:g} cl" for d in ds) if ds else "4 cl (desserts des menus)"
        dmax = " / ".join(f"{d * k:.2f}" for d in ds) if ds else f"{4 * k:.2f}"
        put(ws, r, [a, lib, round(dispo), round(dehors), round(reste), round(calc), round(k, 2), dmax,
                    "oui" if k >= 1 else "non : plafonnee aux achats"],
            [None, None, "#,##0", "#,##0", "#,##0", "#,##0", "0.00", None, None],
            fill=(lambda j: OK if j == 9 else None) if k >= 1 else (lambda j: BAD if j == 9 else None))
        r += 1
    ws.cell(r + 1, 1, "Coefficient maximal = (volume disponible - volume sorti autrement) / volume de cuisine calcule aux doses retenues. Au-dela, le stock ne suit plus.")
    ws.cell(r + 2, 1, "Volume disponible : colonne du service (p. 65 a 67) pour le Calvados, le vin jaune, le porto et le macvin ; achats factures FCBS pour les six autres.")
    ws.cell(r + 3, 1, "Marc de Bourgogne : 280 cl, soit les 4 bouteilles du code article 550252 (Jacoulot 45 degres). Les 980 cl du cumul du dossier etaient un total de famille : ils y ajoutaient 700 cl de marc du Jura Tissot 50 degres (code 520096, 10 bouteilles), qui est un autre produit, vendu au verre.")
    ws.cell(r + 4, 1, "Liqueur de Poire : 1 750 cl, soit les 25 bouteilles du code article 591050, la ligne du 15/03/2024 (facture n. 508974) portant une designation tronquee que le rapprochement par libelle avait perdue.")

    # --- 3. bilan matiere ----------------------------------------------------
    ws = sheet(wb, "3-Bilan matiere", "3. Bilan matiere par alcool et par exercice (centilitres)",
               ["Alcool", "Exercice", "Achats factures FCBS", "Volume disponible du service",
                "Vendu au verre (caisse)", "Cocktails (caisse)", "Cuisine a la carte",
                "Cuisine dans les menus", "Total cuisine", "Reste"],
               [20, 12, 15, 16, 14, 13, 14, 15, 13, 12])
    r = 4
    for x in lignes_solde:
        a = x["alcool"]
        for e in EXOS:
            dsp = x["dispo"][e] if x["dispo"] else x["achats"][e]
            v = verre.get(a, {e: 0})[e]; ck = cocktails.get(a, {e: 0})[e]
            put(ws, r, [a, LAB[e], round(x["achats"][e]), round(dsp), round(v), round(ck),
                        round(x["carte"][e]), round(x["menus"][e]), round(x["calc"][e]),
                        round(dsp - v - ck - x["calc"][e])],
                [None, None] + ["#,##0"] * 8)
            r += 1
    ws.cell(r + 1, 1, "Marc de Bourgogne : achats du seul code article 550252 (Jacoulot 45 degres), 70 + 140 + 70 cl. Le marc du Jura Tissot 50 degres (code 520096, 700 cl) est un produit distinct, vendu au verre, et ne figure pas dans ce bilan. Le reste negatif de l exercice 1 est precisement le motif du plafonnement retenu a la feuille 4 : nous ramenons la demande a 210 cl sur les trois exercices.")
    ws.cell(r + 2, 1, "Liqueur de Poire : achats du code article 591050, 140 + 840 + 770 cl, soit 25 bouteilles de 70 cl.")

    # --- 4. les deux grandeurs ----------------------------------------------
    ws = sheet(wb, "4-Cuisine et supplement", "4. Deux grandeurs distinctes : le volume physiquement parti en cuisine, et le supplement demande au service (litres, 3 exercices)",
               ["Alcool", "A. Cuisine calculee (plats vendus x dose)", "Plafond : achats factures FCBS",
                "A. Volume physiquement parti en cuisine", "Deja retranche par le service",
                "B. Supplement demande", "Observation"],
               [20, 17, 16, 18, 16, 14, 66])
    NOTE = {
        "Calvados": "plafonne aux achats factures (73,0 L) ; le repere D retranche deja 93,2 L, soit davantage : aucun supplement demande",
        "Macvin": "le repere Q retranche deja 240,1 L, soit davantage que le volume calcule : aucun supplement demande",
        "Creme de Cassis": "la part desserts du volume unique des cremes (33,3 L, p. 69) est superieure : aucun supplement demande",
        "Arbois Vin Jaune": "repere E : 111,6 L deja retranches",
        "Porto": "repere G : 15,4 L deja retranches, pour 6 015 portions de plats au porto lues en caisse",
        "Ravelin": "aucun BIB de ravelin sur l exercice 1 : le retranchement opere sur le volume unique des BIB ne peut pas le couvrir",
        "Bailey's": "aucun retranchement identifie dans la reponse du service",
        "Grand Marnier": "aucun retranchement identifie ; plafonne aux achats factures",
        "Marc de Bourgogne": "aucun retranchement identifie ; 4 bouteilles de marc de Bourgogne Jacoulot 45 degres facturees sur 3 exercices, soit 280 cl (code article 550252) ; demande plafonnee a 210 cl, volume sorti du stock, et non aux 5,58 L calcules. Le marc du Jura Tissot 50 degres (code 520096, 10 bouteilles, 700 cl) est un autre produit, vendu au verre",
        "Liqueur de Poire": "aucun retranchement identifie ; 25 bouteilles facturees sur 3 exercices",
    }
    r = 4
    for x in lignes_solde:
        a = x["alcool"]
        put(ws, r, [a, round(sum(x["calc"].values()) / 100, 2), round(sum(x["plafond"].values()) / 100, 2),
                    round(sum(x["phys"].values()) / 100, 2), round(sum(x["deja"].values()) / 100, 2),
                    round(sum(x["sup"].values()) / 100, 2), NOTE.get(a.replace("è", "e"), NOTE.get(a, ""))],
            [None] + ["#,##0.00"] * 5 + [None])
        ws.cell(r, 7).alignment = Alignment(wrap_text=True, vertical="top")
        r += 1
    put(ws, r, ["TOTAL", round(TOT_CALC / 100, 2),
                round(sum(sum(x["plafond"].values()) for x in lignes_solde) / 100, 2),
                round(TOT_PHYS / 100, 2),
                round(sum(sum(x["deja"].values()) for x in lignes_solde) / 100, 2),
                round(TOT_SUP / 100, 2), ""],
        [None] + ["#,##0.00"] * 5 + [None], bold=True)
    ws.cell(r + 2, 1, "A = volume qui a quitte le stock : c est la grandeur du bilan matiere. B = ce que nous demandons au service en plus de ce qu il retranche deja.")
    ws.cell(r + 4, 1, "La colonne « cuisine calculee » n est jamais modifiee par un plafonnement : elle reste le produit du nombre de plats par la dose. Le Calvados y garde 119,1 L en face de 73,0 L retenus, le marc de Bourgogne 5,58 L en face de 2,10 L retenus.")
    ws.cell(r + 5, 1, "Le plafonnement joue exercice par exercice, sauf pour le marc de Bourgogne, plafonne sur les trois exercices pris ensemble aux 210 cl sortis du stock (280 cl factures moins la bouteille inventoriee au 31/03/2025), faute de savoir lequel des deux marcs achetes entre dans le baba.")
    ws.cell(r + 3, 1, "Sensibilite du plafond : achats factures FCBS %.1f L ; colonne « volume disponible » du service %.1f L ; le plus faible des deux %.1f L."
            % (sum(sum(x["phys"].values()) for x in lignes_solde) / 100,
               sum(sum(x["phys_svc"].values()) for x in lignes_solde) / 100,
               sum(sum(x["phys_min"].values()) for x in lignes_solde) / 100))

    # --- 5. achats des alcools secondaires ----------------------------------
    ws = sheet(wb, "5-Achats secondaires", "5. Achats factures FCBS des alcools discutes p. 69 et 70, exercice par exercice, contre les volumes retenus par le service",
               ["Produit (code article)", "Contenance", "Exercice 1 (unites)", "Exercice 2 (unites)",
                "Exercice 3 (unites)", "Total 3 exercices (cl)", "Volume retenu par le service (cl)",
                "Ce que le volume du service represente"],
               [26, 12, 14, 14, 14, 15, 17, 52])
    RET = {
        "Bailey's": (1400, "les achats de l exercice 1 (280 cl), l exercice 2 diminue d une bouteille (1 050 cl) et une seule bouteille de l exercice 3 (70 cl)"),
        "Marc de Bourgogne": (70, "une seule bouteille, soit les achats d un exercice sur trois"),
        "Liqueur de Poire": (140, "les achats du seul exercice 1"),
        "Grand Marnier": (0, "aucun volume retenu"),
        "Marc du Jura": (0, "produit non discute par le service"),
        "Ravelin BIB 10 L": (0, "premiere facture le 21/04/2023, soit au debut de l exercice 2"),
        "Ravelin 99 cl": (0, "achete des l exercice 1"),
        "Ravelin 75 cl": (0, "achete des l exercice 1"),
    }
    r = 4
    for k2 in ["Ravelin 75 cl", "Ravelin 99 cl", "Ravelin BIB 10 L", "Bailey's", "Marc de Bourgogne",
               "Marc du Jura", "Liqueur de Poire", "Grand Marnier"]:
        (q, _l), cont = ACHATS_UNITES[k2]
        ret, obs = RET[k2]
        put(ws, r, [k2, f"{cont:g} cl", q[EXOS[0]], q[EXOS[1]], q[EXOS[2]],
                    round(sum(q.values()) * cont), ret or "", obs],
            [None, None, "#,##0.0", "#,##0.0", "#,##0.0", "#,##0", "#,##0", None])
        ws.cell(r, 8).alignment = Alignment(wrap_text=True, vertical="top")
        r += 1

    # --- 6. detail des factures ---------------------------------------------
    ws = sheet(wb, "6-Factures", "6. Detail des factures Franche-Comte Boissons Services pour ces produits",
               ["Produit", "Exercice", "Date", "N de facture", "Code", "Designation imprimee",
                "Quantite", "Montant HT"],
               [20, 12, 12, 12, 10, 52, 10, 11])
    r = 4
    for k2 in ["Ravelin 75 cl", "Ravelin 99 cl", "Ravelin BIB 10 L", "Bailey's", "Marc de Bourgogne",
               "Marc du Jura", "Liqueur de Poire", "Grand Marnier"]:
        (q, lg), cont = ACHATS_UNITES[k2]
        for (p, dt, num, code, des, qt, mt) in lg:
            put(ws, r, [k2, LAB[p], dt, num, code, des, qt, mt],
                [None] * 6 + ["#,##0.0", "#,##0.00"])
            r += 1

    os.makedirs(OUT, exist_ok=True)
    wb.save(OUT + "R1-alcool-cuisine-encadrement.xlsx")
    print("-> public/documents/pieces-reponse-1/R1-alcool-cuisine-encadrement.xlsx")
    print(f"cuisine (A) {TOT_PHYS/100:.1f} L | supplement (B) {TOT_SUP/100:.1f} L | calcule {TOT_CALC/100:.1f} L")


if __name__ == "__main__":
    main()
