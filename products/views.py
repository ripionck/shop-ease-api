from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import *
from .serializers import *


class CategoryView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    
    def get(self, request):
        queryset = Category.objects.filter(parent_category__isnull=True)
        total = queryset.count()
        skip = int(request.query_params.get('skip', 0))
        limit = int(request.query_params.get('limit', 30))
        categories = queryset[skip:skip + limit]
        serializer = CategorySerializer(categories, many=True)
        return Response({
            "categories": serializer.data,
            "total": total,
            "skip": skip,
            "limit": limit,
        })
    
    def post(self, request):
        if not request.user.is_authenticated or not request.user.is_staff:
            return Response({'detail': 'Only admin can create category.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk):
        if not request.user.is_authenticated or not request.user.is_staff:
            return Response({'detail': 'Only admin can update category.'}, status=status.HTTP_403_FORBIDDEN)
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        if not request.user.is_authenticated or not request.user.is_staff:
            return Response({'detail': 'Only admin can delete category.'}, status=status.HTTP_403_FORBIDDEN)
        category = get_object_or_404(Category, pk=pk)
        category.delete()
        return Response({"message": "Category deleted successfully."}, status=status.HTTP_200_OK)
    
class ProductView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request):
        queryset = Product.objects.all()
        total = queryset.count()
        skip = int(request.query_params.get('skip', 0))
        limit = int(request.query_params.get('limit', 30))
        products = queryset[skip:skip + limit]
        serializer = ProductSerializer(products, many=True)
        return Response({
            "products": serializer.data,
            "total": total,
            "skip": skip,
            "limit": limit
        })

    def post(self, request):
        if not request.user.is_authenticated or not request.user.is_staff:
            return Response(
                {'detail': 'Only admin can create product.'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(Product, pk=pk)

    def get(self, request, pk):
        product = self.get_object(pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, pk):
        if not request.user.is_authenticated or not request.user.is_staff:
            return Response(
                {'detail': 'Only admin can update product.'},
                status=status.HTTP_403_FORBIDDEN
            )
        product = self.get_object(pk)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not request.user.is_authenticated or not request.user.is_staff:
            return Response(
                {'detail': 'Only admin can delete product.'},
                status=status.HTTP_403_FORBIDDEN
            )
        product = self.get_object(pk)
        product.delete()
        return Response(
            {"message": "Product deleted successfully."},
            status=status.HTTP_200_OK
        )
    
    
class ProductImageView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, product_id):
        if not request.user.is_staff:
            return Response(
                {'detail': 'Only admin can add product image.'},
                status=status.HTTP_403_FORBIDDEN
            )

        product = get_object_or_404(Product, pk=product_id)
        image = request.FILES.get('image')
        if not image:
            return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if admin wants this image to be main.
        # The "is_main" option can be provided in the payload (as a boolean value or string)
        is_main = request.data.get('is_main', 'false').lower() == 'true'
        if is_main:
            # Unset any current main image for this product.
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
        return Response({'reviews': serializer.data}, status=status.HTTP_200_OK)
    
    def post(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        serializer = ReviewSerializer(data=request.data, context={'request': request, 'product': product})
        if serializer.is_valid():
            review = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ReviewDetailView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, review_id):
        return get_object_or_404(Review, pk=review_id)

    def delete(self, request, review_id):
        review = self.get_object(review_id)
        # Allow deletion if user is admin or the owner of the review.
        if not request.user.is_staff and review.user != request.user:
            return Response({'detail': 'Permission denied.'},
                            status=status.HTTP_403_FORBIDDEN)
        review.delete()
        return Response({'message': 'Review deleted successfully.'}, status=status.HTTP_200_OK)
