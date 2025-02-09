from django.urls import path
from .views import (
    OrderListView,
    OrderDetailView,
    CreateOrderView,
    UpdateOrderStatusView
)

urlpatterns = [
    path('orders', OrderListView.as_view(), name='order-list'),
    path('orders/<uuid:order_id>', OrderDetailView.as_view(), name='order-detail'),
    path('orders/create', CreateOrderView.as_view(), name='create-order'),
    path('orders/<uuid:order_id>/update-status', UpdateOrderStatusView.as_view(), name='update-order-status'),
]