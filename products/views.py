from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, BasePermission, IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import *
from .serializers import *

class IsAdminOrReadOnly(BasePermission):
    """
    Custom permission to allow read-only access to all, but
    only allow admin users to create, update, or delete.
    """
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True  

        # Check for admin role for other methods
        return request.user.is_authenticated and request.user.role == 'admin'


class CategoryView(APIView):
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request):
        queryset = Category.objects.filter(parent_category__isnull=True)
        total = queryset.count()
        skip = int(request.query_params.get('skip', 0))
        limit = int(request.query_params.get('limit', 10))
        categories = queryset[skip:skip + limit]
        serializer = CategorySerializer(categories, many=True)
        return Response({
            "success": True,
            "categories": serializer.data,
            "total": total,
            "skip": skip,
            "limit": limit,
        })

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError:  
                return Response({"error": "A category with this name already exists."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Category updated successfully", "category":serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        category.delete()
        return Response({"message": "Category deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class ProductView(APIView):
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request):
        queryset = Product.objects.all()
        total = queryset.count()
        skip = int(request.query_params.get('skip', 0))
        limit = int(request.query_params.get('limit', 30))
        products = queryset[skip:skip + limit]
        serializer = ProductSerializer(products, many=True)
        return Response({
            "success": True,
            "products": serializer.data,
            "total": total,
            "skip": skip,
            "limit": limit
        })

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"message": "Product added successfully", "product":serializer.data}, status=status.HTTP_201_CREATED)
            except IntegrityError:  
                return Response({"error": "A product with this name already exists."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(Product, pk=pk)

    def get(self, request, pk):
        product = self.get_object(pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, pk):
        product = self.get_object(pk)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        product = self.get_object(pk)
        product.delete()
        return Response({"message": "Product deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class ProductImageView(APIView):
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        image = request.FILES.get('image')
        if not image:
            return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)

        is_main = request.data.get('is_main', 'false').lower() == 'true'
        if is_main:
            ProductImage.objects.filter(product=product, is_main=True).update(is_main=False)

        product_image = ProductImage.objects.create(
            product=product,
            image=image,
            is_main=is_main
        )

        return Response(ProductImageSerializer(product_image).data, status=status.HTTP_201_CREATED)


class ReviewView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, product_id):
        reviews = Review.objects.filter(product_id=product_id)
        serializer = ReviewSerializer(reviews, many=True)
        return Response({"success": True,'reviews': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request, product_id):
        self.permission_classes = [IsAuthenticated]
        product = get_object_or_404(Product, pk=product_id)
        serializer = ReviewSerializer(data=request.data, context={'request': request, 'product': product})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Review created for the peoduct", "review": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewDetailView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, review_id):
        return get_object_or_404(Review, pk=review_id)

    def delete(self, request, review_id):
        review = self.get_object(review_id)
        if not request.user.is_staff and review.user != request.user:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        review.delete()
        return Response({'message': 'Review deleted successfully.'}, status=status.HTTP_200_OK)