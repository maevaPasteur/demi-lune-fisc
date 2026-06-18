import { Box, Stack, Text } from '@mantine/core'
import { useMatch } from 'react-router-dom'
import { navLinks } from './navLinks'
import NavLinkItem from './NavLinkItem'
import RenduFinalNav from './RenduFinalNav'
import Brand from './Brand'

// Colonne complète, affichée en tablette/desktop : marque en haut puis navigation.
export default function SideMenu() {
  // Sur /rendu-final(/*), on remplace la navigation générale par le sommaire
  // numéroté du Rendu final (blocs > griefs).
  const surRenduFinal = Boolean(useMatch({ path: '/rendu-final/*', end: false }))
  if (surRenduFinal) return <RenduFinalNav />

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
          <NavLinkItem key={link.to} link={link} />
        ))}
      </Stack>
    </Stack>
  )
}
