from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
)
from flask_login import login_required
from models import db, Project, Certificate
from forms import ProjectForm, CertificateForm

admin_manage_bp = Blueprint("admin_manage", __name__, url_prefix="/admin")


# --- Dashboard redirects ---
@admin_manage_bp.route("/dashboard")
@admin_manage_bp.route("/dashboard/")
def dashboard_redirect():
    return redirect("/admin", code=301)


@admin_manage_bp.route("/dashboard/project/")
def dashboard_project_redirect():
    return redirect("/admin/project/", code=301)


@admin_manage_bp.route("/dashboard/certificate/")
def dashboard_certificate_redirect():
    return redirect("/admin/certificate/", code=301)


# --- Project management ---
@admin_manage_bp.route("/project/add", methods=["GET", "POST"])
@login_required
def add_project():
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(
            title=form.title.data,
            short_description=form.short_description.data,
            long_description=form.long_description.data,
            image_path=form.image_path.data,
            stack=form.stack.data,
            link_type=form.link_type.data,  # "github" or "gdrive"
            git_link=form.git_link.data,
        )
        db.session.add(project)
        db.session.commit()
        flash("Project added successfully!", "success")
        return redirect(url_for("admin.index"))
    return render_template("admin/add_project.html", form=form)


@admin_manage_bp.route("/edit_project/<int:project_id>", methods=["GET", "POST"])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    form = ProjectForm(obj=project)
    if form.validate_on_submit():
        form.populate_obj(project)
        db.session.commit()
        flash("Project updated successfully!", "success")
        return redirect(url_for("admin.index"))
    return render_template("admin/edit_project.html", form=form)


@admin_manage_bp.route("/delete_project/<int:project_id>", methods=["POST"])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    flash("Project deleted.", "warning")
    return redirect(url_for("admin.index"))


# --- Certificate management ---
@admin_manage_bp.route("/certificate/add", methods=["GET", "POST"])
@login_required
def add_certificate():
    form = CertificateForm()
    if form.validate_on_submit():
        certificate = Certificate(
            title=form.title.data,
            issuer=form.issuer.data,
            link=form.link.data,
        )
        db.session.add(certificate)
        db.session.commit()
        flash("Certificate added successfully.", "success")
        return redirect("/admin")
    return render_template("admin/add_certificate.html", form=form)


@admin_manage_bp.route(
    "/edit_certificate/<int:certificate_id>", methods=["GET", "POST"]
)
@login_required
def edit_certificate(certificate_id):
    certificate = Certificate.query.get_or_404(certificate_id)
    form = CertificateForm(obj=certificate)
    if form.validate_on_submit():
        form.populate_obj(certificate)
        db.session.commit()
        flash("Certificate updated successfully!", "success")
        return redirect(url_for("admin.index"))
    return render_template("admin/edit_certificate.html", form=form)


@admin_manage_bp.route("/delete_certificate/<int:certificate_id>", methods=["POST"])
@login_required
def delete_certificate(certificate_id):
    certificate = Certificate.query.get_or_404(certificate_id)
    db.session.delete(certificate)
    db.session.commit()
    flash("Certificate deleted.", "warning")
    return redirect(url_for("admin.index"))
