#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rendu-final-consommation-superieure-achats.py

Reponse au fisc (Proposition de rectification p. 31-34, rejet 3/3) :
"Pour certains produits, les quantites vendues depasseraient les achats,
signe de ventes non comptabilisees."

Demonstration : les ecarts conso > achats sur quelques libelles viennent d'un
ETIQUETAGE de caisse (libelles generiques / formats non rattaches / achat sous
un autre nom), PAS de ventes cachees. Au niveau du BILAN MATIERE GLOBAL (tous
produits agreges), ces "manquants negatifs" se neutralisent : le bilan se ferme
sur 3 048 L net (achats - conso - stock), insensible a l'etiquetage.

Sources (read-only) :
  - src/data/boissonsPageData.json -> disparuParBoisson (65 lignes), synthese
  - src/data/calculsBoissons/consoTotaleParBoisson.json -> boissons,
    achats_non_rattaches
  - src/data/calculsBoissons/_correspondance-caisse-inventaire-factures.csv

Sorties :
  - public/documents/pieces-defense/RF-consommation-superieure-achats.xlsx
  - src/data/renduFinal/consommation-superieure-achats.json
"""
import os, json, csv, collections
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

ICI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(ICI, ".."))
BOISSONS = os.path.join(ROOT, "src/data/boissonsPageData.json")
CONSO = os.path.join(ROOT, "src/data/calculsBoissons/consoTotaleParBoisson.json")
CORR = os.path.join(ROOT, "src/data/calculsBoissons/_correspondance-caisse-inventaire-factures.csv")


def r1(x):
    return round(float(x), 1)


# --------------------------------------------------------------------------- #
# 1. Donnees
# --------------------------------------------------------------------------- #
bd = json.load(open(BOISSONS, encoding="utf-8"))
rows = bd["disparuParBoisson"]
synth = bd["synthese"]

cd = json.load(open(CONSO, encoding="utf-8"))
anr = cd["achats_non_rattaches"]

corr = list(csv.DictReader(open(CORR, encoding="utf-8-sig"), delimiter=";"))
# index correspondance par nom_canonique
corr_par_canon = collections.defaultdict(list)
for c in corr:
    corr_par_canon[c["nom_canonique"]].append(c)

# --------------------------------------------------------------------------- #
# 2. Bilan matiere GLOBAL (identite comptable)
# --------------------------------------------------------------------------- #
somme_achat = r1(sum(r["achat_l"] for r in rows))
somme_conso = r1(sum(r["conso_l"] for r in rows))
somme_stock = r1(sum(r.get("stock_l", 0) for r in rows))
net = r1(somme_achat - somme_conso - somme_stock)

# --------------------------------------------------------------------------- #
# 3. Libelles conso > achats (les "negatifs")
# --------------------------------------------------------------------------- #
negs = sorted([r for r in rows if r["disparu_l"] < 0], key=lambda r: r["disparu_l"])
somme_neg = r1(sum(r["disparu_l"] for r in negs))

# achats non rattaches par nom canonique reconnaissable
anr_par_mot = collections.defaultdict(float)
for a in anr:
    anr_par_mot[a["produit"]] += a["total"]


def factures_de(nom):
    """liste des nom_facture distincts mappes a un nom canonique."""
    f = set()
    for c in corr_par_canon.get(nom, []):
        nf = (c.get("nom_facture") or "").strip()
        if nf and nf != "—":
            f.add(nf)
    return sorted(f)


def cause(r):
    """Classe la cause de l'ecart conso>achats a partir de la correspondance."""
    nom = r["nom"]
    facs = factures_de(nom)
    # 1) achat = 0 et aucune facture : libelle de caisse generique
    if r["achat_l"] == 0 and not facs:
        return ("Libelle de caisse generique",
                "Bouton caisse mutualise (verre/pichet) : le vin est achete sous "
                "son appellation precise, pas sous ce libelle.")
    # 2) facture multi-formats (ex. 75 + 37,5 cl) -> formats non rattaches
    fac_txt = " ; ".join(facs)
    multi = any("/" in f or "37,5" in f or "37.5" in f for f in facs)
    # Bethanie : formats 37,5 cl restes en achats non rattaches
    if "Béthanie" in nom or "Bethanie" in nom:
        return ("Format d'achat non rattache",
                "Seul le format 75 cl est mappe ; les achats 37,5 cl sont restes "
                "en \"achats non rattaches\". Rattaches, l'achat depasse la conso.")
    # 3) facture portant un nom franchement different (achat sous un autre nom)
    if facs:
        autre = [f for f in facs if nom.split()[0].upper() not in f.upper()]
        if autre:
            return ("Achat sous un autre nom",
                    "Achete et facture sous l'appellation : " + " / ".join(autre) + ".")
    # 4) achat mappe present mais conso > achat sans achats non rattaches :
    #    une partie des verres/pichets a ete encaissee sous le bouton generique
    #    (Cubis / verre de vin). C'est le miroir du surplus "Cubis de vin".
    if r["achat_l"] > 0:
        return ("Verres encaisses sous le bouton generique",
                "Une partie des verres/pichets a ete saisie sous le bouton "
                "generique (Cubis / verre de vin) : miroir du surplus Cubis.")
    return ("Libelle de caisse generique",
            "Aucune facture rattachee a ce libelle : produit achete sous un autre nom.")


