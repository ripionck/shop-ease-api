from rest_framework import serializers
from .models import Payment


class PaymentMethodSerializer(serializers.Serializer):
    payment_method_id = serializers.CharField(required=True)
    order_id = serializers.UUIDField(required=True)


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'order', 'amount', 'payment_method',
                  'transaction_id', 'status', 'created_at']
        read_only_fields = ['transaction_id', 'status', 'created_at']
