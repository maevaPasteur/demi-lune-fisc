# -*- coding: utf-8 -*-
"""Normalisation commune de la mise en page des fiches /rendu-final.

Règles imposées à TOUTES les pages (cf. consignes mise en page) :
  1. Les pièces téléchargeables ne sont PAS une section à gros titre : juste une
     carte (piecejointe). On supprime tout chapitre « Toutes les pièces ... ».
  2. Tous les grands titres de section (chapitre) sont numérotés séquentiellement.
  3. La conclusion est la DERNIÈRE section titrée (chapitre « Conclusion »).
  4. Son texte est du texte normal (paragraphe), jamais une carte verte (alerte).
  5. Ordre final : … contenu … → Conclusion → carte « pièces à télécharger »
     (en tout dernier visible) → notes internes (masquées).
"""

CLES_CONCL = (
    "résultat", "resultat", "conclusion",
    "ce qu'il faut retenir", "ce qu’il faut retenir",
    "ce que ce grief fait tomber",
)
TITRE_PIECES = "pièces téléchargeable"  # sous-chaîne du chapitre à supprimer


def _titre(s):
    return (s.get("titre") or "").lower()


def normaliser_sections(sections):
    # 1. Retirer le chapitre des pièces (la pièce reste une simple carte).
    sections = [s for s in sections
                if not (s.get("kind") == "chapitre" and TITRE_PIECES in _titre(s))]

    # 2. Mettre de côté les internes (toujours en dernier, masqués) et les pièces.
    internes = [s for s in sections if s.get("kind") == "interne"]
    pieces = [s for s in sections if s.get("kind") == "piecejointe"]
    rest = [s for s in sections if s.get("kind") not in ("interne", "piecejointe")]

    # 3. Isoler le bloc conclusion et récupérer son/ses texte(s).
    concl_textes = []
    idx_chap = next((i for i, s in enumerate(rest)
                     if s.get("kind") == "chapitre" and "conclusion" in _titre(s)), None)
    if idx_chap is not None:
        body = rest[:idx_chap]
        for s in rest[idx_chap + 1:]:
            if s.get("kind") in ("paragraphe", "alerte", "note") and s.get("texte"):
                concl_textes.append(s["texte"])
            # tout autre kind après le chapitre Conclusion est ignoré (cas non prévu)
    else:
        idx_al = next((i for i in range(len(rest) - 1, -1, -1)
                       if rest[i].get("kind") == "alerte"
                       and any(k in _titre(rest[i]) for k in CLES_CONCL)), None)
        if idx_al is not None:
            if rest[idx_al].get("texte"):
                concl_textes.append(rest[idx_al]["texte"])
            body = rest[:idx_al] + rest[idx_al + 1:]
        else:
            body = rest

    # 4. Reconstituer : contenu → Conclusion (texte normal) → pièces → internes.
    out = list(body)
    if concl_textes:
        out.append({"kind": "chapitre", "source": "nous", "titre": "Conclusion"})
        for t in concl_textes:
            out.append({"kind": "paragraphe", "texte": t})
    out.extend(pieces)
    out.extend(internes)

    # 5. Renuméroter tous les chapitres séquentiellement.
    n = 0
    for s in out:
        if s.get("kind") == "chapitre":
            n += 1
            s["numero"] = n
    return out


# Compat : ancien nom utilisé par certains scripts.
ajouter_conclusion = normaliser_sections
