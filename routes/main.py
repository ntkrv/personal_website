from flask import Blueprint, render_template
from models import Project

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    projects = Project.query.limit(3).all()
    return render_template('index.html', projects=projects)

@main_bp.route('/about')
def about():
    return render_template('about.html')
