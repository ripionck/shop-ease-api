from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from products.models import Product
from .models import Review
from .serializers import ReviewSerializer


class ReviewListView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, product_id):
        try:
            reviews = Review.objects.filter(product_id=product_id)
            serializer = ReviewSerializer(reviews, many=True)
            return Response(
                {
                    "message": "Reviews retrieved successfully.",
                    "reviews": serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"message": "Failed to retrieve reviews."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request, product_id):
        if not request.user.is_authenticated:
            return Response(
                {"message": "Authentication required to create a review."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            product = Product.objects.get(pk=product_id)
            serializer = ReviewSerializer(
                data=request.data,
                context={
                    'request': request,
                    'product': product
                }
            )

            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "message": "Review created successfully!",
                        "review": serializer.data
                    },
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {
                    "message": "Validation error",
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except Product.DoesNotExist:
            return Response(
                {"message": "Product not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"message": "Failed to create review."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ReviewDetailView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, review_id):
        return get_object_or_404(Review, pk=review_id)

    def get(self, request, review_id):
        try:
            review = self.get_object(review_id)
            serializer = ReviewSerializer(review)
            return Response(
                {
                    "message": "Review retrieved successfully.",
                    "review": serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"message": "Failed to retrieve review."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def patch(self, request, review_id):
        try:
            review = self.get_object(review_id)

            if review.user != request.user:
                return Response(
                    {"message": "You don't have permission to edit this review."},
                    status=status.HTTP_403_FORBIDDEN
                )

            serializer = ReviewSerializer(
                review,
                data=request.data,
                partial=True
            )

            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "message": "Review updated successfully!",
                        "review": serializer.data
                    },
                    status=status.HTTP_200_OK
                )
            return Response(
                {
                    "message": "Validation error",
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return Response(
                {"message": "Failed to update review."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, review_id):
        try:
            review = self.get_object(review_id)

            if review.user != request.user:
                return Response(
                    {"message": "You don't have permission to delete this review."},
                    status=status.HTTP_403_FORBIDDEN
                )

            review.delete()
            return Response(
                {"message": "Review deleted successfully!"},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"message": "Failed to delete review."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
