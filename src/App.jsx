import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout.jsx'
import Home from './pages/Home.jsx'

// Le routeur est en place : on n'expose pour l'instant que la page d'accueil.
// Les futures pages (documents, analyses, chronologie…) s'ajoutent ici en
// une ligne : <Route path="documents" element={<Documents />} />
export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
      </Route>
    </Routes>
  )
}
