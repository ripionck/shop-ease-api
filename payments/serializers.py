from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'amount', 'payment_method',
            'transaction_id', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'transaction_id', 'status',
            'created_at', 'updated_at'
        ]

