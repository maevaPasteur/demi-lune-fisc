"""C-12 : les 42 tickets à clôture différée (B1 D-3 b). Détail ; test des prix (prix unitaire de chaque article comparé aux prix pratiqués pour le
même libellé dans les 15 jours d'ouverture autour de la création estimée et autour de la clôture, le ticket lui-même exclu) ; position ; effet par exercice.
Sorties : out/B2/08.txt, 08_42.csv"""
import sys; sys.path.insert(0,"scripts/lot7-tables-virtuelles")
from B2_common import *
C,E,F,H,A=load(); S=source(); S['id']=S.id.astype(int); p=out2('08.txt')
M=pd.read_csv(OUT+'D03b_multijours.csv')
days=sorted(H.date_ticket.unique()); di={d:i for i,d in enumerate(days)}
C['pc']=(C.pu*100).round().astype(int)
def prices(lib,d,excl_id,k=15):
    i=di.get(d)
    if i is None:
        i=max(j for j,x in enumerate(days) if x<=d)
    win=set(days[max(0,i-k):i+k+1]); x=C[(C.libs==lib)&C.date.isin(win)&(C.id!=excl_id)&(C.pc>0)]
    return set(x.pc)
D=E[E.typEven=='DEL']; dk=D.groupby(['dateEven','t']).ac.sum()
N=H[(H.serie==1)&(H.tc!=0)]; first_day=N.groupby('date_ticket').t.min()
rows=[]
for _,r in M.iterrows():
    c=C[C.id==r.id]; res={'close_only':0,'create_only':0,'both':0,'neither':0}
    for l,pc in zip(c.libs,c.pc):
        if pc==0: continue
        a=pc in prices(l,r.jour_ouv_est,r.id); b=pc in prices(l,r.date_ticket,r.id)
        res['both' if a and b else ('create_only' if a else ('close_only' if b else 'neither'))]+=1
    t=tm(r.heure_ticket); svc_first=N[(N.date_ticket==r.date_ticket)&((N.t<1080)==(t<1080))].t.min()
    pos='premier ticket du jour' if t<=first_day.get(r.date_ticket,9999) else ('premier du service' if t<=svc_first else 'en cours de service')
    rg='; '.join(f'{a} {b:.2f}' for a,b in F[F.id==r.id][['mod_regl','montant']].values)
    delm=dk.get((r.date_ticket,t),0)/100 if r.tot_ttc==0 else np.nan
    rows.append(dict(id=r.id,cloture=f'{r.date_ticket} {r.heure_ticket}',rang=r.no_ticket,serie=r.serie,z=r.no_z_report,total=r.tot_ttc,reglements=rg,
        creation_bornee=r.jour_ouv_est,prefixe_syuk=r.jour_prefixe_syuk,delai_j=r.delai_j,position=pos,DEL_minute=delm,**res,ex_creation=r.ex_ouv,ex_cloture=r.ex_clo,articles=r.articles))
R=pd.DataFrame(rows); R.to_csv(OUT2+'08_42.csv',index=False)
nz=R[R.total!=0]
p(f'42 tickets : non nuls {len(nz)} ({nz.total.sum():.2f} €) ; à 0,00 € {len(R)-len(nz)}')
p(f'Test des prix (29 tickets non nuls, articles de PU > 0) : articles au prix des deux périodes {int(nz.both.sum())} ; prix pratiqué seulement autour de la clôture {int(nz.close_only.sum())} ; seulement autour de la création {int(nz.create_only.sum())} ; ni l un ni l autre {int(nz.neither.sum())}')
p(f'   tickets avec au moins un article au prix de la seule clôture : {int((nz.close_only>0).sum())} ; de la seule création : {int((nz.create_only>0).sum())}')
for i in [54679,53572,47675,51185]:
    x=R[R.id==i].iloc[0]; p(f'   {i} : clos {x.cloture}, créé vers {x.creation_bornee} (préfixe {x.prefixe_syuk}), {x.total:.2f} € ; prix : deux périodes {x.both}, clôture seule {x.close_only}, création seule {x.create_only}, aucun {x.neither}')
z=R[R.total==0]; p(f'13 tickets à 0,00 € : à la minute d un DEL {int((z.DEL_minute>0).sum())} (montant {z.DEL_minute.sum():.2f} €)')
p('Position à la clôture :',R.position.value_counts().to_dict())
ch=R[R.ex_creation!=R.ex_cloture]; p('Changement d exercice :',ch[['id','creation_bornee','cloture','total']].values.tolist())
for _,x in ch.iterrows():
    tva=C[C.id==x.id]; ht=(tva.tot_lig/(1+tva.taux/100)).sum()
    p(f'   {x.id} : {x.total:.2f} € TTC, {ht:.2f} € HT, rattaché à {x.ex_cloture} au lieu de {x.ex_creation}')
p(R.drop(columns=['articles']).to_string())
