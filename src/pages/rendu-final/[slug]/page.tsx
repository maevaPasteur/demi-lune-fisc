import { Link, useParams } from 'react-router-dom'
import { Anchor, Box, Button, Group, Stack, Text, Title } from '@mantine/core'
import { IconArrowLeft, IconHome } from '@tabler/icons-react'
import { griefParSlug, blocs } from '../../../data/renduFinal'
import AnalyseContent from '../../../components/AnalyseContent'

function RetourLien() {
  return (
    <Anchor component={Link} to="/rendu-final" c="dimmed" fw={500}>
      <Group gap={6} wrap="nowrap">
        <IconArrowLeft size={16} />
        Tout le rendu final
      </Group>
    </Anchor>
  )
}

// Route : /rendu-final/:slug - réponse détaillée à un grief du fisc.
export default function GriefDetail() {
  const { slug } = useParams()
  const grief = slug ? griefParSlug(slug) : undefined

  if (!grief) {
    return (
      <Stack gap="lg">
        <RetourLien />
        <Title order={1} fz={{ base: 32, sm: 44 }}>
          Grief introuvable
        </Title>
        <Text c="dimmed">Aucun grief ne correspond à « {slug} ».</Text>
        <Button component={Link} to="/rendu-final" radius="md" w="fit-content">
          Retour au rendu final
        </Button>
      </Stack>
    )
  }

  const bloc = blocs.find((b) => b.id === grief.bloc)

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
          {grief.titre}
        </Title>
        <Text size="xs" c="dimmed">
          {grief.refRapport}
          {grief.enjeu ? ` · Enjeu : ${grief.enjeu}` : ''}
        </Text>

        {/* Rappel du grief + verdict, avant le détail. */}
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
            <IconHome size={15} color="var(--mantine-color-red-7)" />
            <Text size="xs" tt="uppercase" fw={700} c="red.7" style={{ letterSpacing: '0.06em' }}>
              Ce que dit le fisc
            </Text>
          </Group>
          <Text size="sm" c="red.9">
            {grief.griefFisc}
          </Text>
        </Box>
        <Text fw={600} size="lg" maw={820}>
          {grief.reponseCourte}
        </Text>
      </Stack>

      <AnalyseContent sections={grief.sections} />
    </Stack>
  )
}
