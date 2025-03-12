from django.urls import path
from .views import PaymentView, UpdatePaymentStatusView, stripe_webhook

app_name = 'payments'
urlpatterns = [
    path('orders/<int:order_id>/payment/',
         PaymentView.as_view(), name='create_payment'),
    path('payments/<int:pk>/', PaymentView.as_view(), name='get_payment'),
    path('payments/<int:pk>/update-status/',
         UpdatePaymentStatusView.as_view(), name='update_payment'),
    path('webhook/stripe/', stripe_webhook, name='stripe_webhook'),
]
