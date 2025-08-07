from app import db
from datetime import datetime
import string
import random

class Coupon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    discount_type = db.Column(db.String(20), nullable=False, default='percentage') # 'percentage', 'fixed_amount'
    discount_value = db.Column(db.Float, nullable=False)
    valid_from = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    valid_to = db.Column(db.DateTime, nullable=True)
    max_uses = db.Column(db.Integer, nullable=True) # Total allowed uses
    uses_count = db.Column(db.Integer, default=0) # How many times used
    # min_purchase_amount = db.Column(db.Float, nullable=True) # Future consideration
    is_active = db.Column(db.Boolean, default=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    owner = db.relationship('User', backref=db.backref('coupons', lazy=True))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Coupon {self.code}>'

    @staticmethod
    def generate_code(length=8):
        # Generate a random alphanumeric code
        # Ensure it's unique by checking the database (simplified here, retry logic might be needed for high volume)
        chars = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(random.choice(chars) for _ in range(length))
            if not Coupon.query.filter_by(code=code).first():
                return code
