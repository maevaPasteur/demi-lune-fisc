import { Box, Stack, Text } from '@mantine/core'
import { IconMessage2Exclamation } from '@tabler/icons-react'
import { Link, useLocation } from 'react-router-dom'
import { blocs, pointsParBloc, numeroDuPoint } from '../data/reponse1'
import Brand from './Brand'
import classes from './RenduFinalNav.module.css'

type Reponse1NavProps = {
  // Optionnel : referme le tiroir mobile à la navigation.
  onNavigate?: () => void
}

// Sommaire numéroté de la Réponse 1 (1. Bloc > 1.1 Point > 3.1.1 sous-point),
// reconstruit depuis les données pour rester synchronisé avec les sous-pages.
// Remplace la navigation générale tant qu'on est sur /reponse-1(/*).
export default function Reponse1Nav({ onNavigate }: Reponse1NavProps) {
  const { pathname } = useLocation()

  return (
    <Stack h="100%" gap={0} p="md">
      <Box pb="md">
        <Brand />
      </Box>

      <div className={classes.scroll}>
        <Text
          size="xs"
          fw={600}
          c="dimmed"
          tt="uppercase"
          px={14}
          mb={6}
          style={{ letterSpacing: '0.08em' }}
        >
          Réponse 1
        </Text>

        <Link
          to="/reponse-1"
          className={classes.overview}
          data-active={pathname === '/reponse-1' || undefined}
          onClick={onNavigate}
        >
          <IconMessage2Exclamation size={17} stroke={1.7} />
          Vue d’ensemble
        </Link>

        {blocs.map((bloc) => {
          const items = pointsParBloc(bloc.id)
          if (items.length === 0) return null
          return (
            <Box key={bloc.id}>
              <Link to="/reponse-1" className={classes.bloc} onClick={onNavigate}>
                <span className={classes.blocNum}>{bloc.numero}</span>
                <span>{bloc.titre}</span>
              </Link>

              {items.map((p) => {
                const to = `/reponse-1/${p.slug}`
                return (
                  <Link
                    key={p.slug}
                    to={to}
                    className={classes.grief}
                    data-active={pathname === to || undefined}
                    onClick={onNavigate}
                    style={p.parent ? { paddingLeft: 34 } : undefined}
                  >
                    <span className={classes.griefNum}>{numeroDuPoint(p.slug)}</span>
                    <span>{p.titre}</span>
                  </Link>
                )
              })}
            </Box>
          )
        })}
      </div>
    </Stack>
  )
}
