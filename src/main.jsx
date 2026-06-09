import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { MantineProvider, createTheme } from '@mantine/core'
import '@mantine/core/styles.css'
import '@mantine/charts/styles.css'
import './theme.css'
import App from './App.jsx'

// Palette « or / ambre » maison (10 nuances, du crème au brun doré). C'est la
// couleur tonique du dossier ; le bleu n'est gardé qu'en accent secondaire.
const gold = [
  '#fbf6e9',
  '#f4e9c9',
  '#ebd79b',
  '#e1c168',
  '#d8ae3e',
  '#cf9f23',
  '#c08d12',
  '#a0740d',
  '#7f5c0e',
  '#6a4d0f',
]

// Thème global : dashboard clair et chaleureux, accent doré, grands titres serif
// (Playfair Display) et corps sans-serif. Cartes blanches finement bordées.
const theme = createTheme({
  colors: { gold },
  primaryColor: 'gold',
  primaryShade: 6,
  defaultRadius: 'lg',
  fontFamily:
    '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
  // Titres en serif élégant haute graisse.
  headings: {
    fontWeight: '700',
    fontFamily: '"Playfair Display", Georgia, "Times New Roman", serif',
  },
  shadows: {
    xs: '0 1px 2px rgba(60, 45, 12, 0.04)',
    sm: '0 1px 3px rgba(60, 45, 12, 0.06), 0 1px 2px rgba(60, 45, 12, 0.04)',
    md: '0 6px 20px rgba(60, 45, 12, 0.07)',
    lg: '0 16px 40px rgba(60, 45, 12, 0.10)',
  },
  components: {
    Paper: {
      defaultProps: { shadow: 'sm', radius: 'lg', withBorder: true },
    },
  },
})

// Note : le fond clair de la page est appliqué sur la zone de contenu
// (AppShell.Main dans Layout), surtout pas via --mantine-color-body - sinon les
// cartes Paper, qui s'appuient sur cette variable, perdraient leur fond blanc.
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <MantineProvider
      theme={theme}
      defaultColorScheme="light"
      forceColorScheme="light"
    >
      {/* basename dérivé de la base Vite : URLs propres sans # */}
      <BrowserRouter basename={import.meta.env.BASE_URL.replace(/\/$/, '')}>
        <App />
      </BrowserRouter>
    </MantineProvider>
  </React.StrictMode>,
)
