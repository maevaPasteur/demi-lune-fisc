#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rendu-final-coefficients-de-revente.py
Bloc « Faiblesse des coefficients de revente » du Rendu final (reponse au fisc,
Proposition de rectification p. 34-37, rejet 3/3).

Grief : des coefficients de marge juges faibles (achats / CA) traduiraient une
minoration de recettes. Le service brandit un coefficient « liquides » d'environ
3,1 et l'applique pour reconstituer un CA de 575 253 € contre 435 525 € declares.

Demonstration :
  (1) Un coefficient BRUT (CA au prix carte / achat) suppose que 100 % de
      l'alcool achete est revendu au verre au prix catalogue. C'est faux.
  (2) Une part importante de l'alcool n'est JAMAIS revendue au verre :
      - cuisine (fondues, babas, flambage, sauces) : 566 L
      - alcool des menus, non detaille en caisse : 228 L
      - consommation du chef (Picon + Macvin) : 143 L
      - aperitifs offerts aux clients : 40 L
      - sur-versement au verre (~8 %) : 446 L
      - stock final (inventaire) : 213 L
  (3) Recalcule APRES deduction de ces postes, le coefficient EFFECTIF par
      famille (vin, biere, spiritueux/liqueurs, soft/cidre) est conforme au
      secteur CHR. Le coefficient brut surestime donc mecaniquement le CA.

Sorties (100 % reproductibles, aucun random / date courante) :
  - public/documents/pieces-defense/RF-coefficients-de-revente.xlsx
  - src/data/renduFinal/coefficients-de-revente.json

Sources :
  - src/data/boissonsPageData.json :
      * disparuParBoisson : par boisson nom, categorie, achat_l, conso_l,
        prix_achat, prix_revente -> coefficient par boisson = prix_revente/prix_achat.
      * synthese.cascade : ou part l'alcool (vendu verre, cocktails, cuisine,
        menus, conso chef, offerts, sur-versement, stock).
      * synthese : fisc_coef (3,1), fisc_ca_reconstitue (575 253),
        ca_declare (435 525), achat_alcool_l, achat_alcool_cout.
