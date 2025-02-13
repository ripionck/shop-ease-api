from rest_framework import serializers
from products.models import Product
from .models import Wishlist

class WishlistProductSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()

    def validate_product_id(self, value):
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError("Product does not exist.")
        return value

class WishlistSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()

    class Meta:
        model = Wishlist
        fields = ['products', 'created_at']  
        read_only_fields = ['created_at']

    def get_products(self, obj):
        product_data = []
        for product in obj.products.all():
            main_image = product.images.filter(is_main=True).first()
            product_data.append({
                "product_id": product.id,
                "name": product.name,
                "price": product.price,
                "thumbnail": main_image.image.url if main_image else None
            })
        return product_data