"""B0 point 5 : couverts, services et occupation recalculés depuis l'annexe C, avec la classification reconstituée (s09)
et sensibilité aux choix de définition. Sortie : out/s10_occupation.txt, out/s10_services.csv"""
import pandas as pd, numpy as np
O='scripts/lot7-tables-virtuelles/out/'
C=pd.read_pickle(O+'B0cache/C.pkl'); A=pd.read_pickle(O+'B0cache/A.pkl'); H=pd.read_pickle(O+'B0cache/H2.pkl')
S92=pd.read_pickle(O+'B0cache/S92.pkl'); P12=pd.read_pickle(O+'B0cache/P12.pkl'); F=pd.read_pickle(O+'B0cache/F.pkl')
L=pd.read_csv(O+'B0_s09_libelles.csv'); PLAT=set(L[L.inclus==1].lib)
out=open(O+'B0_s10_occupation.txt','w')
def p(*a): print(*a); print(*a,file=out)
C['libs']=C.lib.astype(str).str.strip()
s2=set(H[(H.serie==2)].id)
ENF={"Menu 'Enfant'",'Menu Bambin'}
LARGE={'Croûtes Morilles','MACHON GOURMET','Chèvre  chaud','Feuilleté Forestier','Escargots de Bourgog','Assortiment charcute','Jamhon Persillé','Jambon sec'}
def note_cv(plat_set, excl_s2=True, large=False, min1=False):
    c=C[~C.id.isin(s2)] if excl_s2 else C
    g=c[c.libs.isin(plat_set)].groupby('id').qte.sum()
    cv=A.set_index('id').reindex(columns=[]).assign(cv=g).cv.fillna(0)
    if large:
        e=c[c.libs.isin(LARGE)].groupby('id').qte.sum(); cv=np.maximum(cv,e.reindex(cv.index).fillna(0))
    if min1: cv=cv.where(cv>0,1.0)
    if excl_s2: cv=cv[~cv.index.isin(s2)]
    return cv
def tmin(h): return int(h[:2])*60+int(h[3:])
A['t']=A.heure.map(tmin); A['mois']=A.date.str[5:7].astype(int)
def services(cv, seuil=18*60, merge_s2_by_rank=False):
    a=A.set_index('id').loc[cv.index].copy(); a['cv']=cv.values
    a['service']=np.where(a.t<seuil,'midi','soir')
    s=a.groupby(['date','service']).agg(cv=('cv','sum'),notes=('cv','size'),ex=('ex','first'),mois=('mois','first')).reset_index()
    return s
def occ(s, mois_terrasse=(5,6,7,8), places=(46,48), only_pos=True, rnd=True, ratio=False, fixed=None):
    s=s[s.cv>0] if only_pos else s
    s=s.copy()
    s['esp']=np.where(s.mois.isin(mois_terrasse),'terrasse','intérieur')
    s['pl']=fixed if fixed else np.where(s.esp=='terrasse',places[1],places[0])
    s['o']=s.cv/s.pl*100
    if rnd: s['o']=np.floor(s.o+0.5)   # ROUND Excel (demi vers le haut, valeurs positives)
    m=(s.cv.sum()/s.pl.sum()*100) if ratio else s.o.mean()
    return s,m
