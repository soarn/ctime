from datetime import datetime
from flask import Blueprint, jsonify, request
from flasgger import swag_from
from pytz import utc, timezone as tz
from db.db_models import User, WeeklySchedule
from auth import api_key_required

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
                    'role': {'type': 'string'}
                }
            }
        },
        401: {'description': 'Unauthorized - Missing or invalid API key'},
        418: {'description': 'Invalid API key'}
    }
})
def get_user(user):
    """Returns the details of the authenticated user."""
    # return jsonify({'user': user.to_dict()}), 200
    return jsonify({
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
        "email": user.email,
        "role": user.role,
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
                        'role': {'type': 'string'}
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
        "username": u.username, "email": u.email, "role": u.role
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
    
    # Get timezone from request args, default to UTC if not provided
    tz_name = request.args.get('timezone', 'UTC')
    try:
        viewer_tz = tz(tz_name)
    except Exception as e:
        return jsonify({'message': f"Invalid timezone: {e}"}), 400

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
                "start_time": schedule_start_time_local.strftime('%H:%M%Z') if schedule.start_time else None,
                "end_time": schedule_end_time_local.strftime('%H:%M%Z') if schedule.end_time else None,
                "is_virtual": schedule.is_virtual,
                "is_unavailable": schedule.is_unavailable
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

    # Get timezone from request args, default to UTC if not provided
    tz_name = request.args.get('timezone', 'UTC')
    try:
        viewer_tz = tz(tz_name)
    except Exception as e:
        return jsonify({'message': f"Invalid timezone: {e}"}), 400

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
                "start_time": schedule_start_time_local.strftime('%H:%M%Z') if schedule.start_time else None,
                "end_time": schedule_end_time_local.strftime('%H:%M%Z') if schedule.end_time else None,
                "is_virtual": schedule.is_virtual,
                "is_unavailable": schedule.is_unavailable
            })
        except Exception as e:
            return jsonify({'message': f"Error converting schedule times: {e}"}), 500
    
    return jsonify({"schedules": all_schedules, "timezone": viewer_tz.zone})
