from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'notification_type', 'message',
            'is_read', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def validate_notification_type(self, value):
        """
        Validate that the notification_type is one of the allowed choices.
        """
        if value not in dict(Notification.NOTIFICATION_TYPE_CHOICES):
            raise serializers.ValidationError("Invalid notification type.")
        return value
