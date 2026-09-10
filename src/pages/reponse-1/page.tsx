import { Link } from 'react-router-dom'
import { Badge, Box, Group, Paper, SimpleGrid, Stack, Text, Title } from '@mantine/core'
import { IconArrowRight, IconMessage2Exclamation } from '@tabler/icons-react'
import { blocs, pointsParBloc, numeroDuPoint, type Point, type Statut } from '../../data/reponse1'

// Pastille de verdict : où en est la réfutation de ce point.
const VERDICT: Record<Statut, { label: string; couleur: string }> = {
  demonte: { label: 'Réfuté', couleur: 'teal' },
  partiel: { label: 'Réfuté en partie', couleur: 'yellow' },
  'a-etayer': { label: 'À étayer', couleur: 'gray' },
}

// Carte compacte d'un point du courrier, pensée pour une grille responsive.
function CartePoint({ p }: { p: Point }) {
  return (
    <Paper
      component={Link}
      to={`/reponse-1/${p.slug}`}
      p={{ base: 'md', sm: 'lg' }}
      radius="lg"
      withBorder
      style={{
        textDecoration: 'none',
        color: 'inherit',
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
      }}
    >
      <Stack gap="sm" style={{ flex: 1 }}>
        <Group justify="space-between" wrap="nowrap" align="flex-start" gap="xs">
          <Text size="xs" c="dimmed">
            {numeroDuPoint(p.slug)} · {p.refCourrier}
          </Text>
          <Badge size="xs" variant="light" color={VERDICT[p.statut].couleur} style={{ flexShrink: 0 }}>
            {VERDICT[p.statut].label}
          </Badge>
        </Group>

        <Title order={3} ff="heading" fz={{ base: 18, sm: 20 }} lh={1.2}>
          {p.titre}
        </Title>

        {p.reponseCourte && (
          <Text size="sm" c="gray.7" lineClamp={4}>
            {p.reponseCourte}
          </Text>
        )}

        {p.enjeu && (
          <Text size="xs" c="dimmed" fs="italic">
            Enjeu : {p.enjeu}
          </Text>
        )}
      </Stack>

      <Group gap={6} wrap="nowrap" mt="md">
        <Text fw={600} c="gold.7" size="sm">
          Voir la contre-analyse
        </Text>
        <IconArrowRight size={16} color="var(--mantine-color-gold-7)" />
      </Group>
    </Paper>
  )
}

export default function Reponse1() {
  return (
    <Stack gap={36}>
      <Stack gap="xs">
        <Group gap="xs">
          <IconMessage2Exclamation size={18} color="var(--mantine-color-gold-6)" />
          <Text fw={700} size="sm" c="gold.7" tt="uppercase" style={{ letterSpacing: '0.12em' }}>
            Contre-analyse de la réponse du 4 septembre 2026
          </Text>
        </Group>
        <Title order={1} ff="heading" fz={{ base: 40, sm: 56 }} lh={1.05}>
          Réponse 1
        </Title>
        <Text c="dimmed" size="lg" maw={820}>
          Le 4 septembre 2026, la Direction départementale des finances publiques du Jura
          a répondu, sur 96 pages, au mémoire adressé au service le 10 juillet 2026. Elle
          maintient l’intégralité des rectifications. Cet onglet reprend son courrier
          <strong> point par point, dans son ordre exact</strong> : ce que soutient
          l’administration, puis la réfutation, textes et calculs à l’appui.
        </Text>
      </Stack>

      {blocs.map((bloc) => {
        const items = pointsParBloc(bloc.id)
        if (items.length === 0) return null
        return (
          <Stack key={bloc.id} gap="md">
            <Stack gap={4}>
              <Group gap="sm" align="center">
                <Box
                  w={32}
                  h={32}
                  style={{
                    borderRadius: 999,
                    background: 'var(--mantine-color-gold-1)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                  }}
                >
                  <Text ff="heading" fw={700} c="gold.8">
                    {bloc.numero}
                  </Text>
                </Box>
                <Title order={2} ff="heading" fz={{ base: 24, sm: 30 }} lh={1.1}>
                  {bloc.titre}
                </Title>
              </Group>
              <Text c="dimmed" size="sm" maw={820}>
                {bloc.sousTitre}
              </Text>
            </Stack>

            <SimpleGrid cols={{ base: 1, sm: 2, lg: 3 }} spacing="md">
              {items.map((p) => (
                <CartePoint key={p.slug} p={p} />
              ))}
            </SimpleGrid>
          </Stack>
        )
      })}
    </Stack>
  )
}
