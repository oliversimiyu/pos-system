from django.db import models
from django.conf import settings
from apps.products.models import Product


class Sale(models.Model):
    """Sale/Order model"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('unpaid', 'Unpaid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    )
    
    sale_number = models.CharField(max_length=50, unique=True, db_index=True)
    cashier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='sales')
    customer_name = models.CharField(max_length=200, blank=True)
    customer_phone = models.CharField(max_length=15, blank=True)
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    change = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'sales'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sale_number']),
            models.Index(fields=['created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Sale {self.sale_number} - {self.total}"
    
    def calculate_totals(self):
        """Calculate sale totals from line items"""
        items = self.items.all()
        self.subtotal = sum(item.subtotal for item in items)
        self.tax_amount = sum(item.tax_amount for item in items)
        self.total = self.subtotal + self.tax_amount - self.discount
        self.save()
    
    def update_payment_status(self):
        """Update payment status based on amount paid"""
        if self.amount_paid >= self.total:
            self.payment_status = 'paid'
        elif self.amount_paid > 0:
            self.payment_status = 'partial'
        else:
            self.payment_status = 'unpaid'
        self.save()


class SaleItem(models.Model):
    """Sale line items"""
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='sale_items')
    
    product_name = models.CharField(max_length=200)  # Snapshot of product name at time of sale
    product_barcode = models.CharField(max_length=100)  # Snapshot
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity = models.IntegerField(default=1)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'sale_items'
        ordering = ['id']
    
    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        """Calculate line totals before saving"""
        self.subtotal = self.unit_price * self.quantity
        self.tax_amount = (self.subtotal * self.tax_rate) / 100
        self.total = self.subtotal + self.tax_amount
        super().save(*args, **kwargs)
