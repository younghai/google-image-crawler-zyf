from flask import Blueprint, render_template, url_for, flash, redirect, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.coupon import Coupon
from app.forms import CouponForm
import datetime

coupon_bp = Blueprint('coupon', __name__)

@coupon_bp.route('/list')
@login_required
def list_coupons():
    coupons = Coupon.query.filter_by(owner=current_user).order_by(Coupon.created_at.desc()).all()
    return render_template('coupon/list_coupons.html', title='My Coupons', coupons=coupons)

@coupon_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_coupon():
    form = CouponForm()
    if form.validate_on_submit():
        code_to_save = form.code.data
        if not code_to_save or form.generate_code_checkbox.data: # If field is blank or checkbox is ticked
            code_to_save = Coupon.generate_code()
            # Re-validate generated code for extremely rare collisions if form didn't catch it (form validation runs on original data)
            while Coupon.query.filter_by(code=code_to_save).first():
                 code_to_save = Coupon.generate_code()

        new_coupon = Coupon(
            code=code_to_save,
            description=form.description.data,
            discount_type=form.discount_type.data,
            discount_value=form.discount_value.data,
            valid_from=form.valid_from.data,
            valid_to=form.valid_to.data,
            max_uses=form.max_uses.data if form.max_uses.data is not None and form.max_uses.data > 0 else None,
            is_active=form.is_active.data,
            owner=current_user
        )
        db.session.add(new_coupon)
        db.session.commit()
        flash(f'Coupon "{new_coupon.code}" created successfully!', 'success')
        return redirect(url_for('coupon.list_coupons'))
    return render_template('coupon/create_edit_coupon.html', title='Create Coupon', form=form, legend='New Coupon', coupon_id_hidden=None)

@coupon_bp.route('/<int:coupon_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_coupon(coupon_id):
    coupon = Coupon.query.get_or_404(coupon_id)
    if coupon.owner != current_user:
        flash('You do not have permission to edit this coupon.', 'danger')
        return redirect(url_for('coupon.list_coupons'))

    # Pass coupon_id to the form context for validation logic
    form = CouponForm(obj=coupon)

    if form.validate_on_submit():
        # Code generation/handling logic for edit
        original_code = coupon.code
        new_code_data = form.code.data

        if not new_code_data: # If user blanks out the code field
            flash('Coupon code cannot be empty.', 'danger')
            return render_template('coupon/create_edit_coupon.html', title='Edit Coupon', form=form, legend=f'Edit {original_code}', coupon_id_hidden=coupon.id)

        coupon.code = new_code_data
        coupon.description = form.description.data
        coupon.discount_type = form.discount_type.data
        coupon.discount_value = form.discount_value.data
        coupon.valid_from = form.valid_from.data
        coupon.valid_to = form.valid_to.data
        coupon.max_uses = form.max_uses.data if form.max_uses.data is not None and form.max_uses.data > 0 else None
        coupon.is_active = form.is_active.data
        # uses_count is not editable by user

        db.session.commit()
        flash(f'Coupon "{coupon.code}" updated successfully!', 'success')
        return redirect(url_for('coupon.list_coupons'))
    elif request.method == 'GET':
        # DateTime fields need to be pre-filled correctly if None
        form.valid_from.data = coupon.valid_from if coupon.valid_from else None
        form.valid_to.data = coupon.valid_to if coupon.valid_to else None
        form.max_uses.data = coupon.max_uses if coupon.max_uses is not None else 0 # Show 0 if None for consistency in IntegerField

    return render_template('coupon/create_edit_coupon.html', title='Edit Coupon', form=form, legend=f'Edit {coupon.code}', coupon_id_hidden=coupon.id)

@coupon_bp.route('/<int:coupon_id>/delete', methods=['POST'])
@login_required
def delete_coupon(coupon_id):
    coupon = Coupon.query.get_or_404(coupon_id)
    if coupon.owner != current_user:
        flash('You do not have permission to delete this coupon.', 'danger')
        return redirect(url_for('coupon.list_coupons'))

    db.session.delete(coupon)
    db.session.commit()
    flash(f'Coupon "{coupon.code}" deleted successfully!', 'success')
    return redirect(url_for('coupon.list_coupons'))

EOF
