from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import current_user, login_required
from pytz import utc
import logging  
from db.db_models import User, WeeklySchedule, TimeOffRequest
from db.db import db
from forms import AdminWeeklyScheduleForm, ApproveRejectForm, AdminUserForm
from utils import get_user_timezone

logger = logging.getLogger(__name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash("Unauthorized", "danger")
            return redirect(url_for('web.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Blueprint Configuration
admin = Blueprint('admin', __name__)

# ADMIN DASHBOARD ROUTE
@admin.route("/admin_dashboard", methods=["GET", "POST"])
@login_required
@admin_required
def admin_dashboard():
    
    # Initialize forms
    approve_reject_form = ApproveRejectForm()

    # Fetch users and schedules
    users = User.query.filter_by(role='user').all()
    all_users = User.query.all()
    # Only users have schedules, admins do not
    weekly_schedules = WeeklySchedule.query.join(User).filter(User.role == 'user').all()
    time_off_requests = TimeOffRequest.query.filter(TimeOffRequest.date >= datetime.today().date()).all() # Filter past dates

    # Calculate the current week's dates (Monday to Sunday)
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday()) # Start on Monday
    week_dates = [(start_of_week + timedelta(days=i)) for i in range(7)]

    # Get the user's timezone
    viewer_tz = get_user_timezone()

    # Map schedules to users
    user_schedule_mapping = {}
    for user in users:
        user_schedule_mapping[user.id] = {}
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            schedule = next((s for s in weekly_schedules if s.user_id == user.id and s.day_of_week == day), None)
            has_time_off = any(r for r in time_off_requests if r.user_id == user.id and r.date.strftime('%A') == day and r.status == 'approved')

            # Convert times to viewer's timezone
            try:
                if schedule and schedule.start_time:
                    schedule_start_datetime = datetime.combine(datetime.today(), schedule.start_time)
                    schedule.start_time = utc.localize(schedule_start_datetime).astimezone(viewer_tz).time()
                if schedule and schedule.end_time:
                    schedule_end_datetime = datetime.combine(datetime.today(), schedule.end_time)
                    schedule.end_time = utc.localize(schedule_end_datetime).astimezone(viewer_tz).time()
            except Exception as e:
                logger.error(f"Error converting schedule times for user {user.id} on {day}: {e}")
                flash(f"Error converting schedule times for user {user.id} on {day}.", "danger")

            user_schedule_mapping[user.id][day] = {
                'schedule': schedule,
                'has_time_off': has_time_off,
            }
    
    return render_template(
        "admin_dashboard.html",
        approve_reject_form=approve_reject_form,
        user_schedule_mapping=user_schedule_mapping,
        time_off_requests=time_off_requests,
        users=users,
        week_dates=week_dates,
        all_users=all_users
    )

# ADMIN: HANDLE TIME OFF ROUTE
@admin.route("/admin_dashboard/handle_time_off", methods=["POST"])
@login_required
@admin_required
def handle_time_off():

    approve_reject_form = ApproveRejectForm()

    logger.debug(f"Processing time-off request ID: {approve_reject_form.request_id.data}, Action: {approve_reject_form.action.data}")
    if approve_reject_form.validate_on_submit():
        request_id = approve_reject_form.request_id.data
        action = approve_reject_form.action.data

        try:
            time_off_request = TimeOffRequest.query.get(request_id)
            if not time_off_request:
                flash('Time off request not found.', 'error')
                return redirect(url_for('admin.admin_dashboard'))
            
            if action == 'approve':
                time_off_request.status = 'approved'
                flash('Time off request approved.', 'success')
            elif action == 'reject':
                time_off_request.status = 'rejected'
                flash('Time off request rejected.', 'danger')

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error processing time-off request: {e}")
            flash('Error processing request.', 'error')
        return redirect(url_for('admin.admin_dashboard'))
    else:
        logger.error("Form validation failed.")
        for field, errors in approve_reject_form.errors.items():
            logger.error(f"Validation errors for {field}: {errors}")
            flash(f"Validation errors for {field}: {errors}", "danger")
        return redirect(url_for('admin.admin_dashboard'))

@admin.route("/admin_dashboard/update_user/<int:user_id>", methods=["GET", "POST"])
@login_required
@admin_required
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    viewer_tz = get_user_timezone()

    if request.method == "GET":
        forms = {day: AdminWeeklyScheduleForm(prefix=f"{user_id}_{day}") for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']}

        schedules = {s.day_of_week: s for s in WeeklySchedule.query.filter_by(user_id=user_id).all()}
        for day, form in forms.items():
            form.day_of_week.data = day
            if day in schedules:
                schedule = schedules[day]

                try:
                    if schedule.start_time:
                        schedule_start_datetime = datetime.combine(datetime.today(), schedule.start_time)
                        form.start_time.data = utc.localize(schedule_start_datetime).astimezone(viewer_tz).time()
                    if schedule.end_time:
                        schedule_end_datetime = datetime.combine(datetime.today(), schedule.end_time)
                        form.end_time.data = utc.localize(schedule_end_datetime).astimezone(viewer_tz).time()
                except Exception as e:
                    logger.error(f"Error converting times for user {user_id} on {day}: {e}")
                    flash(f"Error displaying schedule times for {day}.", "danger")

                form.is_virtual.data = schedule.is_virtual
                form.is_unavailable.data = schedule.is_unavailable

        user_form = AdminUserForm(obj=user)
        return render_template("manage_user.html", user=user, user_form=user_form, forms=forms)

    # Determine which form was submitted
    form_type = request.form.get("form_type")

    if form_type == "user_form":
        user_form = AdminUserForm(obj=user)
        if user_form.validate_on_submit():
            old_role = user.role  # Store the previous role

            user.first_name = user_form.first_name.data
            user.last_name = user_form.last_name.data
            user.username = user_form.username.data
            user.email = user_form.email.data
            user.role = user_form.role.data

            if user_form.password.data:
                user.set_password(user_form.password.data)  # Reset password

            # If user is promoted to admin, delete their schedule
            if old_role != "admin" and user_form.role.data == "admin":
                WeeklySchedule.query.filter_by(user_id=user_id).delete()

            try:
                db.session.commit()
                flash("User details updated successfully.", "success")

                # Redirect to `manage_admin.html` if the user was promoted
                if user_form.role.data == "admin":
                    return redirect(url_for("admin.manage_admin", user_id=user_id))
                    
            except Exception as e:
                logger.error(f"Error updating user details for {user_id}: {e}")
                flash("An error occurred while updating user details.", "danger")

        return redirect(url_for("admin.update_user", user_id=user_id))

    elif form_type == "schedule_form":
        forms = {day: AdminWeeklyScheduleForm(prefix=f"{user_id}_{day}") for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']}
        
        for form in forms.values():
            form.process(formdata=request.form)

        if all(form.validate() for form in forms.values()):
            WeeklySchedule.query.filter_by(user_id=user_id).delete()

            for day, form in forms.items():
                is_unavailable = form.is_unavailable.data
                start_time_utc, end_time_utc = None, None

                if form.start_time.data and form.end_time.data and not is_unavailable:
                    start_time_utc = viewer_tz.localize(datetime.combine(datetime.today(), form.start_time.data)).astimezone(utc).time()
                    end_time_utc = viewer_tz.localize(datetime.combine(datetime.today(), form.end_time.data)).astimezone(utc).time()

                db.session.add(WeeklySchedule(user_id=user_id, day_of_week=day, start_time=start_time_utc, end_time=end_time_utc, is_virtual=form.is_virtual.data, is_unavailable=is_unavailable))

            db.session.commit()
            flash("Schedule updated successfully.", "success")

        return redirect(url_for("admin.update_user", user_id=user_id))

    return redirect(url_for("admin.admin_dashboard"))


@admin.route("/admin_dashboard/manage_admin/<int:user_id>", methods=["GET", "POST"])
@login_required
@admin_required
def manage_admin(user_id):
    user = User.query.get_or_404(user_id)

    # Prevent self-demotion from admin role
    if current_user.id == user.id and request.method == "POST":
        if request.form.get("role") != "admin":
            flash("You cannot remove your own admin privileges.", "danger")
            return redirect(url_for("admin.manage_admin", user_id=user_id))

    user_form = AdminUserForm(obj=user)

    if request.method == "POST" and user_form.validate_on_submit():
        old_role = user.role  # Store current role before updating

        user.first_name = user_form.first_name.data
        user.last_name = user_form.last_name.data
        user.username = user_form.username.data
        user.email = user_form.email.data
        user.role = user_form.role.data

        if user_form.password.data:
            user.set_password(user_form.password.data)  # Reset password if provided

        try:
            db.session.commit()
            flash("Admin details updated successfully.", "success")

            # If the admin is demoted to user, redirect to `manage_user`
            if old_role == "admin" and user_form.role.data != "admin":
                return redirect(url_for("admin.update_user", user_id=user_id))
                
        except Exception as e:
            logger.error(f"Error updating admin details for {user_id}: {e}")
            flash("An error occurred while updating admin details.", "danger")

        return redirect(url_for("admin.manage_admin", user_id=user_id))

    return render_template("manage_admin.html", user=user, user_form=user_form)
