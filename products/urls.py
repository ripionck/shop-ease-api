from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/<uuid:pk>/', views.ProductDetailView.as_view(), name='product-detail'),

    path('products/<uuid:product_id>/images/', views.ProductImageUploadView.as_view(),
        name='product-image-upload'),
]