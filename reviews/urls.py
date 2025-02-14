from django.urls import path
from .views import ReviewListView, ReviewDetailView

urlpatterns = [
    path('products/<uuid:product_id>/reviews/',
         ReviewListView.as_view(), name='review-list'),
    path('reviews/<uuid:review_id>/',
         ReviewDetailView.as_view(), name='review-detail'),
]
