#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
R1 - Partie R de la reponse DDFiP du 04/09/2026 (p. 87 et 88) : les assiettes d'achats
opposees a l'alcool de cuisine, et le contenu reel des nombres de caisse du service.

Produit public/documents/pieces-reponse-1/R1-alcool-cuisine-assiettes.xlsx :
  1. Achats factures, facture par facture, pour les trois produits dont le service
     dit p. 88 que le volume demande depasse « celui disponible » : Bailey's,
     marc de Bourgogne, liqueur de poire. Le marc du Jura, produit distinct, y est
     joint pour montrer qu'il ne se confond pas avec le marc de Bourgogne.
  2. Assiette du service en regard de l'assiette facturee, exercice par exercice.
  3. Reconstitution, a partir des quantites de caisse, des deux nombres que le service
     tire lui-meme de ses annexes 7-1 a 7-3 : 236 cl pour le Bailey's, 20 cl pour le
     marc de Bourgogne. On y lit ce que ces nombres contiennent reellement.
  4. Calvados : les achats factures par exercice en regard du « volume disponible »
     imprime p. 65, qui porte la signature d'une variation de stock.
  5. Les doses de cuisine : origine de chacune, et valeur appliquee de part et d'autre.

Sources (lecture seule) :
  src/data/factures-fournisseur.json                   (factures FCBS)
  src/data/calculsBoissons/itemsCaisse.json            (ANNEXE-D, quantites vendues)
  public/documents/vins-boissons/_pipeline_conso_alcool.py (mapping libelle -> dose)

