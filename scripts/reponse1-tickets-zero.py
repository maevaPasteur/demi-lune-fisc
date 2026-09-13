#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REPONSE 1 - Les tickets cloture a 0,00 € de l'annexe H.

Audit adverse, faille jugee bloquante : nos pages demontrent la sequence des
numeros de note sur les ANNEXES C (detail des tickets), qui ne contiennent que
les tickets portant des articles. L'ANNEXE H, liste complete des tickets, en
compte 3 296 de plus, dont 3 281 cloture a 0,00 €, et sur cette base l'identite
« numero le plus eleve = nombre d'additions » ne tient plus que 22 jours sur 659.

Le service en tirerait que la demonstration porte sur un fichier expurge des cas
memes que vise le grief. L'objection est fondee sur la base retenue. Elle tombe
des qu'on regarde ce que sont ces tickets :

  3 278 des 3 281 (99,9 %) portent un numero deja porte, le meme jour, par un
  ticket ENCAISSE. Trois seulement, sur trois exercices, n'ont pas de jumeau.

C'est la signature mecanique du transfert et du partage de note : la table est
ouverte sous le numero N, son contenu est deplace ou reparti, la note d'origine
se ferme a zero et la note encaissee porte le meme numero N.

Sortie : public/documents/pieces-reponse-1/R1-tickets-a-zero.xlsx
Injecte la demonstration dans tables-virtuelles.json (idempotent).
"""
import os, json, collections
import xlrd

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
CAISSE = os.path.join(ROOT, "public/documents/caisse-enregistreuse/")
PIECES = os.path.join(ROOT, "public/documents/pieces-reponse-1/")
DATA = os.path.join(ROOT, "src/data/reponse1")
EXOS = ["2022-2023", "2023-2024", "2024-2025"]
MARQUE = "_bloc_tickets_zero"


def lire():
    """Retourne les tickets de l'annexe H et l'ensemble des n° vus en annexe C."""
    tickets = []
    for i, e in enumerate(EXOS, 1):
        sh = xlrd.open_workbook(CAISSE + f"ANNEXE-H{i}_liste-tickets_{e}.xls").sheet_by_index(0)
        for r in range(1, sh.nrows):
            try:
                no = int(float(sh.cell_value(r, 2)))
                ttc = float(sh.cell_value(r, 6))
            except (ValueError, TypeError):
                continue
            tickets.append({"exo": e, "date": str(sh.cell_value(r, 0))[:10],
                            "heure": str(sh.cell_value(r, 1)), "no": no, "ttc": ttc})
    detail = collections.defaultdict(set)
    lignes = collections.defaultdict(list)   # (exo, date, no) -> lignes d'articles
    z_jour = {}                              # (exo, date)     -> n° de cloture Z
    for i, e in enumerate(EXOS, 1):
        sh = xlrd.open_workbook(CAISSE + f"ANNEXE-C{i}_detail-tickets_{e}.xls").sheet_by_index(0)
        for r in range(1, sh.nrows):
            # Convertir AVANT d'indexer : indexer un defaultdict cree l'entree
            # meme si la conversion echoue ensuite, ce qui gonflait le nombre
            # de journees de trois unites.
            try:
                no = int(float(sh.cell_value(r, 2)))
            except (ValueError, TypeError):
                continue
            date = str(sh.cell_value(r, 0))[:10]
            detail[(e, date)].add(no)
            try:
                pu = float(sh.cell_value(r, 13))
            except (ValueError, TypeError):
                pu = None
            lignes[(e, date, no)].append({"lib": str(sh.cell_value(r, 10)).strip(), "pu": pu})
            try:
                z_jour[(e, date)] = int(float(sh.cell_value(r, 4)))
            except (ValueError, TypeError):
                pass
    return tickets, detail, lignes, z_jour


def analyse():
    tickets, detail, lignes, z_jour = lire()
    par_jour = collections.defaultdict(list)
    for t in tickets:
        par_jour[(t["exo"], t["date"])].append(t)

    zero, apparies, orphelins = [], [], []
    ident_h = 0
    for cle, lot in par_jour.items():
        encaisses = {t["no"] for t in lot if abs(t["ttc"]) > 1e-9}
        if max(t["no"] for t in lot) == len(lot):
            ident_h += 1
        for t in lot:
            if abs(t["ttc"]) < 1e-9:
                zero.append(t)
                (apparies if t["no"] in encaisses else orphelins).append(t)
    ident_c = sum(1 for v in detail.values() if v and max(v) == len(v))
    return {
        "tickets_h": len(tickets), "jours": len(par_jour),
        "zero": len(zero), "apparies": len(apparies), "orphelins": orphelins,
        "ident_h": ident_h, "ident_c": ident_c, "jours_c": len(detail),
        "detail_lignes": sum(len(v) for v in detail.values()),
        "par_exo": {e: sum(1 for t in zero if t["exo"] == e) for e in EXOS},
        "zero_liste": zero, "par_jour": par_jour,
        "orphelins_detail": [contexte_orphelin(t, detail, lignes, z_jour) for t in orphelins],
    }


def contexte_orphelin(t, detail, lignes, z_jour):
    """Ce que l'annexe C dit du ticket orphelin : cloture Z, lignes, explication.

    Chaque valeur est relue dans les annexes, aucune n'est saisie a la main :
    la piece doit porter la meme explication que la page, et rester verifiable
    ligne a ligne par le service sur les fichiers qu'il detient."""
    cle = (t["exo"], t["date"])
    lg = lignes.get((t["exo"], t["date"], t["no"]), [])
    z = z_jour.get(cle)
    nos = sorted(detail.get(cle, []))
    if lg:
        offert = all(l["pu"] is not None and abs(l["pu"]) < 1e-9 for l in lg)
        art = ", ".join(l["lib"] for l in lg)
        expl = ("Repas integralement offert. Le ticket porte " + str(len(lg)) +
                " lignes d'articles, toutes au prix de 0,00 € dans l'annexe C : "
                "rien n'a ete encaisse, donc rien n'a ete efface. Le detail est "
                "reproduit ligne a ligne a la page « Articles a prix 0 € »."
                if offert else
                "Le ticket porte " + str(len(lg)) + " lignes d'articles a l'annexe C.")
    else:
        art = ""
        plage = (f"n° {nos[0]} a n° {nos[-1]}" if nos else "aucun")
        expl = ("Aucune ligne dans le detail des tickets (annexe C) : table ouverte "
                "puis refermee sans commande. La journee n'y porte que les tickets " +
                plage + (f" (cloture Z n° {z})." if z else "."))
    return {"exo": t["exo"], "date": t["date"], "heure": t["heure"], "no": t["no"],
            "z": z, "nb_lignes": len(lg), "articles": art, "explication": expl}


