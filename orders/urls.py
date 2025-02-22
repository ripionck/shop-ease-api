from django.urls import path
from .views import (
    ListOrdersView,
    CreateOrderView,
    UpdateOrderStatusView,
    TrackOrderView,
    OrderDetailsView,
    CancelOrderView,
)
app_name = 'orders'
urlpatterns = [
    path('orders/', ListOrdersView.as_view(), name='list-orders'),
    path('orders/create/', CreateOrderView.as_view(), name='create-order'),
    path('orders/<uuid:order_id>/status/',
         UpdateOrderStatusView.as_view(), name='update-order-status'),
    path('orders/<uuid:order_id>/track/',
         TrackOrderView.as_view(), name='track-order'),
    path('orders/<uuid:order_id>/',
         OrderDetailsView.as_view(), name='order-details'),
    path('orders/<uuid:order_id>/cancel/',
         CancelOrderView.as_view(), name='cancel-order'),
]
