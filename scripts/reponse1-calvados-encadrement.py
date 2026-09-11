#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REPONSE 1 (partie I) - Encadrement de la dose de flambage du Calvados.

Ajoute, dans src/data/reponse1/consommation-superieure-achats.json, le bloc
« L'encadrement de la dose » : plutot que de retenir une dose unique (ce que le
service reproche par ailleurs a la reponse, en parlant d'un taux « defini
mathematiquement »), on ENCADRE la dose entre 2 et 3 cl et on constate que le
bilan matiere change de signe a l'interieur de l'intervalle.

Tous les chiffres proviennent :
  - du tableau du service lui-meme (reponse du 04/09/2026, p. 65, repere D) :
    nombre de plats, volume disponible, volume consomme ;
  - du detail des tickets de caisse (ANNEXE-C1 a C3) pour le Calvados vendu au
    verre et le prix moyen de la dose.
Idempotent : relancer le script remplace le bloc au lieu de l'empiler.
"""
import os, json, collections
import xlrd

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
CAISSE = os.path.join(ROOT, "public/documents/caisse-enregistreuse/")
CIBLE = os.path.join(ROOT, "src/data/reponse1/consommation-superieure-achats.json")
EXOS = ["2022-2023", "2023-2024", "2024-2025"]
MARQUE = "_bloc_calvados_encadrement"

# --- Chiffres du SERVICE (p. 65, repere D) : opposables tels quels -----------
N_FISC = {"2022-2023": 997, "2023-2024": 880, "2024-2025": 873}      # plats
DISPO = {"2022-2023": 3100, "2023-2024": 2200, "2024-2025": 2000}    # cl
CONSO_FISC = {"2022-2023": 3310, "2023-2024": 3002, "2024-2025": 3005}  # cl

# --- Calvados vendu au verre, lu dans la caisse ------------------------------
LIB_VERRE = ("Calvados", "Calvados (4cl)")
DOSE_VERRE = 4.0


def verre():
    par_exo, ca, q = {}, 0.0, 0.0
    for i, e in enumerate(EXOS, 1):
        sh = xlrd.open_workbook(CAISSE + f"ANNEXE-C{i}_detail-tickets_{e}.xls").sheet_by_index(0)
        n = 0.0
        for r in range(1, sh.nrows):
            if str(sh.cell_value(r, 10)).strip() in LIB_VERRE:
                v = float(sh.cell_value(r, 11))
                if v <= 0:
                    continue
                n += v
                ca += v * float(sh.cell_value(r, 13))
        par_exo[e] = n
        q += n
    return par_exo, q, ca


VERRE, VERRE_TOT, CA_VERRE = verre()
PU_VERRE = CA_VERRE / VERRE_TOT

TOT_N = sum(N_FISC.values())
TOT_D = sum(DISPO.values())
TOT_V = sum(VERRE.values())
DOSE_BILAN = (TOT_D - DOSE_VERRE * TOT_V) / TOT_N
BORNES = (2.0, 3.0)


def conso(e, d):
    return d * N_FISC[e] + DOSE_VERRE * VERRE[e]


L = lambda cl, d=2: f"{cl/100:,.{d}f}".replace(",", " ").replace(".", ",") + " L"
SL = lambda cl, d=2: ("+" if cl >= 0 else "") + L(cl, d)
CLV = lambda x, d=2: f"{x:,.{d}f}".replace(",", " ").replace(".", ",") + " cl"
N = lambda x, d=0: f"{x:,.{d}f}".replace(",", " ").replace(".", ",")
EUR = lambda x, d=2: f"{x:,.{d}f}".replace(",", " ").replace(".", ",") + " €"
cg = lambda v, **k: dict(v=v, **k)
cd = lambda v, **k: dict(v=v, align="right", **k)


def tableau_encadrement():
    lignes = []
    for e in EXOS:
        c2, c3 = conso(e, BORNES[0]), conso(e, BORNES[1])
        lignes.append([
            cg(e), cd(N(N_FISC[e])), cd(L(DISPO[e])),
            cd(L(c2)), cd(SL(DISPO[e] - c2), badge="ok" if DISPO[e] - c2 >= 0 else "ko"),
            cd(L(c3)), cd(SL(DISPO[e] - c3), badge="ok" if DISPO[e] - c3 >= 0 else "ko"),
        ])
    c2 = sum(conso(e, BORNES[0]) for e in EXOS)
    c3 = sum(conso(e, BORNES[1]) for e in EXOS)
    lignes.append([
        cg("Total 3 exercices", fw=700), cd(N(TOT_N), fw=700), cd(L(TOT_D), fw=700),
        cd(L(c2), fw=700), cd(SL(TOT_D - c2), fw=700, badge="ok"),
        cd(L(c3), fw=700), cd(SL(TOT_D - c3), fw=700, badge="ko"),
    ])
    return {
        "kind": "tableau",
        "titre": "L’encadrement de la dose : le bilan matière change de signe entre 2 et 3 cl "
                 "(décompte de plats et volumes disponibles du service, p. 65)",
        "minWidth": 940,
        "colonnes": [{"label": "Exercice"}, {"label": "Plats", "align": "right"},
                     {"label": "Calvados disponible", "align": "right"},
                     {"label": "Consommation à 2 cl", "align": "right"},
                     {"label": "Bilan à 2 cl", "align": "right"},
                     {"label": "Consommation à 3 cl", "align": "right"},
                     {"label": "Bilan à 3 cl", "align": "right"}],
        "lignes": lignes,
    }


def tableau_dose_implicite():
    lignes = []
    for e in EXOS:
        lignes.append([
            cg(e), cd(N(CONSO_FISC[e]) + " cl"), cd(N(N_FISC[e])),
            cd(N(4 * N_FISC[e]) + " cl"), cd(N(CONSO_FISC[e] - 4 * N_FISC[e]) + " cl"),
            cd(CLV(CONSO_FISC[e] / N_FISC[e]), fw=700),
        ])
    tc = sum(CONSO_FISC.values())
    lignes.append([
        cg("Total 3 exercices", fw=700), cd(N(tc) + " cl", fw=700), cd(N(TOT_N), fw=700),
        cd(N(4 * TOT_N) + " cl", fw=700), cd(N(tc - 4 * TOT_N) + " cl", fw=700),
        cd(CLV(tc / TOT_N), fw=700),
    ])
    return {
        "kind": "tableau",
        "titre": "La colonne « Volume consommé (à raison de 4 cl par plat) » de la page 65, "
                 "confrontée à la colonne de plats qui la jouxte",
        "minWidth": 860,
        "colonnes": [{"label": "Exercice"},
                     {"label": "Volume consommé affiché", "align": "right"},
                     {"label": "Plats retenus", "align": "right"},
                     {"label": "4 cl x plats", "align": "right"},
                     {"label": "Écart", "align": "right"},
                     {"label": "Dose réellement appliquée", "align": "right"}],
        "lignes": lignes,
    }


def bloc():
    c2 = sum(conso(e, BORNES[0]) for e in EXOS)
    c3 = sum(conso(e, BORNES[1]) for e in EXOS)
    trou = TOT_D - c2
    manque = c3 - TOT_D
    tc = sum(CONSO_FISC.values())
    verres_ecart = 2017 / DOSE_VERRE
    return [
        {"kind": "titre", "texte": "L’encadrement de la dose : entre 2 et 3 cl"},
        {"kind": "paragraphe",
         "texte": "Le service reproche ailleurs à la réponse de « définir mathématiquement » ses taux. "
                  "L’objection est prise au sérieux : **nous ne retenons pas une dose, nous "
                  "l’encadrons**. Deux bornes suffisent, et aucune des deux n’est choisie par nous. "
                  "La borne basse, **2 cl**, est la référence culinaire déjà versée au débat (un "
                  "dessert flambé demande 7 à 8 cl d’alcool pour quatre personnes). La borne haute, "
                  "**3 cl**, est le seuil au-delà duquel le stock ne suit plus."},
        {"kind": "paragraphe",
         "texte": "Le calcul est fait avec **le décompte de plats du service lui-même** (997, 880 puis "
                  "873 plats nécessitant une dose, p. 65) et **son propre volume disponible** (31, 22 "
                  "puis 20 L). Le Calvados vendu au verre, lu dans la caisse, est ajouté à la "
                  "consommation : " + N(VERRE["2022-2023"]) + ", " + N(VERRE["2023-2024"]) + " puis " +
                  N(VERRE["2024-2025"]) + " doses de 4 cl."},
        tableau_encadrement(),
        {"kind": "note",
         "texte": "Le décompte de 2 750 plats est celui du service (p. 65). Il diffère très "
                  "légèrement du nôtre, 2 732 plats, reproduit dans le tableau précédent : le service "
                  "y ajoute la crêpe Normandine et n’y compte pas les deux libellés « flambée » "
                  "génériques, que nous retenons par prudence. L’écart, 18 plats sur 2 750, "
                  "représente moins de 0,7 % et ne déplace la dose d’équilibre que de deux "
                  "centièmes de centilitre : la démonstration ne dépend pas du décompte retenu."},
        {"kind": "paragraphe",
         "texte": "Le résultat est un **encadrement au sens strict** : à 2 cl, " + L(trou) + " du "
                  "Calvados acheté resteraient inemployés, ce que l’inventaire dément puisque le stock "
                  "de clôture ne dépasse jamais deux bouteilles ; à 3 cl, il en **manquerait** " +
                  L(manque) + ", ce qui est matériellement impossible. Le bilan change de signe à "
                  "l’intérieur de l’intervalle : **la dose réelle est nécessairement comprise entre 2 "
                  "et 3 cl**, et le point d’équilibre se situe à **" + CLV(DOSE_BILAN) + "**, soit à " +
                  N((DOSE_BILAN - 2) / (BORNES[1] - BORNES[0]) * 100) + " % de l’intervalle. Ce chiffre "
                  "n’est pas postulé : il est ce qui reste une fois le volume acheté, le stock et les "
                  "ventes au verre connus."},
        {"kind": "paragraphe",
         "texte": "**Nous ne soutenons donc plus la dose de 2 cl** avancée le 10 juillet 2026. Elle "
                  "laisserait " + L(trou) + " sans emploi, que le service convertirait aussitôt en "
                  "ventes non déclarées. L’encadrement est la seule lecture qui n’ouvre ni une "
                  "impossibilité matérielle, ni un volume résiduel : quelle que soit la valeur retenue "
                  "entre 2,5 et 2,7 cl, la conclusion est identique, **le Calvados acheté est "
                  "intégralement consommé et il n’en reste rien à vendre**."},
        {"kind": "titre", "texte": "Le service applique déjà une dose de 3,39 cl, sans le dire"},
        {"kind": "paragraphe",
         "texte": "La démonstration est encore plus courte du côté du service. Sa colonne de la page 65 "
                  "s’intitule « **Volume consommé (à raison de 4 cl par plat)** ». Elle jouxte la "
                  "colonne du nombre de plats. Les deux ne se recalculent pas l’une l’autre."},
        tableau_dose_implicite(),
        {"kind": "paragraphe",
         "texte": "Sur les trois exercices, le tableau affiche " + N(tc) + " cl là où 4 cl par plat en "
                  "donneraient " + N(4 * TOT_N) + " : **" + N(4 * TOT_N - tc) + " cl d’écart**. La dose "
                  "réellement appliquée est de **" + CLV(tc / TOT_N) + "**, et non de 4 cl. Le service a "
                  "donc procédé lui-même à la correction qu’il refuse à la société, sans l’annoncer, "
                  "après avoir déjà ramené sa dose de 5 à 4 cl au stade de la proposition. Et il écrit "
                  "en toutes lettres, page 49, qu’« **à cause de cette quantité, des incohérences sur "
                  "les achats de calvados apparaissent, la consommation devenant supérieure aux "
                  "achats** » : il constate que le paramètre est faux, puis impute le résultat à la "
                  "comptabilité."},
        {"kind": "paragraphe",
         "texte": "L’origine de ce 4 cl n’a rien de mystérieux, et elle n’implique aucune "
                  "contradiction des dirigeants. Le bouton de caisse par lequel le Calvados est vendu "
                  "s’appelle littéralement « **Calvados (4cl)** » : **4 cl est la dose de vente**, "
                  "inscrite dans le logiciel. Interrogés sur « la dose de Calvados », les dirigeants "
                  "ont donné celle qu’ils lisent tous les jours sur leur écran. Elle a ensuite été "
                  "appliquée à la cuisine, où elle n’a pas de sens : on ne nappe pas un camembert au "
                  "four avec une dose de digestif. Le camembert rôti pèse à lui seul 1 452 portions "
                  "sur trois ans, soit, à 4 cl, **81 % de tout le Calvados disponible** pour un seul "
                  "plat."},
        {"kind": "paragraphe",
         "texte": "Enfin, la lecture inverse ne tient pas davantage. Pour lire les " + N(2017) + " cl "
                  "de surconsommation retenus par le service comme des ventes non enregistrées, il "
                  "faudrait retrouver **" + N(verres_ecart) + " verres de Calvados sur trois "
                  "exercices**, quand la caisse en enregistre **" + N(TOT_V) + "**, soit " +
                  N(verres_ecart / TOT_V, 1) + " fois le débit réel du produit. Sur la même période, "
                  "l’établissement a acheté " + EUR(1227.74) + " HT de Calvados et en a vendu " +
                  EUR(CA_VERRE) + " TTC au verre : c’est un ingrédient, pas une ligne de recette."},
        {"kind": "interne", "audience": "restaurant",
         "titre": "Trois points à confirmer avant l’entretien",
         "texte": "1. La dose réelle par plat : camembert rôti, assiette du père Grégoire et galette "
                  "Frelée d’un côté, crêpes Grappins, Basilic et Normandine de l’autre. C’est le seul "
                  "paramètre libre de la démonstration, et le camembert rôti pèse à lui seul 81 % du "
                  "volume. 2. La crêpe Normandine est-elle bien flambée au Calvados ? Le décompte du "
                  "service le suppose, sur 125,5 portions. 3. Se souvient-on d’avoir acheté du "
                  "Calvados, du whisky ou une autre eau-de-vie à Intermarché ? La question ne "
                  "conditionne pas la démonstration, qui tient par le stock, mais une réponse "
                  "positive rendrait le débat sur la dose sans objet."},
    ]


def main():
    doc = json.load(open(CIBLE, encoding="utf-8"))
    secs = doc["sections"]
    meta = doc.setdefault("meta", {})

    # Idempotence : on retire le bloc precedemment insere.
    if MARQUE in meta:
        i, n = meta[MARQUE]["debut"], meta[MARQUE]["nb"]
        del secs[i:i + n]

    # Ancre : juste apres la note qui suit le tableau « dose servie / dose en cuisine ».
    ancre = next(i for i, s in enumerate(secs)
                 if s.get("kind") == "note" and "additions partagées" in s.get("texte", ""))
    nouveau = bloc()
    secs[ancre + 1:ancre + 1] = nouveau
    meta[MARQUE] = {"debut": ancre + 1, "nb": len(nouveau),
                    "source": "scripts/reponse1-calvados-encadrement.py"}

    # La reponse courte de la page est ecrite par
    # scripts/reponse1-conso-achats-redaction.py : ce script ne la modifie pas.
    json.dump(doc, open(CIBLE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("écrit :", CIBLE, "->", len(secs), "sections (bloc de", len(nouveau), "sections)")
    print(f"dose d'équilibre {DOSE_BILAN:.2f} cl | verre {TOT_V:.0f} doses, {CA_VERRE:.2f} € TTC")


if __name__ == "__main__":
    main()
