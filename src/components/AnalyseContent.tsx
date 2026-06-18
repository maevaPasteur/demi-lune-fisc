import { useState, type ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { BarChart, LineChart } from '@mantine/charts'
import {
  Accordion,
  ActionIcon,
  Alert,
  Anchor,
  Badge,
  Box,
  Button,
  Divider,
  Group,
  Modal,
  Paper,
  ScrollArea,
  SimpleGrid,
  Stack,
  Table,
  Text,
  Title,
} from '@mantine/core'
import {
  IconAlertTriangle,
  IconArrowRight,
  IconCalendar,
  IconChartBar,
  IconChevronDown,
  IconCircleCheck,
  IconDownload,
  IconEye,
  IconFileText,
  IconGavel,
  IconInfoCircle,
  IconToolsKitchen2,
} from '@tabler/icons-react'
import type { ComposanteDetail, JourPartage, KpiItem, Section } from '../data/analyses'
import { fileUrl } from './PieceCards'
import { formatEuro, formatEuroPrecis, formatInt } from '../utils/format'

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

// Justification : tableau de journées + œil -> popin reconstituant les tables partagées.
function quantite(q: number): string {
  return Number.isInteger(q) ? String(q) : q.toString().replace('.', ',')
}
const STATUT_RECON: Record<string, { label: string; color: string; regle: string }> = {
  faute_frappe: { label: 'Faute de frappe', color: 'orange', regle: 'montant ≥ 1 000 €' },
  retrait_article: { label: 'Retrait d’un article', color: 'teal', regle: 'montant = prix exact d’un article du catalogue' },
  partage_forfait: { label: 'Partage / forfait', color: 'blue', regle: 'montant composé, à la même minute qu’une table partagée ou un forfait' },
  a_expliquer: { label: 'À expliquer', color: 'red', regle: 'montant composé, sans table partagée ni forfait à la même minute' },
}
const ORDRE_STATUT = ['a_expliquer', 'partage_forfait', 'retrait_article', 'faute_frappe']
function JoursPartagesView({ section }: { section: Extract<Section, { kind: 'joursPartages' }> }) {
  const [jour, setJour] = useState<JourPartage | null>(null)
  return (
    <Stack gap="sm">
      {section.intro && <Text size="sm" c="dimmed">{richText(section.intro)}</Text>}
      <Paper withBorder radius="lg" p={0} style={{ overflow: 'hidden' }}>
        <Table.ScrollContainer minWidth={620}>
          <Table striped highlightOnHover verticalSpacing="sm" horizontalSpacing="md">
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Date</Table.Th>
                <Table.Th ta="right">Notes du jour</Table.Th>
                <Table.Th ta="right">Tables partagées</Table.Th>
                <Table.Th ta="right">Notes issues de partages</Table.Th>
                <Table.Th ta="right">Suppressions</Table.Th>
                <Table.Th ta="center">Détail</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {section.jours.map((j) => (
                <Table.Tr key={j.date}>
                  <Table.Td>{j.date}</Table.Td>
                  <Table.Td ta="right">{formatInt(j.nb_notes)}</Table.Td>
                  <Table.Td ta="right">{formatInt(j.nb_partages)}</Table.Td>
                  <Table.Td ta="right">{formatInt(j.nb_notes_partagees)}</Table.Td>
                  <Table.Td ta="right">{formatInt(j.nb_suppressions)}</Table.Td>
                  <Table.Td ta="center">
                    <ActionIcon variant="light" color="gold" radius="md" aria-label={`Détail du ${j.date}`} onClick={() => setJour(j)}>
                      <IconEye size={17} />
                    </ActionIcon>
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </Table.ScrollContainer>
      </Paper>

      <Modal
        opened={jour !== null}
        onClose={() => setJour(null)}
        size="xl"
        radius="lg"
        title={jour ? `Suppressions du ${jour.date} : ce qu’il s’est passé, ligne par ligne` : ''}
      >
        {jour && (
          <Stack gap="lg">
            {/* BILAN UNIQUE — rattachement de chaque suppression (somme = total, au centime) */}
            {(() => {
              const r = jour.reconciliation
              const br = r.bilan_rattachement
              const tot = r.total_somme || 1
              const pc = (x: number) => Math.round((100 * x) / tot)
              const rest = br['a_expliquer'] ?? { n: 0, somme: 0 }
              return (
                <Paper withBorder radius="md" p="md">
                  <Group justify="space-between" wrap="nowrap" mb={2}>
                    <Text fw={700} size="sm">{formatInt(r.suppressions.length)} suppressions = {formatEuroPrecis(r.total_somme)}</Text>
                    <Badge color={rest.n ? 'red' : 'teal'} variant="light" size="lg">
                      À expliquer : {formatInt(rest.n)} · {formatEuroPrecis(rest.somme)} ({pc(rest.somme)} %)
                    </Badge>
                  </Group>
                  <Text size="xs" c="dimmed" mb="sm">
                    Chaque suppression reçoit <b>un seul statut</b> (la somme des statuts égale le total, au centime). « À expliquer » = ce qui reste après rattachement.
                  </Text>
                  {ORDRE_STATUT.map((k) => {
                    const v = br[k] ?? { n: 0, somme: 0 }
                    const s = STATUT_RECON[k]
                    return (
                      <Group key={k} justify="space-between" wrap="nowrap" mb={4} gap="xs">
                        <Group gap={6} wrap="nowrap" style={{ minWidth: 0 }}>
                          <Badge color={s.color} variant="light" size="sm" style={{ flexShrink: 0 }}>{s.label}</Badge>
                          <Text size="xs" c="dimmed" lineClamp={1}>— {s.regle}</Text>
                        </Group>
                        <Text fw={600} size="sm" style={{ flexShrink: 0 }}>{formatInt(v.n)} · {formatEuroPrecis(v.somme)}</Text>
                      </Group>
                    )
                  })}
                  {rest.n > 0 && <Text size="xs" c="red.7" mt={2}>Restantes : {r.restantes.join(', ')}</Text>}
                </Paper>
              )
            })()}
            {/* OPÉRATIONS JUSTIFICATIVES (chaînes explicites) */}
            {jour.reconciliation.evenements.length > 0 && (
              <div>
                <Text fw={700} size="sm" mb={2}>Opérations justificatives reconstituées ({jour.reconciliation.nb_tables_partagees} notes partagées)</Text>
                <Text size="xs" c="dimmed" mb={8}>
                  Chaque partage de table ou passage au forfait, avec les suppressions <b>concomitantes</b> (rapprochement par l’heure — hypothèse, pas un identifiant).
                </Text>
                <Stack gap={6}>
                  {jour.reconciliation.evenements.map((e, i) => (
                    <Paper key={i} withBorder radius="sm" p="xs" style={{ background: e.type === 'forfait' ? 'var(--mantine-color-blue-0)' : 'var(--mantine-color-teal-0)' }}>
                      <Text size="xs">{e.explication}</Text>
                    </Paper>
                  ))}
                </Stack>
              </div>
            )}
            {/* 1. JOURNAL DES SUPPRESSIONS (D) */}
            <div>
              <Text fw={700} size="sm">Journal des suppressions (D1 → D{jour.reconciliation.suppressions.length})</Text>
              <Text size="xs" c="dimmed" mb={8}>
                Statut déterminé par le <b>montant</b> (fait). La colonne « Table » est un rapprochement par l’heure (<b>hypothèse</b> ; « ~ » = ambigu car une autre table clôt à la même minute). Le fichier Événement ne donne ni produit ni table.
              </Text>
              {jour.suppr_par_heure.length > 0 && (
                <>
                  <Text size="xs" c="dimmed" mb={2}>Nombre de suppressions par heure (les heures sans service n’apparaissent pas) :</Text>
                  <BarChart h={120} data={jour.suppr_par_heure} dataKey="heure"
                    series={[{ name: 'n', color: 'gold.5', label: 'suppressions' }]}
                    withTooltip={false} barProps={{ radius: 4 }} gridAxis="y" mb="sm" />
                </>
              )}
              <ScrollArea.Autosize mah={220}>
                <Table withTableBorder withColumnBorders verticalSpacing={2} fz="xs" stickyHeader>
                  <Table.Thead><Table.Tr>
                    <Table.Th>D</Table.Th><Table.Th>Heure</Table.Th><Table.Th ta="right">Montant</Table.Th><Table.Th>Table (hypothèse)</Table.Th><Table.Th>Statut</Table.Th>
                  </Table.Tr></Table.Thead>
                  <Table.Tbody>
                    {jour.reconciliation.suppressions.map((s) => {
                      const st = STATUT_RECON[s.statut] ?? STATUT_RECON.a_expliquer
                      return (
                        <Table.Tr key={s.nom} style={s.statut === 'a_expliquer' ? { background: 'var(--mantine-color-red-0)' } : undefined}>
                          <Table.Td fw={600}>{s.nom}</Table.Td>
                          <Table.Td>{s.heure}</Table.Td>
                          <Table.Td ta="right">{formatEuroPrecis(s.montant)}</Table.Td>
                          <Table.Td c="dimmed">{s.table ? `${s.confiance === 'ambigu' ? '~ ' : ''}${s.table}` : '—'}</Table.Td>
                          <Table.Td><Badge size="xs" color={st.color} variant="light">{st.label}</Badge></Table.Td>
                        </Table.Tr>
                      )
                    })}
                  </Table.Tbody>
                </Table>
              </ScrollArea.Autosize>
            </div>

            {/* JOURNAL DES MODIFICATIONS DE PRIX (M) */}
            {jour.reconciliation.modifications.length > 0 && (
              <div>
                <Text fw={700} size="sm">Modifications de prix (M1 → M{jour.reconciliation.modifications.length})</Text>
                <Text size="xs" c="dimmed" mb={8}>
                  Articles facturés à un prix hors catalogue de la période (forfait, addition ajustée pour être divisée).
                </Text>
                <Table withTableBorder withColumnBorders verticalSpacing={2} fz="xs">
                  <Table.Thead><Table.Tr>
                    <Table.Th>M</Table.Th><Table.Th>Heure</Table.Th><Table.Th>Article</Table.Th>
                    <Table.Th ta="right">Prix facturé</Table.Th><Table.Th ta="right">Prix de référence</Table.Th><Table.Th>Table</Table.Th>
                  </Table.Tr></Table.Thead>
                  <Table.Tbody>
                    {jour.reconciliation.modifications.map((m) => (
                      <Table.Tr key={m.nom}>
                        <Table.Td fw={600}>{m.nom}</Table.Td>
                        <Table.Td>{m.heure}</Table.Td>
                        <Table.Td>{m.article}</Table.Td>
                        <Table.Td ta="right">{formatEuroPrecis(m.prix)}</Table.Td>
                        <Table.Td ta="right" c="dimmed">{m.prix_ref.map((p) => formatEuroPrecis(p)).join(' / ')}</Table.Td>
                        <Table.Td c="dimmed">{m.table}</Table.Td>
                      </Table.Tr>
                    ))}
                  </Table.Tbody>
                </Table>
              </div>
            )}

            {/* VENTES PAR TABLE (T + lignes A) avec croisement */}
            <div>
              <Text fw={700} size="sm" mb={2}>Ventes par table (T1 → T{jour.reconciliation.tables.length}) et croisement</Text>
              <Text size="xs" c="dimmed" mb={8}>
                Chaque table encaissée (lignes A…, total) avec : ses suppressions rapprochées par l’heure (D…), ses prix modifiés (M…) et si elle a été <b>partagée</b> (notes de même total, articles en 0,5 = divisée pour payer séparément).
              </Text>
              <ScrollArea.Autosize mah={360}>
                <Accordion variant="separated" multiple chevronPosition="left">
                  {jour.reconciliation.tables.map((t) => (
                    <Accordion.Item key={t.nom} value={t.nom}>
                      <Accordion.Control>
                        <Group gap="xs" wrap="wrap">
                          <Text fw={700} size="sm">{t.nom}</Text>
                          <Text size="xs" c="dimmed">{t.heure} · {formatEuroPrecis(t.total)}</Text>
                          {t.partagee && <Badge size="xs" color="teal" variant="light">partagée{t.jumelles.length ? ` (${t.jumelles.join(', ')})` : ''}</Badge>}
                          {t.modifications.length > 0 && <Badge size="xs" color="orange" variant="light">prix modifié : {t.modifications.join(', ')}</Badge>}
                          {t.nb_suppressions > 0 && <Badge size="xs" color="gray" variant="light">{t.nb_suppressions} suppr. (~heure) : {t.suppressions.join(', ')}</Badge>}
                        </Group>
                      </Accordion.Control>
                      <Accordion.Panel>
                        <Table withTableBorder withColumnBorders verticalSpacing={2} fz="xs">
                          <Table.Thead><Table.Tr>
                            <Table.Th>A</Table.Th><Table.Th>Article</Table.Th><Table.Th ta="right">Qté</Table.Th>
                            <Table.Th ta="right">Prix</Table.Th><Table.Th ta="right">Montant</Table.Th>
                          </Table.Tr></Table.Thead>
                          <Table.Tbody>
                            {t.lignes.map((l) => (
                              <Table.Tr key={l.nom} style={l.modifie ? { background: 'var(--mantine-color-orange-0)' } : undefined}>
                                <Table.Td fw={600}>{l.nom}</Table.Td>
                                <Table.Td>{l.lib}{l.modifie && <Badge ml={4} size="xs" color="orange" variant="light">prix modifié</Badge>}</Table.Td>
                                <Table.Td ta="right">{quantite(l.qte)}</Table.Td>
                                <Table.Td ta="right">{formatEuroPrecis(l.pu)}</Table.Td>
                                <Table.Td ta="right">{formatEuroPrecis(l.montant)}</Table.Td>
                              </Table.Tr>
                            ))}
                          </Table.Tbody>
                        </Table>
                      </Accordion.Panel>
                    </Accordion.Item>
                  ))}
                </Accordion>
              </ScrollArea.Autosize>
            </div>
          </Stack>
        )}
      </Modal>
    </Stack>
  )
}

// Quantité « jolie » : 2 → "2", 0,5 → "0,5".
function qteFr(q: number): string {
  return Number.isInteger(q) ? String(q) : q.toLocaleString('fr-FR', { maximumFractionDigits: 2 })
}

// Une note encaissée (la « table ») : en-tête + contenu détaillé, article mis en
// évidence si c'est lui qui justifie la suppression (cas « article déplacé »).
function NoteCard({ note }: { note: import('../data/analyses').CasNote }) {
  return (
    <Paper withBorder radius="md" p="sm" bg="var(--mantine-color-gray-0)">
      <Group justify="space-between" wrap="nowrap" mb={6}>
        <Text fw={700} size="sm">{note.label}</Text>
        <Text size="xs" c="dimmed">{note.heure} · {formatEuroPrecis(note.total)}</Text>
      </Group>
      <Table verticalSpacing={2} horizontalSpacing="xs" fz="xs" withRowBorders={false}>
        <Table.Tbody>
          {note.items.map((it, i) => {
            const on = it.highlight || (note.highlight && it.lib === note.highlight)
            return (
              <Table.Tr key={i} style={on ? { background: 'var(--mantine-color-teal-0)' } : undefined}>
                <Table.Td fw={on ? 700 : 400}>{it.lib}</Table.Td>
                <Table.Td c="dimmed" ta="right" style={{ whiteSpace: 'nowrap' }}>
                  {qteFr(it.qte)} × {formatEuroPrecis(it.pu)}
                </Table.Td>
                <Table.Td ta="right" fw={on ? 700 : 500} style={{ whiteSpace: 'nowrap' }}>
                  {formatEuroPrecis(it.montant)}
                </Table.Td>
              </Table.Tr>
            )
          })}
        </Table.Tbody>
      </Table>
    </Paper>
  )
}

// Une FICHE d'exemple : à gauche les suppressions (heure + montant), à droite
// l'encaissement correspondant (note(s) avec leur contenu). Lecture : ce qui a
// été supprimé n'a pas disparu, il est encaissé sur la note de droite.
function ExempleFiche({ ex }: { ex: import('../data/analyses').CasExemple }) {
  const sommeSupp = ex.suppressions.reduce((s, d) => s + d.montant, 0)
  // La « Somme » n'a de sens que si elle reconstitue le total d'une note (forfait) :
  // somme des suppressions = total de la note re-facturée, au centime.
  const noteTie = ex.suppressions.length > 1
    ? ex.notes.find((n) => Math.abs(n.total - sommeSupp) < 0.05)
    : undefined
  return (
    <Paper withBorder radius="lg" p="md">
      <Group gap="xs" mb="sm">
        <IconCalendar size={15} color="var(--mantine-color-dimmed)" />
        <Text fw={700} size="sm">{ex.date}</Text>
        {ex.article && <Badge size="sm" variant="light" color="teal">{ex.article}</Badge>}
      </Group>
      <SimpleGrid cols={{ base: 1, sm: 2 }} spacing="md" verticalSpacing="md">
        {/* Suppressions */}
        <Stack gap={6}>
          <Text size="xs" tt="uppercase" fw={700} c="dimmed" lts={0.4}>
            Suppression{ex.suppressions.length > 1 ? 's' : ''}
          </Text>
          {ex.suppressions.length === 0 ? (
            <Text size="xs" c="dimmed" fs="italic">
              Pas de suppression isolée : la note a directement été scindée pour le paiement.
            </Text>
          ) : (
            <Stack gap={4}>
              {ex.suppressions.map((d, i) => (
                <Stack key={i} gap={0} style={{ borderBottom: '1px solid var(--mantine-color-gray-2)', paddingBottom: 3 }}>
                  <Group justify="space-between" wrap="nowrap" gap="xs">
                    <Text size="sm" c="dimmed" style={{ fontVariantNumeric: 'tabular-nums', whiteSpace: 'nowrap' }}>
                      {ex.date} · {d.heure}
                    </Text>
                    <Text size="sm" fw={600} c="red.7" style={{ whiteSpace: 'nowrap' }}>
                      − {formatEuroPrecis(d.montant)}
                    </Text>
                  </Group>
                  {d.devient && (
                    <Text size="xs" c="teal.7">
                      → {d.devient}
                      {d.tables && d.tables.length > 0 && (
                        <Text span c="dimmed"> · réparti sur {d.tables.join(' · ')}</Text>
                      )}
                    </Text>
                  )}
                </Stack>
              ))}
              {noteTie && (
                <Group justify="space-between" wrap="nowrap" mt={2}>
                  <Group gap={4} wrap="nowrap">
                    <IconCircleCheck size={14} color="var(--mantine-color-teal-7)" />
                    <Text size="xs" c="dimmed">Somme = total de la note</Text>
                  </Group>
                  <Text size="sm" fw={700} style={{ whiteSpace: 'nowrap' }}>{formatEuroPrecis(sommeSupp)}</Text>
                </Group>
              )}
            </Stack>
          )}
        </Stack>
        {/* Encaissement correspondant */}
        <Stack gap={6}>
          <Group gap={4} wrap="nowrap">
            <IconArrowRight size={14} color="var(--mantine-color-teal-7)" />
            <Text size="xs" tt="uppercase" fw={700} c="teal.7" lts={0.4}>
              Encaissé sur {ex.notes.length > 1 ? 'ces notes' : 'cette note'}
            </Text>
          </Group>
          {ex.notes.map((n, i) => <NoteCard key={i} note={n} />)}
        </Stack>
      </SimpleGrid>
    </Paper>
  )
}

function CasSuppressionsView({ section }: { section: Extract<Section, { kind: 'casSuppressions' }> }) {
  return (
    <Stack gap="xl">
      {section.cas.map((c) => (
        <Stack key={c.id} gap="sm">
          <div>
            <Badge variant="light" color="teal" size="sm" mb={6}>Notre analyse</Badge>
            <Title order={3} fw={800} style={{ letterSpacing: '-0.01em' }}>{c.titre}</Title>
            <Text size="sm" c="dimmed" mt={2}>{c.preuve}</Text>
          </div>
          <Text size="md">{richText(c.description)}</Text>
          <Text size="xs" c="dimmed">
            Exemples datés ci-dessous (d’autres dans la pièce jointe).
          </Text>
          <Stack gap="md">
            {c.exemples.map((ex, i) => <ExempleFiche key={i} ex={ex} />)}
          </Stack>
        </Stack>
      ))}
    </Stack>
  )
}

function SectionView({ section }: { section: Section }) {
  switch (section.kind) {
    case 'joursPartages':
      return <JoursPartagesView section={section} />

    case 'casSuppressions':
      return <CasSuppressionsView section={section} />

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

    case 'interne': {
      const AUD = {
        restaurant: { label: 'Restaurant / exploitant', color: 'grape' },
        comptable: { label: 'Expert-comptable', color: 'indigo' },
        avocat: { label: 'Avocat', color: 'violet' },
      } as const
      const a = AUD[section.audience]
      return (
        <Alert
          color={a.color}
          variant="light"
          radius="lg"
          icon={<IconInfoCircle size={18} />}
          title={
            <Group gap={8} wrap="wrap">
              <Badge color={a.color} variant="filled" radius="sm" size="sm">
                Note interne · {a.label}
              </Badge>
              <Text span fw={700} c="dark.6">
                {section.titre}
              </Text>
            </Group>
          }
          p="lg"
          styles={{
            root: {
              backgroundColor: `var(--mantine-color-${a.color}-0)`,
              border: `1px dashed var(--mantine-color-${a.color}-4)`,
            },
            message: {
              fontSize: 'var(--mantine-font-size-md)',
              lineHeight: 1.55,
              color: 'var(--mantine-color-dark-6)',
            },
            body: { gap: 8 },
          }}
        >
          <Stack gap={6}>
            <div>{richText(section.texte)}</div>
            <Text size="xs" c="dimmed" fs="italic">
              Note de travail interne, à retirer avant toute transmission à l’administration fiscale.
            </Text>
          </Stack>
        </Alert>
      )
    }

    case 'chapitre': {
      const MAP = {
        fisc: { color: 'red', label: 'Le fisc' },
        nous: { color: 'teal', label: 'Notre analyse' },
        neutre: { color: 'gold', label: 'En clair' },
      } as const
      const c = MAP[section.source] ?? MAP.neutre
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
              {(section.fichiers ?? []).map((f) => (
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

    case 'grilleTables':
      return (
        <Paper p={{ base: 'md', sm: 'lg' }} radius="lg">
          <Stack gap="sm">
            {section.titre && (
              <Title order={3} fz={{ base: 18, sm: 22 }}>
                {section.titre}
              </Title>
            )}
            {section.sousTitre && (
              <Text size="sm" c="dimmed">
                {section.sousTitre}
              </Text>
            )}
            <SimpleGrid cols={{ base: 3, xs: 4, sm: 6, md: 9 }} spacing="xs" verticalSpacing="xs">
              {section.tables.map((t) => {
                const isNote = section.variante === 'notes' || typeof t.total === 'number'
                const type = t.type ?? 'reelle'
                const palette =
                  type === 'virtuelle'
                    ? { color: 'teal', border: 'var(--mantine-color-teal-5)', style: 'dashed', bg: 'var(--mantine-color-teal-0)', icon: 'var(--mantine-color-teal-7)' }
                    : type === 'inexistante'
                      ? { color: 'red', border: 'var(--mantine-color-red-4)', style: 'dashed', bg: 'var(--mantine-color-red-0)', icon: 'var(--mantine-color-red-5)' }
                      : { color: 'gray', border: 'var(--mantine-color-gray-3)', style: 'solid', bg: undefined as string | undefined, icon: 'var(--mantine-color-gray-6)' }
                return (
                  <Paper
                    key={t.numero}
                    withBorder
                    radius="md"
                    p="xs"
                    style={{
                      borderColor: isNote ? 'var(--mantine-color-gray-3)' : palette.border,
                      borderStyle: isNote ? 'solid' : palette.style,
                      backgroundColor: isNote ? undefined : palette.bg,
                    }}
                  >
                    <Stack gap={2} align="center">
                      {isNote ? (
                        <>
                          <Text fw={700} size="sm">
                            {t.numero}
                          </Text>
                          <Text fw={700} fz={22} c="teal.7" lh={1}>
                            {(t.total ?? 0).toLocaleString('fr-FR')}
                          </Text>
                          <Text size="xs" c="dimmed">
                            encaissements
                          </Text>
                        </>
                      ) : (
                        <>
                          <IconToolsKitchen2 size={20} color={palette.icon} />
                          <Text fw={700} size="sm" td={type === 'inexistante' ? 'line-through' : undefined}>
                            {t.numero}
                          </Text>
                          <Badge size="xs" variant="light" color={palette.color} radius="sm">
                            {type === 'virtuelle' ? 'Virtuelle' : type === 'inexistante' ? 'Inexistante' : 'Réelle'}
                          </Badge>
                          {t.note && (
                            <Text size="xs" c="dimmed" ta="center" lh={1.1}>
                              {t.note}
                            </Text>
                          )}
                        </>
                      )}
                    </Stack>
                  </Paper>
                )
              })}
            </SimpleGrid>
          </Stack>
        </Paper>
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
                  {section.colonnes.map((col, ci) => {
                    const c = (typeof col === 'string' ? { label: col } : col) as {
                      label: string
                      align?: 'left' | 'right' | 'center'
                    }
                    return (
                      <Table.Th key={ci} ta={c.align ?? 'left'}>
                        <Text size="xs" tt="uppercase" c="dimmed" fw={600}>
                          {c.label}
                        </Text>
                      </Table.Th>
                    )
                  })}
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {section.lignes.map((ligne, ri) => (
                  <Table.Tr key={ri}>
                    {ligne.map((rawCell, ci) => {
                      const cell = (typeof rawCell === 'string' ? { v: rawCell } : rawCell) as {
                        v: string
                        align?: 'left' | 'right' | 'center'
                        fw?: number
                        badge?: 'ok' | 'ko'
                      }
                      return (
                        <Table.Td key={ci} ta={cell.align ?? 'left'} fw={cell.fw}>
                          {cell.badge ? (
                            <Badge color={cell.badge === 'ok' ? 'teal' : 'red'} variant="light" radius="sm">
                              {cell.v}
                            </Badge>
                          ) : (
                            cell.v
                          )}
                        </Table.Td>
                      )
                    })}
                  </Table.Tr>
                ))}
              </Table.Tbody>
              </Table>
            </Table.ScrollContainer>
          </Stack>
        </Paper>
      )

    case 'graphiqueLignes': {
      const ticks = section.moisTicks?.map((t) => t.tick)
      const labels = Object.fromEntries((section.moisTicks ?? []).map((t) => [t.tick, t.label]))
      return (
        <Paper p={{ base: 'md', sm: 'lg' }} radius="lg">
          <Stack gap="sm">
            {section.titre && (
              <Title order={3} fz={{ base: 18, sm: 22 }}>
                {section.titre}
              </Title>
            )}
            {section.sousTitre && (
              <Text size="sm" c="dimmed">
                {section.sousTitre}
              </Text>
            )}
            <LineChart
              h={section.hauteur}
              data={section.data}
              dataKey={section.dataKey}
              series={section.series.map((s) => ({ name: s.name, color: s.couleur }))}
              valueFormatter={(v) => (section.format === 'euro' ? formatEuro(v) : formatInt(v))}
              curveType="monotone"
              withDots={false}
              connectNulls
              withLegend
              gridAxis="xy"
              xAxisProps={{
                ticks,
                tickFormatter: (v: number) => labels[v] ?? '',
              }}
            />
          </Stack>
        </Paper>
      )
    }

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

    case 'graphiqueEmpile':
      return (
        <Paper p={{ base: 'md', sm: 'lg' }} radius="lg">
          <Stack gap="sm">
            {section.titre && (
              <Title order={3} fz={{ base: 18, sm: 22 }}>
                {section.titre}
              </Title>
            )}
            <BarChart
              h={section.hauteur}
              data={section.data}
              dataKey={section.dataKey}
              type={section.type ?? 'stacked'}
              series={section.series.map((s) => ({ name: s.name, color: s.couleur }))}
              valueFormatter={(v) => (section.format === 'euro' ? formatEuro(v) : formatInt(v))}
              withLegend
              gridAxis="y"
            />
          </Stack>
        </Paper>
      )

    case 'barreComposition': {
      const CAT: Record<string, { color: string; label: string }> = {
        mesure: { color: 'teal', label: 'Mesuré (caisse, inventaire)' },
        calcul: { color: 'blue', label: 'Calculé (cuisine, menus)' },
        estime: { color: 'orange', label: 'Estimé (chef, offerts, sur-versement)' },
        residuel: { color: 'gray', label: 'Perte résiduelle' },
        neutre: { color: 'indigo', label: 'Autre' },
        alerte: { color: 'red', label: 'Espèces' },
      }
      const total = section.total ?? section.segments.reduce((a, s) => a + s.valeur, 0)
      const fmt = (v: number) =>
        section.unite === '%' ? `${v.toLocaleString('fr-FR')} %` : `${formatInt(Math.round(v))} ${section.unite}`
      const usedCats = Array.from(new Set(section.segments.map((s) => s.categorie)))
      return (
        <Paper p={{ base: 'md', sm: 'lg' }} radius="lg">
          <Stack gap="md">
            {section.titre && (
              <div>
                <Title order={3} fz={{ base: 18, sm: 22 }}>
                  {section.titre}
                </Title>
                {section.sousTitre && (
                  <Text size="sm" c="dimmed" mt={2}>
                    {section.sousTitre}
                  </Text>
                )}
              </div>
            )}
            {/* Barre proportionnelle : largeur = valeur / total (part de 0, somme = 100 %) */}
            <div style={{ display: 'flex', height: 34, borderRadius: 8, overflow: 'hidden', gap: 2 }}>
              {section.segments.map((s, i) => (
                <Box
                  key={i}
                  title={`${s.label} - ${fmt(s.valeur)}`}
                  style={{
                    width: `${(100 * s.valeur) / total}%`,
                    background: `var(--mantine-color-${CAT[s.categorie].color}-${s.categorie === 'residuel' ? 4 : 6})`,
                  }}
                />
              ))}
            </div>
            {/* Légende chiffrée : un poste par ligne, valeur + part % */}
            <Stack gap={6}>
              {section.segments.map((s, i) => (
                <Group key={i} justify="space-between" wrap="nowrap" gap="sm">
                  <Group gap={8} wrap="nowrap">
                    <Box
                      w={11}
                      h={11}
                      style={{ borderRadius: 3, background: `var(--mantine-color-${CAT[s.categorie].color}-${s.categorie === 'residuel' ? 4 : 6})`, flexShrink: 0 }}
                    />
                    <Text size="sm">{s.label}</Text>
                  </Group>
                  <Text size="sm" fw={600} style={{ flexShrink: 0 }}>
                    {fmt(s.valeur)} <Text span c="dimmed" size="xs">({Math.round((100 * s.valeur) / total)} %)</Text>
                  </Text>
                </Group>
              ))}
            </Stack>
            {section.legende && (
              <Group gap="md" mt={2}>
                {usedCats.map((c) => (
                  <Group key={c} gap={6} wrap="nowrap">
                    <Box w={11} h={11} style={{ borderRadius: 3, background: `var(--mantine-color-${CAT[c].color}-${c === 'residuel' ? 4 : 6})` }} />
                    <Text size="xs" c="dimmed">
                      {CAT[c].label}
                    </Text>
                  </Group>
                ))}
              </Group>
            )}
          </Stack>
        </Paper>
      )
    }

    default:
      return null
  }
}

// Rend la suite des sections d'une analyse.
// Les notes « interne » (notes de travail de l'avocat) ne doivent JAMAIS
// apparaître sur la page montrée à l'administration, ni dans une impression /
// capture / partage de lien. Elles sont donc masquées par défaut et ne
// s'affichent qu'en mode interne explicite, activé par « ?interne=1 » dans l'URL.
function modeInterneActif(): boolean {
  if (typeof window === 'undefined') return false
  return new URLSearchParams(window.location.search).get('interne') === '1'
}

export default function AnalyseContent({ sections }: { sections: Section[] }) {
  const interne = modeInterneActif()
  const visibles = interne ? sections : sections.filter((s) => s.kind !== 'interne')
  return (
    <Stack gap="lg">
      {interne && sections.some((s) => s.kind === 'interne') && (
        <Alert
          color="orange"
          variant="filled"
          radius="lg"
          icon={<IconInfoCircle size={18} />}
          title="Mode interne — notes de travail affichées"
        >
          Cette vue contient des notes internes à l’avocat.{' '}
          <Text span fw={700}>
            Retirez « ?interne=1 » de l’adresse
          </Text>{' '}
          avant toute impression, capture ou transmission à l’administration.
        </Alert>
      )}
      {visibles.map((section, i) => (
        <SectionView key={i} section={section} />
      ))}
    </Stack>
  )
}
