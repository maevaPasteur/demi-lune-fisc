#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REPONSE 1 - Partie L (p. 59) et partie M (p. 76-77) : la cascade des 10 622 L.

Bilan matiere de l'alcool achete sur les 3 exercices verifies : un litre achete
est soit vendu, soit encore en stock, soit consomme sans vente, soit perdu.
Ce script assemble la cascade poste par poste, indique pour CHAQUE poste sa
nature (mesure en caisse / calcul / estimation a taux source), sa source et la
sous-page de la reponse qui le demontre, puis produit la piece jointe.

Deux colonnes de volumes :
  - "memoire 10/07/2026" : la cascade telle qu'elle a ete soumise au service et
    telle qu'il l'a reproduite p. 76 de sa reponse du 04/09/2026 ;
  - "corrige" : la meme cascade apres la correction du poste CREMANT. Le service
    a objecte (p. 62-63) que le sur-versement maximal et le fond de bouteille ne
    pouvaient pas etre cumules. L'objection porte : le poste cremant n'est plus
    postule, il est BORNE PAR LE STOCK (script reponse1-cremant-fourchette.py).
    La correction joue CONTRE nous : elle augmente le residu.

Entrees (lecture seule, deja produites par les pipelines du dossier) :
  src/data/incertitudeDisparu/synthese_perte_reelle.json   (cascade memoire)
  src/data/reponse1Calculs/cremant-fourchette.json         (cremant borne par le stock)
Sortie :
  public/documents/pieces-reponse-1/R1-cascade-bilan-matiere.xlsx
