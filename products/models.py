import uuid
from django.db import models
from cloudinary.models import CloudinaryField
from django.db.models.signals import pre_delete
from django.dispatch import receiver
import cloudinary.uploader
from django.db.models import Avg
from django.core.exceptions import ValidationError
from categories.models import Category
from reviews.models import Review  # Make sure this import is correct

COLOR_CHOICES = [
    ('red', 'Red'),
    ('blue', 'Blue'),
    ('green', 'Green'),
    ('black', 'Black'),
    ('white', 'White'),
    ('custom', 'Custom'),
]


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='products')
    subcategory = models.ForeignKey(Category, on_delete=models.CASCADE,
                                    related_name='products_in_subcategory', null=True, blank=True)
    brand = models.CharField(max_length=255, null=True, blank=True)
    images = models.JSONField(default=list)
    stock = models.PositiveIntegerField(default=0)
    rating = models.FloatField(null=True, blank=True)
    reviews = models.JSONField(default=list)
    features = models.JSONField(default=list)
    specifications = models.JSONField(default=dict)
    tags = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.subcategory and self.subcategory.parent_category != self.category:
            raise ValidationError(
                "Subcategory must belong to the selected category.")

    def update_rating(self):
        average_rating = Review.objects.filter(
            product=self).aggregate(Avg('rating'))['rating__avg']
        self.rating = average_rating if average_rating is not None else 0.0
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
        Product, on_delete=models.CASCADE, related_name='images')
    image = CloudinaryField('image')
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.name} - Image"

    class Meta:
        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"
        indexes = [
            models.Index(fields=['product']),
        ]


@receiver(pre_delete, sender=ProductImage)
def delete_product_image_from_cloudinary(sender, instance, **kwargs):
    if instance.image and hasattr(instance.image, 'public_id'):
        cloudinary.uploader.destroy(instance.image.public_id)


@receiver(pre_delete, sender=Product)
def delete_product_and_images_from_cloudinary(sender, instance, **kwargs):
    for image in instance.images.all():
        if image.image and hasattr(image.image, 'public_id'):
            cloudinary.uploader.destroy(image.image.public_id)
