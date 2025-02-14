from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer


class NotificationListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve all notifications for the authenticated user.
        """
        notifications = Notification.objects.filter(user=request.user)
        serializer = NotificationSerializer(notifications, many=True)
        return Response({
            'status': 'success',
            'message': 'Notifications retrieved successfully.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Create a new notification for the authenticated user.
        """
        serializer = NotificationSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                'status': 'success',
                'message': 'Notification created successfully.',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'status': 'error',
            'message': 'Notification creation failed.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class NotificationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        """
        Helper method to get a notification by ID and ensure it belongs to the user.
        """
        try:
            return Notification.objects.get(pk=pk, user=user)
        except Notification.DoesNotExist:
            return None

    def get(self, request, pk):
        """
        Retrieve a specific notification by ID.
        """
        notification = self.get_object(pk, request.user)
        if notification:
            serializer = NotificationSerializer(notification)
            return Response({
                'status': 'success',
                'message': 'Notification retrieved successfully.',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            'status': 'error',
            'message': 'Notification not found.'
        }, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        """
        Update a specific notification by ID (e.g., mark as read).
        """
        notification = self.get_object(pk, request.user)
        if notification:
            serializer = NotificationSerializer(
                notification, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': 'success',
                    'message': 'Notification updated successfully.',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            return Response({
                'status': 'error',
                'message': 'Notification update failed.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'status': 'error',
            'message': 'Notification not found.'
        }, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        """
        Delete a specific notification by ID.
        """
        notification = self.get_object(pk, request.user)
        if notification:
            notification.delete()
            return Response({
                'status': 'success',
                'message': 'Notification deleted successfully.'
            }, status=status.HTTP_204_NO_CONTENT)
        return Response({
            'status': 'error',
            'message': 'Notification not found.'
        }, status=status.HTTP_404_NOT_FOUND)
