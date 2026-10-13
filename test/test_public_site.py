import re

import pytest

from app import _case_format, create_app
from cli import seed_command
from config import TestingConfig
from extensions import db, mail
from models import AdminUser, Certificate, ContactMessage, Project


def _contact(client, **overrides):
    data = {"name": "Ann", "email": "ann@example.com", "message": "Hello"}
    data.update(overrides)
    return client.post("/contact", data=data)


# --- Contact form -----------------------------------------------------

def test_contact_honeypot_drops_submission(client):
    with mail.record_messages() as outbox:
        response = _contact(client, website="http://spam.example")

    assert response.status_code == 302
    assert ContactMessage.query.count() == 0
    assert outbox == []


def test_contact_validation_error_keeps_home_page_projects(client):
    db.session.add(Project(title="Visible case study", short_description="x"))
    db.session.commit()

    response = _contact(client, email="not-an-email")

    assert response.status_code == 200
    assert b"Visible case study" in response.data
    assert ContactMessage.query.count() == 0


# --- CSRF and logout --------------------------------------------------

class CsrfConfig(TestingConfig):
    WTF_CSRF_ENABLED = True


def test_csrf_rejects_post_without_token():
    app = create_app(CsrfConfig)
    with app.app_context():
        db.create_all()
        response = app.test_client().post(
            "/contact",
            data={"name": "Ann", "email": "ann@example.com", "message": "Hi"},
        )
        assert response.status_code == 400
        assert ContactMessage.query.count() == 0
        db.drop_all()


def test_logout_is_post_only(client):
    user = AdminUser(username="admin")
    user.set_password("admin-password-123")
    db.session.add(user)
    db.session.commit()
    client.post(
        "/admin-auth/login",
        data={"username": "admin", "password": "admin-password-123"},
    )

    assert client.get("/admin-auth/logout").status_code == 405
    assert client.get("/admin/dashboard").status_code == 200

    client.post("/admin-auth/logout")
    assert client.get("/admin/dashboard").status_code == 302


# --- CSP ----------------------------------------------------------------

def test_csp_uses_nonce_instead_of_unsafe_inline(client):
    response = client.get("/")
    csp = response.headers["Content-Security-Policy"]
    script_src = next(d for d in csp.split(";") if d.strip().startswith("script-src"))

    assert "'unsafe-inline'" not in script_src
    nonce = re.search(r"'nonce-([^']+)'", script_src).group(1)

    html = response.get_data(as_text=True)
    inline = re.findall(r"<script(?![^>]*\bsrc=)([^>]*)>", html)
    assert inline, "expected inline scripts on the home page"
    for attrs in inline:
        assert f'nonce="{nonce}"' in attrs
    assert not re.search(r"\son[a-z]+=", html), "inline event handler found"


def test_csp_nonce_changes_per_response(client):
    def nonce():
        csp = client.get("/").headers["Content-Security-Policy"]
        return re.search(r"'nonce-([^']+)'", csp).group(1)

    assert nonce() != nonce()


# --- case_format filter -----------------------------------------------

def test_case_format_escapes_html_and_builds_sections():
    html = str(_case_format("**Problem.** <script>x</script>\n\nPlain <b>text</b>"))

    assert '<h3 class="case-heading">Problem</h3>' in html
    assert "<script>" not in html and "&lt;script&gt;" in html
    assert "&lt;b&gt;text&lt;/b&gt;" in html


def test_case_format_empty():
    assert str(_case_format(None)) == ""


# --- Public pages -----------------------------------------------------

def test_robots_and_sitemap(client):
    db.session.add(Project(title="Data Pipeline"))
    db.session.commit()

    assert b"Disallow: /admin/" in client.get("/robots.txt").data
    sitemap = client.get("/sitemap.xml")
    assert sitemap.mimetype == "application/xml"
    assert b"https://ntkrv.dev/project/data-pipeline" in sitemap.data


def test_project_id_redirects_to_slug(client):
    project = Project(title="Data Pipeline")
    db.session.add(project)
    db.session.commit()

    response = client.get(f"/project/{project.id}")
    assert response.status_code == 301
    assert response.headers["Location"].endswith("/project/data-pipeline")
    assert client.get("/project/999").status_code == 404


@pytest.mark.parametrize(
    "path", ["/", "/projects", "/certificates", "/agencies", "/privacy"]
)
def test_public_pages_render(client, path):
    assert client.get(path).status_code == 200


# --- Logistics demo ---------------------------------------------------

def test_demo_page_and_api(client):
    assert client.get("/demo/logistics-kpi").status_code == 200

    full = client.get("/demo/logistics-kpi/api/figures").get_json()
    recent = client.get("/demo/logistics-kpi/api/figures?period=30").get_json()
    assert full["figures"] and full["trucks"]
    assert full["kpis"] != recent["kpis"]

    # Unknown periods fall back to full history instead of erroring.
    junk = client.get("/demo/logistics-kpi/api/figures?period=7; drop").get_json()
    assert junk["kpis"] == full["kpis"]


def test_demo_truck_drilldown(client):
    trucks = client.get("/demo/logistics-kpi/api/figures").get_json()["trucks"]
    truck_id = trucks[0]["truck_id"]

    assert client.get(f"/demo/logistics-kpi/api/truck/{truck_id}").status_code == 200
    assert client.get("/demo/logistics-kpi/api/truck/NOPE").status_code == 404


# --- CLI ----------------------------------------------------------------

def test_seed_requires_confirmation(app, runner):
    db.session.add(Certificate(title="Keep me"))
    db.session.commit()

    aborted = runner.invoke(seed_command, input="n\n")
    assert aborted.exit_code != 0
    assert Certificate.query.filter_by(title="Keep me").count() == 1

    done = runner.invoke(seed_command, ["--yes"])
    assert done.exit_code == 0, done.output
    assert Certificate.query.filter_by(title="Keep me").count() == 0
    assert Project.query.count() > 0
