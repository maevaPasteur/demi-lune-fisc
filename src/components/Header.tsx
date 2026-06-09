import { Fragment } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Anchor, Box, Burger, Group, Text } from '@mantine/core'
import { IconChevronRight } from '@tabler/icons-react'
import { navLinks } from './navLinks'
import { titreParSlug } from '../data/documents'
import { analyseParSlug } from '../data/analyses'
import { frontParSlug } from '../data/defense'
import Brand from './Brand'

type HeaderProps = {
  // État + bascule du menu burger (mobile uniquement).
  opened: boolean
  toggle: () => void
}

type Crumb = { label: string; to?: string }

// Fil d'Ariane « Dossier / Section / Détail » dérivé de la route active.
// Le dernier élément est la page courante (non cliquable).
function useBreadcrumb(): Crumb[] {
  const { pathname } = useLocation()
  const trail: Crumb[] = [{ label: 'Dossier', to: '/' }]

  const section =
    navLinks.find((l) => (l.end ? l.to === pathname : pathname.startsWith(l.to))) ??
    navLinks[0]

  // Page détail : /documents|analyses|defense/<slug>
  const detail = pathname.match(/^\/(documents|analyses|defense)\/(.+)$/)

  if (section) {
    trail.push({
      label: section.label,
      // La section devient cliquable uniquement si une page détail suit.
      to: detail && section.to !== '/' ? section.to : undefined,
    })
  }

  if (detail) {
    const slug = decodeURIComponent(detail[2])
    const titre =
      detail[1] === 'analyses'
        ? analyseParSlug(slug)?.titre
        : detail[1] === 'defense'
          ? frontParSlug(slug)?.titre
          : titreParSlug(slug)
    trail.push({ label: titre ?? 'Détail' })
  }

  return trail
}

// En-tête au-dessus du contenu : fil d'Ariane à gauche, badge confidentiel à
// droite. La marque vit dans la colonne ; en mobile on la rappelle ici.
export default function Header({ opened, toggle }: HeaderProps) {
  const trail = useBreadcrumb()

  return (
    <Group h="100%" px="lg" justify="space-between" wrap="nowrap">
      <Group gap="sm" wrap="nowrap" style={{ minWidth: 0 }}>
        <Burger
          opened={opened}
          onClick={toggle}
          hiddenFrom="sm"
          size="sm"
          aria-label="Ouvrir le menu"
        />
        {/* Marque compacte, mobile uniquement */}
        <Box hiddenFrom="sm">
          <Brand compact />
        </Box>
        {/* Fil d'Ariane, desktop / tablette */}
        <Group gap={8} wrap="nowrap" visibleFrom="sm" style={{ minWidth: 0 }}>
          {trail.map((crumb, i) => {
            const last = i === trail.length - 1
            return (
              <Fragment key={`${crumb.label}-${i}`}>
                {i > 0 && (
                  <IconChevronRight
                    size={15}
                    color="var(--mantine-color-gray-4)"
                    style={{ flexShrink: 0 }}
                  />
                )}
                {last ? (
                  <Text size="sm" fw={600} c="dark" lineClamp={1}>
                    {crumb.label}
                  </Text>
                ) : crumb.to ? (
                  <Anchor
                    component={Link}
                    to={crumb.to}
                    size="sm"
                    fw={500}
                    c="dimmed"
                    style={{ whiteSpace: 'nowrap' }}
                  >
                    {crumb.label}
                  </Anchor>
                ) : (
                  <Text size="sm" fw={500} c="dimmed" style={{ whiteSpace: 'nowrap' }}>
                    {crumb.label}
                  </Text>
                )}
              </Fragment>
            )
          })}
        </Group>
      </Group>

    </Group>
  )
}
