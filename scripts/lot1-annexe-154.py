#!/usr/bin/env python3
"""Annexe n° 154 : erreurs d'addition et de valorisation des inventaires d'origine (3 clôtures).

Entrées (versionnées dans scripts/lot1-annexe-154/) :
  inv2023.csv, inv2024.csv, inv2025.csv : transcription ligne à ligne des PDF
    public/documents/inventaires/Inventaire_Demi_Lune_20YY-03-31.pdf (annexes 63, 64, 65),
    relue sur les images à 300 dpi ; colonnes type;page;feuille;libelle;quantite;prix;valeur;lecture;observation
  prix-non-mis-a-jour.csv : lignes dont le prix d'inventaire est antérieur au dernier prix facturé
    par Franche-Comté Boissons Service avant la clôture (relu sur les factures).
Sortie : public/documents/pieces-lot1/154-R3-inventaires-erreurs-addition-valorisation-3-clotures.xlsx
Toutes les sommes, écarts, nets et ratios sont des formules ; recalcul LibreOffice puis contrôle.
"""
import csv
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(__file__).resolve().parent / "lot1-annexe-154"
OUT = ROOT / "public/documents/pieces-lot1/154-R3-inventaires-erreurs-addition-valorisation-3-clotures.xlsx"

EUR = '# ##0,00 "€"'
EUR3 = '# ##0,00## "€"'
PCT = '0,00 %'
B = Font(bold=True)
H = Font(bold=True, size=12)
GRIS = PatternFill("solid", fgColor="EEEEEE")
WRAP = Alignment(wrap_text=True, vertical="top")
ANNEXE = {"2023": 63, "2024": 64, "2025": 65}
STOCK_TOTAL = {"2023": 7030.61, "2024": 9873.07, "2025": 9774.17}


def num(s):
    s = (s or "").strip()
    if s == "":
        return None
    return float(s.replace(",", "."))


def lire(an):
    return list(csv.DictReader(open(DATA / f"inv{an}.csv", encoding="utf-8"), delimiter=";"))


