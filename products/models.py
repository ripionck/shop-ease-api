import uuid
from django.db import models
from cloudinary.models import CloudinaryField
from django.core.exceptions import ValidationError
from categories.models import Category


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True,
                            help_text="The name of the product.")
    description = models.TextField(
        help_text="Detailed description of the product.")
    price = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Price of the product.")
    discounted_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, help_text="Discounted price of the product (if applicable).")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='products_in_category', help_text="Category of the product.")
    subcategory = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='products_in_subcategory', help_text="Subcategory of the product (must belong to the selected category).")
    brand = models.CharField(max_length=255, null=True,
                             blank=True, help_text="Brand of the product.")
    stock = models.PositiveIntegerField(
        default=0, help_text="Available stock of the product.")
    rating = models.FloatField(
        default=0.0, help_text="Average rating of the product.")
    total_rating_sum = models.FloatField(
        default=0.0, help_text="Sum of all ratings for the product.")
    total_reviews = models.PositiveIntegerField(
        default=0, help_text="Total number of reviews for the product.")
    features = models.JSONField(
        default=list, help_text="List of features of the product.")
    specifications = models.JSONField(
        default=dict, help_text="Specifications of the product.")
    tags = models.JSONField(
        default=list, help_text="Tags associated with the product.")
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Timestamp when the product was created.")
    updated_at = models.DateTimeField(
        auto_now=True, help_text="Timestamp when the product was last updated.")

    def clean(self):
        if self.subcategory and self.subcategory.parent_category != self.category:
            raise ValidationError(
                "Subcategory must belong to the selected category.")

    def update_rating(self, new_rating=None, old_rating=None):
        """
        Incrementally update the product's rating when a review is added, updated, or deleted.
        """
        if new_rating is not None:
            self.total_rating_sum += new_rating
            self.total_reviews += 1
        if old_rating is not None:
            self.total_rating_sum -= old_rating
            self.total_reviews -= 1

        if self.total_reviews > 0:
            self.rating = self.total_rating_sum / self.total_reviews
        else:
            self.rating = 0.0

        self.save()

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['subcategory']),
            models.Index(fields=['brand']),
        ]
        ordering = ['-created_at']


class ProductImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='product_images',
        help_text="The product this image belongs to.")
    image = CloudinaryField('image', help_text="Image of the product.")
    is_main = models.BooleanField(
        default=False, help_text="Whether this is the main image of the product.")

    def __str__(self):
        return f"{self.product.name} - Image"

    class Meta:
        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"
        indexes = [
            models.Index(fields=['product']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'is_main'],
                condition=models.Q(is_main=True),
                name='unique_main_image_per_product'
            )
        ]
