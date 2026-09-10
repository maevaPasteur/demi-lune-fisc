#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REPONSE 1 - Cremant : fourchette de perte (sur-versement 0 % a +23,6 %).

Le service (reponse du 04/09/2026, p. 62-63 et 84-85) oppose au memoire une
impossibilite materielle : 93,20 L jetes + 118,08 L x 1,236 = 239,05 L pour
206,25 L disponibles. Ce script refait le calcul au niveau JOURNALIER, sur la
caisse certifiee, avec LES DOSES DU SERVICE LUI-MEME (tableau p. 62), et
balaie le taux de sur-versement de 0 % a 23,6 % pour produire une FOURCHETTE.

Identite de compta matiere, par exercice :
    U(a) = bouteilles ouvertes(a) x 75 cl   (cremant sorti du stock au service)
    S(a) = N x (1 + a)                      (cremant reellement verse)
    J(a) = U(a) - S(a)                      (fonds de bouteille jetes le soir)
    non vendu(a) = U(a) - N = J(a) + sur-versement
et la contrainte physique :  U(a) + bouteilles vendues entieres <= disponible.

Sources (lecture seule, reproductible) :
  public/documents/caisse-enregistreuse/ANNEXE-C{1,2,3}_detail-tickets_{exo}.xls
Sorties :
  src/data/reponse1/_cremant-fourchette.json
  public/documents/pieces-reponse-1/R1-cremant-fourchette.xlsx
  public/documents/pieces-reponse-1/R1-cremant-jour-par-jour-{exo}.csv
