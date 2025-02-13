import uuid
from django.db import models
from django.conf import settings
from cloudinary.models import CloudinaryField
from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
import cloudinary.uploader
from django.db.models import Avg
from django.core.exceptions import ValidationError

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    parent_category = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        indexes = [
            models.Index(fields=['parent_category']),
        ]
        ordering = ['name']


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    subcategory = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategory_products')
    main_image = CloudinaryField('image', blank=True, null=True)
    brand = models.CharField(max_length=255, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    rating = models.FloatField(null=True, blank=True)
    features = models.JSONField(default=list)
    specifications = models.JSONField(default=list)
    tags = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.subcategory and self.subcategory.parent_category != self.category:
            raise ValidationError("Subcategory must belong to the selected category.")

    def update_rating(self):
        average_rating = self.reviews.aggregate(Avg('rating'))['rating__avg']
        self.rating = average_rating if average_rating is not None else None
        self.save(update_fields=['rating'])

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
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
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


class Review(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['user']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.user.username} on {self.product.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.product.update_rating()


@receiver(pre_delete, sender=ProductImage)
def delete_product_image_from_cloudinary(sender, instance, **kwargs):
    if instance.image and hasattr(instance.image, 'public_id'):
        cloudinary.uploader.destroy(instance.image.public_id)

@receiver(pre_delete, sender=Product)
def delete_product_and_images_from_cloudinary(sender, instance, **kwargs):
    for image in instance.images.all():
        if image.image and hasattr(image.image, 'public_id'):
            cloudinary.uploader.destroy(image.image.public_id)