from django.urls import path
from .views import CancelOrderView, CreateOrderView, ListOrdersView, OrderDetailsView, TrackOrderView, UpdateOrderStatusView

app_name = 'orders'
urlpatterns = [
    path('orders/', ListOrdersView.as_view(), name='order-list'),
    path('orders/create/', CreateOrderView.as_view(), name='order-create'),
    path('orders/update-status/<uuid:order_id>/',
         UpdateOrderStatusView.as_view(), name='order-update-status'),
    path('orders/track/<uuid:order_id>/',
         TrackOrderView.as_view(), name='order-track'),
    path('orders/<uuid:order_id>/',
         OrderDetailsView.as_view(), name='order-details'),
    path('orders/cancel/<uuid:order_id>/',
         CancelOrderView.as_view(), name='order-cancel'),
]
