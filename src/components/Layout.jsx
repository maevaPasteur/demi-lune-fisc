import { useEffect } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import { AppShell, Box, Container, Text } from '@mantine/core'
import { useDisclosure } from '@mantine/hooks'
import Header from './Header.tsx'
import SideMenu from './SideMenu.tsx'
import MobileMenu from './MobileMenu.tsx'

// Remonte en haut de page à chaque changement de route (sinon on conserve la
// position de défilement de la page précédente).
function ScrollToTop() {
  const { pathname } = useLocation()
  useEffect(() => {
    window.scrollTo(0, 0)
  }, [pathname])
  return null
}

// Coque commune (layout "alt") : colonne de navigation pleine hauteur à gauche
// (marque + liens + état), en-tête au-dessus du contenu (fil d'Ariane +
// confidentiel), zone de contenu sur fond crème avec un léger halo doré en haut.
export default function Layout() {
  const [opened, { toggle, close }] = useDisclosure(false)

  return (
    <>
      <ScrollToTop />
      <AppShell
      layout="alt"
      header={{ height: 72 }}
      navbar={{
        width: 280,
        breakpoint: 'sm',
        collapsed: { mobile: !opened },
      }}
      padding={0}
      styles={{
        header: { borderBottom: '1px solid var(--app-border)' },
        navbar: { borderRight: '1px solid var(--app-border)' },
      }}
    >
      <AppShell.Header bg="white">
        <Header opened={opened} toggle={toggle} />
      </AppShell.Header>

      <AppShell.Navbar bg="white">
        {/* Colonne persistante en tablette/desktop */}
        <Box h="100%" visibleFrom="sm">
          <SideMenu />
        </Box>
        {/* Tiroir affiché par le burger en mobile */}
        <Box h="100%" hiddenFrom="sm">
          <MobileMenu onNavigate={close} />
        </Box>
      </AppShell.Navbar>

      <AppShell.Main
        style={{
          background:
            'linear-gradient(180deg, rgba(216,174,62,0.10) 0%, rgba(216,174,62,0) 320px), var(--app-bg)',
          minHeight: '100vh',
        }}
      >
        <Container size="lg" py={{ base: 24, sm: 44 }}>
          <Outlet />
        </Container>
        <Container size="lg" pb={40}>
          <Text size="xs" c="dimmed" ta="center">
            Espace de travail privé - usage strictement confidentiel dans le
            cadre de la défense fiscale. Non destiné à la diffusion publique.
          </Text>
        </Container>
      </AppShell.Main>
      </AppShell>
    </>
  )
}
