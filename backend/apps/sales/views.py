from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Sale, SaleItem
from .serializers import (
    SaleSerializer, SaleCreateSerializer, SaleUpdateSerializer,
    SaleItemSerializer
)


class SaleViewSet(viewsets.ModelViewSet):
    """ViewSet for sales/orders"""
    queryset = Sale.objects.all().select_related('cashier').prefetch_related('items__product')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'payment_status', 'cashier']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return SaleCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return SaleUpdateSerializer
        return SaleSerializer
    
    def get_queryset(self):
        """Filter by date range if provided"""
        queryset = super().get_queryset()
        
        # Cashiers can only see their own sales
        if self.request.user.role == 'cashier':
            queryset = queryset.filter(cashier=self.request.user)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        # Search by sale number or customer
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(sale_number__icontains=search) |
                Q(customer_name__icontains=search) |
                Q(customer_phone__icontains=search)
            )
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a sale and restore inventory"""
        sale = self.get_object()
        
        if sale.status == 'cancelled':
            return Response(
                {'error': 'Sale is already cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if sale.payment_status == 'paid':
            return Response(
                {'error': 'Cannot cancel a paid sale. Issue refund instead.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Restore stock
        for item in sale.items.all():
            item.product.stock += item.quantity
            item.product.save()
        
        # Update sale status
        sale.status = 'cancelled'
        sale.save()
        
        serializer = self.get_serializer(sale)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark sale as completed"""
        sale = self.get_object()
        
        if sale.status == 'completed':
            return Response(
                {'error': 'Sale is already completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if sale.payment_status != 'paid':
            return Response(
                {'error': 'Sale must be fully paid before completing'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        sale.status = 'completed'
        sale.save()
        
        serializer = self.get_serializer(sale)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's sales"""
        from django.utils import timezone
        today = timezone.now().date()
        
        sales = self.get_queryset().filter(created_at__date=today)
        
        serializer = self.get_serializer(sales, many=True)
        return Response(serializer.data)
