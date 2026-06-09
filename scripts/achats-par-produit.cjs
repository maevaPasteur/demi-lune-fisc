// Agrège factures-fournisseur.json au niveau PRODUIT (code) × EXERCICE.
// Produit = unité de comparaison future (achats vs ventes caisse vs inventaire).
// 100 % local, aucun appel modèle.
const fs = require('fs')
const path = require('path')

const SRC = path.join(__dirname, '..', 'src', 'data', 'factures-fournisseur.json')
const OUT = path.join(__dirname, '..', 'src', 'data', 'achats-par-produit.json')

const data = JSON.parse(fs.readFileSync(SRC, 'utf8'))
const r2 = (n) => Math.round(n * 100) / 100
const r3 = (n) => Math.round(n * 1000) / 1000

// --- Contenance (cl) déduite du libellé : "75 CL", "1 L", "8 L"… --------------
function contenanceCl(lib) {
  const m = lib.match(/(\d+(?:[.,]\d+)?)\s*(CL|L)(?![A-Za-zÀ-ÿ])/i)
  if (m) {
    const v = parseFloat(m[1].replace(',', '.'))
    return /^l$/i.test(m[2]) ? v * 100 : v
  }
  if (/\bLITRE\b/i.test(lib)) return 100
  return null
}

// --- Catégorie déduite du libellé (heuristique, ordre = priorité) -------------
const REGLES = [
  // Non-boissons isolées en premier (ne contiennent pas de mots de boisson).
  ['materiel', /\b(BAC|PAILLE|PAILLES|CARTOUCHE|RECYCLAGE|VERRE PERDU|GOBELET|SET|DIVERS|NETTOYANT|GAZ|CO2|FILM|SACHET PLAST|EMBALLAGE|TIRAGE|PRETE|PRÊTE)\b/],
  ['alimentaire', /\b(CRACKERS|BRETZEL|MADELEINE|MADELEINES|GALET|GALETTE|GALETTES|BISCUIT|ST MICHEL|SAINT MICHEL|CHIPS|CACAHUETE|CACAHUÈTE|OLIVE|OLIVES|GRAINE|CHOCOLAT|BONBON|SNACK|TUC|GRESSIN)\b/],
  ['eau', /\b(PERRIER|VITTEL|SAN PELLEGRINO|BADOIT|EVIAN|CRISTALLINE|EAU)\b/],
  ['biere', /\b(BIERE|BIÈRE|FUT|AFFLIGEM|BLADE|HEINEKEN|PICON|PANACHE|PANACHÉ|ROUGET|DESPERADOS|KRONENBOURG|1664|LEFFE|GRIMBERGEN|MORT SUBITE|MONT BLANC|DELIRIUM|CHOUFFE|KWAK|BARBAR|ORVAL|DUVEL|PELFORTH|PIETRA|WITTE)\b/],
  ['macvin', /\bMACVIN\b/],
  ['cremant_petillant', /\b(CREMANT|CRÉMANT|CIDRE|MOUSSEUX|CHAMPAGNE|PROSECCO|POIRE BOLEE|BOLEE)\b/],
  ['spiritueux_digestif', /\b(WHISKY|WHISKEY|VODKA|RHUM|RICARD|PASTIS|PONTARLIER|GET|COGNAC|ARMAGNAC|MARC|GENEPI|GÉNÉPI|BAILEY|MARNIER|LIQUEUR|CALVADOS|PORTO|MARTINI|SUZE|GIN|TEQUILA|PASSOA|PASSOÄ|SOHO|CURACAO|CURAÇAO|APEROL|ABSINTHE|CREME|CRÈME|EAU DE VIE|EAU-DE-VIE|WILLIAMS|MIRABELLE|KIRSCH|PRUNE|SAPIN|FERNET|CHARTREUSE|COINTREAU|MALIBU|JAGER)\b/],
  ['vin', /\b(VIN|ARBOIS|SAVAGNIN|CHARDONNAY|TROUSSEAU|POULSARD|PLOUSSARD|CÔTES?|COTES?|CTES|BOURGOGNE|BEAUJOLAIS|BORDEAUX|GEWURZ|RIESLING|PINOT|PROVENCE|CHABLIS|MACON|MÂCON|JOSEPH|MIRAVAL|MINUTY|MOULIN A VENT|MORGON|BROUILLY|FLEURIE|SANCERRE|GASCOGNE|LANGUEDOC|ALIGOTE|ALIGOTÉ|VERAN|NUITS|RAVELIN|JAMELLES|NEGLY|CLAPE|SORCIERES|SYLVANER|MUSCADET|VENTOUX|LUBERON|CORBIERES|RIOJA|CHIANTI|ROSE|ROSÉ|BIB)\b/],
  ['cafe_the', /\b(CAFE|CAFÉ|MALONGO|THE|THÉ|INFUSION|CAPSULE|EXPRESSO|CHICOREE)\b/],
  ['sirop', /\b(SIROP|MONIN|GRENADINE|ORGEAT|TEISSEIRE)\b/],
  ['jus', /\b(JUS|GRANINI|NECTAR|\bNEC\b|PRESSADE|PAGO|ALAIN MILLIAT)\b/],
  ['soft', /\b(COCA|SCHWEPPES|ORANGINA|FANTA|FUZETEA|FUZE|LIMONADE|MORTUACIENNE|SODA|TONIC|OASIS|ICE TEA|RED BULL|PEPSI|SPRITE|SEVEN UP|7UP|VOLVIC|TROPICO|PULCO)\b/],
]
// Marques/mots additionnels pris en compte ci-dessus :
//  - spiritueux : CLAN CAMPBELL, JACK DANIEL, MASSENEZ  (+ repli par degré ≥ 16°)
//  - bière      : HEFEWEIZEN, WEIZEN, SZIGET, IPA, PILS
//  - vin        : BOHEME, GRIS, CAMARGUE
//  - alimentaire: SUCRE, FINANCIER, CARAMBAR, MILKA, BISCOFF, LOTUS, NAPOLITAIN, GATEAU
REGLES.find((r) => r[0] === 'spiritueux_digestif')[1] =
  /\b(WHISKY|WHISKEY|VODKA|RHUM|RICARD|PASTIS|PONTARLIER|GET|COGNAC|ARMAGNAC|MARC|GENEPI|GÉNÉPI|BAILEY|MARNIER|LIQUEUR|CALVADOS|PORTO|MARTINI|SUZE|GIN|TEQUILA|PASSOA|PASSOÄ|SOHO|CURACAO|CURAÇAO|APEROL|ABSINTHE|CREME|CRÈME|EAU DE VIE|EAU-DE-VIE|WILLIAMS|MIRABELLE|KIRSCH|PRUNE|SAPIN|FERNET|CHARTREUSE|COINTREAU|MALIBU|JAGER|CLAN CAMPBELL|CAMPBELL|JACK DANIEL|MASSENEZ)\b/
