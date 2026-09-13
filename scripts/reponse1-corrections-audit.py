#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REPONSE 1 - Corrections issues de l'audit des sources (AUDIT-SOURCES.md).

Ne traite que les corrections MECANIQUES et non ambigues : chiffres faux,
valeurs divergentes entre pages, clause dupliquee par un script non idempotent.
Les arbitrages de fond (745 L / 794 L, 1 505 L perimes, reintegration de
l'arret 22TL21401, socle juridique de inventaires-de-stocks, lien de l'article
286 du CGI) sont traites separement.

Chaque correction porte le numero de l'anomalie du rapport d'audit.
Idempotent : relancer le script ne produit aucun changement supplementaire.
"""
import os, json, re, glob

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DATA = os.path.join(ROOT, "src/data/reponse1")

# (page, ancien, nouveau, reference de l'anomalie)
REMPL = [
    # --- N1 : especes recalculees ligne a ligne sur les annexes F --------
    ("penalites-et-amendes", "17 042,16 €", "17 333,18 €", "N1"),
    ("penalites-et-amendes", "17 042 €", "17 333 €", "N1"),
    ("suppressions-de-notes", "17 042,16 €", "17 333,18 €", "N1"),
    ("suppressions-de-notes", "17 042 €", "17 333 €", "N1"),
    ("suppressions-de-notes", "1,34 % du CA TTC", "1,36 % du CA TTC", "N1"),
    # --- N2 : liqueur de poire. CORRECTION DE LA CORRECTION.
    # Ce bloc ramenait 1 750 cl a 1 680 cl en supposant que la 25e bouteille
    # etait une eau-de-vie Poire William 42 degres. Verification faite sur les
    # factures FCBS elles-memes : c'est faux. La 25e bouteille porte le code
    # article 591050, celui de la liqueur Golden Eight, sur la facture 508974
    # du 15/03/2024, avec une accise de 0,70 L a 25 degres ; seule sa
    # designation est tronquee a l'impression, ce qui avait induit l'erreur.
    # Les eaux-de-vie de poire sont les codes 520131 (40 degres) et 520127
    # (42 degres), 140 cl au total, jamais comptes dans les 25 bouteilles.
    # Le service retient lui aussi 25 bouteilles (annexe n. 6, ligne
    # « Liqueur Golden 8 70 cl », 2 + 12 + 11).
    # Les entrees ci-dessous retablissent donc 1 750 cl.
    ("alcool-de-cuisine", "1 680 cl", "1 750 cl", "N2"),
    ("recon-6-alcool-plats-menus", "1 680 cl", "1 750 cl", "N2"),
    ("recon-6-alcool-plats-menus", "140 cl au lieu de 1 680", "140 cl au lieu de 1 750", "N2"),
    ("recon-6-alcool-plats-menus",
     "**24 bouteilles de 70 cl** de liqueur Golden Eight sont facturées, soit 16,8 L, quand nous "
     "chiffrons 4,1 L, situés sur les exercices 2 et 3, où 22 bouteilles ont été achetées",
     "**25 bouteilles de 70 cl** de liqueur Golden Eight sont facturées, soit 17,5 L, quand nous "
     "chiffrons 4,1 L, situés sur les exercices 2 et 3, où 23 bouteilles ont été achetées", "N2"),
    # --- Marc : ne retenir que le Marc de Bourgogne, ingredient du baba.
    # Les 980 cl additionnaient 280 cl de Marc de Bourgogne (4 bouteilles) et
    # 700 cl de Marc du Jura, produit distinct. L'argument de la fraction
    # d'exercice tient toujours : le service ne retient que 70 cl, soit une
    # bouteille, quand les factures en portent quatre.
    ("alcool-de-cuisine", "70 cl au lieu de 980 cl", "70 cl au lieu de 280 cl", "MARC"),
    ("alcool-de-cuisine", "Marc facturé sur 3 ans", "Marc de Bourgogne facturé sur 3 ans", "MARC"),
    ("alcool-de-cuisine", '"valeur": "980 cl"', '"valeur": "280 cl"', "MARC"),
    ("recon-6-alcool-plats-menus", "70 cl au lieu de 980", "70 cl au lieu de 280", "MARC"),
    # --- N3 : troisieme extrait du service, 32 lignes et non 36 ----------
    ("articles-a-zero-euro", "36 lignes", "32 lignes", "N3"),
    # --- N4 : cumul BIB recalcule ---------------------------------------
    ("degustation-offerte", "198,15 L", "198,31 L", "N4"),
    ("degustation-offerte", "+ 0,15", "+ 0,31", "N4"),
    # --- N5 : 139 727,76 / 5 367,47 = 26,03 -----------------------------
    ("penalites-et-amendes", "26,1 fois", "26,0 fois", "N5"),
    # --- N6 : 2 162,13 / 12,50 = 172,97 L -------------------------------
    ("recon-9-variation-de-stock", "175 à 200 L", "173 à 200 L", "N6"),
    ("recon-9-variation-de-stock", "175 à 200 litres", "173 à 200 litres", "N6"),
    # --- N7 : le script donne 839 menus ---------------------------------
    ("factures-sans-detail", "332 menus sur 840", "332 menus sur 839", "N7"),
    ("factures-sans-detail", "sur 840", "sur 839", "N7"),
    ("factures-sans-detail", "39,5 %", "39,6 %", "N7"),
    # --- N8 : 96,6 / 0,06 = 1 610 ---------------------------------------
    ("recon-5-alcool-cuisine", "1 609 verres", "1 610 verres", "N8"),
    # --- X5 : 98,7 % est le chiffre du service, le notre est 98,64 % -----
    ("recon-3-cremant-vendu",
     "Le taux de bancarisation de l’établissement est de 98,7 %",
     "Le taux de bancarisation de l’établissement, recalculé sur les annexes de règlements, "
     "est de 98,64 %", "X5"),
    # --- X7 : exercice clos en 2013, constats de 2019 --------------------
    ("reconstitution-cadre-general", "cinq ans aux exercices", "six ans aux exercices", "X7"),
    # --- J6 / non verifiable : ne pas affirmer une preuve negative -------
    ("perte-de-biere",
     "ne figure ni sur Légifrance, ni sur Juricaf, ni sur ArianeWeb",
     "n’a pu être retrouvée dans aucune base librement accessible", "NV"),
    ("recon-2-perte-biere",
     "ne figure ni sur Légifrance, ni sur Juricaf, ni sur ArianeWeb",
     "n’a pu être retrouvée dans aucune base librement accessible", "NV"),
]

# Clause dupliquee par le .replace() non idempotent de
# scripts/reponse1-penalites-finalisation.py (defaut 6.4 n° 2).
DUP = " au cumul des trois exercices, l’écart annuel allant de 0,60 % à 2,42 %"


def applique(doc, ancien, nouveau):
    """Remplace dans toutes les chaines du document. Retourne le nombre de coups."""
    n = 0

    def walk(o):
        nonlocal n
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str) and ancien in v:
                    o[k] = v.replace(ancien, nouveau)
                    n += v.count(ancien)
                else:
                    walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(doc)
    return n


def main():
    total = 0
    par_page = {}
    for slug, ancien, nouveau, ref in REMPL:
        chemin = os.path.join(DATA, slug + ".json")
        doc = json.load(open(chemin, encoding="utf-8"))
        n = applique(doc, ancien, nouveau)
        if n:
            json.dump(doc, open(chemin, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            par_page.setdefault(slug, []).append(f"{ref} : {n}x « {ancien[:40]} »")
            total += n

    # Deduplication de la clause repetee (on n'en garde qu'une).
    chemin = os.path.join(DATA, "penalites-et-amendes.json")
    doc = json.load(open(chemin, encoding="utf-8"))
    change = 0
    for s in doc["sections"]:
        t = s.get("texte", "")
        if t.count(DUP) > 1:
            avant = t
            while DUP + DUP in t:
                t = t.replace(DUP + DUP, DUP)
            if t != avant:
                s["texte"] = t
                change += 1
    if change:
        json.dump(doc, open(chemin, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        par_page.setdefault("penalites-et-amendes", []).append(
            f"6.4 : clause dupliquée réduite à une occurrence ({change} section)")

    # Clarification des KPI de la cascade (X4) : dire qu'ils reproduisent
    # l'etat du memoire de juillet, corrige plus bas dans la meme page.
    chemin = os.path.join(DATA, "cascade-10622-litres.json")
    doc = json.load(open(chemin, encoding="utf-8"))
    fait = False
    for s in doc["sections"]:
        if s.get("kind") != "kpis":
            continue
        for it in s.get("items", []):
            if it.get("valeur") == "85,5 %" and "corrigée plus bas" not in (it.get("sub") or ""):
                it["sub"] = ("conclusion du mémoire du 10/07/2026 reproduite p. 76, "
                             "corrigée plus bas dans cette page")
                fait = True
            if it.get("valeur") == "14,5 %" and "corrigée plus bas" not in (it.get("sub") or ""):
                it["sub"] = "soit 1 543 L (p. 76), valeur corrigée plus bas dans cette page"
                fait = True
    if fait:
        json.dump(doc, open(chemin, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        par_page.setdefault("cascade-10622-litres", []).append(
            "X4 : KPI 85,5 % et 14,5 % rattachés explicitement au mémoire de juillet")

    for slug in sorted(par_page):
        print(slug)
        for x in par_page[slug]:
            print("   ", x)
    print(f"\n{total} remplacement(s) de chaîne.")

    # Controle : plus aucune trace des valeurs fausses.
    restes = []
    for f in glob.glob(DATA + "/*.json"):
        t = open(f, encoding="utf-8").read()
        for mot in ("17 042", "1 750 cl", "198,15 L", "26,1 fois", "1 609 verres"):
            if mot in t:
                restes.append(f"{os.path.basename(f)} contient encore « {mot} »")
    print("CONTRÔLE :", "aucune valeur fausse résiduelle" if not restes else restes)


if __name__ == "__main__":
    main()