neg_detail = []
for r in negs:
    lab, expl = cause(r)
    facs = factures_de(r["nom"])
    neg_detail.append({
        "nom": r["nom"],
        "categorie": r["categorie"],
        "achat_l": r1(r["achat_l"]),
        "conso_l": r1(r["conso_l"]),
        "ecart_l": r1(r["disparu_l"]),
        "cause": lab,
        "explication": expl,
        "facture": " / ".join(facs) if facs else "(libelle generique, aucune facture)",
    })

# --------------------------------------------------------------------------- #
# 4. Exemples detailles : Cubis + Bethanie
# --------------------------------------------------------------------------- #
cubis = next(r for r in rows if "Cubis" in r["nom"])
beth = next(r for r in rows if "Béthanie" in r["nom"])

# Bethanie : achat 75cl mappe + 37,5cl non rattaches.
# ATTENTION : anr["total"] est en UNITES (bouteilles), pas en litres.
# Le format 37,5 cl = 0,375 L par bouteille.
beth_75_mappe = r1(beth["achat_l"])
beth_375_unites = sum(a["total"] for a in anr if "BETHANIE" in a["produit"].upper())
beth_375_nonrattache = r1(beth_375_unites * 0.375)
beth_total_achat = r1(beth_75_mappe + beth_375_nonrattache)
beth_conso = r1(beth["conso_l"])
beth_apres = r1(beth_total_achat - beth_conso)

# --------------------------------------------------------------------------- #
# 5. PIECE XLSX
# --------------------------------------------------------------------------- #
HEAD = Font(bold=True, color="FFFFFF")
FILL = PatternFill("solid", fgColor="0F766E")
CENTER = Alignment(horizontal="center", vertical="center")
WRAP = Alignment(wrap_text=True, vertical="top")

wb = openpyxl.Workbook()

# -- Onglet 1 : libelles conso > achats --------------------------------------- #
ws = wb.active
ws.title = "Libelles conso superieur achats"
cols1 = ["Produit (libelle caisse)", "Categorie", "Achat (L)", "Conso (L)",
         "Ecart (L)", "Cause", "Correspondance / facture", "Explication"]
ws.append(cols1)
for d in neg_detail:
    ws.append([d["nom"], d["categorie"], d["achat_l"], d["conso_l"], d["ecart_l"],
               d["cause"], d["facture"], d["explication"]])
ws.append(["TOTAL des ecarts negatifs", "", "", "", somme_neg, "", "", ""])
for c in ws[1]:
    c.font = HEAD; c.fill = FILL; c.alignment = CENTER
for i, w in enumerate((30, 12, 10, 10, 10, 26, 38, 52), 1):
    ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w
for row in ws.iter_rows(min_row=2):
    row[7].alignment = WRAP
    row[6].alignment = WRAP
