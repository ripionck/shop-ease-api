from rest_framework import serializers
from django.shortcuts import get_object_or_404
from .models import *
from cloudinary import uploader

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
        # Create parent category
        category = Category.objects.create(**validated_data)
        # Create subcategories if provided
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
            # Remove existing subcategories and recreate with new data.
            instance.subcategories.all().delete()
            for subcategory in subcategories_data:
                Category.objects.create(parent_category=instance, **subcategory)
                
        return instance
    
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_main']
        read_only_fields = ['id']

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'rating', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']

    def create(self, validated_data):
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("Request context not provided")
        user = request.user
        product = validated_data.pop('product')
        review = Review.objects.create(
            product=product,
            user=user,
            **validated_data
        )
        product.update_rating()
        return review

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep.pop('product', None)
        rep.pop('user', None)
        return rep
    
class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, required=False)
    main_image = serializers.ImageField(write_only=True, required=False)
    category_id = serializers.UUIDField(write_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'discounted_price',
            'category_id', 'category', 'main_image', 'images', 'brand',
            'stock', 'rating', 'features', 'specifications', 'tags',
            'created_at', 'updated_at', 'reviews'
        ]
        read_only_fields = ['rating', 'created_at', 'updated_at']

    def create(self, validated_data):
        reviews_data = validated_data.pop('reviews', [])
        main_image = validated_data.pop('main_image', None)
        category_uuid = validated_data.pop('category_id')
        category = get_object_or_404(Category, id=category_uuid)
        validated_data['category'] = category

        product = super().create(validated_data)

        if main_image:
            ProductImage.objects.create(
                product=product,
                image=main_image,
                is_main=True
            )
        
        # Create nested reviews.
        # Note: The ReviewSerializer expects the user from request context.
        request = self.context.get('request')
        for review_data in reviews_data:
            # Ensure the product field is not sent from the client.
            review_serializer = ReviewSerializer(data=review_data, context={'request': request})
            review_serializer.is_valid(raise_exception=True)
            # Save each review, attaching the created product.
            review_serializer.save(product=product)
            product.update_rating()
        
        return product

