from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, UserLoginSerializer
from django.contrib.auth.models import update_last_login


class UserRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "message": "Registration successful.",
                    "user": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                "message": "Invalid input.",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            update_last_login(None, user)

            refresh = RefreshToken.for_user(user)
            user_data = UserSerializer(user).data

            return Response(
                {
                    "message": "Login successful.",
                    "user": user_data,
                    "refresh": str(refresh),
                    "access": str(refresh.access_token)
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "message": "Invalid credentials.",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        serializer = UserSerializer(request.user)
        return Response(
            {
                "message": "Profile retrieved successfully.",
                "user": serializer.data
            },
            status=status.HTTP_200_OK
        )

    def patch(self, request, format=None):
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Profile updated successfully.",
                    "user": serializer.data
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "message": "Update failed. Invalid input.",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, format=None):
        request.user.delete()
        return Response(
            {"message": "Account deleted successfully."},
            status=status.HTTP_200_OK
        )
