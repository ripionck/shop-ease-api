from django.urls import path
from cart.views import AddToCartView, CartDetailView, RemoveFromCartView, UpdateCartItemView

app_name = 'cart'
urlpatterns = [
    path('cart/', CartDetailView.as_view(), name='cart-detail'),
    path('cart/add/', AddToCartView.as_view(), name='add-to-cart'),
    path('cart/update/<uuid:product_id>/',
         UpdateCartItemView.as_view(), name='update-cart-item'),
    path('cart/remove/<uuid:product_id>/',
         RemoveFromCartView.as_view(), name='remove-from-cart'),
]