REGLES.find((r) => r[0] === 'biere')[1] =
  /\b(BIERE|BIÈRE|FUT|AFFLIGEM|BLADE|HEINEKEN|PICON|PANACHE|PANACHÉ|ROUGET|DESPERADOS|KRONENBOURG|1664|LEFFE|GRIMBERGEN|MORT SUBITE|MONT BLANC|DELIRIUM|CHOUFFE|KWAK|BARBAR|ORVAL|DUVEL|PELFORTH|PIETRA|WITTE|HEFEWEIZEN|WEIZEN|SZIGET|IPA|PILS)\b/
REGLES.find((r) => r[0] === 'vin')[1] =
  /\b(VIN|ARBOIS|SAVAGNIN|CHARDONNAY|TROUSSEAU|POULSARD|PLOUSSARD|CÔTES?|COTES?|CTES|BOURGOGNE|BEAUJOLAIS|BORDEAUX|GEWURZ|RIESLING|PINOT|PROVENCE|CHABLIS|MACON|MÂCON|JOSEPH|MIRAVAL|MINUTY|MOULIN A VENT|MORGON|BROUILLY|FLEURIE|SANCERRE|GASCOGNE|LANGUEDOC|ALIGOTE|ALIGOTÉ|VERAN|NUITS|RAVELIN|JAMELLES|NEGLY|CLAPE|SORCIERES|SYLVANER|MUSCADET|VENTOUX|LUBERON|CORBIERES|RIOJA|CHIANTI|ROSE|ROSÉ|BIB|BOHEME|GRIS|CAMARGUE)\b/
REGLES.find((r) => r[0] === 'alimentaire')[1] =
  /\b(CRACKERS|BRETZEL|MADELEINE|MADELEINES|GALET|GALETTE|GALETTES|BISCUIT|ST MICHEL|SAINT MICHEL|CHIPS|CACAHUETE|CACAHUÈTE|OLIVE|OLIVES|GRAINE|CHOCOLAT|BONBON|SNACK|TUC|GRESSIN|SUCRE|FINANCIER|CARAMBAR|MILKA|BISCOFF|LOTUS|NAPOLITAIN|GATEAU|GÂTEAU|SPECULOOS)\b/

function categorie(lib) {
  const L = lib.toUpperCase()
  for (const [cat, re] of REGLES) if (re.test(L)) return cat
  // Repli : degré d'alcool élevé => spiritueux/digestif (vins ~11-14°, bières <10°).
  const deg = L.match(/(\d{1,2})(?:[.,]\d)?\s*°/)
  if (deg && parseInt(deg[1], 10) >= 16) return 'spiritueux_digestif'
  return 'autre'
}

// --- Agrégation --------------------------------------------------------------
const annees = [...new Set(data.factures.map((f) => f.annee))].sort()
const blankAnnee = () =>
  Object.fromEntries(annees.map((a) => [a, { quantite: 0, volumeL: 0, montantHT: 0, nbLignes: 0 }]))

