import uuid
from django.db import models
from cloudinary.models import CloudinaryField
from categories.models import Category


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )
    brand = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    rating = models.FloatField(default=0.0)
    total_rating_sum = models.FloatField(default=0.0)
    total_reviews = models.PositiveIntegerField(default=0)
    features = models.JSONField(default=list)
    specifications = models.JSONField(default=dict)
    tags = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def update_rating(self, new_rating=None, old_rating=None):
        if new_rating is not None:
            self.total_rating_sum += new_rating
            self.total_reviews += 1
        if old_rating is not None:
            self.total_rating_sum -= old_rating
            self.total_reviews -= 1

        self.rating = self.total_rating_sum / \
            self.total_reviews if self.total_reviews > 0 else 0.0
        self.save()

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['brand']),
        ]
        ordering = ['-created_at']


class ProductImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product_images'
    )
    image = CloudinaryField('image')
    is_main = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'is_main'],
                condition=models.Q(is_main=True),
                name='unique_main_image_per_product'
            )
        ]
