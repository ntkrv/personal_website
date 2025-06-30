from flask import Blueprint, render_template, redirect, url_for, flash, request
from forms import ContactForm
from models import db, ContactMessage

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

        flash("Message has been sent", "success")
        return redirect(url_for("contact.contact"))  # stay on same page
    return render_template("index.html", form=form)
