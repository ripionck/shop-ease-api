from rest_framework import serializers
from .models import Category


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'description')
        read_only_fields = ('id',)


class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubCategorySerializer(many=True, required=False)
    parent_category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), allow_null=True, required=False)

    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'parent_category',
                  'subcategories', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def create(self, validated_data):
        subcategories_data = validated_data.pop('subcategories', [])
        parent_category = validated_data.pop(
            'parent_category', None)

        category = Category.objects.create(**validated_data)
        if parent_category:
            category.parent_category = parent_category
            category.save()

        for subcategory in subcategories_data:
            Category.objects.create(parent_category=category, **subcategory)
        return category

    def update(self, instance, validated_data):
        subcategories_data = validated_data.pop('subcategories', None)
        parent_category = validated_data.pop(
            'parent_category', None)
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get(
            'description', instance.description)

        if parent_category is not None:
            instance.parent_category = parent_category
        instance.save()

        return instance

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.parent_category is None:
            ret['parent_category'] = None
        elif instance.parent_category:
            ret['parent_category'] = instance.parent_category.id
        return ret
