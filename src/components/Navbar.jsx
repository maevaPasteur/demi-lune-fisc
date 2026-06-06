import { NavLink } from 'react-router-dom'

// Liens de navigation. On déclare déjà les rubriques à venir (désactivées)
// pour donner la structure cible du dossier.
const links = [
  { to: '/', label: 'Accueil', end: true, ready: true },
  { to: '/documents', label: 'Documents', ready: false },
  { to: '/analyses', label: 'Analyses', ready: false },
  { to: '/chronologie', label: 'Chronologie', ready: false },
]

export default function Navbar() {
  return (
    <header className="navbar">
      <div className="navbar__brand">
        <span className="navbar__logo" aria-hidden="true">◐</span>
        <div>
          <strong>Demi-Lune</strong>
          <span className="navbar__subtitle">Dossier de contrôle fiscal</span>
        </div>
      </div>
      <nav className="navbar__links">
        {links.map((link) =>
          link.ready ? (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.end}
              className={({ isActive }) =>
                'navbar__link' + (isActive ? ' navbar__link--active' : '')
              }
            >
              {link.label}
            </NavLink>
          ) : (
            <span
              key={link.to}
              className="navbar__link navbar__link--disabled"
              title="Bientôt disponible"
            >
              {link.label}
            </span>
          ),
        )}
      </nav>
    </header>
  )
}
