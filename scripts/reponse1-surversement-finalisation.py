#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REPONSE 1 - Finalisation des deux pages « sur-versement » (partie N et point 1).

1. Corrige une erreur de lecture : la page affirmait qu'une ligne Champagne
   Lancon du tableau p. 81 portait 9 ventes pour 0 disponible. La verification
   montre que le disponible y est porte par une CELLULE FUSIONNEE au niveau du
   groupe (Bollinger + Ruinart + Lancon + Sandrin) et que le taux imprime par le
   service se recalcule exactement sur le total du groupe. Ce n'est donc pas une
   anomalie, et l'affirmation est retiree.
2. Ajoute le releve exhaustif du tableau de la page 81, recalcule ligne a ligne.
3. Reference la piece R1-p81-articles-unite.xlsx et passe les deux pages en
   statut « demonte ».

Chiffres lus dans public/documents/pieces-reponse-1/R1-p81-articles-unite.xlsx
(produit par scripts/reponse1-p81-articles-unite.py). Idempotent.
"""
import os, json
from openpyxl import load_workbook

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DATA = os.path.join(ROOT, "src/data/reponse1")
PIECE = os.path.join(ROOT, "public/documents/pieces-reponse-1/R1-p81-articles-unite.xlsx")
MARQUE = "_bloc_p81"

wb = load_workbook(PIECE)
IMP = [r for r in wb["Lignes impossibles"].iter_rows(min_row=5, values_only=True)
       if r[0] and r[2]]
TOT = [r for r in wb["Tableau p.81 recalcule"].iter_rows(min_row=5, values_only=True) if r[0]]
SYNTH = {r[0]: (r[3], r[4], r[5]) for r in wb["Lignes impossibles"].iter_rows(min_row=5, values_only=True)
         if r[0] and str(r[0]).startswith(("Exercice", "Total"))}
FUSION = [r for r in wb["Blocs fusionnes"].iter_rows(min_row=5, values_only=True) if r[0]]

NEG = [r for r in IMP if "negatif" in str(r[7])]
CENT = [r for r in IMP if "sans aucune vente de l" in str(r[7])]
NULS = [r for r in IMP if "disponible et des ventes nuls" in str(r[7])]
PLUS = [r for r in IMP if "plus vendu que disponible, et pourtant" in str(r[7])]
DIFF = [r for r in IMP if "different du taux recalcule" in str(r[7])]

cg = lambda v, **k: dict(v=v, **k)
cd = lambda v, **k: dict(v=v, align="right", **k)


def tableau_types():
    lignes = []
    for lib, lot in [
        ("Taux de disparition négatif imprimé : il a été vendu plus que le disponible", NEG),
        ("100,00 % de disparition alors qu’aucune vente n’est enregistrée sur l’exercice", CENT),
        ("Taux imprimé sur un disponible ET des ventes tous deux nuls", NULS),
        ("Ventes supérieures au disponible, et pourtant un taux positif imprimé", PLUS),
        ("Taux imprimé différent de celui que produit la formule annoncée", DIFF),
    ]:
        ex = lot[0]
        lignes.append([
            cg(lib), cd(str(len(lot))),
            cg(f"{ex[0]}, exercice clos le {ex[2]}"),
            cd(str(ex[3])), cd(str(ex[4])), cd(str(ex[5])),
        ])
    lignes.append([cg("Total des couples (article, exercice) en anomalie", fw=700),
                   cd(str(len(IMP)), fw=700), cg(""), cg(""), cg(""), cg("")])
    return {
        "kind": "tableau",
        "titre": "Le tableau de la page 81 recalculé ligne à ligne : les résultats que sa formule "
                 "ne peut pas produire",
        "minWidth": 900,
        "colonnes": [{"label": "Nature de l’anomalie"}, {"label": "Lignes", "align": "right"},
                     {"label": "Exemple"},
                     {"label": "Disponible", "align": "right"},
                     {"label": "Vendu", "align": "right"},
                     {"label": "Taux imprimé", "align": "right"}],
        "lignes": lignes,
    }


def bloc():
    d3, v3, p3 = SYNTH["Total 3 exercices"]
    return [
        {"kind": "titre", "texte": "Le tableau de la page 81, recalculé ligne à ligne"},
        {"kind": "paragraphe",
         "texte": "Ces constats ne sont pas des exceptions choisies. Le tableau des articles vendus "
                  "à l’unité de la page 81 comporte **" + str(len(TOT)) + " lignes**, et nous les "
                  "avons toutes reprises en appliquant la formule que le service annonce lui-même, "
                  "soit le disponible diminué des ventes, rapporté au disponible. **" + str(len(IMP)) +
                  " couples (article, exercice) donnent un résultat que cette formule ne peut pas "
                  "produire.**"},
        tableau_types(),
        {"kind": "paragraphe",
         "texte": "Le poids de ces lignes n’est pas marginal. Sur les **" + str(d3) + " unités** que "
                  "le tableau déclare disparues au total des trois exercices, **" + str(v3) + " unités, "
                  "soit " + str(p3) + "**, figurent sur des lignes où **aucune vente n’est enregistrée "
                  "sur l’exercice**. Ce sont, pour l’essentiel, des bières en bouteille et des sodas : "
                  "un article livré et jamais scanné à la vente n’est pas un article détourné, c’est un "
                  "article dont le libellé de facture n’a pas été rattaché au bouton de caisse "
                  "correspondant."},
        {"kind": "paragraphe",
         "texte": "La conséquence porte sur la conclusion même de la partie. Le service tire de la "
                  "volatilité des taux de ce tableau que « le sur-versement ne peut pas être la seule "
                  "explication » et qu’il faut y voir une dissimulation. Un tableau qui produit "
                  "simultanément des taux négatifs, des disparitions totales sans la moindre vente et "
                  "des taux qui ne se recalculent pas sur ses propres colonnes ne mesure pas des "
                  "disparitions : il mesure d’abord le défaut d’appariement entre le référentiel des "
                  "factures et celui de la caisse. Il ne peut donc pas fonder une accusation."},
        {"kind": "note",
         "texte": "Deux blocs de ce tableau, Granini et Champagne, ne sont pas en anomalie et nous ne "
                  "les présentons pas comme tels : le disponible y est porté par une cellule fusionnée "
                  "au niveau du groupe, et le taux imprimé par le service se recalcule exactement sur "
                  "le total du groupe sur les " + str(len(FUSION)) + " lignes concernées. Ces blocs se "
                  "lisent au groupe, non à la ligne."},
    ]


def maj(slug, patch, marqueur=False, sections=None, ancre=None):
    chemin = os.path.join(DATA, slug + ".json")
    doc = json.load(open(chemin, encoding="utf-8"))
    secs, meta = doc["sections"], doc.setdefault("meta", {})
    if marqueur:
        if MARQUE in meta:
            i, n = meta[MARQUE]["debut"], meta[MARQUE]["nb"]
            del secs[i:i + n]
        i = ancre(secs)
        secs[i:i] = sections
        meta[MARQUE] = {"debut": i, "nb": len(sections),
                        "source": "scripts/reponse1-surversement-finalisation.py"}
    patch(doc, secs)
    json.dump(doc, open(chemin, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("écrit :", slug, "->", len(secs), "sections")


def patch_n(doc, secs):
    # Correction de l'erreur de lecture sur le bloc Champagne.
    for s in secs:
        if s.get("kind") == "paragraphe" and "Champagne Lançon" in s.get("texte", ""):
            s["texte"] = (
                "La même page aligne à l’inverse des lignes à **100,00 % de disparition** pour des "
                "articles dont la quantité vendue est **nulle** : 1664 33 cl (234 disponibles, 0 "
                "vendue), White Mort Subite 33 cl (108 et 0), Hefeweizen 33 cl (48 et 0), White "
                "Rabbit 33 cl (24 et 0). Le relevé complet, ci-dessous, en dénombre dix-huit.")
        if s.get("kind") == "paragraphe" and s.get("texte", "").startswith("Ces trois anomalies"):
            s["texte"] = (
                "Ces deux anomalies ont la même cause et elle n’est pas comptable : l’appariement "
                "article par article entre la facture et la caisse n’est pas fiable, parce qu’un "
                "produit change de nom, se regroupe avec un autre ou se substitue à lui. Un tableau "
                "qui produit à la fois - 46,67 % et + 100,00 % sans aucune vente mesure d’abord un "
                "défaut de correspondance de référentiels. Nous traitons ce point en détail à la page "
                "[Consommation supérieure aux achats](/reponse-1/consommation-superieure-achats).")
    for s in secs:
        if s.get("kind") == "piecejointe":
            f = [x["fichier"] for x in s["fichiers"]]
            if "pieces-reponse-1/R1-p81-articles-unite.xlsx" not in f:
                s["fichiers"].append({
                    "fichier": "pieces-reponse-1/R1-p81-articles-unite.xlsx",
                    "label": "Tableau de la page 81 recalculé ligne à ligne (XLSX, 3 onglets)"})
    doc["entete"]["statut"] = "demonte"
    doc["entete"]["reponseCourte"] = (
        "Le verre de 17,64 cl, le pichet de 58,80 cl et la bouteille de 88,20 cl sortent du calcul "
        "du service lui-même, qui applique un taux moyen à des contenants dont le sur-versement est "
        "nul par construction ; séparé assiette par assiette le sur-versement est de 494 L, le stock "
        "en autoriserait jusqu’à quatre fois plus, et le tableau par lequel il conclut à la "
        "dissimulation comporte 25 lignes que sa propre formule ne peut pas produire.")


def patch_1(doc, secs):
    doc["entete"]["statut"] = "demonte"
    doc["entete"]["reponseCourte"] = (
        "Les taux ne sont pas des affirmations gratuites mais deux mesures publiées auxquelles le "
        "service n’oppose aucune mesure ; recalculé par régime de service le sur-versement est de "
        "494 L, soit moins du quart de l’écart constaté, quand le stock en autoriserait jusqu’à "
        "119,8 % de la base versée à la main.")


if __name__ == "__main__":
    maj("sur-versement-au-verre", patch_n, marqueur=True, sections=bloc(),
        ancre=lambda secs: next(i for i, s in enumerate(secs)
                                if s.get("kind") == "titre"
                                and "cocktails : deux objections" in s.get("texte", "")))
    maj("recon-1-doses-figees", patch_1)
    print(f"\np. 81 : {len(TOT)} lignes reprises, {len(IMP)} couples en anomalie "
          f"({len(CENT)} à 100 % sans vente, {len(NEG)} négatifs, {len(NULS)} sur des colonnes nulles, "
          f"{len(PLUS)} ventes > disponible, {len(DIFF)} non reproductibles)")
