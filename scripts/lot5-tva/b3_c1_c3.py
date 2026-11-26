"""B3 : C1 (extrait p.44), C2 (signature du décalage), C3 (matrice colonne E / taux appliqué / taux légal)."""
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
CC=pd.read_pickle(CA+'C_taux2.pkl').sort_values(['ex','rowC']).reset_index(drop=True)
A=pd.read_pickle(CA+'B3_articles.pkl').set_index('ref')
CC['tl']=CC.ref.map(lambda r: A.taux_legal[r] if A.taux_legal[r]!='' else np.nan)
CC['prev_rart']=CC.groupby('ex').rart.shift(1)
CC['Ecor']=np.where(CC.Es=='10 % / 20 %',20,np.where(CC.Es=='20 % / 10 %',10,np.nan))
G=loadG(); G['r']=G['taux_tva%'].astype(int); G['pal']=G.VAT_base_c+100*G.r
k=lambda t,r: t*r/(100+r)
print('===== C1')
d=CC[(CC.date=='2022-04-14')&(CC.ticket.isin([11,12,13,14,15,16]))&(CC.z==2938)].copy()
d['img']=(d.qte==0.5)   # l'image p.44 est filtrée sur Qte = 0,50 (icône de filtre active, colonne 12)
print('lignes C',len(d),'rowC',d.rowC.min(),'-',d.rowC.max(),'; lignes de l image (Qte fractionnaire)',int(d.img.sum()),'; lignes absentes de l image :',d[~d.img][['rowC','ticket','lib_s','qte']].values.tolist())
for lab,x in [('40 lignes C',d),('lignes de l image (Qte = 0,50)',d[d.img])]:
    s=x[x.Es!='']
    print(f'  {lab}: (a) rf = taux appliqué ligne précédente {int((x.rf==x.prev_rart).sum())}/{len(x)} ; rf = taux appliqué {int((x.rf==x.rart).sum())} ; (b) signalées E {len(s)} ; (c) E correct = taux appliqué {int((s.Ecor==s.rart).sum())} ; (d) E vers 10 % d un article légal 20 % {int(((s.Ecor==10)&(s.tl==20)).sum())} ; (e) taux appliqué ≠ légal {int((x.rart!=x.tl).sum())}')
    print(f'     colonne F : Σ {x.Fs.sum():.4f} ; part (c) {s[s.Ecor==s.rart].Fs.sum():.4f} ; part (d) {s[(s.Ecor==10)&(s.tl==20)].Fs.sum():.4f}')
print(d[['rowC','heure','ticket','ref','lib_s','qte','tot','rf','rart','prev_rart','Es','Fs','tl','img']].to_string())
gk=G[(G.dateTicket=='2022-04-14')&(G.noTicket.isin(range(11,17)))]
for t in range(11,17):
    g=gk[gk.noTicket==t]; x=d[d.ticket==t]
    p10=int(g[g.r==10].pal.sum()); p20=int(g[g.r==20].pal.sum())
    c10=int(x[x.rart==10].tot.map(c).sum()); c20=int(x[x.rart==20].tot.map(c).sum())
    print(f'  note {t}: G palier10 {e(p10)} palier20 {e(p20)} ; C (taux appliqué) {e(c10)} / {e(c20)} ; égal {p10==c10 and p20==c20} ; tot_tva {x.tot_tva.iloc[0]} ; Σ tax G {g.tax_amount.sum():.2f}')
print('===== C2')
CC['ok_file']=CC.rf==CC.rart; CC['same_prev']=CC.rart==CC.prev_rart
CC['pos']=CC.groupby(['ex','id']).cumcount()
for ex in EX+['3ex']:
    x=CC if ex=='3ex' else CC[CC.ex==ex]
    m=x.prev_rart.notna()
    ct=pd.crosstab(x[m].ok_file,x[m].same_prev)
    print(f'{ex}: croisé [fichier=appliqué]×[appliqué=appliqué précédent] {ct.to_dict()} ; lignes sans précédent (1re du fichier) {int((~m).sum())} ; part au bon taux {100*x.ok_file.mean():.3f} % ; part même taux que précédent {100*x[m].same_prev.mean():.3f} %')
    bad=x[~x.ok_file]; print(f'   désaccords {len(bad)} ; dont 1re ligne de note {int((bad.pos==0).sum())} ({100*(bad.pos==0).mean():.2f} %) ; notes concernées {bad.id.nunique()}')
