#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REPONSE 1 - Mise en cohérence des PAGES sur la cascade des 10 622 L.

ATTENTION : ce script n'est plus producteur de la cascade. Il la CONSOMME.
La seule source de vérité est scripts/reponse1-cascade-valeurs.py, qui écrit
src/data/reponse1Calculs/cascade-10622.json et la pièce
R1-cascade-bilan-matiere.xlsx. Ce script se borne à réécrire les sections
chiffrées de la page « cascade-10622-litres » à partir de ce JSON.
Lancer d'abord reponse1-cascade-valeurs.py.

Il ÉCRIT dans src/data/reponse1/ : ne pas le lancer tant que la vague de
correction des pages n'a pas été passée sur la fiche 12-cascade-unifiee.md.

Trois postes ont été corrigés A LA BAISSE dans les sous-pages, après
vérification contradictoire sur les factures et sur le stock :
  - crémant           347 L -> 272 L (borné par le stock, page recon-3)
  - sur-versement     720 L -> 494 L (assiette par assiette, page N)
  - alcool de cuisine 794 L -> 745 L (plafonné aux factures, pages 5, 6 et R)
  - freinte bière    129 L -> 122 L (assiette corrigée : le taux de 10 % est
    appliqué à la bière réellement sortie du fût, 1 219,2 L lus en caisse, et
    non à la contenance des verres, 1 292,9 L, qui comprend 73,7 L de limonade,
    de grenadine et de Picon ; pages O et L)
    ATTENTION : 745 L est le volume PHYSIQUEMENT consommé en cuisine, seul pertinent
    dans un bilan matière. Les 173 L cités dans la page 5 sont autre chose : c'est le
    supplément demandé au service, une fois retranché ce qu'il déduit déjà lui-même
    dans sa reconstitution (repères D, E, G et Q).
Ce script répercute ces corrections sur la page de cadrage chiffrée du bloc 3
(partie M), de sorte qu'aucun chiffre du site ne se contredise. La partie L ne
porte plus de volume poste par poste : elle n'est plus patchée ici.

