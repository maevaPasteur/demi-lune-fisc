"""M0-2 : 2.6.4 b, tableaux 60 et 61 ; compteurs tot_sum / tot_tax_sum de H (et G), deux séries, raccords, tickets
postérieurs à la dernière ligne, sommes B / C / G / F. Sources : xls primaires (H relu par s02 ; G, B relus ici)."""
import xlrd, pandas as pd, numpy as np
D='public/documents/caisse-enregistreuse/'; CA='scripts/lot6-evenement-reglement/cache/'
EX=['2022-2023','2023-2024','2024-2025']
c=lambda x:int(round(float(x)*100)); e=lambda n:f"{n/100:,.2f}".replace(',',' ').replace('.',',')
out=open('scripts/lot6-evenement-reglement/out/s06_series.txt','w')
def p(*a):
    print(*a); print(*a,file=out)
H=pd.read_pickle(CA+'H.pkl'); Hf=pd.read_pickle(CA+'H_foot.pkl'); F=pd.read_pickle(CA+'F.pkl')
CC=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/CC.pkl')
# ---- G relu
Gs=[];Gf={}
for ex,f in zip(EX,['ANNEXE-G1_journal-tva_2022-2023.xls','ANNEXE-G2_journal-tva_2023-2024.xls','ANNEXE-G3_journal-tva_2024-2025.xls']):
    s=xlrd.open_workbook(D+f).sheet_by_index(0); hdr=s.row_values(0); rows=[];ft=[]
    for r in range(1,s.nrows):
        v=s.row_values(r)
        if str(v[0])[:2]=='20': rows.append(v+[r+1])
        else: ft.append((r+1,[x for x in v]))
    g=pd.DataFrame(rows,columns=hdr+['ligneXLS']); g['ex']=ex; Gs.append(g); Gf[ex]=ft
G=pd.concat(Gs,ignore_index=True)
for k in ['tot_ttc','tot_sum','tot_tax_sum']: G[k+'_c']=G[k].map(c)
G.to_pickle(CA+'G.pkl'); pd.to_pickle(Gf,CA+'G_foot.pkl')
for ex in EX:
    p(f'--- pieds H {ex} :'); [p('  ligne',r,[x for x in v if x!='']) for r,v in Hf[ex]]
    p(f'--- pieds G {ex} :'); [p('  ligne',r,[x for x in v if x!='']) for r,v in Gf[ex]]
# ---- séries
S1MIN=c(977739.78)
H['serie']=np.where(H.tot_sum_c>=S1MIN,1,2)
p('\nTickets par série et exercice :'); p(H.groupby(['serie','ex']).size().unstack().to_string())
p('Tickets à 0 € par série :',H[H.tot_ttc_c==0].groupby(['serie','ex']).size().to_dict())
p('Tickets ≠ 0 par série :',H[H.tot_ttc_c!=0].groupby(['serie','ex']).size().to_dict())
op={ex:(c(v[8]),c(v[9])) for ex in EX for r,v in Hf[ex] if v[0]=='A NOUVEAUX'}
p('A NOUVEAUX (tot_sum, tot_tax_sum) :',{k:(e(a),e(b)) for k,(a,b) in op.items()})
# chaînage : trier par compteur et vérifier incrément = tot_ttc (et taxe = tot_tva)
for s in (1,2):
    X=H[H.serie==s].sort_values(['tot_sum_c','id']).reset_index(drop=True)
    d=X.tot_sum_c.diff(); dt_=X.tot_tax_sum_c.diff()
    ok=(d.iloc[1:]==X.tot_ttc_c.iloc[1:]).sum(); okt=(dt_.iloc[1:]==X.tot_tva.map(c).iloc[1:]).sum()
    # tickets à 0 : même compteur que le précédent
    p(f'\nSérie {s} : {len(X)} tickets ; compteur {e(X.tot_sum_c.min())} → {e(X.tot_sum_c.max())} ; taxe {e(X.tot_tax_sum_c.min())} → {e(X.tot_tax_sum_c.max())}')
    p(f'  incrément = tot_ttc du ticket : {ok}/{len(X)-1} ; incrément taxe = tot_tva : {okt}/{len(X)-1}')
    bad=X.iloc[1:][(d.iloc[1:]!=X.tot_ttc_c.iloc[1:]).values]
    p('  ruptures :',len(bad)); p(bad[['ex','date_ticket','heure_ticket','no_ticket','tot_ttc','tot_sum']].head(10).to_string() if len(bad) else '')
    # premier ticket : compteur - tot_ttc = ouverture ?
    first=X.iloc[0]; p('  premier ticket : compteur',e(first.tot_sum_c),' - tot_ttc',e(first.tot_ttc_c),' =',e(first.tot_sum_c-first.tot_ttc_c))
    for ex in EX:
        Y=H[(H.serie==s)&(H.ex==ex)]
        lo=Y.tot_sum_c.min()-Y.loc[Y.tot_sum_c.idxmin()].tot_ttc_c
        p(f'  {ex} : tickets {len(Y)} ; ≠0 {int((Y.tot_ttc_c!=0).sum())} ; ouverture déduite {e(lo)} ; clôture (max) {e(Y.tot_sum_c.max())} ; Σ tot_ttc {e(Y.tot_ttc_c.sum())} ; '
          f'clôture − ouverture {e(Y.tot_sum_c.max()-lo)} ; taxe : ouv {e(Y.tot_tax_sum_c.min()-Y.loc[Y.tot_tax_sum_c.idxmin()].tot_tva*100)} clôt {e(Y.tot_tax_sum_c.max())} Σ tot_tva {e(Y.tot_tva.map(c).sum())}')