ex_=CC[CC.prev_rart.notna()&(CC.ok_file!=CC.same_prev)]; print('exceptions (hors 1re ligne de fichier) :',len(ex_))
f1=CC[CC.prev_rart.isna()]; print('1res lignes de fichier :',f1[['ex','rowC','lib_s','rf','rart']].values.tolist())
day=CC.groupby('date').ok_file.agg(lambda s: 1-s.mean())
print(f'journées {len(day)} ; avec ≥1 désaccord {int((day>0).sum())} ; part de désaccord par journée min {day.min():.4f} médiane {day.median():.4f} max {day.max():.4f}')
print('journées sans désaccord :',day[day==0].index.tolist()[:10])
# seconde série (notes hors G)
gid=set(pd.read_pickle(CA+'B5_tickets.pkl').index.get_level_values(1))
s2=CC[~CC.id.isin(gid)]
print(f'seconde série : lignes {len(s2)} ; rf == taux appliqué ligne précédente {int((s2.rf==s2.prev_rart).sum())} ; rf == taux appliqué {int(s2.ok_file.sum())}')
print('===== C3')
CC['flag']=CC.Es!=''; CC['tserv']=np.where(CC.flag,CC.Ecor,CC.rf)
CC['ind']=CC.tl.isna()
CC['serv_ok']=CC.tserv==CC.tl; CC['app_ok']=CC.rart==CC.tl
CC['tva_app']=k(CC.tot,CC.rart); CC['tva_serv']=k(CC.tot,CC.tserv); CC['tva_leg']=k(CC.tot,CC.tl.fillna(CC.rart))
rows=[]
for ex in EX+['3ex']:
    x=CC if ex=='3ex' else CC[CC.ex==ex]
    g=x.groupby([x.flag,np.where(x.ind,'ind',x.serv_ok.astype(str)),np.where(x.ind,'ind',x.app_ok.astype(str))]).agg(lignes=('tot','size'),TTC=('tot','sum'),TVA_app=('tva_app','sum'),TVA_serv=('tva_serv','sum'),TVA_leg=('tva_leg','sum'),F=('Fs','sum')).round(2)
    g.index.names=['signalée E','service=légal','appliqué=légal']; print('---',ex); print(g.to_string())
x=CC
cat={'(a) vraie erreur caisse signalée':x.flag&~x.ind&~x.app_ok&x.serv_ok,
     '(b) vraie erreur caisse non signalée':~x.flag&~x.ind&~x.app_ok,
     '(c) artefact signalé (caisse juste, service juste)':x.flag&~x.ind&x.app_ok&x.serv_ok,
     '(d) signalée, service se trompe (caisse juste)':x.flag&~x.ind&x.app_ok&~x.serv_ok,
     '(e) non signalée, service (taux fichier) se trompe, caisse juste':~x.flag&~x.ind&x.app_ok&~x.serv_ok,
     '(f) signalée, caisse fausse et service faux':x.flag&~x.ind&~x.app_ok&~x.serv_ok,
     '(g) indéterminés signalés':x.flag&x.ind,'(h) indéterminés non signalés':~x.flag&x.ind}
for k_,m in cat.items():
    print(f'{k_}: lignes {int(m.sum())} ; TTC {x[m].tot.sum():.2f} ; F {x[m].Fs.sum():.2f}')
print('contrôle : signalées',int(x.flag.sum()))
print('désaccord E/taux appliqué (tserv≠rart) :',int((x.tserv!=x.rart).sum()),' = signalées où Ecor≠rart',int((x.flag&(x.Ecor!=x.rart)).sum()),'+ non signalées où rf≠rart',int((~x.flag&(x.rf!=x.rart)).sum()))
dd=x[cat['(d) signalée, service se trompe (caisse juste)']]
print(dd.groupby(['ref','lib_s','rart','tserv']).agg(lignes=('tot','size'),TTC=('tot','sum'),F=('Fs','sum')).round(2).sort_values('lignes',ascending=False).to_string())
ee=x[cat['(e) non signalée, service (taux fichier) se trompe, caisse juste']]
print('(e) top :',ee.groupby(['lib_s','rart','rf']).size().sort_values(ascending=False).head(10).to_dict())
aa=x[cat['(a) vraie erreur caisse signalée']|cat['(b) vraie erreur caisse non signalée']|cat['(f) signalée, caisse fausse et service faux']]
print(aa.groupby(['lib_s','flag','rf','rart','tserv']).size().to_string())
CC.to_pickle(CA+'C_b3.pkl')