# ------------------------------------------------------------------ onglets Lignes
class Lignes:
    def __init__(self, wb, an):
        self.an = an
        self.nom = f"Lignes_{an}"
        self.ws = wb.create_sheet(self.nom)
        self.rows = []      # (page, feuille, libelle, row)
        self.blocs = []     # dict(feuille, page, somme_row, pieds=[(libelle,row,ecart_row)])
        self.recap = []     # (libelle, row)
        self.nb = {}

    def ref(self, col, row, absolu=True):
        return f"'{self.nom}'!${col}${row}" if absolu else f"'{self.nom}'!{col}{row}"

    def construire(self):
        ws = self.ws
        data = lire(self.an)
        ws["A1"] = f"Inventaire au 31/03/{self.an} (annexe n° {ANNEXE[self.an]}) : transcription ligne à ligne de l'état d'origine"
        ws["A1"].font = H
        ws["A2"] = "Valeurs lues sur les images du PDF. Colonnes G et H : formules. Sous chaque feuille : somme des lignes (formule), pied porté (lu), écart (formule)."
        hdr = ["Page", "Feuille / catégorie", "Libellé (tel qu'écrit)", "Quantité lue", "Prix unitaire lu",
               "Valeur portée sur l'état", "Quantité × prix (formule)", "Écart portée moins calcul (formule)", "Lecture", "Observation"]
        for i, h in enumerate(hdr, 1):
            c = ws.cell(4, i, h)
            c.font = B
            c.fill = GRIS
            c.alignment = WRAP
        ws.freeze_panes = "A5"
        r = 5
        # page 1 récapitulative
        rec = [x for x in data if x["type"] == "RECAP"]
        if rec:
            ws.cell(r, 1, "Page récapitulative").font = B
            r += 1
            for x in rec:
                ws.cell(r, 1, int(x["page"]))
                ws.cell(r, 2, x["feuille"])
                ws.cell(r, 3, x["libelle"])
                c = ws.cell(r, 6, num(x["valeur"]))
                c.number_format = EUR
                ws.cell(r, 9, x["lecture"] or "sûre")
                ws.cell(r, 10, x["observation"])
                self.recap.append((x["page"], x["libelle"], r))
                r += 1
            r += 1
        # feuilles, dans l'ordre d'apparition
        ordre = []
        for x in data:
            if x["type"] in ("LIGNE", "PIED") and x["feuille"] not in ordre:
                ordre.append(x["feuille"])
        for f in ordre:
            lignes = [x for x in data if x["feuille"] == f and x["type"] == "LIGNE"]
            pieds = [x for x in data if x["feuille"] == f and x["type"] == "PIED"]
            pages = sorted({int(x["page"]) for x in lignes + pieds})
            ws.cell(r, 1, f"p.{pages[0]}" + (f"-{pages[-1]}" if len(pages) > 1 else ""))
            ws.cell(r, 2, f).font = B
            r += 1
            r0 = r
            for x in lignes:
                ws.cell(r, 1, int(x["page"]))
                ws.cell(r, 2, f)
                ws.cell(r, 3, x["libelle"])
                for col, k in ((4, "quantite"), (5, "prix"), (6, "valeur")):
                    v = num(x[k])
                    if v is not None:
                        ws.cell(r, col, v)
                ws.cell(r, 5).number_format = EUR3
                ws.cell(r, 6).number_format = EUR3
                ws.cell(r, 7, f'=IF(AND(ISNUMBER(D{r}),ISNUMBER(E{r})),ROUND(D{r}*E{r},2),"")').number_format = EUR
                ws.cell(r, 8, f'=IF(AND(ISNUMBER(F{r}),ISNUMBER(G{r})),ROUND(F{r}-G{r},2),"")').number_format = EUR
                ws.cell(r, 9, x["lecture"] or "sûre")
                ws.cell(r, 10, x["observation"])
                self.rows.append((x["page"], f, x["libelle"], r))
                r += 1
            r1 = r - 1
            self.nb[f] = len(lignes)
            if not lignes:
                bloc = {"feuille": f, "pages": pages, "somme_row": None, "pieds": []}
                for p in pieds:
                    ws.cell(r, 1, int(p["page"]))
                    ws.cell(r, 3, f"Report porté : {p['libelle']}").font = B
                    ws.cell(r, 6, num(p["valeur"])).number_format = EUR3
                    ws.cell(r, 9, p["lecture"] or "sûre")
                    ws.cell(r, 10, p["observation"])
                    bloc["pieds"].append((p["libelle"], r, None))
                    r += 1
                self.blocs.append(bloc)
                r += 1
                continue
            ws.cell(r, 3, "Somme des lignes").font = B
            ws.cell(r, 6, f"=SUM(F{r0}:F{r1})").number_format = EUR3
            somme_row = r
            r += 1
            bloc = {"feuille": f, "pages": pages, "somme_row": somme_row, "pieds": []}
            for p in pieds:
                ws.cell(r, 1, int(p["page"]))
                ws.cell(r, 3, f"Pied porté sur la feuille : {p['libelle']}").font = B
                ws.cell(r, 6, num(p["valeur"])).number_format = EUR3
                ws.cell(r, 9, p["lecture"] or "sûre")
                ws.cell(r, 10, p["observation"])
                pr = r
                r += 1
                ws.cell(r, 3, "Écart pied moins somme")
                ws.cell(r, 6, f"=ROUND(F{pr}-F{somme_row},2)").number_format = EUR
                bloc["pieds"].append((p["libelle"], pr, r))
                r += 1
            self.blocs.append(bloc)
            r += 1
        for col, w in zip("ABCDEFGHIJ", (7, 26, 46, 10, 12, 14, 14, 14, 34, 60)):
            ws.column_dimensions[col].width = w
        for row in ws.iter_rows(min_row=5):
            for c in row:
                if c.column in (3, 9, 10):
                    c.alignment = WRAP

    def ligne(self, page, motif):
        t = [r for (p, f, lib, r) in self.rows if p == str(page) and re.search(motif, lib, re.I)]
        if len(t) != 1:
            raise SystemExit(f"{self.nom} p.{page} /{motif}/ : {len(t)} correspondance(s)")
        return t[0]

    def bloc(self, motif):
        t = [b for b in self.blocs if re.search(motif, b["feuille"], re.I)]
        if len(t) != 1:
            raise SystemExit(f"{self.nom} feuille /{motif}/ : {len(t)} correspondance(s) {[b['feuille'] for b in self.blocs]}")
        return t[0]

    def pied(self, motif_feuille, motif_pied=None):
        b = self.bloc(motif_feuille)
        ps = b["pieds"] if motif_pied is None else [p for p in b["pieds"] if re.search(motif_pied, p[0], re.I)]
        if len(ps) != 1:
            raise SystemExit(f"{self.nom} pied /{motif_feuille}/{motif_pied}/ : {len(ps)}")
        return ps[0][1], b["somme_row"]

    def recap_row(self, motif, page="1"):
        t = [r for (p, lib, r) in self.recap if p == page and re.search(motif, lib, re.I)]
        if len(t) != 1:
            raise SystemExit(f"{self.nom} recap /{motif}/ : {len(t)}")
        return t[0]


