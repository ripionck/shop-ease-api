from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db import transaction

from cart.models import CartItem
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
        serializer = OrderSerializer(
            data=request.data, context={'request': request})

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    # Get cart items
                    cart_items = CartItem.objects.filter(cart__user=user)
                    if not cart_items.exists():
                        return Response(
                            {"detail": "Cart is empty"},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    # Calculate total amount
                    total_amount = sum(item.product.price *
                                       item.quantity for item in cart_items)

                    # Create order
                    order = Order.objects.create(
                        user=user,
                        total_amount=total_amount,
                        shipping_address=request.data.get(
                            'shipping_address', {})
                    )

                    # Create order items from cart
                    order_items = [
                        OrderItem(
                            order=order,
                            product=item.product,
                            quantity=item.quantity,
                            price=item.product.price
                        ) for item in cart_items
                    ]
                    OrderItem.objects.bulk_create(order_items)

                    # Clear cart
                    cart_items.delete()

                    return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response(
                    {"detail": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
