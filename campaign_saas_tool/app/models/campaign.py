from app import db
from datetime import datetime

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    campaign_type = db.Column(db.String(50), nullable=False) # e.g., 'web_push', 'popup', 'banner'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Specific campaign settings can be stored as JSON or in related tables
    settings = db.Column(db.Text) # Using Text to store JSON settings for simplicity

    templates = db.relationship('Template', backref='campaign', lazy=True)

    def __repr__(self):
        return f'<Campaign {self.name}>'
