from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import json # For Jinja context
from flask_login import LoginManager # Add LoginManager
import os

db = SQLAlchemy()
login_manager = LoginManager() # Initialize LoginManager
login_manager.login_view = 'auth.login' # Specify the login view route
login_manager.login_message_category = 'info' # Optional: for flash messages

def create_app():
    app = Flask(__name__)

    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_fallback_secret_key_change_me') # Use env var
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, '..', 'site.db'))
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app) # Initialize Flask-Login with the app

    # User loader function for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from .models.user import User # Import here to avoid circular dependency
        return User.query.get(int(user_id))

    with app.app_context():
        from .models import user, campaign, template # Ensure models are imported
        db.create_all() # Create tables

        # Import and register blueprints
        from .routes.auth import auth_bp
        app.register_blueprint(auth_bp, url_prefix='/auth')

        from .routes.main import main_bp # Assuming a main blueprint for other routes
        app.register_blueprint(main_bp)

        from .routes.settings import settings_bp
        app.register_blueprint(settings_bp, url_prefix='/settings')

        from .routes.hellobar import hellobar_bp
        app.register_blueprint(hellobar_bp, url_prefix='/hellobar')

        from .routes.banner import banner_bp
        app.register_blueprint(banner_bp, url_prefix='/banner')

        from .routes.popup import popup_bp
        app.register_blueprint(popup_bp, url_prefix='/popup')

        from .routes.coupon import coupon_bp
        app.register_blueprint(coupon_bp, url_prefix='/coupon')

        from .routes.templates_mgmt import templates_bp
        app.register_blueprint(templates_bp, url_prefix='/templates')

    @app.context_processor
    def utility_processor():
        return dict(json=json)

    return app
