from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                  'role', 'phone_number', 'is_active', 'created_at')
        read_only_fields = ('id', 'created_at')


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users"""
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name', 
                  'role', 'phone_number')
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            data['user'] = user
        else:
            raise serializers.ValidationError('Must include username and password')
        
        return data
