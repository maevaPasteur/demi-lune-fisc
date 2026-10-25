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
  IconInfoCircle,
  IconBuildingBank,
  IconUsers,
  type Icon,
} from '@tabler/icons-react'
import {
  associes,
  cascade,
  controle,
  delai,
  societe,
  totalActuel,
  totalAssocies,
  totalParAssocie,
  totalPenalites,
  totalSociete,
  amende1759,
  type PostePenalite,
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
          <Text ff="heading" fz={valueFz} fw={700} c={highlight ? 'white' : undefined} lh={1.15}>
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
        label="Exposition actuelle"
        value={formatEuro(totalActuel)}
        sub="Société + associés (après désignation)"
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

// --- Bandeau de rappel : montant initial et abandon du 1759 ------------------
function RappelInitial() {
  return (
    <Paper
      p="lg"
      radius="lg"
      withBorder
      style={{
        background: 'var(--mantine-color-gold-0)',
        borderColor: 'var(--mantine-color-gold-3)',
      }}
    >
      <Group gap="sm" wrap="nowrap" align="flex-start">
        <ThemeIcon size={34} radius="md" variant="light" color="gold">
          <IconInfoCircle size={20} stroke={1.8} />
        </ThemeIcon>
        <Text size="sm" c="gray.8">
          Initialement notifié <strong>{formatEuro(totalPenalites)}</strong>, dont{' '}
          <strong>{formatEuro(amende1759)}</strong> d’amende de 100 % (art. 1759 CGI). Après la
          désignation des bénéficiaires du 16 juin 2026 (art. 117 CGI), cette amende est{' '}
          <strong>abandonnée</strong> et remplacée par la taxation personnelle des deux co-gérants
          (propositions de rectification du 19 octobre 2026). L’ensemble reste suspendu au sort de la
          reconstitution.
        </Text>
      </Group>
    </Paper>
  )
}

// --- Détail chiffré (barres de proportion sur un total donné) ----------------
function LigneMontant({
  poste,
  montant,
  total,
  color,
}: {
  poste: string
  montant: number
  total: number
  color: string
}) {
  const part = total > 0 ? (montant / total) * 100 : 0
  return (
    <div className={`${classes.row} ${classes.line}`}>
      <Group gap={10} wrap="nowrap">
        <Box w={10} h={10} style={{ borderRadius: '50%', background: color, flexShrink: 0 }} />
        <Text fw={500}>{poste}</Text>
      </Group>
      <div className={classes.part}>
        <Progress value={part} color={color} size="sm" radius="xl" style={{ flex: 1 }} />
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

const COULEUR_IS = 'var(--mantine-color-gold-6)'
const COULEUR_TVA = 'var(--mantine-color-blue-6)'
const COULEUR_ASSOCIE = '#b4452e'

function couleurSociete(poste: string): string {
  return /tva/i.test(poste) ? COULEUR_TVA : COULEUR_IS
}

// --- Étage 1 : la société -----------------------------------------------------
function BlocSociete() {
  return (
    <Paper p="xl">
      <Group justify="space-between" align="flex-start" wrap="wrap" gap="sm" mb="lg">
        <Group gap="sm" wrap="nowrap">
          <ThemeIcon size={36} radius="md" variant="light" color="gold">
            <IconBuildingBank size={20} stroke={1.8} />
          </ThemeIcon>
          <div>
            <Title order={3} fz={24}>
              Niveau société — SARL LA DEMI-LUNE
            </Title>
            <Text size="sm" c="dimmed">
              Droits et majorations maintenus (IS, TVA, 1729, intérêts)
            </Text>
          </div>
        </Group>
        <Text ff="heading" fw={700} fz={26} c="gold.7">
          {formatEuro(totalSociete)}
        </Text>
      </Group>

      <div className={`${classes.row} ${classes.head}`}>
        <Text size="xs" tt="uppercase" c="dimmed" fw={600} style={{ letterSpacing: '0.06em' }}>
          Poste
        </Text>
        <Text size="xs" tt="uppercase" c="dimmed" fw={600} className={classes.part} style={{ letterSpacing: '0.06em' }}>
          Part
        </Text>
        <Text size="xs" tt="uppercase" c="dimmed" fw={600} ta="right" style={{ letterSpacing: '0.06em' }}>
          Montant
        </Text>
      </div>

      {societe.map((ligne: PostePenalite) => (
        <LigneMontant
          key={ligne.poste}
          poste={ligne.poste}
          montant={ligne.montant}
          total={totalSociete}
          color={couleurSociete(ligne.poste)}
        />
      ))}
    </Paper>
  )
}

// --- Étage 2 : les associés ---------------------------------------------------
function BlocAssocies() {
  return (
    <Paper p="xl">
      <Group justify="space-between" align="flex-start" wrap="wrap" gap="sm" mb="lg">
        <Group gap="sm" wrap="nowrap">
          <ThemeIcon size={36} radius="md" variant="light" color="red">
            <IconUsers size={20} stroke={1.8} />
          </ThemeIcon>
          <div>
            <Title order={3} fz={24}>
              Niveau associés — taxation personnelle
            </Title>
            <Text size="sm" c="dimmed">
              Distributions imposées en RCM (propositions du 19/10/2026)
            </Text>
          </div>
        </Group>
        <Text ff="heading" fw={700} fz={26} c="red.8">
          {formatEuro(totalAssocies)}
        </Text>
      </Group>

      <div className={`${classes.row} ${classes.head}`}>
        <Text size="xs" tt="uppercase" c="dimmed" fw={600} style={{ letterSpacing: '0.06em' }}>
          Associé (supplément d’impôt total)
        </Text>
        <Text size="xs" tt="uppercase" c="dimmed" fw={600} className={classes.part} style={{ letterSpacing: '0.06em' }}>
          Part
        </Text>
        <Text size="xs" tt="uppercase" c="dimmed" fw={600} ta="right" style={{ letterSpacing: '0.06em' }}>
          Montant
        </Text>
      </div>

      {associes.map((a) => (
        <LigneMontant
          key={a.nom}
          poste={`${a.nom}  (${a.annees.map((x) => x.annee).join(' · ')})`}
          montant={totalParAssocie(a)}
          total={totalAssocies}
          color={COULEUR_ASSOCIE}
        />
      ))}

      <Text size="xs" c="dimmed" mt="md" fs="italic">
        Chaque supplément cumule l’impôt sur le revenu (barème, assiette majorée de 25 %), la
        CSG/CRDS, le prélèvement de solidarité, la majoration de 40 % (art. 1729) et les intérêts.
        Base distribuée identique pour les deux foyers (50 / 50). Détail et recalcul en Réponse 2.
      </Text>
    </Paper>
  )
}

// --- Total consolidé ----------------------------------------------------------
function TotalConsolide() {
  return (
    <Paper
      p="xl"
      radius="lg"
      style={{
        background:
          'linear-gradient(135deg, var(--mantine-color-gold-7) 0%, var(--mantine-color-gold-9) 100%)',
        border: 'none',
      }}
    >
      <Group justify="space-between" align="center" wrap="wrap" gap="md">
        <div>
          <Text size="xs" tt="uppercase" c="gold.1" fw={600} style={{ letterSpacing: '0.08em' }}>
            Exposition totale actuelle
          </Text>
          <Text c="gold.1" size="sm" mt={4}>
            Société {formatEuro(totalSociete)} + associés {formatEuro(totalAssocies)}
          </Text>
        </div>
        <Text ff="heading" fw={700} fz={{ base: 34, sm: 44 }} c="white" lh={1}>
          {formatEuro(totalActuel)}
        </Text>
      </Group>
    </Paper>
  )
}

// --- Compteur de délai --------------------------------------------------------
function CompteurDelai() {
  const jours = joursRestants(delai.dateLimite)
  const urgent = jours !== null && jours < 15

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
        Déroulé de la procédure
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
        <Text fw={700} size="sm" c="gold.7" tt="uppercase" style={{ letterSpacing: '0.12em' }}>
          Synthèse du dossier
        </Text>
        <Title order={1} fz={{ base: 40, sm: 56 }} lh={1.05}>
          Accueil
        </Title>
        <Text c="dimmed" size="lg" maw={720}>
          Synthèse du contentieux après les propositions de rectification personnelles du 19 octobre
          2026. Document de travail confidentiel.
        </Text>
      </Stack>

      <CartesStats />
      <RappelInitial />

      <Stack gap="lg">
        <BlocSociete />
        <BlocAssocies />
        <TotalConsolide />
      </Stack>

      <CompteurDelai />
      <Cascade />

      {/* B - Parcourir le dossier */}
      <Stack gap="lg">
        <Title order={2}>Parcourir le dossier</Title>
        <SimpleGrid cols={{ base: 1, md: 2 }} spacing="lg">
          <AccesCard
            to="/reponse-2"
            titre="Réponse"
            desc="La contre-analyse complète et à jour : rejet de comptabilité, méthode de reconstitution et taxation personnelle des associés, point par point, pièces et calculs à l'appui."
          />
          <AccesCard
            to="/documents"
            titre="Documents"
            desc="Les pièces du dossier : courriers du contentieux, annexes comptables et preuves chiffrées, avec aperçu et téléchargement."
          />
        </SimpleGrid>
      </Stack>
    </Stack>
  )
}