# ------------------------------------------------------------------ définition des erreurs
def erreurs(L):
    """Chaque erreur : (clôture, groupe, pièce, nature, porté, correct, variante, statut).

    porté / correct : formules ; variante : formule donnant le montant « sens » de la lecture
    alternative, ou None. Sens = porté - correct (positif : stock surévalué).
    """
    E = []
    a = L["2023"]
    # 2023
    pr, sr = a.pied(r"entretien")
    E.append(("2023", "Autres (entretien)", "INV23 p.9, produits d'entretien",
              "Pied 995,27 € contre somme des lignes 829,39 € ; la ligne « 8 Gels Fondue », sans valeur, est portée sous le pied ; la page récapitulative mentionne le gel fondue dans cette catégorie",
              a.ref("F", pr), a.ref("F", sr), "0", "écart vrai ; qualification non déterminable : + 165,88 € si le pied n'intègre pas la ligne « 8 Gels Fondue », 0,00 € s'il l'intègre (variante)"))
    r = a.ligne(12, r"aff?lig") if any(p == "12" and re.search(r"aff?lig", l, re.I) for p, f, l, _ in a.rows) else a.ligne(11, r"aff?lig")
    E.append(("2023", "Boissons", "INV23, tableau des alcools, fût Affligem",
              "« 4 × 4,07 = 16,28 » : 4 fûts de 8 litres valorisés au prix du litre (valeur correcte 4 × 8 × 4,07)",
              a.ref("F", r), f"ROUND({a.ref('D', r)}*8*{a.ref('E', r)},2)", None,
              "si le comptage est postérieur au 23/03/2023 (prix de 4,07 € le litre facturé à partir du 23/02/2023)"))
    r = a.ligne(7, r"entrec")
    E.append(("2023", "Denrées", "INV23 p.7, viande", "Entrecôte : 5,48 × 17,01 = 93,21 € ; écrit 92,21 €",
              a.ref("F", r), a.ref("G", r), None, "vrai"))
    r = a.ligne(6, r"camembert")
    E.append(("2023", "Denrées", "INV23 p.6, crèmerie", "Camembert : « 15 + 6 = 21 à 1,88 » = 39,48 € ; écrit 26,28 €",
              a.ref("F", r), a.ref("G", r), None, "vrai (lecture « 15 + 6 = 21 », seule cohérente avec l'addition portée)"))
    pr, sr = a.pied(r"cr[èe]merie")
    E.append(("2023", "Denrées", "INV23 p.6, crèmerie", "Pied 158,85 € contre somme des valeurs portées 158,93 €",
              a.ref("F", pr), a.ref("F", sr), None, "vrai"))
    pr, sr = a.pied(r"listing p3-p5 surgel")
    E.append(("2023", "Denrées", "INV23 p.3, listing de denrées (surgelés)",
              "Le sous-total imprimé « Sous-total surg » (1 022,22 €) n'inclut pas la dernière ligne au-dessus de lui (sauce pesto, 1 × 24,42 €) ; somme des lignes 1 046,64 €",
              a.ref("F", pr), a.ref("F", sr), None, "vrai"))
    rr = a.recap_row(r"aliment")
    b_ns = a.pied(r"non surgel", r"manuscrit")[0]
    E.append(("2023", "Denrées", "INV23 p.1, page récapitulative",
              "Alimentaire porté 1 734,15 € ; sous-totaux du listing 1 022,22 € (imprimé) + 711,96 € (manuscrit) = 1 734,18 €",
              a.ref("F", rr), f"ROUND({a.ref('F', a.pied(r'listing p3-p5 surgel')[0])}+{a.ref('F', b_ns)},2)", None, "vrai"))
    # 2024 et 2025 : voir erreurs_2024() et erreurs_2025()
    E += erreurs_2024(L["2024"])
    E += erreurs_2025(L["2025"])
    return E


def erreurs_2024(b):
    return ERREURS_2024(b)


def erreurs_2025(c):
    E = []
    pr, sr = c.pied(r"boissons 2/5")
    E.append(("2025", "Boissons", "INV25 p.9, boissons (folio 2/5)", "Pied 1 524,04 € contre somme des lignes 1 534,04 €",
              c.ref("F", pr), c.ref("F", sr), None, "vrai"))
    pr, sr = c.pied(r"boissons 4/5")
    r = c.ligne(11, r"schweppes")
    E.append(("2025", "Boissons", "INV25 p.11, boissons (folio 4/5)", "Schweppes : valeur lue 19,20 € (30 × 0,64) ou 19,80 € (chiffre surchargé) ; le pied 478,41 € vaut la somme avec 19,20 €",
              c.ref("F", pr), c.ref("F", sr), "ROUND(-0.6,2)", "lecture : 0,00 € avec 19,20 ; - 0,60 € avec 19,80 (variante)"))
    pr, sr = c.pied(r"denr[ée]es 2/4")
    E.append(("2025", "Denrées", "INV25 p.4, denrées (folio 2/4)", "Pied 1 044,52 € contre somme des lignes 1 044,53 € (cassonade lue 6,68 €) ou 1 044,45 € (cassonade lue 6,60 €)",
              c.ref("F", pr), c.ref("F", sr), "ROUND(0.07,2)", "lecture : - 0,01 € avec 6,68 ; + 0,07 € avec 6,60 (variante)"))
    pr, sr = c.pied(r"denr[ée]es 3/4")
    E.append(("2025", "Denrées", "INV25 p.5, denrées (folio 3/4)", "Pied 794,17 € contre somme des lignes 754,17 €",
              c.ref("F", pr), c.ref("F", sr), "ROUND(39.8,2)", "vrai ; morbier lu 23,60 € (2 × 11,80) ou 23,80 € : + 40,00 € ou + 39,80 € (variante)"))
    r = c.ligne(7, r"pesto")
    E.append(("2025", "Denrées", "INV25 p.7, denrées (folio 4/4)", "Pesto : 2 × 7,28 = 14,56 € ; écrit 44,56 €",
              c.ref("F", r), c.ref("G", r), None, "vrai"))
    r = c.ligne(7, r"pommes? saut")
    E.append(("2025", "Denrées", "INV25 p.7, denrées (folio 4/4)", "Pommes sautées : 16 × 7,52 = 120,32 € ; écrit 120,40 €",
              c.ref("F", r), c.ref("G", r), None, "vrai"))
    rr = c.recap_row(r"DIVE\]?RS")
    sr = c.bloc(r"divers")["somme_row"]
    E.append(("2025", "Autres (divers)", "INV25 p.13 et p.1, divers non comestibles", "Page datée 1 585,00 € ; somme des lignes de la feuille 1 585,03 €",
              c.ref("F", rr), c.ref("F", sr), None, "vrai"))
    return E


