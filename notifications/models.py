from django.db import models
from django.conf import settings


class Notification(models.Model):
    """Notification for a user"""
    
    TYPE_CHOICES = [
        ('order', 'Order Update'),
        ('ride', 'Ride Update'),
        ('message', 'Message'),
        ('system', 'System'),
        ('promo', 'Promotion'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='system')
    
    # Optional link
    link = models.CharField(max_length=300, blank=True, null=True)
    
    # Icon (emoji for simplicity)
    icon = models.CharField(max_length=10, default='🔔')
    
    # Status
    is_read = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def mark_as_read(self):
        self.is_read = True
        self.save()
    
    class Meta:
        ordering = ['-created_at']