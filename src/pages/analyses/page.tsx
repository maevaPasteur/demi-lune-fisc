import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import {
  Anchor,
  Badge,
  Box,
  Button,
  Group,
  Paper,
  SimpleGrid,
  Stack,
  Text,
  Title,
} from '@mantine/core'
import {
  IconArrowRight,
  IconCircleCheck,
  IconFileText,
  IconHome,
  IconReceiptEuro,
  IconShieldCheck,
} from '@tabler/icons-react'
import { analyses, type Analyse } from '../../data/analyses'
import { totalPenalites } from '../../data/dossier'
import { formatEuro } from '../../utils/format'

// Pastille de statistique de l'en-tête.
function StatPill({ icon, value, label }: { icon: ReactNode; value: string; label: string }) {
  return (
    <Group
      gap="xs"
      px="lg"
      py={10}
      wrap="nowrap"
      style={{ border: '1px solid var(--mantine-color-gray-3)', borderRadius: 999, background: 'var(--mantine-color-white)' }}
    >
      {icon}
      <Text fw={700} ff="heading">
        {value}
      </Text>
      <Text c="dimmed" size="sm">
        {label}
      </Text>
    </Group>
  )
}

// Petit titre de section dans la carte.
function Etiquette({ children, color = 'dimmed' }: { children: ReactNode; color?: string }) {
  return (
    <Text size="xs" tt="uppercase" fw={700} c={color} style={{ letterSpacing: '0.06em' }}>
      {children}
    </Text>
  )
}

// Carte "levier" : argument du contrôleur vs démonstration, ce que ça fait tomber.
function CarteAnalyse({ a, num }: { a: Analyse; num: number }) {
  return (
    <Paper p={{ base: 'lg', sm: 'xl' }} radius="lg">
      <Stack gap="lg">
        {/* En-tête : numéro + titre + force */}
        <Group justify="space-between" align="flex-start" wrap="nowrap" gap="md">
          <Group gap="md" wrap="nowrap" align="center">
            <Box
              w={42}
              h={42}
              style={{
                borderRadius: 999,
                background: 'var(--mantine-color-gold-1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
              }}
            >
              <Text ff="heading" fw={700} fz={20} c="gold.8">
                {num}
              </Text>
            </Box>
            <div>
              <Text fw={700} size="xs" c="gold.7" tt="uppercase" style={{ letterSpacing: '0.1em' }}>
                {a.eyebrow}
              </Text>
              <Title order={2} ff="heading" fz={{ base: 22, sm: 28 }} lh={1.1}>
                {a.titre}
              </Title>
            </div>
          </Group>
          <Badge variant="light" color="teal" radius="sm" size="lg" tt="uppercase" style={{ flexShrink: 0 }}>
            Levier {a.force === 'forte' ? 'fort' : 'moyen'}
          </Badge>
        </Group>

        {/* Contrôleur vs démonstration */}
        <SimpleGrid cols={{ base: 1, md: 2 }} spacing="md">
          <Box
            p="md"
            style={{
              background: 'var(--mantine-color-red-0)',
              border: '1px solid var(--mantine-color-red-2)',
              borderRadius: 'var(--mantine-radius-md)',
            }}
          >
            <Group gap={6} mb={6} wrap="nowrap">
              <IconHome size={15} color="var(--mantine-color-red-7)" />
              <Etiquette color="red.7">Ce que dit le contrôleur</Etiquette>
            </Group>
            <Text size="sm" c="red.9">
              {a.controleurDit}
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
              <IconCircleCheck size={15} color="var(--mantine-color-teal-7)" />
              <Etiquette color="teal.7">La démonstration</Etiquette>
            </Group>
            <Text size="sm">{a.demonstration}</Text>
          </Box>
        </SimpleGrid>

        {/* Ce que ça fait tomber */}
        {a.faitTomber && (
          <div>
            <Etiquette>Ce que ça fait tomber</Etiquette>
            <Group
              gap={8}
              mt={6}
              px="md"
              py={10}
              wrap="nowrap"
              style={{
                background: 'var(--mantine-color-teal-0)',
                border: '1px solid var(--mantine-color-teal-2)',
                borderRadius: 'var(--mantine-radius-md)',
              }}
            >
              <IconCircleCheck size={17} color="var(--mantine-color-teal-7)" />
              <Text fw={600} c="teal.8">
                {a.faitTomber}
              </Text>
            </Group>
          </div>
        )}

        {/* Pièces liées */}
        {a.pieces && a.pieces.length > 0 && (
          <div>
            <Etiquette>Pièces liées</Etiquette>
            <Group gap="xs" mt={6}>
              {a.pieces.map((p) => (
                <Button
                  key={p.to}
                  component={Link}
                  to={p.to}
                  size="xs"
                  variant="default"
                  radius="md"
                  leftSection={<IconFileText size={13} />}
                >
                  {p.label}
                </Button>
              ))}
            </Group>
          </div>
        )}

        {/* Lien vers l'analyse détaillée */}
        <Anchor component={Link} to={`/analyses/${a.slug}`} fw={600} c="gold.7" style={{ textDecoration: 'none' }}>
          <Group gap={6} wrap="nowrap">
            Voir l’analyse chiffrée
            <IconArrowRight size={16} />
          </Group>
        </Anchor>
      </Stack>
    </Paper>
  )
}

export default function Analyses() {
  return (
    <Stack gap={32}>
      <Stack gap="lg">
        <Stack gap="xs">
          <Text fw={700} size="sm" c="gold.7" tt="uppercase" style={{ letterSpacing: '0.12em' }}>
            Preuves chiffrées
          </Text>
          <Title order={1} ff="heading" fz={{ base: 40, sm: 56 }} lh={1.05}>
            Les analyses
          </Title>
          <Text c="dimmed" size="lg" maw={720}>
            Chaque analyse confronte l’argument du contrôleur à la démonstration
            chiffrée, et précise ce qu’elle fait tomber.
          </Text>
        </Stack>

        <Group gap="sm">
          <StatPill
            icon={<IconShieldCheck size={17} color="var(--mantine-color-gold-6)" />}
            value={String(analyses.length)}
            label="analyses chiffrées"
          />
          <StatPill
            icon={<IconReceiptEuro size={17} color="var(--mantine-color-gold-6)" />}
            value={formatEuro(totalPenalites)}
            label="contestés"
          />
        </Group>
      </Stack>

      <Stack gap="lg">
        {analyses.map((a, i) => (
          <CarteAnalyse key={a.slug} a={a} num={i + 1} />
        ))}
      </Stack>
    </Stack>
  )
}
