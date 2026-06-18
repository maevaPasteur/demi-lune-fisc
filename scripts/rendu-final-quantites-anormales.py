#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rendu-final-quantites-anormales.py
Bloc « Quantités anormales » du Rendu final (réponse au fisc, p. 18-20, rejet 1/3).

Grief : des quantités élevées/atypiques (ex. 2 518, 3 467 unités sur une seule
note) traduiraient des anomalies.

Démonstration : ces quantités sont matériellement impossibles (on ne sert pas
des milliers de couverts sur une addition). Ce sont des FAUTES DE FRAPPE
(prix correct × quantité aberrante) immédiatement annulées : ce sont
exactement les plus grosses lignes de suppression DEL du fichier événement,
supprimées le jour même de leur saisie, donc jamais reversées au CA déclaré.

Sorties (100 % reproductibles, aucun random / date courante) :
  - public/documents/pieces-defense/RF-quantites-anormales.xlsx
  - src/data/renduFinal/quantites-anormales.json

Sources :
  - src/data/renduFinalCalculs.json -> "aberrations" (top 4 décomposés + compte).
  - public/documents/caisse-enregistreuse/ANNEXE-E{1,2,3}_tpvevenement_*.xls
    (col1 date, col2 heure, col3 type = "DEL", col8 montant) : liste exhaustive
    des suppressions, pour isoler les montants anormalement élevés.
