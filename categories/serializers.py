from rest_framework import serializers
from .models import Category


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
    


