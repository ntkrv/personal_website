from flask import Blueprint, render_template

from forms import ContactForm

agencies_bp = Blueprint("agencies", __name__)


@agencies_bp.route("/agencies")
def agencies():
    form = ContactForm()
    return render_template("agencies.html", form=form)
