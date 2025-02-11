from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db import transaction
from .models import Order, OrderItem
from products.models import Product
from .serializers import OrderSerializer


class ListOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data

        # Validate required fields
        shipping_address = data.get('shipping_address')
        payment_method = data.get('payment_method')
        items_data = data.get('items', [])
        if not shipping_address or not payment_method or not items_data:
            return Response(
                {"error": "shipping_address, payment_method, and items are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                total_amount = 0
                order_items = []

                for item_data in items_data:
                    product_id = item_data.get('product_id')
                    quantity = item_data.get('quantity')

                    if not product_id or not quantity:
                        return Response(
                            {"error": "Each item must have 'product_id' and 'quantity'."},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    try:
                        product = Product.objects.get(id=product_id)
                    except Product.DoesNotExist:
                        return Response(
                            {"error": f"Product with id {product_id} not found."},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    price = product.price
                    total_amount += price * quantity
                    order_items.append((product, quantity, price))

                # Create the order
                order = Order.objects.create(
                    user=user,
                    total_amount=total_amount,
                    shipping=data.get('shipping', 0),
                    tax=data.get('tax', 0),
                    shipping_address=shipping_address,
                    payment_method=payment_method
                )

                # Add order items
                for product, quantity, price in order_items:
                    OrderItem.objects.create(order=order, product=product, quantity=quantity, price=price)

                # Serialize the created order
                serializer = OrderSerializer(order)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class UpdateOrderStatusView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')
        if not new_status or new_status not in dict(Order.STATUS_CHOICES):
            return Response({"error": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)

        order.status = new_status
        order.save()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class TrackOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found or you do not have permission to view it."}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class OrderDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        if not (request.user == order.user or request.user.is_staff):
            return Response({"error": "You do not have permission to view this order."}, status=status.HTTP_403_FORBIDDEN)

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)