from rest_framework import serializers
from categories.models import Category
from .models import Product, ProductImage


class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['image_url', 'is_main']
        read_only_fields = ['image_url']

    def get_image_url(self, obj):
        return obj.image.url


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category_id = serializers.UUIDField(write_only=True)
    category = serializers.StringRelatedField(read_only=True)

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

    def validate_category_id(self, value):
        if not Category.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Invalid category ID.")
        return value

    def create(self, validated_data):
        validated_data['category'] = Category.objects.get(
            pk=validated_data.pop('category_id')
        )
        return super().create(validated_data)
