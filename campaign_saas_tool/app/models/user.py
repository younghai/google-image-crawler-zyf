from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    campaigns = db.relationship('Campaign', backref='owner', lazy=True)

    # VAPID keys for web push
    vapid_public_key = db.Column(db.String(200), nullable=True)
    vapid_private_key = db.Column(db.String(200), nullable=True)
    # Email for VAPID (optional, but good practice)
    vapid_claims_email = db.Column(db.String(120), nullable=True)


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'
