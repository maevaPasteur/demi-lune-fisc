"""s08b : caissiers de G/H ; prix unitaires des articles suspects (taux caisse reconstitué)."""
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
G=loadG(); H=loadH(); print(G.caissier.value_counts().to_dict(), H.caissier.value_counts().to_dict())
CC=pd.read_pickle(CA+'C_taux2.pkl')
for r in ['1989','1949','0357','2005','0099','0354','1816','1957','1940','2119']:
    x=CC[CC.ref==r]; print(r, x.lib_s.iloc[0], int(x.rart.iloc[0]), x.pu.value_counts().head(4).to_dict())
