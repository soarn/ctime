from functools import wraps
from flask import request, jsonify
from app.db.db_models import User

def api_key_required(admin_only=False):
    """Decorator to require an API key for access."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': 'Invalid Authorization header format. Use: Bearer <API_KEY>'}), 401
            api_key = auth_header.replace('Bearer ', '')
            if not api_key:
                return jsonify({'error': 'Missing API key'}), 401
            
            user = User.query.filter_by(api_key=api_key).first()
            if not user:
                return jsonify({'error': 'Invalid API key'}), 418
            
            if admin_only and user.role != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
            
            return f(user, *args, **kwargs) # Pass user to route
        return decorated_function
    return decorator
