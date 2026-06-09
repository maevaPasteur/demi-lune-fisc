# Synthèse de la proposition de rectification (DGFiP)

> **SARL LA DEMI-LUNE** — restaurant, 39 rue Pasteur, 39100 Dole (Jura)
> Proposition de rectification (imprimé **3924-V-SD**) — période vérifiée **01/04/2022 → 31/03/2025** (3 exercices clos).
> Document de travail à destination de l'avocat fiscaliste.

## À propos de ce dossier

Les fichiers PDF du dossier `rapports-des-finances-publiques` sont des **scans** (aucune couche texte). Ils ont été océrisés en local (Tesseract, français), puis synthétisés section par section. Cette synthèse **retranscrit fidèlement le propos de l'administration** — elle ne contient ni argument de défense ni opinion (la défense chiffrée se trouve dans les sections *Analyses* et *Défense* du site).

- Le **texte OCR brut** intégral est conservé dans `_ocr-brut/` (4 fichiers `.txt`) pour traçabilité.
- Tout chiffre incertain à l'OCR est suivi de **« (?) »**.
- Les **Annexes A–H** et **Boissons** sont des tableaux scannés très bruités : leur OCR sert de cartographie, mais les **données propres et exploitables existent déjà en `.xls`** ailleurs dans `public/documents/` (annexes E, F, etc.). Ne pas saisir de chiffre depuis l'OCR de ces tableaux sans recoupement.

## L'enjeu chiffré (tel que proposé par l'administration)

| Poste | Droits | Intérêts + majorations | Total |
|---|---:|---:|---:|
| **Impôt sur les sociétés (IS)** | 97 510 € | 43 665 € | **141 175 €** |
| **TVA** | 49 547 € | 22 426 € | **71 973 €** |
| **Amende — distributions (art. 1759 CGI, 100 %)** | — | — | **471 826 €** |
| **TOTAL EN JEU** | | | **≈ 684 974 €** |

Détail (par exercice clos) :

| | 31/03/2023 | 31/03/2024 | 31/03/2025 |
|---|---:|---:|---:|
| CA TTC déclaré | 404 030,87 € | 438 658,43 € | 435 524,92 € |
| CA TTC **reconstitué** | 597 265,42 € | 577 522,00 € | 575 252,68 € |
| Minoration de CA HT retenue | 172 813,45 € | 124 009,56 € | 125 076,16 € |
| Minoration de TVA | 20 421,10 € | 14 854,01 € | 14 651,59 € |
| Base amende art. 1759 (discordance TTC) | 193 234,55 € | 138 863,57 € | 139 727,76 € |

## Logique de la rectification

1. **Rejet de la comptabilité** — l'administration relève des anomalies dans le logiciel de caisse (suppressions de notes, articles à prix 0 €, quantités anormales, fichier événement, modes de règlement, incohérences de TVA) et juge la comptabilité **non probante et non sincère** (consommation vendue > achats, instabilité des prix du « Menu Demi Lune », faiblesse des coefficients de revente).
2. **Reconstitution du chiffre d'affaires** — à partir des **volumes de liquides** (doses, repères O/S/T…), le service reconstitue le nombre d'articles puis le CA, et en déduit une minoration.
3. **Rappels** de TVA collectée et d'IS sur le CA reconstitué, **profit sur le trésor** (cascade, art. L-77 LPF).
4. **Sanctions** — intérêt de retard (art. 1727), **majoration de 40 % pour manquement délibéré** (art. 1729), et **amende de 100 % sur les distributions présumées** (art. 1759, 116/117 CGI) faute de désignation des bénéficiaires.

## Les fiches de synthèse

| # | Fiche | Pages | Objet |
|---|---|---|---|
| 1 | [`01-procedure-presentation.md`](01-procedure-presentation.md) | 1–13 | Débat oral et contradictoire, procédure IS/TVA, garantie fiscale, délai sur place, présentation de l'activité et des annexes |
| 2 | [`02-rejet-comptabilite-1.md`](02-rejet-comptabilite-1.md) | 14–24 | Rejet (1/3) : inventaire de stocks, offerts/gratuits, suppression de note, quantités anormales, articles à 0 €, fichiers Événement (E) et Règlement (F) |
| 3 | [`03-rejet-comptabilite-2.md`](03-rejet-comptabilite-2.md) | 25–31 | Rejet (2/3) : TVA (2ᵉ partie), nombre d'articles, chiffres d'affaires, anomalies de comptabilité matière |
| 4 | [`04-rejet-comptabilite-3.md`](04-rejet-comptabilite-3.md) | 31–37 | Rejet (3/3) : conso > achats, instabilité des prix du Menu Demi Lune, coefficients de revente, conclusion |
| 5 | [`05-methode-reconstitution-1.md`](05-methode-reconstitution-1.md) | 37–44 | Méthode (1/2) : éléments de base, distinction en deux parties, repères de reconstitution |
| 6 | [`06-methode-reconstitution-2.md`](06-methode-reconstitution-2.md) | 44–53 | Méthode (2/2) : offerts/remises/pertes, récapitulation du CA reconstitué par exercice |
| 7 | [`07-rappels-rehaussements-penalites.md`](07-rappels-rehaussements-penalites.md) | 53–66 | **Cœur financier** : rappels TVA et IS, profit sur le trésor, intérêts, majorations 40 % (1729), amende 1759, tableaux récapitulatifs |
| 8 | [`08-annexes-A-H.md`](08-annexes-A-H.md) | Annexes A–H | Cartographie des annexes A à H (tableaux scannés ; renvoi aux `.xls`) |
| 9 | [`09-annexes-boissons-finales.md`](09-annexes-boissons-finales.md) | Annexes Boissons + Finales | Cartographie de la reconstitution des liquides + récapitulatif final |

## Articles et textes invoqués par l'administration

- **CGI** : 38-1, 38-2, 116, 117, 256, 269, 278, 279-0 bis, 1727, 1728, 1729, 1732, 1759.
- **LPF** : L-47-A-II, L-48, L-52, L-55 et s., L-76, L-76 B, L-77, L-189, L-80 A, L-54 B.
- Jurisprudence : CE 14/12/1979 (Banane), CE 28/07/1993 (Mitsukoshi), CE 19/10/1990 n°117 924 (profit sur le trésor), et arrêts sur le manquement délibéré (CE 19/12/1979, 28/10/1981, 22/04/1988, 02/12/1988).

## Points OCR à vérifier sur l'original

- Cascade / droits TVA exercice 1 : **20 041 €** (tableaux récapitulatifs) vs **20 421 €** (TVA nette due) — probable transposition OCR, à confirmer.
- Taux réduit de TVA noté « 279-0-m » → lire **279-0 bis** du CGI.
- Intitulé d'exercices page 57 (« 31 mars 2022 et 31 mars 2023 ») incohérent avec la période vérifiée.
- Les volumes par famille de boissons (pages 30-31 et annexes Boissons) sont largement illisibles à l'OCR → se référer aux `.xls`.
