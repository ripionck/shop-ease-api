from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from orders.models import Order
from .models import Payment


class PaymentAPITestCase(TestCase):
    def setUp(self):
        # Create test order
        self.order = Order.objects.create(
            # Add required fields for your Order model
            total_amount=100.00
        )

        self.client = APIClient()

    def test_make_payment(self):
        url = reverse('make_payment')
        data = {
            'order_id': self.order.id,
            'card_number': '4242424242424242',
            'expiry_month': '12',
            'expiry_year': '2025',
            'cvc': '123'
        }

        response = self.client.post(url, data, format='json')

        # Check basic response structure
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('payment_id', response.data)

        # Check if payment was created in database
        payment_id = response.data['payment_id']
        payment_exists = Payment.objects.filter(id=payment_id).exists()
        self.assertTrue(payment_exists)

    def test_invalid_card(self):
        url = reverse('make_payment')
        data = {
            'order_id': self.order.id,
            'card_number': '4242424242424241',  # Invalid card number
            'expiry_month': '12',
            'expiry_year': '2025',
            'cvc': '123'
        }

        response = self.client.post(url, data, format='json')

        # Should return error
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_payment_status(self):
        # First create a payment
        payment = Payment.objects.create(
            order=self.order,
            amount=100.00,
            payment_method='card',
            status='pending'
        )

        url = reverse('payment_status', kwargs={'payment_id': payment.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['payment_id'], payment.id)
        self.assertEqual(response.data['status'], 'pending')
