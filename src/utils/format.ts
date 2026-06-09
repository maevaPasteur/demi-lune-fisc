// Helpers de présentation. Aucune donnée métier ici, uniquement du formatage.

const euroFormat = new Intl.NumberFormat('fr-FR', {
  style: 'currency',
  currency: 'EUR',
  maximumFractionDigits: 0,
})

/** Formate un montant en euros français : "471 826 €" (espace insécable). */
export function formatEuro(montant: number): string {
  return euroFormat.format(montant)
}

const euroPrecisFormat = new Intl.NumberFormat('fr-FR', {
  style: 'currency',
  currency: 'EUR',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
})

/** Euros avec centimes : "8,70 €" (pour les valeurs unitaires). */
export function formatEuroPrecis(montant: number): string {
  return euroPrecisFormat.format(montant)
}

const intFormat = new Intl.NumberFormat('fr-FR')

/** Entier avec séparateur de milliers : "21 302". */
export function formatInt(n: number): string {
  return intFormat.format(n)
}

/** Pourcentage français : "33,8 %" (1 décimale par défaut). */
export function formatPct(valeur: number, decimales = 1): string {
  return `${valeur.toLocaleString('fr-FR', {
    minimumFractionDigits: decimales,
    maximumFractionDigits: decimales,
  })} %`
}

/**
 * Nombre de jours restants jusqu'à une date ISO (AAAA-MM-JJ).
 * Renvoie null si la date est absente ou invalide (placeholder non renseigné).
 */
export function joursRestants(dateISO: string): number | null {
  const cible = new Date(dateISO)
  if (Number.isNaN(cible.getTime())) return null

  const aujourdhui = new Date()
  aujourdhui.setHours(0, 0, 0, 0)
  cible.setHours(0, 0, 0, 0)

  const msParJour = 1000 * 60 * 60 * 24
  return Math.round((cible.getTime() - aujourdhui.getTime()) / msParJour)
}
