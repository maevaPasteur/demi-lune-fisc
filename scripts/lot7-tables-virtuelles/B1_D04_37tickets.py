"""D-4 : les 37 tickets sans article porteurs de règlements. Une ligne par ticket ; égalités avec des notes du jour (± 60 min),
seules ou par sommes de 2 ou 3 ; hasard par transport au 1er, 2e, 3e, 5e et 8e jour d'ouverture suivant (même minute) ;
doubles de règlement ; borne par exercice de la part comptabilisable. Sorties : out/B1/D04.txt, D04_37.csv"""
import sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from B1_common import *
from itertools import combinations
C,E,F,H,A=load(); S=source(); S['id']=S.id.astype(int); p=out('D04.txt')
F['t']=F.heureTicket.map(tm); F['mc']=(F.montant*100).round().astype(int)
Fs=F.groupby('id').mc.sum()
Z=H[(~H.dansC)].copy(); Z['regl']=Z.id.map(Fs).fillna(0).astype(int); Z=Z[Z.regl!=0].copy()
tv=tv2359()[['d','t','V']].copy(); tv['d']=tv.d.astype(str); tv['t']=tv.t.astype(str).map(tm); tvd={(d,t):v for d,t,v in tv.values}
D=E[E.typEven=='DEL']; Dmin=D.groupby(['dateEven','t']).ac.sum().to_dict()
N=H[(H.serie==1)&(H.tc!=0)]; days=sorted(H.date_ticket.unique()); di={d:i for i,d in enumerate(days)}
def notes_win(d,t): g=N[(N.date_ticket==d)&(N.t.between(t-60,t+60))]; return g
def eqs(g,target):
    v=g.tc.values; n=len(v); c=[0,0,0]
    if target<=0: return c
    c[0]=int((v==target).sum())
    for i,j in combinations(range(n),2):
        if v[i]+v[j]==target: c[1]+=1
    if n<=60:
        for i,j,k in combinations(range(n),3):
            if v[i]+v[j]+v[k]==target: c[2]+=1
    return c
rows=[]
for _,r in Z.sort_values('id').iterrows():
    d,t=r.date_ticket,r.t
    cont=tvd.get((d,t)); src='lot 2.2 (V)'
    if cont is None:
        cont=Dmin.get((d,t)); src='DEL de la minute'
    if cont is None:
        cont=sum(Dmin.get((d,t+k),0) for k in (-1,1)); src='DEL à ± 1 min'
    fl=F[F.id==r.id]; et=S[S.id==r.id].etat.tolist()
    diff=cont-r.regl
    g=notes_win(d,t)
    e_c=eqs(g,cont); e_d=eqs(g,diff); e_r=eqs(g,r.regl)
    # hasard : même minute, jours d'ouverture suivants
    hz=[]
    for k in (1,2,3,5,8):
        if di[d]+k<len(days):
            g2=notes_win(days[di[d]+k],t); hz.append([sum(eqs(g2,x)) for x in (cont,diff,r.regl)])
    hz=np.mean(hz,axis=0) if hz else [np.nan]*3
    # double de règlement : même mode, même montant, à la même minute (± 0) et à ± 5 min, sur une autre note
    dbl0=dbl5=0
    for m_,mc in zip(fl.mod_regl,fl.mc):
        o=F[(F.dateTicket==d)&(F.id!=r.id)&(F.mod_regl==m_)&(F.mc==mc)]
        dbl0+=int((o.t==t).sum()); dbl5+=int((o.t-t).abs().le(5).sum())
    rows.append(dict(date=d,heure=r.heure_ticket,id=r.id,rang2=r.no_ticket,Z=r.no_z_report,ex=r.ex,
        reglements='; '.join(f'{a} {b:.2f}' for a,b in zip(fl.mod_regl,fl.montant)),etat=','.join(map(str,sorted(set(et)))),
        regl=r.regl/100,contenu=cont/100,source_contenu=src,difference=diff/100,notes_fenetre=len(g),
        eg_contenu_1_2_3='/'.join(map(str,e_c)),eg_diff_1_2_3='/'.join(map(str,e_d)),eg_regl_1_2_3='/'.join(map(str,e_r)),
        hasard_contenu=round(hz[0],2),hasard_diff=round(hz[1],2),hasard_regl=round(hz[2],2),double_meme_minute=dbl0,double_5min=dbl5))
R=pd.DataFrame(rows); R.to_csv(OUT+'D04_37.csv',index=False)
p(R.drop(columns=['reglements']).to_string())
p(f'\nTotaux : règlements {R.regl.sum():.2f} € ; contenu {R.contenu.sum():.2f} € ; différence {R.difference.sum():.2f} € ; lignes F {len(F[F.id.isin(R.id)])} ; etat : {S[S.id.isin(R.id)].etat.value_counts().to_dict()}')
p('etat = 9 dans tout l export : lignes',int((S.etat.astype(str)=='9').sum()),' ; ids',S[S.etat.astype(str)=='9'].id.nunique(),' ; dont parmi les 37 :',len(set(S[S.etat.astype(str)=='9'].id)&set(R.id)))
tot=lambda col: sum(sum(map(int,x.split('/'))) for x in R[col])
p(f'Égalités observées (1, 2 ou 3 notes à ± 60 min) : contenu {tot("eg_contenu_1_2_3")} (hasard moyen {R.hasard_contenu.sum():.1f}) ; différence {tot("eg_diff_1_2_3")} (hasard {R.hasard_diff.sum():.1f}) ; règlement {tot("eg_regl_1_2_3")} (hasard {R.hasard_regl.sum():.1f})')
p(f'Tickets ayant au moins une égalité : contenu {int((R.eg_contenu_1_2_3!="0/0/0").sum())} ; différence {int((R.eg_diff_1_2_3!="0/0/0").sum())} ; règlement {int((R.eg_regl_1_2_3!="0/0/0").sum())}')
p(f'Doubles de règlement (même mode, même montant, autre note) : à la même minute {int(R.double_meme_minute.sum())} ; à ± 5 min {int(R.double_5min.sum())}')
# borne comptable : écart comptabilité - première série par exercice (Doc 26/11, tableau 48, source proposition p. 26)
ec={'2022-2023':62.41,'2023-2024':67.73,'2024-2025':40.49}
by=R.groupby('ex').regl.sum()
inc=sum(min(by.get(e,0),ec[e]) for e in ec)
p(f'Règlements des 37 par exercice : {by.round(2).to_dict()} ; écart comptabilité − première série (tableau 48 du Doc) : {ec} ; part au plus comptabilisable si l écart s y rapportait entièrement : {inc:.2f} € ; donc au moins {R.regl.sum()-inc:.2f} € hors du chiffre d affaires comptabilisé, sous cette hypothèse')
