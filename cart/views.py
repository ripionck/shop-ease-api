from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.core.cache import cache
from products.models import Product
from .models import Cart, CartItem
from .serializers import AddToCartSerializer, CartItemUpdateSerializer, CartSerializer


def get_cart_cache_key(user_id):
    return f"cart:{user_id}"


class CartDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        cache_key = get_cart_cache_key(request.user.id)
        cached_cart = cache.get(cache_key)

        if cached_cart:
            return Response({"success": True, "cart": cached_cart}, status=status.HTTP_200_OK)

        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart, context={'request': request})

        # Cache the cart data for 5 minutes
        cache.set(cache_key, serializer.data, timeout=300)

        return Response({"success": True, "cart": serializer.data}, status=status.HTTP_200_OK)


class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = AddToCartSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']

        product = get_object_or_404(Product, id=product_id)
        cart, _ = Cart.objects.get_or_create(user=request.user)
        existing_cart_item = CartItem.objects.filter(
            cart=cart, product=product).first()

        if existing_cart_item:
            existing_cart_item.quantity += quantity
            existing_cart_item.save()
        else:
            CartItem.objects.create(
                cart=cart, product=product, quantity=quantity)

        # Invalidate the cart cache
        cache_key = get_cart_cache_key(request.user.id)
        cache.delete(cache_key)

        cart_serializer = CartSerializer(cart, context={'request': request})
        return Response({
            "success": True,
            "message": "Item added to cart",
            "cart": cart_serializer.data
        }, status=status.HTTP_201_CREATED)


class UpdateCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, product_id, *args, **kwargs):
        cart = Cart.objects.get(user=request.user)
        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        except CartItem.DoesNotExist:
            return Response({"success": False, "message": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CartItemUpdateSerializer(
            cart_item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            # Invalidate the cart cache
            cache_key = get_cart_cache_key(request.user.id)
            cache.delete(cache_key)

            cart_serializer = CartSerializer(
                cart, context={'request': request})
            return Response({
                "success": True,
                "message": "Cart item updated successfully",
                "cart": cart_serializer.data
            }, status=status.HTTP_200_OK)

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class RemoveFromCartView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, product_id, *args, **kwargs):
        cart = Cart.objects.get(user=request.user)
        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        except CartItem.DoesNotExist:
            return Response({"success": False, "message": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)

        cart_item.delete()

        # Invalidate the cart cache
        cache_key = get_cart_cache_key(request.user.id)
        cache.delete(cache_key)

        cart_serializer = CartSerializer(cart, context={'request': request})
        return Response({
            "success": True,
            "message": "Item removed from cart",
            "cart": cart_serializer.data
        }, status=status.HTTP_200_OK)