# --- reproduction de la pièce
cv0=note_cv(PLAT,excl_s2=False)   # P11 rattache les 17 tickets de 2e série au rang partagé : on les garde
p('Couverts par note, classification reconstituée, 17 tickets de 2e série inclus :',round(cv0.sum(),2))
s0=services(cv0)
s0r=s0.copy(); s0r['cvr']=np.floor(s0r.cv+0.5)
m=s0r.merge(S92,on=['date','service'],how='outer',suffixes=('','_92'))
p('Services avec au moins une note :',len(s0),' ; avec couverts > 0 :',(s0.cv>0).sum(),' ; lignes S92 :',len(S92))
p('  S92 absents des services recalculés à couverts>0 :',m[m.cv_92.notna()&~(m.cv>0)][['date','service','cv','notes','cv_92']].to_string())
p('  écarts couverts arrondis vs S92 :',int((m.cvr!=m.cv_92)[m.cv_92.notna()].sum()),' ; somme des arrondis',int(m[m.cv_92.notna()].cvr.sum()),' vs S92',int(S92.cv.sum()))
p('  services avec notes mais 0 couvert (boissons seules), exclus de S92 :',int(((s0.cv==0)).sum()),' notes concernées',int(s0[s0.cv==0].notes.sum()))
p('  écarts d espace S92 vs règle mai-août :',int(((np.where(S92.date.str[5:7].astype(int).isin([5,6,7,8]),'terrasse','intérieur'))!=S92.espace).sum()))
# indicateurs pièce depuis S92 (valeurs arrondies)
S=S92.copy(); S['mois']=S.date.str[5:7].astype(int)
p('Indicateurs S92 : services',len(S),' couverts',S.cv.sum(),' moyenne',round(S.cv.mean(),2),' occupation (moy. % arrondis)',round(S.occ.mean(),2))
for e,g in S.groupby('espace'): p(f'  {e}: services {len(g)} ; couverts moy {g.cv.mean():.2f} ; occ {g.occ.mean():.2f} ; >100 % {(g.occ>100).sum()}')
p('  >100 % total',(S.occ>100).sum(),' par mois',S[S.occ>100].mois.value_counts().sort_index().to_dict())
p('  par exercice :',S.groupby('ex').occ.mean().round(2).to_dict(),' services',S.groupby('ex').size().to_dict())
p('  occupation non arrondie (moyenne de cv/places) :',round((S.cv/S.places*100).mean(),2),' ; ratio des sommes :',round(S.cv.sum()/S.places.sum()*100,2))
p('  >100 % non arrondi (cv>places) :',int((S.cv>S.places).sum()),' ; >=100 % arrondi :',int((S.occ>=100).sum()))
# tableau 74
S['occ_exact']=S.cv/S.places*100
T=S.sort_values(['occ','cv'],ascending=False).head(14)
T['jour']=pd.to_datetime(T.date).dt.day_name()
p('Douze services les plus chargés (S92) :'); p(T[['date','jour','service','espace','cv','occ','occ_exact']].to_string())
# 9 juillet 2022
a=A[A.date=='2022-07-09']; p('09/07/2022 : additions',len(a),' midi(<18h)',int((a.t<1080).sum()),' soir',int((a.t>=1080).sum()),' couverts S92',S[S.date=='2022-07-09'].cv.tolist())
# --- sensibilité
p('\n== Sensibilité du taux d occupation (moyenne des % par service, sauf mention)')
rows=[]
def add(lab,cv,**kw):
    seuil=kw.pop('seuil',18*60); s=services(cv,seuil=seuil); ss,mm=occ(s,**kw)
    rows.append((lab,len(ss),round(ss.cv.sum(),1),round(ss.cv.mean(),2),round(mm,2),int((ss.cv/ss.pl>1).sum()) ))
add('P0 pièce (2e série incluse, % arrondis)',cv0)
add('P0 sans arrondi des %',cv0,rnd=False)
add('P0 ratio des sommes',cv0,ratio=True)
cv1=note_cv(PLAT)
add('N1 hors 17 tickets 2e série',cv1)
add('N2 N1 sans « Galette nature »',note_cv(PLAT-{'Galette nature'}))
add('N2b N1 sans Saucisse de Morteau, Steak haché, NOIRAUD (98-100 % avec un autre plat)',note_cv(PLAT-{'Saucisse de Morteau','Steak haché','NOIRAUD'}))
add('N2c N1 sans Galette nature, Saucisse, Steak haché, NOIRAUD, menus enfants (borne basse)',note_cv(PLAT-{'Galette nature','Saucisse de Morteau','Steak haché','NOIRAUD'}-ENF))
add('N3 N1 sans menus enfants (Enfant, Bambin)',note_cv(PLAT-ENF))
add('N4 N1 + entrées/planches (max par note)',note_cv(PLAT,large=True))
add('N5 N1, note sans plat = 1 couvert',note_cv(PLAT,min1=True))
add('D1 N1, services à 0 couvert inclus',cv1,only_pos=False)
add('D2 N1, terrasse mai-septembre',cv1,mois_terrasse=(5,6,7,8,9))
add('D3 N1, terrasse avril-septembre',cv1,mois_terrasse=(4,5,6,7,8,9))
add('D4 N1, terrasse juin-août',cv1,mois_terrasse=(6,7,8))
add('D5 N1, 46 places partout',cv1,fixed=46)
add('D6 N1, 48 places partout',cv1,fixed=48)
add('D7 N1, 94 places (deux espaces)',cv1,fixed=94)
add('D8 N1, anciens chiffres 44 / 43 places',cv1,places=(44,43))
add('P0, anciens chiffres 44 / 43 places',cv0,places=(44,43))
add('M1 N1, midi avant 17 h',cv1,seuil=17*60)
add('M2 N1, midi avant 17 h 30',cv1,seuil=17*60+30)
add('M3 N1, midi avant 18 h 30',cv1,seuil=18*60+30)
R=pd.DataFrame(rows,columns=['variante','services','couverts','moy/service','occupation %','services >100 %'])
p(R.to_string(index=False))
# 37 tickets à 0,00 € porteurs de règlements : couverts implicites au ticket moyen par couvert
z=pd.read_csv(O+'B0_s03_zero.csv'); regl=z[z.regl.abs()>0.004].regl.sum()
ca=A.tot.sum(); pc=ca/cv1.sum()
p(f'\n37 tickets à 0,00 € : 0 couvert par construction (aucune ligne C) ; règlements {regl:.2f} € ; dépense TTC moyenne par couvert {pc:.2f} € ; équivalent {regl/pc:.1f} couverts ({regl/pc/cv1.sum()*100:.3f} % des couverts)')
s0.to_csv(O+'B0_s10_services.csv',index=False)
out.close()
