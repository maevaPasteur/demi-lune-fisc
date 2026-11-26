"""Vidage formules / valeurs des pièces 89, 90, 91, 87, 72 de la société (sortie : out/s12_dump_pieces.txt)."""
import openpyxl, sys
P='public/documents/caisse-enregistreuse/'
sys.stdout=open('scripts/lot6-evenement-reglement/out/s12_dump_pieces.txt','w')
def dump(f,sheets,maxr=60):
    wf=openpyxl.load_workbook(P+f); wv=openpyxl.load_workbook(P+f,data_only=True)
    for sn in sheets:
        print(f'##### {f} :: {sn}')
        ws=wf[sn]; vs=wv[sn]
        for row in ws.iter_rows(min_row=1,max_row=min(ws.max_row,maxr)):
            cells=[]
            for c in row:
                if c.value is None: continue
                v=vs[c.coordinate].value
                if isinstance(c.value,str) and c.value.startswith('='): cells.append(f'{c.coordinate}={c.value!s:.90} -> {v!r}')
                else: cells.append(f'{c.coordinate}:{str(c.value)[:160]!r}')
            if cells: print(' | '.join(cells))
dump('89-R2-fichiers-E-F-C-reconciliation-DEL-reglements-CA-quantites-TVA-3-exercices.xlsx',['Methode','Remises','Calcul'])
dump('90-R1-compteur-perpetuel-deux-series-quatre-montants-B-dans-C.xlsx',['0 - Méthode','1 - Compteur perpétuel','2 - Les deux séries','3 - Les quatre montants','4 - Écart des deux lectures','5 - Annexe B dans annexe C','7 - Colonne de contrôle'])
dump('90-R1-compteur-perpetuel-deux-series-quatre-montants-B-dans-C.xlsx',['6 - Lignes de C absentes de B'],maxr=8)
dump('91-R1-reconciliation-annexes-A-B-C-F-G-H-quantites-exemple-14-04-2022.xlsx',['1 CA par annexe','2 Compteur perpetuel','3 Quantites B vs C','4 Exemple 14-04-2022','6 Colonnes TVA du service'])
dump('91-R1-reconciliation-annexes-A-B-C-F-G-H-quantites-exemple-14-04-2022.xlsx',['5 Lignes C absentes de B'],maxr=8)
dump('87-R3-tva-colonnes-E-et-F-annexes-C-corrections-de-taux-erratum.xlsx',['Erratum R2','2 Somme de la colonne F','3 Incidence reelle','5 Taux par article'])
dump('72-R2-suppressions-DEL-rapprochement-ventilation-en-euros-3-exercices.xlsx',['Méthode','Synthèse','prix exact'],maxr=12)