def ERREURS_2024(b):
    E = []
    pr, sr = b.pied(r"FCBS p6 avec")
    E.append(("2024", "Boissons", "INV24 p.6, fiche FCBS (feuille 5), avec alcool", "Pied 1 704,49 € contre somme des lignes 1 702,49 € (le chiffre des unités du pied est surchargé)",
              b.ref("F", pr), b.ref("F", sr), None, "vrai"))
    pr, sr = b.pied(r"FCBS p3 sans")
    E.append(("2024", "Boissons", "INV24 p.3, fiche FCBS (feuille 2), sans alcool", "Pied 585,13 € contre somme des lignes 585,19 €",
              b.ref("F", pr), b.ref("F", sr), None, "vrai"))
    r = b.ligne(3, r"granini pomme")
    E.append(("2024", "Boissons", "INV24 p.3, fiche FCBS (feuille 2)", "Granini pomme : 9 × 2,80 = 25,20 € ; écrit 18,72 € (quantité surchargée)",
              b.ref("F", r), b.ref("G", r), None, "lecture incertaine de la quantité (9 surchargé)"))
    r = b.ligne(3, r"granini tomate")
    E.append(("2024", "Boissons", "INV24 p.3, fiche FCBS (feuille 2)", "Granini tomate : 23 × 1,02 = 23,46 € ; écrit 23,40 €",
              b.ref("F", r), b.ref("G", r), None, "vrai"))
    r = b.ligne(3, r"402005 coca")
    E.append(("2024", "Boissons", "INV24 p.3, fiche FCBS (feuille 2)", "Coca : 116 × 0,66 = 76,56 € ; écrit 71,94 €",
              b.ref("F", r), b.ref("G", r), None, "vrai"))
    r = b.ligne(4, r"cidre doux")
    E.append(("2024", "Boissons", "INV24 p.4, fiche FCBS (feuille 3)", "Cidre doux : quantité lue « 12 + 6 » = 18, soit 52,02 € ; écrit 46,24 € (= 16 × 2,89)",
              b.ref("F", r), b.ref("G", r), "0", "lecture : - 5,78 € avec « 12 + 6 » ; 0,00 € avec « 12 + 4 », lecture retenue par le service dans son annexe 1 (variante)"))
    pr, sr = b.pied(r"FCBS p5 avec")
    r = b.ligne(5, r"poliakov")
    E.append(("2024", "Boissons", "INV24 p.5, fiche FCBS (feuille 4)", "Vodka Poliakov : valeur lue 9,88 € ou 9,28 € (1 × 9,28) ; le pied 900,99 € vaut la somme avec 9,28 €",
              b.ref("F", pr), f"ROUND({b.ref('F', sr)}-{b.ref('F', r)}+{b.ref('G', r)},2)", None, "sans effet sur la valeur de la feuille, quelle que soit la lecture"))
    rr = b.recap_row(r"total \(boissons\)")
    rb = b.pied(r"report boissons", r"total boissons")[0]
    E.append(("2024", "Boissons", "INV24 p.1, page récapitulative", "« Total : 4 807.60 € » imprimé ; ses deux lignes (870,59 € + 3 937,07 €) et le report manuscrit de la p.7 font 4 807,66 € ; coquille propagée au total général de 9 873,07 €",
              b.ref("F", rr), b.ref("F", rb), None, "vrai"))
    r = b.ligne(14, r"cremeux|crémeux")
    E.append(("2024", "Denrées", "INV24 p.14, crèmerie", "Crémeux : 8 × 4,17 = 33,36 € ; écrit 50,04 €",
              b.ref("F", r), b.ref("G", r), None, "vrai sur la pièce"))
    r = b.ligne(12, r"polenta")
    E.append(("2024", "Denrées", "INV24 p.12, surgelés", "Polenta : « 1 carton + 1/2 carton » × 55,27 = 82,91 € ; écrit 138,17 € (= 2,5 × 55,27)",
              b.ref("F", r), b.ref("G", r), None, "vrai sur la pièce"))
    pr, sr = b.pied(r"suite surgel")
    E.append(("2024", "Denrées", "INV24 p.12, surgelés", "Truite : valeur lue 164,22 € ou 161,22 € (troisième chiffre) ; pied 1 011,40 €, égal à la somme avec 161,22 €",
              b.ref("F", pr), b.ref("F", sr), "0", "lecture : - 3,00 € avec 164,22 ; 0,00 € avec 161,22 (variante)"))
    r = b.ligne(8, r"entrec")
    E.append(("2024", "Denrées", "INV24 p.8, viande", "Entrecôte : 10,22 × 24 = 245,28 € ; écrit 245,20 €",
              b.ref("F", r), b.ref("G", r), None, "vrai"))
    r = b.ligne(8, r"jambon blanc")
    E.append(("2024", "Denrées", "INV24 p.8, viande", "Jambon blanc : 6,5 × 13,40 = 87,10 € ; écrit 87,44 €",
              b.ref("F", r), b.ref("G", r), None, "lecture « 6,5 » incertaine"))
    return E


