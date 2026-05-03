import os
from urllib.parse import urlparse, urljoin
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, current_user
from utils.token_utils import generate_reset_token, verify_reset_token
from utils.email_utils import send_password_reset_email
from extensions import db, limiter
from forms import ResetPasswordForm
from models import AdminUser

admin_auth_bp = Blueprint("admin_auth", __name__, url_prefix="/admin-auth")


def _is_safe_redirect(target):
    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


@admin_auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def login():
    """Login route for admin panel"""
    if current_user.is_authenticated:
        return redirect(url_for("admin_manage.dashboard"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Please enter both username and password.", "warning")
            return redirect(url_for("admin_auth.login"))

        user = AdminUser.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get("next")
            flash("Login successful!", "success")
            if not _is_safe_redirect(next_page):
                next_page = None
            return redirect(next_page or url_for("admin_manage.dashboard"))

        flash("Invalid username or password.", "danger")

    return render_template("admin/admin_login.html")


@admin_auth_bp.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("admin_auth.login"))


@admin_auth_bp.route("/forgot-password", methods=["GET", "POST"])
@limiter.limit("3 per minute", methods=["POST"])
def forgot_password():
    """Password reset email sender.

    Reset link is only ever delivered to ADMIN_RESET_EMAIL (env-configured).
    The submitted address must match — otherwise we silently ignore the
    request and still show the generic flash, so attackers cannot trigger
    a token email to an arbitrary address (account takeover) and cannot
    enumerate whether a given address is the admin's.
    """
    if request.method == "POST":
        submitted_email = (request.form.get("email") or "").strip().lower()
        admin_email = (os.getenv("ADMIN_RESET_EMAIL") or "").strip().lower()
        user = AdminUser.query.first()

        if user and admin_email and submitted_email == admin_email:
            token = generate_reset_token(user.username)
            send_password_reset_email(admin_email, token)

        flash(
            "If the address is registered, a reset link has been sent.",
            "info",
        )
        return redirect(url_for("admin_auth.login"))

    return render_template("admin/forgot_password.html")


@admin_auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def reset_password(token):
    """Handles password reset form"""
    username = verify_reset_token(token)
    if not username:
        flash("Invalid or expired token.", "danger")
        return redirect(url_for("admin_auth.forgot_password"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = AdminUser.query.filter_by(username=username).first()
        if user:
            user.set_password(form.new_password.data)
            db.session.commit()
            flash("Password has been updated successfully.", "success")
            return redirect(url_for("admin_auth.login"))
        flash("Account not found.", "danger")

    return render_template("admin/reset_password.html", form=form)
