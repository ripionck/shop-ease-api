from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from .models import Offer
from .serializers import OfferSerializer


class OfferListCreateView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        offers = Offer.objects.all()
        if not offers.exists():
            return Response({
                'status': 'success',
                'message': 'No offers found.',
                'data': []
            }, status=status.HTTP_200_OK)

        serializer = OfferSerializer(offers, many=True)
        return Response({
            'status': 'success',
            'message': 'Offers retrieved successfully.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = OfferSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': 'Offer created successfully.',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'status': 'error',
            'message': 'Invalid data provided. Offer creation failed.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class OfferDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get_object(self, pk):
        try:
            return Offer.objects.get(pk=pk)
        except Offer.DoesNotExist:
            return None

    def get(self, request, pk):
        offer = self.get_object(pk)
        if not offer:
            return Response({
                'status': 'error',
                'message': 'Offer not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = OfferSerializer(offer)
        return Response({
            'status': 'success',
            'message': 'Offer retrieved successfully.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def put(self, request, pk):
        offer = self.get_object(pk)
        if not offer:
            return Response({
                'status': 'error',
                'message': 'Offer not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = OfferSerializer(offer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': 'Offer updated successfully.',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            'status': 'error',
            'message': 'Invalid data provided. Offer update failed.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        offer = self.get_object(pk)
        if not offer:
            return Response({
                'status': 'error',
                'message': 'Offer not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        offer.delete()
        return Response({
            'status': 'success',
            'message': 'Offer deleted successfully.'
        }, status=status.HTTP_204_NO_CONTENT)
