"""B2 : (a) décomposition du rappel de TVA de la proposition (TVA reconstituée − 445710) ; part de l'erreur de taux ;
rappel autonome (sans reconstitution). (b) comptabilité p.25 (scan) par mode contre F ; règlements sur notes à 0 €."""
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import *
T=pd.read_pickle(CA+'B5_tickets.pkl')
REC={'TTC':[597265.42,577522.00,575252.68],'HT':[534229.87,516203.20,514595.63],'TVA':[63035.55,61318.80,60657.04]}
LIQ_RED=[8917.07,8450.72,8253.27]; COEF=[2.94,3.02,3.10]; LIQ_RED_TVA=[1324.68,1286.88,1242.14]
print('===== (a)')
for i,ex in enumerate(EX):
    z=T.loc[ex]; leg=z.leg.sum()/100; app=z.app.sum()/100; tot=z.tot_tva.sum()/100; l20=z.l20.sum()/100
    c445=P26['445710'][i]; tv=REC['TVA'][i]
    liq_av=LIQ_RED[i]/0.05; liq=liq_av-3*LIQ_RED[i]; sol=REC['TTC'][i]-liq
    tva_liq=LIQ_RED_TVA[i]/0.05*0.85; tva_sol=sol/11
    print(f'{ex}: reconstitution TTC {REC["TTC"][i]:,.2f} = liquides {liq:,.2f} (avant réductions {liq_av:,.2f}) + solides {sol:,.2f} (rapport {sol/liq:.4f}, coef. {COEF[i]})')
    print(f'   TVA solides à 10 % = {tva_sol:,.2f} ; TVA liquides (réductions/0,05×0,85) = {tva_liq:,.2f} ; somme {tva_sol+tva_liq:,.2f} contre TVA reconstituée {tv:,.2f} (écart {tva_sol+tva_liq-tv:+.2f})')
    print(f'   HT solides {sol-tva_sol:,.2f} + HT liquides {liq-tva_liq:,.2f} = {sol-tva_sol+liq-tva_liq:,.2f} contre {REC["HT"][i]:,.2f}')
    print(f'   rappel lettre = {tv:,.2f} − {c445:,.2f} = {tv-c445:,.2f} = [TVA reconst. − TVA légale ventes caisse {tv-leg:,.2f}] + [TVA légale − 445710 {leg-c445:+,.2f}]')
    print(f'   [TVA légale − 445710] = effet taux {leg-app:+.2f} + arrondi caisse {app-tot:+.2f} + (TVA caisse − 445710) {tot-c445:+.2f}')
    print(f'   rappel autonome (sans reconstitution) : 445710 contre TVA légale : {leg-c445:+.2f} ; indéterminés à 20 % : {l20-c445:+.2f} ; + TVA pourboire 10 % : {leg-c445+round(P26["706800"][i]*0.1,2):+.2f} / {l20-c445+round(P26["706800"][i]*0.1,2):+.2f}')
print('===== (b)')
# comptabilité p.25 (lecture du scan Proposition_1_Lettre.pdf p.25)
CPT={'CHQ':[4627.35,3600.12,4529.10],'CB':[370144.08,399903.10,397677.38],'TR':[9486.32+935.10,9105.04+1024.27,4708.89+4392.72],
     'CHV':[14715.00,23300.00,20405.00],'KDOLE':[290.00,525.00,390.00],'ESP':[3330.63,5958.90,2804.75]}
TOTP=[403528.48,443416.43,434907.84]
print('   contrôle 511221 2023-2024 : 2 240,05 − 1 215,73 =',round(2240.05-1215.73,2),'(imprimé 1 024,27)')
F=pd.read_pickle(C23+'F.pkl'); fz=F[F.tot_ttc==0]
rows=[]
for i,ex in enumerate(EX):
    f=F[F.ex==ex]; z=fz[fz.ex==ex]
    tot_c=sum(v[i] for v in CPT.values()); print(f'{ex}: Σ modes compta {tot_c:,.2f} (imprimé {TOTP[i]:,.2f}) ; F {f.montant.sum():,.2f} ; compta − F {tot_c-f.montant.sum():+,.2f} ; règlements notes à 0 € {z.montant.sum():,.2f} ; compta − (F − notes à 0 €) {tot_c-f.montant.sum()+z.montant.sum():+,.2f}')
    for m,lab in [('CB','CB'),('CHQ','CHQ'),('TR','TR'),('CHV','CHV'),('ESP','ESP')]:
        fm=f[f.mod_regl==m].montant.sum(); zm=z[z.mod_regl==m].montant.sum(); cm=CPT[lab][i]+(CPT['KDOLE'][i] if m=='CHQ' else 0)
        rows.append([ex,m,round(cm,2),round(fm,2),round(cm-fm,2),round(zm,2),round(cm-(fm-zm),2)])
    cpt_ca=c(P26['706000'][i])+c(P26['706300'][i])+c(P26['445710'][i])+c(P26['706800'][i])
    print(f'   encaissements compta (511/530, p.25) − CA comptable TTC avec 706800 (p.26) : {tot_c-cpt_ca/100:+,.2f} ; sans 706800 : {tot_c-(cpt_ca-c(P26["706800"][i]))/100:+,.2f}')
R=pd.DataFrame(rows,columns=['ex','mode','compta (KDOLE en CHQ)','F','compta−F','dont notes à 0 € (F)','compta−(F−notes 0 €)']); print(R.to_string())
