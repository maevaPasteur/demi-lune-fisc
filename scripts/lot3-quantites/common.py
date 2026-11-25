"""Module commun : chemins, normalisation des libellés et chargement des tables mises en cache.
Données : annexe C primaire (enrichie des colonnes de l'annexe B), F, E, horaires des notes, recomposition des tables.
Normalisation des libellés : NFKD sans accents, minuscules, espaces multiples réduits, strip.
Tous les chemins sont relatifs à la racine du dépôt (calculée depuis l'emplacement du présent fichier)."""
import os
import pandas as pd, numpy as np, unicodedata, re, math

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.abspath(os.path.join(ICI, '..', '..'))
DOCS = os.path.join(RACINE, 'public', 'documents')
CAISSE = os.path.join(DOCS, 'caisse-enregistreuse') + os.sep
C = os.path.join(ICI, 'cache') + os.sep          # tables intermédiaires (.pkl)
OUT = os.path.join(C, 'out') + os.sep            # sorties intermédiaires (.csv)
P = os.path.join(C, 'pieces') + os.sep           # pièces régénérées (.xlsx)
for _d in (C, OUT, P): os.makedirs(_d, exist_ok=True)

# Pièces antérieures servant d'entrée (versions R2 et pièce n° 8 du 10/07/2026).
# Une pièce retirée de public/ (remplacée par sa version R3) est relue dans l'historique git : dernière version
# enregistrée du fichier, extraite dans cache/entrees/.
def entree(rel):
    p = os.path.join(RACINE, rel)
    if os.path.exists(p): return p
    import subprocess
    dst = os.path.join(C, 'entrees', os.path.basename(rel))
    if not os.path.exists(dst):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        git = lambda *a: subprocess.run(['git', '-C', RACINE, *a], check=True, capture_output=True).stdout
        try: data = git('show', f'HEAD:{rel}')
        except subprocess.CalledProcessError:
            c = git('rev-list', '-n', '1', 'HEAD', '--', rel).decode().strip()   # commit qui a supprimé le fichier
            data = git('show', f'{c}^:{rel}')
        with open(dst, 'wb') as f: f.write(data)
    return dst
PIECE_77 = entree('public/documents/pieces-reponse-2/R2-quantites-recomposition.xlsx')
PIECE_78 = entree('public/documents/pieces-reponse-2/R2-quantites-chiffrage-service.xlsx')
PIECE_89 = entree('public/documents/pieces-reponse-2/R2-fichiers-EF-reconciliation.xlsx')
PIECE_08 = entree('public/documents/pieces-defense/RF-quantites-anormales.xlsx')

EX = ['2022-2023', '2023-2024', '2024-2025']
_NOMS = {'B': 'prix-vente-quantite', 'C': 'detail-tickets', 'E': 'tpvevenement', 'F': 'reglements', 'G': 'journal-tva', 'H': 'liste-tickets'}
def annexe(lettre, k):
    """Chemin de l'annexe de caisse lettre-k (k = 1, 2, 3 pour les trois exercices)."""
    return CAISSE + f'ANNEXE-{lettre}{k}_{_NOMS[lettre]}_{EX[k-1]}.xls'

def norm(s):
    s=unicodedata.normalize('NFKD',str(s)); s=''.join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r'\s+',' ',s.lower()).strip()
def tmin(h):
    a,b=str(h).split(':'); return int(a)*60+int(b)
def load():
    Cr=pd.read_pickle(C+'Crec.pkl')   # annexe C primaire + Qté B / écart B (s31)
    Cr['lib_s']=Cr.lib.str.strip(); Cr['libn']=Cr.lib.map(norm); Cr['pu100']=(Cr.pu*100).round().astype(int)
    Cr['fracC']=(Cr.qteC-Cr.qteC.round()).abs()>1e-9
    Cr['t']=Cr.heureTicket.map(tmin)
    F=pd.read_pickle(C+'F.pkl'); E=pd.read_pickle(C+'E.pkl'); E['t']=E.heureEven.map(tmin)
    Fid=pd.read_pickle(C+'Fid2.pkl')
    tabs,nd,A=pd.read_pickle(C+'recompo_base.pkl')
    return Cr,F,E,Fid,tabs,nd,A
def ex_of(d):
    return '2022-2023' if d<'2023-04-01' else ('2023-2024' if d<'2024-04-01' else '2024-2025')