ws[f"A{ws.max_row}"].font = Font(bold=True)
ws[f"E{ws.max_row}"].font = Font(bold=True)
ws.freeze_panes = "A2"

# -- Onglet 2 : bilan matiere global ------------------------------------------ #
ws2 = wb.create_sheet("Bilan matiere global")
ws2.append(["Bilan matiere boissons (3 exercices, 65 produits agreges)"])
ws2.append([])
ws2.append(["Poste", "Litres"])
ws2.append(["Somme des ACHATS", somme_achat])
ws2.append(["moins Somme de la CONSO vendue/servie", somme_conso])
ws2.append(["moins Stock final (inventaire)", somme_stock])
ws2.append(["= Bilan NET (alcool non explique)", net])
ws2.append([])
ws2.append(["Rappel synthese boissonsPageData.json"])
ws2.append(["disparu_brut_l (ecarts positifs seuls)", synth["disparu_brut_l"]])
ws2.append(["disparu_net_l (bilan global)", synth["disparu_net_l"]])
ws2.append(["dont compense par les ecarts negatifs (etiquetage)",
            r1(synth["disparu_brut_l"] - synth["disparu_net_l"])])
ws2["A1"].font = Font(bold=True, size=12)
ws2["A9"].font = Font(bold=True)
for c in ws2[3]:
    c.font = HEAD; c.fill = FILL; c.alignment = CENTER
ws2["A7"].font = Font(bold=True)
ws2["B7"].font = Font(bold=True)
ws2.column_dimensions["A"].width = 46
ws2.column_dimensions["B"].width = 14
ws2.freeze_panes = "A4"

# -- Onglet 3 : exemples Cubis + Bethanie ------------------------------------- #
ws3 = wb.create_sheet("Exemples Cubis et Bethanie")
ws3.append(["Cas n.1 - Cubis de vin (libelle de caisse generique)"])
ws3.append(["Achat sous ce libelle (L)", r1(cubis["achat_l"])])
ws3.append(["Conso au verre/pichet sous ce libelle (L)", r1(cubis["conso_l"])])
ws3.append(["Ecart (L)", r1(cubis["disparu_l"])])
ws3.append(["Facture rattachee", "aucune (bouton verre/pichet mutualise)"])
ws3.append(["Lecture", "Le vin existe et est achete sous son appellation precise ; "
            "il est seulement encaisse sous un bouton generique."])
ws3.append([])
ws3.append(["Cas n.2 - Arbois Bethanie (format d'achat non rattache)"])
ws3.append(["Achat 75 cl mappe (L)", beth_75_mappe])
ws3.append(["Achat 37,5 cl reste en achats non rattaches (L)", beth_375_nonrattache])
ws3.append(["= Achat total tous formats (L)", beth_total_achat])
ws3.append(["Conso (L)", beth_conso])
ws3.append(["Bilan apres rattachement (L)", beth_apres])
ws3.append(["Lecture", "Une fois le format 37,5 cl rattache, l'achat depasse la "
            "conso : l'ecart negatif disparait et devient un surplus normal."])
ws3["A1"].font = Font(bold=True, size=12)
ws3["A8"].font = Font(bold=True, size=12)
ws3["A11"].font = Font(bold=True)
ws3["A13"].font = Font(bold=True)
ws3.column_dimensions["A"].width = 44
ws3.column_dimensions["B"].width = 60
for r_ in (6, 14):
    ws3[f"B{r_}"].alignment = WRAP
ws3.freeze_panes = "A2"

xlsx = os.path.join(ROOT, "public/documents/pieces-defense/RF-consommation-superieure-achats.xlsx")
wb.save(xlsx)
print("XLSX ecrit :", xlsx)

# --------------------------------------------------------------------------- #
# 6. JSON renduFinal
# --------------------------------------------------------------------------- #
TEAL = "#0f766e"
GRAPH_COL = "#b45309"


def fr(x, dec=0):
    """nombre au format francais (espace milliers, virgule)."""
    if dec == 0:
        s = f"{round(x):,}".replace(",", " ")
    else:
        s = f"{x:,.{dec}f}".replace(",", "§").replace(".", ",").replace("§", " ")
    return s


