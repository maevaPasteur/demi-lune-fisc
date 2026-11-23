#!/usr/bin/env python3
"""Annexes n° 69, 70 et 71 (inventaires, point 2.1) : révision des classeurs R2 en R3.

Copie chaque classeur source de public/documents/pieces-reponse-2/, applique les
modifications listées ci-dessous (chaque cellule n'est modifiée que si son texte
actuel contient l'ancre attendue), ajoute les calculs à formules, et enregistre
dans public/documents/pieces-lot1/. Les sources R2 ne sont pas modifiées.

Après exécution : recalcul LibreOffice headless puis contrôle des montants
(voir verifier()).
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import openpyxl
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "public/documents/pieces-reponse-2"
DST = ROOT / "public/documents/pieces-lot1"

F69 = ("R2-inventaire-de-stocks-chaine.xlsx", "69-R3-inventaire-report-des-totaux-sur-pages-datees.xlsx")
F70 = ("R2-inventaire-3-exercices.xlsx", "70-R3-inventaire-boissons-valeur-des-pages-datees.xlsx")
F71 = ("R2-stock-variation-310200.xlsx", "71-R3-variation-de-stock-boissons.xlsx")

journal = {F69[1]: [], F70[1]: [], F71[1]: []}
ancres_absentes = {F69[1]: [], F70[1]: [], F71[1]: []}
EUR = '# ##0,00 "€"'


def maj(wb, nom, feuille, cellule, ancre, nouveau=None, remplacer=None, ajouter=None):
    """Modifie une cellule si elle contient l'ancre.

    nouveau   : remplace tout le contenu
    remplacer : liste de couples (ancien, nouveau) appliqués dans le texte
    ajouter   : texte ajouté en fin de cellule
    """
    c = wb[feuille][cellule]
    ancien = c.value if c.value is not None else ""
    if ancre not in str(ancien):
        ancres_absentes[nom].append(f"{feuille}!{cellule} (ancre : {ancre!r})")
        return False
    texte = str(ancien)
    if nouveau is not None:
        texte = nouveau
    if remplacer:
        for a, b in remplacer:
            if a not in texte:
                ancres_absentes[nom].append(f"{feuille}!{cellule} (segment à remplacer absent : {a!r})")
                return False
            texte = texte.replace(a, b)
    if ajouter:
        texte = texte.rstrip() + ajouter
    c.value = texte
    journal[nom].append(f"{feuille}!{cellule} : {ancien!r} -> {texte!r}")
    return True


def note(nom, msg):
    journal[nom].append(msg)


# ---------------------------------------------------------------- annexe 69
def annexe_69():
    nom = F69[1]
    wb = openpyxl.load_workbook(SRC / F69[0])

    maj(wb, nom, "Calcul", "A1", "Calcul : la chaine",
        nouveau="Calcul : report des totaux des feuilles de comptage sur les pages datées, puis variation de stock")
    maj(wb, nom, "Calcul", "A2", "Bloc A : la somme des feuilles de comptage",
        remplacer=[("Bloc A : la somme des feuilles de comptage (SOMME.SI sur l'onglet Sources) est confrontee, categorie par categorie, au total porte sur la page datee.",
                    "Bloc A : la somme des totaux portés en pied des feuilles de comptage (SOMME.SI sur l'onglet Sources) est confrontée, catégorie par catégorie, au total reporté sur la page datée. Ce contrôle porte sur les reports, non sur l'addition des lignes de chaque feuille (voir l'annexe n° 154).")])
    maj(wb, nom, "Calcul", "A4", "A. Rapprochement",
        nouveau="A. Report : somme des pieds de feuilles de comptage et total de la page récapitulative datée")
    maj(wb, nom, "Calcul", "C5", "Somme des feuilles", nouveau="Somme des pieds de feuilles (SOMME.SI Sources)")
    # La qualification « nul » devient « sans écart » (formules F6:F11 et compteur F12).
    for r in range(6, 12):
        cel = f"F{r}"
        maj(wb, nom, "Calcul", cel, '"nul"',
            nouveau=f'=IF(ROUND(E{r},2)=0,"sans écart","ECART")')
    maj(wb, nom, "Calcul", "F12", '"nul"', nouveau='=COUNTIF(F6:F11,"sans écart")&" / "&COUNTA(F6:F11)')
    maj(wb, nom, "Calcul", "B12", "Rapprochements nuls / total",
        nouveau="Reports des pieds de feuilles sur la page datée sans écart / total")
    maj(wb, nom, "Calcul", "A15", "B. Stock de cloture",
        nouveau="B. Stock de clôture (boissons) et variation de stock, confrontés au montant retenu par le service (proposition, p. 34)")
    maj(wb, nom, "Calcul", "G17", "non repris dans nos etats",
        nouveau="stock au 31/03/2022 non produit (inventaire obtenu par le service auprès du cabinet comptable) : variation non calculable")
    maj(wb, nom, "Calcul", "G18", "coincide au centime", nouveau="égalité au centime")
    maj(wb, nom, "Calcul", "G19", "signe inverse au compte, releve pour memoire",
        nouveau="égalité en valeur absolue ; signe contraire à celui des inventaires ; origine (écriture ou report dans le tableau de la page 34) non déterminée")

    maj(wb, nom, "Methode", "A3", "jusqu'au compte de stock dont le service tire sa reconstitution",
        remplacer=[("la chaine des totaux de stock de boissons", "le report des totaux de stock de boissons"),
                   ("jusqu'au compte de stock dont le service tire sa reconstitution",
                    "jusqu'à la variation de stock boissons retenue par le service (proposition, p. 34)"),
                   ("(SOMME, SOMME.SI, IF, COUNTIF)", "(SOMME, SOMME.SI, SI, NB.SI)")])
    maj(wb, nom, "Methode", "A8", "31/03/2025 : feuilles manuscrites cotees 3/5 a 5/5",
        nouveau="   • 31/03/2025 : feuilles manuscrites cotées 1/5 à 5/5 ; alcools p.8 (1/5) = 557,99 / p.9 (2/5) = 1 524,04 / p.10 (3/5) = 1 686,48 ; sans alcool p.11 (4/5) = 478,41 / p.12 (5/5) = 287,33.")
    maj(wb, nom, "Methode", "A10", "CORRECTION DE LECTURE",
        remplacer=[(" : le sixieme rapprochement est nul, et la chaine est nulle 6 fois sur 6.",
                    " : le report de ce pied sur la page datée est sans écart.")],
        ajouter=" Cette somme retient la lecture 19,20 € de la ligne Schweppes, dont un chiffre est surchargé.")
    maj(wb, nom, "Methode", "A12", "montant enregistre en comptabilite",
        remplacer=[(", montant enregistre en comptabilite", "")])
    maj(wb, nom, "Methode", "A14", "Resultat : 6 rapprochements sur 6 nuls au cen",
        remplacer=[("la colonne F le qualifie (« nul » si arrondi a 0)", "la colonne F le qualifie (« sans écart » si arrondi à 0)"),
                   ("Resultat : 6 rapprochements sur 6 nuls au centime.",
                    "Résultat : les six totaux de feuilles sont reportés sans écart sur les pages datées. Ce contrôle porte sur les reports, non sur l'addition des lignes de chaque feuille (voir l'annexe n° 154).")])
    maj(wb, nom, "Methode", "A16", "312000 STOCK BOISSONS",
        remplacer=[("tableau consolide p.34-35)", "tableau p.34-35)")])
    maj(wb, nom, "Methode", "A18", "le service retient -273,41",
        nouveau="   • 2024-2025 : 4 807,66 - 4 534,25 = +273,41 € ; le tableau de la page 34 porte -273,41 € (égalité en valeur absolue, signe contraire ; origine non déterminée).")
    maj(wb, nom, "Methode", "A19", "n'etant pas repris dans nos etats",
        nouveau="   • 2022-2023 : l'inventaire au 31/03/2022 n'étant pas produit (le service l'a obtenu du cabinet comptable), la variation n'est pas calculable ici ; le service retient -800,83 €.")
    maj(wb, nom, "Methode", "A21", "PORTEE.",
        nouveau="PORTÉE. La variation 2023-2024 retenue par le service (-1 029,67 €) est, au centime, la différence entre deux inventaires datés. Cette pièce établit le report des totaux des feuilles sur les pages datées ; elle n'établit ni l'exactitude de chaque addition (voir l'annexe n° 154), ni la date matérielle des comptages.")

    maj(wb, nom, "Pages_datees", "A2", "le report manuscrit de la p.7 et l'ecriture comptable retiennent 4 807,66",
        remplacer=[("le report manuscrit de la p.7 et l'ecriture comptable retiennent 4 807,66 €",
                    "le report manuscrit de la p.7 retient 4 807,66 €")])

    # Cotes des feuilles 2025 dans l'onglet Sources (colonne D).
    maj(wb, nom, "Sources", "D16", "p.8 (feuille cotee 5/5)", nouveau="p.8 (feuille cotée 1/5)")
    maj(wb, nom, "Sources", "D17", "p.9 (feuille cotee 4/5)", nouveau="p.9 (feuille cotée 2/5)")
    maj(wb, nom, "Sources", "D18", "p.10 (feuille cotee 3/5)", nouveau="p.10 (feuille cotée 3/5)")
    maj(wb, nom, "Sources", "D19", "p.11", nouveau="p.11 (feuille cotée 4/5 ; re-sommation des 20 lignes = 478,41, lecture Schweppes 19,20)")
    maj(wb, nom, "Sources", "D20", "p.12 (feuille cotee 5/5)", nouveau="p.12 (feuille cotée 5/5)")

    wb.save(DST / nom)


# ---------------------------------------------------------------- annexe 70
def annexe_70():
    nom = F70[1]
    wb = openpyxl.load_workbook(SRC / F70[0])
    ws = wb["Calcul"]

    maj(wb, nom, "Calcul", "A1", "stock opposable",
        nouveau="R3 - Inventaire boissons : valeur du stock des pages datées, recalculée par formule")
    maj(wb, nom, "Calcul", "D3", "opposable", nouveau="Stock boissons des pages datées = somme (€)")
    maj(wb, nom, "Calcul", "A8", "Stock boissons opposable", remplacer=[("opposable", "des pages datées")])

    # Suppression de la colonne H (écart avec le mémoire du 10/07/2026).
    refs_h = []
    for w in wb:
        for row in w.iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value.startswith("=") and "H" in c.value.upper():
                    if w.title != "Calcul" or c.column_letter != "H":
                        if any(tok in c.value.upper() for tok in ("!H", "H4", "H5", "H6", "$H")):
                            refs_h.append(f"{w.title}!{c.coordinate} {c.value}")
    anciennes = [f"H{r}: {ws.cell(r, 8).value!r}" for r in range(1, ws.max_row + 1) if ws.cell(r, 8).value is not None]
    ws.delete_cols(8)
    note(nom, "Calcul, colonne H supprimée (" + " ; ".join(anciennes) + ")")
    note(nom, "Formules renvoyant à la colonne H : " + (" ; ".join(refs_h) if refs_h else "aucune"))

    maj(wb, nom, "Methode", "A1", "méthode", nouveau="R3 - Inventaire boissons des pages datées : méthode")
    maj(wb, nom, "Methode", "A3", "unique et opposable",
        nouveau="Objet : établir, par formule, la valeur du stock de boissons portée sur la page récapitulative datée de chaque clôture.")
    maj(wb, nom, "Methode", "A5", "Valeur opposable",
        nouveau="Valeur des pages datées = page récapitulative datée de chaque inventaire (PDF joints) :")
    maj(wb, nom, "Methode", "A8", "31/03/2025 : 765,74 + 3 768,51 = 4 534,25",
        ajouter=" Les lignes comptées valent 4 544,25 € ; le pied du folio 2/5 est inférieur de 10,00 € à la somme de ses lignes (annexe n° 154).")
    maj(wb, nom, "Methode", "A10", "Chiffres écartés (mémoire p.31)", nouveau=None, remplacer=None)
    wb["Methode"]["A10"].value = None
    note(nom, "Methode!A10 vidée")
    maj(wb, nom, "Methode", "A12", "Cohérence aval",
        nouveau="Cohérence aval : 3 777,99 - 4 807,66 = -1 029,67 € et 4 807,66 - 4 534,25 = +273,41 €, soit, en valeur absolue, les variations retenues par le service (proposition, p. 34) ; pour 2024-2025, le signe y est contraire.")

    maj(wb, nom, "Sources", "A1", "R2 - Inventaire", remplacer=[("R2 - ", "R3 - ")])
    maj(wb, nom, "Sources", "A2", "valeurs OPPOSABLES",
        remplacer=[("valeurs OPPOSABLES", "valeurs des pages datées"),
                   ("rappelée pour mémoire, ÉCARTÉE là où elle diverge", "écartée")])
    maj(wb, nom, "Calcul", "A10", "Divergence avec le mémoire p.31",
        nouveau="Rappel du mémoire du 10/07/2026 (colonne G) : ses totaux proviennent de la transcription jointe à ce mémoire et sont écartés ; seules les pages datées sont retenues.")

    wb.save(DST / nom)


# ---------------------------------------------------------------- annexe 71
def annexe_71():
    nom = F71[1]
    wb = openpyxl.load_workbook(SRC / F71[0])

    maj(wb, nom, "Sources", "A1", "(compte 310200)",
        nouveau="R3 - Variation de stock boissons (312000 selon les annexes 7 de la proposition) : sources")
    maj(wb, nom, "Sources", "C4", "310200",
        nouveau="Variation stock boissons (312000 selon les annexes 7 de la proposition) (€, signe du service)")
    maj(wb, nom, "Sources", "D5", "non détenu", nouveau="stock au 31/03/2022 non produit")

    maj(wb, nom, "Calcul", "A1", "R2 - Variation", remplacer=[("R2 - ", "R3 - ")])
    maj(wb, nom, "Calcul", "A3", "Le stock est plat",
        nouveau="1. Le stock est stable : variation cumulée rapportée aux achats")
    maj(wb, nom, "Calcul", "C5", "310200", nouveau="Variation retenue par le service, p. 34 (€)")
    maj(wb, nom, "Calcul", "A11", "le stock n'absorbe rien",
        remplacer=[(" : le stock n'absorbe rien, aucune bouteille n'est mise en réserve.", ".")],
        ajouter=" Au signe des inventaires pour 2024-2025 : −1 557,09 € (1,10 % des achats) ; consommation 98,90 %.")
    maj(wb, nom, "Calcul", "A14", "2. La variation du service est, au centime",
        nouveau="2. Variation retenue par le service et différence des inventaires datés (SI − SF)")
    maj(wb, nom, "Calcul", "B17", "non détenu", nouveau="stock 31/03/2022 non produit")
    maj(wb, nom, "Calcul", "A20", "signe inversé en sa défaveur",
        nouveau="2023-2024 : SI − SF = 3 777,99 − 4 807,66 = −1 029,67 €, égal au service (écart 0,00 €). 2024-2025 : SI − SF = +273,41 € ; le tableau de la page 34 porte −273,41 € (signe contraire ; origine non déterminée).")

    # Colonnes G à J : variation au signe des inventaires datés pour 2024-2025.
    ws = wb["Calcul"]
    bold = Font(bold=True)
    entetes = {
        "G5": "Variation au signe des inventaires datés (2023-2024 et 2024-2025 ; service pour 2022-2023) (€)",
        "H5": "|variation| / achats (inventaires datés)",
        "I5": "Consommation = achats + variation (inventaires datés) (€)",
        "J5": "Conso / achats (inventaires datés)",
    }
    for ref, txt in entetes.items():
        ws[ref] = txt
        ws[ref].font = bold
    ws["G6"] = "=C6"
    ws["G7"] = "=Sources!D6-Sources!E6"
    ws["G8"] = "=Sources!D7-Sources!E7"
    ws["G9"] = "=SUM(G6:G8)"
    for r in range(6, 10):
        ws[f"H{r}"] = f"=ABS(G{r})/B{r}*100"
        ws[f"I{r}"] = f"=B{r}+G{r}"
        ws[f"J{r}"] = f"=I{r}/B{r}*100"
        for col in "GI":
            ws[f"{col}{r}"].number_format = EUR
        for col in "HJ":
            ws[f"{col}{r}"].number_format = ws[f"D{r}"].number_format
    for col, w in (("G", 30), ("H", 18), ("I", 30), ("J", 16)):
        ws.column_dimensions[col].width = w
    note(nom, "Calcul!G5:J9 ajoutées (formules) : G6=C6 ; G7=Sources!D6-Sources!E6 ; G8=Sources!D7-Sources!E7 ; G9=SUM(G6:G8) ; H=ABS(G)/B*100 ; I=B+G ; J=I/B*100")

    # Méthode
    maj(wb, nom, "Methode", "A1", "310200", nouveau="R3 - Variation de stock boissons : méthode et sources")
    maj(wb, nom, "Methode", "A3", "stock de boissons est plat",
        nouveau="Objet : établir que, sur les trois exercices vérifiés, le stock de boissons est stable, et que la variation 2023-2024 retenue par le service est, au centime, celle des inventaires datés.")
    maj(wb, nom, "Methode", "A6", "Variation stocks Boissons (compte 310 200)",
        remplacer=[("(compte 310 200)", "(stock boissons, 312000 selon les annexes 7 de la proposition)")])
    maj(wb, nom, "Methode", "A15", "signe inversé, 546,82 €",
        nouveau="- 2024-2025 : SI − SF = +273,41 € ; le tableau de la page 34 porte −273,41 € (signe contraire ; origine non déterminée).")
    maj(wb, nom, "Methode", "A16", "non détenu",
        remplacer=[("stock d'ouverture au 31/03/2022 non détenu", "inventaire d'ouverture au 31/03/2022 non produit")])
    maj(wb, nom, "Methode", "A18", "prouvent l'absence de stock caché (stock plat)",
        remplacer=[("ces chiffres prouvent l'absence de stock caché (stock plat)", "ces chiffres établissent la stabilité du stock de boissons")])
    # Insertion sous A13 (les lignes 14 et suivantes descendent d'une ligne ; pas de formule dans l'onglet).
    wm = wb["Methode"]
    if "98,52 % des achats consommés" in str(wm["A13"].value):
        decal = [f"A{r}" for r in range(14, wm.max_row + 1) if wm[f"A{r}"].value is not None]
        wm.insert_rows(14)
        wm["A14"] = "- Au signe des inventaires pour 2024-2025 (chiffre du service pour 2022-2023) : variation cumulée -1 557,09 € (1,10 % des achats) ; consommation 140 163,29 € (98,90 %)."
        note(nom, "Methode!A14 insérée ; décalées d'une ligne : " + ", ".join(decal) + " (devenues A15 et suivantes)")
    else:
        ancres_absentes[nom].append("Methode!A13 (ancre : '98,52 % des achats consommés')")

    # Contrôle p34
    wc = wb["Controle p34"]
    maj(wb, nom, "Controle p34", "A18", "Lecture : 2022-2023 exact",
        nouveau="Lecture : 2022-2023 sans écart. 2023-2024 : le coût imprimé (183 679,65 €) diffère de 2 000,00 € de la somme des composantes imprimées en page 34, mais égale la somme des composantes de l'annexe 7-2 (achats de denrées 139 971,41 €). 2024-2025 : écart de 20,00 € ; l'annexe 7-3 porte une variation des denrées de -410,25 € au lieu de -430,25 €.")
    wc["A20"] = "Contrôle au regard des annexes 7-2 et 7-3 de la proposition (relues sur Proposition_3_Annexes_Boissons.pdf, annexe 7-2, et Proposition_4_Annexes_Finales.pdf, annexe 7-3)"
    wc["A20"].font = bold
    wc["A21"] = "Annexe 7-2 (2023-2024) : achats de denrées (601100) (€)"
    wc["C21"] = 139971.41
    wc["E21"] = "annexe 7-2, imprimé"
    wc["A22"] = "Annexe 7-3 (2024-2025) : variation des denrées (311000) (€)"
    wc["D22"] = -410.25
    wc["E22"] = "annexe 7-3, imprimé"
    wc["A23"] = "Coût d'achats recalculé avec les entrées des annexes 7 (€)"
    wc["B23"] = "=ROUND(B6+B7+B8+B9,2)"
    wc["C23"] = "=ROUND(C21+C7+C8+C9,2)"
    wc["D23"] = "=ROUND(D6+D7+D22+D9,2)"
    wc["E23"] = "formule"
    wc["A24"] = "Écart coût imprimé − recalculé avec les annexes 7 (€)"
    wc["B24"] = "=ROUND(B10-B23,2)"
    wc["C24"] = "=ROUND(C10-C23,2)"
    wc["D24"] = "=ROUND(D10-D23,2)"
    wc["E24"] = "formule"
    for r in (21, 22, 23, 24):
        for col in "BCD":
            wc[f"{col}{r}"].number_format = EUR
    note(nom, "Controle p34!A20:E24 ajoutées (C21=139 971,41 ; D22=-410,25 ; lignes 23-24 en formules)")

    wb.save(DST / nom)


# ---------------------------------------------------------------- recalcul et contrôle
def recalculer():
    for f in (F69[1], F70[1], F71[1]):
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(["soffice", "--headless", "--calc", "--convert-to", "xlsx", "--outdir", tmp, str(DST / f)],
                           check=True, capture_output=True)
            shutil.move(str(Path(tmp) / f), str(DST / f))


def recherche(f, mots):
    wb = openpyxl.load_workbook(DST / f)
    trouves = []
    for ws in wb:
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str):
                    for m in mots:
                        if m.lower() in c.value.lower():
                            trouves.append(f"{ws.title}!{c.coordinate} [{m}] {c.value[:140]!r}")
    return trouves


def verifier():
    ok = True

    def eq(lbl, obtenu, attendu, tol=0.005):
        nonlocal ok
        bon = obtenu is not None and abs(float(obtenu) - attendu) <= tol
        ok &= bon
        print(f"  {lbl:70s} attendu {attendu:>12} obtenu {obtenu!s:>14} {'OK' if bon else 'ECART'}")

    w = openpyxl.load_workbook(DST / F69[1], data_only=True)
    c, p = w["Calcul"], w["Pages_datees"]
    print("69")
    eq("stock 31/03/2023", p["D5"].value, 3777.99)
    eq("stock 31/03/2024", p["D6"].value, 4807.66)
    eq("stock 31/03/2025", p["D7"].value, 4534.25)
    eq("variation 2023-2024", c["D18"].value, -1029.67)
    eq("variation 2024-2025", c["D19"].value, 273.41)
    print("  reports sans écart :", c["F12"].value, "(attendu 6 / 6)")
    ok &= c["F12"].value == "6 / 6"

    w = openpyxl.load_workbook(DST / F70[1], data_only=True)
    c = w["Calcul"]
    print("70")
    for r, v in ((4, 3777.99), (5, 4807.66), (6, 4534.25)):
        eq(f"stock pages datées ligne {r}", c[f"D{r}"].value, v)
    print("  colonnes Calcul ligne 3 :", [c.cell(3, k).value for k in range(1, 9)])

    w = openpyxl.load_workbook(DST / F71[1], data_only=True)
    c, k = w["Calcul"], w["Controle p34"]
    print("71")
    eq("achats boissons 3 ans", c["B9"].value, 141720.38)
    eq("variation cumulée service", c["C9"].value, -2103.91)
    eq("ratio service %", round(c["D9"].value, 2), 1.48)
    eq("consommation service", c["E9"].value, 139616.47)
    eq("conso/achats service %", round(c["F9"].value, 2), 98.52)
    eq("variation cumulée inventaires", c["G9"].value, -1557.09)
    eq("ratio inventaires %", round(c["H9"].value, 2), 1.10)
    eq("consommation inventaires", c["I9"].value, 140163.29)
    eq("conso/achats inventaires %", round(c["J9"].value, 2), 98.90)
    eq("2024-2025 consommation inventaires", c["I8"].value, 47372.25)
    eq("p34 écart 2023-2024 avec annexe 7-2", k["C24"].value, 0.0)
    eq("p34 écart 2024-2025 avec annexe 7-3", k["D24"].value, 0.0)
    eq("p34 écart 2023-2024 imprimé", k["C14"].value, 2000.0)
    eq("p34 écart 2024-2025 imprimé", k["D14"].value, 20.0)
    return ok


if __name__ == "__main__":
    DST.mkdir(parents=True, exist_ok=True)
    annexe_69()
    annexe_70()
    annexe_71()
    recalculer()
    for f in journal:
        print(f"\n===== {f}\nModifications appliquées :")
        for l in journal[f]:
            print("  -", l)
        print("Ancres non trouvées :", ancres_absentes[f] or "aucune")
    mots69_71 = ["rapprochements nuls", "nuls", "opposable", "310200", "310 200", "plat", "cave cachée",
                 "non revendiqué", "écriture comptable", "ecriture comptable", "chaine des totaux", "signe inversé", "signe inverse"]
    for f in journal:
        print(f"\nOccurrences restantes dans {f} :")
        for t in recherche(f, mots69_71):
            print("  ", t)
    print("\nMontants de contrôle :")
    sys.exit(0 if verifier() else 1)
