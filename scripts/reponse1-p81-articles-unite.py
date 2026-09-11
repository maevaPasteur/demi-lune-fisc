#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REPONSE 1 - Audit arithmetique du tableau des ARTICLES VENDUS A L'UNITE
que le service produit en page 81 de sa reponse du 04/09/2026.

Le service conclut de ce tableau que « pour ces articles, le sur-dosage ne peut
expliquer de tel taux d'ecart ». Ce script reprend le tableau ligne a ligne,
recalcule le taux (disponible - vendues) / disponible et le compare au taux
imprime, puis classe les lignes que la methode elle-meme rend impossibles :
  - taux de disparition NEGATIF (plus vendu que disponible) ;
  - taux de 100,00 % alors qu'AUCUNE vente n'est enregistree de l'exercice ;
  - taux imprime sur une ligne ou le disponible ET les ventes sont nuls.

SOURCE DES CHIFFRES : la page 81 elle-meme, relevee sur l'image du courrier
(la lecture visuelle fait foi, l'OCR est fautif). Les cellules qui n'ont pas pu
etre lues avec certitude sont marquees None et EXCLUES de tout total.

DEUX BLOCS SONT GROUPES dans le tableau du service (cellules fusionnees) : le
bloc Granini et le bloc Champagne, ou la colonne « quantites vendues » porte le
total du groupe et non celui de la ligne. Le script le verifie : rapportes au
total du groupe, les taux imprimes de ces deux blocs tombent juste. Ils ne sont
donc PAS comptes comme des anomalies.

Sorties :
  public/documents/pieces-reponse-1/R1-p81-articles-unite.xlsx
"""
import os

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
PIECES = os.path.join(ROOT, "public/documents/pieces-reponse-1")
EXOS = ["31/03/2023", "31/03/2024", "31/03/2025"]

# designation, groupe, [(dispo, vendues, taux imprime) x 3 exercices]
# None = cellule illisible avec certitude sur le document recu.
T = [
    ("Vittel Evian / Vittel / Velleminfroy 100 cl", None,
     [(49, 34, 30.61), (48, 38, 20.83), (73, 33, 54.79)]),
    ("Vittel Evian 50 cl", None,
     [(50, 21, 58.00), (15, 22, -46.67), (51, 19, 62.75)]),
    ("San Pellegrino 100 cl", None,
     [(249, 177, 28.92), (224, 160, 28.57), (193, 158, 18.13)]),
    ("San Pellegrino 50 cl", None,
     [(198, 136, 31.31), (155, 116, 25.16), (150, 118, 21.33)]),
    ("Carola Bleue 50 cl", None,
     [(20, 0, 100.00), (20, 0, 100.00), (0, 0, 0.00)]),
    ("Perrier 33 cl", None,
     [(448, 144, 67.86), (415, 126, 69.64), (429, 129, 69.93)]),
    ("Coca Cola 33 cl", None,
     [(2688, 453, 83.15), (1464, 399, 72.75), (1750, 403, 76.97)]),
    ("Orangina 33 cl", None,
     [(277, 81, 70.76), (127, 71, 44.09), (148, 73, 50.68)]),
    ("Fanta 33 cl", None,
     [(137, 53, 61.31), (69, 36, 47.83), (129, 40, 68.99)]),
    ("Fuzetea 33 cl", None,
     [(622, 195, 68.65), (443, 204, 53.95), (270, 198, 26.67)]),
    ("Schweppes Agrume 33 cl", None,
     [(158, 78, 50.63), (102, 72, 29.41), (118, 71, 39.83)]),
    ("Granini Fraise 25 cl", "Granini",
     [(161, None, None), (260, None, None), (307, None, None)]),
    ("Granini Framboise 25 cl", "Granini",
     [(154, None, None), (37, None, None), (0, None, None)]),
    ("Granini Raisin 25 cl", "Granini",
     [(124, 417, 20.57), (31, 360, 11.33), (0, 342, 17.39)]),
    ("Granini Tomate 25 cl", "Granini",
     [(86, None, None), (78, None, None), (107, None, None)]),
    ("Sprite 33 cl", None,
     [(0, None, 0.00), (24, 0, 100.00), (24, 0, 100.00)]),
    ("Tropico 50 cl", None,
     [(0, None, 0.00), (156, 0, 100.00), (32, 0, 100.00)]),
    ("La Rouget Ambree 33 cl", None,
     [(200, 131, 34.50), (182, 126, 30.77), (187, 130, 30.48)]),
    ("Des Neiges Abbaye / La Rouget Blanche 33 cl", None,
     [(168, 157, 6.55), (166, 123, 25.90), (226, 134, 40.71)]),
    ("1664 33 cl", None,
     [(234, 0, 100.00), (120, 0, 100.00), (36, 0, 100.00)]),
    ("Bleue Du Mont Blanc 33 cl", None,
     [(0, 0, 100.00), (0, 0, 0.00), (168, 0, 100.00)]),
    ("Grimbergen Blanche 33 cl", None,
     [(24, 0, 100.00), (0, 0, 0.00), (0, 0, 0.00)]),
    ("Hefeweizen 33 cl", None,
     [(48, 0, 100.00), (0, 0, 0.00), (0, 0, 0.00)]),
    ("White Rabbit 33 cl", None,
     [(24, 0, 100.00), (0, 0, 0.00), (0, 0, 0.00)]),
    ("White Mort Subite 33 cl", None,
     [(108, 0, 100.00), (12, 0, 100.00), (144, 0, 100.00)]),
    ("Heineken 50 cl", None,
     [(0, 0, 100.00), (24, 0, 100.00), (0, 0, 0.00)]),
    ("Heineken 33 cl", None,
     [(24, 0, 100.00), (0, 0, 0.00), (0, 0, 0.00)]),
    ("Cidre La Mordue 27 cl", None,
     [(214, 70, 67.29), (355, 130, 63.38), (289, 143, 50.52)]),
    ("Cidre Sassy 33 cl", None,
     [(12, 65, 100.00), (0, 0, 0.00), (None, 0, 100.00)]),
    ("Cidre Brut 75 cl", None,
     [(80, 55, 18.75), (60, 53, 11.67), (41, 49, -19.51)]),
    ("Cidre Doux 75 cl", None,
     [(80, 1, 31.88), (58, 48, 17.24), (52, 41, 21.15)]),
    ("Cremant Rose", None,
     [(0, None, 0.00), (0, 0, 0.00), (0, 0, 0.00)]),
    ("Champagne Bollinger 75 cl", "Champagne",
     [(3, None, 70.00), (0, None, None), (0, None, None)]),
    ("Champagne Ruinart 75 cl", "Champagne",
     [(8, None, None), (8, None, None), (12, None, None)]),
    ("Champagne Lancon 75 cl", "Champagne",
     [(0, 9, None), (4, 7, 46.15), (8, 2, 90.00)]),
    ("Champagne Sandrin 75 cl", "Champagne",
     [(19, None, None), (1, None, None), (None, None, None)]),
]

# Totaux de groupe imprimes par le service sous chaque bloc a cellules fusionnees.
TOTAUX_GROUPE = {"Granini": [525, 406, 414], "Champagne": [30, 13, 20]}


def controle_groupes():
    """Verifie que les taux imprimes des blocs fusionnes tombent juste quand on
    les rapporte au TOTAL du groupe : ils ne sont donc pas des anomalies."""
    res = []
    for nom, totaux in TOTAUX_GROUPE.items():
        for ligne in T:
            if ligne[1] != nom:
                continue
            for i, (d, v, tx) in enumerate(ligne[2]):
                if v is None or tx is None or not totaux[i]:
                    continue
                calc = (totaux[i] - v) / totaux[i] * 100
                res.append({"groupe": nom, "ligne": ligne[0], "exercice": EXOS[i],
                            "total_groupe": totaux[i], "vendues_groupe": v,
                            "taux_imprime": tx, "taux_recalcule_sur_le_groupe": round(calc, 2),
                            "concordant": abs(calc - tx) < 0.05})
    return res


def audit():
    lignes, anomalies = [], []
    for nom, groupe, cellules in T:
        for i, (d, v, tx) in enumerate(cellules):
            calc = None if (d in (None, 0) or v is None) else (d - v) / d * 100
            nature = ""
            if groupe in ("Granini", "Champagne"):
                nature = "cellule fusionnee (total du groupe) : hors audit"
            elif groupe == "lecture incertaine":
                nature = "lecture incertaine : hors audit"
            elif d is not None and v is not None and d > 0 and v > d:
                nature = ("taux negatif imprime : plus vendu que disponible"
                          if (tx is not None and tx < 0)
                          else "plus vendu que disponible, et pourtant un taux positif imprime")
            elif d is not None and v is not None and d > 0 and v == 0 and tx == 100.0:
                nature = "100,00 % sans aucune vente de l'exercice"
            elif d == 0 and v == 0 and tx not in (None, 0.0):
                nature = "taux imprime sur un disponible et des ventes nuls"
            elif calc is not None and tx is not None and abs(calc - tx) > 0.05:
                nature = "taux imprime different du taux recalcule"
            lignes.append({"designation": nom, "groupe": groupe or "", "exercice": EXOS[i],
                           "disponibles": d, "vendues": v, "taux_imprime": tx,
                           "taux_recalcule": None if calc is None else round(calc, 2),
                           "nature": nature})
            if nature and "hors audit" not in nature:
                anomalies.append(lignes[-1])
    return lignes, anomalies


def totaux(lignes):
    """Unites declarees disparues, hors blocs fusionnes et lectures incertaines,
    et part provenant des lignes sans aucune vente."""
    tot = {e: 0 for e in EXOS}
    zero = {e: 0 for e in EXOS}
    for l in lignes:
        if l["groupe"] in ("Granini", "Champagne", "lecture incertaine"):
            continue
        d, v = l["disponibles"], l["vendues"]
        if d is None or v is None:
            continue
        if d - v > 0:
            tot[l["exercice"]] += d - v
            if v == 0:
                zero[l["exercice"]] += d - v
    return tot, zero


def fr(x, dec=2):
    return f"{x:,.{dec}f}".replace(",", " ").replace(".", ",")


def ecrire(lignes, anomalies, groupes, tot, zero):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    blanc = Font(bold=True, color="FFFFFF")
    tete = PatternFill("solid", fgColor="0F766E")
    alerte = PatternFill("solid", fgColor="FBD5D5")
    neutre = PatternFill("solid", fgColor="EEF2F6")
    trait = Side(style="thin", color="D8DEE4")
    bord = Border(left=trait, right=trait, top=trait, bottom=trait)

    def entetes(ws, cols, ligne):
        ws.append(cols)
        for c in range(1, len(cols) + 1):
            cell = ws.cell(row=ligne, column=c)
            cell.font, cell.fill, cell.border = blanc, tete, bord
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    def largeurs(ws, w):
        for i, x in enumerate(w, 1):
            ws.column_dimensions[get_column_letter(i)].width = x

    def borde(ws):
        r = ws.max_row
        for c in range(1, ws.max_column + 1):
            ws.cell(row=r, column=c).border = bord
        return r

    ws = wb.active
    ws.title = "Tableau p.81 recalcule"
    ws.append(["Tableau des articles vendus a l'unite, page 81 de la reponse du 04/09/2026, "
               "recalcule ligne a ligne"])
    ws["A1"].font = Font(bold=True, size=13)
    ws.append(["Taux recalcule = (quantites disponibles - quantites vendues) / quantites "
               "disponibles. Les cellules non lisibles avec certitude sur le document recu "
               "sont laissees vides et exclues de tout total. Les blocs Granini et Champagne "
               "comportent des cellules fusionnees : la colonne des ventes y porte le total du "
               "groupe, ce que la feuille 3 verifie."])
    ws["A2"].font = Font(italic=True, size=9, color="64748B")
    ws.append([])
    cols = ["Designation", "Bloc", "Exercice clos le", "Quantites disponibles",
            "Quantites vendues", "Taux imprime par le service", "Taux recalcule",
            "Ce que la ligne produit"]
    entetes(ws, cols, 4)
    for l in lignes:
        ws.append([l["designation"], l["groupe"], l["exercice"], l["disponibles"], l["vendues"],
                   None if l["taux_imprime"] is None else f"{fr(l['taux_imprime'])} %",
                   None if l["taux_recalcule"] is None else f"{fr(l['taux_recalcule'])} %",
                   l["nature"]])
        r = borde(ws)
        if l["nature"] and "hors audit" not in l["nature"]:
            for c in range(1, len(cols) + 1):
                ws.cell(row=r, column=c).fill = alerte
        elif l["nature"]:
            for c in range(1, len(cols) + 1):
                ws.cell(row=r, column=c).fill = neutre
    largeurs(ws, [42, 20, 18, 20, 18, 22, 18, 46])
    ws.freeze_panes = "D5"

    ws2 = wb.create_sheet("Lignes impossibles")
    ws2.append(["Les lignes que la methode du service rend impossibles"])
    ws2["A1"].font = Font(bold=True, size=13)
    ws2.append(["Aucune de ces lignes ne peut correspondre a une disparition physique de "
                "marchandise : un taux negatif signifie qu'il a ete vendu plus que ce qui "
                "etait disponible, et un taux de 100,00 % sans la moindre vente de l'exercice "
                "signale un article qui n'a jamais ete enregistre en caisse."])
    ws2["A2"].font = Font(italic=True, size=9, color="64748B")
    ws2.append([])
    entetes(ws2, cols, 4)
    for l in anomalies:
        ws2.append([l["designation"], l["groupe"], l["exercice"], l["disponibles"], l["vendues"],
                    None if l["taux_imprime"] is None else f"{fr(l['taux_imprime'])} %",
                    None if l["taux_recalcule"] is None else f"{fr(l['taux_recalcule'])} %",
                    l["nature"]])
        borde(ws2)
    ws2.append([])
    ws2.append([f"{len(anomalies)} couples (article, exercice) en anomalie."])
    ws2.cell(row=ws2.max_row, column=1).font = Font(bold=True)
    ws2.append([])
    ws2.append(["Unites que le tableau declare disparues, hors blocs fusionnes et lectures "
                "incertaines :"])
    ws2.cell(row=ws2.max_row, column=1).font = Font(bold=True)
    for e in EXOS:
        part = 100 * zero[e] / tot[e] if tot[e] else 0
        ws2.append([f"Exercice clos le {e}", "", "", tot[e], zero[e],
                    f"{fr(part, 1)} %", "", "dont lignes sans aucune vente de l'exercice"])
        borde(ws2)
    st, sz = sum(tot.values()), sum(zero.values())
    ws2.append(["Total 3 exercices", "", "", st, sz, f"{fr(100 * sz / st, 1)} %", "",
                "dont lignes sans aucune vente de l'exercice"])
    r = borde(ws2)
    for c in range(1, len(cols) + 1):
        ws2.cell(row=r, column=c).font = Font(bold=True)
    largeurs(ws2, [42, 20, 18, 20, 18, 22, 18, 46])

    ws3 = wb.create_sheet("Blocs fusionnes")
    ws3.append(["Controle des deux blocs a cellules fusionnees : Granini et Champagne"])
    ws3["A1"].font = Font(bold=True, size=13)
    ws3.append(["Dans ces deux blocs, la colonne des quantites vendues porte le total du "
                "groupe. Rapportes a ce total, les taux imprimes tombent juste : ces lignes "
                "ne sont donc PAS des anomalies, et nous ne les invoquons pas."])
    ws3["A2"].font = Font(italic=True, size=9, color="64748B")
    ws3.append([])
    cols3 = ["Bloc", "Ligne portant la cellule fusionnee", "Exercice clos le",
             "Total du groupe", "Ventes du groupe", "Taux imprime",
             "Taux recalcule sur le total du groupe", "Concordant"]
    entetes(ws3, cols3, 4)
    for g in groupes:
        ws3.append([g["groupe"], g["ligne"], g["exercice"], g["total_groupe"],
                    g["vendues_groupe"], f"{fr(g['taux_imprime'])} %",
                    f"{fr(g['taux_recalcule_sur_le_groupe'])} %",
                    "oui" if g["concordant"] else "NON"])
        borde(ws3)
    largeurs(ws3, [16, 34, 18, 18, 20, 18, 32, 14])

    os.makedirs(PIECES, exist_ok=True)
    wb.save(os.path.join(PIECES, "R1-p81-articles-unite.xlsx"))


def main():
    lignes, anomalies = audit()
    groupes = controle_groupes()
    tot, zero = totaux(lignes)
    ecrire(lignes, anomalies, groupes, tot, zero)

    print("=== Controle des blocs fusionnes ===")
    for g in groupes:
        print(f"  {g['groupe']:10s} {g['exercice']}  imprime {g['taux_imprime']:7.2f} %  "
              f"recalcule sur le groupe {g['taux_recalcule_sur_le_groupe']:7.2f} %  "
              f"{'concordant' if g['concordant'] else 'NON CONCORDANT'}")
    print()
    print("=== Lignes impossibles ===")
    par_nature = {}
    for a in anomalies:
        par_nature.setdefault(a["nature"], []).append(a)
    for nature, lst in par_nature.items():
        u = sum(x["disponibles"] or 0 for x in lst)
        print(f"  {len(lst):2d} couples : {nature}  ({u} unites concernees)")
        for x in lst:
            print(f"       {x['designation'][:38]:38s} {x['exercice']}  "
                  f"dispo {x['disponibles']}  vendues {x['vendues']}  "
                  f"imprime {x['taux_imprime']} %")
    print()
    st, sz = sum(tot.values()), sum(zero.values())
    for e in EXOS:
        print(f"  exercice clos le {e} : {tot[e]} unites declarees disparues, "
              f"dont {zero[e]} sans aucune vente ({100 * zero[e] / tot[e]:.1f} %)")
    print(f"  TOTAL 3 exercices : {st} unites, dont {sz} sans aucune vente "
          f"({100 * sz / st:.1f} %)")


if __name__ == "__main__":
    main()
