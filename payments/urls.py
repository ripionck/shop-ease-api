from django.urls import path
from .views import PaymentView, UpdatePaymentStatusView, stripe_webhook

urlpatterns = [
    path('payments', PaymentView.as_view(), name='payment-create'),
    path('payments/<uuid:pk>', PaymentView.as_view(), name='payment-detail'), 
    path('payments/<uuid:pk>/status/', UpdatePaymentStatusView.as_view(), name='payment-status-update'),
    path('stripe/webhook/', stripe_webhook, name='stripe-webhook')
]