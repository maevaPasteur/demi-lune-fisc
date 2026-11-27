"""D-13 : services des 14 juillet et des week-ends du « Week-end gourmand du Chat Perché » (dates de sources publiques :
30/09-02/10/2022, 30/09-01/10/2023, 27-29/09/2024 ; identification avec le « Chat Gourmand » de l'attestation : inférence).
Effet de l'hypothèse « tables 116 et 117 : + 2 à + 4 places chacune ». Sortie : out/B1/D13.txt"""
import sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from B1_common import *
p=out('D13.txt'); S=pd.read_pickle(Q+'S92.pkl')
J=['2022-07-14','2023-07-14','2024-07-14']; CP=['2022-09-30','2022-10-01','2022-10-02','2023-09-30','2023-10-01','2024-09-27','2024-09-28','2024-09-29']
x=S[S.date.isin(J+CP)].copy(); x['jour']=pd.to_datetime(x.date).dt.day_name()
p('Services de ces journées (pièce 92) :'); p(x[['date','jour','service','espace','places','cv','occ']].to_string())
p('Journées sans service :',sorted(set(J+CP)-set(S.date)))
for add in (4,8):
    y=x.copy(); y['pl2']=y.places+add; y['o2']=y.cv/y.pl2*100
    p(f'Hypothèse + {add} places ces jours-là : services > 100 % parmi eux {int((y.cv>y.places).sum())} → {int((y.cv>y.pl2).sum())} ; total des 42 → {42-int((y.cv>y.places).sum())+int((y.cv>y.pl2).sum())}')
