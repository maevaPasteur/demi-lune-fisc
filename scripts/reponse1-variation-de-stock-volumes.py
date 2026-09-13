#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reponse1-variation-de-stock-volumes.py

Piece de la reponse au courrier DDFiP 39 du 04/09/2026, point 9 (p. 74)
"Volume disponible gonfle par une variation de stock erronee".

Objet : verifier, a partir des trois inventaires physiques de cloture, la
variation de stock boissons retenue par le service (compte 310200), en euros ET
en litres, en declarant toutes les conventions de contenance appliquees.

Sorties : public/documents/pieces-reponse-1/R1-variation-de-stock-en-volumes.xlsx
  1. "Recapitulatifs dates"  : totaux portes sur les pages recapitulatives datees
                               des trois inventaires, et rapprochement avec les
                               variations du compte 310200 retenues par le service.
  2. "Volumes par cloture"   : litres en stock aux 3 clotures, par categorie.
  3. "Sensibilite contenance": les trois lectures possibles des libelles et ce
                               qu'elles donnent, pour que le lecteur puisse choisir.
  4. "Detail par produit"    : chaque ligne d'inventaire, contenance, litres.
  5. "Table de contenances"  : la regle appliquee, ligne par ligne, et sa source.
  6. "Methode"               : sources, conventions et reserves.

Sources (lecture seule) :
  - public/documents/inventaires/inventaires.json  (3 inventaires physiques)
  - public/documents/inventaires/Inventaire_Demi_Lune_{2023,2024,2025}-03-31.pdf
    (pages recapitulatives datees : constantes RECAPITULATIFS ci-dessous)
