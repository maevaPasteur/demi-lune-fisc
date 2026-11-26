"""c1 : ratios de matérialité de l'erreur de paramétrage des taux de TVA.
Arithmétique pure sur des chiffres établis par les scripts précédents :
- b1_calculs.py, B-5 (TVA liquidée, TVA légale, tickets touchés, sous/sur-liquidation) ;
- s02 (Σ TTC tickets G) ; proposition p. 26 (comptes 706000, 706300, 445710) via common.P26 ;
- proposition p. 53-54 et 63-65 (droits 20 421 / 20 041 / 14 854 / 14 652 ; bases HT rehaussées) ;
- B1, B-3 et B-4 (323 références ; 1 260 + 183 lignes ; 97 769 lignes C).
Centimes entiers, aucun arrondi intermédiaire."""
import os, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import P26, e, OUT

EX = ['2022-2023', '2023-2024', '2024-2025']
TTC_G   = [40337042, 43799292, 43482786]          # Σ tot_ttc G (s02)
TVA_LIQ = [4255276, 4640008, 4592663]             # Σ tax_amount G (B1 B-5)
TVA_LEG = [4277029, 4660601, 4615280]             # TVA légale recalculée (B1 B-5)
SOUS    = [22724, 21930, 23632]                   # sous-liquidation (B1 B-5)
SUR     = [1041, 1424, 1100]                      # sur-liquidation (B1 B-5)
TK_TOUCH = [498, 439, 431]; TK_TOT = [5658, 5529, 5418]
DROITS_LETTRE = [2042100, 1485400, 1465200]       # p. 54 (arrondis à l'euro)
DROITS_DECOMPTE = [2004100, 1485400, 1465200]     # p. 63-65
BASES_REH = [17281345, 12400956, 12507616]        # p. 53 minoration CA HT
c = lambda x: int(round(x * 100))
pct = lambda a, b, d=4: f"{100*a/b:.{d}f} %".replace('.', ',')

out = []
P = lambda s='': out.append(s)
solde = [l - q for l, q in zip(TVA_LEG, TVA_LIQ)]
P('1. TVA légale − TVA liquidée (= effet de taux pur B1 B-5 + arrondi de caisse 0,70 / 0,87 / 0,85), par exercice et cumul')
for i, x in enumerate(EX):
    P(f'  {x} : {e(solde[i])} € ; / TVA liquidée {pct(solde[i], TVA_LIQ[i])} ; / CA TTC G {pct(solde[i], TTC_G[i])} ;'
      f' / droits lettre {pct(solde[i], DROITS_LETTRE[i], 2)} ; / droits décompte {pct(solde[i], DROITS_DECOMPTE[i], 2)}')
S = sum(solde)
P(f'  Cumul : {e(S)} € ; / TVA liquidée {pct(S, sum(TVA_LIQ))} ; / CA TTC {pct(S, sum(TTC_G))} ;'
  f' / droits lettre ({e(sum(DROITS_LETTRE))}) {pct(S, sum(DROITS_LETTRE), 2)} ; / droits décompte ({e(sum(DROITS_DECOMPTE))}) {pct(S, sum(DROITS_DECOMPTE), 2)}')
P(f'  Sous-liquidation brute {e(sum(SOUS))} € ; sur-liquidation {e(sum(SUR))} € ; brut / TVA liquidée {pct(sum(SOUS), sum(TVA_LIQ))}')
P(f'  Tickets touchés {sum(TK_TOUCH)} / {sum(TK_TOT)} = {pct(sum(TK_TOUCH), sum(TK_TOT), 2)}')
P(f'  Lignes C d\'articles mal paramétrés : 1 260 + 183 = 1 443 / 97 769 = {pct(1443, 97769, 2)} ; références 5 / 323 = {pct(5, 323, 2)}')
P(f'  Bases HT rehaussées (p. 53) : {e(sum(BASES_REH))} € ; base touchée par l\'erreur de taux : 0,00 €')
P()
P('2. Erreur interne du service sur les droits 2022-2023 (lettre p. 54 − décompte p. 63)')
d = DROITS_LETTRE[0] - DROITS_DECOMPTE[0]
P(f'  {e(d)} € ; rapport à l\'effet taux 2022-2023 ({e(solde[0])} €) : {d/solde[0]:.3f} ; à l\'effet taux 3 ans : {pct(d, S, 2)}')
P()
P('3. Base HT comptabilisée (706000 + 706300) − base HT légale (Σ TTC G − TVA légale)')
for i, x in enumerate(EX):
    hc = c(P26['706000'][i]) + c(P26['706300'][i])
    hl = TTC_G[i] - TVA_LEG[i]
    hliq = TTC_G[i] - TVA_LIQ[i]
    P(f'  {x} : compta {e(hc)} ; légale {e(hl)} ; écart compta − légale {e(hc - hl)} € ; (pour mémoire compta − HT caisse {e(hc - hliq)} €)')
hc = sum(c(P26['706000'][i]) + c(P26['706300'][i]) for i in range(3)); hl = sum(TTC_G) - sum(TVA_LEG)
P(f'  Cumul : compta {e(hc)} ; légale {e(hl)} ; écart {e(hc - hl)} €')
P()
P('4. TVA comptabilisée 445710 − TVA légale (rappel B1 B-7 (vi))')
for i, x in enumerate(EX):
    P(f'  {x} : {e(c(P26["445710"][i]) - TVA_LEG[i])} €')
P()
P('5. Ratios des grandeurs B1/B2 : effet de taux 647,21 € ; rappel autonome contre 445710 444,41 € (B2 1 a) ; 380 € du service')
for lab, v in [('effet de taux', 64721), ('rappel autonome', 44441), ('variante indéterminés 20 %', 62362), ('variante maximale', 80886)]:
    P(f'  {lab} {e(v)} € : / TVA liquidée {pct(v, sum(TVA_LIQ))} ; / CA TTC {pct(v, sum(TTC_G))} ; / droits décompte {pct(v, sum(DROITS_DECOMPTE), 2)} ; / bases HT rehaussées {pct(v, sum(BASES_REH), 3)}')
P(f'  380 € / rappel autonome 2022-2023 (155,84 €) : {38000/15584:.3f}')
P()
P('6. Notes de seconde série non reprises (B3 C6) : 306,80 € TTC, 32,03 € de TVA')
P(f'  / CA TTC {pct(30680, sum(TTC_G), 3)} ; TVA / TVA liquidée {pct(3203, sum(TVA_LIQ), 3)}')
P('7. Décomposition de l écart de base HT (B3 § 0 (ii)) : 649,63 − 34,59 = ' + e(64963 - 3459) + ' €')
txt = '\n'.join(out)
print(txt)
open(OUT + 'c1_materialite.txt', 'w', encoding='utf-8').write(txt + '\n')