const produits = new Map() // code -> agrégat
const libCount = new Map() // code -> Map(designation -> n)

for (const f of data.factures) {
  for (const l of f.lignes) {
    if (!l.code) continue
    const q = l.quantite || 0
    const ht = l.montantHT || 0
    if (!produits.has(l.code)) {
      produits.set(l.code, { code: l.code, accise: !!l.accise, parAnnee: blankAnnee() })
      libCount.set(l.code, new Map())
    }
    const p = produits.get(l.code)
    if (l.accise) p.accise = true
    const a = p.parAnnee[f.annee]
    a.quantite += q
    a.montantHT += ht
    a.nbLignes += 1
    // libellé le plus fréquent pour ce code
    const lc = libCount.get(l.code)
    if (l.designation) lc.set(l.designation, (lc.get(l.designation) || 0) + 1)
  }
}

// Choix du libellé représentatif + contenance + volume + totaux
const liste = []
for (const [code, p] of produits) {
  const lc = libCount.get(code)
  const libelle = [...lc.entries()].sort((a, b) => b[1] - a[1])[0]?.[0] || ''
  const cl = contenanceCl(libelle)
  const cat = categorie(libelle)

  const total = { quantite: 0, volumeL: 0, montantHT: 0, nbLignes: 0 }
  for (const an of annees) {
    const a = p.parAnnee[an]
    a.volumeL = cl != null ? r3((cl * a.quantite) / 100) : null
    a.puMoyen = a.quantite ? r3(a.montantHT / a.quantite) : null
    a.montantHT = r2(a.montantHT)
    a.quantite = r3(a.quantite)
    total.quantite += a.quantite
    total.montantHT += a.montantHT
    total.nbLignes += a.nbLignes
    if (a.volumeL != null) total.volumeL += a.volumeL
  }
  total.volumeL = cl != null ? r3(total.volumeL) : null
  total.montantHT = r2(total.montantHT)
  total.quantite = r3(total.quantite)
  total.puMoyen = total.quantite ? r3(total.montantHT / total.quantite) : null

  liste.push({ code, libelle, categorie: cat, contenanceCl: cl, accise: p.accise, parAnnee: p.parAnnee, total })
}
liste.sort((a, b) => b.total.montantHT - a.total.montantHT)

// --- Synthèse par catégorie × exercice ---------------------------------------
const parCategorie = {}
for (const p of liste) {
  if (!parCategorie[p.categorie]) {
    parCategorie[p.categorie] = {
      nbProduits: 0,
      parAnnee: Object.fromEntries(annees.map((a) => [a, { quantite: 0, volumeL: 0, montantHT: 0 }])),
      total: { quantite: 0, volumeL: 0, montantHT: 0 },
    }
  }
  const c = parCategorie[p.categorie]
  c.nbProduits += 1
  for (const an of annees) {
    const a = p.parAnnee[an]
    c.parAnnee[an].quantite = r3(c.parAnnee[an].quantite + a.quantite)
    c.parAnnee[an].montantHT = r2(c.parAnnee[an].montantHT + a.montantHT)
    if (a.volumeL != null) c.parAnnee[an].volumeL = r3(c.parAnnee[an].volumeL + a.volumeL)
    c.total.quantite = r3(c.total.quantite + a.quantite)
    c.total.montantHT = r2(c.total.montantHT + a.montantHT)
    if (a.volumeL != null) c.total.volumeL = r3(c.total.volumeL + a.volumeL)
  }
}

const out = {
  source: 'src/data/factures-fournisseur.json',
  fournisseur: data.fournisseur,
  annees,
  nbProduits: liste.length,
  parCategorie,
  produits: liste,
}
fs.writeFileSync(OUT, JSON.stringify(out, null, 2), 'utf8')

// --- Rapport -----------------------------------------------------------------
console.log(`Produits distincts : ${liste.length}`)
console.log(`JSON : ${path.relative(process.cwd(), OUT)} (${(fs.statSync(OUT).size / 1024).toFixed(0)} Ko)`)
console.log('\nSynthèse par catégorie (montant HT total) :')
Object.entries(parCategorie)
  .sort((a, b) => b[1].total.montantHT - a[1].total.montantHT)
  .forEach(([cat, c]) =>
    console.log(`  ${cat.padEnd(20)} ${String(c.nbProduits).padStart(3)} prod · ${c.total.montantHT.toFixed(2).padStart(10)} € HT · ${(c.total.volumeL || 0).toFixed(0).padStart(6)} L`),
  )
const sansContenance = liste.filter((p) => p.contenanceCl == null).length
const autre = parCategorie['autre']?.nbProduits || 0
console.log(`\nÀ surveiller : ${sansContenance} produits sans contenance, ${autre} en catégorie « autre ».`)
