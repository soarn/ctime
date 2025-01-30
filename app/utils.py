# Various utility functions for the app

import hashlib
import pytz
from flask import request


def get_gravatar_url(email, size=200, default='identicon'):
    """Generate a Gravatar URL for the given email address."""
    email_hash = hashlib.md5(email.lower().encode()).hexdigest()
    # Construct the URL
    return f"https://www.gravatar.com/avatar/{email_hash}?s={size}&d={default}"

def get_user_timezone():
    """Get the user's timezone from cookies, defaulting to UTC."""
    timezone =  request.cookies.get("timezone", "UTC")
    return pytz.timezone(timezone)