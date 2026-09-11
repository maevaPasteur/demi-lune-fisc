#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REPONSE 1 - Colonnes E et F des annexes C-1 a C-3 : ce qu'elles mesurent
========================================================================
Reponse DDFiP 39 du 04/09/2026, p. 44 et p. 93.

Le service a ajoute deux colonnes dans son propre tableur, sur l'archive des
tickets :
  E « Erreur Taux TVA dans Base Envoyee Faux/Correct »
  F « Correction TVA Sur Taux »
et en tire un grief d'« erreurs d'application de taux de TVA sur les articles ».

Ce script etablit :
  1. la semantique exacte des deux colonnes (formule, sens, agregation) ;
  2. l'incidence reelle des « erreurs de taux » sur la TVA reellement due ;
  3. les controles qui departagent les deux lectures possibles.

READ-ONLY sur les sources. Sortie :
  public/documents/pieces-reponse-1/R1-tva-colonnes-ef.xlsx

Lancer :  python3 scripts/reponse1-tva-colonnes-ef.py
"""

import collections
import os

import xlrd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAISSE = os.path.join(ROOT, "public", "documents", "caisse-enregistreuse")
OUT_DIR = os.path.join(ROOT, "public", "documents", "pieces-reponse-1")
OUT = os.path.join(OUT_DIR, "R1-tva-colonnes-ef.xlsx")

EXOS = [("1", "2022-2023", "31/03/2023"),
        ("2", "2023-2024", "31/03/2024"),
        ("3", "2024-2025", "31/03/2025")]

# Comptabilite, chiffres reproduits par le service p. 26 de la proposition de
# rectifications : bases HT declarees (706300 a 10 %, 706000 a 20 %) et TVA
# collectee portee au compte 445710.
HT_DECLARE = {"2022-2023": {10: 296105.87, 20: 64712.51},
              "2023-2024": {10: 319179.31, 20: 72416.55},
              "2024-2025": {10: 318345.43, 20: 70517.47}}
TVA_445710 = {"2022-2023": 42614.45, "2023-2024": 46464.79, "2024-2025": 46005.45}
COMPTA = {e: {t: round(HT_DECLARE[e][t] * t / 100.0, 2) for t in (10, 20)} for e in HT_DECLARE}

# Colonnes de l'annexe C (0-based)
C_DATE, C_TICKET, C_TOTTTC, C_TOTTVA, C_ID = 0, 2, 5, 6, 8
C_REF, C_LIB, C_QTE, C_PU, C_TAUX, C_TTC = 9, 10, 11, 13, 15, 16
C_E, C_F = 21, 22

FLAG_10_20 = "10 % / 20 %"   # taux 10 applique, 20 juge correct
FLAG_20_10 = "20 % / 10 %"   # taux 20 applique, 10 juge correct


def sheet(nom):
    return xlrd.open_workbook(os.path.join(CAISSE, nom)).sheet_by_index(0)


def flag(v):
    return str(v).replace("\xa0", " ").strip()


def tva(ttc, taux):
    return ttc * taux / (100.0 + taux)


# ------------------------------------------------------------------ lecture --
def lire_C(i, lib):
    sh = sheet("ANNEXE-C%s_detail-tickets_%s.xls" % (i, lib))
    d = dict(
        entete_E=sh.cell_value(0, C_E), entete_F=sh.cell_value(0, C_F),
        total_F_ligne=None,
        n_lignes=0, n_flag=collections.Counter(), ttc_flag=collections.Counter(),
        somme_F=0.0, somme_F_par_sens=collections.Counter(),
        formule_ok=0, formule_ko=[],
        ttc_brut=collections.Counter(), ttc_corr=collections.Counter(),
        taux_par_ref_brut=collections.defaultdict(set),
        taux_par_ref_corr=collections.defaultdict(set),
        libelle_ref={},
        ticket_brut=collections.defaultdict(lambda: [0.0, 0.0]),
        ticket_corr=collections.defaultdict(lambda: [0.0, 0.0]),
        tva_ticket={}, ttc_ticket={},
        lignes_brutes=[])
    for r in range(1, sh.nrows):
        v = sh.row_values(r)
        if v[C_TICKET] == "TOTAL":
            d["total_F_ligne"] = v[C_F]
            continue
        if v[C_DATE] == "" or not isinstance(v[C_TAUX], float) or not isinstance(v[C_TTC], float):
            continue
        ttc, taux, ref = v[C_TTC], v[C_TAUX], str(v[C_REF])
        d["n_lignes"] += 1
        d["libelle_ref"][ref] = v[C_LIB]
        d["taux_par_ref_brut"][ref].add(taux)
        d["ttc_brut"][taux] += ttc
        k = (v[C_DATE], int(v[C_TICKET]))
        d["ticket_brut"][k][0 if taux == 10 else 1] += ttc
        d["tva_ticket"][int(v[C_ID])] = v[C_TOTTVA]
        d["ttc_ticket"][int(v[C_ID])] = v[C_TOTTTC]

        e = flag(v[C_E])
        if e in (FLAG_10_20, FLAG_20_10):
            d["n_flag"][e] += 1
            d["ttc_flag"][e] += ttc
            taux_corr = 20.0 if e == FLAG_10_20 else 10.0
            sgn = 1.0 if e == FLAG_10_20 else -1.0
            attendu = sgn * ttc / 13.2          # ttc*(20/120) - ttc*(10/110)
            f = v[C_F] if isinstance(v[C_F], float) else 0.0
            d["somme_F"] += f
            d["somme_F_par_sens"][e] += f
            if abs(f - attendu) <= 0.005:
                d["formule_ok"] += 1
            else:
                d["formule_ko"].append((r + 1, v[C_DATE], int(v[C_TICKET]), ref, v[C_LIB],
                                        v[C_QTE], v[C_PU], ttc, e, f, attendu))
        else:
            taux_corr = taux
        d["taux_par_ref_corr"][ref].add(taux_corr)
        d["ttc_corr"][taux_corr] += ttc
        d["ticket_corr"][k][0 if taux_corr == 10 else 1] += ttc
    return d


def lire_G(i, lib):
    sh = sheet("ANNEXE-G%s_journal-tva_%s.xls" % (i, lib))
    d = dict(tva10=0.0, tva20=0.0, tax=0.0, ticket=collections.defaultdict(lambda: [0.0, 0.0]))
    for r in range(1, sh.nrows):
        v = sh.row_values(r)
        if v[0] in ("TOTAL", "A NOUVEAUX", "") or not isinstance(v[2], float):
            continue
        k = (v[0], int(v[2]))
        if isinstance(v[14], float):
            d["tax"] += v[14]
        if isinstance(v[16], float):
            d["tva10"] += v[16]
            d["ticket"][k][0] += v[16]
        if isinstance(v[18], float):
            d["tva20"] += v[18]
            d["ticket"][k][1] += v[18]
    return d


D = {}
for i, lib, clos in EXOS:
    C, G = lire_C(i, lib), lire_G(i, lib)
    communs = set(C["ticket_brut"]) & set(G["ticket"])

    def concordance(src):
        ok = 0
        for k in communs:
            a, b = round(src[k][0] / 11.0, 2), round(src[k][1] / 6.0, 2)
            if abs(a - G["ticket"][k][0]) <= 0.03 and abs(b - G["ticket"][k][1]) <= 0.03:
                ok += 1
        return ok

    D[lib] = dict(C=C, G=G, clos=clos, n_communs=len(communs),
                  conc_brut=concordance(C["ticket_brut"]),
                  conc_corr=concordance(C["ticket_corr"]))

# ------------------------------------------------------------------ ecriture -
os.makedirs(OUT_DIR, exist_ok=True)
wb = Workbook()

TITRE = Font(bold=True, color="FFFFFF", size=11)
FOND = PatternFill("solid", fgColor="1F3864")
GRAS = Font(bold=True)
EURO = '#,##0.00 "€"'
PCT = '0.00 "%"'
WRAP = Alignment(wrap_text=True, vertical="top")


def entete(ws, cols, largeurs):
    ws.append(cols)
    for c in range(1, len(cols) + 1):
        cell = ws.cell(row=ws.max_row, column=c)
        cell.font, cell.fill = TITRE, FOND
        cell.alignment = Alignment(wrap_text=True, vertical="center")
    for c, w in enumerate(largeurs, start=1):
        ws.column_dimensions[get_column_letter(c)].width = w
    ws.freeze_panes = "A2"


def fr(x):
    """Nombre au format francais : espace comme separateur de milliers, virgule."""
    return "{:,.2f}".format(x).replace(",", " ").replace(".", ",")


def note(ws, texte, col=1, largeur=None):
    ws.append([])
    ws.append([texte])
    ws.cell(row=ws.max_row, column=col).alignment = WRAP


# ---- 1. Ce que mesurent les colonnes E et F ---------------------------------
ws = wb.active
ws.title = "1 Semantique E et F"
entete(ws, ["Point etabli", "Constat", "Comment il est verifie"], [34, 58, 78])
C1 = D["2022-2023"]["C"]
tot_ok = sum(D[l]["C"]["formule_ok"] for _, l, _ in EXOS)
tot_ko = sum(len(D[l]["C"]["formule_ko"]) for _, l, _ in EXOS)
rows = [
    ("Origine des colonnes",
     "Colonnes ajoutees par le service dans son tableur, pas des colonnes de la caisse",
     "Le fichier numerote 1 a 17 les colonnes issues du logiciel, puis A a G celles que le "
     "service ajoute. E et F sont des lettres."),
    ("En-tete de la colonne E",
     C1["entete_E"].replace("\n", " "),
     "Lu directement en ligne 1 de l'annexe C-1. « Base Envoyee » : l'erreur est situee par "
     "le service lui-meme dans le FICHIER TRANSMIS, pas dans la taxe liquidee."),
    ("En-tete de la colonne F",
     C1["entete_F"].replace("\n", " "),
     "Lu directement en ligne 1 de l'annexe C-1."),
    ("Ce que porte la colonne E",
     "Deux valeurs seulement : « %s » et « %s »" % (FLAG_10_20, FLAG_20_10),
     "Lecture : taux applique dans le fichier / taux juge correct par le service. "
     "La colonne est un drapeau, elle ne s'additionne pas."),
    ("Formule exacte de la colonne F",
     "F = TTC de la ligne x (taux correct/(100+taux correct) - taux applique/(100+taux applique)) "
     "soit +/- TTC / 13,2",
     "Verifie ligne a ligne : %d lignes conformes au centime sur %d, %d exception(s) "
     "(voir onglet 2)." % (tot_ok, tot_ok + tot_ko, tot_ko)),
    ("Sens de la colonne F",
     "F = TVA au taux corrige MOINS TVA au taux du fichier. Positive quand le service "
     "redresse 10 % vers 20 %, negative dans l'autre sens.",
     "Chaque ligne signalee porte UNE valeur signee. Il n'y a pas de double comptage : "
     "les deux sens sont des lignes differentes, pas la meme ligne comptee deux fois."),
    ("Agregation correcte",
     "Somme algebrique des valeurs de ligne, en excluant la ligne TOTAL du fichier",
     "La ligne TOTAL de chaque annexe C porte deja le total de la colonne F. L'y inclure "
     "double mecaniquement le resultat (voir onglet 2)."),
    ("Ce que la colonne F ne mesure PAS",
     "Un trop-paye ou un manque a gagner de TVA",
     "La TVA liquidee ne se lit pas dans la colonne « taux » de l'archive des tickets mais "
     "au niveau du ticket (colonne tot_tva) et du journal de TVA (annexe G). "
     "Onglets 3, 4 et 5."),
]
for a, b, c in rows:
    ws.append([a, b, c])
    for col in (1, 2, 3):
        ws.cell(row=ws.max_row, column=col).alignment = WRAP
note(ws, "Conclusion de l'onglet : les colonnes E et F sont une CORRECTION, portee par le service, "
         "de la colonne « taux_tva » de l'archive des tickets. Elles disent que cette colonne du "
         "fichier transmis est fausse ligne a ligne. Elles ne disent rien, par elles-memes, de la "
         "TVA reellement liquidee et reversee.")

# ---- 2. Somme de la colonne F, et le piege de la ligne TOTAL ----------------
ws = wb.create_sheet("2 Somme de la colonne F")
entete(ws, ["Exercice clos", "Lignes « 10 % / 20 % »", "Lignes « 20 % / 10 % »",
            "Total lignes signalees", "Somme F sens 10 vers 20", "Somme F sens 20 vers 10",
            "Somme F (lignes seules)", "Valeur portee par la ligne TOTAL du fichier",
            "Somme si l'on inclut la ligne TOTAL"],
       [14, 16, 16, 14, 18, 18, 18, 20, 20])
tot = collections.Counter()
for i, lib, clos in EXOS:
    C = D[lib]["C"]
    a, b = C["n_flag"][FLAG_10_20], C["n_flag"][FLAG_20_10]
    fa, fb = C["somme_F_par_sens"][FLAG_10_20], C["somme_F_par_sens"][FLAG_20_10]
    ws.append([clos, a, b, a + b, round(fa, 2), round(fb, 2), round(C["somme_F"], 2),
               round(C["total_F_ligne"], 2), round(C["somme_F"] + C["total_F_ligne"], 2)])
    for c in (5, 6, 7, 8, 9):
        ws.cell(row=ws.max_row, column=c).number_format = EURO
    tot["a"] += a; tot["b"] += b; tot["fa"] += fa; tot["fb"] += fb
    tot["f"] += C["somme_F"]; tot["t"] += C["total_F_ligne"]
ws.append(["Cumul", tot["a"], tot["b"], tot["a"] + tot["b"], round(tot["fa"], 2),
           round(tot["fb"], 2), round(tot["f"], 2), round(tot["t"], 2),
           round(tot["f"] + tot["t"], 2)])
for c in range(1, 10):
    ws.cell(row=ws.max_row, column=c).font = GRAS
for c in (5, 6, 7, 8, 9):
    ws.cell(row=ws.max_row, column=c).number_format = EURO
note(ws, "Lecture : la ligne TOTAL de chaque annexe C porte deja, dans la colonne F, la somme des "
         "lignes. Une addition qui balaie le fichier de haut en bas sans exclure cette ligne obtient "
         "donc exactement le double du vrai total. C'est la seule origine du facteur deux : la colonne "
         "ne compte aucune correction deux fois.")
ws.append([])
ws.append(["Lignes ou la colonne F du service s'ecarte de sa propre formule :"])
ws.cell(row=ws.max_row, column=1).font = GRAS
ws.append(["Exercice", "Ligne du fichier", "Date", "Ticket", "Reference", "Libelle", "Qte",
           "Prix unitaire", "TTC de la ligne", "Sens", "Valeur F du service", "Valeur attendue"])
for c in range(1, 13):
    ws.cell(row=ws.max_row, column=c).font = GRAS
for i, lib, clos in EXOS:
    for k in D[lib]["C"]["formule_ko"]:
        ws.append([clos, k[0], k[1], k[2], k[3], k[4], k[5], k[6], k[7], k[8],
                   round(k[9], 2), round(k[10], 2)])
note(ws, "Sur cette ligne, le service a applique sa formule au prix catalogue multiplie par la "
         "quantite, et non au montant TTC effectivement encaisse apres remise. L'ecart est de "
         "0,91 EUR sur trois exercices : il explique que la somme brute de la colonne F "
         "(9 424,74 EUR) et l'ecart de TVA reellement produit par les corrections "
         "(9 423,82 EUR, onglet 3) ne coincident pas au centime.")

# ---- 3. Incidence reelle sur la TVA ----------------------------------------
ws = wb.create_sheet("3 Incidence reelle")
entete(ws, ["Exercice clos", "Taux",
            "A. TVA calculee avec la colonne « taux » du fichier, telle quelle",
            "B. TVA calculee avec les taux corriges par le service (colonne E)",
            "B - A : effet des corrections",
            "C. TVA collectee reversee (compte 445710)",
            "B - C : ecart avec la TVA reversee"],
       [14, 10, 26, 26, 20, 22, 22])
g = collections.Counter()
for i, lib, clos in EXOS:
    C = D[lib]["C"]
    sa = sb = sc = 0.0
    for taux in (10.0, 20.0):
        a = tva(C["ttc_brut"][taux], taux)
        b = tva(C["ttc_corr"][taux], taux)
        c = COMPTA[lib][int(taux)]
        sa += a; sb += b
        ws.append([clos, "%d %%" % taux, round(a, 2), round(b, 2), round(b - a, 2),
                   c, round(b - c, 2)])
        for col in (3, 4, 5, 6, 7):
            ws.cell(row=ws.max_row, column=col).number_format = EURO
    sc = TVA_445710[lib]
    ws.append([clos, "Total", round(sa, 2), round(sb, 2), round(sb - sa, 2), round(sc, 2),
               round(sb - sc, 2)])
    for col in range(1, 8):
        ws.cell(row=ws.max_row, column=col).font = GRAS
    for col in (3, 4, 5, 6, 7):
        ws.cell(row=ws.max_row, column=col).number_format = EURO
    g["a"] += round(sa, 2); g["b"] += round(sb, 2); g["c"] += round(sc, 2)
    ws.append([])
ws.append(["Cumul 3 exercices", "Total", round(g["a"], 2), round(g["b"], 2),
           round(g["b"] - g["a"], 2), round(g["c"], 2), round(g["b"] - g["c"], 2)])
for col in range(1, 8):
    ws.cell(row=ws.max_row, column=col).font = GRAS
for col in (3, 4, 5, 6, 7):
    ws.cell(row=ws.max_row, column=col).number_format = EURO
note(ws, "Lecture, et c'est le point decisif. La colonne A n'a jamais servi d'assiette a une "
         "declaration : personne n'a jamais reverse %s EUR de TVA. La colonne B, celle qui applique "
         "les corrections du service, tombe a %s EUR de la TVA effectivement reversee sur trois "
         "exercices, soit %s %%. Les corrections des colonnes E et F ne revelent donc pas un "
         "trop-paye : elles RESTITUENT la taxe telle qu'elle a ete liquidee et reversee. Leur "
         "incidence sur la TVA due est nulle."
     % (fr(g["a"]), fr(abs(g["b"] - g["c"])),
        ("%.3f" % (abs(g["b"] - g["c"]) / g["c"] * 100)).replace(".", ",")))

# ---- 4. Controle par ticket contre le journal de TVA ------------------------
ws = wb.create_sheet("4 Controle par ticket")
entete(ws, ["Exercice clos", "Tickets presents dans les annexes C et G",
            "Tickets dont la ventilation 10/20 est exacte avec la colonne « taux » du fichier",
            "En %", "Tickets dont la ventilation 10/20 est exacte avec les taux corriges",
            "En %", "TVA du journal G (tax_amount)", "TVA du ticket (annexe C, tot_tva)"],
       [14, 18, 26, 10, 26, 10, 20, 20])
for i, lib, clos in EXOS:
    d = D[lib]
    n = d["n_communs"]
    ws.append([clos, n, d["conc_brut"], round(100.0 * d["conc_brut"] / n, 2),
               d["conc_corr"], round(100.0 * d["conc_corr"] / n, 2),
               round(d["G"]["tax"], 2), round(sum(d["C"]["tva_ticket"].values()), 2)])
    for c in (4, 6):
        ws.cell(row=ws.max_row, column=c).number_format = PCT
    for c in (7, 8):
        ws.cell(row=ws.max_row, column=c).number_format = EURO
note(ws, "Lecture : ticket par ticket, la ventilation 10 % / 20 % reconstituee avec la colonne "
         "« taux » du fichier ne retrouve la ventilation reelle du journal de TVA que dans un "
         "ticket sur cinq. Avec les taux corriges par le service, elle la retrouve dans plus de "
         "quatre tickets sur cinq. Les corrections des colonnes E et F vont donc dans le sens de "
         "la taxe reellement liquidee : elles reparent le fichier, elles ne redressent pas la "
         "societe.")

# ---- 5. Le taux redevient un attribut de l'article -------------------------
ws = wb.create_sheet("5 Taux par article")
entete(ws, ["Exercice clos", "References vendues",
            "References apparaissant aux DEUX taux avec la colonne « taux » du fichier", "En %",
            "References apparaissant aux deux taux APRES les corrections du service", "En %"],
       [14, 16, 30, 10, 30, 10])
for i, lib, clos in EXOS:
    C = D[lib]["C"]
    n = len(C["taux_par_ref_brut"])
    nb = sum(1 for k in C["taux_par_ref_brut"] if len(C["taux_par_ref_brut"][k]) > 1)
    nc = sum(1 for k in C["taux_par_ref_corr"] if len(C["taux_par_ref_corr"][k]) > 1)
    ws.append([clos, n, nb, round(100.0 * nb / n, 2), nc, round(100.0 * nc / n, 2)])
    for c in (4, 6):
        ws.cell(row=ws.max_row, column=c).number_format = PCT
note(ws, "Lecture : dans un logiciel de caisse, le taux de TVA est un attribut de la fiche article. "
         "Telle qu'elle figure dans le fichier transmis, la colonne « taux » fait apparaitre plus de "
         "huit references sur dix tantot a 10 %, tantot a 20 % : elle ne restitue donc pas le taux de "
         "l'article. Une fois les corrections du service appliquees, la quasi-totalite des references "
         "retrouve un taux unique. C'est la demonstration que la colonne E corrige un defaut de "
         "l'export, et non un parametrage de la caisse.")
ws.append([])
ws.append(["References qui conservent deux taux apres correction :"])
ws.cell(row=ws.max_row, column=1).font = GRAS
ws.append(["Exercice clos", "Reference", "Libelle"])
for c in (1, 2, 3):
    ws.cell(row=ws.max_row, column=c).font = GRAS
for i, lib, clos in EXOS:
    C = D[lib]["C"]
    for k in sorted(C["taux_par_ref_corr"]):
        if len(C["taux_par_ref_corr"][k]) > 1:
            ws.append([clos, k, C["libelle_ref"][k]])

# ---- 6. Exemple : la journee que le service reproduit page 44 --------------
ws = wb.create_sheet("6 Exemple 14-04-2022")
entete(ws, ["Ticket", "Reference", "Libelle", "Qte", "TTC de la ligne",
            "Taux porte par le fichier", "Colonne E du service", "Taux corrige",
            "Colonne F du service"],
       [10, 12, 30, 8, 14, 16, 18, 12, 16])
shC = sheet("ANNEXE-C1_detail-tickets_2022-2023.xls")
cibles = (2, 3)
recap = collections.defaultdict(lambda: [0.0, 0.0, 0.0, 0.0])
for r in range(1, shC.nrows):
    v = shC.row_values(r)
    if v[C_TICKET] == "TOTAL" or v[C_DATE] != "2022-04-14":
        continue
    if not isinstance(v[C_TICKET], float) or int(v[C_TICKET]) not in cibles:
        continue
    e = flag(v[C_E])
    tc = 20.0 if e == FLAG_10_20 else (10.0 if e == FLAG_20_10 else v[C_TAUX])
    ws.append([int(v[C_TICKET]), str(v[C_REF]), v[C_LIB], v[C_QTE], v[C_TTC],
               "%d %%" % v[C_TAUX], e if e in (FLAG_10_20, FLAG_20_10) else "",
               "%d %%" % tc, round(v[C_F], 2) if isinstance(v[C_F], float) else ""])
    for c in (5, 9):
        ws.cell(row=ws.max_row, column=c).number_format = EURO
    k = int(v[C_TICKET])
    recap[k][0 if v[C_TAUX] == 10 else 1] += v[C_TTC]
    recap[k][2 if tc == 10 else 3] += v[C_TTC]
shG = sheet("ANNEXE-G1_journal-tva_2022-2023.xls")
gt = collections.defaultdict(lambda: [0.0, 0.0])
for r in range(1, shG.nrows):
    v = shG.row_values(r)
    if v[0] != "2022-04-14" or not isinstance(v[2], float) or int(v[2]) not in cibles:
        continue
    if isinstance(v[16], float):
        gt[int(v[2])][0] += v[16]
    if isinstance(v[18], float):
        gt[int(v[2])][1] += v[18]
ws.append([])
ws.append(["Ticket", "TVA 10 % selon la colonne du fichier", "TVA 20 % selon la colonne du fichier",
           "TVA 10 % avec les taux corriges", "TVA 20 % avec les taux corriges",
           "TVA 10 % REELLE (journal G)", "TVA 20 % REELLE (journal G)"])
for c in range(1, 8):
    ws.cell(row=ws.max_row, column=c).font = GRAS
for k in sorted(recap):
    ws.append([k, round(recap[k][0] / 11.0, 2), round(recap[k][1] / 6.0, 2),
               round(recap[k][2] / 11.0, 2), round(recap[k][3] / 6.0, 2),
               round(gt[k][0], 2), round(gt[k][1], 2)])
    for c in range(2, 8):
        ws.cell(row=ws.max_row, column=c).number_format = EURO
note(ws, "Lecture : c'est la journee que le service reproduit page 44 de sa reponse. Sur le ticket 2, "
         "le fichier porte la biere « La Vouivre » a 10 % et le « Coca (25cl) » a 20 %. Le journal de "
         "TVA de la caisse, lui, a bien liquide la biere a 20 % et le soda a 10 %. La colonne E du "
         "service retablit exactement cette repartition. L'erreur est dans la colonne « taux » du "
         "fichier remis, pas dans la taxe encaissee. Sur le ticket 3, la reconstitution corrigee "
         "reste approchee : la correction du service repare la colonne sans la rendre exacte sur "
         "chaque ticket. L'onglet 4 chiffre cette concordance ticket par ticket, et l'onglet 3 "
         "montre qu'a l'echelle des trois exercices elle ramene la TVA reconstituee a 18,76 EUR "
         "de la TVA reversee.")

wb.save(OUT)

# ------------------------------------------------------------------- sortie --
print("Ecrit :", OUT)
ga = gb = gc = gf = 0.0
for i, lib, clos in EXOS:
    C = D[lib]["C"]
    a = sum(tva(C["ttc_brut"][t], t) for t in (10.0, 20.0))
    b = sum(tva(C["ttc_corr"][t], t) for t in (10.0, 20.0))
    c = TVA_445710[lib]
    ga += round(a, 2); gb += round(b, 2); gc += round(c, 2); gf += C["somme_F"]
    print("%s | somme colonne F = %+9.2f | ligne TOTAL du fichier = %+9.2f | somme + TOTAL = %+9.2f"
          % (clos, C["somme_F"], C["total_F_ligne"], C["somme_F"] + C["total_F_ligne"]))
    print("            TVA taux du fichier %10.2f | taux corriges %10.2f | effet %+8.2f | reversee %10.2f | ecart %+7.2f"
          % (a, b, b - a, c, b - c))
print("CUMUL      | somme colonne F = %+9.2f" % gf)
print("            TVA taux du fichier %10.2f | taux corriges %10.2f | effet %+8.2f | reversee %10.2f | ecart %+7.2f"
      % (ga, gb, gb - ga, gc, gb - gc))
for i, lib, clos in EXOS:
    d = D[lib]
    print("%s | tickets communs %d | ventilation exacte : colonne brute %d (%.1f %%), taux corriges %d (%.1f %%)"
          % (clos, d["n_communs"], d["conc_brut"], 100.0 * d["conc_brut"] / d["n_communs"],
             d["conc_corr"], 100.0 * d["conc_corr"] / d["n_communs"]))
