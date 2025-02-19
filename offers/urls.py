from django.urls import path
from .views import OfferListCreateView, OfferDetailView


app_name = 'offers'
urlpatterns = [
    path('offers/', OfferListCreateView.as_view(), name='offer-list-create'),
    path('offers/<uuid:pk>/', OfferDetailView.as_view(), name='offer-detail'),
]