# ------------------------------------------------------------------ autres onglets
def onglet_erreurs(wb, E):
    ws = wb.create_sheet("Erreurs")
    ws["A1"] = "Erreurs d'addition et de valorisation relevées sur les états d'origine"
    ws["A1"].font = H
    ws["A2"] = "Convention : sens = valeur portée sur l'état moins valeur correcte. Un montant positif signifie un stock surévalué. Colonne H : montant de la lecture alternative, s'il y en a une."
    hdr = ["Clôture", "Groupe", "Pièce", "Nature", "Valeur portée", "Valeur correcte (formule)", "Sens et montant (formule)",
           "Variante (lecture alternative)", "Montant bas (formule)", "Montant haut (formule)", "Statut", "Valeur absolue maximale (formule)"]
    for i, h in enumerate(hdr, 1):
        c = ws.cell(4, i, h)
        c.font = B
        c.fill = GRIS
        c.alignment = WRAP
    ws.freeze_panes = "A5"
    r = 5
    lignes = {}
    for an in ("2023", "2024", "2025"):
        r0 = r
        for (cl, grp, piece, nature, porte, correct, variante, statut) in [e for e in E if e[0] == an]:
            ws.cell(r, 1, f"31/03/{cl}")
            ws.cell(r, 2, grp)
            ws.cell(r, 3, piece)
            ws.cell(r, 4, nature)
            ws.cell(r, 5, f"={porte}").number_format = EUR3
            ws.cell(r, 6, f"={correct}").number_format = EUR3
            ws.cell(r, 7, f"=ROUND(E{r}-F{r},2)").number_format = EUR
            if variante is not None:
                ws.cell(r, 8, f"={variante}").number_format = EUR
                ws.cell(r, 9, f"=MIN(G{r},H{r})").number_format = EUR
                ws.cell(r, 10, f"=MAX(G{r},H{r})").number_format = EUR
            else:
                ws.cell(r, 9, f"=G{r}").number_format = EUR
                ws.cell(r, 10, f"=G{r}").number_format = EUR
            ws.cell(r, 11, statut)
            ws.cell(r, 12, f"=MAX(ABS(I{r}),ABS(J{r}))").number_format = EUR
            r += 1
        r1 = r - 1
        lignes[an] = {"r0": r0, "r1": r1}
        for lab, col in (("Net (lecture principale)", "G"), ("Net, bas", "I"), ("Net, haut", "J")):
            ws.cell(r, 3, f"{lab} au 31/03/{an}").font = B
            ws.cell(r, 7 if col == "G" else (9 if col == "I" else 10), f"=ROUND(SUM({col}{r0}:{col}{r1}),2)").number_format = EUR
            lignes[an][lab] = (col if col != "G" else "G", r)
            r += 1
        ws.cell(r, 3, f"Brut (valeurs absolues, lecture maximale) au 31/03/{an}").font = B
        ws.cell(r, 7, f"=ROUND(SUM(L{r0}:L{r1}),2)").number_format = EUR
        lignes[an]["brut"] = r
        r += 2
    for col, w in zip("ABCDEFGHIJKL", (11, 16, 30, 60, 14, 16, 14, 14, 13, 13, 50, 14)):
        ws.column_dimensions[col].width = w
    for row in ws.iter_rows(min_row=5):
        for c in row:
            if c.column in (3, 4, 11):
                c.alignment = WRAP
    return ws, lignes


