from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from orders.models import Order
from .models import Payment
from .serializers import PaymentSerializer
import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import logging

stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)


class PaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        """Initiate payment for an order"""
        try:
            order = Order.objects.get(id=order_id, user=request.user)

            # Create Stripe Payment Intent
            intent = stripe.PaymentIntent.create(
                amount=int(order.total_amount * 100),
                currency="usd",
                payment_method_types=["card"],
                metadata={
                    "order_id": str(order.id),
                    "user_id": str(request.user.id)
                }
            )

            # Create payment record
            payment = Payment.objects.create(
                order=order,
                amount=order.total_amount,
                payment_method='card',
                transaction_id=intent.id,
                status='requires_payment_method'
            )

            return Response({
                "message": "Payment initiated successfully",
                "data": {
                    "client_secret": intent.client_secret,
                    "payment_id": payment.id
                }
            }, status=status.HTTP_201_CREATED)

        except Order.DoesNotExist:
            return Response({
                "message": "Order not found",
                "error": "order_not_found"
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"Payment initiation failed: {str(e)}")
            return Response({
                "message": "Payment initiation failed",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk):
        """Retrieve payment details"""
        try:
            payment = Payment.objects.get(pk=pk, order__user=request.user)
            serializer = PaymentSerializer(payment)
            return Response({
                "message": "Payment retrieved successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Payment.DoesNotExist:
            return Response({
                "message": "Payment not found",
                "error": "payment_not_found"
            }, status=status.HTTP_404_NOT_FOUND)


class UpdatePaymentStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        """Update payment status"""
        try:
            payment = Payment.objects.get(pk=pk)

            # Ensure user can only update their own payments
            if payment.order.user != request.user:
                return Response({
                    "message": "Unauthorized access",
                    "error": "unauthorized"
                }, status=status.HTTP_403_FORBIDDEN)

            serializer = PaymentSerializer(
                payment, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "Payment status updated successfully",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)

            return Response({
                "message": "Invalid data",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Payment.DoesNotExist:
            return Response({
                "message": "Payment not found",
                "error": "payment_not_found"
            }, status=status.HTTP_404_NOT_FOUND)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        logger.warning("Invalid Stripe webhook payload")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        logger.warning("Invalid Stripe webhook signature")
        return HttpResponse(status=400)

    payment_intent = event['data'].get('object', {})
    payment_id = payment_intent.get('metadata', {}).get('payment_id')

    if payment_id:
        try:
            payment = Payment.objects.get(pk=payment_id)
        except Payment.DoesNotExist:
            logger.error(f"Webhook: Payment {payment_id} not found")
            return HttpResponse(status=200)
    else:
        logger.error("Webhook: Payment ID not found in metadata")
        return HttpResponse(status=200)

    if event['type'] == 'payment_intent.succeeded':
        payment.status = 'completed'
        payment.save()
        logger.info(f"Payment {payment_id} marked as completed via webhook")

    elif event['type'] == 'payment_intent.payment_failed':
        payment.status = 'failed'
        payment.save()
        logger.warning(f"Payment {payment_id} failed via webhook")

    elif event['type'] == 'payment_intent.canceled':
        payment.status = 'canceled'
        payment.save()
        logger.info(f"Payment {payment_id} canceled via webhook")

    return HttpResponse(status=200)
