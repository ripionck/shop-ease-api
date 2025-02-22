from django.shortcuts import get_object_or_404
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
        if request.user.is_staff:
            orders = Order.objects.all()
        else:
            orders = Order.objects.filter(user=request.user)
        if not orders:
            message = "No orders found." if request.user.is_staff else "You haven't placed any orders yet."
            return Response({
                "success": True,
                "message": message,
                "orders": []
            }, status=status.HTTP_200_OK)

        serializer = OrderSerializer(orders, many=True)
        return Response({
            "success": True,
            "orders": serializer.data
        }, status=status.HTTP_200_OK)


class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data

        shipping_address = data.get('shipping_address')
        products_data = data.get('products', [])

        if not shipping_address or not products_data:
            return Response(
                {"success": False, "message": "shipping_address and products are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                total_amount = 0
                order_items = []

                for product_data in products_data:
                    product_id = product_data.get('product_id')
                    quantity = product_data.get('quantity')

                    if not product_id or not quantity:
                        return Response(
                            {"success": False,
                                "message": "Each product must have 'product_id' and 'quantity'."},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    product = get_object_or_404(Product, id=product_id)
                    price = product.price
                    total_amount += price * quantity
                    order_items.append((product, quantity, price))

                order = Order.objects.create(
                    user=user,
                    total_amount=total_amount,
                    shipping_address=shipping_address,
                )

                for product, quantity, price in order_items:
                    OrderItem.objects.create(
                        order=order, product=product, quantity=quantity, price=price)

                serializer = OrderSerializer(order)
                return Response({
                    "success": True,
                    "message": "Order created successfully.",
                    "order": serializer.data
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"success": False, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UpdateOrderStatusView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)

        new_status = request.data.get('status')
        if not new_status or new_status not in dict(Order.STATUS_CHOICES):
            return Response({"success": False, "message": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)

        order.status = new_status
        order.save()

        serializer = OrderSerializer(order)
        return Response({
            "success": True,
            "message": "Order status updated successfully.",
            "order": serializer.data
        }, status=status.HTTP_200_OK)


class TrackOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)

        serializer = OrderSerializer(order)
        return Response({
            "success": True,
            "order": serializer.data
        }, status=status.HTTP_200_OK)


class OrderDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)

        if not (request.user == order.user or request.user.is_staff):
            return Response({
                "success": False,
                "message": "You do not have permission to view this order."
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = OrderSerializer(order)
        return Response({
            "success": True,
            "order": serializer.data
        }, status=status.HTTP_200_OK)


class CancelOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)

        if order.status == 'cancelled':
            return Response({
                "success": False,
                "message": "This order is already cancelled."
            }, status=status.HTTP_400_BAD_REQUEST)

        if order.status in ('shipped', 'delivered'):
            return Response({
                "success": False,
                "message": "This order cannot be cancelled as it has already been shipped or delivered."
            }, status=status.HTTP_400_BAD_REQUEST)

        order.status = 'cancelled'
        order.save()

        serializer = OrderSerializer(order)
        return Response({
            "success": True,
            "message": "Order cancelled successfully.",
            "order": serializer.data
        }, status=status.HTTP_200_OK)
