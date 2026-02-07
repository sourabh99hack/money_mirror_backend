from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer
)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response({
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "is_onboarded": user.is_onboarded,
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        user.last_login_at = timezone.now()
        user.save(update_fields=["last_login_at"])

        refresh = RefreshToken.for_user(user)

        return Response({
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "is_onboarded": user.is_onboarded,
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "expires_in": 3600,
        }, status=status.HTTP_200_OK)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
