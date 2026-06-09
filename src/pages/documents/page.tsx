import { useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Accordion,
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
  IconClipboardList,
  IconDownload,
  IconEye,
  IconFileText,
  IconGlassFull,
  IconNotebook,
  IconReceipt2,
} from '@tabler/icons-react'
import {
  documents,
  groupes,
  rapports,
  piecesDefense,
  source,
  carnetManuscrit,
  RAPPORTS_SLUG,
  SOURCE_SLUG,
  CARTES_SLUG,
  FACTURES_SLUG,
  MANUSCRIT_SLUG,
  INVENTAIRES_SLUG,
  type Document,
  type GroupeAnnexe,
} from '../../data/documents'
import {
  ApercuModal,
  DocCard,
  NiveauBadge,
  RapportCard,
  fileUrl,
} from '../../components/PieceCards'
import { cartes, facturesParAnnee, inventaires } from '../../data/bibliothequePdf'
import SectionNav, {
  SCROLL_OFFSET,
  type Section,
} from '../../components/SectionNav'

// Identifiants d'ancre des sections (partagés par le sommaire et le contenu).
const ID_RAPPORT = 'rapport-finances-publiques'
const ID_PIECES_DEFENSE = 'pieces-defense'
const ID_CARTES = 'carte-des-vins'
const ID_FACTURES = 'factures-fournisseur'
const ID_MANUSCRIT = 'carnet-manuscrit'
const ID_INVENTAIRES = 'inventaires'
const ID_SOURCE = 'source-brute'
const annexeId = (slug: string) => `annexe-${slug}`

// Liste des sections pour le sommaire d'ancres.
const sections: Section[] = [
  { id: ID_RAPPORT, label: 'Rapport des Finances Publiques' },
  { id: ID_PIECES_DEFENSE, label: 'Pièces de défense (analyses)' },
  ...groupes.map((g) => ({ id: annexeId(g.slug), label: `Annexe ${g.lettre}` })),
  { id: ID_CARTES, label: 'Carte des vins' },
  { id: ID_FACTURES, label: 'Factures fournisseur' },
  { id: ID_INVENTAIRES, label: 'Inventaires' },
  { id: ID_MANUSCRIT, label: 'Carnet manuscrit' },
  { id: ID_SOURCE, label: 'Source brute' },
]

// Statistiques d'en-tête, dérivées des données (jamais saisies en dur).
const stats = [
  { value: String(groupes.length), label: 'Annexes' },
  { value: String(documents.length), label: 'Fichiers' },
  { value: String(groupes[0]?.documents.length ?? 0), label: 'Exercices' },
  { value: '1', label: 'Source brute' },
]

// Lien « Voir le détail → » vers une page détail.
function DetailLink({ to }: { to: string }) {
  return (
    <Anchor
      component={Link}
      to={to}
      fw={600}
      c="gold.7"
      visibleFrom="xs"
      style={{ whiteSpace: 'nowrap' }}
    >
      <Group gap={6} wrap="nowrap">
        Voir le détail
        <IconArrowRight size={16} />
      </Group>
    </Anchor>
  )
}

// Carré-badge contenant la lettre de l'annexe (ou une icône).
function Pastille({ children, gold = true }: { children: React.ReactNode; gold?: boolean }) {
  return (
    <Box
      w={48}
      h={48}
      style={{
        borderRadius: 12,
        background: gold
          ? 'var(--mantine-color-gold-1)'
          : 'var(--mantine-color-gray-1)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0,
      }}
    >
      {children}
    </Box>
  )
}