def onglet_pieds(wb, L):
    ws = wb.create_sheet("Pieds")
    ws["A1"] = "Pieds de feuilles : somme des lignes (formule) et pied porté"
    ws["A1"].font = H
    hdr = ["Clôture", "Page(s)", "Feuille / catégorie", "Nombre de lignes", "Somme des lignes (formule)", "Pied porté", "Écart pied moins somme (formule)", "Libellé du pied"]
    for i, h in enumerate(hdr, 1):
        c = ws.cell(3, i, h)
        c.font = B
        c.fill = GRIS
        c.alignment = WRAP
    ws.freeze_panes = "A4"
    r = 4
    for an in ("2023", "2024", "2025"):
        x = L[an]
        for b in x.blocs:
            if b["somme_row"] is None:
                continue
            pp = b["pieds"] or [("aucun pied porté sur la feuille", None, None)]
            for lib, pr, _ in pp:
                ws.cell(r, 1, f"31/03/{an}")
                ws.cell(r, 2, ", ".join(str(p) for p in b["pages"]))
                ws.cell(r, 3, b["feuille"])
                ws.cell(r, 4, x.nb[b["feuille"]])
                ws.cell(r, 5, f"={x.ref('F', b['somme_row'])}").number_format = EUR3
                if pr:
                    ws.cell(r, 6, f"={x.ref('F', pr)}").number_format = EUR3
                    ws.cell(r, 7, f"=ROUND(F{r}-E{r},2)").number_format = EUR
                ws.cell(r, 8, lib)
                r += 1
        r += 1
    for col, w in zip("ABCDEFGH", (11, 10, 40, 10, 16, 14, 14, 40)):
        ws.column_dimensions[col].width = w
    return ws


def onglet_prix(wb):
    ws = wb.create_sheet("Prix_non_mis_a_jour")
    ws["A1"] = "Prix d'inventaire antérieurs au dernier prix facturé par Franche-Comté Boissons Service avant la clôture"
    ws["A1"].font = H
    ws["A2"] = "Écart positif : le prix d'inventaire est inférieur au dernier prix facturé avant la clôture, le stock est minoré d'autant. Ces écarts jouent en sens inverse des erreurs de l'onglet Erreurs."
    hdr = ["Clôture", "Article", "Quantité", "Prix d'inventaire", "Dernier prix facturé", "Date de la dernière facture", "Code fournisseur",
           "Libellé facture", "N° facture", "Écart = quantité × (dernier prix - prix d'inventaire) (formule)", "Observation"]
    for i, h in enumerate(hdr, 1):
        c = ws.cell(4, i, h)
        c.font = B
        c.fill = GRIS
        c.alignment = WRAP
    ws.freeze_panes = "A5"
    rows = list(csv.DictReader(open(DATA / "prix-non-mis-a-jour.csv", encoding="utf-8"), delimiter=";"))
    r = 5
    tot = {}
    for an in ("2023", "2025"):
        r0 = r
        for x in [y for y in rows if y["cloture"] == an]:
            ws.cell(r, 1, f"31/03/{an}")
            ws.cell(r, 2, x["article"])
            ws.cell(r, 3, num(x["quantite"]))
            ws.cell(r, 4, num(x["prix_inventaire"])).number_format = EUR
            ws.cell(r, 5, num(x["dernier_prix_facture"])).number_format = EUR
            ws.cell(r, 6, x["date_derniere_facture"])
            ws.cell(r, 7, x["code_fournisseur"])
            ws.cell(r, 8, x["libelle_facture"])
            ws.cell(r, 9, x["facture"])
            ws.cell(r, 10, f"=ROUND(C{r}*(E{r}-D{r}),2)").number_format = EUR
            ws.cell(r, 11, x["observation"])
            r += 1
        ws.cell(r, 2, f"Total au 31/03/{an}").font = B
        ws.cell(r, 3, f"=COUNTA(B{r0}:B{r-1})")
        ws.cell(r, 10, f"=ROUND(SUM(J{r0}:J{r-1}),2)").number_format = EUR
        tot[an] = r
        r += 2
    for col, w in zip("ABCDEFGHIJK", (11, 30, 9, 12, 12, 13, 10, 40, 10, 18, 50)):
        ws.column_dimensions[col].width = w
    return tot


