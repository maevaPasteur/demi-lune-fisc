"""C-9 : définition D-P « plat principal ou menu » (règle écrite avant calcul : un libellé de la liste reconstituée (59) est exclu s'il est
documenté comme entrée, accompagnement ou ingrédient par la carte du dossier, ou, à défaut, s'il figure avec un autre plat compté dans au moins
90 % des notes qui le portent) ; examen de « Galette nature » ; bornes V3 (proxy personnes) et « avec entrées et planches » ; tableaux 73 et 74
sous D-P ; variante hors 17 tickets de seconde série et hors 2 notes à 0,00 €. Sorties : out/B2/07.txt, 07_libelles.csv, 07_services_DP.csv"""
import sys; sys.path.insert(0,"scripts/lot7-tables-virtuelles")
from B2_common import *
C,E,F,H,A=load(); P=plats(); p=out2('07.txt')
s2=set(H[H.serie==2].id); z0n=set(H[(H.serie==1)&(H.tc==0)].id)
Cx=C.copy()
# co-occurrence : part des notes portant le libellé où figure un AUTRE libellé de P
nl=Cx[Cx.libs.isin(P)].groupby('id').libs.apply(set)
rows=[]
for l in sorted(P):
    ids=Cx[Cx.libs==l].id.unique(); sh=np.mean([len(nl[i]-{l})>0 for i in ids])
    rows.append((l,len(ids),sh))
Co=pd.DataFrame(rows,columns=['lib','notes','part_avec_autre_plat'])
ENTREES_CARTE={'PAYSANNE'}   # « Salade paysanne » listée parmi les entrées (alcool-plats-cocktails-menus.json) : rapprochement par le nom (inférence)
excl=set(Co[Co.part_avec_autre_plat>=0.90].lib)
p('Co-occurrence (libellés de P, part des notes où figure un autre plat compté) : ≥ 90 % :',Co[Co.part_avec_autre_plat>=0.9].round(3).values.tolist())
p('   entre 80 et 90 % :',Co[(Co.part_avec_autre_plat>=0.8)&(Co.part_avec_autre_plat<0.9)].round(3).values.tolist())
# Galette nature : ingrédients
ING={'Œuf','Jambon Blanc','Jambon Sec','Jambon sec','Comté','Champignons frais','Fromage de Chèvre','Bacon','Ratatouille','Morbier','Bleu de Gex','Oignons','Pommes de Terre','Noix','Miel','Tomates','Crème Fraîche','Cancoillotte','PIGNONS PIN','ECLATS NOISETTES','Amandes grillées','Saucisse de Morteau','SAUCE JURASSIENNE','Sauce Forestière','Sauce Morilles','Salade Verte','Beurre','Beurre Salé','Emmental','Raclette','Lardons','Poulet','Saumon'}
ing_present=sorted(set(Cx.libs)&ING)
gn=Cx[Cx.libs=='Galette nature'].id.unique()
def prof(i):
    s=set(Cx[Cx.id==i].libs); return (len(s&ING)>0, len((s&P)-{'Galette nature'})>0)
pr=[prof(i) for i in gn]
a=sum(1 for x,y in pr if x); b=sum(1 for x,y in pr if (not x) and y); c=sum(1 for x,y in pr if (not x) and (not y))
p(f'Galette nature : {len(gn)} notes ; avec au moins un ingrédient de galette {a} ({a/len(gn)*100:.1f} %) ; sans ingrédient mais avec un autre plat {b} ({b/len(gn)*100:.1f} %) ; ni l un ni l autre {c} ; ingrédients cherchés présents en C : {ing_present}')
q=Cx[Cx.id.isin(gn)]; gq=q[q.libs=='Galette nature'].groupby('id').qte.sum(); iq=q[q.libs.isin(ING)].groupby('id').qte.sum()
p(f'   quantité de Galette nature par note (moyenne) {gq.mean():.2f} ; quantité d ingrédients par note (moyenne, notes qui en portent) {iq.mean():.2f}')
for l in ['Saucisse de Morteau','Steak haché','NOIRAUD','Salade Franc-Comptoi','PAYSANNE','VERDELET']:
    ids=Cx[Cx.libs==l].id.unique(); pr=[prof(i) for i in ids]
    p(f'   {l} : notes {len(ids)} ; avec ingrédient de galette {sum(x for x,_ in pr)} ; avec un autre plat compté {sum(y for _,y in pr)} ({np.mean([y for _,y in pr])*100:.1f} %) ; PU médian {Cx[Cx.libs==l].pu.median():.2f}')
GAL_BASE='Galette nature' if a/len(gn)>=0.5 else None
DP=(P-excl-ENTREES_CARTE)|({'Galette nature'} if GAL_BASE else set())
p(f'D-P : {len(DP)} libellés ; exclus par la règle des 90 % : {sorted(excl-({"Galette nature"} if GAL_BASE else set()))} ; exclu comme entrée de la carte (inférence) : {sorted(ENTREES_CARTE&P)} ; Galette nature {"comptée (base de galette composée)" if GAL_BASE else "exclue"}')
Co['DP']=Co.lib.isin(DP).astype(int); Co.to_csv(OUT2+'07_libelles.csv',index=False)
# calcul des services
LARGE={'Croûtes Morilles','MACHON GOURMET','Chèvre  chaud','Feuilleté Forestier','Escargots de Bourgog','Assortiment charcute','Jamhon Persillé','Jambon sec'}
MENU={"Menu 'Demi Lune'","Menu 'Galette'",'Menu Bourguignon','Menu Franc-Comtois','Menu Végétarien','Menu du Dahu','Menu du jour','Formule Express','FORMULE EXPRESS','Formule à 11','Formule à 12.5','Formule à 14','Plat du jour'}
ENF={"Menu 'Enfant'",'Menu Bambin'}; FON={'Fondue Forestière','Fondue Jurassienne','Fondue des Gourmets','FONDUE VIN JAUNE'}; SAL={'Salade Régionale','Salade Végétarienne','Salade Franc-Comptoi'}
GAL={'Galette nature','GALETTE FORESTIERE','Complète','BARBEULENET','CABRICHOU','CANCOINE','DADOULET','DAHU','ECRESSI','FOULETOT','FRELEE','LIGOUSE','LOURNETTE','NIOLERIES','NOIRAUD','PAYSANNE','PEUTE','TANTELIN','VERDELET'}
def cat(l):
    for n,s in [('menu',MENU),('enfant',ENF),('fondue',FON),('salade',SAL),('galette',GAL)]:
        if l in s: return n
    return 'plat'
