// Consolide les CSV d'inventaire (boissons & alcools) en un JSON unique,
// facile à exploiter pour des analyses. 100 % local, relançable.
const fs = require('fs')
const path = require('path')

const DIR = path.join(__dirname, '..', 'public', 'documents', 'inventaires')
const OUT = path.join(DIR, 'inventaires.json')

// Inventaire au 31/03/AAAA = stock de clôture de l'exercice (avril→mars).
const FICHIERS = [
  { date: '2023-03-31', exercice: '2022-2023', csv: 'inventaire_2023-03-31.csv', pdf: 'Inventaire_Demi_Lune_2023-03-31.pdf' },
  { date: '2024-03-31', exercice: '2023-2024', csv: 'inventaire_2024-03-31.csv', pdf: 'Inventaire_Demi_Lune_2024-03-31.pdf' },
  { date: '2025-03-31', exercice: '2024-2025', csv: 'inventaire_2025-03-31.csv', pdf: 'Inventaire_Demi_Lune_2025-03-31.pdf' },
]

const num = (s) => {
  if (s == null || s.trim() === '') return null
  const v = Number(s.replace(',', '.'))
  return Number.isFinite(v) ? v : null
}
const r2 = (n) => Math.round(n * 100) / 100

function parseCsv(file) {
  const txt = fs.readFileSync(path.join(DIR, file), 'utf8').trim()
  const [, ...rows] = txt.split(/\r?\n/) // ignore l'en-tête
  return rows.filter(Boolean).map((line) => {
    const [produit, categorie, quantite, prix, valeur, fiabilite, page] = line.split(';')
    return {
      produit,
      categorie, // 'boisson_sans_alcool' | 'alcool'
      quantite: num(quantite),
      prixUnitaireHT: num(prix),
      valeurHT: num(valeur),
      fiabilite,
      page: num(page),
      // Lignes "[Page X - écart…]" = résidus non identifiés (valeur connue, produit non).
      residuel: produit.startsWith('['),
    }
  })
}

const inventaires = FICHIERS.map((f) => {
  const lignes = parseCsv(f.csv)
  const somme = (cat) =>
    r2(lignes.filter((l) => l.categorie === cat).reduce((a, l) => a + (l.valeurHT || 0), 0))
  const sansAlcoolHT = somme('boisson_sans_alcool')
  const alcoolHT = somme('alcool')
  return {
    date: f.date,
    exercice: f.exercice,
    pdf: `inventaires/${f.pdf}`,
    csv: `inventaires/${f.csv}`,
    nbLignes: lignes.length,
    totaux: { sansAlcoolHT, alcoolHT, totalHT: r2(sansAlcoolHT + alcoolHT) },
    lignes,
  }
})

const out = {
  objet: "Inventaires physiques de fin d'exercice — boissons & alcools",
  source: 'public/documents/inventaires (PDF scannés -> CSV)',
  avertissement:
    "Périmètre = boissons sans alcool + alcools/vins (hors alimentation, crèmerie, entretien). " +
    "Valeurs HT issues des inventaires ; lignes 'fiabilite=a_verifier' à recouper " +
    "(surtout pages manuscrites 2025). Les lignes 'residuel=true' portent une valeur sans produit identifié.",
  unites: 'quantite en bouteilles/unités ; prix et valeurs en € HT',
  inventaires,
}
fs.writeFileSync(OUT, JSON.stringify(out, null, 2), 'utf8')

console.log(`JSON : ${path.relative(process.cwd(), OUT)}`)
inventaires.forEach((i) =>
  console.log(`  ${i.date} (${i.exercice}) : ${i.nbLignes} lignes | SA ${i.totaux.sansAlcoolHT} € | AA ${i.totaux.alcoolHT} € | total ${i.totaux.totalHT} €`),
)
