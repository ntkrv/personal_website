from flask import Blueprint, render_template
from models import Project
from forms import ContactForm

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    form = ContactForm()
    projects = Project.query.limit(3).all()
    return render_template("index.html", form=form, projects=projects)


@main_bp.app_errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404
