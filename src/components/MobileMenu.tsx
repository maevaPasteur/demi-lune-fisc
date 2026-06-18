import { Box, Stack, Text } from '@mantine/core'
import { useMatch } from 'react-router-dom'
import { navLinks } from './navLinks'
import NavLinkItem from './NavLinkItem'
import RenduFinalNav from './RenduFinalNav'
import Brand from './Brand'

type MobileMenuProps = {
  // Appelé à la sélection d'un lien pour fermer le menu burger.
  onNavigate: () => void
}

// Contenu du tiroir mobile : même composition que la colonne desktop, mais on
// referme le tiroir au clic sur un lien.
export default function MobileMenu({ onNavigate }: MobileMenuProps) {
  // Sur /rendu-final(/*), on bascule sur le sommaire numéroté du Rendu final.
  const surRenduFinal = Boolean(useMatch({ path: '/rendu-final/*', end: false }))
  if (surRenduFinal) return <RenduFinalNav onNavigate={onNavigate} />

  return (
    <Stack h="100%" gap={0} p="md">
      <Box pb="lg">
        <Brand />
      </Box>

      <Stack gap={4} style={{ flex: 1 }}>
        <Text
          size="xs"
          fw={600}
          c="dimmed"
          tt="uppercase"
          px={14}
          mb={6}
          style={{ letterSpacing: '0.08em' }}
        >
          Navigation
        </Text>
        {navLinks.map((link) => (
          <NavLinkItem key={link.to} link={link} onNavigate={onNavigate} />
        ))}
      </Stack>
    </Stack>
  )
}
