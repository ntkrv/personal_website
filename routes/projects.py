from flask import Blueprint, render_template, redirect, url_for, flash
from models import Project
from forms import ProjectForm
from extensions import db

projects_bp = Blueprint("projects", __name__)


@projects_bp.route("/projects")
def projects():
    projects = Project.query.all()
    return render_template("projects.html", projects=projects)


@projects_bp.route("/projects/add", methods=["GET", "POST"])
def add_project():
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(
            title=form.title.data,
            short_description=form.short_description.data,
            long_description=form.long_description.data,
            image_path=form.image_path.data,
            stack=form.stack.data,
            link_type=form.link_type.data,
            git_link=form.git_link.data,
        )
        project.generate_slug()
        db.session.add(project)
        db.session.commit()
        flash("Project added successfully!", "success")
        return redirect(url_for("projects.projects"))
    return render_template("admin/add_project.html", form=form)


@projects_bp.route("/project/<slug>")
def project_detail(slug):
    project = Project.query.filter_by(slug=slug).first_or_404()
    return render_template("project_detail.html", project=project)


@projects_bp.route("/project/<int:project_id>")
def project_redirect(project_id):
    project = Project.query.get_or_404(project_id)
    return redirect(url_for("projects.project_detail", slug=project.slug), code=301)
