#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rendu-final-prix-menu-demi-lune.py

Bloc de defense : "Instabilite des prix du Menu Demi Lune".

Grief du fisc (Proposition de rectification, p. 33-36, rejet 3/3) : la multitude
de prix observes pour le Menu Demi Lune dans la caisse traduirait une
comptabilite non sincere.

Demonstration :
  1) Par periode de carte, le PRIX CATALOGUE du Menu Demi Lune est UNIQUE et
     STABLE (45,00 EUR sur toutes les periodes du controle).
  2) La "variation" provient des ventes HORS catalogue (forfaits de groupe,
     remises, prix negocies), soit 39,5 % des Menus Demi Lune (332 / 840) pour
     14 118 EUR, chacune TRACEE dans la caisse (date, heure, n de ticket).
  3) Exemple date : un ticket groupe de 5 couverts Menu Demi Lune au meme prix
     personnalise, encaisse en totalite.
  4) Ces recettes sont integralement dans le CA declare -> pas d'insincerite.

Sources (read-only) :
  - src/data/renduFinalCalculs.json  -> "menus_par_periode", "menus_custom"
    (calcules par scripts/rendu-final-menus.py a partir des tickets, annexe C).
  - public/documents/caisse-enregistreuse/ANNEXE-B{1,2,3}_*.xls (prix x qte par
    produit) -> distribution des prix observes du Menu Demi Lune, par exercice
    (controle de coherence avec menus_par_periode).
  - public/documents/caisse-enregistreuse/ANNEXE-C3_*.xls (detail tickets) ->
    exemple date du ticket groupe.

Sorties (ne touche PAS renduFinal.ts) :
  - public/documents/pieces-defense/RF-prix-menu-demi-lune.xlsx
  - src/data/renduFinal/prix-menu-demi-lune.json
