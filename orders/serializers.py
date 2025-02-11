from rest_framework import serializers
from products.models import Product
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all()) 

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=False)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    shipping = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    tax = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    shipping_address = serializers.JSONField()
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Order
        fields = ['id', 'user', 'items', 'total_amount', 'status', 'shipping', 'tax', 'shipping_address', 'payment_method', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        user = self.context['user']
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        total_amount = 0
        for item_data in items_data:
            product_id = item_data['product']['product_id']
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                raise serializers.ValidationError(f"Product with ID {product_id} not found.")

            quantity = item_data['quantity']
            price = product.price
            OrderItem.objects.create(order=order, product=product, quantity=quantity, price=price)
            total_amount += quantity * price

        order.total_amount = total_amount
        order.save()
        return order

