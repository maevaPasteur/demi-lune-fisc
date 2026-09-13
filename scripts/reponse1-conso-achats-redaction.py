#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reponse1-conso-achats-redaction.py

Reconstruit la REFUTATION (chapitres 2 et 3) de la page
src/data/reponse1/consommation-superieure-achats.json, partie I de la reponse
du service du 04/09/2026 (p. 48 a 53).

Le chapitre 1 « Ce que soutient l'administration » (transcription fidele du
courrier, sections 0 a 32) est conserve tel quel : le script ne touche qu'a ce
qui suit.

Les chiffres sont repris des deux pieces reproductibles de la page :
  - scripts/reponse1-conso-achats-controles.py     -> R1-conso-achats-controles.xlsx
  - scripts/reponse1-conso-achats-encadrements.py  -> R1-conso-achats-encadrements.xlsx
et recalcules ici a partir des memes sources, de sorte qu'aucun nombre du texte
ne soit saisi a la main.

Apres ce script, relancer scripts/reponse1-calvados-encadrement.py, qui reinsere
son bloc « encadrement de la dose » apres la note d'ancrage.
"""
import os
import json
import subprocess
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
CIBLE = os.path.join(ROOT, "src/data/reponse1/consommation-superieure-achats.json")
BDJ = os.path.join(ROOT, "src/data/boissonsPageData.json")
FIN_CHAPITRE_1 = 33          # les 33 premieres sections sont le chapitre 1

# ---------------------------------------------------------------------------
# Rechargement des chiffres depuis les sources (aucun nombre saisi a la main)
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.join(ROOT, "scripts"))

DOC = json.load(open(CIBLE, encoding="utf-8"))
SECTIONS = DOC["sections"]
BD = json.load(open(BDJ, encoding="utf-8"))
ROWS = BD["disparuParBoisson"]

# --- correction du double comptage de la biere -----------------------------
# boissonsPageData.json porte, pour le fut Affligem, une consommation de
# 1 501,0 L : la contenance entiere du panache, du Monaco et du Picon biere y
# est comptee en plus de leur recette, alors que l'alcool de ces quatre
# articles est deja porte par les cocktails. La contenance en double, etablie
# par scripts/reponse1-cascade-valeurs.py, est retiree ici de la consommation
# du fut. Sans cette correction, le bilan matiere par famille de cette page
# contredit la cascade des 10 622 L. La source (boissonsPageData.json) n'est
# pas modifiee : elle alimente aussi l'onglet /analyses/.
_CASC = os.path.join(ROOT, "src/data/reponse1Calculs/cascade-10622.json")
if not os.path.exists(_CASC):
    raise SystemExit("Lancer d'abord : python3 scripts/reponse1-cascade-valeurs.py")
DOUBLE_BIERE_L = json.load(open(_CASC, encoding="utf-8"))["doubles_comptages"]["biere"]["litres"]
for _r in ROWS:
    if _r["nom"] == "Fût Affligem":
        _r["conso_l"] = round(_r["conso_l"] - DOUBLE_BIERE_L, 2)
        break
else:
    raise SystemExit("Fût Affligem introuvable dans disparuParBoisson")
EXOS = ["31/03/2023", "31/03/2024", "31/03/2025"]


def num(s):
    s = str(s).replace(" ", " ").replace("\xa0", " ").strip()
    if s == "":
        return None
    s = s.replace("%", "").replace(" ", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def N(v, dec=0):
    return f"{v:,.{dec}f}".replace(",", " ").replace(".", ",")


def trouver(fragment):
    for s in SECTIONS:
        if s.get("kind") == "tableau" and fragment in s.get("titre", ""):
            return s
    raise SystemExit("tableau introuvable : " + fragment)


TABLEAUX = [
    ("Vins (p. 48 et 52)", "Vins : le tableau opposé", "cl"),
    ("Articles vendus à la dose (p. 51)", "Articles vendus à la dose", "cl"),
    ("Articles Complexes (p. 52)", "« Articles Complexes »", "cl"),
    ("Articles vendus à l’unité (p. 53)", "Articles vendus à l’unité", "unité"),
]

# --- 1. sens des ecarts sur les quatre tableaux -----------------------------
n_cellules = n_pos = n_neg = n_nul = 0
n_lignes = 0
dispo_u = {"cl": 0.0, "unité": 0.0, "g": 0.0}
neg_u = {"cl": 0.0, "unité": 0.0, "g": 0.0}
neg_n = {"cl": 0, "unité": 0, "g": 0}
negatives = []
par_tableau = {t[0]: {"cellules": 0, "neg": 0, "lignes": 0} for t in TABLEAUX}
for nom, frag, unite in TABLEAUX:
    tab = trouver(frag)
    n_lignes += len(tab["lignes"])
    par_tableau[nom]["lignes"] = len(tab["lignes"])
    for ligne in tab["lignes"]:
        lib = ligne[0]["v"]
        u = "g" if lib.strip().upper().startswith("CAFE") else unite
        for k, exo in enumerate(EXOS):
            d = num(ligne[1 + 3 * k]["v"])
            v = num(ligne[2 + 3 * k]["v"])
            if d is None and v is None:
                continue
            d, v = d or 0.0, v or 0.0
            n_cellules += 1
            par_tableau[nom]["cellules"] += 1
            dispo_u[u] += d
            if v > d:
                n_neg += 1
                neg_u[u] += v - d
                neg_n[u] += 1
                par_tableau[nom]["neg"] += 1
                negatives.append((nom, lib, exo, d, v, v - d, u))
            elif d > v:
                n_pos += 1
            else:
                n_nul += 1

# --- 2. controle arithmetique des pourcentages ------------------------------
n_pct = n_conforme = n_vide = n_anomalie = 0
for nom, frag, _u in TABLEAUX:
    tab = trouver(frag)
    for ligne in tab["lignes"]:
        for k in range(3):
            d = num(ligne[1 + 3 * k]["v"])
            v = num(ligne[2 + 3 * k]["v"])
            p = num(ligne[3 + 3 * k]["v"])
            if p is None:
                continue
            n_pct += 1
            if d is None or v is None:
                n_anomalie += 1
            elif d == 0 and not v:
                if p:
                    n_anomalie += 1
                else:
                    n_vide += 1
            elif d == 0:
                n_anomalie += 1
            elif abs(round((d - v) / d * 100, 2) - p) <= 0.6:
                n_conforme += 1
            else:
                n_anomalie += 1

# --- 3. bilan matiere par famille ------------------------------------------
FAMILLES = {
    "vin": "Vins tranquilles", "vin_rouge": "Vins tranquilles",
    "vin_blanc": "Vins tranquilles", "vin_rose": "Vins tranquilles",
    "petillant": "Crémant et champagne", "vin_de_liqueur": "Vin de liqueur (Macvin)",
    "biere": "Bières", "cidre": "Cidres", "aperitif": "Apéritifs",
    "liqueur": "Liqueurs", "eau_de_vie": "Eaux-de-vie et digestifs",
    "spiritueux": "Spiritueux",
}
ORDRE = ["Vins tranquilles", "Bières", "Vin de liqueur (Macvin)", "Crémant et champagne",
         "Cidres", "Liqueurs", "Apéritifs", "Spiritueux", "Eaux-de-vie et digestifs"]
agg = {}
for r in ROWS:
    f = FAMILLES.get(r.get("categorie"), "Autres")
    a = agg.setdefault(f, {"n": 0, "achat": 0.0, "conso": 0.0, "stock": 0.0})
    a["n"] += 1
    a["achat"] += r["achat_l"]
    a["conso"] += r["conso_l"]
    a["stock"] += r["stock_l"]
T_ACHAT = sum(a["achat"] for a in agg.values())
T_CONSO = sum(a["conso"] for a in agg.values())
T_STOCK = sum(a["stock"] for a in agg.values())
T_NET = T_ACHAT - T_CONSO - T_STOCK
NB_PRODUITS = len(ROWS)

# --- 4. eaux-de-vie : encadrement de la dose --------------------------------
EDV = [r for r in ROWS if r.get("categorie") == "eau_de_vie"]
CAL = next(r for r in EDV if r["nom"] == "Calvados")
ACH_FAM = sum(r["achat_l"] for r in EDV)
CONSO_FAM = sum(r["conso_l"] for r in EDV)
STOCK_FAM = sum(r["stock_l"] for r in EDV)
BILAN_FAM = ACH_FAM - CONSO_FAM - STOCK_FAM
VERRE_L, DOSE_SERVICE = 1.44, 4.0
CUISINE_L_4CL = CAL["conso_l"] - VERRE_L
conso_calva = lambda d: VERRE_L + CUISINE_L_4CL * d / DOSE_SERVICE
bilan_fam = lambda d: ACH_FAM - (CONSO_FAM - CAL["conso_l"] + conso_calva(d)) - STOCK_FAM
DOSE_EQ_FAM = ((ACH_FAM - STOCK_FAM - (CONSO_FAM - CAL["conso_l"]) - VERRE_L)
               / CUISINE_L_4CL * DOSE_SERVICE)
ACH_HORS = sum(r["achat_l"] for r in EDV if r["nom"] != "Calvados")
CONSO_HORS = sum(r["conso_l"] for r in EDV if r["nom"] != "Calvados")
STOCK_HORS = sum(r["stock_l"] for r in EDV if r["nom"] != "Calvados")
BILAN_HORS = ACH_HORS - CONSO_HORS - STOCK_HORS

# --- 4 bis. achats factures non rattaches : notre bilan est un plancher ------
import datetime
FACT = json.load(open(os.path.join(ROOT, "src/data/factures-fournisseur.json"), encoding="utf-8"))
D0, D1 = datetime.date(2022, 4, 1), datetime.date(2025, 3, 31)
BILAN = {r["nom"]: r for r in ROWS}


def bouteilles(cle):
    q = 0.0
    for f in FACT["factures"]:
        try:
            da = datetime.datetime.strptime(f.get("dateFacture") or "", "%d/%m/%Y").date()
        except ValueError:
            continue
        if not (D0 <= da <= D1):
            continue
        for l in f["lignes"]:
            des = (l.get("designation") or "").upper()
            if cle in des and "DECONSIGNE" not in des and "CARAMBAR" not in des:
                q += l.get("quantite") or 0
    return q


FACTURE = {
    "Chablis": bouteilles("CHABLIS") * 0.75,
    "Gewurztraminer": bouteilles("GEWURZ") * 0.75,
    "Arbois Béthanie": bouteilles("BETHANIE 75") * 0.75 + bouteilles("BETHANIE 37,5") * 0.375,
}
MANQUE = {k: v - BILAN[k]["achat_l"] for k, v in FACTURE.items()}
TOT_MANQUE = sum(MANQUE.values())
NB_FACTURES_FCBS = FACT["nbFactures"]

# --- 4 ter. annexe n 5 : les 78 factures Intermarche -------------------------
import re

# --- NEUTRALISE le 13/09/2026 ------------------------------------------------
# La page consommation-superieure-achats a ete entierement reecrite : le Calvados
# y boucle desormais sans aucune dose (73 L entres, 73 L sortis, achats et stocks
# identiques aux annexes n. 1 et n. 6 du service), le bloc des cidres est refute
# par le decalage d'un rang de la colonne « Quantites Vendues », et le trou de la
# colonne « Achats Inter-M » est etabli comme structurel sur 152 lignes.
#
# Ce script regenererait la page dans son etat anterieur et detruirait ces
# demonstrations. Pour le relancer sciemment, exporter
# REPONSE1_CONSO_ACHATS_FORCE=1, et relire d'abord la page.
import os as _os
if not _os.environ.get("REPONSE1_CONSO_ACHATS_FORCE"):
    raise SystemExit(
        "reponse1-conso-achats-redaction.py est neutralise : il reecrirait la "
        "page dans son etat anterieur. Voir le commentaire en tete de fichier."
    )

OCR = os.path.join(ROOT, "public/documents/rapports-des-finances-publiques/synthese/"
                          "_ocr-brut/Proposition_3_Annexes_Boissons.txt")
_ok = []
INTER_N = 0
INTER_HT = 0.0
for ligne in open(OCR, encoding="utf-8", errors="replace").read().split("\n"):
    if "INTERMARCHE" not in ligne.upper():
        continue
    m = re.findall(r"(\d{1,3}(?:[\s.]\d{3})*,\d{2})\s*€", ligne)
    v = [float(x.replace(" ", "").replace(".", "").replace(",", ".")) for x in m]
    if not v:
        continue
    INTER_N += 1
    INTER_HT += v[0]
    if len(v) >= 3 and abs(v[0] + v[1] - v[2]) < 0.05:
        _ok.append((v[0], v[1]))
TAUX_MOY = sum(b for a, b in _ok) / sum(a for a, b in _ok) * 100
TAUX_MAX = max(b / a * 100 for a, b in _ok)
NB_OK = len(_ok)

# valeur du grief Calvados, au prix des factures FCBS de la periode
CALVA_HT = 0.0
CALVA_BT = 0.0
for f in FACT["factures"]:
    try:
        da = datetime.datetime.strptime(f.get("dateFacture") or "", "%d/%m/%Y").date()
    except ValueError:
        continue
    if not (D0 <= da <= D1):
        continue
    for l in f["lignes"]:
        des = (l.get("designation") or "").upper()
        if "CALVADOS BEAUJOUR" in des and "DECONSIGNE" not in des:
            CALVA_BT += l.get("quantite") or 0
            CALVA_HT += l.get("montantHT") or 0
PRIX_L = CALVA_HT / CALVA_BT                 # bouteilles de 100 cl
GRIEF_CL = 2017.0
GRIEF_EUR = GRIEF_CL / 100.0 * PRIX_L

# --- 5. les postes que le service dit qu'il aurait fallu corriger (p. 50) ----
T_DOSE = trouver("Articles vendus à la dose")
T_CPLX = trouver("« Articles Complexes »")
T_VINS = trouver("Vins : le tableau opposé")


def somme_lignes(tab, libelles):
    d = v = 0.0
    for ligne in tab["lignes"]:
        if ligne[0]["v"] in libelles:
            for k in range(3):
                d += num(ligne[1 + 3 * k]["v"]) or 0.0
                v += num(ligne[2 + 3 * k]["v"]) or 0.0
    return d, v


POSTES = [
    ("Le vin jaune", T_DOSE, ["Vin jaune"], "ligne « Vin jaune », p. 51"),
    ("Le vin des sauces et le vin de cuisine", T_VINS, ["VINS EN BIB"],
     "ligne « VINS EN BIB », p. 48 et 52"),
    ("Le vin de tous les cocktails, à 4 cl", T_CPLX,
     ["CREMANT", "MACVIN", "SOHO", "VODKA", "PASSOA", "TEQUILA", "PICON",
      "LIMONADE", "JUS DE FRUIT"], "tableau « Articles Complexes », p. 52"),
    ("Les sirops, à 4 cl", T_DOSE, ["SIROP A L’EAU"], "ligne « SIROP A L’EAU », p. 51"),
]
postes = []
tot_d = tot_v = 0.0
for nom, tab, libs, src in POSTES:
    d, v = somme_lignes(tab, libs)
    tot_d += d
    tot_v += v
    postes.append((nom, src, d, v, d - v, (d - v) / d * 100, d - v / 2.0,
                   (d - v / 2.0) / d * 100))

print("== chiffres recalcules ==")
print(f"cellules {n_cellules} ({n_lignes} lignes) : {n_pos} positives, {n_nul} nulles, "
      f"{n_neg} negatives")
print(f"  cl : {N(neg_u['cl'])} sur {N(dispo_u['cl'])} ; unites : {N(neg_u['unité'])} "
      f"sur {N(dispo_u['unité'])}")
print(f"pourcentages {n_pct} : {n_conforme} conformes, {n_vide} vides, {n_anomalie} anomalies")
print(f"bilan matiere {N(T_ACHAT,1)} / {N(T_CONSO,1)} / {N(T_STOCK,1)} = {N(T_NET,1)} L "
      f"({NB_PRODUITS} produits)")
print(f"eaux-de-vie {N(ACH_FAM,1)} / {N(CONSO_FAM,1)} / {N(STOCK_FAM,1)} = {N(BILAN_FAM,1)} L ; "
      f"dose d'equilibre {N(DOSE_EQ_FAM,2)} cl ; hors Calvados {N(BILAN_HORS,1)} L")
for p in postes:
    print("  poste", p[0], N(p[2]), N(p[3]), N(p[4]), N(p[5], 1) + " %", N(p[6]), N(p[7], 1) + " %")
print("  total postes", N(tot_d), N(tot_v), N(tot_d - tot_v),
      N((tot_d - tot_v) / tot_d * 100, 1) + " %")
for n in negatives:
    print("  neg", n)


# ===========================================================================
# Redaction
# ===========================================================================
cg = lambda v, **k: dict(v=v, **k)
cd = lambda v, **k: dict(v=v, align="right", **k)

CONCEDE_CL = 12950.0
GRANINI_U = 964.0
LANCON_U = 12.0
RESTE_CL = neg_u["cl"] - CONCEDE_CL
RESTE_U = neg_u["unité"] - GRANINI_U - LANCON_U


def tableau_douze():
    lignes = []
    for nom, lib, exo, d, v, ec, u in negatives:
        lignes.append([
            cg(nom.split(" (")[0]), cg(lib), cd(exo),
            cd(N(d)), cd(N(v)), cd(N(ec) + (" cl" if u == "cl" else " u.")),
            cg(EXPLICATIONS[lib]),
        ])
    return {
        "kind": "tableau",
        "titre": "Les douze cellules, sur 226, où les quantités vendues dépassent les quantités "
                 "disponibles",
        "minWidth": 1080,
        "colonnes": [{"label": "Tableau du service"}, {"label": "Désignation"},
                     {"label": "Exercice clos", "align": "right"},
                     {"label": "Disponibles", "align": "right"},
                     {"label": "Vendues", "align": "right"},
                     {"label": "Dépassement", "align": "right"},
                     {"label": "Ce que la cellule recouvre"}],
        "lignes": lignes,
    }


EXPLICATIONS = {
    "H. COTES DE NUITS": "La ligne que le service admet p. 48 qu’il aurait dû rassembler avec "
                         "les deux autres Beaune",
    "BORDEAUX": "Bouteilles achetées sur l’exercice précédent : 2 325 cl disponibles en 2024 "
                "pour 525 cl vendus",
    "Martini Blanc": "Acheté sous le libellé « MARTINI BIANCO 100 CL » : 13,0 L achetés pour "
                     "12,6 L consommés sur trois exercices",
    "Vittel Evian 50 cl": "Deux formats sous deux libellés, le 100 cl restant excédentaire les "
                          "trois exercices",
    "Granini Raisin 25 cl": "Le service porte les ventes de tout le bloc Granini sur cette seule "
                            "ligne : le bloc est excédentaire (525, 406 et 414 disponibles pour "
                            "417, 360 et 342 vendues)",
    "Cidre Sassy 33 cl": "Famille des cidres excédentaire de 201,7 L sur trois exercices",
    "Cidre Brut 75 cl": "Famille des cidres excédentaire de 201,7 L sur trois exercices",
    "Champagne Lancon 75 cl": "Le service porte les ventes de tout le bloc Champagne sur cette "
                              "seule ligne : le bloc est excédentaire (30, 13 et 20 disponibles "
                              "pour 9, 7 et 2 vendues)",
}


def tableau_postes():
    lignes = []
    for nom, src, d, v, ec, pct, ec2, pct2 in postes:
        lignes.append([cg(nom), cg(src), cd(N(d)), cd(N(v)),
                       cd("+" + N(ec), badge="ok"), cd(N(pct, 1) + " %"),
                       cd("+" + N(ec2), badge="ok"), cd(N(pct2, 1) + " %")])
    lignes.append([cg("Total des postes cités", fw=700), cg(""),
                   cd(N(tot_d), fw=700), cd(N(tot_v), fw=700),
                   cd("+" + N(tot_d - tot_v), fw=700, badge="ok"),
                   cd(N((tot_d - tot_v) / tot_d * 100, 1) + " %", fw=700),
                   cd("+" + N(tot_d - tot_v / 2), fw=700, badge="ok"),
                   cd(N((tot_d - tot_v / 2) / tot_d * 100, 1) + " %", fw=700)])
    return {
        "kind": "tableau",
        "titre": "Les postes que le service dit qu’il aurait fallu corriger aussi (p. 50), "
                 "lus dans ses propres tableaux (centilitres, trois exercices)",
        "minWidth": 1080,
        "colonnes": [{"label": "Poste cité p. 50"}, {"label": "Tableau du service"},
                     {"label": "Disponibles", "align": "right"},
                     {"label": "Vendues", "align": "right"},
                     {"label": "Excédent d’achat", "align": "right"},
                     {"label": "En % du disponible", "align": "right"},
                     {"label": "Excédent si la dose était divisée par deux", "align": "right"},
                     {"label": "En % du disponible", "align": "right"}],
        "lignes": lignes,
    }


def tableau_edv():
    lignes = []
    for dose, lib, badge in [
            (4.0, "4 cl : la dose retenue par le service (p. 49)", "ko"),
            (3.0, "3 cl : borne haute de l’encadrement", "ko"),
            (round(DOSE_EQ_FAM, 2), "Dose d’équilibre de la famille (calculée)", None),
            (2.0, "2 cl : borne basse de l’encadrement", "ok")]:
        b = bilan_fam(dose)
        conso = CONSO_FAM - CAL["conso_l"] + conso_calva(dose)
        lignes.append([
            cg(lib), cd(N(dose, 2) + " cl"), cd(N(conso_calva(dose), 1) + " L"),
            cd(N(conso, 1) + " L"), cd(N(ACH_FAM, 1) + " L"),
            cd(("+" if b >= 0 else "") + N(b, 1) + " L", **({"badge": badge} if badge else {})),
        ])
    return {
        "kind": "tableau",
        "titre": "Eaux-de-vie et digestifs : le bilan de la famille change de signe entre 2 et 3 cl "
                 "(achats facturés, consommation de caisse et de cuisine, inventaire)",
        "minWidth": 860,
        "colonnes": [{"label": "Hypothèse de dose en cuisine"},
                     {"label": "Dose", "align": "right"},
                     {"label": "Calvados consommé", "align": "right"},
                     {"label": "Consommation de la famille", "align": "right"},
                     {"label": "Achats facturés", "align": "right"},
                     {"label": "Bilan de la famille", "align": "right"}],
        "lignes": lignes,
    }


def tableau_familles():
    lignes = []
    for f in ORDRE:
        a = agg[f]
        net = a["achat"] - a["conso"] - a["stock"]
        lignes.append([cg(f), cd(N(a["achat"], 1) + " L"), cd(N(a["conso"], 1) + " L"),
                       cd(N(a["stock"], 1) + " L"),
                       cd(("+" if net >= 0 else "") + N(net, 1) + " L",
                          badge="ok" if net >= 0 else "ko"),
                       cd(("+" if net >= 0 else "") + N(net / a["achat"] * 100, 1) + " %")])
    lignes.append([cg(f"Total, {NB_PRODUITS} produits", fw=700),
                   cd(N(T_ACHAT, 1) + " L", fw=700), cd(N(T_CONSO, 1) + " L", fw=700),
                   cd(N(T_STOCK, 1) + " L", fw=700),
                   cd("+" + N(T_NET, 1) + " L", fw=700, badge="ok"),
                   cd("+" + N(T_NET / T_ACHAT * 100, 1) + " %", fw=700)])
    return {
        "kind": "tableau",
        "titre": "Bilan matière par famille : achats (factures), consommation (caisse et cuisine), "
                 "inventaire",
        "minWidth": 860,
        "colonnes": [{"label": "Famille"}, {"label": "Achats factures", "align": "right"},
                     {"label": "Conso caisse et cuisine", "align": "right"},
                     {"label": "Variation d’inventaire", "align": "right"},
                     {"label": "Bilan net", "align": "right"},
                     {"label": "Bilan / achats", "align": "right"}],
        "lignes": lignes,
    }


TAB_BEAUNE = trouver("Haute Côte de Beaune")
TAB_PCT = trouver("Contrôle arithmétique")
TAB_CALVA_USAGE = trouver("dose servie et dose en cuisine")
NOTE_ANCRE = next(x for x in SECTIONS if x.get("kind") == "note"
                  and "additions partagées" in x.get("texte", ""))

P = lambda t: {"kind": "paragraphe", "texte": t}

COLONNES_ANNEXE_5 = (
    "1664 33 cl, 1664 25 cl, 1er Prix Crème cassis 100 cl, IDS Crème cassis 100 cl, "
    "Vedrenne Crème cassis 100 cl, Perrault Dabot 70 cl, H Guyot Crème cassis 100 cl, "
    "Perrier 33 cl, Volvic Juicy 100 cl, Volvic Zest Citron 100 cl, Volvic Citron 33 cl, "
    "Transition Pur Jus 100 cl, Sirop Menthe 50 cl, Sirop Pulco 70 cl, IGP Terre Mid RS Grai, "
    "IGPOC Rosé Grenache, IGPOC Cambras Orme Cins, IGPOC Syrah Rosé Exp, "
    "Vieux Pape Rosé 500 cl, Vin Jaune 62,50 cl, Pontarlier 100 cl")


def bloc_intermarche():
    return [
        T("Le « disponible » du service est un plancher : la grille des achats Intermarché "
          "n’a pas de case pour ce produit", "2.4"),
        P("La proposition de rectifications décrit elle-même la source du disponible : "
          "« à partir des factures d’achats des fournisseurs de boissons (**Franche Comté "
          "Boissons Service et Intermarché**), le service a pu établir pour chaque type de "
          "boissons, et chaque facture, les quantités achetées. Ce sont les annexes n° 2, n° 3, "
          "n° 4 et n° 5 qui compilent toutes ces informations. L’annexe n° 6 récapitule les "
          "achats par type de boissons et grâce aux stocks, établit donc les quantités "
          "disponibles ». Le disponible n’est donc pas une mesure : c’est le produit d’une "
          "ventilation, et il ne vaut que ce que valent les colonnes de cette ventilation."),
        P("Les deux fournisseurs n’y sont pas traités de la même façon. Pour Franche-Comté "
          "Boissons Services, la grille est ouverte produit par produit : l’annexe n° 6 aligne "
          "une ligne pour l’absinthe, l’Aperol, le Baileys, le Calvados, le Cognac, le génépi, "
          "le Get 27/31, le Grand Marnier, le marc du Jura, la mirabelle, la poire, le "
          "Pontarlier, la tequila, la vodka et deux whiskies. Pour Intermarché, l’annexe n° 5 "
          "ventile les **" + N(INTER_N) + " factures**, soit **" + N(INTER_HT, 2) + " € HT**, "
          "sur une grille fermée de **21 colonnes** : " + COLONNES_ANNEXE_5 + "."),
        P("Aucune de ces 21 colonnes ne correspond à un Calvados, un whisky, une vodka, un "
          "cognac, un rhum, un Grand Marnier, un Get, un génépi, un Baileys, un marc ou une "
          "eau-de-vie de fruit. **Une bouteille de Calvados achetée dans ce magasin n’a donc "
          "aucune case où être inscrite**, et n’a par construction aucune chance d’apparaître "
          "dans le disponible. La grille n’est pourtant pas fermée aux alcools : elle comporte "
          "quatre colonnes de crème de cassis, deux de bière 1664, cinq de vins, une de vin jaune "
          "et une de Pontarlier, qui est un anis à 45°. Le magasin n’est donc pas, pour cet "
          "établissement, un fournisseur de boissons sans alcool : c’est la grille, et elle "
          "seule, qui s’arrête avant les eaux-de-vie."),
        P("L’effet se lit sur la ligne même du grief. Dans l’annexe n° 6, la ligne « Calvados "
          "Beaujour 100 cl » porte, pour les trois exercices, une colonne **« Achats Inter-M » "
          "vide** : le disponible retenu (31, 22 puis 20 bouteilles) est exactement l’achat "
          "Franche-Comté Boissons Services corrigé du stock (32 + 1 − 2, 22 + 2 − 2, "
          "19 + 2 − 1). Sur toute la partie « alcools » de cette annexe, une trentaine de "
          "lignes, la colonne « Achats Inter-M » n’est renseignée qu’une seule fois, sur la "
          "crème de cassis 100 cl."),
        tableau_intermarche(),
        P("Un second indice, tiré des mêmes factures, va dans le même sens. Sur les **" +
          N(NB_OK) + " factures Intermarché dont les trois montants se recoupent exactement** "
          "(HT + TVA = TTC), le taux moyen de TVA ressort à **" + N(TAUX_MOY, 1) + " %**, et "
          "atteint " + N(TAUX_MAX, 1) + " % sur certaines. Des eaux, des sodas, des jus et des "
          "sirops achetés en magasin relèvent du taux de 5,5 % ; le taux de 20 % est celui des "
          "boissons alcooliques. Un taux moyen de " + N(TAUX_MOY, 1) + " % établit qu’une part "
          "substantielle de ces achats est taxée à 20 %. Nous ne prétendons pas en déduire un "
          "volume. Deux lectures sont possibles, et aucune ne sert la démonstration du service : "
          "ou bien ces factures portent des alcools que sa grille ne pouvait pas recevoir, ou "
          "bien elles portent des articles qui ne sont pas des boissons, et la ventilation "
          "qu’il en tire pour établir un disponible de boissons n’est pas fiable."),
        P("Il faut enfin mesurer l’enjeu. La surconsommation de Calvados que le service retient "
          "sur trois exercices est de **" + N(GRIEF_CL) + " cl, soit " + N(GRIEF_CL / 100, 1) +
          " L**. Au prix des factures de la période (" + N(CALVA_HT, 2) + " € HT pour " +
          N(CALVA_BT) + " bouteilles d’un litre), ces " + N(GRIEF_CL / 100, 1) + " L "
          "représentent **" + N(GRIEF_EUR, 0) + " € HT**, soit " +
          N(GRIEF_EUR / INTER_HT * 100, 1) + " % de ce qui a été dépensé chez Intermarché sur la "
          "période. Vingt bouteilles achetées au supermarché en trois ans, environ sept par an, "
          "effacent le grief en entier."),
        P("La société ne détient pas ces " + N(INTER_N) + " factures et n’est pas en mesure "
          "de les produire ; le mémoire du 10 juillet 2026 ne le pouvait pas davantage. Nous "
          "ne promettons donc pas une production que nous ne maîtrisons pas, et nous n’avons "
          "pas à le faire. **Le service les "
          "détient**, puisqu’il les a lui-même recensées, chiffrées et ventilées dans son "
          "annexe n° 5. C’est donc à lui, qui supporte la charge d’établir le bien-fondé des "
          "rectifications, de dire si la colonne « Achats Inter-M » du Calvados est vide parce "
          "qu’aucun Calvados n’a été acheté dans ce magasin, ou parce que sa grille de "
          "ventilation ne comportait pas de colonne pour ce produit. Tant que cette vérification "
          "n’est pas faite, le disponible qu’il oppose reste un minorant, et un écart calculé à "
          "partir d’un minorant d’achats ne peut pas fonder le rejet d’une comptabilité."),
        {"kind": "alerte", "couleur": "orange",
         "titre": "Une vérification que le service est seul à pouvoir faire",
         "texte": "Les " + N(INTER_N) + " factures Intermarché sont entre les mains du service, "
                  "qui les a ventilées lui-même sur les 21 colonnes de son annexe n° 5. Il lui "
                  "suffit de les rouvrir pour dire si elles comportent des eaux-de-vie. La "
                  "société, qui ne les a pas, ne peut ni le confirmer ni le démentir."},
    ]


def tableau_intermarche():
    return {
        "kind": "tableau",
        "titre": "Calvados : le disponible retenu par le service (annexe n° 6) et l’écart qu’il "
                 "en tire (p. 49)",
        "minWidth": 900,
        "colonnes": [{"label": "Exercice clos"},
                     {"label": "Achats FCBS (bt 100 cl)", "align": "right"},
                     {"label": "Achats Inter-M", "align": "right"},
                     {"label": "Stock initial", "align": "right"},
                     {"label": "Stock final", "align": "right"},
                     {"label": "Disponible retenu", "align": "right"},
                     {"label": "Surconsommation retenue", "align": "right"}],
        "lignes": [
            [cg("31/03/2023"), cd("32"), cd("colonne vide"), cd("1"), cd("2"), cd("31"),
             cd("210 cl")],
            [cg("31/03/2024"), cd("22"), cd("colonne vide"), cd("2"), cd("2"), cd("22"),
             cd("802 cl")],
            [cg("31/03/2025"), cd("19"), cd("colonne vide"), cd("2"), cd("1"), cd("20"),
             cd("1 005 cl")],
            [cg("Total", fw=700), cd("73", fw=700), cd("0", fw=700), cd(""), cd(""),
             cd("73", fw=700), cd("2 017 cl", fw=700)],
        ],
    }
T = lambda t, n=None: ({"kind": "titre", "texte": t, "numero": n} if n
                       else {"kind": "titre", "texte": t})


def refutation():
    s = []
    s.append({"kind": "chapitre", "source": "nous", "numero": 2, "titre": "Notre réponse",
              "sousTitre": "Les quatre tableaux opposés comptent " + N(n_cellules) +
                           " cellules : douze seulement montrent des quantités vendues "
                           "supérieures aux quantités disponibles, et la plus lourde est celle "
                           "que le service concède lui-même."})
    s.append(P("Le reproche central de la partie I est que la réponse du 10 juillet 2026 « ne "
               "porte donc que sur 4 types de boissons » (p. 50). Il est entendu. Nous répondons "
               "ici sur la totalité des articles que le service oppose : les **" + N(n_lignes) +
               " lignes** des quatre tableaux des pages 48, 51, 52 et 53, soit **" +
               N(n_cellules) + " cellules** de comptabilité matière, reprises une à une, plus le "
               "bilan matière complet des " + N(NB_PRODUITS) + " produits achetés sur la période."))

    # --- 2.1 -----------------------------------------------------------------
    s.append(T("Sur les " + N(n_cellules) + " cellules opposées, douze vont dans le sens du "
               "grief", "2.1"))
    s.append(P("La partie I s’intitule « Consommation vendue supérieure aux achats ». Une seule "
               "configuration correspond à cet intitulé : une cellule où les **quantités vendues "
               "dépassent les quantités disponibles**. Les autres disent soit l’inverse, un "
               "produit acheté et non vendu, qui ne peut par construction révéler aucune recette "
               "dissimulée, soit rien du tout."))
    s.append(P("Le décompte est sans ambiguïté. Sur les " + N(n_cellules) + " cellules des quatre "
               "tableaux, **" + N(n_pos) + " montrent des disponibles supérieurs aux vendues**, " +
               N(n_nul) + " sont nulles ou vides, et **" + N(n_neg) + " seulement** montrent des "
               "vendues supérieures aux disponibles. Ces douze cellules représentent " +
               N(neg_u["cl"]) + " cl dans les trois tableaux libellés en centilitres, sur " +
               N(dispo_u["cl"]) + " cl disponibles, et " + N(neg_u["unité"]) + " unités dans le "
               "tableau des articles vendus à l’unité, sur " + N(dispo_u["unité"]) + "."))
    s.append(tableau_douze())
    s.append(P("Ces douze cellules se réduisent encore. **" + N(CONCEDE_CL) + " cl** des " +
               N(neg_u["cl"]) + " cl, soit " +
               N(CONCEDE_CL / neg_u["cl"] * 100, 1) + " %, tiennent à la seule ligne "
               "« H. COTES DE NUITS », celle que le service admet page 48 qu’il aurait dû "
               "rassembler avec les autres Beaune. **" + N(GRANINI_U + LANCON_U) + " unités** des " +
               N(neg_u["unité"]) + ", soit " + N((GRANINI_U + LANCON_U) / neg_u["unité"] * 100, 1) +
               " %, viennent de deux blocs où le service imprime les ventes de tout un groupe sur "
               "une ligne de détail : le bloc Granini et le bloc Champagne sont excédentaires les "
               "trois exercices. Il reste **" + N(RESTE_CL) + " cl** et **" + N(RESTE_U) +
               " unités**, soit " + N(RESTE_CL / dispo_u["cl"] * 100, 2) + " % et " +
               N(RESTE_U / dispo_u["unité"] * 100, 2) + " % des volumes disponibles des mêmes "
               "tableaux, tous rattachés à un libellé voisin ou à un exercice voisin."))
    s.append({"kind": "kpis", "items": [
        {"label": "Cellules opposées", "valeur": N(n_cellules),
         "sub": N(n_lignes) + " lignes d’articles, quatre tableaux, trois exercices",
         "couleur": "blue"},
        {"label": "Cellules où les ventes dépassent les achats", "valeur": N(n_neg),
         "sub": "les seules qui correspondent au titre de la partie I", "highlight": True,
         "couleur": "teal"},
        {"label": "Part imputable à la ligne concédée p. 48", "valeur":
         N(CONCEDE_CL / neg_u["cl"] * 100, 0) + " %",
         "sub": N(CONCEDE_CL) + " cl sur " + N(neg_u["cl"]) + " cl de dépassement", "couleur": "gold"},
        {"label": "Dépassement résiduel", "valeur": N(RESTE_CL / dispo_u["cl"] * 100, 2) + " %",
         "sub": N(RESTE_CL) + " cl sur " + N(dispo_u["cl"]) + " cl disponibles", "couleur": "teal"},
    ]})

    s.append(P("Le tableau de la page 53, celui dont le service souligne que la réponse "
               "« s’abstient de tout commentaire », appelle la même lecture. Ses " +
               N(par_tableau["Articles vendus à l’unité (p. 53)"]["lignes"]) + " lignes sont "
               "des eaux, des sodas, des jus, des bières en bouteille, des cidres et des "
               "champagnes vendus à l’unité. Sur les " +
               N(par_tableau["Articles vendus à l’unité (p. 53)"]["cellules"]) +
               " cellules qu’il contient, " +
               N(par_tableau["Articles vendus à l’unité (p. 53)"]["neg"]) + " seulement "
               "montrent des ventes supérieures aux disponibles, dont cinq par le seul effet des "
               "blocs Granini et Champagne. Toutes les autres constatent des bouteilles achetées "
               "et non vendues, dont le sort est établi dans les parties consacrées à la "
               "**consommation du personnel**, aux **offerts** et aux **pertes**."))

    # --- 2.2 : la concession du service --------------------------------------
    s.append(T("Le service concède l’exemple qui portait le grief", "2.2"))
    s.append(P("Sur le Beaune, le service écrit : « La réponse se limite à deux types de vins. "
               "**Au sens de la réponse, le service aurait effectivement dû rassembler ces "
               "types.** » (p. 48). La concession porte sur l’écart le plus lourd de toute la "
               "comptabilité matière : les **12 950 cl** que la proposition présentait comme "
               "vendus sans qu’aucune bouteille n’ait été achetée, soit **129,5 L**."))
    s.append(P("Une fois les trois libellés voisins rassemblés, comme le service admet qu’il "
               "aurait fallu le faire, la famille est **excédentaire de 41,8 L** sur trois "
               "exercices : 220,6 L achetés pour 178,8 L consommés. Il n’existe aucun volume de "
               "blanc vendu sans achat : le volume visé est du **rouge** enregistré au verre et "
               "au pichet sous « C. DE BEAUNE », et le Nuits blanc est un vin distinct, acheté "
               "18,0 L pour 2,2 L consommés."))
    s.append(TAB_BEAUNE)
    s.append(P("Le tableau que le service oppose à la page 48 le confirme lui-même. Sur la ligne "
               "« H. COTES DE NUITS », exercice clos au 31/03/2024, il imprime **0 quantité "
               "disponible, 12 950 quantités vendues et 0,00 % de volumes disparus**. La ligne "
               "qui portait à elle seule 129,5 L de ventes sans achat est cotée à zéro pour cent "
               "dans le tableau censé démontrer l’existence de ces disparitions."))

    # --- 2.3 : arithmetique des pourcentages ---------------------------------
    s.append(T("Les pourcentages imprimés ne se déduisent pas des colonnes qui les précèdent",
               "2.3"))
    s.append(P("Les quatre tableaux appliquent une formule unique : volumes disparus = "
               "(quantités disponibles − quantités vendues) / quantités disponibles. Nous avons "
               "recalculé les **" + N(n_pct) + " pourcentages** imprimés à partir des deux "
               "colonnes affichées en face de chacun. **" + N(n_conforme) + " se retrouvent, " +
               N(n_vide) + " portent sur des lignes entièrement à zéro et " + N(n_anomalie) +
               " ne se reproduisent pas.** Le détail cellule par cellule figure dans la pièce "
               "jointe."))
    s.append(TAB_PCT)
    s.append(P("Trois défauts se dégagent. Les lignes à **zéro disponible** reçoivent tantôt "
               "0,00 %, tantôt 100,00 %, sans règle : c’est le cas des 12 950 cl du Beaune, "
               "cotés 0 %, et de la bière Bleue Du Mont Blanc, cotée 100 % alors que ses deux "
               "colonnes sont vides. Sur les **blocs regroupés** (Granini, Champagne), le "
               "pourcentage du bloc est imprimé sur une ligne de détail, ce qui donne des taux "
               "sans rapport avec cette ligne. Enfin, sur le **bloc des cidres 2023**, les taux "
               "imprimés correspondent aux quantités affichées une ligne plus haut."))
    s.append(P("Un dernier contrôle porte sur l’unité de compte. Les deux lignes « Arbois Blanc "
               "Béthanie 37,5 cl » et « Arbois Blanc Béthanie 75 cl » sont annoncées en "
               "**centilitres** dans la colonne « Format Quantités », mais elles sont en réalité "
               "libellées en **bouteilles** : le service y porte 186, 131 et 134 pour les demi-"
               "bouteilles et 107, 90 et 85 pour les bouteilles, quand les factures Franche-Comté "
               "Boissons Services de la période en portent " +
               N(bouteilles("BETHANIE 37,5")) + " et " + N(bouteilles("BETHANIE 75")) +
               ". Lues en centilitres, elles donneraient moins de cinq demi-bouteilles et "
               "moins de deux bouteilles disponibles par exercice, pour un vin qui figure sur "
               "les factures par cartons entiers."))
    s.append(P("Un dernier profil mérite d’être relevé, car il est arithmétiquement conforme : "
               "les **pourcentages négatifs**. Le Martini Blanc affiche −26,00 % en 2023 et "
               "−22,00 % en 2025, le Cidre Brut −19,51 % en 2025, la Vittel Evian 50 cl −46,67 % "
               "en 2024. Un taux négatif signifie que la caisse enregistre **plus de ventes que "
               "d’unités disponibles**. Ce n’est pas la trace d’une dissimulation, c’est la "
               "preuve qu’un même produit est vendu sous plusieurs boutons de caisse et acheté "
               "sous plusieurs libellés de facture : exactement le rattachement que le service "
               "admet, pour le Beaune, avoir manqué."))

    # --- 2.4 : le disponible du service, plancher ----------------------------
    s.extend(bloc_intermarche())

    # --- 2.5 : la dose de cuisson --------------------------------------------
    s.append(T("Une dose de cuisson n’est pas une dose servie", "2.5"))
    s.append(P("Le service répond que « ce sont les dirigeants qui ont informé le vérificateur "
               "que la dose de flambage était de 4 centilitres » et que ramener cette dose à 2 cl "
               "serait « très commode » (p. 49 et 50). Il n’y a aucune contestation sur ce point : "
               "la dose de **4 cl a bien été donnée**, et elle vise le **flambage**, c’est-à-dire "
               "un geste de cuisine. Le débat ne porte pas sur son origine, mais sur ce qu’elle "
               "mesure."))
    s.append(P("Deux usages doivent être distingués. La **dose servie** est celle du verre de "
               "digestif : elle est enregistrée en caisse, elle est facturée au client, elle "
               "produit une recette. La **dose de cuisson** est versée dans une poêle ou sur un "
               "fromage : une partie brûle, une partie s’évapore, rien n’est enregistré sous un "
               "bouton de boisson, et le produit est un **coût de matière première**, jamais une "
               "recette. Surestimer la seconde ne peut révéler aucune vente dissimulée."))
    s.append(P("La caisse permet de mesurer exactement la part de chacune. Sur trois exercices, "
               "le Calvados **vendu au verre** représente **36 doses, soit 1,44 L**. Tout le "
               "reste, **109,3 L**, part en cuisine, dans sept plats et desserts identifiés. La "
               "dose servie représente **1,3 % du Calvados consommé** : c’est la dose de cuisson, "
               "et elle seule, qui pilote la totalité de l’écart."))
    s.append(TAB_CALVA_USAGE)
    s.append(NOTE_ANCRE)
    # le bloc « encadrement de la dose » est reinsere ici par
    # scripts/reponse1-calvados-encadrement.py (ancre : la note ci-dessus)

    # --- 2.6 : les eaux-de-vie ------------------------------------------------
    s.append(T("Le même encadrement ferme le seul déficit du bilan matière", "2.6"))
    s.append(P("Le bilan matière complet, produit par produit, ne laisse subsister qu’un seul "
               "déficit de famille : **" + N(-BILAN_FAM, 1) + " L manquants sur les eaux-de-vie "
               "et digestifs**. Nous ne le contournons pas, nous le fermons par la même méthode que "
               "le Calvados, et pour la même raison : ce déficit est celui du Calvados, et de lui "
               "seul. Hors Calvados, la famille est **excédentaire de " + N(BILAN_HORS, 1) +
               " L** (" + N(ACH_HORS, 1) + " L achetés, " + N(CONSO_HORS, 1) + " L consommés et " +
               N(STOCK_HORS, 1) + " L en stock)."))
    s.append(P("La dose de cuisine est le seul paramètre libre. Le tableau ci-dessous la fait "
               "varier et laisse le stock arbitrer. À 4 cl, la famille aurait consommé " +
               N(-BILAN_FAM, 1) + " L de plus qu’elle n’a acheté, ce qui est matériellement "
               "impossible. À 2 cl, elle laisserait " + N(bilan_fam(2.0), 1) + " L inemployés, "
               "que l’inventaire dément. **Le bilan change de signe à l’intérieur du même "
               "intervalle de 2 à 3 cl**, et le point d’équilibre de la famille se situe à **" +
               N(DOSE_EQ_FAM, 2) + " cl**. Ce chiffre n’est pas choisi : il est ce qui reste une "
               "fois les achats facturés, l’inventaire et les ventes au verre connus."))
    s.append(tableau_edv())
    s.append(P("La conséquence est double. Une fois la dose ramenée dans son encadrement, le "
               "bilan matière ne comporte plus aucun déficit de famille. Et la dose qui ferme la "
               "famille entière est la même que celle qui ferme le seul Calvados : la correction "
               "n’a donc rien de sélectif, elle est imposée par le stock, et non choisie pour "
               "l’alcool qui pose problème."))

    # --- 2.7 : etendre la logique a toutes les doses --------------------------
    s.append(T("Étendre la correction à toutes les doses ne pourrait pas accroître le grief",
               "2.7"))
    s.append(P("Le service écrit qu’il aurait fallu corriger de la même façon « le vin jaune, le "
               "vin pour les sauces, le vin pour la cuisine, le vin pour tous les cocktails "
               "(4 cl retenus, également), les sirops (4 cl retenus, également) », et qu’ainsi "
               "« les écarts de boissons dans la comptabilité matière établie par le service se "
               "seraient fortement accrus » (p. 50). L’affirmation n’est pas chiffrée. Elle se "
               "chiffre, et elle se retourne."))
    s.append(P("Une dose est le coefficient qui convertit un nombre de ventes ou de plats en un "
               "volume. La réduire réduit le volume compté comme vendu, donc **augmente** l’écart "
               "entre le disponible et le vendu. Elle ne peut donc, en aucun cas, faire "
               "apparaître une consommation supérieure aux achats : elle produit exactement le "
               "contraire, davantage de produit acheté et non vendu. Or c’est la consommation "
               "supérieure aux achats, et elle seule, qui donne son titre et son objet à la "
               "partie I."))
    s.append(P("Poste par poste, dans les propres tableaux du service, chacun des postes qu’il "
               "cite est déjà excédentaire : **" + N(tot_d - tot_v) + " cl achetés et non "
               "vendus** sur " + N(tot_d) + " cl disponibles, soit " +
               N((tot_d - tot_v) / tot_d * 100, 1) + " %. Aucun de ces postes ne bascule dans "
               "l’autre sens, quelle que soit la dose retenue."))
    s.append(tableau_postes())
    s.append(P("Une précision s’impose, parce qu’elle joue contre nous et qu’il vaut mieux la "
               "porter que la taire. Dans la reconstitution, la dose sert aussi à convertir en "
               "nombre de verres le volume que le service juge vendable : abaisser une dose de "
               "cuisine libère du volume, et abaisser une dose de service multiplie les verres "
               "tirés de ce volume. **Nous ne demandons donc aucune extension.** Nous demandons "
               "une seule correction, celle que le stock impose, et nous en assumons la "
               "conséquence."))
    s.append(P("Sur le Calvados, cette conséquence est nulle, et elle l’est par les chiffres du "
               "service. Son volume disponible sur trois exercices est de **7 300 cl** (31, 22 "
               "puis 20 L, p. 65) et il retranche déjà, au titre de la cuisine, **9 317 cl** "
               "(repère D, p. 65 et 69). Il retranche donc, avant toute correction, 2 017 cl de "
               "plus qu’il n’en a de disponible : ramener la dose dans son encadrement ne libère "
               "aucun volume vendable, cela supprime seulement un solde négatif que la "
               "reconstitution ne pouvait pas valoriser."))

    # --- 2.8 : le bilan matiere d'ensemble ------------------------------------
    s.append(T("La seule grandeur probante est le bilan matière", "2.8"))
    s.append(P("Le service reproche à la réponse de « globaliser » pour lisser les incohérences "
               "(p. 52). Le reproche inverse la logique du bilan matière. Un litre acheté est "
               "soit vendu, soit consommé sans vente, soit perdu ; et lorsque deux libellés se "
               "recouvrent, ce qui manque sur l’un se retrouve sur l’autre. Un écart isolé sur un "
               "libellé ne prouve donc rien tant qu’il n’a pas été rapproché du libellé voisin. "
               "C’est ce que le service reconnaît lui-même en admettant qu’il aurait dû "
               "rassembler les types de Beaune."))
    s.append(P("Le rapprochement complet a été fait, produit par produit, en reliant chaque "
               "libellé de **caisse** à sa **facture** fournisseur et à l’**inventaire**. Agrégé "
               "par famille, il ne laisse subsister qu’un seul déficit, celui des eaux-de-vie, "
               "dont le 2.6 vient d’établir qu’il tient entièrement à la dose de cuisine du "
               "Calvados et qu’il se ferme à l’intérieur de l’encadrement de 2 à 3 cl. Le "
               "tableau ci-dessous conserve délibérément la dose de 4 cl retenue par le service, "
               "c’est-à-dire l’hypothèse qui **minore** notre excédent de " + N(-BILAN_FAM, 1) +
               " L."))
    s.append(tableau_familles())
    s.append(P("Toutes familles confondues, l’établissement a **acheté " + N(T_NET, 1) + " L de "
               "plus qu’il n’a servi**, soit " + N(T_NET / T_ACHAT * 100, 1) + " % de ses achats. "
               "Une comptabilité matière ne peut pas être présentée comme révélant une "
               "consommation supérieure aux achats lorsque, mesurée sur l’ensemble, elle se ferme "
               "largement à l’excédent."))
    s.append(P("Une réserve doit être portée, parce qu’elle joue contre nos propres chiffres. Ce "
               "bilan est bâti sur les **" + N(NB_FACTURES_FCBS) + " factures Franche-Comté "
               "Boissons Services**, les seules dont la société dispose : les 78 factures "
               "Intermarché n’y figurent pas davantage que dans le disponible du service. Et "
               "trois libellés y sont sous-évalués à l’achat, parce que les millésimes sont "
               "facturés sous des désignations distinctes et que les demi-bouteilles ne sont pas "
               "rattachées au produit : le Chablis (" + N(FACTURE["Chablis"], 1) + " L facturés "
               "pour " + N(BILAN["Chablis"]["achat_l"], 1) + " L retenus), le Gewurztraminer (" +
               N(FACTURE["Gewurztraminer"], 1) + " L pour " +
               N(BILAN["Gewurztraminer"]["achat_l"], 1) + " L) et l’Arbois Béthanie (" +
               N(FACTURE["Arbois Béthanie"], 1) + " L pour " +
               N(BILAN["Arbois Béthanie"]["achat_l"], 1) + " L), soit **" + N(TOT_MANQUE, 1) +
               " L d’achats facturés absents du bilan**. Nous les laissons de côté par prudence : "
               "les reprendre ne ferait qu’augmenter l’excédent. Ce défaut de rattachement "
               "explique à lui seul le déficit que ces trois libellés affichent dans notre "
               "propre bilan, alors que le tableau du service les cote en excédent d’achat les "
               "trois exercices (Chablis, Gewurztraminer, Béthanie, p. 52)."))
    s.append(P("Le service objecte enfin que la décote de 14,50 % serait « totalement incohérente "
               "économiquement » (p. 52), et conteste les trois taux de 5 % retenus pour les "
               "offerts, la consommation du personnel et la perte (p. 52 et 53). Ces trois points "
               "sont traités dans les parties consacrées aux **pertes**, aux **offerts** et à la "
               "**consommation du personnel** de la présente réponse, où ils sont chiffrés et "
               "documentés."))

    # --- chapitre 3 -----------------------------------------------------------
    s.append({"kind": "chapitre", "source": "nous", "numero": 3,
              "titre": "Ce que cela fait tomber",
              "sousTitre": "Trois fois répétée, la conclusion de la partie I ne repose plus sur "
                           "aucune quantité mesurée."})
    s.append(P("La partie I conclut trois fois, aux pages 50, 51 et 53, que le rejet de "
               "comptabilité fondé sur la comptabilité matière est maintenu. Cette conclusion "
               "suppose que les écarts constatés soient établis, et qu’ils aillent dans le sens "
               "d’une consommation supérieure aux achats. Or, sur les " + N(n_cellules) +
               " cellules opposées, **" + N(n_pos) + " établissent l’inverse** ; l’exemple le "
               "plus lourd, **129,5 L de vin blanc prétendument vendu sans achat**, est concédé "
               "par le service lui-même ; **" + N(n_anomalie) + " des " + N(n_pct) +
               " pourcentages** imprimés ne se recalculent pas à partir des colonnes affichées ; "
               "et le disponible qui sert de référence ne ventile pas la totalité des achats du "
               "second fournisseur que la proposition cite."))
    s.append(P("Il ne reste, au terme de ces contrôles, aucune quantité mesurée démontrant qu’il "
               "aurait été vendu plus qu’il n’a été acheté. Le bilan matière complet, caisse "
               "contre factures contre inventaire, laisse au contraire **" + N(T_NET, 1) +
               " L d’achats non servis**, et son unique déficit de famille se referme à "
               "l’intérieur de l’encadrement de dose que le stock impose. La comptabilité "
               "matière ne peut donc, à elle seule, justifier le rejet de la comptabilité ni la "
               "reconstitution de chiffre d’affaires qui en découle, elle-même amplifiée par le "
               "coefficient appliqué à la cuisine."))

    s.append({"kind": "interne", "audience": "avocat",
              "titre": "Points à sécuriser avant l’entretien et, le cas échéant, devant la "
                       "commission",
              "texte": "1. Intermarché : la société ne détient pas les " + N(INTER_N) +
                       " factures. La démonstration du 2.4 repose sur trois éléments "
                       "vérifiables par le service lui-même (les 21 colonnes de son annexe "
                       "n° 5, la colonne « Achats Inter-M » vide sur la ligne Calvados de son "
                       "annexe n° 6, le taux moyen de TVA de " + N(TAUX_MOY, 1) +
                       " % sur ses propres montants) et sur la charge de la preuve. Ne jamais "
                       "annoncer une production de pièces que nous ne maîtrisons pas. Si "
                       "l’exploitante retrouve des relevés bancaires ou des tickets de la "
                       "période, demander la communication de l’annexe n° 5 en original et "
                       "faire constater ligne à ligne les produits achetés. "
                       "2. Le taux de TVA des factures Intermarché a été lu sur la "
                       "transcription de l’annexe ; sur les " + N(INTER_N) + " lignes, " +
                       N(NB_OK) + " se recoupent exactement (HT + TVA = TTC) et seules "
                       "celles-là ont été retenues. Faire confirmer la lecture sur l’annexe "
                       "papier avant toute audience. "
                       "3. Notre propre bilan matière est bâti sur les " +
                       N(NB_FACTURES_FCBS) + " factures Franche-Comté Boissons Services. Trois "
                       "libellés y sont sous-évalués à l’achat pour " + N(TOT_MANQUE, 1) +
                       " L (Chablis, Gewurztraminer, demi-bouteilles de Béthanie) : le "
                       "rattachement doit être repris avant tout débat d’expert, mais la "
                       "correction joue en notre faveur et nous conservons volontairement le "
                       "chiffre bas. "
                       "4. Le seul paramètre libre de la démonstration reste la dose de cuisine "
                       "réelle, plat par plat. L’encadrement entre 2 et 3 cl la rend "
                       "indifférente, mais une confirmation de l’exploitante sur le camembert "
                       "rôti, qui pèse 81 % du volume, la verrouillerait."})
    s.append({"kind": "piecejointe",
              "intro": "Contrôles reproductibles de la partie I. Le premier fichier recalcule les "
                       + N(n_pct) + " pourcentages des quatre tableaux du service, établit le "
                       "bilan matière par famille et par produit, et sépare la dose de Calvados "
                       "servie au verre de la dose utilisée en cuisine (script "
                       "scripts/reponse1-conso-achats-controles.py). Le second classe les " +
                       N(n_cellules) + " cellules des quatre tableaux selon le sens de l’écart, "
                       "encadre la dose de cuisine des eaux-de-vie et chiffre poste par poste "
                       "l’hypothèse d’extension des corrections de dose "
                       "(script scripts/reponse1-conso-achats-encadrements.py).",
              "fichiers": [
                  {"fichier": "pieces-reponse-1/R1-conso-achats-controles.xlsx",
                   "label": "Contrôles arithmétiques et bilan matière (partie I)"},
                  {"fichier": "pieces-reponse-1/R1-conso-achats-encadrements.xlsx",
                   "label": "Sens des écarts, encadrement des eaux-de-vie et postes de doses"},
              ]})
    return s


REPONSE_COURTE = (
    "Sur les " + N(n_cellules) + " cellules des quatre tableaux opposés, " + N(n_neg) +
    " seulement montrent des ventes supérieures aux achats, et la plus lourde est celle que le "
    "service concède ; son disponible ne ventile pas la totalité des achats du second "
    "fournisseur qu’il cite ; encadrée entre 2 et 3 cl par le stock lui-même, la dose de cuisine "
    "ferme le dernier déficit du bilan matière, qui reste excédentaire de " + N(T_NET, 1) + " L.")

POSITION_SERVICE = DOC["entete"]["positionService"]


def main():
    doc = json.load(open(CIBLE, encoding="utf-8"))
    doc["sections"] = doc["sections"][:FIN_CHAPITRE_1] + refutation()
    doc["entete"]["reponseCourte"] = REPONSE_COURTE
    doc["entete"]["statut"] = "demonte"
    doc.get("meta", {}).pop("_bloc_calvados_encadrement", None)
    json.dump(doc, open(CIBLE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("écrit :", CIBLE, "->", len(doc["sections"]), "sections")

    # Ce script reconstruit toute la refutation et efface donc le bloc
    # « L'encadrement de la dose : entre 2 et 3 cl ». On le reinsere aussitot :
    # l'oubli de cette etape avait ete releve par l'audit des sources.
    import subprocess
    ici = os.path.dirname(os.path.abspath(__file__))
    subprocess.run([sys.executable, os.path.join(ici, "reponse1-calvados-encadrement.py")],
                   check=True)


if __name__ == "__main__":
    main()
