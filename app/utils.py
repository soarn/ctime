# Various utility functions for the app

import hashlib


def get_gravatar_url(email, size=200, default='identicon'):
    """Generate a Gravatar URL for the given email address."""
    email_hash = hashlib.md5(email.lower().encode()).hexdigest()
    # Construct the URL
    return f"https://www.gravatar.com/avatar/{email_hash}?s={size}&d={default}"