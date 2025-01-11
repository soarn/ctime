from db.db import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'employee' or 'admin'

    # Hash the password before storing it
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    # Check the password against the stored hash
    def check_password(self, password):
        return check_password_hash(self.password, password)

class WeeklySchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('weekly_schedules', lazy=True))
    day_of_week = db.Column(db.String(10), nullable=False)  # e.g., 'Monday'
    start_time = db.Column(db.Time, nullable=True)
    end_time = db.Column(db.Time, nullable=True)
    is_virtual = db.Column(db.Boolean, default=False)
    is_unavailable = db.Column(db.Boolean, default=False)

class TimeOffRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('time_off_requests', lazy=True))
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(10), default='pending')  # 'pending', 'approved', 'rejected'