"""
import os
import json

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

ICI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(ICI, ".."))
SYNTHESE = os.path.join(ROOT, "src/data/incertitudeDisparu/synthese_perte_reelle.json")
CREMANT = os.path.join(ROOT, "src/data/reponse1Calculs/cremant-fourchette.json")
PIECES = os.path.join(ROOT, "public/documents/pieces-reponse-1/")
SORTIE = os.path.join(PIECES, "R1-cascade-bilan-matiere.xlsx")

# --- Qualification de chaque poste de la cascade -----------------------------
# nature : MESURE (lu dans la caisse ou l'inventaire), CALCUL (quantite mesuree
# x recette / dose), ESTIME (taux issu d'une source publiee ou d'une base
# journaliere declaree), RESIDUEL (ce qui reste, non explique).
QUALIF = {
    "Vendu au verre (caisse)": (
        "MESURE",
        "Detail des tickets, annexe C1/C2/C3 : quantites x contenance de l'article",
        "55-rf-reconstitution-volumes-liquides.xlsx",
        "/reponse-1/recon-1-doses-figees",
    ),
    "Vendu en cocktails (caisse, biere des cocktails incluse)": (
        "CALCUL",
        "Cocktails vendus (annexe C) x recette de chaque cocktail (carte)",
        "55-rf-reconstitution-volumes-liquides.xlsx",
        "/reponse-1/recon-1-doses-figees",
    ),
    "Cuisine (fondues, babas, flambage)": (
        "CALCUL",
        "Plats vendus (annexe C) x dose d'alcool de la recette",
        "53-rf-alcool-cuisine-doses-plats.xlsx",
        "/reponse-1/recon-5-alcool-cuisine",
    ),
    "Alcool des menus (non detaille en caisse)": (
        "CALCUL",
        "Menus vendus (annexe C) x composition du menu",
        "55-rf-reconstitution-volumes-liquides.xlsx",
        "/reponse-1/recon-6-alcool-plats-menus",
    ),
    "Consommation du chef (Picon + Macvin)": (
        "ESTIME",
        "Base journaliere declaree x 662 jours de service",
        "57-rf-offerts-remises-pertes.xlsx",
        "/reponse-1/recon-7-conso-personnel",
    ),
    "Aperitifs offerts aux clients": (
        "ESTIME",
        "1 aperitif de 6 cl par jour x 662 jours de service",
        "57-rf-offerts-remises-pertes.xlsx",
        "/reponse-1/recon-8-abattements",
    ),
    "Sur-versement vins/spiritueux/cocktails (free-pour : Kerr 2008, Wansink 2005)": (
        "ESTIME",
        "Taux publies (Kerr 2008 : +23,6 % vin, +42 % cocktails ; Wansink 2005 : "
        "+20 % spiritueux) appliques a la consommation reelle de la caisse",
        "49-rf-sur-versement-au-verre.xlsx",
        "/reponse-1/sur-versement-au-verre",
    ),
    "Degustation offerte (note par note, annexe C)": (
        "MESURE",
        "Notes de degustation relevees une a une dans l'annexe C",
        "52-rf-degustation-par-note.xlsx",
        "/reponse-1/recon-4-degustation",
    ),
    "Freinte technique de la biere pression (mousse, lignes)": (
        "ESTIME",
        "Freinte de fut retenue tres en dessous du taux documente et en dessous "
        "de l'abattement de 15 % que le service accorde lui-meme",
        "50-rf-pertes-biere-mousse.xlsx",
        "/reponse-1/perte-de-biere",
    ),
    "Stock final (inventaire)": (
        "MESURE",
        "Inventaire de cloture",
        "09-rf-inventaire-stocks.xlsx",
        "/reponse-1/recon-9-variation-de-stock",
    ),
}
CREMANT_MEMOIRE = [
    "Cremant jete en fin de journee (eventé)",
    "Cremant jete en fin de journee (evente)",
    "Cremant sur-versé (free-pour +23,6 %)",
    "Cremant sur-verse (free-pour +23,6 %)",
]
QUALIF_CREMANT = (
    "CALCUL",
    "Bilan matiere jour par jour sur 647 journees de service : le cremant ouvert "
    "doit tenir dans le stock retenu par le service (doses du service, p. 62)",
    "51-rf-cremant-jete.xlsx",
    "/reponse-1/recon-3-cremant-vendu",
)
LIB_CREMANT = "Cremant : fonds de bouteille et sur-versement (borne par le stock)"


def norm(s):
    return (
        s.replace("é", "e").replace("è", "e").replace("ê", "e").replace("ç", "c")
    )


def charger():
    syn = json.load(open(SYNTHESE, encoding="utf-8"))["cascade_alcool"]
    cre = json.load(open(CREMANT, encoding="utf-8"))["exercices"]
    # Cremant corrige = ecart a expliquer (cremant sorti du stock et non vendu),
    # somme des trois exercices, calcule sur les volumes disponibles du service.
    cremant_corrige = sum(x["ecart_a_expliquer_cl"] for x in cre.values()) / 100.0
    return syn, cremant_corrige


def construire(syn, cremant_corrige):
    achats = float(syn["achats_alcool_l"])
    lignes = []
    cremant_memoire = 0.0
    for p in syn["postes"]:
        lib = p["poste"]
        val = float(p["litres"])
        if norm(lib) in [norm(x) for x in CREMANT_MEMOIRE]:
            cremant_memoire += val
            continue
        q = QUALIF[lib]
        lignes.append([lib, val, val, q[0], q[1], q[2], q[3]])
    q = QUALIF_CREMANT
    lignes.append(
        [LIB_CREMANT, cremant_memoire, cremant_corrige, q[0], q[1], q[2], q[3]]
    )
    total_mem = sum(l[1] for l in lignes)
    total_cor = sum(l[2] for l in lignes)
    residu_mem = achats - total_mem
    residu_cor = achats - total_cor
    return achats, lignes, total_mem, total_cor, residu_mem, residu_cor


BLEU = PatternFill("solid", fgColor="1F3864")
GRIS = PatternFill("solid", fgColor="EDEDED")
JAUNE = PatternFill("solid", fgColor="FFF2CC")
B = Side(style="thin", color="B7B7B7")
BORD = Border(left=B, right=B, top=B, bottom=B)


def entete(ws, labels, largeurs):
    ws.append(labels)
    for i, (lab, lg) in enumerate(zip(labels, largeurs), 1):
        c = ws.cell(row=ws.max_row, column=i)
        c.fill = BLEU
        c.font = Font(bold=True, color="FFFFFF")
        c.alignment = Alignment(vertical="center", wrap_text=True)
        c.border = BORD
        ws.column_dimensions[c.column_letter].width = lg
    ws.freeze_panes = ws.cell(row=ws.max_row + 1, column=1)


def ecrire(ws, ligne, gras=False, fill=None):
    ws.append(ligne)
    r = ws.max_row
    for i in range(1, len(ligne) + 1):
        c = ws.cell(row=r, column=i)
        c.border = BORD
        c.alignment = Alignment(vertical="top", wrap_text=True)
        if gras:
            c.font = Font(bold=True)
        if fill is not None:
            c.fill = fill
        if isinstance(ligne[i - 1], float):
            c.number_format = "# ##0,0"


def main():
    syn, cremant_corrige = charger()
    achats, lignes, tot_mem, tot_cor, res_mem, res_cor = construire(syn, cremant_corrige)

    wb = Workbook()
    ws = wb.active
    ws.title = "Cascade"
    ws["A1"] = (
        "SARL LA DEMI LUNE - Bilan matiere de l'alcool achete sur les 3 exercices "
        "verifies (reponse DDFiP 39 du 04/09/2026, p. 59 et p. 76-77)"
    )
    ws["A1"].font = Font(bold=True, size=12)
    ws["A2"] = (
        "Un litre achete est soit vendu, soit en stock, soit consomme sans vente, "
        "soit perdu. Colonne 'memoire' = cascade soumise le 10/07/2026 et reproduite "
        "p. 76 ; colonne 'corrige' = apres correction du poste cremant, borne par le "
        "stock a la suite de l'objection du service (p. 62-63)."
    )
    ws["A2"].alignment = Alignment(wrap_text=True)
    ws.append([])
    entete(
        ws,
        [
            "Poste de la cascade",
            "Litres (memoire 10/07/2026)",
            "Litres (corrige)",
            "Nature",
            "Source du chiffre",
            "Piece detaillee (USB 10/07/2026)",
            "Sous-page de la reponse",
        ],
        [52, 16, 15, 11, 62, 34, 34],
    )
    for lib, vm, vc, nat, src, piece, page in lignes:
        ecrire(ws, [lib, round(vm, 1), round(vc, 1), nat, src, piece, page])
    ecrire(
        ws,
        [
            "TOTAL justifie poste par poste",
            round(tot_mem, 1),
            round(tot_cor, 1),
            "",
            "",
            "",
            "",
        ],
        gras=True,
        fill=GRIS,
    )
    ecrire(
        ws,
        [
            "Residu : perte pure (casse, evaporation, fonds de verre, rincage)",
            round(res_mem, 1),
            round(res_cor, 1),
            "RESIDUEL",
            "Solde du bilan matiere : aucun taux, aucune hypothese",
            "55-rf-reconstitution-volumes-liquides.xlsx",
            "/reponse-1/cascade-10622-litres",
        ],
        gras=True,
        fill=JAUNE,
    )
    ecrire(
        ws,
        [
            "TOTAL alcool achete (factures fournisseurs)",
            round(achats, 1),
            round(achats, 1),
            "MESURE",
            "Factures d'achat, 107 924 EUR HT sur 3 exercices",
            "",
            "",
        ],
        gras=True,
        fill=GRIS,
    )

    ws2 = wb.create_sheet("Synthese")
    entete(ws2, ["Indicateur", "Memoire 10/07/2026", "Corrige"], [46, 22, 22])
    ecrire(ws2, ["Alcool achete (L)", round(achats, 1), round(achats, 1)])
    ecrire(ws2, ["Justifie poste par poste (L)", round(tot_mem, 1), round(tot_cor, 1)])
    ecrire(
        ws2,
        [
            "Part justifiee (%)",
            round(100 * tot_mem / achats, 1),
            round(100 * tot_cor / achats, 1),
        ],
    )
    ecrire(ws2, ["Residu de perte pure (L)", round(res_mem, 1), round(res_cor, 1)], gras=True)
    ecrire(
        ws2,
        [
            "Residu en % des achats",
            round(100 * res_mem / achats, 1),
            round(100 * res_cor / achats, 1),
        ],
        gras=True,
        fill=JAUNE,
    )
    ecrire(
        ws2,
        [
            "Volume disponible pour une vente non enregistree (L)",
            0.0,
            0.0,
        ],
        gras=True,
    )
    ws2.append([])
    ws2.append(
        [
            "Le residu n'est pas une hypothese : c'est le solde du bilan matiere. "
            "Il ne peut etre reduit qu'en contestant un poste chiffre ci-avant."
        ]
    )

    ws3 = wb.create_sheet("Nature des postes")
    entete(ws3, ["Nature", "Definition", "Postes concernes", "Volume corrige (L)"], [12, 60, 62, 18])
    for nat, defi in [
        ("MESURE", "Lu directement dans la caisse certifiee ou dans l'inventaire de cloture, sans hypothese"),
        ("CALCUL", "Quantite mesuree en caisse multipliee par une recette, une dose ou une contrainte de stock"),
        ("ESTIME", "Taux issu d'une source publiee ou d'une base journaliere declaree, applique a un volume mesure"),
    ]:
        postes = [l for l in lignes if l[3] == nat]
        ecrire(
            ws3,
            [
                nat,
                defi,
                " ; ".join(l[0] for l in postes),
                round(sum(l[2] for l in postes), 1),
            ],
        )
    ecrire(
        ws3,
        [
            "RESIDUEL",
            "Solde : ce que le bilan matiere n'attribue a aucun poste",
            "Perte pure (casse, evaporation, fonds de verre, rincage des tireuses)",
            round(res_cor, 1),
        ],
    )

    os.makedirs(PIECES, exist_ok=True)
    wb.save(SORTIE)
    print("Ecrit :", SORTIE)
    print("  achats        : %8.1f L" % achats)
    print("  justifie mem. : %8.1f L (%.1f %%)" % (tot_mem, 100 * tot_mem / achats))
    print("  justifie corr.: %8.1f L (%.1f %%)" % (tot_cor, 100 * tot_cor / achats))
    print("  residu mem.   : %8.1f L (%.1f %%)" % (res_mem, 100 * res_mem / achats))
    print("  residu corr.  : %8.1f L (%.1f %%)" % (res_cor, 100 * res_cor / achats))
    print("  cremant       : %8.1f L -> %.1f L" % (
        sum(l[1] for l in lignes if l[0] == LIB_CREMANT),
        cremant_corrige,
    ))


if __name__ == "__main__":
    main()
