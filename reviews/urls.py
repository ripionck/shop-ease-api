from django.urls import path
from . import views

urlpatterns = [
    path('products/<uuid:product_id>/reviews/', views.ReviewListView.as_view(), name='review-list'), 
    path('reviews/<uuid:review_id>/', views.ReviewDetailView.as_view(), name='review-detail'), 
]