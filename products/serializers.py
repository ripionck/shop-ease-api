from rest_framework import serializers
from django.shortcuts import get_object_or_404
from .models import *

class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'description')
        read_only_fields = ('id',)

class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubCategorySerializer(many=True, required=False)

    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'parent_category', 'subcategories', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def create(self, validated_data):
        subcategories_data = validated_data.pop('subcategories', [])
        category = Category.objects.create(**validated_data)
        for subcategory in subcategories_data:
            Category.objects.create(parent_category=category, **subcategory)
        return category

    def update(self, instance, validated_data):
        subcategories_data = validated_data.pop('subcategories', None)

        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.parent_category = validated_data.get('parent_category', instance.parent_category)
        instance.save()

        if subcategories_data is not None:
            instance.subcategories.all().delete()
            for subcategory in subcategories_data:
                Category.objects.create(parent_category=instance, **subcategory)

        return instance


class ReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'reviewer', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'reviewer', 'created_at']

    def get_reviewer(self, instance):
        return instance.user.username

    def create(self, validated_data):
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("Request context not provided")
        user = request.user
        product = self.context.get('product')
        if not product:
            raise serializers.ValidationError("Product not provided in context")
        review = Review.objects.create(product=product, user=user, **validated_data)
        product.update_rating()
        return review
    
class ProductImageUploadSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'image_url', 'is_main']

    def get_image_url(self, obj):
        return obj.image if obj.image else None  


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageUploadSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, required=False)
    category_id = serializers.UUIDField(write_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'discounted_price',
            'category_id', 'category', 'images', 'color', 'brand',
            'stock', 'rating', 'features', 'specifications', 'tags',
            'created_at', 'updated_at', 'reviews'
        ]
        read_only_fields = ['rating', 'created_at', 'updated_at']

    def create(self, validated_data):
        reviews_data = validated_data.pop('reviews', [])
        category_uuid = validated_data.pop('category_id')
        category = get_object_or_404(Category, id=category_uuid)
        validated_data['category'] = category
        product = super().create(validated_data)

        request = self.context.get('request')
        for review_data in reviews_data:
            review_serializer = ReviewSerializer(data=review_data, context={'request': request, 'product': product})
            review_serializer.is_valid(raise_exception=True)
            review_serializer.save()
            product.update_rating()

        return product