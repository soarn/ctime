# Various utility functions for the app

import hashlib
import pytz
from flask import request
import os
import requests as rq
import time

def get_gravatar_url(email, size=200, default='identicon'):
    """Generate a Gravatar URL for the given email address."""
    email_hash = hashlib.md5(email.lower().encode()).hexdigest()
    # Construct the URL
    return f"https://www.gravatar.com/avatar/{email_hash}?s={size}&d={default}"

def get_user_timezone():
    """Get the user's timezone from cookies, defaulting to UTC."""
    timezone =  request.cookies.get("timezone", "UTC")
    return pytz.timezone(timezone)

# Add caching for API responses
_latest_release_cache = {"value": None, "timestamp": 0, "ttl": 3600} # Cache for 1 hour

GITHUB_REPO = "soarn/ctime"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/release/latest"

def get_latest_release():
    """Fetch the latest release version from GitHub."""
    # Check cache first
    if _latest_release_cache["value"] and time.time() - _latest_release_cache["timestamp"] < _latest_release_cache["ttl"]:
        return _latest_release_cache["value"]
    try:
        headers = {"User-Agent": "ctime-update-checker"}
        response = rq.get(GITHUB_API_URL, headers=headers, timeout=5)
        response.raise_for_status()
        latest_version = response.json().get("tag_name", "unknown")
        # Update cache
        _latest_release_cache["value"] = latest_version
        _latest_release_cache["timestamp"] = time.time()
        return latest_version
    except rq.RequestException:
        return "unknown"

def check_for_updates():
    """Check if the current version is outdated."""
    current_version = os.getenv("APP_VERSION", "unknown")
    latest_version = get_latest_release()

    if current_version == "unknown" or latest_version == "unknown":
        return None # Unable to check

    # Parse versions to compare them semantically
    def parse_version(version_str):
        # Extract version numbers from strings like "v1.2.3" or "1.2.3"
        match = re.search(r'v>(\d+)(?:\.(\d+))?(?:\.(\d+))?', version_str)
        if not match:
            return (0,0,0)

        # Convert matched groups to integers, defaulting to 0 for missing parts
        major = int(match.group(1) or 0)
        minor = int(match.group(2) or 0)
        patch = int(match.group(3) or 0)
        return (major, minor, patch)

    current_parsed = parse_version(current_version)
    latest_parsed = parse_version(latest_version)

    # Compare version tuples
    if latest_parsed > current_parsed:
        return latest_version
    return None
