"""Convertit la section 2.6 (Markdown, format de l'export du Google Doc) en sections JSON du site.

Usage : python3 md_to_page.py <section.md> <page.json existante> <sortie.json>
Les sections « schema » de la page existante (figures 26 et 27) sont reprises telles quelles.
"""
import json
import re
import sys

src, old_page, out = sys.argv[1:4]
L = open(src, encoding='utf-8').read().split('\n')
old = json.load(open(old_page, encoding='utf-8'))
schemas = [s for s in old['sections'] if s['kind'] == 'schema']

# Libellés RPR / CON / TIR : sens non documenté (lot 2.2, D100 à D102)
LIB = {
    'RPR : reprise d’une note': 'RPR : événement sans montant, de sens non documenté',
    'CON : consultation ou contrôle': 'CON : événement sans montant, de sens non documenté',
    'TIR : ouverture du tiroir': 'TIR : événement sans montant, de sens non documenté',
}


def _clean(t, keep_bold=True):
    t = t.replace('\\\\+', '+').replace('\\+', '+').replace('\\*\\*', '**').replace('\\*', '\u2217')
    t = t.replace('\\[', '[').replace('\\]', ']').replace('\\_', '_')
    t = t.replace('\\*\\*', '**')
    if not keep_bold:
        t = t.replace('*', '')
        return t.strip()
    t = re.sub(r'\*{3,}', '', t)  # gras + italique mêlés : retirés
    t = re.sub(r'(?<!\*)\*(?!\*)([^*\n]+?)(?<!\*)\*(?!\*)', r'\1', t)  # italique retiré
    t = re.sub(r'\*\*\s*\*\*', '', t)
    for a, b in LIB.items():
        t = t.replace(a, b)
    return t.strip()


def clean(t, keep_bold=True):
    return _clean(t, keep_bold).replace('\u2217', '*')


def indent(line):
    return len(line) - len(line.lstrip(' '))


sections = []
reponse_courte = None
sous_titre = None
i = 0
n = len(L)
current_title = None
in_position = False


def push(s):
    sections.append(s)


def parse_list(i):
    """Liste à puces imbriquée (indentations 2, 6, 10) ou numérotée."""
    items = []
    stack = []  # (niveau, liste d'items)
    numbered = bool(re.match(r'^\d+\.\s', L[i]))
    while i < n:
        line = L[i]
        if not line.strip():
            # fin de liste si la ligne suivante non vide n'est pas un élément ou une suite
            j = i + 1
            while j < n and not L[j].strip():
                j += 1
            if j < n and (re.match(r'^\s*- ', L[j]) or (numbered and re.match(r'^\d+\.\s', L[j]))):
                i = j
                continue
            break
        m = re.match(r'^(\s*)- (.*)$', line)
        mn = re.match(r'^(\d+)\.\s+(.*)$', line) if numbered else None
        if m or mn:
            lvl = 0 if mn else {0: 0, 2: 0, 4: 1, 6: 1, 8: 2, 10: 2}.get(len(m.group(1)), 2)
            txt = clean((mn or m).group(2))
            node = {'texte': txt, 'sous': []}
            if lvl == 0:
                items.append(node)
                stack = [node]
            else:
                parent = stack[min(lvl, len(stack)) - 1]
                parent['sous'].append(node)
                stack = stack[:min(lvl, len(stack))] + [node]
            i += 1
            continue
        if indent(line) >= 2 and stack:
            # ligne de suite d'un élément (après ses sous-puces)
            target = stack[0] if indent(line) <= 4 else stack[-1]
            target['suite'] = (target.get('suite', '') + ' ' + clean(line)).strip()
            i += 1
            continue
        break

    def simplify(node):
        if not node['sous'] and 'suite' not in node:
            return node['texte']
        d = {'texte': node['texte']}
        if node['sous']:
            d['sous'] = [simplify(x) for x in node['sous']]
        if 'suite' in node:
            d['suite'] = node['suite']
        return d

    sec = {'kind': 'liste', 'items': [simplify(x) for x in items]}
    if numbered:
        sec['style'] = 'numeros'
    return sec, i


