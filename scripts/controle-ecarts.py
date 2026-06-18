#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
controle-ecarts.py
================================================================================
Garde-fou pour les pages du « Rendu final ».

Objet : eviter les angles morts du type « le texte affirme un seuil que les
chiffres ne soutiennent pas » (ex. « bases a moins de 0,06 % pres » alors qu'un
ecart par taux atteint 0,21 %).

Le script, pour chaque src/data/renduFinal/*.json :
  1. recalcule les ECARTS RELATIFS des tableaux de reconciliation
     (colonnes « reconstitue/caisse/applique » vs « compta/706.../attendu »),
     par paire de colonnes ET sur la somme (total) ;
  2. verifie l'ARITHMETIQUE des colonnes « Ecart » (ecart == valeur - reference) ;
  3. extrait les AFFIRMATIONS DE SEUIL du texte (« moins de X % », « a X € pres »,
     « mieux que X % », « au plus X % », « < X % »...) et les confronte aux ecarts
     reels (en distinguant la portee « total » de la portee « par poste ») ;
  4. signale deux pieges connus : un bloc « interne » laisse dans une page
     destinee au fisc (fuite a l'export), et un tableau au FORMAT PLAT
     (colonnes/cellules en chaine -> tableau vide a l'affichage).

Sortie : un rapport par page. Code de sortie 1 si au moins un FAIL.
Lecture seule. Aucune dependance externe.
"""
import os
import re
import sys
import glob
import json

ICI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(ICI, ".."))
PAGES = sorted(glob.glob(os.path.join(ROOT, "src/data/renduFinal/*.json")))

# Tolerance : un ecart de seuil n'est signale que s'il depasse la borne d'au
# moins 5 % de sa valeur (evite le bruit sur les arrondis d'affichage).
TOL = 0.05

RE_EUR = re.compile(r"(-?\d[\d   ]*(?:,\d+)?)\s*€")
RE_PCT = re.compile(r"(-?\d+(?:,\d+)?)\s*%")
NUM = r"(\d+(?:,\d+)?)"
SEUILS = [
    (re.compile(r"moins de\s+" + NUM + r"\s*(%|€)", re.I), "max"),
    (re.compile(r"au plus\s+" + NUM + r"\s*(%|€)", re.I), "max"),
    (re.compile(r"mieux que\s+" + NUM + r"\s*(%|€)", re.I), "max"),
    (re.compile(r"inf[ée]rieur[e]?\s+[àa]\s+" + NUM + r"\s*(%|€)", re.I), "max"),
    (re.compile(r"[àa]\s+" + NUM + r"\s*(%|€)\s+pr[èe]s", re.I), "max"),
    (re.compile(r"<\s*" + NUM + r"\s*(%|€)", re.I), "max"),
]
VAL_KW = re.compile(r"reconstitu|caisse|appliqu|r[ée]el", re.I)
REF_KW = re.compile(r"compt|706|445|attendu|th[ée]oriqu", re.I)
EXCL_KW = re.compile(r"brut|fisc", re.I)
ECART_KW = re.compile(r"^\s*[ée]cart", re.I)
TOTAL_KW = re.compile(r"total|global|cumul", re.I)


def fr2f(s):
    s = s.replace(" ", "").replace(" ", "").replace(" ", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def parse_eur(cell):
    m = RE_EUR.search(cell or "")
    return fr2f(m.group(1)) if m else None


def label_of(col):
    return col if isinstance(col, str) else (col.get("label", "") if isinstance(col, dict) else "")


def cellval(c):
    return c if isinstance(c, str) else (c.get("v", "") if isinstance(c, dict) else "")


def section_text(s):
    out = []
    for k in ("texte", "titre", "sousTitre", "intro"):
        v = s.get(k)
        if isinstance(v, str):
            out.append(v)
    return "\n".join(out)


def tables(sections):
    return [s for s in sections if s.get("kind") == "tableau"]


def is_flat(tab):
    cols = tab.get("colonnes") or []
    ligs = tab.get("lignes") or []
    flat_c = bool(cols) and isinstance(cols[0], str)
    flat_l = bool(ligs) and bool(ligs[0]) and isinstance(ligs[0][0], str)
    return flat_c or flat_l


def rel_errors(tab):
    """Ecarts relatifs (%) par paire valeur/reference + sur la somme (total).
    Retourne une liste de dicts {scope, pair, row, rel, v, r}."""
    cols = [label_of(c) for c in (tab.get("colonnes") or [])]
    ligs = tab.get("lignes") or []
    val_idx = [i for i, c in enumerate(cols) if VAL_KW.search(c) and not EXCL_KW.search(c)]
    ref_idx = [i for i, c in enumerate(cols) if REF_KW.search(c) and not EXCL_KW.search(c)]
    out = []
    if not val_idx or not ref_idx:
        return out
    # appariement : chaque colonne valeur avec la reference la plus proche a droite
    def nearest_ref(i):
        rights = [j for j in ref_idx if j > i]
        return min(rights) if rights else min(ref_idx, key=lambda j: abs(j - i))
    pairs = [(i, nearest_ref(i)) for i in val_idx]
    title = tab.get("titre", "")
    # somme « total » seulement si les colonnes valeur sont HOMOGENES (un meme
    # mot dans tous les libelles : « base », etc.) -> sommer base10+base20 a un
    # sens (HT total), sommer TVA+CA n'en a pas.
    def toks(lab):
        return set(re.findall(r"[a-zàâ]{3,}", lab.lower()))
    common = set.intersection(*[toks(cols[i]) for i in val_idx]) if val_idx else set()
    common -= {"reconstituee", "reconstitue", "caisse", "applique"}
    homogene = bool(common)
    for ligne in ligs:
        rowlabel = cellval(ligne[0]) if ligne else ""
        sv = sr = 0.0
        nsum = 0
        for vi, rj in pairs:
            if vi >= len(ligne) or rj >= len(ligne):
                continue
            v = parse_eur(cellval(ligne[vi]))
            r = parse_eur(cellval(ligne[rj]))
            if v is None or r is None or r == 0:
                continue
            out.append({"scope": "total" if TOTAL_KW.search(rowlabel) else "poste",
                        "pair": f"{cols[vi]} / {cols[rj]}", "row": rowlabel,
                        "rel": abs(v - r) / abs(r) * 100, "v": v, "r": r, "title": title})
            sv += v
            sr += r
            nsum += 1
        if homogene and nsum >= 2 and sr:
            out.append({"scope": "total", "pair": "somme (total) des postes", "row": rowlabel,
                        "rel": abs(sv - sr) / abs(sr) * 100, "v": sv, "r": sr, "title": title})
    return out


def check_ecart_columns(tab):
    """Verifie que toute colonne « Ecart » vaut bien valeur - reference (a 0,02 € pres)."""
    cols = [label_of(c) for c in (tab.get("colonnes") or [])]
    ligs = tab.get("lignes") or []
    problems = []
    for ei, c in enumerate(cols):
        if not ECART_KW.search(c):
            continue
        # deux colonnes euro juste avant l'ecart
        prev = [j for j in range(ei - 1, -1, -1)]
        for ligne in ligs:
            if ei >= len(ligne):
                continue
            ec = parse_eur(cellval(ligne[ei]))
            if ec is None:
                continue
            nums = []
            for j in prev:
                if j < len(ligne):
                    val = parse_eur(cellval(ligne[j]))
                    if val is not None:
                        nums.append(val)
                if len(nums) == 2:
                    break
            if len(nums) < 2:
                continue
            a, b = nums[0], nums[1]  # nums[0] = colonne la plus proche a gauche
            if min(abs((a - b) - ec), abs((b - a) - ec)) > 0.02:
                problems.append((tab.get("titre", ""), cellval(ligne[0]), c, ec, b, a))
    return problems


def scan_seuils(text):
    out = []
    for rx, kind in SEUILS:
        for m in rx.finditer(text):
            val = fr2f(m.group(1))
            unit = m.group(2)
            snip = re.sub(r"\s+", " ", text[max(0, m.start() - 55):m.end() + 5]).strip()
            # portee : fenetre large (la mention « HT total » est souvent en debut
            # de phrase, avant le seuil)
            ctx = text[max(0, m.start() - 130):m.end() + 20]
            scope = "total" if TOTAL_KW.search(ctx) or re.search(r"ht total", ctx, re.I) else "poste"
            out.append({"val": val, "unit": unit, "kind": kind, "snip": snip, "scope": scope})
    return out


def table_summary(t):
    """Resume d'un tableau de reconciliation : max ecart relatif par portee + max ecart €."""
    rels = rel_errors(t)
    summ = {"poste": (0.0, None), "total": (0.0, None)}
    for r in rels:
        if r["rel"] > summ[r["scope"]][0]:
            summ[r["scope"]] = (r["rel"], r)
    max_eur = 0.0
    cols = [label_of(c) for c in (t.get("colonnes") or [])]
    for ci, lab in enumerate(cols):
        if ECART_KW.search(lab):
            for ligne in (t.get("lignes") or []):
                if ci < len(ligne):
                    v = parse_eur(cellval(ligne[ci]))
                    if v is not None:
                        max_eur = max(max_eur, abs(v))
    return {"recon": bool(rels), "poste": summ["poste"], "total": summ["total"],
            "max_eur": max_eur, "titre": t.get("titre", "")}


def main():
    fails = 0
    warns = 0
    for path in PAGES:
        name = os.path.basename(path)
        doc = json.load(open(path, encoding="utf-8"))
        sections = doc.get("sections", doc if isinstance(doc, list) else [])
        if isinstance(doc, dict) and doc.get("kind"):
            sections = [doc]
        if not isinstance(sections, list):
            continue
        lines = []

        # index des tableaux de reconciliation (avec leur position)
        recon = []  # (idx, summary)
        for i, s in enumerate(sections):
            if s.get("kind") == "tableau":
                summ = table_summary(s)
                if summ["recon"]:
                    recon.append((i, summ))

        def nearest(idx):
            return min(recon, key=lambda t: abs(t[0] - idx))[1] if recon else None

        # 1) FAIL mecanique : arithmetique des colonnes Ecart + format plat
        for t in tables(sections):
            for pb in check_ecart_columns(t):
                lines.append(f"  FAIL  arithmetique : « {pb[2]} » affiche {pb[3]:.2f} € mais "
                             f"{pb[5]:.2f} - {pb[4]:.2f} (ligne {pb[1]!r}, tableau {pb[0]!r})")
                fails += 1
            if is_flat(t):
                lines.append(f"  FAIL  tableau au format plat (rendu vide) : {t.get('titre','')!r}")
                fails += 1

        # 2) WARN : bloc interne (fuite a l'export)
        if any(s.get("kind") == "interne" for s in sections):
            lines.append("  WARN  bloc « interne » present (fuite a l'export d'une page fisc-facing)")
            warns += 1

        # 3) WARN « a verifier » : seuil annonce > ecart reel du tableau le plus proche
        nseuils = 0
        for i, s in enumerate(sections):
            for cl in scan_seuils(section_text(s)):
                if cl["val"] is None:
                    continue
                nseuils += 1
                tb = nearest(i)
                if not tb:
                    continue
                if cl["unit"] == "%":
                    sc = cl["scope"]
                    # pas de repli : un seuil « total » non verifiable (pas de
                    # donnee total) n'est pas compare aux ecarts par poste.
                    rel, ref = tb[sc]
                    if rel and rel > cl["val"] * (1 + TOL):
                        loc = f"{ref['pair']}, ligne {ref['row']!r}" if ref else ""
                        lines.append(f"  WARN  a verifier : « ...{cl['snip'][-48:]} » -> "
                                     f"ecart {rel:.3f} % observe ({loc} ; tableau {tb['titre'][:40]!r})")
                        warns += 1
                else:  # €
                    # un seuil « a X € pres » qui parle du bouclage / CA TTC / somme
                    # ne se compare pas aux colonnes « Ecart » (autre grandeur).
                    if re.search(r"ca ttc|boucl|somme|total", cl["snip"], re.I):
                        continue
                    if tb["max_eur"] and tb["max_eur"] > cl["val"] * (1 + TOL):
                        lines.append(f"  WARN  a verifier : « ...{cl['snip'][-48:]} » -> "
                                     f"ecart jusqu'a {tb['max_eur']:.2f} € (tableau {tb['titre'][:40]!r})")
                        warns += 1

        status = "FAIL" if any("FAIL" in l for l in lines) else ("WARN" if lines else "OK")
        head = f"[{status}] {name}"
        if recon:
            mp = max(t[1]["poste"][0] for t in recon)
            mt = max(t[1]["total"][0] for t in recon)
            head += f"  | reconciliation : {len(recon)} tableau(x), ecart max poste {mp:.3f} % / total {mt:.3f} %"
        if nseuils:
            head += f"  | {nseuils} seuil(s)"
        print(head)
        for l in lines:
            print(l)

    print()
    print(f"Resultat : {fails} FAIL, {warns} WARN sur {len(PAGES)} pages.")
    print("Note : les FAIL (arithmetique, format plat) sont fiables ; les WARN "
          "« a verifier » sont des candidats a relire (le seuil peut viser un autre "
          "perimetre que le tableau le plus proche).")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
