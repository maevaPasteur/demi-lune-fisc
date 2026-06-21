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
    """Normalise EN PLACE, sans déplacer les pièces contextuelles (une fiche peut
    avoir un fichier téléchargeable par section : il doit rester DANS sa section)."""
    sections = [dict(s) for s in sections]

    # 1. Retirer le chapitre des pièces (gros titre) : la pièce reste une carte en place.
    sections = [s for s in sections
                if not (s.get("kind") == "chapitre" and TITRE_PIECES in _titre(s))]

    # 2. Normaliser la conclusion EN PLACE (texte normal, jamais une carte verte).
    ci = next((i for i, s in enumerate(sections)
               if s.get("kind") == "chapitre" and "conclusion" in _titre(s)), None)
    if ci is not None:
        # Les alertes qui composent la conclusion deviennent du texte normal.
        j = ci + 1
        while j < len(sections) and sections[j].get("kind") in ("paragraphe", "alerte", "note"):
            if sections[j].get("kind") == "alerte":
                sections[j] = {"kind": "paragraphe", "texte": sections[j].get("texte", "")}
            j += 1
    else:
        # Pas de chapitre Conclusion : la dernière alerte de conclusion le devient.
        ai = next((i for i in range(len(sections) - 1, -1, -1)
                   if sections[i].get("kind") == "alerte"
                   and any(k in _titre(sections[i]) for k in CLES_CONCL)), None)
        if ai is not None:
            sections[ai] = {"kind": "paragraphe", "texte": sections[ai].get("texte", "")}
            sections.insert(ai, {"kind": "chapitre", "source": "nous", "titre": "Conclusion"})

    # 3. Les notes internes (masquées) vont toujours en toute fin.
    internes = [s for s in sections if s.get("kind") == "interne"]
    sections = [s for s in sections if s.get("kind") != "interne"] + internes

    # 4. Renuméroter les chapitres séquentiellement.
    n = 0
    for s in sections:
        if s.get("kind") == "chapitre":
            n += 1
            s["numero"] = n
    return sections


# Compat : ancien nom utilisé par certains scripts.
ajouter_conclusion = normaliser_sections
