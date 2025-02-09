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
        cart = ShoppingCart.objects.get(user=request.user)
        serializer = ShoppingCartSerializer(cart)
        return Response(serializer.data)

class EditCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, cart_item_id, *args, **kwargs):
        cart_item = self.get_object(cart_item_id, request.user)
        if not cart_item:
            return Response({"error": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)

        new_quantity = request.data.get('quantity')
        if new_quantity is None:
            return Response({"error": "Quantity is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_quantity = int(new_quantity)
            if new_quantity < 0:
                raise ValueError("Quantity must be non-negative.")
        except ValueError:
            return Response({"error": "Invalid quantity value."}, status=status.HTTP_400_BAD_REQUEST)

        return self.update_or_delete_cart_item(cart_item, new_quantity)

    def get_object(self, cart_item_id, user):
        try:
            return CartItem.objects.get(id=cart_item_id, cart__user=user)
        except CartItem.DoesNotExist:
            return None

    def update_or_delete_cart_item(self, cart_item, new_quantity):
        if new_quantity == 0:
            cart_item.delete()
            return Response({"message": "Cart item removed successfully."}, status=status.HTTP_204_NO_CONTENT)
        else:
            cart_item.quantity = new_quantity
            cart_item.save()
            return Response({"message": "Cart item updated successfully."}, status=status.HTTP_200_OK)

class DeleteCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, cart_item_id, *args, **kwargs):
        cart_item = EditCartItemView().get_object(cart_item_id, request.user)
        if not cart_item:
            return Response({"error": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)

        cart_item.delete()
        return Response({"message": "Cart item deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = AddToCartSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']

        cart, _ = ShoppingCart.objects.get_or_create(user=request.user)
        product = Product.objects.get(id=product_id)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

        return Response({"message": "Product added to cart successfully."}, status=status.HTTP_201_CREATED)
