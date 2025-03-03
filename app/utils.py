# Various utility functions for the app

import hashlib
import pytz
from flask import request
import os
import requests as rq

def get_gravatar_url(email, size=200, default='identicon'):
    """Generate a Gravatar URL for the given email address."""
    email_hash = hashlib.md5(email.lower().encode()).hexdigest()
    # Construct the URL
    return f"https://www.gravatar.com/avatar/{email_hash}?s={size}&d={default}"

def get_user_timezone():
    """Get the user's timezone from cookies, defaulting to UTC."""
    timezone =  request.cookies.get("timezone", "UTC")
    return pytz.timezone(timezone)

GITHUB_REPO = "soarn/ctime"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/release/latest"

def get_latest_release():
    """Fetch the latest release version from GitHub."""
    try:
        response = rq.get(GITHUB_API_URL, timeout=5)
        response.raise_for_status()
        latest_version = response.json().get("tag_name", "unknown")
        return latest_version
    except rq.RequestException:
        return "unknown"

def check_for_updates():
    """Check if the current version is outdated."""
    current_version = os.getenv("APP_VERSION", "unknown")
    latest_version = get_latest_release()

    if current_version == "unknown" or latest_version == "unknown":
        return None # Unable to check

    return latest_version if latest_version != current_version else None
