from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from cloudinary.uploader import upload
from .models import Category, Product, ProductImage, Review
from .serializers import CategorySerializer, ProductImageUploadSerializer, ProductSerializer, ReviewSerializer
from django.db.models import Q


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
        return Response({"success": True, "categories": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        if not request.user.is_staff:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Category added successfully!", "category": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"message": "Invalid data.", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


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
        if not request.user.is_staff:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        category = self.get_object(pk)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Category updated successfully!", "category": serializer.data}, status=status.HTTP_200_OK) 
        return Response({"message": "Invalid data.", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not request.user.is_staff:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        category = self.get_object(pk)
        category.delete()
        return Response({"message": "Category deleted!"}, status=status.HTTP_204_NO_CONTENT)


class ProductPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductListView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    pagination_class = ProductPagination

    def get(self, request):
        queryset = Product.objects.all().prefetch_related('category', 'subcategory', 'images')

        # Search functionality
        search_query = request.GET.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |  # Case-insensitive name search
                Q(description__icontains=search_query) |  # Case-insensitive description search
                Q(brand__icontains=search_query) |  # Case-insensitive brand search
                Q(category__name__icontains=search_query) |  # Search in category name
                Q(subcategory__name__icontains=search_query)  # Search in subcategory name
            ).distinct()  # Use distinct() to avoid duplicate results

        # Filtering by category
        category_id = request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        # Filtering by subcategory
        subcategory_id = request.GET.get('subcategory')
        if subcategory_id:
            queryset = queryset.filter(subcategory_id=subcategory_id)

        # Filtering by color
        color = request.GET.get('color')
        if color:
            queryset = queryset.filter(color__iexact=color)  # Case-insensitive color filter

        #Filtering by price range
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')

        if min_price and max_price:
            queryset = queryset.filter(price__range = (min_price, max_price))
        elif min_price:
            queryset = queryset.filter(price__gte=min_price)
        elif max_price:
            queryset = queryset.filter(price__lte=max_price)

        # Ordering
        ordering = request.GET.get('ordering', '-created_at') #Default ordering by created_at
        queryset = queryset.order_by(ordering)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        serializer = ProductSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
    def post(self, request):
        if not request.user.is_staff:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProductSerializer(data=request.data, context={'request': request}) 
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Product added successfully!", "product": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"message": "Invalid data.", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(Product, pk=pk)

    def get(self, request, pk):
        product = self.get_object(pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK) 

    def put(self, request, pk):
        if not request.user.is_staff:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        product = self.get_object(pk)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Product updated successfully!", "product": serializer.data}, status=status.HTTP_200_OK) 
        return Response({"message": "Invalid data.", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not request.user.is_staff:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        product = self.get_object(pk)
        product.delete()
        return Response({"message": "Product deleted!"}, status=status.HTTP_204_NO_CONTENT)


class ProductImageUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, product_id, *args, **kwargs):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        image_file = request.data.get('image')
        if not image_file:
            return Response({"error": "No image provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            upload_result = upload(image_file)
            image_url = upload_result.get("secure_url")

            is_main = request.data.get('is_main', False)
            if not product.images.filter(is_main=True).exists():
                is_main = True

            product_image = ProductImage.objects.create(
                product=product,
                image=image_url,
                is_main=is_main
            )

            serializer = ProductImageUploadSerializer(product_image)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": f"Failed to upload image: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


