from rest_framework import serializers
from categories.models import Category
from .models import Product, ProductImage


class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'image_url', 'is_main']
        read_only_fields = ['id', 'image_url']

    def get_image_url(self, obj):
        return obj.image.url


class ProductSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    category_id = serializers.UUIDField(write_only=True)
    category = serializers.StringRelatedField(read_only=True)
    specifications = serializers.JSONField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category', 'description', 'price',
            'discounted_price', 'category_id', 'brand', 'stock_quantity',
            'is_active', 'rating', 'images', 'features',
            'specifications', 'tags', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'rating', 'created_at',
            'updated_at', 'images', 'category'
        ]

    def get_images(self, obj):
        images = obj.product_images.all()
        return ProductImageSerializer(images, many=True).data

    def validate_specifications(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Specifications must be a JSON object")
        return value

    def create(self, validated_data):
        validated_data['category'] = Category.objects.get(
            pk=validated_data.pop('category_id')
        )
        return super().create(validated_data)
