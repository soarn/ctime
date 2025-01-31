from datetime import datetime, timezone as tz
from flask import Blueprint, render_template, request, redirect, flash, url_for, get_flashed_messages
from flask_login import current_user, login_user, logout_user, login_required
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pytz import utc
from utils import get_user_timezone
from db.db_models import User, WeeklySchedule, TimeOffRequest
from db.db import db
from forms import CancelTimeOffForm, LoginForm, ProfileForm, RegisterForm, TimeOffRequestForm, WeeklyScheduleForm
import logging

# Initialize logger
logger = logging.getLogger(__name__)

# Blueprint Configuration
web = Blueprint('web', __name__)

# Rate Limiter Configuration
limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
        )

# HOME ROUTE
@web.route("/")
def home():
    return render_template("home.html")

# LOGIN ROUTE
@web.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            # Update the last login time
            user.last_login = datetime.now(tz.utc)
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
@limiter.limit("3 per hour")
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        username = form.username.data
        email = form.email.data
        password = form.password.data

        # Check if the username or email is already taken
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        if existing_user:
            flash("Username or email already exists.", "danger")
        else:
            # Check if this is the first user, if so, make them an admin
            role = "admin" if User.query.count() == 0 else "user"
            
            # Create a new user
            new_user = User(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                role=role
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
    cancel_time_off_form = CancelTimeOffForm()

    # Get the user's timezone
    viewer_tz = get_user_timezone()

    # Fetch existing schedules
    try:
        existing_schedules = {s.day_of_week: s for s in WeeklySchedule.query.filter_by(user_id=user_id).all()}
        time_off_requests = TimeOffRequest.query.filter_by(user_id=user_id).all()
    except Exception as e:
        logger.error(f"Error fetching user data: {e}")
        flash("Error loading dashboard data. Please try again.", "danger")
        return redirect(url_for("web.home"))

    # Populate forms with existing data
    for day, form in schedule_forms.items():
        form.day_of_week.data = day # Populate hidden field
        if day in existing_schedules:
            schedule = existing_schedules[day]

            # Convert the schedule times to the user's timezone
            try:
                if schedule.start_time:
                    schedule_start_datetime = datetime.combine(datetime.today(), schedule.start_time)
                    schedule_start_time_local = utc.localize(schedule_start_datetime).astimezone(viewer_tz).time()
                    form.start_time.data = schedule_start_time_local
                if schedule.end_time:
                    schedule_end_datetime = datetime.combine(datetime.today(), schedule.end_time)
                    schedule_end_time_local = utc.localize(schedule_end_datetime).astimezone(viewer_tz).time()
                    form.end_time.data = schedule_end_time_local
            except Exception as e:
                logger.error(f"Error converting schedule times for user {user_id} on {day}: {e}")
                flash(f"Error converting schedule times for {day}.", "danger")

            form.day_of_week.data = day
            form.is_virtual.data = schedule.is_virtual
            form.is_unavailable.data = schedule.is_unavailable
        else:
            form.day_of_week.data = day

    return render_template(
        "employee_dashboard.html",
        schedule_forms=schedule_forms,
        time_off_form=time_off_form,
        time_off_requests=time_off_requests,
        cancel_time_off_form=cancel_time_off_form
    )

# Update Schedule Route
@web.route("/employee_dashboard/update_schedule", methods=["POST"])
@login_required
def update_schedule():
    user_id = current_user.id

    # Initialize forms for each day of the week
    schedule_forms = {day: WeeklyScheduleForm(prefix=day) for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']}

    # Get the user's timezone
    viewer_tz = get_user_timezone()

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

                # Convert the schedule times to UTC
                start_time_utc = None
                end_time_utc = None
                if form.start_time.data and form.end_time.data and not is_unavailable:
                    try:
                        start_time_datetime = datetime.combine(datetime.today(), form.start_time.data)
                        start_time_localized = viewer_tz.localize(start_time_datetime)
                        start_time_utc = start_time_localized.astimezone(utc).time()
                        
                        end_time_datetime = datetime.combine(datetime.today(), form.end_time.data)
                        end_time_localized = viewer_tz.localize(end_time_datetime)
                        end_time_utc = end_time_localized.astimezone(utc).time()
                    except Exception as e:
                        logger.error(f"Error converting schedule times for user {user_id} on {day}: {e}")
                        flash(f"Error converting schedule times for {day}.", "danger")
                        return redirect(url_for("web.employee_dashboard"))

                new_schedule = WeeklySchedule(
                    user_id=user_id,
                    day_of_week=day,
                    start_time=start_time_utc,
                    end_time=end_time_utc,
                    is_virtual=form.is_virtual.data,
                    is_unavailable=is_unavailable,
                )
                db.session.add(new_schedule)

            db.session.commit()
            flash("Schedule updated successfully.", "success")
            return redirect(url_for("web.employee_dashboard"))
        except Exception as e:
            logger.error(f"Error during schedule update: {e}")
            flash("An error occurred while updating the schedule.", "danger")
    else:
        logger.error("Form validation failed.")
        for day, form in schedule_forms.items():
            if not form.validate():
                logger.error(f"Validation errors for {day}: {form.errors}")
        flash("Failed to update schedule. Please check the form and try again.", "danger")

# Request Time Off Route
@web.route("/employee_dashboard/request_time_off", methods=["POST"])
@login_required
def request_time_off():
    user_id = current_user.id
    time_off_form = TimeOffRequestForm()

    if time_off_form.validate_on_submit():
        date = time_off_form.date.data
        comment = time_off_form.comment.data
        existing_request = TimeOffRequest.query.filter_by(user_id=user_id, date=date).first()
        if existing_request:
            flash("You have already requested time off for this date.", "warning")
            return redirect(url_for("web.employee_dashboard"))
        else:
            time_off_request = TimeOffRequest(user_id=user_id, date=date, comment=comment)
            db.session.add(time_off_request)
            db.session.commit()
            flash("Time off request submitted.", "success")
            return redirect(url_for("web.employee_dashboard"))
    else:
        flash("Failed to submit time off request. Please try again.", "danger")
        return redirect(url_for("web.employee_dashboard"))

# Cancel Time Off Route
@web.route("/employee_dashboard/cancel_time_off", methods=["POST"])
@login_required
def cancel_time_off():
    user_id = current_user.id
    request_id = request.form.get("request_id")
    time_off_request = TimeOffRequest.query.filter_by(id=request_id, user_id=user_id).first()
    if not time_off_request:
        flash("Failed to cancel time off request.", "danger")
        return redirect(url_for("web.employee_dashboard"))
    
    if time_off_request.status != "pending":
        flash("Cannot cancel a time off request that has already been approved or rejected.", "danger")
        return redirect(url_for("web.employee_dashboard"))
    
    db.session.delete(time_off_request)
    db.session.commit()
    flash("Time off request cancelled.", "success")
    return redirect(url_for("web.employee_dashboard"))


# Profile Route
@web.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        # Check if username or email is taken by another user
        existing_user = User.query.filter(
            (User.username == form.username.data) | (User.email == form.email.data),
            User.id != current_user.id
        ).first()
        if existing_user:
            flash('Username or email is already taken.', 'danger')
            return redirect(url_for('web.profile'))
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.username = form.username.data
        current_user.email = form.email.data
        if form.password.data:
            current_user.set_password(form.password.data) # Hash and save the password
        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            logger.error(f"Error updating profile: {e}")
            flash('An error occurred while updating your profile. Please try again.', 'danger')
        return redirect(url_for('web.profile'))
    return render_template('profile.html', form=form)
