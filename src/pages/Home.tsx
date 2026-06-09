import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import {
  Badge,
  Box,
  Group,
  Paper,
  Progress,
  SimpleGrid,
  Stack,
  Text,
  ThemeIcon,
  Title,
} from '@mantine/core'
import {
  IconArrowRight,
  IconCalendarStats,
  IconClockHour4,
  IconReceiptEuro,
  type Icon,
} from '@tabler/icons-react'
import {
  cascade,
  controle,
  delai,
  penalites,
  totalPenalites,
} from '../data/dossier'
import { formatEuro, joursRestants } from '../utils/format'
import classes from './Penalites.module.css'

// --- Cartes de statistiques (KPI) --------------------------------------------
function StatCard({
  label,
  value,
  sub,
  icon: Icon,
  highlight = false,
  valueFz = 28,
}: {
  label: string
  value: string
  sub: string
  icon: Icon
  highlight?: boolean
  valueFz?: number
}) {
  return (
    <Paper
      p="lg"
      h="100%"
      style={
        highlight
          ? {
              background:
                'linear-gradient(135deg, var(--mantine-color-gold-6) 0%, var(--mantine-color-gold-8) 100%)',
              border: 'none',
            }
          : undefined
      }
    >
      <Stack gap="md" h="100%" justify="space-between">
        <Group justify="space-between" align="flex-start" wrap="nowrap">
          <Text size="sm" lineClamp={2} c={highlight ? 'gold.1' : 'dimmed'}>
            {label}
          </Text>
          <ThemeIcon
            size={40}
            radius="md"
            variant={highlight ? 'white' : 'light'}
            color="gold"
            style={highlight ? { background: 'rgba(255,255,255,0.18)' } : undefined}
          >
            <Icon size={22} stroke={1.8} color={highlight ? 'white' : undefined} />
          </ThemeIcon>
        </Group>
        <div>
          <Text
            ff="heading"
            fz={valueFz}
            fw={700}
            c={highlight ? 'white' : undefined}
            lh={1.15}
          >
            {value}
          </Text>
          <Text size="xs" mt={6} c={highlight ? 'gold.1' : 'dimmed'}>
            {sub}
          </Text>
        </div>
      </Stack>
    </Paper>
  )
}

function CartesStats() {
  return (
    <SimpleGrid cols={{ base: 1, sm: 2, lg: 3 }} spacing="lg">
      <StatCard
        label="Total en jeu"
        value={formatEuro(totalPenalites)}
        sub="Sommes notifiées"
        icon={IconReceiptEuro}
        highlight
      />
      <StatCard
        label="Durée du contrôle"
        value={controle.duree}
        sub={`${controle.debut} → ${controle.fin}`}
        icon={IconClockHour4}
      />
      <StatCard
        label="Période contrôlée"
        value={`${controle.periodeDebut} → ${controle.periodeFin}`}
        sub="Exercices vérifiés"
        icon={IconCalendarStats}
        valueFz={22}
      />
    </SimpleGrid>
  )
}

// --- Détail chiffré (barres de proportion) -----------------------------------
// Chaque poste est rattaché à une catégorie (couleur) : impôt sur les sociétés,
// TVA, ou pénalité pour distributions occultes.
type Categorie = 'is' | 'tva' | 'penalite'

const CATEGORIES: Record<Categorie, { label: string; color: string }> = {
  is: { label: 'Impôt sur les sociétés', color: 'var(--mantine-color-gold-6)' },
  tva: { label: 'TVA', color: 'var(--mantine-color-blue-6)' },
  penalite: { label: 'Pénalité distributions', color: '#b4452e' },
}

function categorie(poste: string): Categorie {
  if (/tva/i.test(poste)) return 'tva'
  if (/1759|distribution/i.test(poste)) return 'penalite'
  return 'is'
}

function PuceLegende({ color, label }: { color: string; label: string }) {
  return (
    <Group gap={8} wrap="nowrap">
      <Box
        w={10}
        h={10}
        style={{ borderRadius: '50%', background: color, flexShrink: 0 }}
      />
      <Text size="sm" c="dimmed">
        {label}
      </Text>
    </Group>
  )
}

function LignePenalite({
  poste,
  montant,
}: {
  poste: string
  montant: number
}) {
  const { color } = CATEGORIES[categorie(poste)]
  const part = totalPenalites > 0 ? (montant / totalPenalites) * 100 : 0

  return (
    <div className={`${classes.row} ${classes.line}`}>
      <Group gap={10} wrap="nowrap">
        <Box
          w={10}
          h={10}
          style={{ borderRadius: '50%', background: color, flexShrink: 0 }}
        />
        <Text fw={500}>{poste}</Text>
      </Group>

      <div className={classes.part}>
        <Progress
          value={part}
          color={color}
          size="sm"
          radius="xl"
          style={{ flex: 1 }}
        />
        <Text size="sm" c="dimmed" w={56} ta="right" style={{ flexShrink: 0 }}>
          {part.toFixed(1)} %
        </Text>
      </div>

      <Text ff="heading" fw={700} ta="right">
        {formatEuro(montant)}
      </Text>
    </div>
  )
}