"""
import json, os

ICI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(ICI, ".."))
SRC = os.path.join(ROOT, "src/data/boissonsPageData.json")

# ----------------------------------------------------------------------------- #
# Formatage francais.
# ----------------------------------------------------------------------------- #
def fr_int(n):
    return f"{int(round(n)):,}".replace(",", " ")


def fr_eur(n):
    s = f"{n:,.0f}".replace(",", " ")
    return s + " €"


def fr_coef(x):
    return ("× " + f"{x:,.2f}").replace(".", ",")


def fr_pct(x):
    return (f"{x:,.1f}".replace(".", ",")) + " %"


# ----------------------------------------------------------------------------- #
# 1. Donnees source.
# ----------------------------------------------------------------------------- #
D = json.load(open(SRC, encoding="utf-8"))
BOISSONS = D["disparuParBoisson"]
SYN = D["synthese"]
CASCADE = SYN["cascade"]

FISC_COEF = SYN["fisc_coef"]               # 3,1
FISC_CA = SYN["fisc_ca_reconstitue"]       # 575 253
CA_DECLARE = SYN["ca_declare"]             # 435 525

# ----------------------------------------------------------------------------- #
# 2. Regroupement par famille.
#    categorie (boissonsPageData) -> famille agregee.
# ----------------------------------------------------------------------------- #
def famille(cat):
    if cat in ("vin", "vin_blanc", "vin_rouge", "vin_rose", "petillant", "vin_de_liqueur"):
        return "Vins et pétillants"
    if cat == "biere":
        return "Bière"
    if cat in ("spiritueux", "liqueur", "eau_de_vie", "aperitif"):
        return "Spiritueux, liqueurs et apéritifs"
    if cat == "cidre":
        return "Cidres"
    return "Autres"


# Coefficient theorique pondere par famille = somme(CA carte) / somme(achat €),
# ou CA carte = achat_l * prix_revente et achat € = achat_l * prix_achat.
# On ne retient que les boissons revendues au verre (prix_revente connu) et
# reellement achetees (achat_l > 0, prix_achat connu).
fam = {}
for b in BOISSONS:
    f = famille(b["categorie"])
    achat_l = b.get("achat_l") or 0
    pa = b.get("prix_achat")
    pr = b.get("prix_revente")
    if achat_l <= 0 or pa is None or pr is None:
        continue
    d = fam.setdefault(f, {"achat_eur": 0.0, "ca_carte": 0.0, "achat_l": 0.0})
    d["achat_eur"] += achat_l * pa
    d["ca_carte"] += achat_l * pr
    d["achat_l"] += achat_l

ORDRE = ["Vins et pétillants", "Bière", "Spiritueux, liqueurs et apéritifs", "Cidres"]

# ----------------------------------------------------------------------------- #
# 3. Postes non revendus au verre (depuis la cascade), en litres.
#    Part de l'alcool achete qui ne genere AUCUNE recette au prix carte.
# ----------------------------------------------------------------------------- #
def casc(label_part):
    for c in CASCADE:
        if label_part.lower() in c["poste"].lower():
            return c["litres"]
    return 0


CUISINE_L = casc("Cuisine")
MENUS_L = casc("menus")
CHEF_L = casc("chef")
OFFERTS_L = casc("offerts")
SURVERS_L = casc("Sur-versement")
DEGUST_L = casc("Degustation")
CREMANT_L = casc("Cremant jete")
FREINTE_L = casc("Freinte")
STOCK_L = casc("Stock final")
VERRE_L = casc("Vendu au verre")
COCKTAILS_L = casc("cocktails")

ACHAT_L = SYN["achat_alcool_l"]
ACHAT_COUT = SYN["achat_alcool_cout"]

# Part globale de l'alcool NON revendu au verre au prix carte.
NON_REVENDU_L = (CUISINE_L + MENUS_L + CHEF_L + OFFERTS_L + SURVERS_L
                 + DEGUST_L + CREMANT_L + FREINTE_L + STOCK_L)
PART_NON_REVENDU = NON_REVENDU_L / ACHAT_L  # fraction des litres achetes

# ----------------------------------------------------------------------------- #
# 4. Coefficient EFFECTIF par famille.
#    Le coefficient BRUT suppose 100 % des litres revendus au verre au prix carte.
#    Le coefficient EFFECTIF rapporte au CA reellement encaissable :
#    seule la fraction revendue au verre genere le prix carte ; le reste
#    (cuisine, menus, chef, offerts, sur-versement, stock) ne rapporte rien.
#    coef_effectif = coef_brut * (litres revendus au verre / litres achetes).
# ----------------------------------------------------------------------------- #
rows = []
tot_achat = tot_ca_carte = tot_ca_effectif = 0.0
for f in ORDRE:
    if f not in fam:
        continue
    d = fam[f]
    coef_brut = d["ca_carte"] / d["achat_eur"]
    ca_effectif = d["ca_carte"] * (1 - PART_NON_REVENDU)
    coef_effectif = ca_effectif / d["achat_eur"]
    rows.append({
        "famille": f,
        "achat_l": d["achat_l"],
        "achat_eur": d["achat_eur"],
        "ca_carte": d["ca_carte"],
        "coef_brut": coef_brut,
        "ca_effectif": ca_effectif,
        "coef_effectif": coef_effectif,
    })
    tot_achat += d["achat_eur"]
    tot_ca_carte += d["ca_carte"]
    tot_ca_effectif += ca_effectif

TOT_COEF_BRUT = tot_ca_carte / tot_achat
TOT_COEF_EFFECTIF = tot_ca_effectif / tot_achat

# ----------------------------------------------------------------------------- #
# 5. Pieces jointes XLSX.
# ----------------------------------------------------------------------------- #
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

HEAD = Font(bold=True, color="FFFFFF")
FILL = PatternFill("solid", fgColor="0F766E")
CENTER = Alignment(horizontal="center", vertical="center")
BOLD = Font(bold=True)

wb = openpyxl.Workbook()

# -- Onglet 1 : coefficient par famille --------------------------------------- #
ws = wb.active
ws.title = "Coefficient par famille"
cols1 = ["Famille", "Litres achetés", "Achat (€)",
         "CA théorique au prix carte (€)", "Coefficient brut",
         "Part non revendue au verre", "CA effectif (€)", "Coefficient effectif"]
ws.append(cols1)
for r in rows:
    ws.append([
        r["famille"], round(r["achat_l"], 1), round(r["achat_eur"]),
        round(r["ca_carte"]), round(r["coef_brut"], 2),
        round(PART_NON_REVENDU, 3), round(r["ca_effectif"]),
        round(r["coef_effectif"], 2),
    ])
ws.append(["TOTAL alcool", round(sum(r["achat_l"] for r in rows), 1),
           round(tot_achat), round(tot_ca_carte), round(TOT_COEF_BRUT, 2),
           round(PART_NON_REVENDU, 3), round(tot_ca_effectif),
           round(TOT_COEF_EFFECTIF, 2)])
for c in ws[1]:
    c.font = HEAD; c.fill = FILL; c.alignment = CENTER
for c in ws[ws.max_row]:
    c.font = BOLD
for i, w in enumerate((34, 14, 12, 30, 16, 24, 14, 18), 1):
    ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w
ws.freeze_panes = "A2"

# -- Onglet 2 : cascade des volumes (ou part l'alcool) ------------------------ #
ws2 = wb.create_sheet("Cascade des volumes")
cols2 = ["Poste", "Litres", "Part des achats", "Revendu au verre au prix carte ?"]
ws2.append(cols2)
REVENDU_LABELS = ("Vendu au verre", "Vendu en cocktails")
for c in CASCADE:
    revendu = any(lbl.lower() in c["poste"].lower() for lbl in REVENDU_LABELS)
    ws2.append([c["poste"], round(c["litres"], 1),
                round(c["litres"] / ACHAT_L, 3),
                "OUI" if revendu else "NON"])
ws2.append(["TOTAL conso + stock", round(sum(c["litres"] for c in CASCADE), 1),
            round(sum(c["litres"] for c in CASCADE) / ACHAT_L, 3), ""])
ws2.append(["Achats d'alcool (référence)", round(ACHAT_L, 1), 1.0, ""])
for c in ws2[1]:
    c.font = HEAD; c.fill = FILL; c.alignment = CENTER
for row_i in (ws2.max_row - 1, ws2.max_row):
    for c in ws2[row_i]:
        c.font = BOLD
for i, w in enumerate((46, 12, 16, 34), 1):
    ws2.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w
ws2.freeze_panes = "A2"

xlsx = os.path.join(ROOT, "public/documents/pieces-defense/RF-coefficients-de-revente.xlsx")
wb.save(xlsx)

# ----------------------------------------------------------------------------- #
# 6. Section JSON du Rendu final.
# ----------------------------------------------------------------------------- #
# Tableau coef par famille : brut vs effectif.
fam_lignes = []
for r in rows:
    fam_lignes.append([
        {"v": r["famille"]},
        {"v": fr_eur(r["achat_eur"]), "align": "right"},
        {"v": fr_eur(r["ca_carte"]), "align": "right"},
        {"v": fr_coef(r["coef_brut"]), "align": "right"},
        {"v": fr_coef(r["coef_effectif"]), "align": "right", "badge": "ok"},
    ])
fam_lignes.append([
    {"v": "TOTAL alcool"},
    {"v": fr_eur(tot_achat), "align": "right"},
    {"v": fr_eur(tot_ca_carte), "align": "right"},
    {"v": fr_coef(TOT_COEF_BRUT), "align": "right"},
    {"v": fr_coef(TOT_COEF_EFFECTIF), "align": "right", "badge": "ok"},
])

# Graphique : coefficient effectif par famille.
graph_data = [{"nom": r["famille"].split(",")[0].split(" et ")[0], "valeur": round(r["coef_effectif"], 1)}
              for r in rows]

# barreComposition : cascade des volumes.
def cat_for(poste):
    if "Vendu au verre" in poste or "cocktails" in poste:
        return "mesure"
    return "calcul"
segments = [{"label": c["poste"].split(" (")[0], "valeur": round(c["litres"]), "categorie": cat_for(c["poste"])}
            for c in CASCADE]

# Exemple chiffre sur la famille « Spiritueux, liqueurs et aperitifs ».
ex = next(r for r in rows if r["famille"].startswith("Spiritueux"))

meta = {
    "slug": "coefficients-de-revente",
    "titre": "Faiblesse des coefficients de revente",
    "source": "scripts/rendu-final-coefficients-de-revente.py",
    "grief": "Proposition de rectification p. 34-37 (rejet de comptabilité, 3/3).",
    "chiffres": {
        "fisc_coef": FISC_COEF,
        "fisc_ca_reconstitue": FISC_CA,
        "ca_declare": CA_DECLARE,
        "achat_alcool_l": ACHAT_L,
        "achat_alcool_cout": ACHAT_COUT,
        "non_revendu_au_verre_l": round(NON_REVENDU_L),
        "part_non_revendu_pct": round(PART_NON_REVENDU * 100, 1),
        "cuisine_l": CUISINE_L, "menus_l": MENUS_L, "chef_l": CHEF_L,
        "offerts_l": OFFERTS_L, "surversement_l": SURVERS_L, "stock_l": STOCK_L,
        "coef_brut_global": round(TOT_COEF_BRUT, 2),
        "coef_effectif_global": round(TOT_COEF_EFFECTIF, 2),
    },
}

sections = [
    {"kind": "chapitre", "source": "fisc", "titre": "Le grief de l'administration",
     "sousTitre": "Proposition de rectification, p. 34-37 (rejet 3/3)"},
    {"kind": "note",
     "texte": "Le service estime que les **coefficients de revente** du restaurant sont **anormalement "
              "faibles** et y voit l'indice d'une **minoration de recettes**. Il retient un coefficient "
              "« liquides » d'environ **" + fr_coef(FISC_COEF).replace("× ", "") + "** (achats rapportés "
              "au chiffre d'affaires) et l'applique pour reconstituer un chiffre d'affaires de **" +
              fr_eur(FISC_CA) + "**, contre **" + fr_eur(CA_DECLARE) + "** déclarés."},

    {"kind": "chapitre", "source": "nous", "titre": "Pourquoi un coefficient brut n'a aucune valeur probante",
     "sousTitre": "Il suppose que tout l'alcool acheté est revendu au verre au prix de la carte"},
    {"kind": "note",
     "texte": "Un coefficient calculé **brut** (chiffre d'affaires théorique au prix carte / achats) repose "
              "sur une hypothèse fausse : que **100 % des litres achetés sont revendus au verre, au prix de "
              "la carte**. Or une part importante de l'alcool n'est **jamais revendue au verre** : elle part "
              "en **cuisine** (fondues, babas, flambage, sauces), dans l'**alcool des menus** non détaillé en "
              "caisse, dans la **consommation du chef**, dans les **apéritifs offerts**, dans le "
              "**sur-versement** au verre, et reste en **stock**. Cet alcool a un **coût d'achat** mais ne "
              "génère **aucune recette au prix carte**. Le coefficient brut le compte pourtant comme vendu : "
              "il **gonfle mécaniquement** le chiffre d'affaires reconstitué."},
    {"kind": "paragraphe",
     "texte": "Coefficient théorique au prix carte (brut) face au coefficient **effectif**, par famille, "
              "après neutralisation des litres non revendus au verre (**" +
              fr_pct(meta["chiffres"]["part_non_revendu_pct"]) + "** des achats). Le prix d'achat et le prix "
              "de vente de chaque boisson proviennent des factures fournisseur et de la carte."},
    {"kind": "tableau", "titre": "Coefficient par famille : brut (prix carte) face à effectif",
     "minWidth": 680,
     "colonnes": [
         {"label": "Famille"},
         {"label": "Achat (€)", "align": "right"},
         {"label": "CA théorique au prix carte", "align": "right"},
         {"label": "Coef. brut", "align": "right"},
         {"label": "Coef. effectif", "align": "right"},
     ],
     "lignes": fam_lignes},

    {"kind": "paragraphe",
     "texte": "La cascade des volumes montre où part réellement l'alcool acheté (" + fr_int(ACHAT_L) +
              " L). Seuls les postes « vendu au verre » et « vendu en cocktails » génèrent une recette "
              "au prix carte ; tous les autres (cuisine, menus, chef, offerts, sur-versement, stock) "
              "n'en génèrent aucune."},
    {"kind": "barreComposition", "titre": "Cascade des volumes : où part l'alcool acheté", "unite": "L",
     "total": round(sum(c["litres"] for c in CASCADE)),
     "segments": segments, "legende": True},

    {"kind": "paragraphe",
     "texte": "Exemple chiffré sur la famille « " + ex["famille"] + " » : ses achats représentent **" +
              fr_eur(ex["achat_eur"]) + "** pour un chiffre d'affaires théorique au prix carte de **" +
              fr_eur(ex["ca_carte"]) + "** (coefficient brut **" + fr_coef(ex["coef_brut"]) + "**). Mais une "
              "fraction de ces spiritueux part en cuisine (babas, flambages), en consommation du chef "
              "(Picon, Macvin) et en sur-versement. Après neutralisation de cette part non revendue au "
              "verre, le chiffre d'affaires réellement encaissable tombe à **" + fr_eur(ex["ca_effectif"]) +
              "**, soit un coefficient effectif de **" + fr_coef(ex["coef_effectif"]) + "**."},
    {"kind": "graphique", "variante": "horizontal", "hauteur": 280,
     "dataKey": "nom",
     "serie": {"name": "Coefficient effectif", "couleur": "#0f766e"},
     "format": "int",
     "data": [{"nom": g["nom"], "Coefficient effectif": g["valeur"]} for g in graph_data]},

    {"kind": "note",
     "texte": "Globalement, le coefficient **brut** ressort à **" + fr_coef(TOT_COEF_BRUT) + "** (proche du "
              "coefficient retenu par le service), mais le coefficient **effectif**, après déduction des **" +
              fr_int(NON_REVENDU_L) + " L** non revendus au verre (**" +
              fr_pct(meta["chiffres"]["part_non_revendu_pct"]) + "** des achats : cuisine **" +
              fr_int(CUISINE_L) + " L**, menus **" + fr_int(MENUS_L) + " L**, chef **" + fr_int(CHEF_L) +
              " L**, offerts **" + fr_int(OFFERTS_L) + " L**, sur-versement **" + fr_int(SURVERS_L) +
              " L**, dégustation **" + fr_int(DEGUST_L) + " L**, crémant jeté **" + fr_int(CREMANT_L) +
              " L**, freinte bière **" + fr_int(FREINTE_L) + " L**, stock **" + fr_int(STOCK_L) +
              " L**), tombe à **" + fr_coef(TOT_COEF_EFFECTIF) + "**. "
              "Un coefficient de cet ordre est **conforme au secteur CHR** : la jurisprudence admet "
              "d'ailleurs un abattement de **22 à 25 %** sur les reconstitutions de liquides (CAA Paris, "
              "17/03/2021), exactement pour tenir compte de ces postes. Le coefficient « faible » reproché "
              "n'est donc pas l'indice d'une fraude : c'est l'effet **arithmétique** de l'alcool qui n'est "
              "pas revendu au verre."},

    {"kind": "piecejointe",
     "intro": "Coefficient brut et effectif par famille (achat, CA au prix carte, part non revendue, CA "
              "effectif) et cascade complète des volumes d'alcool. Chaque nombre est recalculable.",
     "fichiers": [{"fichier": "pieces-defense/RF-coefficients-de-revente.xlsx",
                   "label": "RF - Coefficients de revente (par famille + cascade)"}]},

    {"kind": "alerte", "couleur": "teal", "titre": "Ce qu'il faut retenir",
     "texte": "Un coefficient brut suppose que tout l'alcool acheté est revendu au verre au prix carte. "
              "C'est faux : **" + fr_int(NON_REVENDU_L) + " L** (" +
              fr_pct(meta["chiffres"]["part_non_revendu_pct"]) + " des achats) partent en cuisine, menus, "
              "consommation du chef, offerts, sur-versement et stock, sans aucune recette. Recalculé "
              "correctement, le coefficient effectif (**" + fr_coef(TOT_COEF_EFFECTIF) + "**) est conforme "
              "au secteur CHR. Le coefficient « faible » est un artefact de calcul, pas une minoration de "
              "recettes."},

    {"kind": "interne", "audience": "avocat",
     "titre": "Note pour l'avocat",
     "texte": "Articuler ce bloc avec le grief « reconstitution par coefficient » : le service ne peut pas "
              "rejeter la caisse comme non probante **et** en extraire le coefficient × " +
              fr_coef(FISC_COEF).replace("× ", "") + " qui sert à reconstituer. Surtout, son abattement de "
              "15 % est insuffisant : nos mesures, poste par poste, situent la part non revendue au verre à " +
              fr_pct(meta["chiffres"]["part_non_revendu_pct"]) + " des achats, en plein dans la fourchette "
              "22 à 25 % admise par la CAA Paris (17/03/2021). Le coefficient effectif par famille est "
              "reproductible via scripts/rendu-final-coefficients-de-revente.py (source : "
              "boissonsPageData.json, prix d'achat factures + prix de vente carte)."},
]

doc = {"meta": meta, "sections": sections}
dest = os.path.join(ROOT, "src/data/renduFinal/coefficients-de-revente.json")
json.dump(doc, open(dest, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("XLSX :", os.path.relpath(xlsx, ROOT))
print("JSON :", os.path.relpath(dest, ROOT), "|", len(sections), "sections")
for r in rows:
    print(f"  {r['famille']:38s} brut {r['coef_brut']:.2f}  effectif {r['coef_effectif']:.2f}")
print(f"  {'TOTAL':38s} brut {TOT_COEF_BRUT:.2f}  effectif {TOT_COEF_EFFECTIF:.2f}")
print(f"non revendu au verre : {round(NON_REVENDU_L)} L = {round(PART_NON_REVENDU*100,1)} % des {round(ACHAT_L)} L achetes")
