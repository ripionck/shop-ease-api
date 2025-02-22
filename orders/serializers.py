from rest_framework import serializers
from products.models import Product
from .models import OrderItem, Order


class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField(source='product.id')
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(
        source='product.price', read_only=True, max_digits=10, decimal_places=2)

    class Meta:
        model = OrderItem
        fields = ['product_id', 'quantity', 'price',
                  'product_name', 'product_price']
        read_only_fields = ['id', 'price', 'product_name', 'product_price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user_id', 'total_amount', 'items', 'status', 'shipping_address',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at',
                            'updated_at', 'items', 'total_amount']
