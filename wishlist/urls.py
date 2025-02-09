from django.urls import path
from .views import (
    WishlistDetailView,
    AddToWishlistView,
    RemoveFromWishlistView
)

urlpatterns = [
    path('wishlist', WishlistDetailView.as_view(), name='wishlist-detail'),
    path('wishlist/add', AddToWishlistView.as_view(), name='add-to-wishlist'),
    path('wishlist/remove/<uuid:product_id>', RemoveFromWishlistView.as_view(), name='remove-from-wishlist'),
]