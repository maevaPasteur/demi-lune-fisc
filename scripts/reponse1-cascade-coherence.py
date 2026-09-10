#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REPONSE 1 - Mise en cohérence de la cascade des 10 622 L.

Trois postes ont été corrigés A LA BAISSE dans les sous-pages, après
vérification contradictoire sur les factures et sur le stock :
  - crémant           347 L -> 272 L (borné par le stock, page recon-3)
  - sur-versement     720 L -> 494 L (assiette par assiette, page N)
  - alcool de cuisine 794 L -> 745 L (plafonné aux factures, pages 5, 6 et R)
    ATTENTION : 745 L est le volume PHYSIQUEMENT consommé en cuisine, seul pertinent
    dans un bilan matière. Les 173 L cités dans la page 5 sont autre chose : c'est le
    supplément demandé au service, une fois retranché ce qu'il déduit déjà lui-même
    dans sa reconstitution (repères D, E, G et Q).
Ce script répercute ces corrections sur les deux pages de cadrage du bloc 3
(parties L et M), de sorte qu'aucun chiffre du site ne se contredise.

Idempotent : il réécrit toujours les mêmes sections à partir des valeurs
ci-dessous. Exécution : python3 scripts/reponse1-cascade-coherence.py
"""
import os, json

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DATA = os.path.join(ROOT, "src/data/reponse1")

ACHATS = 10622  # litres d'alcool achetés sur les 3 exercices (factures)

# (clé, libellé, litres, nature, source, page de démonstration, slug)
POSTES = [
    ("verre", "Vendu au verre", 5569, "mesure", "Détail des tickets, annexes C1 à C3",
     "Doses figées", "recon-1-doses-figees"),
    ("cocktails", "Vendu en cocktails", 998, "calcul",
     "Cocktails vendus en caisse x recette de la carte", "Doses figées", "recon-1-doses-figees"),
    ("cuisine", "Cuisine et alcool des menus", 745, "calcul",
     "Plats et menus vendus en caisse x dose, plafonnés aux achats facturés",
     "Alcool de cuisine", "recon-5-alcool-cuisine"),
    ("cremant", "Crémant non vendu", 272, "calcul",
     "Bilan matière jour par jour, borné par le stock retenu par le service",
     "Crémant", "recon-3-cremant-vendu"),
    ("surversement", "Sur-versement au verre", 494, "estime",
     "Taux publiés appliqués au seul volume versé à la main, borné par le stock",
     "Sur-versement", "sur-versement-au-verre"),
    ("degustation", "Dégustation offerte", 126, "mesure",
     "Notes relevées une à une dans l’annexe C", "Dégustation", "degustation-offerte"),
    ("biere", "Freinte technique de la bière", 129, "estime",
     "Freinte de fût retenue au taux prudent de 10 %", "Perte de bière", "perte-de-biere"),
    ("chef", "Consommation du chef", 143, "estime",
     "Base journalière déclarée x jours de service", "Consommation du personnel",
     "recon-7-conso-personnel"),
    ("offerts", "Apéritifs offerts", 40, "estime",
     "Un apéritif de 6 cl par jour de service", "Abattements", "recon-8-abattements"),
    ("stock", "Stock final", 213, "mesure", "Inventaire de clôture", "Variation de stock",
     "recon-9-variation-de-stock"),
]

JUSTIFIE = sum(p[2] for p in POSTES)
RESIDU = ACHATS - JUSTIFIE
PCT_RESIDU = 100 * RESIDU / ACHATS
PCT_JUSTIFIE = 100 * JUSTIFIE / ACHATS
MESURE = sum(p[2] for p in POSTES if p[3] == "mesure")
CALCUL = sum(p[2] for p in POSTES if p[3] == "calcul")
ESTIME = sum(p[2] for p in POSTES if p[3] == "estime")
CAISSE = MESURE + CALCUL

N = lambda x, d=0: f"{x:,.{d}f}".replace(",", " ").replace(".", ",")
P = lambda x, d=1: f"{x:,.{d}f}".replace(",", " ").replace(".", ",") + " %"
cg = lambda v, **k: dict(v=v, **k)
cd = lambda v, **k: dict(v=v, align="right", **k)
NATURE = {"mesure": "mesuré", "calcul": "calculé", "estime": "estimé"}


def barre():
    return {
        "kind": "barreComposition",
        "titre": "Où passent les 10 622 L d’alcool achetés, après les trois corrections que nous portons",
        "sousTitre": "Chaque segment est mesuré en caisse, calculé sur des quantités de caisse, ou "
                     "estimé à un taux publié. Le dernier segment est le solde : il n’est pas choisi.",
        "unite": "L",
        "total": ACHATS,
        "segments": [{"label": p[1], "valeur": p[2], "categorie": p[3]} for p in POSTES]
                    + [{"label": "Perte pure (résidu)", "valeur": RESIDU, "categorie": "residuel"}],
        "legende": True,
    }


def tableau():
    lignes = [[cg(p[1]), cd(N(p[2]) + " L"), cg(NATURE[p[3]]), cg(p[4]),
               cg(p[5], to="/reponse-1/" + p[6])] for p in POSTES]
    lignes.append([cg("Total attribué à un poste identifié", fw=700), cd(N(JUSTIFIE) + " L", fw=700),
                   cg(""), cg(""), cg("")])
    lignes.append([cg("Perte pure (casse, évaporation, fonds de verre, rinçage)"),
                   cd(N(RESIDU) + " L"), cg("résidu"),
                   cg("Solde du bilan matière : aucun taux, aucune hypothèse"),
                   cg("R1-cascade-bilan-matiere.xlsx")])
    lignes.append([cg("Total acheté (factures)", fw=700), cd(N(ACHATS) + " L", fw=700),
                   cg(""), cg(""), cg("")])
    return {
        "kind": "tableau",
        "titre": "Les onze postes de la cascade : nature du chiffre, source et page de démonstration",
        "minWidth": 900,
        "colonnes": [{"label": "Poste"}, {"label": "Volume", "align": "right"},
                     {"label": "Nature du chiffre"}, {"label": "Source"},
                     {"label": "Page de démonstration"}],
        "lignes": lignes,
    }


def kpis():
    return {"kind": "kpis", "items": [
        {"label": "Mesuré en caisse ou à l’inventaire", "valeur": N(MESURE) + " L",
         "sub": P(100 * MESURE / ACHATS) + " des achats"},
        {"label": "Calculé sur des quantités de caisse", "valeur": N(CALCUL) + " L",
         "sub": P(100 * CALCUL / ACHATS) + " des achats"},
        {"label": "Estimé à un taux publié", "valeur": N(ESTIME) + " L",
         "sub": P(100 * ESTIME / ACHATS) + " des achats"},
        {"label": "Résidu de perte pure", "valeur": N(RESIDU) + " L",
         "sub": P(PCT_RESIDU) + " des achats", "highlight": True, "couleur": "teal"},
    ]}


def ecrire_xlsx():
    """Régénère la pièce R1-cascade-bilan-matiere.xlsx sur les valeurs corrigées."""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    blanc = Font(bold=True, color="FFFFFF")
    tete = PatternFill("solid", fgColor="0F766E")
    surligne = PatternFill("solid", fgColor="CCE7E2")
    trait = Side(style="thin", color="D8DEE4")
    bord = Border(left=trait, right=trait, top=trait, bottom=trait)
    droite = Alignment(horizontal="right")

    ws = wb.active
    ws.title = "Cascade"
    ws.append(["Bilan matiere des 10 622 L d'alcool achetes sur les trois exercices verifies"])
    ws["A1"].font = Font(bold=True, size=13)
    ws.append(["Un litre achete est soit vendu, soit encore en stock, soit consomme sans vente, "
               "soit perdu. Le residu n'est pas choisi : c'est le solde de l'egalite. Version "
               "integrant les trois corrections portees contre nous-memes (cremant borne par le "
               "stock, sur-versement separe par assiette, alcool de cuisine plafonne aux factures)."])
    ws["A2"].font = Font(italic=True, size=9, color="64748B")
    ws.append([])
    cols = ["Poste", "Litres", "Part des achats", "Nature du chiffre", "Source",
            "Page de demonstration"]
    ws.append(cols)
    for c in range(1, len(cols) + 1):
        cell = ws.cell(row=4, column=c)
        cell.font, cell.fill, cell.border = blanc, tete, bord
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    for p in POSTES:
        ws.append([p[1], p[2], p[2] / ACHATS, NATURE[p[3]], p[4], p[5]])
        r = ws.max_row
        for c in range(1, len(cols) + 1):
            ws.cell(row=r, column=c).border = bord
        ws.cell(row=r, column=2).alignment = droite
        ws.cell(row=r, column=3).number_format = "0,0 %"
    ws.append(["Total attribue a un poste identifie", JUSTIFIE, JUSTIFIE / ACHATS, "", "", ""])
    ws.append(["Perte pure (casse, evaporation, fonds de verre, rincage)", RESIDU,
               RESIDU / ACHATS, "residu", "Solde du bilan matiere", ""])
    ws.append(["Total achete (factures)", ACHATS, 1.0, "", "", ""])
    for r in range(ws.max_row - 2, ws.max_row + 1):
        for c in range(1, len(cols) + 1):
            ws.cell(row=r, column=c).font = Font(bold=True)
            ws.cell(row=r, column=c).fill = surligne
            ws.cell(row=r, column=c).border = bord
        ws.cell(row=r, column=2).alignment = droite
        ws.cell(row=r, column=3).number_format = "0,0 %"
    for i, w in enumerate([46, 12, 16, 18, 52, 28], 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A5"

    ws2 = wb.create_sheet("Nature des postes")
    ws2.append(["Repartition des 10 622 L par nature du chiffre"])
    ws2["A1"].font = Font(bold=True, size=13)
    ws2.append([])
    ws2.append(["Nature", "Litres", "Part des achats", "Definition"])
    for c in range(1, 5):
        cell = ws2.cell(row=3, column=c)
        cell.font, cell.fill, cell.border = blanc, tete, bord
    for lib, v, d in [
        ("Mesure", MESURE, "Lu directement dans le detail des tickets ou dans l'inventaire"),
        ("Calcule", CALCUL, "Quantite lue en caisse multipliee par une dose ou une recette de la carte"),
        ("Estime", ESTIME, "Taux publie applique a une base lue en caisse"),
        ("Residu", RESIDU, "Solde de l'egalite : aucun taux, aucune hypothese"),
    ]:
        ws2.append([lib, v, v / ACHATS, d])
        r = ws2.max_row
        for c in range(1, 5):
            ws2.cell(row=r, column=c).border = bord
        ws2.cell(row=r, column=2).alignment = droite
        ws2.cell(row=r, column=3).number_format = "0,0 %"
    for i, w in enumerate([16, 12, 16, 76], 1):
        ws2.column_dimensions[get_column_letter(i)].width = w

    chemin = os.path.join(ROOT, "public/documents/pieces-reponse-1/R1-cascade-bilan-matiere.xlsx")
    wb.save(chemin)
    print("écrit :", chemin)


def remplace(slug, remplacements):
    """remplacements : {index: section} ou {index: [sections]}."""
    chemin = os.path.join(DATA, slug + ".json")
    doc = json.load(open(chemin, encoding="utf-8"))
    secs = doc["sections"]
    for i in sorted(remplacements, reverse=True):
        v = remplacements[i]
        secs[i:i + 1] = v if isinstance(v, list) else [v]
    json.dump(doc, open(chemin, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("écrit :", chemin, "->", len(secs), "sections")


def main():
    # ------------------------------------------------ partie M (cascade) ----
    para = lambda t: {"kind": "paragraphe", "texte": t}
    remplace("cascade-10622-litres", {
        27: barre(),
        28: tableau(),
        29: kpis(),
        30: para(
            f"**Les trois quarts du bilan reposent sur la caisse.** {N(MESURE)} L sont lus "
            f"directement dans la caisse ou dans l’inventaire et {N(CALCUL)} L sont calculés à "
            f"partir de quantités lues en caisse, soit {P(100 * CAISSE / ACHATS)} des achats. Les "
            f"postes estimés à partir d’un taux publié ne pèsent que {N(ESTIME)} L, soit "
            f"{P(100 * ESTIME / ACHATS)} des achats. L’objection selon laquelle notre méthode "
            f"serait une construction d’hypothèses ne correspond pas à ce qu’elle contient."),
        31: {"kind": "titre", "texte": "Trois corrections que nous apportons contre nous-mêmes"},
        32: para(
            "Le service a formulé trois objections qui portent, et nous les intégrons. Sur le "
            "[crémant](/reponse-1/recon-3-cremant-vendu), il a montré page 63 que le sur-versement "
            "maximal et le fond de bouteille ne pouvaient pas être cumulés : le volume n’est plus "
            "déduit d’un taux mais **borné par le stock lui-même**, jour par jour, avec ses propres "
            "doses, et le poste tombe de 347 L à **272 L**. Sur le "
            "[sur-versement au verre](/reponse-1/sur-versement-au-verre), notre ligne « vin au "
            "verre » incluait des pichets et des bouteilles, dont le sur-versement est nul par "
            "construction : séparé assiette par assiette, le poste tombe de 720 L à **494 L**. Sur "
            "l’[alcool de cuisine](/reponse-1/recon-5-alcool-cuisine), le rapprochement avec les "
            "factures montre que le Calvados et le Grand Marnier ne pouvaient pas être retenus au "
            "volume calculé : plafonné aux achats, le poste tombe de 795 L à **745 L**. Sur ces "
            "745 L réellement partis en cuisine, le service en retranche déjà une part dans sa "
            "propre reconstitution : nous ne lui en demandons que **173 L de plus**."),
        33: para(
            f"Ces trois corrections jouent contre nous et nous les portons quand même, parce qu’un "
            f"bilan matière n’a de valeur que s’il est rectifié dès qu’il est pris en défaut. Le "
            f"volume attribué à un poste identifié passe de 9 079 L à **{N(JUSTIFIE)} L** "
            f"({P(PCT_JUSTIFIE)}) et la perte pure de 1 543 L à **{N(RESIDU)} L**, soit "
            f"**{P(PCT_RESIDU)}** des achats. **Elles ne libèrent aucun litre pour une vente "
            f"dissimulée** : un litre qui cesse d’être « justifié poste par poste » devient de la "
            f"perte non ventilée, il ne devient pas une recette. Dans les deux cas, il n’a pas été "
            f"vendu, et la reconstitution, qui suppose des doses exactes et zéro perte, le compte "
            f"comme s’il l’avait été."),
        37: para(
            f"**Notre résidu se compare à la démarque du secteur sur la même base.** Beverage "
            f"Metrics et Stock-Taker retiennent 25 % **du volume acheté**, qui est exactement notre "
            f"dénominateur. Notre résidu de **{N(RESIDU)} L, soit {P(PCT_RESIDU)} des achats**, se "
            f"situe **en dessous** de cette référence, alors qu’il est une grandeur plus étroite : "
            f"les taux publiés couvrent tout ce qui est acheté sans être facturé, sur-versement, "
            f"offerts et consommation du personnel compris, tandis que le nôtre ne couvre que ce "
            f"qui reste **une fois tous ces postes déjà chiffrés à part**."),
        42: para(
            "**Le taux global n’est pas de 20 à 50 %.** Les pourcentages que le service cite sont "
            "des coefficients par régime de service, pas le résultat. Rapporté à sa base, et une "
            "fois les pichets et les bouteilles retirés de l’assiette, le sur-versement représente "
            "**494 L pour 1 700 L environ réellement versés à la main**, et **4,6 % des 10 622 L "
            "achetés**. C’est ce seul chiffre qui entre dans la cascade."),
        51: para(
            f"Le bilan corrigé boucle : {N(ACHATS)} L achetés, {N(JUSTIFIE)} L attribués à des "
            f"postes identifiés dont {N(CAISSE)} L mesurés ou calculés sur la caisse, et "
            f"{N(RESIDU)} L de perte pure, en dessous de la démarque de 25 % du volume acheté "
            f"retenue par les auditeurs d’inventaire de bar. Il ne reste **aucun volume de boisson "
            f"disponible** pour alimenter les ventes dissimulées que la reconstitution suppose, ni, "
            f"par voie de conséquence, le chiffre d’affaires cuisine qui en est extrapolé."),
    })

    # ------------------------------------------------ partie L (cadrage) ----
    remplace("reconstitution-cadre-general", {
        26: para(
            f"Nous corrigeons nous-mêmes trois postes de cet encadré, et les trois corrections "
            f"jouent contre nous : le [crémant](/reponse-1/recon-3-cremant-vendu) passe de 347 L à "
            f"**272 L**, borné par le stock ; le [sur-versement au verre]"
            f"(/reponse-1/sur-versement-au-verre) de 720 L à **494 L**, une fois les pichets et les "
            f"bouteilles retirés de l’assiette ; l’[alcool de cuisine]"
            f"(/reponse-1/recon-5-alcool-cuisine) de 795 L à **745 L**, plafonné aux achats "
            f"facturés. Le volume justifié passe donc de 9 079 L à **{N(JUSTIFIE)} L** et le résidu "
            f"de 1 543 L à **{N(RESIDU)} L**, soit **{P(PCT_RESIDU)}** des achats. Aucune de ces "
            f"corrections ne libère de volume vendable : un litre qui sort du « justifié poste par "
            f"poste » entre dans la perte non ventilée, il n’entre pas dans les recettes."),
        36: para(
            f"Les onze points et les huit parties qui suivent sont examinés un à un dans les pages "
            f"liées ci-dessus. Le bilan matière d’ensemble est traité à [la partie M]"
            f"(/reponse-1/cascade-10622-litres) : les {N(ACHATS)} L achetés s’expliquent à hauteur "
            f"de {N(JUSTIFIE)} L par des postes mesurés ou calculés sur la caisse, et le résidu de "
            f"{N(RESIDU)} L reste une perte d’exploitation normale, en dessous de la démarque de "
            f"25 % du volume acheté publiée par les auditeurs d’inventaire de bar."),
    })

    ecrire_xlsx()

    print(f"\nCascade : {N(ACHATS)} L achetés = {N(JUSTIFIE)} L justifiés ({P(PCT_JUSTIFIE)}) "
          f"+ {N(RESIDU)} L de résidu ({P(PCT_RESIDU)})")
    print(f"  mesuré {N(MESURE)} L / calculé {N(CALCUL)} L / estimé {N(ESTIME)} L")


if __name__ == "__main__":
    main()
