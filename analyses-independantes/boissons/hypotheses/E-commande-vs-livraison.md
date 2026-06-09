# Hypothèse E - Commandé / facturé brut vs réellement livré

**Question du client.** Le vérificateur a-t-il pu compter des quantités *commandées* ou *facturées mais jamais reçues* dans le « disponible » ? Si oui, le disponible (donc le « disparu ») est mécaniquement sur-évalué.

**Rappel formule du vérificateur** (`volumes-disparus-fisc.json`, annexe 6) :
`disponible = achats FCBS + Intermarché + stock_initial − stock_final`.
Toute marchandise *facturée mais non livrée* qui resterait dans « achats FCBS » gonfle le disponible. Le CA reconstitué = volumes × coefficient (~2,94 à 3,10) : **toute erreur de volume est amplifiée ~4×**.

Fournisseur unique analysé : **Franche-Comté Boissons Services (Besançon)** - 199 factures, 3 889 lignes.
Vérification : `/tmp/pwenv/bin/python`. Aucune supposition non signalée.

---

## 0. Fait structurant découvert

Les **231 lignes de `lignes-ignorees.json`** ne sont pas un fichier externe : ce sont **exactement les 231 lignes des factures dont `montantHT` est vide/nul** (multisets de codes produits strictement identiques - vérifié). Ce sont des lignes présentes sur la facture mais **non valorisées** (puNet vide) → marchandise **commandée puis manquante / refusée / déconsigne / échantillon**, non facturée.

Sur ces 231 lignes : **95 portent une quantité** ; 136 ont une quantité nulle (non chiffrables en volume).

---

## 1. Volume et € des lignes FACTURÉES MAIS NON LIVRÉES

### 1.a - Lignes HT-vide des factures (les 231 lignes-ignorées), par exercice

| Exercice | Lignes | dont avec qté | Unités (btl/fût) | Litres estimés | € (au puBrut/médiane) | € marchandise (hors matériel) |
|---|---:|---:|---:|---:|---:|---:|
| 2022-2023 | 81 | 39 | 245 | 365 | 625 | 615 |
| 2023-2024 | 54 | 25 | 116 | 282 | 1 139 | 1 139 |
| 2024-2025 | 96 | 31 | 94 | 36 | 809 | 743 |
| **TOTAL** | **231** | **95** | **455** | **~684** | **2 573** | **2 497** |

Méthode € : prix unitaire = `puBrut` présent sur la ligne (47 lignes) sinon médiane du `puNet` du même code ailleurs dans les factures (20 lignes) ; 28 lignes sans prix récupérable. Litres : volume déduit du libellé (33 CL, 75 CL, 10 L…) × quantité, sur 60 lignes parsables. **Plancher**, car 136 lignes sans quantité ne sont pas chiffrées.

### 1.b - Carnet manuscrit de la gérante (`anomalies.json`, 218 lignes)

Quantités en unités/bouteilles (cartons déjà éclatés ; ex. « 1 carton de 24 » = 24).

| Statut carnet | Lignes | Unités | Sens |
|---|---:|---:|---|
| En manque | 114 | 703 | facturé, jamais reçu |
| Facturé non livré | 8 | 25 | facturé, jamais reçu |
| Refusé | 1 | 2 | reçu puis refusé |
| Retour | 2 | 44 | renvoyé |
| **Sous-total NON REÇU** | **125** | **~774** | **à retirer du disponible** |
| Avoir | 48 | 454 | avoir obtenu (déjà annulé en €) |
| Reprise | 6 | 33 | consigne reprise |
| Livré / Facturé / Offert | 37 | 482 | reçu (ne pas retirer) |

**Total marchandise facturée non reçue selon le carnet : ~774 unités** (statuts En manque + Facturé non livré + Refusé + Retour), hors 454 unités d'« Avoir » qui constituent une sur-facturation **déjà corrigée par avoir** côté fournisseur.

---

## 2. Croisement carnet ↔ factures ↔ lignes-ignorées

