from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.CategoryView.as_view(), name='category-list'),
    path('categories/<uuid:pk>/', views.CategoryView.as_view(), name='category-detail'),
    
    path('products/', views.ProductView.as_view(), name='product-list'),
    path('products/<uuid:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('products/<uuid:product_id>/images/', views.ProductImageView.as_view(), name='product-image-list'),
    path('products/<uuid:product_id>/reviews/', views.ReviewView.as_view(), name='product-review-list'),
    path('reviews/<uuid:review_id>/', views.ReviewDetailView.as_view(), name='review-detail'),
]