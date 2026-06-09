import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import {
  Accordion,
  Anchor,
  Badge,
  Button,
  Divider,
  Group,
  Paper,
  SimpleGrid,
  Stack,
  Text,
  Title,
} from '@mantine/core'
import { IconArrowLeft, IconDownload, IconEye, IconFileText } from '@tabler/icons-react'
import {
  groupeParSlug,
  rapports,
  source,
  carnetManuscrit,
  RAPPORTS_SLUG,
  SOURCE_SLUG,
  CARTES_SLUG,
  FACTURES_SLUG,
  MANUSCRIT_SLUG,
  INVENTAIRES_SLUG,
  type Document,
} from '../../../data/documents'
import {
  ApercuModal,
  DocCard,
  NiveauBadge,
  RapportCard,
  fileUrl,
} from '../../../components/PieceCards'
import { cartes, facturesParAnnee, inventaires } from '../../../data/bibliothequePdf'

// Lien de retour vers la liste des pièces.
function RetourLien() {
  return (
    <Anchor component={Link} to="/documents" c="dimmed" fw={500}>
      <Group gap={6} wrap="nowrap">
        <IconArrowLeft size={16} />
        Toutes les pièces
      </Group>
    </Anchor>
  )
}

// Une ligne de métadonnée (clé / valeur).
function Meta({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <Text
        size="xs"
        tt="uppercase"
        c="dimmed"
        fw={600}
        style={{ letterSpacing: '0.06em' }}
      >
        {label}
      </Text>
      <Text fw={600} mt={4}>
        {value}
      </Text>
    </div>
  )
}

// En-tête commun (eyebrow + titre + description + badge de niveau).
function EnTete({
  eyebrow,
  titre,
  description,
  niveau,
  niveauColor,
}: {
  eyebrow: string
  titre: string
  description: string
  niveau: string
  niveauColor?: string
}) {
  return (
    <Stack gap="xs">
      <Text
        fw={700}
        size="sm"
        c="gold.7"
        tt="uppercase"
        style={{ letterSpacing: '0.12em' }}
      >
        {eyebrow}
      </Text>
      <Title order={1} fz={{ base: 36, sm: 52 }} lh={1.05}>
        {titre}
      </Title>
      <Text c="dimmed" size="lg" maw={760}>
        {description}
      </Text>
      <Group mt="xs">
        <NiveauBadge niveau={niveau} color={niveauColor} />
      </Group>
    </Stack>
  )
}

function FicheMeta({ items }: { items: { label: string; value: string }[] }) {
  return (
    <Paper p={{ base: 'lg', sm: 'xl' }} radius="lg">
      <SimpleGrid cols={{ base: 2, sm: items.length }} spacing="lg">
        {items.map((m) => (
          <Meta key={m.label} label={m.label} value={m.value} />
        ))}
      </SimpleGrid>
    </Paper>
  )
}

function SectionFichiers({
  titre,
  children,
}: {
  titre: string
  children: React.ReactNode
}) {
  return (
    <Stack gap="md">
      <Title order={2} fz={{ base: 20, sm: 24 }}>
        {titre}
      </Title>
      <Divider />
      {children}
    </Stack>
  )
}

