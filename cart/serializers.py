from rest_framework import serializers
from .models import ShoppingCart, CartItem, Product

class ProductCartSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='product.id')
    title = serializers.CharField(source='product.name')
    price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2)
    quantity = serializers.IntegerField()
    total = serializers.SerializerMethodField()
    discountPercentage = serializers.SerializerMethodField()
    discountedPrice = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            'id', 'title', 'price', 'quantity', 'total',
            'discountPercentage', 'discountedPrice', 'thumbnail'
        ]

    def get_total(self, obj):
        return obj.quantity * float(obj.product.price)

    def get_discountPercentage(self, obj):
        if obj.product.discounted_price:
            original_price = float(obj.product.price)
            discounted_price = float(obj.product.discounted_price)
            return round(((original_price - discounted_price) / original_price) * 100, 2)
        return 0

    def get_discountedPrice(self, obj):
        if obj.product.discounted_price:
            return obj.quantity * float(obj.product.discounted_price)
        return self.get_total(obj)

    def get_thumbnail(self, obj):
        if obj.product:
            return obj.product.main_image
        return None


class ShoppingCartSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    discountedTotal = serializers.SerializerMethodField()
    userId = serializers.CharField(source='user.id')
    totalProducts = serializers.SerializerMethodField()
    totalQuantity = serializers.SerializerMethodField()

    class Meta:
        model = ShoppingCart
        fields = [
            'id', 'products', 'total', 'discountedTotal',
            'userId', 'totalProducts', 'totalQuantity'
        ]

    def get_products(self, obj):
        cart_items = obj.items.all()
        return ProductCartSerializer(cart_items, many=True).data

    def get_total(self, obj):
        return round(sum(
            item.quantity * float(item.product.price)
            for item in obj.items.all()
        ), 2)

    def get_discountedTotal(self, obj):
        return round(sum(
            item.quantity * float(item.product.discounted_price or item.product.price)
            for item in obj.items.all()
        ), 2)


    def get_totalProducts(self, obj):
        return obj.items.count()

    def get_totalQuantity(self, obj):
        return sum(item.quantity for item in obj.items.all())


class CartItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)

    def validate_product_id(self, value):
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError("Product does not exist.")
        return value