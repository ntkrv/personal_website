from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user
from models import AdminUser

admin_auth_bp = Blueprint('admin_auth', __name__, url_prefix='/admin')

@admin_auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = AdminUser.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin.index'))
        else:
            flash('Invalid username or password')
    return render_template('admin_login.html')

@admin_auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('admin_auth.login'))
