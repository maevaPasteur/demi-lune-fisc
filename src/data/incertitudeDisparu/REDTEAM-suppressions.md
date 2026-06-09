# RED TEAM - Attaque fiscale des 430 763 € de lignes supprimees (DEL)

Position : INSPECTEUR DES IMPOTS hostile. Objectif : requalifier les suppressions en recettes
dissimulees, ou a defaut maximiser le rappel et les penalites. Toutes les verifications ci-dessous
ont ete reproduites avec /tmp/xlsenv/bin/python sur les ANNEXES certifiees.

## VERIFICATIONS REPRODUITES (les chiffres de la defense tiennent factuellement)
- Total DEL = 430 763 € / 21 302 lignes (script 08, reproduit). Hors pieds de page « Nb lignes ».
- CA declare = encaissements : 1 275 924 vs 1 275 980 (ecart -56 €). Especes = 17 042 € = 1,3 %.
- Triangulation A/H/encaissements ~1,276 M€, ecart cumule < 0,2 %.
- 9 sessions Z ou suppr > CA du jour (script 11, reproduit).
- 9 « erreurs de quantite » = 140 355 € (recalcule : top-9 DEL = 140 355 €, soit 32,6 %).

MAIS la verification fait apparaitre des FAILLES que le fisc exploitera.

---

## ATTAQUE FAIT PAR FAIT

### FAIT 1 - « 430 763 €, 34 % du CA, mais c'est du workflow »
**Attaque :** 34 % du CA en lignes effacees est en soi un indice de gravite (CGI art. L. 47 A / L. 74,
opposition a controle ; jurisprudence CHR : un taux massif de suppressions justifie le rejet de
comptabilite, art. L. 193 LPF — la charge de la preuve BASCULE alors sur le contribuable). Le simple
fait de retirer la ligne « Nb lignes » pour passer de 861 k a 430 k est un choix de retraitement du
**contribuable**, que le fisc n'est pas tenu d'accepter : il peut retenir le montant brut du journal.
**La defense tient-elle ? OUI partiellement.** Le double-comptage des pieds de page est demontrable
ligne a ligne (verifiable). Mais le taux de 34 % reste l'argument-massue du rejet de comptabilite.

### FAIT 2 - « 140 221 € = 9 erreurs de quantite »
**Attaque :** ANNEXE-E ne contient AUCUNE colonne quantite ni produit (cols : noCaisse, dateEven,
heureEven, typEven, caissier, no_zEport, mf_Number, amount, id). La decomposition « prix carte ×
quantite » est une **reconstruction a posteriori, non sourcee**. Pire : les deux fichiers de la defense
se contredisent sur la meme ligne de 68 993,10 € (aberrations_del.json : 6,90 € × 9999 ; 
del_justification.json : 9,90 € × 6969). Cette incoherence interne sera retournee comme preuve que le
chiffrage est « habille ». Et meme accepte, cela ne neutralise que 140 k : il RESTE 290 409 € de DEL de
taille normale.
**La defense tient-elle ? OUI sur les 4 geantes (68 993, 44 955, 19 600, 4 455 : montants impossibles a
servir/encaisser), NON sur la methode** (contradiction a corriger, source quantite a produire).

### FAIT 3 - « Sur 9 Z, suppr > CA du jour : forcement fictif » (la plus forte)
**Attaque :** argument valable pour CES 9 sessions seulement (~148 k concentres sur les Z geants). Il ne
dit RIEN des 647 autres Z, ou les suppressions sont INFERIEURES au CA et donc parfaitement compatibles
avec des ventes encaissees au noir puis effacees. Le fisc concede les 9 et garde les ~282 k restants.
**La defense tient-elle ? OUI mais portee etroite.** Imparable sur les 9 Z ; non generalisable.

