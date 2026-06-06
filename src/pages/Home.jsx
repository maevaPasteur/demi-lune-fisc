// Page d'accueil : présente l'objet du dossier et les rubriques à venir.
// Les "cartes" servent de structure : chacune deviendra une page dédiée.
const sections = [
  {
    icon: '📁',
    title: 'Documents',
    description:
      'Répertoire centralisé des pièces du dossier : comptabilité, factures, ' +
      'relevés, courriers de l’administration. Aperçu et téléchargement.',
    status: 'À venir',
  },
  {
    icon: '📊',
    title: 'Analyses',
    description:
      'Synthèses et analyses chiffrées pour appuyer la défense : ratios, ' +
      'reconstitutions de recettes, points de contestation.',
    status: 'À venir',
  },
  {
    icon: '🗓️',
    title: 'Chronologie',
    description:
      'Frise des échéances et événements de la procédure : avis, réponses, ' +
      'délais de recours.',
    status: 'À venir',
  },
]

export default function Home() {
  return (
    <div className="home">
      <section className="hero">
        <p className="hero__eyebrow">Dossier confidentiel</p>
        <h1 className="hero__title">
          Espace de défense fiscale — Restaurant Demi-Lune
        </h1>
        <p className="hero__lead">
          Plateforme privée réunissant les pièces du dossier et les analyses
          destinées à assister l’avocat fiscaliste et son client dans le cadre
          d’un contrôle fiscal en cours.
        </p>
      </section>

      <section className="cards">
        {sections.map((s) => (
          <article className="card" key={s.title}>
            <div className="card__icon" aria-hidden="true">
              {s.icon}
            </div>
            <h2 className="card__title">{s.title}</h2>
            <p className="card__text">{s.description}</p>
            <span className="card__status">{s.status}</span>
          </article>
        ))}
      </section>

      <section className="notice">
        <strong>Confidentialité.</strong> Les informations réunies ici sont
        couvertes par le secret professionnel. L’accès est réservé aux
        intervenants autorisés du dossier.
      </section>
    </div>
  )
}
