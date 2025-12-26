import re
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'phone_number']

    def validate_phone_number(self, value):
        if not re.match(r'^\+?[1-9]\d{6,14}$', value):
            raise serializers.ValidationError('Invalid phone number format')
        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()

    def validate_phone_number(self, value):
        if not re.match(r'^\+?[1-9]\d{6,14}$', value):
            raise serializers.ValidationError('Invalid phone number format')
        return value


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'phone_number', 'created_at']
        read_only_fields = ['id', 'created_at']


class AuthTokenSerializer(serializers.Serializer):
    token = serializers.CharField()
    user = UserSerializer()
