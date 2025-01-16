from datetime import datetime
from flask import Blueprint, render_template, request, redirect, flash, url_for, get_flashed_messages
from flask_login import current_user, login_user, logout_user, login_required
from db.db_models import User, WeeklySchedule, TimeOffRequest
from db.db import db
from forms import LoginForm, RegisterForm, TimeOffRequestForm, WeeklyScheduleForm
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
            # Check if this is the first user, if so, make them an admin
            if User.query.count() == 0:
                role = "admin"
            else:
                role = "user"
            
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
        return redirect(url_for("admin.admin_dashboard"))
    else:
        return redirect(url_for("web.employee_dashboard"))

# EMPLOYEE DASHBOARD ROUTE
@web.route("/employee_dashboard", methods=["GET", "POST"])
@login_required
def employee_dashboard():
    if current_user.role != "user":
        return redirect(url_for("web.login"))

    user_id = current_user.id

    # Initialize forms for each day of the week
    schedule_forms = {day: WeeklyScheduleForm(prefix=day) for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']}
    time_off_form = TimeOffRequestForm()

    # Fetch existing schedules
    existing_schedules = {s.day_of_week: s for s in WeeklySchedule.query.filter_by(user_id=user_id).all()}

    # Populate forms with existing data
    for day, form in schedule_forms.items():
        form.day_of_week.data = day # Populate hidden field
        if day in existing_schedules:
            schedule = existing_schedules[day]
            form.day_of_week.data = day
            form.start_time.data = schedule.start_time
            form.end_time.data = schedule.end_time
            form.is_virtual.data = schedule.is_virtual
            form.is_unavailable.data = schedule.is_unavailable
        else:
            form.day_of_week.data = day

    time_off_requests = TimeOffRequest.query.filter_by(user_id=user_id).all()

    return render_template(
        "employee_dashboard.html",
        schedule_forms=schedule_forms,
        time_off_form=time_off_form,
        time_off_requests=time_off_requests,
    )

# Update Schedule Route
@web.route("/employee_dashboard/update_schedule", methods=["POST"])
@login_required
def update_schedule():
    user_id = current_user.id

    # Initialize forms for each day of the week
    schedule_forms = {day: WeeklyScheduleForm(prefix=day) for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']}

    # Bind form data for each day
    for day, form in schedule_forms.items():
        form.day_of_week.data = day
        form.process(formdata=request.form)

    # Validate and update schedule
    if all(form.validate() for form in schedule_forms.values()):
        try: # Delete existing schedule
            WeeklySchedule.query.filter_by(user_id=user_id).delete()

            # Add new schedules
            for day, form in schedule_forms.items():
                is_unavailable = form.is_unavailable.data
                new_schedule = WeeklySchedule(
                    user_id=user_id,
                    day_of_week=day,
                    start_time=form.start_time.data if not is_unavailable else None,
                    end_time=form.end_time.data if not is_unavailable else None,
                    is_virtual=form.is_virtual.data,
                    is_unavailable=is_unavailable,
                )
                db.session.add(new_schedule)

            db.session.commit()
            flash("Schedule updated successfully.", "success")
            return redirect(url_for("web.employee_dashboard"))
        except Exception as e:
            print(f"Error during schedule update: {e}")
            flash("An error occurred while updating the schedule.", "danger")
    else:
        print("Form validation failed.")
        for day, form in schedule_forms.items():
            if not form.validate():
                print(f"Validation errors for {day}: {form.errors}")
        flash("Failed to update schedule. Please check the form and try again.", "danger")

    return redirect(url_for("web.employee_dashboard"))

# Request Time Off Route
@web.route("/employee_dashboard/request_time_off", methods=["POST"])
@login_required
def request_time_off():
    user_id = current_user.id
    time_off_form = TimeOffRequestForm()

    if time_off_form.validate_on_submit():
        date = time_off_form.date.data
        existing_request = TimeOffRequest.query.filter_by(user_id=user_id, date=date).first()
        if existing_request:
            flash("You have already requested time off for this date.", "warning")
        else:
            time_off_request = TimeOffRequest(user_id=user_id, date=date)
            db.session.add(time_off_request)
            db.session.commit()
            flash("Time off request submitted.", "success")
    else:
        flash("Failed to submit time off request. Please try again.", "danger")

    return redirect(url_for("web.employee_dashboard"))

