from rest_framework import serializers
from .models import OrderItem, Order

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']
        read_only_fields = ['id', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user_id', 'total_amount', 'items','status', 'shipping', 'tax',
            'payment_method','shipping_address', 'created_at', 'updated_at', 
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'items']

    def validate_shipping_address(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Shipping address must be a JSON object.")
        return value