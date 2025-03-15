from django.conf import settings
import stripe
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .serializers import PaymentMethodSerializer, PaymentSerializer
from .models import Payment
from orders.models import Order

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentAPI(APIView):
    serializer_class = PaymentMethodSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = get_object_or_404(
                Order, id=serializer.validated_data['order_id'])
            payment_method_id = serializer.validated_data['payment_method_id']

            # Create or retrieve existing Payment record
            payment, created = Payment.objects.get_or_create(
                order=order,
                defaults={
                    'amount': order.total_amount,
                    'payment_method': 'card',
                    'status': 'requires_confirmation'
                }
            )

            # Create or update Payment Intent
            if not payment.stripe_payment_intent_id:
                payment_intent = stripe.PaymentIntent.create(
                    amount=int(order.total_amount * 100),
                    currency='usd',
                    payment_method=payment_method_id,
                    confirmation_method='manual',
                    confirm=True,
                    metadata={
                        'order_id': str(order.id),
                        'payment_id': payment.id
                    }
                )
                payment.stripe_payment_intent_id = payment_intent.id
                payment.save()
            else:
                payment_intent = stripe.PaymentIntent.modify(
                    payment.stripe_payment_intent_id,
                    payment_method=payment_method_id
                )

            # Handle payment confirmation
            if payment_intent.status == 'requires_action':
                return Response({
                    'client_secret': payment_intent.client_secret,
                    'requires_action': True,
                    'payment_id': payment.id
                }, status=status.HTTP_200_OK)

            if payment_intent.status == 'succeeded':
                payment.status = 'completed'
                payment.transaction_id = payment_intent.id
                payment.save()
                return Response(PaymentSerializer(payment).data, status=status.HTTP_200_OK)

            return Response({
                'error': f'Unexpected payment status: {payment_intent.status}',
                'payment_id': payment.id
            }, status=status.HTTP_400_BAD_REQUEST)

        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentStatusAPI(APIView):
    def get(self, request, payment_id):
        try:
            payment = get_object_or_404(Payment, id=payment_id)
            payment_intent = stripe.PaymentIntent.retrieve(
                payment.stripe_payment_intent_id
            ) if payment.stripe_payment_intent_id else None

            # Update status if changed
            if payment_intent and payment_intent.status != payment.status:
                payment.status = payment_intent.status
                payment.save()

            return Response({
                'payment_id': payment.id,
                'status': payment.status,
                'client_secret': payment_intent.client_secret if payment_intent else None,
                'amount': float(payment.amount),
                'order_id': payment.order.id
            })

        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class StripeWebhook(APIView):
    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            return Response({'error': 'Invalid payload'}, status=400)
        except stripe.error.SignatureVerificationError as e:
            return Response({'error': 'Invalid signature'}, status=400)

        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            try:
                payment = Payment.objects.get(
                    stripe_payment_intent_id=payment_intent['id']
                )
                payment.status = 'completed'
                payment.transaction_id = payment_intent['id']
                payment.save()
            except Payment.DoesNotExist:
                pass

        return Response({'status': 'success'}, status=200)
