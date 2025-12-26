from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Payment, PaymentCallback, Refund
from .serializers import (
    PaymentSerializer, PaymentInitiateSerializer,
    PaymentCallbackSerializer, RefundSerializer, RefundRequestSerializer
)


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for payments"""
    queryset = Payment.objects.all().select_related('sale', 'initiated_by')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['sale', 'method', 'status']
    
    def get_serializer_class(self):
        if self.action == 'initiate':
            return PaymentInitiateSerializer
        return PaymentSerializer
    
    def get_queryset(self):
        """Filter by date range if provided"""
        queryset = super().get_queryset()
        
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(initiated_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(initiated_at__lte=end_date)
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def initiate(self, request):
        """Initiate a payment"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()
        
        method = payment.method
        
        # Route to appropriate payment handler
        if method == 'mpesa':
            from payments.mpesa.services import initiate_mpesa_payment
            result = initiate_mpesa_payment(payment)
        elif method == 'airtel':
            from payments.airtel.services import initiate_airtel_payment
            result = initiate_airtel_payment(payment)
        elif method == 'card':
            from payments.cards.services import initiate_card_payment
            result = initiate_card_payment(payment)
        elif method == 'cash':
            # Cash payments are instant
            from django.utils import timezone
            payment.status = 'success'
            payment.completed_at = timezone.now()
            payment.save()
            
            # Update sale
            payment.sale.amount_paid += payment.amount
            payment.sale.update_payment_status()
            
            result = {'success': True, 'payment': payment}
        else:
            result = {'success': False, 'error': 'Unsupported payment method'}
        
        if result.get('success'):
            return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)
        else:
            payment.status = 'failed'
            payment.error_message = result.get('error', 'Unknown error')
            payment.save()
            return Response(
                {'error': payment.error_message},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify payment status"""
        payment = self.get_object()
        
        if payment.method == 'mpesa':
            from payments.mpesa.services import verify_mpesa_payment
            result = verify_mpesa_payment(payment)
        elif payment.method == 'airtel':
            from payments.airtel.services import verify_airtel_payment
            result = verify_airtel_payment(payment)
        elif payment.method == 'card':
            from payments.cards.services import verify_card_payment
            result = verify_card_payment(payment)
        else:
            result = {'success': False, 'error': 'Cannot verify this payment method'}
        
        serializer = self.get_serializer(payment)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get all pending payments"""
        payments = self.get_queryset().filter(status__in=['pending', 'processing'])
        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data)


class PaymentCallbackViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for payment callbacks (read-only)"""
    queryset = PaymentCallback.objects.all().select_related('payment')
    serializer_class = PaymentCallbackSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['callback_type', 'processed', 'success']


class RefundViewSet(viewsets.ModelViewSet):
    """ViewSet for refunds"""
    queryset = Refund.objects.all().select_related('payment', 'requested_by', 'approved_by')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['payment', 'status']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return RefundRequestSerializer
        return RefundSerializer
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve and process refund"""
        refund = self.get_object()
        
        if refund.status != 'pending':
            return Response(
                {'error': 'Refund is not pending'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Process refund based on payment method
        payment = refund.payment
        
        if payment.method == 'mpesa':
            from payments.mpesa.services import process_mpesa_refund
            result = process_mpesa_refund(refund)
        elif payment.method == 'airtel':
            from payments.airtel.services import process_airtel_refund
            result = process_airtel_refund(refund)
        elif payment.method == 'card':
            from payments.cards.services import process_card_refund
            result = process_card_refund(refund)
        elif payment.method == 'cash':
            # Cash refunds are manual
            from django.utils import timezone
            refund.status = 'completed'
            refund.approved_by = request.user
            refund.completed_at = timezone.now()
            refund.save()
            
            # Update payment status
            payment.status = 'refunded'
            payment.save()
            
            result = {'success': True}
        else:
            result = {'success': False, 'error': 'Unsupported refund method'}
        
        if result.get('success'):
            serializer = self.get_serializer(refund)
            return Response(serializer.data)
        else:
            refund.status = 'failed'
            refund.error_message = result.get('error', 'Unknown error')
            refund.save()
            return Response(
                {'error': refund.error_message},
                status=status.HTTP_400_BAD_REQUEST
            )
