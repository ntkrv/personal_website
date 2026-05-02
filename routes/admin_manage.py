from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from extensions import db
from models import Project, Certificate
from forms import ProjectForm, CertificateForm
from services.project_service import (
    create_project,
    update_project,
    delete_project as delete_project_service,
)
from services.certificate_service import (
    create_certificate,
    update_certificate,
    delete_certificate as delete_certificate_service,
)

admin_manage_bp = Blueprint("admin_manage", __name__, url_prefix="/admin")


@admin_manage_bp.route("/")
@admin_manage_bp.route("/dashboard")
@login_required
def dashboard():
    projects = Project.query.all()
    certificates = Certificate.query.all()
    return render_template(
        "admin/dashboard.html", projects=projects, certificates=certificates
    )


# --- Project management ---
@admin_manage_bp.route("/project/add", methods=["GET", "POST"])
@login_required
def add_project():
    form = ProjectForm()
    if form.validate_on_submit():
        create_project(form.data)
        flash("Project added successfully!", "success")
        return redirect(url_for("admin_manage.dashboard"))
    return render_template("admin/add_project.html", form=form)


@admin_manage_bp.route("/edit_project/<int:project_id>", methods=["GET", "POST"])
@login_required
def edit_project(project_id):
    project = db.session.get(Project, project_id)
    if project is None:
        flash("Project not found.", "danger")
        return redirect(url_for("admin_manage.dashboard"))
    form = ProjectForm(obj=project)
    if form.validate_on_submit():
        update_project(project, form.data)
        flash("Project updated successfully!", "success")
        return redirect(url_for("admin_manage.dashboard"))
    return render_template("admin/edit_project.html", form=form)


@admin_manage_bp.route("/delete_project/<int:project_id>", methods=["POST"])
@login_required
def delete_project(project_id):
    project = db.session.get(Project, project_id)
    if project is None:
        flash("Project not found.", "danger")
        return redirect(url_for("admin_manage.dashboard"))
    delete_project_service(project)
    flash("Project deleted.", "warning")
    return redirect(url_for("admin_manage.dashboard"))


# --- Certificate management ---
@admin_manage_bp.route("/certificate/add", methods=["GET", "POST"])
@login_required
def add_certificate():
    form = CertificateForm()
    if form.validate_on_submit():
        create_certificate(form.data)
        flash("Certificate added successfully.", "success")
        return redirect(url_for("admin_manage.dashboard"))
    return render_template("admin/add_certificate.html", form=form)


@admin_manage_bp.route(
    "/edit_certificate/<int:certificate_id>", methods=["GET", "POST"]
)
@login_required
def edit_certificate(certificate_id):
    certificate = db.session.get(Certificate, certificate_id)
    if certificate is None:
        flash("Certificate not found.", "danger")
        return redirect(url_for("admin_manage.dashboard"))
    form = CertificateForm(obj=certificate)
    if form.validate_on_submit():
        update_certificate(certificate, form.data)
        flash("Certificate updated successfully!", "success")
        return redirect(url_for("admin_manage.dashboard"))
    return render_template("admin/edit_certificate.html", form=form)


@admin_manage_bp.route("/delete_certificate/<int:certificate_id>", methods=["POST"])
@login_required
def delete_certificate(certificate_id):
    certificate = db.session.get(Certificate, certificate_id)
    if certificate is None:
        flash("Certificate not found.", "danger")
        return redirect(url_for("admin_manage.dashboard"))
    delete_certificate_service(certificate)
    flash("Certificate deleted.", "warning")
    return redirect(url_for("admin_manage.dashboard"))
