import { Link } from 'react-router-dom'
import {
  Badge,
  Button,
  Paper,
  SimpleGrid,
  Stack,
  Text,
  Title,
} from '@mantine/core'
import { IconArrowRight } from '@tabler/icons-react'
import { fronts, strategieSections } from '../../data/defense'
import type { Analyse } from '../../data/analyses'
import AnalyseContent from '../../components/AnalyseContent'

function CarteFront({ f }: { f: Analyse }) {
  return (
    <Paper
      component={Link}
      to={`/defense/${f.slug}`}
      p={{ base: 'lg', sm: 'xl' }}
      radius="lg"
      h="100%"
      style={{ textDecoration: 'none', color: 'inherit', display: 'block' }}
    >
      <Stack gap="md" h="100%">
        <Text fw={700} size="sm" c="gold.7" tt="uppercase" style={{ letterSpacing: '0.12em' }}>
          {f.eyebrow}
        </Text>
        <Title order={2} fz={{ base: 22, sm: 26 }}>
          {f.titre}
        </Title>
        <Text c="dimmed">{f.resume}</Text>
        <SimpleGrid cols={2} spacing="md">
          {f.apercu.map((k) => (
            <div key={k.label}>
              <Text ff="heading" fz={26} fw={700} lh={1}>
                {k.valeur}
              </Text>
              <Text size="xs" c="dimmed" mt={4}>
                {k.label}
              </Text>
            </div>
          ))}
        </SimpleGrid>
        <Button
          variant="light"
          color="gold"
          radius="md"
          mt="auto"
          w="fit-content"
          rightSection={<IconArrowRight size={16} />}
          component="span"
        >
          En savoir plus
        </Button>
      </Stack>
    </Paper>
  )
}

export default function Defense() {
  return (
    <Stack gap={32}>
      <Stack gap="xs">
        <Text fw={700} size="sm" c="gold.7" tt="uppercase" style={{ letterSpacing: '0.12em' }}>
          Stratégie de défense
        </Text>
        <Title order={1} fz={{ base: 40, sm: 56 }} lh={1.05}>
          Défense
        </Title>
        <Text c="dimmed" size="lg" maw={720}>
          Les arguments opposables à la proposition de rectification, reliés aux
          preuves chiffrées et aux pièces du dossier.
        </Text>
      </Stack>

      {/* Stratégie + action urgente */}
      <AnalyseContent sections={strategieSections} />

      {/* Les fronts */}
      <Stack gap="xs">
        <Title order={2} fz={{ base: 20, sm: 24 }}>
          Les fronts de défense
        </Title>
        <Badge variant="light" color="gray" radius="sm" w="fit-content">
          {fronts.length} fronts
        </Badge>
      </Stack>
      <SimpleGrid cols={{ base: 1, md: 2 }} spacing="lg">
        {fronts.map((f) => (
          <CarteFront key={f.slug} f={f} />
        ))}
      </SimpleGrid>
    </Stack>
  )
}