def onglet_synthese(wb, lig, tot_prix):
    ws = wb.create_sheet("Synthese", 1)
    ws["A1"] = "Synthèse : erreurs d'addition et de valorisation relevées sur les états d'origine (tableau 4 bis)"
    ws["A1"].font = H
    hdr = ["Clôture", "Erreurs relevées", "Sens et montant, bas (formule)", "Sens et montant, haut (formule)", "Effet net sur la valeur du stock, bas (formule)", "Effet net, haut (formule)"]
    for i, h in enumerate(hdr, 1):
        c = ws.cell(3, i, h)
        c.font = B
        c.fill = GRIS
        c.alignment = WRAP
    r = 4
    res = {}
    for an in ("2023", "2024", "2025"):
        r0, r1 = lig[an]["r0"], lig[an]["r1"]
        groupes = []
        for rr in range(r0, r1 + 1):
            g = wb["Erreurs"].cell(rr, 2).value
            if g not in groupes:
                groupes.append(g)
        first = r
        for g in groupes:
            ws.cell(r, 1, f"31/03/{an}")
            ws.cell(r, 2, g)
            ws.cell(r, 3, f'=ROUND(SUMIFS(Erreurs!$I${r0}:$I${r1},Erreurs!$B${r0}:$B${r1},B{r}),2)').number_format = EUR
            ws.cell(r, 4, f'=ROUND(SUMIFS(Erreurs!$J${r0}:$J${r1},Erreurs!$B${r0}:$B${r1},B{r}),2)').number_format = EUR
            res[(an, g)] = r
            r += 1
        ws.cell(first, 5, f"=Erreurs!I{lig[an]['Net, bas'][1]}").number_format = EUR
        ws.cell(first, 6, f"=Erreurs!J{lig[an]['Net, haut'][1]}").number_format = EUR
        res[(an, "net")] = first
        r += 1
    r += 1
    ws.cell(r, 1, "Rapport au stock inventorié").font = B
    r += 1
    hdr2 = ["Clôture", "Stock inventorié total (page 1, imprimé)", "Net bas / stock (formule)", "Net haut / stock (formule)", "Brut / stock (formule)", "Prix non mis à jour : minoration (formule)"]
    for i, h in enumerate(hdr2, 1):
        c = ws.cell(r, i, h)
        c.font = B
        c.fill = GRIS
        c.alignment = WRAP
    r += 1
    for an in ("2023", "2024", "2025"):
        n = res[(an, "net")]
        ws.cell(r, 1, f"31/03/{an}")
        ws.cell(r, 2, STOCK_TOTAL[an]).number_format = EUR
        ws.cell(r, 3, f"=E{n}/B{r}").number_format = PCT
        ws.cell(r, 4, f"=F{n}/B{r}").number_format = PCT
        ws.cell(r, 5, f"=Erreurs!G{lig[an]['brut']}/B{r}").number_format = PCT
        if an in tot_prix:
            ws.cell(r, 6, f"=Prix_non_mis_a_jour!J{tot_prix[an]}").number_format = EUR
        res[(an, "ratio")] = r
        r += 1
    for col, w in zip("ABCDEF", (12, 44, 18, 18, 20, 18)):
        ws.column_dimensions[col].width = w
    return res


METHODE = [
    "Annexe n° 154 : erreurs d'addition et de valorisation relevées sur les états d'inventaire d'origine des trois clôtures (31/03/2023, 31/03/2024, 31/03/2025).",
    "",
    "OBJET. Re-sommer ligne à ligne les états d'origine, boissons et denrées, et chiffrer chaque erreur d'addition ou de valorisation, avec son sens et son montant.",
    "",
    "SOURCES. Annexe n° 63 : Inventaire_Demi_Lune_2023-03-31.pdf (17 pages). Annexe n° 64 : Inventaire_Demi_Lune_2024-03-31.pdf (15 pages). Annexe n° 65 : Inventaire_Demi_Lune_2025-03-31.pdf (13 pages). Chaque valeur est relue sur l'image de la page, à 300 dpi. La transcription jointe au mémoire du 10 juillet 2026 n'est pas utilisée. Prix fournisseur : factures de Franche-Comté Boissons Service.",
    "",
    "Convention : sens = valeur portée sur l'état moins valeur correcte. Un montant positif signifie un stock surévalué.",
    "Les lectures incertaines sont données en deux variantes ; aucune n'est retenue à la place de l'autre.",
    "L'écart de 165,88 € de la feuille d'entretien du 31 mars 2023 est un fait ; sa qualification n'est pas établie : surévaluation de 165,88 € si le pied n'intègre pas la ligne « 8 Gels Fondue », effet nul s'il l'intègre.",
    "La sous-évaluation de 113,96 € du fût Affligem du 31 mars 2023 suppose un comptage postérieur au 23 mars 2023.",
    "Cette pièce porte sur l'arithmétique et la valorisation des lignes ; elle ne dit rien de la date matérielle des comptages ni de la reprise des pages datées au bilan.",
    "",
    "ONGLETS.",
    "Synthese : le tableau 4 bis (erreurs par clôture et par groupe, effet net, bas et haut), puis le rapport au stock inventorié et la minoration due aux prix non mis à jour.",
    "Lignes_2023, Lignes_2024, Lignes_2025 : transcription de toutes les lignes, colonnes quantité, prix, valeur portée ; produit quantité × prix et écart en formules ; sous chaque feuille, somme des lignes (formule), pied porté (lu) et écart (formule).",
    "Pieds : une ligne par pied de feuille, somme des lignes et écart en formules.",
    "Erreurs : une ligne par erreur, valeur portée et valeur correcte renvoyant aux onglets Lignes ; sens, variante, montants bas et haut, nets et brut par clôture en formules.",
    "Prix_non_mis_a_jour : lignes dont le prix d'inventaire est antérieur au dernier prix facturé avant la clôture ; écart en formule.",
    "Sources : pages de chaque PDF et leur contenu.",
    "",
    "LIMITES. Les montants « bas » et « haut » combinent les variantes de lecture ; le brut est la somme des valeurs absolues dans la lecture la plus défavorable. Les pages imprimées sans comptage (listing fournisseur du 31/03/2023, p. 13 à 17) sont transcrites pour mémoire, sans valeur. La page 6 de l'état du 31/03/2025 est un second scan de la page 7 ; elle n'est pas additionnée.",
]


