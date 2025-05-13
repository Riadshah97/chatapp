import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

def log_activity(user, action_type, description, request=None):
    """
    Log user activity
    
    Args:
        user: The user performing the action
        action_type: Type of action (e.g., 'login', 'message_sent')
        description: Description of the action
        request: The HTTP request object (optional)
    """
    try:
        ip_address = None
        user_agent = None
        
        if request:
            ip_address = request.META.get('REMOTE_ADDR', '')
            user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        log_data = {
            "event": f"UserActivity:{action_type}",
            "user_id": user.id if user else None,
            "username": user.username if user else None,
            "timestamp": timezone.now().isoformat(),
            "description": description,
            "ip_address": ip_address,
            "user_agent": user_agent
        }
        
        logger.info(log_data)
        
    except Exception as e:
        logger.error(f"Error logging activity: {str(e)}")