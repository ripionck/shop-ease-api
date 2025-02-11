from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Cart, CartItem, Product
from .serializers import (
    CartSerializer,
    CartItemUpdateSerializer,
    AddToCartSerializer,
    ProductCartSerializer
)

class CartDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart, context={'request': request})
        return Response({"success": True, "cart": serializer.data}, status=status.HTTP_200_OK)

class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = AddToCartSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"success": False, "message": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        cart, _ = Cart.objects.get_or_create(user=request.user)

        existing_cart_item = CartItem.objects.filter(cart=cart, product=product).first()

        if existing_cart_item:
            # Product already exists in the cart, return an error
            return Response({"success": False, "message": "Product is already in the cart.  Please update quantity instead."}, status=status.HTTP_400_BAD_REQUEST)

        else:
            cart_item = CartItem.objects.create(cart=cart, product=product, quantity=quantity)
            cart_serializer = CartSerializer(cart, context={'request': request})
            cart_data = cart_serializer.data

            formatted_products = []
            for item in cart.items.all():
                product_data = ProductCartSerializer(item).data
                formatted_products.append({
                    "productId": product_data['product_id'],
                    "quantity": item.quantity
                })
            cart_data['products'] = formatted_products

            return Response({"success": True, "message": "Item added to cart", "cart": cart_data}, status=status.HTTP_201_CREATED)

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
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
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
        cart_serializer = CartSerializer(cart_item.cart, context={'request': request})
        cart_data = cart_serializer.data

        formatted_products = []
        for item in cart_item.cart.items.all(): 
            product_data = ProductCartSerializer(item).data
            formatted_products.append({
                "productId": product_data['product_id'],
                "quantity": item.quantity
            })
        cart_data['products'] = formatted_products
        return Response({"success": True, "message": "Cart item updated successfully.", "cart": cart_data}, status=status.HTTP_200_OK)


    def delete(self, request, *args, **kwargs):
        serializer = CartItemUpdateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        product_id = validated_data.get('product_id')

        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response({"success": False, "message": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        except CartItem.DoesNotExist:
            return Response({"success": False, "message": "Cart item not found for this product."}, status=status.HTTP_404_NOT_FOUND)

        cart_item.delete()
        cart_serializer = CartSerializer(cart_item.cart, context={'request': request})
        cart_data = cart_serializer.data

        formatted_products = []
        for item in cart_item.cart.items.all():  
            product_data = ProductCartSerializer(item).data
            formatted_products.append({
                "productId": product_data['product_id'],
                "quantity": item.quantity
            })
        cart_data['products'] = formatted_products

        return Response({"success": True, "message": "Cart item removed successfully.", "cart": cart_data}, status=status.HTTP_200_OK)