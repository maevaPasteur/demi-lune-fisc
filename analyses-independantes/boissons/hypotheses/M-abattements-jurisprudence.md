# Hypothèse M — Abattements jurisprudence (offerts + pertes + casse + personnel)

**Question.** Notre décomposition chiffre « pertes + consommation personnel » à **13 283 €** en appliquant les taux du fisc (5 % + 5 % = 10 %, bière 15 %) à nos achats réels. La jurisprudence admet des abattements plus élevés en restauration. De combien l'écart de disparition s'explique-t-il EN PLUS si on retient les taux admis par la jurisprudence ?

## Données de référence (vérifiées)

| Donnée | Source | Valeur |
|---|---|---|
| Achats boissons HT (3 ans) | `disparitions.json` → `global.achatBoissonsHT.total` | **126 752,49 €** |
| Disparition (coût HT) | `disparitions.json` → `global.valDisparitionCoutHT.total` | **58 059,52 €** |
| Bière HT | `disparitions.json` → `parCategorie.biere.achatHT` | **12 163,55 €** |
| Abattements fisc | `reconstitution-administration.json` → `methode.abattements` | remise 5 %, pertes 5 %, conso perso 5 % ; **bière 15 %** (conso perso + pertes) |

> NB : l'« achats réels » de 137 971 € HT issu de `achats-exercice.json` inclut alimentaire/matériel/café/eau hors périmètre de disparition ; la base boissons retenue par tout le dossier est bien **126 752 €**.

---

## 1. Taux du FISC — VÉRIFIÉ (le vérificateur les applique lui-même)

Le fisc applique trois abattements de 5 % (remise, pertes, conso personnel) sur le CA liquide, et un abattement **spécifique de 15 %** sur la bière (`notesMethodologiques` + ingrédient « Bière », ligne `consoPersonnelPertesPct: 0.15`).

**Notre chiffrage actuel « pertes + personnel »** = 10 % × 126 752 + supplément bière (15 % au lieu de 10 %) :

- 10 % × 126 752,49 = **12 675,25 €**
- + 5 % bière (15 %−10 %) × 12 163,55 = **608,18 €**
- **= 13 283,43 €** ✔ (correspond exactement au « 13 283 € » du dossier)

**Ce que nous n'avons PAS compté : la REMISE 5 %**, que le fisc applique pourtant lui-même :

- **Remise 5 % × 126 752,49 = 6 337,62 €**

Donc le **total des abattements réellement appliqués par le fisc** (remise + pertes + perso + 5 % bière) = **19 621 €**, soit **33,8 %** de la disparition de 58 060 € — alors que nous n'en revendiquions que 13 283 € (**22,9 %**). À taux fisc inchangés, la remise oubliée couvre déjà **+6 338 €** de plus.

---

## 2. Taux JURISPRUDENCE — ARGUMENT JURIDIQUE (admis mais à plaider)

La jurisprudence admet en restauration un abattement global **22 à 25 %** au titre des offerts + pertes + casse + consommation du personnel (déjà cité dans `src/data/defense.ts`, motif « Abattement de 15 % insuffisant » : *« La jurisprudence admet 22 à 25 % (CAA Paris 17/03/2021) »*).

Appliqué à nos achats réels boissons (126 752 €) :

| Taux | Montant abattu | Écart **supplémentaire** vs 13 283 € actuel | Part de la disparition (58 060 €) couverte |
|---|---|---|---|
| **22 %** | **27 886 €** | **+14 602 €** | **48,0 %** |
| **25 %** | **31 688 €** | **+18 405 €** | **54,6 %** |

→ L'écart supplémentaire expliqué par la jurisprudence vs notre chiffrage actuel est de **+14 600 € à +18 400 €**.

---

## 3. Statut probatoire — à séparer clairement

- **Taux fisc (5 %+5 %, bière 15 %, remise 5 %) = VÉRIFIÉ.** Le vérificateur les applique lui-même dans la reconstitution (`reconstitution-administration.json`). Opposable sans débat : à ce seul titre la remise 5 % oubliée vaut déjà **6 338 €**.
- **Taux jurisprudence (22–25 %) = ARGUMENT JURIDIQUE.** Admis en restauration mais **à plaider**.

**Référence jurisprudentielle.** La seule citée dans le dossier est **CAA Paris 17/03/2021** (reprise de `defense.ts`). Je ne peux pas vérifier de façon fiable le numéro de rôle exact ni que ce taux 22–25 % en émane littéralement (pas d'accès source primaire ici) : **à faire confirmer par le conseil avant de l'opposer**, et compléter idéalement par d'autres décisions (la fourchette 20–30 % offerts/pertes/personnel est classique en CAA mais doit être étayée pièce par pièce).

---

## 4. Conclusion — part de l'écart couverte SANS le stock

Avec les abattements jurisprudence **22 à 25 %** appliqués aux achats réels, on couvre **48 % à 55 %** de la disparition de 58 060 € HT **sans même mobiliser la variation de stock**. Reste à expliquer (hors stock) : **30 174 € (à 22 %) à 26 371 € (à 25 %)**.

Progression de la couverture :
- Notre chiffrage actuel (13 283 €) : **22,9 %**
- Fisc complet, remise 5 % réintégrée (19 621 €) : **33,8 %**
- Jurisprudence 22 % (27 886 €) : **48,0 %**
- Jurisprudence 25 % (31 688 €) : **54,6 %**