// --- Bloc d'une annexe (A…H), cliquable vers sa page détail -------------------
function BlocAnnexe({
  groupe,
  onApercu,
}: {
  groupe: GroupeAnnexe
  onApercu: (d: Document) => void
}) {
  const to = `/documents/${groupe.slug}`
  return (
    <Paper
      id={annexeId(groupe.slug)}
      p={{ base: 'lg', sm: 'xl' }}
      radius="lg"
      style={{ scrollMarginTop: SCROLL_OFFSET }}
    >
      <Stack gap="lg">
        <Group justify="space-between" align="center" wrap="nowrap">
          <Group gap="md" wrap="nowrap" align="center">
            <Pastille>
              <Text ff="heading" fz={24} fw={700} c="gold.8">
                {groupe.lettre}
              </Text>
            </Pastille>
            <Anchor
              component={Link}
              to={to}
              underline="never"
              c="inherit"
            >
              <Title order={2} fz={{ base: 22, sm: 26 }}>
                {groupe.titre}
              </Title>
            </Anchor>
          </Group>
          <DetailLink to={to} />
        </Group>

        <Text c="dimmed" maw={760}>
          {groupe.description}
        </Text>

        <NiveauBadge niveau={groupe.niveau} />

        <SimpleGrid cols={{ base: 1, md: 3 }} spacing="md">
          {groupe.documents.map((d) => (
            <DocCard key={d.id} doc={d} onApercu={onApercu} />
          ))}
        </SimpleGrid>
      </Stack>
    </Paper>
  )
}

// --- Section « Carte des vins » (PDF) ----------------------------------------
function SectionCartes() {
  return (
    <Paper id={ID_CARTES} p={{ base: 'lg', sm: 'xl' }} radius="lg" style={{ scrollMarginTop: SCROLL_OFFSET }}>
      <Stack gap="lg">
        <Group justify="space-between" align="center" wrap="nowrap">
          <Group gap="md" wrap="nowrap" align="center">
            <Pastille>
              <IconGlassFull size={24} color="var(--mantine-color-gold-8)" />
            </Pastille>
            <Title order={2} fz={{ base: 22, sm: 26 }}>
              Carte des vins
            </Title>
          </Group>
          <DetailLink to={`/documents/${CARTES_SLUG}`} />
        </Group>
        <Text c="dimmed" maw={760}>
          Cartes des vins & boissons du restaurant, au format PDF.
        </Text>
        <NiveauBadge niveau="Document PDF" />
        <SimpleGrid cols={{ base: 1, md: 3 }} spacing="md">
          {cartes.map((c) => (
            <RapportCard key={c.fichier} doc={c as unknown as Document} />
          ))}
        </SimpleGrid>
      </Stack>
    </Paper>
  )
}

// --- Section « Factures fournisseur » (accordéon par année) ------------------
function SectionFactures() {
  const total = facturesParAnnee.reduce((a, y) => a + y.nb, 0)
  return (
    <Paper id={ID_FACTURES} p={{ base: 'lg', sm: 'xl' }} radius="lg" style={{ scrollMarginTop: SCROLL_OFFSET }}>
      <Stack gap="lg">
        <Group justify="space-between" align="center" wrap="nowrap">
          <Group gap="md" wrap="nowrap" align="center">
            <Pastille>
              <IconReceipt2 size={24} color="var(--mantine-color-gold-8)" />
            </Pastille>
            <Title order={2} fz={{ base: 22, sm: 26 }}>
              Factures fournisseur
            </Title>
          </Group>
          <DetailLink to={`/documents/${FACTURES_SLUG}`} />
        </Group>
        <Text c="dimmed" maw={760}>
          Factures Franche-Comté Boissons par exercice, au format PDF
          ({total} pièces). Cliquer ouvre le PDF dans un nouvel onglet.
        </Text>
        <Accordion variant="separated" radius="md" chevronPosition="left">
          {facturesParAnnee.map((y) => (
            <Accordion.Item key={y.annee} value={y.annee}>
              <Accordion.Control>
                <Group justify="space-between" pr="md" wrap="nowrap">
                  <Text fw={600}>Exercice {y.annee}</Text>
                  <Badge variant="light" color="gold" radius="sm">
                    {y.nb} pièces
                  </Badge>
                </Group>
              </Accordion.Control>
              <Accordion.Panel>
                <Group gap="xs">
                  {y.pieces.map((p) => (
                    <Button
                      key={p.fichier}
                      component="a"
                      href={fileUrl(p.fichier)}
                      target="_blank"
                      rel="noopener noreferrer"
                      title={p.label}
                      variant={p.type === 'releve' ? 'light' : 'default'}
                      color={p.type === 'releve' ? 'gold' : 'gray'}
                      size="xs"
                      radius="xl"
                      leftSection={<IconFileText size={14} />}
                    >
                      {p.label.replace(/^Facture\s/, '')}
                    </Button>
                  ))}
                </Group>
              </Accordion.Panel>
            </Accordion.Item>
          ))}
        </Accordion>
      </Stack>
    </Paper>
  )
}

