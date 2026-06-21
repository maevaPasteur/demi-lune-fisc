import { Link } from 'react-router-dom'
import { Box, Group, Paper, SimpleGrid, Stack, Text, Title } from '@mantine/core'
import { IconArrowRight, IconScale } from '@tabler/icons-react'
import { blocs, griefsParBloc, type Grief } from '../../data/renduFinal'

// Carte compacte d'un grief, pensée pour une grille responsive.
function CarteGrief({ g }: { g: Grief }) {
  return (
    <Paper
      component={Link}
      to={`/rendu-final/${g.slug}`}
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
        <Text size="xs" c="dimmed">
          {g.refRapport}
        </Text>

        <Title order={3} ff="heading" fz={{ base: 18, sm: 20 }} lh={1.2}>
          {g.titre}
        </Title>

        {g.enjeu && (
          <Text size="xs" c="dimmed" fs="italic">
            Enjeu : {g.enjeu}
          </Text>
        )}
      </Stack>

      <Group gap={6} wrap="nowrap" mt="md">
        <Text fw={600} c="gold.7" size="sm">
          Voir la réponse
        </Text>
        <IconArrowRight size={16} color="var(--mantine-color-gold-7)" />
      </Group>
    </Paper>
  )
}

export default function RenduFinal() {
  return (
    <Stack gap={36}>
      <Stack gap="xs">
        <Group gap="xs">
          <IconScale size={18} color="var(--mantine-color-gold-6)" />
          <Text fw={700} size="sm" c="gold.7" tt="uppercase" style={{ letterSpacing: '0.12em' }}>
            Réponse à la proposition de rectification
          </Text>
        </Group>
        <Title order={1} ff="heading" fz={{ base: 40, sm: 56 }} lh={1.05}>
          Rendu final
        </Title>
        <Text c="dimmed" size="lg" maw={760}>
          Chaque grief de la proposition de rectification est repris point par point :
          ce que soutient l’administration, notre réponse, le calcul exact, les
          fichiers à l’appui et le résultat. Conçu pour le rendez-vous avec le service.
        </Text>
      </Stack>

      {blocs.map((bloc) => {
        const items = griefsParBloc(bloc.id)
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
              <Text c="dimmed" size="sm" maw={760}>
                {bloc.sousTitre}
              </Text>
            </Stack>

            <SimpleGrid cols={{ base: 1, sm: 2, lg: 3 }} spacing="md">
              {items.map((g) => (
                <CarteGrief key={g.slug} g={g} />
              ))}
            </SimpleGrid>
          </Stack>
        )
      })}
    </Stack>
  )
}