def parse_table(i, titre):
    rows = []
    while i < n and L[i].strip().startswith('|'):
        cells = [c.strip() for c in L[i].strip().strip('|').split('|')]
        rows.append(cells)
        i += 1
    rows = [r for r in rows if not all(re.fullmatch(r':?-+:?', c) or c == '' for c in r) or all(c == '' for c in r)]
    if rows and all(c == '' for c in rows[0]):
        rows = rows[1:]
    head, body = rows[0], rows[1:]
    head = [clean(c, keep_bold=False) for c in head]
    ncol = len(head)
    colonnes = [{'label': h} if k == 0 else {'label': h, 'align': 'right'} for k, h in enumerate(head)]
    lignes = []
    for r in body:
        r = (r + [''] * ncol)[:ncol]
        ligne = []
        for k, c in enumerate(r):
            v = clean(c)
            cell = {'v': v}
            if v.startswith('**') and v.endswith('**') and v.count('**') == 2:
                cell = {'v': v[2:-2], 'fw': 700}
            if k > 0:
                cell['align'] = 'right'
            ligne.append(cell)
        lignes.append(ligne)
    width = 640 if ncol <= 4 else (760 if ncol <= 6 else 900)
    return {'kind': 'tableau', 'titre': titre, 'minWidth': width, 'colonnes': colonnes, 'lignes': lignes}, i


while i < n:
    line = L[i]
    s = line.strip()
    if not s or s == ' ' or s == '##':
        i += 1
        continue
    if s.startswith('## **2.6.'):
        i += 1
        continue
    if s.startswith('## ') and reponse_courte is None:
        reponse_courte = clean(s[3:])
        i += 1
        continue
    if reponse_courte is not None and sous_titre is None and not s.startswith('#'):
        sous_titre = clean(s)
        push({'kind': 'chapitre', 'source': 'neutre', 'numero': 1,
              'titre': 'Les fichiers Événement et Règlement (grief G)', 'sousTitre': sous_titre})
        push({'kind': '__kpis__'})
        i += 1
        continue
    m = re.match(r'^###\s+\*\*(2\.6\.\d+)\.\s+(.*?)\*\*\s*$', s)
    if m:
        push({'kind': 'titre', 'numero': m.group(1), 'texte': clean(m.group(2))})
        in_position = False
        i += 1
        continue
    m = re.match(r'^####\s+\*\*(.*?)\*\*\s*$', s)
    if m:
        t = clean(m.group(1))
        if t.startswith('Pièces annexées'):
            push({'kind': 'titre', 'texte': t})
            in_position = False
        else:
            push({'kind': 'titre', 'texte': t})
            in_position = t.endswith('La position du service')
        i += 1
        continue
    if s.startswith('**Tableau '):
        titre = clean(s, keep_bold=False)
        i += 1
        while i < n and not L[i].strip():
            i += 1
        sec, i = parse_table(i, titre)
        push(sec)
        in_position = False
        continue
    if re.match(r'^\*Figure \d+\.', s):
        num = int(re.match(r'^\*Figure (\d+)', s).group(1))
        sch = schemas[0] if num == 26 else schemas[1]
        push(sch)
        push({'kind': 'note', 'texte': clean(s)})
        i += 1
        continue
    if s.startswith('*Références juridiques'):
        push({'kind': 'paragraphe', 'texte': clean(s)})
        i += 1
        continue
    if re.match(r'^\*[^*].*\*$', s):  # légende en italique
        push({'kind': 'note', 'texte': clean(s)})
        i += 1
        continue
    if re.match(r'^(\s*- |\d+\.\s)', line):
        sec, i = parse_list(i)
        push(sec)
        continue
    # paragraphe
    t = clean(s)
    if in_position and not t.startswith(('Ce motif', 'Le montant de 435')):
        if sections and sections[-1]['kind'] == 'reproche':
            sections[-1]['resume'].append(t)
        else:
            mp = re.match(r'^(Pages? [^:]*?)\s*:', t)
            push({'kind': 'reproche', 'resume': [t]})
    else:
        push({'kind': 'paragraphe', 'texte': t})
    i += 1

json.dump({'reponseCourte': reponse_courte, 'sections': sections}, open(out, 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('sections', len(sections))
