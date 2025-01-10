from datetime import timedelta
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from db.db import db
from db.db_models import User, WeeklySchedule, TimeOffRequest
import os

def create_app():

    app = Flask(__name__)

    # SQLAlchemy Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("CONNECTION_STRING")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Flask-Login Configuration
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=7)



    db.init_app(app)

    @app.route('/')
    def index():
        if 'user_id' in session:
            return redirect(url_for('dashboard'))
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']

            user = User.query.filter_by(email=email).first()
            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                session['role'] = user.role
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid credentials', 'danger')

        return render_template('login.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            password = generate_password_hash(request.form['password'])
            role = request.form['role']

            new_user = User(name=name, email=email, password=password, role=role)
            db.session.add(new_user)
            db.session.commit()

            flash('Registration successful', 'success')
            return redirect(url_for('login'))

        return render_template('register.html')

    @app.route('/dashboard')
    def dashboard():
        if 'user_id' not in session:
            return redirect(url_for('login'))

        user_role = session.get('role')
        if user_role == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('employee_dashboard'))

    @app.route('/employee_dashboard', methods=['GET', 'POST'])
    def employee_dashboard():
        if 'user_id' not in session or session.get('role') != 'employee':
            return redirect(url_for('login'))

        user_id = session['user_id']

        if request.method == 'POST':
            days_of_week = request.form.getlist('days_of_week')
            start_time = request.form['start_time']
            end_time = request.form['end_time']
            is_virtual = 'is_virtual' in request.form

            for day in days_of_week:
                new_schedule = WeeklySchedule(user_id=user_id, day_of_week=day, start_time=start_time, end_time=end_time, is_virtual=is_virtual)
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
            elif 'delete_schedule' in request.form:
                schedule_id = request.form['delete_schedule']
                schedule = WeeklySchedule.query.get(schedule_id)
                db.session.delete(schedule)
                db.session.commit()
                flash('Schedule deleted.', 'success')

        weekly_schedules = WeeklySchedule.query.all()
        time_off_requests = TimeOffRequest.query.all()

        return render_template('admin_dashboard.html', weekly_schedules=weekly_schedules, time_off_requests=time_off_requests)

    @app.route('/add_schedule', methods=['GET', 'POST'])
    def add_schedule():
        if request.method == 'POST':
            user_id = request.form['user_id']
            days_of_week = request.form.getlist('days_of_week')
            start_time = request.form['start_time']
            end_time = request.form['end_time']
            is_virtual = 'is_virtual' in request.form

            for day in days_of_week:
                new_schedule = WeeklySchedule(user_id=user_id, day_of_week=day, start_time=start_time, end_time=end_time, is_virtual=is_virtual)
                db.session.add(new_schedule)
            db.session.commit()

            flash('Schedule added successfully', 'success')
            return redirect(url_for('admin_dashboard'))

        users = User.query.filter_by(role='employee').all()
        return render_template('add_schedule.html', users=users)

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
    db.create_all()
    app.run(debug=True)
