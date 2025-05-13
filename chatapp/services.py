import logging
from django.utils.translation import gettext_lazy as _
from .repositories import ChatSessionRepository, ChatMessageRepository

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        self.session_repo = ChatSessionRepository()
        self.message_repo = ChatMessageRepository()

    def create_user_message(self, user, message, session_id=None):
        """
        Create a user message and return the session and message objects
        """
        try:
            # Get or create a chat session
            if session_id:
                session = self.session_repo.get_session_by_id(session_id, user)
                if not session:
                    return None, None, _("Chat session not found")
            else:
                session = self.session_repo.create_session(user)
                if not session:
                    return None, None, _("Failed to create chat session")
            
            # Save the user message
            user_message = self.message_repo.create_message(
                session=session,
                role='user',
                content=message
            )
            
            if not user_message:
                return None, None, _("Failed to create user message")
            
            # Update the session's last updated timestamp
            session.save()
            
            return session, user_message, None
            
        except Exception as e:
            logger.error(f"Error creating user message: {str(e)}")
            return None, None, _("An error occurred while processing your request")
    
    def get_session_messages(self, user, session_id):
        """
        Get all messages for a specific chat session
        """
        try:
            session = self.session_repo.get_session_by_id(session_id, user)
            if not session:
                return None, None, _("Chat session not found")
            
            messages = self.message_repo.get_session_messages(session)
            if messages is None:
                return None, None, _("Failed to retrieve chat messages")
            
            return session, messages, None
            
        except Exception as e:
            logger.error(f"Error retrieving session messages: {str(e)}")
            return None, None, _("An error occurred while retrieving messages")
    
    def get_user_sessions(self, user):
        """
        Get all chat sessions for a user
        """
        try:
            sessions = self.session_repo.get_user_sessions(user)
            if sessions is None:
                return None, _("Failed to retrieve chat sessions")
            
            return sessions, None
            
        except Exception as e:
            logger.error(f"Error retrieving user sessions: {str(e)}")
            return None, _("An error occurred while retrieving sessions")
    
    def delete_session(self, user, session_id):
        """
        Delete a chat session
        """
        try:
            success = self.session_repo.delete_session(session_id, user)
            if not success:
                return False, _("Chat session not found or could not be deleted")
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error deleting session: {str(e)}")
            return False, _("An error occurred while deleting the session")
