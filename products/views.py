from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import Http404
from django.db.models import Q
from .models import Product, ProductImage
from .serializers import ProductSerializer, ProductImageSerializer


class ProductListAPIView(APIView):
    def get(self, request):
        search_term = request.query_params.get('search', '')
        queryset = Product.objects.all()
        if search_term:
            queryset = queryset.filter(
                Q(name__icontains=search_term) |
                Q(brand__icontains=search_term) |
                Q(category__name__icontains=search_term)
            )
        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        product = self.get_object(pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def patch(self, request, pk):
        product = self.get_object(pk)
        serializer = ProductSerializer(
            product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        product = self.get_object(pk)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductImageAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        image_file = request.FILES.get('image')
        if not image_file:
            return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)

        is_main = request.data.get('is_main', False)
        if is_main:
            ProductImage.objects.filter(
                product=product, is_main=True).update(is_main=False)

        product_image = ProductImage(
            product=product, image=image_file, is_main=is_main)
        try:
            product_image.full_clean()
            product_image.save()
        except ValidationError as e:
            return Response({'error': e.message_dict}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProductImageSerializer(product_image)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
