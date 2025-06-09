from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_required, current_user
from app import db
from app.forms import VAPIDKeyForm
from pywebpush import generate_vapid_keys # For generating keys

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/vapid-keys', methods=['GET', 'POST'])
@login_required
def manage_vapid_keys():
    form = VAPIDKeyForm(obj=current_user) # Pre-populate form with current user's data

    if form.validate_on_submit():
        if form.generate_new.data:
            keys = generate_vapid_keys()
            current_user.vapid_public_key = keys['public_key']
            current_user.vapid_private_key = keys['private_key']
            flash('New VAPID keys generated and saved.', 'success')
        else:
            current_user.vapid_public_key = form.public_key.data
            current_user.vapid_private_key = form.private_key.data
            flash('VAPID keys updated.', 'success')

        current_user.vapid_claims_email = form.claims_email.data
        db.session.commit()
        return redirect(url_for('settings.manage_vapid_keys'))
    elif request.method == 'GET':
        # Populate form fields from current_user if they exist
        form.public_key.data = current_user.vapid_public_key
        form.private_key.data = current_user.vapid_private_key
        form.claims_email.data = current_user.vapid_claims_email


    return render_template('settings/vapid_keys.html', title='Manage VAPID Keys', form=form)
