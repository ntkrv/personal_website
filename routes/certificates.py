from flask import Blueprint, render_template
from models import Certificate

certificates_bp = Blueprint("certificates", __name__)


@certificates_bp.route("/certificates")
def certificates():
    certificates = Certificate.query.all()
    return render_template("certificates.html", certificates=certificates)
