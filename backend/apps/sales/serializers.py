from rest_framework import serializers
from .models import Sale, SaleItem
from apps.products.models import Product
from apps.products.serializers import ProductSerializer
from django.utils import timezone
import uuid


class SaleItemSerializer(serializers.ModelSerializer):
    """Serializer for sale items"""
    product_details = ProductSerializer(source='product', read_only=True)
    
    class Meta:
        model = SaleItem
        fields = [
            'id', 'product', 'product_details', 'product_name', 'product_barcode',
            'unit_price', 'cost_price', 'quantity', 'tax_rate',
            'subtotal', 'tax_amount', 'total', 'created_at'
        ]
        read_only_fields = ['id', 'subtotal', 'tax_amount', 'total', 'created_at']


class SaleItemCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating sale items"""
    
    class Meta:
        model = SaleItem
        fields = ['product', 'quantity']
    
    def validate_product(self, value):
        """Ensure product exists and is active"""
        if not value.is_active:
            raise serializers.ValidationError("Product is not active")
        return value
    
    def validate_quantity(self, value):
        """Ensure quantity is positive"""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero")
        return value
    
    def validate(self, data):
        """Check stock availability"""
        product = data['product']
        quantity = data['quantity']
        
        if product.stock < quantity:
            raise serializers.ValidationError({
                'quantity': f"Insufficient stock. Available: {product.stock}"
            })
        
        return data


class SaleSerializer(serializers.ModelSerializer):
    """Serializer for sales"""
    items = SaleItemSerializer(many=True, read_only=True)
    cashier_name = serializers.CharField(source='cashier.username', read_only=True)
    
    class Meta:
        model = Sale
        fields = [
            'id', 'sale_number', 'cashier', 'cashier_name',
            'customer_name', 'customer_phone',
            'subtotal', 'tax_amount', 'discount', 'total',
            'amount_paid', 'change', 'status', 'payment_status',
            'notes', 'items', 'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'sale_number', 'subtotal', 'tax_amount', 'total',
            'change', 'payment_status', 'created_at', 'updated_at'
        ]


class SaleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating sales with items"""
    items = SaleItemCreateSerializer(many=True, write_only=True)
    
    class Meta:
        model = Sale
        fields = [
            'customer_name', 'customer_phone', 'discount',
            'amount_paid', 'notes', 'items'
        ]
    
    def validate_items(self, value):
        """Ensure at least one item"""
        if not value:
            raise serializers.ValidationError("Sale must have at least one item")
        return value
    
    def create(self, validated_data):
        """Create sale with items and update inventory"""
        items_data = validated_data.pop('items')
        request = self.context.get('request')
        
        # Generate unique sale number
        sale_number = f"SALE-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        # Create sale
        sale = Sale.objects.create(
            sale_number=sale_number,
            cashier=request.user,
            **validated_data
        )
        
        # Create sale items and update stock
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            
            # Create sale item with snapshot data
            SaleItem.objects.create(
                sale=sale,
                product=product,
                product_name=product.name,
                product_barcode=product.barcode,
                unit_price=product.price,
                cost_price=product.cost_price,
                quantity=quantity,
                tax_rate=product.tax
            )
            
            # Reduce stock
            product.stock -= quantity
            product.save()
        
        # Calculate totals
        sale.calculate_totals()
        
        # Update payment status
        sale.update_payment_status()
        
        # Mark as completed if fully paid
        if sale.payment_status == 'paid':
            sale.status = 'completed'
            sale.completed_at = timezone.now()
            sale.change = sale.amount_paid - sale.total
            sale.save()
        
        return sale


class SaleUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating sale status"""
    
    class Meta:
        model = Sale
        fields = ['status', 'amount_paid', 'notes']
    
    def update(self, instance, validated_data):
        """Update sale and recalculate payment status"""
        instance = super().update(instance, validated_data)
        
        if 'amount_paid' in validated_data:
            instance.update_payment_status()
            instance.change = max(0, instance.amount_paid - instance.total)
            instance.save()
        
        if instance.payment_status == 'paid' and instance.status == 'pending':
            instance.status = 'completed'
            instance.completed_at = timezone.now()
            instance.save()
        
        return instance
