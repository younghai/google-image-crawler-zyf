from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.campaign import Campaign # Import Campaign model
from app.models.coupon import Coupon # Import Coupon model for listing too

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/index')
def index():
    return render_template('main/index.html', title='Home')

@main_bp.route('/status')
def status():
    try:
        db.session.execute(db.text('SELECT 1')) # Use db.text for SQLAlchemy 2.0
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    return jsonify(status="ok", db_status=db_status)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Fetch all campaigns owned by the current user
    campaigns = Campaign.query.filter_by(owner=current_user).order_by(Campaign.created_at.desc()).all()

    # Fetch all coupons owned by the current user (if we want to list them on dashboard too)
    coupons = Coupon.query.filter_by(owner=current_user).order_by(Coupon.created_at.desc()).all()

    # We need to generate correct URLs based on campaign_type in the template.
    # We can pass campaign types and their corresponding blueprint edit/delete views.
    # Or, more simply, construct them in the template using if/else on campaign.campaign_type.

    return render_template('main/dashboard.html',
                           title='Dashboard',
                           campaigns=campaigns,
                           coupons=coupons) # Pass coupons to the template
