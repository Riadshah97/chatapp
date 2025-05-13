import logging
from django.utils.translation import gettext_lazy as _
from .models import ChatSession, ChatMessage

logger = logging.getLogger(__name__)

class ChatSessionRepository:
    @staticmethod
    def get_user_sessions(user):
        """Get all chat sessions for a user"""
        try:
            return ChatSession.objects.filter(user=user).order_by('-updated_at')
        except Exception as e:
            logger.error(f"Error retrieving user sessions: {str(e)}")
            return None

    @staticmethod
    def get_session_by_id(session_id, user):
        """Get a specific chat session by ID for a user"""
        try:
            return ChatSession.objects.get(id=session_id, user=user)
        except ChatSession.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Error retrieving session by ID: {str(e)}")
            return None

    @staticmethod
    def create_session(user):
        """Create a new chat session for a user"""
        try:
            return ChatSession.objects.create(user=user)
        except Exception as e:
            logger.error(f"Error creating chat session: {str(e)}")
            return None

    @staticmethod
    def delete_session(session_id, user):
        """Delete a chat session"""
        try:
            session = ChatSession.objects.get(id=session_id, user=user)
            session.delete()
            return True
        except ChatSession.DoesNotExist:
            return False
        except Exception as e:
            logger.error(f"Error deleting session: {str(e)}")
            return False

class ChatMessageRepository:
    @staticmethod
    def get_session_messages(session):
        """Get all messages for a chat session"""
        try:
            return ChatMessage.objects.filter(session=session).order_by('created_at')
        except Exception as e:
            logger.error(f"Error retrieving session messages: {str(e)}")
            return None

    @staticmethod
    def get_message_by_id(message_id):
        """Get a specific message by ID"""
        try:
            return ChatMessage.objects.get(id=message_id)
        except ChatMessage.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Error retrieving message by ID: {str(e)}")
            return None

    @staticmethod
    def create_message(session, role, content):
        """Create a new message in a chat session"""
        try:
            return ChatMessage.objects.create(
                session=session,
                role=role,
                content=content
            )
        except Exception as e:
            logger.error(f"Error creating chat message: {str(e)}")
            return None

    @staticmethod
    def get_recent_messages(session, limit=10):
        """Get the most recent messages for a chat session"""
        try:
            return ChatMessage.objects.filter(session=session).order_by('created_at')[:limit]
        except Exception as e:
            logger.error(f"Error retrieving recent messages: {str(e)}")
            return None