// --- Section « Carnet manuscrit » (XLS, aperçu) ------------------------------
function SectionManuscrit({ onApercu }: { onApercu: (d: Document) => void }) {
  return (
    <Paper id={ID_MANUSCRIT} p={{ base: 'lg', sm: 'xl' }} radius="lg" style={{ scrollMarginTop: SCROLL_OFFSET }}>
      <Stack gap="lg">
        <Group justify="space-between" align="center" wrap="nowrap">
          <Group gap="md" wrap="nowrap" align="center">
            <Pastille>
              <IconNotebook size={24} color="var(--mantine-color-gold-8)" />
            </Pastille>
            <Anchor component={Link} to={`/documents/${MANUSCRIT_SLUG}`} underline="never" c="inherit">
              <Title order={2} fz={{ base: 22, sm: 26 }}>
                Carnet manuscrit - anomalies boissons
              </Title>
            </Anchor>
          </Group>
          <DetailLink to={`/documents/${MANUSCRIT_SLUG}`} />
        </Group>
        <Text c="dimmed" maw={760}>
          {carnetManuscrit.description}
        </Text>
        <NiveauBadge niveau={carnetManuscrit.niveau} />
        <SimpleGrid cols={{ base: 1, md: 3 }} spacing="md">
          <DocCard doc={carnetManuscrit} onApercu={onApercu} />
        </SimpleGrid>
      </Stack>
    </Paper>
  )
}

// --- Section « Inventaires » (PDF scanné + CSV d'extraction boissons) --------
function SectionInventaires() {
  return (
    <Paper id={ID_INVENTAIRES} p={{ base: 'lg', sm: 'xl' }} radius="lg" style={{ scrollMarginTop: SCROLL_OFFSET }}>
      <Stack gap="lg">
        <Group justify="space-between" align="center" wrap="nowrap">
          <Group gap="md" wrap="nowrap" align="center">
            <Pastille>
              <IconClipboardList size={24} color="var(--mantine-color-gold-8)" />
            </Pastille>
            <Title order={2} fz={{ base: 22, sm: 26 }}>
              Inventaires
            </Title>
          </Group>
          <DetailLink to={`/documents/${INVENTAIRES_SLUG}`} />
        </Group>
        <Text c="dimmed" maw={760}>
          Inventaires physiques au 31/03 : scan d'origine (PDF) et extraction des
          boissons & alcools (CSV : produit, quantité, prix, valeur HT).
        </Text>
        <NiveauBadge niveau="Document PDF" />
        <SimpleGrid cols={{ base: 1, md: 3 }} spacing="md">
          {inventaires.map((inv) => (
            <Paper key={inv.annee} withBorder shadow="none" radius="lg" p="lg" bg="var(--mantine-color-gray-0)">
              <Stack gap="md" h="100%" justify="space-between">
                <Group justify="space-between" align="center" wrap="nowrap">
                  <Text fw={700}>Inventaire 31/03/{inv.annee}</Text>
                  <Badge variant="outline" color="gray" radius="sm" size="sm">
                    PDF + CSV
                  </Badge>
                </Group>
                <Group gap="sm" wrap="nowrap">
                  {inv.pdf && (
                    <Button
                      component="a"
                      href={fileUrl(inv.pdf)}
                      target="_blank"
                      rel="noopener noreferrer"
                      variant="default"
                      radius="md"
                      size="sm"
                      style={{ flex: 1 }}
                      leftSection={<IconEye size={16} />}
                    >
                      Scan PDF
                    </Button>
                  )}
                  {inv.csv && (
                    <Button
                      component="a"
                      href={fileUrl(inv.csv)}
                      download
                      variant="gradient"
                      gradient={{ from: 'gold.4', to: 'gold.6', deg: 160 }}
                      radius="md"
                      size="sm"
                      style={{ flex: 1, color: 'var(--mantine-color-gold-9)' }}
                      leftSection={<IconDownload size={16} />}
                    >
                      CSV boissons
                    </Button>
                  )}
                </Group>
              </Stack>
            </Paper>
          ))}
        </SimpleGrid>
      </Stack>
    </Paper>
  )
}

