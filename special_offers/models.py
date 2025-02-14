from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from categories.models import Category


class Offer(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    discount_percentage = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    image = models.URLField()
    products = models.JSONField(default=list)
    category = models.ForeignKey(
        Category(), on_delete=models.CASCADE, related_name='offers')

    def __str__(self):
        return self.title
