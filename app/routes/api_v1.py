from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, send_file
from flasgger import swag_from
from pytz import utc, timezone as tz
import io
import pandas as pd
import dataframe_image as dfi
from app.db.db_models import User, WeeklySchedule, TimeOffRequest
from app.auth import api_key_required

api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# Get User Details
@api_v1.route('/user', methods=['GET'], endpoint='get_user')
@api_key_required()
@swag_from({
    'tags': ['User'],
    'summary': 'Get User Details',
    'description': 'Returns details of the authenticated user.',
    'security': [{'APIKeyAuth': []}],
    'responses': {
        200: {
            'description': 'User details retrieved successfully',
            'schema': {
                'id': 'User',
                'properties': {
                    'id': {'type': 'integer'},
                    'first_name': {'type': 'string'},
                    'last_name': {'type': 'string'},
                    'username': {'type': 'string'},
                    'email': {'type': 'string'},
                    'role': {'type': 'string'},
                    'slack_username': {'type': 'string'}
                }
            }
        },
        401: {'description': 'Unauthorized - Missing or invalid API key'},
        418: {'description': 'Invalid API key'}
    }
})
def get_user(user):
    """Returns the details of the authenticated user."""
    return jsonify({
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "slack_username": user.slack_username
    })

# Get All Users (Admin Only)
@api_v1.route('/users/all', methods=['GET'], endpoint='get_all_users')
@api_key_required(admin_only=True)
@swag_from({
    'tags': ['Admin'],
    'summary': 'Get All Users',
    'description': 'Returns a list of all users (Admin only).',
    'security': [{'APIKeyAuth': []}],
    'responses': {
        200: {
            'description': 'List of all users retrieved successfully',
            'schema': {
                'type': 'array',
                'items': {
                    'properties': {
                        'id': {'type': 'integer'},
                        'first_name': {'type': 'string'},
                        'last_name': {'type': 'string'},
                        'username': {'type': 'string'},
                        'email': {'type': 'string'},
                        'role': {'type': 'string'},
                        'slack_username': {'type': 'string'}
                    }
                }
            }
        },
        401: {'description': 'Unauthorized - Missing or invalid API key'},
        403: {'description': 'Forbidden - Admin access required'},
        418: {'description': 'Invalid API key'}
    }
})
def get_all_users(user):
    """Returns a list of all users (Admin only)."""
    users = User.query.all()
    return jsonify([{
        "id": u.id, "first_name": u.first_name, "last_name": u.last_name,
        "username": u.username, "email": u.email, "role": u.role,
        "slack_username": u.slack_username
    } for u in users])