"""
import os, json, math, csv, collections
import xlrd

ICI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(ICI, ".."))
CAISSE = os.path.join(ROOT, "public/documents/caisse-enregistreuse/")
PIECES = os.path.join(ROOT, "public/documents/pieces-reponse-1/")
DATA = os.path.join(ROOT, "src/data/reponse1Calculs/")
EXOS = ["2022-2023", "2023-2024", "2024-2025"]
C = {e: CAISSE + f"ANNEXE-C{i}_detail-tickets_{e}.xls" for i, e in enumerate(EXOS, 1)}
BOUTEILLE = 75.0

# --- Doses RETENUES PAR LE SERVICE (tableau « DONNEES ISSUES LOGICIEL DE
# CAISSE », p. 62 de sa reponse du 04/09/2026) : le service applique 6 cl de
# cremant a chacun des trois cocktails et 12 cl au verre de cremant. On adopte
# SES doses : elles ne peuvent pas lui etre opposees.
DOSES_SERVICE = {
    "La Vouivre": 6, "VOUIVRE": 6,
    "Père Gregoire": 6, "Père Grégoire": 6,
    "KITTYKIR": 6, "Kittykir": 6,
    "Crémant": 12, "Crément / Jura VERRE": 12,
    "Kir Princier": 12,          # kir royal : meme verre que le cremant au verre
}
# Postes que le service a OMIS de son propre tableau p. 62 (donc absents de ses
# 11 808 cl) : ils augmentent la consommation reelle, jamais l'inverse.
OMIS_PAR_LE_SERVICE = ["Kir Princier", "VOUIVRE"]

# Bouteilles vendues scellees : sorties du stock, mais jamais ouvertes au service.
BOUTEILLES_ENTIERES = ["Crémant du Jura", "Crément du Jura", "Crémant Rosé"]

# Quantites disponibles retenues PAR LE SERVICE (p. 62 et 84 de sa reponse).
DISPO_BOUTEILLES = {"2022-2023": 275, "2023-2024": 325, "2024-2025": 322}

# Taux de sur-versement balayes. Borne haute : Kerr, Patterson, Koenen &
# Greenfield (2008), Alcoholism: Clinical and Experimental Research, +23,6 %.
TAUX = [0.0, 0.025, 0.05, 0.075, 0.10, 0.125, 0.15, 0.175, 0.20, 0.236]
# Balayage fin (0 a 23,6 % par pas de 0,1 point) pour trouver le taux exact
# qui boucle le bilan matiere.
TAUX_FIN = [i / 1000 for i in range(0, 237)]


def lignes(fn):
    sh = xlrd.open_workbook(fn).sheet_by_index(0)
    for r in range(1, sh.nrows):
        lib = str(sh.cell_value(r, 10)).strip()
        try:
            q = float(sh.cell_value(r, 11))
        except ValueError:
            q = 0.0
        yield str(sh.cell_value(r, 0))[:10], lib, q


def collecte():
    """{exo: {date: cl nominaux}}, {exo: {libelle: qte}}, {exo: bouteilles vendues}."""
    par_jour, par_lib, bt_vendues = {}, {}, {}
    for ex, fn in C.items():
        jour = collections.defaultdict(float)
        lib_q = collections.defaultdict(float)
        bt = 0.0
        for date, lib, q in lignes(fn):
            if q <= 0:
                continue
            dose = DOSES_SERVICE.get(lib)
            if dose is not None:
                jour[date] += q * dose
                lib_q[lib] += q
            elif lib in BOUTEILLES_ENTIERES:
                bt += q
        par_jour[ex] = dict(jour)
        par_lib[ex] = dict(lib_q)
        bt_vendues[ex] = bt
    return par_jour, par_lib, bt_vendues


def scenario(jour, taux):
    """Retourne servi_cl, bouteilles ouvertes, jete_cl pour un taux donne."""
    servi = 0.0
    bouteilles = 0
    for cl in jour.values():
        s = cl * (1 + taux)
        servi += s
        bouteilles += math.ceil(s / BOUTEILLE - 1e-9)
    return servi, bouteilles, bouteilles * BOUTEILLE - servi


def fr(x, dec=2):
    return f"{x:,.{dec}f}".replace(",", " ").replace(".", ",")


def ecrire_xlsx(res):
    """Piece justificative : bilan matiere du cremant, exercice par exercice."""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    blanc = Font(bold=True, color="FFFFFF")
    gras = Font(bold=True)
    tete = PatternFill("solid", fgColor="0F766E")
    surligne = PatternFill("solid", fgColor="CCE7E2")
    trait = Side(style="thin", color="D8DEE4")
    bord = Border(left=trait, right=trait, top=trait, bottom=trait)
    droite = Alignment(horizontal="right")

    def entetes(ws, cols, ligne):
        ws.append(cols)
        for c in range(1, len(cols) + 1):
            cell = ws.cell(row=ligne, column=c)
            cell.font, cell.fill, cell.border = blanc, tete, bord
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    # ---- Feuille 1 : le bilan matiere par exercice -----------------------
    ws = wb.active
    ws.title = "Bilan matiere"
    ws.append(["Cremant : bilan matiere par exercice (quantites disponibles retenues par le service)"])
    ws["A1"].font = Font(bold=True, size=13)
    ws.append(["Doses retenues : celles du tableau du service, reponse du 04/09/2026 p. 62 "
               "(cocktails 6 cl, verre de cremant 12 cl). Bouteille = 75 cl. "
               "Source des ventes : ANNEXE-C, detail des tickets, lecture seule."])
    ws["A2"].font = Font(italic=True, size=9, color="64748B")
    ws.append([])
    cols = ["Exercice", "Jours servis", "Cremant vendu en caisse (L)",
            "Bouteilles disponibles", "Cremant disponible (L)",
            "Bouteilles vendues scellees", "Disponible pour le service au verre (L)",
            "Ecart a expliquer (L)", "Ecart par jour de service (cl)"]
    entetes(ws, cols, 4)
    for ex in EXOS:
        e = res["exercices"][ex]
        ws.append([ex, e["jours_servis"], round(e["nominal_cl"] / 100, 2),
                   e["dispo_bouteilles"], round(e["dispo_cl"] / 100, 2),
                   e["bouteilles_vendues_entieres"], round(e["dispo_service_cl"] / 100, 2),
                   round(e["ecart_a_expliquer_cl"] / 100, 2), e["ecart_par_jour_cl"]])
        for c in range(1, len(cols) + 1):
            ws.cell(row=ws.max_row, column=c).border = bord
            if c > 1:
                ws.cell(row=ws.max_row, column=c).alignment = droite
    for i, w in enumerate([14, 13, 24, 18, 20, 20, 26, 20, 22], 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A5"

    # ---- Feuille 2 : la fourchette de sur-versement ----------------------
    ws2 = wb.create_sheet("Fourchette sur-versement")
    ws2.append(["Fourchette de sur-versement compatible avec le stock reellement disponible"])
    ws2["A1"].font = Font(bold=True, size=13)
    ws2.append(["Pour chaque taux de sur-versement, le volume verse est recalcule jour par jour, "
                "le nombre de bouteilles de 75 cl ouvertes chaque jour en est deduit (arrondi "
                "superieur), et le solde du soir est perdu. Un scenario n'est retenu que si le "
                "cremant ainsi ouvert tient dans le stock disponible. Borne haute testee : "
                "+23,6 % (Kerr, Patterson, Koenen & Greenfield, 2008)."])
    ws2["A2"].font = Font(italic=True, size=9, color="64748B")
    ws2.append([])
    cols2 = ["Exercice", "Sur-versement", "Cremant verse (L)", "Bouteilles ouvertes",
             "Cremant sorti du stock (L)", "Jete en fin de journee (L)",
             "Non vendu = jete + sur-verse (L)", "Reste disponible (L)", "Compatible avec le stock"]
    entetes(ws2, cols2, 4)
    for ex in EXOS:
        e = res["exercices"][ex]
        for sc in e["scenarios"]:
            ws2.append([ex, f"+{fr(sc['taux'] * 100, 1)} %", round(sc["servi_cl"] / 100, 2),
                        sc["bouteilles_ouvertes"], round(sc["utilise_cl"] / 100, 2),
                        round(sc["jete_cl"] / 100, 2), round(sc["non_vendu_cl"] / 100, 2),
                        round(sc["reste_dispo_cl"] / 100, 2),
                        "oui" if sc["compatible"] else "NON"])
            r = ws2.max_row
            for c in range(1, len(cols2) + 1):
                ws2.cell(row=r, column=c).border = bord
                if c > 1:
                    ws2.cell(row=r, column=c).alignment = droite
            if sc["compatible"]:
                for c in range(1, len(cols2) + 1):
                    ws2.cell(row=r, column=c).fill = surligne
        ws2.append([])
    for i, w in enumerate([14, 15, 18, 18, 24, 22, 28, 20, 22], 1):
        ws2.column_dimensions[get_column_letter(i)].width = w
    ws2.freeze_panes = "A5"

    # ---- Feuille 3 : le point d'equilibre --------------------------------
    ws3 = wb.create_sheet("Point d equilibre")
    ws3.append(["Point d'equilibre : le sur-versement maximal que le stock autorise"])
    ws3["A1"].font = Font(bold=True, size=13)
    ws3.append(["Balayage au millieme entre 0 % et 23,6 %. Le repere theorique est le solde moyen "
                "d'une bouteille entamee lorsque le besoin du jour n'est pas un multiple de 75 cl, "
                "soit 37,5 cl par jour de service : il ne depend d'aucun parametre."])
    ws3["A2"].font = Font(italic=True, size=9, color="64748B")
    ws3.append([])
    cols3 = ["Exercice", "Sur-versement maximal compatible", "Bouteilles ouvertes",
             "Cremant sorti du stock (L)", "Jete en fin de journee (L)",
             "Depassement du stock (L)", "Ecart constate (L)",
             "Repere theorique 37,5 cl x jours (L)", "Ecart au repere"]
    entetes(ws3, cols3, 4)
    for ex in EXOS:
        e = res["exercices"][ex]
        q = e["equilibre"]
        ws3.append([ex,
                    ("aucun taux positif" if e["taux_max_compatible_fin"] in (None, 0.0)
                     else f"+{fr(e['taux_max_compatible_fin'] * 100, 1)} %"),
                    q["bouteilles_ouvertes"], round(q["utilise_cl"] / 100, 2),
                    round(q["jete_cl"] / 100, 2), round(q["depassement_cl"] / 100, 2),
                    round(e["ecart_a_expliquer_cl"] / 100, 2),
                    round(e["jete_theorique_cl"] / 100, 2),
                    f"{fr(e['jete_theorique_ecart_pct'], 1)} %"])
        for c in range(1, len(cols3) + 1):
            ws3.cell(row=ws3.max_row, column=c).border = bord
            if c > 1:
                ws3.cell(row=ws3.max_row, column=c).alignment = droite
    for i, w in enumerate([14, 30, 18, 24, 22, 22, 20, 28, 16], 1):
        ws3.column_dimensions[get_column_letter(i)].width = w

    # ---- Feuille 4 : les libelles retenus et leurs doses ------------------
    ws4 = wb.create_sheet("Libelles et doses")
    ws4.append(["Libelles de caisse retenus comme contenant du cremant, et dose appliquee"])
    ws4["A1"].font = Font(bold=True, size=13)
    ws4.append(["Les doses sont celles que le service applique lui-meme dans son tableau p. 62. "
                "Les libelles Kir Princier et VOUIVRE ne figurent pas dans ce tableau : ils sont "
                "ajoutes ici, ce qui augmente la consommation reconnue et reduit d'autant "
                "l'ecart reproche. Les Kir Bourgogne et Kir Pamplemousse (vin tranquille) sont "
                "exclus, comme le service les exclut."])
    ws4["A2"].font = Font(italic=True, size=9, color="64748B")
    ws4.append([])
    cols4 = ["Exercice", "Libelle de caisse", "Dose de cremant (cl)", "Quantite vendue",
             "Cremant (cl)", "Present dans le tableau du service p. 62"]
    entetes(ws4, cols4, 4)
    for ex in EXOS:
        e = res["exercices"][ex]
        for lib, q in e["par_libelle"].items():
            dose = DOSES_SERVICE[lib]
            ws4.append([ex, lib, dose, q, round(q * dose, 1),
                        "non" if lib in OMIS_PAR_LE_SERVICE else "oui"])
            for c in range(1, len(cols4) + 1):
                ws4.cell(row=ws4.max_row, column=c).border = bord
                if c > 2:
                    ws4.cell(row=ws4.max_row, column=c).alignment = droite
        ws4.append([])
    for i, w in enumerate([14, 26, 20, 16, 16, 38], 1):
        ws4.column_dimensions[get_column_letter(i)].width = w

    os.makedirs(PIECES, exist_ok=True)
    wb.save(PIECES + "R1-cremant-bilan-matiere.xlsx")


def main():
    par_jour, par_lib, bt_vendues = collecte()
    res = {"exercices": {}, "taux": TAUX, "meta": {
        "doses_service": DOSES_SERVICE,
        "omis_par_le_service": OMIS_PAR_LE_SERVICE,
        "bouteille_cl": BOUTEILLE,
        "dispo_bouteilles_service": DISPO_BOUTEILLES,
        "source": "public/documents/caisse-enregistreuse/ANNEXE-C{1,2,3} (lecture seule)",
        "surversement_haut": "Kerr, Patterson, Koenen & Greenfield (2008), +23,6 %",
    }}

    for ex in EXOS:
        jour = par_jour[ex]
        N = sum(jour.values())                       # consommation nominale (cl)
        dispo_cl = DISPO_BOUTEILLES[ex] * BOUTEILLE  # cremant disponible (cl)
        bt_vendues_cl = bt_vendues[ex] * BOUTEILLE
        A = dispo_cl - bt_vendues_cl                 # disponible au service ouvert
        ecart = A - N                                # ce que le service appelle « ventes occultes »

        scen = []
        for t in TAUX:
            servi, bt, jete = scenario(jour, t)
            utilise = bt * BOUTEILLE
            scen.append({
                "taux": t,
                "servi_cl": round(servi, 1),
                "bouteilles_ouvertes": bt,
                "utilise_cl": round(utilise, 1),
                "jete_cl": round(jete, 1),
                "non_vendu_cl": round(utilise - N, 1),
                "surversement_cl": round(servi - N, 1),
                "reste_dispo_cl": round(A - utilise, 1),
                "compatible": utilise <= A + 1e-6,
            })
        # Taux exact qui boucle le bilan matiere (balayage fin).
        alpha_max = None
        for t in TAUX_FIN:
            _, bt, _ = scenario(jour, t)
            if bt * BOUTEILLE <= A + 1e-6:
                alpha_max = t
        # Repere theorique, sans aucun parametre : si le besoin du jour n'est pas
        # un multiple exact de 75 cl, le solde perdu est en moyenne 75/2 = 37,5 cl.
        theorique_cl = 37.5 * len(jour)
        # Point d'equilibre : le taux le plus eleve compatible avec le stock,
        # et le detail du bilan matiere a ce taux.
        if alpha_max is None:
            servi0, bt0, jete0 = scenario(jour, 0.0)
            equilibre = {"taux": 0.0, "servi_cl": round(servi0, 1),
                         "bouteilles_ouvertes": bt0, "utilise_cl": round(bt0 * BOUTEILLE, 1),
                         "jete_cl": round(jete0, 1),
                         "depassement_cl": round(bt0 * BOUTEILLE - A, 1)}
        else:
            servi1, bt1, jete1 = scenario(jour, alpha_max)
            equilibre = {"taux": alpha_max, "servi_cl": round(servi1, 1),
                         "bouteilles_ouvertes": bt1, "utilise_cl": round(bt1 * BOUTEILLE, 1),
                         "jete_cl": round(jete1, 1),
                         "depassement_cl": round(bt1 * BOUTEILLE - A, 1)}
        compat = [s for s in scen if s["compatible"]]
        res["exercices"][ex] = {
            "jours_servis": len(jour),
            "nominal_cl": round(N, 1),
            "dispo_bouteilles": DISPO_BOUTEILLES[ex],
            "dispo_cl": dispo_cl,
            "bouteilles_vendues_entieres": bt_vendues[ex],
            "dispo_service_cl": round(A, 1),
            "ecart_a_expliquer_cl": round(ecart, 1),
            "ecart_pct_du_dispo": round(100 * ecart / A, 2),
            "scenarios": scen,
            "taux_max_compatible": max((s["taux"] for s in compat), default=None),
            "taux_max_compatible_fin": alpha_max,
            "jete_theorique_cl": round(theorique_cl, 1),
            "jete_theorique_ecart_pct": round(100 * (theorique_cl - ecart) / ecart, 1),
            "ecart_par_jour_cl": round(ecart / len(jour), 1),
            "equilibre": equilibre,
            "par_libelle": {k: round(v, 1) for k, v in sorted(
                par_lib[ex].items(), key=lambda kv: -kv[1])},
        }

        # --- CSV jour par jour (piece justificative) ----------------------
        os.makedirs(PIECES, exist_ok=True)
        with open(PIECES + f"R1-cremant-jour-par-jour-{ex}.csv", "w",
                  newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow([f"Cremant ouvert au service, jour par jour - exercice {ex}"])
            w.writerow(["Source : ANNEXE-C, detail des tickets. Doses retenues par le service "
                        "(reponse du 04/09/2026, p. 62) : cocktails 6 cl, verre 12 cl. "
                        "Bouteille = 75 cl. Une bouteille de cremant ouverte n'est pas "
                        "reservable au lendemain : le solde du soir est perdu."])
            w.writerow([])
            entetes = ["Date", "Cremant vendu (cl, doses carte)"]
            for t in TAUX:
                p = f"{t*100:.1f}".replace(".", ",")
                entetes += [f"Verse a +{p} % (cl)", f"Bouteilles ouvertes +{p} %",
                            f"Jete le soir +{p} % (cl)"]
            w.writerow(entetes)
            for d in sorted(jour):
                cl = jour[d]
                ligne = [d, f"{cl:.1f}".replace(".", ",")]
                for t in TAUX:
                    s = cl * (1 + t)
                    b = math.ceil(s / BOUTEILLE - 1e-9)
                    ligne += [f"{s:.1f}".replace(".", ","), b,
                              f"{b*BOUTEILLE - s:.1f}".replace(".", ",")]
                w.writerow(ligne)
            tot = ["TOTAL", f"{N:.1f}".replace(".", ",")]
            for t in TAUX:
                servi, b, jete = scenario(jour, t)
                tot += [f"{servi:.1f}".replace(".", ","), b, f"{jete:.1f}".replace(".", ",")]
            w.writerow(tot)

    ecrire_xlsx(res)

    os.makedirs(DATA, exist_ok=True)
    with open(DATA + "cremant-fourchette.json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)

    # --- Resume console ---------------------------------------------------
    for ex in EXOS:
        e = res["exercices"][ex]
        print(f"\n=== {ex} : {e['jours_servis']} jours servis")
        print(f"  nominal (doses du service)   : {e['nominal_cl']/100:8.2f} L")
        print(f"  disponible (service)         : {e['dispo_bouteilles']} bt = "
              f"{e['dispo_cl']/100:.2f} L  moins {e['bouteilles_vendues_entieres']:.0f} bt vendues "
              f"=> {e['dispo_service_cl']/100:.2f} L")
        print(f"  ECART a expliquer            : {e['ecart_a_expliquer_cl']/100:8.2f} L "
              f"({e['ecart_pct_du_dispo']} % du disponible)")
        print(f"  {'taux':>7} {'servi L':>9} {'bt':>5} {'utilise L':>10} {'jete L':>8} "
              f"{'non vendu L':>12} {'reste L':>9}  ok")
        for s in e["scenarios"]:
            print(f"  {s['taux']*100:6.1f}% {s['servi_cl']/100:9.2f} {s['bouteilles_ouvertes']:5d} "
                  f"{s['utilise_cl']/100:10.2f} {s['jete_cl']/100:8.2f} "
                  f"{s['non_vendu_cl']/100:12.2f} {s['reste_dispo_cl']/100:9.2f}  "
                  f"{'oui' if s['compatible'] else 'NON'}")
        print(f"  taux max compatible (balayage fin) : "
              f"{'aucun' if e['taux_max_compatible_fin'] is None else format(e['taux_max_compatible_fin']*100, '.1f') + ' %'}")
        print(f"  repere theorique 37,5 cl x {e['jours_servis']} j = "
              f"{e['jete_theorique_cl']/100:.2f} L  (ecart {e['jete_theorique_ecart_pct']} % vs "
              f"{e['ecart_a_expliquer_cl']/100:.2f} L constates)")
        print(f"  ecart par jour de service : {e['ecart_par_jour_cl']} cl")
        print("  libelles retenus :", e["par_libelle"])
    print("\nJSON :", DATA + "cremant-fourchette.json")


if __name__ == "__main__":
    main()
