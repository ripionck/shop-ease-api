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
        reviews = Review.objects.filter(product_id=product_id)
        serializer = ReviewSerializer(reviews, many=True)
        return Response({"reviews": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request, product_id):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required to create a review."}, status=status.HTTP_401_UNAUTHORIZED)

        product = get_object_or_404(Product, pk=product_id)

        serializer = ReviewSerializer(data=request.data, context={'request': request, 'product': product})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"message": "Review added successfully!", "review": serializer.data}, status=status.HTTP_201_CREATED)

        return Response({"message": "Invalid data.", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ReviewDetailView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, review_id):
        return get_object_or_404(Review, pk=review_id)

    def get(self, request, review_id): 
        review = self.get_object(review_id)
        serializer = ReviewSerializer(review)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, review_id):
        review = self.get_object(review_id)

        if not request.user.is_staff and review.user != request.user:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Review updated successfully!", "review": serializer.data}, status=status.HTTP_200_OK)
        return Response({"message": "Invalid data.", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, review_id):
        review = self.get_object(review_id)

        if not request.user.is_staff and review.user != request.user:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        review.delete()
        return Response({"message": "Review deleted!"}, status=status.HTTP_204_NO_CONTENT)