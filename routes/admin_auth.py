import os
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, current_user
from utils.token_utils import generate_reset_token, verify_reset_token
from utils.email_utils import send_password_reset_email
from extensions import db
from forms import ResetPasswordForm
from models import AdminUser

admin_auth_bp = Blueprint("admin_auth", __name__, url_prefix="/admin-auth")


@admin_auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect("/admin")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = AdminUser.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page or "/admin")
        else:
            flash("Invalid username or password")

    return render_template("admin/admin_login.html")


@admin_auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("admin_auth.login"))


@admin_auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        submitted_email = request.form.get("email")
        valid_email = os.getenv("MAIL_USERNAME")

        if submitted_email != valid_email:
            flash("Invalid email address", "danger")
            return redirect(url_for("admin_auth.forgot_password"))

        token = generate_reset_token(submitted_email)
        send_password_reset_email(submitted_email, token)
        flash("Password reset link sent to your email.", "info")
        return redirect(url_for("admin_auth.login"))

    return render_template("admin/forgot_password.html")


@admin_auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    email = verify_reset_token(token)
    if not email:
        flash("Invalid or expired token", "danger")
        return redirect(url_for("admin_auth.forgot_password"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = AdminUser.query.filter_by(username=os.getenv("ADMIN_USERNAME")).first()
        if user:
            user.set_password(form.new_password.data)
            db.session.commit()
            flash("Password has been updated.", "success")
            return redirect(url_for("admin_auth.login"))

    return render_template("admin/reset_password.html", form=form)
