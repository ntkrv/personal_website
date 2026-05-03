from datetime import date
from flask import Blueprint, Response, render_template, url_for
from models import Project
from forms import ContactForm

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    form = ContactForm()
    projects = Project.query.limit(3).all()
    return render_template("index.html", form=form, projects=projects)


@main_bp.route("/robots.txt")
def robots():
    body = (
        "User-agent: *\n"
        "Disallow: /admin/\n"
        "Disallow: /admin-auth/\n"
        "Allow: /\n"
        "Sitemap: https://ntkrv.dev/sitemap.xml\n"
    )
    return Response(body, mimetype="text/plain")


@main_bp.route("/sitemap.xml")
def sitemap():
    today = date.today().isoformat()
    urls = [
        ("https://ntkrv.dev/", "1.0", "weekly"),
        ("https://ntkrv.dev" + url_for("projects.projects"), "0.9", "weekly"),
        ("https://ntkrv.dev" + url_for("certificates.certificates"), "0.7", "monthly"),
        ("https://ntkrv.dev" + url_for("agencies.agencies"), "0.8", "monthly"),
    ]
    for project in Project.query.all():
        urls.append((
            "https://ntkrv.dev"
            + url_for("projects.project_detail", slug=project.slug),
            "0.6",
            "monthly",
        ))

    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, priority, changefreq in urls:
        parts.append(
            f"<url><loc>{loc}</loc><lastmod>{today}</lastmod>"
            f"<changefreq>{changefreq}</changefreq>"
            f"<priority>{priority}</priority></url>"
        )
    parts.append("</urlset>")
    return Response("\n".join(parts), mimetype="application/xml")
