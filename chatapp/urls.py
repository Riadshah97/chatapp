from django.urls import path
from .views import (
    ChatSessionListView,
    ChatSessionDetailView,
    ChatView,
    ChatMessagesView
)

urlpatterns = [
    path('sessions/', ChatSessionListView.as_view(), name='chat-sessions'),
    path('sessions/<int:session_id>/', ChatSessionDetailView.as_view(), name='chat-session-detail'),
    path('send/', ChatView.as_view(), name='chat-send'),
    path('messages/<int:session_id>/', ChatMessagesView.as_view(), name='chat-messages'),
]