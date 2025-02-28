from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from cart.models import CartItem
from .models import Order, OrderItem
from .serializers import OrderSerializer
from rest_framework.pagination import PageNumberPagination


class ListOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == 'admin':
            orders = Order.objects.all()
        else:
            orders = Order.objects.filter(user=request.user)

        # Pagination
        paginator = PageNumberPagination()
        paginator.page_size = request.query_params.get('page_size', 10)

        result_page = paginator.paginate_queryset(orders, request)
        serializer = OrderSerializer(result_page, many=True)

        return paginator.get_paginated_response({
            "success": True,
            "message": "Orders retrieved successfully.",
            "data": serializer.data
        })


class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        serializer = OrderSerializer(
            data=request.data, context={'request': request})

        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Invalid data provided.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                cart_items = CartItem.objects.filter(cart__user=user)

                if not cart_items.exists():
                    return Response({
                        "success": False,
                        "message": "Your cart is empty. Add items to proceed."
                    }, status=status.HTTP_400_BAD_REQUEST)

                total_amount = sum(item.product.price *
                                   item.quantity for item in cart_items)
                order = Order.objects.create(
                    user=user,
                    total_amount=total_amount,
                    shipping_address=request.data.get('shipping_address', {})
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

                return Response({
                    "success": True,
                    "message": "Order created successfully.",
                    "data": OrderSerializer(order).data
                }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "success": False,
                "message": "An error occurred while creating the order.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateOrderStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, order_id):
        if request.user.role != 'admin':
            return Response({
                "success": False,
                "message": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)

        order = get_object_or_404(Order, id=order_id)
        new_status = request.data.get('status')

        if not new_status or new_status not in dict(Order.STATUS_CHOICES):
            return Response({
                "success": False,
                "message": "Invalid status provided."
            }, status=status.HTTP_400_BAD_REQUEST)

        order.status = new_status
        order.save()
        return Response({
            "success": True,
            "message": "Order status updated successfully.",
            "data": OrderSerializer(order).data
        }, status=status.HTTP_200_OK)


class TrackOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)

        if request.user.role != 'admin' and order.user != request.user:
            return Response({
                "success": False,
                "message": "You do not have permission to view this order."
            }, status=status.HTTP_403_FORBIDDEN)

        return Response({
            "success": True,
            "message": "Order details retrieved successfully.",
            "data": OrderSerializer(order).data
        }, status=status.HTTP_200_OK)


class OrderDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)

        if request.user.role != 'admin' and order.user != request.user:
            return Response({
                "success": False,
                "message": "You do not have permission to view this order."
            }, status=status.HTTP_403_FORBIDDEN)

        return Response({
            "success": True,
            "message": "Order details retrieved successfully.",
            "data": OrderSerializer(order).data
        }, status=status.HTTP_200_OK)


class CancelOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)

        if request.user.role != 'admin' and order.user != request.user:
            return Response({
                "success": False,
                "message": "You do not have permission to cancel this order."
            }, status=status.HTTP_403_FORBIDDEN)

        if order.status == 'cancelled':
            return Response({
                "success": False,
                "message": "This order is already cancelled."
            }, status=status.HTTP_400_BAD_REQUEST)

        if order.status in ['shipped', 'delivered']:
            return Response({
                "success": False,
                "message": "Cannot cancel an order that has already been shipped or delivered."
            }, status=status.HTTP_400_BAD_REQUEST)

        order.status = 'cancelled'
        order.save()
        return Response({
            "success": True,
            "message": "Order cancelled successfully.",
            "data": OrderSerializer(order).data
        }, status=status.HTTP_200_OK)