Idempotent : il réécrit toujours les mêmes sections à partir des valeurs
ci-dessous. Exécution : python3 scripts/reponse1-cascade-coherence.py
"""
import os, json

# --- NEUTRALISE le 13/09/2026 ------------------------------------------------
# Ce script patche la page cascade-10622-litres PAR INDEX DE SECTION, et son
# texte est perime : il porte encore 795 L, 745 L et 173 L, alors que la
# partition retenue est 10 622 = 8 394 (79,0 %) + 2 228 (21,0 %) et que la page
# a ete entierement reecrite (55 -> 77 sections). Le lancer detruirait la page
# et remettrait des valeurs fausses aux mauvais endroits.
#
# Le producteur unique de la cascade est desormais reponse1-cascade-valeurs.py,
# controle par reponse1-cascade-controle.py (24 controles).
# Pour relancer celui-ci sciemment, exporter REPONSE1_CASCADE_COHERENCE_FORCE=1,
# apres avoir reecrit ses index et ses textes.
import os as _os
if not _os.environ.get("REPONSE1_CASCADE_COHERENCE_FORCE"):
    raise SystemExit(
        "reponse1-cascade-coherence.py est neutralise : il patche la page par "
        "index avec un texte perime. Voir le commentaire en tete de fichier."
    )


ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DATA = os.path.join(ROOT, "src/data/reponse1")

_CASC = os.path.join(ROOT, "src/data/reponse1Calculs/cascade-10622.json")
if not os.path.exists(_CASC):
    raise SystemExit("Lancer d'abord : python3 scripts/reponse1-cascade-valeurs.py")
CASC = json.load(open(_CASC, encoding="utf-8"))

ACHATS = int(round(CASC["achats_l"]))

# (clé, libellé, litres, nature, source, page de démonstration, slug)
POSTES = [(p["cle"], p["libelle"], p["litres_arrondi"], p["nature"], p["source"],
           p["page"], p["slug"]) for p in CASC["postes"]]

JUSTIFIE = CASC["attribue_arrondi_l"]
RESIDU = CASC["residu_arrondi_l"]
PCT_RESIDU = 100 * RESIDU / ACHATS
PCT_JUSTIFIE = 100 * JUSTIFIE / ACHATS
MESURE = CASC["nature"]["mesure"]["litres_arrondi"]
CALCUL = CASC["nature"]["calcul"]["litres_arrondi"]
ESTIME = CASC["nature"]["estime"]["litres_arrondi"]
CAISSE = MESURE + CALCUL
ASS = {a["cle"]: a for a in CASC["assiettes"]}

N = lambda x, d=0: f"{x:,.{d}f}".replace(",", " ").replace(".", ",")
P = lambda x, d=1: f"{x:,.{d}f}".replace(",", " ").replace(".", ",") + " %"
cg = lambda v, **k: dict(v=v, **k)
cd = lambda v, **k: dict(v=v, align="right", **k)
NATURE = {"mesure": "mesuré", "calcul": "calculé", "estime": "estimé"}


def barre():
    return {
        "kind": "barreComposition",
        "titre": "Où passent les 10 622 L d’alcool achetés, après les six corrections que nous portons",
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


# La pièce R1-cascade-bilan-matiere.xlsx est produite par
# scripts/reponse1-cascade-valeurs.py, seul producteur de la cascade.
# Ce script ne l'écrit plus.


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
            f"**Près des trois quarts du bilan reposent sur la caisse.** {N(MESURE)} L sont lus "
            f"directement dans la caisse ou dans l’inventaire et {N(CALCUL)} L sont calculés à "
            f"partir de quantités lues en caisse, soit {P(100 * CAISSE / ACHATS)} des achats. Les "
            f"postes estimés à partir d’un taux publié ne pèsent que {N(ESTIME)} L, soit "
            f"{P(100 * ESTIME / ACHATS)} des achats. L’objection selon laquelle notre méthode "
            f"serait une construction d’hypothèses ne correspond pas à ce qu’elle contient."),
        31: {"kind": "titre", "texte": "Six corrections que nous apportons contre nous-mêmes"},
        32: para(
            "Le service a formulé trois objections qui portent, et nous les intégrons. Nous en "
            "ajoutons trois que nous avons trouvées nous-mêmes en reprenant notre propre "
            "pipeline de calcul. Sur le "
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
            "propre reconstitution : nous ne lui en demandons que **173 L de plus**. "
            "Sur la [perte de bière](/reponse-1/perte-de-biere), notre assiette incluait la "
            "contenance des verres, limonade, grenadine et Picon compris : ramenée à la bière "
            "réellement sortie du fût, 1 205,0 L lus en caisse, la freinte tombe de 129 L à "
            "**120 L**. Sur le poste « vendu au verre », le panaché, le Monaco et le Picon "
            "bière étaient comptés pour la contenance entière du verre alors que leur alcool "
            "est déjà porté par le poste « vendu en cocktails » : **296 L étaient comptés deux "
            "fois**, nous les retirons. Sur les offerts enfin, les 25,8 L d’alcool sonnés à "
            "0,00 € figurent déjà dans les ventes : le poste tombe de 40 L à **14 L**."),
        33: para(
            f"Ces six corrections jouent contre nous et nous les portons quand même, parce qu’un "
            f"bilan matière n’a de valeur que s’il est rectifié dès qu’il est pris en défaut. Le "
            f"volume attribué à un poste identifié passe de 9 079 L à **{N(JUSTIFIE)} L** "
            f"({P(PCT_JUSTIFIE)}) et la perte pure de 1 543 L à **{N(RESIDU)} L**, soit "
            f"**{P(PCT_RESIDU)}** des achats. **Elles ne libèrent aucun litre pour une vente "
            f"dissimulée** : un litre qui cesse d’être « justifié poste par poste » devient de la "
            f"perte non ventilée, il ne devient pas une recette. Dans les deux cas, il n’a pas été "
            f"vendu, et la reconstitution, qui suppose des doses exactes et zéro perte, le compte "
            f"comme s’il l’avait été. **Aucun litre ne figure dans deux postes** : le panaché, "
            f"le Monaco et le Picon bière ne sont portés que par le poste des cocktails, les "
            f"offerts enregistrés à 0,00 € ne sont portés que par les postes de vente, et les "
            f"173 L de supplément d’alcool de cuisine demandés au service ne sont pas un poste "
            f"de la cascade mais une demande : ils ne s’y ajoutent pas."),
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
    # La page « reconstitution-cadre-general » (partie L) ne fige plus aucun volume
    # poste par poste : elle porte la méthode et le droit du bloc, et renvoie à la
    # partie M pour le chiffrage. Elle n'est donc plus patchée ici, et aucune
    # correction de volume n'a d'incidence sur son texte.

    print(f"\nCascade : {N(ACHATS)} L achetés = {N(JUSTIFIE)} L justifiés ({P(PCT_JUSTIFIE)}) "
          f"+ {N(RESIDU)} L de résidu ({P(PCT_RESIDU)})")
    print(f"  mesuré {N(MESURE)} L / calculé {N(CALCUL)} L / estimé {N(ESTIME)} L")


if __name__ == "__main__":
    main()
