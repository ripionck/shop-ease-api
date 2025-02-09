from rest_framework import serializers
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

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    main_image = serializers.ImageField(write_only=True, required=False)
    category = serializers.PrimaryKeyRelatedField(queryset = Category.objects.all())
    subcategory = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=False)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'discounted_price', 'category', 'subcategory', 'main_image', 'images', 'brand', 'stock', 'rating', 'features', 'specifications', 'tags', 'created_at', 'updated_at']
        read_only_fields = ['rating', 'created_at', 'updated_at']

    def create(self, validate_data):
        main_image = validate_data.pop('main_image', None)
        product = super().create(validate_data)

        if main_image:
            ProductImage.objects.create(
                product=product,
                image=main_image,
                is_main=True
            )

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']

    def create(self, validate_data):
        request = self.context.get('request')
        user = request.user
        product_id = validate_data.get('product')
        product = Product.objects.get(id=product_id)
        review = Review.objects.create(
            product=product,
            user=user,
            **validate_data
        )
        product.update_rating()
        return review