from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from cart.models import CartItem
from .models import Order, OrderItem
from .serializers import OrderSerializer


class ListOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == 'admin':
            orders = Order.objects.all()
        else:
            orders = Order.objects.filter(user=request.user)

        if not orders.exists():
            message = "No orders found." if request.user.role == 'admin' else "You haven't placed any orders yet."
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
                    cart_items = CartItem.objects.filter(cart__user=user)

                    if not cart_items.exists():
                        return Response(
                            {"detail": "Cart is empty"},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    total_amount = sum(item.product.price *
                                       item.quantity for item in cart_items)
                    order = Order.objects.create(
                        user=user,
                        total_amount=total_amount,
                        shipping_address=request.data.get(
                            'shipping_address', {})
                    )

                    order_items = [
                        OrderItem(
                            order=order,
                            product=item.product,
                            quantity=item.quantity,
                            price=item.product.price
                        ) for item in cart_items
                    ]
                    OrderItem.objects.bulk_create(order_items)
                    cart_items.delete()

                    return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(
                    {"detail": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateOrderStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, order_id):
        # Only admins can update order status
        if request.user.role != 'admin':
            return Response({
                "success": False,
                "message": "You don't have permission to perform this action"
            }, status=status.HTTP_403_FORBIDDEN)

        order = get_object_or_404(Order, id=order_id)
        new_status = request.data.get('status')

        if not new_status or new_status not in dict(Order.STATUS_CHOICES):
            return Response({
                "success": False,
                "message": "Invalid status"
            }, status=status.HTTP_400_BAD_REQUEST)

        order.status = new_status
        order.save()
        return Response({
            "success": True,
            "message": "Order status updated",
            "order": OrderSerializer(order).data
        }, status=status.HTTP_200_OK)


class TrackOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)

        # Check permissions
        if request.user.role != 'admin' and order.user != request.user:
            return Response({
                "success": False,
                "message": "You don't have permission to view this order"
            }, status=status.HTTP_403_FORBIDDEN)

        return Response({
            "success": True,
            "order": OrderSerializer(order).data
        }, status=status.HTTP_200_OK)


class OrderDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)

        # Check permissions
        if request.user.role != 'admin' and order.user != request.user:
            return Response({
                "success": False,
                "message": "You don't have permission to view this order"
            }, status=status.HTTP_403_FORBIDDEN)

        return Response({
            "success": True,
            "order": OrderSerializer(order).data
        }, status=status.HTTP_200_OK)


class CancelOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)

        # Check permissions
        if request.user.role != 'admin' and order.user != request.user:
            return Response({
                "success": False,
                "message": "You don't have permission to cancel this order"
            }, status=status.HTTP_403_FORBIDDEN)

        if order.status == 'cancelled':
            return Response({
                "success": False,
                "message": "Order is already cancelled"
            }, status=status.HTTP_400_BAD_REQUEST)

        if order.status in ['shipped', 'delivered']:
            return Response({
                "success": False,
                "message": "Cannot cancel shipped/delivered orders"
            }, status=status.HTTP_400_BAD_REQUEST)

        order.status = 'cancelled'
        order.save()
        return Response({
            "success": True,
            "message": "Order cancelled successfully",
            "order": OrderSerializer(order).data
        }, status=status.HTTP_200_OK)
