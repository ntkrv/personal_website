from flask import Blueprint, render_template, redirect, url_for
from models import Project

projects_bp = Blueprint("projects", __name__)


@projects_bp.route("/projects")
def projects():
    projects = Project.query.all()
    return render_template("projects.html", projects=projects)


@projects_bp.route("/project/<slug>")
def project_detail(slug):
    project = Project.query.filter_by(slug=slug).first_or_404()
    return render_template("project_detail.html", project=project)


@projects_bp.route("/project/<int:project_id>")
def project_redirect(project_id):
    project = Project.query.get_or_404(project_id)
    return redirect(url_for("projects.project_detail", slug=project.slug), code=301)
