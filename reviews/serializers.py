from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'reviewer', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'reviewer', 'created_at']

    def get_reviewer(self, instance):
        return instance.user.username

    def validate(self, data):
        request = self.context.get('request')
        product = self.context.get('product')

        if Review.objects.filter(user=request.user, product=product).exists():
            raise serializers.ValidationError(
                "You have already reviewed this product.")

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("Request context not provided")

        user = request.user
        product = self.context.get('product')
        if not product:
            raise serializers.ValidationError(
                "Product not provided in context")

        review = Review.objects.create(
            product=product, user=user, **validated_data)
        # Update the product's rating
        product.update_rating(new_rating=review.rating)
        return review

    def update(self, instance, validated_data):
        old_rating = instance.rating  # Store the old rating
        instance = super().update(instance, validated_data)
        product = instance.product
        # Update the product's rating
        product.update_rating(new_rating=instance.rating,
                              old_rating=old_rating)
        return instance

    def delete(self, instance):
        product = instance.product
        old_rating = instance.rating
        instance.delete()
        # Update the product's rating
        product.update_rating(old_rating=old_rating)
        return instance
