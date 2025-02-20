from rest_framework import serializers
from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    totalProducts = serializers.IntegerField(
        source='total_products', read_only=True)
    activeProducts = serializers.IntegerField(
        source='active_products', read_only=True)
    outOfStock = serializers.IntegerField(
        source='out_of_stock', read_only=True)

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'description',
            'totalProducts', 'activeProducts', 'outOfStock',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
