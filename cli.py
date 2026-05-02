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


def register_cli(app) -> None:
    app.cli.add_command(create_admin_command)
    app.cli.add_command(seed_command)
