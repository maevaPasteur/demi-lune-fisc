"""Prépare cache/entrees/ : liens vers les fichiers de caisse et les pièces du dépôt, sous les noms attendus par les scripts.
À lancer depuis la racine du dépôt : python3 scripts/lot7-tables-virtuelles/prepare_entrees.py"""
import os
B = 'public/documents/'
CE = B + 'caisse-enregistreuse/'
E = 'scripts/lot7-tables-virtuelles/cache/entrees/'
L = {}
for i, (x, ex) in enumerate([('1', '2022-2023'), ('2', '2023-2024'), ('3', '2024-2025')]):
    L[f'{14+i}-annexe-e{x}-{ex}.xls'] = f'{CE}ANNEXE-E{x}_tpvevenement_{ex}.xls'
    L[f'{17+i}-annexe-c{x}-{ex}.xls'] = f'{CE}ANNEXE-C{x}_detail-tickets_{ex}.xls'
    L[f'{20+i}-annexe-f{x}-{ex}.xls'] = f'{CE}ANNEXE-F{x}_reglements_{ex}.xls'
    L[f'{24+i}-annexe-b{x}-{ex}.xls'] = f'{CE}ANNEXE-B{x}_prix-vente-quantite_{ex}.xls'
    L[f'ANNEXE-G{x}_journal-tva_{ex}.xls'] = f'{CE}ANNEXE-G{x}_journal-tva_{ex}.xls'
    L[f'ANNEXE-H{x}_liste-tickets_{ex}.xls'] = f'{CE}ANNEXE-H{x}_liste-tickets_{ex}.xls'
L['lot27/11-rf-encaissements-couverts.xlsx'] = B + 'pieces-defense/RF-encaissements-couverts.xlsx'
L['lot27/12-rf-couverts-par-service.xlsx'] = B + 'pieces-defense/RF-couverts-par-service.xlsx'
L['lot27/92-R2-tables-virtuelles-rangs-de-note-659-journees-tickets-zero-occupation.xlsx'] = B + 'pieces-reponse-2/R2-tables-virtuelles-numeros.xlsx'
L['lot27/93-R1-numeros-de-note-couverts-et-occupation-jour-par-jour.xlsx'] = B + 'pieces-reponse-1/R1-numeros-de-note-par-jour.xlsx'
L['lot27/94-R2-menus-prix-rafales-DEL-09-09-2022-et-61-conversions-au-forfait.xlsx'] = B + 'pieces-reponse-2/R2-menus-prix.xlsx'
L['lot27/157-R4-conversions-au-forfait-133-suites.xlsx'] = B + 'pieces-lot2/157-R4-conversions-au-forfait-133-suites.xlsx'
for n in ('155-R3-tables-videes-traces-egalites-paiements-separes.xlsx', '156-R3-tableau-p40-37-tickets-17-tickets-au-centime.xlsx'):
    L['lot27/vC/' + n] = B + 'pieces-lot2/' + n
for dst, src in L.items():
    p = E + dst
    os.makedirs(os.path.dirname(p), exist_ok=True)
    if not os.path.exists(src):
        print('absent :', src); continue
    if os.path.lexists(p): os.remove(p)
    os.symlink(os.path.relpath(src, os.path.dirname(p)), p)
for d in ('out/B0cache', 'out/B1', 'out/B2', 'out/B4', 'out/pieces'):
    os.makedirs('scripts/lot7-tables-virtuelles/' + d, exist_ok=True)
print(len(L), 'entrées préparées')
