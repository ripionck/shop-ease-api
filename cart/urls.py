from django.urls import path
from .views import (
    CartDetailView,
    EditCartItemView,
    AddToCartView
)

urlpatterns = [
    path('cart/items/', CartDetailView.as_view(), name='cart-detail'),
    path('cart/item/', EditCartItemView.as_view(), name='edit-cart-item'), 
    path('cart/add/', AddToCartView.as_view(), name='add-to-cart'),
]