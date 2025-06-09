from app import db
from datetime import datetime

class Template(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    # e.g., 'popup_custom_html', 'hellobar_message_text', 'banner_image_url', 'email_body_html'
    template_type = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False) # Actual template content (HTML, text, JSON for complex settings)
    description = db.Column(db.String(255), nullable=True) # Optional description

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    owner = db.relationship('User', backref=db.backref('templates', lazy=True))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Template {self.name} ({self.template_type})>'
