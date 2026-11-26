"""Contrôles B-1, B-2, B-3, B-17.
Transcription du scan p. 25 et p. 26 (Proposition_1_Lettre.pdf, rendu cache/p25-25.png et p26-26.png) ; recalculs ; comparaison à F et à l'export natif."""
import pandas as pd, numpy as np
CA='scripts/lot6-evenement-reglement/cache/'
EX=['2022-2023','2023-2024','2024-2025']
c=lambda x:int(round(float(x)*100)); e=lambda n:f"{n/100:,.2f}".replace(',',' ').replace('.',',')
out=open('scripts/lot6-evenement-reglement/out/t01_partieX.txt','w')
def p(*a): print(*a); print(*a,file=out)
F=pd.read_pickle(CA+'F.pkl'); H=pd.read_pickle(CA+'H.pkl'); S=pd.read_pickle(CA+'SOURCE.pkl')
# ---- transcription du scan (centimes) ; None = non imprimé
T={ # compte : [(brut, ajust, net imprimé)] x 3
 '511200':[(519465,-56730,462735),(352256,7756,360012),(475410,-22500,452910)],
 '511210':[(None,None,37014408),(None,None,39990310),(39766638,1100,39767738)],
 '511220':[(962050,-13418,948632),(911236,-732,910504),(None,None,470889)],
 '511221':[(93510,None,93510),(224005,-121573,102427),(None,None,439272)],
 '511230':[(1493450,-21950,1471500),(2302662,27338,2330000),(2020300,20200,2040500)],
 '511240':[(None,None,29000),(None,None,52500),(None,None,39000)],
}
C530=[(339065,53802,-59804,333063),(601043,54622,-59775,595890),(361309,-15177,-65657,280475)]
TOT25=[40352848,44341643,43490784]
P26={'706000':[6471251,7241655,7051747],'706300':[29610587,31917931,31834543],'706800':[59804,59775,65657],'445710':[4261445,4646479,4600545],'TOT':[40403087,43865843,43552492]}
p('== B-1. Recalcul des nets et totaux (p. 25 et 26)')
for k,v in T.items():
    for i,(b,a,n) in enumerate(v):
        if b is not None and a is not None and b+a!=n: p(f'  {k} {EX[i]} : {e(b)} {e(a)} = {e(b+a)} ; imprimé {e(n)} ; ERREUR {e(n-(b+a))}')
for i,(b,a,pb,n) in enumerate(C530):
    p(f'  530 {EX[i]} : {e(b)} + {e(a)} {e(pb)} = {e(b+a+pb)} ; imprimé {e(n)} ; {"OK" if b+a+pb==n else "ERREUR"}')
    s=sum(T[k][i][2] for k in T)+n; p(f'  TOTAL p. 25 {EX[i]} : Σ nets imprimés {e(s)} ; imprimé {e(TOT25[i])} ; écart {e(s-TOT25[i])}')
    s26=P26['706000'][i]+P26['706300'][i]+P26['706800'][i]+P26['445710'][i]; p(f'  TOTAL p. 26 {EX[i]} : Σ lignes {e(s26)} ; imprimé {e(P26["TOT"][i])} ; écart {e(P26["TOT"][i]-s26)}')
# ---- (a) par mode
z=F[F.tot_ttc_c==0]
def compta(i,mode,variant='net'):
    if mode=='CB': return T['511210'][i][2]
    if mode=='CHQ': return T['511200'][i][2]
    if mode=='KDOLE': return T['511240'][i][2]
    if mode=='TR': return T['511220'][i][2]+T['511221'][i][2]
    if mode=='CHV': return T['511230'][i][2]
    if mode=='ESP': return C530[i][3] if variant=='net' else C530[i][0]+C530[i][2]
rows=[]
for i,ex in enumerate(EX):
    for m in ['CB','CHQ','KDOLE','TR','CHV','ESP']:
        fm='CHQ' if m=='CHQ' else m
        f=F[(F.ex==ex)&(F.mod_regl==m)].montant_c.sum() if m!='KDOLE' else 0
        f9=z[(z.ex==ex)&(z.mod_regl==m)].montant_c.sum() if m!='KDOLE' else 0
        rows.append((ex,m,compta(i,m),f,compta(i,m)-f,f9,compta(i,m)-(f-f9)))
R=pd.DataFrame(rows,columns=['ex','mode','compta','F','compta-F','F etat9','compta-(F-etat9)'])
cum=R.groupby('mode').sum(numeric_only=True).reset_index(); cum['ex']='cumul'
R=pd.concat([R,cum]); tot=R.groupby('ex').sum(numeric_only=True).reset_index(); tot['mode']='TOTAL'
R=pd.concat([R,tot])
for col in ['compta','F','compta-F','F etat9','compta-(F-etat9)']: R[col]=R[col].map(e)
p('\n== B-1 (a) compta − F par mode (KDOLE isolé ; F n\'a pas de mode KDOLE)'); p(R.to_string(index=False))
p('Variante ESP sans les « ajustements nets » (530 brut − pourboires) :',[e(C530[i][0]+C530[i][2]-F[(F.ex==ex)&(F.mod_regl=="ESP")].montant_c.sum()) for i,ex in enumerate(EX)],
  ' ; ajustements nets',[e(C530[i][1]) for i in range(3)])
