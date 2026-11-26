"""Module commun : chemins, fichiers d'entrée, constantes de la p. 26 de la proposition, conversions en centimes
et chargement des tables mises en cache par s00_charger.py (annexes C, G, H, F, E).
Tous les chemins sont relatifs à la racine du dépôt (calculée depuis l'emplacement du présent fichier)."""
import os, subprocess
import pandas as pd, numpy as np, xlrd, unicodedata, re

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.abspath(os.path.join(ICI, '..', '..'))
DOCS = os.path.join(RACINE, 'public', 'documents')
CAISSE = os.path.join(DOCS, 'caisse-enregistreuse') + os.sep
CA = os.path.join(ICI, 'cache') + os.sep          # tables intermédiaires (.pkl)
C23 = CA                                          # tables de base (s00_charger.py), même dossier
OUT = os.path.join(CA, 'out') + os.sep            # sorties texte et .csv
PIECES = os.path.join(CA, 'pieces') + os.sep      # pièces régénérées (.xlsx)
for _d in (CA, OUT, OUT + 'b1', OUT + 'b4', PIECES): os.makedirs(_d, exist_ok=True)
D = ''                                            # les listes de fichiers ci-dessous sont des chemins complets

EX = ['2022-2023', '2023-2024', '2024-2025']
_NOMS = {'B': 'prix-vente-quantite', 'C': 'detail-tickets', 'E': 'tpvevenement', 'F': 'reglements', 'G': 'journal-tva', 'H': 'liste-tickets'}
def annexe(lettre, k):
    """Chemin de l'annexe de caisse lettre-k (k = 1, 2, 3 pour les trois exercices)."""
    return CAISSE + f'ANNEXE-{lettre}{k}_{_NOMS[lettre]}_{EX[k-1]}.xls'
GF = [annexe('G', k) for k in (1, 2, 3)]
HF = [annexe('H', k) for k in (1, 2, 3)]
CF = [annexe('C', k) for k in (1, 2, 3)]
FF = [annexe('F', k) for k in (1, 2, 3)]
SOURCE_REGLEMENT = CAISSE + 'SOURCE-reglement-brut_2022-2025.xls'

def entree(rel):
    """Pièce antérieure servant d'entrée. Si elle n'est plus dans public/, sa dernière version enregistrée dans
    l'historique git est extraite dans cache/entrees/."""
    p = os.path.join(RACINE, rel)
    if os.path.exists(p): return p
    dst = os.path.join(CA, 'entrees', os.path.basename(rel))
    if not os.path.exists(dst):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        git = lambda *a: subprocess.run(['git', '-C', RACINE, *a], check=True, capture_output=True).stdout
        try: data = git('show', f'HEAD:{rel}')
        except subprocess.CalledProcessError:
            c_ = git('rev-list', '-n', '1', 'HEAD', '--', rel).decode().strip()   # commit qui a supprimé le fichier
            data = git('show', f'{c_}^:{rel}')
        with open(dst, 'wb') as f: f.write(data)
    return dst
# Pièces d'origine reprises par les errata (n° 38, 85, 86, 87, 88) et extrait CSV n° 36.
PIECE_38 = entree('public/documents/pieces-defense/RF-anomalies-tva.xlsx')
PIECE_36 = entree('public/documents/pieces-defense/RF-tva-1-extrait-fichier-caisse.csv')
PIECE_85 = entree('public/documents/pieces-reponse-2/R2-tva-bouclage.xlsx')
PIECE_86 = entree('public/documents/pieces-reponse-1/R1-tva-rapprochement.xlsx')
PIECE_87 = entree('public/documents/pieces-reponse-1/R1-tva-colonnes-ef.xlsx')
PIECE_88 = entree('public/documents/pieces-reponse-1/R1-taux-tva-et-encaissements.xlsx')

# p. 26 de la proposition
P26={'706000':[64712.51,72416.55,70517.47],'706300':[296105.87,319179.31,318345.43],
     '706800':[598.04,597.75,656.57],'445710':[42614.45,46464.79,46005.45],'TOT':[404030.87,438658.43,435524.92]}
P26G={'CA':[403324.72,437881.12,434709.26],'TVA':[42548.21,46387.76,45914.28],'B10':[269445.43,296113.00,296625.31],
      'B20':[-11645.01,-1680.08,572.55],'T10':[29611.10,31917.44,31852.20],'T20':[12941.66,14482.64,14074.43]}
c=lambda x: int(round(float(x)*100))      # centimes exacts
e=lambda n: f"{n/100:,.2f}".replace(',',' ').replace('.',',')
def tmin(h):
    a,b=str(h).split(':'); return int(a)*60+int(b)
def loadG():
    G=pd.read_pickle(C23+'G.pkl'); G=G.rename(columns={'Base TVA10\xa0%':'B10s','TVA10\xa0%':'T10s','Base TVA20\xa0%':'B20s','TVA20\xa0%':'T20s'})
    for k in ['tot_ttc','tot_tva','tot_sum','tot_tax_sum','VAT_base','tax_amount']: G[k+'_c']=G[k].map(c)
    G['tk']=G.ex+'|'+G.dateTicket+'|'+G.heureTicket+'|'+G.noTicket.astype(str)+'|'+G.no_zReport.astype(str)
    return G
def loadH(): return pd.read_pickle(C23+'H.pkl')
def loadC():
    CC=pd.read_pickle(C23+'CC.pkl'); CC['Es']=CC.Es.astype(str).str.replace('\xa0',' ')
    return CC
