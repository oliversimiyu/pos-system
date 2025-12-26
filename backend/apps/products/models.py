from django.db import models


class Category(models.Model):
    """Product Category model"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """Product model with barcode support"""
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    barcode = models.CharField(max_length=100, unique=True, db_index=True)
    sku = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Tax percentage")
    stock = models.IntegerField(default=0)
    low_stock_threshold = models.IntegerField(default=10)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['barcode']),
            models.Index(fields=['sku']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.barcode})"
    
    @property
    def is_low_stock(self):
        return self.stock <= self.low_stock_threshold
    
    @property
    def total_price(self):
        """Calculate price including tax"""
        tax_amount = (self.price * self.tax) / 100
        return self.price + tax_amount
