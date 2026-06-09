// Conversion rigoureuse .ods -> .xls (BIFF8) via SheetJS.
// - Préserve toutes les feuilles, les valeurs, les dates et les formats de nombre.
// - Vérifie après écriture que chaque feuille a les mêmes dimensions et le même
//   nombre de cellules non vides (contrôle d'intégrité), puis supprime l'.ods.
const fs = require('fs')
const path = require('path')
const XLSX = require('xlsx')

const dir = path.join(__dirname, '..', 'public', 'documents')
const odsFiles = fs.readdirSync(dir).filter((f) => f.toLowerCase().endsWith('.ods'))

// Assainit un nom de feuille pour le format .xls : décodage des entités,
// suppression des caractères interdits (: \ / ? * [ ]), troncature à 31 car.
// On renomme les onglets dans le classeur (le nom d'export d'origine est un
// artefact technique ; seules les données comptent).
function sanitizeName(name, fallback) {
  let n = String(name)
    .replace(/&apos;/g, "'")
    .replace(/&amp;/g, '&')
    .replace(/[:\\/?*[\]]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .replace(/^'+|'+$/g, '')
    .slice(0, 31)
    .trim()
  if (!n) n = fallback
  return n.slice(0, 31)
}

function renameSheets(wb) {
  const used = new Set()
  const newNames = wb.SheetNames.map((name, i) => {
    let base = sanitizeName(name, `Feuille${i + 1}`)
    let candidate = base
    let k = 1
    while (used.has(candidate)) {
      const suffix = `_${k++}`
      candidate = base.slice(0, 31 - suffix.length) + suffix
    }
    used.add(candidate)
    return candidate
  })
  const sheets = {}
  wb.SheetNames.forEach((old, i) => {
    sheets[newNames[i]] = wb.Sheets[old]
  })
  wb.SheetNames = newNames
  wb.Sheets = sheets
  return wb
}

// Empreinte d'un classeur : par feuille, dimensions + nb de cellules non vides.
function fingerprint(wb) {
  return wb.SheetNames.map((name) => {
    const ws = wb.Sheets[name]
    const ref = ws['!ref'] || 'A1:A1'
    const range = XLSX.utils.decode_range(ref)
    let cells = 0
    for (const key of Object.keys(ws)) {
      if (key[0] === '!') continue
      const c = ws[key]
      if (c && c.v !== undefined && c.v !== null && c.v !== '') cells++
    }
    return { name, rows: range.e.r - range.s.r + 1, cols: range.e.c - range.s.c + 1, cells }
  })
}

let ok = 0
const failures = []

for (const file of odsFiles) {
  const src = path.join(dir, file)
  const out = path.join(dir, file.replace(/\.ods$/i, '.xls'))

  const wb = XLSX.readFile(src, { cellDates: true, cellNF: true })
  renameSheets(wb)
  const before = fingerprint(wb)

  XLSX.writeFile(wb, out, { bookType: 'biff8', cellDates: true })

  // Relecture du .xls produit pour contrôle d'intégrité.
  const wb2 = XLSX.readFile(out, { cellDates: true, cellNF: true })
  const after = fingerprint(wb2)

  const same =
    before.length === after.length &&
    before.every((b, i) => {
      const a = after[i]
      return a && a.name === b.name && a.rows === b.rows && a.cols === b.cols && a.cells === b.cells
    })

  if (same) {
    fs.unlinkSync(src)
    ok++
    console.log(`OK  ${file} -> ${path.basename(out)}  ` + before.map((b) => `${b.name}:${b.rows}x${b.cols}/${b.cells}`).join(', '))
  } else {
    failures.push(file)
    console.error(`FAIL ${file}`)
    console.error('  before:', JSON.stringify(before))
    console.error('  after :', JSON.stringify(after))
  }
}

console.log(`\n${ok}/${odsFiles.length} converties.`)
if (failures.length) {
  console.error('Échecs:', failures.join(', '))
  process.exit(1)
}
