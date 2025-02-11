from django.urls import path
from . import views

urlpatterns = [
    path('categories', views.CategoryView.as_view()),
    path('categories/<uuid:pk>', views.CategoryView.as_view()),
    
    path('products', views.ProductView.as_view()),
    path('products/<uuid:pk>', views.ProductDetailView.as_view()),
    path('products/<uuid:product_id>/images', views.ProductImageView.as_view()),
    path('products/<uuid:product_id>/reviews', views.ReviewView.as_view()),
]
