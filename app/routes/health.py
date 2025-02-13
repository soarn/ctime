from flask import Blueprint, jsonify
from app.db.db import db

health = Blueprint('health', __name__)

@health.route('/heath')
def health_check():
    try:
        # Check database connectivity
        db.session.execute('SELECT 1')
        return jsonify({
            'status': 'healthy',
            'database': 'connected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }), 503
