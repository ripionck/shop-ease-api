from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Wishlist, Product
from .serializers import WishlistSerializer, WishlistProductSerializer


class WishlistDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)

        if not wishlist.products.exists():
            return Response(
                {"message": "Your wishlist is currently empty."},
                status=status.HTTP_200_OK
            )

        serializer = WishlistSerializer(wishlist)
        return Response(
            {
                "message": "Wishlist retrieved successfully.",
                "wishlist": serializer.data
            },
            status=status.HTTP_200_OK
        )


class AddToWishlistView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = WishlistProductSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "message": "Invalid input data.",
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        product_id = serializer.validated_data['product_id']
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"message": "Product not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)

        if product in wishlist.products.all():
            return Response(
                {"message": "Product already exists in your wishlist."},
                status=status.HTTP_200_OK
            )

        wishlist.products.add(product)
        return Response(
            {"message": "Product added to wishlist successfully."},
            status=status.HTTP_201_CREATED
        )


class RemoveFromWishlistView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, product_id, *args, **kwargs):
        try:
            wishlist = Wishlist.objects.get(user=request.user)
        except Wishlist.DoesNotExist:
            return Response(
                {"message": "Wishlist not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"message": "Product not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if product not in wishlist.products.all():
            return Response(
                {"message": "Product not found in your wishlist."},
                status=status.HTTP_400_BAD_REQUEST
            )

        wishlist.products.remove(product)

        response_data = {
            "message": "Product removed from wishlist successfully."
        }

        if not wishlist.products.exists():
            response_data["message"] = "Product removed. Your wishlist is now empty."

        return Response(
            response_data,
            status=status.HTTP_200_OK
        )