// --- Section « Pièces de défense » (analyses chiffrées, XLSX) ----------------
function SectionPiecesDefense() {
  return (
    <Paper
      id={ID_PIECES_DEFENSE}
      p={{ base: 'lg', sm: 'xl' }}
      radius="lg"
      withBorder
      style={{
        scrollMarginTop: SCROLL_OFFSET,
        borderColor: 'var(--mantine-color-teal-4)',
      }}
    >
      <Stack gap="lg">
        <Group gap="md" wrap="nowrap" align="center">
          <Pastille gold={false}>
            <IconClipboardList size={24} color="var(--mantine-color-teal-7)" />
          </Pastille>
          <Title order={2} fz={{ base: 22, sm: 26 }}>
            Pièces de défense - analyses chiffrées
          </Title>
        </Group>
        <Text c="dimmed" maw={760}>
          Analyses produites pour l'avocat et le fisc. Chaque chiffre est sourcé
          et reproductible à partir des annexes certifiées (A, B, E, H).
          Classeurs au format tableur.
        </Text>
        <NiveauBadge niveau="Analyse chiffrée" color="teal" />
        <SimpleGrid cols={{ base: 1, md: 2 }} spacing="md">
          {piecesDefense.map((d) => (
            <Paper
              key={d.id}
              withBorder
              shadow="none"
              radius="lg"
              p="lg"
              bg="var(--mantine-color-gray-0)"
            >
              <Stack gap="md" h="100%" justify="space-between">
                <Stack gap={6}>
                  <Group justify="space-between" align="flex-start" wrap="nowrap">
                    <Text fw={700}>{d.titre}</Text>
                    <Badge variant="light" color="teal" radius="sm" size="sm">
                      {d.niveau}
                    </Badge>
                  </Group>
                  <Text size="sm" c="dimmed">
                    {d.description}
                  </Text>
                </Stack>
                <Button
                  component="a"
                  href={fileUrl(d.fichier)}
                  download
                  variant="gradient"
                  gradient={{ from: 'teal.5', to: 'teal.7', deg: 160 }}
                  radius="md"
                  size="sm"
                  leftSection={<IconDownload size={16} />}
                >
                  Télécharger le classeur
                </Button>
              </Stack>
            </Paper>
          ))}
        </SimpleGrid>
      </Stack>
    </Paper>
  )
}

