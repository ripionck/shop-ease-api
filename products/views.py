from django.core.cache import cache
from django.utils.http import urlencode
import hashlib
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.exceptions import PermissionDenied
from django.core.exceptions import ValidationError
from django.http import Http404
from django.db.models import Q
from core.utils import IsAdminOrReadOnly
from .models import Product, ProductImage
from .serializers import ProductSerializer, ProductImageSerializer
from .filters import ProductFilter
from rest_framework.pagination import PageNumberPagination


def generate_cache_key(base_key, request):
    """Generate unique cache key from request parameters"""
    params = urlencode(sorted(request.query_params.items()))
    key_hash = hashlib.md5(params.encode()).hexdigest()
    return f"{base_key}:{key_hash}"


def invalidate_product_caches():
    """Invalidate all product-related caches"""
    cache.delete_pattern("product_list:*")  # Requires redis-py >= 3.0
    cache.delete_pattern("product_detail:*")


class ProductListAPIView(APIView):
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        try:
            cache_key = generate_cache_key("product_list", request)
            cached_data = cache.get(cache_key)

            if cached_data:
                return Response(cached_data)

            # Adjust query parameters to handle 'category[]'
            query_params = request.query_params.copy()
            if 'category[]' in query_params:
                query_params.setlist(
                    'category', query_params.getlist('category[]'))
                del query_params['category[]']

            # Apply filters
            queryset = Product.objects.all()
            product_filter = ProductFilter(query_params, queryset=queryset)

            # Validate filters
            if not product_filter.form.is_valid():
                errors = {
                    field: [error.message for error in errors]
                    for field, errors in product_filter.form.errors.items()
                }
                return Response({
                    "success": False,
                    "message": "Invalid filters.",
                    "errors": errors
                }, status=status.HTTP_400_BAD_REQUEST)

            filtered_queryset = product_filter.qs

            # pagination
            paginator = PageNumberPagination()
            paginator.page_size = request.query_params.get('page_size', 10)

            result_page = paginator.paginate_queryset(
                filtered_queryset, request)
            serializer = ProductSerializer(result_page, many=True)

            return paginator.get_paginated_response({
                "success": True,
                "message": "Products retrieved successfully.",
                "products": serializer.data
            })

        except Exception as e:
            return Response({
                "success": False,
                "message": "An error occurred while retrieving products.",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        if not request.user.is_staff:
            raise PermissionDenied("Only admin users can create products.")

        if request.content_type == 'application/json':
            data = request.data
        else:
            data = request.data.dict()

        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            invalidate_product_caches()
            return Response({
                "success": True,
                "message": "Product created successfully.",
                "product": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "message": "Invalid product data.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailAPIView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        cache_key = f"product_detail:{pk}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response({"success": True, "message": "Product retrieved successfully.", "product": cached_data})

        product = self.get_object(pk)
        serializer = ProductSerializer(product)
        cache.set(cache_key, serializer.data, timeout=900)
        return Response({"success": True, "message": "Product retrieved successfully.", "product": serializer.data})

    def patch(self, request, pk):
        product = self.get_object(pk)

        if not request.user.is_staff:
            raise PermissionDenied("Only admin users can update products.")

        serializer = ProductSerializer(
            product,
            data=request.data,
            partial=True,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()
            cache.delete(f"product_detail:{pk}")
            invalidate_product_caches()
            return Response({
                "success": True,
                "message": "Product updated successfully.",
                "product": serializer.data
            })

        return Response({
            "success": False,
            "message": "Failed to update product.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        product = self.get_object(pk)

        if not request.user.is_staff:
            raise PermissionDenied("Only admin users can delete products.")

        product.delete()
        cache.delete(f"product_detail:{pk}")
        invalidate_product_caches()
        return Response({
            "success": True,
            "message": "Product deleted successfully."
        }, status=status.HTTP_204_NO_CONTENT)


class ProductImageAPIView(APIView):
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, product_id):
        try:
            if not request.user.is_staff:
                raise PermissionDenied("Only admin users can add images.")

            product = Product.objects.get(id=product_id)
            images = request.FILES.getlist('image')

            if not images:
                return Response({
                    "success": False,
                    "message": "No image files provided."
                }, status=status.HTTP_400_BAD_REQUEST)

            main_index = int(request.data.get('main_image_index', 0))

            created_images = []
            for index, image in enumerate(images):
                is_main = (index == main_index)

                if is_main:
                    ProductImage.objects.filter(
                        product=product,
                        is_main=True
                    ).update(is_main=False)

                product_image = ProductImage(
                    product=product,
                    image=image,
                    is_main=is_main
                )

                product_image.full_clean()
                product_image.save()
                created_images.append(product_image)

            serializer = ProductImageSerializer(created_images, many=True)
            cache.delete(f"product_detail:{product_id}")
            invalidate_product_caches()

            return Response({
                "success": True,
                "message": "Images added successfully.",
                "images": serializer.data
            }, status=status.HTTP_201_CREATED)

        except Product.DoesNotExist:
            return Response({
                "success": False,
                "message": "Product not found."
            }, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({
                "success": False,
                "message": "Validation error.",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "success": False,
                "message": "An error occurred while adding images.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
