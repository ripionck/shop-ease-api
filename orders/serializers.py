from rest_framework import serializers
from .models import OrderItem, Order


class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField(source='product.id')
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(
        source='product.price', read_only=True, max_digits=10, decimal_places=2
    )
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            'product_id', 'quantity', 'price', 'product_name', 'product_price', 'product_image'
        ]
        read_only_fields = ['id', 'price', 'product_name',
                            'product_price', 'product_image']

    def get_product_image(self, obj):
        main_image = obj.product.product_images.filter(is_main=True).first()
        if main_image and main_image.image:
            return main_image.image.url
        return None


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
