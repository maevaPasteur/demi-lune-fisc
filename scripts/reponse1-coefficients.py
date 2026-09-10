#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REPONSE 1 - Coefficients et extrapolation cuisine
=================================================
Reponse DDFiP 39 du 04/09/2026 : point 11 (p. 76), partie K (p. 56 a 59) et
partie T (p. 90 a 93).

Ce script etablit, a partir des seules donnees de caisse remises au service :
  1. le chiffre d'affaires LIQUIDES et le chiffre d'affaires CUISINE reellement
     enregistres, exercice par exercice (annexes D, controle sur les annexes C) ;
  2. le chiffre d'affaires reconstitue par le service et la part qui provient de
     l'extrapolation cuisine (bras de levier du coefficient) ;
  3. le coefficient sur achat revendu, par exercice et globalise, puis les DEUX
     manieres de lui appliquer un taux de perte de 15 % : sur le resultat (methode
     du service, p. 59 et 93) ou sur la matiere (le denominateur).

READ-ONLY sur les sources. Sortie :
  public/documents/pieces-reponse-1/R1-coefficients-et-extrapolation.xlsx

Lancer :  python3 scripts/reponse1-coefficients.py
"""

import collections
import json
import os

import xlrd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAISSE = os.path.join(ROOT, "public", "documents", "caisse-enregistreuse")
OUT_DIR = os.path.join(ROOT, "public", "documents", "pieces-reponse-1")
OUT = os.path.join(OUT_DIR, "R1-coefficients-et-extrapolation.xlsx")

EXOS = [("2022-2023", "1"), ("2023-2024", "2"), ("2024-2025", "3")]


def sheet(nom):
    return xlrd.open_workbook(os.path.join(CAISSE, nom)).sheet_by_index(0)


# --------------------------------------------------------------------------- #
# 1. Annexes D : ventilation liquides / solides etablie par le SERVICE lui-meme.
#    Le bas de chaque annexe D porte les totaux et la ligne
#    « RAPPORT POUR 1 € DE CA LIQUIDE = ... C-A SOLIDE » : c'est de la que
#    viennent les coefficients 2,94 / 3,02 / 3,10 de la proposition p. 52.
# --------------------------------------------------------------------------- #
def lire_D(i, lib):
    sh = sheet("ANNEXE-D%s_synthese-produit_%s.xls" % (i, lib))
    seg, refs, tot = None, {}, {}
    rapport = None
    for r in range(sh.nrows):
        v = sh.row_values(r)
        a = str(v[0]).replace("\xa0", " ").strip()
        if a.startswith("LIQUIDE – TVA 10"):
            seg = "LIQ10"
            continue
        if a.startswith("LIQUIDE – TVA 20"):
            seg = "LIQ20"
            continue
        if a.startswith("SOLIDE – TVA 10"):
            seg = "SOL10"
            continue
        if a.startswith("TOTAL") or a.startswith("RAPPORT"):
            seg = None
            if a.startswith("RAPPORT"):
                rapport = v[2]
            elif "CA LIQUIDES 10" in a:
                tot["LIQ10"] = v[5]
            elif "CA LIQUIDES 20" in a:
                tot["LIQ20"] = v[5]
            elif "SOLIIDES" in a or "SOLIDES" in a:
                tot["SOL10"] = v[5]
            elif a.startswith("TOTAL GENERAL"):
                tot["GENERAL"] = v[5]
            continue
        if seg and a and a != "Ref_prd" and v[5] != "":
            refs.setdefault(a, seg)
    return {"refs": refs, "tot": tot, "rapport": rapport}


# --------------------------------------------------------------------------- #
# 2. Annexes C : detail des tickets. Controle independant de la ventilation,
#    ligne a ligne, en reprenant la classification produit des annexes D.
# --------------------------------------------------------------------------- #
def lire_C(i, lib, refs):
    sh = sheet("ANNEXE-C%s_detail-tickets_%s.xls" % (i, lib))
    agg = collections.defaultdict(float)
    lignes, inconnus = 0, 0.0
    for r in range(1, sh.nrows):
        v = sh.row_values(r)
        ref = str(v[9]).strip()
        if not ref or v[2] == "TOTAL":
            continue
        montant = v[16] or 0.0
        seg = refs.get(ref)
        if seg is None:
            inconnus += montant
        else:
            agg[seg] += montant
        lignes += 1
    return {"agg": dict(agg), "lignes": lignes, "inconnus": inconnus}


D, C = {}, {}
for lib, i in EXOS:
    D[lib] = lire_D(i, lib)
    C[lib] = lire_C(i, lib, D[lib]["refs"])


# --------------------------------------------------------------------------- #
# 3. La reconstitution du service (proposition p. 52, reproduite p. 90 de la
#    reponse du 04/09/2026) et le grief coefficient (p. 56, proposition p. 34-35).
# --------------------------------------------------------------------------- #
SERVICE = {
    "2022-2023": {"liq_recon": 151590, "coef": 2.94, "sol_recon": 445675,
                  "total_recon": 597265, "declare": 404031,
                  "matieres": 175437, "coef_recon": 3.40},
    "2023-2024": {"liq_recon": 143662, "coef": 3.02, "sol_recon": 433860,
                  "total_recon": 577522, "declare": 438658,
                  "matieres": 183693, "coef_recon": 3.14},
    "2024-2025": {"liq_recon": 140306, "coef": 3.10, "sol_recon": 434947,
                  "total_recon": 575253, "declare": 435525,
                  "matieres": 188539, "coef_recon": 3.05},
}

for lib, _ in EXOS:
    s = SERVICE[lib]
    d = D[lib]["tot"]
    s["liq_reel"] = d["LIQ10"] + d["LIQ20"]
    s["sol_reel"] = d["SOL10"]
    s["alcool_reel"] = d["LIQ20"]
    s["rapport_D"] = D[lib]["rapport"]
    s["discordance"] = s["total_recon"] - s["declare"]
    s["cuisine_fantome"] = s["sol_recon"] - s["sol_reel"]
    s["part_cuisine"] = s["cuisine_fantome"] / s["discordance"]
    s["levier"] = 1 + s["coef"]
    s["gonflement"] = s["liq_recon"] / s["liq_reel"]


# --------------------------------------------------------------------------- #
# 4. Le coefficient sur achat revendu (3,85) et les deux corrections a 15 %.
# --------------------------------------------------------------------------- #
BD = json.load(open(os.path.join(ROOT, "src/data/boissonsPageData.json"), encoding="utf-8"))
SYN = BD["synthese"]
CASCADE = {c["poste"]: c["litres"] for c in SYN["cascade"]}

ACHAT_L = SYN["achat_alcool_l"]                 # 10 622 L
ACHAT_COUT = SYN["achat_alcool_cout"]           # 107 924 €
REVENDU_L = (CASCADE["Vendu au verre (caisse)"]
             + CASCADE["Vendu en cocktails (caisse, biere des cocktails incluse)"])
PART_REVENDUE = REVENDU_L / ACHAT_L             # 61,8 %
COUT_REVENDU = ACHAT_COUT * PART_REVENDUE
CA_ALCOOL = sum(SERVICE[lib]["alcool_reel"] for lib, _ in EXOS)
COEF_REVENDU = CA_ALCOOL / COUT_REVENDU         # 3,85
COEF_ACHATS_TOTAUX = CA_ALCOOL / ACHAT_COUT     # 2,38

TAUX_SERVICE = 0.15

# Methode A : celle du service (p. 59 et 93). L'abattement porte sur le RESULTAT.
# Le denominateur (cout de l'alcool revendu) est inchange : cela revient a
# amputer de 15 % le chiffre d'affaires encaisse.
# Le service pose 3,85 x (1-0,15) = 3,2725 : on reprend son propre resultat.
A_COEF = round(3.85 * (1 - TAUX_SERVICE), 4)    # 3,2725, chiffre du courrier
A_COUT = COUT_REVENDU
A_CA = A_COEF * A_COUT

# Methode B : l'abattement porte sur la MATIERE. Si 15 % seulement des achats ne
# sont pas revendus, alors le cout des achats effectivement revendus passe de
# 61,8 % a 85 % des achats. Le chiffre d'affaires encaisse, lui, ne bouge pas.
B_COUT = ACHAT_COUT * (1 - TAUX_SERVICE)
B_CA = CA_ALCOOL
B_COEF = B_CA / B_COUT

# Repartition par exercice du cout de l'alcool : poids de chaque exercice dans
# les achats d'alcool factures (FCBS). La cascade des volumes n'est etablie que
# de facon globale : le coefficient par exercice est donc une REPARTITION, pas
# une mesure. C'est le coeur de la critique du « globalise sur 3 exercices ».
ACH = json.load(open(os.path.join(ROOT, "src/data/calculsBoissons/achatsBoissonsParPeriode.json"),
                     encoding="utf-8"))["achats"]
CAT_ALCOOL = {"bière", "vin/cidre", "spiritueux/liqueur"}
poids = collections.defaultdict(float)
for p in ACH:
    if p["categorie"] in CAT_ALCOOL:
        for k, v in p["par_periode"].items():
            poids[k] += v.get("montant_ht", 0.0)
tot_poids = sum(poids.values())

for lib, _ in EXOS:
    s = SERVICE[lib]
    s["poids"] = poids[lib] / tot_poids
    s["cout_alcool"] = ACHAT_COUT * s["poids"]
    s["cout_revendu"] = s["cout_alcool"] * PART_REVENDUE
    s["coef_revendu"] = s["alcool_reel"] / s["cout_revendu"]
    # Ce que devient le CA reconstitue si l'on applique a chaque exercice le
    # repere de coefficient global retenu (methode A du service, puis methode B).
    s["ca_si_A"] = A_COEF * s["matieres"]
    s["ca_si_B"] = B_COEF * s["matieres"]
    s["exces_A"] = s["total_recon"] - s["ca_si_A"]
    s["exces_B"] = s["total_recon"] - s["ca_si_B"]


# --------------------------------------------------------------------------- #
# 5. Sortie XLSX.
# --------------------------------------------------------------------------- #
os.makedirs(OUT_DIR, exist_ok=True)
wb = Workbook()
TITRE = Font(bold=True, color="FFFFFF")
FOND = PatternFill("solid", fgColor="1F3864")
GRAS = Font(bold=True)
EURO = '#,##0 "€"'
NB3 = '#,##0.000'
PCT = '0.0 %'


def entete(ws, cols, largeurs):
    ws.append(cols)
    for c in range(1, len(cols) + 1):
        cell = ws.cell(row=ws.max_row, column=c)
        cell.font = TITRE
        cell.fill = FOND
        cell.alignment = Alignment(wrap_text=True, vertical="center")
    for c, w in enumerate(largeurs, start=1):
        ws.column_dimensions[get_column_letter(c)].width = w
    ws.freeze_panes = "A2"


def fmt(ws, colonnes, code, depuis=2):
    for r in range(depuis, ws.max_row + 1):
        for c in colonnes:
            ws.cell(row=r, column=c).number_format = code


def gras_ligne(ws):
    for c in range(1, ws.max_column + 1):
        ws.cell(row=ws.max_row, column=c).font = GRAS


# ---- 1. CA reellement enregistre en caisse --------------------------------- #
ws = wb.active
ws.title = "1 CA reel en caisse"
entete(ws, ["Exercice", "CA liquides reel TTC (annexe D)", "dont alcool TVA 20 %",
            "CA cuisine reel TTC (annexe D)", "Rapport pour 1 € de CA liquide "
            "(calcul du service, bas de l'annexe D)", "Coefficient applique par le "
            "service (proposition p. 52)", "CA total enregistre (annexe D)",
            "Controle annexe C : total des lignes de tickets",
            "Ecart annexe C / annexe D", "Nb de lignes de tickets (annexe C)"],
       [13, 18, 16, 18, 22, 20, 18, 20, 15, 16])
tl = ts = tc = 0.0
for lib, _ in EXOS:
    s, d, c = SERVICE[lib], D[lib]["tot"], C[lib]
    somme_C = sum(c["agg"].values())
    ws.append([lib, s["liq_reel"], s["alcool_reel"], s["sol_reel"], s["rapport_D"],
               s["coef"], d["GENERAL"], somme_C, somme_C - d["GENERAL"], c["lignes"]])
    tl += s["liq_reel"]
    ts += s["sol_reel"]
    tc += d["GENERAL"]
ws.append(["TOTAL 3 ans", tl, sum(SERVICE[l]["alcool_reel"] for l, _ in EXOS), ts,
           ts / tl, "", tc, "", "", ""])
gras_ligne(ws)
fmt(ws, [2, 3, 4, 7, 8, 9], EURO)
fmt(ws, [5, 6], NB3)

# ---- 2. Ce que le service reconstitue et la part qui vient de la cuisine ---- #
ws = wb.create_sheet("2 Part de l'extrapolation")
entete(ws, ["Exercice", "CA liquides reconstitue (apres abattement)",
            "Coefficient", "CA cuisine extrapole", "Total reconstitue", "CA declare",
            "Rehaussement", "Cuisine reellement encaissee (annexe D)",
            "Cuisine extrapolee en trop", "Part du rehaussement provenant de la cuisine",
            "Gonflement du CA liquides", "Levier sur le total (1 + coefficient)"],
       [13, 20, 11, 16, 16, 14, 15, 18, 18, 18, 15, 18])
for lib, _ in EXOS:
    s = SERVICE[lib]
    ws.append([lib, s["liq_recon"], s["coef"], s["sol_recon"], s["total_recon"],
               s["declare"], s["discordance"], s["sol_reel"], s["cuisine_fantome"],
               s["part_cuisine"], s["gonflement"] - 1, s["levier"]])
T = {k: sum(SERVICE[l][k] for l, _ in EXOS)
     for k in ("liq_recon", "sol_recon", "total_recon", "declare", "discordance",
               "sol_reel", "cuisine_fantome")}
ws.append(["TOTAL 3 ans", T["liq_recon"], "", T["sol_recon"], T["total_recon"],
           T["declare"], T["discordance"], T["sol_reel"], T["cuisine_fantome"],
           T["cuisine_fantome"] / T["discordance"], "", ""])
gras_ligne(ws)
fmt(ws, [2, 4, 5, 6, 7, 8, 9], EURO)
fmt(ws, [3, 12], NB3)
fmt(ws, [10, 11], PCT)

ws.append([])
ws.append(["Bras de levier : effet sur le rehaussement total de 1 000 € de CA "
           "liquides surevalues"])
gras_ligne(ws)
ws.append(["Exercice", "CA liquides surevalue", "Effet sur le CA cuisine extrapole",
           "Effet sur le total reconstitue"])
gras_ligne(ws)
for lib, _ in EXOS:
    s = SERVICE[lib]
    ws.append([lib, 1000, 1000 * s["coef"], 1000 * s["levier"]])
    for c in (2, 3, 4):
        ws.cell(row=ws.max_row, column=c).number_format = EURO

# ---- 3. Coefficient sur achat revendu et les deux corrections -------------- #
ws = wb.create_sheet("3 Coefficient revendu")
entete(ws, ["Exercice", "Achats d'alcool (cout, repartition par exercice)",
            "Part effectivement revendue au verre et en cocktails",
            "Cout de l'alcool revendu", "CA alcool encaisse (annexe D, TVA 20 %)",
            "Coefficient sur achat revendu", "Coefficient sur la totalite des achats"],
       [13, 22, 20, 18, 20, 18, 20])
for lib, _ in EXOS:
    s = SERVICE[lib]
    ws.append([lib, s["cout_alcool"], PART_REVENDUE, s["cout_revendu"],
               s["alcool_reel"], s["coef_revendu"], s["alcool_reel"] / s["cout_alcool"]])
ws.append(["GLOBALISE 3 ans", ACHAT_COUT, PART_REVENDUE, COUT_REVENDU, CA_ALCOOL,
           COEF_REVENDU, COEF_ACHATS_TOTAUX])
gras_ligne(ws)
fmt(ws, [2, 4, 5], EURO)
fmt(ws, [3], PCT)
fmt(ws, [6, 7], NB3)
ws.append([])
ws.append(["Le volume d'alcool non revendu (cascade de 10 622 L) n'est etabli que "
           "de facon globale sur les trois exercices : la ventilation par exercice "
           "ci-dessus est une repartition au prorata des achats factures, non une "
           "mesure. Le coefficient de 3,85 est, par construction, un chiffre "
           "triennal."])

ws.append([])
ws.append(["Les deux facons d'appliquer un taux de perte de 15 % au coefficient de "
           "3,85 (reponse du 04/09/2026, p. 59 et p. 93)"])
gras_ligne(ws)
ws.append(["Methode", "Ce sur quoi porte l'abattement", "Cout retenu au denominateur",
           "CA retenu au numerateur", "Coefficient obtenu"])
gras_ligne(ws)
ws.append(["A - calcul du service : 3,85 x (1-0,15)",
           "sur le RESULTAT : le denominateur ne bouge pas, ce qui revient a "
           "amputer de 15 % le chiffre d'affaires encaisse",
           A_COUT, A_CA, A_COEF])
ws.append(["B - correction de la matiere",
           "sur le DENOMINATEUR : si 15 % seulement des achats ne sont pas revendus, "
           "le cout des achats revendus passe de 61,8 % a 85 % des achats ; le CA "
           "encaisse est inchange",
           B_COUT, B_CA, B_COEF])
ws.append(["Ecart entre les deux methodes", "", B_COUT - A_COUT, B_CA - A_CA,
           B_COEF - A_COEF])
gras_ligne(ws)
for r in range(ws.max_row - 2, ws.max_row + 1):
    for c in (3, 4):
        ws.cell(row=r, column=c).number_format = EURO
    ws.cell(row=r, column=5).number_format = NB3

# ---- 4. Confrontation aux coefficients reconstitues ------------------------ #
ws = wb.create_sheet("4 Confrontation")
entete(ws, ["Exercice", "Cout des matieres (proposition p. 34-35)",
            "CA reconstitue par le service", "Coefficient reconstitue",
            "Repere methode A (3,2725)", "CA correspondant au repere A",
            "Exces du CA reconstitue sur le repere A", "Repere methode B",
            "CA correspondant au repere B", "Exces du CA reconstitue sur le repere B"],
       [13, 20, 18, 16, 15, 18, 20, 15, 18, 20])
for lib, _ in EXOS:
    s = SERVICE[lib]
    ws.append([lib, s["matieres"], s["total_recon"], s["coef_recon"], A_COEF,
               s["ca_si_A"], s["exces_A"], B_COEF, s["ca_si_B"], s["exces_B"]])
ws.append(["TOTAL 3 ans", sum(SERVICE[l]["matieres"] for l, _ in EXOS),
           T["total_recon"], "", A_COEF,
           sum(SERVICE[l]["ca_si_A"] for l, _ in EXOS),
           sum(SERVICE[l]["exces_A"] for l, _ in EXOS), B_COEF,
           sum(SERVICE[l]["ca_si_B"] for l, _ in EXOS),
           sum(SERVICE[l]["exces_B"] for l, _ in EXOS)])
gras_ligne(ws)
fmt(ws, [2, 3, 6, 7, 9, 10], EURO)
fmt(ws, [4, 5, 8], NB3)

# ---- 5. Sources ------------------------------------------------------------ #
ws = wb.create_sheet("5 Sources")
entete(ws, ["Donnee", "Source exacte"], [46, 100])
for l in [
    ["CA liquides et CA cuisine reels", "ANNEXE-D1/D2/D3, blocs LIQUIDE TVA 10 %, "
     "LIQUIDE TVA 20 %, SOLIDE TVA 10 % et lignes de total en bas de fichier"],
    ["Rapport pour 1 € de CA liquide", "ANNEXE-D1/D2/D3, derniere ligne "
     "« RAPPORT POUR 1 € DE CA LIQUIDE = ... C-A SOLIDE » (calcul du service)"],
    ["Controle ligne a ligne", "ANNEXE-C1/C2/C3, colonne 17 Tot_rem Ttc, agregee par "
     "reference produit et classee selon les blocs des annexes D"],
    ["CA liquides reconstitue, coefficients 2,94 / 3,02 / 3,10, totaux reconstitues",
     "Proposition de rectifications p. 52, tableau reproduit p. 90 de la reponse du 04/09/2026"],
    ["Cout des matieres et coefficients reconstitues 3,40 / 3,14 / 3,05",
     "Proposition de rectifications p. 34-35, tableau reproduit p. 56 de la reponse du 04/09/2026"],
    ["Coefficient sur achat revendu 3,85 et taux de perte de 15 %",
     "Reponse du 04/09/2026, p. 59, repris p. 93"],
    ["Achats d'alcool 10 622 L / 107 924 € et cascade des volumes",
     "src/data/boissonsPageData.json (scripts/rendu-final-*.py), factures fournisseur"],
    ["Repartition des achats d'alcool par exercice",
     "src/data/calculsBoissons/achatsBoissonsParPeriode.json (factures FCBS, "
     "categories biere, vin/cidre, spiritueux/liqueur)"],
]:
    ws.append(l)
    ws.cell(row=ws.max_row, column=2).alignment = Alignment(wrap_text=True, vertical="top")

wb.save(OUT)

# --------------------------------------------------------------------------- #
print("Ecrit :", OUT)
for lib, _ in EXOS:
    s = SERVICE[lib]
    print("%s  liq reel %9.2f  cuisine reelle %9.2f  rapport D %.4f  coef service %.2f"
          % (lib, s["liq_reel"], s["sol_reel"], s["rapport_D"], s["coef"]))
    print("      controle annexe C : %.2f  vs annexe D general %.2f  (ecart %.2f)"
          % (sum(C[lib]["agg"].values()), D[lib]["tot"]["GENERAL"],
             sum(C[lib]["agg"].values()) - D[lib]["tot"]["GENERAL"]))
    print("      cuisine extrapolee %d  fantome %d  part du rehaussement %.1f %%"
          % (s["sol_recon"], s["cuisine_fantome"], s["part_cuisine"] * 100))
    print("      coef sur achat revendu %.3f" % s["coef_revendu"])
print("Cuisine reelle 3 ans : %.0f | extrapolee : %.0f | fantome : %.0f (%.1f %% du rehaussement %.0f)"
      % (T["sol_reel"], T["sol_recon"], T["cuisine_fantome"],
         T["cuisine_fantome"] / T["discordance"] * 100, T["discordance"]))
print("Coefficient sur achat revendu globalise : %.4f" % COEF_REVENDU)
print("Coefficient sur la totalite des achats d'alcool : %.4f" % COEF_ACHATS_TOTAUX)
print("Methode A (service) : %.4f   Methode B (matiere) : %.4f   ecart %.4f"
      % (A_COEF, B_COEF, A_COEF - B_COEF))
for lib, _ in EXOS:
    s = SERVICE[lib]
    print("  %s exces/repere A %+9.0f €   exces/repere B %+9.0f €"
          % (lib, s["exces_A"], s["exces_B"]))
print("Exces sur repere A : %.0f €   sur repere B : %.0f €"
      % (sum(SERVICE[l]["exces_A"] for l, _ in EXOS),
         sum(SERVICE[l]["exces_B"] for l, _ in EXOS)))
