import { Link, useParams } from 'react-router-dom'
import { Anchor, Badge, Button, Group, Stack, Text, Title } from '@mantine/core'
import { IconArrowLeft } from '@tabler/icons-react'
import { analyseParSlug } from '../../../data/analyses'
import AnalyseContent from '../../../components/AnalyseContent'

function RetourLien() {
  return (
    <Anchor component={Link} to="/analyses" c="dimmed" fw={500}>
      <Group gap={6} wrap="nowrap">
        <IconArrowLeft size={16} />
        Toutes les analyses
      </Group>
    </Anchor>
  )
}

// Route : /analyses/:slug - page détail d'une analyse, rendue depuis les données.
export default function AnalyseDetail() {
  const { slug } = useParams()
  const analyse = slug ? analyseParSlug(slug) : undefined

  if (!analyse) {
    return (
      <Stack gap="lg">
        <RetourLien />
        <Title order={1} fz={{ base: 32, sm: 44 }}>
          Analyse introuvable
        </Title>
        <Text c="dimmed">Aucune analyse ne correspond à « {slug} ».</Text>
        <Button component={Link} to="/analyses" radius="md" w="fit-content">
          Retour aux analyses
        </Button>
      </Stack>
    )
  }

  return (
    <Stack gap={32}>
      <RetourLien />
      <Stack gap="xs">
        <Group gap="sm">
          <Text fw={700} size="sm" c="gold.7" tt="uppercase" style={{ letterSpacing: '0.12em' }}>
            {analyse.eyebrow}
          </Text>
          <Badge variant="light" color={analyse.force === 'forte' ? 'teal' : 'gray'} radius="sm">
            {analyse.force}
          </Badge>
        </Group>
        <Title order={1} fz={{ base: 34, sm: 50 }} lh={1.05}>
          {analyse.titre}
        </Title>
        <Text c="dimmed" size="lg" maw={760}>
          {analyse.resume}
        </Text>
      </Stack>

      <AnalyseContent sections={analyse.sections} />
    </Stack>
  )
}
