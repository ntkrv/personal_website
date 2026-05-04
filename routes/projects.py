from flask import Blueprint, render_template, redirect, url_for
from models import Project

projects_bp = Blueprint("projects", __name__)


# Slug substring → demo endpoint. We match by substring so admin-edited
# titles ("Logistics KPI workspace…" vs "Logistics KPI dashboard…") still
# resolve. Keep this list tiny and explicit.
DEMO_BY_SLUG_FRAGMENT = {
    "logistics-kpi": "demo.logistics_kpi",
}


def _demo_endpoint_for(project: Project) -> str | None:
    slug = (project.slug or "").lower()
    for fragment, endpoint in DEMO_BY_SLUG_FRAGMENT.items():
        if fragment in slug:
            return endpoint
    return None


@projects_bp.route("/projects")
def projects():
    projects = Project.query.all()
    return render_template("projects.html", projects=projects)


@projects_bp.route("/project/<slug>")
def project_detail(slug):
    project = Project.query.filter_by(slug=slug).first_or_404()
    demo_endpoint = _demo_endpoint_for(project)
    demo_url = url_for(demo_endpoint) if demo_endpoint else None
    return render_template(
        "project_detail.html", project=project, demo_url=demo_url
    )


@projects_bp.route("/project/<int:project_id>")
def project_redirect(project_id):
    project = Project.query.get_or_404(project_id)
    return redirect(url_for("projects.project_detail", slug=project.slug), code=301)
