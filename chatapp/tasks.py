import os
import requests
from celery import shared_task
from django.utils.translation import gettext_lazy as _
from .repositories import ChatSessionRepository, ChatMessageRepository
from .utils import log_activity
import logging

logger = logging.getLogger(__name__)

@shared_task
def process_chat_request(session_id, message_id):
    """
    Process a chat request asynchronously using OpenAI API
    """
    try:
        message_repo = ChatMessageRepository()
        session_repo = ChatSessionRepository()
        
        # Get the message that needs a response
        message = message_repo.get_message_by_id(message_id)
        if not message:
            logger.error({"event": "ProcessChatRequest:error", "message": "Message not found"})
            return {"success": False, "error": "Message not found"}
            
        session = session_repo.get_session_by_id(session_id, message.session.user)
        if not session:
            logger.error({"event": "ProcessChatRequest:error", "message": "Session not found"})
            return {"success": False, "error": "Session not found"}
        
        # Get conversation history (last 10 messages for context)
        history = message_repo.get_recent_messages(session, 10)
        if not history:
            logger.error({"event": "ProcessChatRequest:error", "message": "Failed to retrieve message history"})
            return {"success": False, "error": "Failed to retrieve message history"}
            
        messages = [{"role": msg.role, "content": msg.content} for msg in history]
        
        # Call OpenAI API
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise ValueError(_("OPENAI_API_KEY environment variable not set"))
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": messages
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            logger.error({"event": "OpenAIAPI:error", "message": response.text})
            raise Exception(_("OpenAI API returned status code {status_code}").format(
                status_code=response.status_code
            ))
        
        # Extract the assistant's response
        response_data = response.json()
        assistant_response = response_data['choices'][0]['message']['content']
        
        # Save the assistant's response to the database
        assistant_message = message_repo.create_message(
            session=session,
            role='assistant',
            content=assistant_response
        )
        
        if not assistant_message:
            logger.error({"event": "ProcessChatRequest:error", "message": "Failed to save assistant message"})
            return {"success": False, "error": "Failed to save assistant message"}
        
        # Log the activity
        log_activity(
            session.user, 
            'ai_response', 
            _("AI responded to user message")
        )
        
        return {
            "success": True, 
            "response": assistant_response,
            "message_id": assistant_message.id
        }
        
    except Exception as e:
        logger.error({"event": "ProcessChatRequest:error", "message": str(e)})
        return {"success": False, "error": str(e)}
