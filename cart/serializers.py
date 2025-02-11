from rest_framework import serializers
from .models import ShoppingCart, CartItem, Product

class ProductCartSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField(source='product.id', read_only=True) 
    title = serializers.CharField(source='product.name')
    price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2)
    quantity = serializers.IntegerField()
    total = serializers.SerializerMethodField()
    discountPercentage = serializers.SerializerMethodField()
    discountedTotal = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            'product_id', 'title', 'price', 'quantity', 'total',
            'discountPercentage', 'discountedTotal', 'thumbnail'
        ]
    
    def get_total(self, obj):
        return round(obj.quantity * float(obj.product.price), 2)

    def get_discountPercentage(self, obj):
        if obj.product.discounted_price:
            original_price = float(obj.product.price)
            discounted_price = float(obj.product.discounted_price)
            return round(((original_price - discounted_price) / original_price) * 100, 2)
        return 0

    def get_discountedTotal(self, obj):
        if obj.product.discounted_price:
            return round(obj.quantity * float(obj.product.discounted_price), 2)
        return self.get_total(obj)

    def get_thumbnail(self, obj):
        main_image = obj.product.images.filter(is_main=True).first()
        return main_image.image.url if main_image else None


class ShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True) 
    products = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    discountedTotal = serializers.SerializerMethodField()
    userId = serializers.UUIDField(source='user.id', read_only=True)
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
    

class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)

    def validate_product_id(self, value):
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError("Product does not exist.")
        return value


class CartItemUpdateSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(min_value=0, required=False) # 
    product_id = serializers.UUIDField(required=False, allow_null=True)
    class Meta:
        model = CartItem
        fields = ['quantity', 'product_id']
    def validate(self, data):
        quantity = data.get('quantity')
        product_id = data.get('product_id')
        if quantity is None and product_id is None:
            raise serializers.ValidationError("At least one of 'quantity' or 'product_id' must be provided.")
        if product_id is not None and not Product.objects.filter(id=product_id).exists():
            raise serializers.ValidationError("Product does not exist.")
        return data


    


