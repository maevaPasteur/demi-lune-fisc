# Journal de verification independante - incertitudeDisparu

Date : 2026-06-09
Verificateur : agent independant
Methode : re-execution des scripts 08, 09, 10, 11 via `/tmp/xlsenv/bin/python <script>.py`
(Python 3.14.2, xlrd) depuis le dossier `incertitudeDisparu`, puis recalculs de controle
sur les fichiers sources `public/documents/caisse-enregistreuse/ANNEXE-*.xls`.

Toutes les annexes attendues sont presentes. Les 4 scripts s'executent sans erreur et
regenerent leurs JSON.

---

## 1. Total DEL = 430 763 € et exclusion du pied "Nb lignes"

VERDICT : CONFIRME (avec nuance d'arrondi).

- Recalcul direct sur ANNEXE-E (3 exos), lignes DEL uniquement, pieds de page exclus :
  - 2022-2023 : 193 005,09 € (8 014 lignes)
  - 2023-2024 : 140 686,55 € (6 943 lignes)
  - 2024-2025 :  97 071,51 € (6 345 lignes)
  - **TOTAL EXACT = 430 763,15 €** (21 302 lignes) -> arrondi = **430 763 €**. CONFORME.

- Exclusion du pied "Nb lignes" : CONFIRMEE et CRITIQUE.
  Il y a 12 lignes de pied de page detectees (filtre `"nb lignes" in dateEven` OU `noCaisse` vide).
  La somme des montants de ces pieds = 430 763,15 €, soit EXACTEMENT le total DEL.
  Sans l'exclusion, le total doublerait a ~861 526 €. Le filtre est donc indispensable et correct.

- NUANCE : les scripts 08 et 11 AFFICHENT "430 764 €" (et l'ecrivent dans le JSON `totaux`),
  parce qu'ils arrondissent CHAQUE exercice a 0 decimale AVANT de sommer
  (193 005 + 140 687 + 97 072 = 430 764). C'est un artefact d'agregation d'arrondis : +1 €.
  Le chiffre cle reel de 430 763 € (claim) est exact ; c'est le JSON intermediaire qui derive de 1 €.
  Gravite : mineure (cosmetique), mais a corriger pour coherence (sommer puis arrondir).

## 2. Les 9 erreurs de quantite = ~140 221 € ; 4 geantes factorisent exactement

VERDICT : CONFIRME pour le total et le nombre ; CONFIRME pour les factorisations geantes
(via script 09), mais INCOHERENCE D'AFFICHAGE dans le script 10.

- Script 10 : 9 lignes a quantite >= 12, somme = **140 221,10 €** (~140 221, claim OK), soit 33% du total DEL.
- Les 4 montants geants sont : 68 993,10 / 44 955,00 / 19 600,00 / 4 455,00.
  Factorisations du claim verifiees a la main :
  - 6,90 x 9999 = 68 993,10 OK
  - 45,00 x 999 = 44 955,00 OK
  - 19,60 x 1000 = 19 600,00 OK
  - 45,00 x 99 = 4 455,00 OK
  Le script 09 (`factorise`, priorite fat-finger 9999/999/99) RESTITUE bien ces 4 factorisations
  [EXACT]. CONFORME au claim.

- DIVERGENCE INTER-SCRIPTS : le script 10 (`min_articles`, plus grand prix de la grille ventes
  qui divise le montant) affiche pour les MEMES lignes des factorisations differentes et moins
  parlantes :
  - 68 993,10 = 9,9 x 6969  (au lieu de 6,90 x 9999)
  - 19 600,00 = 50,0 x 392  (au lieu de 19,60 x 1000)
  (les deux autres geantes coincident : 45 x 999 et 45 x 99).
  Les deux lectures sont arithmetiquement exactes mais racontent une histoire differente.
  Pour la defense, c'est le script 09 qu'il faut citer (factorisations "fat-finger" lisibles),
  pas le tableau "A" du script 10. Gravite : moyenne (risque de contradiction si les deux
  sorties sont produites cote a cote devant l'administration).

## 3. 9 sessions Z ou suppr > CA du jour ; Z3015 : CA 2563 vs suppr 69557

VERDICT : CONFIRME.

- Script 11 : 659 sessions Z au total ; **9 sessions** avec suppr > CA (et CA > 0). CONFORME.
- Z 3015 (2022-2023) : CA tickets = 2 563,40 € ; suppr = 69 556,60 € (37 lignes).
  Arrondi -> CA 2563, suppr 69557. CONFORME au claim.
- Top sessions coherentes (Z3216 : 1686 / 45280 ; Z3026 : 2210 / 20088, etc.).

## 4. Triangulation CA : A = 1 275 924, H = 1 277 216, encaissements = 1 275 980

VERDICT : CONFIRME.

- Cumul 3 exercices (script 11, JSON `triangulation`) :
  - CA synthese ANNEXE-A : 1 275 924 € (claim OK)
  - CA liste tickets ANNEXE-H : 1 277 216 € (claim OK)
  - Encaissements ANNEXE-A : 1 275 980 € (claim OK)
  - Ecart max (H vs A) = +1 292 € = 0,10 % du CA. La formule du script (`abs(ca-enc)<100`)
    ne couvre PAS l'ecart H-A ; mais le claim "< 0,2%" est respecte.
- Remarque : l'ecart encaissements vs CA est +56 € (encaissements > CA), localise sur
  2024-2025 (CA 437 698 vs enc 437 754). Sub-millieme, sans impact materiel.

## 5. Especes = 1,3 % du CA

VERDICT : CONFIRME.

- Especes totales = 17 042 € sur 1 275 980 € d'encaissements = **1,3 %** (global). CONFORME.
- Par exercice : 0,9 % / 1,9 % / 1,2 %. Le 1,3 % est bien la moyenne ponderee globale,
  pas une valeur par exo. (a preciser dans la redaction pour eviter toute ambiguite.)

---

## Hypotheses fragiles / reserves a signaler

1. **Arrondi d'agregation (08 et 11)** : "430 764" dans les JSON `totaux` vs 430 763,15 reel.
   Corriger pour annoncer 430 763 € partout.

2. **Double recit de factorisation (09 vs 10)** : pour 2 des 4 geantes, le script 10 propose
   une autre decomposition. Ne presenter qu'une version (la 09) en externe.

3. **Verrou approvisionnement non recalcule ici** : le script 08 AFFIRME que "les achats
   boissons se reconcilient et le stock est stable" mais ne le DEMONTRE pas dans ce script
   (pas de lecture d'achats/stock). C'est une assertion importee d'un autre module ; a ne pas
   presenter comme prouvee par 08. Hypothese a etayer par les modules conso/achats.

4. **Diagnostic MACRO assume** : aucune classification ligne a ligne des 21 302 DEL. La these
   "workflow, pas occultation" repose sur 2 verrous (paiement + appro) + la preuve de
   distribution (script 10 B), pas sur une justification individuelle. Le script le dit
   honnetement ("reserve"), mais c'est le point que l'administration attaquera.

5. **ANNEXE-F ecartee** : le choix d'ecarter ANNEXE-F (reglements, qui double-compte) au profit
   d'ANNEXE-A est documente mais structurant ; a justifier explicitement face au verificateur.

## Synthese

Les 5 chiffres cles du claim sont CONFIRMES sur le fond. Deux frictions purement techniques :
(a) un +1 € d'arrondi d'agregation dans les JSON (430 764 affiche vs 430 763 reel), et
(b) une incoherence de presentation des factorisations geantes entre 09 et 10. Aucune erreur
materielle. Les reserves portent surtout sur le caractere MACRO du diagnostic et sur le verrou
"approvisionnement" qui est asserte mais pas prouve dans ces 4 scripts.
