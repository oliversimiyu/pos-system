from django.db import models
from django.conf import settings
from apps.products.models import Product


class StockMovement(models.Model):
    """Track all inventory movements"""
    MOVEMENT_TYPE_CHOICES = (
        ('purchase', 'Purchase/Restock'),
        ('sale', 'Sale'),
        ('adjustment', 'Manual Adjustment'),
        ('return', 'Return'),
        ('damage', 'Damage/Loss'),
        ('transfer', 'Transfer'),
    )
    
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='stock_movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPE_CHOICES)
    quantity = models.IntegerField()  # Positive for additions, negative for reductions
    stock_before = models.IntegerField()
    stock_after = models.IntegerField()
    
    reference_number = models.CharField(max_length=100, blank=True, help_text="Sale/Purchase reference")
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='stock_movements')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'stock_movements'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'created_at']),
            models.Index(fields=['movement_type']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - {self.movement_type} ({self.quantity})"


class StockAlert(models.Model):
    """Low stock alerts"""
    ALERT_STATUS_CHOICES = (
        ('active', 'Active'),
        ('resolved', 'Resolved'),
        ('ignored', 'Ignored'),
    )
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_alerts')
    current_stock = models.IntegerField()
    threshold = models.IntegerField()
    status = models.CharField(max_length=20, choices=ALERT_STATUS_CHOICES, default='active')
    
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='resolved_alerts'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'stock_alerts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"Alert: {self.product.name} - Stock: {self.current_stock}/{self.threshold}"


class StockCount(models.Model):
    """Physical stock count/audit"""
    STATUS_CHOICES = (
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    count_number = models.CharField(max_length=50, unique=True, db_index=True)
    description = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    
    started_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT, 
        related_name='started_counts'
    )
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True,
        related_name='completed_counts'
    )
    
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'stock_counts'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Stock Count {self.count_number} - {self.status}"


class StockCountItem(models.Model):
    """Items in a stock count"""
    stock_count = models.ForeignKey(StockCount, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    
    system_quantity = models.IntegerField(help_text="Quantity per system records")
    physical_quantity = models.IntegerField(help_text="Actual counted quantity")
    variance = models.IntegerField(default=0)
    
    notes = models.TextField(blank=True)
    counted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'stock_count_items'
        unique_together = ['stock_count', 'product']
    
    def __str__(self):
        return f"{self.product.name} - System: {self.system_quantity}, Physical: {self.physical_quantity}"
    
    def save(self, *args, **kwargs):
        """Calculate variance"""
        self.variance = self.physical_quantity - self.system_quantity
        super().save(*args, **kwargs)
