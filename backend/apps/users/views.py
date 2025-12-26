from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import login
from .models import User
from .serializers import UserSerializer, UserCreateSerializer, LoginSerializer


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User CRUD operations"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'login']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        """User login endpoint"""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        })
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """User logout endpoint"""
        request.user.auth_token.delete()
        return Response({'message': 'Successfully logged out'})
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user info"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
