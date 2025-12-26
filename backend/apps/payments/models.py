from django.db import models
from django.conf import settings
from apps.sales.models import Sale


class Payment(models.Model):
    """Payment transactions for sales"""
    METHOD_CHOICES = (
        ('cash', 'Cash'),
        ('mpesa', 'M-Pesa'),
        ('airtel', 'Airtel Money'),
        ('card', 'Card Payment'),
        ('bank', 'Bank Transfer'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    )
    
    sale = models.ForeignKey(Sale, on_delete=models.PROTECT, related_name='payments')
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_reference = models.CharField(max_length=100, unique=True, db_index=True)
    external_reference = models.CharField(max_length=100, blank=True, help_text="M-Pesa/Airtel/Gateway ref")
    
    phone_number = models.CharField(max_length=15, blank=True)
    account_number = models.CharField(max_length=100, blank=True)
    
    initiated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='initiated_payments')
    initiated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    error_message = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-initiated_at']
        indexes = [
            models.Index(fields=['sale', 'status']),
            models.Index(fields=['method', 'status']),
            models.Index(fields=['transaction_reference']),
        ]
    
    def __str__(self):
        return f"{self.method} - {self.amount} - {self.status}"


class PaymentCallback(models.Model):
    """Log all payment callbacks/webhooks"""
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='callbacks', null=True, blank=True)
    
    callback_type = models.CharField(max_length=50, help_text="mpesa_callback, airtel_callback, etc.")
    raw_data = models.JSONField()
    processed = models.BooleanField(default=False)
    
    transaction_id = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    
    success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    
    received_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'payment_callbacks'
        ordering = ['-received_at']
        indexes = [
            models.Index(fields=['callback_type', 'processed']),
            models.Index(fields=['transaction_id']),
        ]
    
    def __str__(self):
        return f"{self.callback_type} - {self.transaction_id} - {'Processed' if self.processed else 'Pending'}"


class Refund(models.Model):
    """Payment refunds"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    payment = models.ForeignKey(Payment, on_delete=models.PROTECT, related_name='refunds')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    refund_reference = models.CharField(max_length=100, unique=True)
    external_reference = models.CharField(max_length=100, blank=True)
    
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='requested_refunds')
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True,
        related_name='approved_refunds'
    )
    
    requested_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    error_message = models.TextField(blank=True)
    
    class Meta:
        db_table = 'refunds'
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"Refund {self.refund_reference} - {self.amount} - {self.status}"
