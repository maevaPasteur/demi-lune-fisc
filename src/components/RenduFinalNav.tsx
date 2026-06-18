import { Box, Stack, Text } from '@mantine/core'
import { IconScale } from '@tabler/icons-react'
import { Link, useLocation } from 'react-router-dom'
import { blocs, griefsParBloc } from '../data/renduFinal'
import Brand from './Brand'
import classes from './RenduFinalNav.module.css'

type RenduFinalNavProps = {
  // Optionnel : referme le tiroir mobile à la navigation.
  onNavigate?: () => void
}

// Sommaire numéroté du Rendu final (1. Bloc > 1.1 Grief …), reconstruit depuis
// les données (blocs + griefs) pour rester synchronisé avec les sous-pages.
// Remplace la navigation générale tant qu'on est sur /rendu-final(/*).
export default function RenduFinalNav({ onNavigate }: RenduFinalNavProps) {
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
          Rendu final
        </Text>

        <Link
          to="/rendu-final"
          className={classes.overview}
          data-active={pathname === '/rendu-final' || undefined}
          onClick={onNavigate}
        >
          <IconScale size={17} stroke={1.7} />
          Vue d’ensemble
        </Link>

        {blocs.map((bloc) => {
          const items = griefsParBloc(bloc.id)
          if (items.length === 0) return null
          return (
            <Box key={bloc.id}>
              <Link to="/rendu-final" className={classes.bloc} onClick={onNavigate}>
                <span className={classes.blocNum}>{bloc.numero}</span>
                <span>{bloc.titre}</span>
              </Link>

              {items.map((g, i) => {
                const to = `/rendu-final/${g.slug}`
                return (
                  <Link
                    key={g.slug}
                    to={to}
                    className={classes.grief}
                    data-active={pathname === to || undefined}
                    onClick={onNavigate}
                  >
                    <span className={classes.griefNum}>
                      {bloc.numero}.{i + 1}
                    </span>
                    <span>{g.titre}</span>
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
