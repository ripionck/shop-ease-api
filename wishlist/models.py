from django.db import models
from products.models import Product
from users.models import User

class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist')
    products = models.ManyToManyField(Product, related_name='wishlisted_by')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wishlist of {self.user.username}"

    class Meta:
        verbose_name = "Wishlist"
        verbose_name_plural = "Wishlists"
