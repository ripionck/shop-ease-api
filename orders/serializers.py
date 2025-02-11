from rest_framework import serializers
from products.models import Product
from .models import Order, OrderItem
from decimal import Decimal

class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']
        read_only_fields = ['id', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, write_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)  
    shipping = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    tax = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)    

    class Meta:
        model = Order
        fields = ['id', 'user', 'items', 'subtotal', 'shipping', 'tax', 'total', 'status', 'shipping_address', 'payment_method', 'created_at', 'updated_at']  
        read_only_fields = ['id', 'subtotal', 'total', 'created_at', 'updated_at', 'status']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        shipping_address = validated_data.pop('shipping_address')
        shipping = validated_data.pop('shipping')
        tax = validated_data.pop('tax')
        order = Order.objects.create(shipping_address=shipping_address, shipping=shipping, tax=tax, **validated_data) 

        subtotal = Decimal(0)
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            price = product.price
            OrderItem.objects.create(order=order, product=product, quantity=quantity, price=price)
            subtotal += Decimal(price) * Decimal(quantity)

        order.subtotal = subtotal
        order.total = subtotal + shipping + tax 
        order.save()
        return order