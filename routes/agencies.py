from flask import Blueprint, render_template

agencies_bp = Blueprint("agencies", __name__)


@agencies_bp.route("/agencies")
def agencies():
    return render_template("agencies.html")