# Get User Schedule
@api_v1.route('/schedule', methods=['GET'], endpoint='get_user_schedule')
@api_key_required()
@swag_from({
    'tags': ['Schedule'],
    'summary': 'Get User Schedule',
    'description': 'Returns the authenticated user\'s schedule.',
    'security': [{'APIKeyAuth': []}],
    'parameters': [
        {
            'name': 'timezone',
            'in': 'query',
            'type': 'string',
            'description': 'Timezone for schedule conversion (default: UTC)'
        }
    ],
    'responses': {
        200: {
            'description': 'Schedule retrieved successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'schedule': {'type': 'array', 'items': {
                        'properties': {
                            'day': {'type': 'string'},
                            'start_time': {'type': 'string'},
                            'end_time': {'type': 'string'},
                            'is_virtual': {'type': 'boolean'},
                            'is_unavailable': {'type': 'boolean'}
                        }
                    }},
                    'timezone': {'type': 'string'}
                }
            }
        },
        400: {'description': 'Invalid timezone'},
        401: {'description': 'Unauthorized - Missing or invalid API key'},
        418: {'description': 'Invalid API key'}
    }
})
def get_user_schedule(user):
    """Returns the authenticated user's schedule."""
    schedules = WeeklySchedule.query.filter_by(user_id=user.id).all()
    time_off_requests = TimeOffRequest.query.filter_by(user_id=user.id).all()
    
    # Get timezone from request args, default to UTC if not provided
    tz_name = request.args.get('timezone', 'UTC')
    try:
        viewer_tz = tz(tz_name)
    except Exception as e:
        return jsonify({'message': f"Invalid timezone: {e}"}), 400

    # Filter time-off requests for current and future dates only
    today = datetime.today().date()
    time_off_requests = [t for t in time_off_requests if t.date >= today]

    time_off_data = {t.date.strftime("%A"): True for t in time_off_requests}

    schedule_data = []
    for schedule in schedules:
        # Convert the schedule times to the specified timezone
        try:
            if schedule.start_time:
                schedule_start_datetime = datetime.combine(datetime.today(), schedule.start_time)
                schedule_start_time_local = utc.localize(schedule_start_datetime).astimezone(viewer_tz).time()
            if schedule.end_time:
                schedule_end_datetime = datetime.combine(datetime.today(), schedule.end_time)
                schedule_end_time_local = utc.localize(schedule_end_datetime).astimezone(viewer_tz).time()
            
            schedule_data.append({
                "day": schedule.day_of_week,
                "start_time": schedule_start_time_local.strftime('%H:%M%Z') if schedule.start_time and schedule_start_time_local else None,
                "end_time": schedule_end_time_local.strftime('%H:%M%Z') if schedule.end_time and schedule_end_time_local else None,
                "is_virtual": schedule.is_virtual,
                "is_unavailable": schedule.is_unavailable,
                "has_day_off": time_off_data.get(schedule.day_of_week, False)
            })
        except Exception as e:
            return jsonify({'message': f"Error converting schedule times: {e}"}), 500
    
    return jsonify({"schedule": schedule_data, "timezone": viewer_tz.zone})

# Get All Schedules (Admin Only)
@api_v1.route('/schedule/all', methods=['GET'], endpoint='get_all_schedules')
@api_key_required(admin_only=True)
@swag_from({
    'tags': ['Admin'],
    'summary': 'Get All Schedules',
    'description': 'Returns all schedules (Admin only).',
    'security': [{'APIKeyAuth': []}],
    'parameters': [
        {
            'name': 'timezone',
            'in': 'query',
            'type': 'string',
            'description': 'Timezone for schedule conversion (default: UTC)'
        }
    ],
    'responses': {
        200: {
            'description': 'All schedules retrieved successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'schedules': {'type': 'object'},
                    'timezone': {'type': 'string'}
                }
            }
        },
        400: {'description': 'Invalid timezone'},
        401: {'description': 'Unauthorized - Missing or invalid API key'},
        403: {'description': 'Forbidden - Admin access required'},
        418: {'description': 'Invalid API key'}
    }
})
def get_all_schedules(user):
    """Returns all schedules (Admin only)."""
    schedules = WeeklySchedule.query.all()
    time_off_requests = TimeOffRequest.query.filter_by(user_id=user.id).all()

    # Get timezone from request args, default to UTC if not provided
    tz_name = request.args.get('timezone', 'UTC')
    try:
        viewer_tz = tz(tz_name)
    except Exception as e:
        return jsonify({'message': f"Invalid timezone: {e}"}), 400

    today = datetime.today().date()
    time_off_requests = [t for t in time_off_requests if t.date >= today]

    time_off_data = {}
    for t in time_off_requests:
        day_of_week = t.date.strftime("%A")
        if t.user_id not in time_off_data:
            time_off_data[t.user_id] = {}
        time_off_data[t.user_id][day_of_week] = True

    all_schedules = {}
    for schedule in schedules:
        if schedule.user_id not in all_schedules:
            all_schedules[schedule.user_id] = {
                "user_id": schedule.user_id,
                "schedules": []
            }
        
        # Convert the schedule times to the specified timezone
        try:
            if schedule.start_time:
                schedule_start_datetime = datetime.combine(datetime.today(), schedule.start_time)
                schedule_start_time_local = utc.localize(schedule_start_datetime).astimezone(viewer_tz).time()
            if schedule.end_time:
                schedule_end_datetime = datetime.combine(datetime.today(), schedule.end_time)
                schedule_end_time_local = utc.localize(schedule_end_datetime).astimezone(viewer_tz).time()
            
            all_schedules[schedule.user_id]["schedules"].append({
                "day": schedule.day_of_week,
                "start_time": schedule_start_time_local.strftime('%H:%M%Z') if schedule.start_time and schedule_start_time_local else None,
                "end_time": schedule_end_time_local.strftime('%H:%M%Z') if schedule.end_time and schedule_end_time_local else None,
                "is_virtual": schedule.is_virtual,
                "is_unavailable": schedule.is_unavailable,
                "has_day_off": time_off_data.get(schedule.user_id, {}).get(schedule.day_of_week, False)
            })
        except Exception as e:
            return jsonify({'message': f"Error converting schedule times: {e}"}), 500
    
    return jsonify({"schedules": all_schedules, "timezone": viewer_tz.zone})

