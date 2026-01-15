from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from django.contrib.auth import get_user_model

from recycling.services import RecyclingService

User = get_user_model()

from .serializers import (
    UserRegistrationSerializer, UserSerializer, UserStatsSerializer
)

class UserRegistrationView(generics.CreateAPIView):
    """Register a new user"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Register a new user",
        description="Create a new user account for the recycling system"
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'message': 'User registered successfully',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get or update user profile"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    @extend_schema(
        summary="Get user profile",
        description="Retrieve the authenticated user's profile information"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class UserStatsView(APIView):
    """Get user statistics"""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Get user statistics",
        description="Get comprehensive statistics about the user's recycling activity",
        responses={200: UserStatsSerializer}
    )
    def get(self, request):
        service = RecyclingService()
        stats = service.get_user_stats(request.user)
        
        serializer = UserStatsSerializer(stats)
        return Response(serializer.data)

