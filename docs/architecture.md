# Architecture

The browser sends requirements to Flask; all costs, eligibility, ranks, and sensitivity experiments are computed in Python. React only displays returned results. Flask serves the Vite production build on the same origin. During development Vite proxies API requests.

CSV sources are imported into SQLite transactionally at startup. The in-memory snapshot is immutable across requests; changes to datasets require a server restart. There are no user accounts or stored personal requirements. Export is a client-side JSON download of the evaluated snapshot. The app runs on localhost through Waitress; deploying publicly would need authentication, operational monitoring, TLS, and environment-specific settings.

The frontend separates form controls, API transport, provider details, analysis charts, and application shell. It labels pending edits and maintains the last successfully evaluated snapshot when a new request fails. Dialogs support Escape, initial focus, and focus containment. Mobile layouts stack the form and keep wide tables scrollable.
