import { useEffect, useState } from 'react'
import {
  ActionIcon,
  Alert,
  Badge,
  Box,
  Button,
  Group,
  Loader,
  Modal,
  Paper,
  Stack,
  Table,
  Text,
} from '@mantine/core'
import { IconDownload, IconEye } from '@tabler/icons-react'
import type { Document } from '../data/documents'

// URL d'un fichier de public/documents (BASE_URL => compatible GitHub Pages).
// On encode chaque segment du chemin mais on conserve les "/" des sous-dossiers.
export const fileUrl = (fichier: string) =>
  `${import.meta.env.BASE_URL}documents/${fichier
    .split('/')
    .map(encodeURIComponent)
    .join('/')}`

// Couleur de la pastille selon le niveau : résumé = bleu, détaillé = doré,
// données brutes = gris.
export function couleurNiveau(niveau: string): string {
  const n = niveau.toLowerCase()
  if (n.startsWith('résumé')) return 'blue'
  if (n.startsWith('données')) return 'gray'
  return 'gold'
}

// --- Pastille de niveau ------------------------------------------------------
export function NiveauBadge({
  niveau,
  color,
}: {
  niveau: string
  color?: string
}) {
  const resolved = color ?? couleurNiveau(niveau)
  return (
    <Badge
      variant="light"
      color={resolved}
      radius="sm"
      size="lg"
      tt="uppercase"
      leftSection={
        <Box
          w={7}
          h={7}
          style={{
            borderRadius: '50%',
            background: `var(--mantine-color-${resolved}-6)`,
          }}
        />
      }
      styles={{ root: { letterSpacing: '0.04em', fontWeight: 600 } }}
    >
      {niveau}
    </Badge>
  )
}

// --- Carte d'un fichier (une période) ----------------------------------------
export function DocCard({
  doc,
  onApercu,
}: {
  doc: Document
  onApercu: (d: Document) => void
}) {
  return (
    <Paper withBorder shadow="none" radius="lg" p="lg" bg="var(--mantine-color-gray-0)">
      <Stack gap="lg">
        <Group justify="space-between" align="center" wrap="nowrap">
          <Text fw={700}>
            {doc.periode === '2022-2025'
              ? 'Toute la période'
              : `Exercice ${doc.periode}`}
          </Text>
          <Badge variant="outline" color="gray" radius="sm" size="sm">
            {doc.format}
          </Badge>
        </Group>
        <Group gap="sm" wrap="nowrap">
          <Button
            variant="default"
            radius="md"
            leftSection={<IconEye size={16} />}
            onClick={() => onApercu(doc)}
            style={{ flex: 1 }}
          >
            Aperçu
          </Button>
          <ActionIcon
            component="a"
            href={fileUrl(doc.fichier)}
            download={doc.fichier}
            variant="gradient"
            gradient={{ from: 'gold.4', to: 'gold.6', deg: 160 }}
            radius="md"
            size={36}
            aria-label="Télécharger"
            title="Télécharger"
            style={{ color: 'var(--mantine-color-gold-9)' }}
          >
            <IconDownload size={18} />
          </ActionIcon>
        </Group>
      </Stack>
    </Paper>
  )
}

// --- Carte d'un rapport PDF --------------------------------------------------
// Pas d'aperçu tableur ici : le PDF s'ouvre dans un nouvel onglet.
export function RapportCard({ doc }: { doc: Document }) {
  return (
    <Paper withBorder shadow="none" radius="lg" p="lg" bg="var(--mantine-color-gray-0)">
      <Stack gap="md" h="100%" justify="space-between">
        <Group justify="space-between" align="flex-start" wrap="nowrap">
          <Text fw={700}>{doc.titre}</Text>
          <Badge variant="outline" color="gray" radius="sm" size="sm">
            {doc.format}
          </Badge>
        </Group>
        <Text size="sm" c="dimmed">
          {doc.description}
        </Text>
        <Group gap="sm" wrap="nowrap">
          <Button
            component="a"
            href={fileUrl(doc.fichier)}
            target="_blank"
            rel="noopener noreferrer"
            variant="default"
            radius="md"
            leftSection={<IconEye size={16} />}
            style={{ flex: 1 }}
          >
            Aperçu
          </Button>
          <ActionIcon
            component="a"
            href={fileUrl(doc.fichier)}
            download
            variant="gradient"
            gradient={{ from: 'gold.4', to: 'gold.6', deg: 160 }}
            radius="md"
            size={36}
            aria-label="Télécharger"
            title="Télécharger"
            style={{ color: 'var(--mantine-color-gold-9)' }}
          >
            <IconDownload size={18} />
          </ActionIcon>
        </Group>
      </Stack>
    </Paper>
  )
}

// --- Aperçu côté client (aucun envoi externe : données confidentielles) -------
export function ApercuModal({
  doc,
  onClose,
}: {
  doc: Document | null
  onClose: () => void
}) {
  const [rows, setRows] = useState<unknown[][]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!doc) return
    let cancelled = false
    setLoading(true)
    setError(null)
    setRows([])
    ;(async () => {
      try {
        const r = await fetch(fileUrl(doc.fichier))
        if (!r.ok) throw new Error('Fichier introuvable')
        const buf = await r.arrayBuffer()
        // xlsx chargé à la demande (bundle principal allégé).
        const XLSX = await import('xlsx')
        // sheetRows : on ne lit que les premières lignes (rapide même sur gros fichiers).
        const wb = XLSX.read(buf, { type: 'array', sheetRows: 60 })
        const ws = wb.Sheets[wb.SheetNames[0]]
        const data = XLSX.utils.sheet_to_json<unknown[]>(ws, {
          header: 1,
          blankrows: false,
        })
        if (!cancelled) setRows(data.slice(0, 51))
      } catch (e: unknown) {
        if (!cancelled)
          setError(e instanceof Error ? e.message : 'Erreur de lecture')
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [doc])

  const header = (rows[0] ?? []) as unknown[]
  const body = rows.slice(1)

  return (
    <Modal
      opened={doc !== null}
      onClose={onClose}
      size="80%"
      title={doc ? `${doc.titre} - ${doc.periode}` : ''}
    >
      {loading && (
        <Group justify="center" p="xl">
          <Loader />
        </Group>
      )}
      {error && <Alert color="red" variant="light">{error}</Alert>}
      {!loading && !error && rows.length > 0 && (
        <Stack gap="sm">
          <Text size="xs" c="dimmed">
            Aperçu des 50 premières lignes - télécharger le fichier pour
            l’intégralité.
          </Text>
          <Table.ScrollContainer minWidth={400}>
            <Table
              striped
              withTableBorder
              withColumnBorders
              fz="xs"
              verticalSpacing={4}
            >
              <Table.Thead>
                <Table.Tr>
                  {header.map((h, i) => (
                    <Table.Th key={i}>{String(h ?? '')}</Table.Th>
                  ))}
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {body.map((row, ri) => (
                  <Table.Tr key={ri}>
                    {header.map((_, ci) => (
                      <Table.Td key={ci}>
                        {String((row as unknown[])[ci] ?? '')}
                      </Table.Td>
                    ))}
                  </Table.Tr>
                ))}
              </Table.Tbody>
            </Table>
          </Table.ScrollContainer>
        </Stack>
      )}
      {!loading && !error && rows.length === 0 && (
        <Text c="dimmed">Aperçu indisponible.</Text>
      )}
    </Modal>
  )
}
