from flask import Blueprint, render_template, redirect, url_for, flash
from forms import ContactForm

contact_bp = Blueprint('contact', __name__)

@contact_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        flash('Message has been sent', 'success')
        return redirect(url_for('contact.contact'))
    return render_template('contact.html', form=form)