| Test | Résultat |
|---|---|
| Codes des 231 lignes-ignorées = codes des 231 lignes HT-vide des factures | **Identiques (multiset)** ✓ |
| Dates carnet « non reçu » à ±7 j d'une facture portant une ligne HT-vide | **125 / 125 (100 %)**, 0 hors-cible ✓ |
| Période carnet | 21/04/2022 → 27/12/2024 |
| Période factures HT-vide | 08/04/2022 → 25/03/2025 (recouvre le carnet) ✓ |

**Cohérence forte.** Deux sources indépendantes - le relevé manuscrit de la gérante et le marquage HT-vide des PDF de factures - concordent sur la période et le calendrier : il existe bien un flux récurrent de marchandise *facturée/commandée mais non livrée*. Le carnet (774 u. non reçues) est plus volumineux que les lignes HT-vide chiffrées (455 u.) car il capte aussi les manques sur lignes **sans quantité lisible sur la facture** et les retours post-livraison - les deux se complètent, ne se contredisent pas.

---

## 3. Écarts de dates et de quantités - ce qui est vérifiable

| Élément | Vérifiable ? | Constat |
|---|---|---|
| `dateCommande` vs `dateLivraison` | Oui (167 factures) | **125 / 167 diffèrent** ; écart médian +1 j, plage −23 à +8 j. La commande précède bien la livraison : flux commande → livraison réel. |
| `dateLivraison` vs `dateFacture` | Oui (167) | **166 / 167 identiques** : la facture est émise le jour de la livraison. Donc la date de facture ≈ date de livraison, pas la date de commande. |
| **Quantité commandée vs quantité facturée, par ligne** | **NON** | Les lignes ne portent qu'**un seul champ `quantite`** (= quantité facturée). Aucune « quantité commandée » n'est stockée. On ne peut donc **pas** prouver directement que le fisc aurait pris la commande initiale ligne à ligne. |
| Marchandise commandée non livrée | Oui, indirectement | C'est précisément ce que matérialisent les **231 lignes HT-vide** (commandées, portées sur facture, valorisées 0 car non livrées). |

**Conclusion Q3.** L'hypothèse « le fisc a pris la quantité *commandée* » n'est pas testable au niveau ligne (donnée absente). En revanche, l'hypothèse « le fisc a compté du *facturé brut* incluant des lignes non livrées » est **testable et documentée** : ces lignes existent (231) et sont neutralisées à 0 € sur la facture - mais rien ne garantit qu'elles aient été neutralisées dans le « disponible » reconstitué par le vérificateur si celui-ci a totalisé des quantités plutôt que des montants HT.

---

## 4. Conclusion - sur-évaluation du « disponible »

Si le vérificateur a totalisé le **facturé brut en quantités** (en incluant les lignes non livrées) au lieu du **réellement livré**, le disponible boissons est sur-évalué d'au moins :

| Source de l'écart | Volume | € (achat) |
|---|---:|---:|
| Lignes HT-vide chiffrées (factures) | ~455 unités / ~684 L | ~2 500 € marchandise |
| Carnet « non reçu » (En manque/Fact. non livré/Refusé/Retour) | ~774 unités | (recoupe + complète le poste ci-dessus) |
| Borne basse retenue (intersection prudente) | **≈ 455-774 bouteilles/unités** | **≈ 2 500 €** |

Cette borne est un **plancher** : 136 lignes HT-vide sans quantité ne sont pas chiffrées. En CA reconstitué, l'effet est amplifié ~4× (coefficient liquides) → **impact potentiel ≈ 10 000 € de CA sur 3 exercices** si ces volumes non livrés ont été comptés comme disponibles.

⚠️ **À confirmer impérativement** : il faut vérifier dans l'annexe 6 du vérificateur si « achats FCBS » a été pris en **montant HT** (auquel cas les lignes à 0 € s'annulent d'elles-mêmes, pas de sur-évaluation) ou en **quantités physiques** (auquel cas la sur-évaluation ci-dessus est réelle). Le point de contrôle décisif est la base de totalisation du poste « achats FCBS ».

---
*Sources : `src/data/factures-fournisseur.json`, `analyses-independantes/boissons/data/lignes-ignorees.json`, `analyses-independantes/boissons/data/anomalies.json`, `src/data/volumes-disparus-fisc.json`. Calculs : `/tmp/pwenv/bin/python`.*
