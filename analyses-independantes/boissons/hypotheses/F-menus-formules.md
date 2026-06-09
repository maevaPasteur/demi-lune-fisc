# Hypothèse F - Boissons incluses dans des menus / formules

**Question du client.** Une partie de l'écart achats−ventes de boissons (58 060 € HT / 3 ans) s'explique-t-elle par des boissons *consommées mais facturées sous le bouton « menu / formule »* (apéritif maison offert, kir, cidre, verre de vin ou café « compris dans le menu ») ? Dans ce cas le liquide sort du stock mais n'apparaît jamais sous un bouton « boisson » → il paraît « disparu ».

Vérification : `/tmp/pwenv/bin/python`. Distinction stricte **EXACT** (lu dans les données) vs **SUPPOSÉ** (à confirmer par pièces).

---

## 1. Recensement des menus / formules vendus - **EXACT**

Les menus **n'apparaissent PAS** dans `ventes-caisse.json` (cet extrait ne contient que les 127 boutons *boissons* par exercice : cafés, vins, bières, apéritifs… aucun item « Menu », « Formule » ou « Plat du jour »). Les boutons menus sont connus uniquement via `src/data/analyseRefacturation.ts` :

| Article (bouton caisse) | Lignes (≈ nb menus vendus) | dont prix forcé | CA cumulé |
|---|---:|---:|---:|
| Menu Demi Lune | 501 | 175 | 14 427 € |
| Menu du jour | 129 | 102 | 6 216 € |
| Formules | 910 | 48 | 1 274 € |
| **TOTAL** | **1 540** | **325** | **21 918 €** |

> Réserve EXACTE : ces totaux sont *cumulés sur la période couverte par l'analyse refacturation* et ne sont **pas ventilés par exercice** dans les données fournies. La répartition par exercice demandée au point 1 est donc **non disponible en l'état**.

## 2. Un menu inclut-il une boisson ? - **NON DÉTERMINABLE en l'état**

Recherche exhaustive (`prix-carte.json`, 3 cartes / 271 items, et `ventes-caisse.json`) des mots `menu | formule | compris | offert | inclus | apéritif maison | franc-comtois | dessert | midi | kir` :

- **Cartes (`prix-carte.json`)** : ce sont **3 cartes des vins & boissons uniquement** (`carte_vins-boissons_*.xls`). Les `description` décrivent des cépages/domaines. **Aucune mention** d'un apéritif/kir/verre/café « compris dans le menu », **aucune composition de menu**. → la carte ne dit rien d'une boisson incluse.
- **Caisse** : aucun libellé ne couple boisson + menu.

**« Menu Franc-Comtois » - point central, EXACT.** Dans `reconstitution-administration.json`, ce menu apparaît, mais **uniquement comme destination d'ingrédient en cuisine**, pas comme boisson servie au client. Le fisc y déduit déjà du Macvin *versé dans le plat et le dessert* :

| Usage déduit par le fisc | nb articles | volume |
|---|---:|---:|
| Menu Franc-Comtois - plat (Poulet/Assiette) | 803 | 1 244 cl |
| Menu Franc-Comtois - dessert (Baba/Crème brûlée) | 803 | 1 729 cl |

→ EXACT : le seul « menu » présent dans la méthode fisc associe du liquide à la **recette de cuisine** (déjà sorti du « disparu »), **PAS à une boisson servie**. Rien dans les données ne prouve qu'un apéritif/kir/verre/café soit servi *en plus* avec ces menus.

**Conclusion point 2 : NON DÉTERMINABLE sans la composition exacte des menus.**
Pièces qu'il faudrait pour trancher :
- la **carte des menus / ardoise du jour** (et non la carte des vins) mentionnant « apéritif maison / kir / verre de vin / café compris » ;
- la **fiche-recette ou descriptif commercial** du « Menu Demi Lune », « Menu du jour », « Formules » indiquant la boisson incluse, sa **nature** et sa **dose** ;
- à défaut, une **attestation de la gérante** sur la pratique (ex. « kir offert avec le menu du soir »).

## 3. Chiffrage du volume/coût - **SUPPOSÉ (scénarios, à confirmer)**

Faute de composition, chiffrage impossible « en dur ». Sensibilité (1 540 menus, 1 boisson servie) :

| Hyp. % menus avec boisson | Dose | Volume sur la période | Coût matière boisson (≈ 0,6-1,5 €/dose) |
|---|---:|---:|---:|
| 50 % | 8-12 cl | ~62 à 92 L | ~460 à 1 155 € |
| 100 % | 8-12 cl | ~123 à 185 L | ~920 à 2 310 € |

Tous **SUPPOSÉS** : aucune ligne de donnée ne fixe ni le taux, ni la dose, ni la nature.

## 4. Conclusion - part de l'écart expliquée

- **Prouvé (EXACT) : 0 €.** Aucune donnée ne démontre qu'une boisson est servie/incluse dans un menu et facturée sous le bouton menu. Le seul lien menu↔liquide documenté (Macvin du « Menu Franc-Comtois ») est un **usage cuisine déjà déduit** par le fisc, donc **déjà sorti** du volume « disparu » - il ne peut pas re-expliquer l'écart.
- **À confirmer (SUPPOSÉ) : faible.** Même au scénario maximal (100 % des 1 540 menus, 12 cl), on couvre **~185 L et ~2 300 € de coût matière** sur 3 ans - soit **moins de 4 %** de l'écart de 58 060 € HT. Ordre de grandeur **marginal** : cette piste ne peut être qu'un appoint, jamais l'explication principale.

→ **Hypothèse F : NON DÉTERMINABLE en l'état, et plafonnée à un effet marginal (< ~4 %)** même en hypothèse haute. À documenter par la carte des menus si l'on veut la défendre, mais à ne pas mettre en avant comme pilier.
