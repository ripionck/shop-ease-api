from django.urls import path
from .views import ProductListAPIView, ProductDetailAPIView, ProductImageAPIView

urlpatterns = [
    path('products/', ProductListAPIView.as_view(), name='product-list'),
    path('products/<uuid:pk>/', ProductDetailAPIView.as_view(),
         name='product-detail'),
    path('products/<uuid:product_id>/images/',
         ProductImageAPIView.as_view(), name='product-image-upload'),
]
