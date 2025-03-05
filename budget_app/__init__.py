from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import google.generativeai as genai

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    from .config import Config
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Configure Gemini
    genai.configure(api_key=Config.GEMINI_API_KEY)
    
    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.main import main_bp
    from .routes.budget import budget_bp
    from .routes.payment import payment_bp
    from .routes.gemini import gemini_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(budget_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(gemini_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app