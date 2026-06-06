import { Outlet } from 'react-router-dom'
import Navbar from './Navbar.jsx'

// Coque commune à toutes les pages : barre de navigation + zone de contenu.
export default function Layout() {
  return (
    <div className="app-shell">
      <Navbar />
      <main className="app-main">
        <Outlet />
      </main>
      <footer className="app-footer">
        <p>
          Espace de travail privé — usage strictement confidentiel dans le cadre
          de la défense fiscale. Non destiné à la diffusion publique.
        </p>
      </footer>
    </div>
  )
}
