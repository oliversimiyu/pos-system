from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import login
from .models import User
from .serializers import UserSerializer, UserCreateSerializer, LoginSerializer


class IsAdmin(IsAuthenticated):
    """Permission class for admin-only access"""
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == 'admin'


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User CRUD operations"""
    queryset = User.objects.all().order_by('-created_at')
    serializer_class = UserSerializer
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def get_permissions(self):
        if self.action == 'login':
            return [AllowAny()]
        elif self.action in ['list', 'retrieve', 'create', 'update', 'partial_update', 'destroy']:
            # Only admins can manage users
            return [IsAdmin()]
        return [IsAuthenticated()]
    
    def list(self, request, *args, **kwargs):
        """List all users - admin only"""
        # Check if user is admin
        if not hasattr(request.user, 'role') or request.user.role != 'admin':
            return Response({'detail': 'Permission denied. Admin access required.'}, 
                          status=status.HTTP_403_FORBIDDEN)
        return super().list(request, *args, **kwargs)
    
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
