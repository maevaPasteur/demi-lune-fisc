import { Link, useParams } from 'react-router-dom'
import { Anchor, Box, Button, Group, Paper, Stack, Text, Title } from '@mantine/core'
import { IconArrowLeft, IconArrowRight, IconBuildingBank } from '@tabler/icons-react'
import {
  pointParSlug,
  sectionsDuPoint,
  numeroDuPoint,
  voisins,
  blocs,
} from '../../../data/reponse1'
import AnalyseContent from '../../../components/AnalyseContent'

function RetourLien() {
  return (
    <Anchor component={Link} to="/reponse-1" c="dimmed" fw={500}>
      <Group gap={6} wrap="nowrap">
        <IconArrowLeft size={16} />
        Toute la réponse 1
      </Group>
    </Anchor>
  )
}

// Route : /reponse-1/:slug - contre-analyse d'un point de la réponse du fisc.
export default function PointDetail() {
  const { slug } = useParams()
  const point = slug ? pointParSlug(slug) : undefined

  if (!point) {
    return (
      <Stack gap="lg">
        <RetourLien />
        <Title order={1} fz={{ base: 32, sm: 44 }}>
          Point introuvable
        </Title>
        <Text c="dimmed">Aucun point ne correspond à « {slug} ».</Text>
        <Button component={Link} to="/reponse-1" radius="md" w="fit-content">
          Retour à la réponse 1
        </Button>
      </Stack>
    )
  }

  const bloc = blocs.find((b) => b.id === point.bloc)
  const sections = sectionsDuPoint(point.slug)
  const { prec, suiv } = voisins(point.slug)

  return (
    <Stack gap={32}>
      <RetourLien />
      <Stack gap="sm">
        {bloc && (
          <Text fw={700} size="sm" c="gold.7" tt="uppercase" style={{ letterSpacing: '0.12em' }}>
            Bloc {bloc.numero} — {bloc.titre}
          </Text>
        )}
        <Title order={1} fz={{ base: 32, sm: 48 }} lh={1.05}>
          {point.titre}
        </Title>
        <Text size="xs" c="dimmed">
          {numeroDuPoint(point.slug)} · {point.refCourrier}
          {point.enjeu ? ` · Enjeu : ${point.enjeu}` : ''}
        </Text>

        {/* Rappel de la position maintenue par le service, avant le détail. */}
        {point.positionService && (
          <Box
            mt="xs"
            p="md"
            style={{
              background: 'var(--mantine-color-red-0)',
              border: '1px solid var(--mantine-color-red-2)',
              borderRadius: 'var(--mantine-radius-md)',
            }}
          >
            <Group gap={6} mb={6} wrap="nowrap">
              <IconBuildingBank size={15} color="var(--mantine-color-red-7)" />
              <Text size="xs" tt="uppercase" fw={700} c="red.7" style={{ letterSpacing: '0.06em' }}>
                Ce que maintient l’administration
              </Text>
            </Group>
            <Text size="sm" c="red.9">
              {point.positionService}
            </Text>
          </Box>
        )}
        {point.reponseCourte && (
          <Text fw={600} size="lg" maw={820}>
            {point.reponseCourte}
          </Text>
        )}
      </Stack>

      {sections.length > 0 ? (
        <AnalyseContent sections={sections} />
      ) : (
        <Paper p="lg" radius="lg" withBorder>
          <Text size="sm" c="dimmed">
            Contre-analyse en cours de rédaction pour ce point.
          </Text>
        </Paper>
      )}

      {/* Navigation séquentielle : on suit l'ordre du courrier du 04/09/2026. */}
      <Group justify="space-between" wrap="nowrap" align="stretch" gap="md">
        {prec ? (
          <Anchor component={Link} to={`/reponse-1/${prec.slug}`} c="dimmed" fw={500} maw="48%">
            <Group gap={6} wrap="nowrap" align="flex-start">
              <IconArrowLeft size={16} style={{ marginTop: 3, flexShrink: 0 }} />
              <span>{prec.titre}</span>
            </Group>
          </Anchor>
        ) : (
          <span />
        )}
        {suiv ? (
          <Anchor
            component={Link}
            to={`/reponse-1/${suiv.slug}`}
            c="dimmed"
            fw={500}
            maw="48%"
            ta="right"
          >
            <Group gap={6} wrap="nowrap" align="flex-start" justify="flex-end">
              <span>{suiv.titre}</span>
              <IconArrowRight size={16} style={{ marginTop: 3, flexShrink: 0 }} />
            </Group>
          </Anchor>
        ) : (
          <span />
        )}
      </Group>
    </Stack>
  )
}
