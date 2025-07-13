import os
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_mail import Message
from forms import ContactForm
from models import db, ContactMessage
from extensions import mail
from utils.email_utils import send_contact_email

contact_bp = Blueprint("contact", __name__)


@contact_bp.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        message = ContactMessage(
            name=form.name.data, email=form.email.data, message=form.message.data
        )
        db.session.add(message)
        db.session.commit()

        send_contact_email(form.name.data, form.email.data, form.message.data)

        try:
            recipient = os.getenv("MAIL_DEFAULT_RECIPIENT")
            msg = Message(
                subject=f"New Contact Form Submission from {form.name.data}",
                recipients=[recipient],
                body=f"From: {form.name.data} <{form.email.data}>\n\n{form.message.data}",
            )
            mail.send(msg)
            flash("Message has been sent", "success")
        except Exception as e:
            flash(f"Failed to send email: {str(e)}", "danger")

        return redirect(url_for("contact.contact"))
    return render_template("index.html", form=form)
