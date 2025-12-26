from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer, ProductCreateUpdateSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Category CRUD operations"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for Product CRUD operations with barcode search"""
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'barcode', 'sku', 'description']
    ordering_fields = ['name', 'price', 'stock', 'created_at']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductSerializer
    
    @action(detail=False, methods=['get'], url_path='barcode/(?P<barcode>[^/.]+)')
    def by_barcode(self, request, barcode=None):
        """Get product by barcode - for barcode scanner integration"""
        try:
            product = Product.objects.select_related('category').get(barcode=barcode, is_active=True)
            serializer = self.get_serializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found with this barcode'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get products with low stock"""
        low_stock_products = [p for p in self.get_queryset() if p.is_low_stock]
        serializer = self.get_serializer(low_stock_products, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_stock(self, request, pk=None):
        """Update product stock"""
        product = self.get_object()
        quantity = request.data.get('quantity', 0)
        operation = request.data.get('operation', 'add')  # 'add' or 'subtract'
        
        try:
            quantity = int(quantity)
            if operation == 'add':
                product.stock += quantity
            elif operation == 'subtract':
                if product.stock < quantity:
                    return Response(
                        {'error': 'Insufficient stock'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                product.stock -= quantity
            
            product.save()
            serializer = self.get_serializer(product)
            return Response(serializer.data)
        except ValueError:
            return Response(
                {'error': 'Invalid quantity'},
                status=status.HTTP_400_BAD_REQUEST
            )
