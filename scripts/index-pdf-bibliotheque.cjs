// Indexe les PDF "carte des vins" et "factures fournisseur par année" présents
// dans public/documents/vins-boissons → src/data/pdf-bibliotheque.json
// 100 % local, relançable quand on ajoute des PDF.
const fs = require('fs')
const path = require('path')

const BASE = path.join(__dirname, '..', 'public', 'documents')
const VB = path.join(BASE, 'vins-boissons')
const OUT = path.join(__dirname, '..', 'src', 'data', 'pdf-bibliotheque.json')

const isPdf = (f) => /\.pdf$/i.test(f)

// --- Cartes des vins (PDF à la racine de vins-boissons) ----------------------
function titreCarte(f) {
  const actuelle = /actuelle|aujourdhui/i.test(f)
  // Format de date dans le nom : AAAA-MM-JJ (préféré) ou JJ:MM:AA (ancien).
  let date = null
  const iso = f.match(/(\d{4})-(\d{2})-(\d{2})/)
  const old = f.match(/(\d{2}):(\d{2}):(\d{2})/)
  if (iso) date = `${iso[3]}/${iso[2]}/${iso[1]}`
  else if (old) date = `${old[1]}/${old[2]}/20${old[3]}`
  if (date) return actuelle ? `Carte en vigueur (${date})` : `Carte du ${date}`
  return f.replace(/\.pdf$/i, '')
}

const cartes = fs
  .readdirSync(VB)
  .filter((f) => isPdf(f))
  .sort()
  .map((f) => ({
    titre: titreCarte(f),
    description: 'Carte des vins & boissons (menu).',
    fichier: `vins-boissons/${f}`,
    format: 'PDF',
  }))

// --- Factures fournisseur par année -----------------------------------------
const FOURN = path.join(VB, 'fournisseur')
const annees = fs
  .readdirSync(FOURN)
  .filter((d) => /^\d{4}$/.test(d) && fs.statSync(path.join(FOURN, d)).isDirectory())
  .sort()

function labelPiece(f) {
  const mFac = f.match(/Facture_n°_(\d+)/i)
  if (mFac) return { label: `Facture n° ${mFac[1]}`, type: 'facture', tri: Number(mFac[1]) }
  if (/extrait de compte/i.test(f)) return { label: 'Extrait de compte', type: 'releve', tri: 0 }
  return { label: f.replace(/\.pdf$/i, ''), type: 'autre', tri: 0 }
}

const facturesParAnnee = annees.map((annee) => {
  const dir = path.join(FOURN, annee)
  const pieces = fs
    .readdirSync(dir)
    .filter((f) => isPdf(f))
    .map((f) => {
      const { label, type, tri } = labelPiece(f)
      return { label, type, fichier: `vins-boissons/fournisseur/${annee}/${f}`, tri }
    })
    .sort((a, b) => a.tri - b.tri)
    .map(({ label, type, fichier }) => ({ label, type, fichier }))
  return { annee, nb: pieces.length, pieces }
})

// --- Inventaires (PDF scanné + CSV d'extraction boissons par année) ----------
const INV = path.join(BASE, 'inventaires')
let inventaires = []
if (fs.existsSync(INV)) {
  const files = fs.readdirSync(INV)
  const anneesInv = [
    ...new Set(files.map((f) => (f.match(/(\d{4})/) || [])[1]).filter(Boolean)),
  ].sort()
  inventaires = anneesInv.map((annee) => {
    const pdf = files.find((f) => /\.pdf$/i.test(f) && f.includes(annee))
    const csv = files.find((f) => /\.csv$/i.test(f) && f.includes(annee))
    return {
      annee,
      pdf: pdf ? `inventaires/${pdf}` : null,
      csv: csv ? `inventaires/${csv}` : null,
    }
  })
}

const out = {
  source: 'public/documents/vins-boissons',
  cartes,
  facturesParAnnee,
  inventaires,
}
fs.writeFileSync(OUT, JSON.stringify(out, null, 2), 'utf8')

console.log(`Cartes : ${cartes.length}`)
facturesParAnnee.forEach((a) => console.log(`Factures ${a.annee} : ${a.nb}`))
inventaires.forEach((i) => console.log(`Inventaire ${i.annee} : pdf=${!!i.pdf} csv=${!!i.csv}`))
console.log(`→ ${path.relative(process.cwd(), OUT)}`)
