from flask import Blueprint, current_app, render_template, redirect, url_for, flash, request
from forms import ContactForm
from extensions import db, limiter
from models import ContactMessage
from utils.email_utils import send_contact_email


contact_bp = Blueprint("contact", __name__)


@contact_bp.route("/contact", methods=["GET", "POST"])
@limiter.limit("5 per hour", methods=["POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        # Honeypot trap. Real users never see the `website` field, so
        # any value there means a bot. We log the IP and pretend success
        # so the bot doesn't retry, but skip DB + email entirely.
        if form.website.data:
            current_app.logger.info(
                "Contact honeypot triggered from IP: %s", request.remote_addr
            )
            flash("Message has been sent successfully.", "success")
            return redirect(url_for("main.index"))

        message = ContactMessage(
            name=form.name.data,
            email=form.email.data,
            message=form.message.data,
        )
        db.session.add(message)
        db.session.commit()

        email_sent = send_contact_email(
            form.name.data, form.email.data, form.message.data
        )

        if email_sent:
            flash("Message has been sent successfully.", "success")
        else:
            flash("Failed to send email. Please try again later.", "danger")

        return redirect(url_for("main.index"))

    return render_template("index.html", form=form)