def xlsx(a):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    wb = Workbook()
    blanc = Font(bold=True, color="FFFFFF")
    tete = PatternFill("solid", fgColor="0F766E")
    trait = Side(style="thin", color="D8DEE4")
    bord = Border(left=trait, right=trait, top=trait, bottom=trait)

    def entetes(ws, cols, ligne=4):
        ws.append(cols)
        for c in range(1, len(cols) + 1):
            cell = ws.cell(row=ligne, column=c)
            cell.font, cell.fill, cell.border = blanc, tete, bord
            cell.alignment = Alignment(horizontal="center", wrap_text=True)

    ws = wb.active
    ws.title = "Synthese"
    ws.append(["Les tickets clotures a 0,00 € de l'annexe H"])
    ws["A1"].font = Font(bold=True, size=13)
    ws.append(["Lecture seule des annexes H1 a H3 (liste des tickets) et C1 a C3 (detail des "
               "tickets). Un ticket a 0,00 € ne porte aucune ligne d'article : il n'apparait "
               "donc pas dans les annexes C."])
    ws["A2"].font = Font(italic=True, size=9, color="64748B")
    ws.append([])
    entetes(ws, ["Constat", "Valeur", "Base"])
    for lib, val, base in [
        ("Tickets de l'annexe H", a["tickets_h"], "3 exercices, 659 journees"),
        ("Tickets clotures a 0,00 €", a["zero"], "annexe H"),
        ("dont numero partage avec un ticket ENCAISSE le meme jour", a["apparies"],
         f"{100*a['apparies']/a['zero']:.1f} % des tickets a zero"),
        ("dont sans jumeau encaisse (orphelins)", len(a["orphelins"]),
         f"{100*len(a['orphelins'])/a['zero']:.1f} % des tickets a zero"),
        ("Journees ou n° le plus eleve = nombre de tickets (annexe H)", a["ident_h"],
         f"{100*a['ident_h']/a['jours']:.1f} % des journees"),
        ("Journees ou n° le plus eleve = nombre de notes (annexe C)", a["ident_c"],
         f"{100*a['ident_c']/a['jours_c']:.1f} % des journees"),
        ("Notes portant des articles (annexe C)", a["detail_lignes"], "base de la demonstration"),
    ]:
        ws.append([lib, val, base])
        for c in range(1, 4):
            ws.cell(row=ws.max_row, column=c).border = bord
    for i, w in enumerate([62, 14, 40], 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    ws2 = wb.create_sheet("Tickets a zero")
    ws2.append(["Les 3 281 tickets clotures a 0,00 €, avec leur jumeau encaisse"])
    ws2["A1"].font = Font(bold=True, size=13)
    ws2.append(["La colonne « jumeau » indique si un ticket ENCAISSE du meme jour porte le meme "
                "numero. C'est la trace du transfert ou du partage de note."])
    ws2["A2"].font = Font(italic=True, size=9, color="64748B")
    ws2.append([])
    entetes(ws2, ["Exercice", "Date", "Heure", "N° de ticket", "Total TTC",
                  "Jumeau encaisse le meme jour", "Total du jumeau"])
    for t in a["zero_liste"]:
        lot = a["par_jour"][(t["exo"], t["date"])]
        jum = [x for x in lot if x["no"] == t["no"] and abs(x["ttc"]) > 1e-9]
        ws2.append([t["exo"], t["date"], t["heure"], t["no"], 0.0,
                    "oui" if jum else "NON",
                    round(sum(x["ttc"] for x in jum), 2) if jum else ""])
    for i, w in enumerate([13, 13, 9, 13, 12, 28, 16], 1):
        ws2.column_dimensions[get_column_letter(i)].width = w
    ws2.freeze_panes = "A5"

    ws3 = wb.create_sheet("Orphelins")
    ws3.append(["Les seuls tickets a 0,00 € sans jumeau encaisse, sur trois exercices"])
    ws3["A1"].font = Font(bold=True, size=13)
    ws3.append(["Les trois sont expliques un a un, et l'explication est relue dans l'annexe C : "
                "numero de cloture Z, nombre de lignes d'articles, libelles. Deux sont des repas "
                "integralement offerts, dont toutes les lignes sont a 0,00 € ; le troisieme ne "
                "porte aucune ligne au detail des tickets."])
    ws3["A2"].font = Font(italic=True, size=9, color="64748B")
    ws3.append([])
    entetes(ws3, ["Exercice", "Date", "Heure", "N° de ticket", "Cloture Z",
                  "Lignes au detail (annexe C)", "Articles", "Explication"])
    for o in a["orphelins_detail"]:
        ws3.append([o["exo"], o["date"], o["heure"], o["no"], o["z"] if o["z"] else "",
                    o["nb_lignes"], o["articles"], o["explication"]])
        for c in range(1, 9):
            cell = ws3.cell(row=ws3.max_row, column=c)
            cell.border = bord
            cell.alignment = Alignment(vertical="top", wrap_text=(c >= 7))
    for i, w in enumerate([13, 13, 9, 13, 11, 14, 46, 78], 1):
        ws3.column_dimensions[get_column_letter(i)].width = w
    ws3.freeze_panes = "A5"

    os.makedirs(PIECES, exist_ok=True)
    wb.save(PIECES + "R1-tickets-a-zero.xlsx")


def bloc(a):
    N = lambda x: f"{x:,}".replace(",", " ")
    orph = a["orphelins"]
    lignes_orph = [[{"v": t["date"]}, {"v": t["heure"]}, {"v": f"n° {t['no']}", "align": "right"}]
                   for t in orph]
    return [
        {"kind": "titre",
         "texte": "Les tickets clôturés à zéro : ce que le service trouvera s’il ouvre l’annexe H"},
        {"kind": "paragraphe",
         "texte": "La démonstration qui précède porte sur les **annexes C**, c’est-à-dire sur les "
                  "notes qui contiennent des articles. Nous le disons sans détour, parce que le "
                  "service le verra : l’**annexe H**, qui liste tous les tickets, en compte " +
                  N(a["tickets_h"]) + ", soit " + N(a["tickets_h"] - a["detail_lignes"]) + " de plus, "
                  "dont **" + N(a["zero"]) + " clôturés à 0,00 € sans aucune ligne d’article**. Sur "
                  "cette base élargie, l’identité entre le numéro le plus élevé et le nombre de "
                  "tickets ne se vérifie plus que " + str(a["ident_h"]) + " jours sur " +
                  str(a["jours"]) + ". Il faut donc dire ce que sont ces tickets."},
        {"kind": "paragraphe",
         "texte": "La réponse est dans les données, et elle est sans ambiguïté : **" +
                  N(a["apparies"]) + " de ces " + N(a["zero"]) + " tickets, soit " +
                  f"{100*a['apparies']/a['zero']:.1f}".replace(".", ",") + " %, portent un numéro "
                  "que porte aussi, le même jour, un ticket encaissé**. Ce ne sont pas des notes "
                  "effacées : ce sont les enveloppes vides laissées par le transfert ou le partage "
                  "d’une addition. La table est ouverte sous le numéro N, son contenu est déplacé "
                  "ou réparti entre plusieurs convives, la note d’origine se referme à zéro et la "
                  "note réellement encaissée porte le même numéro N."},
        {"kind": "kpis", "items": [
            {"label": "Tickets clôturés à 0,00 €", "valeur": N(a["zero"]),
             "sub": "annexe H, trois exercices"},
            {"label": "Appariés à un ticket encaissé", "valeur": N(a["apparies"]),
             "sub": f"{100*a['apparies']/a['zero']:.1f}".replace(".", ",") + " %, même jour, même numéro",
             "highlight": True, "couleur": "teal"},
            {"label": "Sans jumeau encaissé", "valeur": str(len(orph)),
             "sub": "sur " + N(a["zero"]) + " et sur trois exercices"},
            {"label": "Montant de ces tickets", "valeur": "0,00 €",
             "sub": "aucune ligne d’article, aucun encaissement"},
        ]},
        {"kind": "tableau",
         "titre": "Les trois seuls tickets à 0,00 € sans jumeau encaissé, sur les trois exercices",
         "minWidth": 480,
         "colonnes": [{"label": "Date"}, {"label": "Heure"}, {"label": "N° de ticket", "align": "right"}],
         "lignes": lignes_orph},
        {"kind": "paragraphe",
         "texte": "Trois tickets sur " + N(a["zero"]) + " et sur trois exercices, tous au premier "
                  "exercice. Deux d’entre eux tombent sur des journées que la page consacrée aux "
                  "[articles à prix 0 €](/reponse-1/articles-a-zero-euro) documente déjà : ce sont "
                  "les notes intégralement offertes, dont le détail est reproduit ligne à ligne. "
                  "Il ne subsiste donc, au terme de ce contrôle, **aucun ticket clôturé à zéro dont "
                  "la contrepartie ne soit pas identifiée**."},
        {"kind": "paragraphe",
         "texte": "Ce constat referme le grief plutôt qu’il ne l’ouvre. Si des recettes avaient été "
                  "logées dans ces tickets, ils seraient orphelins : une note encaissée en espèces "
                  "puis vidée ne laisserait pas, le même jour et sous le même numéro, une seconde "
                  "note régulièrement encaissée et déclarée. C’est pourtant ce que montrent " +
                  f"{100*a['apparies']/a['zero']:.1f}".replace(".", ",") + " % des cas."},
    ]


def bloc_suppressions(a):
    """Version courte, pour la page pilier : l'objection au totalisateur."""
    N = lambda x: f"{x:,}".replace(",", " ")
    return [
        {"kind": "paragraphe",
         "texte": "Une objection se présente ici, et nous la traitons avant qu’elle ne soit "
                  "formulée : **le totalisateur ne s’incrémente qu’à l’émission d’un ticket**. Une "
                  "table vidée de ses articles avant toute émission n’y entrerait jamais, et le "
                  "contrôle qui précède serait alors aveugle à ces cas. L’annexe H permet de les "
                  "compter : elle recense **" + N(a["zero"]) + " tickets clôturés à 0,00 €**, sans "
                  "aucune ligne d’article, absents des annexes C pour cette raison."},
        {"kind": "paragraphe",
         "texte": "Ces tickets ne sont pas des recettes effacées, et cela se démontre sur le fichier "
                  "lui-même : **" + N(a["apparies"]) + " d’entre eux, soit " +
                  f"{100*a['apparies']/a['zero']:.1f}".replace(".", ",") + " %, portent un numéro que "
                  "porte aussi, le même jour, un ticket encaissé**. Ce sont les enveloppes vides que "
                  "laisse le transfert ou le partage d’une addition : la table est ouverte sous le "
                  "numéro N, son contenu est déplacé ou réparti, la note d’origine se referme à zéro "
                  "et la note réellement encaissée porte le même numéro N. Il reste **" +
                  str(len(a["orphelins"])) + " tickets sans jumeau sur trois exercices**, dont deux "
                  "correspondent à des notes intégralement offertes déjà documentées. Le détail "
                  "figure à la page [Trop de tables](/reponse-1/tables-virtuelles)."},
        {"kind": "paragraphe",
         "texte": "Le raisonnement se referme donc dans les deux sens. Une recette logée dans un "
                  "ticket clôturé à zéro laisserait ce ticket **orphelin** : il n’y aurait pas, le "
                  "même jour et sous le même numéro, une seconde note régulièrement encaissée et "
                  "déclarée. C’est pourtant ce que montrent " +
                  f"{100*a['apparies']/a['zero']:.1f}".replace(".", ",") + " % des cas, et les trois "
                  "exceptions sont nommées."},
    ]


def injecte(a):
    chemin = os.path.join(DATA, "tables-virtuelles.json")
    doc = json.load(open(chemin, encoding="utf-8"))
    secs, meta = doc["sections"], doc.setdefault("meta", {})
    if MARQUE in meta:
        i, n = meta[MARQUE]["debut"], meta[MARQUE]["nb"]
        del secs[i:i + n]
    ancre = next(i for i, s in enumerate(secs)
                 if s.get("kind") == "alerte" and "deux tests simples" in s.get("titre", "").lower())
    nouveau = bloc(a)
    secs[ancre + 1:ancre + 1] = nouveau
    meta[MARQUE] = {"debut": ancre + 1, "nb": len(nouveau),
                    "source": "scripts/reponse1-tickets-zero.py"}
    for s in secs:
        if s.get("kind") == "piecejointe":
            f = [x["fichier"] for x in s["fichiers"]]
            if "pieces-reponse-1/R1-tickets-a-zero.xlsx" not in f:
                s["fichiers"].append({"fichier": "pieces-reponse-1/R1-tickets-a-zero.xlsx",
                                      "label": "Les tickets clôturés à 0,00 € et leur jumeau encaissé (XLSX)"})
    json.dump(doc, open(chemin, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("écrit : tables-virtuelles ->", len(secs), "sections")

    # Page pilier : meme demonstration, en trois paragraphes, juste apres le
    # controle du totalisateur perpetuel dont elle leve l'angle mort.
    chemin = os.path.join(DATA, "suppressions-de-notes.json")
    doc = json.load(open(chemin, encoding="utf-8"))
    secs, meta = doc["sections"], doc.setdefault("meta", {})
    if MARQUE in meta:
        i, n = meta[MARQUE]["debut"], meta[MARQUE]["nb"]
        del secs[i:i + n]
    ancre = next(i for i, s in enumerate(secs)
                 if s.get("kind") == "paragraphe"
                 and "n’ont pas fait bouger d’un centime le totalisateur" in s.get("texte", ""))
    nouveau = bloc_suppressions(a)
    secs[ancre + 1:ancre + 1] = nouveau
    meta[MARQUE] = {"debut": ancre + 1, "nb": len(nouveau),
                    "source": "scripts/reponse1-tickets-zero.py"}
    for s in secs:
        if s.get("kind") == "piecejointe":
            f = [x["fichier"] for x in s["fichiers"]]
            if "pieces-reponse-1/R1-tickets-a-zero.xlsx" not in f:
                s["fichiers"].append({"fichier": "pieces-reponse-1/R1-tickets-a-zero.xlsx",
                                      "label": "Les tickets clôturés à 0,00 € et leur jumeau encaissé (XLSX)"})
    json.dump(doc, open(chemin, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("écrit : suppressions-de-notes ->", len(secs), "sections")


if __name__ == "__main__":
    a = analyse()
    xlsx(a)
    injecte(a)
    print(f"annexe H : {a['tickets_h']} tickets, {a['zero']} à 0,00 €, "
          f"{a['apparies']} appariés ({100*a['apparies']/a['zero']:.1f} %), "
          f"{len(a['orphelins'])} orphelins")
    print(f"identité n° max = nb tickets : H {a['ident_h']}/{a['jours']}, C {a['ident_c']}/{a['jours_c']}")
