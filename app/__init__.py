from flask import Flask
from flask_cors import CORS
from app.extensions import db, migrate
from app.config import config, Config
from app.api import expenses_bp, incomes_bp, users_bp
import os
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

def create_app(config_name=None):
    """Create Flask application using the factory pattern."""
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
    app.config["JWT_SECRET_KEY"] = os.getenv('JWT_SECRET_KEY')
    jwt = JWTManager(app)
    
    # Initialize Flask extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Register blueprints
    app.register_blueprint(expenses_bp, url_prefix='/api')
    app.register_blueprint(incomes_bp, url_prefix='/api')
    app.register_blueprint(users_bp, url_prefix='/api')
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Internal server error'}, 500
    
    # Create upload directories if they don't exist
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    CORS(app)

    return app

# Import models to ensure they're registered with SQLAlchemy
from app.models import expense