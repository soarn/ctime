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

def create_app():

    # Initialize Flask App
    app = Flask(__name__)

    # Initialize Swagger
    swagger = Swagger(app)

    # Database Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("CONNECTION_STRING")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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

    # @app.route('/view_user/<int:user_id>', methods=['GET', 'POST'])
    # def view_user(user_id):
    #     if 'user_id' not in session or session.get('role') != 'admin':
    #         return redirect(url_for('login'))

    #     user = User.query.get_or_404(user_id)
    #     if request.method == 'POST':
    #         WeeklySchedule.query.filter_by(user_id=user_id).delete()
    #         for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
    #             start_time = request.form.get(f'start_time_{day}')
    #             end_time = request.form.get(f'end_time_{day}')
    #             is_virtual = request.form.get(f'is_virtual_{day}') == 'on'
    #             is_unavailable = request.form.get(f'is_unavailable_{day}') == 'on'

    #             new_schedule = WeeklySchedule(
    #                 user_id=user_id,
    #                 day_of_week=day,
    #                 start_time=start_time if not is_unavailable else None,
    #                 end_time=end_time if not is_unavailable else None,
    #                 is_virtual=is_virtual,
    #                 is_unavailable=is_unavailable
    #             )
    #             db.session.add(new_schedule)
    #         db.session.commit()
    #         flash(f'Schedule updated for {user.name}.', 'success')

    #     weekly_schedules = WeeklySchedule.query.filter_by(user_id=user_id).all()
    #     return render_template('view_user.html', user=user, weekly_schedules=weekly_schedules)

    # @app.route('/request_day_off', methods=['POST'])
    # def request_day_off():
    #     if 'user_id' not in session:
    #         return redirect(url_for('login'))

    #     user_id = session['user_id']
    #     date = request.form['date']

    #     time_off_request = TimeOffRequest(user_id=user_id, date=date)
    #     db.session.add(time_off_request)
    #     db.session.commit()

    #     flash('Day off request submitted', 'success')
    #     return redirect(url_for('employee_dashboard'))
    
    @app.route('/create_db')
    def create_db():
        db.create_all()
        return 'Database created'
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
