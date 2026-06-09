import { Link, useMatch } from 'react-router-dom'
import type { NavLink } from './navLinks'
import classes from './Navigation.module.css'

type NavLinkItemProps = {
  link: NavLink
  // Optionnel : referme le tiroir mobile à la navigation.
  onNavigate?: () => void
}

// Item de navigation partagé par la colonne (SideMenu) et le tiroir (MobileMenu).
// Icône + libellé, état actif tinté bleu avec barre d'accent (voir le CSS).
export default function NavLinkItem({ link, onNavigate }: NavLinkItemProps) {
  const { to, label, icon: Icon, end, ready } = link
  // Hook toujours appelé (règle des hooks) ; ignoré si la page n'est pas prête.
  const active = Boolean(useMatch({ path: to, end: Boolean(end) }))

  const content = (
    <>
      <span className={classes.icon}>
        <Icon size={20} stroke={1.7} />
      </span>
      <span className={classes.label}>{label}</span>
      {!ready && <span className={classes.soon}>Bientôt</span>}
    </>
  )

  if (!ready) {
    return (
      <span className={classes.link} data-disabled aria-disabled>
        {content}
      </span>
    )
  }

  return (
    <Link
      to={to}
      className={classes.link}
      data-active={active || undefined}
      onClick={onNavigate}
    >
      {content}
    </Link>
  )
}
