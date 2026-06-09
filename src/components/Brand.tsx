import { Group, Image, Text } from '@mantine/core'

// Logo servi depuis public/ ; BASE_URL respecte le sous-chemin GitHub Pages.
const logoUrl = `${import.meta.env.BASE_URL}images/logo.png`

type BrandProps = {
  // Variante compacte (sans sous-titre) pour l'en-tête mobile.
  compact?: boolean
}

// Marque du dossier : logo dans un carré doré + nom. En haut de la colonne de
// navigation (desktop / tiroir mobile).
export default function Brand({ compact = false }: BrandProps) {
  return (
    <Group gap="sm" wrap="nowrap">
      <Image src={logoUrl} alt="Logo Demi-Lune" h={46} w="auto" fit="contain" />

      <div>
        <Text fw={700} fz="lg" lh={1.15} ff="heading">
          Demi-Lune
        </Text>
        {!compact && (
          <Text size="xs" c="dimmed">
            Dossier de contrôle fiscal
          </Text>
        )}
      </div>
    </Group>
  )
}
