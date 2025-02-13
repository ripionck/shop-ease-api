from rest_framework import serializers
from products.models import Product
from .models import Cart, CartItem

class ProductCartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='product.id', read_only=True)
    name = serializers.CharField(source='product.name')
    color = serializers.CharField(source='product.color', allow_null=True, allow_blank=True)
    price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2)
    image = serializers.SerializerMethodField()
    quantity = serializers.IntegerField()

    class Meta:
        model = CartItem
        fields = ['id', 'name', 'color', 'price', 'image', 'quantity']

    def get_image(self, obj):
        main_image = obj.product.images.filter(is_main=True).first()
        return main_image.image.url if main_image and main_image.image else None


class CartSerializer(serializers.ModelSerializer):
    userId = serializers.UUIDField(source='user.id', read_only=True)
    products = serializers.SerializerMethodField()
    updatedAt = serializers.DateTimeField(source='updated_at')

    class Meta:
        model = Cart
        fields = ['userId', 'products', 'updatedAt']

    def get_products(self, obj):
        cart_items = obj.items.all()
        return ProductCartSerializer(cart_items, many=True).data


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)

    def validate_product_id(self, value):
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError("Product does not exist.")
        return value


class CartItemUpdateSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(min_value=0, required=False)
    product_id = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = CartItem
        fields = ['quantity', 'product_id']

    def validate(self, data):
        quantity = data.get('quantity')
        product_id = data.get('product_id')

        if quantity is None and product_id is None:
            raise serializers.ValidationError("At least one of 'quantity' or 'product_id' must be provided.")

        if product_id is not None:
            if not Product.objects.filter(id=product_id).exists():
                raise serializers.ValidationError("Product does not exist.")
            cart = self.instance.cart
            if CartItem.objects.filter(cart=cart, product_id=product_id).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("This Product is already in the cart.")

        return data

    def update(self, instance, validated_data):
        quantity = validated_data.get('quantity')
        product_id = validated_data.get('product_id')

        if quantity is not None:
            instance.quantity = quantity

        if product_id is not None:
            product = Product.objects.get(id=product_id)
            instance.product = product

        instance.save()
        return instance