import {
  IconChartBar,
  IconFiles,
  IconGavel,
  IconLayoutDashboard,
  IconScale,
  type Icon,
} from '@tabler/icons-react'

// Rubriques du dossier, partagées par le menu latéral et le menu mobile.
// Les pages à venir sont listées mais désactivées (`ready: false`).
export type NavLink = {
  to: string
  label: string
  icon: Icon
  end?: boolean
  ready: boolean
}

export const navLinks: NavLink[] = [
  { to: '/', label: 'Accueil', icon: IconLayoutDashboard, end: true, ready: true },
  { to: '/rendu-final', label: 'Rendu final', icon: IconScale, ready: true },
  { to: '/defense', label: 'Défense', icon: IconGavel, ready: true },
  { to: '/analyses', label: 'Analyses', icon: IconChartBar, ready: true },
  { to: '/documents', label: 'Documents', icon: IconFiles, ready: true },
]
