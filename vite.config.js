import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// base relative ('./') => fonctionne sur GitHub Pages quel que soit le nom du dépôt
// (username.github.io/<repo>/) sans avoir à coder le chemin en dur.
export default defineConfig({
  plugins: [react()],
  base: './',
})
