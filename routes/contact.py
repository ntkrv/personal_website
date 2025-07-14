from flask import Blueprint, render_template, redirect, url_for, flash
from forms import ContactForm
from models import db, ContactMessage
from utils.email_utils import send_contact_email

contact_bp = Blueprint("contact", __name__)


@contact_bp.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
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

        return redirect(url_for("contact.contact"))

    return render_template("index.html", form=form)
