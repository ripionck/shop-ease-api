from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Category
from .serializers import CategorySerializer
from core.utils import IsAdminOrReadOnly
from rest_framework.pagination import PageNumberPagination


class CategoryListView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        categories = Category.objects.all()

        # Pagination
        paginator = PageNumberPagination()
        paginator.page_size = request.query_params.get('page_size', 10)

        result_page = paginator.paginate_queryset(categories, request)
        serializer = CategorySerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Category created successfully.",
                    "category": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                "message": "Category creation failed.",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class CategoryDetailView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return None

    def get(self, request, pk):
        category = self.get_object(pk)
        if category is None:
            return Response(
                {"message": "Category not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = CategorySerializer(category)
        return Response({
            "message": "Category retrieved successfully.",
            "category": serializer.data
        }, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        category = self.get_object(pk)
        if category is None:
            return Response(
                {"message": "Category not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = CategorySerializer(
            category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Category updated successfully.",
                "category": serializer.data
            }, status=status.HTTP_200_OK)
        return Response(
            {
                "message": "Category update failed.",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        category = self.get_object(pk)
        if category is None:
            return Response(
                {"message": "Category not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        category.delete()
        return Response(
            {"message": "Category deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )
