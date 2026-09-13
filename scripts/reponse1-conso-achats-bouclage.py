#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reponse1-conso-achats-bouclage.py

Troisieme piece de la reponse au courrier DDFiP 39 du 04/09/2026, partie I
"Consommation vendue superieure aux achats" (p. 48 a 53).

Elle repond a UNE question, et a elle seule : la comptabilite contient-elle,
pour un produit quelconque, une consommation VENDUE superieure aux achats ?
La demonstration n'utilise aucune dose : elle ne rapproche que des factures,
des inventaires et des tickets de caisse.

Produit public/documents/pieces-reponse-1/R1-conso-achats-bouclage.xlsx :

  1. "Calvados factures"   : les 62 lignes de facture Franche-Comte Boissons
     Services du Calvados, bouteille par bouteille, avec les lignes facturees
     puis notees "M/SE MANQUANTE S/ CAMION" isolees.
  2. "Calvados bouclage"   : achats livres, stock d'inventaire a chaque cloture,
     volume sorti du stock, volume vendu au verre en caisse. Le bouclage se
     ferme sans qu'aucune dose n'intervienne.
  3. "Calvados caisse"     : le detail des ventes au verre et des plats, par
     exercice, tel qu'il est enregistre sous chaque libelle de caisse.
  4. "Les deux chiffres"   : ce que le service imprime lui-meme pour le Calvados
     a la page 65 (volume disponible, volume consomme, nombre de plats) et a la
     page 69 (repere D), et l'ecart entre ces deux chiffres.
  5. "Unite des lignes"    : la colonne "Format Quantites" des tableaux du
     service annonce des CENTILITRES. Quatre lignes sont en BOUTEILLES : le
     controle est fait ligne par ligne contre le detail des factures.
  6. "Bethanie millesimes" : le meme vin facture sous six designations.

Sources (lecture seule) :
  - src/data/factures-fournisseur.json (199 factures Franche-Comte Boissons
    Services, detail ligne a ligne)
  - public/documents/inventaires/inventaire_YYYY-MM-DD.csv (inventaires de
    cloture au 31/03/2023, 31/03/2024 et 31/03/2025)
  - public/documents/caisse-enregistreuse/ANNEXE-D1/D2/D3 (synthese produit)
  - public/documents/vins-boissons/conso-exacte-carte.xlsx (plats et desserts
    dont la recette comporte du Calvados)
  - src/data/reponse1/consommation-superieure-achats.json (transcription des
    quatre tableaux du courrier, chapitre 1)

Idempotent : relancer le script reecrit le classeur.
"""
import os
import csv
import json
import re
import datetime

import xlrd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

ICI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(ICI, ".."))
FACT = os.path.join(ROOT, "src/data/factures-fournisseur.json")
PAGE = os.path.join(ROOT, "src/data/reponse1/consommation-superieure-achats.json")
INV = os.path.join(ROOT, "public/documents/inventaires")
CAISSE = os.path.join(ROOT, "public/documents/caisse-enregistreuse")
CARTE = os.path.join(ROOT, "public/documents/vins-boissons/conso-exacte-carte.xlsx")
OUTDIR = os.path.join(ROOT, "public/documents/pieces-reponse-1")
OUT = os.path.join(OUTDIR, "R1-conso-achats-bouclage.xlsx")

GRAS = Font(bold=True)
GBLANC = Font(bold=True, color="FFFFFF")
ENTETE = PatternFill("solid", fgColor="0F766E")
ROUGE = PatternFill("solid", fgColor="FEE2E2")
VERT = PatternFill("solid", fgColor="DCFCE7")
CENTRE = Alignment(horizontal="center", vertical="center", wrap_text=True)
GAUCHE = Alignment(horizontal="left", vertical="center", wrap_text=True)
BORD = Border(*(4 * (Side(style="thin", color="D1D5DB"),)))

EXOS = ["2022-2023", "2023-2024", "2024-2025"]
CLOTURES = {"2022-2023": "2023-03-31", "2023-2024": "2024-03-31", "2024-2025": "2025-03-31"}


def exercice(datefr):
    j, m, a = (int(x) for x in datefr.split("/"))
    d = datetime.date(a, m, j)
    if d <= datetime.date(2023, 3, 31):
        return "2022-2023"
    if d <= datetime.date(2024, 3, 31):
        return "2023-2024"
    if d <= datetime.date(2025, 3, 31):
        return "2024-2025"
    return None


# ---------------------------------------------------------------------------
# 1 et 2. Le Calvados : factures, inventaires, caisse
# ---------------------------------------------------------------------------
FACTURES = json.load(open(FACT, encoding="utf-8"))

calva_rows = []
achats = {e: 0 for e in EXOS}
achats_ht = {e: 0.0 for e in EXOS}
non_livre = {e: 0 for e in EXOS}
for f in FACTURES["factures"]:
    exo = exercice(f["dateFacture"])
    if not exo:
        continue
    for l in f["lignes"]:
        if "CALVA" not in l["designation"].upper():
            continue
        qte = l["quantite"] or 0
        ht = l["montantHT"] or 0.0
        cond = (l["conditionnement"] or "").upper()
        manquant = "MANQUANTE" in cond
        if manquant:
            non_livre[exo] += qte
        else:
            achats[exo] += qte
            achats_ht[exo] += ht
        calva_rows.append([
            f["dateFacture"], f["numero"], exo,
            l["designation"].split(" Ci-dessous")[0].split(" Articles Manquants")[0],
            l["conditionnement"], qte or None, l["puNet"], round(ht, 2) if ht else None,
            "Facturee puis notee manquante sur le camion : non livree" if manquant
            else ("Ligne sans quantite (renvoi de deconsigne)" if not qte else "Livree"),
        ])

# Inventaires de cloture
stock_final = {}
for exo, jour in CLOTURES.items():
    chemin = os.path.join(INV, f"inventaire_{jour}.csv")
    with open(chemin, encoding="utf-8") as fh:
        for row in csv.DictReader(fh, delimiter=";"):
            if "calva" in row["produit"].lower():
                stock_final[exo] = {
                    "produit": row["produit"],
                    "qte": float(row["quantite"]),
                    "valeur": float(row["valeur_ht"]),
                    "page": row.get("page", ""),
                }
if len(stock_final) != 3:
    raise SystemExit("Calvados absent d'un inventaire de cloture")

# Le stock d'ouverture au 31/03/2022 n'est pas detenu par la societe : c'est
# celui que le service retient dans son annexe n. 6, une bouteille.
STOCK_OUVERTURE_SERVICE = 1.0

# Ventes au verre lues dans la synthese produit de la caisse
verre_rows = []
verre_qte = {e: 0.0 for e in EXOS}
verre_ttc = {e: 0.0 for e in EXOS}
for i, exo in enumerate(EXOS):
    chemin = os.path.join(CAISSE, f"ANNEXE-D{i + 1}_synthese-produit_{exo}.xls")
    sh = xlrd.open_workbook(chemin).sheet_by_index(0)
    for r in range(sh.nrows):
        lib = str(sh.cell_value(r, 1))
        if "calva" not in lib.lower():
            continue
        pu = sh.cell_value(r, 2)
        qte = sh.cell_value(r, 4)
        ttc = sh.cell_value(r, 5)
        qte = float(qte) if isinstance(qte, float) else 0.0
        ttc = float(ttc) if isinstance(ttc, float) else 0.0
        verre_qte[exo] += qte
        verre_ttc[exo] += ttc
        verre_rows.append([exo, lib, pu, qte, round(ttc, 2)])

# Plats et desserts dont la recette comporte du Calvados
plats = {}
ws_carte = openpyxl.load_workbook(CARTE)["Conso exacte carte"]
for r in ws_carte.iter_rows(min_row=2, values_only=True):
    if not r[8] or "Calvados" not in str(r[8]):
        continue
    if str(r[5]) != "Cuisine (plat/dessert)":
        continue
    plats.setdefault(str(r[2]), {e: 0.0 for e in EXOS})[str(r[0])] += r[6] or 0

bouclage_rows = []
ouverture = STOCK_OUVERTURE_SERVICE
for exo in EXOS:
    sf = stock_final[exo]["qte"]
    sorti = achats[exo] + ouverture - sf
    bouclage_rows.append([
        exo, achats[exo], non_livre[exo] or None, round(achats_ht[exo], 2),
        ouverture, sf, round(sorti, 1), round(verre_qte[exo], 0),
        round(verre_ttc[exo], 2), round(sorti - verre_qte[exo] * 0.04, 2),
    ])
    ouverture = sf
tot_achats = sum(achats.values())
tot_sorti = tot_achats + STOCK_OUVERTURE_SERVICE - stock_final["2024-2025"]["qte"]
tot_verre = sum(verre_qte.values())
bouclage_rows.append([
    "Trois exercices", tot_achats, sum(non_livre.values()) or None,
    round(sum(achats_ht.values()), 2), STOCK_OUVERTURE_SERVICE,
    stock_final["2024-2025"]["qte"], round(tot_sorti, 1), round(tot_verre, 0),
    round(sum(verre_ttc.values()), 2), round(tot_sorti - tot_verre * 0.04, 2),
])

# ---------------------------------------------------------------------------
# 4. Les deux chiffres que le service imprime pour le meme produit
# ---------------------------------------------------------------------------
# Valeurs relevees sur les images du courrier (p. 65, tableau du repere D, et
# p. 69, "Repere D - Calvados : 93 litres (arrondi)").
P65 = [
    ("Exercice 1 (clos au 31/03/2023)", 3310, 997, 3100),
    ("Exercice 2 (clos au 31/03/2024)", 3002, 880, 2200),
    ("Exercice 3 (clos au 31/03/2025)", 3005, 873, 2000),
]
deux_rows = []
for lib, conso, nb, dispo in P65:
    deux_rows.append([
        lib, conso, nb, dispo, conso - dispo, nb * 4,
        round(conso / nb, 2) if nb else None,
    ])
tc = sum(x[1] for x in P65)
tn = sum(x[2] for x in P65)
td = sum(x[3] for x in P65)
deux_rows.append(["Trois exercices", tc, tn, td, tc - td, tn * 4, round(tc / tn, 2)])

# ---------------------------------------------------------------------------
# 5. L'unite reelle de chaque ligne du tableau des vins
# ---------------------------------------------------------------------------
DOC = json.load(open(PAGE, encoding="utf-8"))


def trouver(fragment):
    for s in DOC["sections"]:
        if s.get("kind") == "tableau" and fragment in s.get("titre", ""):
            return s
    raise SystemExit("tableau introuvable : " + fragment)


def nombre(s):
    s = str(s).replace(" ", " ").replace("\xa0", " ").replace(" ", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def contenance(designation):
    """Contenance en centilitres lue dans le libelle de facture."""
    u = designation.upper()
    m = re.search(r"(\d+(?:[,.]\d+)?)\s*CL", u)
    if m:
        return float(m.group(1).replace(",", "."))
    m = re.search(r"(\d+(?:[,.]\d+)?)\s*L\b", u)
    if m:
        return float(m.group(1).replace(",", ".")) * 100
    # Les demi-bouteilles d'Arbois Bethanie sont facturees « BETHANIE 37,5 »,
    # sans unite : le format est porte par le seul nombre.
    m = re.search(r"BETHANIE\s+(\d+(?:[,.]\d+)?)\b", u)
    if m:
        return float(m.group(1).replace(",", "."))
    return None


# Mots-cles de rattachement des lignes de facture a chaque ligne du service.
MOTS = {
    "Arbois Trousseau Le": ["TROUSSEAU"],
    "C du Rhone St Josep": ["ST JOSEPH", "SAINT JOSEPH"],
    "Beaujolais Moulin à": ["MOULIN A VENT"],
    "H.C. DE BEAUNE": ["BEAUNE"],
    "Arbois Blanc Béthanie 37,5 cl": ["BETHANIE 37,5"],
    "Arbois Blanc Béthanie 75 cl": ["BETHANIE 75"],
    "Arbois Chardonnay 75 cl": ["CHARDONNAY"],
    "SAVAGNIN": ["SAVAGNIN"],
    "SAINT VERAN": ["ST VERAN", "SAINT VERAN"],
    "MACON": ["MACON"],
    "Chablis": ["CHABLIS"],
    "Gewurztraminer": ["GEWURZ"],
    "VINS ROSES": ["ROSE"],
}
mesure = {k: {e: [0.0, 0.0] for e in EXOS} for k in MOTS}
for f in FACTURES["factures"]:
    exo = exercice(f["dateFacture"])
    if not exo:
        continue
    for l in f["lignes"]:
        if "MANQUANTE" in (l["conditionnement"] or "").upper():
            continue
        u = l["designation"].upper()
        qte = l["quantite"] or 0
        c = contenance(l["designation"])
        for k, mots in MOTS.items():
            if any(m in u for m in mots):
                mesure[k][exo][0] += qte
                if c:
                    mesure[k][exo][1] += qte * c

T_VINS = trouver("Vins : le tableau opposé")
unite_rows = []
for ligne in T_VINS["lignes"]:
    lib = ligne[0]["v"]
    if lib not in MOTS:
        continue
    for k, exo in enumerate(EXOS):
        dispo = nombre(ligne[1 + 3 * k]["v"])
        if dispo is None:
            continue
        bout, cl = mesure[lib][exo]
        ecart_bt = abs(dispo - bout)
        ecart_cl = abs(dispo - cl)
        verdict = "Bouteilles" if ecart_bt < ecart_cl else "Centilitres"
        unite_rows.append([
            lib, exo, dispo, round(bout), round(cl),
            "exact a la bouteille" if ecart_bt == 0 else "",
            verdict,
        ])

# ---------------------------------------------------------------------------
# 6. Bethanie : un vin, six designations de facture
# ---------------------------------------------------------------------------
beth = {}
for f in FACTURES["factures"]:
    exo = exercice(f["dateFacture"])
    if not exo:
        continue
    for l in f["lignes"]:
        u = l["designation"].upper()
        if "BETHANIE" not in u:
            continue
        des = l["designation"].split(" Ci-dessous")[0].split(" Articles Manquants")[0]
        livre = "MANQUANTE" not in (l["conditionnement"] or "").upper()
        k = (des, livre)
        beth.setdefault(k, {e: 0.0 for e in EXOS})[exo] += l["quantite"] or 0
beth_rows = [[d, "Livree" if livre else "Non livree (manquante sur le camion)",
              v["2022-2023"], v["2023-2024"], v["2024-2025"],
              sum(v.values())] for (d, livre), v in sorted(beth.items())]

# ---------------------------------------------------------------------------
# 7. La ligne CAFE : la colonne « Quantites Vendues » contre les tasses de caisse
# ---------------------------------------------------------------------------
# Libelles de cafe de la synthese produit. Le rapprochement est fait par racine
# contenue dans le libelle, pour absorber les libelles tronques par le logiciel
# de caisse (« Double Expresso Crem »), et une liste d'exclusion ecarte les
# articles qui portent le mot cafe sans etre une tasse.
CAFES = ("expresso", "cafe", "deca")
PAS_CAFES = ("sauce", "eclats", "chocolat", "crepe", "infusion", "glace", "liegeois")


def sansaccent(s):
    import unicodedata
    s = "".join(c for c in unicodedata.normalize("NFD", str(s))
                if unicodedata.category(c) != "Mn")
    return " ".join(s.lower().split())


# Ce que le service imprime sur la ligne CAFE (p. 51), en grammes.
CAFE_SERVICE = {"2022-2023": (42000, 23723, "43,52 %"), "2023-2024": (33000, 7642, "76,84 %"),
                "2024-2025": (40000, 7618, "80,96 %")}
cafe_rows = []
for i, exo in enumerate(EXOS):
    sh = xlrd.open_workbook(
        os.path.join(CAISSE, f"ANNEXE-D{i + 1}_synthese-produit_{exo}.xls")).sheet_by_index(0)
    detail = {}
    for r in range(sh.nrows):
        n = sansaccent(sh.cell_value(r, 1))
        if not any(c in n for c in CAFES) or any(c in n for c in PAS_CAFES):
            continue
        q = sh.cell_value(r, 4)
        detail[n] = detail.get(n, 0.0) + (float(q) if isinstance(q, float) else 0.0)
    tasses = sum(detail.values())
    dispo, vendues, pct = CAFE_SERVICE[exo]
    cafe_rows.append([
        exo, dispo, vendues, round(tasses, 1), round(vendues / tasses, 2),
        round(tasses * 7), pct,
        " ; ".join(f"{k} {v:g}" for k, v in sorted(detail.items())),
    ])

# ---------------------------------------------------------------------------
# 8. Les douze cellules ou les quantites vendues depassent les disponibles
# ---------------------------------------------------------------------------
# Chaque cause est etablie par une piece du dossier, nommee dans la derniere
# colonne. Les quantites de caisse sont celles de la synthese produit
# (ANNEXE-D), source que le service utilise lui-meme : ses « quantites vendues »
# du Porto, du Martini, de la Vittel 50 cl et des cidres s'en deduisent.
DOUZE = [
    ["Vins (p. 48 et 52)", "BORDEAUX", "31/03/2025", 0, 450, "cl",
     "Achat de l'exercice precedent",
     "Le service porte 2 325 cl disponibles en 2024 pour 525 cl vendus : le solde a ete bu "
     "sur l'exercice suivant, ou il n'achete plus."],
    ["Vins (p. 48 et 52)", "H. COTES DE NUITS", "31/03/2024", 0, 12950, "cl",
     "Materiellement impossible",
     "12 950 cl valent 173 bouteilles de 75 cl. Les factures de la periode portent 25 "
     "bouteilles de ce vin (12 + 6 + 6 sur le premier exercice, 1 sur le troisieme), soit "
     "1 875 cl. Le service cote lui-meme cette cellule a 0,00 % de disparition. Cette seule "
     "cellule pese 95,4 % du depassement total."],
    ["Articles vendus a la dose (p. 51)", "Martini Blanc", "31/03/2023", 400, 504, "cl",
     "Frontiere d'exercice, compensee au centilitre pres",
     "Le disponible se reconstitue exactement (500 + 0 - 100 = 400). Le deficit de 104 cl de "
     "2023 est exactement l'excedent de 104 cl de 2024 (500 disponibles, 396 vendues)."],
    ["Articles vendus a la dose (p. 51)", "Martini Blanc", "31/03/2025", 300, 366, "cl",
     "Stock d'ouverture laisse vide et demi-doses arrondies au superieur",
     "L'annexe n. 1 ne porte aucun stock de Martini au 31/03/2022. Sur trois exercices : "
     "1 300 cl achetes (13 bouteilles de 100 cl), 100 cl de stock final, 1 257 cl vendus aux "
     "quantites exactes de caisse (209,5 doses de 6 cl), que le service arrondit a 1 266 cl. "
     "Avec une bouteille a l'ouverture, le compte se ferme."],
    ["Articles vendus a l'unite (p. 53)", "Vittel Evian 50 cl", "31/03/2024", 15, 22, "unite",
     "Stock de cloture 2023 laisse vide dans l'annexe n. 1",
     "L'annexe n. 1 porte 30 unites au 31/03/2022, aucune au 31/03/2023, 25 au 31/03/2024 et "
     "14 au 31/03/2025 ; l'inventaire du 31/03/2023 ne porte pas davantage de ligne « Vittel "
     "50 cl ». Le disponible du service se reconstitue sur cette lecture (20 + 30 - 0 = 50 ; "
     "40 + 0 - 25 = 15 ; 40 + 25 - 14 = 51). Or 20 unites achetees et 30 en stock pour 21 "
     "vendues laissaient necessairement 29 unites au 31/03/2023."],
    ["Articles vendus a l'unite (p. 53)", "Granini Raisin 25 cl", "31/03/2023", 124, 417, "unite",
     "Deux perimetres differents",
     "Le disponible du bloc (525) ne couvre que les quatre bouteilles de 25 cl ; les 417 vendues "
     "sont le seul bouton de caisse « Jus de Fruit » (416,5), qui couvre aussi les jus servis "
     "depuis les cartons d'un litre. Le bloc est excedentaire les trois exercices."],
    ["Articles vendus a l'unite (p. 53)", "Granini Raisin 25 cl", "31/03/2024", 31, 360, "unite",
     "Deux perimetres differents",
     "Meme cause. Bloc : 406 disponibles pour 360 vendues."],
    ["Articles vendus a l'unite (p. 53)", "Granini Raisin 25 cl", "31/03/2025", 0, 342, "unite",
     "Deux perimetres differents",
     "Meme cause. Bloc : 414 disponibles pour 342 vendues."],
    ["Articles vendus a l'unite (p. 53)", "Cidre Sassy 33 cl", "31/03/2023", 12, 65, "unite",
     "Ventes decalees d'une ligne sur le premier exercice",
     "La caisse porte Cidre Bouche Brut 65, Cidre Bouche Doux 54,5 et cidre la Mordue 70. Le "
     "service imprime 65 sur la ligne Sassy, 55 sur la ligne Brut et 1 sur la ligne Doux. Les "
     "deux exercices suivants sont correctement apparies (53 et 48, puis 49 et 41)."],
    ["Articles vendus a l'unite (p. 53)", "Cidre Brut 75 cl", "31/03/2025", 41, 49, "unite",
     "Achats de l'exercice sous-comptes",
     "Les factures portent 108 bouteilles sur l'exercice ; avec les stocks (15 puis 22) le "
     "disponible est de 101. La meme formule reproduit exactement le service sur les deux "
     "premiers exercices (84 + 11 - 15 = 80 ; 60 + 15 - 15 = 60)."],
    ["Articles vendus a l'unite (p. 53)", "Champagne Lancon 75 cl", "31/03/2023", 0, 9, "unite",
     "Bouton de caisse generique affecte a une marque non encore achetee",
     "La caisse ne connait qu'un bouton « Champagne » (9, 7 puis 2). Le Lanson n'est achete qu'a "
     "partir du deuxieme exercice (0, 12 puis 0) ; les champagnes du premier sont le Jean "
     "Sandrin (25) et le Ruinart (8). Le bloc du service couvre les ventes : 30, 13 et 20 "
     "disponibles pour 9, 7 et 2 vendues."],
    ["Articles vendus a l'unite (p. 53)", "Champagne Lancon 75 cl", "31/03/2024", 4, 7, "unite",
     "Bouton de caisse generique affecte a une marque non encore achetee",
     "Meme cause."],
]
douze_rows = [[t, lib, exo, d, v, round(v - d), u, cause, preuve]
              for t, lib, exo, d, v, u, cause, preuve in DOUZE]

# ---------------------------------------------------------------------------
# Ecriture du classeur
# ---------------------------------------------------------------------------
TITRE = ("La Demi-Lune : bouclage physique du Calvados et unite des tableaux, partie I de la "
         "reponse du service du 04/09/2026 (consommation vendue superieure aux achats, p. 48 a 53)")


def feuille(wb, i, nom, sous_titre, headers, rows, widths):
    ws = wb.create_sheet(nom) if i else wb.active
    if not i:
        ws.title = nom
    ws["A1"] = TITRE
    ws["A1"].font = Font(bold=True, size=12)
    ws["A2"] = sous_titre
    ws["A2"].alignment = Alignment(wrap_text=True, vertical="top")
    ws.merge_cells(start_row=2, start_column=1, end_row=4, end_column=max(len(headers), 6))
    for c, (h, w) in enumerate(zip(headers, widths), start=1):
        cell = ws.cell(row=6, column=c, value=h)
        cell.font = GBLANC
        cell.fill = ENTETE
        cell.alignment = CENTRE
        cell.border = BORD
        ws.column_dimensions[openpyxl.utils.get_column_letter(c)].width = w
    for r, row in enumerate(rows, start=7):
        for c, v in enumerate(row, start=1):
            cell = ws.cell(row=r, column=c, value=v)
            cell.border = BORD
            cell.alignment = GAUCHE if c == 1 else CENTRE
            if isinstance(row[0], str) and row[0].startswith("Trois exercices"):
                cell.font = GRAS
    ws.freeze_panes = "A7"
    return ws


wb = openpyxl.Workbook()

feuille(
    wb, 0, "Calvados factures",
    "Toutes les lignes de facture Franche-Comte Boissons Services portant du Calvados, du "
    "01/04/2022 au 31/03/2025. Deux bouteilles facturees le 26/07/2024 portent la mention "
    "« M/SE MANQUANTE S/ CAMION » : elles n'ont pas ete livrees et ne sont pas comptees dans "
    "les achats. Les achats livres ressortent a "
    f"{achats['2022-2023']:.0f}, {achats['2023-2024']:.0f} puis {achats['2024-2025']:.0f} "
    f"bouteilles d'un litre, soit {tot_achats:.0f} L pour "
    f"{sum(achats_ht.values()):,.2f} EUR HT".replace(",", " "),
    ["Date de facture", "N. de facture", "Exercice", "Designation", "Conditionnement",
     "Quantite", "Prix unitaire net (EUR)", "Montant HT (EUR)", "Lecture"],
    calva_rows, [14, 12, 12, 40, 26, 10, 14, 14, 46])

feuille(
    wb, 1, "Calvados bouclage",
    "Le bouclage n'utilise aucune dose : il ne rapproche que les factures, les inventaires de "
    "cloture et la caisse. Le stock d'ouverture au 31/03/2022 n'est pas detenu par la societe : "
    "c'est celui que le service retient lui-meme dans son annexe n. 6, une bouteille. "
    f"Sur trois exercices, {tot_sorti:.0f} L sont sortis du stock et {tot_verre:.0f} doses de "
    f"Calvados ont ete vendues au verre, pour {sum(verre_ttc.values()):.2f} EUR TTC. La "
    "consommation vendue n'a depasse les achats a aucun exercice.",
    ["Exercice", "Bouteilles livrees", "Bouteilles facturees non livrees", "Achats HT (EUR)",
     "Stock d'ouverture", "Stock de cloture (inventaire)", "Volume sorti du stock (L)",
     "Doses vendues au verre", "Ventes au verre (EUR TTC)",
     "Volume sorti sans vente au verre (L, doses de 4 cl)"],
    bouclage_rows, [16, 16, 20, 14, 14, 18, 18, 16, 16, 22])

caisse_rows = verre_rows + [["", "", "", "", ""]]
for lib, v in sorted(plats.items()):
    caisse_rows.append(["Plats et desserts", lib, "",
                        round(sum(v.values()), 1),
                        f"{v['2022-2023']:g} / {v['2023-2024']:g} / {v['2024-2025']:g}"])
feuille(
    wb, 2, "Calvados caisse",
    "Ce que la caisse enregistre. En haut, les ventes au verre, libelle par libelle et exercice "
    "par exercice : le bouton porte litteralement le nom « Calvados (4cl) ». En bas, les plats et "
    "desserts dont la recette comporte du Calvados, avec le total des trois exercices puis le "
    "detail par exercice. Les quantites fractionnaires viennent des additions partagees entre "
    "plusieurs clients.",
    ["Exercice ou nature", "Libelle de caisse", "Prix unitaire TTC (EUR)",
     "Quantite", "Montant TTC (EUR) ou detail par exercice"],
    caisse_rows, [20, 30, 18, 14, 34])

feuille(
    wb, 3, "Les deux chiffres",
    "Les deux chiffres que le service imprime pour le Calvados, sur les memes trois exercices. "
    "A la page 65, le tableau du repere D donne le volume disponible et le volume consomme, sous "
    "un intitule qui annonce « a raison de 4 cl par plat ». A la page 69, le meme repere D est "
    f"recapitule a « 93 litres (arrondi) ». Le volume consomme totalise {tc} cl quand le volume "
    f"disponible totalise {td} cl : le service retranche {tc - td} cl de plus qu'il n'en a de "
    f"disponible. Rapporte aux {tn} plats qu'il compte, le volume qu'il retient correspond a "
    f"{tc / tn:.2f} cl par plat, et non a 4 cl.",
    ["Exercice (p. 65)", "Volume consomme imprime (cl)", "Nombre de plats imprime",
     "Volume disponible imprime (cl)", "Consomme moins disponible (cl)",
     "4 cl x nombre de plats (cl)", "Volume consomme / nombre de plats (cl)"],
    deux_rows, [28, 20, 18, 20, 20, 18, 20])

feuille(
    wb, 4, "Unite des lignes",
    "La colonne « Format Quantites » des tableaux du service annonce des CENTILITRES pour toutes "
    "les lignes de vins. Chaque quantite disponible imprimee est ici confrontee, sur le meme "
    "exercice, au nombre de bouteilles livrees par les factures Franche-Comte Boissons Services "
    "et au volume correspondant en centilitres. Quatre lignes sont en bouteilles, dont trois "
    "cellules exactes a la bouteille pres. Les ecarts residuels des autres lignes correspondent "
    "a la variation de stock, que le disponible du service integre et que ce controle n'integre "
    "pas.",
    ["Ligne du service", "Exercice", "Quantite disponible imprimee",
     "Bouteilles livrees (factures)", "Volume livre (cl)", "Concordance",
     "Unite reelle de la ligne"],
    unite_rows, [30, 12, 20, 18, 16, 20, 18])

feuille(
    wb, 5, "Bethanie millesimes",
    "Un seul vin, l'Arbois blanc cuvee Bethanie, est facture sous six designations distinctes : "
    "le libelle nu et quatre millesimes, pour deux contenances. Le service a neanmoins regroupe "
    "ces designations : sa quantite disponible de 186 pour l'exercice clos au 31/03/2023 est "
    "exactement le total des bouteilles de 37,5 cl livrees cette annee-la.",
    ["Designation de facture", "Livraison", "2022-2023", "2023-2024", "2024-2025",
     "Total trois exercices"],
    beth_rows, [56, 34, 14, 14, 14, 18])

feuille(
    wb, 6, "Ligne CAFE",
    "La ligne « CAFE » du tableau de la page 51 est la seule exprimee en GRAMMES. Sa colonne "
    "« Quantites Vendues » est ici confrontee au nombre de tasses reellement enregistrees en "
    "caisse, tous libelles de cafe confondus (synthese produit, ANNEXE-D). Le nombre de tasses "
    "est stable sur les trois exercices ; la colonne du service est divisee par trois entre le "
    "premier et le deuxieme. La dose implicite passe de 6,88 g a 2,22 g par tasse. Au premier "
    "exercice, une dose de 7 g reconstitue le chiffre imprime.",
    ["Exercice", "Quantites disponibles (g, service)", "Quantites vendues (g, service)",
     "Tasses enregistrees en caisse", "Grammes par tasse que cela implique",
     "Grammes qu'une dose de 7 g donnerait", "Volumes disparus imprimes par le service",
     "Detail des libelles de caisse"],
    cafe_rows, [14, 20, 20, 18, 20, 20, 18, 60])

feuille(
    wb, 7, "Douze cellules",
    "Sur les 226 cellules renseignees des quatre tableaux opposes aux pages 48, 51, 52 et 53, "
    "douze montrent des quantites vendues superieures aux quantites disponibles : ce sont les "
    "seules qui correspondent au titre de la partie I. Chacune recoit ici sa cause, etablie sur "
    "une facture, un inventaire ou la caisse. Aucune ne constate une vente sans achat.",
    ["Tableau du service", "Designation", "Exercice clos", "Quantites disponibles",
     "Quantites vendues", "Depassement", "Unite", "Cause etablie", "Piece et verification"],
    douze_rows, [30, 24, 14, 16, 16, 14, 10, 40, 86])

# Bloc des cidres, exercice clos au 31/03/2023 : le pourcentage imprime par le
# service suppose, ligne par ligne, exactement les quantites de caisse, alors
# que sa colonne « Quantites Vendues » est decalee d'un rang vers le haut.
CIDRES = [
    ("Cidre La Mordue 27 cl", 214, 70, 67.29, 70.0, "cidre la Mordue"),
    ("Cidre Sassy 33 cl", 12, 65, 100.00, 0.0, "aucun bouton Sassy en caisse"),
    ("Cidre Brut 75 cl", 80, 55, 18.75, 65.0, "Cidre Bouche Brut"),
    ("Cidre Doux 75 cl", 80, 1, 31.88, 54.5, "Cidre Bouche Doux"),
]
cidre_rows = [[lib, d, v, f"{pct:.2f} %".replace(".", ","), round(d * (1 - pct / 100), 2),
               caisse, qc, "Concorde" if abs(d * (1 - pct / 100) - qc) < 0.01 else "Ecart"]
              for lib, d, v, pct, qc, caisse in CIDRES]

feuille(
    wb, 8, "Bloc des cidres",
    "Exercice clos au 31/03/2023. Pour chaque ligne, la quantite vendue que le pourcentage "
    "imprime par le service suppose, soit disponibles x (1 - pourcentage), est comparee a la "
    "quantite reellement enregistree en caisse. Les quatre concordent. La colonne "
    "« Quantites Vendues » imprimee a cote est, elle, decalee d'un rang vers le haut a partir "
    "de la deuxieme ligne : c'est ce decalage qui fait apparaitre 65 unites vendues en face de "
    "12 disponibles sur la ligne du Cidre Sassy.",
    ["Ligne du service", "Quantites disponibles", "Quantites vendues imprimees",
     "Volumes disparus imprimes", "Ventes que ce pourcentage suppose",
     "Libelle de caisse", "Quantite de caisse", "Controle"],
    cidre_rows, [26, 18, 20, 20, 22, 26, 16, 14])

# ---------------------------------------------------------------------------
# 10. Les postes que le service dit qu'il aurait fallu corriger aussi (p. 50)
# ---------------------------------------------------------------------------
# Une dose convertit un nombre de ventes ou de plats en volume. La reduire
# reduit le volume compte comme vendu, donc AUGMENTE l'ecart entre disponible
# et vendu : aucun de ces postes ne peut, par cette voie, faire apparaitre une
# consommation superieure aux achats.
T_DOSE = trouver("Articles vendus à la dose")
T_CPLX = trouver("« Articles Complexes »")


def somme(tableau, libelles):
    d = v = 0.0
    trouves = set()
    for ligne in tableau["lignes"]:
        if ligne[0]["v"] in libelles:
            trouves.add(ligne[0]["v"])
            for k in range(3):
                d += nombre(ligne[1 + 3 * k]["v"]) or 0.0
                v += nombre(ligne[2 + 3 * k]["v"]) or 0.0
    manquants = set(libelles) - trouves
    if manquants:
        raise SystemExit("libelles introuvables : " + ", ".join(sorted(manquants)))
    return d, v


POSTES = [
    ("Le vin jaune", T_DOSE, ["Vin jaune"], "ligne « Vin jaune », p. 51"),
    ("Le vin des sauces et le vin de cuisine", T_VINS, ["VINS EN BIB"],
     "ligne « VINS EN BIB », p. 48 et 52"),
    ("Le vin de tous les cocktails, a 4 cl", T_CPLX,
     ["CREMANT", "MACVIN", "SOHO", "VODKA", "PASSOA", "TEQUILA", "PICON", "LIMONADE",
      "JUS DE FRUIT"], "tableau « Articles Complexes », p. 52"),
    ("Les sirops, a 4 cl", T_DOSE, ["SIROP A L’EAU"],
     "ligne « SIROP A L’EAU », p. 51"),
]
postes_rows = []
td = tv = 0.0
for nom, tabl, libs, src in POSTES:
    d, v = somme(tabl, libs)
    td += d
    tv += v
    postes_rows.append([nom, src, round(d), round(v), round(d - v),
                        round((d - v) / d * 100, 2), round(v / 2), round(d - v / 2),
                        round((d - v / 2) / d * 100, 2),
                        "Excedent d'achat, avant comme apres"])
postes_rows.append(["Total des postes cites", "", round(td), round(tv), round(td - tv),
                    round((td - tv) / td * 100, 2), round(tv / 2), round(td - tv / 2),
                    round((td - tv / 2) / td * 100, 2), "Excedent d'achat, avant comme apres"])

feuille(
    wb, 9, "Postes de doses",
    "Le service ecrit (p. 50) qu'etendre la correction de dose « a toutes les doses d'alcool » "
    "aurait « fortement accru » les ecarts. Poste par poste, avec ses propres tableaux : chacun "
    "des postes qu'il cite est deja excedentaire, il a ete achete plus qu'il n'a ete vendu. "
    "Reduire une dose diminue le volume compte comme vendu, donc augmente cet excedent : aucun "
    "de ces postes ne peut, par cette voie, faire apparaitre une consommation superieure aux "
    "achats.",
    ["Poste cite par le service", "Tableau d'origine", "Quantites disponibles (3 exercices)",
     "Quantites vendues (3 exercices)", "Excedent d'achat", "Excedent / disponible (%)",
     "Quantites vendues si la dose etait divisee par deux",
     "Excedent d'achat dans cette hypothese", "Excedent / disponible (%)", "Lecture"],
    postes_rows, [34, 34, 20, 20, 16, 18, 22, 20, 18, 30])

os.makedirs(OUTDIR, exist_ok=True)
wb.save(OUT)

print(f"Ecrit : {OUT}")
print(f"  Calvados : achats livres {tot_achats:.0f} L ({achats['2022-2023']:.0f} / "
      f"{achats['2023-2024']:.0f} / {achats['2024-2025']:.0f} bouteilles), "
      f"{sum(achats_ht.values()):.2f} EUR HT")
print(f"  stocks de cloture : " + " / ".join(
    f"{stock_final[e]['qte']:.0f}" for e in EXOS))
print(f"  volume sorti du stock sur la periode : {tot_sorti:.1f} L")
print(f"  ventes au verre : {tot_verre:.0f} doses, {sum(verre_ttc.values()):.2f} EUR TTC")
print(f"  service p. 65 : consomme {tc} cl, disponible {td} cl, plats {tn}, "
      f"soit {tc / tn:.3f} cl par plat")
print(f"  lignes en bouteilles : " + ", ".join(sorted(
    {r[0] for r in unite_rows if r[6] == "Bouteilles"})))
