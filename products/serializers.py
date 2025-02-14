from rest_framework import serializers
from .models import Product, ProductImage
from categories.models import Category


class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['image_url', 'is_main']
        read_only_fields = ['image_url']

    def get_image_url(self, obj):
        return obj.image.url


class ProductSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    category_id = serializers.UUIDField(write_only=True)
    category = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category', 'description', 'price', 'discounted_price',
            'category_id', 'brand', 'stock', 'rating', 'images',
            'features', 'specifications', 'tags', 'created_at',
            'updated_at']
        read_only_fields = ['id', 'rating', 'created_at',
                            'updated_at', 'images', 'category']

    def get_images(self, obj):
        return [image.image.url for image in obj.product_images.all()]

    def get_category(self, obj):
        return obj.category.name if obj.category else None

    def validate(self, data):
        if self.instance is None:
            category_id = data.get('category_id')
            try:
                category = Category.objects.get(pk=category_id)
                data['category'] = category
            except Category.DoesNotExist:
                raise serializers.ValidationError("Invalid category ID.")
        elif 'category_id' in data:
            category_id = data['category_id']
            try:
                category = Category.objects.get(pk=category_id)
                data['category'] = category
            except Category.DoesNotExist:
                raise serializers.ValidationError("Invalid category ID.")
        elif not data.get('category') and self.instance:
            data['category'] = self.instance.category
        return data

    def create(self, validated_data):
        category = validated_data.pop('category')

        product = Product.objects.create(**validated_data)
        product.category = category
        product.save()

        return product

    def update(self, instance, validated_data):
        category = validated_data.pop('category', instance.category)

        instance.category = category
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation
