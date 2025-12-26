from django.contrib import admin
from .models import StockMovement, StockAlert, StockCount, StockCountItem


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['product', 'movement_type', 'quantity', 'stock_before', 'stock_after', 'created_at']
    list_filter = ['movement_type', 'created_at']
    search_fields = ['product__name', 'reference_number']
    readonly_fields = ['stock_before', 'stock_after', 'created_at']
    
    fieldsets = (
        ('Movement Details', {
            'fields': ('product', 'movement_type', 'quantity', 'stock_before', 'stock_after')
        }),
        ('Reference Information', {
            'fields': ('reference_number', 'unit_cost', 'notes')
        }),
        ('Audit Info', {
            'fields': ('created_by', 'created_at')
        }),
    )


@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = ['product', 'current_stock', 'threshold', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['product__name']
    readonly_fields = ['created_at', 'updated_at']


class StockCountItemInline(admin.TabularInline):
    model = StockCountItem
    extra = 0
    readonly_fields = ['variance', 'counted_at']


@admin.register(StockCount)
class StockCountAdmin(admin.ModelAdmin):
    list_display = ['count_number', 'description', 'status', 'started_at', 'completed_at']
    list_filter = ['status', 'started_at']
    search_fields = ['count_number', 'description']
    readonly_fields = ['count_number', 'started_at', 'completed_at']
    inlines = [StockCountItemInline]
