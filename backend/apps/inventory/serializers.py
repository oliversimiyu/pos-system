from rest_framework import serializers
from .models import StockMovement, StockAlert, StockCount, StockCountItem
from apps.products.models import Product
from apps.products.serializers import ProductSerializer


class StockMovementSerializer(serializers.ModelSerializer):
    """Serializer for stock movements"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = StockMovement
        fields = [
            'id', 'product', 'product_name', 'movement_type',
            'quantity', 'stock_before', 'stock_after',
            'reference_number', 'unit_cost', 'notes',
            'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'stock_before', 'stock_after', 'created_by', 'created_at']


class StockMovementCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating stock movements"""
    
    class Meta:
        model = StockMovement
        fields = ['product', 'movement_type', 'quantity', 'unit_cost', 'reference_number', 'notes']
    
    def validate_quantity(self, value):
        """Validate quantity for movement type"""
        movement_type = self.initial_data.get('movement_type')
        
        # For sales and reductions, quantity should be negative
        if movement_type in ['sale', 'damage', 'transfer'] and value > 0:
            return -abs(value)
        
        # For purchases and additions, quantity should be positive
        if movement_type in ['purchase', 'return'] and value < 0:
            return abs(value)
        
        return value
    
    def create(self, validated_data):
        """Create stock movement and update product stock"""
        request = self.context.get('request')
        product = validated_data['product']
        quantity = validated_data['quantity']
        
        # Record current stock
        stock_before = product.stock
        stock_after = stock_before + quantity
        
        # Create movement
        movement = StockMovement.objects.create(
            created_by=request.user,
            stock_before=stock_before,
            stock_after=stock_after,
            **validated_data
        )
        
        # Update product stock
        product.stock = stock_after
        product.save()
        
        # Check for low stock and create alert if needed
        if product.is_low_stock and not StockAlert.objects.filter(
            product=product, status='active'
        ).exists():
            StockAlert.objects.create(
                product=product,
                current_stock=product.stock,
                threshold=product.low_stock_threshold
            )
        
        return movement


class StockAlertSerializer(serializers.ModelSerializer):
    """Serializer for stock alerts"""
    product_details = ProductSerializer(source='product', read_only=True)
    resolved_by_name = serializers.CharField(source='resolved_by.username', read_only=True)
    
    class Meta:
        model = StockAlert
        fields = [
            'id', 'product', 'product_details', 'current_stock', 'threshold',
            'status', 'resolved_by', 'resolved_by_name', 'resolved_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StockCountItemSerializer(serializers.ModelSerializer):
    """Serializer for stock count items"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_barcode = serializers.CharField(source='product.barcode', read_only=True)
    
    class Meta:
        model = StockCountItem
        fields = [
            'id', 'product', 'product_name', 'product_barcode',
            'system_quantity', 'physical_quantity', 'variance',
            'notes', 'counted_at'
        ]
        read_only_fields = ['id', 'variance', 'counted_at']


class StockCountSerializer(serializers.ModelSerializer):
    """Serializer for stock counts"""
    items = StockCountItemSerializer(many=True, read_only=True)
    started_by_name = serializers.CharField(source='started_by.username', read_only=True)
    completed_by_name = serializers.CharField(source='completed_by.username', read_only=True)
    
    class Meta:
        model = StockCount
        fields = [
            'id', 'count_number', 'description', 'status',
            'started_by', 'started_by_name', 'completed_by', 'completed_by_name',
            'started_at', 'completed_at', 'notes', 'items'
        ]
        read_only_fields = ['id', 'count_number', 'started_by', 'started_at']