# Get User Schedule by Identifier (Admin Only)
@api_v1.route('/schedule/<identifier>', methods=['GET'], endpoint='get_user_schedule_by_identifier')
@api_key_required(admin_only=True)
@swag_from({
    'tags': ['Admin'],
    'summary': 'Get User Schedule by Identifier',
    'description': 'Returns the schedule for a specific Slack username or user ID (Admin only).',
    'security': [{'APIKeyAuth': []}],
    'parameters': [
        {
            'name': 'identifier',
            'in': 'path',
            'type': 'string',
            'description': 'Slack username or user ID'
        },
        {
            'name': 'timezone',
            'in': 'query',
            'type': 'string',
            'description': 'Timezone for schedule conversion (default: UTC)'
        }
    ],
    'responses': {
        200: {
            'description': 'Schedule retrieved successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'schedule': {'type': 'array', 'items': {
                        'properties': {
                            'day': {'type': 'string'},
                            'start_time': {'type': 'string'},
                            'end_time': {'type': 'string'},
                            'is_virtual': {'type': 'boolean'},
                            'is_unavailable': {'type': 'boolean'}
                        }
                    }},
                    'timezone': {'type': 'string'}
                }
            }
        },
        400: {'description': 'Invalid identifier or timezone'},
        401: {'description': 'Unauthorized - Missing or invalid API key'},
        403: {'description': 'Forbidden - Admin access required'},
        418: {'description': 'Invalid API key'}
    }
})
def get_user_schedule_by_identifier(user, identifier):
    """Returns the schedule for a specific Slack username or user ID (Admin only)."""
    if identifier.isdigit():
        target_user = User.query.filter_by(id=int(identifier), role='user').first()
    else:
        target_user = User.query.filter_by(slack_username=identifier, role='user').first()

    if not target_user:
        return jsonify({'message': 'User not found'}), 400

    schedules = WeeklySchedule.query.filter_by(user_id=target_user.id).all()
    time_off_requests = TimeOffRequest.query.filter_by(user_id=user.id).all()
    
    # Get timezone from request args, default to UTC if not provided
    tz_name = request.args.get('timezone', 'UTC')
    try:
        viewer_tz = tz(tz_name)
    except Exception as e:
        return jsonify({'message': f"Invalid timezone: {e}"}), 400

    # Filter time-off requests for current and future dates only
    today = datetime.today().date()
    start_of_week = today - timedelta(days=today.weekday()) # Get Monday of this week
    days_of_week = [(start_of_week + timedelta(days=i)).strftime("%A, %b %d") for i in range(7)] # Monday to Sunday
    day_date_mapping = {d.split(",")[0]: d for d in days_of_week}  # {"Monday": "Monday, Feb 05", ...}
    
    time_off_requests = [t for t in time_off_requests if t.date >= today]

    # Organize time-off data properly
    time_off_data = {}
    for t in time_off_requests:
        day_of_week = t.date.strftime("%A") # Convert date to day name
        time_off_data[day_of_week] = True

    schedule_data = []
    for schedule in schedules:
        # Convert the schedule times to the specified timezone
        try:
            if schedule.start_time:
                schedule_start_datetime = datetime.combine(datetime.today(), schedule.start_time)
                schedule_start_time_local = utc.localize(schedule_start_datetime).astimezone(viewer_tz).time()
            if schedule.end_time:
                schedule_end_datetime = datetime.combine(datetime.today(), schedule.end_time)
                schedule_end_time_local = utc.localize(schedule_end_datetime).astimezone(viewer_tz).time()
            
            schedule_data.append({
                "day": schedule.day_of_week,
                "start_time": schedule_start_time_local.strftime('%H:%M%Z') if schedule.start_time and schedule_start_time_local else None,
                "end_time": schedule_end_time_local.strftime('%H:%M%Z') if schedule.end_time and schedule_end_time_local else None,
                "is_virtual": schedule.is_virtual,
                "is_unavailable": schedule.is_unavailable,
                "has_day_off": time_off_data[schedule.day_of_week]
            })
        except Exception as e:
            return jsonify({'message': f"Error converting schedule times: {e}"}), 500
    
    return jsonify({"schedule": schedule_data, "timezone": viewer_tz.zone})

