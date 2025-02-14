from rest_framework import serializers
from categories.serializers import CategorySerializer
from .models import Offer, Category


class OfferSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )

    class Meta:
        model = Offer
        fields = [
            'id', 'title', 'description', 'discount_percentage',
            'start_date', 'end_date', 'image', 'products', 'category', 'category_id'
        ]