function TableauPenalites() {
  return (
    <Paper p="xl">
      <Group justify="space-between" align="flex-start" wrap="wrap" gap="sm" mb="lg">
        <Title order={3} fz={26}>
          Détail des sommes notifiées
        </Title>
        <Text size="sm" c="dimmed">
          Part de chaque poste dans le total en jeu
        </Text>
      </Group>

      {/* Légende des catégories */}
      <Group gap="lg" wrap="wrap" mb="md">
        {(Object.keys(CATEGORIES) as Categorie[]).map((key) => (
          <PuceLegende
            key={key}
            color={CATEGORIES[key].color}
            label={CATEGORIES[key].label}
          />
        ))}
      </Group>

      {/* En-têtes de colonnes */}
      <div className={`${classes.row} ${classes.head}`}>
        <Text size="xs" tt="uppercase" c="dimmed" fw={600} style={{ letterSpacing: '0.06em' }}>
          Poste
        </Text>
        <Text
          size="xs"
          tt="uppercase"
          c="dimmed"
          fw={600}
          className={classes.part}
          style={{ letterSpacing: '0.06em' }}
        >
          Part
        </Text>
        <Text size="xs" tt="uppercase" c="dimmed" fw={600} ta="right" style={{ letterSpacing: '0.06em' }}>
          Montant
        </Text>
      </div>

      {/* Lignes */}
      {penalites.map((ligne) => (
        <LignePenalite key={ligne.poste} poste={ligne.poste} montant={ligne.montant} />
      ))}

      {/* Total */}
      <div className={`${classes.row} ${classes.line}`} style={{ marginTop: 8 }}>
        <Title order={4} fz={20}>
          Total en jeu
        </Title>
        <div className={classes.part} />
        <Text ff="heading" fw={700} fz={26} c="gold.7" ta="right">
          {formatEuro(totalPenalites)}
        </Text>
      </div>
    </Paper>
  )
}

// --- Compteur de délai --------------------------------------------------------
function CompteurDelai() {
  const jours = joursRestants(delai.dateLimite)
  const urgent = jours !== null && jours < 10

  let badge: ReactNode
  if (jours === null) {
    badge = (
      <Badge color="gray" variant="light" size="xl" radius="sm">
        Date limite à renseigner
      </Badge>
    )
  } else if (jours < 0) {
    badge = (
      <Badge color="red" variant="filled" size="xl" radius="sm">
        Échéance dépassée
      </Badge>
    )
  } else {
    badge = (
      <Badge color={urgent ? 'red' : 'blue'} variant="filled" size="xl" radius="sm">
        {jours} jour{jours > 1 ? 's' : ''} restant{jours > 1 ? 's' : ''}
      </Badge>
    )
  }

  return (
    <Paper p="xl">
      <Group justify="space-between" align="center" wrap="wrap" gap="md">
        <div>
          <Text size="xs" tt="uppercase" c={urgent ? 'red' : 'dimmed'} fw={600} mb={4}>
            Échéance critique
          </Text>
          <Text fw={600}>{delai.label}</Text>
        </div>
        {badge}
      </Group>
    </Paper>
  )
}

// --- Cascade procédurale ------------------------------------------------------
function Cascade() {
  return (
    <Paper p="xl">
      <Text size="xs" tt="uppercase" c="dimmed" fw={600} mb="md">
        Cascade de la procédure
      </Text>
      <Group gap="xs" wrap="wrap">
        {cascade.map((etape, index) => (
          <Group gap="xs" wrap="nowrap" key={etape}>
            <Paper withBorder shadow="none" radius="md" px="md" py={6} bg="gray.0">
              <Text size="sm" fw={500}>
                {etape}
              </Text>
            </Paper>
            {index < cascade.length - 1 && (
              <Text c="dimmed" fz="lg" aria-hidden>
                →
              </Text>
            )}
          </Group>
        ))}
      </Group>
    </Paper>
  )
}

// --- Carte d'accès à une section du dossier ----------------------------------
function AccesCard({ to, titre, desc }: { to: string; titre: string; desc: string }) {
  return (
    <Paper
      component={Link}
      to={to}
      p="xl"
      radius="lg"
      style={{ textDecoration: 'none', color: 'inherit', display: 'block' }}
    >
      <Stack gap="xs">
        <Group justify="space-between" wrap="nowrap">
          <Title order={3}>{titre}</Title>
          <IconArrowRight size={20} color="var(--mantine-color-gold-7)" />
        </Group>
        <Text c="dimmed" size="sm">
          {desc}
        </Text>
      </Stack>
    </Paper>
  )
}

// --- Page ---------------------------------------------------------------------
export default function Home() {
  return (
    <Stack gap={40}>
      {/* A - En-tête */}
      <Stack gap="xs">
        <Text
          fw={700}
          size="sm"
          c="gold.7"
          tt="uppercase"
          style={{ letterSpacing: '0.12em' }}
        >
          Synthèse du dossier
        </Text>
        <Title order={1} fz={{ base: 40, sm: 56 }} lh={1.05}>
          Accueil
        </Title>
        <Text c="dimmed" size="lg" maw={680}>
          Synthèse des arguments opposables au contrôle fiscal, classés par
          puissance. Document de travail confidentiel.
        </Text>
      </Stack>

      <CartesStats />
      <TableauPenalites />
      <CompteurDelai />
      <Cascade />

      {/* B - Parcourir le dossier */}
      <Stack gap="lg">
        <Title order={2}>Parcourir le dossier</Title>
        <SimpleGrid cols={{ base: 1, md: 3 }} spacing="lg">
          <AccesCard
            to="/defense"
            titre="Défense"
            desc="Les arguments opposables au contrôle, par front, reliés aux preuves et aux pièces."
          />
          <AccesCard
            to="/analyses"
            titre="Analyses"
            desc="Les preuves chiffrées, recalculées et vérifiées depuis la caisse certifiée."
          />
          <AccesCard
            to="/documents"
            titre="Documents"
            desc="Les annexes comptables et la proposition de rectification, avec aperçu et téléchargement."
          />
        </SimpleGrid>
      </Stack>
    </Stack>
  )
}
