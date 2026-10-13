from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from extensions import db
from models import Project, Certificate, ContactMessage
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
from utils.uploads import delete_image_if_orphaned, save_image

admin_manage_bp = Blueprint("admin_manage", __name__, url_prefix="/admin")


def _project_data_with_image(form, current_path: str | None = None) -> dict:
    """Build the dict passed to the project service from form data.

    Upload trumps URL trumps current value. The `image_file` field is
    stripped because services don't expect it.
    """
    data = dict(form.data)
    uploaded = save_image(data.pop("image_file", None))
    if uploaded:
        data["image_path"] = uploaded
    elif not data.get("image_path") and current_path:
        # User cleared URL field on edit but didn't upload a new file —
        # keep the existing image instead of wiping it.
        data["image_path"] = current_path
    return data


@admin_manage_bp.route("/")
@admin_manage_bp.route("/dashboard")
@login_required
def dashboard():
    projects = Project.query.all()
    certificates = Certificate.query.all()
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template(
        "admin/dashboard.html",
        projects=projects,
        certificates=certificates,
        messages=messages,
    )


# --- Project management ---
@admin_manage_bp.route("/project/add", methods=["GET", "POST"])
@login_required
def add_project():
    form = ProjectForm()
    if form.validate_on_submit():
        create_project(_project_data_with_image(form))
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
        old_image = project.image_path
        update_project(project, _project_data_with_image(form, old_image))
        if project.image_path != old_image:
            delete_image_if_orphaned(old_image)
        flash("Project updated successfully!", "success")
        return redirect(url_for("admin_manage.dashboard"))
    return render_template("admin/edit_project.html", form=form, project=project)


@admin_manage_bp.route("/delete_project/<int:project_id>", methods=["POST"])
@login_required
def delete_project(project_id):
    project = db.session.get(Project, project_id)
    if project is None:
        flash("Project not found.", "danger")
        return redirect(url_for("admin_manage.dashboard"))
    image = project.image_path
    delete_project_service(project)
    delete_image_if_orphaned(image)
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


# --- Contact messages ---
@admin_manage_bp.route("/delete_message/<int:message_id>", methods=["POST"])
@login_required
def delete_message(message_id):
    message = db.session.get(ContactMessage, message_id)
    if message is None:
        flash("Message not found.", "danger")
        return redirect(url_for("admin_manage.dashboard"))
    db.session.delete(message)
    db.session.commit()
    flash("Message deleted.", "warning")
    return redirect(url_for("admin_manage.dashboard", _anchor="messages"))
