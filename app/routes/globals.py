""" GLOBAL CONTEXT PROCESSORS """

from flask import Blueprint, request
import user_agents


globals = Blueprint('globals', __name__)

# USER AGENT
@globals.app_context_processor
def inject_device_type():
    user_agent = request.headers.get("User-Agent", "")
    try:
        ua = user_agents.parse(user_agent)
        is_mobile = ua.is_mobile
    except Exception:
        is_mobile = False
    return {"is_mobile": is_mobile}