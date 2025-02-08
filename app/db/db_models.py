from app.db.db import db
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import secrets

# Database Models
class User(UserMixin, db.Model):
    id            = db.Column(db.Integer       , primary_key =True                                                  )
    first_name    = db.Column(db.String   (50) , nullable    =False                                                 )
    last_name     = db.Column(db.String   (50) , nullable    =False                                                 )
    username      = db.Column(db.String   (80) , nullable    =False, unique=True                                    )
    email         = db.Column(db.String   (100), nullable    =False, unique=True                                    )
    password_hash = db.Column(db.String   (255), nullable    =False                                                 )
    role          = db.Column(db.String   (10) , nullable    =False, default='user'                                 ) # 'user' or 'admin'
    created_at    = db.Column(db.DateTime      , nullable    =False, default=lambda: datetime.now(timezone.utc)     )
    last_login    = db.Column(db.DateTime      , nullable    =True , default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    api_key       = db.Column(db.String   (64) , nullable    =True , unique=True                                    )
    slack_username = db.Column(db.String(50), nullable=True, default=lambda context: context.get_current_parameters()['username'])

    # Hash the password before storing it
    def set_password(self, password):
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in password):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in password):
            raise ValueError("Password must contain at least one number")
        if not any(c in "!@#$%^&*" for c in password):
            raise ValueError("Password must contain at least one special character")
        self.password_hash = generate_password_hash(password)
    
    # Check the password against the stored hash
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # Generate a new API key
    def generate_api_key(self):
        self.api_key = secrets.token_hex(32) # Secure 64-character key
        db.session.commit()
        return self.api_key

    def clear_api_key(self):
        self.api_key = None
        db.session.commit()

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
    VALID_STATUSES = ['pending', 'approved', 'rejected']
    status = db.Column(db.String(10), default='pending', nullable=False)
    __table_args__ = (
        db.CheckConstraint(status.in_(VALID_STATUSES), name='valid_status'),
    )
    comment = db.Column(db.Text(255), nullable=True)