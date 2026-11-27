"""Chargement commun (série B1). Données lues par B0_s00_load.py depuis les fichiers d'origine (out/B0cache),
export natif des règlements (cache lot 2.6 SOURCE.pkl, identique à F ligne à ligne selon le lot 2.6), annexe B (cache lot 2.3 B.pkl),
tables vidées version C du lot 2.2 (cache lot 2.6 b5_tables_videes.pkl), classification reconstituée (out/B0_s09_libelles.csv)."""
import pandas as pd, numpy as np
O='scripts/lot7-tables-virtuelles/out/'; Q=O+'B0cache/'; OUT=O+'B1/'
SEED=20261123
def tm(h): return int(h[:2])*60+int(h[3:])
def ex_of(d): return '2022-2023' if d<'2023-04-01' else ('2023-2024' if d<'2024-04-01' else '2024-2025')
def load():
    C=pd.read_pickle(Q+'C.pkl'); C['libs']=C.lib.astype(str).str.strip()
    E=pd.read_pickle(Q+'E.pkl'); E['t']=E.heureEven.map(tm); E['ac']=(E.amount*100).round().astype(int)
    F=pd.read_pickle(Q+'F.pkl'); H=pd.read_pickle(Q+'H2.pkl'); H['t']=H.heure_ticket.map(tm); H['tc']=(H.tot_ttc*100).round().astype(int)
    A=pd.read_pickle(Q+'A.pkl'); A['t']=A.heure.map(tm)
    return C,E,F,H,A
def source():
    S=pd.read_pickle('scripts/lot6-evenement-reglement/cache/SOURCE.pkl')
    S['sy']=S.sy_uk.astype(str); S['pre']=S.sy.str[:4].astype(int); S['tail']=S.sy.str[10:].astype(int)
    return S
def plats():
    L=pd.read_csv(O+'B0_s09_libelles.csv'); return set(L[L.inclus==1].lib)
def tv2359():
    return pd.read_pickle('scripts/lot6-evenement-reglement/cache/b5_tables_videes.pkl')
def out(name):
    f=open(OUT+name,'w')
    def p(*a):
        print(*a); print(*a,file=f); f.flush()
    return p
