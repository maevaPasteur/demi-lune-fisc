"""B-21 : sommes H (série 1 et deux séries) et F par année civile, pour comparaison aux annexes A (année civile) si elles sont produites."""
import pandas as pd
CA='scripts/lot6-evenement-reglement/cache/'; H=pd.read_pickle(CA+'H.pkl'); F=pd.read_pickle(CA+'F.pkl')
e=lambda n:f"{n/100:,.2f}".replace(',',' ').replace('.',',')
out=open('scripts/lot6-evenement-reglement/out/t07_annees_civiles.txt','w')
for y in ['2022','2023','2024','2025']:
    s1=H[(H.serie==1)&H.date_ticket.str.startswith(y)].tot_ttc_c.sum(); a=H[H.date_ticket.str.startswith(y)].tot_ttc_c.sum(); f=F[F.dateTicket.str.startswith(y)].montant_c.sum()
    s=f'{y} : H série 1 {e(s1)} ; H deux séries {e(a)} ; F {e(f)} ; jours {H[H.date_ticket.str.startswith(y)].date_ticket.nunique()} ; du {H[H.date_ticket.str.startswith(y)].date_ticket.min()} au {H[H.date_ticket.str.startswith(y)].date_ticket.max()}'
    print(s); print(s,file=out)
out.close()
