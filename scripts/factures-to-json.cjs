// Extraction des factures fournisseur (Franche-Comté Boissons / logiciel SERIG)
// vers un JSON unique. 100 % local (pdftotext), aucun appel modèle.
//
// Stratégie : pdftotext -layout, puis découpage des lignes-articles par
// positions de colonnes lues sur la ligne d'en-tête du tableau (robuste aux
// cellules vides). Auto-contrôle : somme des lignes vs total HT imprimé.
const fs = require('fs')
const path = require('path')
const { execSync } = require('child_process')

const ROOT = path.join(__dirname, '..', 'public', 'documents', 'vins-boissons', 'fournisseur')
const OUT = path.join(__dirname, '..', 'src', 'data', 'factures-fournisseur.json')

// --- Utils -------------------------------------------------------------------
// "1.679,15" -> 1679.15 ; "60,00-" -> -60 ; "" -> null
function num(s) {
  if (s == null) return null
  let t = String(s).trim()
  if (!t) return null
  const neg = t.endsWith('-')
  t = t.replace(/-/g, '').replace(/\./g, '').replace(',', '.').replace(/\s/g, '')
  if (!/^\d+(\.\d+)?$/.test(t)) return null
  const v = parseFloat(t)
  return neg ? -v : v
}

function clean(s) {
  return (s || '').replace(/\s+/g, ' ').trim()
}

