import { useState, type ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { BarChart } from '@mantine/charts'
import {
  Alert,
  Anchor,
  Badge,
  Box,
  Button,
  Divider,
  Group,
  Paper,
  SimpleGrid,
  Stack,
  Table,
  Text,
  Title,
} from '@mantine/core'
import {
  IconAlertTriangle,
  IconArrowRight,
  IconChartBar,
  IconChevronDown,
  IconCircleCheck,
  IconDownload,
  IconFileText,
  IconGavel,
  IconInfoCircle,
} from '@tabler/icons-react'
import type { ComposanteDetail, KpiItem, Section } from '../data/analyses'
import { fileUrl } from './PieceCards'
import { formatEuro, formatInt } from '../utils/format'

// Icône d'encart selon la couleur (info / alerte / validation / juridique).
function alerteIcon(couleur: string) {
  switch (couleur) {
    case 'red':
    case 'orange':
    case 'yellow':
      return <IconAlertTriangle size={18} />
    case 'teal':
    case 'green':
      return <IconCircleCheck size={18} />
    case 'gray':
      return <IconGavel size={18} />
    default:
      return <IconInfoCircle size={18} />
  }
}

// Emphase : transforme "texte **fort** texte" en JSX avec fragments en gras.
function richText(texte: string): ReactNode[] {
  return texte.split(/(\*\*[^*]+\*\*)/g).map((part, i) =>
    part.startsWith('**') && part.endsWith('**') ? (
      <Text key={i} span fw={700} c="gold.8">
        {part.slice(2, -2)}
      </Text>
    ) : (
      <Text key={i} span>
        {part}
      </Text>
    ),
  )
}

// Couleur de la cote d'attaquabilité (forte = favorable à la défense).
function coteColor(cote: string): string {
  const c = cote.toLowerCase()
  if (c.includes('faible')) return 'gray'
  if (c.includes('forte')) return 'teal'
  if (c.includes('modérée')) return 'yellow'
  return 'blue'
}

function Kpi({ item }: { item: KpiItem }) {
  const hl = item.highlight
  const couleur = item.couleur ?? 'blue'
  return (
    <Paper p="lg" radius="lg" h="100%" bg={hl ? couleur : undefined}>
      <Stack gap="md" h="100%" justify="space-between">
        <Text size="sm" lineClamp={2} c={hl ? 'white' : 'dimmed'}>
          {item.label}
        </Text>
        <div>
          <Text ff="heading" fz={32} fw={700} lh={1.05} c={hl ? 'white' : undefined}>
            {item.valeur}
          </Text>
          {item.sub && (
            <Text size="xs" mt={6} c={hl ? 'white' : 'dimmed'} opacity={hl ? 0.85 : 1}>
              {item.sub}
            </Text>
          )}
        </div>
      </Stack>
    </Paper>
  )
}

// Couleur / label de la source d'un poste de décomposition.
const decompColor = (s: string) => (s === 'fisc' ? 'red' : s === 'nous' ? 'teal' : 'gray')
const decompLabel = (s: string) =>
  s === 'fisc' ? 'Chiffré par le fisc' : s === 'nous' ? 'Vérifié par nous' : 'À confirmer (inventaire)'

// Justification détaillée d'un poste : méthode + tableau de données + sources.
function DetailTable({ d }: { d: ComposanteDetail }) {
  return (
    <Paper withBorder shadow="none" radius="md" p="md" mt="sm" bg="var(--mantine-color-gray-0)">
      <Stack gap="sm">
        <Text size="sm">{richText(d.methode)}</Text>
        <Table.ScrollContainer minWidth={560}>
          <Table verticalSpacing="xs" highlightOnHover withRowBorders>
            <Table.Thead>
              <Table.Tr>
                {d.colonnes.map((c, i) => (
                  <Table.Th key={i} ta={i === 0 ? 'left' : 'right'}>
                    <Text size="xs" tt="uppercase" c="dimmed" fw={600}>
                      {c}
                    </Text>
                  </Table.Th>
                ))}
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {d.lignes.map((ln, ri) => (
                <Table.Tr key={ri}>
                  {ln.map((cell, ci) => (
                    <Table.Td key={ci} ta={ci === 0 ? 'left' : 'right'}>
                      {cell}
                    </Table.Td>
                  ))}
                </Table.Tr>
              ))}
              <Table.Tr>
                <Table.Td fw={700} colSpan={Math.max(1, d.colonnes.length - 1)}>
                  {d.totalLabel}
                </Table.Td>
                <Table.Td ta="right" fw={700}>
                  {d.totalValeur}
                </Table.Td>
              </Table.Tr>
            </Table.Tbody>
          </Table>
        </Table.ScrollContainer>
        {d.note && (
          <Text size="xs" c="dimmed">
            {d.note}
          </Text>
        )}
        {d.sources.length > 0 && (
          <Group gap={6} align="center">
            <Text size="xs" tt="uppercase" c="dimmed" fw={600}>
              Sources
            </Text>
            {d.sources.map((s, i) => (
              <Badge key={i} variant="light" color="gray" radius="sm" size="sm">
                {s.label}
              </Badge>
            ))}
          </Group>
        )}
      </Stack>
    </Paper>
  )
}

// Décomposition : barre empilée + cartes ; chaque poste se déplie vers sa preuve.
function DecompositionView({ section }: { section: Extract<Section, { kind: 'decomposition' }> }) {
  const [open, setOpen] = useState<Record<string, boolean>>({})
  const toggle = (cle: string) => setOpen((o) => ({ ...o, [cle]: !o[cle] }))
  return (
    <Paper p={{ base: 'md', sm: 'lg' }} radius="lg">
      <Stack gap="lg">
        {/* Barre empilée : poids de chaque composante */}
        <div style={{ display: 'flex', height: 30, borderRadius: 8, overflow: 'hidden' }}>
          {section.items.map((it) => (
            <Box
              key={it.cle}
              title={`${it.label} - ${formatEuro(it.montantHT)}`}
              style={{
                width: `${(100 * it.montantHT) / section.total}%`,
                background: `var(--mantine-color-${decompColor(it.source)}-${it.source === 'attente' ? 3 : 5})`,
              }}
            />
          ))}
        </div>
        {/* Cartes des composantes, dépliables */}
        <Stack gap="lg">
          {section.items.map((it) => (
            <div key={it.cle}>
              <Group wrap="nowrap" align="flex-start" gap="md">
                <Box
                  w={12}
                  h={12}
                  mt={5}
                  style={{ borderRadius: 999, background: `var(--mantine-color-${decompColor(it.source)}-${it.source === 'attente' ? 3 : 6})`, flexShrink: 0 }}
                />
                <div style={{ flex: 1 }}>
                  <Group gap={8} wrap="nowrap" align="center">
                    <Text fw={700}>{it.label}</Text>
                    {it.plancher && (
                      <Badge size="xs" variant="light" color="gray" radius="sm">
                        plancher
                      </Badge>
                    )}
                  </Group>
                  <Text size="sm" c="dimmed" mt={2}>
                    {it.preuve}
                  </Text>
                  <Group gap="md" mt={4} wrap="nowrap">
                    <Text size="xs" c={decompColor(it.source) + '.7'} fw={600} tt="uppercase" style={{ letterSpacing: '0.04em' }}>
                      {decompLabel(it.source)}
                    </Text>
                    {it.detail && (
                      <Button
                        variant="subtle"
                        size="compact-xs"
                        color={decompColor(it.source)}
                        onClick={() => toggle(it.cle)}
                        rightSection={
                          <IconChevronDown
                            size={14}
                            style={{ transform: open[it.cle] ? 'rotate(180deg)' : 'none', transition: 'transform 150ms' }}
                          />
                        }
                      >
                        {open[it.cle] ? 'Masquer le détail' : 'Voir la justification détaillée'}
                      </Button>
                    )}
                  </Group>
                </div>
                <div style={{ textAlign: 'right', flexShrink: 0 }}>
                  <Text ff="heading" fw={700} fz={22}>
                    {Math.round((100 * it.montantHT) / section.total)} %
                  </Text>
                  <Text size="xs" c="dimmed">
                    {formatEuro(it.montantHT)} au coût
                  </Text>
                </div>
              </Group>
              {it.detail && open[it.cle] && <DetailTable d={it.detail} />}
            </div>
          ))}
        </Stack>
      </Stack>
    </Paper>
  )
}

// Carte argument (accusation / réponse), avec démonstration chiffrée dépliable.
function ArgumentView({ section }: { section: Extract<Section, { kind: 'argument' }> }) {
  const [open, setOpen] = useState(false)
  return (
    <Paper withBorder shadow="none" radius="md" p="lg" bg="var(--mantine-color-gray-0)">
      <Stack gap="sm">
        <Group justify="space-between" wrap="nowrap" align="flex-start" gap="sm">
          <Text fw={700}>{section.titre}</Text>
          <Badge variant="light" color={coteColor(section.cote)} radius="sm" style={{ flexShrink: 0 }}>
            {section.cote}
          </Badge>
        </Group>
        <div>
          <Text size="xs" tt="uppercase" c="dimmed" fw={600} mb={2}>
            Ce que dit l’administration{section.page ? ` · ${section.page}` : ''}
          </Text>
          <Text size="sm">{section.accusation}</Text>
        </div>
        <div>
          <Text size="xs" tt="uppercase" c="dimmed" fw={600} mb={2}>
            Notre réponse
          </Text>
          <Text size="sm">{richText(section.faille)}</Text>
        </div>
        {(section.preuves.length > 0 || section.pieces.length > 0 || section.detail) && (
          <Group gap="xs">
            {section.preuves.map((l) => (
              <Button
                key={l.to}
                component={Link}
                to={l.to}
                size="xs"
                variant="default"
                radius="md"
                leftSection={<IconChartBar size={13} color="var(--mantine-color-blue-6)" />}
                rightSection={<IconArrowRight size={13} />}
                styles={{ root: { fontWeight: 600 } }}
              >
                {l.label}
              </Button>
            ))}
            {section.pieces.map((l) => (
              <Button
                key={l.to}
                component={Link}
                to={l.to}
                size="xs"
                variant="default"
                radius="md"
                leftSection={<IconFileText size={13} color="var(--mantine-color-gold-7)" />}
                rightSection={<IconArrowRight size={13} />}
                styles={{ root: { fontWeight: 600 } }}
              >
                {l.label}
              </Button>
            ))}
            {section.detail && (
              <Button
                size="xs"
                variant="subtle"
                color="teal"
                radius="md"
                onClick={() => setOpen((o) => !o)}
                rightSection={
                  <IconChevronDown size={14} style={{ transform: open ? 'rotate(180deg)' : 'none', transition: 'transform 150ms' }} />
                }
              >
                {open ? 'Masquer la démonstration' : 'Voir la démonstration chiffrée'}
              </Button>
            )}
          </Group>
        )}
        {section.detail && open && <DetailTable d={section.detail} />}
      </Stack>
    </Paper>
  )
}

function SectionView({ section }: { section: Section }) {
  switch (section.kind) {
    case 'paragraphe':
      return <Text size="md">{richText(section.texte)}</Text>

    case 'alerte':
      return (
        <Alert
          color={section.couleur}
          variant="light"
          radius="lg"
          icon={alerteIcon(section.couleur)}
          title={section.titre}
          p="lg"
          styles={{
            root: {
              backgroundColor: `var(--mantine-color-${section.couleur}-0)`,
              border: `1px solid var(--mantine-color-${section.couleur}-3)`,
            },
            title: { fontSize: 'var(--mantine-font-size-sm)', letterSpacing: '0.02em' },
            message: {
              fontSize: 'var(--mantine-font-size-md)',
              lineHeight: 1.55,
              color: 'var(--mantine-color-dark-6)',
            },
            body: { gap: 8 },
          }}
        >
          {richText(section.texte)}
        </Alert>
      )

    case 'note':
      return (
        <Text size="xs" c="dimmed">
          {section.texte}
        </Text>
      )

    case 'chapitre': {
      const MAP = {
        fisc: { color: 'red', label: 'Le fisc' },
        nous: { color: 'teal', label: 'Notre analyse' },
        neutre: { color: 'gold', label: 'En clair' },
      } as const
      const c = MAP[section.source]
      const num = section.numero
      // Gros titre numéroté précédé d'une barre de séparation colorée (pas de carte pleine).
      return (
        <Stack gap="md" mt={{ base: 36, sm: 56 }} mb={4}>
          <Divider size="md" color={`${c.color}.5`} />
          <Group align="center" gap="lg" wrap="nowrap">
            {num != null && (
              <Text
                ff="heading"
                fz={{ base: 56, sm: 88 }}
                fw={800}
                c={`${c.color}.6`}
                lh={0.85}
                style={{ flexShrink: 0 }}
              >
                {num}.
              </Text>
            )}
            <Stack gap={6}>
              <Badge
                color={c.color}
                variant="light"
                radius="sm"
                size="md"
                tt="uppercase"
                style={{ alignSelf: 'flex-start', fontWeight: 800, letterSpacing: '0.08em' }}
              >
                {c.label}
              </Badge>
              <Title order={2} ff="heading" fz={{ base: 27, sm: 40 }} lh={1.05}>
                {section.titre}
              </Title>
              {section.sousTitre && (
                <Text size="md" c="dimmed">
                  {section.sousTitre}
                </Text>
              )}
            </Stack>
          </Group>
        </Stack>
      )
    }

    case 'decomposition':
      return <DecompositionView section={section} />

    case 'argument':
      return <ArgumentView section={section} />

    case 'sources':
      return (
        <Stack gap={8}>
          <Text size="xs" tt="uppercase" c="dimmed" fw={600}>
            Sources - pièces du dossier
          </Text>
          {section.items.map((it) => (
            <Anchor key={it.slug} component={Link} to={`/documents/${it.slug}`} fw={500}>
              <Group gap={6} wrap="nowrap">
                <IconFileText size={15} />
                {it.label}
                <IconArrowRight size={14} />
              </Group>
            </Anchor>
          ))}
        </Stack>
      )

    case 'piecejointe':
      return (
        <Paper
          p={{ base: 'md', sm: 'lg' }}
          radius="lg"
          withBorder
          style={{ borderColor: 'var(--mantine-color-teal-4)', backgroundColor: 'var(--mantine-color-teal-0)' }}
        >
          <Stack gap="sm">
            <Text size="xs" tt="uppercase" c="teal.8" fw={700}>
              Données détaillées (téléchargement)
            </Text>
            {section.intro && (
              <Text size="sm" c="dimmed">
                {section.intro}
              </Text>
            )}
            <Group gap="sm">
              {section.fichiers.map((f) => (
                <Button
                  key={f.fichier}
                  component="a"
                  href={fileUrl(f.fichier)}
                  download
                  variant="light"
                  color="teal"
                  radius="md"
                  size="sm"
                  leftSection={<IconDownload size={16} />}
                >
                  {f.label}
                </Button>
              ))}
            </Group>
          </Stack>
        </Paper>
      )

    case 'kpis':
      return (
        <SimpleGrid cols={{ base: 2, md: Math.min(section.items.length, 4) }} spacing="lg">
          {section.items.map((it) => (
            <Kpi key={it.label} item={it} />
          ))}
        </SimpleGrid>
      )

    case 'tableau':
      return (
        <Paper p={{ base: 'md', sm: 'lg' }} radius="lg">
          <Stack gap="sm">
            {section.titre && (
              <Title order={3} fz={{ base: 18, sm: 22 }}>
                {section.titre}
              </Title>
            )}
            <Table.ScrollContainer minWidth={section.minWidth ?? 480}>
              <Table verticalSpacing="sm" highlightOnHover withRowBorders>
              <Table.Thead>
                <Table.Tr>
                  {section.colonnes.map((col) => (
                    <Table.Th key={col.label} ta={col.align ?? 'left'}>
                      <Text size="xs" tt="uppercase" c="dimmed" fw={600}>
                        {col.label}
                      </Text>
                    </Table.Th>
                  ))}
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {section.lignes.map((ligne, ri) => (
                  <Table.Tr key={ri}>
                    {ligne.map((cell, ci) => (
                      <Table.Td key={ci} ta={cell.align ?? 'left'} fw={cell.fw}>
                        {cell.badge ? (
                          <Badge color={cell.badge === 'ok' ? 'teal' : 'red'} variant="light" radius="sm">
                            {cell.v}
                          </Badge>
                        ) : (
                          cell.v
                        )}
                      </Table.Td>
                    ))}
                  </Table.Tr>
                ))}
              </Table.Tbody>
              </Table>
            </Table.ScrollContainer>
          </Stack>
        </Paper>
      )

    case 'graphique':
      return (
        <Paper p={{ base: 'md', sm: 'lg' }} radius="lg">
          <BarChart
            h={section.hauteur}
            data={section.data}
            dataKey={section.dataKey}
            orientation={section.variante === 'horizontal' ? 'vertical' : 'horizontal'}
            series={[{ name: section.serie.name, color: section.serie.couleur }]}
            valueFormatter={(v) => (section.format === 'euro' ? formatEuro(v) : formatInt(v))}
            barProps={{ radius: section.variante === 'horizontal' ? 6 : 4 }}
            tickLine={section.variante === 'horizontal' ? 'none' : 'y'}
            gridAxis={section.variante === 'horizontal' ? 'x' : 'y'}
          />
        </Paper>
      )

    default:
      return null
  }
}

// Rend la suite des sections d'une analyse.
export default function AnalyseContent({ sections }: { sections: Section[] }) {
  return (
    <Stack gap="lg">
      {sections.map((section, i) => (
        <SectionView key={i} section={section} />
      ))}
    </Stack>
  )
}