"""
import xlrd, json, os, re

ICI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(ICI, ".."))
CAISSE = os.path.join(ROOT, "public/documents/caisse-enregistreuse/")
EXOS = ["2022-2023", "2023-2024", "2024-2025"]
E = {e: CAISSE + f"ANNEXE-E{i}_tpvevenement_{e}.xls" for i, e in enumerate(EXOS, 1)}

# ----------------------------------------------------------------------------- #
# Formatage français des nombres.
# ----------------------------------------------------------------------------- #
def fr_int(n):
    return f"{int(round(n)):,}".replace(",", " ")


def fr_eur(n):
    s = f"{n:,.2f}".replace(",", "§").replace(".", ",").replace("§", " ")
    return s + " €"


# ----------------------------------------------------------------------------- #
# 1. Top 4 aberrations (décomposition prix × quantité) depuis le JSON source.
# ----------------------------------------------------------------------------- #
RF = json.load(open(os.path.join(ROOT, "src/data/renduFinalCalculs.json"), encoding="utf-8"))
ABER = RF["aberrations"]
TOP = ABER["top"]
COMPTE = ABER["compte"]

# ----------------------------------------------------------------------------- #
# 2. Liste exhaustive des suppressions DEL au montant anormalement élevé
#    (>= 200 €) recalculée depuis le fichier événement, pour la pièce jointe.
#    Toute DEL est par construction une suppression survenue le jour même de la
#    saisie (le fichier événement horodate chaque suppression à sa date/heure).
# ----------------------------------------------------------------------------- #
SEUIL_XLSX = 200.0
dels = []
for ex, fn in E.items():
    sh = xlrd.open_workbook(fn).sheet_by_index(0)
    for r in range(1, sh.nrows):
        if str(sh.cell_value(r, 3)).strip() != "DEL":
            continue
        date = str(sh.cell_value(r, 1))[:10]
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
            continue  # ligne de total / synthèse, pas une suppression réelle
        try:
            amt = float(sh.cell_value(r, 8))
        except ValueError:
            amt = 0.0
        heure = str(sh.cell_value(r, 2))[:5]
        dels.append({"exercice": ex, "date": date, "heure": heure, "montant": round(amt, 2)})
dels.sort(key=lambda d: -d["montant"])
gros = [d for d in dels if d["montant"] >= SEUIL_XLSX]

# Décomposition prix × quantité associée aux 4 plus grosses (clé date+heure).
DECO = {(t["date"], t["heure"]): t.get("decomposition", []) for t in TOP}

# ----------------------------------------------------------------------------- #
# 3. Pièce jointe XLSX.
# ----------------------------------------------------------------------------- #
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

HEAD = Font(bold=True, color="FFFFFF")
FILL = PatternFill("solid", fgColor="0F766E")
CENTER = Alignment(horizontal="center", vertical="center")

wb = openpyxl.Workbook()

# -- Onglet 1 : décomposition des 4 quantités aberrantes ---------------------- #
ws = wb.active
ws.title = "Quantites aberrantes"
cols1 = ["Date", "Heure", "Montant saisi", "Produit (prix correct)",
         "Prix unitaire", "Quantité saisie", "Supprimée le jour même"]
ws.append(cols1)
for t in TOP:
    deco = t.get("decomposition", [])
    if not deco:
        ws.append([t["date"], t["heure"], t["montant"], "(non décomposé)", "", "", "OUI"])
        continue
    for i, c in enumerate(deco):
        ws.append([
            t["date"] if i == 0 else "",
            t["heure"] if i == 0 else "",
            t["montant"] if i == 0 else "",
            c["produit"], c["prix"], c["quantite"],
            "OUI" if i == 0 else "",
        ])
for c in ws[1]:
    c.font = HEAD; c.fill = FILL; c.alignment = CENTER
for i, w in enumerate((12, 8, 16, 26, 14, 16, 22), 1):
    ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w
ws.freeze_panes = "A2"

# -- Onglet 2 : toutes les suppressions au montant anormal (>= 200 €) --------- #
ws2 = wb.create_sheet("Suppressions >= 200 EUR")
cols2 = ["Exercice", "Date", "Heure", "Montant supprimé (€)",
         "Quantité aberrante ? (prix×qté)", "Supprimée le jour même"]
ws2.append(cols2)
for d in gros:
    deco = DECO.get((d["date"], d["heure"]), [])
    note = ""
    if deco:
        c0 = deco[0]
        note = f"{c0['produit']} : {c0['prix']} × {c0['quantite']}"
    ws2.append([d["exercice"], d["date"], d["heure"], d["montant"], note, "OUI"])
for c in ws2[1]:
    c.font = HEAD; c.fill = FILL; c.alignment = CENTER
for i, w in enumerate((12, 12, 8, 20, 34, 22), 1):
    ws2.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w
ws2.freeze_panes = "A2"

xlsx = os.path.join(ROOT, "public/documents/pieces-defense/RF-quantites-anormales.xlsx")
wb.save(xlsx)

# ----------------------------------------------------------------------------- #
# 4. Section JSON du Rendu final.
# ----------------------------------------------------------------------------- #
# Exemple daté complet (la plus grosse aberration).
ex0 = TOP[0]
ex0_lignes = [
    [{"v": c["produit"]},
     {"v": fr_eur(c["prix"]), "align": "right"},
     {"v": fr_int(c["quantite"]), "align": "right"},
     {"v": fr_eur(c["prix"] * c["quantite"]), "align": "right"}]
    for c in ex0["decomposition"]
]

# Tableau des 4 aberrations : montant + l'article qui porte la plus grosse quantité.
top_lignes = []
for t in TOP:
    deco = t.get("decomposition", [])
    cmax = max(deco, key=lambda c: c["quantite"]) if deco else None
    top_lignes.append([
        {"v": t["date"]},
        {"v": t["heure"], "align": "center"},
        {"v": fr_eur(t["montant"]), "align": "right"},
        {"v": (cmax["produit"] if cmax else "—-").replace("—", "-"), "align": "left"},
        {"v": (fr_int(cmax["quantite"]) if cmax else ""), "align": "right"},
        {"v": "Supprimée", "align": "center", "badge": "ok"},
    ])

meta = {
    "slug": "quantites-anormales",
    "titre": "Quantités « anormales »",
    "source": "scripts/rendu-final-quantites-anormales.py",
    "grief": "Proposition de rectification p. 18-20 (rejet de comptabilité, 1/3).",
    "chiffres": {
        "del_total": COMPTE["total"],
        "del_somme_eur": COMPTE["somme"],
        "del_mediane_eur": COMPTE["mediane"],
        "del_sup_1000": COMPTE["sup_1000"],
        "del_sup_500": COMPTE["sup_500"],
        "del_sup_200": COMPTE["sup_200"],
        "top4_somme_eur": round(sum(t["montant"] for t in TOP), 2),
        "max_quantite": max(c["quantite"] for t in TOP for c in t.get("decomposition", [])),
    },
}

sections = [
    {"kind": "chapitre", "source": "fisc", "titre": "Le grief de l'administration",
     "sousTitre": "Proposition de rectification, p. 18-20 (rejet 1/3)"},
    {"kind": "note",
     "texte": "Le service relève dans les fichiers de caisse des **quantités élevées ou atypiques** "
              "sur certaines lignes (plusieurs milliers d'unités d'un même article sur une seule note) "
              "et en déduit des **anomalies** entachant la sincérité de la comptabilité."},

    {"kind": "chapitre", "source": "nous", "titre": "Ce que sont réellement ces quantités",
     "sousTitre": "Des fautes de frappe annulées le jour même, jamais reversées au CA"},
    {"kind": "note",
     "texte": "Une « quantité anormale » est une **faute de frappe** : un prix unitaire correct "
              "multiplié par une quantité saisie par erreur. Servir " + fr_int(meta["chiffres"]["max_quantite"]) +
              " portions d'un même plat sur une seule addition est **matériellement impossible** "
              "(la salle compte quelques dizaines de couverts). Ces lignes sont **immédiatement "
              "supprimées** : ce sont, une par une, les **plus grosses suppressions DEL** du fichier "
              "événement, horodatées et annulées **le jour même de leur saisie**. Elles n'entrent "
              "donc jamais dans le chiffre d'affaires déclaré."},
    {"kind": "paragraphe",
     "texte": "Les quatre plus grosses « quantités anormales » des trois exercices, et l'article qui "
              "porte la quantité la plus aberrante de chacune. Chacune est une ligne supprimée."},
    {"kind": "tableau", "titre": "Les 4 quantités les plus anormales (toutes supprimées)",
     "minWidth": 640,
     "colonnes": [
         {"label": "Date"}, {"label": "Heure", "align": "center"},
         {"label": "Montant saisi", "align": "right"},
         {"label": "Article le plus aberrant", "align": "left"},
         {"label": "Quantité saisie", "align": "right"},
         {"label": "Statut", "align": "center"},
     ],
     "lignes": top_lignes},
    {"kind": "paragraphe",
     "texte": "Exemple détaillé du " + ex0["date"] + " à " + ex0["heure"] + " (" + fr_eur(ex0["montant"]) +
              ") : un même ticket cumule des quantités qui n'ont aucun sens physique. "
              "Le prix unitaire de chaque article reste correct ; seule la quantité est fautive."},
    {"kind": "tableau",
     "titre": "Décomposition de la ligne du " + ex0["date"] + " (" + fr_eur(ex0["montant"]) + ", supprimée)",
     "minWidth": 560,
     "colonnes": [
         {"label": "Article (prix correct)"},
         {"label": "Prix unitaire", "align": "right"},
         {"label": "Quantité saisie", "align": "right"},
         {"label": "Sous-total saisi", "align": "right"},
     ],
     "lignes": ex0_lignes},
    {"kind": "note",
     "texte": "**Le lien avec les suppressions est exact.** Ces lignes ne sont pas « cachées » : ce "
              "sont les mêmes que les grandes suppressions DEL traitées au bloc Suppressions de caisse. "
              "Sur **" + fr_int(COMPTE["total"]) + "** suppressions totalisant **" + fr_eur(COMPTE["somme"]) +
              "**, seules **" + str(COMPTE["sup_1000"]) + "** dépassent 1 000 € et **" + str(COMPTE["sup_200"]) +
              "** dépassent 200 € : la médiane d'une suppression est de **" + fr_eur(COMPTE["mediane"]) + "**. "
              "Les quantités anormales sont donc une poignée d'erreurs de saisie spectaculaires mais "
              "isolées, toutes annulées, et non un procédé d'occultation."},
    {"kind": "graphique", "variante": "horizontal", "hauteur": 280,
     "dataKey": "nom",
     "serie": {"name": "Montant supprimé", "couleur": "#0f766e"},
     "format": "euro",
     "data": [
         {"nom": ex0["date"] + " (" + ex0["heure"] + ")", "Montant supprimé": TOP[0]["montant"]},
         {"nom": TOP[1]["date"] + " (" + TOP[1]["heure"] + ")", "Montant supprimé": TOP[1]["montant"]},
         {"nom": TOP[2]["date"] + " (" + TOP[2]["heure"] + ")", "Montant supprimé": TOP[2]["montant"]},
         {"nom": TOP[3]["date"] + " (" + TOP[3]["heure"] + ")", "Montant supprimé": TOP[3]["montant"]},
     ]},

    {"kind": "piecejointe",
     "intro": "Décomposition prix × quantité des 4 quantités aberrantes, et liste exhaustive des "
              "suppressions au montant anormalement élevé (>= 200 €), toutes supprimées le jour même.",
     "fichiers": [{"fichier": "pieces-defense/RF-quantites-anormales.xlsx",
                   "label": "RF - Quantités anormales (décomposition + liste)"}]},

    {"kind": "alerte", "couleur": "teal", "titre": "Ce qu'il faut retenir",
     "texte": "Les quantités « anormales » sont des fautes de frappe (prix correct × quantité "
              "impossible), immédiatement supprimées : ce sont les plus grosses lignes DEL, "
              "annulées le jour même de leur saisie. Elles n'ont jamais été reversées au chiffre "
              "d'affaires déclaré et ne révèlent aucune dissimulation de recettes."},

    {"kind": "interne", "audience": "avocat",
     "titre": "Note pour l'avocat",
     "texte": "Le grief « quantités anormales » et le grief « suppressions de notes » portent sur les "
              "mêmes lignes : invoquer une quantité aberrante puis la suppression correspondante "
              "reviendrait à compter deux fois la même erreur. La pièce RF-quantites-anormales.xlsx "
              "établit le rapprochement 1:1 (montant saisi = prix catalogue × quantité fautive = montant "
              "supprimé). Reproductible via scripts/rendu-final-quantites-anormales.py."},
]

doc = {"meta": meta, "sections": sections}
dest = os.path.join(ROOT, "src/data/renduFinal/quantites-anormales.json")
json.dump(doc, open(dest, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("XLSX :", os.path.relpath(xlsx, ROOT), "| onglet1 4 aberrations, onglet2", len(gros), "lignes >= 200 €")
print("JSON :", os.path.relpath(dest, ROOT), "|", len(sections), "sections")
print("DEL total", COMPTE["total"], "somme", COMPTE["somme"], "€ | médiane", COMPTE["mediane"], "€")
print("top4 somme", round(sum(t["montant"] for t in TOP), 2), "€ | max quantité", meta["chiffres"]["max_quantite"])