// --- Parse d'une facture -----------------------------------------------------
function parseFacture(text, fichier, annee) {
  const lines = text.split('\n')

  const fac = {
    fichier,
    annee,
    numero: null,
    dateFacture: null,
    dateCommande: null,
    dateLivraison: null,
    nClient: null,
    nCommande: null,
    nBonLivraison: null,
    lignes: [],
    totaux: {
      totalHT: null,
      totalTVA: null,
      totalTTC: null,
      totalFacture: null,
      ancienSolde: null,
      tvaDetail: [],
    },
  }

  // N° pièce + date : « FACTURE N° » ou « AVOIR N° » (notes d'avoir).
  // Repli sur le nom de fichier (Facture_n°_XXXXXX.PDF) si l'en-tête échoue.
  const mNum = text.match(/(?:FACTURE|AVOIR)\s*N°\s+(\d+)\s+FOLIO/)
  if (mNum) fac.numero = mNum[1]
  if (!fac.numero) {
    const mFile = fichier.match(/(\d{5,})/)
    if (mFile) fac.numero = mFile[1]
  }
  // Type de pièce (facture vs avoir) déduit de l'en-tête.
  fac.type = /AVOIR\s*N°/.test(text) ? 'avoir' : 'facture'
  if (fac.numero) {
    const mDate = text.match(new RegExp(fac.numero + '\\s+(\\d{2}/\\d{2}/\\d{4})'))
    if (mDate) fac.dateFacture = mDate[1]
  }
  // Ligne d'identités : N° CLIENT  N° COMMANDE  DATE COMMANDE  [N° BON LIVR.]  DATE LIVR.
  const mId = text.match(/\b(\d{5})\s+(\d{6})\s+(\d{2}\/\d{2}\/\d{4})\s+(?:(\d{4,6})\s+)?(\d{2}\/\d{2}\/\d{4})/)
  if (mId) {
    fac.nClient = mId[1]
    fac.nCommande = mId[2]
    fac.dateCommande = mId[3]
    fac.nBonLivraison = mId[4] || null
    fac.dateLivraison = mId[5]
  }

  // --- Lignes-articles : découpage par colonnes ------------------------------
  let cols = null
  let current = null
  let inTable = false

  const findHeader = (l) =>
    l.includes('CODE') && l.includes('DESIGNATION') && l.includes('CONDITIONNEMENT')

  for (const raw of lines) {
    const l = raw.replace(/\t/g, ' ')

    if (findHeader(l)) {
      const idxHT = l.indexOf('H.T.')
      cols = {
        code: l.indexOf('CODE'),
        des: l.indexOf('DESIGNATION'),
        cond: l.indexOf('CONDITIONNEMENT'),
        colis: l.indexOf('COLIS'),
        colsq: l.indexOf('COLS'),
        pxbt: l.indexOf('PX.U.BT'),
        rem: l.indexOf('REM.U'),
        pxnet: l.indexOf('PX.U.NET'),
        mnt: l.indexOf('MNT.'),
        v: idxHT >= 0 ? l.indexOf('V', idxHT + 4) : -1,
      }
      inTable = true
      current = null
      continue
    }

    if (!inTable || !cols) continue

    // Fin du tableau sur la page
    if (/TOTAL T\.T\.C\.|Poids Brut/.test(l)) {
      inTable = false
      current = null
      continue
    }
    if (!l.trim()) continue

    // Le code (6 chiffres) commence en début de ligne, avant le label "CODE".
    const mCode = l.match(/^\s*(\d{6})\s*(\*?)\s*/)

    if (mCode) {
      const codeEnd = mCode[0].length
      // Zone "MNT. H.T." + code TVA : on isole le montant (avec signe éventuel)
      // et le code TVA, robuste au léger décalage de colonne et aux avoirs.
      const region = l.slice(cols.mnt, cols.v >= 0 ? cols.v + 4 : undefined)
      const mm = region.match(/(\d{1,3}(?:[.,]\d+)+)\s*(-?)\s*([12])?/)
      let montantHT = null
      let tva = null
      if (mm) {
        montantHT = num(mm[1] + (mm[2] || ''))
        tva = mm[3] || null
      }
      if (!tva && cols.v >= 0) tva = (l.slice(cols.v - 1, cols.v + 5).match(/[12]/) || [null])[0]
      // Désignation vs conditionnement : la zone texte (après le code, avant COLIS)
      // contient les deux, séparés par un grand espacement (séparateur de colonnes).
      const txtRegion = l.slice(codeEnd, cols.colis)
      const parts = txtRegion.split(/\s{2,}/).map((s) => s.trim()).filter(Boolean)
      const designation = parts[0] || ''
      const conditionnement = clean(parts.slice(1).join(' '))
      const ligne = {
        code: mCode[1],
        accise: mCode[2] === '*',
        designation,
        conditionnement,
        colis: num(l.slice(cols.colis, cols.colsq)),
        quantite: num(l.slice(cols.colsq, cols.pxbt)),
        puBrut: num(l.slice(cols.pxbt, cols.rem)),
        remise: num(l.slice(cols.rem, cols.pxnet)),
        puNet: num(l.slice(cols.pxnet, cols.mnt)),
        montantHT,
        tva,
      }
      fac.lignes.push(ligne)
      current = ligne
    } else {
      // Continuation = 2e ligne de désignation PURE (aucun chiffre dans la zone
      // numérique → exclut les lignes de consigne/récup qui ont des montants).
      const txt = clean(l)
      const zoneNum = l.slice(cols.colis)
      if (current && txt && !/\d/.test(zoneNum) && !/\d{2}\/\d{2}\/\d{4}/.test(txt) && txt.length < 70) {
        current.designation = (current.designation + ' ' + txt).trim()
      }
    }
  }

  // --- Totaux (dernière occurrence renseignée) -------------------------------
  const lastVal = (re) => {
    let m, v = null
    const g = new RegExp(re, 'g')
    while ((m = g.exec(text))) if (m[1] && m[1].trim()) v = num(m[1])
    return v
  }
  fac.totaux.totalTTC = lastVal('TOTAL T\\.T\\.C\\.\\s+([\\d.,]+-?)')
  fac.totaux.totalFacture = lastVal('TOTAL FACTURE\\s+\\(13\\)\\s+([\\d.,]+-?)')
  fac.totaux.ancienSolde = lastVal('ANCIEN SOLDE\\s+([\\d.,]+-?)')

  // Ligne " TOTAUX <HT> <TVA> [taux] MONTANT REGLE …" (bloc C TAUX / MONTANT H.T. / MONTANT TVA)
  for (const l of lines) {
    const m = l.match(/^\s*TOTAUX\s+([\d.,]+-?)\s+([\d.,]+-?)(?:\s+([\d.,]+-?))?\s+MONTANT REGLE/)
    if (m && num(m[1]) != null && num(m[2]) != null) {
      fac.totaux.totalHT = num(m[1])
      fac.totaux.totalTVA = num(m[2])
    }
  }
  // Détail TVA par taux : "<code> <taux>  <HT>  <TVA>  (DECONSIGNE|Net|Préc...)"
  for (const l of lines) {
    const m = l.match(/^\s*([12])\s+(\d+,\d+)\s+([\d.,]+-?)\s+([\d.,]+-?)\s+(?:DECONSIGNE|Net|Préc)/)
    if (m) {
      fac.totaux.tvaDetail.push({ tva: m[1], taux: num(m[2]), ht: num(m[3]), tva_montant: num(m[4]) })
    }
  }

  return fac
}