def onglet_methode(wb):
    ws = wb.active
    ws.title = "Methode"
    for i, t in enumerate(METHODE, 1):
        c = ws.cell(i, 1, t)
        c.alignment = WRAP
        if i == 1:
            c.font = H
    ws.column_dimensions["A"].width = 130


def onglet_sources(wb):
    ws = wb.create_sheet("Sources")
    ws["A1"] = "Sources : pages des états d'origine et leur contenu"
    ws["A1"].font = H
    for i, h in enumerate(["Clôture", "Annexe", "Page du PDF", "Contenu"], 1):
        c = ws.cell(3, i, h)
        c.font = B
        c.fill = GRIS
    r = 4
    for an in ("2023", "2024", "2025"):
        data = lire(an)
        pages = {}
        for x in data:
            pages.setdefault(int(x["page"]), [])
            if x["feuille"] not in pages[int(x["page"])]:
                pages[int(x["page"])].append(x["feuille"])
        infos = {}
        for x in data:
            if x["type"] == "INFO":
                infos.setdefault(int(x["page"]), []).append(x["libelle"])
        for p in sorted(pages):
            ws.cell(r, 1, f"31/03/{an}")
            ws.cell(r, 2, ANNEXE[an])
            ws.cell(r, 3, p)
            ws.cell(r, 4, " ; ".join(pages[p]) + ((" : " + " ; ".join(infos[p])) if p in infos else ""))
            ws.cell(r, 4).alignment = WRAP
            r += 1
        r += 1
    for col, w in zip("ABCD", (11, 8, 10, 140)):
        ws.column_dimensions[col].width = w


def textes_explicites(wb):
    """Les cellules de texte qui commencent par « = » restent du texte (pas des formules)."""
    for ws in wb:
        if ws.title.startswith("Lignes_") or ws.title == "Sources":
            for row in ws.iter_rows():
                for c in row:
                    if c.column in (2, 3, 4, 9, 10) and isinstance(c.value, str) and c.value.startswith("=") and c.column != 6:
                        if ws.title.startswith("Lignes_") and c.column in (6, 7, 8):
                            continue
                        c.value = "soit " + c.value[1:].lstrip()


def construire():
    wb = openpyxl.Workbook()
    onglet_methode(wb)
    L = {}
    for an in ("2023", "2024", "2025"):
        L[an] = Lignes(wb, an)
        L[an].construire()
    onglet_pieds(wb, L)
    E = erreurs(L)
    _, lig = onglet_erreurs(wb, E)
    tot = onglet_prix(wb)
    res = onglet_synthese(wb, lig, tot)
    onglet_sources(wb)
    textes_explicites(wb)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT)
    return L, lig, res, tot


def recalculer():
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["soffice", "--headless", "--calc", "--convert-to", "xlsx", "--outdir", tmp, str(OUT)], check=True, capture_output=True)
        shutil.move(str(Path(tmp) / OUT.name), str(OUT))


if __name__ == "__main__":
    L, lig, res, tot = construire()
    recalculer()
    wb = openpyxl.load_workbook(OUT, data_only=True)
    e, s, p = wb["Erreurs"], wb["Synthese"], wb["Prix_non_mis_a_jour"]
    for an in ("2023", "2024", "2025"):
        print(f"\n{an} : lignes transcrites par feuille")
        for f, n in L[an].nb.items():
            print(f"   {n:4d}  {f}")
        for rr in range(lig[an]["r0"], lig[an]["r1"] + 1):
            print(f"   {e.cell(rr,3).value[:45]:45s} sens {e.cell(rr,7).value!s:>9}  var {e.cell(rr,8).value!s:>8}  bas {e.cell(rr,9).value!s:>8} haut {e.cell(rr,10).value!s:>8}")
        print("   net principal", e.cell(lig[an]["Net (lecture principale)"][1], 7).value,
              "net bas", e.cell(lig[an]["Net, bas"][1], 9).value, "net haut", e.cell(lig[an]["Net, haut"][1], 10).value,
              "brut", e.cell(lig[an]["brut"], 7).value)
        rr = res[(an, "ratio")]
        print("   ratios bas/haut/brut :", s.cell(rr, 3).value, s.cell(rr, 4).value, s.cell(rr, 5).value, " prix :", s.cell(rr, 6).value)
        for (a2, g), r2 in res.items():
            if a2 == an and g not in ("net", "ratio"):
                print(f"   groupe {g:20s} bas {s.cell(r2,3).value} haut {s.cell(r2,4).value}")
    print("\nPrix non mis à jour :", {an: (p.cell(r, 3).value, p.cell(r, 10).value) for an, r in tot.items()})
    # erreurs de formule
    nerr = 0
    for ws in wb:
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value.startswith(("#", "Err:")):
                    nerr += 1
                    print("ERREUR", ws.title, c.coordinate, c.value)
    print("cellules en erreur :", nerr)
