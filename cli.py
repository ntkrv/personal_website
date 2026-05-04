"""Flask CLI commands.

Register via `_register_cli` from `app.py`. Usage:
    flask create-admin
    flask seed
"""
import os

import click
from flask.cli import with_appcontext

from extensions import db
from models import AdminUser, Project, Certificate


@click.command("create-admin")
@click.option("--username", default=lambda: os.getenv("ADMIN_USERNAME"))
@click.option(
    "--password",
    default=lambda: os.getenv("ADMIN_PASSWORD"),
    prompt=True,
    hide_input=True,
    confirmation_prompt=False,
)
@with_appcontext
def create_admin_command(username: str, password: str) -> None:
    """Create or update an admin user. Reads ADMIN_USERNAME/ADMIN_PASSWORD by default."""
    if not username or not password:
        raise click.UsageError(
            "username and password are required (set ADMIN_USERNAME / ADMIN_PASSWORD or pass via flags)"
        )

    user = AdminUser.query.filter_by(username=username).first()
    if user is None:
        user = AdminUser(username=username)
        user.set_password(password)
        db.session.add(user)
        click.echo(f"Created admin '{username}'")
    else:
        user.set_password(password)
        click.echo(f"Updated password for admin '{username}'")
    db.session.commit()


@click.command("seed")
@with_appcontext
def seed_command() -> None:
    """Seed the database with sample projects and certificates."""
    from data.seed_data import PROJECTS, CERTIFICATES

    Project.query.delete()
    Certificate.query.delete()

    for p in PROJECTS:
        db.session.add(Project(**p))
    for c in CERTIFICATES:
        db.session.add(Certificate(**c))

    db.session.commit()
    click.echo(
        f"Seeded {len(PROJECTS)} projects and {len(CERTIFICATES)} certificates."
    )


@click.command("sync-logistics-demo")
@with_appcontext
def sync_logistics_demo_command() -> None:
    """Upsert the Logistics KPI cockpit case study to match the live demo.

    Matches the existing project by 'logistics-kpi' slug fragment and
    overwrites title / short_description / long_description / stack /
    image_path. The slug itself is left alone so inbound /project/<slug>
    URLs and the demo-link mapping in routes/projects.py keep working.
    If no matching record exists, a fresh one is created (slug is then
    auto-derived from the new title).
    """
    from data.seed_data import PROJECTS

    payload = next(
        (p for p in PROJECTS if "logistics" in p["title"].lower()
         and "kpi" in p["title"].lower()),
        None,
    )
    if payload is None:
        raise click.UsageError(
            "Couldn't find the Logistics KPI entry in data/seed_data.py."
        )

    project = (Project.query
               .filter(Project.slug.contains("logistics-kpi"))
               .first())

    if project is None:
        project = Project(**payload)
        db.session.add(project)
        action = "created"
    else:
        for field, value in payload.items():
            setattr(project, field, value)
        action = "updated"

    db.session.commit()
    click.echo(
        f"Logistics KPI cockpit project {action} (slug: {project.slug})."
    )


def register_cli(app) -> None:
    app.cli.add_command(create_admin_command)
    app.cli.add_command(seed_command)
    app.cli.add_command(sync_logistics_demo_command)
