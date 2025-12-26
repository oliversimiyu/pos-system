from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User model with role-based access"""
    
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('cashier', 'Cashier'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='cashier')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.username} ({self.role})"
