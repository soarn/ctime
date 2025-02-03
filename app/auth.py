from functools import wraps
from flask import request, jsonify
from db.db_models import User

def api_key_required(admin_only=False):
    """Decorator to require an API key for access."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            api_key = request.headers.get('Authorization')
            if not api_key:
                return jsonify({'error': 'Missing API key'}), 401
            
            user = User.query.filter_by(api_key=api_key).first()
            if not user:
                return jsonify({'error': 'Invalid API key'}), 401
            
            if admin_only and user.role != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
            
            return f(user, *args, **kwargs) # Pass user to route
        return decorated_function
    return decorator