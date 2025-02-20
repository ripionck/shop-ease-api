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


class ProductListAPIView(APIView):
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        try:
            search_term = request.query_params.get('search', '')
            category_id = request.query_params.get('category')
            brand = request.query_params.get('brand')
            min_price = request.query_params.get('min_price')
            max_price = request.query_params.get('max_price')

            queryset = Product.objects.all()

            if search_term:
                queryset = queryset.filter(
                    Q(name__icontains=search_term) |
                    Q(brand__icontains=search_term) |
                    Q(category__name__icontains=search_term)
                )

            if category_id:
                queryset = queryset.filter(category__id=category_id)

            if brand:
                queryset = queryset.filter(brand__iexact=brand)

            if min_price:
                queryset = queryset.filter(price__gte=min_price)

            if max_price:
                queryset = queryset.filter(price__lte=max_price)

            serializer = ProductSerializer(queryset, many=True)
            return Response({
                "success": True,
                "count": queryset.count(),
                "products": serializer.data
            })

        except Exception as e:
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        if not request.user.is_staff:
            raise PermissionDenied("Only admin users can create products")

        # Handle JSON data
        if request.content_type == 'application/json':
            data = request.data
        # Handle form-data
        else:
            data = request.data.dict()

        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Product created successfully",
                "product": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "message": "Invalid product data",
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
        product = self.get_object(pk)
        serializer = ProductSerializer(product)
        return Response({"success": True, "product": serializer.data})

    def patch(self, request, pk):
        product = self.get_object(pk)

        if not request.user.is_staff:
            raise PermissionDenied("Only admin users can update products")

        serializer = ProductSerializer(
            product,
            data=request.data,
            partial=True,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Product updated successfully",
                "product": serializer.data
            })

        return Response({
            "success": False,
            "message": "Update failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        product = self.get_object(pk)

        if not request.user.is_staff:
            raise PermissionDenied("Only admin users can delete products")

        product.delete()
        return Response({
            "success": True,
            "message": "Product deleted successfully"
        }, status=status.HTTP_204_NO_CONTENT)


class ProductImageAPIView(APIView):
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, product_id):
        try:
            if not request.user.is_staff:
                raise PermissionDenied("Only admin users can add images")

            product = Product.objects.get(id=product_id)
            image_file = request.FILES.get('image')

            if not image_file:
                return Response({
                    "success": False,
                    "error": "No image file provided"
                }, status=status.HTTP_400_BAD_REQUEST)

            is_main = request.data.get('is_main', False)

            # Handle main image update
            if is_main:
                ProductImage.objects.filter(
                    product=product,
                    is_main=True
                ).update(is_main=False)

            product_image = ProductImage(
                product=product,
                image=image_file,
                is_main=is_main
            )

            product_image.full_clean()
            product_image.save()

            return Response({
                "success": True,
                "message": "Image added successfully",
                "image": ProductImageSerializer(product_image).data
            }, status=status.HTTP_201_CREATED)

        except Product.DoesNotExist:
            return Response({
                "success": False,
                "error": "Product not found"
            }, status=status.HTTP_404_NOT_FOUND)

        except ValidationError as e:
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