// --- Page détail dynamique (template) ----------------------------------------
// Route : /documents/:slug - gère les annexes, le rapport et la source.
export default function DocumentDetail() {
  const { slug } = useParams()
  const [apercu, setApercu] = useState<Document | null>(null)

  const groupe = slug ? groupeParSlug(slug) : undefined

  // 1) Rapport des Finances Publiques (PDF)
  if (slug === RAPPORTS_SLUG) {
    return (
      <Stack gap={32}>
        <RetourLien />
        <EnTete
          eyebrow="Pièce maîtresse"
          titre="Rapport des Finances Publiques"
          description="Réponses à la proposition de rectification et leurs annexes, au format PDF."
          niveau="Document PDF"
        />
        <FicheMeta
          items={[
            { label: 'Documents', value: String(rapports.length) },
            { label: 'Format', value: 'PDF' },
            { label: 'Période', value: '2022 → 2025' },
          ]}
        />
        <SectionFichiers titre="Documents">
          <SimpleGrid cols={{ base: 1, md: 2 }} spacing="md">
            {rapports.map((r) => (
              <RapportCard key={r.id} doc={r} />
            ))}
          </SimpleGrid>
        </SectionFichiers>
      </Stack>
    )
  }

  // 2) Export brut des règlements (source)
  if (slug === SOURCE_SLUG) {
    return (
      <Stack gap={32}>
        <RetourLien />
        <EnTete
          eyebrow="Source"
          titre={source.titre}
          description={source.description}
          niveau={source.niveau}
          niveauColor="gray"
        />
        <FicheMeta
          items={[
            { label: 'Format', value: source.format },
            { label: 'Période', value: '2022 → 2025' },
            { label: 'Niveau', value: source.niveau },
          ]}
        />
        <SectionFichiers titre="Fichier">
          <SimpleGrid cols={{ base: 1, md: 3 }} spacing="md">
            <DocCard doc={source} onApercu={setApercu} />
          </SimpleGrid>
        </SectionFichiers>
        <ApercuModal doc={apercu} onClose={() => setApercu(null)} />
      </Stack>
    )
  }

  // 3) Carte des vins (PDF)
  if (slug === CARTES_SLUG) {
    return (
      <Stack gap={32}>
        <RetourLien />
        <EnTete
          eyebrow="Restaurant"
          titre="Carte des vins"
          description="Cartes des vins & boissons du restaurant, au format PDF (historique des versions)."
          niveau="Document PDF"
        />
        <FicheMeta
          items={[
            { label: 'Cartes', value: String(cartes.length) },
            { label: 'Format', value: 'PDF' },
            { label: 'Période', value: '2021 → 2023' },
          ]}
        />
        <SectionFichiers titre="Cartes disponibles">
          <SimpleGrid cols={{ base: 1, md: 3 }} spacing="md">
            {cartes.map((c) => (
              <RapportCard key={c.fichier} doc={c as unknown as Document} />
            ))}
          </SimpleGrid>
        </SectionFichiers>
      </Stack>
    )
  }

  // 4) Factures fournisseur (PDF, par exercice)
  if (slug === FACTURES_SLUG) {
    const total = facturesParAnnee.reduce((a, y) => a + y.nb, 0)
    return (
      <Stack gap={32}>
        <RetourLien />
        <EnTete
          eyebrow="Achats"
          titre="Factures fournisseur"
          description="Factures Franche-Comté Boissons par exercice, au format PDF. Cliquer ouvre le PDF dans un nouvel onglet."
          niveau="Document PDF"
        />
        <FicheMeta
          items={[
            { label: 'Exercices', value: String(facturesParAnnee.length) },
            { label: 'Pièces', value: String(total) },
            { label: 'Fournisseur', value: 'FCBS' },
          ]}
        />
        <SectionFichiers titre="Factures par exercice">
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
        </SectionFichiers>
      </Stack>
    )
  }

  // 5) Carnet manuscrit (XLS, aperçu)
  if (slug === MANUSCRIT_SLUG) {
    return (
      <Stack gap={32}>
        <RetourLien />
        <EnTete
          eyebrow="Preuve boissons"
          titre={carnetManuscrit.titre}
          description={carnetManuscrit.description}
          niveau={carnetManuscrit.niveau}
        />
        <FicheMeta
          items={[
            { label: 'Lignes', value: '218' },
            { label: 'Période', value: 'avr. 2022 → mars 2025' },
            { label: 'Format', value: carnetManuscrit.format },
          ]}
        />
        <SectionFichiers titre="Transcription">
          <SimpleGrid cols={{ base: 1, md: 3 }} spacing="md">
            <DocCard doc={carnetManuscrit} onApercu={setApercu} />
          </SimpleGrid>
        </SectionFichiers>
        <ApercuModal doc={apercu} onClose={() => setApercu(null)} />
      </Stack>
    )
  }

  // 6) Inventaires (PDF scanné + CSV d'extraction boissons)
  if (slug === INVENTAIRES_SLUG) {
    return (
      <Stack gap={32}>
        <RetourLien />
        <EnTete
          eyebrow="Stocks au 31/03"
          titre="Inventaires"
          description="Inventaires physiques de fin d'exercice : scan d'origine (PDF) et extraction des boissons & alcools (CSV : produit, catégorie, quantité, prix unitaire, valeur HT)."
          niveau="Document PDF"
        />
        <FicheMeta
          items={[
            { label: 'Exercices', value: String(inventaires.length) },
            { label: 'Formats', value: 'PDF + CSV' },
            { label: 'Période', value: '2023 → 2025' },
          ]}
        />
        <SectionFichiers titre="Inventaires par exercice">
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
        </SectionFichiers>
      </Stack>
    )
  }

  // 7) Annexe A…H
  if (groupe) {
    const formats = Array.from(
      new Set(groupe.documents.map((d) => d.format)),
    ).join(', ')
    return (
      <Stack gap={32}>
        <RetourLien />
        <EnTete
          eyebrow={`Annexe ${groupe.lettre}`}
          titre={groupe.titre}
          description={groupe.description}
          niveau={groupe.niveau}
        />
        <FicheMeta
          items={[
            { label: 'Annexe', value: groupe.lettre },
            { label: 'Exercices', value: String(groupe.documents.length) },
            { label: 'Format', value: formats },
            { label: 'Période', value: '2022 → 2025' },
          ]}
        />
        <SectionFichiers titre="Fichiers par exercice">
          <SimpleGrid cols={{ base: 1, md: 3 }} spacing="md">
            {groupe.documents.map((d) => (
              <DocCard key={d.id} doc={d} onApercu={setApercu} />
            ))}
          </SimpleGrid>
        </SectionFichiers>
        <ApercuModal doc={apercu} onClose={() => setApercu(null)} />
      </Stack>
    )
  }

  // 4) Slug inconnu
  return (
    <Stack gap="lg">
      <RetourLien />
      <Title order={1} fz={{ base: 32, sm: 44 }}>
        Pièce introuvable
      </Title>
      <Text c="dimmed">Aucune pièce ne correspond à « {slug} ».</Text>
      <Button component={Link} to="/documents" radius="md" w="fit-content">
        Retour à la bibliothèque
      </Button>
    </Stack>
  )
}
