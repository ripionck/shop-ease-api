from rest_framework import serializers
from .models import Category


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'description')
        read_only_fields = ('id',)


class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubCategorySerializer(many=True, required=False)
    parent_category = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'parent_category',
                  'subcategories', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at',
                            'updated_at', 'parent_category')

    def get_parent_category_name(self, obj):
        if obj.parent_category:
            return obj.parent_category.name
        return None

    def validate_parent_category(self, value):
        if value == "":
            return None
        return value

    def create(self, validated_data):
        subcategories_data = validated_data.pop('subcategories', [])
        parent_category = validated_data.pop('parent_category', None)

        category = Category.objects.create(**validated_data)
        if parent_category:
            category.parent_category = parent_category
            category.save()

        for subcategory in subcategories_data:
            Category.objects.create(parent_category=category, **subcategory)
        return category

    def update(self, instance, validated_data):
        subcategories_data = validated_data.pop('subcategories', None)
        parent_category = validated_data.pop('parent_category', None)

        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get(
            'description', instance.description)

        if parent_category is not None:
            instance.parent_category = parent_category
        instance.save()

        return instance
