# ntkrv.dev

Personal portfolio for **Nicolas Tokariev** — a Data Analyst & Software Engineer.

A Flask + Tailwind CSS site that doubles as a working sample of the stack:
admin-managed case studies, a contact form, an agency-subcontracting offer,
a hardened deploy pipeline, and a small set of tasteful micro-interactions.

Live at **[ntkrv.dev](https://ntkrv.dev)**.

---

## Contents

- [What's on the site](#whats-on-the-site)
- [Tech stack](#tech-stack)
- [Project layout](#project-layout)
- [Local setup](#local-setup)
- [Useful CLI commands](#useful-cli-commands)
- [Architecture notes](#architecture-notes)
- [Deployment](#deployment)
- [Author & licence](#author--licence)

---

## What's on the site

| Section | Route | Notes |
| --- | --- | --- |
| Home | `/` | Hero, animated stat counters, services, about, skills, day-to-day tools marquee, case-studies preview, testimonials, agency pitch card, contact form. |
| Case studies | `/projects` | All anonymized engagements pulled from the `Project` table. |
| Case study detail | `/project/<slug>` | Renders `long_description` through the `case_format` Jinja filter (Problem / Action / Outcome blocks). |
| For agencies | `/agencies` | Dedicated subcontracting page: white-label engagement types, NDA-first process, embedded contact form. |
| Certificates | `/certificates` | Verified certifications with skill tags. |
| Contact | `POST /contact` | CSRF-protected, rate-limited, persists to DB and emails via SMTP. |
| Admin | `/admin/...` | Login-gated CRUD for projects/certificates. |

The hero stat **`Years in data`** is computed live from a context processor —
`current_year - CAREER_START_YEAR` — so it ticks up every January 1 with no
code change.

---

## Tech stack

**Backend.** Python 3.11 · Flask 2.3 · Flask-SQLAlchemy · Flask-Migrate
(Alembic) · Flask-Login · Flask-WTF · Flask-Mail · Flask-Limiter ·
Flask-Talisman · python-slugify · python-dotenv.

**Frontend.** Tailwind CSS 3.4 (dark-first with arbitrary `[.light_&]:`
variants) · vanilla JS · GSAP + ScrollTrigger for reveals and stat counters
· hand-rolled `interactions.js` for hover-tilt cards · pure-CSS marquee
and animated conic-gradient borders.

**Data.** SQLite by default (`instance/dev.db`), Postgres-ready via
`SQLALCHEMY_DATABASE_URI`.

**Tooling.** npm (Tailwind build) · black · flake8 · pytest · coverage.

---

## Project layout

```
.
├── app.py                  # create_app() factory, blueprints, context
│                           # processors, the case_format Jinja filter
├── config.py               # Dev / Test / Prod config classes
├── extensions.py           # db, mail, login_manager, limiter, talisman
├── models.py               # Project, Certificate, ContactMessage, AdminUser
├── forms.py                # WTForms (ContactForm, admin forms, auth)
├── cli.py                  # `flask seed`, `flask create-admin`
├── routes/                 # One blueprint per concern
│   ├── main.py             #   /
│   ├── projects.py         #   /projects, /project/<slug>
│   ├── certificates.py
│   ├── contact.py          #   POST /contact
│   ├── agencies.py         #   /agencies
│   ├── admin_auth.py       #   /admin/login, /admin/logout, password reset
│   ├── admin_manage.py     #   /admin/dashboard, project/cert CRUD
│   └── errors.py           #   403/404/429/500
├── services/               # Thin DB helpers
├── data/seed_data.py       # Anonymized case-study seed payload
├── templates/
│   ├── base.html           # Layout, header, footer, theme toggle
│   ├── _contact_form.html  # Reusable contact card (home + /agencies)
│   ├── index.html, agencies.html, projects.html, certificates.html
│   ├── project_detail.html # Renders long_description via case_format
│   ├── admin/...           # Admin UI
│   └── errors/...
├── static/
│   ├── src/input.css       # Tailwind source + custom utilities
│   ├── css/styles.css      # Built artifact (ignored from manual edits)
│   ├── js/scroll_animation.js  # GSAP reveals + stat counters
│   ├── js/interactions.js      # .tilt cards (pointer-driven 3D)
│   ├── js/theme_toggle.js
│   └── icons/, img/
├── migrations/             # Alembic
├── scripts/                # Bash + PowerShell helpers (run, run_dev, install, …)
├── test/                   # pytest tests
└── tailwind.config.js
```

---

## Local setup

### 1. Clone & install Python deps

```bash
git clone https://github.com/ntkrv/personal_website.git
cd personal_website

python3 -m venv .venv
source .venv/bin/activate                 # Windows: .venv\Scripts\activate

pip install -r requirements.txt
pip install -r requirements-dev.txt       # tests, lint, coverage
```

### 2. Install Tailwind tooling and build CSS

```bash
npm install
npm run build:css                         # → static/css/styles.css
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env — at minimum set SECRET_KEY and DEV_DATABASE_URL.
# SMTP variables only required if you want the contact form to email.
```

### 4. Initialise the database

```bash
flask db upgrade                          # apply migrations
flask seed                                # load anonymized case studies + certs
flask create-admin                        # prompts for password
```

### 5. Run

```bash
flask run                                 # http://127.0.0.1:5000
```

Or use the all-in-one script:

```bash
./scripts/run.sh                          # macOS / Linux
.\scripts\run_dev.ps1                     # Windows / PowerShell
```

These scripts run black + flake8, apply migrations, rebuild Tailwind, and
start Flask.

---

## Useful CLI commands

```bash
# Tailwind
npm run build:css                         # one-shot build, minified
npm run dev                               # watch mode

# Flask
flask db migrate -m "msg"                 # create a new Alembic revision
flask db upgrade                          # apply pending migrations
flask seed                                # wipe + reseed projects/certificates
flask create-admin                        # create or reset admin user

# Tests
pytest                                    # run the suite
coverage run -m pytest && coverage report
```

---

## Architecture notes

### Theme system

Dark is the default — `<html class="dark">` ships in the markup, and a
no-flash inline script in `<head>` resolves `localStorage.theme` →
system-preference → `dark` before paint. Light mode is opted into via
`html.light` and styled through Tailwind arbitrary variants:

```html
<div class="bg-ink-900 text-white
            [.light_&]:bg-softWhite [.light_&]:text-ink-900">
```

`[.light_&]:X` compiles to `.light .X` — it fires when an ancestor has
`.light`. Two extra hard overrides in `static/src/input.css`
(`html.light, html.light body { … }`) backstop the body bg in case any
utility loses the cascade fight.

### Stat counters

Stats render with their final value server-side (so no-JS users still see
`5+ / 100+ / 60% / 3`). On first scroll into view, a tiny GSAP block in
`scroll_animation.js` reads `data-stat-end` / `data-stat-suffix` and
animates from 0 → end with `power2.out`.

`years_in_data` arrives via a Flask context processor:

```python
@app.context_processor
def inject_globals():
    year = datetime.now().year
    return {
        "current_year": year,
        "years_in_data": max(year - CAREER_START_YEAR, 1),
    }
```

### Case-study rendering

`Project.long_description` is plain text with one bolded section lead per
paragraph:

```text
**Problem.** Body…

**Action.** Body…

**Outcome.** Body…
```

The `case_format` Jinja filter (registered in `app.py`) splits on blank
lines, escapes the content, and wraps each chunk so leading `**Heading.**`
becomes an eyebrow + body block. No markdown library, no `| safe` of user
input.

### Micro-interactions

- **`.tilt`** — `interactions.js` reads `pointermove` on each tagged
  card and writes `--rx` / `--ry` CSS variables. Bails on coarse
  pointers and `prefers-reduced-motion`.
- **`.marquee`** — pure CSS infinite scroll over two duplicated
  children, edge-faded with `mask-image`, paused on hover.
- **`.cta-hover-gradient`** — buttons take on the brand
  `linear-gradient(120deg, #93c5fd, #60a5fa, #a78bfa)` on hover, with
  a 1px lift and brand-blue glow.
- **`.gradient-border`** — angle-driven conic gradient rotating via
  `@property --angle`, applied to the contact card.

### Security

- **CSP** via Flask-Talisman, allow-listing `'self'` plus Google Fonts
  and Unsplash for images.
- **CSRF** on every form via Flask-WTF.
- **Rate limits** on `/contact` and admin auth endpoints via
  Flask-Limiter.
- **Force HTTPS** + secure cookies when `FLASK_ENV=production`.
- **bcrypt** hashing for admin passwords (via `werkzeug.security`).

---

## Deployment

The repo runs cleanly on any Python WSGI host (Gunicorn / uWSGI behind
Nginx). Production checklist:

- `FLASK_ENV=production`
- A real `SECRET_KEY` (long random)
- `DATABASE_URL` pointing at Postgres or a persistent SQLite path
- SMTP credentials wired up
- `npm run build:css` against the deployed checkout
- `flask db upgrade` on each deploy

The dark-first stylesheet is cache-busted via `?v=N` on `<link>` and
`<script>` tags — bump `asset_version` (or just the literal in
`base.html`) when shipping CSS/JS changes.

---

## Author & licence

**Nicolas Tokariev** — Data Analyst & Software Engineer.

- Site: [ntkrv.dev](https://ntkrv.dev)
- GitHub: [@ntkrv](https://github.com/ntkrv)
- LinkedIn: [in/ntokariev](https://www.linkedin.com/in/ntokariev/)
- Email: [contact@ntkrv.dev](mailto:contact@ntkrv.dev)

Released under the **MIT License** — use, fork, or steal whichever bits
are useful, attribution appreciated but not required.
