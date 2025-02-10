from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Payment
from .serializers import PaymentSerializer
import stripe
from django.conf import settings 
import stripe
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt  

stripe.api_key = settings.STRIPE_SECRET_KEY 

class PaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            payment = serializer.save()

            try:
                # Create Stripe Payment Intent
                intent = stripe.PaymentIntent.create(
                    amount=int(payment.amount * 100), 
                    currency="usd", 
                    payment_method_types=["card"],  # Add other methods if needed
                    metadata={"payment_id": str(payment.id), "order_id": str(payment.order.id)}, # Link Stripe intent to your payment and order
                )

                payment.transaction_id = intent.id # Store the Stripe Payment Intent ID
                payment.save() # Update the payment object with transaction ID

                return Response({"clientSecret": intent["client_secret"], "payment_id": payment.id}, status=status.HTTP_200_OK) 

            except stripe.error.StripeError as e:
                payment.status = 'failed'  
                payment.save()
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST) 

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk): 
        try:
            payment = Payment.objects.get(pk=pk)
            serializer = PaymentSerializer(payment)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

class UpdatePaymentStatusView(APIView):
    def patch(self, request, pk):  
        try:
            payment = Payment.objects.get(pk=pk)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = PaymentSerializer(payment, data=request.data, partial=True) 
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        payment_id = payment_intent['metadata']['payment_id']

        try:
            payment = Payment.objects.get(pk=payment_id)
            payment.status = 'completed'
            payment.save()
            print(f"Payment {payment_id} status updated to completed.")
        except Payment.DoesNotExist:
            print(f"Payment {payment_id} not found.")

    elif event['type'] == 'payment_intent.payment_failed':  
        payment_intent = event['data']['object']
        payment_id = payment_intent['metadata']['payment_id']

        try:
            payment = Payment.objects.get(pk=payment_id)
            payment.status = 'failed' 
            payment.save()
            print(f"Payment {payment_id} status updated to failed.")
        except Payment.DoesNotExist:
            print(f"Payment {payment_id} not found.")

    elif event['type'] == 'payment_intent.canceled':
        payment_intent = event['data']['object']
        payment_id = payment_intent['metadata']['payment_id']

        try:
            payment = Payment.objects.get(pk=payment_id)
            payment.status = 'canceled'  
            payment.save()
            print(f"Payment {payment_id} status updated to canceled.")
        except Payment.DoesNotExist:
            print(f"Payment {payment_id} not found.")


    return HttpResponse(status=200)