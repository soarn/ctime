from flask import Blueprint, jsonify
from sqlalchemy import text
from app.db.db import db

health = Blueprint('health', __name__)

@health.route('/health', methods=['GET'])
def health_check():
    try:
        # Check database connectivity
        db.session.execute(text("SELECT 1")).scalar()
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
