from datetime import timedelta
from flask import Flask
from flask_login import LoginManager
from flasgger import Swagger
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
import os
from app.db.db import db
from app.db.db_models import User
from app.routes.web import web
from app.routes.admin import admin
from app.routes.globals import globals
from app.routes.api_v1 import api_v1
from app.utils import get_gravatar_url, get_user_timezone

class Config:
    @classmethod
    def validate_config(cls):
        required_vars = ['CONNECTION_STRING', 'SECRET_KEY']
        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    SQLALCHEMY_DATABASE_URI = os.getenv('CONNECTION_STRING')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    REMEMBER_COOKIE_DURATION = timedelta(days=7)

class ProductionConfig(Config):
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    # Security Headers
    STRICT_TRANSPORT_SECURITY = 'max-age=31536000; includeSubDomains'
    CONTENT_SECURITY_POLICY = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';"
    X_CONTENT_TYPE_OPTIONS = 'nosniff'
    X_FRAME_OPTIONS = 'SAMEORIGIN'

    @classmethod
    def validate_config(cls):
        super().validate_config()
        if os.getenv('FLASK_ENV') == 'production' and not os.getenv('CONNECTION_STRING', '').startswith('mysql+ssl://'):
            raise ValueError("Production environment requires SSL database connection")

def create_app():

    # Initialize Flask App
    app = Flask(__name__)

    # Load configuration from class
    app.config.from_object(ProductionConfig if os.getenv('FLASK_ENV') == 'production' else Config)

    # Initialize Swagger
    swagger_config = {
        'headers': [],
        'specs': [
            {
                'endpoint': 'apispec_1',
                'route': '/apispec_1.json',
                'rule_filter': lambda rule: True,
                'model_filter': lambda tag: True,
            }
        ],
        'static_url_path': '/flasgger_static',
        'swagger_ui': True if os.getenv('FLASK_ENV') != 'production' else False,
        'specs_route': '/docs',
        'securityDefinitions': {
            'APIKeyAuth': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization',
                'description': 'Enter your API key as: Bearer <API_KEY>'
            }
        },
        'security': [
            {
                'APIKeyAuth': []
            }
        ]
    }
    swagger = Swagger(app, config=swagger_config)

    # Flask-Login Configuration
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=7)

    # CSRF Protection
    csrf = CSRFProtect(app)

    # Initialize the database
    # External call to prevent circular imports
    db.init_app(app)

    with app.app_context():
        db.create_all() # Create the database tables if they do not exist
    
    # Initialize Migrate
    migrate = Migrate(app, db)

    # Register Blueprints
    app.register_blueprint(globals)
    app.register_blueprint(web)
    app.register_blueprint(admin)
    app.register_blueprint(api_v1, url_prefix='/api/v1')

    # Initialize Login Manager
    login_manager = LoginManager(app)
    # Redirect users to the login page if they are not logged in
    login_manager.login_view = 'web.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register the Gravatar URL function as a global Jinja variable
    app.jinja_env.globals.update(get_gravatar_url=get_gravatar_url)
    app.jinja_env.globals.update(get_user_timezone=get_user_timezone)
    
    return app

if __name__ == '__main__':
    app = create_app()
    debug_mode = os.getenv('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