"""
import json, os
from collections import Counter, OrderedDict

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

ICI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(ICI, ".."))

CALC = os.path.join(ROOT, "src/data/renduFinalCalculs.json")
ANNEXE_DIR = os.path.join(ROOT, "public/documents/caisse-enregistreuse")
XLSX_OUT = os.path.join(ROOT, "public/documents/pieces-defense/RF-prix-menu-demi-lune.xlsx")
JSON_OUT = os.path.join(ROOT, "src/data/renduFinal/prix-menu-demi-lune.json")

PRIX_CATALOGUE = 45.0  # prix carte du Menu Demi Lune, constant sur tout le controle


def eur(x):
    """Format francais : 14 118,00 EUR -> '14 118,00 €'."""
    s = f"{x:,.2f}"
    s = s.replace(",", " ").replace(".", ",")
    return s + " €"


def eur0(x):
    s = f"{x:,.0f}".replace(",", " ")
    return s + " €"


def num(x):
    return f"{x:,.0f}".replace(",", " ")


# --------------------------------------------------------------------------
# 1. Lecture des donnees de caisse deja agregees (menus_par_periode / custom)
# --------------------------------------------------------------------------
calc = json.load(open(CALC, encoding="utf-8"))
periodes = calc["menus_par_periode"]
menus_custom = calc["menus_custom"]
dl_custom = menus_custom["par_menu"]["Demi Lune"]


def demi_lune_de(p):
    for r in p["menus"]:
        if r["menu"].strip().lower() in ("demi lune", "demi-lune"):
            return r
    return None


# Tableau periode -> prix catalogue (stabilite)
table_periodes = []
for p in periodes:
    r = demi_lune_de(p)
    if not r:
        continue
    table_periodes.append({
        "periode": p["periode"],
        "carte": p.get("carte"),
        "exercice": p.get("exercice"),
        "dates": p.get("dates"),
        "prix_catalogue": r["prix_catalogue"],
        "qte_catalogue": r["qte_catalogue"],
        "qte_hors_catalogue": r["qte_hors_catalogue"],
        "eur_hors_catalogue": r["eur_hors_catalogue"],
    })

# Controle : un seul prix catalogue sur tout le controle
prix_catalogue_distincts = sorted({t["prix_catalogue"] for t in table_periodes})
assert prix_catalogue_distincts == [PRIX_CATALOGUE], prix_catalogue_distincts

# Prix personnalises cumules (toutes periodes) : prix -> qte
custom_agg = Counter()
for p in periodes:
    r = demi_lune_de(p)
    if not r:
        continue
    for px, q in r["prix_custom"]:
        custom_agg[round(px, 2)] += int(q)

custom_q = sum(custom_agg.values())
custom_eur = round(sum(px * q for px, q in custom_agg.items()))
nb_prix_distincts = len(custom_agg)
total_q = dl_custom["total_q"]
cat_q = total_q - custom_q
pct_custom = dl_custom["pct"]

# --------------------------------------------------------------------------
# 2. Controle de coherence avec l'annexe B (distribution des prix observes)
# --------------------------------------------------------------------------
def annexe_b_distribution():
    """Renvoie {exercice: Counter(prix->qte)} pour le Menu Demi Lune."""
    import xlrd
    files = [
        ("ANNEXE-B1_prix-vente-quantite_2022-2023.xls", "2022-2023"),
        ("ANNEXE-B2_prix-vente-quantite_2023-2024.xls", "2023-2024"),
        ("ANNEXE-B3_prix-vente-quantite_2024-2025.xls", "2024-2025"),
    ]
    out = OrderedDict()
    for f, ex in files:
        path = os.path.join(ANNEXE_DIR, f)
        if not os.path.exists(path):
            continue
        wb = xlrd.open_workbook(path)
        sh = wb.sheet_by_index(0)
        dist = Counter()
        for r in range(1, sh.nrows):
            lib = str(sh.cell_value(r, 4)).strip().lower()
            if "demi lune" in lib or "demi-lune" in lib:
                prix = round(float(sh.cell_value(r, 7)), 2)
                try:
                    q = int(sh.cell_value(r, 5))
                except Exception:
                    q = 0
                dist[prix] += q
        out[ex] = dist
    return out


annexe_b = annexe_b_distribution()
# Distribution cumulee tous exercices (pour le graphique)
dist_globale = Counter()
for ex, d in annexe_b.items():
    dist_globale.update(d)

# Coherence annexe B vs menus_par_periode (le 45,00 EUR doit dominer chaque annee)
b_cat = {ex: d.get(PRIX_CATALOGUE, 0) for ex, d in annexe_b.items()}

# --------------------------------------------------------------------------
# 3. XLSX : 2 onglets
# --------------------------------------------------------------------------
H1 = Font(bold=True, size=12, color="FFFFFF")
FILL1 = PatternFill("solid", fgColor="0F766E")
BOLD = Font(bold=True)
FILLT = PatternFill("solid", fgColor="E2E8F0")
THIN = Border(*[Side(style="thin", color="CBD5E0")] * 4)
RA = Alignment(horizontal="right")

wb = openpyxl.Workbook()

# Onglet 1 : Prix catalogue par periode
ws = wb.active
ws.title = "Prix catalogue par periode"
ws.append(["Menu Demi Lune : prix catalogue stable par periode de carte"])
ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=6)
ws.cell(1, 1).font = H1
ws.cell(1, 1).fill = FILL1
ws.append(["Periode", "Carte", "Exercice", "Dates", "Prix catalogue",
           "Qte au prix catalogue", "Qte hors catalogue", "EUR hors catalogue"])
# corriger l'en-tete (8 colonnes)
ws.delete_rows(2)
ws.append(["Periode", "Carte", "Exercice", "Dates", "Prix catalogue",
           "Qte au prix catalogue", "Qte hors catalogue", "EUR hors catalogue"])
ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=8)
for c in ws[2]:
    c.font = BOLD
    c.fill = FILLT
    c.border = THIN
for t in table_periodes:
    ws.append([t["periode"], t["carte"], t["exercice"], t["dates"],
               t["prix_catalogue"], t["qte_catalogue"], t["qte_hors_catalogue"],
               t["eur_hors_catalogue"]])
    for c in ws[ws.max_row]:
        c.border = THIN
        if isinstance(c.value, (int, float)):
            c.alignment = RA
# ligne total
ws.append(["TOTAL", "", "", "", PRIX_CATALOGUE,
           sum(t["qte_catalogue"] for t in table_periodes),
           sum(t["qte_hors_catalogue"] for t in table_periodes),
           sum(t["eur_hors_catalogue"] for t in table_periodes)])
for c in ws[ws.max_row]:
    c.font = BOLD
    c.fill = FILLT
    c.border = THIN
    if isinstance(c.value, (int, float)):
        c.alignment = RA
for i, w in enumerate([9, 7, 12, 26, 14, 21, 20, 18], 1):
    ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w
ws.freeze_panes = "A3"

# Onglet 2 : Prix personnalises
ws2 = wb.create_sheet("Prix personnalises")
ws2.append(["Menu Demi Lune : prix personnalises (hors catalogue) et occurrences"])
ws2.merge_cells(start_row=1, start_column=1, end_row=1, end_column=3)
ws2.cell(1, 1).font = H1
ws2.cell(1, 1).fill = FILL1
ws2.append(["Prix de vente (EUR)", "Nombre d'occurrences", "Montant (EUR)"])
for c in ws2[2]:
    c.font = BOLD
    c.fill = FILLT
    c.border = THIN
for px in sorted(custom_agg):
    q = custom_agg[px]
    ws2.append([px, q, round(px * q, 2)])
    for c in ws2[ws2.max_row]:
        c.border = THIN
        if isinstance(c.value, (int, float)):
            c.alignment = RA
ws2.append(["TOTAL hors catalogue", custom_q, custom_eur])
for c in ws2[ws2.max_row]:
    c.font = BOLD
    c.fill = FILLT
    c.border = THIN
    if isinstance(c.value, (int, float)):
        c.alignment = RA
for i, w in enumerate([20, 22, 16], 1):
    ws2.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w
ws2.freeze_panes = "A3"

os.makedirs(os.path.dirname(XLSX_OUT), exist_ok=True)
wb.save(XLSX_OUT)

# --------------------------------------------------------------------------
# 4. JSON de rendu (textes finaux)
# --------------------------------------------------------------------------
# Graphique : distribution des prix observes (annexe B, cumul). On regroupe les
# prix personnalises par tranches pour la lisibilite, le 45 EUR isole.
def tranche(px):
    if px == PRIX_CATALOGUE:
        return "45,00 € (catalogue)"
    if px < 30:
        return "< 30 €"
    if px < 40:
        return "30 a 40 €"
    if px < 45:
        return "40 a 45 €"
    if px <= 55:
        return "45 a 55 €"
    return "> 55 €"


ordre = ["< 30 €", "30 a 40 €", "40 a 45 €",
         "45,00 € (catalogue)", "45 a 55 €", "> 55 €"]
tr = Counter()
for px, q in dist_globale.items():
    tr[tranche(px)] += q
graph_data = [{"nom": k, "Ventes": tr[k]} for k in ordre if tr[k] > 0]

total_observe = sum(dist_globale.values())
qte_45 = dist_globale.get(PRIX_CATALOGUE, 0)
pct_45 = round(100.0 * qte_45 / total_observe, 1)

# tableau periode -> prix catalogue
lignes_periodes = []
for t in table_periodes:
    lignes_periodes.append([
        {"v": t["periode"]},
        {"v": t["carte"], "align": "center"},
        {"v": t["exercice"], "align": "center"},
        {"v": t["dates"], "align": "center"},
        {"v": eur(t["prix_catalogue"]), "align": "right", "badge": "ok"},
        {"v": num(t["qte_catalogue"]), "align": "right"},
        {"v": num(t["qte_hors_catalogue"]), "align": "right"},
    ])
lignes_periodes.append([
    {"v": "Toutes periodes"},
    {"v": "", "align": "center"},
    {"v": "", "align": "center"},
    {"v": "", "align": "center"},
    {"v": eur(PRIX_CATALOGUE) + " (unique)", "align": "right", "badge": "ok"},
    {"v": num(sum(t["qte_catalogue"] for t in table_periodes)), "align": "right"},
    {"v": num(sum(t["qte_hors_catalogue"] for t in table_periodes)), "align": "right"},
])

# tableau des prix personnalises : top occurrences + total (lisibilite)
top_custom = sorted(custom_agg.items(), key=lambda kv: (-kv[1], kv[0]))[:12]
lignes_custom = []
for px, q in top_custom:
    lignes_custom.append([
        {"v": eur(px)},
        {"v": num(q), "align": "right"},
        {"v": eur(round(px * q, 2)), "align": "right"},
    ])
lignes_custom.append([
    {"v": f"Total hors catalogue ({nb_prix_distincts} prix distincts)"},
    {"v": num(custom_q), "align": "right"},
    {"v": eur(custom_eur), "align": "right"},
])

doc = {
    "meta": {
        "slug": "prix-menu-demi-lune",
        "titre": "Instabilite des prix du « Menu Demi Lune »",
        "source": "scripts/rendu-final-prix-menu-demi-lune.py",
        "grief": "Proposition de rectification, p. 33-36 (rejet de comptabilite, 3/3).",
        "chiffres": {
            "prix_catalogue": PRIX_CATALOGUE,
            "nb_periodes": len(table_periodes),
            "total_q": total_q,
            "cat_q": cat_q,
            "custom_q": custom_q,
            "custom_eur": custom_eur,
            "pct_custom": pct_custom,
            "nb_prix_distincts": nb_prix_distincts,
            "qte_observee_45": qte_45,
            "pct_observee_45": pct_45,
        },
    },
    "sections": [
        {
            "kind": "chapitre",
            "source": "fisc",
            "titre": "Le grief de l'administration",
            "sousTitre": "Proposition de rectification, p. 33-36 (rejet 3/3)",
        },
        {
            "kind": "note",
            "texte": "Le service releve que, sur la carte, le Menu Demi Lune est affiche a **45,00 €**, mais que les donnees de caisse font apparaitre une **multitude de prix differents** pour ce meme menu (d'environ 24 € a 90 €). Il en deduit que la comptabilite serait **non sincere**.",
        },
        {
            "kind": "chapitre",
            "source": "nous",
            "titre": "Ce que mesure reellement cette variation",
            "sousTitre": "Un prix catalogue unique et stable, et des ventes hors catalogue tracees",
        },
        {
            "kind": "note",
            "texte": f"Il faut distinguer deux choses. **Le prix catalogue** du Menu Demi Lune est **unique et stable** : il vaut **{eur(PRIX_CATALOGUE)}** sur **chacune** des {len(table_periodes)} periodes de carte du controle. **La « variation »** invoquee provient exclusivement de ventes **hors prix catalogue** (forfaits de groupe, remises commerciales, prix negocies, menus a contenu adapte). Ces lignes ne sont pas dissimulees : chacune est **horodatee et tracee** dans la caisse, et **integralement encaissee**.",
        },
        {
            "kind": "paragraphe",
            "texte": "Premier constat : par periode de carte, le prix catalogue du Menu Demi Lune ne varie pas. La colonne « Qte hors catalogue » isole les ventes facturees a un autre prix (forfaits, remises), seule origine de l'amplitude relevee par le service.",
        },
        {
            "kind": "tableau",
            "titre": f"Prix catalogue du Menu Demi Lune par periode (stable a {eur(PRIX_CATALOGUE)})",
            "minWidth": 720,
            "colonnes": [
                {"label": "Periode"},
                {"label": "Carte", "align": "center"},
                {"label": "Exercice", "align": "center"},
                {"label": "Dates", "align": "center"},
                {"label": "Prix catalogue", "align": "right"},
                {"label": "Qte au prix catalogue", "align": "right"},
                {"label": "Qte hors catalogue", "align": "right"},
            ],
            "lignes": lignes_periodes,
        },
        {
            "kind": "paragraphe",
            "texte": f"Second constat : les ventes hors catalogue representent **{num(custom_q)}** des **{num(total_q)}** Menus Demi Lune vendus, soit **{str(pct_custom).replace('.', ',')} %**, pour **{eur(custom_eur)}**. Elles se repartissent sur **{nb_prix_distincts}** prix distincts (forfaits de groupe a prix rond, remises, menus adaptes). Le tableau ci-dessous donne les prix personnalises les plus frequents.",
        },
        {
            "kind": "tableau",
            "titre": "Menu Demi Lune : prix personnalises (hors catalogue) et occurrences",
            "minWidth": 520,
            "colonnes": [
                {"label": "Prix de vente"},
                {"label": "Occurrences", "align": "right"},
                {"label": "Montant encaisse", "align": "right"},
            ],
            "lignes": lignes_custom,
        },
        {
            "kind": "paragraphe",
            "texte": f"Distribution de l'ensemble des prix observes pour le Menu Demi Lune dans la caisse, tous exercices confondus (annexes B-1 a B-3, prix x quantite par produit). Sur **{num(total_observe)}** ventes, le prix de **{eur(PRIX_CATALOGUE)}** est de **tres loin** le plus frequent (**{num(qte_45)}** ventes, soit **{str(pct_45).replace('.', ',')} %**) ; les autres prix sont des forfaits et remises, minoritaires et disperses.",
        },
        {
            "kind": "graphique",
            "variante": "horizontal",
            "hauteur": 300,
            "dataKey": "nom",
            "serie": {"name": "Ventes", "couleur": "#0f766e"},
            "format": "int",
            "data": graph_data,
        },
        {
            "kind": "paragraphe",
            "texte": "Exemple date, representatif des forfaits de groupe. Le 31/10/2024 a 13:06, un meme ticket porte **5 couverts** « Menu Demi Lune » au **meme prix personnalise de 48,68 €** (forfait groupe), pour un total de **243,40 €**, encaisse en totalite. Le prix differe du catalogue, mais il est identique pour les 5 couverts, applique sur une seule note, et trace : c'est un forfait, pas une variation erratique.",
        },
        {
            "kind": "tableau",
            "titre": "Exemple : ticket groupe du 31/10/2024 a 13:06 (annexe C-3)",
            "minWidth": 520,
            "colonnes": [
                {"label": "Article"},
                {"label": "Prix unitaire", "align": "right"},
                {"label": "Couverts", "align": "right"},
                {"label": "Total ticket", "align": "right"},
            ],
            "lignes": [
                [
                    {"v": "Menu 'Demi Lune' (forfait groupe)"},
                    {"v": eur(48.68), "align": "right"},
                    {"v": "5", "align": "right"},
                    {"v": eur(243.40), "align": "right", "badge": "ok"},
                ],
            ],
        },
        {
            "kind": "piecejointe",
            "intro": "Prix catalogue par periode (stable) et liste exhaustive des prix personnalises du Menu Demi Lune avec leurs occurrences et montants.",
            "fichiers": [
                {
                    "fichier": "pieces-defense/RF-prix-menu-demi-lune.xlsx",
                    "label": "RF - Prix du Menu Demi Lune (catalogue par periode + prix personnalises)",
                }
            ],
        },
        {
            "kind": "alerte",
            "couleur": "teal",
            "titre": "Ce qu'il faut retenir",
            "texte": f"Le prix catalogue du Menu Demi Lune est unique et stable ({eur(PRIX_CATALOGUE)}) sur toutes les periodes de carte. La « variation » releve uniquement de ventes hors catalogue (forfaits de groupe, remises, prix negocies), soit {str(pct_custom).replace('.', ',')} % des Menus Demi Lune pour {eur(custom_eur)}, chacune horodatee, tracee et integralement portee au chiffre d'affaires declare. Aucune recette n'est dissimulee : le grief d'insincerite n'est pas fonde.",
        },
        {
            "kind": "interne",
            "audience": "avocat",
            "titre": "Note pour l'avocat",
            "texte": "Ce grief recoupe celui des « factures sans detail / forfaits » (menus a prix personnalises) deja traite : il s'agit des memes lignes de caisse, vues sous un autre angle. La pluralite de prix n'est pas une anomalie comptable mais la trace, dans la caisse, de la pratique commerciale (groupes, remises, formules). Le point juridique a tenir : la sincerite s'apprecie sur l'exhaustivite et la tracabilite des recettes, toutes deux etablies ici (chaque vente hors catalogue est horodatee et encaissee), et non sur l'uniformite des prix de vente, qu'aucun texte n'impose a un restaurateur. Reproductible via scripts/rendu-final-prix-menu-demi-lune.py.",
        },
    ],
}

os.makedirs(os.path.dirname(JSON_OUT), exist_ok=True)
json.dump(doc, open(JSON_OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# --------------------------------------------------------------------------
# 5. Recapitulatif console
# --------------------------------------------------------------------------
print("XLSX  ->", XLSX_OUT)
print("JSON  ->", JSON_OUT)
print()
print(f"Prix catalogue (toutes periodes) : {eur(PRIX_CATALOGUE)}  [{len(table_periodes)} periodes]")
for t in table_periodes:
    print(f"  {t['periode']} {t['carte']} {t['exercice']} {t['dates']}: "
          f"cat={t['qte_catalogue']} hors={t['qte_hors_catalogue']} ({eur0(t['eur_hors_catalogue'])})")
print()
print(f"Hors catalogue Demi Lune : {custom_q}/{total_q} ({pct_custom} %) = {eur(custom_eur)} "
      f"sur {nb_prix_distincts} prix distincts")
print(f"Annexe B (controle) - qte au prix 45,00 par exercice : {b_cat}")
print(f"Distribution globale annexe B : total={total_observe}, a 45,00={qte_45} ({pct_45} %)")
print("Graphique (tranches) :", {d['nom']: d['Ventes'] for d in graph_data})
