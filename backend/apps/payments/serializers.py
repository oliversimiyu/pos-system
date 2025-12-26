from rest_framework import serializers
from .models import Payment, PaymentCallback, Refund
from apps.sales.models import Sale
from django.utils import timezone
import uuid


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payments"""
    sale_number = serializers.CharField(source='sale.sale_number', read_only=True)
    initiated_by_name = serializers.CharField(source='initiated_by.username', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'sale', 'sale_number', 'method', 'amount', 'status',
            'transaction_reference', 'external_reference', 'phone_number',
            'account_number', 'initiated_by', 'initiated_by_name',
            'initiated_at', 'completed_at', 'error_message', 'metadata'
        ]
        read_only_fields = [
            'id', 'transaction_reference', 'status', 'external_reference',
            'initiated_by', 'initiated_at', 'completed_at', 'error_message'
        ]


class PaymentInitiateSerializer(serializers.Serializer):
    """Serializer for initiating payments"""
    sale = serializers.PrimaryKeyRelatedField(queryset=Sale.objects.all())
    method = serializers.ChoiceField(choices=Payment.METHOD_CHOICES)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    account_number = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        """Validate payment data"""
        sale = data['sale']
        amount = data['amount']
        method = data['method']
        
        # Check if sale is already fully paid
        if sale.payment_status == 'paid':
            raise serializers.ValidationError("Sale is already fully paid")
        
        # Validate amount
        remaining = sale.total - sale.amount_paid
        if amount > remaining:
            raise serializers.ValidationError(f"Amount exceeds remaining balance: {remaining}")
        
        # Validate phone for mobile payments
        if method in ['mpesa', 'airtel'] and not data.get('phone_number'):
            raise serializers.ValidationError("Phone number is required for mobile payments")
        
        return data
    
    def create(self, validated_data):
        """Create payment record"""
        request = self.context.get('request')
        
        # Generate transaction reference
        transaction_reference = f"PAY-{timezone.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        
        payment = Payment.objects.create(
            transaction_reference=transaction_reference,
            initiated_by=request.user,
            **validated_data
        )
        
        return payment


class PaymentCallbackSerializer(serializers.ModelSerializer):
    """Serializer for payment callbacks"""
    
    class Meta:
        model = PaymentCallback
        fields = [
            'id', 'payment', 'callback_type', 'raw_data', 'processed',
            'transaction_id', 'amount', 'phone_number', 'success',
            'error_message', 'received_at', 'processed_at'
        ]
        read_only_fields = ['id', 'received_at', 'processed_at']


class RefundSerializer(serializers.ModelSerializer):
    """Serializer for refunds"""
    payment_reference = serializers.CharField(source='payment.transaction_reference', read_only=True)
    requested_by_name = serializers.CharField(source='requested_by.username', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.username', read_only=True)
    
    class Meta:
        model = Refund
        fields = [
            'id', 'payment', 'payment_reference', 'amount', 'reason',
            'status', 'refund_reference', 'external_reference',
            'requested_by', 'requested_by_name', 'approved_by', 'approved_by_name',
            'requested_at', 'completed_at', 'error_message'
        ]
        read_only_fields = [
            'id', 'refund_reference', 'status', 'external_reference',
            'requested_by', 'approved_by', 'requested_at', 'completed_at', 'error_message'
        ]


class RefundRequestSerializer(serializers.Serializer):
    """Serializer for requesting refunds"""
    payment = serializers.PrimaryKeyRelatedField(queryset=Payment.objects.all())
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    reason = serializers.CharField()
    
    def validate_payment(self, value):
        """Validate payment can be refunded"""
        if value.status != 'success':
            raise serializers.ValidationError("Can only refund successful payments")
        
        # Check if already refunded
        total_refunded = sum(r.amount for r in value.refunds.filter(status='completed'))
        if total_refunded >= value.amount:
            raise serializers.ValidationError("Payment has already been fully refunded")
        
        return value
    
    def validate(self, data):
        """Validate refund amount"""
        payment = data['payment']
        amount = data['amount']
        
        total_refunded = sum(r.amount for r in payment.refunds.filter(status='completed'))
        available = payment.amount - total_refunded
        
        if amount > available:
            raise serializers.ValidationError(f"Refund amount exceeds available: {available}")
        
        return data
    
    def create(self, validated_data):
        """Create refund request"""
        request = self.context.get('request')
        
        refund_reference = f"REF-{timezone.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        
        refund = Refund.objects.create(
            refund_reference=refund_reference,
            requested_by=request.user,
            **validated_data
        )
        
        return refund