p('\n== B-1 (b) (c) (d)')
for i,ex in enumerate(EX):
    enc=TOT25[i]; ca=P26['706000'][i]+P26['706300'][i]+P26['445710'][i]; f=F[F.ex==ex].montant_c.sum(); f9=z[z.ex==ex].montant_c.sum()
    ca_imp=P26['TOT'][i]-P26['706800'][i]
    p(f'  {ex} : (b) enc − F {e(enc-f)} ; enc − (F − etat9) {e(enc-f+f9)} ; (c) enc − CA {e(enc-ca)} [CA imprimé − 706800 : {e(enc-ca_imp)} ; 511221 corrigé : {e(enc+5-ca)}] ; (d) CA − F {e(ca-f)} ; CA − (F − etat9) {e(ca-f+f9)}')
encs=sum(TOT25); cas=sum(P26['706000'][i]+P26['706300'][i]+P26['445710'][i] for i in range(3)); fs=F.montant_c.sum()
p(f'  cumul : (b) {e(encs-fs)} ; (c) {e(encs-cas)} ; (d) {e(cas-fs)} ; (d) hors etat 9 {e(cas-fs+z.montant_c.sum())}')
# ---- B-2
p('\n== B-2. Lignes etat = 9')
S['m_c']=S.montant.astype(float).map(c); S['ex']=np.where(S.date_ticket<'2023-04-01',EX[0],np.where(S.date_ticket<'2024-04-01',EX[1],EX[2]))
s9=S[S.etat=='9']
p(s9.groupby(['ex','mod_regl']).m_c.agg(['size','sum']).assign(sum=lambda d:d['sum'].map(e)).to_string())
for i,ex in enumerate(EX):
    for m in ['CB','TR','CHV','ESP']:
        g=e(T['511210'][i][2]-F[(F.ex==ex)&(F.mod_regl=='CB')].montant_c.sum()) if m=='CB' else None
    cb9=s9[(s9.ex==ex)&(s9.mod_regl=='CB')].m_c.sum()
    p(f'  {ex} : CB etat 9 {e(cb9)} contre (511210 − F CB) {e(T["511210"][i][2]-F[(F.ex==ex)&(F.mod_regl=="CB")].montant_c.sum())}')
p('Valeurs distinctes des colonnes natives absentes de F :')
for k in ['no_caisse','caissier','cod_clt','tot_rem_globale','tot_rem_lig','etat','(null)','mf_number','mf_desc']:
    p(f'  {k} :',S[k].value_counts(dropna=False).to_dict())
p('  sy_uk : valeurs distinctes',S.sy_uk.nunique(),' ; notes distinctes (id)',S.id.nunique(),' ; tot_sum / tot_tax_sum : numériques, cumuls (non énumérés)')
p('  mod_regl (natif) :',S.mod_regl.value_counts().to_dict(),' ; F :',F.mod_regl.value_counts().to_dict())
# ---- B-3
p('\n== B-3. F par mois et par mode (euros)')
F['mois']=F.dateTicket.str[:7]
M=F.pivot_table(index='mois',columns='mod_regl',values='montant_c',aggfunc='sum',fill_value=0)
p((M/100).round(2).to_string())
for y in ['2023','2024','2025']:
    mar=M.loc[f'{y}-03','CHV'] if f'{y}-03' in M.index else 0; apr=M.loc[f'{y}-04','CHV'] if f'{y}-04' in M.index else 0
    p(f'  CHV mars {y} {e(mar)} ; avril {y} {e(apr)}')
p('  CHV par exercice (F) :',{ex:e(F[(F.ex==ex)&(F.mod_regl=="CHV")].montant_c.sum()) for ex in EX},' ; compta :',[e(T['511230'][i][2]) for i in range(3)])
p('  CHV cumul 3 ex. : F',e(F[F.mod_regl=='CHV'].montant_c.sum()),' compta',e(sum(T['511230'][i][2] for i in range(3))))
# ---- B-17
p('\n== B-17. Tableau 63 à périmètre égal (CA = 706000 + 706300 + 445710, somme des lignes)')
for i,ex in enumerate(EX):
    ca=P26['706000'][i]+P26['706300'][i]+P26['445710'][i]
    s1=H[(H.ex==ex)&(H.serie==1)].tot_ttc_c.sum(); cc=H[H.ex==ex].tot_ttc_c.sum(); f=F[F.ex==ex].montant_c.sum(); f9=z[z.ex==ex].montant_c.sum()
    p(f'  {ex} : CA {e(ca)} ; − H série 1 {e(ca-s1)} ; − C {e(ca-cc)} ; − F {e(ca-f)} ; − (F sans etat 9) {e(ca-f+f9)} ; CA imprimé − 706800 − série 1 {e(P26["TOT"][i]-P26["706800"][i]-s1)}')
out.close()
