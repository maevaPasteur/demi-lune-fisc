# incertitudeDisparu — modèle d'incertitude du « disparu » boissons

Approche data science du disparu, complémentaire de `calculsBoissons`. Au lieu de
chercher où sont passées les bouteilles (comptabilité, point fixe), on **propage
l'incertitude** des hypothèses de consommation et on regarde la **distribution**
du disparu. Tout est reproductible (graine fixe) et chaque hypothèse est éditable.

## Idée centrale

Le pipeline `calculsBoissons` calcule `disparu = achats − stock − conso`, où la
conso utilise des doses **nominales**, **zéro perte**, **zéro conso personnel**.
C'est une hypothèse implicite d'**incertitude nulle**. On la remplace par des
fourchettes documentées (`parametres.json`) et on propage par Monte Carlo.

Deux corrections de fond, validées sur les données :
1. **Softs/eaux exclus du disparu.** La source caisse (ANNEXE-D synthèse) ne
   contient AUCUN soft vendu en direct (Coca, jus, eaux hors cocktail). Leur
   « disparu » est un **trou de données** (vente non enregistrée), pas une
   disparition. Repéré via `conso_complete = Non` + conso Coca = usage cocktail
   seul (14,6 L sur 1 964 L achetés).
2. **Incertitude par composante.** Sur-versement (vin/spiritueux au verre),
   perte de ligne (pression), doses cocktails, doses cuisine, alcool des menus
   (que la caisse ne détaille pas), conso personnel/offerts.

## Fichiers

| Fichier | Rôle |
|---|---|
| `01_extraction.py` | Joint `consoTotaleParBoisson.json` (composantes conso) + `rapprochementDisparuTotal.xlsx` (prix + drapeau « conso complète »). Sortie : `base_disparu.json`. |
| `parametres.json` | **Cœur auditable** : les fourchettes d'incertitude, justifiées, ÉDITABLES. |
| `02_montecarlo.py` | Propagation 20 000 tirages. Sortie : `resultats_montecarlo.json`. |
| `03_sensibilite.py` | Tornado : quel paramètre pilote le résultat. Sortie : `sensibilite.json`. |
| `04_signature.py` | Signature vol vs erreur de mesure, par sous-groupe. Sortie : `signature.json`. |
| `05_mapping_audit.py` | Audit mapping 4 sources (factures/cartes/caisse/inventaire) + correction du bug "Cubis de vin". Sorties : `mapping_audit.json`, `base_disparu_ajuste.json`. |
| `06_conso_staff.py` | Estimation bornee conso personnel/owner (Picon, Macvin) + softs staff. Sorties : `staff_conso.json`, `base_disparu_ajuste2.json`. |
| `07_softs_reels.py` | Recupere les ventes de softs au niveau TICKET (ANNEXE-B) et ferme le bilan (achat = vendu + cocktails + staff + stock + residu). Sortie : `softs_balance.json`. |
| `08_reconciliation_suppressions.py` | Reconcilie les 430 k€ de lignes supprimees (DEL) : CA declare vs encaissements vs especes vs achats. Verdict = workflow, pas occultation. Sortie : `reconciliation_suppressions.json`. |
| `09_aberrations_del.py` | Identifie les 4 grosses suppressions = erreurs de quantite (prix x 9999/999/...). Sortie : `aberrations_del.json`. |
| `10_del_justification.py` | (A) erreurs de quantite a toutes echelles (9 lignes) ; (B) preuve que les suppressions epousent la grille de prix des ventes reelles. Sortie : `del_justification.json`. |
| `11_reconciliation_par_z.py` | Reconciliation par session de caisse (Z) : triangulation 3 exports certifies (A/H/encaissements) ; 9 sessions ou suppr > CA du jour. Sortie : `reconciliation_par_z.json`. |
| `REDTEAM-suppressions.md` / `VERIFICATION-chiffres.md` / `ARGUMENTAIRE-AVOCAT-suppressions.md` | Revue adversariale, verification, et argumentaire avocat (generes par agents). |
| `SYNTHESE-suppressions-DEL.md` | Trace de bout en bout du pipeline suppressions. |
| `doses_cliente/` | Trace des doses reelles fournies par la cliente (cuisine, cocktails, menus par periode). |

## Lancer

```bash
cd src/data/incertitudeDisparu
/tmp/xlsenv/bin/python 01_extraction.py
/tmp/xlsenv/bin/python 05_mapping_audit.py            # audit + base corrigee
/tmp/xlsenv/bin/python 02_montecarlo.py               # disparu sur base brute
/tmp/xlsenv/bin/python 02_montecarlo.py base_disparu_ajuste.json resultats_montecarlo_ajuste.json
/tmp/xlsenv/bin/python 03_sensibilite.py
/tmp/xlsenv/bin/python 04_signature.py
```

## Bug de mapping trouve (Cubis de vin)

Le scan d'orphelins (conso>0, achat~0) ne revele qu'UN bouton generique non
ventile : "Cubis de vin" = 427 L de vin vendus au verre/pichet sans couleur,
non rattaches aux vins maison. Redistribues au prorata sur Aligote/Cap des
Pins/Chusclan => disparu vins maison -427 L / -11 k€. Hypothese tracee et
editable. Le reste du mapping (renommages de carte, Macon) est sain : pas de
decalage de carte mesurable sur le disparu.

## Limites (à lire avant d'utiliser le chiffre)

- Les fourchettes de `parametres.json` sont des **ordres de grandeur métier**, à
  valider/ajuster par la cliente (vraies doses au verre, doses de cuisson, conso
  personnel réelle). Le but est de montrer la **dépendance** du disparu à ces
  hypothèses, pas de figer un chiffre.
- Le modèle ne traite PAS le coefficient de reconstitution du fisc (×3,1), qui
  est l'autre moitié du litige.
- Valorisation au **prix de revente carte** (terrain du fisc), pas au coût.
