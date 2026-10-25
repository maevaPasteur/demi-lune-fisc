import {
  IconFiles,
  IconLayoutDashboard,
  IconMessage2Exclamation,
  type Icon,
} from '@tabler/icons-react'

// Rubriques du menu latéral et du menu mobile.
// Menu volontairement réduit à trois entrées : Accueil, Réponse (dernière
// contre-analyse en date = Réponse 2), Documents. Les onglets « Réponse 1 »,
// « Rendu final », « Défense » et « Analyses » restent accessibles par URL
// directe (et par les renvois internes), mais ne figurent plus au menu.
export type NavLink = {
  to: string
  label: string
  icon: Icon
  end?: boolean
  ready: boolean
}

export const navLinks: NavLink[] = [
  { to: '/', label: 'Accueil', icon: IconLayoutDashboard, end: true, ready: true },
  { to: '/reponse-2', label: 'Réponse', icon: IconMessage2Exclamation, ready: true },
  { to: '/documents', label: 'Documents', icon: IconFiles, ready: true },
]
