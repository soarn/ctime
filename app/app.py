from datetime import timedelta, datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from flasgger import Swagger
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from db.db import db
from db.db_models import User, WeeklySchedule, TimeOffRequest
from routes.web import web
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

    # Initialize Login Manager
    login_manager = LoginManager(app)
    # Redirect users to the login page if they are not logged in
    login_manager.login_view = 'web.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


    # @app.route('/')
    # def index():
    #     if 'user_id' in session:
    #         return redirect(url_for('dashboard'))
    #     return render_template('index.html')

    # @app.route('/login', methods=['GET', 'POST'])
    # def login():
    #     if request.method == 'POST':
    #         email = request.form['email']
    #         password = request.form['password']

    #         user = User.query.filter_by(email=email).first()
    #         if user and check_password_hash(user.password, password):
    #             session['user_id'] = user.id
    #             session['role'] = user.role
    #             return redirect(url_for('dashboard'))
    #         else:
    #             flash('Invalid credentials', 'danger')

    #     return render_template('login.html')

    # @app.route('/register', methods=['GET', 'POST'])
    # def register():
    #     if request.method == 'POST':
    #         name = request.form['name']
    #         email = request.form['email']
    #         password = generate_password_hash(request.form['password'])
    #         role = request.form['role']

    #         new_user = User(name=name, email=email, password=password, role=role)
    #         db.session.add(new_user)
    #         db.session.commit()

    #         flash('Registration successful', 'success')
    #         return redirect(url_for('login'))

    #     return render_template('register.html')

    # @app.route('/dashboard')
    # def dashboard():
    #     if 'user_id' not in session:
    #         return redirect(url_for('login'))

    #     user_role = session.get('role')
    #     if user_role == 'admin':
    #         return redirect(url_for('admin_dashboard'))
    #     else:
    #         return redirect(url_for('employee_dashboard'))

    @app.route('/employee_dashboard', methods=['GET', 'POST'])
    def employee_dashboard():
        if 'user_id' not in session or session.get('role') != 'employee':
            return redirect(url_for('login'))

        user_id = session['user_id']

        if request.method == 'POST':
            # Overwrite existing schedules
            WeeklySchedule.query.filter_by(user_id=user_id).delete()

            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
                start_time = request.form.get(f'start_time_{day}')
                end_time = request.form.get(f'end_time_{day}')
                is_virtual = request.form.get(f'is_virtual_{day}') == 'on'
                is_unavailable = request.form.get(f'is_unavailable_{day}') == 'on'

                new_schedule = WeeklySchedule(
                    user_id=user_id,
                    day_of_week=day,
                    start_time=start_time if not is_unavailable else None,
                    end_time=end_time if not is_unavailable else None,
                    is_virtual=is_virtual,
                    is_unavailable=is_unavailable
                )
                db.session.add(new_schedule)

            db.session.commit()
            flash('Schedule updated successfully', 'success')

        weekly_schedules = WeeklySchedule.query.filter_by(user_id=user_id).all()
        time_off_requests = TimeOffRequest.query.filter_by(user_id=user_id).all()

        return render_template('employee_dashboard.html', weekly_schedules=weekly_schedules, time_off_requests=time_off_requests)

    @app.route('/admin_dashboard', methods=['GET', 'POST'])
    def admin_dashboard():
        if 'user_id' not in session or session.get('role') != 'admin':
            return redirect(url_for('login'))

        if request.method == 'POST':
            if 'approve_request' in request.form:
                request_id = request.form['approve_request']
                time_off_request = TimeOffRequest.query.get(request_id)
                time_off_request.status = 'approved'
                db.session.commit()
                flash('Time off request approved.', 'success')
            elif 'reject_request' in request.form:
                request_id = request.form['reject_request']
                time_off_request = TimeOffRequest.query.get(request_id)
                time_off_request.status = 'rejected'
                db.session.commit()
                flash('Time off request rejected.', 'danger')

        # Calculate the current week's dates starting from Sunday
        today = datetime.today()
        start_of_week = today - timedelta(days=today.weekday() + 1)
        week_dates = [(start_of_week + timedelta(days=i)).date() for i in range(7)]  # Sunday to Saturday

        # Retrieve all data
        users = User.query.filter_by(role='employee').all()
        weekly_schedules = WeeklySchedule.query.all()
        time_off_requests = TimeOffRequest.query.all()

        # Create a mapping of user schedules for display
        user_schedule_mapping = {}
        for user in users:
            user_schedule_mapping[user.id] = {}
            for i, day_date in enumerate(week_dates):
                day_name = day_date.strftime('%A')  # Get the day name
                schedule = next((s for s in weekly_schedules if s.user_id == user.id and s.day_of_week == day_name), None)
                has_time_off = any(r for r in time_off_requests if r.user_id == user.id and r.date == day_date and r.status == 'approved')
                user_schedule_mapping[user.id][day_name] = {
                    'schedule': schedule,
                    'has_time_off': has_time_off
                }

        return render_template(
            'admin_dashboard.html',
            users=users,
            week_dates=week_dates,
            user_schedule_mapping=user_schedule_mapping,
            time_off_requests=time_off_requests
        )

    @app.route('/view_user/<int:user_id>', methods=['GET', 'POST'])
    def view_user(user_id):
        if 'user_id' not in session or session.get('role') != 'admin':
            return redirect(url_for('login'))

        user = User.query.get_or_404(user_id)
        if request.method == 'POST':
            WeeklySchedule.query.filter_by(user_id=user_id).delete()
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
                start_time = request.form.get(f'start_time_{day}')
                end_time = request.form.get(f'end_time_{day}')
                is_virtual = request.form.get(f'is_virtual_{day}') == 'on'
                is_unavailable = request.form.get(f'is_unavailable_{day}') == 'on'

                new_schedule = WeeklySchedule(
                    user_id=user_id,
                    day_of_week=day,
                    start_time=start_time if not is_unavailable else None,
                    end_time=end_time if not is_unavailable else None,
                    is_virtual=is_virtual,
                    is_unavailable=is_unavailable
                )
                db.session.add(new_schedule)
            db.session.commit()
            flash(f'Schedule updated for {user.name}.', 'success')

        weekly_schedules = WeeklySchedule.query.filter_by(user_id=user_id).all()
        return render_template('view_user.html', user=user, weekly_schedules=weekly_schedules)

    @app.route('/request_day_off', methods=['POST'])
    def request_day_off():
        if 'user_id' not in session:
            return redirect(url_for('login'))

        user_id = session['user_id']
        date = request.form['date']

        time_off_request = TimeOffRequest(user_id=user_id, date=date)
        db.session.add(time_off_request)
        db.session.commit()

        flash('Day off request submitted', 'success')
        return redirect(url_for('employee_dashboard'))

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('index'))
    
    @app.route('/create_db')
    def create_db():
        db.create_all()
        return 'Database created'
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
