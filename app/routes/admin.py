from datetime import datetime
from functools import wraps
from flask import Blueprint, render_template, request, redirect, flash, url_for, get_flashed_messages, jsonify
from flask_login import current_user, login_required
from db.db_models import User, WeeklySchedule, TimeOffRequest
from db.db import db
from forms import AdminWeeklyScheduleForm, ApproveRejectForm

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
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
    schedule_forms = {}

    # Fetch users and schedules
    users = User.query.filter_by(role='user').all()
    # Only users have schedules, admins do not
    weekly_schedules = WeeklySchedule.query.join(User).filter(User.role == 'user').all()
    time_off_requests = TimeOffRequest.query.all()

    user_schedule_mapping = {}
    for user in users:
        user_schedule_mapping[user.id] = {}
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            schedule = next((s for s in weekly_schedules if s.user_id == user.id and s.day_of_week == day), None)
            has_time_off = any(r for r in time_off_requests if r.user_id == user.id and r.date.strftime('%A') == day and r.status == 'approved')
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
    )

# ADMIN: HANDLE TIME OFF ROUTE
@admin.route("/admin_dashboard/handle_time_off", methods=["POST"])
@login_required
@admin_required
def handle_time_off():

    approve_reject_form = ApproveRejectForm()

    print(f"Request ID: {approve_reject_form.request_id}, Action: {approve_reject_form.action}")
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
            flash('Error processing request.', 'error')
            return redirect(url_for('admin.admin_dashboard'))
    else:
        print("Form validation failed.")
        for field, errors in approve_reject_form.errors.items():
            print(f"Validation errors for {field}: {errors}")
            flash(f"Validation errors for {field}: {errors}", "danger")
        return redirect(url_for('admin.admin_dashboard'))

# ADMIN: UPDATE SCHEDULE ROUTE
@admin.route("/admin_dashboard/update_schedule/<int:user_id>", methods=["GET", "POST"])
@login_required
@admin_required
def update_schedule(user_id):
    if request.method == "GET":
        user = User.query.get_or_404(user_id)
        forms = {day: AdminWeeklyScheduleForm(prefix=f"{user_id}_{day}") for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']}

    # 
    for day, form in forms.items():
        form.day_of_week.data = day
        form.process(formdata=request.form)

    if all(form.validate() for form in forms.values()):
        try: # Delete existing schedule
            WeeklySchedule.query.filter_by(user_id=user_id).delete()

            # Add new schedules
            for day, form in forms.items():
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
            flash(f"Schedule for user {user_id} updated successfully.", "success")
            return redirect(url_for('admin.admin_dashboard'))
        except Exception as e:
            print(f"Error during schedule update: {e}")
            flash(f"An error occurred while updating the schedule for user {user_id}.", "danger")
    else:
        print("Form validation failed.")
        for day, form in forms.items():
            if not form.validate():
                print(f"Validation errors for {day}: {form.errors}")
                flash(f"Validation errors for {day}: {form.errors}", "danger")
    
    return redirect(url_for('admin.admin_dashboard'))

# ADMIN: ADD SCHEDULE ROUTE
@admin.route("/admin_dashboard/add_schedule/<int:user_id>", methods=["GET"])
@login_required
@admin_required
def add_schedule(user_id):
    user = User.query.get_or_404(user_id)
    return render_template("add_schedule.html", user=user)