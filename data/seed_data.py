"""Seed data for `flask seed` command.

Case studies are anonymized — they describe real engagements with
identifying details stripped. The long_description format is:

    **Section heading.**

    Body paragraph...

The `case_format` Jinja filter (registered in app.py) splits on
blank lines and turns the leading `**bold.**` of each paragraph
into a section eyebrow + heading.
"""

PROJECTS = [
    {
        "title": "Power BI / BI analytics portfolio",
        "short_description": (
            "A short portfolio of my Power BI and BI analytics work — "
            "follow the link to browse the dashboards."
        ),
        "long_description": (
            "**Portfolio.** This entry points to a short portfolio of my "
            "Power BI and BI analytics work. Follow the link below to "
            "browse a brief showcase of my dashboard development — "
            "semantic models, reports, and the SQL / ETL work behind them."
        ),
        "image_path": "https://images.unsplash.com/photo-1666875753105-c63a6f3bdc86?q=80&w=1600&auto=format&fit=crop",
        "stack": "Power BI, SQL Server, DAX, Power Query",
        "link_type": None,
        "git_link": None,
    },
    # Aligned with the live /demo/logistics-kpi cockpit. The CLI command
    # `flask sync-logistics-demo` upserts this same dict into the DB
    # without touching the slug, so the existing /project/<slug> URL
    # keeps working after edits to title or copy.
    {
        "title": "Logistics KPI cockpit, single source of truth",
        "short_description": (
            "Operations cockpit for a road carrier. Fleet utilisation, "
            "planner KPIs, and freight-forwarder spend in three tabs — "
            "drillable to a single truck with cost-per-km spread and an "
            "EU route map. Built end-to-end on Flask + Plotly."
        ),
        "long_description": (
            "**Problem.** A mid-sized road carrier ran ops on three siloed "
            "systems — TMS for dispatch, WMS for warehousing, a freight-"
            "invoice export from accounting — plus weekly XLS sheets owned "
            "by individual planners. Every metric (on-time %, €/km, empty-"
            "km, CO₂) had a different number depending on who you asked. "
            "Standup meetings burned half their time arguing whose version "
            "was right.\n\n"
            "**Action.** Built a unified data model joining trips, trucks, "
            "planners, and forwarders into a single SQL warehouse, then a "
            "web cockpit on top of it (Flask + Plotly + Pandas — no "
            "Tableau or Power BI license needed). Three tabs frame the "
            "daily question: Fleet (utilisation, fuel, CO₂), Planning "
            "(empty-km, idle time, on-time per planner), and Forwarders "
            "(volume, €/km vs in-house, claims). Every truck is drillable "
            "from the Fleet roster — revenue, min/median/avg/max €/km, "
            "top routes, and an EU route map of every origin↔destination "
            "pair the truck ran.\n\n"
            "**Outcome.** One opened-by-default URL replaced four "
            "spreadsheets and a stale BI export nobody trusted. Disputes "
            "about whose number is right stopped within the first sprint. "
            "The CEO uses the Forwarders tab to renegotiate two "
            "underperforming carriers; the planning lead uses the per-"
            "truck drill-down to surface deadhead patterns by route. **A "
            "live demo with 28 trucks of mock data is linked at the top "
            "of this page.**"
        ),
        "image_path": "https://images.unsplash.com/photo-1494412651409-8963ce7935a7?q=80&w=1600&auto=format&fit=crop",
        "stack": "Flask, Plotly, Pandas, SQL, NumPy, JavaScript",
        "link_type": None,
        "git_link": None,
    },
    {
        "title": "Internal admin tool, replaced an Excel + Slack workflow",
        "short_description": (
            "Excel form → Flask admin in 4 weeks. Customer-change requests "
            "with audit trail, role-based auth, and a 12-page README the "
            "team's juniors actually use."
        ),
        "long_description": (
            "**Problem.** A growing ops team filed customer-account changes "
            "through a shared Excel form linked from a pinned Slack "
            "message. Requests got lost, two people sometimes edited the "
            "same row at once, and there was no audit trail for compliance. "
            "Engineering didn't want to ship \"yet another internal app\" "
            "from scratch.\n\n"
            "**Action.** Designed and shipped a Flask + SQLAlchemy admin "
            "panel in 4 weeks: typed forms, role-based auth (Flask-Login), "
            "per-row audit log, soft-deletes, CSV export, and a Docker "
            "deploy with CI. Documentation up front: a 12-page README "
            "covering data model, how to extend it, and a runbook for "
            "incidents.\n\n"
            "**Outcome.** Zero \"lost change request\" tickets since launch. "
            "Onboarding new ops staff dropped from a multi-day Slack "
            "shadow-session to a 30-minute README walkthrough. Engineering "
            "later forked the same template for two other internal tools — "
            "the codebase is, in their words, \"code I can read months "
            "later.\""
        ),
        "image_path": "https://images.unsplash.com/photo-1621839673705-6617adf9e890?q=80&w=1600&auto=format&fit=crop",
        "stack": "Flask, SQLAlchemy, Tailwind CSS, Flask-Login, Docker, CI/CD",
        "link_type": None,
        "git_link": None,
    },
    {
        "title": "ntkrv.dev — this very portfolio",
        "short_description": (
            "The Flask + Tailwind site you're reading right now — a modern "
            "resume on steroids, where any employer can see who I am and "
            "what I've built in one place."
        ),
        "long_description": (
            "**Idea.** I wanted one place where any employer or client "
            "could get the full picture of me: my background, the "
            "projects I've shipped, and how I actually write code. A CV "
            "in PDF can't do that — so I built a modern resume on "
            "steroids instead.\n\n"
            "**Action.** Designed and built the whole site myself with "
            "Flask, SQLAlchemy, Flask-Login, Flask-Migrate, and Tailwind "
            "CSS. Dark-first theme with a manual light/dark toggle, "
            "smooth scroll animations with GSAP, a server-rendered "
            "years-in-data counter that ticks up every January 1, and a "
            "hardened production setup (CSP, rate limits, force-https).\n\n"
            "**Outcome.** Visitors don't just read a list of skills — "
            "they see the stack working. Source is open on GitHub so "
            "anyone can poke around the code that runs the site they're "
            "looking at."
        ),
        "image_path": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?q=80&w=1600&auto=format&fit=crop",
        "stack": "Flask, Tailwind CSS, SQLAlchemy, GSAP",
        "link_type": "github",
        "git_link": "https://github.com/ntkrv/personal_website",
    },
]

CERTIFICATES = [
    {
        "title": "Python Basic",
        "issuer": "Hillel IT School",
        "link": "https://certificate.ithillel.ua/ru/view/53638263",
    },
    {
        "title": "Python Pro",
        "issuer": "Hillel IT School",
        "link": "https://certificate.ithillel.ua/ru/view/73097786",
    },
    {
        "title": "Data Visualization",
        "issuer": "Udemy",
        "link": "https://udemy.com/certificate/data-visualization",
    },
]
