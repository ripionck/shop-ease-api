from email.policy import HTTP
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from .models import Category, Product, ProductImage, Review
from .serializers import CategorySerializer, ProductSerializer, ProductImageSerializer, ReviewSerializer


class IsAdminOrReadOnly(IsAuthenticatedOrReadOnly):
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return request.user.is_authenticated and request.user.is_staff


class CategoryListView(APIView):
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [JSONParser]

    def get(self, request):
        queryset = Category.objects.filter(parent_category__isnull=True)
        serializer = CategorySerializer(queryset, many=True)
        return Response({"success": True, "categories":serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Category added successfully!", "category": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetailView(APIView):
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [JSONParser]

    def get_object(self, pk):
        return get_object_or_404(Category, pk=pk)

    def get(self, request, pk):
        category = self.get_object(pk)
        serializer = CategorySerializer(category)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        category = self.get_object(pk)
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        category = self.get_object(pk)
        category.delete()
        return Response({"message":"Product deleted!"}, status=status.HTTP_204_NO_CONTENT)


class ProductPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductListView(APIView):
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    pagination_class = ProductPagination

    def get(self, request):
        queryset = Product.objects.all().prefetch_related('category', 'subcategory')
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        serializer = ProductSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Product added successfully!", "product": serializer.data}, status=status.HTTP_201_CREATED)
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
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductImageView(APIView):
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        serializer = ProductImageSerializer(data=request.data)
        if serializer.is_valid():
            is_main = serializer.validated_data.get('is_main', False)
            if is_main:
                ProductImage.objects.filter(product=product, is_main=True).update(is_main=False)
            product_image = serializer.save(product=product)
            if is_main:
                product.main_image = product_image.image
                product.save(update_fields=['main_image'])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ReviewListView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, product_id):
        reviews = Review.objects.filter(product_id=product_id)
        serializer = ReviewSerializer(reviews, many=True)
        return Response({"reviews": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        serializer = ReviewSerializer(data=request.data, context={'request': request, 'product': product})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"message":"review added", "review": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ReviewDetailView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, review_id):
        return get_object_or_404(Review, pk=review_id)

    def delete(self, request, review_id):
        review = self.get_object(review_id)
        if not request.user.is_staff and review.user != request.user:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        review.delete()
        return Response({"message": "Review deleted!"},status=status.HTTP_204_NO_CONTENT)