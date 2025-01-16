from datetime import timedelta, datetime
from flask import Flask
from flask_login import LoginManager
from flask_mysqldb import MySQL
from flasgger import Swagger
from flask_wtf.csrf import CSRFProtect
from db.db import db
from db.db_models import User, WeeklySchedule, TimeOffRequest
from routes.web import web
from routes.admin import admin
from flask_migrate import Migrate
import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('CONNECTION_STRING')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    REMEMBER_COOKIE_DURATION = timedelta(days=7)

class ProductionConfig(Config):
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True

def create_app():

    # Initialize Flask App
    app = Flask(__name__)

    # Initialize Swagger
    swagger = Swagger(app)

    # Load configuration from class
    app.config.from_object(ProductionConfig if os.getenv('FLASK_ENV') == 'production' else Config)

    # Flask-Login Configuration
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=7)

    # CSRF Protection
    csrf = CSRFProtect(app)

    # Initialize the database
    # External call to prevent circular imports
    db.init_app(app)

    # Initialize Migrate
    migrate = Migrate(app, db)

    # Register Blueprints
    app.register_blueprint(web)
    app.register_blueprint(admin)

    # Initialize Login Manager
    login_manager = LoginManager(app)
    # Redirect users to the login page if they are not logged in
    login_manager.login_view = 'web.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    @app.route('/create_db')
    def create_db():
        db.create_all()
        return 'Database created'
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
