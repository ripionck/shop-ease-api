from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from .models import Order
from .serializers import OrderSerializer
from django.conf import settings 
from django.template.loader import render_to_string 
from django.core.mail import send_mail

    
class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        shipping_address = request.data.get('shipping_address', {})
        if isinstance(shipping_address, dict):
            request.data['shipping_address'] = shipping_address

        cart_data = request.data.get('cart', {})
        if not cart_data:
            return Response({"error": "Cart data is required"}, status=status.HTTP_400_BAD_REQUEST)

        order_data = {
            'items': [],
            'shipping_address': shipping_address,
            'payment_method': request.data.get('payment_method'),
            'shipping': request.data.get('shipping'),  
            'tax': request.data.get('tax')        
        }

        for product in cart_data.get('products', []):
            order_data['items'].append({
                'product': product['product_id'],
                'quantity': product['quantity']
            })

        serializer = OrderSerializer(data=order_data, context={'request': request})

        if serializer.is_valid():
            order = serializer.save()

            subtotal = order.total_amount
            shipping = order.shipping
            tax = order.tax
            total = subtotal + shipping + tax

            order.total_amount = total  
            order.save()

            try:
                subject = "Your Order Confirmation"
                html_message = render_to_string('orders/templates/order_confirmation_email.html', {'order': order})
                plain_message = render_to_string('orders/templates/order_confirmation_email.txt', {'order': order})

                send_mail(
                    subject,
                    plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [order.user.email],
                    html_message=html_message
                )
                print("Email Sent")
            except Exception as e:
                print(f"Error sending confirmation email: {e}")

            response_data = serializer.data
            response_data['subtotal'] = str(subtotal) 
            response_data['shipping'] = str(shipping)  
            response_data['tax'] = str(tax)            
            response_data['total'] = str(total)        

            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id, *args, **kwargs):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateOrderStatusView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]  

    def patch(self, request, order_id, *args, **kwargs):
        try:
            order = Order.objects.get(id=order_id) 
        except Order.DoesNotExist:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')
        if new_status not in dict(Order.STATUS_CHOICES):
            return Response({"error": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)

        order.status = new_status
        order.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
