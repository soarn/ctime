from datetime import datetime
from flask import Blueprint, render_template, request, redirect, flash, url_for, get_flashed_messages, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import desc
from sqlalchemy.orm import aliased
from db.db_models import User, WeeklySchedule, TimeOffRequest
from db.db import db
# from routes.api_v1 import
from forms import AdminScheduleForm, ApproveRejectForm, LoginForm, RegisterForm, TimeOffRequestForm, WeeklyScheduleForm

# Blueprint Configuration
web = Blueprint('web', __name__)

# HOME ROUTE
@web.route("/")
def home():
    return render_template("home.html")

# LOGIN ROUTE
@web.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            # Update the last login time
            user.last_login = datetime.now()
            db.session.commit()

            # Log the user in, remember me is optional
            login_user(user, remember=remember)

            # Clear any flashed messages
            get_flashed_messages()

            # Get the 'next' argument to see where the user was redirected from
            next_page = request.args.get('next')

            # Only flash if user was not redirected to login
            if not next_page:
                flash('Login successful', 'success')
            
            # Redirect to the next page if it exists, otherwise, redirect to dashboard by default
            if next_page:
                return redirect(next_page)
            return redirect(url_for('web.dashboard'))
        else:
            flash("Invalid username or password. Please try again.", "danger")
    return render_template("login.html", form=form)

# LOGOUT ROUTE
@web.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out", "success")
    return redirect(url_for("web.home"))

# REGISTER ROUTE
@web.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        username = form.username.data
        email = form.email.data
        password = form.password.data

        # Check if the username is already taken
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists.", "danger")
        else:
            # # Check if this is the first user, if so, make them an admin
            # if User.query.count() == 0:
            #     role = "admin"
            # else:
            #     role = "user"
            
            # Create a new user
            new_user = User(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email#,
                # role=role
            )
            new_user.set_password(password) # Hash the password
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("web.login"))
        
    return render_template("register.html", form=form)

# DASHBOARD ROUTE
@web.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "admin":
        return redirect(url_for("web.admin_dashboard"))
    else:
        return redirect(url_for("web.employee_dashboard"))

# EMPLOYEE DASHBOARD ROUTE
@web.route("/employee_dashboard", methods=["GET", "POST"])
@login_required
def employee_dashboard():
    if current_user.role != "user":
        return redirect(url_for("web.login"))

    user_id = current_user.id
    time_off_form = TimeOffRequestForm()
    schedule_forms = [WeeklyScheduleForm(prefix=f'day_{day}') for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']]

    if time_off_form.validate_on_submit() and time_off_form.submit.data:
        time_off_request = TimeOffRequest(user_id=user_id, date=time_off_form.date.data)
        db.session.add(time_off_request)
        db.session.commit()
        flash('Day off request submitted.', 'success')
        return redirect(url_for('web.employee_dashboard'))
    
    if request.method == "POST":
        # Overwrite existing schedules
        WeeklySchedule.query.filter_by(user_id=user_id).delete()

        for schedule_form in schedule_forms:
            if schedule_form.validate():
                is_unavailable = schedule_form.is_unavailable.data
                new_schedule = WeeklySchedule(
                    user_id=user_id,
                    day_of_week=schedule_form.day_of_week.data,
                    start_time=schedule_form.start_time.data if not is_unavailable else None,
                    end_time=schedule_form.end_time.data if not is_unavailable else None,
                    is_virtual=schedule_form.is_virtual.data,
                    is_unavailable=is_unavailable,
                )
                db.session.add(new_schedule)
        
        db.session.commit()
        flash('Schedule updated successfully.', 'success')
        return redirect(url_for('web.dashboard'))
    
    weekly_schedules = WeeklySchedule.query.filter_by(user_id=user_id).all()
    time_off_requests = TimeOffRequest.query.filter_by(user_id=user_id).all()

    return render_template(
        'employee_dashboard.html',
        schedule_forms=schedule_forms,
        time_off_form=time_off_form,
        weekly_schedules=weekly_schedules,
        time_off_requests=time_off_requests
    )

# TODO: Might need to make a separate route for the forms because of how flask forms submit data

# ADMIN DASHBOARD ROUTE
@web.route("/admin_dashboard", methods=["GET", "POST"])
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        return redirect(url_for("web.login"))
    
    approve_reject_form = ApproveRejectForm()
    admin_schedule_form = AdminScheduleForm()

    if approve_reject_form.validate_on_submit():
        request_id = approve_reject_form.request_id.data
        action = approve_reject_form.action.data

        time_off_request = TimeOffRequest.query.get(request_id)
        if action == 'approve':
            time_off_request.status = 'approved'
            flash('Time off request approved.', 'success')
        elif action == 'reject':
            time_off_request.status = 'rejected'
            flash('Time off request rejected.', 'success')
        db.session.commit()
        return redirect(url_for('web.admin_dashboard'))
    
    users = User.query.filter_by(role='user').all()
    # weekly_schedules = WeeklySchedule.query.filter(WeeklySchedule.user_id.in_([user.id for user in users])).all()
    # TODO: Thats weird lol
    weekly_schedules = WeeklySchedule.query.all()
    time_off_requests = TimeOffRequest.query.all()

    return render_template(
        'admin_dashboard.html',
        users=users,
        approve_reject_form=approve_reject_form,
        admin_schedule_form=admin_schedule_form,
        weekly_schedules=weekly_schedules,
        time_off_requests=time_off_requests
    )

# REQUEST TIME OFF ROUTE
@web.route('/time_off', methods=['POST'])
@login_required
def request_day_off():
    if current_user.role != 'user':
        return redirect(url_for('web.login'))
    
    user_id = current_user.id
    time_off_form = TimeOffRequestForm()
    if time_off_form.validate_on_submit():
        time_off_request = TimeOffRequest(user_id=user_id, date=time_off_form.date.data)
        db.session.add(time_off_request)
        db.session.commit()
        flash('Time off request submitted.', 'success')
    return redirect(url_for('web.dashboard'))