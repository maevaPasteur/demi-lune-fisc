import { Link, useParams } from 'react-router-dom'
import { Anchor, Badge, Button, Group, Stack, Text, Title } from '@mantine/core'
import { IconArrowLeft } from '@tabler/icons-react'
import { frontParSlug } from '../../../data/defense'
import AnalyseContent from '../../../components/AnalyseContent'

function RetourLien() {
  return (
    <Anchor component={Link} to="/defense" c="dimmed" fw={500}>
      <Group gap={6} wrap="nowrap">
        <IconArrowLeft size={16} />
        Toute la défense
      </Group>
    </Anchor>
  )
}

// Route : /defense/:slug - page détail d'un front de défense.
export default function FrontDetail() {
  const { slug } = useParams()
  const front = slug ? frontParSlug(slug) : undefined

  if (!front) {
    return (
      <Stack gap="lg">
        <RetourLien />
        <Title order={1} fz={{ base: 32, sm: 44 }}>
          Front introuvable
        </Title>
        <Text c="dimmed">Aucun front ne correspond à « {slug} ».</Text>
        <Button component={Link} to="/defense" radius="md" w="fit-content">
          Retour à la défense
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
            {front.eyebrow}
          </Text>
          <Badge variant="light" color="teal" radius="sm">
            {front.force}
          </Badge>
        </Group>
        <Title order={1} fz={{ base: 34, sm: 50 }} lh={1.05}>
          {front.titre}
        </Title>
        <Text c="dimmed" size="lg" maw={760}>
          {front.resume}
        </Text>
      </Stack>

      <AnalyseContent sections={front.sections} />
    </Stack>
  )
}
