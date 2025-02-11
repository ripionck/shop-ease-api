from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import ShoppingCart, CartItem, Product
from .serializers import (
    ShoppingCartSerializer,
    CartItemUpdateSerializer,
    AddToCartSerializer
)

class ShoppingCartDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        cart, _ = ShoppingCart.objects.get_or_create(user=request.user)
        serializer = ShoppingCartSerializer(cart, context={'request': request})
        return Response({"cart": serializer.data}, status=status.HTTP_200_OK)

class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = AddToCartSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        cart, _ = ShoppingCart.objects.get_or_create(user=request.user)

        existing_cart_item = CartItem.objects.filter(cart=cart, product=product).first()

        if existing_cart_item:
            return Response({"error": "Product is already in the cart."}, status=status.HTTP_400_BAD_REQUEST)  

        else:
            cart_item = CartItem.objects.create(cart=cart, product=product, quantity=quantity)
            return Response({"message": "Product added to cart successfully."}, status=status.HTTP_201_CREATED)


class EditCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        serializer = CartItemUpdateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        product_id = validated_data.get('product_id')
        quantity = validated_data.get('quantity')

        if not product_id and not quantity:
            return Response({"error": "At least one of 'quantity' or 'product_id' must be provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart = ShoppingCart.objects.get(user=request.user)
        except ShoppingCart.DoesNotExist:
            return Response({"error": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        except CartItem.DoesNotExist:
            return Response({"error": "Cart item not found for this product."}, status=status.HTTP_404_NOT_FOUND)

        if quantity is not None:
            cart_item.quantity = quantity
            if cart_item.quantity <= 0:
                cart_item.delete()
                return Response({"message": "Cart item removed successfully."}, status=status.HTTP_204_NO_CONTENT)

        cart_item.save()
        serializer = ShoppingCartSerializer(cart_item.cart, context={'request': request})
        return Response({"message": "Cart item updated successfully.", "cart": serializer.data}, status=status.HTTP_200_OK)


    def delete(self, request, *args, **kwargs): 
        serializer = CartItemUpdateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        validated_data = serializer.validated_data
        product_id = validated_data.get('product_id')

        try:
            cart = ShoppingCart.objects.get(user=request.user)
        except ShoppingCart.DoesNotExist:
            return Response({"error": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        except CartItem.DoesNotExist:
            return Response({"error": "Cart item not found for this product."}, status=status.HTTP_404_NOT_FOUND)

        cart_item.delete()
        return Response({"message": "Cart item removed successfully.", "cart": ShoppingCartSerializer(cart_item.cart).data}, status=status.HTTP_204_NO_CONTENT)

