import logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema

from .serializers import (
    ChatSessionSerializer, 
    ChatMessageSerializer, 
    ChatRequestSerializer,
    UserSerializer
)
from .tasks import process_chat_request
from .services import ChatService

logger = logging.getLogger(__name__)

class BaseApiView(APIView):
    permission_classes = [IsAuthenticated]

class ChatSessionListView(BaseApiView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chat_service = ChatService()

    def get(self, request):
        try:
            sessions, error = self.chat_service.get_user_sessions(request.user)
            
            if not sessions:
                result = {
                    "message": error,
                }
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
            result = {
                "message": _("Chat sessions retrieved successfully."),
                "data": {
                    "sessions": ChatSessionSerializer(sessions, many=True).data,
                },
            }
            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error({"event": "ChatSessionListView:get", "message": "Unexpected error occurred", "error": str(e)})
            raise e
    
    @swagger_auto_schema(request_body=ChatSessionSerializer)
    def post(self, request):
        try:
            serializer = ChatSessionSerializer(data=request.data)
            if not serializer.is_valid():
                result = {
                    "message": _("Invalid input. Please check the provided details."),
                    "errors": serializer.errors,
                }
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
            session = serializer.save(user=request.user)
            
            result = {
                "message": _("Chat session created successfully."),
                "data": {
                    "session": ChatSessionSerializer(session).data,
                },
            }
            return Response(result, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error({"event": "ChatSessionListView:post", "message": "Unexpected error occurred", "error": str(e)})
            raise e

class ChatSessionDetailView(BaseApiView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chat_service = ChatService()

    def get(self, request, session_id):
        try:
            session = self.chat_service.session_repo.get_session_by_id(session_id, request.user)
            
            if not session:
                result = {
                    "message": _("Chat session not found."),
                }
                return Response(result, status=status.HTTP_404_NOT_FOUND)
            
            result = {
                "message": _("Chat session retrieved successfully."),
                "data": {
                    "session": ChatSessionSerializer(session).data,
                },
            }
            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error({"event": "ChatSessionDetailView:get", "message": "Unexpected error occurred", "error": str(e)})
            raise e
    
    def delete(self, request, session_id):
        try:
            success, error = self.chat_service.delete_session(request.user, session_id)
            
            if not success:
                result = {
                    "message": error,
                }
                return Response(result, status=status.HTTP_404_NOT_FOUND)
            
            result = {
                "message": _("Chat session deleted successfully."),
            }
            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error({"event": "ChatSessionDetailView:delete", "message": "Unexpected error occurred", "error": str(e)})
            raise e

class ChatView(BaseApiView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chat_service = ChatService()

    @swagger_auto_schema(request_body=ChatRequestSerializer)
    def post(self, request):
        try:
            serializer = ChatRequestSerializer(data=request.data)
            if not serializer.is_valid():
                result = {
                    "message": _("Invalid input. Please check the provided details."),
                    "errors": serializer.errors,
                }
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

            message = serializer.validated_data["message"]
            session_id = serializer.validated_data.get("session_id")
            
            # Get or create a chat session
            session, user_message, error = self.chat_service.create_user_message(
                user=request.user,
                message=message,
                session_id=session_id
            )
            
            if not session:
                result = {
                    "message": error,
                }
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
            # Process the message asynchronously
            process_chat_request.delay(session.id, user_message.id)
            
            result = {
                "message": _("Message received and being processed."),
                "data": {
                    "session_id": session.id,
                    "message_id": user_message.id
                },
            }
            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error({"event": "ChatView:post", "message": "Unexpected error occurred", "error": str(e)})
            raise e

class ChatMessagesView(BaseApiView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chat_service = ChatService()

    def get(self, request, session_id):
        try:
            session, messages, error = self.chat_service.get_session_messages(
                user=request.user,
                session_id=session_id
            )
            
            if not session:
                result = {
                    "message": error,
                }
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
            result = {
                "message": _("Chat messages retrieved successfully."),
                "data": {
                    "session": ChatSessionSerializer(session).data,
                    "messages": ChatMessageSerializer(messages, many=True).data,
                },
            }
            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error({"event": "ChatMessagesView:get", "message": "Unexpected error occurred", "error": str(e)})
            raise e
