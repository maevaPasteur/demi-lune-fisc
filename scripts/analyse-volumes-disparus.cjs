// Analyse des « volumes disparus » du vérificateur, croisée avec les achats réels
// (factures FCBS extraites). 100 % local, aucun appel modèle.
const fs = require('fs')
const path = require('path')

const fisc = require('../src/data/volumes-disparus-fisc.json')
const achats = require('../src/data/achats-par-produit.json')

// --- Helper : achats réels (toutes années) pour un motif de libellé ----------
function achatsReels(regex) {
  const ps = achats.produits.filter((p) => regex.test(p.libelle.toUpperCase()))
  const total = ps.reduce((a, p) => a + (p.total.quantite || 0), 0)
  const parAnnee = {}
  for (const p of ps)
    for (const [an, v] of Object.entries(p.parAnnee))
      parAnnee[an] = (parAnnee[an] || 0) + (v.quantite || 0)
  return { total, parAnnee, libelles: ps.map((p) => p.libelle) }
}

const num = (v) => (typeof v === 'number' ? v : null)
const out = (s) => console.log(s)

// =============================================================================
out('═══════════════════════════════════════════════════════════════')
out('  ANALYSE — VOLUMES DISPARUS (vérificateur) × ACHATS RÉELS (FCBS)')
out('═══════════════════════════════════════════════════════════════\n')

// --- 1. Décompte global ------------------------------------------------------
const P = fisc.produits
const param = P.filter((p) => p.preuve_parametrage)
const cent = [] // produits à 100 % (zéro vente) sur ≥1 exercice
const surco = [] // surconsommation (pct < 0 ou vente sans achat)
for (const p of P) {
  for (const [an, d] of Object.entries(p.donnees)) {
    if (d.pct_disparu === 100) cent.push({ nom: p.nom, an, dispo: d.disponible })
    if ((num(d.pct_disparu) != null && d.pct_disparu < 0) || d.type === 'surconsommation' || d.anomalie === 'vente sans achat')
      surco.push({ nom: p.nom, an, d })
  }
}
out(`Produits couverts : ${P.length}`)
out(`Produits « preuve_parametrage » (reconnus douteux) : ${param.length}`)
out(`Occurrences à 100 % (ZÉRO vente caisse) : ${cent.length}`)
out(`Occurrences surconsommation / vente sans achat : ${surco.length}\n`)

// --- 2. Les 100 % : achetés mais JAMAIS vendus => impossible -----------------
out('── 2. PRODUITS À 100 % « DISPARUS » = 0 VENTE EN CAISSE ──')
out('   (achetés et au menu, mais aucune vente enregistrée → artefact caisse, pas occultation)\n')
const MAP_100 = {
  '1664 33 cl': /1664/,
  'Heineken 33 cl': /HEINEKEN/,
  'Grimbergen Blanche 33 cl': /GRIMBERGEN/,
  'Hefeweizen 33 cl': /HEFEWEIZEN|SZIGET|WEIZEN/,
  'White Rabbit 33 cl': /RABBIT/,
  'White Mort Subite 33 cl': /MORT SUBITE/,
  'Bleue du Mont Blanc 33 cl': /MONT BLANC/,
  'Carola Bleue 50 cl': /CAROLA/,
  'Cidre Sassy 33 cl': /SASSY/,
}
for (const [nom, re] of Object.entries(MAP_100)) {
  const p = P.find((x) => x.nom === nom)
  const d2223 = p?.donnees['2022-2023']
  const r = achatsReels(re)
  out(`  • ${nom.padEnd(28)} fisc: dispo ${String(d2223?.disponible ?? '?').padStart(4)} / vendu 0  →  achats réels FCBS : ${r.total} bt`)
  if (r.total > 0)
    out(`      ⇒ produit BEL ET BIEN ACHETÉ (${r.libelles[0]}) : « 0 vente » sur un an est matériellement impossible.`)
}

