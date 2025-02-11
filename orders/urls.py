from django.urls import path
from .views import OrderListView, OrderDetailView, CreateOrderView, TrackOrderView, UpdateOrderStatusView

urlpatterns = [
    path('orders', OrderListView.as_view(), name='order-list'),  
    path('orders/<uuid:order_id>', OrderDetailView.as_view(), name='order-detail'), 
    path('orders/create', CreateOrderView.as_view(), name='order-create'),
    path('orders/<uuid:order_id>/', TrackOrderView.as_view(), name='track-order'), 
    path('orders/<uuid:order_id>/status', UpdateOrderStatusView.as_view(), name='order-status-update'), 
]
