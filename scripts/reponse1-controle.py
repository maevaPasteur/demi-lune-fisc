#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contrôle qualité de l'onglet /reponse-1/ : complétude, format, liens, style."""
import os, json, re, glob

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DATA = os.path.join(ROOT, "src/data/reponse1")
DOCS = os.path.join(ROOT, "public/documents")

slugs = re.findall(r"slug: '([a-z0-9-]+)'", open(os.path.join(ROOT, "src/data/reponse1.ts"),
                                                 encoding="utf-8").read())
pb = []
present = {os.path.basename(f)[:-5] for f in glob.glob(DATA + "/*.json")}

for s in slugs:
    if s not in present:
        pb.append(f"[MANQUANT] {s}.json")
        continue
    d = json.load(open(os.path.join(DATA, s + ".json"), encoding="utf-8"))
    secs = d.get("sections", [])
    ent = d.get("entete", {})
    txt = json.dumps(d, ensure_ascii=False)

    if not ent.get("positionService"):
        pb.append(f"[EN-TÊTE] {s} : positionService vide")
    if not ent.get("reponseCourte"):
        pb.append(f"[PHASE 2] {s} : reponseCourte vide (réfutation non rédigée ?)")
    if ent.get("statut") not in ("demonte", "partiel", "a-etayer"):
        pb.append(f"[EN-TÊTE] {s} : statut = {ent.get('statut')!r}")
    if not any(x.get("kind") == "chapitre" and x.get("source") == "fisc" for x in secs):
        pb.append(f"[STRUCTURE] {s} : pas de chapitre « fisc »")
    if not any(x.get("kind") == "chapitre" and x.get("source") == "nous" for x in secs):
        pb.append(f"[STRUCTURE] {s} : pas de chapitre « nous » (réfutation absente)")
    if any(x.get("kind") == "chapitre" and "réfuter" in x.get("titre", "") for x in secs):
        pb.append(f"[STRUCTURE] {s} : le chapitre de travail « Ce qu'il faut réfuter » subsiste")
    for c in ("—", "–"):
        if c in txt:
            n = txt.count(c)
            pb.append(f"[STYLE] {s} : {n} occurrence(s) de « {c} »")
    # Fichiers joints réellement présents
    for sec in secs:
        if sec.get("kind") == "piecejointe":
            for f in sec.get("fichiers", []):
                if not os.path.exists(os.path.join(DOCS, f["fichier"])):
                    pb.append(f"[LIEN MORT] {s} : {f['fichier']}")
    # Liens internes /reponse-1/<slug>
    for m in re.findall(r"/reponse-1/([a-z0-9-]+)", txt):
        if m not in slugs:
            pb.append(f"[LIEN INTERNE] {s} : /reponse-1/{m} n'existe pas")
    # Tables : nombre de colonnes cohérent
    for i, sec in enumerate(secs):
        if sec.get("kind") == "tableau":
            n = len(sec.get("colonnes", []))
            for j, ln in enumerate(sec.get("lignes", [])):
                if len(ln) != n:
                    pb.append(f"[TABLEAU] {s} §{i} ligne {j} : {len(ln)} cellules pour {n} colonnes")
                    break

print(f"{len(slugs)} pages attendues, {len(present & set(slugs))} présentes.")
if pb:
    print(f"\n{len(pb)} anomalie(s) :")
    for x in pb:
        print(" ", x)
else:
    print("Aucune anomalie.")