# Get Full Schedule Image (Admin Only)
@api_v1.route('/schedule/image', methods=['GET'], endpoint='get_schedules_image')
@api_key_required(admin_only=True)
@swag_from({
    'tags': ['Admin'],
    'summary': 'Get Full Schedule Image',
    'description': 'Returns an image representation of all schedules (Admin only).',
    'security': [{'APIKeyAuth': []}],
    'parameters': [
        {
            'name': 'timezone',
            'in': 'query',
            'type': 'string',
            'description': 'Timezone for schedule conversion (default: UTC)'
        }
    ],
    'responses': {
        200: {
            'description': 'Schedule image retrieved successfully',
            'content': {
                'image/png': {
                    'schema': {
                        'type': 'string',
                        'format': 'binary'
                    }
                }
            }
        },
        400: {'description': 'Invalid timezone'},
        401: {'description': 'Unauthorized - Missing or invalid API key'},
        403: {'description': 'Forbidden - Admin access required'},
        418: {'description': 'Invalid API key'}
    }
})
def get_schedules_image(user):
    """Returns an image representation of all schedules (Admin only)."""

    schedules = WeeklySchedule.query.all()
    time_off_requests = TimeOffRequest.query.all()
    users = {u.id: f"{u.first_name} {u.last_name}" for u in User.query.filter_by(role='user').order_by(User.first_name, User.last_name).all()} # Sort by name

    # Get timezone from request args, default to UTC if not provided
    tz_name = request.args.get('timezone', 'UTC')
    try:
        viewer_tz = tz(tz_name)
    except Exception as e:
        return jsonify({'message': f"Invalid timezone: {e}"}), 400

    # Get the current week's Monday and calculate all dates for this week
    today = datetime.today().date()
    start_of_week = today - timedelta(days=today.weekday())  # Get Monday of this week
    days_of_week = [(start_of_week + timedelta(days=i)).strftime("%A, %b %d") for i in range(7)]  # Monday to Sunday
    day_date_mapping = {d.split(",")[0]: d for d in days_of_week}  # {"Monday": "Monday, Feb 05", ...}

    # Filter time-off requests for current and future dates only
    time_off_requests = [t for t in time_off_requests if t.date >= today]

    # Organize time-off data properly
    time_off_data = {}
    for t in time_off_requests:
        day_of_week = t.date.strftime("%A")  # Convert date to day name
        if t.user_id not in time_off_data:
            time_off_data[t.user_id] = {}
        time_off_data[t.user_id][day_of_week] = "Day Off"

    # Organize schedule data
    schedule_data = {}
    for schedule in schedules:
        user_id = schedule.user_id
        day = schedule.day_of_week

        if user_id not in schedule_data:
            schedule_data[user_id] = {"user": users[user_id], "schedule": {d: "No Schedule" for d in day_date_mapping.keys()}}

        # Convert schedule times to the specified timezone
        start_time_str, end_time_str = None, None
        try:
            if schedule.start_time:
                start_dt = datetime.combine(datetime.today(), schedule.start_time)
                start_time_local = utc.localize(start_dt).astimezone(viewer_tz).time()
                start_time_str = start_time_local.strftime('%H:%M %Z')
            if schedule.end_time:
                end_dt = datetime.combine(datetime.today(), schedule.end_time)
                end_time_local = utc.localize(end_dt).astimezone(viewer_tz).time()
                end_time_str = end_time_local.strftime('%H:%M %Z')

            # Construct schedule entry
            if start_time_str and end_time_str:
                entry = f"{start_time_str} - {end_time_str}"
            else:
                entry = "No Schedule"

            if schedule.is_virtual:
                entry += "\n (Virtual)"
            if schedule.is_unavailable:
                entry = "Unavailable"

            # If user has a time-off entry for this day, override it
            if user_id in time_off_data and day in time_off_data[user_id]:
                entry = time_off_data[user_id][day]

            schedule_data[user_id]["schedule"][day] = entry
        except Exception as e:
            return jsonify({'message': f"Error converting schedule times: {e}"}), 500

    # Convert data into a Pandas DataFrame
    schedule_rows = []
    for user_id, details in sorted(schedule_data.items(), key=lambda item: item[1]["user"]):
        row = [details["user"]] + [details["schedule"][day] for day in day_date_mapping.keys()]
        schedule_rows.append(row)

    df = pd.DataFrame(schedule_rows, columns=["Employee"] + days_of_week)

    # Apply Pandas Styler
    def highlight_virtual(val):
        """Styles Virtual Workdays in Light Blue"""
        return 'background-color: #dbeafe' if "(Virtual)" in val else ''

    def highlight_unavailable(val):
        """Styles Unavailable Days in Light Red"""
        return 'background-color: #ffcccc' if "Unavailable" in val else ''
    
    def highlight_off(val):
        """Styles Days Off in Light Yellow"""
        return 'background-color: #fff3c4' if "Day Off" in val else ''

    styled_df = df.style.map(highlight_virtual).map(highlight_unavailable).map(highlight_off) \
        .set_caption(f"Weekly Schedule ({tz_name})") \
        .set_properties(**{'text-align': 'center', 'border': '2px solid black'}) \
        .set_table_styles([
            {'selector': 'caption', 'props': [('font-size', '16px'), ('font-weight', 'bold')]}
        ])

    # Save the styled dataframe as an image
    img_io = io.BytesIO()
    dfi.export(styled_df, img_io, table_conversion="matplotlib", dpi=200)
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')