// --- Page ---------------------------------------------------------------------
export default function Documents() {
  const [apercu, setApercu] = useState<Document | null>(null)

  return (
    <Stack gap={32}>
      {/* En-tête */}
      <Stack gap="xs">
        <Text
          fw={700}
          size="sm"
          c="gold.7"
          tt="uppercase"
          style={{ letterSpacing: '0.12em' }}
        >
          Bibliothèque des annexes
        </Text>
        <Title order={1} fz={{ base: 40, sm: 56 }} lh={1.05}>
          Pièces du dossier
        </Title>
        <Text c="dimmed" size="lg" maw={680}>
          Annexes comptables des exercices 2022-2023 à 2024-2025. Aperçu et
          téléchargement de chaque pièce, au format tableur.
        </Text>
      </Stack>

      {/* Sommaire d'ancres (collant, scroll-spy) */}
      <SectionNav sections={sections} />

      {/* Statistiques */}
      <SimpleGrid cols={{ base: 2, sm: 4 }} spacing="md">
        {stats.map((s) => (
          <Paper key={s.label} p="lg" radius="lg">
            <Text ff="heading" fz={34} fw={700} lh={1}>
              {s.value}
            </Text>
            <Text size="sm" c="dimmed" mt={6}>
              {s.label}
            </Text>
          </Paper>
        ))}
      </SimpleGrid>

      {/* Rapport des Finances Publiques (PDF) - pièce maîtresse, en premier */}
      <Paper
        id={ID_RAPPORT}
        p={{ base: 'lg', sm: 'xl' }}
        radius="lg"
        style={{ scrollMarginTop: SCROLL_OFFSET }}
      >
        <Stack gap="lg">
          <Group justify="space-between" align="center" wrap="nowrap">
            <Group gap="md" wrap="nowrap" align="center">
              <Pastille>
                <IconFileText size={24} color="var(--mantine-color-gold-8)" />
              </Pastille>
              <Title order={2} fz={{ base: 22, sm: 26 }}>
                Rapport des Finances Publiques
              </Title>
            </Group>
            <DetailLink to={`/documents/${RAPPORTS_SLUG}`} />
          </Group>
          <Text c="dimmed" maw={760}>
            Réponses à la proposition de rectification et leurs annexes, au
            format PDF.
          </Text>
          <NiveauBadge niveau="Document PDF" />
          <SimpleGrid cols={{ base: 1, md: 2 }} spacing="md">
            {rapports.map((r) => (
              <RapportCard key={r.id} doc={r} />
            ))}
          </SimpleGrid>
        </Stack>
      </Paper>

      {/* Pièces de défense - analyses chiffrées (XLSX) */}
      <SectionPiecesDefense />

      {/* Blocs d'annexes */}
      <Stack gap="lg">
        {groupes.map((g) => (
          <BlocAnnexe key={g.lettre} groupe={g} onApercu={setApercu} />
        ))}
      </Stack>

      {/* Carte des vins (PDF) */}
      <SectionCartes />

      {/* Factures fournisseur par année (PDF) */}
      <SectionFactures />

      {/* Inventaires (PDF + CSV) */}
      <SectionInventaires />

      {/* Carnet manuscrit (XLS) */}
      <SectionManuscrit onApercu={setApercu} />

      {/* Fichier source brut */}
      <Paper
        id={ID_SOURCE}
        p={{ base: 'lg', sm: 'xl' }}
        radius="lg"
        style={{ scrollMarginTop: SCROLL_OFFSET }}
      >
        <Stack gap="lg">
          <Group justify="space-between" align="center" wrap="nowrap">
            <Group gap="md" wrap="nowrap" align="center">
              <Pastille gold={false}>
                <Text ff="heading" fz={16} fw={700} c="gray.7">
                  SRC
                </Text>
              </Pastille>
              <Title order={2} fz={{ base: 22, sm: 26 }}>
                {source.titre}
              </Title>
            </Group>
            <DetailLink to={`/documents/${SOURCE_SLUG}`} />
          </Group>
          <Text c="dimmed" maw={760}>
            {source.description}
          </Text>
          <NiveauBadge niveau={source.niveau} color="gray" />
          <SimpleGrid cols={{ base: 1, md: 3 }} spacing="md">
            <DocCard doc={source} onApercu={setApercu} />
          </SimpleGrid>
        </Stack>
      </Paper>

      <ApercuModal doc={apercu} onClose={() => setApercu(null)} />
    </Stack>
  )
}
