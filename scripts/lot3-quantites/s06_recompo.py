"""Recomposition des tables partagées (algorithme décrit dans l'onglet « Méthode » de la pièce n° 77).
Sorties : cache/recompo_base.pkl, NOTES.pkl, Fid2.pkl.
Paramètres : fenêtre W (min, strict <), seuil eps, mode de chaînage."""
import pandas as pd, numpy as np, math, sys
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import C
Cr=pd.read_pickle(C+'Crec.pkl'); F=pd.read_pickle(C+'F.pkl')
Cr['lib_s']=Cr.lib.str.strip(); Cr['pu100']=(Cr.pu*100).round().astype(int)
Cr['fracC']=(abs(Cr.qteC-Cr.qteC.round())>1e-9)
Fid=F.groupby('id').agg(heure=('heureTicket','first'),tot=('tot_ttc','first'),mods=('mod_regl',lambda s:' / '.join(s)),mont=('montant','sum'),nreg=('id','size'))
def tmin(h): hh,mm=h.split(':'); return int(hh)*60+int(mm)
Fid['t']=Fid.heure.map(tmin)
fracnotes=Cr[Cr.fracC].id.unique()
NOTES=Cr[Cr.id.isin(fracnotes)].copy()
NOTES['t']=NOTES.id.map(Fid.t)
def build(W=15, share=True, pairwise_prev=True, nowin=False, le=True):
    """retourne liste de tables : (ex,date,[ids])"""
    out=[]
    nd=NOTES.groupby('id').agg(ex=('ex','first'),date=('date','first'),tk=('ticket','first'),t=('t','first'))
    fa=NOTES[NOTES.fracC].groupby('id').apply(lambda g:set(zip(g.lib_s,g.pu100)))
    nd['fa']=fa
    for (ex,d),g in nd.sort_values(['t','tk']).groupby(['ex','date'],sort=False):
        cur=[]; curart=set(); lastt=None
        for i,r in g.iterrows():
            ok = bool(cur)
            if ok and not nowin: ok = ((r.t-lastt) <= W) if le else ((r.t-lastt) < W)
            if ok and share: ok = len(r.fa & curart)>0
            if ok:
                cur.append(i); curart|=r.fa; lastt=r.t
            else:
                if cur: out.append((ex,d,cur))
                cur=[i]; curart=set(r.fa); lastt=r.t
        if cur: out.append((ex,d,cur))
    return out, nd
def articles(tables, nd, eps=0.02):
    rows=[]
    for k,(ex,d,ids) in enumerate(tables):
        if len(ids)<2: continue
        sub=NOTES[NOTES.id.isin(ids)]
        fkeys=set(zip(sub[sub.fracC].lib_s,sub[sub.fracC].pu100))
        for (lib,pu),g in sub.groupby(['lib_s','pu100']):
            if (lib,pu) not in fkeys: continue
            s=round(g.qteC.sum(),6)
            nnotes_frac=g[g.fracC].id.nunique(); nnotes=g.id.nunique()
            ref= abs(s-round(s))<eps
            comp=0.0 if ref else (math.ceil(s-1e-9)-s)*pu/100
            rows.append(dict(tab=k,ex=ex,date=d,lib=lib,pu=pu/100,somme=s,ref=ref,comp=comp,nn=nnotes,nnf=nnotes_frac,ids=tuple(ids)))
    return pd.DataFrame(rows)
def summarize(tables,nd,eps=0.02,label=''):
    A=articles(tables,nd,eps)
    T=[t for t in tables if len(t[2])>=2]
    iso=[t for t in tables if len(t[2])==1]
    res={}
    for ex in ['2022-2023','2023-2024','2024-2025','ALL']:
        a=A if ex=='ALL' else A[A.ex==ex]
        tt=[t for t in T if ex=='ALL' or t[0]==ex]; ii=[t for t in iso if ex=='ALL' or t[0]==ex]
        nids=[i for t in tt for i in t[2]]
        res[ex]=dict(tables=len(tt),notes_tab=len(nids),notes_iso=len(ii),art=len(a),ref=int(a.ref.sum()),nonref=int((~a.ref).sum()),
                     comp=round(a.comp.sum(),2),tab_res=a[~a.ref].tab.nunique(),tot_tab=round(sum(Fid.tot[i] for i in nids),2))
    return pd.DataFrame(res).T, A
if __name__=='__main__':
    tabs,nd=build(15,True)
    S,A=summarize(tabs,nd)
    print(S)
    pd.to_pickle((tabs,nd,A),C+'recompo_base.pkl')
    NOTES.to_pickle(C+'NOTES.pkl'); Fid.to_pickle(C+'Fid2.pkl')
