import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Base ABSOLUE = chemin du site de projet GitHub Pages
// (https://<user>.github.io/demi-lune-comptabilite/). Indispensable pour le
// routage sans # (BrowserRouter) : les routes profondes comme /documents/xxx
// doivent référencer les assets en chemin absolu, pas relatif.
// → Si tu changes d'hébergement (domaine perso ou site user/org), mets '/'.
export default defineConfig({
  plugins: [react()],
  base: '/demi-lune-fisc/',
})
