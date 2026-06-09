import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout.jsx'
import Home from './pages/Home'
import Documents from './pages/documents/page'
import DocumentDetail from './pages/documents/[slug]/page'
import Analyses from './pages/analyses/page'
import AnalyseDetail from './pages/analyses/[slug]/page'
import Defense from './pages/defense/page'
import FrontDetail from './pages/defense/[slug]/page'

// Le routeur est en place : on n'expose pour l'instant que la page d'accueil.
// Les futures pages (documents, analyses, chronologie…) s'ajoutent ici en
// une ligne : <Route path="documents" element={<Documents />} />
export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="documents" element={<Documents />} />
        <Route path="documents/:slug" element={<DocumentDetail />} />
        <Route path="analyses" element={<Analyses />} />
        <Route path="analyses/:slug" element={<AnalyseDetail />} />
        <Route path="defense" element={<Defense />} />
        <Route path="defense/:slug" element={<FrontDetail />} />
      </Route>
    </Routes>
  )
}
