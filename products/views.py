import uuid
from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, BasePermission, IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import *
from .serializers import *
from rest_framework.pagination import PageNumberPagination

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

class CategoryPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class CategoryView(APIView):
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    pagination_class = CategoryPagination

    def get(self, request):
        queryset = Category.objects.filter(parent_category__isnull=True)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        serializer = CategorySerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

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

class ProductPagination(PageNumberPagination):
    page_size = 5  
    page_size_query_param = 'page_size'
    max_page_size = 100

class ProductView(APIView):
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    pagination_class = ProductPagination

    def get(self, request):
        queryset = Product.objects.all().prefetch_related('category', 'subcategory')

        # Optimize with values() if you only need a subset of fields:
        # products = queryset.values('id', 'name', 'price', 'category_id', 'subcategory_id', 'main_image').prefetch_related('category', 'subcategory') # Exampl

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        serializer = ProductSerializer(page, many=True)
        return paginator.get_paginated_response( serializer.data)

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

class ReviewPagination(PageNumberPagination):
    page_size = 10 
    page_size_query_param = 'page_size'
    max_page_size = 100

class ReviewView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = ReviewPagination

    def get(self, request, product_id):
        reviews = Review.objects.filter(product_id=product_id)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(reviews, request)
        serializer = ReviewSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, product_id):
        self.permission_classes = [IsAuthenticated]
        product = get_object_or_404(Product, pk=product_id)
        serializer = ReviewSerializer(data=request.data, context={'request': request, 'product': product})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Review created for the product", "review": serializer.data}, status=status.HTTP_201_CREATED)
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