def note_cv(libset,excl_ids,mode='sum'):
    x=Cx[Cx.libs.isin(libset)&~Cx.id.isin(excl_ids)]
    if mode=='sum': cv=x.groupby('id').qte.sum()
    elif mode=='v3':
        x=x.assign(c=x.libs.map(cat)); cv=x.groupby(['id','c']).qte.sum().groupby('id').max()
    elif mode=='large':
        cv=x.groupby('id').qte.sum(); e=Cx[Cx.libs.isin(LARGE)&~Cx.id.isin(excl_ids)].groupby('id').qte.sum()
        cv=pd.concat([cv,e],axis=1).fillna(0).max(axis=1)
    a=A[~A.id.isin(excl_ids)].set_index('id'); a['cv']=cv.reindex(a.index).fillna(0); return a
def services(a):
    a=a.copy(); a['svc']=np.where(a.t<1080,'midi','soir'); a['mois']=a.date.str[5:7].astype(int)
    s=a.groupby(['date','svc']).agg(cv=('cv','sum'),mois=('mois','first'),ex=('ex','first')).reset_index()
    s['esp']=np.where(s.mois.isin([5,6,7,8]),'terrasse','intérieur'); s['pl']=np.where(s.esp=='terrasse',48,46); s['o']=s.cv/s.pl*100
    return s
def report(lab,s):
    p(f'\n{lab} : services {len(s)} ; couverts {s.cv.sum():.1f} ; par service {s.cv.mean():.2f} ; occupation (moyenne des taux) {s.o.mean():.2f} % ; rapport des sommes {s.cv.sum()/s.pl.sum()*100:.2f} % ; > 100 % {int((s.o>100).sum())} ; max {s.o.max():.0f} % ; écart au repère {s.o.mean()-58:+.2f} pt')
    for e,g in s.groupby('esp'): p(f'    {e} : services {len(g)} ; couverts / service {g.cv.mean():.2f} ; occupation {g.o.mean():.2f} % ; > 100 % {int((g.o>100).sum())}')
    p('    par exercice :',s.groupby('ex').o.mean().round(2).to_dict())
    return s
base_excl=set()      # société : 17 tickets de 2e série rattachés par le rang ; ici, version « réellement encaissé » : on exclut s2 et les 2 notes à 0 €
ex_strict=s2|z0n
sV0=report('V0 (liste société, 17 tickets de seconde série et 2 notes à 0,00 € exclus)',services(note_cv(P,ex_strict)))
sDP=report('D-P',services(note_cv(DP,ex_strict)))
sV3=report('Borne basse V3 (par note, maximum des sommes par catégorie : menus, menus enfants, fondues, salades, galettes, autres plats ; liste société)',services(note_cv(P,ex_strict,'v3')))
sL=report('Borne haute « avec entrées et planches » (par note, maximum entre les plats comptés et les entrées / planches)',services(note_cv(P,ex_strict,'large')))
sDP.to_csv(OUT2+'07_services_DP.csv',index=False)
T=sDP.sort_values('o',ascending=False).head(12); T['jour']=pd.to_datetime(T.date).dt.day_name()
p('\nTableau 74 sous D-P :'); p(T[['date','jour','svc','esp','cv','o']].round(1).to_string())
p(f'\nPièce « réellement encaissé » : couverts de la liste société sans les 17 tickets ni les 2 notes à 0,00 € : {note_cv(P,ex_strict).cv.sum():.2f} ; écart à 37 370,68 : {37370.68-note_cv(P,ex_strict).cv.sum():.2f}')
# D-P corrigée : la règle littérale des 90 % exclut des menus enfants et des galettes que la carte classe parmi les plats ; règle corrigée,
# écrite après lecture du résultat littéral (à signaler) : exclusion des seuls libellés hors menus de prix médian < 10 € présents avec un autre plat compté
# dans au moins 90 % de leurs notes ; menus enfants comptés ; galettes comptées ; PAYSANNE en variante.
pu=Cx.groupby('libs').pu.median()
acc={l for l in excl if pu[l]<10 and l not in MENU|ENF}
DPc=P-acc
p(f'\nD-P corrigée : exclus {sorted(acc)} ; libellés comptés {len(DPc)}')
sDPc=report('D-P corrigée (PAYSANNE comptée)',services(note_cv(DPc,ex_strict)))
sDPc2=report('D-P corrigée sans PAYSANNE',services(note_cv(DPc-{'PAYSANNE'},ex_strict)))
T=sDPc.sort_values('o',ascending=False).head(12); T['jour']=pd.to_datetime(T.date).dt.day_name()
p('\nTableau 74 sous D-P corrigée :'); p(T[['date','jour','svc','esp','cv','o']].round(1).to_string())
Co['DP_corrigee']=Co.lib.isin(DPc).astype(int); Co.to_csv(OUT2+'07_libelles.csv',index=False); sDPc.to_csv(OUT2+'07_services_DPc.csv',index=False)
