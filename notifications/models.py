from django.db import models
from django.conf import settings

class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ('order_confirmation', 'Order Confirmation'),
        ('payment_success', 'Payment Success'),
        ('payment_failure', 'Payment Failure'),
        ('password_reset', 'Password Reset'),
        ('wishlist_update', 'Wishlist Update'),
        ('review_received', 'Review Received'),
    ]

    id = models.CharField(primary_key=True, max_length=255)  
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPE_CHOICES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification {self.id} for {self.user.first_name}: {self.notification_type}"

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
