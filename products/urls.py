from django.urls import path
from .views import (
    CategoryListView, CategoryDetailView,
    ProductListView, ProductDetailView,
    ProductImageView, ReviewListView, ReviewDetailView
)

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<uuid:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<uuid:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('products/<uuid:product_id>/images/', ProductImageView.as_view(), name='product-image-list'),
    path('products/<uuid:product_id>/reviews/', ReviewListView.as_view(), name='review-list'),
    path('reviews/<uuid:review_id>/', ReviewDetailView.as_view(), name='delete-review'),
]