# raccords série 1 avec A NOUVEAUX
for i,ex in enumerate(EX):
    Y=H[(H.serie==1)&(H.ex==ex)]
    nxt=op.get(EX[i+1]) if i<2 else None
    p(f'Série 1 {ex} : ouverture fichier {e(op[ex][0])} / taxe {e(op[ex][1])} ; clôture max {e(Y.tot_sum_c.max())} / {e(Y.tot_tax_sum_c.max())} ; ouverture suivante {nxt and (e(nxt[0]),e(nxt[1]))} ; écarts {nxt and (Y.tot_sum_c.max()-nxt[0], Y.tot_tax_sum_c.max()-nxt[1])}')
# variations taxe série 1
p('Variations taxe série 1 :',[e(H[(H.serie==1)&(H.ex==ex)].tot_tax_sum_c.max()-op[ex][1]) for ex in EX])
# dernière ligne du fichier (ordre du fichier) et tickets postérieurs
p('\nDernière ligne du fichier H et G, tickets au compteur supérieur :')
for ex in EX:
    Y=H[H.ex==ex].sort_values('ligneXLS'); last=Y.iloc[-1]
    Yg=G[G.ex==ex].sort_values('ligneXLS'); lastg=Yg.iloc[-1]
    after=Y[(Y.serie==1)&(Y.tot_sum_c>last.tot_sum_c)]
    p(f' {ex} : dernière ligne H n°{last.ligneXLS} {last.date_ticket} {last.heure_ticket} ticket {last.no_ticket} Z {last.no_z_report} compteur {e(last.tot_sum_c)} ; − ouverture = {e(last.tot_sum_c-op[ex][0])} ; '
      f'dernière ligne G compteur {e(lastg.tot_sum_c)} − ouverture = {e(lastg.tot_sum_c-op[ex][0])}')
    p('   tickets série 1 au compteur > dernière ligne :'); p(after[['ligneXLS','date_ticket','heure_ticket','no_ticket','no_z_report','tot_ttc','tot_sum','id']].to_string())
    p('   Σ',e(after.tot_ttc_c.sum()))
# sommes par annexe
B=pd.read_pickle('scripts/lot6-evenement-reglement/cache/lot23/B.pkl')
p('\nΣ par exercice (centimes exacts) :')
for ex in EX:
    s1=H[(H.serie==1)&(H.ex==ex)].tot_ttc_c.sum(); s2=H[(H.serie==2)&(H.ex==ex)].tot_ttc_c.sum()
    p(f' {ex} : H série1 {e(s1)} ; H série2 {e(s2)} ; H total {e(s1+s2)} ; B lignes {e(B[B.ex==ex].tot.map(c).sum())} ; C lignes {e(CC[CC.ex==ex].tot.map(c).sum())} ; '
      f'F {e(F[F.ex==ex].montant_c.sum())} ; G Σ tot_ttc par ticket {e(G[G.ex==ex].drop_duplicates(["dateTicket","heureTicket","noTicket","no_zReport"]).tot_ttc_c.sum())}')
# 17 tickets non nuls de la série 2
s2=H[(H.serie==2)&(H.tot_ttc_c!=0)]
p('\n17 tickets non nuls série 2 :',len(s2),e(s2.tot_ttc_c.sum())); p(s2[['ex','date_ticket','heure_ticket','no_ticket','no_z_report','tot_ttc','tot_sum','id']].to_string())
p('  dans F :',int(s2.id.isin(F.id).sum()),' dans C :',int(s2.id.isin(CC.id).sum()),' lignes C',int(CC.id.isin(s2.id).sum()),' ; dans G (date,heure,n°,Z) :',
  int(sum(((G.dateTicket==r.date_ticket)&(G.heureTicket==r.heure_ticket)&(G.noTicket==r.no_ticket)&(G.no_zReport==r.no_z_report)).any() for r in s2.itertuples())))
# 2 tickets à 0 de la série 1
z1=H[(H.serie==1)&(H.tot_ttc_c==0)]; p('\nTickets à 0 € de la série 1 :'); p(z1[['ex','date_ticket','heure_ticket','no_ticket','no_z_report','tot_sum','id']].to_string()); p('  lignes C :',int(CC.id.isin(z1.id).sum()))
H.to_pickle(CA+'H.pkl')
out.close()
