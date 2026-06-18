import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { Badge, Box, Group, Paper, Stack, Text, Title } from '@mantine/core'
import { IconArrowRight, IconHome, IconCircleCheck, IconScale } from '@tabler/icons-react'
import { blocs, griefsParBloc, type Grief, type Statut } from '../../data/renduFinal'

// Libellé + couleur du statut d'un grief.
const STATUT: Record<Statut, { label: string; color: string }> = {
  demonte: { label: 'Démonté', color: 'teal' },
  partiel: { label: 'Étayé', color: 'blue' },
  'a-etayer': { label: 'À étayer', color: 'gray' },
}

function Etiquette({ children, color = 'dimmed' }: { children: ReactNode; color?: string }) {
  return (
    <Text size="xs" tt="uppercase" fw={700} c={color} style={{ letterSpacing: '0.06em' }}>
      {children}
    </Text>
  )
}

// Carte d'un grief dans la liste.
function CarteGrief({ g }: { g: Grief }) {
  const s = STATUT[g.statut]
  return (
    <Paper
      component={Link}
      to={`/rendu-final/${g.slug}`}
      p={{ base: 'lg', sm: 'xl' }}
      radius="lg"
      style={{ textDecoration: 'none', color: 'inherit', display: 'block' }}
    >
      <Stack gap="md">
        <Group justify="space-between" align="flex-start" wrap="nowrap" gap="md">
          <div>
            <Text size="xs" c="dimmed" mb={4}>
              {g.refRapport}
            </Text>
            <Title order={3} ff="heading" fz={{ base: 19, sm: 23 }} lh={1.15}>
              {g.titre}
            </Title>
          </div>
          <Badge variant="light" color={s.color} radius="sm" size="lg" tt="uppercase" style={{ flexShrink: 0 }}>
            {s.label}
          </Badge>
        </Group>

        <Box
          p="md"
          style={{
            background: 'var(--mantine-color-red-0)',
            border: '1px solid var(--mantine-color-red-2)',
            borderRadius: 'var(--mantine-radius-md)',
          }}
        >
          <Group gap={6} mb={6} wrap="nowrap">
            <IconHome size={14} color="var(--mantine-color-red-7)" />
            <Etiquette color="red.7">Ce que dit le fisc</Etiquette>
          </Group>
          <Text size="sm" c="red.9">
            {g.griefFisc}
          </Text>
        </Box>

        <Box
          p="md"
          style={{
            background: 'var(--mantine-color-teal-0)',
            border: '1px solid var(--mantine-color-teal-2)',
            borderRadius: 'var(--mantine-radius-md)',
          }}
        >
          <Group gap={6} mb={6} wrap="nowrap">
            <IconCircleCheck size={14} color="var(--mantine-color-teal-7)" />
            <Etiquette color="teal.7">Notre réponse</Etiquette>
          </Group>
          <Text size="sm">{g.reponseCourte}</Text>
        </Box>

        <Group justify="space-between" wrap="nowrap">
          {g.enjeu ? (
            <Text size="xs" c="dimmed" fs="italic">
              Enjeu : {g.enjeu}
            </Text>
          ) : (
            <span />
          )}
          <Group gap={6} wrap="nowrap" c="gold.7">
            <Text fw={600} c="gold.7" size="sm">
              Voir la réponse
            </Text>
            <IconArrowRight size={16} color="var(--mantine-color-gold-7)" />
          </Group>
        </Group>
      </Stack>
    </Paper>
  )
}

export default function RenduFinal() {
  return (
    <Stack gap={36}>
      <Stack gap="lg">
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
            <Stack gap="md">
              {items.map((g) => (
                <CarteGrief key={g.slug} g={g} />
              ))}
            </Stack>
          </Stack>
        )
      })}
    </Stack>
  )
}