Aucune valeur n'est saisie a la main, hors les nombres imprimes par le service, qui
sont recopies du courrier avec leur page.
"""
import ast, json, os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/"
OUT = BASE + "public/documents/pieces-reponse-1/"
EXOS = ["2022-2023", "2023-2024", "2024-2025"]
LAB = {"2022-2023": "Exercice 1", "2023-2024": "Exercice 2", "2024-2025": "Exercice 3"}

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


# ---------------------------------------------------------------------------
# 1. achats factures, ligne par ligne
# ---------------------------------------------------------------------------
PRODUITS = [
    ("Bailey's", "510133", 70.0, "BAILEY'S 70 CL 17°"),
    ("Marc de Bourgogne", "550252", 70.0, "MARC DE BOURGOGNE 70 CL 45° EXTRA EGRAPPE MAISON JACOULOT"),
    ("Marc du Jura", "520096", 70.0, "MARC DU JURA TISSOT 70 CL MICHEL TISSOT"),
    ("Liqueur de Poire", "591050", 70.0, "LIQUEUR GOLDEN EIGHT 70 CL 25° LIQUEUR DE POIRE WILLIAM"),
    ("Calvados", "520055", 100.0, "CALVADOS BEAUJOUR 100 CL 40°"),
]

lignes_achats = []   # detail
achats = {}          # nom -> {exo: cl}
ecartees = []        # lignes non retenues
for nom, code, cl, _lib in PRODUITS:
    achats[nom] = {e: 0.0 for e in EXOS}
    for f in FACT:
        p = periode(f["dateFacture"])
        if not p:
            continue
        for ln in f.get("lignes", []):
            if str(ln.get("code") or "") != code:
                continue
            q = ln.get("quantite")
            if ln.get("montantHT") is None or q is None:
                ecartees.append({"nom": nom, "date": f["dateFacture"], "num": f["numero"],
                                 "designation": (ln.get("designation") or "").strip(),
                                 "motif": "quantité ou montant HT absent : ligne non facturée"})
                continue
            achats[nom][p] += q * cl
            lignes_achats.append({"nom": nom, "code": code, "exo": p, "date": f["dateFacture"],
                                  "num": f["numero"], "designation": (ln.get("designation") or "").strip(),
                                  "qte": q, "cl_unite": cl, "cl": q * cl,
                                  "pu": ln.get("puNet"), "ht": ln.get("montantHT")})

# ---------------------------------------------------------------------------
# 2. ce que le service oppose, p. 88 et p. 69-70 (recopie du courrier)
# ---------------------------------------------------------------------------
OPPOSE = [
    {"nom": "Bailey's", "cl": 1400, "citation": "« ce volume correspond à la totalité des achats disponibles (280 + 1050 + 70 = 1 400 centilitres) »", "page": "p. 88 et 69"},
    {"nom": "Marc de Bourgogne", "cl": 70, "citation": "« un volume près de 6 fois supérieur à celui disponible (70 centilitres) »", "page": "p. 88 et 70"},
    {"nom": "Liqueur de Poire", "cl": 140, "citation": "« un volume près de 3 fois supérieur à celui disponible (140 centilitres) »", "page": "p. 88 et 70"},
]

# ---------------------------------------------------------------------------
# 3. quantites de caisse (ANNEXE-D)
# ---------------------------------------------------------------------------
items = {}
for it in json.load(open(BASE + "src/data/calculsBoissons/itemsCaisse.json", encoding="utf-8"))["items"]:
    items.setdefault(it["produit"], {e: 0.0 for e in EXOS})
    for e in EXOS:
        items[it["produit"]][e] += it["quantite"].get(e, 0.0)

# nombres que le service tire lui-meme de ses annexes 7-1 a 7-3
CAISSE_SERVICE = [
    {"nom": "Bailey's", "total": 236, "termes": "20+16+80+32+28+60",
     "citation": "« les articles enregistrés susceptibles d’utiliser cet alcool (confection de Dessert ou verre), sur trois ans, n’entraînerait qu’une consommation de 236 centilitres »",
     "page": "p. 88 et 69",
     "articles": [("Baileys", "verre", 4.0), ("BAILEYS", "verre", 4.0), ("IVRESSE", "dessert à la carte", 4.0)]},
    {"nom": "Marc de Bourgogne", "total": 20, "termes": "8 + 4 + 8",
     "citation": "« les articles enregistrés susceptibles d’utiliser cet alcool (confection de verre), sur trois ans, n’entraînerait qu’une consommation de 20 centilitres »",
     "page": "p. 70",
     "articles": [("Vieux Marc Bourgogne", "verre", 4.0)]},
]

# ---------------------------------------------------------------------------
# 4. Calvados : disponible imprime p. 65
# ---------------------------------------------------------------------------
DISPO_CALVA = {"2022-2023": 3100, "2023-2024": 2200, "2024-2025": 2000}

# ---------------------------------------------------------------------------
# 5. doses de cuisine : celles que nous appliquons, lues dans le pipeline
# ---------------------------------------------------------------------------
src = open(BASE + "public/documents/vins-boissons/_pipeline_conso_alcool.py", encoding="utf-8").read()
FOOD = None
for node in ast.parse(src).body:
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "FOOD":
        FOOD = ast.literal_eval(node.value)
assert FOOD, "FOOD introuvable"

doses_nous = {}
for libelle, d in FOOD.items():
    q = items.get(libelle)
    if not q:
        continue
    for (alc, dose, _e) in d:
        doses_nous.setdefault(dose, []).append((libelle, alc, sum(q.values())))

DOSE_SERVICE = [
    ("Sauce et plat en sauce", "1 cl", "1 cl",
     "p. 67, texte du service : « les sauces en cuisse pour des plats spécifiques (1cl) » ; p. 67, en-tête du tableau du porto : « dose de 1cl » ; p. 66, en-tête du tableau du vin jaune : « 1cl / 10 cl »"),
    ("Fondue", "10 cl", "10 cl",
     "p. 66, en-tête du tableau du vin jaune : « Nombre de plats (nécessitant une dose) 1cl / 10 cl », la seconde valeur visant les fondues"),
    ("Baba, flambage, dessert, assiette", "4 cl", "4 cl",
     "p. 65, en-tête du tableau du Calvados : « Volume consommé (à raison de 4 cl par plat) » ; p. 67, texte du service : « 4 cl, pour la préparation des plats/desserts ( en cuisine ) » et en-tête du tableau du macvin : « dose de 4 cl »"),
]

# ---------------------------------------------------------------------------
# ecriture
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
        c.fill, c.font, c.border = HEAD, HF, B
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
        if fmts and fmts[j - 1]:
            c.number_format = fmts[j - 1]
        if fill and fill(j):
            c.fill = fill(j)


wb = Workbook()

# --- 1. assiettes -----------------------------------------------------------
ws = sheet(wb, "1-Assiettes", "1. Ce que le service oppose p. 88, et ce que portent les factures sur les trois exercices",
           ["Produit", "Code article", "Volume opposé par le service (cl)", "Formule du courrier",
            "Achats facturés exercice 1 (cl)", "Exercice 2 (cl)", "Exercice 3 (cl)",
            "Achats facturés 3 exercices (cl)", "Ce à quoi correspond le volume opposé",
            "Écart avec les factures (cl)"],
           [20, 11, 15, 44, 13, 13, 13, 15, 40, 13], first=True)
r = 4
for o in OPPOSE:
    nom = o["nom"]
    code = [c for n, c, _cl, _l in PRODUITS if n == nom][0]
    a = achats[nom]
    tot = sum(a.values())
    corr = [LAB[e] for e in EXOS if abs(a[e] - o["cl"]) < 0.01]
    if nom == "Bailey's":
        quoi = "exercice 1 seul pour le premier terme (280 cl) ; le total retenu vaut 20 des 32 bouteilles facturées"
    elif corr:
        quoi = ("exactement " + " ou ".join(corr) + " pris isolément") if len(corr) > 1 else ("exactement l’" + corr[0].lower() + " pris isolément")
    else:
        quoi = "ne correspond à aucun exercice"
    put(ws, r, [nom, code, o["cl"], o["citation"], a["2022-2023"], a["2023-2024"], a["2024-2025"],
                tot, quoi, o["cl"] - tot],
        [None, None, "#,##0", None, "#,##0", "#,##0", "#,##0", "#,##0", None, "#,##0"],
        fill=lambda j: BAD if j in (3, 10) else (OK if j == 8 else None))
    r += 1
mj = achats["Marc du Jura"]
put(ws, r, ["Marc du Jura", "520096", "", "produit distinct, non visé p. 88, joint pour comparaison",
            mj["2022-2023"], mj["2023-2024"], mj["2024-2025"], sum(mj.values()),
            "vendu au verre sous le libellé « Marc du Jura (4cl) » ; jamais mélangé au Jacoulot dans les factures (prix 18,61 / 19,48 € contre 22,10 / 25,90 €)", ""],
    [None, None, None, None, "#,##0", "#,##0", "#,##0", "#,##0", None, None])
r += 2
for t in ["Exercices : exercice 1 = 01/04/2022 au 31/03/2023, exercice 2 = 01/04/2023 au 31/03/2024, exercice 3 = 01/04/2024 au 31/03/2025.",
          "Seules les lignes portant a la fois une quantite et un montant HT sont comptees ; les lignes « M/SE MANQUANTE S/ CAMION » et les lignes de deconsigne, qui n'en portent pas, sont ecartees et listees a la feuille 2. Les avoirs sont conserves en negatif.",
          "Le service ecrit p. 88, pour le Calvados, le vin jaune, le porto et le macvin, qu'il raisonne en « volume globalise sur trois ans conformement a la logique de Maitre THIVEND », et pour la creme de cassis « en reprenant la logique de Maitre THIVEND qui veut globaliser le volume sur trois ans ». Les trois volumes ci-dessus ne sont pas globalises sur trois ans."]:
    ws.cell(r, 1, t)
    r += 1

# --- 2. detail facture par facture -----------------------------------------
ws = sheet(wb, "2-Factures", "2. Achats facturés, facture par facture (fournisseur Franche-Comté Boissons Services)",
           ["Produit", "Code", "Exercice", "Date de facture", "N° de facture", "Désignation portée sur la facture",
            "Quantité", "Contenance (cl)", "Volume (cl)", "P.U. net (€)", "Montant HT (€)"],
           [20, 9, 11, 13, 12, 54, 9, 11, 10, 10, 11])
r = 4
for x in sorted(lignes_achats, key=lambda z: (z["nom"], z["exo"], z["date"].split("/")[::-1])):
    put(ws, r, [x["nom"], x["code"], LAB[x["exo"]], x["date"], x["num"], x["designation"],
                x["qte"], x["cl_unite"], x["cl"], x["pu"], x["ht"]],
        [None] * 6 + ["#,##0.##", "#,##0", "#,##0", "#,##0.00", "#,##0.00"])
    r += 1
r += 1
ws.cell(r, 1, "Lignes écartées (ni quantité ni montant HT : marchandise non livrée ou ligne de déconsigne)").font = Font(bold=True)
r += 1
for x in ecartees:
    put(ws, r, [x["nom"], "", "", x["date"], x["num"], x["designation"], "", "", "", "", x["motif"]])
    r += 1

# --- 3. ce que contiennent les nombres de caisse du service -----------------
ws = sheet(wb, "3-Nombres de caisse", "3. Ce que contiennent les nombres que le service tire de ses propres annexes 7-1 à 7-3",
           ["Produit", "Total imprimé par le service (cl)", "Termes imprimés", "Page",
            "Article de caisse", "Nature", "Dose (cl)", "Exercice 1", "Exercice 2", "Exercice 3",
            "Volume 3 exercices (cl)"],
           [18, 14, 20, 9, 24, 20, 8, 11, 11, 11, 13])
r = 4
for c in CAISSE_SERVICE:
    first = True
    tot = 0.0
    for (art, nature, dose) in c["articles"]:
        q = items.get(art)
        if not q:
            continue
        v = [q[e] * dose for e in EXOS]
        tot += sum(v)
        put(ws, r, [c["nom"] if first else "", c["total"] if first else "", c["termes"] if first else "",
                    c["page"] if first else "", art, nature, dose, v[0], v[1], v[2], sum(v)],
            [None, "#,##0", None, None, None, None, "0.#", "#,##0", "#,##0", "#,##0", "#,##0"])
        first = False
        r += 1
    put(ws, r, ["", "", "", "", "Total reconstitué depuis la caisse", "", "", "", "", "", tot],
        [None] * 10 + ["#,##0"], bold=True,
        fill=(lambda j: OK if j == 11 else None) if abs(tot - c["total"]) < 0.5 else None)
    r += 1
    put(ws, r, ["", "", "", "", "Écart avec le nombre imprimé par le service", "", "", "", "", "", tot - c["total"]],
        [None] * 10 + ["#,##0"])
    r += 2
for t in ["Marc de Bourgogne : les trois termes imprimes par le service, 8 + 4 + 8, sont exactement les 2, 1 et 2 verres de « Vieux Marc Bourgogne » sonnes sur les trois exercices, a 4 cl. Son nombre est donc un volume vendu au verre, non un volume de cuisine. Il ne contient pas l'article « Marc du Jura (4cl) », 25 + 17 + 18 verres : le service distingue donc lui-meme les deux produits en caisse.",
          "Bailey's : cinq des six termes imprimes par le service se retrouvent au centilitre, 20 / 80 / 32 pour le Bailey's vendu au verre et 28 / 16 pour le dessert IVRESSE des exercices 1 et 3 ; le sixieme, 60, vaut 12 cl de plus que les 48 cl que la caisse porte a l'IVRESSE de l'exercice 2. Sur les 236 cl qu'il oppose, 132 cl sont donc du Bailey's servi dans un verre et vendu comme tel, et 104 cl le seul dessert de la carte.",
          "Liqueur de poire, p. 70 : le service imprime « 480 centilitres (216+48+8+84+44+80) » pour la consommation lue dans ses annexes, et « 140 centilitres » pour le volume disponible, dans le meme paragraphe. Nous ne reconstituons pas sa selection d'articles, faute de la connaitre ; nous relevons que le second nombre ne peut pas produire le premier.",
          "Les articles servis a l'interieur d'un menu au forfait ne sont pas sonnes a l'article : ils ne peuvent donc pas figurer dans ces additions."]:
    ws.cell(r, 1, t)
    r += 1

# --- 4. Calvados ------------------------------------------------------------
INV = json.load(open(BASE + "public/documents/inventaires/inventaires.json", encoding="utf-8"))["inventaires"]
stock = {}
for inv in INV:
    n = sum(l["quantite"] for l in inv.get("lignes", []) if "alvados" in l["produit"])
    stock[inv["date"]] = n
CLOTURE = {"2022-2023": stock.get("2023-03-31", 0), "2023-2024": stock.get("2024-03-31", 0),
           "2024-2025": stock.get("2025-03-31", 0)}
OUVERTURE = {"2022-2023": None, "2023-2024": CLOTURE["2022-2023"], "2024-2025": CLOTURE["2023-2024"]}

ws = sheet(wb, "4-Calvados stock", "4. Calvados : le « volume disponible » imprimé p. 65 se reproduit au centilitre à partir des factures et des inventaires",
           ["Exercice", "Bouteilles de 100 cl facturées", "Stock d’ouverture (bouteilles)",
            "Stock de clôture (bouteilles)", "Achats + ouverture - clôture (cl)",
            "« Volume disponible » imprimé p. 65 (cl)", "Écart (cl)", "Lecture"],
           [12, 14, 14, 14, 16, 17, 10, 58])
r = 4
ta = td = 0
LECT = {"2022-2023": "aucun inventaire au 31/03/2022 : l’ouverture n’est pas mesurée. Une bouteille en stock au 01/04/2022 suffit à reproduire le chiffre du service",
        "2023-2024": "reproduit au centilitre, sans aucun paramètre libre",
        "2024-2025": "reproduit au centilitre, sans aucun paramètre libre"}
for e in EXOS:
    a = achats["Calvados"][e]
    btl = a / 100
    ouv = OUVERTURE[e]
    clo = CLOTURE[e]
    rec = None if ouv is None else (btl + ouv - clo) * 100
    d = DISPO_CALVA[e]
    ta += a
    td += d
    put(ws, r, [LAB[e], btl, "non mesuré" if ouv is None else ouv, clo,
                "" if rec is None else rec, d, "" if rec is None else rec - d, LECT[e]],
        [None, "#,##0", None, "#,##0", "#,##0", "#,##0", "#,##0", None],
        fill=(lambda j: OK if j == 7 else None) if rec is not None and abs(rec - d) < 0.5 else None)
    r += 1
put(ws, r, ["Total 3 ans", ta / 100, "", "", "", td, "",
            "achats facturés 7 300 cl, « volume disponible » 7 300 cl : sur ce produit, l’assiette du service couvre bien les trois exercices"],
    [None, "#,##0", None, None, None, "#,##0", None, None], bold=True)
r += 2
for t in ["Achats : code article 520055, bouteilles de 100 cl, lignes facturees seulement. Stocks : inventaires physiques aux trois clotures, lignes « Calvados 100cl » et « Calvados Beaujour 100cl 40 degres ».",
          "Ce que cela etablit : le « volume disponible » du service est un volume entre dans l'etablissement, achats augmentes de la variation de stock. Rien n'en a ete retranche pour la cuisine, les pertes, les offerts ni la consommation du personnel.",
          "Ce que cela etablit aussi : sur le Calvados, le service dispose bien d'une assiette de trois exercices. Les volumes qu'il oppose p. 88 au Bailey's, au marc de Bourgogne et a la liqueur de poire, eux, sont inferieurs aux achats des trois exercices pris ensemble, et aucun jeu de stock ne peut produire cela.",
          "Le porto : les trois volumes que le service inscrit p. 67, 2 730, 4 760 et 4 480 cl, sont des multiples exacts de 70 cl, soit 39, 68 et 64 contenants. Les 173 bouteilles de porto facturees sur la periode sont toutes des 75 cl."]:
    ws.cell(r, 1, t)
    r += 1

# --- 5. doses ---------------------------------------------------------------
ws = sheet(wb, "5-Doses", "5. Les doses de cuisine : celles que le service imprime, et celles que nous appliquons",
           ["Préparation", "Dose imprimée par le service", "Dose que nous appliquons",
            "Écart", "Où le service l’écrit"],
           [30, 22, 20, 10, 78])
r = 4
for (prep, ds, dn, ou) in DOSE_SERVICE:
    put(ws, r, [prep, ds, dn, "aucun", ou], fill=lambda j: OK if j == 4 else None)
    r += 1
r += 1
ws.cell(r, 1, "Detail des articles auxquels chaque dose s'applique chez nous (quantites lues en caisse, 3 exercices)").font = Font(bold=True)
r += 2
for j, h in enumerate(["Dose (cl)", "Article de caisse", "Alcool", "Quantité 3 exercices"], 1):
    c = ws.cell(r, j, h)
    c.fill, c.font, c.border = HEAD, HF, B
r += 1
for dose in sorted(doses_nous, reverse=True):
    for (lib, alc, q) in sorted(doses_nous[dose], key=lambda z: -z[2]):
        put(ws, r, [dose, lib, alc, q], ["0.#", None, None, "#,##0"])
        r += 1
r += 1
for t in ["Les doses des dirigeants ont ete recueillies par ecrit par le verificateur a la suite de l'entrevue du 30 mars 2026. Le service ecrit p. 68 : « Pour toutes les doses des alcools necessaires a la cuisine, le service n'a fait que suivre les recommandations des dirigeants. »",
          "Aucune dose n'est modifiee par notre reponse : le volume de cuisine se deduit de ces trois doses et du nombre d'articles vendus."]:
    ws.cell(r, 1, t)
    r += 1

# --- 6. annexe 7-3 : la seule ligne dont le detail soit produit ------------
RA = json.load(open(BASE + "src/data/reconstitution-administration.json", encoding="utf-8"))
mac = [i for i in RA["ingredients"] if i.get("ref") == "Macvin"][0]
ws = sheet(wb, "6-Annexe 7-3 macvin", "6. Annexe 7-3 du service, macvin, exercice 3 : la seule ligne de ses tableaux dont le détail soit produit",
           ["Poste de l’annexe du service", "Nombre d’articles", "Dose (cl)",
            "Probabilité de choix appliquée par le service", "Volume (cl)",
            "Nos propres quantités de caisse (exercice 3)"],
           [42, 13, 9, 20, 12, 26])
NOTRE = {"Baba au Macvin": ("Baba", items.get("Baba", {})),
         "Saucisse flambée au Macvin": ("ASSIETTE FRANC-COMTO", items.get("ASSIETTE FRANC-COMTO", {}))}
r = 4
tot_n = tot_v = 0
for det in mac["deductions"]["detail"]:
    u = det["usage"]
    n = det["nbArticles"]
    pr = det.get("proportion")
    v = det["volumeCl"]
    tot_n += n
    tot_v += v
    if u in NOTRE:
        lib, q = NOTRE[u]
        cmp = f"{lib} : {q.get('2024-2025', 0):.0f}"
    else:
        cmp = "menus au forfait, non sonnés à l’article"
    put(ws, r, [u, n, 4, "" if pr is None else pr, v, cmp],
        [None, "#,##0", "0", "0.00%", "#,##0", None])
    r += 1
put(ws, r, ["Total", tot_n, "", "", tot_v, ""], [None, "#,##0", None, None, "#,##0", None], bold=True)
r += 1
put(ws, r, ["Ce que le tableau de la p. 67 imprime sur cette ligne", 2714, "", "", 7406, ""],
    [None, "#,##0", None, None, "#,##0", None], bold=True, fill=lambda j: OK if j in (2, 5) else None)
r += 3
for t in ["Source : Proposition_4_Annexes_Finales.pdf, transcrite dans src/data/reconstitution-administration.json. Le total des volumes, 7 405 cl, est le 7 406 cl imprime au tableau du macvin p. 67 ; le total des articles, 2 714, est la colonne « Nombre de plats » du meme tableau.",
          "Premier constat : la dose est de 4 cl sur les quatre postes. C'est la notre.",
          "Deuxieme constat : les 561 babas et les 547 assiettes sont, au libelle pres, nos deux articles de carte du macvin sur l'exercice 3, aux memes quantites.",
          "Troisieme constat : le service pondere lui-meme le plat et le dessert du menu Franc-Comtois par la probabilite que le client les choisisse, 38,74 % et 53,84 %. C'est la methode que notre reponse expose pour les menus.",
          "Quatrieme constat : les 803 menus figurent deux fois dans la colonne « Nombre de plats » et n'y sont pas ponderes. Le rapport des deux colonnes, 7 406 / 2 714 = 2,73 cl, n'est donc pas une dose : c'est un artefact de construction du tableau. Aucune dose ne peut etre deduite de ce rapport, ni dans un sens ni dans l'autre.",
          "L'annexe 7-3 porte enfin : « Macvin ROSE exclu du calcul. Vin Jaune affecte au Poulet a la Jurassienne (61,26 % des assiettes), Macvin aux Assiettes Franc-Comtoises (38,74 %). »"]:
    ws.cell(r, 1, t)
    r += 1

# --- 7. ce que portent les annexes 7-1 a 7-3 du service ---------------------
# Lu sur les images des annexes de la proposition de rectifications
# (Proposition_3_Annexes_Boissons.pdf, pages 171, 185 et 199 du document,
# pages 53, 67 et 81 du PDF), colonnes « Quantites Disponibles (Bouteilles) »
# et « Volume Disponible (Centilitres) ».
ANNEXES = [
    # produit, (btl, cl) exercice 1, exercice 2, exercice 3, volume oppose p. 88/70
    ("Bailey's", (4, 280), (15, 1050), (12, 840), 1400,
     "« ce volume correspond a la totalite des achats disponibles (280 + 1050 + 70 = 1 400 centilitres) » : le troisieme terme est 70 la ou l'annexe 7-3 porte 840"),
    ("Liqueur de Poire", (3.75, 263), (10, 700), (13, 910), 140,
     "« un volume pres de 3 fois superieur a celui disponible (140 centilitres) » : les trois annexes en portent 1 873"),
    ("Marc de Bourgogne", (0, 0), (1, 70), (0, 0), 70,
     "« un volume pres de 6 fois superieur a celui disponible (70 centilitres) » : c'est bien le total de ses annexes, mais elles ne portent qu'une bouteille la ou les factures en portent quatre"),
    ("Marc du Jura", (8, 560), (1, 70), (3, 210), None,
     "non vise p. 88 ; ses annexes en portent 12 bouteilles quand les factures en portent 10"),
]
ws = sheet(wb, "7-Annexes 7-1 a 7-3", "7. Ce que les annexes 7-1, 7-2 et 7-3 du service portent elles-mêmes comme volume disponible",
           ["Produit", "Annexe 7-1, exercice 1 (bouteilles)", "Volume (cl)",
            "Annexe 7-2, exercice 2 (bouteilles)", "Volume (cl)",
            "Annexe 7-3, exercice 3 (bouteilles)", "Volume (cl)",
            "Total des trois annexes (cl)", "Volume opposé p. 88 ou p. 70 (cl)",
            "Achats facturés 3 exercices (cl)", "Lecture"],
           [18, 13, 10, 13, 10, 13, 10, 14, 14, 14, 66])
r = 4
for (nom, e1, e2, e3, opp, lect) in ANNEXES:
    tot = e1[1] + e2[1] + e3[1]
    fac = sum(achats[nom].values())
    put(ws, r, [nom, e1[0], e1[1], e2[0], e2[1], e3[0], e3[1], tot,
                "" if opp is None else opp, fac, lect],
        [None, "#,##0.##", "#,##0", "#,##0.##", "#,##0", "#,##0.##", "#,##0", "#,##0", "#,##0", "#,##0", None],
        fill=(lambda j: BAD if j == 9 else (OK if j in (8, 10) else None)) if opp is not None and opp < tot else None)
    r += 1
r += 1
for t in ["Source : Proposition_3_Annexes_Boissons.pdf, pages 171 (annexe 7-1), 185 (annexe 7-2) et 199 (annexe 7-3) du document. Colonnes « Quantites (2) Disponibles (Bouteilles) », « Designation Articles (2) (par rapport Achats) » et « Volume Disponible (Centilitres) ».",
          "Bailey's : les deux premiers termes de l'addition imprimee p. 88, 280 et 1 050, sont exactement les volumes des annexes 7-1 et 7-2. Le troisieme, 70, n'est pas celui de l'annexe 7-3, qui porte 840 cl pour 12 bouteilles. Le total des trois annexes est de 2 170 cl et les factures portent 2 240 cl.",
          "Liqueur de poire : les annexes portent 263 cl, 700 cl et 910 cl, soit 1 873 cl. Le courrier oppose 140 cl.",
          "Marc de Bourgogne et marc du Jura : les annexes portent 1 et 12 bouteilles, les factures 4 et 10. Treize bouteilles chez le service, quatorze dans les factures : l'ecart tient a la ligne sur laquelle chaque bouteille a ete portee, non a un volume manquant. Les deux marcs reunis representent 910 cl dans ses propres annexes.",
          "Calvados, meme source : 31 bouteilles et 3 100 cl a l'annexe 7-1, 22 et 2 200 a la 7-2, 20 et 2 000 a la 7-3, soit les trois nombres de la colonne « volume disponible » de la p. 65."]:
    ws.cell(r, 1, t)
    r += 1

os.makedirs(OUT, exist_ok=True)
dest = OUT + "R1-alcool-cuisine-assiettes.xlsx"
wb.save(dest)
print("ecrit :", dest)
for nom in achats:
    print(f"  {nom:20}", {LAB[e]: achats[nom][e] for e in EXOS}, "total", sum(achats[nom].values()))
