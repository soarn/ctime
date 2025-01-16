from datetime import datetime
from functools import wraps
from flask import Blueprint, render_template, request, redirect, flash, url_for, get_flashed_messages, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import desc
from sqlalchemy.orm import aliased
from db.db_models import User, WeeklySchedule, TimeOffRequest
from db.db import db
# from routes.api_v1 import
from forms import AdminScheduleForm, ApproveRejectForm, LoginForm, RegisterForm, TimeOffRequestForm, WeeklyScheduleForm

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
        return redirect(url_for('admin.admin_dashboard'))
    
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