# Get Schedule Image by Slack Username or User ID (Admin Only)
@api_v1.route('/schedule/image/<identifier>', methods=['GET'], endpoint='get_schedule_image_by_identifier')
@api_key_required(admin_only=True)
@swag_from({
    'tags': ['Admin'],
    'summary': 'Get Schedule Image by Slack Username or User ID',
    'description': 'Returns an image representation of the schedule for a specific Slack username or user ID (Admin only).',
    'security': [{'APIKeyAuth': []}],
    'parameters': [
        {
            'name': 'identifier',
            'in': 'path',
            'type': 'string',
            'description': 'Slack username or user ID'
        },
        {
            'name': 'timezone',
            'in': 'query',
            'type': 'string',
            'description': 'Timezone for schedule conversion (default: UTC)'
        }
    ],
    'responses': {
        200: {
            'description': 'Schedule image retrieved successfully',
            'content': {
                'image/png': {
                    'schema': {
                        'type': 'string',
                        'format': 'binary'
                    }
                }
            }
        },
        400: {'description': 'Invalid identifier or timezone'},
        401: {'description': 'Unauthorized - Missing or invalid API key'},
        403: {'description': 'Forbidden - Admin access required'},
        418: {'description': 'Invalid API key'}
    }
})
def get_schedule_image_by_identifier(user, identifier):
    """Returns an image representation of the schedule for a specific Slack username or user ID (Admin only)."""
    if identifier.isdigit():
        user = User.query.filter_by(id=int(identifier), role='user').first()
    else:
        user = User.query.filter_by(slack_username=identifier, role='user').first()

    if not user:
        return jsonify({'message': 'User not found'}), 400

    schedules = WeeklySchedule.query.filter_by(user_id=user.id).all()
    time_off_requests = TimeOffRequest.query.filter_by(user_id=user.id).all()
    
    # Get timezone from request args, default to UTC if not provided
    tz_name = request.args.get('timezone', 'UTC')
    try:
        viewer_tz = tz(tz_name)
    except Exception as e:
        return jsonify({'message': f"Invalid timezone: {e}"}), 400

    # Get the current week's Monday and calculate all dates for this week
    today = datetime.today().date()
    start_of_week = today - timedelta(days=today.weekday())  # Get Monday of this week
    days_of_week = [(start_of_week + timedelta(days=i)).strftime("%A, %b %d") for i in range(7)]  # Monday to Sunday
    day_date_mapping = {d.split(",")[0]: d for d in days_of_week}  # {"Monday": "Monday, Feb 05", ...}

    # Organize schedule data
    schedule_data = {"user": f"{user.first_name} {user.last_name}", "schedule": {d: "No Schedule" for d in day_date_mapping.keys()}}
    
    # Filter time-off requests for current and future dates only
    time_off_requests = [t for t in time_off_requests if t.date >= today]

    # Organize time-off data properly
    time_off_data = {}
    for t in time_off_requests:
        day_of_week = t.date.strftime("%A")  # Convert date to day name
        time_off_data[day_of_week] = "Day Off"

    for schedule in schedules:
        # Convert schedule times to the specified timezone
        start_time_str, end_time_str = None, None
        try:
            if schedule.start_time:
                start_dt = datetime.combine(datetime.today(), schedule.start_time)
                start_time_local = utc.localize(start_dt).astimezone(viewer_tz).time()
                start_time_str = start_time_local.strftime('%H:%M %Z')
            if schedule.end_time:
                end_dt = datetime.combine(datetime.today(), schedule.end_time)
                end_time_local = utc.localize(end_dt).astimezone(viewer_tz).time()
                end_time_str = end_time_local.strftime('%H:%M %Z')

            # Construct schedule entry
            if start_time_str and end_time_str:
                entry = f"{start_time_str} - {end_time_str}"
            else:
                entry = "No Schedule"

            if schedule.is_virtual:
                entry += "\n (Virtual)"
            if schedule.is_unavailable:
                entry = "Unavailable"

            # If user has a time-off entry for this day, override it
            if schedule.day_of_week in time_off_data:
                entry = time_off_data[schedule.day_of_week]

            schedule_data["schedule"][schedule.day_of_week] = entry
        except Exception as e:
            return jsonify({'message': f"Error converting schedule times: {e}"}), 500

    # Convert data into a Pandas DataFrame
    schedule_rows = [[schedule_data["user"]] + [schedule_data["schedule"][day] for day in day_date_mapping.keys()]]
    df = pd.DataFrame(schedule_rows, columns=["Employee"] + days_of_week)

    # Apply Pandas Styler
    def highlight_virtual(val):
        """Styles Virtual Workdays in Light Blue"""
        return 'background-color: #dbeafe' if "(Virtual)" in val else ''

    def highlight_unavailable(val):
        """Styles Unavailable Days in Light Red"""
        return 'background-color: #ffcccc' if "Unavailable" in val else ''
    
    def highlight_off(val):
        """Styles Days Off in Light Yellow"""
        return 'background-color: #fff3c4' if "Day Off" in val else ''

    styled_df = df.style.applymap(highlight_virtual).applymap(highlight_unavailable).applymap(highlight_off) \
        .set_caption(f"Weekly Schedule ({tz_name})") \
        .set_properties(**{'text-align': 'center', 'border': '2px solid black'}) \
        .set_table_styles([
            {'selector': 'caption', 'props': [('font-size', '16px'), ('font-weight', 'bold')]}
        ])

    # Save the styled dataframe as an image
    img_io = io.BytesIO()
    dfi.export(styled_df, img_io, table_conversion="matplotlib", dpi=200)
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')