### FAIT 4 - « Les prix des DEL epousent la grille du menu »
**Attaque : ARGUMENT A DOUBLE TRANCHANT — le plus dangereux pour la defense.** Si les lignes effacees
ont exactement la distribution de prix des VRAIES ventes (3,90 : 8,7 % vs 8,6 % ; 18,60 : 6,3 % vs 6,0 %),
c'est precisement ce qu'on attend de **vraies ventes encaissees puis supprimees du journal**. La defense
prouve elle-meme que les DEL sont de vrais articles vendus, pas des artefacts techniques. Verifie :
hors 9 geantes, 263 k de DEL tombent dans la bande 5–100 € (taille repas/boisson normale).
**La defense tient-elle ? NON, l'argument se retourne.** A reformuler : la similarite de distribution
n'a de valeur que COUPLEE au verrou paiement (sinon elle accuse).

### FAIT 5 - Triangulation 3 exports a 1,276 M€
**Attaque :** les 3 exports proviennent du MEME logiciel de caisse (A = synthese, H = tickets,
encaissements = bloc A). Convergence interne ≠ exhaustivite : si des ventes sont sorties AVANT
consolidation (ligne supprimee = jamais agregee au ticket), les 3 convergent quand meme, a un CA ampute.
La triangulation prouve la coherence de la caisse, pas l'absence d'omission. Le seul juge de
l'exhaustivite est le **releve bancaire reel** + les achats — absents de ces 3 sources.
**La defense tient-elle ? OUI pour la coherence interne, NON comme preuve d'exhaustivite.**

### FAIT 6 - Verrou paiement : CA = encaissements, especes 1,3 %
**Attaque la plus serieuse contre la defense :** (a) l'egalite CA = encaissements est **quasi
tautologique** : les deux sortent de la caisse (ANNEXE-A), pas du compte bancaire. Elle ne prouve rien
sur l'occultation. (b) Le plafond « 17 042 € d'especes » ne vaut QUE pour l'occultation en especes. Or
les DEL pourraient avoir ete re-encaissees en **CB / ticket-resto / cheque-vacances** sur un ticket
agrege different (mecanisme « facture sans detail » admis par la defense elle-meme !). Le canal n'est
donc PAS limite a 1,3 %. La bancarisation 98,7 % est affirmee mais **non etayee par les releves** dans le
dossier.
**La defense tient-elle ? PARTIELLEMENT.** Le 1,3 % especes plafonne reellement l'occultation-especes
(fort). Mais le verrou « CA=encaissements » est circulaire, et le canal CB n'est pas ferme. **Faille
majeure : produire les releves bancaires.**

### FAIT 7 - Verrou approvisionnement : achats reconcilies, stock stable
**Attaque DEVASTATRICE — la defense se contredit avec son propre modele :** resultats_montecarlo_ajuste2
.json affiche un « disparu » alcool de **76 113 € en mediane (IC 62 262 – 87 321 €), soit 21,5 % des
achats d'alcool**, valorise au prix de revente. Il y a DONC des inputs pour des ventes fantomes, a
hauteur de 62–94 k. Plus 35 690 € de softs « non fiables » non bilantes. Le fisc dira : voila l'amont
des ventes occultees, et il recoupe l'ordre de grandeur des 290 k de DEL « normales ». Affirmer « pas
d'inputs » alors que le propre Monte Carlo chiffre 62–94 k de disparu est intenable en l'etat.
**La defense tient-elle ? NON en l'etat.** Il faut justifier le disparu alcool (pertes, casse, conso
perso, doses, offerts) AVANT de l'opposer, sinon ce fait est une arme pour le fisc.

