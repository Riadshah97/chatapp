from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class ChatSession(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='chat_sessions',
        verbose_name=_("User")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At")
    )
    
    def __str__(self):
        return f"Chat session {self.id} - {self.user.username}"
    
    class Meta:
        verbose_name = _("Chat Session")
        verbose_name_plural = _("Chat Sessions")

class ChatMessage(models.Model):
    ROLE_CHOICES = (
        ('user', _('User')),
        ('assistant', _('Assistant')),
    )
    
    session = models.ForeignKey(
        ChatSession, 
        on_delete=models.CASCADE, 
        related_name='messages',
        verbose_name=_("Chat Session")
    )
    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES,
        db_index=True,
        verbose_name=_("Role")
    )
    content = models.TextField(
        verbose_name=_("Content")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At")
    )
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."
    
    class Meta:
        verbose_name = _("Chat Message")
        verbose_name_plural = _("Chat Messages")