// --- Parcours ----------------------------------------------------------------
const factures = []
const warnings = []
const annees = fs.readdirSync(ROOT).filter((d) => /^\d{4}$/.test(d)).sort()

for (const annee of annees) {
  const dir = path.join(ROOT, annee)
  const files = fs
    .readdirSync(dir)
    .filter((f) => /\.pdf$/i.test(f) && !/extrait de compte/i.test(f))
    .sort()
  for (const f of files) {
    const full = path.join(dir, f)
    let text
    try {
      text = execSync(`pdftotext -layout "${full}" -`, { maxBuffer: 64 * 1024 * 1024 }).toString('utf8')
    } catch (e) {
      warnings.push(`LECTURE ECHEC: ${annee}/${f}`)
      continue
    }
    const fac = parseFacture(text, `${annee}/${f}`, Number(annee))

    // Auto-contrôle : somme lignes vs total HT imprimé
    const sumHT = fac.lignes.reduce((s, l) => s + (l.montantHT || 0), 0)
    const tHT = fac.totaux.totalHT
    const diff = tHT != null ? Math.round((sumHT - tHT) * 100) / 100 : null
    fac._controle = { sumLignesHT: Math.round(sumHT * 100) / 100, totalHT: tHT, ecart: diff }
    if (!fac.numero) warnings.push(`SANS N°: ${annee}/${f}`)
    if (!fac.lignes.length) warnings.push(`0 LIGNE: ${annee}/${f}`)
    if (diff != null && Math.abs(diff) > 0.05) warnings.push(`ECART HT ${diff} : ${annee}/${f} (${fac.lignes.length} lignes, total ${tHT})`)

    factures.push(fac)
  }
}

// Champ de contrôle retiré du JSON final (servait au rapport).
for (const f of factures) delete f._controle

const out = {
  fournisseur: 'Franche-Comté Boissons Services (Besançon)',
  source: 'public/documents/vins-boissons/fournisseur',
  nbFactures: factures.length,
  factures,
}
fs.writeFileSync(OUT, JSON.stringify(out, null, 2), 'utf8')

// --- Rapport compact ---------------------------------------------------------
const nLignes = factures.reduce((s, f) => s + f.lignes.length, 0)
const sansTotal = factures.filter((f) => f.totaux.totalHT == null).length
console.log(`Factures: ${factures.length} | Lignes: ${nLignes} | sans total HT: ${sansTotal}`)
console.log(`JSON: ${path.relative(process.cwd(), OUT)} (${(fs.statSync(OUT).size / 1024).toFixed(0)} Ko)`)
console.log(`\nAvertissements (${warnings.length}) :`)
warnings.slice(0, 40).forEach((w) => console.log('  - ' + w))
if (warnings.length > 40) console.log(`  … (+${warnings.length - 40})`)
