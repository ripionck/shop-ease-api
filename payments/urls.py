from django.urls import path
from .views import PaymentAPI, PaymentStatusAPI, StripeWebhook

app_name = 'payments'
urlpatterns = [
    path('create-payment/', PaymentAPI.as_view(), name='create-payment'),
    path('payment-status/<int:payment_id>/',
         PaymentStatusAPI.as_view(), name='payment-status'),
    path('webhook/', StripeWebhook.as_view(), name='stripe-webhook'),
]
