from rest_framework import serializers

from products.models import Product
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())  

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']
        read_only_fields = ['id', 'price', 'created_at'] 

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, write_only=True)  
    user = serializers.HiddenField(default=serializers.CurrentUserDefault()) 
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True) 

    class Meta:
        model = Order
        fields = ['id', 'user', 'items', 'total_amount', 'status', 'shipping_address', 'payment_method', 'created_at', 'updated_at']
        read_only_fields = ['id', 'total_amount', 'created_at', 'updated_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(total_amount=0,**validated_data)

        total_amount = 0
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            price = product.price  
            OrderItem.objects.create(order=order, product=product, quantity=quantity, price=price)
            total_amount += price * quantity

        order.total_amount = total_amount
        order.save()
        return order