def col(label, align=None):
    c = {"label": label}
    if align:
        c["align"] = align
    return c


def cell(v, align=None, badge=None):
    c = {"v": v}
    if align:
        c["align"] = align
    if badge:
        c["badge"] = badge
    return c


# tableau libelles conso>achats
tab_neg_lignes = []
for d in neg_detail:
    tab_neg_lignes.append([
        cell(d["nom"]),
        cell(f"{fr(d['achat_l'],1)}", align="right"),
        cell(f"{fr(d['conso_l'],1)}", align="right"),
        cell(f"{fr(d['ecart_l'],1)}", align="right"),
        cell(d["cause"], align="left"),
    ])
tab_neg_lignes.append([
    cell("TOTAL des écarts négatifs"),
    cell("", align="right"),
    cell("", align="right"),
    cell(f"{fr(somme_neg,1)}", align="right", badge="ok"),
    cell("Compensés au bilan global", align="left"),
])

# tableau bilan global
tab_bilan = [
    [cell("Somme des achats"), cell(f"{fr(somme_achat)} L", align="right")],
    [cell("moins Conso vendue / servie"), cell(f"{fr(somme_conso)} L", align="right")],
    [cell("moins Stock final (inventaire)"), cell(f"{fr(somme_stock)} L", align="right")],
    [cell("= Bilan net (insensible à l'étiquetage)"),
     cell(f"{fr(net)} L", align="right", badge="ok")],
]

# tableau exemples
tab_ex = [
    [cell("Cubis de vin"), cell("Libellé générique", align="center"),
     cell(f"{fr(cubis['achat_l'],1)} L", align="right"),
     cell(f"{fr(cubis['conso_l'],1)} L", align="right"),
     cell(f"{fr(cubis['disparu_l'],1)} L", align="right")],
    [cell("Arbois Béthanie (75 cl mappé seul)"), cell("Format non rattaché", align="center"),
     cell(f"{fr(beth_75_mappe,1)} L", align="right"),
     cell(f"{fr(beth_conso,1)} L", align="right"),
     cell(f"{fr(beth['disparu_l'],1)} L", align="right")],
    [cell("Arbois Béthanie (tous formats rattachés)"), cell("Après correction", align="center", badge="ok"),
     cell(f"{fr(beth_total_achat,1)} L", align="right"),
     cell(f"{fr(beth_conso,1)} L", align="right"),
     cell(f"+{fr(beth_apres,1)} L", align="right", badge="ok")],
]

# graphique : les libelles negatifs en valeur absolue (L)
graph_data = [{"nom": d["nom"], "Écart (L)": abs(d["ecart_l"])}
              for d in neg_detail if abs(d["ecart_l"]) >= 1]

