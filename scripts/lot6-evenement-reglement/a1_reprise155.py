# décomposition de l'onglet « Reprise » de l'annexe 155-R3 (f = 11,7 %) et sensibilité au placebo
import openpyxl, sys
P='public/documents/pieces-lot2/155-R3-tables-videes-traces-egalites-paiements-separes.xlsx'
ws=openpyxl.load_workbook(P,read_only=True,data_only=True)['Reprise']
rows=[r for r in list(ws.iter_rows(values_only=True))[1:] if isinstance(r[0],(int,float)) and isinstance(r[1],(int,float))]
M=sum(r[1] for r in rows); O=sum(r[6] for r in rows); A=sum(r[10] for r in rows)
print(f'tables {len(rows)} montant {M:.2f} observe {O:.2f} ({O/M:.4%}) autre_jour {A:.2f} ({A/M:.4%})')
print(f'exces en euros O-A = {O-A:.2f} ({(O-A)/M:.4%} du montant)')
f=(O/M-A/M)/(1-A/M); print(f'f = {f:.4%} ; f x montant = {f*M:.2f}')
# par forme (affectation exclusive dans l'ordre (1),(2),(3)) : observe
o1=sum(r[1] for r in rows if r[3]==1); o2=sum(r[1] for r in rows if r[3]!=1 and r[4]==1); o3=sum(r[5] for r in rows if r[3]!=1 and r[4]!=1)
print(f'observe par forme : egalite {o1:.2f} ; table entiere {o2:.2f} ; lignes au meme prix {o3:.2f} ; total {o1+o2+o3:.2f}')
# esperance autre jour par forme (colonnes H, I, J) selon la meme regle d'affectation approximative : somme brute
h=sum(r[1]*r[7] for r in rows); i=sum(r[1]*r[8] for r in rows); j=sum(r[9] for r in rows)
print(f'autre jour (sommes brutes, non exclusives) : egalite {h:.2f} ; table entiere {i:.2f} ; lignes {j:.2f}')
for d in (-0.02,-0.01,0,0.01,0.02,0.03):
    a=A/M+d; print(f'placebo {a:.4%} -> f = {(O/M-a)/(1-a):.4%}')
