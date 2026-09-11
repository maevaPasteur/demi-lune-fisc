#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REPONSE 1 - Finalisation du bloc « Consequences financieres et penalites ».

Corrige, dans les trois pages, ce que la verification juridique a etabli :

1. CE 24 novembre 2003 n° 241664 est RETIRE. La phrase que nous lui attribuions
   n'est pas un motif de la decision : c'est le texte de l'ANCIENNE redaction de
   l'article L. 80 D, que l'arret cite « dans sa redaction alors en vigueur » et
   qui ne figure plus dans la version actuelle. De plus l'arret, statuant sur des
   faits proches des notres (rejet de comptabilite et reconstitution d'un
   restaurant), REJETTE les conclusions du contribuable : il se retourne contre
   nous.
2. L'article L. 80 D est cite dans sa redaction ACTUELLE, verifiee verbatim au
   point 35 de CAA Douai 4e ch., 18 septembre 2025, n° 25DA00174.
3. CE 7 juin 2019 n° 412536 : la citation etait tronquee de la clause qui porte
   la censure. Elle est retablie et sa portee exacte est indiquee.
4. CE 11 fevrier 2021 n° 432960 : le point 4, le plus fort, est exploite (la
   date d'appreciation est celle de la declaration).
5. La motivation de la penalite EXISTE, aux pages 57 et 58 de la proposition.
   Le soutenir absent etait une breche. Le moyen est recentre sur le contenu de
   cette motivation et sur le critere que le service pose lui-meme.
6. Especes : 17 333,18 € (et non 17 042,16 €), recalcule sur les annexes F.
7. Le rappel de TVA du premier exercice porte DEUX valeurs dans le meme
   document : 20 421,10 € sert d'assiette a l'amende de 100 %, 20 041 € sert
   d'assiette a l'impot et aux droits de TVA.
8. Interets de retard : le decompte est conforme et meme legerement favorable a
   la societe. Le dire renforce la credibilite du reste.

Idempotent : le script reecrit toujours les memes sections.
"""
import os, json

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DATA = os.path.join(ROOT, "src/data/reponse1")
JURICAF = "https://juricaf.org/arret/FRANCE-CONSEILDETAT-"
CE_432960 = f"[CE, 9e ch., 11 février 2021, n° 432960]({JURICAF}20210211-432960)"
CE_412536 = f"[CE, 9e et 10e ch. réunies, 7 juin 2019, n° 412536]({JURICAF}20190607-412536)"
CE_489235 = f"[CE, 8e ch., 23 juillet 2024, n° 489235]({JURICAF}20240723-489235)"
BOFIP_INT = "https://bofip.impots.gouv.fr/bofip/1458-PGP.html"
BOFIP_NAT = "https://bofip.impots.gouv.fr/bofip/1383-PGP.html"
BOFIP_CUM = "https://bofip.impots.gouv.fr/bofip/7234-PGP.html"

cg = lambda v, **k: dict(v=v, **k)
cd = lambda v, **k: dict(v=v, align="right", **k)
P = lambda t: {"kind": "paragraphe", "texte": t}
T = lambda t: {"kind": "titre", "texte": t}


# ------------------------------------------------------ PÉNALITÉS (40 %) ----
BLOC_MOTIVATION = [
    T("Ce que le service retient pour motiver la pénalité, et pourquoi cela ne suffit pas"),
    P("La pénalité est motivée, et nous ne soutenons pas le contraire : les pages 57 et 58 de la "
      "proposition de rectification lui consacrent quatre rubriques, « Anomalie et caractère non "
      "probant de la comptabilité », « Importance des minorations », « Répétition de l’infraction » "
      "et « Omission de déclaration ». Notre moyen est plus étroit et il porte sur le contenu de "
      "cette motivation, non sur son existence."),
    P("Le service pose lui-même le critère applicable, page 57 : le manquement délibéré « est établi "
      "lorsqu’il est démontré que celui-ci avait **la connaissance exacte des faits ou de la "
      "situation qui motivent les rehaussements** ». Or les faits qui motivent les rehaussements "
      "sont des paramètres arrêtés après le contrôle : une dose de service figée au centilitre, un "
      "taux de perte forfaitaire, un coefficient d’extrapolation de la cuisine. Au moment où elle "
      "déposait ses déclarations, la société ne pouvait pas avoir « la connaissance exacte » de "
      "grandeurs qui n’existaient pas encore."),
    P("C’est exactement la règle que pose le Conseil d’État : « **pour établir le caractère "
      "intentionnel du manquement du contribuable à son obligation déclarative, l’administration "
      "doit se placer au moment de la déclaration** », et si elle se fonde également sur des "
      "éléments tirés du comportement du contribuable pendant la vérification, un tel motif « ne "
      "peut en lui-même justifier l’application d’une telle pénalité » (" + CE_432960 + ", point 4). "
      "Dans cette affaire, la cour d’appel avait été censurée pour s’être fondée « exclusivement sur "
      "des éléments tirés du comportement du contribuable pendant la vérification »."),
    P("Or le seul développement propre de la partie B du courrier du 4 septembre 2026 est une "
      "appréciation portée sur nos écritures de la phase contradictoire : nos explications seraient "
      "« totalement inconcevables économiquement ou physiquement » (p. 94). C’est un jugement sur le "
      "comportement du contribuable pendant la procédure, postérieur de plus de trois ans aux "
      "déclarations de l’exercice clos en 2023. Aucun fait n’y est rapporté, aucun exercice n’y est "
      "distingué, aucun montant de pénalité n’y est cité, et le taux de 40 % n’y est pas discuté."),
    P("L’[article L. 80 D du livre des procédures fiscales](https://www.legifrance.gouv.fr/codes/"
      "article_lc/LEGIARTI000037095002) exige que les décisions mettant à la charge des "
      "contribuables des sanctions fiscales soient motivées, et qu’un délai soit ouvert pour "
      "présenter des observations sur ces motifs. Ce délai, le courrier l’ouvre. Il reste que la "
      "réponse apportée à nos observations sur les sanctions ne les discute pas : elle renvoie aux "
      "quatre vingt treize pages qui précèdent."),
]

BLOC_AMPLEUR = [
    T("L’intention ne se déduit pas de l’ampleur ni de la répétition de l’écart"),
    P("Le raisonnement du service est un enchaînement : les chiffres d’affaires reconstitués "
      "« demeurent les mêmes », donc la dissimulation « a bien été établie », donc la majoration est "
      "maintenue. Le montant du redressement devient ainsi sa propre preuve. La charge de la preuve "
      "de l’intention, qui pèse sur l’administration, s’en trouve renversée."),
    P("Le Conseil d’État a censuré pour erreur de droit une cour qui, pour établir l’intention, "
      "s’était bornée « à relever le montant des revenus d’origine indéterminée et la fréquence des "
      "versements effectués sur le compte bancaire », **alors que la fréquence de virements d’un "
      "compte à un autre compte appartenant au même contribuable ne saurait, par elle-même, "
      "caractériser une telle intention** (" + CE_412536 + ", point 4). Les faits de cette affaire "
      "sont différents des nôtres, et nous ne lui prêtons pas une portée qu’elle n’a pas : ce qu’elle "
      "établit, c’est que l’administration doit caractériser l’intention par des éléments qui lui "
      "soient propres, et non par la seule dimension de ce qu’elle a reconstitué."),
    P("La règle de fond, elle, est constante et le Conseil d’État l’a rappelée encore récemment : "
      "« pour établir l’existence d’un manquement délibéré de la part d’un contribuable, "
      "l’administration doit apporter la preuve, d’une part, de l’insuffisance, de l’inexactitude ou "
      "du caractère incomplet de ses déclarations et, d’autre part, de l’intention de l’intéressé "
      "d’éluder l’impôt » (" + CE_489235 + ", point 2). Les deux termes sont cumulatifs. Le premier "
      "suppose la reconstitution établie, ce qu’elle n’est pas."),
]


def tableau_canal():
    lignes = [
        ["Exercice clos le 31/03/2023", "193 234,55 €", "3 797,30 €", "50,9 fois"],
        ["Exercice clos le 31/03/2024", "138 863,57 €", "8 168,41 €", "17,0 fois"],
        ["Exercice clos le 31/03/2025", "139 727,76 €", "5 367,47 €", "26,1 fois"],
    ]
    out = [[cg(a), cd(b), cd(c), cd(d, fw=700)] for a, b, c, d in lignes]
    out.append([cg("Total 3 exercices", fw=700), cd("471 825,88 €", fw=700),
                cd("17 333,18 €", fw=700), cd("27,2 fois", fw=700)])
    return {
        "kind": "tableau",
        "titre": "Ce que suppose la dissimulation alléguée, confronté aux espèces réellement encaissées",
        "minWidth": 760,
        "colonnes": [{"label": "Exercice"},
                     {"label": "Distributions retenues (proposition p. 58)", "align": "right"},
                     {"label": "Espèces encaissées (annexes F)", "align": "right"},
                     {"label": "Rapport", "align": "right"}],
        "lignes": out,
    }


PARA_ESPECES = (
    "**Les encaissements sont bancarisés à 98,64 %.** Carte bancaire 91,22 %, chèques vacances "
    "3,73 %, titres restaurant 2,62 %, chèques 1,07 %. Les espèces représentent **1,36 % des "
    "règlements, soit 17 333,18 €** sur trois exercices, recalculés ligne à ligne sur les annexes F. "
    "Tous les autres flux sont tracés par un tiers, banque, ANCV ou émetteur de titres. Or le "
    "service retient des distributions de **471 825,88 €** (proposition p. 58). La somme qu’il "
    "suppose détournée représente **27,2 fois la totalité des espèces** encaissées sur la période, "
    "et jusqu’à 50,9 fois sur le premier exercice. Le courrier n’indique nulle part par quel canal "
    "elle aurait transité.")

PARA_ANTERIORITE = (
    "**Aucune infraction antérieure n’est relevée.** Les tableaux de liquidation de la proposition "
    "portent, pour les trois exercices et pour les deux impôts, la mention « Majorations "
    "antérieures : 0 » (p. 61 à 65). Le service ne fait état d’aucune obstruction, d’aucun refus de "
    "communication, d’aucune opposition à contrôle. Il ne relève pas davantage d’écriture fictive, "
    "de double facturation, de compte occulte ou d’excédent d’espèces : aucun procédé destiné à "
    "égarer le vérificateur n’est allégué. Les fichiers de caisse, les inventaires et les factures "
    "ont été remis, et le mémoire du 10 juillet 2026 était accompagné de cinquante neuf fichiers de "
    "travail.")

NOTE_INTERNE_PENA = {
    "kind": "interne", "audience": "avocat",
    "titre": "Contre-autorité à connaître avant l’entretien",
    "texte": "CAA de Douai, 4e ch., 18 septembre 2025, n° 25DA00174, SARL Aux Magots "
             "(https://juricaf.org/arret/FRANCE-COURADMINISTRATIVEDAPPELDEDOUAI-20250918-25DA00174). "
             "Faits très proches : restaurant, rejet de comptabilité, recettes reconstituées à "
             "partir des seules ventes de boissons alcoolisées, trois exercices, majoration de 40 %. "
             "Aux points 38 à 40, la cour juge que l’importance des minorations (29 à 37 % du "
             "chiffre d’affaires reconstitué, soit des proportions voisines des nôtres) et leur "
             "caractère récurrent sur trois exercices consécutifs suffisent à établir l’intention. "
             "Cet arrêt n’est volontairement pas cité dans le corps de la page. Ce qui distingue "
             "notre dossier et qu’il faut mettre en avant si le service l’invoque : aux points 29, "
             "30 et 33, la cour retient que la SARL Aux Magots n’avait rien produit pendant le "
             "contrôle et ne rapportait pas la preuve de l’exagération, alors qu’ici la société a "
             "remis l’intégralité de ses fichiers et conteste des paramètres de méthode. "
             "Point à confirmer auprès de la gérante avant l’entretien : l’absence de tout contrôle "
             "fiscal antérieur, la mention « Majorations antérieures : 0 » n’en étant qu’un indice."}


def patch_penalites(doc):
    secs = doc["sections"]
    # Remplacement du bloc « motivation » (titre §19 -> §24 inclus).
    # Ancres tolerantes : le script doit pouvoir etre relance sur sa propre sortie.
    def ancre(*motifs):
        return next(i for i, s in enumerate(secs)
                    if s.get("kind") == "titre"
                    and any(m in s.get("texte", "") for m in motifs))

    i = ancre("aucune motivation propre", "retient pour motiver")
    j = ancre("ampleur")
    secs[i:j] = BLOC_MOTIVATION
    i = ancre("ampleur")
    j = ancre("éléments de sincérité")
    secs[i:j] = BLOC_AMPLEUR
    # Corrections ponctuelles.
    for k, s in enumerate(secs):
        t = s.get("texte", "")
        if s.get("kind") == "paragraphe" and "bancarisés à 98,64" in t:
            s["texte"] = PARA_ESPECES
            if secs[k + 1].get("kind") == "tableau":
                secs[k + 1] = tableau_canal()
        elif s.get("kind") == "paragraphe" and t.startswith("**Les dirigeants ont participé"):
            s["texte"] = PARA_ANTERIORITE
        elif (s.get("kind") == "paragraphe" and "0,17 %" in t
              and "au cumul des trois exercices" not in t):
            s["texte"] = t.replace(
                "Les trois grandeurs convergent à **0,17 %** près",
                "Les trois grandeurs convergent à **0,17 %** près au cumul des trois exercices, "
                "l’écart annuel allant de 0,60 % à 2,42 %")
        elif s.get("kind") == "paragraphe" and t.startswith("Nous demandons la décharge"):
            s["texte"] = (
                "Nous demandons la décharge de la majoration de 40 %, à titre principal parce que la "
                "preuve du manquement délibéré, qui incombe au service en application de l’article "
                "L. 195 A du LPF, n’est pas rapportée par des éléments propres à la société et "
                "appréciés à la date des déclarations. À titre subsidiaire, la majoration doit être "
                "réduite dans la proportion de chaque grief de reconstitution écarté, son assiette "
                "étant celle des droits rappelés.")
    if not any(s.get("kind") == "interne" for s in secs):
        secs.insert(len(secs) - 1, NOTE_INTERNE_PENA)
    doc["entete"]["statut"] = "demonte"
    doc["entete"]["reponseCourte"] = (
        "Le service pose lui-même le critère du manquement délibéré, la connaissance exacte des "
        "faits qui motivent les rehaussements, alors que ces faits sont des paramètres arrêtés après "
        "le contrôle : l’intention s’apprécie à la date de la déclaration, et la dissimulation "
        "alléguée représente 27,2 fois la totalité des espèces encaissées en trois ans.")


# ------------------------------------------- RAPPELS ET PROFIT SUR TRÉSOR ----
def patch_rappels(doc):
    secs = doc["sections"]
    for s in secs:
        if s.get("kind") == "tableau" and "n’ajoute rien à la base imposable" in s.get("titre", ""):
            s["titre"] = ("Le profit sur le Trésor n’ajoute rien à la base imposable "
                          "(proposition de rectification, p. 55, 56 et 59)")
            s["lignes"][0][3] = cd("+ 20 041 €")
            s["lignes"][0][4] = cd("- 20 041 €")
        t = s.get("texte", "")
        if s.get("kind") == "paragraphe" and t.startswith("Ce sont les tableaux qui commandent"):
            s["texte"] = (
                "Ce sont les tableaux de liquidation qui commandent : le total de TVA de la page 65 "
                "(49 547 €) est bâti sur 20 041 €, la majoration de 8 016 € correspond à 40 % de "
                "20 041 €, et les intérêts de retard de 1 483 € sont calculés sur cette même base. "
                "La récapitulation de la page 56 imprime en revanche 20 421 € sur les lignes "
                "« Profit sur le trésor » et « Cascade », alors que les totaux qu’elle produit "
                "elle-même sont calculés avec 20 041 € : 39 543 + 172 813 + 20 041 = 232 397 €, puis "
                "232 397 − 20 041 = 212 356 €. Avec 20 421 €, ces totaux seraient de 232 777 € et "
                "211 976 €. Les deux autres exercices sont, eux, parfaitement cohérents.")
        if s.get("kind") == "paragraphe" and t.startswith("Une vérification s’impose"):
            s["texte"] = (
                "Une vérification s’impose avant toute mise en recouvrement. Pour l’exercice clos le "
                "31 mars 2023, le corps de la proposition retient un rappel de **20 421 €** (p. 54 "
                "et 56, ligne « TVA nette due en Euros »), tandis que les tableaux de liquidation "
                "retiennent **20 041 €** (p. 59, ligne « cascade à déduire », et p. 63, lignes "
                "« droits rappelés », « droits éludés » et « droits pénalisables »). L’écart est de "
                "**380 €**.")
    # Ajout du constat décisif après le paragraphe « Ce sont les tableaux… ».
    k = next(i for i, s in enumerate(secs)
             if s.get("kind") == "paragraphe"
             and s.get("texte", "").startswith("Ce sont les tableaux de liquidation"))
    ajout = P(
        "Cette discordance n’est pas neutre, car les deux valeurs ne servent pas au même usage. "
        "L’assiette des distributions et de l’amende de 100 %, soit **193 234,55 €** (p. 58), est "
        "construite sur 20 421,10 € : 172 813,45 + 20 421,10 = 193 234,55 exactement. La base de "
        "l’impôt sur les sociétés et les droits de TVA mis en recouvrement sont, eux, construits sur "
        "20 041 €. **Le même rappel de taxe porte donc deux montants différents dans le même "
        "document, le plus élevé servant à asseoir l’amende et le plus faible à asseoir l’impôt.** "
        "Les pages 59 et 63 s’intitulant expressément « Article L 48 du Livre des Procédures "
        "Fiscales », nous demandons que le montant exact soit arrêté et notifié avant toute mise en "
        "recouvrement, et qu’une seule et même valeur serve aux deux usages.")
    if not any("193 234,55" in s.get("texte", "") for s in secs):
        secs.insert(k + 1, ajout)
    doc["entete"]["statut"] = "demonte"
    doc["entete"]["reponseCourte"] = (
        "Le service ne défend ni le rappel de TVA ni le profit sur le Trésor pour eux-mêmes : il les "
        "fait reposer en totalité sur sa reconstitution, ses propres tableaux montrent que le profit "
        "sur le Trésor est intégralement neutralisé par la cascade, et le rappel du premier exercice "
        "y porte deux montants différents, le plus élevé servant à asseoir l’amende de 100 %.")


# ----------------------------------------------------- INTÉRÊTS DE RETARD ----
def patch_interets(doc):
    secs = doc["sections"]
    k = next(i for i, s in enumerate(secs)
             if s.get("kind") == "paragraphe"
             and s.get("texte", "").startswith(("Deux points de la liquidation",
                                                "Nous avons refait l’intégralité")))
    secs[k]["texte"] = (
        "Nous avons refait l’intégralité de la liquidation, et elle se vérifie. Le taux retenu est "
        "bien celui du III de l’article 1727, 0,20 % par mois, soit 6,8 % pour 34 mois, 4,4 % pour "
        "22 mois et 2 % pour 10 mois à l’impôt sur les sociétés, et 7,4 %, 5 % puis 2,6 % en matière "
        "de TVA. Les montants suivent : 42 908 x 6,8 % = 2 918 €, 27 120 x 4,4 % = 1 193 €, "
        "27 482 x 2 % = 550 €, puis 20 041 x 7,4 % = 1 483 €, 14 854 x 5 % = 743 € et "
        "14 652 x 2,6 % = 381 €. Le point d’arrivée, arrêté au 31 mai 2026, correspond au 4 du IV du "
        "même article, la proposition étant datée du 18 mai 2026.")
    ajout = [
        P("Deux points méritent d’être relevés, et ils jouent en faveur du service : nous les "
          "signalons pour que le débat porte sur ce qui compte. En matière de taxes sur le chiffre "
          "d’affaires, la doctrine admet que l’intérêt soit décompté « à partir du premier jour de "
          "l’exercice suivant celui sur lequel portent lesdites rectifications » "
          "([BOI-CF-INF-10-10-20](" + BOFIP_INT + "), § 100). Le service a retenu le 1er mai plutôt "
          "que le 1er avril pour les deux premiers exercices : son décompte est donc conforme, et "
          "même d’un mois plus favorable à la société que ce que la doctrine autorise."),
        P("Le § 130 du même document précise en outre que « la période comprise entre la proposition "
          "de rectification et la mise en recouvrement des impositions correspondantes est "
          "neutralisée, quelle que soit la nature de l’impôt concerné ». Aucun intérêt ne court donc "
          "depuis le 31 mai 2026, et la durée de la phase contradictoire est sans incidence sur le "
          "montant dû."),
        P("Enfin, l’intérêt de retard « présente le caractère d’une réparation pécuniaire et non "
          "d’une sanction » et, de ce fait, « n’a pas à être motivé » "
          "([BOI-CF-INF-10-10-10](" + BOFIP_NAT + "), § 1). Nous n’élevons donc aucun moyen de "
          "motivation sur ce poste : son sort est entièrement commandé par celui des droits."),
    ]
    if not any("§ 100" in s.get("texte", "") for s in secs):
        secs[k + 1:k + 1] = ajout
    for s in secs:
        if s.get("kind") == "paragraphe" and "ne se cumule pas avec l’amende" in s.get("texte", ""):
            s["texte"] = s["texte"].replace("La doctrine administrative précise",
                                            "La doctrine administrative ([BOI-CF-INF-20-10-20]("
                                            + BOFIP_CUM + "), § 20) précise")
    doc["entete"]["statut"] = "demonte"
    doc["entete"]["reponseCourte"] = (
        "Le service et nous appliquons la même règle, les intérêts suivent les droits : refaite "
        "intégralement, la liquidation des 7 268 € se vérifie et le décompte est même d’un mois plus "
        "favorable que la doctrine ne l’autorise, de sorte que ce poste tombera avec la "
        "reconstitution sans qu’aucun moyen propre ait à être élevé.")


if __name__ == "__main__":
    for slug, fn in [("penalites-et-amendes", patch_penalites),
                     ("rappels-et-profit-sur-le-tresor", patch_rappels),
                     ("interets-de-retard", patch_interets)]:
        chemin = os.path.join(DATA, slug + ".json")
        doc = json.load(open(chemin, encoding="utf-8"))
        fn(doc)
        json.dump(doc, open(chemin, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("écrit :", slug, "->", len(doc["sections"]), "sections,",
              doc["entete"]["statut"])
