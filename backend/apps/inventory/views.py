from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import StockMovement, StockAlert, StockCount, StockCountItem
from .serializers import (
    StockMovementSerializer, StockMovementCreateSerializer,
    StockAlertSerializer, StockCountSerializer, StockCountItemSerializer
)
from apps.products.models import Product
import uuid


class StockMovementViewSet(viewsets.ModelViewSet):
    """ViewSet for stock movements"""
    queryset = StockMovement.objects.all().select_related('product', 'created_by')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product', 'movement_type', 'created_by']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return StockMovementCreateSerializer
        return StockMovementSerializer
    
    def get_queryset(self):
        """Filter by date range if provided"""
        queryset = super().get_queryset()
        
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        return queryset


class StockAlertViewSet(viewsets.ModelViewSet):
    """ViewSet for stock alerts"""
    queryset = StockAlert.objects.all().select_related('product', 'resolved_by')
    serializer_class = StockAlertSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'product']
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark alert as resolved"""
        alert = self.get_object()
        
        if alert.status == 'resolved':
            return Response(
                {'error': 'Alert is already resolved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        alert.status = 'resolved'
        alert.resolved_by = request.user
        alert.resolved_at = timezone.now()
        alert.save()
        
        serializer = self.get_serializer(alert)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def ignore(self, request, pk=None):
        """Mark alert as ignored"""
        alert = self.get_object()
        alert.status = 'ignored'
        alert.save()
        
        serializer = self.get_serializer(alert)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active alerts"""
        alerts = self.get_queryset().filter(status='active')
        serializer = self.get_serializer(alerts, many=True)
        return Response(serializer.data)


class StockCountViewSet(viewsets.ModelViewSet):
    """ViewSet for stock counts"""
    queryset = StockCount.objects.all().prefetch_related('items__product')
    serializer_class = StockCountSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']
    
    def create(self, request, *args, **kwargs):
        """Create new stock count"""
        count_number = f"COUNT-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        stock_count = StockCount.objects.create(
            count_number=count_number,
            description=request.data.get('description', ''),
            started_by=request.user
        )
        
        serializer = self.get_serializer(stock_count)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """Add product to stock count"""
        stock_count = self.get_object()
        
        if stock_count.status != 'in_progress':
            return Response(
                {'error': 'Can only add items to in-progress counts'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        product_id = request.data.get('product')
        physical_quantity = request.data.get('physical_quantity')
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        item, created = StockCountItem.objects.update_or_create(
            stock_count=stock_count,
            product=product,
            defaults={
                'system_quantity': product.stock,
                'physical_quantity': physical_quantity,
                'notes': request.data.get('notes', '')
            }
        )
        
        serializer = StockCountItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete stock count and apply adjustments"""
        stock_count = self.get_object()
        
        if stock_count.status != 'in_progress':
            return Response(
                {'error': 'Stock count is not in progress'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Apply adjustments for items with variance
        for item in stock_count.items.all():
            if item.variance != 0:
                # Create stock movement for adjustment
                StockMovement.objects.create(
                    product=item.product,
                    movement_type='adjustment',
                    quantity=item.variance,
                    stock_before=item.system_quantity,
                    stock_after=item.physical_quantity,
                    reference_number=stock_count.count_number,
                    notes=f"Stock count adjustment: {item.notes}",
                    created_by=request.user
                )
                
                # Update product stock
                item.product.stock = item.physical_quantity
                item.product.save()
        
        # Mark as completed
        stock_count.status = 'completed'
        stock_count.completed_by = request.user
        stock_count.completed_at = timezone.now()
        stock_count.save()
        
        serializer = self.get_serializer(stock_count)
        return Response(serializer.data)
