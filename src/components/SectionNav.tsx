import { useEffect, useState } from 'react'
import classes from './SectionNav.module.css'

export type Section = { id: string; label: string }

// Décalage d'ancre = en-tête (72) + barre de sommaire + marge. Doit être en
// cohérence avec `scroll-margin-top` posé sur chaque section.
export const SCROLL_OFFSET = 140

// Sommaire d'ancres collant, avec surlignage de la section visible (scroll-spy).
export default function SectionNav({ sections }: { sections: Section[] }) {
  const [active, setActive] = useState(sections[0]?.id ?? '')

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)
        if (visible[0]) setActive(visible[0].target.id)
      },
      // Zone active : sous la barre collante, dans le premier tiers de l'écran.
      { rootMargin: `-${SCROLL_OFFSET}px 0px -65% 0px`, threshold: 0 },
    )
    sections.forEach((s) => {
      const el = document.getElementById(s.id)
      if (el) observer.observe(el)
    })
    return () => observer.disconnect()
  }, [sections])

  const handleClick = (e: React.MouseEvent, id: string) => {
    e.preventDefault()
    const el = document.getElementById(id)
    if (!el) return
    el.scrollIntoView({ behavior: 'smooth', block: 'start' })
    setActive(id)
    window.history.replaceState(null, '', `#${id}`)
  }

  return (
    <nav className={classes.bar} aria-label="Sommaire des sections">
      <div className={classes.scroll}>
        {sections.map((s) => (
          <a
            key={s.id}
            href={`#${s.id}`}
            className={classes.pill}
            data-active={active === s.id || undefined}
            onClick={(e) => handleClick(e, s.id)}
          >
            {s.label}
          </a>
        ))}
      </div>
    </nav>
  )
}
