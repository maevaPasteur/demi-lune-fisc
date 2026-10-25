import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout.jsx'
import Home from './pages/Home'
import Documents from './pages/documents/page'
import DocumentDetail from './pages/documents/[slug]/page'
import Analyses from './pages/analyses/page'
import AnalyseDetail from './pages/analyses/[slug]/page'
import Defense from './pages/defense/page'
import FrontDetail from './pages/defense/[slug]/page'
import RenduFinal from './pages/rendu-final/page'
import GriefDetail from './pages/rendu-final/[slug]/page'
import Reponse1 from './pages/reponse-1/page'
import Reponse1Detail from './pages/reponse-1/[slug]/page'
import Reponse2 from './pages/reponse-2/page'
import Reponse2Detail from './pages/reponse-2/[slug]/page'

// Le menu n'expose que Accueil / Réponse (= Réponse 2) / Documents, mais toutes
// les routes restent actives : les anciens onglets sont accessibles par URL et
// par les renvois internes (la Réponse 2 pointe vers la Réponse 1).
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
        <Route path="rendu-final" element={<RenduFinal />} />
        <Route path="rendu-final/:slug" element={<GriefDetail />} />
        <Route path="reponse-1" element={<Reponse1 />} />
        <Route path="reponse-1/:slug" element={<Reponse1Detail />} />
        <Route path="reponse-2" element={<Reponse2 />} />
        <Route path="reponse-2/:slug" element={<Reponse2Detail />} />
      </Route>
    </Routes>
  )
}
