from django.urls import path
from .views import (
    ShoppingCartDetailView,
    EditCartItemView,
    AddToCartView
)

urlpatterns = [
    path('cart/items', ShoppingCartDetailView.as_view(), name='shopping-cart-detail'),
    path('cart/item', EditCartItemView.as_view(), name='edit-cart-item'), 
    path('cart/add', AddToCartView.as_view(), name='add-to-cart'),
]