"""
import os
import re
import json
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

ICI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(ICI, ".."))
INV = os.path.join(ROOT, "public/documents/inventaires/inventaires.json")
OUTDIR = os.path.join(ROOT, "public/documents/pieces-reponse-1")
OUT = os.path.join(OUTDIR, "R1-variation-de-stock-en-volumes.xlsx")

# ---------------------------------------------------------------------------
# Constantes transcrites des pieces (chaque valeur est verifiable sur le PDF cite)
# ---------------------------------------------------------------------------

# Totaux portes sur la page recapitulative DATEE de chaque inventaire.
# Ce sont les totaux du document lui-meme, pas ceux de notre transcription CSV.
RECAPITULATIFS = {
    "2023-03-31": {
        "sans_alcool": 727.70,
        "alcool": 3050.29,
        "source": ("Inventaire_Demi_Lune_2023-03-31.pdf, p. 1 : tableau dactylographie "
                   "« INVENTAIRE H.T. DEMI LUNE 31/03/2023 » (BOISSONS SANS ALCOOL 727,70 ; "
                   "ALCOOLS ET VINS 3 050,29 ; TOTAL 7 030,61). Le total ALCOOLS ET VINS "
                   "est repris en pied de la page 11 du meme PDF (« TOTAL 3050,29 »)."),
    },
    "2024-03-31": {
        "sans_alcool": 870.59,
        "alcool": 3937.07,
        "source": ("Inventaire_Demi_Lune_2024-03-31.pdf, p. 1 : « INVENTAIRE H.T. AU 31 MARS 2024 » "
                   "(Boissons sans alcool 870,59 ; Vins & Alcools 3 937,07). La page 7 du meme PDF "
                   "porte le report manuscrit « Total Sans Alcool = 870,59 / Avec Alcool = 3937,07 / "
                   "4807,66 ». La page 1 imprime « Total : 4 807,60 », soit 0,06 EUR de moins que "
                   "la somme de ses deux lignes."),
    },
    "2025-03-31": {
        "sans_alcool": 765.74,
        "alcool": 3768.51,
        "source": ("Inventaire_Demi_Lune_2025-03-31.pdf, p. 1 : « INVENTAIRE HT 31/03/2025 » "
                   "(BOISSONS 4 534,25 ; dont sans alcool 765,74 et vins et alcools 3 768,51)."),
    },
}

# Variations du compte de stock boissons retenues par le service
# (Proposition de rectification, tableau de comptabilite matiere ; reprises en
#  annexe n°7-2 pour -1 029,67 EUR ; rappelees p. 74 de la reponse du 04/09/2026).
VARIATION_SERVICE = {
    "2022-2023": -800.83,
    "2023-2024": -1029.67,
    "2024-2025": -273.41,
}

# Table de contenances : conventions appliquees, en clair.
# 1. Contenance lue dans le libelle quand il en porte une (75cl, 1L, 10L, 33cl...).
# 2. Futs de biere Affligem : la quantite inventoriee n'est pas exprimee dans la
#    meme unite d'une cloture a l'autre. Le fournisseur facture ces futs AU LITRE
#    (fiche client Franche-Comte Boissons Service du 07/03/2024, reproduite en
#    p. 2 du PDF 2024 : « AFFLIGEM BLADE 8 L 6,7 | K 8 | prix net 4,230 »). Le prix
#    unitaire porte sur l'inventaire leve donc l'ambiguite :
#      - prix unitaire voisin du prix au litre  -> la quantite est deja en litres ;
#      - prix unitaire voisin de 8 fois ce prix -> la quantite est en futs de 8 L.
# 3. Cafes, thes, infusions et lignes de reconciliation : hors litres, jamais hors euros.
# 4. Lignes de liquides dont le libelle ne porte pas de contenance alors que le meme
#    produit en porte une aux clotures suivantes (les quatre jus Granini de 2023) :
#    traitees en variante, jamais dans le chiffre principal.
SEUIL_FUT = 1.6  # prix unitaire < contenance x 1,6 => quantite deja en litres

JUS_SANS_CONTENANCE_2023 = {
    "Granini Nectar Ananas": 1.0,
    "Granini Nectar Poire": 1.0,
    "Granini Jus Orange": 1.0,
    "Granini Jus Ananas": 1.0,
}

GRAS = Font(bold=True)
GBLANC = Font(bold=True, color="FFFFFF")
ENTETE = PatternFill("solid", fgColor="0F766E")
JAUNE = PatternFill("solid", fgColor="FEF3C7")
ROUGE = PatternFill("solid", fgColor="FEE2E2")
VERT = PatternFill("solid", fgColor="D1FAE5")
CENTRE = Alignment(horizontal="center", vertical="center", wrap_text=True)
GAUCHE = Alignment(horizontal="left", vertical="center", wrap_text=True)
BORD = Border(*(4 * (Side(style="thin", color="D1D5DB"),)))

RE_CONT = re.compile(r"(\d+(?:[.,]\d+)?)\s*(cl|CL|L|l)\b")


def fr(v, dec=2):
    if v is None:
        return ""
    return f"{v:,.{dec}f}".replace(",", " ").replace(".", ",")


def contenance_libelle(libelle):
    """Contenance unitaire en litres portee dans le libelle, ou None."""
    m = RE_CONT.search(libelle)
    if not m:
        return None
    v = float(m.group(1).replace(",", "."))
    return v / 100 if m.group(2).lower() == "cl" else v


def contenance_retenue(libelle, prix_unitaire):
    """Contenance unitaire retenue, apres application de la table ci-dessus."""
    c = contenance_libelle(libelle)
    if c is None:
        return None, "pas de contenance au libelle"
    if "Affligem" in libelle and prix_unitaire is not None:
        if prix_unitaire < c * SEUIL_FUT:
            return 1.0, ("fut facture au litre : prix unitaire %s EUR voisin du prix au litre, "
                         "la quantite inventoriee est donc en litres" % fr(prix_unitaire))
        return c, ("fut compte a l'unite : prix unitaire %s EUR voisin de %s fois le prix au litre"
                   % (fr(prix_unitaire), fr(c, 0)))
    return c, "contenance lue au libelle"


DATA = json.load(open(INV, encoding="utf-8"))
INVENTAIRES = DATA["inventaires"]
DATES = [i["date"] for i in INVENTAIRES]
EXERCICES = ["2022-2023", "2023-2024", "2024-2025"]
CATS = ["alcool", "boisson_sans_alcool"]

# ---------------------------------------------------------------------------
# Agregation
# ---------------------------------------------------------------------------
def agreger(mode):
    """mode : 'table' (regle retenue), 'litteral' (libelle brut), 'jus' (table + jus 1 L 2023)."""
    vol = {d: {c: 0.0 for c in CATS} for d in DATES}
    for inv in INVENTAIRES:
        d = inv["date"]
        for l in inv["lignes"]:
            q = l["quantite"] or 0
            if mode == "litteral":
                c = contenance_libelle(l["produit"])
            else:
                c, _ = contenance_retenue(l["produit"], l.get("prixUnitaireHT"))
                if c is None and mode == "jus" and d == "2023-03-31":
                    c = JUS_SANS_CONTENANCE_2023.get(l["produit"])
            if c is not None:
                vol[d][l["categorie"]] += c * q
    return vol


VOL = agreger("table")
VOL_LIT = agreger("litteral")
VOL_JUS = agreger("jus")

eur_csv = {d: {c: 0.0 for c in CATS} for d in DATES}
sans_contenance = {d: 0 for d in DATES}
a_verifier = {d: {"n": 0, "eur": 0.0} for d in DATES}
detail = []
table_conventions = {}

for inv in INVENTAIRES:
    d = inv["date"]
    for l in inv["lignes"]:
        q = l["quantite"] or 0
        v = l["valeurHT"] or 0
        c, motif = contenance_retenue(l["produit"], l.get("prixUnitaireHT"))
        eur_csv[d][l["categorie"]] += v
        if l["fiabilite"] != "exact":
            a_verifier[d]["n"] += 1
            a_verifier[d]["eur"] += v
        if c is None:
            sans_contenance[d] += 1
        if motif != "contenance lue au libelle":
            table_conventions.setdefault((l["produit"], motif), []).append(d)
        detail.append({
            "date": d, "produit": l["produit"], "categorie": l["categorie"],
            "contenance_cl": None if c is None else round(c * 100, 1),
            "quantite": q, "litres": None if c is None else round(c * q, 3),
            "valeurHT": v, "fiabilite": l["fiabilite"], "motif": motif,
        })

# Euros : totaux des pages recapitulatives datees (le document lui-meme)
eur_recap = {d: RECAPITULATIFS[d]["sans_alcool"] + RECAPITULATIFS[d]["alcool"] for d in DATES}

wb = openpyxl.Workbook()

# ---------------------------------------------------------------------------
# 1. Recapitulatifs dates et rapprochement avec le compte 310200
# ---------------------------------------------------------------------------
ws = wb.active
ws.title = "Recapitulatifs dates"
ws["A1"] = ("Totaux portes sur la page recapitulative DATEE de chaque inventaire, "
            "et rapprochement avec la variation de stock retenue par le service")
ws["A1"].font = Font(bold=True, size=12)
cols = ["Cloture", "Boissons sans alcool (EUR HT)", "Vins et alcools (EUR HT)",
        "Total boissons (EUR HT)", "Source dans la piece"]
for j, c in enumerate(cols, start=1):
    cell = ws.cell(row=3, column=j, value=c)
    cell.font, cell.fill, cell.alignment, cell.border = GBLANC, ENTETE, CENTRE, BORD
r = 4
for d in DATES:
    R = RECAPITULATIFS[d]
    vals = [d[8:] + "/" + d[5:7] + "/" + d[:4], fr(R["sans_alcool"]), fr(R["alcool"]),
            fr(R["sans_alcool"] + R["alcool"]), R["source"]]
    for j, v in enumerate(vals, start=1):
        cell = ws.cell(row=r, column=j, value=v)
        cell.alignment = GAUCHE if j in (1, 5) else CENTRE
        cell.border = BORD
    r += 1

r += 1
ws.cell(row=r, column=1, value=(
    "Rapprochement : identite comptable « achats + variation de stock = quantites disponibles », "
    "la variation de stock etant, par convention du plan comptable, le stock initial moins le "
    "stock final (SI - SF).")).font = GRAS
r += 2
cols2 = ["Exercice", "Stock initial (EUR HT)", "Stock final (EUR HT)",
         "SI - SF calcule sur les recapitulatifs", "Variation retenue par le service (310200)",
         "Ecart"]
for j, c in enumerate(cols2, start=1):
    cell = ws.cell(row=r, column=j, value=c)
    cell.font, cell.fill, cell.alignment, cell.border = GBLANC, ENTETE, CENTRE, BORD
r += 1
ecarts = {}
for k, ex in enumerate(EXERCICES):
    serv = VARIATION_SERVICE[ex]
    if k == 0:
        si, sf, dv, ec = None, eur_recap[DATES[0]], None, None
        note_si = "stock au 31/03/2022 : non repris dans nos inventaires"
    else:
        si, sf = eur_recap[DATES[k - 1]], eur_recap[DATES[k]]
        dv = round(si - sf, 2)
        ec = round(dv - serv, 2)
        note_si = None
    vals = [ex, note_si or fr(si), fr(sf), fr(dv), fr(serv), fr(ec)]
    for j, v in enumerate(vals, start=1):
        cell = ws.cell(row=r, column=j, value=v)
        cell.alignment = GAUCHE if j in (1, 2) and note_si else CENTRE
        cell.border = BORD
    if ec is not None:
        ecarts[ex] = ec
        ws.cell(row=r, column=6).fill = VERT if abs(ec) < 0.005 else ROUGE
    r += 1

r += 1
for txt in [
    "Lecture 2023-2024 : SI - SF = %s EUR. La variation retenue par le service est de %s EUR. "
    "L'ecart est de %s EUR : la variation retenue est celle qui ressort des inventaires, au centime."
    % (fr(round(eur_recap[DATES[0]] - eur_recap[DATES[1]], 2)),
       fr(VARIATION_SERVICE["2023-2024"]), fr(ecarts.get("2023-2024", 0))),
    "Lecture 2024-2025 : le stock a BAISSE de %s EUR, donc SI - SF = %s EUR, quand la variation "
    "retenue par le service est de %s EUR. La societe ne conteste pas ce montant et n'en tire "
    "aucune demande."
    % (fr(round(eur_recap[DATES[1]] - eur_recap[DATES[2]], 2)),
       fr(round(eur_recap[DATES[1]] - eur_recap[DATES[2]], 2)),
       fr(VARIATION_SERVICE["2024-2025"])),
]:
    ws.cell(row=r, column=1, value=txt).alignment = GAUCHE
    r += 1
ws.column_dimensions["A"].width = 26
for c in "BCDE":
    ws.column_dimensions[c].width = 24
ws.column_dimensions["F"].width = 18

# ---------------------------------------------------------------------------
# 2. Volumes par cloture
# ---------------------------------------------------------------------------
ws2 = wb.create_sheet("Volumes par cloture")
ws2["A1"] = ("Stock physique de boissons aux trois clotures, EN LITRES "
             "(table de contenances declaree, feuille « Table de contenances »)")
ws2["A1"].font = Font(bold=True, size=12)
cols = ["Poste", "31/03/2023", "31/03/2024", "31/03/2025",
        "Variation 2023-2024", "Variation 2024-2025"]
for j, c in enumerate(cols, start=1):
    cell = ws2.cell(row=3, column=j, value=c)
    cell.font, cell.fill, cell.alignment, cell.border = GBLANC, ENTETE, CENTRE, BORD
lignes_vol = [
    ("Alcools et vins (litres)", [VOL[d]["alcool"] for d in DATES]),
    ("Boissons sans alcool (litres)", [VOL[d]["boisson_sans_alcool"] for d in DATES]),
    ("TOTAL boissons (litres)", [sum(VOL[d].values()) for d in DATES]),
]
r = 4
for lab, vals in lignes_vol:
    ws2.cell(row=r, column=1, value=lab).alignment = GAUCHE
    for j, v in enumerate(vals, start=2):
        ws2.cell(row=r, column=j, value=fr(v)).alignment = CENTRE
    ws2.cell(row=r, column=5, value=fr(vals[1] - vals[0])).alignment = CENTRE
    ws2.cell(row=r, column=6, value=fr(vals[2] - vals[1])).alignment = CENTRE
    if lab.startswith("TOTAL"):
        for j in range(1, 7):
            ws2.cell(row=r, column=j).font = GRAS
            ws2.cell(row=r, column=j).fill = JAUNE
    for j in range(1, 7):
        ws2.cell(row=r, column=j).border = BORD
    r += 1
r += 1
for txt in [
    "Reserve n°1 : les litres ne sont pas une grandeur homogene. Un stock de boissons additionne "
    "des futs, des bouteilles de 75 cl et des canettes de 33 cl dont le cout va de moins de 1 EUR "
    "le litre a plus de 40 EUR le litre. C'est la raison pour laquelle l'inventaire est valorise "
    "et le compte de stock tenu en euros : le tableau en euros de la premiere feuille est le seul "
    "qui se rapproche du compte 310200.",
    "Reserve n°2 : au 31/03/2025, trois lignes de reconciliation (413,00 EUR, dont 318,41 EUR "
    "d'alcools) ne portent ni produit ni contenance et n'entrent donc dans aucun litre. Le stock "
    "d'alcools en litres au 31/03/2025 est a ce titre un minorant.",
    "Reserve n°3 : au 31/03/2023, quatre lignes de jus Granini (29 unites, 84,46 EUR) ne portent "
    "pas de contenance au libelle alors que les memes produits en portent une (« 1L ») aux "
    "clotures suivantes. Voir la feuille « Sensibilite contenance ».",
]:
    ws2.cell(row=r, column=1, value=txt).alignment = GAUCHE
    r += 1
ws2.column_dimensions["A"].width = 46
for c in "BCDEF":
    ws2.column_dimensions[c].width = 18

# ---------------------------------------------------------------------------
# 3. Sensibilite contenance
# ---------------------------------------------------------------------------
ws3 = wb.create_sheet("Sensibilite contenance")
ws3["A1"] = "Ce que donnent les differentes lectures des libelles d'inventaire"
ws3["A1"].font = Font(bold=True, size=12)
cols = ["Lecture", "31/03/2023 (L)", "31/03/2024 (L)", "31/03/2025 (L)",
        "Variation 2023-2024 (L)", "Variation 2024-2025 (L)", "Observation"]
for j, c in enumerate(cols, start=1):
    cell = ws3.cell(row=3, column=j, value=c)
    cell.font, cell.fill, cell.alignment, cell.border = GBLANC, ENTETE, CENTRE, BORD
variantes = [
    ("Table de contenances declaree (retenue)", VOL,
     "Les futs Affligem sont ramenes a l'unite reelle a partir du prix unitaire porte sur l'etat."),
    ("Lecture litterale du libelle, sans table", VOL_LIT,
     "Compte 32 futs de 8 L au 31/03/2024, soit 256 L d'Affligem pour 135,36 EUR, c'est a dire "
     "0,53 EUR le litre : contredit par la facture du fournisseur (4,23 EUR le litre)."),
    ("Table declaree + jus Granini 2023 a 1 L", VOL_JUS,
     "Homogeneise les libelles de jus entre 2023 et 2024 ; ramene la hausse des boissons sans "
     "alcool a un niveau negligeable."),
]
r = 4
for lab, v, obs in variantes:
    tot = [sum(v[d].values()) for d in DATES]
    vals = [lab, fr(tot[0]), fr(tot[1]), fr(tot[2]),
            fr(tot[1] - tot[0]), fr(tot[2] - tot[1]), obs]
    for j, x in enumerate(vals, start=1):
        cell = ws3.cell(row=r, column=j, value=x)
        cell.alignment = GAUCHE if j in (1, 7) else CENTRE
        cell.border = BORD
    if lab.startswith("Table de contenances declaree"):
        for j in range(1, 8):
            ws3.cell(row=r, column=j).fill = JAUNE
    r += 1
ws3.column_dimensions["A"].width = 40
for c in "BCDEF":
    ws3.column_dimensions[c].width = 18
ws3.column_dimensions["G"].width = 70

# ---------------------------------------------------------------------------
# 4. Detail par produit
# ---------------------------------------------------------------------------
ws4 = wb.create_sheet("Detail par produit")
cols = ["Cloture", "Produit (libelle d'inventaire)", "Categorie",
        "Contenance unitaire retenue (cl)", "Quantite", "Volume (litres)",
        "Valeur (EUR HT)", "Fiabilite de la transcription", "Regle appliquee"]
for j, c in enumerate(cols, start=1):
    cell = ws4.cell(row=1, column=j, value=c)
    cell.font, cell.fill, cell.alignment, cell.border = GBLANC, ENTETE, CENTRE, BORD
r = 2
for d in detail:
    vals = [d["date"], d["produit"], d["categorie"],
            fr(d["contenance_cl"], 1), fr(d["quantite"], 0),
            fr(d["litres"], 3), fr(d["valeurHT"]), d["fiabilite"], d["motif"]]
    for j, v in enumerate(vals, start=1):
        cell = ws4.cell(row=r, column=j, value=v)
        cell.alignment = GAUCHE if j in (2, 9) else CENTRE
        cell.border = BORD
    r += 1
ws4.column_dimensions["A"].width = 14
ws4.column_dimensions["B"].width = 44
for c in "CDEFGH":
    ws4.column_dimensions[c].width = 16
ws4.column_dimensions["I"].width = 62
ws4.freeze_panes = "A2"

# ---------------------------------------------------------------------------
# 5. Table de contenances
# ---------------------------------------------------------------------------
ws5 = wb.create_sheet("Table de contenances")
regles = [
    ("1. Contenance portee au libelle",
     "Retenue telle quelle : « Cremant du Jura 75cl » = 0,75 L, « BIB Rose 10L » = 10 L, "
     "« Coca-Cola 33cl » = 0,33 L."),
    ("2. Futs de biere Affligem",
     "Le fournisseur facture ces futs AU LITRE : fiche client Franche-Comte Boissons Service du "
     "07/03/2024, reproduite p. 2 du PDF d'inventaire 2024, ligne « AFFLIGEM BLADE 8 L 6,7 | K 8 | "
     "prix net 4,230 ». Le prix unitaire porte sur l'etat indique donc l'unite de la quantite "
     "inventoriee : voisin du prix au litre, la quantite est en litres ; voisin de huit fois ce "
     "prix, elle est en futs de 8 L. Application : 31/03/2023, 4 unites a 4,07 EUR = 16,28 EUR, "
     "soit 4 litres ; 31/03/2024, 32 unites a 4,23 EUR = 135,36 EUR, soit 32 litres (quatre futs) ; "
     "31/03/2025, 5 unites a 33,84 EUR = 169,20 EUR, soit 5 futs, c'est a dire 40 litres."),
    ("3. Cafes, thes et infusions",
     "Produits non liquides en stock : exclus des litres, jamais des euros."),
    ("4. Lignes de reconciliation",
     "Trois lignes au 31/03/2025 (413,00 EUR) ne designent aucun produit : exclues des litres, "
     "conservees dans les euros."),
    ("5. Liquides sans contenance au libelle",
     "Quatre jus Granini au 31/03/2023 (29 unites, 84,46 EUR) et une ligne Routin (2 unites, "
     "7,64 EUR). Aucune contenance ne leur est attribuee dans le chiffre principal ; l'effet d'une "
     "attribution a 1 L figure dans la feuille « Sensibilite contenance »."),
]
r = 1
for k, v in regles:
    ws5.cell(row=r, column=1, value=k).font = GRAS
    ws5.cell(row=r, column=1).alignment = GAUCHE
    ws5.cell(row=r, column=2, value=v).alignment = GAUCHE
    r += 1
r += 1
ws5.cell(row=r, column=1, value="Lignes ou une regle autre que la lecture directe du libelle s'applique").font = GRAS
r += 1
for (produit, motif), dts in sorted(table_conventions.items()):
    if motif == "pas de contenance au libelle":
        continue
    ws5.cell(row=r, column=1, value=produit).alignment = GAUCHE
    ws5.cell(row=r, column=2, value="%s (clotures : %s)" % (motif, ", ".join(dts))).alignment = GAUCHE
    r += 1
ws5.column_dimensions["A"].width = 42
ws5.column_dimensions["B"].width = 110

# ---------------------------------------------------------------------------
# 6. Methode
# ---------------------------------------------------------------------------
ws6 = wb.create_sheet("Methode")
notes = [
    ("Objet", "Verifier la variation de stock boissons retenue par le service (compte 310200) a "
              "partir des trois inventaires physiques de cloture, en euros et en litres."),
    ("Source des euros", "Pages recapitulatives datees des trois PDF d'inventaire (feuille "
                         "« Recapitulatifs dates »). Ce sont les totaux du document, pas ceux de "
                         "notre transcription."),
    ("Source des litres", "public/documents/inventaires/inventaires.json, transcription ligne a "
                          "ligne des memes PDF."),
    ("Ecart entre les deux sources", "Notre transcription CSV retient un perimetre strictement "
                                     "« boissons » : elle exclut les biscuits, le sucre, les "
                                     "pailles et les consommables inscrits sur les memes pages. "
                                     "Elle porte en outre une colonne de fiabilite : %s lignes sur "
                                     "%s (%s EUR) y sont marquees « a verifier ». Les totaux en "
                                     "euros retenus ici sont ceux du document, non ceux du CSV."
                                     % (sum(a_verifier[d]["n"] for d in DATES),
                                        sum(len(i["lignes"]) for i in INVENTAIRES),
                                        fr(sum(a_verifier[d]["eur"] for d in DATES)))),
    ("Convention de signe", "Variation de stock = stock initial moins stock final (SI - SF), "
                            "convention du plan comptable et de l'identite « achats + variation de "
                            "stock = quantites disponibles » que le service rappelle p. 74."),
    ("Contenances", "Voir la feuille « Table de contenances ». Aucune contenance n'est retenue sans "
                    "regle ecrite ; les effets des lectures concurrentes sont chiffres dans la "
                    "feuille « Sensibilite contenance »."),
    ("Variation retenue par le service", "-800,83 EUR, -1 029,67 EUR et -273,41 EUR (compte de "
                                         "stock boissons). Le montant de -1 029,67 EUR figure "
                                         "egalement en annexe n°7-2 de la proposition de rectification."),
    ("Genere par", "scripts/reponse1-variation-de-stock-volumes.py"),
]
r = 1
for k, v in notes:
    ws6.cell(row=r, column=1, value=k).font = GRAS
    ws6.cell(row=r, column=1).alignment = GAUCHE
    ws6.cell(row=r, column=2, value=v).alignment = GAUCHE
    r += 1
ws6.column_dimensions["A"].width = 32
ws6.column_dimensions["B"].width = 110

os.makedirs(OUTDIR, exist_ok=True)
wb.save(OUT)
print("OK ->", OUT)
print("Euros recapitulatifs :", {d: round(eur_recap[d], 2) for d in DATES})
print("SI-SF               :", {EXERCICES[k]: round(eur_recap[DATES[k-1]] - eur_recap[DATES[k]], 2)
                                for k in (1, 2)})
print("Service             :", VARIATION_SERVICE)
print("Ecarts              :", ecarts)
print("Litres (table)      :", {d: round(sum(VOL[d].values()), 2) for d in DATES})
print("Litres (litteral)   :", {d: round(sum(VOL_LIT[d].values()), 2) for d in DATES})
print("Litres (table+jus)  :", {d: round(sum(VOL_JUS[d].values()), 2) for d in DATES})
print("a_verifier          :", {d: (a_verifier[d]["n"], round(a_verifier[d]["eur"], 2)) for d in DATES})
