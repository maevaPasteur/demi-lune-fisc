"""B0 point 4 et 8 : événements E, identifiants, enchaînements, DEL (nombre, montant, aberrantes).
Sortie : out/s04_evenements.txt"""
import pandas as pd, numpy as np
O='scripts/lot7-tables-virtuelles/out/'
E=pd.read_pickle(O+'B0cache/E.pkl')
out=open(O+'B0_s04_evenements.txt','w')
def p(*a): print(*a); print(*a,file=out)
p('Événements :',len(E),' par exercice',E.groupby('ex').size().to_dict())
p('Types :',E.typEven.value_counts().to_dict())
p('id min/max :',E.id.min(),E.id.max(),' ; distincts',E.id.nunique(),' ; manquants',(E.id.max()-E.id.min()+1)-E.id.nunique())
for ex,g in E.groupby('ex'): p('  ',ex,'id',g.id.min(),'->',g.id.max(),' n',len(g),' trous',(g.id.max()-g.id.min()+1)-g.id.nunique())
p('id croissant avec ordre du fichier :',(E.id.diff().dropna()==1).all())
D=E[E.typEven=='DEL']
p('DEL :',len(D),' montant',round(D.amount.sum(),2),' par exercice',D.groupby('ex').amount.agg(['size','sum']).round(2).to_dict())
p('DEL montants <0 :',(D.amount<0).sum(),' =0 :',(D.amount==0).sum())
p('DEL rattachés à un Z :',D.no_zEport.notna().sum(),' couples (date,Z) :',len(D[['dateEven','no_zEport']].drop_duplicates()))
top=D.sort_values('amount',ascending=False).head(8)
p(top[['dateEven','heureEven','no_zEport','amount','id','ex']].to_string())
ab=top.head(4); p('4 plus fortes :',round(ab.amount.sum(),2),f'{ab.amount.sum()/D.amount.sum()*100:.2f} %')
p('Total hors 4 :',round(D.amount.sum()-ab.amount.sum(),2))
for v in [68993.10,44955,19600,4455]:
    for q in range(2,1000):
        pass
# décompositions plausibles prix x quantité
for _,r in ab.iterrows():
    cand=[(q,round(r.amount/q,2)) for q in range(2,1000) if abs(r.amount/q-round(r.amount/q,2))<1e-9 and round(r.amount/q,2) in (100,45,55,99,50,69,68.9,69.9,9.9,19.9)]
    p('  ',r.dateEven,r.amount,'décompositions candidates',cand[:10])
D.to_pickle(O+'B0cache/DEL.pkl')
out.close()