// --- 3. Ventes SANS achat (les deux preuves internes) -----------------------
out('\n── 3. VENTES SANS ACHAT (preuves internes citées par le vérificateur) ──\n')
const bordeaux = achatsReels(/MOUTON CADET/)
const hcnuits = achatsReels(/CTES DE NUITS|COTES DE NUITS|HTES CTES|NUITS/)
out(`  • Bordeaux Mouton Cadet — fisc 2024-2025 : 6 bt vendues, 0 dispo (vente sans achat)`)
out(`      Achats réels FCBS (toutes années) : ${bordeaux.total} bt ${JSON.stringify(bordeaux.parAnnee)}`)
out(`      Libellés trouvés : ${bordeaux.libelles.join(' | ') || '(aucun)'}`)
out(`  • Hautes Côtes de Nuits — fisc 2023-2024 : 172 bt (12 950 cl) vendues, 0 dispo`)
out(`      Achats réels FCBS (toutes années) : ${hcnuits.total} bt ${JSON.stringify(hcnuits.parAnnee)}`)
out(`      Libellés trouvés : ${hcnuits.libelles.join(' | ') || '(aucun)'}`)
out(`      ⇒ Vendre 172 bt sans achat correspondant = confusion de code caisse (cf. « Verre H côte »/« Pichet C.DE BEAUNE »).`)

// --- 4. Eaux : "disparues" alors qu'aucun usage cuisine ---------------------
out('\n── 4. EAUX MINÉRALES « DISPARUES » (aucun usage cuisine possible) ──\n')
for (const p of P.filter((x) => x.categorie === 'eau')) {
  const d = p.donnees['2022-2023']
  if (num(d?.pct_disparu) != null)
    out(`  • ${p.nom.padEnd(24)} dispo ${String(d.disponible).padStart(4)} / vendu ${String(d.vendu_caisse).padStart(4)} → ${d.pct_disparu}% « disparu »`)
}
out('   ⇒ Une eau minérale ne « disparaît » pas (ni cuisine, ni casse massive) : ces taux trahissent une sous-saisie caisse systémique (carafes/offerts/menus).')

// --- 5. Surconsommation (arithmétiquement impossible) -----------------------
out('\n── 5. SURCONSOMMATION — vendu > acheté (impossible sans erreur caisse) ──\n')
for (const s of surco) {
  const v = s.d.pct_disparu ?? s.d.pct_des_disponibles
  out(`  • ${s.nom.padEnd(24)} ${s.an} : ${v != null ? v + ' %' : (s.d.anomalie || s.d.type)}`)
}

// --- 6. Verdicts du vérificateur --------------------------------------------
out('\n── 6. VERDICTS (méta du fisc) ──\n')
for (const [k, v] of Object.entries(fisc.meta.verdict_hypotheses)) out(`  • ${k} : ${v}`)

// --- 7. Aveu jus de fruit ----------------------------------------------------
const jus = P.find((p) => p.nom.startsWith('Jus de fruit'))?.donnees['2022-2023']
if (jus)
  out(`\n── 7. AVEU JUS DE FRUIT (2022-2023) ──\n  dispo ${jus.disponible_cl} cl · vendu ${jus.vendu_cl} cl · reconstitué ${jus.reconstitue_cl} cl · valorisé CA : ${jus.valorise_ca}\n  ⇒ Le service n'a même pas utilisé tout le volume disponible : preuve, de son propre aveu, que la méthode peut être minorée.`)

// --- 8. Export d'un résumé exploitable --------------------------------------
const resume = {
  genereDepuis: ['volumes-disparus-fisc.json', 'achats-par-produit.json'],
  compte: { produits: P.length, preuveParametrage: param.length, occurrences100pct: cent.length, surconsommation: surco.length },
  produits100pctAchetes: Object.entries(MAP_100).map(([nom, re]) => ({
    nom,
    fiscDispo2223: P.find((x) => x.nom === nom)?.donnees['2022-2023']?.disponible ?? null,
    achatsReelsTotal: achatsReels(re).total,
  })),
  ventesSansAchat: {
    bordeauxMoutonCadet: { fisc: '6 bt vendues 2024-2025, 0 dispo', achatsReels: bordeaux.parAnnee },
    hautesCotesDeNuits: { fisc: '172 bt vendues 2023-2024, 0 dispo', achatsReels: hcnuits.parAnnee },
  },
}
const OUT = path.join(__dirname, '..', 'src', 'data', 'analyse-disparus.json')
fs.writeFileSync(OUT, JSON.stringify(resume, null, 2), 'utf8')
out(`\n→ Résumé exporté : ${path.relative(process.cwd(), OUT)}`)