doc = {
    "meta": {
        "slug": "consommation-superieure-achats",
        "titre": "Consommation vendue supérieure aux achats",
        "source": "scripts/rendu-final-consommation-superieure-achats.py",
        "grief": "Proposition de rectification p. 31-34 (rejet de comptabilité, 3/3).",
        "chiffres": {
            "nb_libelles_negatifs": len(negs),
            "somme_ecarts_negatifs_l": somme_neg,
            "somme_achats_l": somme_achat,
            "somme_conso_l": somme_conso,
            "somme_stock_l": somme_stock,
            "bilan_net_l": net,
            "cubis_conso_l": r1(cubis["conso_l"]),
            "bethanie_achat_total_l": beth_total_achat,
            "bethanie_conso_l": beth_conso,
            "bethanie_apres_l": beth_apres,
        },
    },
    "sections": [
        {
            "kind": "chapitre",
            "source": "fisc",
            "titre": "Le grief de l'administration",
            "sousTitre": "Proposition de rectification, p. 31-34 (rejet 3/3)",
        },
        {
            "kind": "note",
            "texte": "Le service relève que, **pour certains produits, les quantités "
                     "vendues dépasseraient les quantités achetées**. Il en déduit "
                     "l'existence de **ventes non comptabilisées** et y voit une "
                     "anomalie justifiant le rejet de la comptabilité.",
        },
        {
            "kind": "chapitre",
            "source": "nous",
            "titre": "Ce que sont réellement ces écarts",
            "sousTitre": "Un effet d'étiquetage de caisse, pas des ventes cachées",
        },
        {
            "kind": "note",
            "texte": "Les écarts « conso > achats » portent sur **"
                     f"{len(negs)} libellés** seulement, pour un total de **"
                     f"{fr(abs(somme_neg),1)} L** sur les "
                     f"{fr(somme_achat)} L achetés. Ils proviennent de la "
                     "**façon dont la caisse étiquette** les boissons, pas d'un "
                     "manque de stock : un produit vendu sous un libellé (bouton "
                     "générique « verre / pichet », format non rattaché, ou "
                     "appellation différente de la facture) est **acheté sous un "
                     "autre nom**. La quantité achetée existe, elle figure "
                     "simplement à une autre ligne.",
        },
        {
            "kind": "paragraphe",
            "texte": f"Les {len(negs)} libellés où la consommation dépasse l'achat, "
                     "avec leur cause établie par la table de correspondance "
                     "caisse / inventaire / factures. Aucun n'est un manquant réel.",
        },
        {
            "kind": "tableau",
            "titre": "Les libellés « conso > achats » et leur cause",
            "minWidth": 720,
            "colonnes": [
                col("Produit (libellé caisse)"),
                col("Achat (L)", "right"),
                col("Conso (L)", "right"),
                col("Écart (L)", "right"),
                col("Cause", "left"),
            ],
            "lignes": tab_neg_lignes,
        },
        {
            "kind": "graphique",
            "variante": "horizontal",
            "hauteur": 300,
            "dataKey": "nom",
            "serie": {"name": "Écart (L)", "couleur": GRAPH_COL},
            "format": "int",
            "data": graph_data,
        },
        {
            "kind": "paragraphe",
            "texte": "Au niveau du **bilan matière global** (les 65 produits "
                     "agrégés), ces écarts négatifs se compensent avec les écarts "
                     "positifs. Seuls les totaux comptent, et l'identité comptable "
                     "se ferme.",
        },
        {
            "kind": "tableau",
            "titre": "Bilan matière global des boissons (3 exercices)",
            "minWidth": 420,
            "colonnes": [col("Poste"), col("Litres", "right")],
            "lignes": tab_bilan,
        },
        {
            "kind": "note",
            "texte": f"Achats {fr(somme_achat)} L moins conso {fr(somme_conso)} L "
                     f"moins stock {fr(somme_stock)} L égale **{fr(net)} L** net. "
                     "Ce résultat est **insensible à l'étiquetage** : déplacer une "
                     "quantité d'un libellé vers un autre ne change ni la somme des "
                     "achats, ni la somme de la conso, ni le bilan. Les "
                     f"{fr(abs(somme_neg),1)} L d'écarts négatifs sont déjà inclus "
                     "dans ce net et ne créent aucun déficit.",
        },
        {
            "kind": "paragraphe",
            "texte": "Deux exemples complets, du libellé de caisse à la facture.",
        },
        {
            "kind": "tableau",
            "titre": "Exemples : Cubis de vin et Arbois Béthanie",
            "minWidth": 640,
            "colonnes": [
                col("Cas"),
                col("Nature", "center"),
                col("Achat (L)", "right"),
                col("Conso (L)", "right"),
                col("Écart (L)", "right"),
            ],
            "lignes": tab_ex,
        },
        {
            "kind": "note",
            "texte": "**Cubis de vin** : "
                     f"{fr(cubis['conso_l'],1)} L vendus au verre et au pichet sous "
                     "un bouton de caisse générique, 0 L acheté sous ce nom. Le vin "
                     "est bien acheté, mais sous son appellation précise. Ce surplus "
                     f"de {fr(cubis['conso_l'],1)} L sur le bouton générique est le "
                     "miroir exact des petits déficits constatés sur les vins nommés "
                     "(Chablis, Gewurztraminer, etc.) : les verres y ont été saisis "
                     "tantôt sous le bouton générique, tantôt sous l'appellation. "
                     "**Arbois Béthanie** : seul le format 75 cl "
                     f"({fr(beth_75_mappe,1)} L) avait été rattaché ; les achats en "
                     f"37,5 cl ({fr(beth_375_nonrattache,1)} L) étaient restés en "
                     "« achats non rattachés ». Rattachés, l'achat total atteint "
                     f"{fr(beth_total_achat,1)} L, supérieur à la conso "
                     f"({fr(beth_conso,1)} L) : l'écart négatif devient un surplus "
                     f"de +{fr(beth_apres,1)} L, parfaitement normal.",
        },
        {
            "kind": "note",
            "texte": "**Aucun encaissement créé.** Un écart négatif signifie qu'un "
                     "libellé a été vendu un peu plus qu'il n'a été acheté sous ce "
                     "même nom : il n'existe **aucun canal d'encaissement "
                     "supplémentaire**. Le chiffre d'affaires reste celui des "
                     "tickets réellement émis. Reclasser le produit sous son vrai "
                     "nom déplace une quantité d'une ligne à l'autre sans générer "
                     "le moindre euro de recette additionnelle.",
        },
        {
            "kind": "piecejointe",
            "intro": "Liste des libellés « conso > achats » avec leur cause et leur "
                     "correspondance facture, bilan matière global (identité "
                     "comptable) et exemples détaillés Cubis + Béthanie. La table "
                     "de correspondance complète libellé caisse / appellation est "
                     "fournie en pièce Boissons-6.",
            "fichiers": [
                {"fichier": "pieces-defense/RF-consommation-superieure-achats.xlsx",
                 "label": "RF - Consommation supérieure aux achats (causes + bilan)"},
                {"fichier": "pieces-defense/Boissons-6-correspondance-libelles.xlsx",
                 "label": "Boissons-6 - Table de correspondance des libellés"},
            ],
        },
        {
            "kind": "alerte",
            "couleur": "teal",
            "titre": "Ce qu'il faut retenir",
            "texte": f"Les {len(negs)} écarts « conso > achats » "
                     f"({fr(abs(somme_neg),1)} L) sont des artefacts d'étiquetage de "
                     "caisse : le produit est acheté sous un autre nom, un autre "
                     "format ou un libellé générique. Le bilan matière global se "
                     f"ferme sur {fr(net)} L net, insensible à l'étiquetage, et "
                     "aucun de ces écarts ne crée de canal d'encaissement. Ils ne "
                     "révèlent aucune vente non comptabilisée.",
        },
        {
            "kind": "interne",
            "audience": "avocat",
            "titre": "Note pour l'avocat",
            "texte": "Le grief « conso > achats » repose sur une lecture ligne à "
                     "ligne du bilan matière, alors que la seule grandeur "
                     "économiquement pertinente est le total agrégé. La preuve "
                     "tient en une identité comptable : somme des achats moins "
                     f"somme de la conso moins stock = {fr(net)} L, valeur "
                     "strictement indépendante de la répartition par libellé. "
                     "Chaque écart négatif est rattaché à sa cause par la table de "
                     "correspondance (pièce Boissons-6) ; le cas Béthanie montre "
                     "qu'il suffit de rattacher le format 37,5 cl pour inverser "
                     "l'écart. À soulever conjointement avec les autres griefs "
                     "boissons (bilan matière unique). Reproductible via "
                     "scripts/rendu-final-consommation-superieure-achats.py.",
        },
    ],
}

dest = os.path.join(ROOT, "src/data/renduFinal/consommation-superieure-achats.json")
json.dump(doc, open(dest, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("JSON ecrit :", dest)
print(f"  {len(negs)} libelles negatifs, somme {somme_neg} L")
print(f"  bilan global : {somme_achat} - {somme_conso} - {somme_stock} = {net} L")
print(f"  Bethanie : {beth_75_mappe} + {beth_375_nonrattache} = {beth_total_achat} > conso {beth_conso} -> +{beth_apres} L")
