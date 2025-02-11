from django.urls import path
from .views import (
    CreateOrderView,
    UpdateOrderStatusView,
    TrackOrderView,
    ListOrdersView,
    OrderDetailsView
)

urlpatterns = [
    path('orders/create/', CreateOrderView.as_view(), name='create-order'),
    path('orders/<uuid:order_id>/update-status/', UpdateOrderStatusView.as_view(), name='update-order-status'),
    path('orders/<uuid:order_id>/track/', TrackOrderView.as_view(), name='track-order'),
    path('orders/', ListOrdersView.as_view(), name='list-orders'),
    path('orders/<uuid:order_id>/details/', OrderDetailsView.as_view(), name='order-details'),
]