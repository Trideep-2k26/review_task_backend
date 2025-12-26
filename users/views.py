from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from .models import User
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data['phone_number']
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return Response(
                {'error': 'User with this phone number does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)