### FAIT 8 - Menus prix custom = 21 433 € (2 %)
**Attaque :** sans portee. 2 % n'explique que 2 % ; le fisc l'ignore et garde les 98 % restants.
**La defense tient-elle ? OUI mais negligeable** (n'explique presque rien du total).

### FAIT 9 - Cartes cadeau non identifiables
**Attaque :** un mecanisme exonerant INVOQUE mais NON PROUVE et non chiffrable est nul en
contentieux. « Je ne peux pas le decomposer mais c'est legitime » = aveu d'absence de tracabilite, lu
contre le contribuable (caisse non probante, art. L. 193 LPF). Le fisc retournera : « si vous ne pouvez
pas distinguer une carte cadeau d'une vente occultee, c'est exactement le defaut qui fonde le rejet ».
**La defense tient-elle ? NON.** Argument a manier avec prudence ; il etaye le rejet de comptabilite.

### FAIT 10 - Caisse NF525, DEL loguees et declarees
**Attaque :** NF525 logue les suppressions mais ne prouve pas leur LICEITE. Le journal certifie
documente justement l'ampleur (430 k) — c'est la PIECE A CHARGE du fisc, pas un bouclier. La traçabilite
technique de l'effacement ≠ regularite fiscale de l'operation. Un seul compte caissier « LUNA » pour les
21 302 DEL (verifie) affaiblit l'argument de controle interne.
**La defense tient-elle ? PARTIELLEMENT.** La transparence du log est un bon argument de bonne foi
(utile contre la majoration 40/80 %), mais ne neutralise pas le rappel en principal.

---

## ANGLES NON COUVERTS PAR LA DEFENSE (a anticiper)

1. **Rejet de comptabilite + reconstitution extra-comptable (L. 193 LPF).** Un taux de DEL de 34 % suffit
   a la jurisprudence CHR pour ecarter la comptabilite ; ensuite le fisc reconstitue par
   achats × coefficient. La defense raisonne « CA declare exact » alors que le fisc raisonnera
   « comptabilite non probante, donc je reconstruis ». Changement de terrain non traite.
2. **Methode coefficient / vins-liquides.** Le disparu alcool 76 k (au prix de revente) EST une
   reconstitution par les achats prete a l'emploi pour le fisc. C'est l'angle d'attaque n°1 reel.
3. **TVA.** Si requalification, rappel de TVA collectee (taux 10 % restauration / 20 % alcool) sur le
   montant retenu, en plus du BIC/IS et de l'IR. Non chiffre cote defense.
4. **Penalites.** Suppressions « systematiques » (656/659 Z, present quasi chaque jour, un seul
   operateur) = terrain pour manquement delibere (40 %) voire manoeuvres frauduleuses (80 %) si le fisc
   qualifie l'effacement de procede. La transparence NF525 (fait 10) est le meilleur contre-feu.
5. **Sessions Z manquantes / continuite.** 659 Z mais numerotation non verifiee comme continue ;
   tout trou de chrono Z serait exploite comme preuve de manipulation.
6. **Tickets-restaurant / cheques-vacances** (≈ 23 k et 47 k cumules) : canaux d'encaissement NON
   especes qui echappent au plafond « 1,3 % especes » — renforce l'attaque du fait 6.
7. **Le 1,3 % d'especes pris isolement** est en realite l'argument le PLUS solide de la defense
   (une occultation cash est plafonnee a 17 k), mais il ne couvre QUE le cash.

---

## SYNTHESE DE L'INSPECTEUR

Concessions inevitables pour le fisc : les 4 DEL geantes (138 k, montants impossibles) et les 9 Z
ou suppr > CA (148 k, partiellement les memes). Soit ~140–150 k indefendables comme recettes.

Cible retenue par le fisc : les **~290 k de DEL de taille normale**, dont la distribution epouse le
menu (fait 4 retourne), avec un amont credible (disparu alcool 62–94 k, fait 7 retourne), des canaux
d'encaissement non-especes ouverts (CB/TR/CV, fait 6), sur une comptabilite rendue non probante par le
taux de 34 % (rejet → reconstitution). Le fisc ne cherchera pas a tracer ligne a ligne : il rejettera et
reconstituera par coefficient.

La defense est SOLIDE sur : double-comptage pieds de page, 4 geantes, 9 Z, plafond especes 17 k.
La defense est FRAGILE sur : methode quantite non sourcee + contradiction, verrou paiement circulaire,
verrou achats contredit par son propre Monte Carlo, cartes cadeau non prouvees, absence de releves
bancaires, absence de reponse au scenario « rejet + reconstitution coefficient ».
