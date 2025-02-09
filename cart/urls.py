from django.urls import path
from .views import (
    ShoppingCartDetailView,
    EditCartItemView,
    DeleteCartItemView,
    AddToCartView
)

urlpatterns = [
    path('cart', ShoppingCartDetailView.as_view(), name='shopping-cart-detail'),
    path('cart/edit/<int:cart_item_id>', EditCartItemView.as_view(), name='edit-cart-item'),
    path('cart/delete/<int:cart_item_id>', DeleteCartItemView.as_view(), name='delete-cart-item'),
    path('cart/add', AddToCartView.as_view(), name='add-to-cart'),
]